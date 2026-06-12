"""Analyze M24-I controlled S2 replication results.

Ingests the clean M24-H session, verifies completeness, computes
per-velocity statistics, and compares against M24-F, M19C, and M23-C.

Usage:
  python scripts/analyze_m24i_controlled_s2_replication.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_SESSION = Path(
    "data/compensation_experiments/m24h_controlled_s2_replication/"
    "m24h_controlled_s2_replication_clean_20260612_171419"
)
DEFAULT_M19C_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
DEFAULT_M23C_PAIRS = Path("outputs/compensation_experiments/m23c_k1_before_after_pairs.csv")
DEFAULT_M24F_SUMMARY = Path("outputs/compensation_experiments/m24f_corrected_s2_per_velocity_summary.csv")
OUTPUT_DIR = Path("outputs/compensation_experiments")
ARCHIVE_PATH = Path(
    "m24h_controlled_s2_replication_results_m24h_controlled_s2_replication_clean_20260612_171419.tar.gz"
)

VALID_DECISIONS = [
    "response_reproducible_profile_adoption_planning_allowed",
    "response_environment_dependent_keep_identity_only",
    "extraction_or_protocol_issue_persists",
    "insufficient_data",
]

PER_VELOCITY_FIELDS = [
    "command_velocity_mps", "desired_velocity_mps", "n",
    "mean_actual_velocity_mps", "median_actual_velocity_mps", "std_actual_velocity_mps",
    "min_actual_velocity_mps", "max_actual_velocity_mps",
    "mean_tracking_error_mps", "mean_abs_tracking_error_mps",
    "median_abs_tracking_error_mps", "max_abs_tracking_error_mps",
    "mean_yaw_drift_deg", "median_yaw_drift_deg", "max_yaw_drift_deg",
    "repeat_variability_mps", "repeat_variability_flag", "direct_near_optimal_flag",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze M24-I controlled S2 replication.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--old-profile", type=Path, default=DEFAULT_M19C_PROFILE)
    parser.add_argument("--m23c-pairs", type=Path, default=DEFAULT_M23C_PAIRS)
    parser.add_argument("--m24f-summary", type=Path, default=DEFAULT_M24F_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--reproducibility-threshold", type=float, default=0.03)
    parser.add_argument("--near-optimal-threshold", type=float, default=0.02)
    args = parser.parse_args(argv)

    session_dir = args.session_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # 1. Ingestion summary
    # ------------------------------------------------------------------
    ingestion = _build_ingestion(session_dir, timestamp)
    _write_json(output_dir / "m24i_ingestion_summary.json", ingestion)
    _write_md(output_dir / "m24i_ingestion_summary.md", _ingestion_md(ingestion))

    # ------------------------------------------------------------------
    # 2. Verify session completeness
    # ------------------------------------------------------------------
    verification = _verify_session(session_dir)
    if not verification["complete"]:
        print(f"ERROR: Session incomplete: {verification['errors']}", file=sys.stderr)
        _write_json(output_dir / "m24i_controlled_s2_replication_summary.json",
                     {"decision": "insufficient_data", "errors": verification["errors"]})
        return 1

    print(f"Session verified: {verification['trial_count']} trials, {verification['executed']} executed")

    # ------------------------------------------------------------------
    # 3. Load extracted results
    # ------------------------------------------------------------------
    ext_path = session_dir / "corrected_extracted_results.csv"
    with ext_path.open(newline="", encoding="utf-8-sig") as f:
        extracted = list(csv.DictReader(f))

    # ------------------------------------------------------------------
    # 4. Per-velocity statistics
    # ------------------------------------------------------------------
    per_vel = _compute_per_velocity(extracted, args)
    per_vel_csv = output_dir / "m24i_controlled_s2_per_velocity_summary.csv"
    with per_vel_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PER_VELOCITY_FIELDS)
        w.writeheader()
        for row in per_vel:
            w.writerow({k: row.get(k, "") for k in PER_VELOCITY_FIELDS})
    print(f"Per-velocity summary: {per_vel_csv}")

    # ------------------------------------------------------------------
    # 5. Compare against M24-F
    # ------------------------------------------------------------------
    m24f_comp = _compare_m24f(per_vel, args.m24f_summary, args)
    _write_csv(output_dir / "m24i_m24f_replication_comparison.csv", m24f_comp)

    # ------------------------------------------------------------------
    # 6. Compare against M19C
    # ------------------------------------------------------------------
    m19c_comp = _compare_m19c(per_vel, args.old_profile)
    _write_csv(output_dir / "m24i_old_m19c_comparison.csv", m19c_comp)

    # ------------------------------------------------------------------
    # 7. Compare against M23-C direct
    # ------------------------------------------------------------------
    m23c_comp = _compare_m23c(per_vel, args.m23c_pairs)
    _write_csv(output_dir / "m24i_m23c_direct_comparison.csv", m23c_comp)

    # ------------------------------------------------------------------
    # 8. Controlled response decision
    # ------------------------------------------------------------------
    decision = _make_decision(per_vel, m24f_comp, m19c_comp, m23c_comp, verification, args)
    _write_json(output_dir / "m24i_controlled_s2_replication_summary.json", decision)
    _write_md(output_dir / "m24i_controlled_s2_replication_decision.md",
              _decision_md(decision, per_vel, m24f_comp, timestamp))

    # ------------------------------------------------------------------
    # 9. Profile candidate
    # ------------------------------------------------------------------
    candidate = _build_profile_candidate(per_vel, decision, timestamp)
    _write_json(output_dir / "m24i_controlled_s2_profile_candidate.json", candidate)
    _write_md(output_dir / "m24i_controlled_s2_profile_candidate.md",
              _candidate_md(candidate, per_vel, timestamp))

    # ------------------------------------------------------------------
    # 10. Final report
    # ------------------------------------------------------------------
    report = _build_report(ingestion, verification, per_vel, m24f_comp, m19c_comp, m23c_comp, decision, timestamp)
    _write_md(output_dir / "m24i_controlled_s2_replication_report.md", report)

    print(f"\nDecision: {decision['decision']}")
    print(f"  M24-F matches: {decision.get('m24f_match_count', 0)}/{decision.get('m24f_total', 0)}")
    print(f"  M19C matches: {decision.get('m19c_match_count', 0)}/{decision.get('m19c_total', 0)}")
    return 0


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def _build_ingestion(session_dir: Path, timestamp: str) -> dict:
    archive_size = ARCHIVE_PATH.stat().st_size if ARCHIVE_PATH.exists() else 0
    sha = ""
    if ARCHIVE_PATH.exists():
        sha = hashlib.sha256(ARCHIVE_PATH.read_bytes()).hexdigest()[:16]
    return {
        "ingestion_time": timestamp,
        "archive_filename": str(ARCHIVE_PATH),
        "archive_size_bytes": archive_size,
        "checksum_sha256_16": sha,
        "extracted_session_path": str(session_dir),
        "session_id": session_dir.name,
    }


def _verify_session(session_dir: Path) -> dict:
    errors = []
    records_path = session_dir / "trial_records.csv"
    ext_path = session_dir / "corrected_extracted_results.csv"
    meta_path = session_dir / "controlled_metadata.json"
    qc_path = session_dir / "qc_summary.json"

    if not records_path.exists():
        return {"complete": False, "errors": ["trial_records.csv missing"]}

    with records_path.open(newline="", encoding="utf-8-sig") as f:
        records = list(csv.DictReader(f))

    n = len(records)
    executed = sum(1 for r in records if r.get("physical_run_status") == "executed")
    skipped = sum(1 for r in records if r.get("physical_run_status") == "skipped")
    invalid = sum(1 for r in records if r.get("valid", "").lower() != "true")
    surfaces = {r.get("surface") for r in records}
    conditions = {r.get("condition") for r in records}
    vels = sorted({float(r["command_velocity_mps"]) for r in records})

    if n != 20:
        errors.append(f"trial_count:{n}_expected_20")
    if executed != 20:
        errors.append(f"executed:{executed}_expected_20")
    if invalid > 0:
        errors.append(f"invalid:{invalid}")
    if surfaces != {"S2_marble_floor"}:
        errors.append(f"surfaces:{surfaces}")
    if conditions != {"direct_refresh_controlled"}:
        errors.append(f"conditions:{conditions}")
    if set(vels) != {0.40, 0.45, 0.50, 0.55}:
        errors.append(f"velocities:{vels}")

    # Check extraction
    if not ext_path.exists():
        errors.append("corrected_extracted_results.csv missing")
    else:
        with ext_path.open(newline="", encoding="utf-8-sig") as f:
            ext_rows = list(csv.DictReader(f))
        if len(ext_rows) != 20:
            errors.append(f"extraction_count:{len(ext_rows)}")

    if not meta_path.exists():
        errors.append("controlled_metadata.json missing")

    return {
        "complete": len(errors) == 0,
        "errors": errors,
        "trial_count": n, "executed": executed, "skipped": skipped, "invalid": invalid,
        "velocities": [str(v) for v in vels], "surfaces": list(surfaces),
        "conditions": list(conditions),
    }


# ---------------------------------------------------------------------------
# Per-velocity statistics
# ---------------------------------------------------------------------------

def _compute_per_velocity(extracted: list[dict], args: argparse.Namespace) -> list[dict]:
    groups: dict[float, list[dict]] = {}
    for r in extracted:
        v = float(r["command_velocity_mps"])
        groups.setdefault(v, []).append(r)

    results = []
    for v in sorted(groups):
        rows = groups[v]
        actuals = [float(r["measured_actual_velocity_mps"]) for r in rows]
        yaws = [float(r.get("yaw_drift_deg", 0) or 0) for r in rows]
        n = len(actuals)
        mean_a = statistics.fmean(actuals)
        std_a = statistics.stdev(actuals) if n > 1 else 0.0
        med_a = statistics.median(actuals)
        abs_errors = [abs(a - v) for a in actuals]

        repeat_var = std_a
        repeat_flag = "high_variability" if repeat_var > args.reproducibility_threshold else "acceptable"
        near_opt = "yes" if mean_a >= v - args.near_optimal_threshold else "no"

        results.append({
            "command_velocity_mps": v, "desired_velocity_mps": v,
            "n": n,
            "mean_actual_velocity_mps": round(mean_a, 6),
            "median_actual_velocity_mps": round(med_a, 6),
            "std_actual_velocity_mps": round(std_a, 6),
            "min_actual_velocity_mps": round(min(actuals), 6),
            "max_actual_velocity_mps": round(max(actuals), 6),
            "mean_tracking_error_mps": round(mean_a - v, 6),
            "mean_abs_tracking_error_mps": round(statistics.fmean(abs_errors), 6),
            "median_abs_tracking_error_mps": round(statistics.median(abs_errors), 6),
            "max_abs_tracking_error_mps": round(max(abs_errors), 6),
            "mean_yaw_drift_deg": round(statistics.fmean(yaws), 4),
            "median_yaw_drift_deg": round(statistics.median(yaws), 4),
            "max_yaw_drift_deg": round(max(yaws), 4),
            "repeat_variability_mps": round(repeat_var, 6),
            "repeat_variability_flag": repeat_flag,
            "direct_near_optimal_flag": near_opt,
        })
    return results


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------

def _compare_m24f(per_vel: list[dict], m24f_path: Path, args: argparse.Namespace) -> list[dict]:
    if not m24f_path.exists():
        return [{"note": "m24f_summary_not_found"}]

    with m24f_path.open(newline="", encoding="utf-8-sig") as f:
        m24f = list(csv.DictReader(f))

    m24f_lookup: dict[float, float] = {}
    for r in m24f:
        try:
            m24f_lookup[float(r["command_velocity_mps"])] = float(r.get("mean_actual_velocity_mps", 0) or 0)
        except (ValueError, KeyError):
            pass

    rows = []
    for pv in per_vel:
        v = pv["command_velocity_mps"]
        m24f_val = m24f_lookup.get(v)
        if m24f_val is not None:
            diff = abs(pv["mean_actual_velocity_mps"] - m24f_val)
            rows.append({
                "command_velocity_mps": v,
                "m24f_mean_actual_mps": round(m24f_val, 6),
                "m24i_mean_actual_mps": pv["mean_actual_velocity_mps"],
                "difference_mps": round(diff, 6),
                "absolute_difference_mps": round(diff, 6),
                "reproducibility_threshold_mps": args.reproducibility_threshold,
                "replication_match_flag": "yes" if diff <= args.reproducibility_threshold else "no",
            })
    return rows


def _compare_m19c(per_vel: list[dict], profile_path: Path) -> list[dict]:
    if not profile_path.exists():
        return [{"note": "m19c_profile_not_found"}]

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    stats = profile.get("per_surface_response_statistics", [])
    s2_rows = [r for r in stats if r.get("surface_id") == "S2_marble_floor"]
    m19c_lookup: dict[float, float] = {}
    for r in s2_rows:
        try:
            m19c_lookup[float(r["command_velocity"])] = float(r.get("mean_actual_velocity", 0) or 0)
        except (ValueError, KeyError):
            pass

    rows = []
    for pv in per_vel:
        v = pv["command_velocity_mps"]
        m19c_val = m19c_lookup.get(v)
        if m19c_val is not None:
            diff = abs(pv["mean_actual_velocity_mps"] - m19c_val)
            rows.append({
                "command_velocity_mps": v,
                "m19c_mean_actual_mps": round(m19c_val, 6),
                "m24i_mean_actual_mps": pv["mean_actual_velocity_mps"],
                "absolute_difference_mps": round(diff, 6),
                "mismatch_flag": "yes" if diff > 0.05 else "no",
            })
        else:
            rows.append({
                "command_velocity_mps": v,
                "m19c_mean_actual_mps": "unavailable",
                "m24i_mean_actual_mps": pv["mean_actual_velocity_mps"],
                "absolute_difference_mps": "unavailable",
                "mismatch_flag": "unavailable",
            })
    return rows


def _compare_m23c(per_vel: list[dict], pairs_path: Path) -> list[dict]:
    if not pairs_path.exists():
        return [{"note": "m23c_pairs_not_found"}]

    with pairs_path.open(newline="", encoding="utf-8-sig") as f:
        pairs = list(csv.DictReader(f))

    # Get direct condition measurements
    direct: dict[float, list[float]] = {}
    for r in pairs:
        if r.get("condition") == "direct":
            try:
                v = float(r["desired_velocity_mps"])
                direct.setdefault(v, []).append(float(r.get("measured_actual_velocity_mps", 0) or 0))
            except (ValueError, KeyError):
                pass

    rows = []
    for pv in per_vel:
        v = pv["command_velocity_mps"]
        vals = direct.get(v, [])
        if vals:
            m23c_mean = statistics.fmean(vals)
            diff = abs(pv["mean_actual_velocity_mps"] - m23c_mean)
            rows.append({
                "command_velocity_mps": v,
                "m23c_direct_mean_mps": round(m23c_mean, 6),
                "m24i_mean_actual_mps": pv["mean_actual_velocity_mps"],
                "absolute_difference_mps": round(diff, 6),
                "match_flag": "yes" if diff <= 0.05 else "no",
            })
        else:
            rows.append({
                "command_velocity_mps": v,
                "m23c_direct_mean_mps": "unavailable",
                "m24i_mean_actual_mps": pv["mean_actual_velocity_mps"],
                "absolute_difference_mps": "unavailable",
                "match_flag": "unavailable",
            })
    return rows


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

def _make_decision(per_vel: list[dict], m24f_comp: list[dict],
                   m19c_comp: list[dict], m23c_comp: list[dict],
                   verification: dict, args: argparse.Namespace) -> dict:
    if not verification["complete"]:
        return {"decision": "insufficient_data", "reason": "Session verification failed",
                "errors": verification["errors"]}

    # M24-F matches
    m24f_matches = [r for r in m24f_comp if r.get("replication_match_flag") == "yes"]
    m24f_total = len([r for r in m24f_comp if "replication_match_flag" in r])

    # M19C matches
    m19c_matches = [r for r in m19c_comp if r.get("mismatch_flag") == "no"]

    # Decision logic
    if m24f_total > 0 and len(m24f_matches) >= m24f_total * 0.75:
        decision = "response_reproducible_profile_adoption_planning_allowed"
        reason = f"{len(m24f_matches)}/{m24f_total} velocities match M24-F within {args.reproducibility_threshold}m/s threshold. Controlled S2 response is reproducible enough for profile adoption planning."
    elif m24f_total > 0 and len(m24f_matches) >= m24f_total * 0.5:
        decision = "response_environment_dependent_keep_identity_only"
        reason = f"Only {len(m24f_matches)}/{m24f_total} velocities match M24-F. Response appears environment-dependent. Keep identity-only profile for now."
    elif m24f_total == 0:
        decision = "insufficient_data"
        reason = "No M24-F comparison data available."
    else:
        decision = "response_environment_dependent_keep_identity_only"
        reason = f"Only {len(m24f_matches)}/{m24f_total} velocities reproducible. Environment-dependent response."

    return {
        "decision": decision, "reason": reason,
        "analysis_time": datetime.now(timezone.utc).isoformat(),
        "m24f_match_count": len(m24f_matches), "m24f_total": m24f_total,
        "m19c_match_count": len(m19c_matches), "m19c_total": len(m19c_comp),
        "reproducibility_threshold": args.reproducibility_threshold,
        "gold_profile_overwritten": False,
        "candidate_profile_adopted": False,
        "compensation_validated": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
    }


# ---------------------------------------------------------------------------
# Profile candidate
# ---------------------------------------------------------------------------

def _build_profile_candidate(per_vel: list[dict], decision: dict, timestamp: str) -> dict:
    return {
        "profile_name": "m24i_controlled_s2_profile_candidate",
        "created_at": timestamp,
        "surface": "S2_marble_floor",
        "condition": "direct_refresh_controlled",
        "status": "candidate_only",
        "warnings": [
            "candidate_only",
            "not_gold_profile",
            "not_deployment_ready",
            "requires_review_before_adoption",
            "does_not_validate_compensation",
            "do_not_use_for_go1_g1",
        ],
        "per_velocity": per_vel,
        "decision": decision["decision"],
        "gold_profile_path": "outputs/real_k1_validation_m19/k1_gold_profile_v1.json",
        "gold_profile_overwritten": False,
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _build_report(ingestion: dict, verification: dict, per_vel: list[dict],
                  m24f: list[dict], m19c: list[dict], m23c: list[dict],
                  decision: dict, timestamp: str) -> str:
    lines = [
        "# M24-I Controlled S2 Replication Analysis Report",
        f"Generated: {timestamp}",
        "",
        "## Session Summary",
        f"- Session ID: {ingestion['session_id']}",
        f"- Trials: {verification['trial_count']} ({verification['executed']} executed)",
        f"- Velocities: {', '.join(verification['velocities'])}",
        f"- Surface: S2_marble_floor",
        f"- Condition: direct_refresh_controlled",
        "",
        "## Per-Velocity Controlled Response",
        "| v_cmd | n | mean_actual | std | mean_abs_error | yaw_drift | repeat_var | near_opt |",
        "|-------|---|-------------|-----|----------------|-----------|------------|----------|",
    ]
    for pv in per_vel:
        lines.append(f"| {pv['command_velocity_mps']} | {pv['n']} | {pv['mean_actual_velocity_mps']:.4f} | "
                     f"{pv['std_actual_velocity_mps']:.4f} | {pv['mean_abs_tracking_error_mps']:.4f} | "
                     f"{pv['mean_yaw_drift_deg']:.2f} | {pv['repeat_variability_mps']:.4f} | "
                     f"{pv['direct_near_optimal_flag']} |")

    lines += [
        "",
        "## M24-F Replication Comparison",
        "| v | M24-F mean | M24-I mean | diff | match? |",
        "|---|------------|------------|------|--------|",
    ]
    for r in m24f:
        if "replication_match_flag" in r:
            lines.append(f"| {r['command_velocity_mps']} | {r.get('m24f_mean_actual_mps','?')} | "
                         f"{r['m24i_mean_actual_mps']} | {r['absolute_difference_mps']} | {r['replication_match_flag']} |")

    lines += [
        "",
        "## Decision",
        f"**{decision['decision']}**",
        f"Reason: {decision['reason']}",
        "",
        "## Status Flags",
        f"- Gold profile overwritten: {decision['gold_profile_overwritten']}",
        f"- Candidate profile adopted: {decision['candidate_profile_adopted']}",
        f"- Deployment ready: {decision['deployment_ready']}",
        f"- GO1/G1 blocked: {decision['go1_g1_blocked']}",
        "",
        "## Claim Boundary",
        "- Controlled replication analyzed: ✅",
        "- Profile adoption: candidate only, not adopted",
        "- Compensation validated: ❌",
        "- Deployment ready: ❌",
        "- GO1/G1: ❌",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _ingestion_md(ingestion: dict) -> str:
    return f"""# M24-I Ingestion Summary
