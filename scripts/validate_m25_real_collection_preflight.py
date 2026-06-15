"""Validate M25-R real-robot collection preflight."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.m25_real_collection_preflight import evaluate_preflight


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate M25 real collection preflight.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_real_collection_preflight_template.yaml"))
    args = parser.parse_args(argv)
    try:
        result = evaluate_preflight(args.config)
    except Exception as exc:
        print(json.dumps({"ready": False, "blocked_reasons": [{"code": "preflight_load_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2), file=sys.stdout if result["ready"] else sys.stderr)
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
