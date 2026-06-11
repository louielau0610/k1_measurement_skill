"""Extract measurements from a Booster K1 measurement session.

Reads session metadata, state logs, and produces extracted measurements
with velocity and yaw drift statistics.

Usage:
  python scripts/extract_booster_k1_measurements.py --session-dir data/measurement_sessions/booster_k1/<session_id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platforms.booster_k1.measurement_extractor import BoosterK1MeasurementExtractor
from platforms.booster_k1.session import BoosterK1Session


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract measurements from a Booster K1 measurement session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python scripts/extract_booster_k1_measurements.py \\
    --session-dir data/measurement_sessions/booster_k1/k1_measurement_20260611_120000_abc12345
        """,
    )
    parser.add_argument(
        "--session-dir",
        required=True,
        help="Path to the session directory",
    )

    args = parser.parse_args(argv)
    session_dir = Path(args.session_dir)

    if not session_dir.exists():
        print(f"Error: session directory not found: {session_dir}", file=sys.stderr)
        return 1

    # Load session metadata
    try:
        metadata = BoosterK1Session.load_metadata(session_dir)
        print(f"Session: {metadata['session_id']}")
        print(f"Platform: {metadata['platform']}")
        print(f"Surface: {metadata.get('surface', 'unknown')}")
        print(f"Speeds: {metadata.get('speeds', [])}")
        print(f"Repeats: {metadata.get('repeats', 0)}")
    except FileNotFoundError:
        print("Warning: session_metadata.json not found. Continuing without metadata.")

    # Extract measurements
    state_log_dir = session_dir / "state_logs"
    if not state_log_dir.exists():
        print(f"Error: state_logs directory not found: {state_log_dir}", file=sys.stderr)
        return 1

    extractor = BoosterK1MeasurementExtractor()
    try:
        summary = extractor.extract_batch(state_log_dir, session_dir)
        print(f"\nExtraction complete:")
        print(f"  Total logs: {summary['total_logs']}")
        print(f"  Successfully extracted: {summary['successfully_extracted']}")
        print(f"  Extraction errors: {summary['extraction_errors']}")
        print(f"  Extracted measurements: {summary['extracted_measurements_path']}")
        print(f"  Summary: {session_dir / 'extraction_summary.json'}")
        print(f"  Report: {session_dir / 'extraction_report.md'}")
    except Exception as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
