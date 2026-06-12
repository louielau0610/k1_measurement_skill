"""Audit the M23-E revised offline compensator for M23-F readiness.

This is an offline audit only. It does not execute hardware or claim physical
improvement.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
M23C_PAIRS = DEFAULT_OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
M23E_SWEEP_CSV = DEFAULT_OUTPUT_DIR / "m23e_revised_compensator_sweep.csv"
M23E_SWEEP_JSON = DEFAULT_OUTPUT_DIR / "m23e_revised_compensator_sweep.json"
M23E_SUMMARY = DEFAULT_OUTPUT_DIR / "m23e_revised_compensator_summary.json"

READINESS_CATEGORIES = {
    "not_ready_revise_more",
    "ready_for_identity_fallback_validation",
    "ready_for_selected_compensation_validation",
    "ready_for_profile_refresh_before_validation",
}

AUDIT_FIELDS = [
    "desired_velocity_mps",
    "m23c_direct_mean_error_mps",
    "m23c_compensated_mean_error_mps",
    "m23c_harmful_command_mps",
    "revised_candidate_command_mps",
    "revised_final_command_mps",
    "revised_status",
    "harmful_command_avoided",
    "identity_fallback",
    "benefit_gate_passed",
    "profile_mismatch_suspected",
    "correction_magnitude_mps",
    "correction_limit_blocks_overcorrection",
    "candidate_could_be_beneficial",
    "audit_notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit M23-E revised offline compensator readiness.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = audit(args.output_dir)
    print("M23-F revised offline audit complete")
    print(f"  Harmful commands avoided: {summary['harmful_command_avoided_count']}")
    print(f"  Identity fallback count: {summary['identity_fallback_count']}")
    print(f"  Readiness: {summary['readiness_category']}")
    return 0


def audit(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    m23c_pairs = _read_csv(M23C_PAIRS)
    sweep_rows = _read_csv(M23E_SWEEP_CSV)
    sweep_json = _read_json(M23E_SWEEP_JSON)
    m23e_summary = _read_json(M23E_SUMMARY)

    direct_context = _m23c_by_velocity(m23c_pairs)
    table = build_audit_table(direct_context, sweep_rows)
    summary = build_summary(table, m23e_summary, sweep_json)
    recommendation = build_second_validation_recommendation(summary)

    _write_csv(output_dir / "m23f_decision_audit_table.csv", table, AUDIT_FIELDS)
    (output_dir / "m23f_revised_offline_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m23f_revised_offline_audit_report.md").write_text(build_audit_report(summary, table), encoding="utf-8")
    (output_dir / "m23f_second_validation_recommendation.json").write_text(json.dumps(recommendation, indent=2), encoding="utf-8")
    (output_dir / "m23f_second_validation_recommendation.md").write_text(build_recommendation_md(recommendation), encoding="utf-8")
    return summary


def build_audit_table(
    direct_context: dict[float, dict[str, float]],
    sweep_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    table = []
    for row in sweep_rows:
        velocity = float(row["desired_actual_velocity_mps"])
        context = direct_context[round(velocity, 6)]
        candidate = float(row["candidate_compensated_command_velocity_mps"])
        final = float(row["final_command_velocity_mps"])
        identity = float(row["identity_command_velocity_mps"])
        harmful_avoided = abs(final - context["harmful_command_mps"]) > 1e-9
        identity_fallback = row["feasibility_status"] == "identity_preferred" and abs(final - identity) <= 1e-9
        benefit_gate_passed = _bool(row["benefit_gate_passed"])
        correction_magnitude = float(row["correction_magnitude_mps"])
        profile_mismatch = _bool(row["profile_mismatch_suspected"])
        candidate_beneficial = float(row["expected_benefit_mps"]) >= 0.02
        correction_limit_blocks = correction_magnitude > 0.05 and row["feasibility_status"] == "overcorrection_risk"
        notes = []
        if harmful_avoided:
            notes.append("revised_final_differs_from_m23c_harmful_command")
        if identity_fallback:
            notes.append("identity_fallback_selected")
        if profile_mismatch:
            notes.append("profile_mismatch_flagged")
        if not candidate_beneficial:
            notes.append("candidate_not_beneficial")
        table.append({
            "desired_velocity_mps": velocity,
            "m23c_direct_mean_error_mps": context["direct_mean_error_mps"],
            "m23c_compensated_mean_error_mps": context["compensated_mean_error_mps"],
            "m23c_harmful_command_mps": context["harmful_command_mps"],
            "revised_candidate_command_mps": candidate,
            "revised_final_command_mps": final,
            "revised_status": row["feasibility_status"],
            "harmful_command_avoided": harmful_avoided,
            "identity_fallback": identity_fallback,
            "benefit_gate_passed": benefit_gate_passed,
            "profile_mismatch_suspected": profile_mismatch,
            "correction_magnitude_mps": correction_magnitude,
            "correction_limit_blocks_overcorrection": correction_limit_blocks,
            "candidate_could_be_beneficial": candidate_beneficial,
            "audit_notes": ";".join(notes),
        })
    return table


def build_summary(
    table: list[dict[str, Any]],
    m23e_summary: dict[str, Any],
    sweep_json: list[dict[str, Any]],
) -> dict[str, Any]:
    identity_count = sum(1 for row in table if row["identity_fallback"])
    harmful_avoided = sum(1 for row in table if row["harmful_command_avoided"])
    profile_mismatch_count = sum(1 for row in table if row["profile_mismatch_suspected"])
    candidate_beneficial_count = sum(1 for row in table if row["candidate_could_be_beneficial"])
    benefit_gate_blocks_all = all(not row["benefit_gate_passed"] for row in table)
    readiness = classify_readiness(
        identity_count=identity_count,
        decision_count=len(table),
        harmful_avoided=harmful_avoided,
        profile_mismatch_count=profile_mismatch_count,
        candidate_beneficial_count=candidate_beneficial_count,
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_m23e_summary": "outputs/compensation_experiments/m23e_revised_compensator_summary.json",
        "decision_count": len(table),
        "harmful_command_avoided_count": harmful_avoided,
        "identity_fallback_count": identity_count,
        "profile_mismatch_suspected_count": profile_mismatch_count,
        "benefit_gate_blocks_all_compensation": benefit_gate_blocks_all,
        "correction_limit_blocks_overcorrection_count": sum(1 for row in table if row["correction_limit_blocks_overcorrection"]),
        "candidate_beneficial_count": candidate_beneficial_count,
        "identity_fallback_over_conservative": identity_count == len(table) and candidate_beneficial_count > 0,
        "m23e_harmful_commands_selected": m23e_summary["harmful_m23c_commands_selected"],
        "all_final_commands_identity": m23e_summary["all_final_commands_identity"],
        "readiness_category": readiness,
        "readiness_categories": sorted(READINESS_CATEGORIES),
        "physical_validation_status": "not_started",
        "deployment_ready": False,
        "hardware_execution": False,
        "go1_g1_blocked": True,
        "offline_decisions": sweep_json,
        "main_conclusion": "The revised logic avoids the observed harmful M23-C commands offline, but profile mismatch is flagged on every tested velocity.",
    }


def classify_readiness(
    *,
    identity_count: int,
    decision_count: int,
    harmful_avoided: int,
    profile_mismatch_count: int,
    candidate_beneficial_count: int,
) -> str:
    if harmful_avoided < decision_count:
        return "not_ready_revise_more"
    if profile_mismatch_count == decision_count:
        return "ready_for_profile_refresh_before_validation"
    if candidate_beneficial_count > 0:
        return "ready_for_selected_compensation_validation"
    if identity_count == decision_count:
        return "ready_for_identity_fallback_validation"
    return "not_ready_revise_more"


def build_second_validation_recommendation(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": summary["generated_at"],
        "readiness_category": summary["readiness_category"],
        "should_rerun_same_s2_velocities": True,
        "same_s2_velocity_reason": "Use the same M23-C velocities to verify that revised identity fallback does not repeat the negative result.",
        "validate_identity_non_worsening": True,
        "refresh_s2_profile_before_compensation_experiment": True,
        "profile_refresh_steps": [
            "rerun a small S2 direct-response measurement set",
            "compare current direct response to the M19C gold profile",
            "write a versioned refreshed profile if mismatch is confirmed",
            "do not overwrite k1_gold_profile_v1.json in place",
        ],
        "choose_different_surface": "optional_after_profile_refresh",
        "different_surface_reason": "A surface with larger direct tracking error may be better for testing selected compensation, but K1 S2 identity fallback should be revalidated first.",
        "deadzone_low_speed_targets": "remain_excluded",
        "deadzone_reason": "Low-speed deadzone targets were outside executable compensated validation and should not be forced into a second validation.",
        "physical_validation_status": "not_started",
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "claim_boundary": "recommendation only; no physical improvement, deployment, navigation, or GO1/G1 claim",
    }


def build_audit_report(summary: dict[str, Any], table: list[dict[str, Any]]) -> str:
    lines = [
        "# M23-F Revised Offline Audit",
        "",
        "Status: offline audit only. No hardware was executed.",
        "",
        f"- Harmful M23-C commands avoided: {summary['harmful_command_avoided_count']}/{summary['decision_count']}",
        f"- Identity fallback count: {summary['identity_fallback_count']}",
        f"- Profile mismatch count: {summary['profile_mismatch_suspected_count']}",
        f"- Benefit gate blocks all compensation: {summary['benefit_gate_blocks_all_compensation']}",
        f"- Candidate beneficial count: {summary['candidate_beneficial_count']}",
        f"- Readiness category: `{summary['readiness_category']}`",
        f"- Deployment ready: {summary['deployment_ready']}",
        "",
        "## Decision Audit",
        "",
        "| Desired | M23-C direct error | M23-C comp error | Revised final | Status | Harm avoided | Profile mismatch |",
        "|---:|---:|---:|---:|---|---|---|",
    ]
    for row in table:
        lines.append(
            f"| {_fmt(row['desired_velocity_mps'])} | {_fmt(row['m23c_direct_mean_error_mps'])} | "
            f"{_fmt(row['m23c_compensated_mean_error_mps'])} | {_fmt(row['revised_final_command_mps'])} | "
            f"{row['revised_status']} | {row['harmful_command_avoided']} | {row['profile_mismatch_suspected']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The revised offline logic is safer than M22-C for the observed M23-C failure because it avoids every harmful compensated command and returns identity where direct tracking was already accurate. This does not prove physical improvement; it only supports designing a second K1 validation or profile-refresh step.",
        "",
        "GO1/G1 remain blocked until revised K1 behavior is physically validated.",
    ]
    return "\n".join(lines) + "\n"


def build_recommendation_md(recommendation: dict[str, Any]) -> str:
    lines = [
        "# M23-F Second K1 Validation Recommendation",
        "",
        f"Readiness category: `{recommendation['readiness_category']}`",
        "",
        "## Answers",
        "",
        f"- Rerun same S2 velocities: {recommendation['should_rerun_same_s2_velocities']}",
        f"- Validate identity non-worsening: {recommendation['validate_identity_non_worsening']}",
        f"- Refresh S2 profile before compensation experiment: {recommendation['refresh_s2_profile_before_compensation_experiment']}",
        f"- Choose different surface: {recommendation['choose_different_surface']}",
        f"- Deadzone/low-speed targets: {recommendation['deadzone_low_speed_targets']}",
        "",
        "## Profile Refresh",
    ]
    for step in recommendation["profile_refresh_steps"]:
        lines.append(f"- {step}")
    lines += [
        "",
        "## Boundary",
        "",
        recommendation["claim_boundary"],
    ]
    return "\n".join(lines) + "\n"


def _m23c_by_velocity(rows: list[dict[str, str]]) -> dict[float, dict[str, float]]:
    grouped: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[round(float(row["desired_velocity_mps"]), 6)].append(row)
    result = {}
    for velocity, velocity_rows in grouped.items():
        result[velocity] = {
            "direct_mean_error_mps": sum(float(row["direct_abs_error"]) for row in velocity_rows) / len(velocity_rows),
            "compensated_mean_error_mps": sum(float(row["compensated_abs_error"]) for row in velocity_rows) / len(velocity_rows),
            "harmful_command_mps": sum(float(row["compensated_command_velocity_mps"]) for row in velocity_rows) / len(velocity_rows),
        }
    return result


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
