#!/usr/bin/env python3
"""Drift check for the VM server's config: env-knob sanity + secret-shape invariants."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config


def test_defaults_are_family_boring(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "MODAL_VM_APP_NAME",
        "MODAL_VM_RETENTION_PERIOD",
        "MODAL_VM_AUTH_SECRET",
        "MODAL_VM_VOLUME_NAME",
        "MODAL_VM_PORT",
        "MODAL_VM_SCALEDOWN_WINDOW",
    ):
        monkeypatch.delenv(name, raising=False)
    cfg = Config.load()
    assert cfg.app_name == "victoriametrics-server"
    assert cfg.port == 8428
    assert cfg.scaledown_window == 3600
    assert cfg.retention_period == "1"
    assert cfg.auth_secret_name == "victoriametrics-auth"
    assert cfg.volume_name == f"{cfg.app_name}-data"


def test_env_knobs_win(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODAL_VM_APP_NAME", "my-metrics")
    monkeypatch.setenv("MODAL_VM_PORT", "9999")
    monkeypatch.setenv("MODAL_VM_SCALEDOWN_WINDOW", "60")
    cfg = Config.load()
    assert cfg.app_name == "my-metrics"
    assert cfg.port == 9999
    assert cfg.scaledown_window == 60
    # volume derives from the app name when not set
    assert cfg.volume_name == "my-metrics-data"


def test_bad_port_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODAL_VM_PORT", "not-a-port")
    assert Config.load().port == 8428


def test_auth_secret_and_user_are_the_only_credential_surface():
    import tomllib

    secrets_path = Path(__file__).resolve().parent / ".." / "secrets.toml"
    secrets = tomllib.loads(secrets_path.read_text())
    secret = secrets["secret"]["auth"]
    assert secret["name"] == "victoriametrics-auth"
    assert set(secret["keys"]) == {"VM_AUTH_USER", "VM_AUTH_PASS"}
