from pathlib import Path

import pytest
import yaml

from k1_measurement.logger_node import K1MeasurementLogger


def test_logger_can_load_topic_mapping_template() -> None:
    logger = K1MeasurementLogger()
    mapping = logger.load_topic_mapping()

    assert mapping["mapping_status"] == "incomplete"
    assert mapping["required_topics"]["odom_topic"] == "TBD"


def test_default_template_mapping_is_incomplete() -> None:
    logger = K1MeasurementLogger()

    assert logger.is_mapping_complete() is False


def test_validate_mapping_for_logging_returns_false_in_dry_run() -> None:
    logger = K1MeasurementLogger(dry_run=True)

    assert logger.validate_mapping_for_logging() is False


def test_start_logging_in_dry_run_does_not_raise() -> None:
    logger = K1MeasurementLogger(dry_run=True)

    logger.start_logging()
    assert logger.is_running is False


def test_start_logging_real_mode_with_incomplete_mapping_raises() -> None:
    logger = K1MeasurementLogger(dry_run=False)

    with pytest.raises(RuntimeError):
        logger.start_logging()


def test_complete_mapping_real_mode_still_not_implemented(tmp_path: Path) -> None:
    mapping_path = tmp_path / "verified_mapping.yaml"
    mapping = {
        "mapping_status": "verified_for_logging",
        "required_topics": {
            "odom_topic": "/verified/odom",
            "imu_topic": "/verified/imu",
            "robot_state_topic": "/verified/robot_state",
        },
        "validation": {
            "odom_verified": True,
            "imu_verified": True,
            "robot_state_verified": True,
            "command_interface_verified": False,
        },
        "safety": {
            "allow_real_logging": True,
            "allow_real_robot_command": False,
        },
    }
    mapping_path.write_text(yaml.safe_dump(mapping), encoding="utf-8")
    logger = K1MeasurementLogger(str(mapping_path), dry_run=False)

    assert logger.is_mapping_complete() is True
    assert logger.validate_mapping_for_logging() is True
    with pytest.raises(NotImplementedError):
        logger.start_logging()


def test_save_csv_writes_header_only(tmp_path: Path) -> None:
    output = tmp_path / "logger_header.csv"
    logger = K1MeasurementLogger()

    logger.save_csv(str(output))

    contents = output.read_text(encoding="utf-8")
    assert "timestamp" in contents
    assert contents.count("\n") == 1
