"""Convert legacy K1 measurements to Measurement Data Contract v1.0 format.

Reads legacy M19C extracted measurements and produces contract-compliant CSV.

Usage:
  python scripts/convert_measurements_to_contract.py \\
    --input data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv \\
    --output outputs/measurement_v1/booster_k1_measurements_contract_v1.csv \\
    --platform booster_k1 \\
    --robot-model Booster_K1 \\
    --dataset-id m19c_booster_k1_gold_v1
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.measurement_contract import (
    TRIAL_CONTRACT_FIELDS,
    MEASUREMENT_CONTRACT_VERSION,
    validate_measurement_csv,
)
from calibration_core.measurement_contract_mapping import map_legacy_trial_row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert legacy K1 measurements to Measurement Data Contract v1.0.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python scripts/convert_measurements_to_contract.py \\
    --input data/m19_repeated_validation_inputs/m19c_extracted_measurements.csv \\
    --output outputs/measurement_v1/booster_k1_measurements_contract_v1.csv \\
    --platform booster_k1 \\
    --robot-model Booster_K1 \\
    --dataset-id m19c_booster_k1_gold_v1
        """,
    )
    parser.add_argument("--input", required=True, help="Path to legacy measurement CSV")
    parser.add_argument("--output", required=True, help="Path for contract-compliant output CSV")
    parser.add_argument("--platform", default="booster_k1", help="Platform identifier")
    parser.add_argument("--robot-model", default="Booster K1", help="Robot model name")
    parser.add_argument("--robot-id", default="Booster_K1", help="Robot ID")
    parser.add_argument("--dataset-id", default="m19c_booster_k1_gold_v1", help="Dataset identifier")
    parser.add_argument("--session-id", default="m19c_full_72_measurement_run_20260611", help="Session identifier")
    parser.add_argument("--environment-id", default="m19c_lab", help="Environment identifier")
    parser.add_argument("--surface-type", default="", help="Surface type (auto-detected if empty)")
    parser.add_argument("--state-source", default="/odometer_state", help="State source topic")
    parser.add_argument("--command-source", default="booster_sdk_kPrepare_kWalking_Move", help="Command source")
    parser.add_argument("--validation-output", default="", help="Path for validation summary JSON")

    args = parser.parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    # Read legacy CSV
    with input_path.open(newline="", encoding="utf-8-sig") as f:
        legacy_rows = list(csv.DictReader(f))

    if not legacy_rows:
        print("Error: input CSV is empty", file=sys.stderr)
        return 1

    print(f"Read {len(legacy_rows)} legacy rows from {input_path}")

    # Detect surface type from trial_id if not provided
    def detect_surface_type(trial_id: str) -> str:
        for prefix, stype in [
            ("S1_lab_hard_floor", "lab_hard_floor"),
            ("S2_marble_floor", "marble_floor"),
            ("S3_artificial_turf", "artificial_turf"),
        ]:
            if prefix in trial_id:
                return stype
        return "unknown"

    # Convert each row
    contract_rows: list[dict[str, object]] = []
    for legacy in legacy_rows:
        trial_id = legacy.get("trial_id", "")
        surface_type = args.surface_type or detect_surface_type(trial_id)

        row = map_legacy_trial_row(
            legacy,
            dataset_id=args.dataset_id,
            platform=args.platform,
            robot_model=args.robot_model,
            robot_id=args.robot_id,
            session_id=args.session_id,
            environment_id=args.environment_id,
            surface_type=surface_type,
            state_source=args.state_source,
            command_source=args.command_source,
            raw_log_path="",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        contract_rows.append(row)

    # Write contract CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRIAL_CONTRACT_FIELDS)
        writer.writeheader()
        for row in contract_rows:
            writer.writerow(row)

    print(f"Wrote {len(contract_rows)} contract rows to {output_path}")

    # Validate output
    validation = validate_measurement_csv(output_path)
    print(f"Validation: {'PASSED' if validation['valid'] else 'FAILED'}")
    print(f"  Valid rows: {validation['valid_rows']}/{validation['total_rows']}")
    if validation["errors"]:
        print(f"  Errors: {len(validation['errors'])}")
        for e in validation["errors"][:10]:
            print(f"    - {e}")

    # Write validation summary
    val_output = Path(args.validation_output) if args.validation_output else output_path.with_suffix(".validation.json")
    val_output.parent.mkdir(parents=True, exist_ok=True)
    val_output.write_text(json.dumps({
        "conversion_time": datetime.now(timezone.utc).isoformat(),
        "contract_version": MEASUREMENT_CONTRACT_VERSION,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "total_rows": len(contract_rows),
        "validation": validation,
    }, indent=2), encoding="utf-8")
    print(f"Validation summary: {val_output}")

    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
