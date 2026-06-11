from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from calibration_core.measurement_manifest import REQUIRED_MANIFEST_FIELDS, load_manifest, validate_measurement_manifest
from calibration_core.measurement_pipeline import MeasurementPipeline

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "outputs/measurement_v1/booster_k1_reference_manifest.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


def test_measurement_manifest_schema_fields_present() -> None:
    manifest = load_manifest(MANIFEST_PATH)
    assert all(field in manifest for field in REQUIRED_MANIFEST_FIELDS)
    assert manifest["platform"] == "booster_k1"
    assert manifest["validation_status"] == "booster_k1_reference_ready"


def test_measurement_module_status_flags_preserve_boundary() -> None:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    assert status["measurement_module_v1_status"] == "consolidated_reference_ready"
    assert status["booster_k1_reference_ready"] is True
    assert status["unitree_go1_measurement_ready"] is False
    assert status["unitree_g1_measurement_ready"] is False
    assert status["velocity_compensation_ready"] is False
    assert status["cross_platform_empirical_validation_ready"] is False


def test_k1_reference_manifest_validation_passes() -> None:
    summary = validate_measurement_manifest(load_manifest(MANIFEST_PATH), ROOT)
    assert summary["valid"] is True
    assert summary["errors"] == []
    assert summary["extracted_measurement_rows"] == 72
    assert summary["compensation_ready"] is False


def test_manifest_validation_detects_missing_artifact() -> None:
    manifest = load_manifest(MANIFEST_PATH)
    manifest["profile_path"] = "outputs/measurement_v1/missing_profile.json"
    summary = validate_measurement_manifest(manifest, ROOT)
    assert summary["valid"] is False
    assert any(error.startswith("profile_path:missing") for error in summary["errors"])


def test_extracted_measurements_are_complete_and_ok() -> None:
    summary = validate_measurement_manifest(load_manifest(MANIFEST_PATH), ROOT)
    assert summary["valid"] is True
    assert summary["extracted_measurement_rows"] == 72
    assert not any("non_ok_status" in error for error in summary["errors"])
    assert not any("surface_speed_cells:not_n3" in error for error in summary["errors"])


def test_measurement_pipeline_dry_run_does_not_require_hardware() -> None:
    pipeline = MeasurementPipeline(platform="booster_k1", robot_model="Booster K1")
    trials = pipeline.plan_trials(["S1_lab_hard_floor"], [0.2], repeats=2, prefix="K1")
    result = pipeline.run_trials(trials)
    assert len(trials) == 2
    assert result["dry_run"] is True
    assert result["hardware_executed"] is False


def test_show_measurement_module_status_cli_output() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_measurement_module_status.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "measurement_module_v1_status: consolidated_reference_ready" in result.stdout
    assert "validated_platforms: booster_k1" in result.stdout
    assert "scaffold_only_platforms: unitree_go1, unitree_g1" in result.stdout
    assert "velocity_compensation_ready: False" in result.stdout


def test_validate_measurement_manifest_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_measurement_manifest.py",
            "--manifest",
            "outputs/measurement_v1/booster_k1_reference_manifest.json",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)
    assert summary["valid"] is True
    assert summary["extracted_measurement_rows"] == 72
    assert summary["compensation_ready"] is False


def test_no_go1_g1_validation_claim() -> None:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    manifest = load_manifest(MANIFEST_PATH)
    assert "unitree_go1" in status["scaffold_only_platforms"]
    assert "unitree_g1" in status["scaffold_only_platforms"]
    assert status["unitree_go1_measurement_ready"] is False
    assert status["unitree_g1_measurement_ready"] is False
    assert manifest["empirical_cross_platform_claim"] is False
