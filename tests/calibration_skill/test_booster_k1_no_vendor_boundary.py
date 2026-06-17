import ast
import socket
import subprocess
import time
from pathlib import Path

FORBIDDEN = (
    "booster_robotics_sdk",
    "B1LocoClient",
    "ChannelFactory",
    "RobotMode",
    "fastdds",
    "cyclonedds",
    "rclpy",
)


def test_no_booster_sdk_import_in_ordinary_runtime():
    for path in Path("calibration_skill").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                names = [alias.name for alias in node.names]
                text = " ".join([module, *names])
                assert not any(forbidden in text for forbidden in FORBIDDEN), path


def test_import_guard_catches_side_effects(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(subprocess, "Popen", fail)
    monkeypatch.setattr(time, "sleep", fail)
    import calibration_skill.adapters.booster_k1 as booster_k1

    assert booster_k1.BoosterK1Adapter is not None


def test_no_sockets_dds_udp_or_file_writes_in_k1_adapter_sources():
    source = "\n".join(path.read_text(encoding="utf-8") for path in Path("calibration_skill/adapters/booster_k1").glob("*.py"))
    forbidden_tokens = ["socket", "UDP", "FastDDS", "DDS", "open(", "Path(", "subprocess", "sleep("]
    for token in forbidden_tokens:
        assert token not in source
