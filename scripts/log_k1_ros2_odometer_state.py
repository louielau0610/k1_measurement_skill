"""Log ROS2 /odometer_state samples for M19C measurement-source smoke tests.

Robot shell requirement:
source /opt/booster/BoosterRos2Interface/install/setup.bash
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Any

OUTPUT_CSV = Path("data/m19_ros2_state_smoke/standing_odometer_state.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
FIELDS = [
    "trial_id",
    "timestamp",
    "t_rel",
    "x",
    "y",
    "theta",
    "low_state_yaw",
    "imu_yaw",
    "source_status",
]


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def log_odometer_state(duration: float, output: Path, output_dir: Path, trial_id: str, include_low_state: bool = True) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    status = "not_started"
    try:
        import rclpy  # type: ignore
        from booster_interface.msg import LowState, Odometer  # type: ignore
    except Exception as exc:
        status = f"ros2_import_unavailable:{exc!r}"
        write_rows(output, rows)
        return write_summary(output_dir, output, rows, status, duration, include_low_state)

    latest_low_yaw: float | None = None

    def odom_callback(msg: Any) -> None:
        now = time.time()
        rows.append(
            {
                "trial_id": trial_id,
                "timestamp": datetime.now().isoformat(),
                "t_rel": now - t0,
                "x": getattr(msg, "x", ""),
                "y": getattr(msg, "y", ""),
                "theta": getattr(msg, "theta", ""),
                "low_state_yaw": "" if latest_low_yaw is None else latest_low_yaw,
                "imu_yaw": "",
                "source_status": "odometer_state",
            }
        )

    def low_callback(msg: Any) -> None:
        nonlocal latest_low_yaw
        imu_state = getattr(msg, "imu_state", None)
        rpy = getattr(imu_state, "rpy", None)
        if rpy is not None and len(rpy) >= 3:
            latest_low_yaw = float(rpy[2])

    rclpy.init(args=None)
    node = rclpy.create_node("m19c_odometer_state_logger")
    node.create_subscription(Odometer, "/odometer_state", odom_callback, 10)
    if include_low_state:
        node.create_subscription(LowState, "/low_state", low_callback, 10)
    t0 = time.time()
    try:
        while time.time() - t0 < duration:
            rclpy.spin_once(node, timeout_sec=0.1)
        status = "ok"
    finally:
        node.destroy_node()
        rclpy.shutdown()
    write_rows(output, rows)
    return write_summary(output_dir, output, rows, status, duration, include_low_state)


def write_summary(output_dir: Path, output: Path, rows: list[dict[str, Any]], status: str, duration: float, include_low_state: bool) -> dict[str, Any]:
    frequency = len(rows) / duration if duration > 0 else 0.0
    position_available = any(str(row.get("x", "")).strip() and str(row.get("y", "")).strip() for row in rows)
    yaw_available = any(str(row.get("theta", "")).strip() for row in rows)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "source_requirement": "source /opt/booster/BoosterRos2Interface/install/setup.bash",
        "primary_topic": "/odometer_state",
        "secondary_topic": "/low_state",
        "duration": duration,
        "include_low_state": include_low_state,
        "samples_written": len(rows),
        "estimated_frequency_hz": frequency,
        "position_available": position_available,
        "yaw_available": yaw_available,
        "source_status": status,
        "output_csv": str(output),
        "full_m19c_measurement_run_ready": frequency >= 5.0 and position_available and yaw_available,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ros2_odometer_state_smoke_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report = (
        "# ROS2 Odometer State Smoke Logger Report\n\n"
        f"Primary topic: `{summary['primary_topic']}`\n\n"
        f"Samples written: {summary['samples_written']}\n\n"
        f"Estimated frequency Hz: {summary['estimated_frequency_hz']:.3f}\n\n"
        f"Position available: {summary['position_available']}\n\n"
        f"Yaw available: {summary['yaw_available']}\n\n"
        f"Full M19C measurement run ready: {summary['full_m19c_measurement_run_ready']}\n\n"
        f"Source status: `{summary['source_status']}`\n"
    )
    (output_dir / "ros2_odometer_state_smoke_report.md").write_text(report, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--trial-id", default="M19C_STANDING_ODOMETER_SMOKE")
    parser.add_argument("--no-low-state", action="store_true")
    args = parser.parse_args(argv)
    summary = log_odometer_state(args.duration, args.output, args.output_dir, args.trial_id, not args.no_low_state)
    print(f"ROS2 odometer samples_written={summary['samples_written']}")
    print(f"Full M19C measurement run ready={summary['full_m19c_measurement_run_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
