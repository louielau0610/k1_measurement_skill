from __future__ import annotations

import csv
from pathlib import Path

import yaml

from k1_measurement.field_session import create_field_session
from k1_measurement.real_log_normalizer import NORMALIZED_COLUMNS, normalize_exported_csv_logs
from tests.test_topic_mapping import confirmed_mapping


def write_mapping(session_dir: Path) -> None:
    (session_dir / "topic_mapping.yaml").write_text(yaml.safe_dump(confirmed_mapping()), encoding="utf-8")


def test_normalizer_behavior_when_no_raw_logs_exist(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)
    session_dir = tmp_path / "test_session"
    write_mapping(session_dir)

    report = normalize_exported_csv_logs(session_dir)

    assert report["success"] is False
    assert report["reason"] == "no parseable exported CSV logs found in raw_ros"
    assert (session_dir / "normalized" / "normalization_report.json").exists()


def test_normalizer_behavior_with_minimal_exported_csv_logs(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)
    session_dir = tmp_path / "test_session"
    write_mapping(session_dir)
    raw_csv = session_dir / "raw_ros" / "exported.csv"
    raw_csv.write_text(
        "timestamp,trial_id,vx_cmd,odom_vx,odom_vy,imu_wz,source_topic\n"
        "1.0,t1,0.1,0.09,0.0,0.01,/odom\n",
        encoding="utf-8",
    )

    report = normalize_exported_csv_logs(session_dir)
    output = Path(report["output_csv"])

    assert report["success"] is True
    assert output.exists()
    with output.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["timestamp"] == "1.0"
    assert rows[0]["vx_cmd_mps"] == "0.1"
    assert rows[0]["odom_vx_mps"] == "0.09"
    assert rows[0]["imu_yaw_rate_radps"] == "0.01"
    assert list(rows[0]) == NORMALIZED_COLUMNS
