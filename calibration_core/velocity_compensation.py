"""Offline velocity compensation prototype.

This module implements the M22-C offline prototype only. It never sends robot
commands and does not make physical validation or deployment-readiness claims.
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from calibration_core.compensation_models import (
    SCHEMA_VERSION,
    SUPPORTED_EMPIRICAL_PLATFORM,
    CompensationDecision,
    CompensationRequest,
    CompensationThresholds,
    MonotonicSegment,
    ResponseCell,
    default_limitations,
    refusal_decision,
)
from calibration_core.compensation_policies import POLICIES, estimate_confidence, evaluate_cell, get_policy

DEFAULT_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
DEFAULT_CONTRACT_CSV = Path("outputs/measurement_v1/booster_k1_measurements_contract_v1.csv")
SUPPORTED_SCAFFOLD_PLATFORMS = {"unitree_go1", "unitree_g1"}


def validate_request(request: CompensationRequest) -> list[str]:
    errors = []
    if not request.platform:
        errors.append("platform is required")
    if not request.robot_model:
        errors.append("robot_model is required")
    if not request.surface_type:
        errors.append("surface_type is required")
    if request.desired_actual_velocity_mps < 0:
        errors.append("desired_actual_velocity_mps must be non-negative")
    if request.risk_policy not in POLICIES:
        errors.append(f"unknown risk_policy {request.risk_policy!r}")
    if request.extrapolation_policy not in {"reject", "nearest_bound"}:
        errors.append(f"unknown extrapolation_policy {request.extrapolation_policy!r}")
    if not request.response_profile_path.exists():
        errors.append(f"response_profile_path missing: {request.response_profile_path}")
    if request.contract_csv_path is not None and not request.contract_csv_path.exists():
        errors.append(f"contract_csv_path missing: {request.contract_csv_path}")
    return errors


def load_response_cells(
    profile_path: Path = DEFAULT_PROFILE,
    contract_csv_path: Path | None = DEFAULT_CONTRACT_CSV,
    *,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> list[ResponseCell]:
    profile_cells = load_cells_from_gold_profile(profile_path, platform=platform)
    if contract_csv_path is None or not contract_csv_path.exists():
        return profile_cells
    contract_cells = load_cells_from_contract_csv(contract_csv_path, profile_path=profile_path, platform=platform)
    profile_keys = {(cell.surface_type, round(cell.command_velocity_mps, 6)) for cell in profile_cells}
    merged = list(profile_cells)
    for cell in contract_cells:
        key = (cell.surface_type, round(cell.command_velocity_mps, 6))
        if key not in profile_keys:
            merged.append(cell)
    return merged


def load_cells_from_gold_profile(profile_path: Path, *, platform: str = SUPPORTED_EMPIRICAL_PLATFORM) -> list[ResponseCell]:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    robot_model = "Booster K1" if profile.get("robot_id") == "Booster_K1" else str(profile.get("robot_id", "unknown"))
    cells = []
    for row in profile.get("per_surface_response_statistics", []):
        cell = ResponseCell(
            platform=platform,
            robot_model=robot_model,
            surface_type=str(row["surface_id"]),
            command_velocity_mps=float(row["command_velocity"]),
            mean_actual_velocity_mps=float(row["mean_actual_velocity"]),
            n=int(row["n"]),
            std_actual_velocity_mps=float(row.get("std_actual_velocity", 0.0)),
            mean_yaw_drift_deg=float(row.get("mean_yaw_drift_deg", 0.0)),
            response_uncertainty=float(row.get("response_uncertainty", row.get("std_actual_velocity", 0.0))),
            no_motion_ratio=float(row.get("no_motion_ratio", 0.0)),
            region_label=str(row.get("region_label", "unclassified")),
            risk_score=float(row.get("risk_score", 1.0)),
            confidence=0.0,
            source="k1_gold_profile",
        )
        cells.append(_with_confidence(cell))
    return cells


def load_cells_from_contract_csv(
    contract_csv_path: Path,
    *,
    profile_path: Path | None = DEFAULT_PROFILE,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> list[ResponseCell]:
    profile_lookup = _profile_lookup(profile_path, platform) if profile_path and profile_path.exists() else {}
    groups: dict[tuple[str, str, str, float], list[dict[str, str]]] = defaultdict(list)
    with contract_csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("platform") != platform or row.get("extraction_status") != "ok":
                continue
            key = (
                row.get("platform", ""),
                row.get("robot_model", ""),
                row.get("surface_type", ""),
                float(row.get("command_velocity_mps", 0.0)),
            )
            groups[key].append(row)
    cells = []
    for (platform_id, robot_model, surface_type, command), rows in sorted(groups.items()):
        actuals = [float(row["measured_actual_velocity_mps"]) for row in rows]
        yaws = [float(row["yaw_drift_deg"]) for row in rows]
        no_motion_ratio = sum(1 for value in actuals if abs(value) <= CompensationThresholds().no_motion_velocity_threshold_mps) / len(actuals)
        lookup = profile_lookup.get((_surface_alias(surface_type), round(command, 6)), {})
        cell = ResponseCell(
            platform=platform_id,
            robot_model=robot_model,
            surface_type=surface_type,
            command_velocity_mps=command,
            mean_actual_velocity_mps=statistics.fmean(actuals),
            n=len(rows),
            std_actual_velocity_mps=statistics.stdev(actuals) if len(actuals) > 1 else 0.0,
            mean_yaw_drift_deg=statistics.fmean(yaws),
            response_uncertainty=statistics.stdev(actuals) if len(actuals) > 1 else 0.0,
            no_motion_ratio=no_motion_ratio,
            region_label=str(lookup.get("region_label", "unclassified")),
            risk_score=float(lookup.get("risk_score", 1.0)),
            confidence=0.0,
            source="measurement_contract_csv",
        )
        cells.append(_with_confidence(cell))
    return cells


def filter_cells_for_request(cells: list[ResponseCell], request: CompensationRequest) -> list[ResponseCell]:
    return [
        cell
        for cell in cells
        if cell.platform == request.platform
        and (cell.surface_type == request.surface_type or _surface_alias(cell.surface_type) == _surface_alias(request.surface_type))
    ]


def apply_risk_policy(
    cells: list[ResponseCell],
    request: CompensationRequest,
    thresholds: CompensationThresholds = CompensationThresholds(),
) -> tuple[list[ResponseCell], list[str]]:
    policy = get_policy(request.risk_policy)
    if policy is None:
        return [], [f"unknown risk policy {request.risk_policy}"]
    accepted = []
    warnings = []
    for cell in cells:
        ok, cell_warnings = evaluate_cell(cell, policy, thresholds, request.minimum_confidence)
        if ok:
            accepted.append(cell)
            warnings.extend(cell_warnings)
    return accepted, sorted(set(warnings))


def build_monotonic_segments(cells: list[ResponseCell], *, minimum_points: int = 2) -> list[MonotonicSegment]:
    ordered = sorted(cells, key=lambda cell: cell.command_velocity_mps)
    if not ordered:
        return []
    raw_segments: list[list[ResponseCell]] = [[ordered[0]]]
    for cell in ordered[1:]:
        current = raw_segments[-1]
        if cell.mean_actual_velocity_mps >= current[-1].mean_actual_velocity_mps:
            current.append(cell)
        else:
            raw_segments.append([cell])
    return [
        MonotonicSegment(segment_id=f"segment_{index}", cells=segment)
        for index, segment in enumerate(raw_segments, start=1)
        if len(segment) >= minimum_points
    ]


def compensate_velocity(
    request: CompensationRequest,
    thresholds: CompensationThresholds = CompensationThresholds(),
) -> CompensationDecision:
    errors = validate_request(request)
    if errors:
        return refusal_decision(request, "invalid_input", "; ".join(errors))
    if request.platform != SUPPORTED_EMPIRICAL_PLATFORM:
        if request.platform in SUPPORTED_SCAFFOLD_PLATFORMS:
            return refusal_decision(request, "platform_not_calibrated", f"{request.platform} is scaffold-only in M22-C")
        return refusal_decision(request, "platform_not_calibrated", f"{request.platform} has no calibrated profile")

    all_cells = load_response_cells(request.response_profile_path, request.contract_csv_path, platform=request.platform)
    surface_cells = filter_cells_for_request(all_cells, request)
    if not surface_cells:
        return refusal_decision(request, "surface_not_calibrated", f"surface {request.surface_type!r} has no response data")

    effective_cells = [
        cell
        for cell in surface_cells
        if cell.region_label != "deadzone"
        and cell.no_motion_ratio < 1.0
        and cell.mean_actual_velocity_mps >= thresholds.no_motion_velocity_threshold_mps
        and cell.n >= thresholds.minimum_cell_repeats
    ]
    if not effective_cells:
        return refusal_decision(request, "infeasible_deadzone", "no effective non-deadzone response cells are available")
    minimum_effective_actual = min(cell.mean_actual_velocity_mps for cell in effective_cells)
    if request.desired_actual_velocity_mps < minimum_effective_actual and request.extrapolation_policy == "reject":
        return refusal_decision(
            request,
            "infeasible_deadzone",
            f"desired velocity {request.desired_actual_velocity_mps:.3f} is below minimum effective actual velocity {minimum_effective_actual:.3f}",
        )

    policy_cells, policy_warnings = apply_risk_policy(surface_cells, request, thresholds)
    if not policy_cells:
        return refusal_decision(
            request,
            "insufficient_evidence",
            f"risk policy {request.risk_policy} removed all candidate cells",
            warnings=policy_warnings,
        )

    max_actual = max(cell.mean_actual_velocity_mps for cell in policy_cells)
    min_actual = min(cell.mean_actual_velocity_mps for cell in policy_cells)
    if request.desired_actual_velocity_mps > max_actual and request.extrapolation_policy == "reject":
        return refusal_decision(
            request,
            "infeasible_out_of_range",
            f"desired velocity {request.desired_actual_velocity_mps:.3f} exceeds max measured valid actual velocity {max_actual:.3f}",
            warnings=policy_warnings,
        )
    if request.desired_actual_velocity_mps < min_actual and request.extrapolation_policy == "reject":
        return refusal_decision(
            request,
            "infeasible_deadzone",
            f"desired velocity {request.desired_actual_velocity_mps:.3f} is below minimum policy-accepted actual velocity {min_actual:.3f}",
            warnings=policy_warnings,
        )

    segments = build_monotonic_segments(policy_cells, minimum_points=thresholds.minimum_segment_points)
    if not segments:
        return refusal_decision(
            request,
            "insufficient_evidence",
            "fewer than two policy-accepted points are available for monotonic inverse lookup",
            warnings=policy_warnings,
        )
    candidates = [segment for segment in segments if segment.brackets(request.desired_actual_velocity_mps)]
    if not candidates and request.extrapolation_policy == "nearest_bound":
        candidates = [_nearest_segment(segments, request.desired_actual_velocity_mps)]
        policy_warnings.append("nearest_bound extrapolation policy used")
    if not candidates:
        return refusal_decision(
            request,
            "infeasible_out_of_range",
            "no monotonic segment brackets the desired velocity and extrapolation is disabled",
            warnings=policy_warnings,
        )
    candidates = sorted(candidates, key=lambda segment: (segment.risk_score, -segment.confidence, _segment_distance(segment, request.desired_actual_velocity_mps)))
    if len(candidates) > 1 and abs(candidates[0].risk_score - candidates[1].risk_score) <= thresholds.comparable_risk_delta:
        return refusal_decision(
            request,
            "non_monotonic_ambiguous",
            "multiple comparable monotonic segments bracket the desired velocity",
            warnings=policy_warnings,
        )
    return _decision_from_segment(request, candidates[0], policy_warnings)


def _decision_from_segment(
    request: CompensationRequest,
    segment: MonotonicSegment,
    warnings: list[str],
) -> CompensationDecision:
    lower, upper = _bracketing_points(segment.cells, request.desired_actual_velocity_mps)
    if lower.command_velocity_mps == upper.command_velocity_mps or lower.mean_actual_velocity_mps == upper.mean_actual_velocity_mps:
        recommended = lower.command_velocity_mps
        expected = lower.mean_actual_velocity_mps
    else:
        ratio = (request.desired_actual_velocity_mps - lower.mean_actual_velocity_mps) / (
            upper.mean_actual_velocity_mps - lower.mean_actual_velocity_mps
        )
        recommended = lower.command_velocity_mps + (upper.command_velocity_mps - lower.command_velocity_mps) * ratio
        expected = lower.mean_actual_velocity_mps + (upper.mean_actual_velocity_mps - lower.mean_actual_velocity_mps) * ratio
    error = expected - request.desired_actual_velocity_mps
    relative_error = error / request.desired_actual_velocity_mps if request.desired_actual_velocity_mps else 0.0
    policy = get_policy(request.risk_policy)
    risky = bool(warnings) or (policy is not None and policy.status_for_success == "feasible_but_risky")
    status = "feasible_but_risky" if risky else "ok"
    region_labels = sorted({cell.region_label for cell in segment.cells})
    return CompensationDecision(
        schema_version=SCHEMA_VERSION,
        platform=request.platform,
        robot_model=request.robot_model,
        surface_type=request.surface_type,
        desired_actual_velocity_mps=request.desired_actual_velocity_mps,
        recommended_command_velocity_mps=recommended,
        expected_actual_velocity_mps=expected,
        expected_tracking_error_mps=error,
        expected_relative_error=relative_error,
        selected_segment=segment.segment_id,
        source_points=[lower.point_dict(), upper.point_dict()] if lower != upper else [lower.point_dict()],
        region_label=",".join(region_labels),
        risk_score=segment.risk_score,
        confidence=segment.confidence,
        feasibility_status=status,
        reason="offline inverse lookup computed from measured monotonic segment",
        warnings=sorted(set(warnings)),
        limitations=default_limitations(),
    )


def _bracketing_points(cells: list[ResponseCell], desired_velocity: float) -> tuple[ResponseCell, ResponseCell]:
    ordered = sorted(cells, key=lambda cell: cell.mean_actual_velocity_mps)
    if desired_velocity <= ordered[0].mean_actual_velocity_mps:
        return ordered[0], ordered[0]
    if desired_velocity >= ordered[-1].mean_actual_velocity_mps:
        return ordered[-1], ordered[-1]
    for lower, upper in zip(ordered, ordered[1:]):
        if lower.mean_actual_velocity_mps <= desired_velocity <= upper.mean_actual_velocity_mps:
            return lower, upper
    return ordered[-1], ordered[-1]


def _with_confidence(cell: ResponseCell) -> ResponseCell:
    return ResponseCell(**{**cell.__dict__, "confidence": estimate_confidence(cell)})


def _nearest_segment(segments: list[MonotonicSegment], desired_velocity: float) -> MonotonicSegment:
    return min(segments, key=lambda segment: _segment_distance(segment, desired_velocity))


def _segment_distance(segment: MonotonicSegment, desired_velocity: float) -> float:
    if segment.brackets(desired_velocity):
        return 0.0
    return min(abs(segment.min_actual - desired_velocity), abs(segment.max_actual - desired_velocity))


def _profile_lookup(profile_path: Path, platform: str) -> dict[tuple[str, float], dict[str, Any]]:
    lookup = {}
    for cell in load_cells_from_gold_profile(profile_path, platform=platform):
        lookup[(cell.surface_type, round(cell.command_velocity_mps, 6))] = {
            "region_label": cell.region_label,
            "risk_score": cell.risk_score,
        }
        lookup[(_surface_alias(cell.surface_type), round(cell.command_velocity_mps, 6))] = {
            "region_label": cell.region_label,
            "risk_score": cell.risk_score,
        }
    return lookup


def _surface_alias(surface: str) -> str:
    for prefix in ("S1_", "S2_", "S3_"):
        if surface.startswith(prefix):
            return surface[len(prefix) :]
    return surface
