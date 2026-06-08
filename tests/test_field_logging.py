from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from k1_measurement.field_logging import build_rosbag_record_command, start_field_logger
from k1_measurement.field_session import create_field_session
from tests.test_topic_mapping import confirmed_mapping


class FakeProcess:
    def __init__(self, timeout: bool = False) -> None:
        self.returncode = 0
        self.timeout = timeout
        self.terminated = False

    def communicate(self, timeout=None):  # type: ignore[no-untyped-def]
        if self.timeout and timeout is not None and not self.terminated:
            raise subprocess.TimeoutExpired(["ros2"], timeout)
        return ("stdout", "stderr")

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = -15


def write_mapping(session_dir: Path) -> None:
    (session_dir / "topic_mapping.yaml").write_text(yaml.safe_dump(confirmed_mapping()), encoding="utf-8")


def test_field_logger_command_construction_from_confirmed_topics(tmp_path: Path) -> None:
    command = build_rosbag_record_command(tmp_path, ["/odom", "/imu", "/cmd_vel"])

    assert command == ["ros2", "bag", "record", "-o", str(tmp_path / "raw_ros" / "rosbag"), "/odom", "/imu", "/cmd_vel"]


def test_field_logger_runs_mocked_rosbag_command(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)
    session_dir = tmp_path / "test_session"
    write_mapping(session_dir)
    calls = []

    def popen(command, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(command)
        return FakeProcess()

    summary = start_field_logger(session_dir, duration_sec=1, popen_factory=popen)

    assert calls[0][:4] == ["ros2", "bag", "record", "-o"]
    assert "/odom" in calls[0]
    assert summary["success"] is True
    assert (session_dir / "logger_run_summary.json").exists()


def test_field_logger_timeout_behavior_using_mocked_subprocess(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)
    session_dir = tmp_path / "test_session"
    write_mapping(session_dir)

    def popen(command, **kwargs):  # type: ignore[no-untyped-def]
        return FakeProcess(timeout=True)

    summary = start_field_logger(session_dir, duration_sec=0.01, popen_factory=popen)

    assert summary["timed_out_and_terminated"] is True
    assert summary["success"] is True


def test_field_logger_rejects_incomplete_mapping(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)

    with pytest.raises(ValueError):
        start_field_logger(tmp_path / "test_session", popen_factory=lambda *args, **kwargs: FakeProcess())
