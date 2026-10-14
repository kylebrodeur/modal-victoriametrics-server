---
name: mtk-vm-build-deploy
description: Use when deploying or upgrading the VM metrics store - secrets gate, drift check, and what deploy does to the Volume.
---

# VM: deploy and upgrade

## Deploy

```bash
mtk deploy vm
```

Order, all refusals before any account write: overlay preflight (files +
composed app name, or the instance-style exception), the vendor drift check
(`vendor/vm-server/` HEAD vs provenance, clean worktree), the secrets gate
(one declared secret; asks per missing key), then the overlay's `deploy.sh`.
Drifted vendor copies need the explicit `--allow-local-changes` (recorded
after success, never the default).

## What deploy does

- Creates the data Volume on first deploy (`<app>-data`).
- Bakes `config.py` + the vendored `libs/` into the image at `/root`
  (Modal does not mount siblings automatically; the app's `add_local_*`
  handles it).
- Resolves the VictoriaMetrics release dynamically at image build
  (GitHub latest); the version pin hardening is a documented follow-up.
- The app scales to zero; the scale-down window is an overlay knob
  (`MODAL_VM_SCALEDOWN_WINDOW`, default 3600 for an always-useful store).

## Upgrade

```bash
mtk pull vm --tag <new-release>
mtk deploy vm
```

Same tag rules as every package: a tag without a GitHub release is not
published; never reset or wipe a vendored copy to fix version confusion.
The data Volume survives every redeploy (storage is Volume-backed).