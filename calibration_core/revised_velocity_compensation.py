"""Revised offline velocity compensation with identity fallback and benefit gate.

M23-E revises the M22-C offline compensator after the M23-C negative physical
result. It remains offline-only and does not execute hardware.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import fmean
from typing import Any

from calibration_core.compensation_models import SUPPORTED_EMPIRICAL_PLATFORM, CompensationRequest
from calibration_core.velocity_compensation import (
    DEFAULT_CONTRACT_CSV,
    DEFAULT_PROFILE,
    compensate_velocity,
    filter_cells_for_request,
    load_response_cells,
)

DEFAULT_M23C_PAIR_CSV = Path("outputs/compensation_experiments/m23c_k1_before_after_pairs.csv")
DEFAULT_DIRECT_ERROR_GOOD_ENOUGH_MPS = 0.02
DEFAULT_MINIMUM_EXPECTED_BENEFIT_MPS = 0.02
DEFAULT_MAX_CORRECTION_MPS = 0.05
DEFAULT_PROFILE_MISMATCH_THRESHOLD_MPS = 0.03
REVISED_SCHEMA_VERSION = "revised_offline_velocity_compensation_v0.1"


@dataclass(frozen=True)
class RevisedCompensationRequest:
    platform: str
    robot_model: str = "Booster K1"
    surface_type: str = "S2_marble_floor"
    desired_actual_velocity_mps: float = 0.0
    response_profile_path: Path = DEFAULT_PROFILE
    contract_csv_path: Path | None = DEFAULT_CONTRACT_CSV
    physical_context_csv_path: Path | None = DEFAULT_M23C_PAIR_CSV
    risk_policy: str = "permissive"
    extrapolation_policy: str = "reject"
    minimum_confidence: float = 0.0
    direct_error_good_enough_mps: float = DEFAULT_DIRECT_ERROR_GOOD_ENOUGH_MPS
    minimum_expected_benefit_mps: float = DEFAULT_MINIMUM_EXPECTED_BENEFIT_MPS
    max_correction_mps: float = DEFAULT_MAX_CORRECTION_MPS
    profile_mismatch_threshold_mps: float = DEFAULT_PROFILE_MISMATCH_THRESHOLD_MPS
    allow_clamping: bool = False


@dataclass(frozen=True)
class BenefitGateResult:
    expected_direct_error_mps: float | None
    expected_compensated_error_mps: float | None
    expected_benefit_mps: float | None
    minimum_expected_benefit_mps: float
    passed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProfileMismatchResult:
    suspected: bool
    old_profile_predicted_actual_velocity_mps: float | None
    observed_direct_actual_velocity_mps: float | None
    difference_mps: float | None
    threshold_mps: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RevisedCompensationDecision:
    schema_version: str
    platform: str
    robot_model: str
    surface_type: str
    desired_actual_velocity_mps: float
    identity_command_velocity_mps: float
    candidate_compensated_command_velocity_mps: float | None
    final_command_velocity_mps: float
    expected_direct_error_mps: float | None
    expected_compensated_error_mps: float | None
    expected_benefit_mps: float | None
    benefit_gate_passed: bool
    correction_magnitude_mps: float | None
    correction_limited: bool
    profile_mismatch_suspected: bool
    feasibility_status: str
    reason: str
    warnings: list[str] = field(default_factory=list)
    benefit_gate: BenefitGateResult | None = None
    profile_mismatch: ProfileMismatchResult | None = None
    m22c_feasibility_status: str = ""
    offline_only: bool = True
    physical_validation_status: str = "not_started"
    deployment_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.benefit_gate is not None:
            data["benefit_gate"] = self.benefit_gate.to_dict()
        if self.profile_mismatch is not None:
            data["profile_mismatch"] = self.profile_mismatch.to_dict()
        return data


def revised_compensate_velocity(request: RevisedCompensationRequest) -> RevisedCompensationDecision:
    """Return a revised offline compensation decision."""
    warnings: list[str] = []
    identity_command = request.desired_actual_velocity_mps

    old_request = CompensationRequest(
        platform=request.platform,
        robot_model=request.robot_model,
        surface_type=request.surface_type,
        desired_actual_velocity_mps=request.desired_actual_velocity_mps,
        response_profile_path=request.response_profile_path,
        contract_csv_path=request.contract_csv_path,
        risk_policy=request.risk_policy,
        extrapolation_policy=request.extrapolation_policy,
        minimum_confidence=request.minimum_confidence,
    )
    old_decision = compensate_velocity(old_request)
    candidate_command = old_decision.recommended_command_velocity_mps

    context = load_physical_context(request.physical_context_csv_path)
    context_row = context.get(round(request.desired_actual_velocity_mps, 6))
    old_profile_direct_actual = predict_profile_actual_velocity(request, identity_command)
    observed_direct_actual = context_row.get("direct_measured_actual_velocity_mps") if context_row else None
    observed_comp_error = context_row.get("compensated_abs_error") if context_row else None

    expected_direct_error = _expected_direct_error(request, old_profile_direct_actual, observed_direct_actual)
    expected_compensated_error = _expected_compensated_error(old_decision, observed_comp_error)
    expected_benefit = (
        expected_direct_error - expected_compensated_error
        if expected_direct_error is not None and expected_compensated_error is not None
        else None
    )

    benefit_gate = BenefitGateResult(
        expected_direct_error_mps=expected_direct_error,
        expected_compensated_error_mps=expected_compensated_error,
        expected_benefit_mps=expected_benefit,
        minimum_expected_benefit_mps=request.minimum_expected_benefit_mps,
        passed=expected_benefit is not None and expected_benefit >= request.minimum_expected_benefit_mps,
        reason=(
            "expected benefit meets threshold"
            if expected_benefit is not None and expected_benefit >= request.minimum_expected_benefit_mps
            else "expected benefit below threshold or unavailable"
        ),
    )
    profile_mismatch = detect_profile_mismatch(
        request,
        old_profile_predicted_actual_velocity_mps=old_profile_direct_actual,
        observed_direct_actual_velocity_mps=observed_direct_actual,
        expected_direct_error_mps=expected_direct_error,
    )
    if profile_mismatch.suspected:
        warnings.append("profile_mismatch_suspected")

    correction_magnitude = abs(candidate_command - identity_command) if candidate_command is not None else None

    if expected_direct_error is not None and expected_direct_error <= request.direct_error_good_enough_mps:
        return _decision(
            request,
            candidate_command,
            identity_command,
            expected_direct_error,
            expected_compensated_error,
            expected_benefit,
            benefit_gate,
            correction_magnitude,
            correction_limited=False,
            profile_mismatch=profile_mismatch,
            old_status=old_decision.feasibility_status,
            status="identity_preferred",
            reason="direct command error is already within the good-enough threshold",
            warnings=warnings,
        )

    if candidate_command is None or old_decision.feasibility_status not in {"ok", "feasible_but_risky"}:
        return _decision(
            request,
            candidate_command,
            identity_command,
            expected_direct_error,
            expected_compensated_error,
            expected_benefit,
            benefit_gate,
            correction_magnitude,
            correction_limited=False,
            profile_mismatch=profile_mismatch,
            old_status=old_decision.feasibility_status,
            status=old_decision.feasibility_status,
            reason=f"M22-C candidate unavailable: {old_decision.reason}",
            warnings=warnings + old_decision.warnings,
        )

    if not benefit_gate.passed:
        return _decision(
            request,
            candidate_command,
            identity_command,
            expected_direct_error,
            expected_compensated_error,
            expected_benefit,
            benefit_gate,
            correction_magnitude,
            correction_limited=False,
            profile_mismatch=profile_mismatch,
            old_status=old_decision.feasibility_status,
            status="compensation_not_beneficial",
            reason="expected compensation benefit does not exceed the benefit gate",
            warnings=warnings,
        )

    if correction_magnitude is not None and correction_magnitude > request.max_correction_mps:
        if not request.allow_clamping:
            return _decision(
                request,
                candidate_command,
                identity_command,
                expected_direct_error,
                expected_compensated_error,
                expected_benefit,
                benefit_gate,
                correction_magnitude,
                correction_limited=False,
                profile_mismatch=profile_mismatch,
                old_status=old_decision.feasibility_status,
                status="overcorrection_risk",
                reason="candidate correction exceeds max_correction_mps and clamping is disabled",
                warnings=warnings,
            )
        direction = 1.0 if candidate_command > identity_command else -1.0
        final_command = identity_command + direction * request.max_correction_mps
        return _decision(
            request,
            candidate_command,
            final_command,
            expected_direct_error,
            expected_compensated_error,
            expected_benefit,
            benefit_gate,
            correction_magnitude,
            correction_limited=True,
            profile_mismatch=profile_mismatch,
            old_status=old_decision.feasibility_status,
            status="feasible_but_clamped",
            reason="candidate correction exceeded max_correction_mps and was clamped",
            warnings=warnings + ["correction_limited"],
        )

    return _decision(
        request,
        candidate_command,
        candidate_command,
        expected_direct_error,
        expected_compensated_error,
        expected_benefit,
        benefit_gate,
        correction_magnitude,
        correction_limited=False,
        profile_mismatch=profile_mismatch,
        old_status=old_decision.feasibility_status,
        status="ok",
        reason="candidate compensation passed identity fallback, benefit gate, and correction limit",
        warnings=warnings,
    )


def detect_profile_mismatch(
    request: RevisedCompensationRequest,
    *,
    old_profile_predicted_actual_velocity_mps: float | None,
    observed_direct_actual_velocity_mps: float | None,
    expected_direct_error_mps: float | None,
) -> ProfileMismatchResult:
    if old_profile_predicted_actual_velocity_mps is None or observed_direct_actual_velocity_mps is None:
        return ProfileMismatchResult(
            suspected=False,
            old_profile_predicted_actual_velocity_mps=old_profile_predicted_actual_velocity_mps,
            observed_direct_actual_velocity_mps=observed_direct_actual_velocity_mps,
            difference_mps=None,
            threshold_mps=request.profile_mismatch_threshold_mps,
            reason="profile or physical direct context unavailable",
        )
    diff = abs(old_profile_predicted_actual_velocity_mps - observed_direct_actual_velocity_mps)
    old_profile_error = abs(old_profile_predicted_actual_velocity_mps - request.desired_actual_velocity_mps)
    direct_good = expected_direct_error_mps is not None and expected_direct_error_mps <= request.direct_error_good_enough_mps
    suspected = diff > request.profile_mismatch_threshold_mps or (direct_good and old_profile_error > request.profile_mismatch_threshold_mps)
    return ProfileMismatchResult(
        suspected=suspected,
        old_profile_predicted_actual_velocity_mps=old_profile_predicted_actual_velocity_mps,
        observed_direct_actual_velocity_mps=observed_direct_actual_velocity_mps,
        difference_mps=diff,
        threshold_mps=request.profile_mismatch_threshold_mps,
        reason="profile prediction differs from M23-C direct physical result" if suspected else "no profile mismatch detected",
    )


def load_physical_context(path: Path | None) -> dict[float, dict[str, float]]:
    if path is None or not path.exists():
        return {}
    grouped: dict[float, list[dict[str, float]]] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            velocity = round(float(row["desired_velocity_mps"]), 6)
            grouped.setdefault(velocity, []).append({
                "direct_measured_actual_velocity_mps": float(row["direct_measured_actual_velocity_mps"]),
                "direct_abs_error": float(row["direct_abs_error"]),
                "compensated_abs_error": float(row["compensated_abs_error"]),
                "compensated_command_velocity_mps": float(row["compensated_command_velocity_mps"]),
            })
    return {
        velocity: {
            "direct_measured_actual_velocity_mps": fmean(row["direct_measured_actual_velocity_mps"] for row in rows),
            "direct_abs_error": fmean(row["direct_abs_error"] for row in rows),
            "compensated_abs_error": fmean(row["compensated_abs_error"] for row in rows),
            "compensated_command_velocity_mps": fmean(row["compensated_command_velocity_mps"] for row in rows),
        }
        for velocity, rows in grouped.items()
    }


def predict_profile_actual_velocity(request: RevisedCompensationRequest, command_velocity_mps: float) -> float | None:
    old_request = CompensationRequest(
        platform=request.platform,
        robot_model=request.robot_model,
        surface_type=request.surface_type,
        desired_actual_velocity_mps=request.desired_actual_velocity_mps,
        response_profile_path=request.response_profile_path,
        contract_csv_path=request.contract_csv_path,
        risk_policy=request.risk_policy,
        extrapolation_policy=request.extrapolation_policy,
        minimum_confidence=request.minimum_confidence,
    )
    cells = sorted(filter_cells_for_request(load_response_cells(request.response_profile_path, None, platform=request.platform), old_request), key=lambda cell: cell.command_velocity_mps)
    if not cells:
        return None
    if command_velocity_mps <= cells[0].command_velocity_mps:
        return cells[0].mean_actual_velocity_mps
    if command_velocity_mps >= cells[-1].command_velocity_mps:
        return cells[-1].mean_actual_velocity_mps
    for lower, upper in zip(cells, cells[1:]):
        if lower.command_velocity_mps <= command_velocity_mps <= upper.command_velocity_mps:
            if upper.command_velocity_mps == lower.command_velocity_mps:
                return lower.mean_actual_velocity_mps
            ratio = (command_velocity_mps - lower.command_velocity_mps) / (upper.command_velocity_mps - lower.command_velocity_mps)
            return lower.mean_actual_velocity_mps + ratio * (upper.mean_actual_velocity_mps - lower.mean_actual_velocity_mps)
    return None


def _expected_direct_error(
    request: RevisedCompensationRequest,
    old_profile_direct_actual: float | None,
    observed_direct_actual: float | None,
) -> float | None:
    if observed_direct_actual is not None:
        return abs(observed_direct_actual - request.desired_actual_velocity_mps)
    if old_profile_direct_actual is not None:
        return abs(old_profile_direct_actual - request.desired_actual_velocity_mps)
    return None


def _expected_compensated_error(old_decision: Any, observed_comp_error: float | None) -> float | None:
    if observed_comp_error is not None:
        return observed_comp_error
    if old_decision.expected_tracking_error_mps is not None:
        return abs(old_decision.expected_tracking_error_mps)
    return None


def _decision(
    request: RevisedCompensationRequest,
    candidate_command: float | None,
    final_command: float,
    expected_direct_error: float | None,
    expected_compensated_error: float | None,
    expected_benefit: float | None,
    benefit_gate: BenefitGateResult,
    correction_magnitude: float | None,
    *,
    correction_limited: bool,
    profile_mismatch: ProfileMismatchResult,
    old_status: str,
    status: str,
    reason: str,
    warnings: list[str],
) -> RevisedCompensationDecision:
    return RevisedCompensationDecision(
        schema_version=REVISED_SCHEMA_VERSION,
        platform=request.platform,
        robot_model=request.robot_model,
        surface_type=request.surface_type,
        desired_actual_velocity_mps=request.desired_actual_velocity_mps,
        identity_command_velocity_mps=request.desired_actual_velocity_mps,
        candidate_compensated_command_velocity_mps=candidate_command,
        final_command_velocity_mps=final_command,
        expected_direct_error_mps=expected_direct_error,
        expected_compensated_error_mps=expected_compensated_error,
        expected_benefit_mps=expected_benefit,
        benefit_gate_passed=benefit_gate.passed,
        correction_magnitude_mps=correction_magnitude,
        correction_limited=correction_limited,
        profile_mismatch_suspected=profile_mismatch.suspected,
        feasibility_status=status,
        reason=reason,
        warnings=sorted(set(warnings)),
        benefit_gate=benefit_gate,
        profile_mismatch=profile_mismatch,
        m22c_feasibility_status=old_status,
        offline_only=True,
        physical_validation_status="not_started",
        deployment_ready=False,
    )


def decision_to_json(decision: RevisedCompensationDecision) -> str:
    return json.dumps(decision.to_dict(), indent=2)
