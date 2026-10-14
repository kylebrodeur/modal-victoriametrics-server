"""modal-shared-libs: the Modal Toolkit family's shared library home.

One repo owning the modules every package uses, vendored verbatim into
each package tree (the established family pattern - see `mtk libs sync`).
Nothing here depends on Modal; everything is stdlib-first so any
package (or any overlay lane) can consume it anywhere.

## Modules

- `libs/hooks.py` — the lifecycle hook seam (register/on/fire, closed
  tag sets, contained errors). Every package configures its own tag
  list; the contract is shared.

## Vendoring contract

Vendored copies are refreshed by `mtk libs sync`; hand-edits are drift
and fail `mtk libs check` (md5 parity per vendored module). The vendored
header must name the canonical home:

    Vendored from modal-shared-libs (libs/hooks.py) by mtk libs sync:
    family repo: <package>, md5 <hash>. Canonical source of truth;
    report fixes there, not here.
"""

from __future__ import annotations

__version__ = "0.1.1"
