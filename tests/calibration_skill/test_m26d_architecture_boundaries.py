import socket
import subprocess
import time
from pathlib import Path

FORBIDDEN = (
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
)


def test_cli_and_manifest_import_no_vendor_sdks():
    paths = [
        Path("calibration_skill/cli.py"),
        Path("calibration_skill/skill/manifest.py"),
        Path("calibration_skill/skill/manifest.schema.json"),
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN:
            assert f"import {forbidden}" not in content
            assert f"from {forbidden}" not in content


def test_importing_cli_has_no_hardware_registration_or_runtime_side_effects(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("forbidden import side effect")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(subprocess, "Popen", fail)
    monkeypatch.setattr(time, "sleep", fail)
    monkeypatch.setattr("os.environ.__getitem__", fail, raising=False)

    import calibration_skill.cli as cli

    assert cli is not None


def test_cli_does_not_write_files_without_output_path(tmp_path):
    import subprocess as sp
    import sys

    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    result = sp.run(
        [sys.executable, "-m", "calibration_skill.cli", "manifest"],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        timeout=30,
    )
    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert result.returncode == 0
    assert before == after
