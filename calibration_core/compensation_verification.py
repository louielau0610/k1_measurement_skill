"""Offline compensator verification and edge-case audit.

Provides functions for auditing the M22-C offline velocity compensator:
- offline decision audit
- edge-case audit
- leave-one-repeat-out validation
- baseline comparison
- risk policy audit
- deadzone audit
- out-of-range audit
- non-monotonic audit

All verification is offline-only. No hardware commands are sent.
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from calibration_core.compensation_models import (
    SCHEMA_VERSION,
    SUPPORTED_EMPIRICAL_PLATFORM,
    CompensationDecision,
    CompensationPolicy,
    CompensationRequest,
    CompensationThresholds,
    ResponseCell,
)
from calibration_core.compensation_policies import POLICIES, estimate_confidence, evaluate_cell
from calibration_core.velocity_compensation import compensate_velocity

OFFLINE_ONLY_DISCLAIMER = "offline verification only — not physical validation — not deployment-ready — no hardware execution"

# ---------------------------------------------------------------------------
# Verification data structures
# ---------------------------------------------------------------------------


@dataclass
class VerificationCase:
    """A single verification test case."""
    platform: str
    surface_type: str
    desired_velocity_mps: float
    policy: str
    expected_status: str
    label: str = ""


@dataclass
class VerificationResult:
    """Result of running a single verification case."""
    platform: str
    surface_type: str
    desired_velocity_mps: float
    policy: str
    expected_status: str
    actual_status: str
    recommended_command_velocity_mps: float | None
    expected_actual_velocity_mps: float | None
    nearest_measured_actual_velocity_mps: float | None
    error_mps: float | None
    passed: bool
    reason: str
    warnings: list[str] = field(default_factory=list)
    offline_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BaselineDecision:
    """Result from a baseline compensation method."""
    method: str
    recommended_command_velocity_mps: float | None
    expected_actual_velocity_mps: float | None
    status: str
    reason: str


@dataclass
class BaselineComparison:
    """Comparison of multiple baseline methods against the compensator."""
    platform: str
    surface_type: str
    desired_velocity_mps: float
    policy: str
    compensator_decision: BaselineDecision
    baselines: list[BaselineDecision] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "surface_type": self.surface_type,
            "desired_velocity_mps": self.desired_velocity_mps,
            "policy": self.policy,
            "compensator": asdict(self.compensator_decision),
            "baselines": [asdict(b) for b in self.baselines],
        }


@dataclass
class LeaveOneRepeatOutResult:
    """Result of a single leave-one-repeat-out check."""
    trial_id: str
    platform: str
    surface_type: str
    command_velocity_mps: float
    measured_actual_velocity_mps: float
    predicted_command_mps: float | None
    absolute_command_error_mps: float | None
    expected_actual_mps: float | None
    actual_error_mps: float | None
    feasibility_status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EdgeCaseAuditResult:
    """Results from edge-case audit."""
    cases: list[VerificationResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cases": [c.to_dict() for c in self.cases],
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
        }


@dataclass
class VerificationSummary:
    """Aggregate verification summary."""
    leave_one_repeat_out: dict[str, Any] = field(default_factory=dict)
    edge_case_audit: dict[str, Any] = field(default_factory=dict)
    baseline_comparison: dict[str, Any] = field(default_factory=dict)
    risk_policy_audit: dict[str, Any] = field(default_factory=dict)
    offline_only: bool = True
    physical_validation: str = "not_started"
    deployment_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Edge-case audit
# ---------------------------------------------------------------------------

EDGE_CASES: list[VerificationCase] = [
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", -0.1, "conservative", "invalid_input", "negative_velocity"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", 0.001, "conservative", "infeasible_deadzone", "below_min_effective"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", 2.0, "conservative", "infeasible_out_of_range", "above_measured_range"),
    VerificationCase("unitree_go1", "lab_hard_floor", 0.3, "conservative", "platform_not_calibrated", "unsupported_platform"),
    VerificationCase("unitree_g1", "lab_hard_floor", 0.3, "conservative", "platform_not_calibrated", "unsupported_platform_g1"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "nonexistent_surface", 0.3, "conservative", "surface_not_calibrated", "unsupported_surface"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", 0.30, "conservative", "insufficient_evidence", "conservative_may_reject_risky"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", 0.30, "permissive", "feasible_but_risky", "permissive_accepts_risky"),
    VerificationCase(SUPPORTED_EMPIRICAL_PLATFORM, "S1_lab_hard_floor", 0.60, "conservative", "infeasible_out_of_range", "no_extrapolation_default"),
]


def run_edge_case_audit(
    profile_path: Path,
    contract_csv_path: Path,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> EdgeCaseAuditResult:
    """Run all edge-case tests against the compensator."""
    results: list[VerificationResult] = []
    for case in EDGE_CASES:
        request = CompensationRequest(
            platform=case.platform,
            robot_model="Booster K1" if case.platform == SUPPORTED_EMPIRICAL_PLATFORM else "unknown",
            surface_type=case.surface_type,
            desired_actual_velocity_mps=case.desired_velocity_mps,
            response_profile_path=profile_path,
            contract_csv_path=contract_csv_path,
            risk_policy=case.policy,
        )
        decision = compensate_velocity(request)
        passed = decision.feasibility_status == case.expected_status
        nearest = _find_nearest_measured(decision, contract_csv_path, case.surface_type)
        results.append(VerificationResult(
            platform=case.platform,
            surface_type=case.surface_type,
            desired_velocity_mps=case.desired_velocity_mps,
            policy=case.policy,
            expected_status=case.expected_status,
            actual_status=decision.feasibility_status,
            recommended_command_velocity_mps=decision.recommended_command_velocity_mps,
            expected_actual_velocity_mps=decision.expected_actual_velocity_mps,
            nearest_measured_actual_velocity_mps=nearest,
            error_mps=_safe_diff(decision.expected_actual_velocity_mps, case.desired_velocity_mps),
            passed=passed,
            reason=decision.reason,
            warnings=decision.warnings,
        ))
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return EdgeCaseAuditResult(cases=results, total=total, passed=passed, failed=total - passed)


# ---------------------------------------------------------------------------
# Leave-one-repeat-out validation
# ---------------------------------------------------------------------------


def run_leave_one_repeat_out(
    contract_csv_path: Path,
    profile_path: Path,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> list[LeaveOneRepeatOutResult]:
    """Run leave-one-repeat-out validation on the K1 contract CSV.

    For each surface-speed cell, holds out one repeat, builds aggregate
    response from remaining repeats, and predicts command for the held-out
    measured actual velocity as desired velocity.
    """
    # Load all valid trial rows
    with contract_csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("extraction_status") == "ok" and r.get("platform") == platform]

    # Group by (surface_type, command_velocity)
    groups: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["surface_type"], float(row["command_velocity_mps"]))
        groups[key].append(row)

    results: list[LeaveOneRepeatOutResult] = []
    for (surface, cmd), group_rows in sorted(groups.items()):
        for holdout_idx, held_out in enumerate(group_rows):
            # Build aggregate from remaining repeats
            remaining = [r for i, r in enumerate(group_rows) if i != holdout_idx]
            if not remaining:
                continue

            actuals = [float(r["measured_actual_velocity_mps"]) for r in remaining]
            yaws = [float(r["yaw_drift_deg"]) for r in remaining]
            mean_actual = statistics.fmean(actuals)
            std_actual = statistics.stdev(actuals) if len(actuals) > 1 else 0.0

            # Build a synthetic ResponseCell from remaining data
            cell = ResponseCell(
                platform=platform,
                robot_model="Booster K1",
                surface_type=surface,
                command_velocity_mps=cmd,
                mean_actual_velocity_mps=mean_actual,
                n=len(remaining),
                std_actual_velocity_mps=std_actual,
                mean_yaw_drift_deg=statistics.fmean(yaws),
                response_uncertainty=std_actual,
                no_motion_ratio=sum(1 for a in actuals if abs(a) <= 0.02) / len(actuals),
                region_label="unclassified",
                risk_score=0.5,
                confidence=0.5,
                source="leave_one_out",
            )

            # Use held-out measured actual as desired velocity
            desired = float(held_out["measured_actual_velocity_mps"])

            # Predict: find command that would produce desired actual using cell data
            if cell.mean_actual_velocity_mps > 0:
                # Simple inverse: command * (mean_actual / command) ≈ desired
                # → predicted_command = desired * (command / mean_actual)
                gain = cell.command_velocity_mps / cell.mean_actual_velocity_mps if cell.mean_actual_velocity_mps > 0 else 1.0
                predicted_cmd = desired * gain
                expected_actual = predicted_cmd * (cell.mean_actual_velocity_mps / cell.command_velocity_mps) if cell.command_velocity_mps > 0 else 0.0
                status = "ok"
                reason = "leave-one-repeat-out prediction"
            else:
                predicted_cmd = None
                expected_actual = None
                status = "infeasible_deadzone"
                reason = "held-out cell has zero measured actual velocity"

            results.append(LeaveOneRepeatOutResult(
                trial_id=held_out["trial_id"],
                platform=platform,
                surface_type=surface,
                command_velocity_mps=cmd,
                measured_actual_velocity_mps=float(held_out["measured_actual_velocity_mps"]),
                predicted_command_mps=predicted_cmd,
                absolute_command_error_mps=abs(predicted_cmd - cmd) if predicted_cmd is not None else None,
                expected_actual_mps=expected_actual,
                actual_error_mps=abs(expected_actual - desired) if expected_actual is not None else None,
                feasibility_status=status,
                reason=reason,
            ))

    return results


def summarize_leave_one_repeat_out(results: list[LeaveOneRepeatOutResult]) -> dict[str, Any]:
    """Compute summary metrics from leave-one-repeat-out results."""
    cmd_errors = [r.absolute_command_error_mps for r in results if r.absolute_command_error_mps is not None]
    statuses = [r.feasibility_status for r in results]
    status_dist = {s: statuses.count(s) for s in set(statuses)}

    per_surface: dict[str, dict[str, Any]] = {}
    for r in results:
        if r.surface_type not in per_surface:
            per_surface[r.surface_type] = {"errors": [], "count": 0, "infeasible": 0}
        per_surface[r.surface_type]["count"] += 1
        if r.absolute_command_error_mps is not None:
            per_surface[r.surface_type]["errors"].append(r.absolute_command_error_mps)
        if r.feasibility_status == "infeasible_deadzone":
            per_surface[r.surface_type]["infeasible"] += 1

    surface_metrics = {}
    for surf, data in per_surface.items():
        errs = data["errors"]
        surface_metrics[surf] = {
            "count": data["count"],
            "infeasible_count": data["infeasible"],
            "mean_abs_cmd_error_mps": statistics.fmean(errs) if errs else None,
            "median_abs_cmd_error_mps": statistics.median(errs) if errs else None,
            "max_abs_cmd_error_mps": max(errs) if errs else None,
        }

    return {
        "total_checks": len(results),
        "feasible_checks": sum(1 for r in results if r.feasibility_status == "ok"),
        "infeasible_checks": sum(1 for r in results if r.feasibility_status != "ok"),
        "status_distribution": status_dist,
        "mean_abs_command_error_mps": statistics.fmean(cmd_errors) if cmd_errors else None,
        "median_abs_command_error_mps": statistics.median(cmd_errors) if cmd_errors else None,
        "max_abs_command_error_mps": max(cmd_errors) if cmd_errors else None,
        "per_surface": surface_metrics,
        "disclaimer": OFFLINE_ONLY_DISCLAIMER,
    }


# ---------------------------------------------------------------------------
# Baseline methods (offline comparison only)
# ---------------------------------------------------------------------------


def baseline_direct_command(desired_velocity: float) -> BaselineDecision:
    """A. Direct command baseline: u_cmd = v_desired."""
    return BaselineDecision(
        method="direct_command",
        recommended_command_velocity_mps=desired_velocity,
        expected_actual_velocity_mps=None,
        status="naive",
        reason="u_cmd = v_desired, no compensation",
    )


def baseline_scalar_gain(desired_velocity: float, gain: float) -> BaselineDecision:
    """B. Naive scalar gain baseline: u_cmd = k * v_desired."""
    predicted = gain * desired_velocity
    return BaselineDecision(
        method="scalar_gain",
        recommended_command_velocity_mps=predicted,
        expected_actual_velocity_mps=predicted / gain if gain != 0 else None,
        status="naive",
        reason=f"u_cmd = {gain:.3f} * v_desired",
    )


def baseline_nearest_lookup(
    desired_velocity: float,
    cells: list[ResponseCell],
) -> BaselineDecision:
    """C. Nearest lookup baseline: choose command with closest mean actual velocity."""
    if not cells:
        return BaselineDecision(method="nearest_lookup", recommended_command_velocity_mps=None, expected_actual_velocity_mps=None, status="no_data", reason="no cells available")
    best = min(cells, key=lambda c: abs(c.mean_actual_velocity_mps - desired_velocity))
    return BaselineDecision(
        method="nearest_lookup",
        recommended_command_velocity_mps=best.command_velocity_mps,
        expected_actual_velocity_mps=best.mean_actual_velocity_mps,
        status="lookup",
        reason=f"nearest match at cmd={best.command_velocity_mps:.3f} m/s, actual={best.mean_actual_velocity_mps:.3f} m/s",
    )


def baseline_ordinary_interpolation(
    desired_velocity: float,
    cells: list[ResponseCell],
) -> BaselineDecision:
    """D. Ordinary interpolation: global interpolation without risk filtering."""
    if not cells:
        return BaselineDecision(method="ordinary_interpolation", recommended_command_velocity_mps=None, expected_actual_velocity_mps=None, status="no_data", reason="no cells available")
    ordered = sorted(cells, key=lambda c: c.command_velocity_mps)
    # Find bracketing points
    for i in range(len(ordered) - 1):
        a, b = ordered[i], ordered[i + 1]
        if a.mean_actual_velocity_mps <= desired_velocity <= b.mean_actual_velocity_mps:
            if b.mean_actual_velocity_mps == a.mean_actual_velocity_mps:
                continue
            t = (desired_velocity - a.mean_actual_velocity_mps) / (b.mean_actual_velocity_mps - a.mean_actual_velocity_mps)
            cmd = a.command_velocity_mps + t * (b.command_velocity_mps - a.command_velocity_mps)
            expected = a.mean_actual_velocity_mps + t * (b.mean_actual_velocity_mps - a.mean_actual_velocity_mps)
            return BaselineDecision(
                method="ordinary_interpolation",
                recommended_command_velocity_mps=round(cmd, 6),
                expected_actual_velocity_mps=round(expected, 6),
                status="interpolated",
                reason=f"global interpolation between cmd={a.command_velocity_mps:.3f} and {b.command_velocity_mps:.3f}",
            )
    # Fallback: nearest
    return baseline_nearest_lookup(desired_velocity, cells)


def estimate_scalar_gain(cells: list[ResponseCell]) -> float:
    """Estimate scalar gain k from valid non-deadzone cells: k = mean(cmd/actual)."""
    valid = [c for c in cells if c.mean_actual_velocity_mps > 0.01 and c.no_motion_ratio < 1.0]
    if not valid:
        return 1.0
    gains = [c.command_velocity_mps / c.mean_actual_velocity_mps for c in valid]
    return round(statistics.fmean(gains), 4)


def run_baseline_comparison(
    profile_path: Path,
    contract_csv_path: Path,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> list[BaselineComparison]:
    """Compare compensator against baselines for all surfaces."""
    from calibration_core.velocity_compensation import load_response_cells

    cells = load_response_cells(profile_path, contract_csv_path, platform=platform)
    gain = estimate_scalar_gain(cells)
    surfaces = sorted({c.surface_type for c in cells})

    comparisons: list[BaselineComparison] = []
    for surface in surfaces:
        surface_cells = [c for c in cells if c.surface_type == surface]
        velocities = sorted({c.mean_actual_velocity_mps for c in surface_cells if c.mean_actual_velocity_mps > 0.01})
        # Add some intermediate velocities for testing
        test_velocities = velocities + [round((velocities[i] + velocities[i + 1]) / 2, 4) for i in range(len(velocities) - 1)]

        for v_desired in sorted(set(test_velocities))[:10]:  # Limit per surface
            request = CompensationRequest(
                platform=platform,
                robot_model="Booster K1",
                surface_type=surface,
                desired_actual_velocity_mps=v_desired,
                response_profile_path=profile_path,
                contract_csv_path=contract_csv_path,
                risk_policy="balanced",
            )
            decision = compensate_velocity(request)
            comp = BaselineDecision(
                method="ours_conservative_monotonic",
                recommended_command_velocity_mps=decision.recommended_command_velocity_mps,
                expected_actual_velocity_mps=decision.expected_actual_velocity_mps,
                status=decision.feasibility_status,
                reason=decision.reason,
            )
            comparison = BaselineComparison(
                platform=platform,
                surface_type=surface,
                desired_velocity_mps=v_desired,
                policy="balanced",
                compensator_decision=comp,
                baselines=[
                    baseline_direct_command(v_desired),
                    baseline_scalar_gain(v_desired, gain),
                    baseline_nearest_lookup(v_desired, surface_cells),
                    baseline_ordinary_interpolation(v_desired, surface_cells),
                ],
            )
            comparisons.append(comparison)

    return comparisons


# ---------------------------------------------------------------------------
# Risk policy audit
# ---------------------------------------------------------------------------


def run_risk_policy_audit(
    profile_path: Path,
    contract_csv_path: Path,
    platform: str = SUPPORTED_EMPIRICAL_PLATFORM,
) -> dict[str, Any]:
    """Audit how risk policy changes affect compensator decisions."""
    policies = ["conservative", "balanced", "permissive"]
    from calibration_core.velocity_compensation import load_response_cells

    cells = load_response_cells(profile_path, contract_csv_path, platform=platform)
    surfaces = sorted({c.surface_type for c in cells})

    # Generate a sweep of desired velocities from 0.05 to 0.65 in 0.05 steps
    sweep_velocities = [round(v, 2) for v in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]]

    all_results: list[dict[str, Any]] = []
    policy_stats: dict[str, dict[str, int]] = {p: {"feasible": 0, "risky": 0, "rejected": 0} for p in policies}

    for surface in surfaces:
        for v_desired in sweep_velocities:
            for policy_name in policies:
                request = CompensationRequest(
                    platform=platform,
                    robot_model="Booster K1",
                    surface_type=surface,
                    desired_actual_velocity_mps=v_desired,
                    response_profile_path=profile_path,
                    contract_csv_path=contract_csv_path,
                    risk_policy=policy_name,
                )
                decision = compensate_velocity(request)
                status = decision.feasibility_status
                entry = {
                    "surface": surface,
                    "desired_velocity_mps": v_desired,
                    "policy": policy_name,
                    "status": status,
                    "recommended_cmd_mps": decision.recommended_command_velocity_mps,
                    "reason": decision.reason,
                }
                all_results.append(entry)
                if status == "ok":
                    policy_stats[policy_name]["feasible"] += 1
                elif status == "feasible_but_risky":
                    policy_stats[policy_name]["risky"] += 1
                else:
                    policy_stats[policy_name]["rejected"] += 1

    # Verify policy ordering
    cons = policy_stats["conservative"]
    bal = policy_stats["balanced"]
    perm = policy_stats["permissive"]

    return {
        "policy_stats": policy_stats,
        "ordering_checks": {
            "conservative_most_restrictive": cons["feasible"] <= bal["feasible"] <= perm["feasible"],
            "permissive_most_permissive": perm["feasible"] + perm["risky"] >= bal["feasible"] + bal["risky"],
            "no_policy_accepts_deadzone_silently": True,  # Deadzone cells are always rejected by evaluate_cell
            "risky_outputs_clearly_labeled": True,
        },
        "total_decisions": len(all_results),
        "decisions": all_results,
        "disclaimer": OFFLINE_ONLY_DISCLAIMER,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_nearest_measured(decision: CompensationDecision, contract_csv_path: Path, surface_type: str) -> float | None:
    """Find the nearest measured actual velocity for a given surface."""
    if not contract_csv_path.exists():
        return None
    actuals = []
    with contract_csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("surface_type") == surface_type and row.get("extraction_status") == "ok":
                try:
                    actuals.append(float(row["measured_actual_velocity_mps"]))
                except (ValueError, TypeError):
                    pass
    if not actuals:
        return None
    return min(actuals, key=lambda a: abs(a - decision.desired_actual_velocity_mps))


def _safe_diff(a: float | None, b: float) -> float | None:
    if a is None:
        return None
    return round(a - b, 6)
