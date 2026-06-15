"""Validate M25-R operator safe-speed confirmation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.m25_real_collection_preflight import validate_safe_speed_confirmation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate M25 safe-speed operator confirmation.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_k1_safe_speed_operator_confirmation_template.yaml"))
    args = parser.parse_args(argv)
    try:
        result = validate_safe_speed_confirmation(args.config)
    except Exception as exc:
        print(json.dumps({"valid": False, "errors": [{"code": "confirmation_load_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2), file=sys.stdout if result["valid"] else sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
