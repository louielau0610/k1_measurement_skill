from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from k1_measurement.research_dataset_schema import (
    assert_velocity_response_record_valid,
    get_disallowed_fields,
    load_velocity_response_schema,
    validate_velocity_response_record,
    validate_velocity_response_schema,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
VALID_RECORD_PATH = REPO_ROOT / "examples" / "velocity_response" / "minimal_valid_record.json"
INVALID_RECORD_PATH = (
    REPO_ROOT / "examples" / "velocity_response" / "invalid_disallowed_field_record.json"
)
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate_velocity_response_dataset_schema.py"


@pytest.fixture()
def schema() -> dict:
    return load_velocity_response_schema(SCHEMA_PATH)


@pytest.fixture()
def valid_record() -> dict:
    return json.loads(VALID_RECORD_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def minimal_dataset() -> dict:
    return {
        "schema_version": "1.0.0",
        "dataset_id": "m13_schema_test_dataset",
        "created_at": "2026-06-09T00:00:00Z",
        "research_problem": {
            "response_equation": "v_actual = f(v_cmd, environment, robot_state)",
            "modeling_goal": "velocity_response_characterization",
            "claim_level": "planned_schema_only",
        },
        "robot": {
            "platform": "Booster K1",
            "identifier": "TBD",
            "firmware_version": "TBD",
            "control_mode": "TBD",
        },
        "environment": {
            "floor_type": "unknown",
            "condition": "unknown",
            "slope": "unknown",
            "test_distance_m": 1.0,
            "ground_truth_method": "unknown",
            "notes": "Schema validation fixture only; not an experimental result.",
        },
        "acquisition": {
            "session_id": "schema_validation_only",
            "raw_log_reference": "TBD",
            "normalized_log_reference": "TBD",
            "topic_mapping_reference": "TBD",
            "operator_confirmation": False,
        },
        "command_grid": {
            "vx_cmd_mps_values": [0.1],
            "vy_cmd_mps": 0,
            "wz_cmd_rps": 0,
            "trials_per_command": 1,
        },
        "trials": [
            {
                "trial_id": "schema_trial_001",
                "session_id": "schema_validation_only",
                "vx_cmd_mps": 0.1,
                "start_time": "2026-06-09T00:00:00Z",
                "end_time": "2026-06-09T00:00:01Z",
                "duration_sec": 1.0,
                "distance_m": 0.0,
                "vx_actual_mean_mps": 0.0,
                "vx_actual_std_mps": 0.0,
                "sample_count": 1,
                "robot_state": {
                    "mode": "TBD",
                    "gait": "TBD",
                },
                "quality_flags": ["schema_validation_only"],
            }
        ],
        "quality": {
            "dataset_confidence": "low",
            "known_limitations": ["No real experiment is represented by this fixture."],
            "excluded_trials": [],
        },
        "downstream_boundaries": {
            "compensation_logic_included": False,
            "inverse_command_mapping_included": False,
            "navigation_control_included": False,
            "safe_command_adapter_included": False,
            "publication_ready_claim": False,
        },
    }


def assert_invalid_dataset(schema: dict, dataset: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(dataset)


def test_load_schema_through_module(schema: dict) -> None:
    assert schema["title"] == "K1 velocity response dataset schema v1"


def test_validate_schema_through_module(schema: dict) -> None:
    errors = validate_velocity_response_schema(schema)

    assert errors == []
    assert {
        "remote_controller_state",
        "hand_controller_state",
        "unconfirmed_ros2_topic",
    }.issubset(get_disallowed_fields(schema))


def test_velocity_response_json_schema_still_accepts_minimal_dataset(
    schema: dict, minimal_dataset: dict
) -> None:
    Draft202012Validator(schema).validate(minimal_dataset)


def test_minimal_dataset_without_battery_state_passes(schema: dict, minimal_dataset: dict) -> None:
    Draft202012Validator(schema).validate(minimal_dataset)


def test_dataset_with_optional_battery_state_passes(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["trials"][0]["robot_state"]["battery_state"] = {
        "percentage": 85.0,
        "voltage_v": 48.0,
    }

    Draft202012Validator(schema).validate(dataset)


def test_dataset_remote_controller_state_is_rejected(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["trials"][0]["robot_state"]["remote_controller_state"] = "manual"

    assert_invalid_dataset(schema, dataset)


def test_downstream_compensation_claim_is_rejected(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["downstream_boundaries"]["compensation_logic_included"] = True

    assert_invalid_dataset(schema, dataset)


def test_accept_minimal_valid_example_record(schema: dict) -> None:
    record = json.loads(VALID_RECORD_PATH.read_text(encoding="utf-8"))

    assert validate_velocity_response_record(record, schema) == []


def test_reject_invalid_disallowed_field_example_record(schema: dict) -> None:
    record = json.loads(INVALID_RECORD_PATH.read_text(encoding="utf-8"))
    errors = validate_velocity_response_record(record, schema)

    assert any("remote_controller_state" in error for error in errors)


@pytest.mark.parametrize(
    "field_name",
    [
        "remote_controller_state",
        "hand_controller_state",
        "unconfirmed_ros2_topic",
    ],
)
def test_reject_nested_disallowed_fields(
    schema: dict,
    valid_record: dict,
    field_name: str,
) -> None:
    record = copy.deepcopy(valid_record)
    record["nested"] = {"state": {field_name: "disallowed"}}

    errors = validate_velocity_response_record(record, schema)

    assert any(field_name in error for error in errors)
    assert any("nested.state" in error for error in errors)


def test_missing_battery_state_is_accepted(schema: dict, valid_record: dict) -> None:
    assert "battery_state" not in valid_record
    assert validate_velocity_response_record(valid_record, schema) == []


def test_readable_error_messages(schema: dict, valid_record: dict) -> None:
    record = copy.deepcopy(valid_record)
    record.pop("vx_cmd_mps")

    errors = validate_velocity_response_record(record, schema)

    assert errors
    assert "Missing required record field: vx_cmd_mps." in errors


def test_assert_valid_raises_readable_error(schema: dict, valid_record: dict) -> None:
    record = copy.deepcopy(valid_record)
    record["robot_state"] = {"hand_controller_state": "disallowed"}

    with pytest.raises(ValueError, match="hand_controller_state"):
        assert_velocity_response_record_valid(record, schema)


def test_validation_does_not_mutate_input_records(schema: dict, valid_record: dict) -> None:
    before = copy.deepcopy(valid_record)

    validate_velocity_response_record(valid_record, schema)

    assert valid_record == before


def test_cli_schema_validation_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_SCRIPT),
            "--schema",
            str(SCHEMA_PATH),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert '"valid_schema": true' in result.stdout
    assert '"valid_record": true' in result.stdout


def test_cli_valid_record_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_SCRIPT),
            "--schema",
            str(SCHEMA_PATH),
            "--record",
            str(VALID_RECORD_PATH),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert '"valid_record": true' in result.stdout


def test_cli_invalid_record_fails() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_SCRIPT),
            "--schema",
            str(SCHEMA_PATH),
            "--record",
            str(INVALID_RECORD_PATH),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "remote_controller_state" in result.stderr
