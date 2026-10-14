---
name: mtk-vm-develop
description: Use when working against a running VM metrics store - the write surface, queries, and the always-burn posture.
---

# VM: develop against a live instance

Applies once `mtk doctor --pkg vm` shows the app live (or a writer 204
lands).

## Writing (the family seam)

`metrics.py` (the toolkit's stdlib writer, vendored per package) is THE
write surface: one POST per point to
`{url}/api/v2/write?precision=s&org=-&bucket=-` with the Basic-Auth header.
`bump("event")` for counters, `MetricTimer("durations")` for elapsed:

```python
from metrics import bump, MetricTimer, write_metric

bump("session_claim_created", tags={"actor": "coordinator"})
with MetricTimer("coordinator_reconcile_seconds"):
    ...
```

## Querying

Everything is VictoriaMetrics' own surface, all under Basic Auth:
`/api/v1/query`, `/api/v1/query_range`, and the built-in UI at `/vmui`
(point a browser at the authed URL). Points land under their measurement
name with the tags you passed; counters accumulate in VM, the client keeps
nothing.

## Rules

- The writer never raises and never retries; a metrics failure never fails
  the host operation. The caller decides retry policy.
- Never put writer credentials in code: the Basic-Auth pair comes from the
  VM Secret (`VM_AUTH_USER`/`VM_ARCH_PASS` is wrong on purpose - the real
  key is `VM_AUTH_PASS`) or the writer env (`MODAL_TOOLKIT_VM_AUTH` or its
  configured prefix).
- Storage is the Volume: deleting or re-creating it loses history. Retention
  (months) is the retention knob (`MODAL_VM_RETENTION_PERIOD`).