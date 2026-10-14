---
name: mtk-vm-setup-hooks
description: Use when wiring hooks and metrics-writer env on the VM package - the boot seam, the writer env prefix, and the writer contract.
---

# VM: setup hooks and writers

## The boot seam

The server carries a lifecycle hook seam: one shared instance named
`victoriametrics`, closed tag set `boot.pre` / `boot.post`. Register without
editing vendored code - the seam brackets only the VM subprocess launch
today, and handler errors are contained and reported (`last_errors(tag)`).

```python
from libs.hooks import hooks


@hooks.on("boot.post")
def observe(cfg):
    print(cfg)
```

## The writer side (any app or lane)

The family's stdlib writer (`metrics.py` in the toolkit, vendored verbatim
per package) writes to this VM. Writer env contract:

- `MODAL_TOOLKIT_VM_URL` (or the vendored copy's configured prefix):
  this VM's URL.
- `MODAL_TOOLKIT_VM_AUTH` (`user:password`): REQUIRED against this server
  (every endpoint is Basic-Auth-gated). Without it every write is a silent
  401 - set it in the writer's Secret or overlay env.

Verify plumbing: one `write_metric("writer_check_probe", 1)` then query it
back through the authed `/api/v1/query`. The writer never raises and never
retries; a metrics failure never fails the host operation.