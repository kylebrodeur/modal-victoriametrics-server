# How-to: modal-victoriametrics-server

Day-to-day operation of the metrics store. The quickstart covers the
first deploy; this covers what running it looks like.

## Day 2: what is running

`mtk status` shows the vm row (configured/secrets/reachable). The URL it
uses comes from the toolkit config's `vm.base_url`; the auth pair is
`vm.auth` (`user:password`) - stored mode 600, never printed by any
command.

## Instance identity (private overlays)

The app name, secret name, volume name, port, scaledown window, and
retention are env knobs (`MODAL_VM_*`), read at import:

| Knob | Default |
|---|---|
| `MODAL_VM_APP_NAME` | `victoriametrics-server` |
| `MODAL_VM_AUTH_SECRET` | `victoriametrics-auth` |
| `MODAL_VM_VOLUME_NAME` | `<app-name>-data` |
| `MODAL_VM_PORT` | `8428` |
| `MODAL_VM_SCALEDOWN_WINDOW` | `3600` |
| `MODAL_VM_RETENTION_PERIOD` | `1` (month) |

A private lane deploys its own instance by setting the knobs in its
overlay's `deploy.sh` (see the toolkit's
[vendor-model walkthrough](https://github.com/kylebrodeur/modal-toolkit/blob/main/docs/quickstart.md)).
Plain-repo deploys stay forbidden: the deploy unit is the vendored
tag-pinned copy through the overlay.

## Writer contract (what clients can rely on)

- One POST per Influx-line point to `/api/v2/write?precision=s`; a
  204 means the point landed. `org`/`bucket` query params are accepted
  Influx placeholders (ignored by single-node).
- The writer never raises and never retries: a failed write returns
  `False` and prints one stderr line; the caller decides the policy.
  A metrics outage must never fail a host operation.
- Fieldset is `key=value` (the module's line builder uses `value=`).
  Timestamps are seconds and mark the reading, not the send: pass
  `ts` explicitly for late events.
- Escape tag keys/values (backslash, comma, equals); measurement
  names cannot contain spaces.

## Feeding the fleet dashboard

The toolkit's dashboard has a vm card (Basic-auth'd health): set the
card's `token` field to the same `user:password` pair and it probes
with Basic auth (`Bearer` for every other package's card).

## Upgrades

The upgrade unit is the upstream release tag:

```bash
mtk pull vm --tag <new-tag>      # re-vendor (confirm: a decision)
mtk deploy vm                    # re-preflight + deploy
```

Storage (the Volume) survives redeploys; deleting it is a real decision,
so there is no volume-wipe verb in the toolkit.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `mtk metrics test` exit 1 ("no VM answers") | The `vm` config section is empty or the app is cold. Check `mtk metrics url` (which URL + source), then `curl` `/health` - a cold app spawns on the first timed-out request; retry once. |
| HTTP 401 from every endpoint | Wrong or missing `vm.auth` pair (or the pair went stale after a secret rotate: `mtk secrets rotate victoriametrics-auth` invalidates live clients - update every writer then). |
| Points missing from queries | Timestamps are the reading time: late callers must pass `ts`; also check the 1-month retention window. |
| "vendor drift for vm" on deploy | A file under `vendor/vm-server/` was edited. Move the change to the overlay or upstream, then re-vendor. |