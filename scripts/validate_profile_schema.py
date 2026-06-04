"""Validate a processed environment profile against the repository schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "contracts" / "measurement_profile_schema.json"
DEFAULT_PROFILE_PATH = REPO_ROOT / "examples" / "dummy_processed_environment_profile.json"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_profile(profile_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    schema = load_json(schema_path)
    profile = load_json(profile_path)
    validator = Draft202012Validator(schema)
    validator.validate(profile)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate processed_environment_profile.json against the M1 schema."
    )
    parser.add_argument(
        "profile",
        nargs="?",
        default=str(DEFAULT_PROFILE_PATH),
        help="Profile JSON path. Defaults to examples/dummy_processed_environment_profile.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = (Path.cwd() / profile_path).resolve()

    try:
        validate_profile(profile_path)
    except FileNotFoundError as exc:
        print(f"Profile validation failed: file not found: {exc.filename}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Profile validation failed: invalid JSON: {exc}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        print(f"Profile validation failed at {path}: {exc.message}", file=sys.stderr)
        return 1

    print(f"Profile validation passed: {profile_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
