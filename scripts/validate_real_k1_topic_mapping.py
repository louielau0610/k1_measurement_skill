"""Validate a real K1 topic mapping YAML file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.topic_mapping import load_topic_mapping, validate_topic_mapping


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate confirmed real K1 topic mapping.")
    parser.add_argument("--mapping", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = validate_topic_mapping(load_topic_mapping(args.mapping))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
