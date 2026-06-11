"""Booster K1 measurement runner.

Implements the split-process K1 measurement workflow:
- SDK command process isolated from ROS2 logger process.
- Dry-run is the default; hardware movement requires explicit --execute.
- Per-trial permit mode is enabled by default.
- Trial records are append-only per session.
- Invalid trials are recorded with reason.

Existing M19C artifacts remain unchanged.
"""
from __future__ import annotations

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from platforms.booster_k1.session import (
    BoosterK1Session,
    TRIAL_RECORD_FIELDS,
)
from calibration_core.trial_scheduler import TrialScheduler, TrialSpec

DEFAULT_SURFACES = ["S1_lab_hard_floor", "S2_marble_floor", "S3_artificial_turf"]
SURFACE_TYPES = {
    "S1_lab_hard_floor": "lab_hard_floor",
    "S2_marble_floor": "marble_floor",
    "S3_artificial_turf": "artificial_turf",
}
DEFAULT_SPEEDS = [0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
DEFAULT_REPEATS = 3
IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0


class BoosterK1MeasurementRunner:
    """Orchestrates a Booster K1 measurement session with split-process awareness.

    The runner never combines rclpy and Booster SDK native command client in the
    same runtime path. It coordinates two separate processes:
    1. SDK command process (robot-side, sends velocity commands)
    2. ROS2 logger process (robot-side, records odometer state)

    Dry-run mode prints the trial plan without moving hardware.
    Execute mode requires explicit --execute and per-trial permit by default.
    """

    platform_id = "booster_k1"
    split_process_required = True

    def __init__(
        self,
        session: BoosterK1Session,
        *,
        execute: bool = False,
        permit: bool = True,
        interface: str = "ros2_odometer",
    ) -> None:
        self.session = session
        self.execute = execute
        self.permit = permit
        self.interface = interface
        self.scheduler = TrialScheduler()
        self._trial_records: list[dict[str, Any]] = []

    def plan_trials(
        self,
        surfaces: list[str] | None = None,
        speeds: list[float] | None = None,
        repeats: int | None = None,
    ) -> list[TrialSpec]:
        """Generate a deterministic trial plan."""
        surfaces = surfaces or self.session.surfaces or DEFAULT_SURFACES
        speeds = speeds or self.session.speeds or DEFAULT_SPEEDS
        repeats = repeats or self.session.repeats or DEFAULT_REPEATS
        trials = self.scheduler.build_trials(
            surfaces=surfaces,
            speeds=speeds,
            repeats=repeats,
            platform="booster_k1",
            prefix="K1",
        )
        return trials

    def run(self, surfaces: list[str] | None = None) -> dict[str, Any]:
        """Run or dry-run a measurement session.

        Returns a summary dict with session metadata and trial outcomes.
        """
        trials = self.plan_trials(surfaces=surfaces)

        if not self.execute:
            return self._dry_run(trials)

        return self._execute_trials(trials)

    def _dry_run(self, trials: list[TrialSpec]) -> dict[str, Any]:
        """Print the trial plan without moving hardware."""
        print(f"\n{'='*60}")
        print(f"  Booster K1 Measurement Session — DRY RUN")
        print(f"  Session ID: {self.session.session_id}")
        print(f"  Platform:   {self.platform_id}")
        print(f"  Surface(s): {', '.join(sorted(set(t.surface_id for t in trials)))}")
        print(f"  Total trials: {len(trials)}")
        print(f"  Split-process required: {self.split_process_required}")
        print(f"  Motor movement: DISABLED (dry-run)")
        print(f"{'='*60}\n")

        for i, t in enumerate(trials, 1):
            print(
                f"  [{i:03d}/{len(trials):03d}] {t.trial_id:40s} "
                f"v_cmd={t.command_velocity:.2f} m/s  surface={t.surface_id}"
            )

        print(f"\n{'='*60}")
        print(f"  Dry-run complete. No hardware was moved.")
        print(f"  To execute, re-run with --execute.")
        print(f"{'='*60}\n")

        return {
            "session_id": self.session.session_id,
            "dry_run": True,
            "hardware_executed": False,
            "total_trials": len(trials),
            "trial_ids": [t.trial_id for t in trials],
        }

    def _execute_trials(self, trials: list[TrialSpec]) -> dict[str, Any]:
        """Execute trials with per-trial permit and append-only recording.

        WARNING: This path moves the robot. It must only be called with
        explicit --execute and per-trial confirmation by default.
        """
        if not self.execute:
            raise RuntimeError("execute_trials called but execute=False")

        session_dir = self.session.ensure_session_dir()
        trial_records_path = session_dir / "trial_records.csv"

        results: list[dict[str, Any]] = []
        executed = 0
        skipped = 0
        invalid = 0

        print(f"\n{'='*60}")
        print(f"  Booster K1 Measurement Session — EXECUTE")
        print(f"  Session ID: {self.session.session_id}")
        print(f"  Total trials: {len(trials)}")
        print(f"  Split-process required: {self.split_process_required}")
        print(f"  Interface: {self.interface}")
        print(f"  Per-trial permit: {'enabled' if self.permit else 'disabled'}")
        print(f"  Session dir: {session_dir}")
        print(f"{'='*60}\n")

        for i, trial in enumerate(trials, 1):
            print(f"\n--- Trial {i}/{len(trials)}: {trial.trial_id} ---")
            print(f"    Surface: {trial.surface_id}")
            print(f"    Command velocity: {trial.command_velocity:.2f} m/s")
            print(f"    Block: {trial.block_index}, Repeat: {trial.repeat_index}")

            record = self._build_trial_record(trial)

            if self.permit:
                response = input("    Execute this trial? [y/N]: ").strip().lower()
                if response != "y":
                    record["valid"] = "false"
                    record["invalid_reason"] = "operator_skipped"
                    results.append(record)
                    skipped += 1
                    print("    → SKIPPED by operator.")
                    self._append_trial_record(trial_records_path, record)
                    continue

            # --- Hardware movement block ---
            # In the split-process design, this is where the operator would:
            # 1. Start the ROS2 logger process (separate terminal)
            # 2. Send the velocity command via the SDK command process
            # 3. Wait for the trial duration
            # 4. Stop the logger process
            # This runner does NOT directly call rclpy or SDK APIs.
            try:
                self._execute_single_trial(trial, record)
                record["valid"] = "true"
                record["invalid_reason"] = ""
                executed += 1
                print(f"    → EXECUTED.")
            except Exception as exc:
                record["valid"] = "false"
                record["invalid_reason"] = f"execution_error:{exc}"
                invalid += 1
                print(f"    → FAILED: {exc}")

            record["timestamp"] = datetime.now(timezone.utc).isoformat()
            results.append(record)
            self._append_trial_record(trial_records_path, record)

        summary = {
            "session_id": self.session.session_id,
            "dry_run": False,
            "hardware_executed": True,
            "total_trials": len(trials),
            "executed": executed,
            "skipped": skipped,
            "invalid": invalid,
            "trial_records_path": str(trial_records_path),
        }

        print(f"\n{'='*60}")
        print(f"  Session complete.")
        print(f"  Executed: {executed}, Skipped: {skipped}, Invalid: {invalid}")
        print(f"  Trial records: {trial_records_path}")
        print(f"{'='*60}\n")

        return summary

    def _build_trial_record(self, trial: TrialSpec) -> dict[str, Any]:
        surface_type = SURFACE_TYPES.get(trial.surface_id, trial.surface_id)
        state_log_path = str(
            self.session.session_dir / "state_logs" / f"{trial.trial_id}.csv"
        )
        return {
            "trial_id": trial.trial_id,
            "session_id": self.session.session_id,
            "robot_id": self.session.robot_id,
            "environment_id": self.session.environment_id,
            "surface_type": surface_type,
            "command_velocity": trial.command_velocity,
            "block_index": trial.block_index,
            "repeat_index": trial.repeat_index,
            "idle_sec": IDLE_SEC,
            "command_sec": COMMAND_SEC,
            "stop_sec": STOP_SEC,
            "state_log_path": state_log_path,
            "valid": "",
            "invalid_reason": "",
            "timestamp": "",
            "notes": "",
        }

    def _execute_single_trial(
        self, trial: TrialSpec, record: dict[str, Any]
    ) -> None:
        """Execute a single trial.

        In split-process mode, the operator is responsible for:
        1. Starting the ROS2 logger in a separate terminal:
           source /opt/booster/BoosterRos2Interface/install/setup.bash
           python scripts/log_k1_ros2_odometer_state.py --trial-id {trial_id} --output {state_log_path}

        2. Sending the velocity command via the SDK command process:
           python scripts/run_booster_k1_measurement.py --execute-single --speed {v_cmd}

        This method validates the split-process requirements and records
        the trial metadata. Actual hardware I/O happens in the separate
        processes described above.
        """
        state_log_dir = self.session.session_dir / "state_logs"
        state_log_dir.mkdir(parents=True, exist_ok=True)

        print(f"    [SPLIT-PROCESS] Start ROS2 logger (separate terminal):")
        print(f"      source /opt/booster/BoosterRos2Interface/install/setup.bash")
        print(f"      python scripts/log_k1_ros2_odometer_state.py \\")
        print(f"        --trial-id {trial.trial_id} \\")
        print(f"        --output {record['state_log_path']}")

        if self.permit:
            input("    Press Enter after starting the ROS2 logger...")

        print(f"    [SPLIT-PROCESS] Send velocity command via SDK process:")
        print(f"      v_cmd = {trial.command_velocity:.2f} m/s for {COMMAND_SEC:.0f}s")
        print(f"      (Use existing validated M19C runner on robot-side environment)")

        if self.permit:
            input("    Press Enter after the trial duration...")

    def _append_trial_record(
        self, path: Path, record: dict[str, Any]
    ) -> None:
        """Append a trial record to the session CSV file."""
        write_header = not path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TRIAL_RECORD_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow(record)
