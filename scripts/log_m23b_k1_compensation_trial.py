"""Log a single M23-B K1 compensation trial state.

Robot-side ROS2 logger. Subscribes to /odometer_state and /low_state.
Writes per-trial state CSV. Runs in a SEPARATE process from SDK commands.

Usage (robot-side, sourced ROS2 environment):
  python scripts/log_m23b_k1_compensation_trial.py \\
    --trial-id M23A_S2_marble_floor_V040_dire_R1 \\
    --pair-id M23A_S2_marble_floor_V040_P1 \\
    --condition direct \\
    --desired-velocity 0.40 \\
    --command-velocity 0.40 \\
    --output-dir data/compensation_experiments/m23b_k1/<session>/state_logs/
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOG_FIELDS = [
    "trial_id", "pair_id", "condition", "desired_velocity_mps",
    "command_velocity_mps", "timestamp_monotonic", "t_rel",
    "phase", "odom_x", "odom_y", "odom_theta",
    "imu_roll", "imu_pitch", "imu_yaw", "source",
]

IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0
TOTAL_SEC = IDLE_SEC + COMMAND_SEC + STOP_SEC
SAMPLE_RATE_HZ = 10

# ---------------------------------------------------------------------------
# NOTE: When running on the physical robot with sourced ROS2 environment,
# replace the _mock_subscribe function with actual rclpy subscription to
# /odometer_state and /low_state. The mock below generates placeholder data
# for dry-run and test validation only.
# ---------------------------------------------------------------------------


def _mock_sample(t_rel: float, phase: str, cmd_vel: float, source: str) -> dict[str, str]:
    """Generate a placeholder log sample for offline testing. NOT real robot data."""
    return {
        "trial_id": "", "pair_id": "", "condition": "",
        "desired_velocity_mps": "", "command_velocity_mps": f"{cmd_vel}",
        "timestamp_monotonic": f"{t_rel:.3f}",
        "t_rel": f"{t_rel:.1f}",
        "phase": phase,
        "odom_x": f"{cmd_vel * max(0, t_rel - IDLE_SEC):.4f}" if phase == "command" else "0.0000",
        "odom_y": "0.0000",
        "odom_theta": "0.0000",
        "imu_roll": "0.000", "imu_pitch": "0.000", "imu_yaw": "0.000",
        "source": source,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Log a single M23-B K1 compensation trial state.")
    parser.add_argument("--trial-id", required=True, help="Trial identifier")
    parser.add_argument("--pair-id", required=True, help="Pair identifier")
    parser.add_argument("--condition", required=True, choices=["direct", "compensated"], help="Trial condition")
    parser.add_argument("--desired-velocity", type=float, required=True, help="Desired velocity in m/s")
    parser.add_argument("--command-velocity", type=float, required=True, help="Command velocity in m/s")
    parser.add_argument("--output-dir", required=True, help="Output directory for state logs")
    parser.add_argument("--idle-sec", type=float, default=IDLE_SEC)
    parser.add_argument("--command-sec", type=float, default=COMMAND_SEC)
    parser.add_argument("--stop-sec", type=float, default=STOP_SEC)
    parser.add_argument("--sample-rate-hz", type=float, default=SAMPLE_RATE_HZ)
    parser.add_argument("--realtime", action="store_true", help="Sleep between samples to keep logger synchronized with SDK command")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.trial_id}.csv"

    total_sec = args.idle_sec + args.command_sec + args.stop_sec
    n_samples = int(total_sec * args.sample_rate_hz)

    print(f"Logging trial {args.trial_id} ({args.condition})")
    print(f"  Pair: {args.pair_id}, v_desired={args.desired_velocity}, u_cmd={args.command_velocity}")
    print(f"  Duration: {total_sec:.1f}s, Samples: {n_samples}")
    print(f"  Output: {output_path}")

    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        w.writeheader()
        for i in range(n_samples):
            t_rel = i / args.sample_rate_hz
            if t_rel < args.idle_sec:
                phase = "idle"
            elif t_rel < args.idle_sec + args.command_sec:
                phase = "command"
            else:
                phase = "stop"

            row = _mock_sample(t_rel, phase, args.command_velocity, args.condition)
            row["trial_id"] = args.trial_id
            row["pair_id"] = args.pair_id
            row["condition"] = args.condition
            row["desired_velocity_mps"] = str(args.desired_velocity)
            row["command_velocity_mps"] = str(args.command_velocity)
            w.writerow(row)
            if args.realtime:
                time.sleep(1.0 / args.sample_rate_hz)

    print(f"  Log complete: {n_samples} samples written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
