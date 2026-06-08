"""Mapping-driven normalization for real K1 exported field logs."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from k1_measurement.field_session import load_ground_truth_sheet, summarize_ground_truth_sheet
from k1_measurement.topic_mapping import load_topic_mapping


NORMALIZED_COLUMNS = [
    "timestamp",
    "trial_id",
    "vx_cmd_mps",
    "odom_vx_mps",
    "odom_vy_mps",
    "imu_yaw_rate_radps",
    "battery_percentage",
    "robot_mode",
    "floor_type",
    "condition",
    "slope",
    "source_topic",
    "notes",
]


def _field(row: dict[str, str], field_name: Any) -> str:
    if not field_name or field_name == "TBD":
        return ""
    return row.get(str(field_name), "")


def _first_available(row: dict[str, str], names: list[str]) -> str:
    for name in names:
        if name in row and row[name] != "":
            return row[name]
    return ""


def _topic_rows(raw_dir: Path) -> list[tuple[Path, dict[str, str]]]:
    rows: list[tuple[Path, dict[str, str]]] = []
    for path in sorted(raw_dir.glob("*.csv")):
        with path.open("r", encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                rows.append((path, row))
    return rows


def _ground_truth_by_trial(session_dir: Path) -> dict[str, dict[str, str]]:
    path = session_dir / "ground_truth_trial_sheet.csv"
    if not path.exists():
        return {}
    return {row.get("trial_id", ""): row for row in load_ground_truth_sheet(path) if row.get("trial_id")}


def normalize_exported_csv_logs(session_dir: str | Path) -> dict[str, Any]:
    """Normalize exported CSV logs when parseable rows are present."""

    session = Path(session_dir)
    raw_dir = session / "raw_ros"
    normalized_dir = session / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    output_csv = normalized_dir / "raw_measurement_log.csv"
    report_path = normalized_dir / "normalization_report.json"
    mapping = load_topic_mapping(session / "topic_mapping.yaml")
    source_rows = _topic_rows(raw_dir)
    ground_truth = _ground_truth_by_trial(session)

    if not source_rows:
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "reason": "no parseable exported CSV logs found in raw_ros",
            "output_csv": str(output_csv),
            "rows_written": 0,
            "ground_truth_summary": summarize_ground_truth_sheet(session / "ground_truth_trial_sheet.csv")
            if (session / "ground_truth_trial_sheet.csv").exists()
            else {},
        }
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    odom = mapping.get("odom", {})
    imu = mapping.get("imu", {})
    battery = mapping.get("battery", {})
    robot_state = mapping.get("robot_state", {})
    command = mapping.get("command", {})

    normalized_rows: list[dict[str, str]] = []
    for source_path, row in source_rows:
        trial_id = _first_available(row, ["trial_id", "trial"])
        gt = ground_truth.get(trial_id, {})
        normalized_rows.append(
            {
                "timestamp": _first_available(row, ["timestamp", str(odom.get("timestamp_field")), str(imu.get("timestamp_field"))]),
                "trial_id": trial_id,
                "vx_cmd_mps": _first_available(row, ["vx_cmd_mps", "vx_cmd", str(command.get("command_vx_field"))]),
                "odom_vx_mps": _first_available(row, ["odom_vx_mps", "odom_vx", str(odom.get("linear_velocity_x_field"))]),
                "odom_vy_mps": _first_available(row, ["odom_vy_mps", "odom_vy", str(odom.get("linear_velocity_y_field"))]),
                "imu_yaw_rate_radps": _first_available(row, ["imu_yaw_rate_radps", str(imu.get("angular_velocity_z_field"))]),
                "battery_percentage": _first_available(row, ["battery_percentage", str(battery.get("battery_percentage_field"))]),
                "robot_mode": _first_available(row, ["robot_mode", str(robot_state.get("mode_field"))]),
                "floor_type": gt.get("floor_type", row.get("floor_type", "")),
                "condition": gt.get("condition", row.get("condition", "")),
                "slope": gt.get("slope", row.get("slope", "")),
                "source_topic": row.get("source_topic", source_path.stem),
                "notes": row.get("notes", ""),
            }
        )

    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=NORMALIZED_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "success": True,
        "output_csv": str(output_csv),
        "rows_written": len(normalized_rows),
        "source_csv_files": sorted({str(path) for path, _ in source_rows}),
        "missing_values_are_empty": True,
        "ground_truth_summary": summarize_ground_truth_sheet(session / "ground_truth_trial_sheet.csv")
        if (session / "ground_truth_trial_sheet.csv").exists()
        else {},
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
