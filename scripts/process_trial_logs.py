"""Process dummy raw trial logs into a schema-compliant environment profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.profile_builder import (
    build_environment_profile,
    load_raw_log,
    save_environment_profile,
)


DEFAULT_INPUT = Path("data/raw/dummy_forward_baseline.csv")
DEFAULT_OUTPUT = Path("data/processed/dummy_processed_environment_profile.json")
SCHEMA_PATH = Path("contracts/measurement_profile_schema.json")


def _validate_profile(profile: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(profile)


def process_trial_logs(input_path: str | Path, output_path: str | Path) -> dict:
    """Build and save a dummy processed environment profile."""

    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"input raw log does not exist: {input_file}")

    rows = load_raw_log(input_file)
    profile = build_environment_profile(rows)
    _validate_profile(profile)
    save_environment_profile(profile, output_path)
    return profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process raw logs into a dummy profile.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input raw CSV path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output profile JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        rows = load_raw_log(input_path)
    except FileNotFoundError:
        print(f"Input raw log does not exist: {input_path}")
        return 2

    profile = build_environment_profile(rows)
    _validate_profile(profile)
    save_environment_profile(profile, output_path)

    trial_ids = {row["trial_id"] for row in rows}
    vx_groups = sorted({row["vx_cmd"] for row in rows})
    print("Processed dummy raw log into environment profile.")
    print(f"Rows: {len(rows)}")
    print(f"Trials: {len(trial_ids)}")
    print(f"vx_cmd groups: {vx_groups}")
    print(f"Output: {output_path}")
    print("Dummy data only. Do not use for compensation or navigation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
