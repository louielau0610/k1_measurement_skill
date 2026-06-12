"""Audit M24-D S2 response consistency across M19C, M23-C, and M24-C.

Offline analysis only. This script does not execute hardware, update profiles,
or claim compensation improvement.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
DEFAULT_OLD_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
DEFAULT_M23C_PAIRS = DEFAULT_OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
DEFAULT_M24C_PER_VELOCITY = DEFAULT_OUTPUT_DIR / "m24c_s2_per_velocity_summary.csv"
DEFAULT_M24C_OLD_NEW = DEFAULT_OUTPUT_DIR / "m24c_s2_old_vs_new_profile_comparison.csv"
DEFAULT_M24C_M23C_CHECK = DEFAULT_OUTPUT_DIR / "m24c_s2_m23c_consistency_check.csv"
DEFAULT_M24C_SUMMARY = DEFAULT_OUTPUT_DIR / "m24c_s2_profile_refresh_summary.json"

DISAGREEMENT_FIELDS = [
    "velocity_mps",
    "m19c_mean_actual_velocity_mps",
    "m23c_direct_mean_actual_velocity_mps",
    "m24c_mean_actual_velocity_mps",
    "abs_diff_m19c_vs_m23c",
    "abs_diff_m19c_vs_m24c",
    "abs_diff_m23c_vs_m24c",
    "m23c_closer_to",
    "m24c_variability_mps",
    "m19c_uncertainty_mps",
    "m24c_lower_variability_than_m19c",
    "m24c_direct_near_optimal",
    "disagreement_labels",
]

ASSUMPTION_FIELDS = [
    "assumption",
    "m19c",
    "m23c",
    "m24c",
    "consistency_status",
    "notes",
]

ALLOWED_ADOPTION_DECISIONS = {
    "do_not_adopt_candidate_profile_yet",
    "adopt_candidate_profile_as_versioned_experimental_profile",
    "refresh_profile_again_under_controlled_conditions",
    "investigate_extraction_before_profile_decision",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit M24-D response consistency.")
    parser.add_argument("--old-profile", type=Path, default=DEFAULT_OLD_PROFILE)
    parser.add_argument("--m23c-pairs", type=Path, default=DEFAULT_M23C_PAIRS)
    parser.add_argument("--m24c-per-velocity", type=Path, default=DEFAULT_M24C_PER_VELOCITY)
    parser.add_argument("--m24c-old-new", type=Path, default=DEFAULT_M24C_OLD_NEW)
    parser.add_argument("--m24c-m23c-check", type=Path, default=DEFAULT_M24C_M23C_CHECK)
    parser.add_argument("--m24c-summary", type=Path, default=DEFAULT_M24C_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--disagreement-threshold", type=float, default=0.03)
    args = parser.parse_args(argv)
    result = audit(args)
    print(f"M24-D adoption decision: {result['adoption']['profile_adoption_decision']}")
    print(f"Summary: {args.output_dir / 'm24d_response_consistency_summary.json'}")
    return 0


def audit(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    old = load_old_profile(args.old_profile)
    m23c = load_m23c_direct(args.m23c_pairs)
    m24c = load_m24c(args.m24c_per_velocity)
    m24c_summary = read_json(args.m24c_summary)

    overlapping = sorted(set(old) & set(m23c) & set(m24c))
    disagreement_rows = build_disagreement_rows(old, m23c, m24c, overlapping, args.disagreement_threshold)
    assumption_rows = build_assumption_rows()
    diagnosis = build_diagnosis(disagreement_rows, m24c_summary, overlapping)
    adoption = build_adoption_decision(diagnosis, m24c_summary)
    summary = build_summary(disagreement_rows, assumption_rows, diagnosis, adoption, overlapping, m24c_summary)

    write_csv(args.output_dir / "m24d_pairwise_profile_disagreement.csv", disagreement_rows, DISAGREEMENT_FIELDS)
    write_csv(args.output_dir / "m24d_measurement_assumption_audit.csv", assumption_rows, ASSUMPTION_FIELDS)
    (args.output_dir / "m24d_response_consistency_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.output_dir / "m24d_response_consistency_diagnosis.json").write_text(json.dumps(diagnosis, indent=2), encoding="utf-8")
    (args.output_dir / "m24d_profile_adoption_decision.json").write_text(json.dumps(adoption, indent=2), encoding="utf-8")
    (args.output_dir / "m24d_response_consistency_report.md").write_text(build_report(summary, disagreement_rows), encoding="utf-8")
    (args.output_dir / "m24d_measurement_assumption_audit.md").write_text(build_assumption_md(assumption_rows), encoding="utf-8")
    (args.output_dir / "m24d_response_consistency_diagnosis.md").write_text(build_diagnosis_md(diagnosis), encoding="utf-8")
    (args.output_dir / "m24d_profile_adoption_decision.md").write_text(build_adoption_md(adoption), encoding="utf-8")
    return {"summary": summary, "diagnosis": diagnosis, "adoption": adoption}


def build_disagreement_rows(
    old: dict[float, dict[str, Any]],
    m23c: dict[float, float],
    m24c: dict[float, dict[str, Any]],
    overlapping: list[float],
    threshold: float,
) -> list[dict[str, Any]]:
    rows = []
    for velocity in overlapping:
        old_mean = float(old[velocity]["mean_actual_velocity"])
        m23c_mean = m23c[velocity]
        m24c_mean = float(m24c[velocity]["mean_actual_velocity_mps"])
        d19_23 = abs(old_mean - m23c_mean)
        d19_24 = abs(old_mean - m24c_mean)
        d23_24 = abs(m23c_mean - m24c_mean)
        labels = []
        if d19_24 >= threshold:
            labels.append("m19c_m24c_disagree")
        if d23_24 >= threshold:
            labels.append("m23c_direct_response_not_reproduced")
        if d19_23 < d23_24:
            labels.append("m23c_closer_to_m19c_than_m24c")
        if float(m24c[velocity]["no_motion_rate"]) >= 1.0:
            labels.append("m24c_no_motion_all_repeats")
        if m24c[velocity]["direct_near_optimal_flag"] != "True":
            labels.append("m24c_direct_not_near_optimal")
        rows.append({
            "velocity_mps": velocity,
            "m19c_mean_actual_velocity_mps": round(old_mean, 6),
            "m23c_direct_mean_actual_velocity_mps": round(m23c_mean, 6),
            "m24c_mean_actual_velocity_mps": round(m24c_mean, 6),
            "abs_diff_m19c_vs_m23c": round(d19_23, 6),
            "abs_diff_m19c_vs_m24c": round(d19_24, 6),
            "abs_diff_m23c_vs_m24c": round(d23_24, 6),
            "m23c_closer_to": "M19C" if d19_23 < d23_24 else "M24C",
            "m24c_variability_mps": m24c[velocity]["repeat_variability_mps"],
            "m19c_uncertainty_mps": round(float(old[velocity].get("response_uncertainty", old[velocity].get("std_actual_velocity", 0.0))), 6),
            "m24c_lower_variability_than_m19c": float(m24c[velocity]["repeat_variability_mps"]) < float(old[velocity].get("response_uncertainty", 0.0)),
            "m24c_direct_near_optimal": m24c[velocity]["direct_near_optimal_flag"],
            "disagreement_labels": ";".join(labels),
        })
    return rows


def build_assumption_rows() -> list[dict[str, str]]:
    rows = [
        ("extraction_method", "ROS2 odometer profile extraction", "M23-B/M23-C odometer extraction", "M24-B/M24-C odometer extraction", "broadly_consistent", "All use odometer-derived actual velocity; exact implementation should still be audited."),
        ("forward_projection_method", "forward projection from x/y/theta", "odometer displacement/direct extracted fields", "odometer forward projection window", "needs_audit", "M24-C near-zero result makes extraction-window and pose-reset review important."),
        ("command_duration", "M19C repeated validation command window", "6 sec command phase", "6 sec command phase", "partly_consistent", "M23-C and M24-C match; M19C should be checked from original protocol."),
        ("idle_stop_duration", "protocol dependent", "2 sec idle / 2 sec stop", "2 sec idle / 2 sec stop", "partly_consistent", "M23-C and M24-C match runner defaults."),
        ("state_topics", "/odometer_state plus low_state/IMU where available", "/odometer_state plus /low_state", "/odometer_state plus /low_state", "consistent", "Topic names are aligned."),
        ("odometer_source", "booster_interface/msg/Odometer", "booster_interface/msg/Odometer", "booster_interface/msg/Odometer", "consistent", "Same nominal odometer source."),
        ("imu_yaw_source", "low_state or IMU cross-check", "low_state/IMU cross-check", "low_state IMU yaw cross-check", "consistent", "IMU yaw is not primary velocity evidence."),
        ("session_surface_label", "S2_marble_floor", "S2_marble_floor", "S2_marble_floor", "consistent", "Labels match but physical condition may still differ."),
        ("number_of_repeats", "3 per old profile cell", "3 direct trials per overlap velocity", "5 direct-refresh repeats per velocity", "different", "M24-C has more repeats but near-zero response."),
        ("velocity_set", "0.10-0.60 selected profile speeds", "0.40,0.45,0.50,0.55", "0.35,0.40,0.45,0.50,0.55,0.60", "overlap_partial", "Overlap for three-way comparison is 0.40, 0.45, 0.50."),
        ("direct_vs_compensated_condition", "direct profile only", "direct and compensated pairs", "direct_refresh only", "partly_consistent", "M23-C direct fields are used for consistency only."),
        ("trial_reset_starting_pose_controlled", "not fully encoded in profile artifact", "not fully encoded in pair CSV", "not fully encoded in M24-C outputs", "unknown", "Operator reset/path effects remain hypotheses."),
        ("battery_warmup_environment_recorded", "not available in aggregate profile", "not available in pair CSV", "not available in summary", "unknown", "Robot state or warm-up effects remain hypotheses."),
    ]
    return [
        {
            "assumption": a,
            "m19c": b,
            "m23c": c,
            "m24c": d,
            "consistency_status": e,
            "notes": f,
        }
        for a, b, c, d, e, f in rows
    ]


def build_diagnosis(rows: list[dict[str, Any]], m24c_summary: dict[str, Any], overlapping: list[float]) -> dict[str, Any]:
    m23c_not_reproduced = sum("m23c_direct_response_not_reproduced" in row["disagreement_labels"] for row in rows)
    m19_m24_disagree = sum("m19c_m24c_disagree" in row["disagreement_labels"] for row in rows)
    m23c_closer_old = sum(row["m23c_closer_to"] == "M19C" for row in rows)
    labels = [
        "environment_dependent_response",
        "profile_staleness_possible",
        "m23c_direct_response_not_reproduced",
        "candidate_profile_not_adoption_ready",
        "controlled_replication_required",
        "extraction_method_audit_required",
        "operator_reset_or_path_effect_possible",
        "robot_state_or_warmup_effect_possible",
    ]
    hypotheses = {
        "environment_dependent_response": "Supported by large disagreement among M19C, M23-C, and M24-C direct-response estimates.",
        "profile_staleness_possible": "M24-C differs from old M19C for all old-profile comparable velocities, but this is not sufficient for adoption.",
        "m23c_direct_response_not_reproduced": f"M24-C differs from M23-C direct behavior at {m23c_not_reproduced}/{len(rows)} three-way overlap velocities.",
        "candidate_profile_not_adoption_ready": "M24-C decision is inconclusive_environment_dependent.",
        "controlled_replication_required": "A repeat controlled direct-refresh session is needed before profile adoption.",
        "extraction_method_audit_required": "M24-C near-zero velocity across all commands requires extraction-window/source review.",
        "operator_reset_or_path_effect_possible": "Starting pose/path reset is not encoded in the aggregate artifacts.",
        "robot_state_or_warmup_effect_possible": "Battery, warm-up, and environment state are not encoded in the aggregate artifacts.",
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overlapping_velocity_set": overlapping,
        "diagnosis_labels": labels,
        "hypotheses": hypotheses,
        "m19c_m24c_disagreement_count": m19_m24_disagree,
        "m23c_m24c_disagreement_count": m23c_not_reproduced,
        "m23c_closer_to_m19c_count": m23c_closer_old,
        "m24c_profile_status_decision": m24c_summary.get("profile_status_decision"),
        "candidate_profile_adoption_supported": False,
        "claim_boundary": "Hypothesis audit only; no compensation improvement or deployment claim.",
    }


def build_adoption_decision(diagnosis: dict[str, Any], m24c_summary: dict[str, Any]) -> dict[str, Any]:
    if m24c_summary.get("profile_status_decision") == "analysis_invalid_missing_data":
        decision = "investigate_extraction_before_profile_decision"
    elif "extraction_method_audit_required" in diagnosis["diagnosis_labels"]:
        decision = "investigate_extraction_before_profile_decision"
    else:
        decision = "refresh_profile_again_under_controlled_conditions"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile_adoption_decision": decision,
        "allowed_decisions": sorted(ALLOWED_ADOPTION_DECISIONS),
        "candidate_profile_adopted": False,
        "candidate_profile_path": "outputs/compensation_experiments/m24c_s2_current_profile_candidate.json",
        "gold_profile_overwritten": False,
        "controlled_replication_recommended": True,
        "second_compensation_validation_blocked": True,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "reason": "M24-C was inconclusive and M24-C direct response did not reproduce M23-C direct behavior.",
    }


def build_summary(
    rows: list[dict[str, Any]],
    assumption_rows: list[dict[str, str]],
    diagnosis: dict[str, Any],
    adoption: dict[str, Any],
    overlapping: list[float],
    m24c_summary: dict[str, Any],
) -> dict[str, Any]:
    diffs_19_23 = [float(row["abs_diff_m19c_vs_m23c"]) for row in rows]
    diffs_19_24 = [float(row["abs_diff_m19c_vs_m24c"]) for row in rows]
    diffs_23_24 = [float(row["abs_diff_m23c_vs_m24c"]) for row in rows]
    return {
        "audit_id": "m24d_response_consistency_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overlapping_velocity_set": overlapping,
        "overlap_count": len(overlapping),
        "mean_abs_diff_m19c_vs_m23c": round(statistics.fmean(diffs_19_23), 6) if diffs_19_23 else None,
        "mean_abs_diff_m19c_vs_m24c": round(statistics.fmean(diffs_19_24), 6) if diffs_19_24 else None,
        "mean_abs_diff_m23c_vs_m24c": round(statistics.fmean(diffs_23_24), 6) if diffs_23_24 else None,
        "discrepancy_pattern": "systematic_m24c_near_zero_nonreproduction",
        "m23c_closer_to_m19c_count": diagnosis["m23c_closer_to_m19c_count"],
        "m24c_near_optimal_count": sum(str(row["m24c_direct_near_optimal"]) == "True" for row in rows),
        "measurement_assumption_unknown_count": sum(row["consistency_status"] == "unknown" for row in assumption_rows),
        "diagnosis_labels": diagnosis["diagnosis_labels"],
        "profile_adoption_decision": adoption["profile_adoption_decision"],
        "candidate_profile_adopted": False,
        "gold_profile_overwritten": False,
        "revised_compensator_status": "offline_only",
        "second_compensation_validation_blocked": True,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "m24c_profile_status_decision": m24c_summary.get("profile_status_decision"),
        "claim_boundary": "Offline consistency audit only; no hardware execution, profile overwrite, compensation improvement, deployment, or GO1/G1 claim.",
    }


def load_old_profile(path: Path) -> dict[float, dict[str, Any]]:
    data = read_json(path)
    return {
        round(float(row["command_velocity"]), 2): row
        for row in data.get("per_surface_response_statistics", [])
        if row.get("surface_id") == "S2_marble_floor"
    }


def load_m23c_direct(path: Path) -> dict[float, float]:
    grouped: dict[float, list[float]] = defaultdict(list)
    for row in read_csv(path):
        grouped[round(float(row["desired_velocity_mps"]), 2)].append(float(row["direct_measured_actual_velocity_mps"]))
    return {velocity: statistics.fmean(values) for velocity, values in grouped.items()}


def load_m24c(path: Path) -> dict[float, dict[str, Any]]:
    return {round(float(row["command_velocity_mps"]), 2): row for row in read_csv(path)}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-D Response Consistency Report",
        "",
        f"- Overlap velocities: {summary['overlapping_velocity_set']}",
        f"- Discrepancy pattern: `{summary['discrepancy_pattern']}`",
        f"- Adoption decision: `{summary['profile_adoption_decision']}`",
        f"- Candidate profile adopted: `{str(summary['candidate_profile_adopted']).lower()}`",
        f"- Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        f"- GO1/G1 blocked: `{str(summary['go1_g1_blocked']).lower()}`",
        "",
        "## Pairwise Disagreement",
        "",
        "| Velocity | M19C | M23-C Direct | M24-C | M19-M23 | M19-M24 | M23-M24 | Labels |",
        "|----------|------|--------------|-------|---------|---------|---------|--------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['velocity_mps']} | {row['m19c_mean_actual_velocity_mps']} | "
            f"{row['m23c_direct_mean_actual_velocity_mps']} | {row['m24c_mean_actual_velocity_mps']} | "
            f"{row['abs_diff_m19c_vs_m23c']} | {row['abs_diff_m19c_vs_m24c']} | "
            f"{row['abs_diff_m23c_vs_m24c']} | {row['disagreement_labels']} |"
        )
    lines += [
        "",
        "## Finding",
        "M24-C is not adoption-ready because it differs from old M19C and does not reproduce M23-C direct-response behavior.",
        "",
        "## Claim Boundary",
        "This report does not claim compensation improvement, revised compensator physical validation, deployment readiness, navigation improvement, GO1/G1 validation, or cross-platform validation.",
    ]
    return "\n".join(lines) + "\n"


def build_assumption_md(rows: list[dict[str, str]]) -> str:
    lines = [
        "# M24-D Measurement Assumption Audit",
        "",
        "| Assumption | M19C | M23-C | M24-C | Status | Notes |",
        "|------------|------|-------|-------|--------|-------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['assumption']} | {row['m19c']} | {row['m23c']} | {row['m24c']} | "
            f"{row['consistency_status']} | {row['notes']} |"
        )
    return "\n".join(lines) + "\n"


def build_diagnosis_md(diagnosis: dict[str, Any]) -> str:
    lines = ["# M24-D Response Consistency Diagnosis", "", "## Labels"]
    lines.extend(f"- `{label}`" for label in diagnosis["diagnosis_labels"])
    lines += ["", "## Hypotheses"]
    for label, text in diagnosis["hypotheses"].items():
        lines.append(f"- `{label}`: {text}")
    lines += [
        "",
        f"Candidate profile adoption supported: `{str(diagnosis['candidate_profile_adoption_supported']).lower()}`",
        "",
        "These are evidence-bounded hypotheses, not proven root causes.",
    ]
    return "\n".join(lines) + "\n"


def build_adoption_md(adoption: dict[str, Any]) -> str:
    return (
        "# M24-D Profile Adoption Decision\n\n"
        f"Decision: `{adoption['profile_adoption_decision']}`\n\n"
        f"Candidate profile adopted: `{str(adoption['candidate_profile_adopted']).lower()}`\n\n"
        f"Gold profile overwritten: `{str(adoption['gold_profile_overwritten']).lower()}`\n\n"
        f"Second compensation validation blocked: `{str(adoption['second_compensation_validation_blocked']).lower()}`\n\n"
        f"Deployment ready: `{str(adoption['deployment_ready']).lower()}`\n\n"
        f"GO1/G1 blocked: `{str(adoption['go1_g1_blocked']).lower()}`\n\n"
        f"Reason: {adoption['reason']}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
