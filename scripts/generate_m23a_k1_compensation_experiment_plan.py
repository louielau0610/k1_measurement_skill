"""Generate M23-A K1 physical compensation experiment trial plans.

Generates a full traceability plan and a separate executable-only paired plan.
No hardware execution occurs here.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import (  # noqa: E402
    SUPPORTED_EMPIRICAL_PLATFORM,
    CompensationRequest,
)
from calibration_core.velocity_compensation import compensate_velocity  # noqa: E402

OUTPUT_DIR = Path("outputs/compensation_experiments")
DEFAULT_SURFACE = "S2_marble_floor"
DEFAULT_VELOCITIES = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
DEFAULT_REPEATS = 3
DEFAULT_RISK_POLICY = "balanced"
DEFAULT_MINIMUM_CONFIDENCE = 0.5
PROFILE_PATH = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
CONTRACT_CSV = Path("outputs/measurement_v1/booster_k1_measurements_contract_v1.csv")
EXECUTABLE_COMPENSATOR_STATUSES = {"ok", "feasible_but_risky"}

EXPERIMENT_PLAN_FIELDS = [
    "trial_id", "pair_id", "surface", "desired_velocity_mps",
    "condition", "command_velocity_mps", "risk_policy",
    "compensator_status", "compensator_reason",
    "repeat_index", "order_in_pair", "randomization_seed",
    "physical_run_status", "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate M23-A K1 compensation experiment trial plans.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--surface", default=DEFAULT_SURFACE, help=f"Surface identifier (default: {DEFAULT_SURFACE})")
    parser.add_argument("--velocities", nargs="*", type=float, default=DEFAULT_VELOCITIES, help="Desired velocities in m/s")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS, help=f"Paired repeats per velocity (default: {DEFAULT_REPEATS})")
    parser.add_argument("--risk-policy", default=DEFAULT_RISK_POLICY, choices=["conservative", "balanced", "permissive"], help=f"Risk policy (default: {DEFAULT_RISK_POLICY})")
    parser.add_argument("--minimum-confidence", type=float, default=DEFAULT_MINIMUM_CONFIDENCE, help=f"Minimum compensator confidence (default: {DEFAULT_MINIMUM_CONFIDENCE})")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Randomization seed")
    parser.add_argument("--no-randomize", action="store_true", help="Use deterministic order instead of alternating condition order")
    args = parser.parse_args(argv)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)
    timestamp = datetime.now(timezone.utc).isoformat()

    print("=" * 60)
    print("  M23-A K1 Compensation Experiment Plan Generator")
    print(f"  Surface:        {args.surface}")
    print(f"  Velocities:     {args.velocities}")
    print(f"  Repeats:        {args.repeats}")
    print(f"  Risk policy:    {args.risk_policy}")
    print(f"  Min confidence: {args.minimum_confidence}")
    print(f"  Random seed:    {args.seed}")
    print(f"  Output:         {output_dir}")
    print("  NO HARDWARE EXECUTION - plan generation only")
    print("=" * 60)

    trials = _build_trial_plan(args)
    validation_errors = _validate_trial_plan(trials)
    if validation_errors:
        print("\nERROR: M23-A trial plan validation failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    executable_trials, excluded_pair_reasons = _build_executable_trials(trials)
    executable_pair_count = len({t["pair_id"] for t in executable_trials})
    if executable_pair_count == 0:
        print(
            "\nWARNING: No executable compensated pairs were produced. "
            "Use --risk-policy permissive with an evidence-appropriate --minimum-confidence "
            "if the offline compensator supports the selected targets.",
            file=sys.stderr,
        )

    trial_csv = output_dir / "m23a_trial_plan.csv"
    _write_csv(trial_csv, trials)
    print(f"\nTrial plan CSV: {trial_csv} ({len(trials)} trials)")

    executable_csv = output_dir / "m23a_executable_trial_plan.csv"
    _write_csv(executable_csv, executable_trials)
    print(f"Executable trial plan CSV: {executable_csv} ({len(executable_trials)} trials)")

    plan_data = _build_plan_data(
        args=args,
        timestamp=timestamp,
        trials=trials,
        executable_trials=executable_trials,
        excluded_pair_reasons=excluded_pair_reasons,
        trial_csv=trial_csv,
        executable_csv=executable_csv,
    )

    plan_json = output_dir / "m23a_experiment_plan.json"
    plan_json.write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
    print(f"Experiment plan JSON: {plan_json}")

    plan_md = output_dir / "m23a_experiment_plan.md"
    plan_md.write_text(_build_plan_md(plan_data, trials, timestamp), encoding="utf-8")
    print(f"Experiment plan MD: {plan_md}")

    analysis_md = output_dir / "m23a_analysis_plan.md"
    analysis_md.write_text(_build_analysis_md(plan_data, timestamp), encoding="utf-8")
    print(f"Analysis plan MD: {analysis_md}")

    executable_summary = _build_executable_summary(
        plan_data,
        executable_trials,
        excluded_pair_reasons,
        executable_csv,
        timestamp,
    )
    executable_summary_json = output_dir / "m23a_executable_trial_plan_summary.json"
    executable_summary_json.write_text(json.dumps(executable_summary, indent=2), encoding="utf-8")
    print(f"Executable summary JSON: {executable_summary_json}")

    executable_summary_md = output_dir / "m23a_executable_trial_plan_summary.md"
    executable_summary_md.write_text(_build_executable_summary_md(executable_summary), encoding="utf-8")
    print(f"Executable summary MD: {executable_summary_md}")

    direct_count = plan_data["direct_trials"]
    comp_count = plan_data["compensated_trials"]
    print(f"\n{'=' * 60}")
    print(f"  Plan generated: {len(trials)} trials ({direct_count} direct + {comp_count} compensated)")
    print(f"  Pairs: {plan_data['planned_pairs']}")
    print(f"  Executable pairs: {executable_pair_count}")
    print(f"  Infeasible compensated targets: {plan_data['infeasible_compensation_targets']}")
    print("  NO HARDWARE EXECUTION - plan generation only")
    print(f"{'=' * 60}")

    return 0


def _build_trial_plan(args: argparse.Namespace) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    for velocity in args.velocities:
        request = CompensationRequest(
            platform=SUPPORTED_EMPIRICAL_PLATFORM,
            robot_model="Booster K1",
            surface_type=args.surface,
            desired_actual_velocity_mps=velocity,
            response_profile_path=PROFILE_PATH,
            contract_csv_path=CONTRACT_CSV,
            risk_policy=args.risk_policy,
            minimum_confidence=args.minimum_confidence,
        )
        decision = compensate_velocity(request)
        compensator_status = decision.feasibility_status
        compensated_cmd = decision.recommended_command_velocity_mps

        for rep in range(1, args.repeats + 1):
            pair_id = f"M23A_{args.surface}_V{int(velocity * 100):03d}_P{rep}"
            conditions = ["direct", "compensated"] if args.no_randomize or rep % 2 == 1 else ["compensated", "direct"]
            for order_idx, condition in enumerate(conditions, 1):
                if condition == "direct":
                    cmd_vel: float | str = velocity
                    cmd_status = "na_direct_baseline"
                    cmd_reason = "u_cmd = v_desired (no compensation)"
                else:
                    if compensator_status in EXECUTABLE_COMPENSATOR_STATUSES and compensated_cmd is None:
                        raise ValueError(
                            f"Compensator returned {compensator_status!r} with blank command "
                            f"for desired velocity {velocity}"
                        )
                    cmd_vel = compensated_cmd if compensated_cmd is not None else ""
                    cmd_status = compensator_status
                    cmd_reason = decision.reason

                executable_compensated = (
                    condition == "compensated"
                    and cmd_status in EXECUTABLE_COMPENSATOR_STATUSES
                    and not _is_blank(cmd_vel)
                )
                infeasible_compensated = condition == "compensated" and not executable_compensated
                trial_id = f"M23A_{args.surface}_V{int(velocity * 100):03d}_{condition[:4]}_R{rep}"
                trials.append({
                    "trial_id": trial_id,
                    "pair_id": pair_id,
                    "surface": args.surface,
                    "desired_velocity_mps": velocity,
                    "condition": condition,
                    "command_velocity_mps": cmd_vel,
                    "risk_policy": args.risk_policy if condition == "compensated" else "na_direct",
                    "compensator_status": cmd_status,
                    "compensator_reason": cmd_reason,
                    "repeat_index": rep,
                    "order_in_pair": order_idx,
                    "randomization_seed": args.seed,
                    "physical_run_status": "not_executable" if infeasible_compensated else "planned",
                    "notes": "excluded_from_executable_plan" if infeasible_compensated else "",
                })
    return trials


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPERIMENT_PLAN_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _validate_trial_plan(trials: list[dict[str, Any]]) -> list[str]:
    errors = []
    seen_trial_ids: set[str] = set()
    for trial in trials:
        trial_id = str(trial.get("trial_id", ""))
        if trial_id in seen_trial_ids:
            errors.append(f"duplicate trial_id {trial_id}")
        seen_trial_ids.add(trial_id)
        if (
            trial.get("condition") == "compensated"
            and trial.get("compensator_status") in EXECUTABLE_COMPENSATOR_STATUSES
            and _is_blank(trial.get("command_velocity_mps"))
        ):
            errors.append(
                f"{trial_id} has compensator_status={trial.get('compensator_status')} "
                "but blank command_velocity_mps"
            )
    return errors


def _build_executable_trials(
    trials: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for trial in trials:
        by_pair.setdefault(str(trial["pair_id"]), []).append(trial)

    executable: list[dict[str, Any]] = []
    excluded: dict[str, str] = {}
    for pair_id in sorted(by_pair):
        rows = sorted(by_pair[pair_id], key=lambda row: int(row["order_in_pair"]))
        direct = [row for row in rows if row["condition"] == "direct"]
        compensated = [row for row in rows if row["condition"] == "compensated"]
        if len(direct) != 1 or len(compensated) != 1:
            excluded[pair_id] = "missing direct/compensated pair member"
            continue
        comp = compensated[0]
        if comp["compensator_status"] not in EXECUTABLE_COMPENSATOR_STATUSES:
            excluded[pair_id] = f"compensator_status={comp['compensator_status']}"
            continue
        if _is_blank(comp["command_velocity_mps"]):
            excluded[pair_id] = "blank compensated command_velocity_mps"
            continue
        executable.extend(rows)
    return executable, excluded


def _build_plan_data(
    *,
    args: argparse.Namespace,
    timestamp: str,
    trials: list[dict[str, Any]],
    executable_trials: list[dict[str, Any]],
    excluded_pair_reasons: dict[str, str],
    trial_csv: Path,
    executable_csv: Path,
) -> dict[str, Any]:
    infeasible_count = sum(
        1
        for trial in trials
        if trial["condition"] == "compensated"
        and trial["compensator_status"] not in EXECUTABLE_COMPENSATOR_STATUSES
    )
    executable_pair_count = len({trial["pair_id"] for trial in executable_trials})
    return {
        "experiment_id": f"m23a_k1_compensation_{args.surface}",
        "generated_at": timestamp,
        "m23a_status": "experiment_design_only",
        "physical_validation": "not_started",
        "deployment_ready": False,
        "platform": SUPPORTED_EMPIRICAL_PLATFORM,
        "robot_model": "Booster K1",
        "surface": args.surface,
        "desired_velocities_mps": args.velocities,
        "repeats": args.repeats,
        "risk_policy": args.risk_policy,
        "minimum_confidence": args.minimum_confidence,
        "total_planned_trials": len(trials),
        "planned_pairs": len(trials) // 2,
        "executable_trials": len(executable_trials),
        "executable_pairs": executable_pair_count,
        "infeasible_compensation_targets": infeasible_count,
        "direct_trials": sum(1 for trial in trials if trial["condition"] == "direct"),
        "compensated_trials": sum(1 for trial in trials if trial["condition"] == "compensated"),
        "trial_plan_csv": str(trial_csv),
        "executable_trial_plan_csv": str(executable_csv),
        "compensator_version": "M22-C",
        "randomization_seed": args.seed,
        "randomized": not args.no_randomize,
        "go1_g1_included": False,
        "hardware_execution": False,
        "warnings": [] if executable_pair_count else ["no executable compensated pairs produced"],
        "excluded_pair_reasons": excluded_pair_reasons,
        "disclaimer": "experiment design only - no hardware execution - no physical validation claim",
    }


def _build_executable_summary(
    plan: dict[str, Any],
    executable_trials: list[dict[str, Any]],
    excluded_pair_reasons: dict[str, str],
    executable_csv: Path,
    timestamp: str,
) -> dict[str, Any]:
    pair_ids = sorted({trial["pair_id"] for trial in executable_trials})
    compensated_rows = [trial for trial in executable_trials if trial["condition"] == "compensated"]
    direct_rows = [trial for trial in executable_trials if trial["condition"] == "direct"]
    desired_velocities = sorted({float(trial["desired_velocity_mps"]) for trial in executable_trials})
    blank_compensated = [
        trial["trial_id"]
        for trial in compensated_rows
        if _is_blank(trial.get("command_velocity_mps"))
    ]
    return {
        "generated_at": timestamp,
        "source_trial_plan_csv": plan["trial_plan_csv"],
        "executable_trial_plan_csv": str(executable_csv),
        "risk_policy": plan["risk_policy"],
        "minimum_confidence": plan["minimum_confidence"],
        "surface": plan["surface"],
        "executable_trial_count": len(executable_trials),
        "executable_pair_count": len(pair_ids),
        "direct_trial_count": len(direct_rows),
        "compensated_trial_count": len(compensated_rows),
        "desired_velocities_mps": desired_velocities,
        "compensated_command_velocity_complete": len(blank_compensated) == 0,
        "blank_compensated_command_trial_ids": blank_compensated,
        "allowed_compensator_statuses": sorted(EXECUTABLE_COMPENSATOR_STATUSES),
        "excluded_pair_count": len(excluded_pair_reasons),
        "excluded_pair_reasons": excluded_pair_reasons,
        "hardware_execution": False,
        "physical_validation": "not_started",
        "deployment_ready": False,
        "claim_boundary": "executable plan only - no hardware execution and no tracking improvement claim",
    }


def _build_plan_md(plan: dict[str, Any], trials: list[dict[str, Any]], timestamp: str) -> str:
    lines = [
        "# M23-A K1 Compensation Experiment Plan",
        "",
        f"Generated: {timestamp}",
        f"Surface: {plan['surface']}",
        f"Platform: {plan['platform']}",
        f"Risk policy: {plan['risk_policy']}",
        f"Minimum confidence: {plan['minimum_confidence']}",
        "",
        "**Status**: EXPERIMENT DESIGN ONLY - no hardware execution - no physical validation claim",
        "",
        "## Trial Plan Summary",
        f"- Total traceability trials: {plan['total_planned_trials']}",
        f"- Traceability pairs: {plan['planned_pairs']}",
        f"- Executable trials: {plan['executable_trials']}",
        f"- Executable pairs: {plan['executable_pairs']}",
        f"- Direct trials: {plan['direct_trials']}",
        f"- Compensated trials: {plan['compensated_trials']}",
        f"- Infeasible compensated targets: {plan['infeasible_compensation_targets']}",
        f"- Executable plan: `{plan['executable_trial_plan_csv']}`",
        f"- Random seed: {plan['randomization_seed']}",
        "",
        "## Desired Velocities",
    ]
    for velocity in plan["desired_velocities_mps"]:
        lines.append(f"- {velocity} m/s")

    lines += [
        "",
        "## Infeasible Pair Handling",
    ]
    if plan["excluded_pair_reasons"]:
        for pair_id, reason in plan["excluded_pair_reasons"].items():
            lines.append(f"- `{pair_id}` excluded from executable plan: {reason}")
    else:
        lines.append("- No pairs excluded from executable plan.")

    lines += [
        "",
        "## Trial Plan",
        "",
        "| # | Trial ID | Pair | v_desired | Condition | u_cmd | Status | Run status |",
        "|---|----------|------|-----------|-----------|-------|--------|------------|",
    ]
    for index, trial in enumerate(trials, 1):
        cmd_value = trial["command_velocity_mps"]
        cmd_str = f"{cmd_value:.3f}" if isinstance(cmd_value, (int, float)) else str(cmd_value)
        lines.append(
            f"| {index} | {trial['trial_id']} | {trial['pair_id']} | "
            f"{trial['desired_velocity_mps']} | {trial['condition']} | {cmd_str} | "
            f"{trial['compensator_status']} | {trial['physical_run_status']} |"
        )

    lines += [
        "",
        "## Next Steps",
        "1. M23-B formal before/after execution must use the executable trial plan CSV.",
        "2. Record ROS2 state logs for executable pairs only.",
        "3. M23-C analyzes before/after results only after physical data pass QC.",
    ]
    return "\n".join(lines) + "\n"


def _build_analysis_md(plan: dict[str, Any], timestamp: str) -> str:
    return f"""# M23-A K1 Compensation Analysis Plan

