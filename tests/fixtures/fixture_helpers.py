"""Test fixture data for Booster K1 measurement module tests.

This is synthetic test data ONLY. Do NOT export as empirical robot results.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent


def build_fixture_session_dir(base_dir: Path) -> Path:
    """Create a minimal fixture session directory for testing.

    Creates:
      session_metadata.json
      trial_plan.csv
      trial_records.csv
      state_logs/<trial>.csv
    """
    import json

    session_dir = base_dir / "fixture_k1_session"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "state_logs").mkdir(parents=True, exist_ok=True)

    # session_metadata.json
    metadata = {
        "session_id": "fixture_k1_session",
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "robot_id": "Booster_K1",
        "surface": "S1_lab_hard_floor",
        "speeds": [0.2, 0.4, 0.6],
        "repeats": 2,
        "block_order": "randomized_by_trial_scheduler",
        "timing": {"idle_sec": 2.0, "command_sec": 6.0, "stop_sec": 2.0},
        "command_source": "booster_sdk_kPrepare_kWalking_Move",
        "state_sources": ["/odometer_state"],
        "measurement_source": "ros2_odometer_state",
        "extraction_method": "odometer_displacement_over_command_window",
        "split_process_required": True,
        "hardware_validated_reference": True,
        "created_at": "2026-06-11T00:00:00Z",
        "operator_notes": "fixture test data only",
        "limitations": ["test fixture data — not empirical robot results"],
    }
    (session_dir / "session_metadata.json").write_text(json.dumps(metadata, indent=2))

    # trial_plan.csv
    trial_plan_fields = [
        "trial_id", "surface_id", "surface_type", "command_velocity",
        "block_index", "repeat_index", "state_log_path",
    ]
    trial_records_fields = [
        "trial_id", "session_id", "robot_id", "environment_id",
        "surface_type", "command_velocity", "block_index", "repeat_index",
        "idle_sec", "command_sec", "stop_sec", "state_log_path",
        "valid", "invalid_reason", "timestamp", "notes",
    ]
    trial_data = [
        {"trial_id": "K1_S1_lab_hard_floor_B1_U020_R1", "surface": "S1_lab_hard_floor", "speed": 0.2, "block": 1, "repeat": 1},
        {"trial_id": "K1_S1_lab_hard_floor_B1_U040_R1", "surface": "S1_lab_hard_floor", "speed": 0.4, "block": 1, "repeat": 1},
        {"trial_id": "K1_S1_lab_hard_floor_B1_U060_R1", "surface": "S1_lab_hard_floor", "speed": 0.6, "block": 1, "repeat": 1},
        {"trial_id": "K1_S1_lab_hard_floor_B2_U020_R2", "surface": "S1_lab_hard_floor", "speed": 0.2, "block": 2, "repeat": 2},
        {"trial_id": "K1_S1_lab_hard_floor_B2_U040_R2", "surface": "S1_lab_hard_floor", "speed": 0.4, "block": 2, "repeat": 2},
        {"trial_id": "K1_S1_lab_hard_floor_B2_U060_R2", "surface": "S1_lab_hard_floor", "speed": 0.6, "block": 2, "repeat": 2},
    ]

    # Write trial_plan.csv
    with (session_dir / "trial_plan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=trial_plan_fields)
        w.writeheader()
        for td in trial_data:
            w.writerow({
                "trial_id": td["trial_id"],
                "surface_id": td["surface"],
                "surface_type": "lab_hard_floor",
                "command_velocity": td["speed"],
                "block_index": td["block"],
                "repeat_index": td["repeat"],
                "state_log_path": f"state_logs/{td['trial_id']}.csv",
            })

    # Write trial_records.csv
    with (session_dir / "trial_records.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=trial_records_fields)
        w.writeheader()
        for td in trial_data:
            w.writerow({
                "trial_id": td["trial_id"],
                "session_id": "fixture_k1_session",
                "robot_id": "Booster_K1",
                "environment_id": "S1_lab_hard_floor_fixture",
                "surface_type": "lab_hard_floor",
                "command_velocity": td["speed"],
                "block_index": td["block"],
                "repeat_index": td["repeat"],
                "idle_sec": "2.0",
                "command_sec": "6.0",
                "stop_sec": "2.0",
                "state_log_path": f"state_logs/{td['trial_id']}.csv",
                "valid": "true",
                "invalid_reason": "",
                "timestamp": "2026-06-11T00:00:00Z",
                "notes": "fixture",
            })

    # Generate synthetic state log CSVs
    log_fields = [
        "timestamp", "t_rel", "phase", "command_velocity",
        "odom_x", "odom_y", "odom_theta", "imu_yaw",
    ]
    for td in trial_data:
        log_path = session_dir / "state_logs" / f"{td['trial_id']}.csv"
        with log_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=log_fields)
            w.writeheader()
            speed = td["speed"]
            # Generate ~60 samples over 6 seconds (10Hz)
            for i in range(60):
                t_rel = i * 0.1
                phase = "command" if 2.0 <= t_rel <= 8.0 else "idle"
                # Simulate odometer: position = speed * time with small noise
                odom_x = speed * (t_rel - 2.0) if t_rel >= 2.0 else 0.0
                odom_y = 0.01 * (i % 3)  # small lateral noise
                w.writerow({
                    "timestamp": f"{i * 0.1:.1f}",
                    "t_rel": f"{t_rel:.1f}",
                    "phase": phase,
                    "command_velocity": f"{speed}",
                    "odom_x": f"{odom_x:.4f}",
                    "odom_y": f"{odom_y:.4f}",
                    "odom_theta": f"{0.001 * i:.4f}",
                    "imu_yaw": f"{0.001 * i:.4f}",
                })

    return session_dir
