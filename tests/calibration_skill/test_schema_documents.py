"""Test schema documents parse as valid JSON."""
import json
import os
import pytest

SCHEMA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "calibration_skill", "schemas", "v1"
)


def _list_schema_files():
    if not os.path.isdir(SCHEMA_DIR):
        return []
    return sorted(
        os.path.join(SCHEMA_DIR, f)
        for f in os.listdir(SCHEMA_DIR)
        if f.endswith(".schema.json")
    )


SCHEMA_FILES = _list_schema_files()


class TestSchemaDocuments:
    @pytest.mark.parametrize("schema_path", SCHEMA_FILES)
    def test_schema_parses_as_json(self, schema_path):
        """Each schema file must parse as valid JSON."""
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "$schema" in data
        assert "$id" in data

    @pytest.mark.parametrize("schema_path", SCHEMA_FILES)
    def test_schema_has_stable_id(self, schema_path):
        """Each schema must have a stable URN identifier."""
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sid = data.get("$id", "")
        assert sid.startswith("urn:calibration-skill:schema:"), \
            f"Schema {os.path.basename(schema_path)} has invalid $id: {sid}"
        assert ":v1" in sid

    def test_all_expected_schemas_exist(self):
        expected = [
            "skill_request.schema.json",
            "skill_response.schema.json",
            "error.schema.json",
            "robot_identity.schema.json",
            "capability_descriptor.schema.json",
            "velocity_command.schema.json",
            "command_receipt.schema.json",
            "telemetry_sample.schema.json",
            "preflight_report.schema.json",
            "safety_envelope.schema.json",
            "operator_authorization.schema.json",
            "calibration_profile.schema.json",
            "execution_audit_record.schema.json",
        ]
        existing = [os.path.basename(f) for f in SCHEMA_FILES]
        for name in expected:
            assert name in existing, f"Missing schema: {name}"

    def test_schema_version_consistency(self):
        """All schemas should have consistent versioning."""
        for schema_path in SCHEMA_FILES:
            with open(schema_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check that the schema describes itself as v1
            assert "v1" in data.get("$id", ""), \
                f"Schema {os.path.basename(schema_path)} missing v1 in $id"