Generated: {timestamp}
Status: Analysis plan only - no data to analyze yet.

## Analysis Set

Use only complete executable pairs from `{plan['executable_trial_plan_csv']}`.
The current executable pair count is {plan['executable_pairs']}. Infeasible pairs
from the full traceability plan are excluded from paired before/after comparison.

## Analysis Steps

1. Load trial results per the M23-A result schema.
2. Pair direct and compensated trials by `pair_id`.
3. Compute per-pair absolute tracking error for both conditions.
4. Compute per-pair error difference: `error_direct - error_compensated`.
5. Compute per-pair yaw drift difference.
6. Aggregate across executable pairs on `{plan['surface']}`.

## Statistical Tests

- **Primary**: Wilcoxon signed-rank test if enough executable pairs have valid physical measurements.
- **Alternative**: Paired t-test if normality assumption is reasonable.
- **Effect size**: Rank-biserial correlation.

## Success Criteria

1. Mean absolute tracking error lower for compensated vs. direct.
2. No significant increase in yaw drift.
3. No increase in invalid trial rate.
4. Infeasible targets rejected, not forced.

## Outputs (to be generated by M23-C)

- `outputs/compensation_experiments/m23c_before_after_analysis.json`
- `outputs/compensation_experiments/m23c_before_after_analysis.md`
- Per-velocity error comparison table
- Before/after plots

