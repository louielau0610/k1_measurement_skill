from __future__ import annotations

import subprocess
from pathlib import Path

from k1_measurement.ros2_readonly_validator import (
    build_validation_report,
    check_ros2_availability,
    classify_topics,
    inspect_message_interfaces,
    parse_topic_list,
    parse_topic_list_with_types,
)


def completed(args: list[str], returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def test_ros2_unavailable() -> None:
    def runner(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise FileNotFoundError("missing ros2")

    result = check_ros2_availability(runner=runner)

    assert result["ros2_available"] is False
    assert "missing ros2" in result["error_message"]


def test_ros2_available() -> None:
    def runner(args, **kwargs):  # type: ignore[no-untyped-def]
        return completed(args, stdout="usage: ros2")

    result = check_ros2_availability(runner=runner)

    assert result["ros2_available"] is True
    assert result["return_code"] == 0


def test_parse_topic_list_without_message_types() -> None:
    topics = parse_topic_list("/odom\n/imu/data\n")

    assert topics == [
        {"name": "/odom", "message_type": None, "raw": "/odom"},
        {"name": "/imu/data", "message_type": None, "raw": "/imu/data"},
    ]


def test_parse_topic_list_with_message_types() -> None:
    topics = parse_topic_list_with_types("/odom [nav_msgs/msg/Odometry]\n/cmd_vel [geometry_msgs/msg/Twist]\n")

    assert topics[0]["name"] == "/odom"
    assert topics[0]["message_type"] == "nav_msgs/msg/Odometry"
    assert topics[1]["message_type"] == "geometry_msgs/msg/Twist"


def test_candidate_classification() -> None:
    grouped = classify_topics(
        [
            {"name": "/odom", "message_type": "nav_msgs/msg/Odometry", "raw": ""},
            {"name": "/imu/data", "message_type": "sensor_msgs/msg/Imu", "raw": ""},
            {"name": "/battery_state", "message_type": None, "raw": ""},
            {"name": "/robot_state", "message_type": None, "raw": ""},
            {"name": "/cmd_vel", "message_type": "geometry_msgs/msg/Twist", "raw": ""},
            {"name": "/camera/image_raw", "message_type": None, "raw": ""},
        ]
    )

    assert grouped["odom_candidates"][0]["name"] == "/odom"
    assert grouped["imu_candidates"][0]["name"] == "/imu/data"
    assert grouped["battery_candidates"][0]["name"] == "/battery_state"
    assert grouped["robot_state_candidates"][0]["name"] == "/robot_state"
    assert grouped["command_candidates"][0]["name"] == "/cmd_vel"
    assert grouped["unknown_topics"][0]["name"] == "/camera/image_raw"


def test_interface_show_success_deduplicates_types() -> None:
    calls: list[list[str]] = []

    def runner(args, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(args)
        return completed(args, stdout="Header header\n")

    results = inspect_message_interfaces(
        [
            {"name": "/odom", "message_type": "nav_msgs/msg/Odometry", "raw": ""},
            {"name": "/odom2", "message_type": "nav_msgs/msg/Odometry", "raw": ""},
        ],
        runner=runner,
    )

    assert list(results) == ["nav_msgs/msg/Odometry"]
    assert len(calls) == 1
    assert results["nav_msgs/msg/Odometry"]["return_code"] == 0


def test_interface_show_timeout() -> None:
    def runner(args, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.TimeoutExpired(args, timeout=1)

    results = inspect_message_interfaces(
        [{"name": "/imu", "message_type": "sensor_msgs/msg/Imu", "raw": ""}],
        timeout_sec=1,
        runner=runner,
    )

    assert "timeout" in results["sensor_msgs/msg/Imu"]["error_message"]


def test_json_and_markdown_report_generation(tmp_path: Path) -> None:
    def runner(args, **kwargs):  # type: ignore[no-untyped-def]
        if args == ["ros2", "--help"]:
            return completed(args, stdout="usage: ros2")
        if args == ["ros2", "topic", "list"]:
            return completed(args, stdout="/odom\n")
        if args == ["ros2", "topic", "list", "-t"]:
            return completed(args, stdout="/odom [nav_msgs/msg/Odometry]\n")
        return completed(args, stdout="interface text")

    report = build_validation_report(
        tmp_path,
        include_interface_show=True,
        runner=runner,
    )

    assert report["ros2_availability"]["ros2_available"] is True
    assert (tmp_path / "ros2_topic_discovery_report.json").exists()
    markdown = (tmp_path / "ros2_topic_discovery_report.md").read_text(encoding="utf-8")
    assert "Real K1 topic mapping is still TBD" in markdown
    assert "Dummy reports are not real K1 findings" in markdown


def test_print_only_behavior_does_not_call_runner(tmp_path: Path) -> None:
    def runner(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("runner should not be called")

    report = build_validation_report(tmp_path, print_only=True, runner=runner)

    assert report["mode"] == "print_only"
    assert report["ros2_availability"]["ros2_available"] is False
    assert (tmp_path / "ros2_topic_discovery_report.json").exists()
