"""Analyze M24-C S2 current-condition profile refresh results.

This script ingests the clean M24-B direct-refresh session, compares the
refreshed direct response against the old M19C S2 profile and M23-C direct
evidence, and writes a candidate current S2 profile. It never overwrites the
K1 gold profile.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_ID = "m24b_s2_profile_refresh_clean_20260612_145358"
PARTIAL_DEBUG_SESSION_ID = "m24b_s2_profile_refresh_20260612_143912"
ARCHIVE = Path("m24b_s2_profile_refresh_results_m24b_s2_profile_refresh_clean_20260612_145358.tar.gz")
DEFAULT_SESSION_DIR = Path("data/compensation_experiments/m24b_s2_profile_refresh") / SESSION_ID
DEFAULT_OLD_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
DEFAULT_M23C_PAIRS = Path("outputs/compensation_experiments/m23c_k1_before_after_pairs.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
EXPECTED_VELOCITIES = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
ALLOWED_DECISIONS = {
    "old_profile_stale_current_s2_profile_needed",
    "old_profile_confirmed_current",
    "inconclusive_environment_dependent",
    "analysis_invalid_missing_data",
}

PER_VELOCITY_FIELDS = [
    "surface",
    "condition",
    "command_velocity_mps",
    "desired_velocity_mps",
    "n",
    "mean_actual_velocity_mps",
    "median_actual_velocity_mps",
    "std_actual_velocity_mps",
    "min_actual_velocity_mps",
    "max_actual_velocity_mps",
    "mean_tracking_error_mps",
    "mean_abs_tracking_error_mps",
    "median_abs_tracking_error_mps",
    "max_abs_tracking_error_mps",
    "mean_yaw_drift_deg",
    "median_yaw_drift_deg",
    "max_yaw_drift_deg",
    "mean_imu_yaw_drift_deg",
    "no_motion_rate",
    "repeat_variability_mps",
    "repeat_variability_flag",
    "direct_near_optimal_flag",
]

OLD_NEW_FIELDS = [
    "command_velocity_mps",
    "old_m19c_s2_mean_actual_velocity_mps",
    "new_m24c_mean_actual_velocity_mps",
    "difference_mps",
    "absolute_difference_mps",
    "old_uncertainty_mps",
    "new_uncertainty_mps",
    "profile_mismatch_threshold_mps",
    "profile_mismatch_flag",
    "old_profile_available",
    "comparison_status",
]

M23C_FIELDS = [
    "desired_velocity_mps",
    "m23c_direct_mean_actual_velocity_mps",
    "m24c_refresh_mean_actual_velocity_mps",
    "old_m19c_s2_mean_actual_velocity_mps",
    "abs_diff_m24c_vs_m23c",
    "abs_diff_m24c_vs_m19c",
    "m24c_matches_m23c_better_than_m19c",
    "consistent_with_profile_staleness",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze M24-C S2 profile refresh results.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION_DIR)
    parser.add_argument("--old-profile", type=Path, default=DEFAULT_OLD_PROFILE)
    parser.add_argument("--m23c-pairs", type=Path, default=DEFAULT_M23C_PAIRS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--profile-mismatch-threshold", type=float, default=0.03)
    parser.add_argument("--near-optimal-threshold", type=float, default=0.02)
    parser.add_argument("--m23c-consistency-threshold", type=float, default=0.03)
    args = parser.parse_args(argv)

    result = analyze(
        session_dir=args.session_dir,
        old_profile=args.old_profile,
        m23c_pairs=args.m23c_pairs,
        output_dir=args.output_dir,
        archive=args.archive,
        profile_mismatch_threshold=args.profile_mismatch_threshold,
        near_optimal_threshold=args.near_optimal_threshold,
        m23c_consistency_threshold=args.m23c_consistency_threshold,
    )
    print(f"M24-C profile decision: {result['summary']['profile_status_decision']}")
    print(f"Summary: {args.output_dir / 'm24c_s2_profile_refresh_summary.json'}")
    return 0 if result["summary"]["profile_status_decision"] != "analysis_invalid_missing_data" else 1


def analyze(
    *,
    session_dir: Path,
    old_profile: Path,
    m23c_pairs: Path,
    output_dir: Path,
    archive: Path,
    profile_mismatch_threshold: float,
    near_optimal_threshold: float,
    m23c_consistency_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = read_csv(session_dir / "extracted_results.csv")
    records = read_csv(session_dir / "trial_records.csv")
    qc_summary = read_json(session_dir / "qc_summary.json")
    run_summary = read_json(session_dir / "run_summary.json")
    metadata = read_json(session_dir / "session_metadata.json")
    validation = validate_session(session_dir, extracted, records, qc_summary, run_summary, metadata)

    old_profile_rows = load_old_profile(old_profile)
    m23c_direct = load_m23c_direct(m23c_pairs)
    per_velocity = build_per_velocity(extracted, near_optimal_threshold)
    old_new = build_old_new_comparison(per_velocity, old_profile_rows, profile_mismatch_threshold)
    m23c_check = build_m23c_check(per_velocity, old_profile_rows, m23c_direct, m23c_consistency_threshold, profile_mismatch_threshold)
    decision = decide(validation, old_new, m23c_check)

    summary = build_summary(
        session_dir=session_dir,
        validation=validation,
        run_summary=run_summary,
        per_velocity=per_velocity,
        old_new=old_new,
        m23c_check=m23c_check,
        decision=decision,
        profile_mismatch_threshold=profile_mismatch_threshold,
        near_optimal_threshold=near_optimal_threshold,
        m23c_consistency_threshold=m23c_consistency_threshold,
    )
    candidate = build_candidate_profile(summary, per_velocity)
    ingestion = build_ingestion_summary(archive, session_dir)

    write_csv(output_dir / "m24c_s2_per_velocity_summary.csv", per_velocity, PER_VELOCITY_FIELDS)
    write_csv(output_dir / "m24c_s2_old_vs_new_profile_comparison.csv", old_new, OLD_NEW_FIELDS)
    write_csv(output_dir / "m24c_s2_m23c_consistency_check.csv", m23c_check, M23C_FIELDS)
    (output_dir / "m24c_s2_profile_refresh_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m24c_s2_current_profile_candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")
    (output_dir / "m24c_ingestion_summary.json").write_text(json.dumps(ingestion, indent=2), encoding="utf-8")
    (output_dir / "m24c_s2_profile_refresh_report.md").write_text(build_report(summary, per_velocity, old_new, m23c_check), encoding="utf-8")
    (output_dir / "m24c_s2_profile_status_decision.md").write_text(build_decision_md(summary), encoding="utf-8")
    (output_dir / "m24c_s2_current_profile_candidate.md").write_text(build_candidate_md(candidate), encoding="utf-8")
    (output_dir / "m24c_ingestion_summary.md").write_text(build_ingestion_md(ingestion), encoding="utf-8")
    return {"summary": summary, "candidate": candidate, "ingestion": ingestion}


def validate_session(
    session_dir: Path,
    extracted: list[dict[str, str]],
    records: list[dict[str, str]],
    qc_summary: dict[str, Any],
    run_summary: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    required = ["trial_records.csv", "extracted_results.csv", "extraction_summary.json", "qc_summary.json", "state_logs"]
    for name in required:
        if not (session_dir / name).exists():
            errors.append(f"missing_required_session_file:{name}")
    if session_dir.name != SESSION_ID or metadata.get("session_id") != SESSION_ID:
        errors.append(f"unexpected_session_id:{session_dir.name}:{metadata.get('session_id')}")
    if PARTIAL_DEBUG_SESSION_ID in str(session_dir):
        errors.append("partial_debug_session_used")

    executed = [row for row in records if row.get("physical_run_status") == "executed" and row.get("valid", "").lower() == "true"]
    skipped = [row for row in records if row.get("physical_run_status") == "skipped"]
    invalid = [row for row in records if row.get("valid", "").lower() != "true"]
    surfaces = {row.get("surface") for row in records + extracted}
    conditions = {row.get("condition") for row in records}
    commands = sorted({round(float(row["command_velocity_mps"]), 2) for row in records if row.get("command_velocity_mps")})
    repeat_counts = Counter(round(float(row["command_velocity_mps"]), 2) for row in records if row.get("command_velocity_mps"))
    missing_measured = [row.get("trial_id", "?") for row in extracted if blank(row.get("measured_actual_velocity_mps"))]
    missing_yaw = [row.get("trial_id", "?") for row in extracted if blank(row.get("yaw_drift_deg"))]
    bad_status = [row.get("trial_id", "?") for row in extracted if row.get("extraction_status") != "ok"]
    if len(records) != 30:
        errors.append(f"planned_trial_count:{len(records)}")
    if len(executed) != 30:
        errors.append(f"executed_trial_count:{len(executed)}")
    if skipped:
        errors.append(f"skipped_trial_count:{len(skipped)}")
    if invalid:
        errors.append(f"invalid_trial_count:{len(invalid)}")
    if surfaces != {"S2_marble_floor"}:
        errors.append(f"unexpected_surfaces:{sorted(surfaces)}")
    if conditions != {"direct_refresh"}:
        errors.append(f"unexpected_conditions:{sorted(conditions)}")
    if commands != EXPECTED_VELOCITIES:
        errors.append(f"unexpected_command_velocities:{commands}")
    bad_repeats = {str(k): v for k, v in repeat_counts.items() if v != 5}
    if bad_repeats or len(repeat_counts) != 6:
        errors.append(f"bad_repeat_counts:{bad_repeats}")
    if len(extracted) != 30:
        errors.append(f"extraction_row_count:{len(extracted)}")
    if missing_measured:
        errors.append(f"missing_measured_actual_velocity:{missing_measured[:5]}")
    if missing_yaw:
        errors.append(f"missing_yaw_drift:{missing_yaw[:5]}")
    if bad_status:
        errors.append(f"non_ok_extraction_status:{bad_status[:5]}")
    if qc_summary.get("overall_pass") is not True:
        errors.append("qc_summary_not_passed")
    if run_summary.get("executed") != 30 or run_summary.get("skipped") != 0 or run_summary.get("invalid") != 0:
        errors.append(f"run_summary_counts:{run_summary}")

    return {
        "passed": not errors,
        "errors": errors,
        "trial_count": len(records),
        "extracted_row_count": len(extracted),
        "executed_count": len(executed),
        "skipped_count": len(skipped),
        "invalid_count": len(invalid),
        "surface_values": sorted(surfaces),
        "condition_values": sorted(conditions),
        "command_velocities_mps": commands,
        "velocity_group_count": len(repeat_counts),
        "repeats_per_velocity": dict(sorted((f"{k:.2f}", v) for k, v in repeat_counts.items())),
        "qc_overall_pass": qc_summary.get("overall_pass"),
    }


def build_per_velocity(rows: list[dict[str, str]], near_optimal_threshold: float) -> list[dict[str, Any]]:
    grouped: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[round(float(row["command_velocity_mps"]), 2)].append(row)
    output = []
    for command in sorted(grouped):
        group = grouped[command]
        measured = [float(row["measured_actual_velocity_mps"]) for row in group]
        desired = [float(row["desired_velocity_mps"]) for row in group]
        tracking = [m - d for m, d in zip(measured, desired)]
        abs_tracking = [abs(value) for value in tracking]
        yaw = [float(row["yaw_drift_deg"]) for row in group]
        imu_yaw = [float(row["imu_yaw_drift_deg"]) for row in group if not blank(row.get("imu_yaw_drift_deg"))]
        std_actual = sample_std(measured)
        mean_abs = statistics.fmean(abs_tracking)
        output.append({
            "surface": "S2_marble_floor",
            "condition": "direct_refresh",
            "command_velocity_mps": command,
            "desired_velocity_mps": round(statistics.fmean(desired), 2),
            "n": len(group),
            "mean_actual_velocity_mps": round(statistics.fmean(measured), 6),
            "median_actual_velocity_mps": round(statistics.median(measured), 6),
            "std_actual_velocity_mps": round(std_actual, 6),
            "min_actual_velocity_mps": round(min(measured), 6),
            "max_actual_velocity_mps": round(max(measured), 6),
            "mean_tracking_error_mps": round(statistics.fmean(tracking), 6),
            "mean_abs_tracking_error_mps": round(mean_abs, 6),
            "median_abs_tracking_error_mps": round(statistics.median(abs_tracking), 6),
            "max_abs_tracking_error_mps": round(max(abs_tracking), 6),
            "mean_yaw_drift_deg": round(statistics.fmean(yaw), 6),
            "median_yaw_drift_deg": round(statistics.median(yaw), 6),
            "max_yaw_drift_deg": round(max(yaw), 6),
            "mean_imu_yaw_drift_deg": "" if not imu_yaw else round(statistics.fmean(imu_yaw), 6),
            "no_motion_rate": round(sum(1 for value in measured if abs(value) < 0.02) / len(measured), 6),
            "repeat_variability_mps": round(std_actual, 6),
            "repeat_variability_flag": std_actual >= 0.03,
            "direct_near_optimal_flag": mean_abs <= near_optimal_threshold,
        })
    return output


def build_old_new_comparison(
    per_velocity: list[dict[str, Any]],
    old_profile: dict[float, dict[str, Any]],
    threshold: float,
) -> list[dict[str, Any]]:
    rows = []
    for new in per_velocity:
        command = float(new["command_velocity_mps"])
        old = old_profile.get(round(command, 2))
        if old is None:
            rows.append({
                "command_velocity_mps": command,
                "old_m19c_s2_mean_actual_velocity_mps": "",
                "new_m24c_mean_actual_velocity_mps": new["mean_actual_velocity_mps"],
                "difference_mps": "",
                "absolute_difference_mps": "",
                "old_uncertainty_mps": "",
                "new_uncertainty_mps": new["std_actual_velocity_mps"],
                "profile_mismatch_threshold_mps": threshold,
                "profile_mismatch_flag": "",
                "old_profile_available": False,
                "comparison_status": "old_velocity_unavailable",
            })
            continue
        diff = float(new["mean_actual_velocity_mps"]) - float(old["mean_actual_velocity"])
        abs_diff = abs(diff)
        rows.append({
            "command_velocity_mps": command,
            "old_m19c_s2_mean_actual_velocity_mps": round(float(old["mean_actual_velocity"]), 6),
            "new_m24c_mean_actual_velocity_mps": new["mean_actual_velocity_mps"],
            "difference_mps": round(diff, 6),
            "absolute_difference_mps": round(abs_diff, 6),
            "old_uncertainty_mps": round(float(old.get("response_uncertainty", old.get("std_actual_velocity", 0.0))), 6),
            "new_uncertainty_mps": new["std_actual_velocity_mps"],
            "profile_mismatch_threshold_mps": threshold,
            "profile_mismatch_flag": abs_diff >= threshold,
            "old_profile_available": True,
            "comparison_status": "compared",
        })
    return rows


def build_m23c_check(
    per_velocity: list[dict[str, Any]],
    old_profile: dict[float, dict[str, Any]],
    m23c_direct: dict[float, float],
    m23c_threshold: float,
    profile_threshold: float,
) -> list[dict[str, Any]]:
    rows = []
    per_map = {round(float(row["desired_velocity_mps"]), 2): row for row in per_velocity}
    for velocity in sorted(set(per_map) & set(m23c_direct)):
        new_mean = float(per_map[velocity]["mean_actual_velocity_mps"])
        m23c_mean = m23c_direct[velocity]
        old = old_profile.get(velocity)
        old_mean = None if old is None else float(old["mean_actual_velocity"])
        diff_m23c = abs(new_mean - m23c_mean)
        diff_old = "" if old_mean is None else abs(new_mean - old_mean)
        matches_m23c_better = False if old_mean is None else diff_m23c < float(diff_old)
        differs_from_old = False if old_mean is None else float(diff_old) >= profile_threshold
        consistent = diff_m23c <= m23c_threshold and differs_from_old
        rows.append({
            "desired_velocity_mps": velocity,
            "m23c_direct_mean_actual_velocity_mps": round(m23c_mean, 6),
            "m24c_refresh_mean_actual_velocity_mps": round(new_mean, 6),
            "old_m19c_s2_mean_actual_velocity_mps": "" if old_mean is None else round(old_mean, 6),
            "abs_diff_m24c_vs_m23c": round(diff_m23c, 6),
            "abs_diff_m24c_vs_m19c": "" if old_mean is None else round(float(diff_old), 6),
            "m24c_matches_m23c_better_than_m19c": matches_m23c_better,
            "consistent_with_profile_staleness": consistent,
        })
    return rows


def decide(validation: dict[str, Any], old_new: list[dict[str, Any]], m23c_check: list[dict[str, Any]]) -> str:
    if not validation["passed"]:
        return "analysis_invalid_missing_data"
    comparable = [row for row in old_new if row["old_profile_available"] is True]
    if not comparable:
        return "analysis_invalid_missing_data"
    mismatch_count = sum(1 for row in comparable if row["profile_mismatch_flag"] is True)
    confirmed_count = len(comparable) - mismatch_count
    m23c_overlap = len(m23c_check)
    m23c_consistent = sum(1 for row in m23c_check if row["consistent_with_profile_staleness"] is True)
    most_comparable = len(comparable) // 2 + 1
    most_m23c = m23c_overlap // 2 + 1 if m23c_overlap else 999
    if mismatch_count >= most_comparable and m23c_consistent >= most_m23c:
        return "old_profile_stale_current_s2_profile_needed"
    if confirmed_count >= most_comparable:
        return "old_profile_confirmed_current"
    return "inconclusive_environment_dependent"


def build_summary(
    *,
    session_dir: Path,
    validation: dict[str, Any],
    run_summary: dict[str, Any],
    per_velocity: list[dict[str, Any]],
    old_new: list[dict[str, Any]],
    m23c_check: list[dict[str, Any]],
    decision: str,
    profile_mismatch_threshold: float,
    near_optimal_threshold: float,
    m23c_consistency_threshold: float,
) -> dict[str, Any]:
    old_available = [row for row in old_new if row["old_profile_available"] is True]
    mismatch_count = sum(1 for row in old_available if row["profile_mismatch_flag"] is True)
    m23c_matches = sum(1 for row in m23c_check if row["consistent_with_profile_staleness"] is True)
    next_map = {
        "old_profile_stale_current_s2_profile_needed": "M24-D current profile adoption plan and revised compensator rerun on candidate profile",
        "old_profile_confirmed_current": "Investigate M23-C discrepancy before another compensation validation",
        "inconclusive_environment_dependent": "Collect more controlled S2 refresh data before compensation validation",
        "analysis_invalid_missing_data": "Fix M24-B extraction/QC or rerun profile refresh",
    }
    return {
        "analysis_id": "m24c_s2_profile_refresh_analysis",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": SESSION_ID,
        "session_dir": str(session_dir),
        "trial_count": validation["trial_count"],
        "executed_count": validation["executed_count"],
        "skipped_count": validation["skipped_count"],
        "invalid_count": validation["invalid_count"],
        "velocity_group_count": validation["velocity_group_count"],
        "repeats_per_velocity": validation["repeats_per_velocity"],
        "profile_mismatch_count": mismatch_count,
        "old_profile_available_count": len(old_available),
        "m23c_overlap_count": len(m23c_check),
        "m24c_matches_m23c_count": m23c_matches,
        "profile_status_decision": decision,
        "candidate_profile_created": True,
        "candidate_profile_path": "outputs/compensation_experiments/m24c_s2_current_profile_candidate.json",
        "gold_profile_overwritten": False,
        "compensation_improvement_claimed": False,
        "revised_compensator_physical_validation_claimed": False,
        "deployment_ready": False,
        "navigation_improvement_claimed": False,
        "go1_g1_validation": False,
        "cross_platform_validation": False,
        "universal_k1_generalization": False,
        "thresholds": {
            "profile_mismatch_threshold_mps": profile_mismatch_threshold,
            "near_optimal_threshold_mps": near_optimal_threshold,
            "m23c_consistency_threshold_mps": m23c_consistency_threshold,
            "no_motion_threshold_mps": 0.02,
            "repeat_variability_metric": "sample standard deviation of measured actual velocity",
            "repeat_variability_flag_threshold_mps": 0.03,
        },
        "validation": validation,
        "run_summary": run_summary,
        "next_recommended_milestone": next_map[decision],
        "claim_boundary": "Direct-response profile refresh analysis only; no compensation improvement, deployment, navigation, GO1/G1, cross-platform, or universal K1 claim.",
    }


def build_candidate_profile(summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_label": "k1_s2_current_profile_candidate_m24c",
        "creation_milestone": "M24-C",
        "created_at": summary["generated_at"],
        "source_session_id": SESSION_ID,
        "source_trial_count": 30,
        "surface": "S2_marble_floor",
        "condition": "direct_refresh",
        "profile_status_decision": summary["profile_status_decision"],
        "thresholds_used": summary["thresholds"],
        "per_command_velocity_aggregates": rows,
        "warnings": [
            "not_gold_profile",
            "not_deployment_ready",
            "requires_review_before_adoption",
            "does_not_validate_compensation",
            "do_not_use_for_go1_g1",
        ],
        "gold_profile_overwritten": False,
        "deployment_ready": False,
    }


def build_ingestion_summary(archive: Path, session_dir: Path) -> dict[str, Any]:
    exists = archive.exists()
    return {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "archive_filename": archive.name,
        "archive_path": str(archive),
        "archive_size_bytes": archive.stat().st_size if exists else None,
        "archive_sha256": sha256_file(archive) if exists else None,
        "extracted_session_path": str(session_dir),
        "session_id": SESSION_ID,
        "clean_session_used": True,
        "partial_debug_session_excluded": PARTIAL_DEBUG_SESSION_ID,
        "no_fabricated_data": True,
        "gold_profile_overwritten": False,
        "notes": "Only the clean M24-B session is used for formal M24-C analysis.",
    }


def load_old_profile(path: Path) -> dict[float, dict[str, Any]]:
    profile = read_json(path)
    result = {}
    for row in profile.get("per_surface_response_statistics", []):
        if row.get("surface_id") == "S2_marble_floor":
            result[round(float(row["command_velocity"]), 2)] = row
    return result


def load_m23c_direct(path: Path) -> dict[float, float]:
    rows = read_csv(path)
    grouped: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        grouped[round(float(row["desired_velocity_mps"]), 2)].append(float(row["direct_measured_actual_velocity_mps"]))
    return {velocity: statistics.fmean(values) for velocity, values in grouped.items()}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def sample_std(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(summary: dict[str, Any], per_velocity: list[dict[str, Any]], old_new: list[dict[str, Any]], m23c: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-C S2 Profile Refresh Analysis Report",
        "",
        "## Session Summary",
        f"- Session ID: `{summary['session_id']}`",
        f"- Trial count: {summary['trial_count']}",
        f"- Executed/skipped/invalid: {summary['executed_count']}/{summary['skipped_count']}/{summary['invalid_count']}",
        f"- Velocity groups: {summary['velocity_group_count']}",
        f"- Profile status decision: `{summary['profile_status_decision']}`",
        f"- Candidate profile: `{summary['candidate_profile_path']}`",
        "",
        "## Refreshed Direct Response",
        "",
        "| Command | n | Mean Actual | Mean Abs Error | No-Motion Rate | Mean Yaw Drift |",
        "|---------|---|-------------|----------------|----------------|----------------|",
    ]
    for row in per_velocity:
        lines.append(
            f"| {row['command_velocity_mps']} | {row['n']} | {row['mean_actual_velocity_mps']} | "
            f"{row['mean_abs_tracking_error_mps']} | {row['no_motion_rate']} | {row['mean_yaw_drift_deg']} |"
        )
    lines += [
        "",
        "## Old M19C Vs New M24-C",
        "",
        "| Command | Old Mean | New Mean | Abs Diff | Mismatch | Status |",
        "|---------|----------|----------|----------|----------|--------|",
    ]
    for row in old_new:
        lines.append(
            f"| {row['command_velocity_mps']} | {row['old_m19c_s2_mean_actual_velocity_mps']} | "
            f"{row['new_m24c_mean_actual_velocity_mps']} | {row['absolute_difference_mps']} | "
            f"{row['profile_mismatch_flag']} | {row['comparison_status']} |"
        )
    lines += [
        "",
        "## M23-C Consistency Check",
        "",
        "| Velocity | M23-C Direct | M24-C Refresh | Old M19C | M24-C vs M23-C | M24-C vs M19C | Staleness Consistent |",
        "|----------|--------------|---------------|----------|----------------|----------------|----------------------|",
    ]
    for row in m23c:
        lines.append(
            f"| {row['desired_velocity_mps']} | {row['m23c_direct_mean_actual_velocity_mps']} | "
            f"{row['m24c_refresh_mean_actual_velocity_mps']} | {row['old_m19c_s2_mean_actual_velocity_mps']} | "
            f"{row['abs_diff_m24c_vs_m23c']} | {row['abs_diff_m24c_vs_m19c']} | {row['consistent_with_profile_staleness']} |"
        )
    lines += [
        "",
        "## Decision",
        f"`{summary['profile_status_decision']}`",
        "",
        f"Next recommended milestone: {summary['next_recommended_milestone']}",
        "",
        "## Candidate Profile Warning",
        "The candidate profile is not a gold profile, is not deployment ready, requires review before adoption, does not validate compensation, and must not be used for GO1/G1.",
        "",
        "## Claim Boundary",
        "M24-C analyzes clean S2 direct-refresh physical data and creates a candidate current S2 profile. It does not claim compensation improvement, revised compensator physical validation, deployment readiness, navigation improvement, GO1/G1 validation, cross-platform validation, or universal K1 generalization.",
    ]
    return "\n".join(lines) + "\n"


def build_decision_md(summary: dict[str, Any]) -> str:
    return (
        "# M24-C S2 Profile Status Decision\n\n"
        f"Decision: `{summary['profile_status_decision']}`\n\n"
        f"Profile mismatch count: {summary['profile_mismatch_count']} / {summary['old_profile_available_count']}\n\n"
        f"M23-C consistency count: {summary['m24c_matches_m23c_count']} / {summary['m23c_overlap_count']}\n\n"
        f"Next recommended milestone: {summary['next_recommended_milestone']}\n\n"
        "Gold profile overwritten: `false`\n\n"
        "Deployment ready: `false`\n"
    )


def build_candidate_md(candidate: dict[str, Any]) -> str:
    lines = [
        "# M24-C Current S2 Profile Candidate",
        "",
        f"Candidate label: `{candidate['candidate_label']}`",
        f"Source session: `{candidate['source_session_id']}`",
        f"Surface: `{candidate['surface']}`",
        f"Condition: `{candidate['condition']}`",
        f"Decision: `{candidate['profile_status_decision']}`",
        "",
        "## Warnings",
    ]
    lines.extend(f"- `{warning}`" for warning in candidate["warnings"])
    lines += [
        "",
        "## Aggregates",
        "",
        "| Command | Mean Actual | Std Actual | Mean Abs Error | No-Motion Rate |",
        "|---------|-------------|------------|----------------|----------------|",
    ]
    for row in candidate["per_command_velocity_aggregates"]:
        lines.append(
            f"| {row['command_velocity_mps']} | {row['mean_actual_velocity_mps']} | "
            f"{row['std_actual_velocity_mps']} | {row['mean_abs_tracking_error_mps']} | {row['no_motion_rate']} |"
        )
    return "\n".join(lines) + "\n"


def build_ingestion_md(ingestion: dict[str, Any]) -> str:
    return (
        "# M24-C Ingestion Summary\n\n"
        f"- Archive: `{ingestion['archive_filename']}`\n"
        f"- Archive size bytes: {ingestion['archive_size_bytes']}\n"
        f"- SHA256: `{ingestion['archive_sha256']}`\n"
        f"- Extracted session path: `{ingestion['extracted_session_path']}`\n"
        f"- Clean session used: `{str(ingestion['clean_session_used']).lower()}`\n"
        f"- Partial/debug session excluded: `{ingestion['partial_debug_session_excluded']}`\n"
        "- No fabricated data: `true`\n"
        "- Gold profile overwritten: `false`\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
