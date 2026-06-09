from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from scripts.validate_velocity_response_dataset_schema import validate_schema_file


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate_velocity_response_dataset_schema.py"


@pytest.fixture()
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def assert_invalid(schema: dict, dataset: dict) -> None:
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(dataset)


def test_velocity_response_schema_is_valid_json_schema() -> None:
    summary = validate_schema_file(SCHEMA_PATH)

    assert summary["valid_schema"] is True
    assert summary["battery_state_required"] is False
    assert summary["prohibited_fields_present"] == []


def test_minimal_dataset_without_battery_state_passes(schema: dict, minimal_dataset: dict) -> None:
    Draft202012Validator(schema).validate(minimal_dataset)


def test_dataset_with_optional_battery_state_passes(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["trials"][0]["robot_state"]["battery_state"] = {
        "percentage": 85.0,
        "voltage_v": 48.0,
    }

    Draft202012Validator(schema).validate(dataset)


def test_remote_controller_state_is_rejected(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["trials"][0]["robot_state"]["remote_controller_state"] = "manual"

    assert_invalid(schema, dataset)


def test_downstream_compensation_claim_is_rejected(schema: dict, minimal_dataset: dict) -> None:
    dataset = copy.deepcopy(minimal_dataset)
    dataset["downstream_boundaries"]["compensation_logic_included"] = True

    assert_invalid(schema, dataset)


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
