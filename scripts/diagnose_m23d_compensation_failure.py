"""Diagnose M23-D compensation failure modes from M23-C outputs.

This milestone is analysis and planning only. It does not implement a revised
compensator and does not execute hardware.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
M23C_PAIRS = DEFAULT_OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
M23C_PER_VELOCITY = DEFAULT_OUTPUT_DIR / "m23c_k1_per_velocity_summary.csv"
M23C_SUMMARY = DEFAULT_OUTPUT_DIR / "m23c_k1_analysis_summary.json"

FAILURE_MODE_FIELDS = [
    "desired_velocity_mps",
    "pair_count",
    "mean_direct_abs_error",
    "mean_compensated_abs_error",
    "mean_error_delta",
    "direct_outperforms_compensated_count",
    "compensated_command_direction",
    "mean_command_delta_mps",
    "identity_preferred",
    "overcorrection_indicator",
    "profile_mismatch_indicator",
    "failure_mode_labels",
]

DIRECT_NEAR_OPTIMAL_ERROR_MPS = 0.02
PROFILE_MISMATCH_RATIO = 3.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose M23-D compensation failure modes.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = diagnose(args.output_dir)
    print("M23-D compensation failure diagnosis complete")
    print(f"  Direct outperformed compensated pairs: {result['direct_outperforms_compensated_pairs']}")
    print(f"  Failure modes: {', '.join(result['failure_mode_labels'])}")
    print(f"  Summary: {args.output_dir / 'm23d_failure_mode_summary.json'}")
    return 0


def diagnose(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    pairs = _read_csv(M23C_PAIRS)
    per_velocity = _read_csv(M23C_PER_VELOCITY)
    m23c_summary = _read_json(M23C_SUMMARY)
    table = build_failure_mode_table(pairs)
    aggregate = build_failure_mode_summary(table, pairs, per_velocity, m23c_summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "m23d_failure_mode_table.csv", table, FAILURE_MODE_FIELDS)
    (output_dir / "m23d_failure_mode_summary.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    (output_dir / "m23d_failure_mode_report.md").write_text(build_report(aggregate, table), encoding="utf-8")
    (output_dir / "m23d_negative_result_diagnosis_summary.json").write_text(
        json.dumps(build_diagnosis_summary(aggregate, m23c_summary), indent=2),
        encoding="utf-8",
    )
    return aggregate


def build_failure_mode_table(pairs: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in pairs:
        grouped[float(row["desired_velocity_mps"])].append(row)

    table = []
    for velocity in sorted(grouped):
        rows = grouped[velocity]
        direct_errors = [float(row["direct_abs_error"]) for row in rows]
        comp_errors = [float(row["compensated_abs_error"]) for row in rows]
        error_deltas = [float(row["error_delta"]) for row in rows]
        command_deltas = [
            float(row["compensated_command_velocity_mps"]) - float(row["direct_command_velocity_mps"])
            for row in rows
        ]
        mean_direct = statistics.fmean(direct_errors)
        mean_comp = statistics.fmean(comp_errors)
        mean_delta = statistics.fmean(error_deltas)
        mean_command_delta = statistics.fmean(command_deltas)
        direct_wins = sum(1 for row in rows if float(row["direct_abs_error"]) < float(row["compensated_abs_error"]))
        command_direction = _command_direction(mean_command_delta)
        identity_preferred = direct_wins == len(rows) and mean_direct <= DIRECT_NEAR_OPTIMAL_ERROR_MPS
        overcorrection = mean_delta > 0 and command_direction != "same_as_direct"
        profile_mismatch = mean_comp >= max(mean_direct * PROFILE_MISMATCH_RATIO, mean_direct + 0.02)
        labels = []
        if identity_preferred:
            labels.append("identity_preferred")
            labels.append("compensation_not_beneficial")
        if overcorrection:
            labels.append("overcorrection_risk")
        if profile_mismatch:
            labels.append("profile_mismatch_suspected")
        if mean_delta > 0:
            labels.append("revision_required")
        table.append({
            "desired_velocity_mps": velocity,
            "pair_count": len(rows),
            "mean_direct_abs_error": mean_direct,
            "mean_compensated_abs_error": mean_comp,
            "mean_error_delta": mean_delta,
            "direct_outperforms_compensated_count": direct_wins,
            "compensated_command_direction": command_direction,
            "mean_command_delta_mps": mean_command_delta,
            "identity_preferred": identity_preferred,
            "overcorrection_indicator": overcorrection,
            "profile_mismatch_indicator": profile_mismatch,
            "failure_mode_labels": ";".join(labels),
        })
    return table


def build_failure_mode_summary(
    table: list[dict[str, Any]],
    pairs: list[dict[str, str]],
    per_velocity: list[dict[str, str]],
    m23c_summary: dict[str, Any],
) -> dict[str, Any]:
    all_labels = sorted({
        label
        for row in table
        for label in str(row["failure_mode_labels"]).split(";")
        if label
    })
    direct_wins = sum(1 for row in pairs if float(row["direct_abs_error"]) < float(row["compensated_abs_error"]))
    comp_lower_count = sum(
        1
        for row in pairs
        if float(row["compensated_command_velocity_mps"]) < float(row["direct_command_velocity_mps"])
    )
    metrics = m23c_summary["aggregate_metrics"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_analysis": "outputs/compensation_experiments/m23c_k1_analysis_summary.json",
        "pair_count": len(pairs),
        "velocity_count": len(per_velocity),
        "direct_outperforms_compensated_pairs": direct_wins,
        "compensated_outperforms_direct_pairs": sum(
            1 for row in pairs if float(row["compensated_abs_error"]) < float(row["direct_abs_error"])
        ),
        "compensated_command_lower_than_direct_pairs": comp_lower_count,
        "compensated_command_higher_than_direct_pairs": sum(
            1
            for row in pairs
            if float(row["compensated_command_velocity_mps"]) > float(row["direct_command_velocity_mps"])
        ),
        "identity_preferred_velocity_count": sum(1 for row in table if row["identity_preferred"]),
        "overcorrection_velocity_count": sum(1 for row in table if row["overcorrection_indicator"]),
        "profile_mismatch_velocity_count": sum(1 for row in table if row["profile_mismatch_indicator"]),
        "mean_direct_error": metrics["mean_absolute_error_direct"],
        "mean_compensated_error": metrics["mean_absolute_error_compensated"],
        "percent_error_reduction": metrics["percent_reduction_mean_absolute_error"],
        "yaw_drift_direct": metrics["yaw_drift_mean_direct"],
        "yaw_drift_compensated": metrics["yaw_drift_mean_compensated"],
        "claim_level": m23c_summary["claim_level"],
        "failure_mode_labels": all_labels,
        "main_reason": "Direct commands were already near optimal; the compensator lowered commands and increased tracking error in every pair.",
        "revision_required": True,
        "deployment_ready": False,
        "hardware_execution": False,
        "revised_compensator_implemented": False,
        "next_milestone": "M23-E revised benefit-gated compensator design and offline validation",
    }


def build_diagnosis_summary(summary: dict[str, Any], m23c_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": summary["generated_at"],
        "source_session": m23c_summary["session_id"],
        "mean_direct_error": summary["mean_direct_error"],
        "mean_compensated_error": summary["mean_compensated_error"],
        "percent_error_reduction": summary["percent_error_reduction"],
        "yaw_drift_direct": summary["yaw_drift_direct"],
        "yaw_drift_compensated": summary["yaw_drift_compensated"],
        "claim_level": summary["claim_level"],
        "failure_mode_labels": summary["failure_mode_labels"],
        "revision_required": True,
        "deployment_ready": False,
        "hardware_execution": False,
        "next_milestone": summary["next_milestone"],
    }


def build_report(summary: dict[str, Any], table: list[dict[str, Any]]) -> str:
    lines = [
        "# M23-D Compensation Failure Mode Report",
        "",
        f"Source: `{summary['source_analysis']}`",
        f"Pairs analyzed: {summary['pair_count']}",
        f"Direct outperformed compensated pairs: {summary['direct_outperforms_compensated_pairs']}",
        f"Compensated command lower than direct pairs: {summary['compensated_command_lower_than_direct_pairs']}",
        f"Claim level inherited from M23-C: `{summary['claim_level']}`",
        "",
        "## Main Diagnosis",
        "",
        summary["main_reason"],
        "",
        "## Failure Mode Labels",
    ]
    for label in summary["failure_mode_labels"]:
        lines.append(f"- `{label}`")

    lines += [
        "",
        "## Per-Velocity Failure Modes",
        "",
        "| Desired | Direct error | Comp error | Delta | Command delta | Direct wins | Labels |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in table:
        lines.append(
            f"| {_fmt(row['desired_velocity_mps'])} | {_fmt(row['mean_direct_abs_error'])} | "
            f"{_fmt(row['mean_compensated_abs_error'])} | {_fmt(row['mean_error_delta'])} | "
            f"{_fmt(row['mean_command_delta_mps'])} | {row['direct_outperforms_compensated_count']} | "
            f"{row['failure_mode_labels']} |"
        )

    lines += [
        "",
        "## Boundary",
        "",
        "M23-D is diagnosis and planning only. No hardware was executed, no revised compensator was implemented, and no compensation improvement or deployment-readiness claim is made.",
    ]
    return "\n".join(lines) + "\n"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _command_direction(delta: float) -> str:
    if delta < -1e-12:
        return "lower_than_direct"
    if delta > 1e-12:
        return "higher_than_direct"
    return "same_as_direct"


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
