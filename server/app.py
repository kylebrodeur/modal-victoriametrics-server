"""modal-victoriametrics-server (candidate package): a CPU-only, scale-to-zero
VictoriaMetrics single-node instance on Modal.

Status: private writing-duo instance today. Structured as a standalone
server/ package from the start (config.py + app.py, env-driven knobs via
MODAL_VM_*) so a future extraction to its own `modal-victoriametrics-server`
repo, mirroring the family's other modal-*-server packages, is a clean
copy-out rather than a rewrite.

Auth model (important, see the design notes doc for the full rationale):
`@modal.web_server` proxies Modal's HTTPS endpoint directly to a local TCP
port with NO Modal-side request auth layer available - unlike the family's
other ASGI-based packages (vault/embedding/inference), there is no app-level
place to add a bearer check in front of a raw-binary web_server function.
Auth is therefore delegated entirely to VictoriaMetrics' own built-in
`-httpAuth.username`/`-httpAuth.password` flags, which gate every HTTP
endpoint (write, query, /vmui, everything) behind one shared credential
pulled from a Modal Secret. There is no public, unauthenticated endpoint at
all, including /health - this is a deliberate, documented divergence from
the family's usual "public /health, gated everything else" pattern, because
the wrapped binary offers no per-route auth granularity.

Version resolution: VictoriaMetrics is a third-party open-source binary, not
a kylebrodeur-owned upstream repo, so there is no "upstream tag pin" in the
usual deploy-dir sense. The image build resolves GitHub's "latest release"
dynamically at build time rather than hardcoding a version string that would
go stale. See the design notes for the tradeoff (reproducibility vs always
current) and the recommendation to pin an exact tested version once this
becomes a real published package.

Local-file baking note (2026-10-13): Modal does NOT automatically mount
sibling files/dirs next to an entrypoint script (hit this identical gap in
both the inference lane shadow-seam work and the dashboard/session-coordinator
apps earlier this session). `config.py` and the `libs/` package are
explicitly baked into the image via `add_local_file`/`add_local_dir` at a
known, hardcoded in-container destination (`/root`).
"""

from __future__ import annotations

from pathlib import Path

import modal

from config import Config
from libs.hooks import Hooks

cfg = Config.load()

# Lifecycle seam (family convention, see modal-shared-libs/libs/hooks.py):
# boot.pre/boot.post bracket the VM subprocess launch. No handlers are
# registered today; this is the extension door for future lanes (e.g. a
# session-coordinator readiness probe) without touching this file again.
hooks = Hooks(("boot.pre", "boot.post"), name="victoriametrics")

_LOCAL_DIR = Path(__file__).parent
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "ca-certificates")
    .run_commands(
        "VERSION=$(curl -fsSL https://api.github.com/repos/VictoriaMetrics/VictoriaMetrics/releases/latest"
        " | grep -m1 '\"tag_name\"' | cut -d '\"' -f4) && "
        "curl -fsSL -o /tmp/vm.tar.gz "
        '"https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/${VERSION}/'
        'victoria-metrics-linux-amd64-${VERSION}.tar.gz" && '
        "tar xzf /tmp/vm.tar.gz -C /usr/local/bin && "
        "chmod +x /usr/local/bin/victoria-metrics-prod && "
        "rm /tmp/vm.tar.gz"
    )
    .add_local_file(str(_LOCAL_DIR / "config.py"), remote_path="/root/config.py")
    .add_local_dir(str(_LOCAL_DIR / "libs"), remote_path="/root/libs")
)

app = modal.App(cfg.app_name, image=image)

data_volume = modal.Volume.from_name(cfg.volume_name, create_if_missing=True)


@app.function(
    image=image,
    volumes={"/vm-data": data_volume},
    secrets=[modal.Secret.from_name(cfg.auth_secret_name, required_keys=["VM_AUTH_USER", "VM_AUTH_PASS"])],
    scaledown_window=cfg.scaledown_window,
    max_containers=1,
)
@modal.concurrent(max_inputs=100)
@modal.web_server(cfg.port, startup_timeout=60)
def serve():
    import os
    import subprocess

    user = os.environ["VM_AUTH_USER"]
    password = os.environ["VM_AUTH_PASS"]
    argv = [
        "/usr/local/bin/victoria-metrics-prod",
        "-storageDataPath=/vm-data",
        f"-retentionPeriod={cfg.retention_period}",
        f"-httpListenAddr=0.0.0.0:{cfg.port}",
        f"-httpAuth.username={user}",
        f"-httpAuth.password={password}",
    ]
    hooks.fire("boot.pre", cfg)
    subprocess.Popen(argv)
    hooks.fire("boot.post", cfg)
