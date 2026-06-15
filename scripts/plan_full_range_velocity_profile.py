"""Generate M25 full-range command-to-actual velocity profile plans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import M25ValidationError, load_config, plan_phase, write_plan_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate M25 exploration or formal velocity profiling plan.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--phase", choices=["exploration", "formal"], required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/full_range_velocity_profile"))
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        plan = plan_phase(config, args.phase)
        name = "m25_exploration_plan" if args.phase == "exploration" else "m25_formal_plan"
        json_path, md_path = write_plan_artifacts(plan, args.output_dir, name)
    except (OSError, M25ValidationError, ValueError) as exc:
        print(json.dumps({"status": "failed", "errors": [{"code": "planning_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps({"status": plan["status"], "executable": plan["executable"], "json": str(json_path), "markdown": str(md_path)}, indent=2))
    return 0 if plan["executable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
