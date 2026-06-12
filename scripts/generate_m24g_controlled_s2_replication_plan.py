"""Generate M24-G controlled S2 replication design artifacts.

This is a design-only generator. It does not execute hardware, create physical
results, adopt a profile, or modify the K1 gold profile.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("outputs/compensation_experiments")
SURFACE = "S2_marble_floor"
CONDITION = "direct_refresh_controlled"
CORE_VELOCITIES = [0.40, 0.45, 0.50, 0.55]
EXTENSION_VELOCITIES = [0.35, 0.60]
CORE_REPEATS = 5
DEFAULT_EXTENSION_REPEATS = 3

PLAN_FIELDS = [
    "trial_id",
    "replication_group_id",
    "surface",
    "condition",
    "command_velocity_mps",
    "desired_velocity_mps",
    "repeat_index",
    "is_extension_velocity",
    "physical_run_status",
    "compensated_command",
    "metadata_required",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate M24-G controlled S2 replication design artifacts.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--include-extension-velocities", action="store_true")
    parser.add_argument("--extension-repeats", type=int, default=DEFAULT_EXTENSION_REPEATS, choices=[3, 5])
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    trials = build_plan(include_extension=args.include_extension_velocities, extension_repeats=args.extension_repeats)

    csv_path = args.output_dir / "m24g_controlled_s2_replication_plan.csv"
    json_path = args.output_dir / "m24g_controlled_s2_replication_plan.json"
    md_path = args.output_dir / "m24g_controlled_s2_replication_plan.md"
    manifest_json_path = args.output_dir / "m24g_controlled_replication_design_manifest.json"
    manifest_md_path = args.output_dir / "m24g_controlled_replication_design_manifest.md"

    write_csv(csv_path, trials)
    summary = build_summary(trials, generated_at, csv_path, args.include_extension_velocities, args.extension_repeats)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path.write_text(build_plan_markdown(summary, trials), encoding="utf-8")

    manifest = build_manifest(summary, manifest_json_path, manifest_md_path)
    manifest_json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest_md_path.write_text(build_manifest_markdown(manifest), encoding="utf-8")

    print("M24-G controlled S2 replication plan generated")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Manifest JSON: {manifest_json_path}")
    print(f"Manifest Markdown: {manifest_md_path}")
    print("NO HARDWARE EXECUTION - design only")
    return 0


def build_plan(*, include_extension: bool, extension_repeats: int) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    trials.extend(build_trials(CORE_VELOCITIES, CORE_REPEATS, is_extension=False))
    if include_extension:
        trials.extend(build_trials(EXTENSION_VELOCITIES, extension_repeats, is_extension=True))
    return trials


def build_trials(velocities: list[float], repeats: int, *, is_extension: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    group_prefix = "M24G_EXT" if is_extension else "M24G_CORE"
    for velocity in sorted(velocities):
        group_id = f"{group_prefix}_{SURFACE}_V{int(round(velocity * 100)):03d}"
        for repeat_index in range(1, repeats + 1):
            rows.append(
                {
                    "trial_id": f"{group_id}_R{repeat_index}",
                    "replication_group_id": group_id,
                    "surface": SURFACE,
                    "condition": CONDITION,
                    "command_velocity_mps": f"{velocity:.2f}",
                    "desired_velocity_mps": f"{velocity:.2f}",
                    "repeat_index": repeat_index,
                    "is_extension_velocity": is_extension,
                    "physical_run_status": "planned_not_run",
                    "compensated_command": "false",
                    "metadata_required": "true",
                    "notes": "direct controlled replication only; no compensated commands",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(
    trials: list[dict[str, Any]],
    generated_at: str,
    csv_path: Path,
    include_extension: bool,
    extension_repeats: int,
) -> dict[str, Any]:
    core_trials = [row for row in trials if row["is_extension_velocity"] is False]
    extension_trials = [row for row in trials if row["is_extension_velocity"] is True]
    return {
        "milestone": "M24-G",
        "generated_at": generated_at,
        "status": "controlled_s2_replication_design_only",
        "platform": "booster_k1",
        "planned_surface": SURFACE,
        "planned_condition": CONDITION,
        "core_velocities_mps": CORE_VELOCITIES,
        "extension_velocities_mps": EXTENSION_VELOCITIES,
        "extension_velocities_included": include_extension,
        "core_repeats_per_velocity": CORE_REPEATS,
        "extension_repeats_per_velocity": extension_repeats,
        "planned_core_trial_count": len(core_trials),
        "planned_extension_trial_count": len(extension_trials),
        "planned_total_trial_count": len(trials),
        "trial_plan_csv": str(csv_path),
        "compensated_command_rows": 0,
        "physical_run_status": "not_run",
        "new_physical_data": False,
        "profile_adoption_status": "not_adopted",
        "m24f_candidate_profile_adopted": False,
        "gold_profile_overwritten": False,
        "revised_compensator_status": "offline_only",
        "compensation_validation_status": "blocked_pending_controlled_replication",
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "claim_boundary": "design only; no hardware run; no physical results; no profile adoption; no compensation improvement claim",
    }


def build_manifest(summary: dict[str, Any], manifest_json_path: Path, manifest_md_path: Path) -> dict[str, Any]:
    return {
        "milestone": "M24-G",
        "manifest_json": str(manifest_json_path),
        "manifest_markdown": str(manifest_md_path),
        "planned_surface": summary["planned_surface"],
        "planned_condition": summary["planned_condition"],
        "planned_velocities_mps": summary["core_velocities_mps"],
        "optional_extension_velocities_mps": summary["extension_velocities_mps"],
        "planned_repeats_per_velocity": summary["core_repeats_per_velocity"],
        "planned_core_trial_count": summary["planned_core_trial_count"],
        "physical_run_status": "not_run",
        "profile_adoption_status": "not_adopted",
        "gold_profile_overwritten": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
    }


def build_plan_markdown(summary: dict[str, Any], trials: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-G Controlled S2 Replication Plan",
        "",
        f"Generated: {summary['generated_at']}",
        f"Surface: `{summary['planned_surface']}`",
        f"Condition: `{summary['planned_condition']}`",
        f"Core repeats per velocity: {summary['core_repeats_per_velocity']}",
        f"Core trial count: {summary['planned_core_trial_count']}",
        f"Physical run status: `{summary['physical_run_status']}`",
        f"Profile adoption status: `{summary['profile_adoption_status']}`",
        "",
        "This plan contains direct controlled replication trials only. It contains no compensated command rows.",
        "",
        "## Core Velocities",
    ]
    lines.extend(f"- {velocity:.2f} m/s" for velocity in summary["core_velocities_mps"])
    lines += [
        "",
        "## Optional Extension Velocities",
    ]
    lines.extend(f"- {velocity:.2f} m/s" for velocity in summary["extension_velocities_mps"])
    lines += [
        "",
        "## Trial Plan",
        "",
        "| Trial ID | Command | Repeat | Extension | Status |",
        "|----------|---------|--------|-----------|--------|",
    ]
    for row in trials:
        lines.append(
            f"| {row['trial_id']} | {row['command_velocity_mps']} | {row['repeat_index']} | "
            f"{str(row['is_extension_velocity']).lower()} | {row['physical_run_status']} |"
        )
    lines += [
        "",
        "## Boundaries",
        "",
        "- Design only; no hardware has been run.",
        "- No physical results are created by this artifact.",
        "- No profile is adopted or overwritten.",
        "- No compensation improvement or deployment readiness is claimed.",
    ]
    return "\n".join(lines) + "\n"


def build_manifest_markdown(manifest: dict[str, Any]) -> str:
    return (
        "# M24-G Controlled Replication Design Manifest\n\n"
        f"- Planned surface: `{manifest['planned_surface']}`\n"
        f"- Planned condition: `{manifest['planned_condition']}`\n"
        f"- Planned velocities: `{manifest['planned_velocities_mps']}`\n"
        f"- Planned repeats per velocity: {manifest['planned_repeats_per_velocity']}\n"
        f"- Planned core trial count: {manifest['planned_core_trial_count']}\n"
        f"- Physical run status: `{manifest['physical_run_status']}`\n"
        f"- Profile adoption status: `{manifest['profile_adoption_status']}`\n"
        f"- Deployment ready: `{str(manifest['deployment_ready']).lower()}`\n"
        f"- GO1/G1 blocked: `{str(manifest['go1_g1_blocked']).lower()}`\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
