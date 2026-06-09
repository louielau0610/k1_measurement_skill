"""Tests for M20 future experiment protocol schema validation."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_future_experiment_protocol_schema import (
    load_json, validate_schema, validate_record, check_disallowed_recursive, check_readiness_flags
)

SCHEMA_PATH = "configs/future_experiment_protocol_schema_v1.json"
MINIMAL_PATH = "examples/future_experiments/minimal_future_experiment_record.json"
INVALID_PATH = "examples/future_experiments/invalid_future_experiment_record.json"

def test_schema_loads():
    schema = load_json(SCHEMA_PATH)
    assert schema["type"] == "object"
    assert "properties" in schema

def test_schema_validates():
    schema = load_json(SCHEMA_PATH)
    errors = validate_schema(schema)
    assert len(errors) == 0

def test_minimal_record_validates():
    schema = load_json(SCHEMA_PATH)
    record = load_json(MINIMAL_PATH)
    errors = validate_record(record)
    assert len(errors) == 0, f"Unexpected errors: {errors}"

def test_invalid_record_rejected():
    record = load_json(INVALID_PATH)
    errors = validate_record(record)
    assert len(errors) > 0
    assert any("remote_controller_state" in e for e in errors)

def test_battery_state_optional():
    record = load_json(MINIMAL_PATH)
    errors = validate_record(record)
    assert len(errors) == 0  # no error for missing battery_state

def test_remote_controller_state_rejected():
    record = {"remote_controller_state": "test"}
    errors = check_disallowed_recursive(record)
    assert len(errors) == 1
    assert "remote_controller_state" in errors[0]

def test_unsafe_readiness_flag_rejected():
    record = {
        "downstream_readiness": {
            "safe_command_adapter_ready": True
        },
        "trial_records": [{"trial_id": "t1"}]
    }
    errors = check_readiness_flags(record)
    assert len(errors) > 0
    assert any("safe_command_adapter_ready" in e for e in errors)

def test_validator_does_not_mutate_input():
    record = load_json(MINIMAL_PATH)
    original = json.dumps(record)
    validate_record(record)
    assert json.dumps(record) == original
