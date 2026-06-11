"""Generate M23-A K1 physical compensation experiment trial plan.

Generates a paired before/after trial plan comparing direct (uncompensated)
and compensated commands for the same desired velocity and surface.

Default: S2_marble_floor, 6 desired velocities, 3 repeats, balanced risk policy.
No hardware execution — plan generation only.

Usage:
  python scripts/generate_m23a_k1_compensation_experiment_plan.py
  python scripts/generate_m23a_k1_compensation_experiment_plan.py --surface S1_lab_hard_floor --repeats 5
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

from calibration_core.compensation_models import (
    SUPPORTED_EMPIRICAL_PLATFORM,
    CompensationRequest,
)
from calibration_core.velocity_compensation import compensate_velocity

OUTPUT_DIR = Path("outputs/compensation_experiments")
DEFAULT_SURFACE = "S2_marble_floor"
DEFAULT_VELOCITIES = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
DEFAULT_REPEATS = 3
DEFAULT_RISK_POLICY = "balanced"
PROFILE_PATH = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
CONTRACT_CSV = Path("outputs/measurement_v1/booster_k1_measurements_contract_v1.csv")

EXPERIMENT_PLAN_FIELDS = [
    "trial_id", "pair_id", "surface", "desired_velocity_mps",
    "condition", "command_velocity_mps", "risk_policy",
    "compensator_status", "compensator_reason",
    "repeat_index", "order_in_pair", "randomization_seed",
    "physical_run_status", "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate M23-A K1 compensation experiment trial plan.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_m23a_k1_compensation_experiment_plan.py
  python scripts/generate_m23a_k1_compensation_experiment_plan.py --repeats 5
  python scripts/generate_m23a_k1_compensation_experiment_plan.py --surface S1_lab_hard_floor
        """,
    )
    parser.add_argument("--surface", default=DEFAULT_SURFACE, help=f"Surface identifier (default: {DEFAULT_SURFACE})")
    parser.add_argument("--velocities", nargs="*", type=float, default=DEFAULT_VELOCITIES, help="Desired velocities in m/s")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS, help=f"Paired repeats per velocity (default: {DEFAULT_REPEATS})")
    parser.add_argument("--risk-policy", default=DEFAULT_RISK_POLICY, choices=["conservative", "balanced", "permissive"], help=f"Risk policy (default: {DEFAULT_RISK_POLICY})")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Randomization seed")
    parser.add_argument("--no-randomize", action="store_true", help="Use deterministic order instead of randomized")
    args = parser.parse_args(argv)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)
    timestamp = datetime.now(timezone.utc).isoformat()

    surface = args.surface
    velocities = args.velocities
    repeats = args.repeats
    risk_policy = args.risk_policy

    print("=" * 60)
    print("  M23-A K1 Compensation Experiment Plan Generator")
    print(f"  Surface:        {surface}")
    print(f"  Velocities:     {velocities}")
    print(f"  Repeats:        {repeats}")
    print(f"  Risk policy:    {risk_policy}")
    print(f"  Random seed:    {args.seed}")
    print(f"  Output:         {output_dir}")
    print(f"  NO HARDWARE EXECUTION — plan generation only")
    print("=" * 60)

    # Generate trial plan
    trials: list[dict[str, Any]] = []
    infeasible_count = 0

    for velocity in velocities:
        # Get compensated command from offline compensator
        request = CompensationRequest(
            platform=SUPPORTED_EMPIRICAL_PLATFORM,
            robot_model="Booster K1",
            surface_type=surface,
            desired_actual_velocity_mps=velocity,
            response_profile_path=PROFILE_PATH,
            contract_csv_path=CONTRACT_CSV,
            risk_policy=risk_policy,
        )
        decision = compensate_velocity(request)
        compensator_status = decision.feasibility_status
        compensated_cmd = decision.recommended_command_velocity_mps

        # Randomize velocity order
        if args.no_randomize:
            vel_order = velocities
        else:
            vel_order = random.sample(velocities, len(velocities))

        for rep in range(1, repeats + 1):
            pair_id = f"M23A_{surface}_V{int(velocity*100):03d}_P{rep}"

            # Randomize condition order within pair
            if args.no_randomize or rep % 2 == 1:
                conditions = ["direct", "compensated"]
            else:
                conditions = ["compensated", "direct"]

            for order_idx, condition in enumerate(conditions, 1):
                if condition == "direct":
                    cmd_vel = velocity
                    cmd_status = "na_direct_baseline"
                    cmd_reason = "u_cmd = v_desired (no compensation)"
                else:
                    cmd_vel = compensated_cmd
                    cmd_status = compensator_status
                    cmd_reason = decision.reason
                    if compensator_status not in ("ok", "feasible_but_risky"):
                        infeasible_count += 1

                trial_id = f"M23A_{surface}_V{int(velocity*100):03d}_{condition[:4]}_R{rep}"
                trials.append({
                    "trial_id": trial_id,
                    "pair_id": pair_id,
                    "surface": surface,
                    "desired_velocity_mps": velocity,
                    "condition": condition,
                    "command_velocity_mps": cmd_vel if cmd_vel is not None else "",
                    "risk_policy": risk_policy if condition == "compensated" else "na_direct",
                    "compensator_status": cmd_status,
                    "compensator_reason": cmd_reason,
                    "repeat_index": rep,
                    "order_in_pair": order_idx,
                    "randomization_seed": args.seed,
                    "physical_run_status": "planned",
                    "notes": "",
                })

    # Write trial plan CSV
    trial_csv = output_dir / "m23a_trial_plan.csv"
    with trial_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXPERIMENT_PLAN_FIELDS, extrasaction="ignore")
        w.writeheader()
        for t in trials:
            w.writerow(t)
    print(f"\nTrial plan CSV: {trial_csv} ({len(trials)} trials)")

    # Write experiment plan JSON
    plan_json = output_dir / "m23a_experiment_plan.json"
    plan_data = {
        "experiment_id": f"m23a_k1_compensation_{surface}",
        "generated_at": timestamp,
        "m23a_status": "experiment_design_only",
        "physical_validation": "not_started",
        "deployment_ready": False,
        "platform": SUPPORTED_EMPIRICAL_PLATFORM,
        "robot_model": "Booster K1",
        "surface": surface,
        "desired_velocities_mps": velocities,
        "repeats": repeats,
        "risk_policy": risk_policy,
        "total_planned_trials": len(trials),
        "planned_pairs": len(trials) // 2,
        "infeasible_compensation_targets": infeasible_count,
        "direct_trials": sum(1 for t in trials if t["condition"] == "direct"),
        "compensated_trials": sum(1 for t in trials if t["condition"] == "compensated"),
        "trial_plan_csv": str(trial_csv),
        "compensator_version": "M22-C",
        "randomization_seed": args.seed,
        "randomized": not args.no_randomize,
        "go1_g1_included": False,
        "hardware_execution": False,
        "disclaimer": "experiment design only — no hardware execution — no physical validation claim",
    }
    plan_json.write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
    print(f"Experiment plan JSON: {plan_json}")

    # Write experiment plan MD
    plan_md = output_dir / "m23a_experiment_plan.md"
    plan_md.write_text(_build_plan_md(plan_data, trials, timestamp), encoding="utf-8")
    print(f"Experiment plan MD: {plan_md}")

    # Write analysis plan MD
    analysis_md = output_dir / "m23a_analysis_plan.md"
    analysis_md.write_text(_build_analysis_md(plan_data, timestamp), encoding="utf-8")
    print(f"Analysis plan MD: {analysis_md}")

    # Summary
    direct_count = plan_data["direct_trials"]
    comp_count = plan_data["compensated_trials"]
    print(f"\n{'=' * 60}")
    print(f"  Plan generated: {len(trials)} trials ({direct_count} direct + {comp_count} compensated)")
    print(f"  Pairs: {plan_data['planned_pairs']}")
    print(f"  Infeasible compensated targets: {infeasible_count}")
    print(f"  NO HARDWARE EXECUTION — plan generation only")
    print(f"{'=' * 60}")

    return 0


