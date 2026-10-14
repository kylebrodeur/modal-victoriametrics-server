---
name: mtk-vm-init-config
description: Use when a project adds the VM metrics store - mtk init, the overlay pair, and the one shared-credential secret setup.
---

# VM: init and config for a project

## Init

```bash
mtk init metrics-lab
cd metrics-lab
mtk pull vm --tag v0.1.0
```

`mtk pull` vendors the exact release tag into `vendor/vm-server/` and writes
its provenance. The copy is read-only; drift refuses a deploy.

## The overlay

`deploys/vm-server/deploy.json` names the app `<project>-vm`:

```json
{
  "pkg": "vm",
  "app_name": "metrics-lab-vm",
  "upstream": { "repo": "modal-victoriametrics-server", "tag": "v0.1.0" },
  "env": {
    "MODAL_VM_RETENTION_PERIOD": "1",
    "MODAL_VM_SCALEDOWN_WINDOW": "3600"
  }
}
```

`deploy.sh` deploys the VENDORED copy under `vendor/vm-server/`: never a live
checkout.

## Before the first deploy

- One secret is declared: `victoriametrics-auth` (keys `VM_AUTH_USER`, asked;
  `VM_AUTH_PASS`, generated). It gates EVERY endpoint - VictoriaMetrics' own
  `-httpAuth.*` flags are the only auth layer in front of the raw binary
  (this package's documented divergence: no public `/health`).
- The data Volume is created on first deploy (`<app>-data`).

## Verify

```bash
mtk doctor --pkg vm
mtk vm status    # wakes the app (Basic-Auth'd): the coordinator/writers answer
```