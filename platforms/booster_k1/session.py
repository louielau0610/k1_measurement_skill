"""Booster K1 measurement session management.

Defines the standard session layout and builds session metadata.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid


# Standard session directory layout
SESSION_SUBDIRS = [
    "state_logs",
]

SESSION_FILES = [
    "session_metadata.json",
    "trial_plan.csv",
    "trial_records.csv",
    "extracted_measurements.csv",
    "qc_summary.json",
    "qc_report.md",
    "response_statistics.csv",
    "profile.json",
    "profile.md",
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

TRIAL_PLAN_FIELDS = [
    "trial_id",
    "surface_id",
    "surface_type",
    "command_velocity",
    "block_index",
    "repeat_index",
    "state_log_path",
]


SESSION_METADATA_FIELDS = [
    "session_id",
    "platform",
    "robot_model",
    "robot_id",
    "surface",
    "speeds",
    "repeats",
    "block_order",
    "timing",
    "command_source",
    "state_sources",
    "measurement_source",
    "extraction_method",
    "split_process_required",
    "hardware_validated_reference",
    "created_at",
    "operator_notes",
    "limitations",
]


class BoosterK1Session:
    """Manages a Booster K1 measurement session.

    Creates the standard session directory layout and builds
    session metadata with all required fields.
    """

    platform_id = "booster_k1"
    split_process_required = True
    hardware_validated_reference = True

    def __init__(
        self,
        session_id: str | None = None,
        *,
        robot_id: str = "Booster_K1",
        robot_model: str = "Booster K1",
        surface: str = "S1_lab_hard_floor",
        speeds: list[float] | None = None,
        repeats: int = 3,
        base_dir: Path | None = None,
        operator_notes: str = "",
    ) -> None:
        self.session_id = session_id or f"k1_measurement_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.robot_id = robot_id
        self.robot_model = robot_model
        self.surface = surface
        self.speeds = speeds or [0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
        self.repeats = repeats
        self.operator_notes = operator_notes

        if base_dir is None:
            base_dir = Path("data/measurement_sessions/booster_k1")
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / self.session_id

    @property
    def environment_id(self) -> str:
        return f"{self.surface}_{self.session_id[:8]}"

    def ensure_session_dir(self) -> Path:
        """Create the session directory layout if it doesn't exist.

        Returns the session directory path.
        """
        self.session_dir.mkdir(parents=True, exist_ok=True)
        for subdir in SESSION_SUBDIRS:
            (self.session_dir / subdir).mkdir(parents=True, exist_ok=True)
        return self.session_dir

    def build_metadata(self) -> dict[str, Any]:
        """Build and return session metadata with all required fields."""
        metadata = {
            "session_id": self.session_id,
            "platform": self.platform_id,
            "robot_model": self.robot_model,
            "robot_id": self.robot_id,
            "surface": self.surface,
            "speeds": self.speeds,
            "repeats": self.repeats,
            "block_order": "randomized_by_trial_scheduler",
            "timing": {
                "idle_sec": 2.0,
                "command_sec": 6.0,
                "stop_sec": 2.0,
            },
            "command_source": "booster_sdk_kPrepare_kWalking_Move",
            "state_sources": ["/odometer_state", "/low_state.imu_state.rpy"],
            "measurement_source": "ros2_odometer_state",
            "extraction_method": "odometer_displacement_over_command_window",
            "split_process_required": self.split_process_required,
            "hardware_validated_reference": self.hardware_validated_reference,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "operator_notes": self.operator_notes,
            "limitations": [
                "single Booster K1 unit",
                "ROS2 odometer-based measurement",
                "SDK command process isolated from ROS2 logger process",
                "no velocity compensation implemented",
                "no GO1/G1 empirical validation",
                "no cross-platform generalization claim",
            ],
        }
        return metadata

    def write_metadata(self) -> Path:
        """Write session_metadata.json to the session directory.

        Returns the path to the written metadata file.
        """
        self.ensure_session_dir()
        metadata = self.build_metadata()
        path = self.session_dir / "session_metadata.json"
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return path

    def write_trial_plan(
        self, trials: list[dict[str, Any]]
    ) -> Path:
        """Write trial_plan.csv to the session directory.

        Each trial dict should have: trial_id, surface_id, surface_type,
        command_velocity, block_index, repeat_index, state_log_path.
        """
        self.ensure_session_dir()
        path = self.session_dir / "trial_plan.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TRIAL_PLAN_FIELDS)
            writer.writeheader()
            for trial in trials:
                row = {k: trial.get(k, "") for k in TRIAL_PLAN_FIELDS}
                writer.writerow(row)
        return path

    @staticmethod
    def load_metadata(session_dir: Path) -> dict[str, Any]:
        """Load session metadata from a session directory."""
        path = Path(session_dir) / "session_metadata.json"
        if not path.exists():
            raise FileNotFoundError(f"Session metadata not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    @classmethod
    def from_metadata(cls, session_dir: Path) -> BoosterK1Session:
        """Reconstruct a session object from existing metadata."""
        metadata = cls.load_metadata(session_dir)
        return cls(
            session_id=metadata["session_id"],
            robot_id=metadata.get("robot_id", "Booster_K1"),
            robot_model=metadata.get("robot_model", "Booster K1"),
            surface=metadata.get("surface", "S1_lab_hard_floor"),
            speeds=metadata.get("speeds", []),
            repeats=metadata.get("repeats", 3),
            base_dir=Path(session_dir).parent,
            operator_notes=metadata.get("operator_notes", ""),
        )


def build_session_directory(
    session_id: str | None = None,
    base_dir: str | Path = "data/measurement_sessions/booster_k1",
    **kwargs: Any,
) -> BoosterK1Session:
    """Convenience function to create a session with directory layout."""
    session = BoosterK1Session(session_id=session_id, base_dir=Path(base_dir), **kwargs)
    session.ensure_session_dir()
    return session
