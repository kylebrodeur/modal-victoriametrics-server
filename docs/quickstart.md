# Quickstart: modal-victoriametrics-server

The metrics store: single-node VictoriaMetrics on Modal, CPU-only,
scale-to-zero, Basic-Auth-gated. This is the `mtk metrics` writer's
drop-in target.

## Deploy (project flow, toolkit 1.10.6+)

Needs: [uv](https://docs.astral.sh/uv/), git, the Modal CLI
(`uv tool install modal` + `modal setup`).

```bash
mtk init metrics-lab && cd metrics-lab
mtk pull vm --tag v0.1.2           # vendor the pinned release
mtk deploy vm                      # preflight, create the secret + volume, deploy
```

`mtk deploy vm` runs the secrets gate: the manifest declares one secret
(`victoriametrics-auth`) with two keys - `VM_AUTH_USER` (ask: prompted)
and `VM_AUTH_PASS` (generate: CSPRNG, never printed). The storage
Volume is created on first deploy.

The printed URL is `https://<workspace>--<app-name>-serve.modal.run`
(or `mtk status` after: the vm row reads it from the config).

## Point writers at it

```bash
mtk config   # then set the vm section:
#   "vm": {"base_url": "https://<workspace>--<app>-serve.modal.run",
#          "auth": "user:password"}     <- the pair you chose at deploy
```

Or env: `MODAL_TOOLKIT_VM_URL` + `MODAL_TOOLKIT_VM_AUTH`.

Then, from any package or Modal app:

```python
from toolkit.metrics import bump, MetricTimer

bump("embedding_job_done")
with MetricTimer("inference_request_seconds"):
    ...
```

## Query it

Every endpoint wants Basic auth (the binary's own `-httpAuth.*`):

```bash
curl -u user:password "https://<app-url>/api/v1/query?query=up"
# and the web UI: /vmui
```

## Verify

```bash
mtk metrics test        # one probe point; 204 = the write contract works
mtk doctor --pkg vm     # health + secrets + drift
```

## Idle cost

One CPU app with a scaledown window (default 1h): idle, it costs
nothing. Retention is 1 month by default (`MODAL_VM_RETENTION_PERIOD`);
the storage Volume is billable per GB-month.