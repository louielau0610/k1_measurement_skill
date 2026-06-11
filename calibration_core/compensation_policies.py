"""Risk policies for offline velocity compensation."""
from __future__ import annotations

from calibration_core.compensation_models import CompensationPolicy, CompensationThresholds, ResponseCell

POLICIES = {
    "conservative": CompensationPolicy(
        name="conservative",
        accepted_labels=("reliable",),
        max_risk_score=0.3,
        min_confidence=0.5,
        max_yaw_drift_deg=5.0,
        max_uncertainty_mps=0.08,
        min_repeats=3,
        status_for_success="ok",
    ),
    "balanced": CompensationPolicy(
        name="balanced",
        accepted_labels=("reliable", "under_track"),
        max_risk_score=0.6,
        min_confidence=0.3,
        max_yaw_drift_deg=10.0,
        max_uncertainty_mps=0.12,
        min_repeats=2,
        status_for_success="ok",
    ),
    "permissive": CompensationPolicy(
        name="permissive",
        accepted_labels=("reliable", "under_track", "unstable", "drift_prone"),
        max_risk_score=1.0,
        min_confidence=0.0,
        max_yaw_drift_deg=999.0,
        max_uncertainty_mps=999.0,
        min_repeats=1,
        status_for_success="feasible_but_risky",
    ),
}


def get_policy(name: str) -> CompensationPolicy | None:
    return POLICIES.get(name)


def estimate_confidence(cell: ResponseCell, thresholds: CompensationThresholds = CompensationThresholds()) -> float:
    risk_component = max(0.0, 1.0 - min(cell.risk_score, 1.0))
    uncertainty_component = max(0.0, 1.0 - min(cell.response_uncertainty / thresholds.uncertainty_high_threshold_mps, 1.0))
    yaw_component = max(0.0, 1.0 - min(cell.mean_yaw_drift_deg / thresholds.yaw_drift_high_threshold_deg, 1.0))
    repeat_component = min(cell.n / thresholds.minimum_cell_repeats, 1.0)
    return round(min(risk_component, uncertainty_component, yaw_component, repeat_component), 6)


def evaluate_cell(
    cell: ResponseCell,
    policy: CompensationPolicy,
    thresholds: CompensationThresholds = CompensationThresholds(),
    minimum_confidence: float | None = None,
) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    min_confidence = policy.min_confidence if minimum_confidence is None else max(policy.min_confidence, minimum_confidence)
    if cell.region_label in {"deadzone", "unclassified"}:
        return False, [f"rejected region_label={cell.region_label}"]
    if cell.n < policy.min_repeats:
        return False, [f"rejected n={cell.n} below policy minimum {policy.min_repeats}"]
    if cell.no_motion_ratio > 0 and not policy.allow_deadzone:
        return False, [f"rejected no_motion_ratio={cell.no_motion_ratio}"]
    if cell.region_label not in policy.accepted_labels:
        return False, [f"rejected region_label={cell.region_label} under {policy.name} policy"]
    if cell.risk_score > policy.max_risk_score:
        return False, [f"rejected risk_score={cell.risk_score:.3f} above {policy.max_risk_score:.3f}"]
    if cell.mean_yaw_drift_deg > policy.max_yaw_drift_deg:
        return False, [f"rejected yaw_drift={cell.mean_yaw_drift_deg:.3f} above {policy.max_yaw_drift_deg:.3f}"]
    if cell.response_uncertainty > policy.max_uncertainty_mps:
        return False, [
            f"rejected response_uncertainty={cell.response_uncertainty:.3f} above {policy.max_uncertainty_mps:.3f}"
        ]
    if cell.confidence < min_confidence:
        return False, [f"rejected confidence={cell.confidence:.3f} below {min_confidence:.3f}"]
    if policy.name in {"balanced", "permissive"}:
        if cell.region_label != "reliable":
            warnings.append(f"accepted non-reliable region_label={cell.region_label}")
        if cell.mean_yaw_drift_deg > thresholds.yaw_drift_high_threshold_deg:
            warnings.append(f"moderate/high yaw drift {cell.mean_yaw_drift_deg:.3f} deg")
        if cell.response_uncertainty > thresholds.uncertainty_high_threshold_mps / 2.0:
            warnings.append(f"elevated response uncertainty {cell.response_uncertainty:.3f} m/s")
    return True, warnings
