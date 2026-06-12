"""Analyze M23-C K1 before/after compensation results.

This script reads a completed M23-B executable-pair session and produces
M23-C analysis artifacts. It does not execute hardware and does not make
deployment, navigation, GO1/G1, cross-platform, or universal K1 claims.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SESSION_DIR = Path("data/compensation_experiments/m23b_k1/m23b_k1_s2_executable_20260612_121605")
DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
EXPECTED_TRIALS = 24
EXPECTED_PAIRS = 12
EXPECTED_VELOCITIES = [0.40, 0.45, 0.50, 0.55]

PAIR_FIELDS = [
    "pair_id",
    "desired_velocity_mps",
    "direct_trial_id",
    "compensated_trial_id",
    "direct_command_velocity_mps",
    "compensated_command_velocity_mps",
    "direct_measured_actual_velocity_mps",
    "compensated_measured_actual_velocity_mps",
    "direct_abs_error",
    "compensated_abs_error",
    "error_delta",
    "improvement",
    "percent_improvement",
    "direct_yaw_drift",
    "compensated_yaw_drift",
    "yaw_drift_delta",
]

PER_VELOCITY_FIELDS = [
    "desired_velocity_mps",
    "pair_count",
    "mean_direct_abs_error",
    "mean_compensated_abs_error",
    "mean_improvement",
    "percent_reduction_mean_abs_error",
    "mean_direct_yaw_drift",
    "mean_compensated_yaw_drift",
    "improved_pairs",
    "worsened_pairs",
    "no_change_pairs",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze M23-C K1 before/after compensation results.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--skip-scipy", action="store_true", help="Skip scipy statistical tests")
    args = parser.parse_args(argv)

    try:
        result = analyze_session(args.session_dir, args.output_dir, skip_scipy=args.skip_scipy)
    except Exception as exc:
        print(f"M23-C analysis failed: {exc}", file=sys.stderr)
        return 1

    print("M23-C analysis complete")
    print(f"  Trials: {result['validation']['trial_count']}")
    print(f"  Complete pairs: {result['validation']['pair_count']}")
    print(f"  Claim level: {result['claim_level']}")
    print(f"  Summary: {args.output_dir / 'm23c_k1_analysis_summary.json'}")
    return 0


def analyze_session(session_dir: Path, output_dir: Path, *, skip_scipy: bool = False) -> dict[str, Any]:
    session_dir = Path(session_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted = _read_csv(session_dir / "extracted_results.csv")
    records = _read_csv(session_dir / "trial_records.csv")
    extraction_summary = _read_json(session_dir / "extraction_summary.json")
    qc_summary = _read_json(session_dir / "qc_summary.json")
    provenance = _read_json(session_dir / "source_provenance.json") if (session_dir / "source_provenance.json").exists() else {}

    validation = validate_inputs(extracted, records, extraction_summary, qc_summary)
    pair_rows = build_pair_rows(extracted)
    per_velocity_rows = build_per_velocity_rows(pair_rows)
    aggregate = build_aggregate_metrics(pair_rows, records)
    stats = compute_statistical_tests([row["improvement"] for row in pair_rows], skip_scipy=skip_scipy)
    claim_level = determine_claim_level(aggregate)

    summary = {
        "analysis_id": "m23c_k1_before_after_compensation_analysis",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_dir.name,
        "session_dir": str(session_dir),
        "surface": "S2_marble_floor",
        "validation": validation,
        "aggregate_metrics": aggregate,
        "statistical_tests": stats,
        "claim_level": claim_level,
        "source_provenance": provenance,
        "baseline_positioning": {
            "physical_direct_baseline": "direct command condition from the executed M23-B session",
            "physical_compensated_condition": "M22-C risk-aware inverse lookup command condition from the executed M23-B session",
            "offline_only_baselines": [
                "scalar gain",
                "nearest lookup",
                "ordinary interpolation",
            ],
            "offline_baseline_boundary": "Offline baselines are context only here; no physical scalar-gain, nearest-lookup, or ordinary-interpolation trials were executed in this session.",
        },
        "claim_boundary": {
            "deployment_ready": False,
            "navigation_improvement_claimed": False,
            "go1_g1_validation_claimed": False,
            "cross_platform_validation_claimed": False,
            "universal_k1_generalization_claimed": False,
        },
    }

    _write_csv(output_dir / "m23c_k1_before_after_pairs.csv", pair_rows, PAIR_FIELDS)
    _write_csv(output_dir / "m23c_k1_per_velocity_summary.csv", per_velocity_rows, PER_VELOCITY_FIELDS)
    (output_dir / "m23c_k1_analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m23c_k1_analysis_report.md").write_text(
        build_report(summary, pair_rows, per_velocity_rows),
        encoding="utf-8",
    )
    (output_dir / "m23c_k1_claim_boundary.md").write_text(
        build_claim_boundary(summary),
        encoding="utf-8",
    )
    return summary


def validate_inputs(
    extracted: list[dict[str, str]],
    records: list[dict[str, str]],
    extraction_summary: dict[str, Any],
    qc_summary: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if len(extracted) != EXPECTED_TRIALS:
        errors.append(f"expected {EXPECTED_TRIALS} extracted trials, found {len(extracted)}")
    if int(extraction_summary.get("successfully_extracted", -1)) != EXPECTED_TRIALS:
        errors.append("extraction_summary successfully_extracted is not 24")
    if int(extraction_summary.get("extraction_errors", -1)) != 0:
        errors.append("extraction_summary reports extraction errors")
    if qc_summary.get("overall_pass") is not True:
        errors.append("qc_summary overall_pass is not true")

    pair_map: dict[str, set[str]] = defaultdict(set)
    velocities = set()
    missing_velocity = []
    missing_yaw = []
    bad_status = []
    for row in extracted:
        trial_id = row.get("trial_id", "")
        pair_map[row.get("pair_id", "")].add(row.get("condition", ""))
        velocities.add(round(float(row.get("desired_velocity_mps", "nan")), 2))
        if row.get("extraction_status") != "ok":
            bad_status.append(trial_id)
        if _blank(row.get("measured_actual_velocity_mps")):
            missing_velocity.append(trial_id)
        if _blank(row.get("yaw_drift_deg")):
            missing_yaw.append(trial_id)

    incomplete_pairs = [
        pair_id
        for pair_id, conditions in pair_map.items()
        if conditions != {"direct", "compensated"}
    ]
    if len(pair_map) != EXPECTED_PAIRS:
        errors.append(f"expected {EXPECTED_PAIRS} pairs, found {len(pair_map)}")
    if incomplete_pairs:
        errors.append(f"incomplete pairs: {incomplete_pairs}")
    if sorted(velocities) != EXPECTED_VELOCITIES:
        errors.append(f"unexpected desired velocities: {sorted(velocities)}")
    if bad_status:
        errors.append(f"non-ok extraction_status trials: {bad_status}")
    if missing_velocity:
        errors.append(f"missing measured velocity: {missing_velocity}")
    if missing_yaw:
        errors.append(f"missing yaw drift: {missing_yaw}")

    return {
        "trial_count": len(extracted),
        "trial_record_count": len(records),
        "pair_count": len(pair_map),
        "expected_pair_count": EXPECTED_PAIRS,
        "desired_velocities_mps": sorted(velocities),
        "extraction_status_ok_count": sum(1 for row in extracted if row.get("extraction_status") == "ok"),
        "qc_overall_pass": qc_summary.get("overall_pass"),
        "qc_checks_passed": qc_summary.get("checks_passed"),
        "qc_checks_total": qc_summary.get("checks_total"),
        "errors": errors,
        "passed": not errors,
    }


def build_pair_rows(extracted: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_pair: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in extracted:
        by_pair[row["pair_id"]][row["condition"]] = row

    pair_rows = []
    for pair_id in sorted(by_pair):
        direct = by_pair[pair_id]["direct"]
        compensated = by_pair[pair_id]["compensated"]
        desired = float(direct["desired_velocity_mps"])
        direct_measured = float(direct["measured_actual_velocity_mps"])
        compensated_measured = float(compensated["measured_actual_velocity_mps"])
        direct_abs_error = abs(direct_measured - desired)
        compensated_abs_error = abs(compensated_measured - desired)
        improvement = direct_abs_error - compensated_abs_error
        percent_improvement = (improvement / direct_abs_error * 100.0) if direct_abs_error > 0 else None
        direct_yaw = float(direct["yaw_drift_deg"])
        compensated_yaw = float(compensated["yaw_drift_deg"])
        pair_rows.append({
            "pair_id": pair_id,
            "desired_velocity_mps": desired,
            "direct_trial_id": direct["trial_id"],
            "compensated_trial_id": compensated["trial_id"],
            "direct_command_velocity_mps": float(direct["command_velocity_mps"]),
            "compensated_command_velocity_mps": float(compensated["command_velocity_mps"]),
            "direct_measured_actual_velocity_mps": direct_measured,
            "compensated_measured_actual_velocity_mps": compensated_measured,
            "direct_abs_error": direct_abs_error,
            "compensated_abs_error": compensated_abs_error,
            "error_delta": compensated_abs_error - direct_abs_error,
            "improvement": improvement,
            "percent_improvement": percent_improvement,
            "direct_yaw_drift": direct_yaw,
            "compensated_yaw_drift": compensated_yaw,
            "yaw_drift_delta": compensated_yaw - direct_yaw,
        })
    return pair_rows


def build_per_velocity_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_velocity: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        by_velocity[float(row["desired_velocity_mps"])].append(row)

    rows = []
    for velocity in sorted(by_velocity):
        group = by_velocity[velocity]
        direct_errors = [row["direct_abs_error"] for row in group]
        comp_errors = [row["compensated_abs_error"] for row in group]
        improvements = [row["improvement"] for row in group]
        direct_yaws = [row["direct_yaw_drift"] for row in group]
        comp_yaws = [row["compensated_yaw_drift"] for row in group]
        mean_direct = statistics.fmean(direct_errors)
        mean_comp = statistics.fmean(comp_errors)
        rows.append({
            "desired_velocity_mps": velocity,
            "pair_count": len(group),
            "mean_direct_abs_error": mean_direct,
            "mean_compensated_abs_error": mean_comp,
            "mean_improvement": statistics.fmean(improvements),
            "percent_reduction_mean_abs_error": ((mean_direct - mean_comp) / mean_direct * 100.0) if mean_direct > 0 else None,
            "mean_direct_yaw_drift": statistics.fmean(direct_yaws),
            "mean_compensated_yaw_drift": statistics.fmean(comp_yaws),
            "improved_pairs": sum(1 for value in improvements if value > 1e-12),
            "worsened_pairs": sum(1 for value in improvements if value < -1e-12),
            "no_change_pairs": sum(1 for value in improvements if abs(value) <= 1e-12),
        })
    return rows


def build_aggregate_metrics(pair_rows: list[dict[str, Any]], records: list[dict[str, str]]) -> dict[str, Any]:
    direct_errors = [row["direct_abs_error"] for row in pair_rows]
    comp_errors = [row["compensated_abs_error"] for row in pair_rows]
    improvements = [row["improvement"] for row in pair_rows]
    direct_yaws = [row["direct_yaw_drift"] for row in pair_rows]
    comp_yaws = [row["compensated_yaw_drift"] for row in pair_rows]
    mean_direct = statistics.fmean(direct_errors)
    mean_comp = statistics.fmean(comp_errors)
    invalid_rates = _invalid_rates(records)
    return {
        "mean_absolute_error_direct": mean_direct,
        "mean_absolute_error_compensated": mean_comp,
        "median_absolute_error_direct": statistics.median(direct_errors),
        "median_absolute_error_compensated": statistics.median(comp_errors),
        "max_absolute_error_direct": max(direct_errors),
        "max_absolute_error_compensated": max(comp_errors),
        "mean_improvement": statistics.fmean(improvements),
        "median_improvement": statistics.median(improvements),
        "percent_reduction_mean_absolute_error": ((mean_direct - mean_comp) / mean_direct * 100.0) if mean_direct > 0 else None,
        "improved_pairs": sum(1 for value in improvements if value > 1e-12),
        "worsened_pairs": sum(1 for value in improvements if value < -1e-12),
        "no_change_pairs": sum(1 for value in improvements if abs(value) <= 1e-12),
        "yaw_drift_mean_direct": statistics.fmean(direct_yaws),
        "yaw_drift_mean_compensated": statistics.fmean(comp_yaws),
        "yaw_drift_median_direct": statistics.median(direct_yaws),
        "yaw_drift_median_compensated": statistics.median(comp_yaws),
        "yaw_drift_mean_delta": statistics.fmean([row["yaw_drift_delta"] for row in pair_rows]),
        "invalid_rate_direct": invalid_rates["direct"],
        "invalid_rate_compensated": invalid_rates["compensated"],
    }


def compute_statistical_tests(improvements: list[float], *, skip_scipy: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "n_pairs": len(improvements),
        "scipy_available": False,
        "paired_t_test": None,
        "wilcoxon_signed_rank": None,
        "effect_size_cohen_dz": None,
        "notes": [],
    }
    if len(improvements) >= 2:
        std = statistics.stdev(improvements)
        if std > 0:
            result["effect_size_cohen_dz"] = statistics.fmean(improvements) / std
        else:
            result["notes"].append("effect size skipped because paired improvements have zero variance")
    if skip_scipy:
        result["notes"].append("scipy tests skipped by request")
        return result
    try:
        from scipy import stats  # type: ignore
    except Exception:
        result["notes"].append("scipy unavailable; significance tests skipped")
        return result

    result["scipy_available"] = True
    try:
        t_stat, p_value = stats.ttest_1samp(improvements, 0.0)
        result["paired_t_test"] = {
            "test": "one-sample t-test on paired improvements vs 0",
            "statistic": _finite_or_none(t_stat),
            "p_value": _finite_or_none(p_value),
        }
    except Exception as exc:
        result["paired_t_test"] = {"error": str(exc)}

    try:
        w_stat, p_value = stats.wilcoxon(improvements, zero_method="wilcox", alternative="two-sided")
        result["wilcoxon_signed_rank"] = {
            "test": "Wilcoxon signed-rank on paired improvements vs 0",
            "statistic": _finite_or_none(w_stat),
            "p_value": _finite_or_none(p_value),
        }
    except Exception as exc:
        result["wilcoxon_signed_rank"] = {"error": str(exc)}
    return result


def determine_claim_level(aggregate: dict[str, Any]) -> str:
    direct = aggregate["mean_absolute_error_direct"]
    comp = aggregate["mean_absolute_error_compensated"]
    yaw_delta = aggregate["yaw_drift_mean_compensated"] - aggregate["yaw_drift_mean_direct"]
    if comp < direct and yaw_delta <= 1.0:
        return "single-platform_single-surface_physical_evidence"
    if comp > direct:
        return "negative_result_requires_compensator_revision"
    return "partial_or_inconclusive_physical_evidence"


def build_report(summary: dict[str, Any], pair_rows: list[dict[str, Any]], per_velocity_rows: list[dict[str, Any]]) -> str:
    metrics = summary["aggregate_metrics"]
    stats = summary["statistical_tests"]
    lines = [
        "# M23-C K1 Before/After Compensation Analysis",
        "",
        f"Session: `{summary['session_id']}`",
        f"Surface: `{summary['surface']}`",
        f"Claim level: `{summary['claim_level']}`",
        "",
        "## Validation",
        f"- Extracted trials: {summary['validation']['trial_count']}",
        f"- Complete pairs: {summary['validation']['pair_count']}",
        f"- QC: {summary['validation']['qc_checks_passed']}/{summary['validation']['qc_checks_total']} checks passed",
        f"- Desired velocities: {', '.join(str(v) for v in summary['validation']['desired_velocities_mps'])}",
        "",
        "## Aggregate Results",
        f"- Mean absolute error, direct: {_fmt(metrics['mean_absolute_error_direct'])} m/s",
        f"- Mean absolute error, compensated: {_fmt(metrics['mean_absolute_error_compensated'])} m/s",
        f"- Percent reduction in mean absolute error: {_fmt(metrics['percent_reduction_mean_absolute_error'])}%",
        f"- Improved pairs: {metrics['improved_pairs']}",
        f"- Worsened pairs: {metrics['worsened_pairs']}",
        f"- No-change pairs: {metrics['no_change_pairs']}",
        f"- Mean yaw drift, direct: {_fmt(metrics['yaw_drift_mean_direct'])} deg",
        f"- Mean yaw drift, compensated: {_fmt(metrics['yaw_drift_mean_compensated'])} deg",
        f"- Invalid rate, direct: {_fmt(metrics['invalid_rate_direct'])}",
        f"- Invalid rate, compensated: {_fmt(metrics['invalid_rate_compensated'])}",
        "",
        "## Statistical Analysis",
        f"- scipy available: {stats['scipy_available']}",
        f"- Effect size Cohen dz: {_fmt(stats['effect_size_cohen_dz'])}",
    ]
    if stats.get("paired_t_test"):
        lines.append(f"- Paired t-test p-value: {_fmt(stats['paired_t_test'].get('p_value'))}")
    if stats.get("wilcoxon_signed_rank"):
        lines.append(f"- Wilcoxon signed-rank p-value: {_fmt(stats['wilcoxon_signed_rank'].get('p_value'))}")
    for note in stats.get("notes", []):
        lines.append(f"- Note: {note}")

    lines += [
        "",
        "These statistical tests are descriptive support for n=12 paired trials. The result should be interpreted conservatively.",
        "",
        "## Per-Velocity Summary",
        "",
        "| Desired velocity | Pairs | Direct mean error | Compensated mean error | Mean improvement |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in per_velocity_rows:
        lines.append(
            f"| {_fmt(row['desired_velocity_mps'])} | {row['pair_count']} | "
            f"{_fmt(row['mean_direct_abs_error'])} | {_fmt(row['mean_compensated_abs_error'])} | "
            f"{_fmt(row['mean_improvement'])} |"
        )

    lines += [
        "",
        "## Pair Results",
        "",
        "| Pair | Desired | Direct error | Compensated error | Improvement | Yaw delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in pair_rows:
        lines.append(
            f"| `{row['pair_id']}` | {_fmt(row['desired_velocity_mps'])} | "
            f"{_fmt(row['direct_abs_error'])} | {_fmt(row['compensated_abs_error'])} | "
            f"{_fmt(row['improvement'])} | {_fmt(row['yaw_drift_delta'])} |"
        )

    lines += [
        "",
        "## Baseline And Ablation Positioning",
        "",
        "The physical direct condition is the direct-command baseline. The physical compensated condition is the M22-C risk-aware inverse lookup output. Scalar gain, nearest lookup, and ordinary interpolation were not executed as physical baselines in this session, so they remain offline context only.",
        "",
        "## Claim Boundary",
        "",
        "This analysis supports only the stated single Booster K1, single S2 marble floor experiment. It does not claim deployment readiness, navigation improvement, GO1/G1 validation, cross-platform physical validation, or universal K1 generalization.",
    ]
    return "\n".join(lines) + "\n"


def build_claim_boundary(summary: dict[str, Any]) -> str:
    return f"""# M23-C Claim Boundary

Claim level: `{summary['claim_level']}`

Allowed claim:

- M23-C analyzes one physical Booster K1 before/after compensation experiment on `S2_marble_floor`.

Not claimed:

- Deployment readiness.
- Navigation improvement.
- GO1 or G1 validation.
- Cross-platform physical validation.
- Universal K1 generalization.
- Physical evidence for scalar gain, nearest lookup, or ordinary interpolation baselines.

The result may inform the paper narrative only as single-platform, single-surface physical evidence.
"""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _invalid_rates(records: list[dict[str, str]]) -> dict[str, float]:
    counts = {"direct": 0, "compensated": 0}
    invalid = {"direct": 0, "compensated": 0}
    for row in records:
        condition = row.get("condition", "")
        if condition not in counts:
            continue
        counts[condition] += 1
        if row.get("valid", "").lower() != "true":
            invalid[condition] += 1
    return {
        condition: (invalid[condition] / counts[condition] if counts[condition] else 0.0)
        for condition in counts
    }


def _blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _finite_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
