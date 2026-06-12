"""Analyze M24-F corrected S2 profile refresh extraction."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_DIR = Path("data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358")
OUTPUT_DIR = Path("outputs/compensation_experiments")
OLD_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
M23C_PAIRS = OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
ALLOWED_DECISIONS = {
    "old_profile_confirmed_current_after_correction",
    "old_profile_stale_current_s2_profile_needed_after_correction",
    "corrected_analysis_inconclusive",
    "corrected_extraction_failed",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze corrected M24-F S2 profile refresh.")
    parser.add_argument("--session-dir", type=Path, default=SESSION_DIR)
    parser.add_argument("--old-profile", type=Path, default=OLD_PROFILE)
    parser.add_argument("--m23c-pairs", type=Path, default=M23C_PAIRS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--profile-mismatch-threshold", type=float, default=0.03)
    parser.add_argument("--m23c-consistency-threshold", type=float, default=0.03)
    parser.add_argument("--near-optimal-threshold", type=float, default=0.02)
    args = parser.parse_args(argv)
    result = analyze(args)
    print(f"M24-F corrected profile decision: {result['summary']['corrected_profile_decision']}")
    return 0 if result["summary"]["corrected_profile_decision"] != "corrected_extraction_failed" else 1


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    corrected = read_csv(args.session_dir / "corrected_extracted_results.csv")
    faulty = read_csv(args.session_dir / "extracted_results.csv")
    qc = read_json(args.session_dir / "corrected_qc_summary.json")
    old = load_old_profile(args.old_profile)
    m23c = load_m23c(args.m23c_pairs)

    per_velocity = per_velocity_summary(corrected, args.near_optimal_threshold)
    old_new = old_new_comparison(per_velocity, old, args.profile_mismatch_threshold)
    consistency = m23c_consistency(per_velocity, old, m23c, args.profile_mismatch_threshold, args.m23c_consistency_threshold)
    comparison = faulty_vs_corrected(faulty, corrected)
    decision = decide(qc, old_new, consistency)
    summary = build_summary(qc, per_velocity, old_new, consistency, decision, args)
    candidate = build_candidate(summary, per_velocity)

    write_csv(args.output_dir / "m24f_corrected_s2_per_velocity_summary.csv", per_velocity, list(per_velocity[0]))
    write_csv(args.output_dir / "m24f_corrected_s2_old_vs_new_profile_comparison.csv", old_new, list(old_new[0]))
    write_csv(args.output_dir / "m24f_corrected_s2_m23c_consistency_check.csv", consistency, list(consistency[0]))
    write_csv(args.output_dir / "m24f_faulty_vs_corrected_extraction_comparison.csv", comparison, list(comparison[0]))
    (args.output_dir / "m24f_corrected_s2_profile_refresh_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.output_dir / "m24f_corrected_s2_current_profile_candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")
    (args.output_dir / "m24f_corrected_s2_profile_refresh_report.md").write_text(report(summary, per_velocity, old_new, consistency), encoding="utf-8")
    (args.output_dir / "m24f_corrected_s2_profile_status_decision.md").write_text(decision_md(summary), encoding="utf-8")
    (args.output_dir / "m24f_corrected_s2_current_profile_candidate.md").write_text(candidate_md(candidate), encoding="utf-8")
    (args.output_dir / "m24f_faulty_vs_corrected_extraction_report.md").write_text(comparison_md(comparison), encoding="utf-8")
    supersession = supersession_notice(summary)
    (args.output_dir / "m24f_supersession_notice.json").write_text(json.dumps(supersession, indent=2), encoding="utf-8")
    (args.output_dir / "m24f_supersession_notice.md").write_text(supersession_md(supersession), encoding="utf-8")
    return {"summary": summary, "candidate": candidate}


def per_velocity_summary(rows: list[dict[str, str]], near_threshold: float) -> list[dict[str, Any]]:
    groups: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[round(float(row["command_velocity_mps"]), 2)].append(row)
    output = []
    for command in sorted(groups):
        group = groups[command]
        actual = [float(row["measured_actual_velocity_mps"]) for row in group]
        desired = [float(row["desired_velocity_mps"]) for row in group]
        err = [a - d for a, d in zip(actual, desired)]
        abs_err = [abs(v) for v in err]
        yaw = [float(row["yaw_drift_deg"]) for row in group]
        imu = [float(row["imu_yaw_drift_deg"]) for row in group if row.get("imu_yaw_drift_deg")]
        output.append({
            "surface": "S2_marble_floor",
            "condition": "direct_refresh",
            "command_velocity_mps": command,
            "desired_velocity_mps": round(statistics.fmean(desired), 2),
            "n": len(group),
            "mean_actual_velocity_mps": round(statistics.fmean(actual), 6),
            "median_actual_velocity_mps": round(statistics.median(actual), 6),
            "std_actual_velocity_mps": round(statistics.stdev(actual), 6) if len(actual) > 1 else 0.0,
            "min_actual_velocity_mps": round(min(actual), 6),
            "max_actual_velocity_mps": round(max(actual), 6),
            "mean_tracking_error_mps": round(statistics.fmean(err), 6),
            "mean_abs_tracking_error_mps": round(statistics.fmean(abs_err), 6),
            "median_abs_tracking_error_mps": round(statistics.median(abs_err), 6),
            "max_abs_tracking_error_mps": round(max(abs_err), 6),
            "mean_yaw_drift_deg": round(statistics.fmean(yaw), 6),
            "median_yaw_drift_deg": round(statistics.median(yaw), 6),
            "max_yaw_drift_deg": round(max(yaw), 6),
            "mean_imu_yaw_drift_deg": "" if not imu else round(statistics.fmean(imu), 6),
            "no_motion_rate": round(sum(1 for value in actual if abs(value) < 0.02) / len(actual), 6),
            "repeat_variability_mps": round(statistics.stdev(actual), 6) if len(actual) > 1 else 0.0,
            "direct_near_optimal_flag": statistics.fmean(abs_err) <= near_threshold,
        })
    return output


def old_new_comparison(per_velocity: list[dict[str, Any]], old: dict[float, dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    rows = []
    for row in per_velocity:
        command = float(row["command_velocity_mps"])
        old_row = old.get(round(command, 2))
        if old_row is None:
            rows.append({
                "command_velocity_mps": command,
                "old_m19c_s2_mean_actual_velocity_mps": "",
                "new_m24f_mean_actual_velocity_mps": row["mean_actual_velocity_mps"],
                "absolute_difference_mps": "",
                "profile_mismatch_flag": "",
                "old_profile_available": False,
                "comparison_status": "old_velocity_unavailable",
            })
            continue
        diff = abs(float(row["mean_actual_velocity_mps"]) - float(old_row["mean_actual_velocity"]))
        rows.append({
            "command_velocity_mps": command,
            "old_m19c_s2_mean_actual_velocity_mps": round(float(old_row["mean_actual_velocity"]), 6),
            "new_m24f_mean_actual_velocity_mps": row["mean_actual_velocity_mps"],
            "absolute_difference_mps": round(diff, 6),
            "profile_mismatch_flag": diff >= threshold,
            "old_profile_available": True,
            "comparison_status": "compared",
        })
    return rows


def m23c_consistency(per_velocity: list[dict[str, Any]], old: dict[float, dict[str, Any]], m23c: dict[float, float], old_threshold: float, m23_threshold: float) -> list[dict[str, Any]]:
    per = {round(float(row["command_velocity_mps"]), 2): row for row in per_velocity}
    rows = []
    for velocity in sorted(set(per) & set(m23c)):
        new_mean = float(per[velocity]["mean_actual_velocity_mps"])
        old_mean = None if velocity not in old else float(old[velocity]["mean_actual_velocity"])
        m23_mean = m23c[velocity]
        diff_m23 = abs(new_mean - m23_mean)
        diff_old = "" if old_mean is None else abs(new_mean - old_mean)
        rows.append({
            "desired_velocity_mps": velocity,
            "m23c_direct_mean_actual_velocity_mps": round(m23_mean, 6),
            "m24f_corrected_mean_actual_velocity_mps": round(new_mean, 6),
            "old_m19c_s2_mean_actual_velocity_mps": "" if old_mean is None else round(old_mean, 6),
            "abs_diff_m24f_vs_m23c": round(diff_m23, 6),
            "abs_diff_m24f_vs_m19c": "" if old_mean is None else round(float(diff_old), 6),
            "m24f_matches_m23c": diff_m23 <= m23_threshold,
            "consistent_with_old_profile_staleness": old_mean is not None and diff_m23 <= m23_threshold and float(diff_old) >= old_threshold,
        })
    return rows


def faulty_vs_corrected(faulty: list[dict[str, str]], corrected: list[dict[str, str]]) -> list[dict[str, Any]]:
    corrected_by_id = {row["trial_id"]: row for row in corrected}
    rows = []
    for row in faulty:
        corr = corrected_by_id[row["trial_id"]]
        faulty_v = float(row["measured_actual_velocity_mps"])
        corr_v = float(corr["measured_actual_velocity_mps"])
        factor = "" if abs(faulty_v) < 1e-9 else round(corr_v / faulty_v, 6)
        rows.append({
            "trial_id": row["trial_id"],
            "command_velocity_mps": row["command_velocity_mps"],
            "faulty_m24c_actual_velocity_mps": faulty_v,
            "corrected_actual_velocity_mps": corr_v,
            "correction_factor": factor,
            "absolute_difference_mps": round(abs(corr_v - faulty_v), 6),
            "faulty_value_near_zero": abs(faulty_v) < 0.02,
            "corrected_value_plausible": abs(corr_v) >= 0.02,
        })
    return rows


def decide(qc: dict[str, Any], old_new: list[dict[str, Any]], consistency: list[dict[str, Any]]) -> str:
    if qc.get("overall_pass") is not True:
        return "corrected_extraction_failed"
    comparable = [row for row in old_new if row["old_profile_available"] is True]
    mismatches = sum(row["profile_mismatch_flag"] is True for row in comparable)
    matches_m23 = sum(row["m24f_matches_m23c"] is True for row in consistency)
    most_old = len(comparable) // 2 + 1
    most_m23 = len(consistency) // 2 + 1 if consistency else 999
    if mismatches >= most_old and matches_m23 >= most_m23:
        return "old_profile_stale_current_s2_profile_needed_after_correction"
    if (len(comparable) - mismatches) >= most_old:
        return "old_profile_confirmed_current_after_correction"
    return "corrected_analysis_inconclusive"


def build_summary(qc: dict[str, Any], per_velocity: list[dict[str, Any]], old_new: list[dict[str, Any]], consistency: list[dict[str, Any]], decision: str, args: argparse.Namespace) -> dict[str, Any]:
    comparison = read_csv(args.output_dir / "m24f_faulty_vs_corrected_extraction_comparison.csv") if (args.output_dir / "m24f_faulty_vs_corrected_extraction_comparison.csv").exists() else []
    return {
        "analysis_id": "m24f_corrected_s2_profile_refresh",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": "m24b_s2_profile_refresh_clean_20260612_145358",
        "corrected_extraction_trial_count": qc.get("corrected_extracted_count"),
        "corrected_qc_pass": qc.get("overall_pass"),
        "velocity_group_count": qc.get("velocity_group_count"),
        "repeats_per_velocity": qc.get("repeats_per_velocity"),
        "old_profile_available_count": sum(row["old_profile_available"] is True for row in old_new),
        "profile_mismatch_count": sum(row["profile_mismatch_flag"] is True for row in old_new),
        "m23c_overlap_count": len(consistency),
        "m24f_matches_m23c_count": sum(row["m24f_matches_m23c"] is True for row in consistency),
        "corrected_profile_decision": decision,
        "allowed_decisions": sorted(ALLOWED_DECISIONS),
        "corrected_candidate_profile_path": "outputs/compensation_experiments/m24f_corrected_s2_current_profile_candidate.json",
        "m24c_artifacts_superseded": True,
        "gold_profile_overwritten": False,
        "candidate_profile_adopted": False,
        "compensation_improvement_claimed": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "thresholds": {
            "profile_mismatch_threshold_mps": args.profile_mismatch_threshold,
            "m23c_consistency_threshold_mps": args.m23c_consistency_threshold,
            "near_optimal_threshold_mps": args.near_optimal_threshold,
        },
        "next_recommended_milestone": "review corrected extraction and collect/compare controlled replication before profile adoption",
    }


def build_candidate(summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_label": "k1_s2_corrected_current_profile_candidate_m24f",
        "creation_milestone": "M24-F",
        "source_session_id": summary["session_id"],
        "source_trial_count": summary["corrected_extraction_trial_count"],
        "surface": "S2_marble_floor",
        "condition": "direct_refresh",
        "profile_status_decision": summary["corrected_profile_decision"],
        "per_command_velocity_aggregates": rows,
        "warnings": [
            "not_gold_profile",
            "not_deployment_ready",
            "requires_review_before_adoption",
            "does_not_validate_compensation",
            "do_not_use_for_go1_g1",
        ],
    }


def supersession_notice(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "superseded_milestone": "M24-C",
        "superseded_candidate_profile": "outputs/compensation_experiments/m24c_s2_current_profile_candidate.json",
        "reason": "M24-C decision and candidate profile were based on faulty extraction.",
        "m24c_artifacts_retained_for_traceability": True,
        "use_instead": "outputs/compensation_experiments/m24f_corrected_s2_profile_refresh_summary.json",
        "m24f_corrected_candidate_profile": summary["corrected_candidate_profile_path"],
        "gold_profile_overwritten": False,
    }


def load_old_profile(path: Path) -> dict[float, dict[str, Any]]:
    data = read_json(path)
    return {round(float(row["command_velocity"]), 2): row for row in data.get("per_surface_response_statistics", []) if row.get("surface_id") == "S2_marble_floor"}


def load_m23c(path: Path) -> dict[float, float]:
    grouped: dict[float, list[float]] = defaultdict(list)
    for row in read_csv(path):
        grouped[round(float(row["desired_velocity_mps"]), 2)].append(float(row["direct_measured_actual_velocity_mps"]))
    return {k: statistics.fmean(v) for k, v in grouped.items()}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def report(summary: dict[str, Any], per_velocity: list[dict[str, Any]], old_new: list[dict[str, Any]], consistency: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-F Corrected S2 Profile Refresh Analysis",
        "",
        f"- Corrected extraction rows: {summary['corrected_extraction_trial_count']}",
        f"- Corrected QC pass: `{str(summary['corrected_qc_pass']).lower()}`",
        f"- Corrected profile decision: `{summary['corrected_profile_decision']}`",
        f"- M24-C artifacts superseded: `{str(summary['m24c_artifacts_superseded']).lower()}`",
        f"- Gold profile overwritten: `{str(summary['gold_profile_overwritten']).lower()}`",
        f"- Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        "",
        "## Corrected Per-Velocity Summary",
        "| Command | n | Mean Actual | Mean Abs Error | No-Motion Rate |",
        "|---------|---|-------------|----------------|----------------|",
    ]
    for row in per_velocity:
        lines.append(f"| {row['command_velocity_mps']} | {row['n']} | {row['mean_actual_velocity_mps']} | {row['mean_abs_tracking_error_mps']} | {row['no_motion_rate']} |")
    lines += [
        "",
        "## Claim Boundary",
        "M24-F corrects extraction and creates a corrected candidate profile only. It does not adopt a profile, overwrite the K1 gold profile, claim compensation improvement, claim deployment readiness, or start GO1/G1 work.",
    ]
    return "\n".join(lines) + "\n"


def decision_md(summary: dict[str, Any]) -> str:
    return (
        "# M24-F Corrected S2 Profile Status Decision\n\n"
        f"Decision: `{summary['corrected_profile_decision']}`\n\n"
        f"Profile mismatch count: {summary['profile_mismatch_count']} / {summary['old_profile_available_count']}\n\n"
        f"M23-C match count: {summary['m24f_matches_m23c_count']} / {summary['m23c_overlap_count']}\n\n"
        "Gold profile overwritten: `false`\n\nDeployment ready: `false`\n"
    )


def candidate_md(candidate: dict[str, Any]) -> str:
    lines = ["# M24-F Corrected Current S2 Profile Candidate", "", f"Candidate: `{candidate['candidate_label']}`", "", "## Warnings"]
    lines.extend(f"- `{w}`" for w in candidate["warnings"])
    return "\n".join(lines) + "\n"


def comparison_md(rows: list[dict[str, Any]]) -> str:
    factors = [abs(float(row["correction_factor"])) for row in rows if row["correction_factor"] not in ("", None)]
    return (
        "# M24-F Faulty Vs Corrected Extraction Comparison\n\n"
        f"- Compared trials: {len(rows)}\n"
        f"- Median absolute correction factor: {statistics.median(factors):.3f}\n"
        "- M24-C values are superseded due to faulty extraction.\n"
    )


def supersession_md(notice: dict[str, Any]) -> str:
    return (
        "# M24-F Supersession Notice\n\n"
        "M24-C profile candidate is superseded.\n\n"
        f"Reason: {notice['reason']}\n\n"
        "M24-C artifacts are retained for traceability. M24-F corrected analysis should be used instead.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
