"""Normalize real K1 exported logs into measurement CSV format."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.real_log_normalizer import normalize_exported_csv_logs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize M8 real K1 field logs.")
    parser.add_argument("--session-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = normalize_exported_csv_logs(args.session_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
