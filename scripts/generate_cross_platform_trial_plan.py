"""Generate a deterministic cross-platform calibration trial plan."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.platform_registry import get_platform
from calibration_core.profile_loader import load_k1_gold_profile
from calibration_core.trial_scheduler import TrialScheduler


def parse_csv_text(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_speeds(value: str) -> list[float]:
    return [float(part) for part in parse_csv_text(value)]


def default_surfaces_and_speeds(platform_id: str) -> tuple[list[str], list[float]]:
    if platform_id == "booster_k1":
        profile = load_k1_gold_profile()
        return list(profile["tested_surfaces"]), [float(speed) for speed in profile["speed_list"]]
    return ["flat_lab_surface"], [0.1, 0.2, 0.3]


def build_plan(
    platform_id: str,
    surfaces: list[str] | None,
    speeds: list[float] | None,
    repeats: int,
) -> list[dict[str, object]]:
    entry = get_platform(platform_id)
    selected_surfaces, selected_speeds = default_surfaces_and_speeds(platform_id)
    selected_surfaces = surfaces or selected_surfaces
    selected_speeds = speeds or selected_speeds
    prefix = "K1" if platform_id == "booster_k1" else platform_id.upper()
    trials = TrialScheduler().build_trials(
        selected_surfaces,
        selected_speeds,
        repeats,
        platform=platform_id,
        prefix=prefix,
    )
    return [
        {
            "trial_id": trial.trial_id,
            "platform_id": trial.platform,
            "robot_model": entry.robot_model,
            "surface_id": trial.surface_id,
            "command_velocity": trial.command_velocity,
            "repeat_index": trial.repeat_index,
            "block_index": trial.block_index,
            "hardware_validated_reference": entry.hardware_validated_reference,
            "plan_only": True,
        }
        for trial in trials
    ]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "trial_id",
        "platform_id",
        "robot_model",
        "surface_id",
        "command_velocity",
        "repeat_index",
        "block_index",
        "hardware_validated_reference",
        "plan_only",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", default="booster_k1")
    parser.add_argument("--surfaces", default=None, help="Comma-separated surface IDs.")
    parser.add_argument("--speeds", default=None, help="Comma-separated command velocities in m/s.")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    rows = build_plan(
        args.platform,
        parse_csv_text(args.surfaces) if args.surfaces else None,
        parse_speeds(args.speeds) if args.speeds else None,
        args.repeats,
    )
    if args.output:
        write_csv(args.output, rows)
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"platform_id: {args.platform}")
        print(f"trial_count: {len(rows)}")
        if args.output:
            print(f"output: {args.output}")
        for row in rows[:10]:
            print(f"{row['trial_id']},{row['surface_id']},{row['command_velocity']},{row['repeat_index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
