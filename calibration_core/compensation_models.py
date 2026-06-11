"""Data models for offline velocity compensation decisions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "offline_velocity_compensation_v0.1"
SUPPORTED_EMPIRICAL_PLATFORM = "booster_k1"
FEASIBILITY_STATUSES = [
    "ok",
    "feasible_but_risky",
    "infeasible_deadzone",
    "infeasible_out_of_range",
    "insufficient_evidence",
    "non_monotonic_ambiguous",
    "platform_not_calibrated",
    "surface_not_calibrated",
    "invalid_input",
]


@dataclass(frozen=True)
class CompensationRequest:
    platform: str
    robot_model: str
    surface_type: str
    desired_actual_velocity_mps: float
    response_profile_path: Path
    contract_csv_path: Path | None = None
    risk_policy: str = "conservative"
    extrapolation_policy: str = "reject"
    minimum_confidence: float = 0.5
    operator_notes: str = ""


@dataclass(frozen=True)
class ResponseCell:
    platform: str
    robot_model: str
    surface_type: str
    command_velocity_mps: float
    mean_actual_velocity_mps: float
    n: int
    std_actual_velocity_mps: float
    mean_yaw_drift_deg: float
    response_uncertainty: float
    no_motion_ratio: float
    region_label: str
    risk_score: float
    confidence: float
    source: str = "gold_profile"

    def point_dict(self) -> dict[str, Any]:
        return {
            "command_velocity_mps": self.command_velocity_mps,
            "mean_actual_velocity_mps": self.mean_actual_velocity_mps,
            "n": self.n,
            "region_label": self.region_label,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class MonotonicSegment:
    segment_id: str
    cells: list[ResponseCell]

    @property
    def min_actual(self) -> float:
        return min(cell.mean_actual_velocity_mps for cell in self.cells)

    @property
    def max_actual(self) -> float:
        return max(cell.mean_actual_velocity_mps for cell in self.cells)

    @property
    def risk_score(self) -> float:
        return max(cell.risk_score for cell in self.cells)

    @property
    def confidence(self) -> float:
        return min(cell.confidence for cell in self.cells)

    def brackets(self, desired_velocity: float) -> bool:
        return self.min_actual <= desired_velocity <= self.max_actual


@dataclass(frozen=True)
class CompensationThresholds:
    no_motion_velocity_threshold_mps: float = 0.02
    yaw_drift_high_threshold_deg: float = 5.0
    uncertainty_high_threshold_mps: float = 0.08
    minimum_segment_points: int = 2
    minimum_cell_repeats: int = 3
    comparable_risk_delta: float = 0.1


@dataclass(frozen=True)
class CompensationPolicy:
    name: str
    accepted_labels: tuple[str, ...]
    max_risk_score: float
    min_confidence: float
    max_yaw_drift_deg: float
    max_uncertainty_mps: float
    min_repeats: int
    allow_deadzone: bool = False
    status_for_success: str = "ok"


@dataclass(frozen=True)
class CompensationDecision:
    schema_version: str
    platform: str
    robot_model: str
    surface_type: str
    desired_actual_velocity_mps: float
    recommended_command_velocity_mps: float | None
    expected_actual_velocity_mps: float | None
    expected_tracking_error_mps: float | None
    expected_relative_error: float | None
    selected_segment: str
    source_points: list[dict[str, Any]]
    region_label: str
    risk_score: float | None
    confidence: float
    feasibility_status: str
    reason: str
    warnings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    offline_only: bool = True
    physical_validation_status: str = "not_started"
    deployment_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def refusal_decision(
    request: CompensationRequest,
    status: str,
    reason: str,
    *,
    warnings: list[str] | None = None,
    limitations: list[str] | None = None,
) -> CompensationDecision:
    return CompensationDecision(
        schema_version=SCHEMA_VERSION,
        platform=request.platform,
        robot_model=request.robot_model,
        surface_type=request.surface_type,
        desired_actual_velocity_mps=request.desired_actual_velocity_mps,
        recommended_command_velocity_mps=None,
        expected_actual_velocity_mps=None,
        expected_tracking_error_mps=None,
        expected_relative_error=None,
        selected_segment="",
        source_points=[],
        region_label="",
        risk_score=None,
        confidence=0.0,
        feasibility_status=status,
        reason=reason,
        warnings=warnings or [],
        limitations=limitations or default_limitations(),
    )


def default_limitations() -> list[str]:
    return [
        "offline prototype only",
        "not physical validation",
        "not deployment-ready compensation",
        "no hardware commands are sent",
        "Booster K1 only for empirical decisions in M22-C",
        "GO1/G1 remain uncalibrated",
    ]
