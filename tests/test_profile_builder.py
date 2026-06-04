from __future__ import annotations

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from k1_measurement.profile_builder import (
    DUMMY_WARNING,
    build_environment_profile,
    load_raw_log,
    save_environment_profile,
)
from scripts.generate_dummy_raw_log import FIELDNAMES, generate_dummy_raw_log


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "contracts" / "measurement_profile_schema.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_dummy_raw_log_generation_creates_csv_with_required_fields(tmp_path: Path) -> None:
    output = tmp_path / "dummy_forward_baseline.csv"

    result = generate_dummy_raw_log(output)

    assert result == output
    assert output.exists()
    rows = _read_csv(output)
    assert rows
    assert set(FIELDNAMES).issubset(rows[0].keys())


def test_dummy_raw_log_contains_expected_velocity_groups_and_trials(tmp_path: Path) -> None:
    output = tmp_path / "dummy_forward_baseline.csv"
    generate_dummy_raw_log(output)
    rows = _read_csv(output)

    vx_groups = sorted({float(row["vx_cmd"]) for row in rows})
    assert vx_groups == [0.1, 0.2, 0.3, 0.4]

    for vx_cmd in vx_groups:
        trial_ids = {row["trial_id"] for row in rows if float(row["vx_cmd"]) == vx_cmd}
        assert len(trial_ids) == 5


def test_profile_builder_builds_schema_valid_dummy_profile(tmp_path: Path) -> None:
    raw_path = tmp_path / "dummy_forward_baseline.csv"
    profile_path = tmp_path / "dummy_processed_environment_profile.json"
    generate_dummy_raw_log(raw_path)

    rows = load_raw_log(raw_path)
    profile = build_environment_profile(rows)
    save_environment_profile(profile, profile_path)

    assert profile_path.exists()
    for key in [
        "schema_version",
        "metadata",
        "environment",
        "valid_speed_range",
        "velocity_profile",
        "quality",
        "downstream_usage",
    ]:
        assert key in profile

    Draft202012Validator(_load_schema()).validate(profile)
    assert profile["downstream_usage"]["recommended_for_compensation"] is False
    assert profile["downstream_usage"]["extrapolation_allowed"] is False
    assert profile["quality"]["confidence"] == "low"
    assert DUMMY_WARNING in profile["quality"]["warnings"]
    assert len(profile["velocity_profile"]) == 4
    assert {point["n_trials"] for point in profile["velocity_profile"]} == {5}


def test_no_compensation_function_is_introduced() -> None:
    import k1_measurement.profile_builder as profile_builder

    assert not hasattr(profile_builder, "compensate_velocity")
