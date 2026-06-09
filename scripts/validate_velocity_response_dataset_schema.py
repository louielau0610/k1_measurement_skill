"""Validate the velocity response dataset schema and optional dataset files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
PROHIBITED_KEYS = {"remote_controller_state"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def iter_schema_keys(node: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(node, dict):
        keys.extend(str(key) for key in node.keys())
        for value in node.values():
            keys.extend(iter_schema_keys(value))
    elif isinstance(node, list):
        for item in node:
            keys.extend(iter_schema_keys(item))
    return keys


def find_required_paths(node: Any, path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    paths: list[tuple[str, ...]] = []
    if isinstance(node, dict):
        required = node.get("required")
        if isinstance(required, list) and "battery_state" in required:
            paths.append(path + ("required",))
        for key, value in node.items():
            paths.extend(find_required_paths(value, path + (str(key),)))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            paths.extend(find_required_paths(item, path + (str(index),)))
    return paths


def validate_schema_file(schema_path: Path) -> dict[str, Any]:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)

    all_keys = set(iter_schema_keys(schema))
    prohibited = sorted(PROHIBITED_KEYS.intersection(all_keys))
    if prohibited:
        raise ValueError(
            "Velocity response schema contains prohibited field(s): "
            + ", ".join(prohibited)
        )

    required_battery_paths = find_required_paths(schema)
    if required_battery_paths:
        rendered = ["/".join(path) for path in required_battery_paths]
        raise ValueError(
            "battery_state must remain optional; found required reference at "
            + ", ".join(rendered)
        )

    return {
        "schema": str(schema_path),
        "valid_schema": True,
        "battery_state_required": False,
        "prohibited_fields_present": prohibited,
    }


def validate_dataset_file(dataset_path: Path, schema_path: Path) -> dict[str, Any]:
    schema = load_json(schema_path)
    dataset = load_json(dataset_path)
    Draft202012Validator(schema).validate(dataset)
    return {
        "dataset": str(dataset_path),
        "valid_dataset": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the M13 velocity response dataset schema and, optionally, "
            "a dataset JSON file."
        )
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Schema JSON path. Defaults to configs/velocity_response_dataset_schema_v1.json.",
    )
    parser.add_argument(
        "--dataset",
        help="Optional dataset JSON path to validate against the schema.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = (Path.cwd() / schema_path).resolve()

    try:
        summary = validate_schema_file(schema_path)
        if args.dataset:
            dataset_path = Path(args.dataset)
            if not dataset_path.is_absolute():
                dataset_path = (Path.cwd() / dataset_path).resolve()
            summary.update(validate_dataset_file(dataset_path, schema_path))
    except FileNotFoundError as exc:
        print(f"Velocity response schema validation failed: file not found: {exc.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Velocity response schema validation failed: invalid JSON: {exc}", file=sys.stderr)
        return 2
    except SchemaError as exc:
        print(f"Velocity response schema validation failed: invalid schema: {exc.message}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        print(f"Velocity response dataset validation failed at {path}: {exc.message}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Velocity response schema validation failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
