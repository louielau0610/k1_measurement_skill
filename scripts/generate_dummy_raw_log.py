"""Generate a deterministic dummy raw measurement log.

This script does not use ROS2 and does not send robot commands.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


DEFAULT_OUTPUT = Path("data/raw/dummy_forward_baseline.csv")
DUMMY_NOTE = "Dummy data only. Not collected from a real K1 robot."
FIELDNAMES = [
    "timestamp",
    "trial_id",
    "vx_cmd",
    "vy_cmd",
    "wz_cmd",
    "command_phase",
    "odom_x",
    "odom_y",
    "odom_yaw",
    "odom_vx",
    "odom_vy",
    "odom_wz",
    "imu_acc_x",
    "imu_acc_y",
    "imu_acc_z",
    "imu_gyro_x",
    "imu_gyro_y",
    "imu_gyro_z",
    "battery_level",
    "robot_mode",
    "floor_type",
    "condition",
    "slope",
    "operator_note",
]


def _phase_for_time(t_sec: float) -> str:
    if t_sec < 1.0:
        return "baseline"
    if t_sec < 7.0:
        return "command"
    return "stop"


def _format_row(row: dict[str, object]) -> dict[str, object]:
    formatted: dict[str, object] = {}
    for key, value in row.items():
        if isinstance(value, float):
            formatted[key] = f"{value:.6f}"
        else:
            formatted[key] = value
    return formatted


def generate_dummy_raw_log(output_path: str | Path = DEFAULT_OUTPUT, seed: int = 7) -> Path:
    """Generate a reproducible dummy forward baseline CSV."""

    rng = random.Random(seed)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    dt = 0.1
    samples_per_trial = int(9.0 / dt) + 1
    trial_index = 0

    for vx_cmd in [0.1, 0.2, 0.3, 0.4]:
        for repeat in range(1, 6):
            trial_index += 1
            trial_id = f"dummy_vx_{vx_cmd:.1f}_trial_{repeat}"
            odom_x = 0.0
            odom_y = 0.0
            odom_yaw = 0.0
            actual_base = 0.8 * vx_cmd

            for sample_index in range(samples_per_trial):
                timestamp = round(sample_index * dt, 6)
                phase = _phase_for_time(timestamp)
                if phase == "command":
                    odom_vx = max(0.0, actual_base + rng.uniform(-0.01, 0.01))
                    odom_vy = rng.uniform(-0.002, 0.002)
                    odom_wz = rng.uniform(-0.003, 0.003)
                else:
                    odom_vx = 0.0
                    odom_vy = 0.0
                    odom_wz = 0.0

                odom_x += odom_vx * dt
                odom_y += odom_vy * dt
                odom_yaw += odom_wz * dt

                rows.append(
                    _format_row(
                        {
                            "timestamp": timestamp,
                            "trial_id": trial_id,
                            "vx_cmd": vx_cmd,
                            "vy_cmd": 0.0,
                            "wz_cmd": 0.0,
                            "command_phase": phase,
                            "odom_x": odom_x,
                            "odom_y": odom_y,
                            "odom_yaw": odom_yaw,
                            "odom_vx": odom_vx,
                            "odom_vy": odom_vy,
                            "odom_wz": odom_wz,
                            "imu_acc_x": 0.0,
                            "imu_acc_y": 0.0,
                            "imu_acc_z": 9.81,
                            "imu_gyro_x": 0.0,
                            "imu_gyro_y": 0.0,
                            "imu_gyro_z": odom_wz,
                            "battery_level": 0.92 - trial_index * 0.001,
                            "robot_mode": "dummy_measurement",
                            "floor_type": "tile",
                            "condition": "dry",
                            "slope": "flat",
                            "operator_note": DUMMY_NOTE,
                        }
                    )
                )

    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a dummy K1 raw measurement log.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output CSV path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = generate_dummy_raw_log(args.output)
    print(f"Dummy raw log generated: {output}")
    print("Dummy data only. Not collected from a real K1 robot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
