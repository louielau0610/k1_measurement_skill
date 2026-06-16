import builtins
import socket
import subprocess
import time

FORBIDDEN = (
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
)


def test_m26c_modules_do_not_import_vendor_sdks():
    import pathlib

    root = pathlib.Path("calibration_skill")
    paths = [
        root / "adapters" / "mock.py",
        root / "adapters" / "registry.py",
        *sorted((root / "skill").glob("*.py")),
        root / "runtime" / "dry_run.py",
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN:
            assert f"import {forbidden}" not in content
            assert f"from {forbidden}" not in content


def test_domain_ports_schemas_do_not_depend_on_new_layers():
    import pathlib

    for dirname in ("domain", "ports", "schemas"):
        for path in (pathlib.Path("calibration_skill") / dirname).glob("*.py"):
            content = path.read_text(encoding="utf-8")
            assert "calibration_skill.skill" not in content
            assert "calibration_skill.runtime" not in content
            assert "calibration_skill.adapters" not in content


def test_importing_top_level_has_no_adapter_registration_or_side_effects(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("import side effect attempted")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(subprocess, "Popen", fail)
    monkeypatch.setattr(time, "sleep", fail)
    monkeypatch.setattr(builtins, "open", fail)
    monkeypatch.setattr("os.environ.__getitem__", fail, raising=False)

    import calibration_skill

    assert "adapters" not in calibration_skill.__all__
    assert "runtime" not in calibration_skill.__all__
