"""Package resource access tests for installed/source layouts."""
from __future__ import annotations

import json
from importlib import resources

from calibration_skill.schemas.validation import get_schema_document, validate_skill_request
from calibration_skill.skill.manifest import build_skill_manifest, operation_catalog


def test_schema_files_accessible_as_package_resources():
    schema_root = resources.files("calibration_skill.schemas.v1")
    request_schema = schema_root.joinpath("skill_request.schema.json")
    response_schema = schema_root.joinpath("skill_response.schema.json")
    assert request_schema.is_file()
    assert response_schema.is_file()
    assert json.loads(request_schema.read_text(encoding="utf-8"))["$id"].endswith(":skill_request:v1")


def test_manifest_schema_accessible_as_package_resource():
    schema = resources.files("calibration_skill.skill").joinpath("manifest.schema.json")
    assert schema.is_file()
    assert json.loads(schema.read_text(encoding="utf-8"))["title"] == "M26-D Skill Manifest"


def test_schema_loader_does_not_require_repository_relative_paths():
    document = get_schema_document("skill_request")
    assert document["$id"].endswith(":skill_request:v1")


def test_operation_catalog_generation_is_runtime_available():
    manifest = build_skill_manifest()
    operations = operation_catalog()
    assert manifest["supported_operations"] == [op["name"] for op in operations]
    assert "dry_run_end_to_end" in manifest["supported_operations"]


def test_example_payload_validates_through_package_schema_loader():
    payload = {
        "schema_version": "1.0.0",
        "request_id": "package-data-smoke",
        "operation": "preflight",
        "platform": "mock",
        "robot_id": "mock-robot",
        "dry_run": True,
        "payload": {},
    }
    assert validate_skill_request(payload)["valid"] is True
