"""Menu auto-switch: VC → Clone should not require manual unload."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

spec = importlib.util.spec_from_file_location("spitztxt_cli", REPO / "spitztxt-CLI.py")
cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cli)

import spitztxt_core as core  # noqa: E402


def test_resolve_clone_after_vc_uses_last_tts(monkeypatch):
    cli._last_tts_family = core.MODEL_ORIGINAL
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_VC)
    assert cli.resolve_family_for("clone") == core.MODEL_ORIGINAL


def test_resolve_clone_keeps_turbo_if_current(monkeypatch):
    cli._last_tts_family = core.MODEL_ORIGINAL
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_TURBO)
    assert cli.resolve_family_for("clone") == core.MODEL_TURBO


def test_resolve_basic_rejects_turbo_and_vc(monkeypatch):
    cli._last_tts_family = core.MODEL_ORIGINAL
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_TURBO)
    assert cli.resolve_family_for("basic") == core.MODEL_ORIGINAL
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_VC)
    assert cli.resolve_family_for("basic") == core.MODEL_ORIGINAL


def test_resolve_emotion_after_vc(monkeypatch):
    cli._last_tts_family = core.MODEL_MTL
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_VC)
    assert cli.resolve_family_for("emotion") == core.MODEL_MTL


def test_resolve_vc_always_vc(monkeypatch):
    monkeypatch.setattr(core, "current_family", lambda: core.MODEL_ORIGINAL)
    assert cli.resolve_family_for("vc") == core.MODEL_VC
