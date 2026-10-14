"""Env-knob configuration for modal-victoriametrics-server (candidate package).

Every knob uses the MODAL_VM_ prefix, matching the "VM" shorthand already
established across this ecosystem's writer-side convention
(`MODAL_TOOLKIT_VM_URL`, `MODAL_SESSION_VM_URL` in vm_metrics.py). This is
the SERVER's own deploy-time configuration, distinct from those writer-side
URL knobs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    app_name: str
    retention_period: str
    auth_secret_name: str
    volume_name: str
    scaledown_window: int
    port: int

    @classmethod
    def load(cls) -> Config:
        app_name = os.environ.get("MODAL_VM_APP_NAME", "").strip() or "victoriametrics-server"
        retention_period = os.environ.get("MODAL_VM_RETENTION_PERIOD", "").strip() or "1"
        auth_secret_name = os.environ.get("MODAL_VM_AUTH_SECRET", "").strip() or "victoriametrics-auth"
        volume_name = os.environ.get("MODAL_VM_VOLUME_NAME", "").strip() or f"{app_name}-data"
        port_raw = os.environ.get("MODAL_VM_PORT", "").strip()
        try:
            port = int(port_raw) if port_raw else 8428
        except ValueError:
            port = 8428
        window_raw = os.environ.get("MODAL_VM_SCALEDOWN_WINDOW", "").strip()
        try:
            scaledown_window = int(window_raw) if window_raw else 3600
        except ValueError:
            scaledown_window = 3600
        return cls(
            app_name=app_name,
            retention_period=retention_period,
            auth_secret_name=auth_secret_name,
            volume_name=volume_name,
            scaledown_window=scaledown_window,
            port=port,
        )