def _build_plan_md(plan: dict, trials: list[dict], timestamp: str) -> str:
    lines = [
        "# M23-A K1 Compensation Experiment Plan",
        "",
        f"Generated: {timestamp}",
        f"Surface: {plan['surface']}",
        f"Platform: {plan['platform']}",
        f"Risk policy: {plan['risk_policy']}",
        "",
        f"**Status**: EXPERIMENT DESIGN ONLY — no hardware execution — no physical validation claim",
        "",
        "## Trial Plan Summary",
        f"- Total trials: {plan['total_planned_trials']}",
        f"- Pairs: {plan['planned_pairs']}",
        f"- Direct trials: {plan['direct_trials']}",
        f"- Compensated trials: {plan['compensated_trials']}",
        f"- Infeasible compensated targets: {plan['infeasible_compensation_targets']}",
        f"- Random seed: {plan['randomization_seed']}",
        "",
        "## Desired Velocities",
    ]
    for v in plan["desired_velocities_mps"]:
        lines.append(f"- {v} m/s")

    lines += [
        "",
        "## Trial Plan",
        "",
        "| # | Trial ID | Pair | v_desired | Condition | u_cmd | Status |",
        "|---|----------|------|-----------|-----------|-------|--------|",
    ]
    for i, t in enumerate(trials, 1):
        cmd_str = f"{t['command_velocity_mps']:.3f}" if isinstance(t['command_velocity_mps'], (int, float)) else str(t['command_velocity_mps'])
        lines.append(f"| {i} | {t['trial_id']} | {t['pair_id']} | {t['desired_velocity_mps']} | {t['condition']} | {cmd_str} | {t['compensator_status']} |")

    lines += [
        "",
        "## Next Steps",
        "1. M23-B: Execute this plan on physical Booster K1.",
        "2. Record ROS2 state logs for all trials.",
        "3. M23-C: Analyze before/after results.",
    ]
    return "\n".join(lines) + "\n"


def _build_analysis_md(plan: dict, timestamp: str) -> str:
    return f"""# M23-A K1 Compensation Analysis Plan

Generated: {timestamp}
Status: Analysis plan only — no data to analyze yet.

## Analysis Steps

1. Load trial results per the M23-A result schema.
2. Pair direct and compensated trials by `pair_id`.
3. Compute per-pair absolute tracking error for both conditions.
4. Compute per-pair error difference: `error_direct - error_compensated`.
5. Compute per-pair yaw drift difference.
6. Aggregate across all pairs on `{plan['surface']}`.

## Statistical Tests

- **Primary**: Wilcoxon signed-rank test (nonparametric, appropriate for n={plan['planned_pairs']} pairs).
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