- Archive: {ingestion['archive_filename']}
- Size: {ingestion['archive_size_bytes']} bytes
- SHA256: {ingestion['checksum_sha256_16']}
- Session: {ingestion['session_id']}
- Path: {ingestion['extracted_session_path']}
"""


def _decision_md(decision: dict, per_vel: list, m24f: list, ts: str) -> str:
    lines = [
        "# M24-I Controlled S2 Replication Decision",
        f"Generated: {ts}",
        f"**Decision**: `{decision['decision']}`",
        f"Reason: {decision['reason']}",
        f"M24-F matches: {decision.get('m24f_match_count','?')}/{decision.get('m24f_total','?')}",
        f"M19C matches: {decision.get('m19c_match_count','?')}/{decision.get('m19c_total','?')}",
    ]
    return "\n".join(lines) + "\n"


def _candidate_md(candidate: dict, per_vel: list, ts: str) -> str:
    lines = [
        "# M24-I Controlled S2 Profile Candidate",
        f"Generated: {ts}",
        f"**Status**: {candidate['status']}",
        "",
        "## Warnings",
    ]
    for w in candidate["warnings"]:
        lines.append(f"- ⚠️ {w}")
    lines += ["", "## Per-Velocity", "| v_cmd | mean_actual | std | n |",
              "|-------|-------------|-----|---|"]
    for pv in per_vel:
        lines.append(f"| {pv['command_velocity_mps']} | {pv['mean_actual_velocity_mps']:.4f} | {pv['std_actual_velocity_mps']:.4f} | {pv['n']} |")
    lines += ["", "**This is a candidate only. Do not use as gold profile. Do not use for compensation validation. Do not use for GO1/G1.**"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
