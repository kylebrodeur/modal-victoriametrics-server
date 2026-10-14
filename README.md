# modal-victoriametrics-server

Single-node [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)
on [Modal](https://modal.com): a CPU-only, scale-to-zero metrics store for
the [Modal Toolkit](https://github.com/kylebrodeur/modal-toolkit) family.

Part of the Modal Toolkit - one operator CLI (`mtk`) that runs the fleet as
one system.

## What it is

- One VM single-node binary behind Modal's HTTPS endpoint, storage on a
  durable Volume, scale-to-zero (idle costs nothing).
- **Every endpoint is Basic-Auth-gated by the binary itself** (`-httpAuth.*`).
  This is this package's documented divergence from the family's usual
  "public /health" pattern: `@modal.web_server` proxies straight to the local
  port with no app-level auth seam, so the wrapped binary's own auth flags
  are the only available layer. There is no unauthenticated endpoint at all.
- Writers use the family's stdlib writer (`metrics.py` in
  [modal-toolkit](https://github.com/kylebrodeur/modal-toolkit), vendored per
  package): one POST per Influx-line point, never raises, never retries.
- Deploy config is env-driven (`MODAL_VM_*`); a deploy overlay + vendor pin
  is the one deploy model. See the
  [toolkit quickstart](https://github.com/kylebrodeur/modal-toolkit/blob/main/docs/quickstart.md)
  for the project flow.
- Lifecycle seam (`boot.pre` / `boot.post`, vendored from
  [modal-shared-libs](https://github.com/kylebrodeur/modal-shared-libs)):
  register from an overlay without touching package source.

## Quickstart

```bash
mtk init metrics-lab && cd metrics-lab
mtk pull vm --tag v0.1.0
mtk deploy vm          # creates the secret (asks) + the Volume, then deploys
```

Point writers at it with `MODAL_TOOLKIT_VM_URL` + `MODAL_TOOLKIT_VM_AUTH`
(`user:password`, required: every endpoint is gated). Query through the
authed `/api/v1/query` or the built-in `/vmui`.

## Deploy shape

```
<project>/vendor/vm-server/          code: git checkout pinned to a release tag
<project>/deploys/vm-server/         deploy.json (app name, env knobs, secret NAMES), deploy.sh
```

## License

Apache-2.0

## Family

Eight standalone Modal utilities from the same author:

- **modal-victoriametrics-server** (this repo)
- [modal-embedding-server](https://github.com/kylebrodeur/modal-embedding-server)
- [modal-inference-server](https://github.com/kylebrodeur/modal-inference-server)
- [modal-vision-server](https://github.com/kylebrodeur/modal-vision-server)
- [modal-vault-server](https://github.com/kylebrodeur/modal-vault-server)
- [modal-finetune-server](https://github.com/kylebrodeur/modal-finetune-server)
- [modal-shared-libs](https://github.com/kylebrodeur/modal-shared-libs)
- [modal-toolkit](https://github.com/kylebrodeur/modal-toolkit)