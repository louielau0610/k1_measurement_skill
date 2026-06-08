"""Start read-only real K1 ROS2 bag logging."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.field_logging import start_field_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start M8 read-only field logger.")
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--duration-sec", type=float)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = start_field_logger(args.session_dir, args.duration_sec)
    except ValueError as exc:
        print(str(exc))
        return 2
    except FileNotFoundError as exc:
        print(f"ROS2 logging command unavailable: {exc}")
        return 3
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
