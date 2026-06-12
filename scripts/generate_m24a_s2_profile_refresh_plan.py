"""Generate the M24-A S2 current-condition profile refresh plan.

This is a design-only artifact generator. It does not execute hardware and
does not update any Booster K1 gold profile.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("outputs/compensation_experiments")
DEFAULT_SURFACE = "S2_marble_floor"
DEFAULT_VELOCITIES = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
DEFAULT_REPEATS = 5
PROFILE_MISMATCH_THRESHOLD_MPS = 0.03

PLAN_FIELDS = [
    "trial_id",
    "surface",
    "command_velocity_mps",
    "desired_velocity_mps",
    "condition",
    "repeat_index",
    "refresh_group_id",
    "physical_run_status",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate M24-A S2 profile refresh design artifacts.")
    parser.add_argument("--surface", default=DEFAULT_SURFACE)
    parser.add_argument("--velocities", nargs="*", type=float, default=DEFAULT_VELOCITIES)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--profile-mismatch-threshold-mps",
        type=float,
        default=PROFILE_MISMATCH_THRESHOLD_MPS,
    )
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    trials = build_plan(args.surface, args.velocities, args.repeats)

    csv_path = args.output_dir / "m24a_s2_profile_refresh_plan.csv"
    write_csv(csv_path, trials)

    summary = build_summary(
        surface=args.surface,
        velocities=args.velocities,
        repeats=args.repeats,
        threshold=args.profile_mismatch_threshold_mps,
        trials=trials,
        csv_path=csv_path,
        timestamp=timestamp,
    )

    json_path = args.output_dir / "m24a_s2_profile_refresh_plan.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_path = args.output_dir / "m24a_s2_profile_refresh_plan.md"
    md_path.write_text(build_markdown(summary, trials), encoding="utf-8")

    print("M24-A S2 profile refresh plan generated")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("NO HARDWARE EXECUTION - design only")
    return 0


def build_plan(surface: str, velocities: list[float], repeats: int) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    for velocity in sorted(velocities):
        group_id = f"M24A_{surface}_V{int(round(velocity * 100)):03d}"
        for repeat_index in range(1, repeats + 1):
            trials.append(
                {
                    "trial_id": f"{group_id}_R{repeat_index}",
                    "surface": surface,
                    "command_velocity_mps": f"{velocity:.2f}",
                    "desired_velocity_mps": f"{velocity:.2f}",
                    "condition": "direct_refresh",
                    "repeat_index": repeat_index,
                    "refresh_group_id": group_id,
                    "physical_run_status": "planned",
                    "notes": "direct command only; no compensation in M24-A/M24-B refresh",
                }
            )
    return trials


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(
    *,
    surface: str,
    velocities: list[float],
    repeats: int,
    threshold: float,
    trials: list[dict[str, Any]],
    csv_path: Path,
    timestamp: str,
) -> dict[str, Any]:
    return {
        "milestone": "M24-A",
        "generated_at": timestamp,
        "status": "profile_refresh_design_only",
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "surface": surface,
        "command_velocities_mps": [round(v, 2) for v in sorted(velocities)],
        "desired_velocities_mps": [round(v, 2) for v in sorted(velocities)],
        "repeats_per_velocity": repeats,
        "recommended_minimum_repeats": 3,
        "condition": "direct_refresh",
        "trial_count": len(trials),
        "refresh_group_count": len({row["refresh_group_id"] for row in trials}),
        "trial_plan_csv": str(csv_path),
        "profile_mismatch_metrics": {
            "old_m19c_mean_actual_velocity_mps": "required_in_M24_C",
            "new_refresh_mean_actual_velocity_mps": "required_in_M24_C",
            "difference_mps": "new_refresh_mean_actual_velocity_mps - old_m19c_mean_actual_velocity_mps",
            "absolute_difference_mps": "abs(difference_mps)",
            "old_uncertainty_mps": "required_in_M24_C",
            "new_uncertainty_mps": "required_in_M24_C",
            "profile_mismatch_threshold_mps": threshold,
            "profile_mismatch_flag": "absolute_difference_mps >= profile_mismatch_threshold_mps",
            "yaw_drift_comparison": "required_in_M24_C",
            "no_motion_rate": "required_in_M24_C",
            "repeat_variability": "required_in_M24_C",
            "direct_tracking_near_optimal": "required_in_M24_C",
        },
        "old_profile_path": "outputs/real_k1_validation_m19/k1_gold_profile_v1.json",
        "new_profile_output": "not_created_in_M24_A",
        "hardware_execution": False,
        "physical_profile_refresh_status": "not_run",
        "gold_profile_overwritten": False,
        "revised_compensator_status": "offline_only",
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "claim_boundary": "design only; no hardware run; no refreshed profile; no compensation improvement claim",
    }


def build_markdown(summary: dict[str, Any], trials: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-A S2 Profile Refresh Plan",
        "",
        f"Generated: {summary['generated_at']}",
        f"Surface: `{summary['surface']}`",
        f"Condition: `{summary['condition']}`",
        f"Repeats per command velocity: {summary['repeats_per_velocity']}",
        f"Physical profile refresh status: `{summary['physical_profile_refresh_status']}`",
        f"Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        "",
        "M24-A is a design-only profile refresh plan. No hardware has been run, no refreshed physical results exist, and the K1 gold profile is not overwritten.",
        "",
        "## Command Velocities",
    ]
    for velocity in summary["command_velocities_mps"]:
        lines.append(f"- {velocity:.2f} m/s")

    lines += [
        "",
        "## Profile Mismatch Metrics",
        "",
        f"- Threshold: {summary['profile_mismatch_metrics']['profile_mismatch_threshold_mps']} m/s",
        "- Old M19C mean actual velocity",
        "- New refresh mean actual velocity",
        "- Difference and absolute difference",
        "- Old and new uncertainty",
        "- Profile mismatch flag",
        "- Yaw drift comparison",
        "- No-motion rate",
        "- Repeat variability",
        "- Direct tracking near-optimal flag",
        "",
        "## Trial Plan",
        "",
        "| Trial ID | Group | Command | Repeat | Status |",
        "|----------|-------|---------|--------|--------|",
    ]
    for row in trials:
        lines.append(
            f"| {row['trial_id']} | {row['refresh_group_id']} | "
            f"{row['command_velocity_mps']} | {row['repeat_index']} | {row['physical_run_status']} |"
        )

    lines += [
        "",
        "## Boundaries",
        "",
        "- Direct command only; no compensated command is planned in M24-A/M24-B.",
        "- The objective is to compare current direct response against the old M19C S2 response profile.",
        "- M24-A cannot claim compensation improvement, physical validation, deployment readiness, or GO1/G1 validation.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
