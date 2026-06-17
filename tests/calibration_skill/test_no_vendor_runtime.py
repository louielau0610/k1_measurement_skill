"""No-vendor runtime boundary tests."""
from __future__ import annotations

import builtins
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
}


def test_calibration_skill_source_has_no_forbidden_vendor_imports():
    offenders: list[str] = []
    for path in (ROOT / "calibration_skill").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in FORBIDDEN:
            if f"import {name}" in text or f"from {name}" in text:
                offenders.append(f"{path.relative_to(ROOT)}:{name}")
    assert offenders == []


def test_cli_import_does_not_attempt_vendor_import(monkeypatch):
    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.split(".")[0].lower() in FORBIDDEN:
            raise AssertionError(f"forbidden import attempted: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    import calibration_skill.cli as cli

    assert cli.main(["manifest"]) == 0


def test_dry_run_invoke_does_not_attempt_vendor_import():
    code = """
import builtins
forbidden = {'booster_robotics_sdk','unitree_sdk2','unitree_legged_sdk','rclpy','cyclonedds','fastdds'}
real_import = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.split('.')[0].lower() in forbidden:
        raise RuntimeError('forbidden import attempted: ' + name)
    return real_import(name, *args, **kwargs)
builtins.__import__ = guarded
import calibration_skill.cli as cli
raise SystemExit(cli.main(['invoke', '--input', 'examples/calibration_skill/dry_run_end_to_end.mock.json']))
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_vendor_import_guard_catches_accidental_import(monkeypatch):
    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.split(".")[0].lower() in FORBIDDEN:
            raise RuntimeError(f"forbidden import attempted: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    try:
        __import__("rclpy")
    except RuntimeError as exc:
        assert "forbidden import attempted" in str(exc)
    else:
        raise AssertionError("guard did not catch forbidden import")
