"""Validate collected trial rows against the M25 velocity contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import M25ValidationError, load_config, validate_collected_session


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate collected M25 trial rows.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--session", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = validate_collected_session(args.session, config.valid_speed_domain)
    except (OSError, M25ValidationError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [{"code": "session_validation_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    stream = sys.stdout if result["valid"] else sys.stderr
    print(json.dumps(result, indent=2), file=stream)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
