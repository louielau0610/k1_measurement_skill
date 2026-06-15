"""Validate M25 full-range velocity profiling configuration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import M25ValidationError, load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate M25 full-range velocity profiling config.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--require-safe-max", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        errors = config.validate(require_safe_max=args.require_safe_max)
    except (OSError, M25ValidationError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [{"code": "config_load_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    result = {"valid": not errors, "errors": errors, "config": config.as_dict()}
    stream = sys.stdout if not errors else sys.stderr
    print(json.dumps(result, indent=2), file=stream)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
