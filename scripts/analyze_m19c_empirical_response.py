"""Analyze the completed M19C K1 empirical response dataset."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from classify_m19c_risk_regions import DEFAULT_THRESHOLDS, classify_rows

INPUT_CSV = Path("data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv")
TRIAL_RECORD_CSV = Path("data/m19_repeated_validation_inputs/m19c_trial_records.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
NO_MOTION_THRESHOLD = 0.02


def parse_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def surface_from_trial_id(trial_id: str) -> str:
    parts = trial_id.split("_B", 1)[0].split("_", 1)
    return parts[1] if len(parts) > 1 else ""


def load_trial_surfaces(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        return {row.get("trial_id", ""): row.get("environment_id", "") for row in csv.DictReader(f)}


def read_measurements(path: Path, trial_records: Path = TRIAL_RECORD_CSV) -> list[dict[str, Any]]:
    trial_surfaces = load_trial_surfaces(trial_records)
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            trial_id = row.get("trial_id", "")
            surface_id = row.get("surface_id") or trial_surfaces.get(trial_id) or surface_from_trial_id(trial_id)
            command = parse_float(row.get("command_velocity"))
            actual = parse_float(row.get("measured_actual_velocity"))
            yaw = parse_float(row.get("yaw_drift_statistic"))
            if command is None or actual is None or yaw is None:
                raise ValueError(f"missing required measurement in {trial_id}")
            row["surface_id"] = surface_id
            row["command_velocity"] = command
            row["measured_actual_velocity"] = actual
            row["yaw_drift_statistic"] = yaw
            row["imu_yaw_drift_deg"] = parse_float(row.get("imu_yaw_drift_deg"))
            rows.append(row)
    return rows


def compute_cell_stats(rows: list[dict[str, Any]], no_motion_threshold: float = NO_MOTION_THRESHOLD) -> list[dict[str, Any]]:
    groups: dict[tuple[str, float], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["surface_id"], row["command_velocity"])].append(row)
    output = []
    for (surface_id, command), items in sorted(groups.items()):
        actuals = [row["measured_actual_velocity"] for row in items]
        yaws = [row["yaw_drift_statistic"] for row in items]
        imu_yaws = [row["imu_yaw_drift_deg"] for row in items if row.get("imu_yaw_drift_deg") is not None]
        errors = [actual - command for actual in actuals]
        under_ratios = [max(command - actual, 0.0) / command for actual in actuals]
        no_motion_ratio = sum(1 for actual in actuals if abs(actual) <= no_motion_threshold) / len(actuals)
        mean_actual = statistics.fmean(actuals)
        mean_error = statistics.fmean(errors)
        row = {
            "surface_id": surface_id,
            "command_velocity": command,
            "n": len(items),
            "mean_actual_velocity": mean_actual,
            "std_actual_velocity": statistics.stdev(actuals) if len(actuals) > 1 else 0.0,
            "median_actual_velocity": statistics.median(actuals),
            "min_actual_velocity": min(actuals),
            "max_actual_velocity": max(actuals),
            "mean_tracking_error": mean_error,
            "mean_abs_tracking_error": statistics.fmean(abs(error) for error in errors),
            "relative_tracking_error": mean_error / command,
            "under_tracking_ratio": statistics.fmean(under_ratios),
            "no_motion_ratio": no_motion_ratio,
            "mean_yaw_drift_deg": statistics.fmean(yaws),
            "std_yaw_drift_deg": statistics.stdev(yaws) if len(yaws) > 1 else 0.0,
            "max_yaw_drift_deg": max(yaws),
            "mean_imu_yaw_drift_deg": statistics.fmean(imu_yaws) if imu_yaws else "",
            "odom_imu_yaw_disagreement_deg": statistics.fmean(abs(row["yaw_drift_statistic"] - row["imu_yaw_drift_deg"]) for row in items if row.get("imu_yaw_drift_deg") is not None) if imu_yaws else "",
            "response_uncertainty": statistics.stdev(actuals) if len(actuals) > 1 else 0.0,
        }
        output.append(row)
    return output


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_gold_profile(rows: list[dict[str, Any]], classified: list[dict[str, Any]], dataset_id: str) -> dict[str, Any]:
    surfaces = sorted({row["surface_id"] for row in rows})
    speeds = sorted({row["command_velocity"] for row in rows})
    reliable_ranges = {}
    deadzone_ranges = {}
    drift_prone_ranges = {}
    for surface in surfaces:
        cells = [row for row in classified if row["surface_id"] == surface]
        reliable_ranges[surface] = [row["command_velocity"] for row in cells if row["region_label"] == "reliable"]
        deadzone_ranges[surface] = [row["command_velocity"] for row in cells if row["region_label"] == "deadzone"]
        drift_prone_ranges[surface] = [row["command_velocity"] for row in cells if row["region_label"] == "drift_prone"]
    return {
        "robot_id": "Booster_K1",
        "dataset_id": dataset_id,
        "surfaces": surfaces,
        "speeds": speeds,
        "per_surface_response_statistics": classified,
        "region_labels": {f"{row['surface_id']}@{row['command_velocity']}": row["region_label"] for row in classified},
        "recommended_reliable_ranges": reliable_ranges,
        "deadzone_ranges": deadzone_ranges,
        "drift_prone_ranges": drift_prone_ranges,
        "extraction_source": "ros2_odometer_state",
        "measurement_method": "analysis_window_forward_projection",
        "limitations": [
            "single K1 unit",
            "three tested surfaces",
            "odometer-based measurement",
            "no cross-robot generalization yet",
            "no compensation controller validated yet",
        ],
    }


def analyze(input_csv: Path = INPUT_CSV, trial_records: Path = TRIAL_RECORD_CSV, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    rows = read_measurements(input_csv, trial_records)
    stats = compute_cell_stats(rows)
    classified = classify_rows(stats, DEFAULT_THRESHOLDS)
    fields = list(stats[0].keys()) if stats else []
    write_csv(output_dir / "surface_response_statistics.csv", stats, fields)
    write_csv(output_dir / "region_classification.csv", classified, list(classified[0].keys()) if classified else [])
    write_csv(output_dir / "yaw_drift_summary.csv", classified, ["surface_id", "command_velocity", "n", "mean_yaw_drift_deg", "std_yaw_drift_deg", "max_yaw_drift_deg", "mean_imu_yaw_drift_deg", "odom_imu_yaw_disagreement_deg", "region_label"])
    dataset_id = "m19c_full_72_ros2_odometer_20260611"
    gold = build_gold_profile(rows, classified, dataset_id)
    (output_dir / "k1_gold_profile_v1.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
    (output_dir / "k1_gold_profile_v1.md").write_text(render_gold_profile(gold), encoding="utf-8")
    summary = {
        "timestamp": datetime.now().isoformat(),
        "dataset_id": dataset_id,
        "input_csv": str(input_csv),
        "rows_ingested": len(rows),
        "surface_speed_cells": len(stats),
        "complete_cells_n3": sum(1 for row in stats if row["n"] == 3),
        "surfaces": sorted({row["surface_id"] for row in rows}),
        "region_counts": dict(sorted({label: sum(1 for row in classified if row["region_label"] == label) for label in {row["region_label"] for row in classified}}.items())),
        "skill_integration_ready": len(rows) == 72 and len(stats) == 24 and all(row["n"] == 3 for row in stats),
        "cross_robot_generalization_claimed": False,
        "compensation_controller_validated": False,
        "navigation_improvement_claimed": False,
    }
    (output_dir / "m19c_empirical_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_empirical_report.md").write_text(render_report(summary, classified), encoding="utf-8")
    return summary


def render_gold_profile(gold: dict[str, Any]) -> str:
    return (
        "# Booster K1 Gold Profile v1\n\n"
        f"Dataset: `{gold['dataset_id']}`\n\n"
        f"Surfaces: {', '.join(gold['surfaces'])}\n\n"
        f"Speeds: {', '.join(str(speed) for speed in gold['speeds'])}\n\n"
        "This profile is a single-K1, odometer-measured calibration reference for skill development. It is not a cross-robot validation.\n"
    )


def render_report(summary: dict[str, Any], classified: list[dict[str, Any]]) -> str:
    top_risk = sorted(classified, key=lambda row: float(row["risk_score"]), reverse=True)[:5]
    lines = [
        "# M19C Empirical Response Report",
        "",
        f"Rows ingested: {summary['rows_ingested']}",
        f"Surface-speed cells: {summary['surface_speed_cells']}",
        f"Complete n=3 cells: {summary['complete_cells_n3']}",
        f"Skill integration ready: {summary['skill_integration_ready']}",
        "",
        "## Region Counts",
    ]
    for label, count in summary["region_counts"].items():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Highest Skill-Side Risk Scores"])
    for row in top_risk:
        lines.append(f"- {row['surface_id']} @ {row['command_velocity']}: {row['region_label']} (R={float(row['risk_score']):.3f})")
    lines.append("\nNo cross-robot generalization, compensation-controller validation, or navigation-improvement claim is made.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_CSV)
    parser.add_argument("--trial-records", type=Path, default=TRIAL_RECORD_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = analyze(args.input, args.trial_records, args.output_dir)
    print(f"M19C-E rows_ingested={summary['rows_ingested']}")
    print(f"M19C-E skill_integration_ready={summary['skill_integration_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