## Claim Levels

| Result | Claim |
|--------|-------|
| Significant improvement (p < 0.05) | Compensation reduces tracking error on {plan['surface']} |
| Suggestive but not significant | More data needed |
| No improvement | Compensation does not help on this surface |
"""


def _build_executable_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# M23-A Executable Trial Plan Summary",
        "",
        f"Generated: {summary['generated_at']}",
        f"Surface: {summary['surface']}",
        f"Risk policy: {summary['risk_policy']}",
        f"Minimum confidence: {summary['minimum_confidence']}",
        "",
        "## Summary",
        f"- Executable trial plan: `{summary['executable_trial_plan_csv']}`",
        f"- Executable pairs: {summary['executable_pair_count']}",
        f"- Executable trials: {summary['executable_trial_count']}",
        f"- Direct trials: {summary['direct_trial_count']}",
        f"- Compensated trials: {summary['compensated_trial_count']}",
        f"- Compensated command velocity complete: {summary['compensated_command_velocity_complete']}",
        f"- Excluded pairs: {summary['excluded_pair_count']}",
        "",
        "## Executable Desired Velocities",
    ]
    for velocity in summary["desired_velocities_mps"]:
        lines.append(f"- {velocity} m/s")

    lines += [
        "",
        "## Excluded Pairs",
    ]
    if summary["excluded_pair_reasons"]:
        for pair_id, reason in summary["excluded_pair_reasons"].items():
            lines.append(f"- `{pair_id}`: {reason}")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Claim Boundary",
        summary["claim_boundary"],
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
