"""Log one M24-B direct-refresh trial state CSV from ROS2 odometer state.

Robot-side ROS2 logger wrapper. This script is intentionally separate from
the Booster SDK sender process and does not import Booster SDK modules.

Robot shell requirement:
source /opt/booster/BoosterRos2Interface/install/setup.bash
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Any


LOG_FIELDS = [
    "trial_id",
    "refresh_group_id",
    "condition",
    "desired_velocity_mps",
    "command_velocity_mps",
    "timestamp_monotonic",
    "t_rel",
    "phase",
    "odom_x",
    "odom_y",
    "odom_theta",
    "imu_roll",
    "imu_pitch",
    "imu_yaw",
    "source",
]

IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0
SAMPLE_RATE_HZ = 10.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Log one M24-B S2 profile refresh trial.")
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--refresh-group-id", required=True)
    parser.add_argument("--condition", required=True, choices=["direct_refresh"])
    parser.add_argument("--desired-velocity", type=float, required=True)
    parser.add_argument("--command-velocity", type=float, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--idle-sec", type=float, default=IDLE_SEC)
    parser.add_argument("--command-sec", type=float, default=COMMAND_SEC)
    parser.add_argument("--stop-sec", type=float, default=STOP_SEC)
    parser.add_argument("--sample-rate-hz", type=float, default=SAMPLE_RATE_HZ)
    parser.add_argument("--realtime", action="store_true", help="Use wall-clock timing; default for robot-side runs")
    parser.add_argument("--mock", action="store_true", help="Write deterministic fixture samples without ROS2")
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / f"{args.trial_id}.csv"
    total_sec = args.idle_sec + args.command_sec + args.stop_sec
    if args.mock:
        rows = build_mock_rows(args, total_sec)
        write_rows(output_path, rows)
        print(f"M24-B mock state log written: {output_path}")
        return 0

    try:
        rows = collect_ros2_rows(args, total_sec)
    except Exception as exc:
        print(f"ERROR: ROS2 odometer logging failed: {exc!r}")
        write_rows(output_path, [])
        return 1

    write_rows(output_path, rows)
    print(f"M24-B ROS2 state log written: {output_path} ({len(rows)} samples)")
    return 0 if rows else 1


def build_mock_rows(args: argparse.Namespace, total_sec: float) -> list[dict[str, str]]:
    sample_count = int(total_sec * args.sample_rate_hz)
    rows: list[dict[str, str]] = []
    for index in range(sample_count):
        t_rel = index / args.sample_rate_hz
        rows.append(build_row(args, t_rel, mock_pose(args, t_rel), "m24b_mock_fixture"))
    return rows


def collect_ros2_rows(args: argparse.Namespace, total_sec: float) -> list[dict[str, str]]:
    try:
        import rclpy  # type: ignore
        from booster_interface.msg import LowState, Odometer  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "ROS2 imports unavailable; source /opt/booster/BoosterRos2Interface/install/setup.bash"
        ) from exc

    rows: list[dict[str, str]] = []
    latest_low_yaw: float | None = None
    latest_odom: Any | None = None
    t0 = time.time()

    def low_callback(msg: Any) -> None:
        nonlocal latest_low_yaw
        imu_state = getattr(msg, "imu_state", None)
        rpy = getattr(imu_state, "rpy", None)
        if rpy is not None and len(rpy) >= 3:
            latest_low_yaw = float(rpy[2])

    def odom_callback(msg: Any) -> None:
        nonlocal latest_odom
        latest_odom = msg

    rclpy.init(args=None)
    node = rclpy.create_node("m24b_s2_profile_refresh_logger")
    node.create_subscription(Odometer, "/odometer_state", odom_callback, 10)
    node.create_subscription(LowState, "/low_state", low_callback, 10)
    try:
        while time.time() - t0 < total_sec:
            rclpy.spin_once(node, timeout_sec=0.1)
            t_rel = time.time() - t0
            if latest_odom is None:
                continue
            pose = {
                "odom_x": getattr(latest_odom, "x", ""),
                "odom_y": getattr(latest_odom, "y", ""),
                "odom_theta": getattr(latest_odom, "theta", ""),
                "imu_yaw": "" if latest_low_yaw is None else latest_low_yaw,
            }
            rows.append(build_row(args, t_rel, pose, "ros2_odometer_state"))
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return rows


def mock_pose(args: argparse.Namespace, t_rel: float) -> dict[str, float]:
    if t_rel < args.idle_sec:
        x = 0.0
    elif t_rel < args.idle_sec + args.command_sec:
        x = args.command_velocity * (t_rel - args.idle_sec)
    else:
        x = args.command_velocity * args.command_sec
    return {"odom_x": x, "odom_y": 0.0, "odom_theta": 0.0, "imu_yaw": 0.0}


def build_row(args: argparse.Namespace, t_rel: float, pose: dict[str, Any], source: str) -> dict[str, str]:
    if t_rel < args.idle_sec:
        phase = "idle"
    elif t_rel < args.idle_sec + args.command_sec:
        phase = "command"
    else:
        phase = "stop"
    return {
        "trial_id": args.trial_id,
        "refresh_group_id": args.refresh_group_id,
        "condition": args.condition,
        "desired_velocity_mps": f"{args.desired_velocity:.3f}",
        "command_velocity_mps": f"{args.command_velocity:.3f}",
        "timestamp_monotonic": f"{time.monotonic():.6f}",
        "t_rel": f"{t_rel:.3f}",
        "phase": phase,
        "odom_x": _format_pose(pose.get("odom_x")),
        "odom_y": _format_pose(pose.get("odom_y")),
        "odom_theta": _format_pose(pose.get("odom_theta")),
        "imu_roll": "",
        "imu_pitch": "",
        "imu_yaw": _format_pose(pose.get("imu_yaw")),
        "source": source,
    }


def _format_pose(value: Any) -> str:
    if value == "" or value is None:
        return ""
    return f"{float(value):.6f}"


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
