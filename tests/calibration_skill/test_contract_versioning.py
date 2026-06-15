"""Contract versioning policy tests."""
import pytest
from calibration_skill.schemas.registry import (
    SCHEMA_REGISTRY, CURRENT_SCHEMA_VERSION, get_schema_info,
    validate_schema_version,
)
from calibration_skill.schemas.validation import validate_payload


class TestSchemaVersioning:
    def test_current_version_is_1_0_0(self):
        assert CURRENT_SCHEMA_VERSION == "1.0.0"

    def test_all_registered_schemas_are_v1(self):
        for schema_id, info in SCHEMA_REGISTRY.items():
            assert info.version.startswith("1."), f"{schema_id} version is {info.version}"

    def test_schema_version_validation(self):
        assert validate_schema_version("skill_request", "1.0.0") is True
        assert validate_schema_version("skill_request", "2.0.0") is False
        assert validate_schema_version("nonexistent", "1.0.0") is False

    def test_get_schema_info_returns_none_for_unknown(self):
        assert get_schema_info("nonexistent") is None

    def test_get_schema_info_returns_info_for_known(self):
        info = get_schema_info("velocity_command")
        assert info is not None
        assert info.schema_id == "velocity_command"
        assert info.version == "1.0.0"

    def test_schema_count_is_13(self):
        assert len(SCHEMA_REGISTRY) == 13

    def test_unsupported_version_on_envelope(self):
        """Envelope with wrong schema_version should fail."""
        result = validate_payload("skill_request", {
            "schema_version": "2.0.0",
            "request_id": "r1", "operation": "test",
            "platform": "mock", "dry_run": True,
        })
        assert not result["valid"]

    def test_unknown_schema_returns_unsupported_code(self):
        result = validate_payload("future_schema_not_yet_defined", {})
        assert not result["valid"]
        assert result.get("error_code") == "schema_version_unsupported"

    def test_additional_properties_rejected(self):
        """By default, v1 schemas use additionalProperties: false."""
        result = validate_payload("error", {
            "code": "test",
            "message": "ok",
            "unexpected_field": "should be rejected",
        })
        assert not result["valid"]
