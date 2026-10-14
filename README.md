<img src="https://kylebrodeur.xyz/brand/readme-headers/modal-victoriametrics-server.png" alt="modal-victoriametrics-server: single-node VictoriaMetrics on Modal" width="100%">

# modal-victoriametrics-server

---

### Production Support, Operator Kit & Architecture Services

The Modal Toolkit projects remain open-source and free to use. For production deployments and team operations, these commercial options are available:

- **[Modal Production Operator Kit ($29)](https://github.com/sponsors/kylebrodeur):** A version-locked vendor installer, a real `mtk` overlay example, retrieval and fine-tune data recipes, a dated cost worksheet, and a Modal Vault MCP client installer.
- **[Modal Architecture, Cost & Safety Audit ($147)](https://github.com/sponsors/kylebrodeur):** A written audit of one Modal application or deploy tree, with prioritized findings and recommendations.
- **[Modal Vendor-Overlay Refactor ($247)](https://github.com/sponsors/kylebrodeur):** One ready-to-review pull request that moves one supported Modal package into a vendored overlay.
- **[GitHub Sponsors ($9-$389/mo or one-time)](https://github.com/sponsors/kylebrodeur):** Monthly support, kit licenses, architecture calls, and retainer hours. Every tier's exact benefits are on that page.

<img src="https://kylebrodeur.xyz/brand/sponsor-tiers/contact-sheet.png" alt="All twelve sponsorship tiers: Supporter, Single Dev Kit + Dev Chat, Team Dev Kit + Dev Chat, Dev Call, Retainer, Retainer Plus, Coffee, Two Coffees, Three Coffees, Operator Kit, Architecture Audit, and Vendor Refactor" width="900">

---

Single-node [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)
on [Modal](https://modal.com): a CPU-only, scale-to-zero metrics store for
the [Modal Toolkit](https://github.com/kylebrodeur/modal-toolkit) family.

Part of the Modal Toolkit - one operator CLI (`mtk`) that runs the fleet as
one system.

## Docs

- [Quickstart](docs/quickstart.md): from a new project to a deployed, authed metrics store, using the `mtk` toolkit.
- [How-to](docs/how-to.md): day-to-day operation of the store (env knobs, writer contract, dashboard, upgrades, troubleshooting).

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
mtk pull vm --tag v0.1.2
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