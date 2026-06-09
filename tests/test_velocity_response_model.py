from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from k1_measurement.velocity_response_model import (
    VelocityResponseModel,
    extract_velocity_response_records,
    load_velocity_response_dataset,
    prediction_to_dict,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = REPO_ROOT / "outputs" / "research_datasets" / "velocity_response_dataset_v1.json"
SCHEMA_PATH = REPO_ROOT / "configs" / "velocity_response_dataset_schema_v1.json"
MODEL_SCRIPT = REPO_ROOT / "scripts" / "run_velocity_response_model_v1.py"


@pytest.fixture()
def dataset() -> dict:
    return load_velocity_response_dataset(DATASET_PATH)


@pytest.fixture()
def model(dataset: dict) -> VelocityResponseModel:
    return VelocityResponseModel.from_dataset(dataset)


def test_load_dataset(dataset: dict) -> None:
    assert dataset["dataset_id"] == "measurement_v0_velocity_response_dataset_v1"


def test_extract_records(dataset: dict) -> None:
    records = extract_velocity_response_records(dataset)

    assert len(records) == 5


def test_build_model_from_dataset(model: VelocityResponseModel) -> None:
    assert len(model.records) == 5
    assert len(model.numeric_records) == 4
    assert len(model.qualitative_only_records) == 1


def test_exact_qualitative_record_does_not_fabricate_numeric_value(
    model: VelocityResponseModel,
) -> None:
    prediction = model.predict(0.1)

    assert prediction.prediction_type == "exact_qualitative_source"
    assert prediction.predicted_vx_actual_mps is None
    assert prediction.qualitative_response_label == "deadzone_or_ineffective_low_speed"


def test_exact_numeric_record_returns_source_numeric_velocity(model: VelocityResponseModel) -> None:
    prediction = model.predict(0.4)

    assert prediction.prediction_type == "exact_numeric_source"
    assert prediction.predicted_vx_actual_mps == pytest.approx(0.274004)


def test_nearest_lookup_baseline_returns_nearest_supported_evidence(
    model: VelocityResponseModel,
) -> None:
    prediction = model.predict(0.11, model_name="nearest_lookup_baseline_v1")

    assert prediction.prediction_type == "nearest_lookup_qualitative"
    assert prediction.predicted_vx_actual_mps is None
    assert prediction.nearest_command_points_mps == [0.1]


def test_naive_global_gain_baseline_uses_only_numeric_records(model: VelocityResponseModel) -> None:
    prediction = model.predict(0.4, model_name="naive_global_gain_baseline_v1")

    assert prediction.predicted_vx_actual_mps is not None
    assert prediction.metadata["numeric_records_used"] == 4


def test_piecewise_linear_baseline_does_not_interpolate_when_numeric_bracketing_unsupported(
    model: VelocityResponseModel,
) -> None:
    prediction = model.predict(0.2, model_name="piecewise_linear_baseline_v1")

    assert prediction.prediction_type == "piecewise_out_of_range_unavailable"
    assert prediction.predicted_vx_actual_mps is None
    assert prediction.extrapolation_used is True


def test_hybrid_model_handles_mixed_evidence_conservatively(model: VelocityResponseModel) -> None:
    prediction = model.predict(0.2)

    assert prediction.prediction_type == "nearest_mixed_evidence"
    assert prediction.predicted_vx_actual_mps is None
    assert prediction.confidence_label == "low"


def test_hybrid_model_handles_bounded_interpolation(model: VelocityResponseModel) -> None:
    prediction = model.predict(0.35)

    assert prediction.prediction_type == "bounded_interpolation"
    assert prediction.interpolation_used is True
    assert prediction.predicted_vx_actual_mps is not None


def test_hybrid_model_handles_out_of_range_conservatively(model: VelocityResponseModel) -> None:
    prediction = model.predict(0.8)

    assert prediction.prediction_type == "out_of_range_conservative"
    assert prediction.predicted_vx_actual_mps is None
    assert prediction.extrapolation_used is True


def test_prediction_objects_are_json_serializable(model: VelocityResponseModel) -> None:
    payload = prediction_to_dict(model.predict(0.4))

    json.dumps(payload)


def test_every_prediction_preserves_safety_flags(model: VelocityResponseModel) -> None:
    for prediction in model.predict_many([0.1, 0.3, 0.35, 0.8]):
        assert prediction.compensation_allowed is False
        assert prediction.safe_command_adapter_allowed is False
        assert prediction.navigation_warning_ready is True


def test_no_prediction_includes_remote_controller_state(model: VelocityResponseModel) -> None:
    payload = json.dumps(prediction_to_dict(model.predict(0.4)), ensure_ascii=False)

    assert "remote_controller_state" not in payload


def test_missing_battery_state_is_accepted(dataset: dict) -> None:
    payload = json.dumps(dataset, ensure_ascii=False)

    assert '"battery_state"' in payload
    assert "battery_state" in dataset["unavailable_fields"]


def test_cli_writes_predictions_and_evaluation_outputs(tmp_path: Path) -> None:
    predictions_path = tmp_path / "predictions.json"
    evaluation_path = tmp_path / "evaluation.json"
    result = subprocess.run(
        [
            sys.executable,
            str(MODEL_SCRIPT),
            "--dataset",
            str(DATASET_PATH),
            "--schema",
            str(SCHEMA_PATH),
            "--predictions-output",
            str(predictions_path),
            "--evaluation-output",
            str(evaluation_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert predictions_path.exists()
    assert evaluation_path.exists()
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    assert "uncertainty_aware_hybrid_v1" in predictions["predictions_by_model"]
    assert evaluation["metrics"]["exact_source_reconstruction_only"] is True


def test_cli_exits_nonzero_for_invalid_dataset_path(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(MODEL_SCRIPT),
            "--dataset",
            str(tmp_path / "missing.json"),
            "--schema",
            str(SCHEMA_PATH),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "missing.json" in result.stderr
