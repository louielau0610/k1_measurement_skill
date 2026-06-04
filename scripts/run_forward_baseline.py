"""CLI for dry-run forward baseline trial planning."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.command_runner import K1CommandRunner
from k1_measurement.trial_manager import K1TrialManager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dry-run K1 forward baseline plan.")
    parser.add_argument("--config", default="config/experiment_forward_v0.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-only", action="store_true")
    return parser.parse_args()


def print_summary(trial_plan: list[dict], config: dict) -> None:
    vx_groups = sorted({trial["vx_cmd_mps"] for trial in trial_plan})
    repeat_counts = Counter(trial["vx_cmd_mps"] for trial in trial_plan)
    first = trial_plan[0]
    environment = config["environment"]
    print("DRY RUN ONLY. No robot command is sent.")
    print(f"Trials: {len(trial_plan)}")
    print(f"Velocity groups: {vx_groups}")
    print(f"Repeats per speed: {dict(sorted(repeat_counts.items()))}")
    print(f"Baseline duration: {first['baseline_duration_sec']} sec")
    print(f"Command duration: {first['command_duration_sec']} sec")
    print(f"Stop duration: {first['stop_duration_sec']} sec")
    print(
        "Environment: "
        f"{environment['floor_type']}/{environment['condition']}/{environment['slope']}"
    )


def main() -> int:
    args = parse_args()
    manager = K1TrialManager(args.config)
    config = manager.load_config()
    trial_plan = manager.generate_trial_plan()
    manager.validate_trial_plan(trial_plan)
    print_summary(trial_plan, config)

    if args.print_only:
        manager.print_trial_plan(trial_plan)
        return 0

    if not args.dry_run:
        print("Real execution is disabled until K1 command interface is verified.")
        return 2

    runner = K1CommandRunner(args.config, dry_run=True)
    for trial in trial_plan:
        runner.run_single_trial(trial)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
