"""Run QC on a Booster K1 measurement session.

Checks session integrity, completeness, and validity.

Usage:
  python scripts/qc_booster_k1_measurement_session.py --session-dir data/measurement_sessions/booster_k1/<session_id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platforms.booster_k1.measurement_qc import BoosterK1MeasurementQC


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run QC on a Booster K1 measurement session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python scripts/qc_booster_k1_measurement_session.py \\
    --session-dir data/measurement_sessions/booster_k1/k1_measurement_20260611_120000_abc12345
        """,
    )
    parser.add_argument(
        "--session-dir",
        required=True,
        help="Path to the session directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output QC summary as JSON",
    )

    args = parser.parse_args(argv)
    session_dir = Path(args.session_dir)

    if not session_dir.exists():
        print(f"Error: session directory not found: {session_dir}", file=sys.stderr)
        return 1

    qc = BoosterK1MeasurementQC()
    try:
        summary = qc.run_qc(session_dir)
    except Exception as exc:
        print(f"QC failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "✅ PASSED" if summary["overall_pass"] else "❌ FAILED"
        print(f"\nQC Result: {status}")
        print(f"  Session: {summary['session_dir']}")
        print(f"  Platform: {summary['platform']}")
        print(f"  Checks: {summary['checks_passed']}/{summary['checks_total']} passed")
        if summary["errors"]:
            print(f"\nErrors ({len(summary['errors'])}):")
            for e in summary["errors"]:
                print(f"  ❌ {e}")
        if summary["warnings"]:
            print(f"\nWarnings ({len(summary['warnings'])}):")
            for w in summary["warnings"]:
                print(f"  ⚠️ {w}")
        if not summary["errors"] and not summary["warnings"]:
            print("  All checks passed.")
        print(f"\n  QC summary: {session_dir / 'qc_summary.json'}")
        print(f"  QC report:  {session_dir / 'qc_report.md'}")

    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
