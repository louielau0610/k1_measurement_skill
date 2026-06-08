"""Create a real K1 field-test session directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.field_session import create_field_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an M8 real K1 field session.")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = create_field_session(args.session_id, args.output_root)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
