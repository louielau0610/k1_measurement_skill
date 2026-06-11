"""Validate artifacts against the Measurement Data Contract v1.0.

Supports:
- Validating a measurement CSV
- Validating a response statistics CSV
- Validating a session metadata JSON
- Validating a session directory

Usage:
  python scripts/validate_measurement_contract.py \\
    --measurements outputs/measurement_v1/booster_k1_measurements_contract_v1.csv

  python scripts/validate_measurement_contract.py \\
    --session-dir data/measurement_sessions/booster_k1/<id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.measurement_contract import (
    MEASUREMENT_CONTRACT_VERSION,
    validate_measurement_csv,
    validate_response_statistics_csv,
    validate_session_directory,
    validate_session_metadata,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate artifacts against the Measurement Data Contract v1.0.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_measurement_contract.py \\
    --measurements outputs/measurement_v1/booster_k1_measurements_contract_v1.csv

  python scripts/validate_measurement_contract.py \\
    --statistics outputs/real_k1_validation_m19/surface_response_statistics.csv

  python scripts/validate_measurement_contract.py \\
    --metadata data/measurement_sessions/booster_k1/<id>/session_metadata.json

  python scripts/validate_measurement_contract.py \\
    --session-dir data/measurement_sessions/booster_k1/<id>
        """,
    )
    parser.add_argument("--measurements", help="Path to a measurement CSV to validate")
    parser.add_argument("--statistics", help="Path to a response statistics CSV to validate")
    parser.add_argument("--metadata", help="Path to a session_metadata.json to validate")
    parser.add_argument("--session-dir", help="Path to a session directory to validate")
    parser.add_argument("--json", action="store_true", default=False, help="Output as JSON")

    args = parser.parse_args(argv)

    if not any([args.measurements, args.statistics, args.metadata, args.session_dir]):
        parser.print_help()
        return 1

    any_failure = False

    # Validate measurement CSV
    if args.measurements:
        path = Path(args.measurements)
        result = validate_measurement_csv(path)
        any_failure = any_failure or not result["valid"]
        _print_result("Measurement CSV", path, result, args.json)

    # Validate response statistics CSV
    if args.statistics:
        path = Path(args.statistics)
        result = validate_response_statistics_csv(path)
        any_failure = any_failure or not result["valid"]
        _print_result("Response Statistics CSV", path, result, args.json)

    # Validate session metadata JSON
    if args.metadata:
        path = Path(args.metadata)
        if not path.exists():
            result = {"valid": False, "errors": [f"file_not_found:{path}"]}
            any_failure = True
        else:
            metadata = json.loads(path.read_text(encoding="utf-8"))
            result = validate_session_metadata(metadata)
        any_failure = any_failure or not result["valid"]
        _print_result("Session Metadata", path, result, args.json)

    # Validate session directory
    if args.session_dir:
        path = Path(args.session_dir)
        result = validate_session_directory(path)
        any_failure = any_failure or not result["valid"]
        _print_result("Session Directory", path, result, args.json)

    return 1 if any_failure else 0


def _print_result(
    label: str,
    path: Path,
    result: dict,
    as_json: bool,
) -> None:
    if as_json:
        print(json.dumps({"label": label, "path": str(path), **result}, indent=2))
    else:
        status = "PASSED" if result["valid"] else "FAILED"
        print(f"\n{label}: {status}")
        print(f"  Path: {path}")
        print(f"  Contract version: {result.get('contract_version', '?')}")
        if "total_rows" in result:
            print(f"  Rows: {result['total_rows']} total, {result.get('valid_rows', 0)} valid, {result.get('invalid_rows', 0)} invalid")
        if result.get("errors"):
            print(f"  Errors ({len(result['errors'])}):")
            for e in result["errors"][:20]:
                print(f"    - {e}")
            if len(result["errors"]) > 20:
                print(f"    ... and {len(result['errors']) - 20} more")
        if result.get("warnings"):
            print(f"  Warnings ({len(result['warnings'])}):")
            for w in result["warnings"][:10]:
                print(f"    - {w}")
        if not result.get("errors") and not result.get("warnings"):
            print("  All checks passed.")


if __name__ == "__main__":
    raise SystemExit(main())
