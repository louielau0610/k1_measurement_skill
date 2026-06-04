from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "contracts" / "measurement_profile_schema.json"
DUMMY_PROFILE_PATH = REPO_ROOT / "examples" / "dummy_processed_environment_profile.json"


@pytest.fixture()
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def dummy_profile() -> dict:
    return json.loads(DUMMY_PROFILE_PATH.read_text(encoding="utf-8"))


def assert_invalid(schema: dict, profile: dict) -> None:
    validator = Draft202012Validator(schema)
    with pytest.raises(ValidationError):
        validator.validate(profile)


def test_dummy_processed_environment_profile_passes_schema(
    schema: dict, dummy_profile: dict
) -> None:
    Draft202012Validator(schema).validate(dummy_profile)


def test_missing_required_top_level_field_fails(schema: dict, dummy_profile: dict) -> None:
    profile = copy.deepcopy(dummy_profile)
    profile.pop("metadata")
    assert_invalid(schema, profile)


def test_invalid_environment_floor_type_fails(schema: dict, dummy_profile: dict) -> None:
    profile = copy.deepcopy(dummy_profile)
    profile["environment"]["floor_type"] = "ice"
    assert_invalid(schema, profile)


def test_invalid_quality_confidence_fails(schema: dict, dummy_profile: dict) -> None:
    profile = copy.deepcopy(dummy_profile)
    profile["quality"]["confidence"] = "certain"
    assert_invalid(schema, profile)


def test_velocity_profile_zero_trials_fails(schema: dict, dummy_profile: dict) -> None:
    profile = copy.deepcopy(dummy_profile)
    profile["velocity_profile"][0]["n_trials"] = 0
    assert_invalid(schema, profile)
