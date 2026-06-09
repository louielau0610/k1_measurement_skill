from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from k1_measurement.research_dataset_schema import (
    load_velocity_response_schema,
    validate_velocity_response_record,
)
from k1_measurement.velocity_response_dataset_builder import (
    build_future_trial_template,
    build_velocity_response_dataset_v1,
    load_measurement_v0_artifacts,
    validate_built_dataset,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT_ROOT = REPO_ROOT / "outputs" / "real_k1_field_tests"
SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
BUILDER_SCRIPT = REPO_ROOT / "scripts" / "build_velocity_response_dataset_v1.py"


@pytest.fixture()
def schema() -> dict:
    return load_velocity_response_schema(SCHEMA_PATH)


def test_builder_loads_measurement_v0_artifact_root() -> None:
    artifacts = load_measurement_v0_artifacts(MEASUREMENT_ROOT)

    assert "profile" in artifacts
    assert "summary" in artifacts
    assert "trials_csv" in artifacts
    assert artifacts["source_artifacts_used"]


def test_builder_creates_dataset_dictionary(schema: dict) -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)

    assert dataset["dataset_id"] == "measurement_v0_velocity_response_dataset_v1"
    assert dataset["records"]
    assert validate_built_dataset(dataset, schema) == []


def test_dataset_includes_source_provenance() -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)

    assert dataset["source_artifacts_used"]
    assert all("source_provenance" in record for record in dataset["records"])


def test_dataset_excludes_remote_controller_state() -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)
    rendered = json.dumps(dataset, ensure_ascii=False)

    assert "remote_controller_state" not in rendered


def test_dataset_does_not_require_battery_state(schema: dict) -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)
    rendered = json.dumps(dataset, ensure_ascii=False)

    assert "battery_state" in dataset["unavailable_fields"]
    assert "battery_state" not in rendered.replace('"battery_state"', "", 1)
    assert validate_velocity_response_record(dataset, schema) == []


def test_dataset_preserves_downstream_readiness_flags() -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)

    assert dataset["compensation_ready"] is False
    assert dataset["safe_command_adapter_ready"] is False
    assert dataset["navigation_warning_ready"] is True
    assert dataset["navigation_control_ready"] is False


def test_builder_does_not_fabricate_actual_velocity_when_absent() -> None:
    dataset = build_velocity_response_dataset_v1(MEASUREMENT_ROOT, SCHEMA_PATH)
    deadzone_record = next(record for record in dataset["records"] if record["vx_cmd_mps"] == 0.1)

    assert "vx_actual_mps_mean" not in deadzone_record
    assert "qualitative_response_label" in deadzone_record
    assert "vx_actual_mps_mean" in deadzone_record["field_categories"]["unavailable"]


def test_future_trial_template_excludes_disallowed_fields(schema: dict) -> None:
    template = build_future_trial_template(SCHEMA_PATH)
    rendered = json.dumps(template, ensure_ascii=False)

    assert "remote_controller_state" not in rendered
    assert "hand_controller_state" not in rendered
    assert "unconfirmed_ros2_topic" not in rendered
    assert validate_built_dataset(template, schema) == []


def test_cli_builds_dataset_and_report_in_temporary_output_dir(tmp_path: Path) -> None:
    dataset_path = tmp_path / "velocity_response_dataset_v1.json"
    report_path = tmp_path / "velocity_response_dataset_v1_validation_report.json"
    template_path = tmp_path / "future_velocity_response_trial_template_v1.json"

    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_SCRIPT),
            "--measurement-root",
            str(MEASUREMENT_ROOT),
            "--schema",
            str(SCHEMA_PATH),
            "--output",
            str(dataset_path),
            "--report",
            str(report_path),
            "--template",
            str(template_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert dataset_path.exists()
    assert report_path.exists()
    assert template_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["validation_passed"] is True


def test_cli_exits_nonzero_for_missing_required_source_root(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_SCRIPT),
            "--measurement-root",
            str(tmp_path / "missing"),
            "--schema",
            str(SCHEMA_PATH),
            "--output",
            str(tmp_path / "dataset.json"),
            "--report",
            str(tmp_path / "report.json"),
            "--template",
            str(tmp_path / "template.json"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Measurement v0 root not found" in result.stderr
