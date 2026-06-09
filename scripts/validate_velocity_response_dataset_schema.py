"""Validate velocity response schema metadata and example records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.research_dataset_schema import (
    get_disallowed_fields,
    load_velocity_response_schema,
    validate_velocity_response_record,
    validate_velocity_response_schema,
)


DEFAULT_SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
DEFAULT_RECORD_PATH = REPO_ROOT / "examples" / "velocity_response" / "minimal_valid_record.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (Path.cwd() / candidate).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the M13 velocity response dataset schema and a record example."
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Schema JSON path. Defaults to configs/velocity_response_dataset_schema_v1.json.",
    )
    parser.add_argument(
        "--record",
        help="Optional record JSON path. Defaults to examples/velocity_response/minimal_valid_record.json.",
    )
    parser.add_argument(
        "--dataset",
        help="Compatibility alias for --record.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_path = resolve_path(args.schema)
    record_arg = args.record or args.dataset or str(DEFAULT_RECORD_PATH)
    record_path = resolve_path(record_arg)

    summary: dict[str, Any] = {
        "schema": str(schema_path),
        "record": str(record_path),
        "valid_schema": False,
        "valid_record": False,
        "battery_state_required": False,
        "disallowed_fields": [],
        "errors": [],
    }

    try:
        schema = load_velocity_response_schema(schema_path)
        schema_errors = validate_velocity_response_schema(schema)
        summary["disallowed_fields"] = sorted(get_disallowed_fields(schema))

        if schema_errors:
            summary["errors"].extend(schema_errors)
        else:
            summary["valid_schema"] = True

        record = load_json(record_path)
        if not isinstance(record, dict):
            summary["errors"].append("Velocity response record must be a JSON object.")
        else:
            record_errors = validate_velocity_response_record(record, schema)
            if record_errors:
                summary["errors"].extend(record_errors)
            else:
                summary["valid_record"] = True
    except FileNotFoundError as exc:
        summary["errors"].append(f"File not found: {exc.filename}")
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        summary["errors"].append(f"Invalid JSON: {exc}")
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        return 2
    except ValueError as exc:
        summary["errors"].append(str(exc))
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    output = json.dumps(summary, indent=2, ensure_ascii=False)
    if summary["valid_schema"] and summary["valid_record"]:
        print(output)
        return 0

    print(output, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
