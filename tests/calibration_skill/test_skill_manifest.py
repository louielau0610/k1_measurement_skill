import json
from pathlib import Path

from jsonschema import Draft202012Validator

from calibration_skill.skill.manifest import build_skill_manifest
from calibration_skill.skill.operations import SUPPORTED_OPERATIONS


ROOT = Path(__file__).resolve().parents[2]


def test_manifest_schema_valid():
    manifest = build_skill_manifest()
    schema = json.loads((ROOT / "calibration_skill/skill/manifest.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(manifest)


def test_manifest_lists_supported_operations_and_no_physical_operation():
    manifest = build_skill_manifest()
    assert tuple(manifest["supported_operations"]) == SUPPORTED_OPERATIONS
    assert all("physical" not in op for op in manifest["supported_operations"])


def test_manifest_real_platforms_unavailable_and_mock_dry_run_only():
    manifest = build_skill_manifest()
    assert manifest["platform_support"]["mock"]["status"] == "supported"
    assert manifest["platform_support"]["mock"]["dry_run_only"] is True
    assert manifest["platform_support"]["booster_k1"]["status"] == "not_available_new_runtime"
    assert manifest["platform_support"]["unitree_g1"]["status"] == "not_available"
    assert manifest["platform_support"]["unitree_go1"]["status"] == "not_available"
    assert manifest["hardware_support"] == "not_supported"


def test_manifest_examples_exist():
    manifest = build_skill_manifest()
    for rel in manifest["examples"].values():
        assert (ROOT / rel).exists(), rel


def test_manifest_artifact_matches_source_of_truth():
    artifact = json.loads((ROOT / "outputs/engineering/m26d_skill_manifest.json").read_text(encoding="utf-8"))
    assert artifact == build_skill_manifest()
