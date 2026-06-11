"""Run guarded M19C ROS2 odometer smoke trials with the known SDK command path."""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from log_k1_ros2_odometer_state import FIELDS, write_rows

OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
DATA_DIR = Path("data/m19_ros2_state_smoke/trials")
TRIALS = [
    ("M19C_SMOKE_S1_lab_hard_floor_U020_R1", 0.20),
    ("M19C_SMOKE_S1_lab_hard_floor_U040_R1", 0.40),
    ("M19C_SMOKE_S1_lab_hard_floor_U060_R1", 0.60),
]


def run_trials(execute: bool, output_dir: Path, data_dir: Path) -> dict[str, Any]:
    trials = []
    if not execute:
        for trial_id, vx in TRIALS:
            trials.append({"trial_id": trial_id, "vx": vx, "executed": False, "output_csv": ""})
        return write_summary(output_dir, trials, execute, "dry_run")

    try:
        import rclpy  # type: ignore
        from booster_interface.msg import Odometer  # type: ignore
        from booster_robotics_sdk_python import B1LocoClient, ChannelFactory, RobotMode  # type: ignore
    except Exception as exc:
        for trial_id, vx in TRIALS:
            trials.append({"trial_id": trial_id, "vx": vx, "executed": False, "output_csv": "", "error": repr(exc)})
        return write_summary(output_dir, trials, execute, "import_failed")

    ChannelFactory.Instance().Init(0, "lo")
    client = B1LocoClient()
    client.Init()
    data_dir.mkdir(parents=True, exist_ok=True)

    rclpy.init(args=None)
    node = rclpy.create_node("m19c_ros2_odometer_smoke_trials")
    rows: list[dict[str, Any]] = []
    active_trial = {"trial_id": "", "t0": time.time()}

    def odom_callback(msg: Any) -> None:
        rows.append(
            {
                "trial_id": active_trial["trial_id"],
                "timestamp": datetime.now().isoformat(),
                "t_rel": time.time() - active_trial["t0"],
                "x": getattr(msg, "x", ""),
                "y": getattr(msg, "y", ""),
                "theta": getattr(msg, "theta", ""),
                "source_status": "odometer_state",
            }
        )

    node.create_subscription(Odometer, "/odometer_state", odom_callback, 10)
    try:
        for trial_id, vx in TRIALS:
            rows.clear()
            active_trial["trial_id"] = trial_id
            active_trial["t0"] = time.time()
            client.ChangeMode(RobotMode.kPrepare)
            spin_for(node, 2.0)
            client.ChangeMode(RobotMode.kWalking)
            spin_for(node, 2.0)
            client.Move(vx, 0, 0)
            spin_for(node, 6.0)
            client.Move(0, 0, 0)
            spin_for(node, 2.0)
            path = data_dir / f"{trial_id}.csv"
            write_rows(path, rows)
            trials.append({"trial_id": trial_id, "vx": vx, "executed": True, "output_csv": str(path), "samples": len(rows)})
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return write_summary(output_dir, trials, execute, "ok")


def spin_for(node: Any, duration: float) -> None:
    import rclpy  # type: ignore

    end = time.time() + duration
    while time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.05)


def write_summary(output_dir: Path, trials: list[dict[str, Any]], execute: bool, status: str) -> dict[str, Any]:
    summary = {
        "timestamp": datetime.now().isoformat(),
        "source_requirement": "source /opt/booster/BoosterRos2Interface/install/setup.bash",
        "primary_topic": "/odometer_state",
        "execute_requested": execute,
        "status": status,
        "trials": trials,
        "dynamic_smoke_trials_run": any(item.get("executed") for item in trials),
        "full_72_trial_protocol_run": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19c_ros2_odometer_smoke_trials_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_ros2_odometer_smoke_trials_report.md").write_text(
        "# M19C ROS2 Odometer Smoke Trials\n\n"
        f"Execute requested: {execute}\n\n"
        f"Dynamic smoke trials run: {summary['dynamic_smoke_trials_run']}\n\n"
        "Only three ROS2 odometer smoke trials are supported here; the full 72-trial protocol is not run.\n",
        encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args(argv)
    summary = run_trials(args.execute, args.output_dir, args.data_dir)
    print(f"ROS2 odometer dynamic smoke trials run={summary['dynamic_smoke_trials_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
