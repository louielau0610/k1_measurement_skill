"""Evaluate whether M25 exploration results are ready for formal collection."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import load_config
from k1_measurement.m25_real_collection_preflight import evaluate_exploration_gate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate M25 exploration-to-formal gate.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = evaluate_exploration_gate(args.results, config.valid_speed_domain)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"ready": False, "decisions": ["gate_evaluation_failed"], "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2), file=sys.stdout if result["ready"] else sys.stderr)
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
