"""M19-A repeated validation schema."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json

EVIDENCE_LEVELS = [
    "real_repeated",
    "real_single_or_sparse",
    "pipeline_only",
    "pending_real_data",
    "test_fixture_only",
]

REGION_LABELS = [
    "deadzone",
    "under_track",
    "drift_prone",
    "reliable",
    "insufficient_evidence",
    "pending_real_data",
]

@dataclass
class RepeatedTrialRecord:
    trial_id: str
    session_id: str
    robot_id: str
    environment_id: str
    environment_description: str
    surface_type: str
    command_velocity: float
    measured_actual_velocity: Optional[float]
    yaw_drift_statistic: Optional[float]
    trial_duration_sec: Optional[float]
    valid: bool
    invalid_reason: Optional[str]
    raw_log_path: str
    normalized_record_path: str
    timestamp: str
    notes: str

@dataclass
class PerCommandAggregate:
    command_velocity: float
    n_total: int
    n_valid: int
    mean_actual_velocity: Optional[float]
    std_actual_velocity: Optional[float]
    mean_tracking_error: Optional[float]
    abs_mean_tracking_error: Optional[float]
    no_motion_ratio: float
    mean_yaw_drift: Optional[float]
    yaw_drift_risk: float
    uncertainty: float
    risk_score: float
    region_label: str
    evidence_level: str

@dataclass
class ValidationSummary:
    analysis_timestamp: str
    mode: str  # "real_data" or "pending_data"
    total_trials: int
    total_valid: int
    commands_evaluated: int
    commands_pending: int
    per_command: list[dict] = field(default_factory=list)
    notes: str = ""
    robot_access_attempted: bool = False
    real_repeated_logs_found: bool = False
    compensation_implemented: bool = False
    safe_command_adapter_implemented: bool = False
    navigation_improvement_claimed: bool = False
    cross_robot_generalization_claimed: bool = False

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, default=str)
