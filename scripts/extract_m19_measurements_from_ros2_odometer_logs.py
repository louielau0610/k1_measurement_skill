"""Extract M19 measurements from ROS2 /odometer_state logs."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/m19c_ros2_odometer_logs")
OUTPUT_CSV = Path("data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
WINDOW_START_SEC = 3.0
WINDOW_END_SEC = 8.0

OUTPUT_FIELDS = [
    "trial_id",
    "measurement_source",
    "measurement_method",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "extraction_status",
    "start_x",
    "start_y",
    "end_x",
    "end_y",
    "start_theta",
    "end_theta",
    "distance_m",
    "time_sec",
    "measured_actual_velocity",
    "start_yaw_deg",
    "end_yaw_deg",
    "yaw_drift_statistic",
    "imu_yaw_drift_deg",
    "measurement_confidence",
    "annotation_notes",
]


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def wrap_to_pi(angle_rad: float) -> float:
    return (angle_rad + math.pi) % (2.0 * math.pi) - math.pi


def forward_displacement_m(start: dict[str, float], end: dict[str, float]) -> float:
    dx = end["x"] - start["x"]
    dy = end["y"] - start["y"]
    theta = start["theta"]
    return dx * math.cos(theta) + dy * math.sin(theta)


def select_window(samples: list[dict[str, str]], start_sec: float, end_sec: float) -> list[dict[str, str]]:
    selected = []
    for row in samples:
        t_rel = parse_float(row.get("t_rel"))
        if t_rel is not None and start_sec <= t_rel <= end_sec:
            selected.append(row)
    selected.sort(key=lambda row: parse_float(row.get("t_rel")) or 0.0)
    return selected


def extract_trial_measurement(
    samples: list[dict[str, str]],
    start_sec: float = WINDOW_START_SEC,
    end_sec: float = WINDOW_END_SEC,
) -> tuple[dict[str, Any] | None, str | None]:
    usable = []
    for row in select_window(samples, start_sec, end_sec):
        t_rel = parse_float(row.get("t_rel"))
        x = parse_float(row.get("odom_x", row.get("x")))
        y = parse_float(row.get("odom_y", row.get("y")))
        theta = parse_float(row.get("odom_theta", row.get("theta")))
        imu_yaw = parse_float(row.get("imu_yaw"))
        if t_rel is None or x is None or y is None or theta is None:
            continue
        usable.append({"t_rel": t_rel, "x": x, "y": y, "theta": theta, "imu_yaw": imu_yaw})
    if len(usable) < 2:
        return None, "insufficient_odometer_samples"
    start = usable[0]
    end = usable[-1]
    time_sec = end["t_rel"] - start["t_rel"]
    if time_sec <= 0:
        return None, "nonpositive_analysis_window_duration"
    distance = forward_displacement_m(start, end)
    yaw_drift_deg = abs(math.degrees(wrap_to_pi(end["theta"] - start["theta"])))
    imu_yaw_drift = None
    if start.get("imu_yaw") is not None and end.get("imu_yaw") is not None:
        imu_yaw_drift = abs(math.degrees(wrap_to_pi(end["imu_yaw"] - start["imu_yaw"])))
    return {
        "analysis_window_start_sec": start_sec,
        "analysis_window_end_sec": end_sec,
        "extraction_status": "ok",
        "start_x": start["x"],
        "start_y": start["y"],
        "end_x": end["x"],
        "end_y": end["y"],
        "start_theta": start["theta"],
        "end_theta": end["theta"],
        "distance_m": distance,
        "time_sec": time_sec,
        "measured_actual_velocity": distance / time_sec,
        "start_yaw_deg": math.degrees(start["theta"]),
        "end_yaw_deg": math.degrees(end["theta"]),
        "yaw_drift_statistic": yaw_drift_deg,
        "imu_yaw_drift_deg": imu_yaw_drift,
    }, None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def discover_log_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.glob("*.csv"))


def extract_from_logs(input_path: Path, output_csv: Path = OUTPUT_CSV, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    log_files = discover_log_files(input_path)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in log_files:
        for row in read_csv(path):
            trial_id = row.get("trial_id") or path.stem
            row["trial_id"] = trial_id
            grouped[trial_id].append(row)

    output_rows = []
    blocked_trials = []
    for trial_id in sorted(grouped):
        measurement, reason = extract_trial_measurement(grouped[trial_id])
        if measurement is None:
            blocked_trials.append({"trial_id": trial_id, "reason": reason})
            continue
        output_rows.append(
            {
                "trial_id": trial_id,
                "measurement_source": "ros2_odometer_state",
                "measurement_method": "odometer_forward_projection_window_3_8s",
                "measurement_confidence": "high",
                "annotation_notes": "extracted_from_ros2_odometer_state",
                **measurement,
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    ready = bool(output_rows) and any(abs(float(row["measured_actual_velocity"])) > 1e-6 for row in output_rows)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "input_path": str(input_path),
        "log_files_found": len(log_files),
        "trials_seen": len(grouped),
        "measurements_extracted": len(output_rows),
        "blocked_trials": blocked_trials,
        "output_csv": str(output_csv),
        "odometer_source": "/odometer_state",
        "position_available": bool(output_rows),
        "yaw_available": bool(output_rows),
        "nonzero_velocity_detected": ready,
        "full_m19c_measurement_run_ready": ready,
        "statistics_computed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19c_ros2_odometer_smoke_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_ros2_odometer_smoke_report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def render_report(summary: dict[str, Any]) -> str:
    return (
        "# M19C ROS2 Odometer Smoke Extraction Report\n\n"
        f"Odometer source: `{summary['odometer_source']}`\n\n"
        f"Log files found: {summary['log_files_found']}\n\n"
        f"Trials seen: {summary['trials_seen']}\n\n"
        f"Measurements extracted: {summary['measurements_extracted']}\n\n"
        f"Position available: {summary['position_available']}\n\n"
        f"Yaw available: {summary['yaw_available']}\n\n"
        f"Nonzero velocity detected: {summary['nonzero_velocity_detected']}\n\n"
        f"Full M19C measurement run ready: {summary['full_m19c_measurement_run_ready']}\n\n"
        "No full empirical M19 analysis or response curves are generated by this smoke extractor.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = extract_from_logs(args.input, args.output_csv, args.output_dir)
    print(f"ROS2 odometer measurements_extracted={summary['measurements_extracted']}")
    print(f"Full M19C measurement run ready={summary['full_m19c_measurement_run_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
