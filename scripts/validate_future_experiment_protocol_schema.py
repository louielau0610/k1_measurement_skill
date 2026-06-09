"""Validate future experiment protocol schema and records for M20."""
from __future__ import annotations
import json
import sys
from pathlib import Path

DISALLOWED_FIELDS = {
    "remote_controller_state",
    "hand_controller_state",
    "unconfirmed_ros2_topic",
}

UNSAFE_READINESS_FLAGS = {
    "navigation_safety_improvement_claim_ready": False,
    "safe_command_adapter_ready": True,
    "compensation_ready": True,
    "publication_ready": True,
    "fabricated_results": True,
}

def load_json(path: str) -> dict:
    """Load JSON file, handling UTF-8 BOM if present."""
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)
    

def validate_schema(schema: dict) -> list[str]:
    errors = []
    if not isinstance(schema, dict):
        errors.append("Schema must be a JSON object")
        return errors
    if schema.get("type") != "object":
        errors.append("Schema root must have type=object")
    if "properties" not in schema:
        errors.append("Schema must have properties")
    return errors

def check_disallowed_recursive(data, path="", errors=None):
    if errors is None:
        errors = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if key in DISALLOWED_FIELDS:
                errors.append(f"DISALLOWED FIELD '{key}' at {current_path}")
            check_disallowed_recursive(value, current_path, errors)
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            check_disallowed_recursive(item, f"{path}[{idx}]", errors)
    return errors

def check_readiness_flags(record: dict, errors: list[str] | None = None) -> list[str]:
    if errors is None:
        errors = []
    readiness = record.get("downstream_readiness", {})
    for flag, unsafe_value in UNSAFE_READINESS_FLAGS.items():
        if readiness.get(flag) == unsafe_value:
            errors.append(f"UNSAFE READINESS FLAG '{flag}' is set to {unsafe_value}")
    if isinstance(record.get("trial_records"), list):
        for tr in record["trial_records"]:
            for flag, unsafe_value in UNSAFE_READINESS_FLAGS.items():
                if tr.get(flag) == unsafe_value:
                    errors.append(f"UNSAFE READINESS FLAG '{flag}' in trial_record")
    return errors

def validate_record(record: dict) -> list[str]:
    errors = []
    errors.extend(check_disallowed_recursive(record))
    errors.extend(check_readiness_flags(record))
    if not record.get("experiment_id"):
        errors.append("Missing required field: experiment_id")
    if not record.get("trial_records"):
        errors.append("Missing required field: trial_records")
    return errors

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, help="Path to schema JSON")
    parser.add_argument("--record", default=None, help="Path to record JSON to validate")
    args = parser.parse_args()

    schema = load_json(args.schema)
    schema_errors = validate_schema(schema)
    if schema_errors:
        print("SCHEMA ERRORS:")
        for e in schema_errors:
            print(f"  - {e}")
        return 1

    print(f"OK: Schema loaded ({args.schema})")

    if args.record:
        record = load_json(args.record)
        record_errors = validate_record(record)
        if record_errors:
            print(f"RECORD ERRORS ({args.record}):")
            for e in record_errors:
                print(f"  - {e}")
            return 1
        print(f"OK: Record valid ({args.record})")

    return 0

if __name__ == "__main__":
    sys.exit(main())
