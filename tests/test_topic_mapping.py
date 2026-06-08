from __future__ import annotations

from pathlib import Path

import yaml

from k1_measurement.topic_mapping import confirmed_topics, load_topic_mapping, validate_topic_mapping


def confirmed_mapping() -> dict:
    return {
        "odom": {
            "topic": "/odom",
            "message_type": "nav_msgs/msg/Odometry",
            "timestamp_field": "stamp",
            "required": True,
            "confirmed": True,
            "linear_velocity_x_field": "odom_vx",
            "linear_velocity_y_field": "odom_vy",
            "angular_velocity_z_field": "odom_wz",
            "position_x_field": "odom_x",
            "position_y_field": "odom_y",
            "notes": "",
        },
        "imu": {
            "topic": "/imu",
            "message_type": "sensor_msgs/msg/Imu",
            "timestamp_field": "stamp",
            "required": True,
            "confirmed": True,
            "angular_velocity_z_field": "imu_wz",
            "orientation_field": "orientation",
            "notes": "",
        },
        "battery": {
            "topic": "TBD",
            "message_type": "TBD",
            "timestamp_field": "TBD",
            "required": False,
            "confirmed": False,
            "battery_percentage_field": "TBD",
            "voltage_field": "TBD",
            "notes": "",
        },
        "robot_state": {
            "topic": "TBD",
            "message_type": "TBD",
            "timestamp_field": "TBD",
            "required": False,
            "confirmed": False,
            "mode_field": "TBD",
            "gait_field": "TBD",
            "notes": "",
        },
        "command": {
            "topic": "/cmd_vel",
            "message_type": "geometry_msgs/msg/Twist",
            "timestamp_field": "stamp",
            "required": True,
            "confirmed": True,
            "command_vx_field": "vx_cmd",
            "command_vy_field": "vy_cmd",
            "command_wz_field": "wz_cmd",
            "notes": "",
        },
    }


def test_topic_mapping_template_loading() -> None:
    mapping = load_topic_mapping("configs/real_k1_topic_mapping_template.yaml")

    assert set(mapping) == {"odom", "imu", "battery", "robot_state", "command"}
    assert mapping["odom"]["topic"] == "TBD"


def test_topic_mapping_validation_success() -> None:
    summary = validate_topic_mapping(confirmed_mapping())

    assert summary["valid"] is True
    assert confirmed_topics(confirmed_mapping()) == ["/odom", "/imu", "/cmd_vel"]


def test_topic_mapping_validation_failure_when_required_topics_tbd() -> None:
    mapping = confirmed_mapping()
    mapping["odom"]["topic"] = "TBD"

    summary = validate_topic_mapping(mapping)

    assert summary["valid"] is False
    assert "odom: required topic remains TBD" in summary["errors"]


def test_topic_mapping_validation_failure_when_confirmed_false() -> None:
    mapping = confirmed_mapping()
    mapping["command"]["confirmed"] = False

    summary = validate_topic_mapping(mapping)

    assert summary["valid"] is False
    assert "command: required section is not confirmed" in summary["errors"]


def test_load_topic_mapping_from_file(tmp_path: Path) -> None:
    path = tmp_path / "mapping.yaml"
    path.write_text(yaml.safe_dump(confirmed_mapping()), encoding="utf-8")

    assert load_topic_mapping(path)["odom"]["topic"] == "/odom"
