"""Run or dry-run the full M19C ROS2 odometer measurement plan."""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path("data/m19c_ros2_odometer_logs")
TRIAL_RECORD_CSV = Path("data/m19_repeated_validation_inputs/m19c_trial_records.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
SURFACES = ["S1_lab_hard_floor", "S2_marble_floor", "S3_artificial_turf"]
SURFACE_TYPES = {
    "S1_lab_hard_floor": "lab_hard_floor",
    "S2_marble_floor": "marble_floor",
    "S3_artificial_turf": "artificial_turf",
}
BLOCK_SCHEDULE = [
    [0.10, 0.40, 0.20, 0.50, 0.30, 0.60, 0.35, 0.45],
    [0.50, 0.20, 0.45, 0.10, 0.60, 0.30, 0.40, 0.35],
    [0.30, 0.60, 0.10, 0.35, 0.50, 0.20, 0.45, 0.40],
]
IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0
LOG_FIELDS = [
    "trial_id",
    "timestamp_monotonic",
    "timestamp",
    "t_rel",
    "phase",
    "command_velocity",
    "odom_x",
    "odom_y",
    "odom_theta",
    "imu_roll",
    "imu_pitch",
    "imu_yaw",
    "source",
]
TRIAL_RECORD_FIELDS = [
    "trial_id",
    "session_id",
    "robot_id",
    "environment_id",
    "surface_type",
    "command_velocity",
    "block_index",
    "repeat_index",
    "idle_sec",
    "command_sec",
    "stop_sec",
    "state_log_path",
    "valid",
    "invalid_reason",
    "timestamp",
    "notes",
]


def speed_code(speed: float) -> str:
    return f"U{int(round(speed * 100)):03d}"


def trial_id(surface_id: str, block_index: int, speed: float, repeat_index: int) -> str:
    return f"M19C_{surface_id}_B{block_index}_{speed_code(speed)}_R{repeat_index}"


def generate_trial_plan(surface: str | None = None) -> list[dict[str, Any]]:
    surfaces = [surface] if surface else SURFACES
    plan = []
    for surface_id in surfaces:
        if surface_id not in SURFACES:
            raise ValueError(f"unknown surface: {surface_id}")
        for block_idx, speeds in enumerate(BLOCK_SCHEDULE, start=1):
            for speed in speeds:
                repeat_idx = block_idx
                tid = trial_id(surface_id, block_idx, speed, repeat_idx)
                plan.append(
                    {
                        "trial_id": tid,
                        "surface_id": surface_id,
                        "surface_type": SURFACE_TYPES[surface_id],
                        "command_velocity": speed,
                        "block_index": block_idx,
                        "repeat_index": repeat_idx,
                        "state_log_path": str(LOG_DIR / f"{tid}.csv"),
                    }
                )
    return plan


def phase_at(t_rel: float) -> str:
    if t_rel < IDLE_SEC:
        return "idle"
    if t_rel < IDLE_SEC + COMMAND_SEC:
        return "command"
    return "stop"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def record_for_trial(trial: dict[str, Any], session_id: str, valid: str, invalid_reason: str = "", notes: str = "") -> dict[str, Any]:
    return {
        "trial_id": trial["trial_id"],
        "session_id": session_id,
        "robot_id": "K1_001",
        "environment_id": trial["surface_id"],
        "surface_type": trial["surface_type"],
        "command_velocity": trial["command_velocity"],
        "block_index": trial["block_index"],
        "repeat_index": trial["repeat_index"],
        "idle_sec": IDLE_SEC,
        "command_sec": COMMAND_SEC,
        "stop_sec": STOP_SEC,
        "state_log_path": trial["state_log_path"],
        "valid": valid,
        "invalid_reason": invalid_reason,
        "timestamp": datetime.now().isoformat(),
        "notes": notes,
    }


def run_trial_execute(trial: dict[str, Any], interface: str, include_low_state: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import rclpy  # type: ignore
    from booster_interface.msg import LowState, Odometer  # type: ignore
    from booster_robotics_sdk_python import B1LocoClient, ChannelFactory, RobotMode  # type: ignore

    rows: list[dict[str, Any]] = []
    latest_low = {"roll": "", "pitch": "", "yaw": ""}
    t0 = time.monotonic()

    def odom_callback(msg: Any) -> None:
        now = time.monotonic()
        rows.append(
            {
                "trial_id": trial["trial_id"],
                "timestamp_monotonic": now,
                "timestamp": datetime.now().isoformat(),
                "t_rel": now - t0,
                "phase": phase_at(now - t0),
                "command_velocity": trial["command_velocity"],
                "odom_x": getattr(msg, "x", ""),
                "odom_y": getattr(msg, "y", ""),
                "odom_theta": getattr(msg, "theta", ""),
                "imu_roll": latest_low["roll"],
                "imu_pitch": latest_low["pitch"],
                "imu_yaw": latest_low["yaw"],
                "source": "/odometer_state",
            }
        )

    def low_callback(msg: Any) -> None:
        imu_state = getattr(msg, "imu_state", None)
        rpy = getattr(imu_state, "rpy", None)
        if rpy is not None and len(rpy) >= 3:
            latest_low["roll"] = rpy[0]
            latest_low["pitch"] = rpy[1]
            latest_low["yaw"] = rpy[2]

    rclpy.init(args=None)
    node = rclpy.create_node("m19c_ros2_odometer_trial_logger")
    node.create_subscription(Odometer, "/odometer_state", odom_callback, 10)
    if include_low_state:
        node.create_subscription(LowState, "/low_state", low_callback, 10)

    ChannelFactory.Instance().Init(0, interface)
    client = B1LocoClient()
    client.Init()
    try:
        client.ChangeMode(RobotMode.kPrepare)
        time.sleep(3.0)
        client.ChangeMode(RobotMode.kWalking)
        time.sleep(2.0)
        t0 = time.monotonic()
        spin_until(node, IDLE_SEC)
        client.Move(float(trial["command_velocity"]), 0, 0)
        spin_until(node, COMMAND_SEC)
        client.Move(0, 0, 0)
        spin_until(node, STOP_SEC)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    write_csv(Path(trial["state_log_path"]), rows, LOG_FIELDS)
    return record_for_trial(trial, "", "TRUE", notes="executed_m19c_ros2_odometer_trial"), rows


def spin_until(node: Any, duration: float) -> None:
    import rclpy  # type: ignore

    end = time.monotonic() + duration
    while time.monotonic() < end:
        rclpy.spin_once(node, timeout_sec=0.02)


def write_run_summary(plan: list[dict[str, Any]], execute: bool, output_dir: Path, status: str, surface: str | None) -> dict[str, Any]:
    summary = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "execute_requested": execute,
        "surface": surface or "all",
        "planned_trials": len(plan),
        "full_protocol_trial_count": len(SURFACES) * len(BLOCK_SCHEDULE) * len(BLOCK_SCHEDULE[0]),
        "state_log_dir": str(LOG_DIR),
        "trial_record_csv": str(TRIAL_RECORD_CSV),
        "empirical_analysis_computed": False,
        "response_model_validation_claimed": False,
        "risk_map_validation_claimed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19c_measurement_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report = (
        "# M19C ROS2 Odometer Measurement Run\n\n"
        f"Status: `{status}`\n\n"
        f"Execute requested: {execute}\n\n"
        f"Surface: `{summary['surface']}`\n\n"
        f"Planned trials in this invocation: {len(plan)}\n\n"
        "No empirical response analysis, response curves, or risk-map validation are produced by this runner.\n"
    )
    (output_dir / "m19c_measurement_run_report.md").write_text(report, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=SURFACES)
    parser.add_argument("--interface", default="lo")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-low-state", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    plan = generate_trial_plan(args.surface)
    session_id = f"M19C_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if not args.execute:
        for trial in plan:
            print(f"DRY RUN {trial['trial_id']} vx={trial['command_velocity']:.2f} log={trial['state_log_path']}")
        write_run_summary(plan, False, args.output_dir, "pending_full_m19c_measurement_run", args.surface)
        return 0

    records = []
    for trial in plan:
        try:
            record, _rows = run_trial_execute(trial, args.interface, not args.no_low_state)
            record["session_id"] = session_id
            records.append(record)
        except Exception as exc:
            records.append(record_for_trial(trial, session_id, "FALSE", invalid_reason=repr(exc), notes="execution_error"))
    write_csv(TRIAL_RECORD_CSV, records, TRIAL_RECORD_FIELDS)
    write_run_summary(plan, True, args.output_dir, "m19c_measurement_logs_recorded_pending_extraction", args.surface)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
