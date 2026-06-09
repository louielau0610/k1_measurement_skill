from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from k1_measurement.navigation_risk_mapping import (
    DISALLOWED_DOWNSTREAM_USES,
    NavigationRiskMapper,
    assessment_to_dict,
    extract_predictions,
    load_response_model_predictions,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = (
    REPO_ROOT / "outputs" / "research_models" / "response_model_predictions_v1.json"
)
RISK_SCRIPT = REPO_ROOT / "scripts" / "run_navigation_risk_mapping_v1.py"


@pytest.fixture()
def predictions_payload() -> dict:
    return load_response_model_predictions(PREDICTIONS_PATH)


@pytest.fixture()
def mapper(predictions_payload: dict) -> NavigationRiskMapper:
    return NavigationRiskMapper.from_predictions_payload(predictions_payload)


def _assessment_by_query(mapper: NavigationRiskMapper, query: float):
    for assessment in mapper.assess_all():
        if assessment.query_vx_cmd_mps == pytest.approx(query):
            return assessment
    raise AssertionError(f"Missing assessment for query {query}")


def test_load_response_model_predictions(predictions_payload: dict) -> None:
    assert "predictions_by_model" in predictions_payload


def test_extract_uncertainty_aware_hybrid_predictions(predictions_payload: dict) -> None:
    predictions = extract_predictions(predictions_payload)

    assert len(predictions) == 5
    assert all(prediction["model_name"] == "uncertainty_aware_hybrid_v1" for prediction in predictions)


def test_build_navigation_risk_mapper(mapper: NavigationRiskMapper) -> None:
    assert mapper.model_name == "uncertainty_aware_hybrid_v1"
    assert len(mapper.predictions) == 5


def test_assess_all_predictions(mapper: NavigationRiskMapper) -> None:
    assessments = mapper.assess_all()

    assert len(assessments) == 5


def test_assessment_objects_are_json_serializable(mapper: NavigationRiskMapper) -> None:
    payload = assessment_to_dict(_assessment_by_query(mapper, 0.1))

    json.dumps(payload)


def test_deadzone_qualitative_record_receives_warning(mapper: NavigationRiskMapper) -> None:
    assessment = _assessment_by_query(mapper, 0.1)

    assert assessment.warning_required is True
    assert assessment.warning_category == "deadzone_or_no_motion"
    assert assessment.navigation_risk_level == "critical"


def test_weak_tracking_record_receives_warning(mapper: NavigationRiskMapper) -> None:
    assessment = _assessment_by_query(mapper, 0.3)

    assert assessment.warning_required is True
    assert assessment.warning_category == "weak_tracking"
    assert assessment.navigation_risk_level == "high"


def test_under_tracking_record_receives_warning(mapper: NavigationRiskMapper) -> None:
    assessment = _assessment_by_query(mapper, 0.4)

    assert assessment.warning_required is True
    assert assessment.warning_category == "under_tracking"
    assert assessment.navigation_risk_level == "high"


def test_stable_reference_has_lower_risk_than_problem_regions(
    mapper: NavigationRiskMapper,
) -> None:
    deadzone = _assessment_by_query(mapper, 0.1)
    weak = _assessment_by_query(mapper, 0.3)
    under = _assessment_by_query(mapper, 0.4)
    stable = _assessment_by_query(mapper, 0.5)

    assert stable.navigation_risk_level == "medium"
    assert deadzone.navigation_risk_level == "critical"
    assert weak.navigation_risk_level == "high"
    assert under.navigation_risk_level == "high"


def test_high_uncertainty_does_not_produce_low_risk(mapper: NavigationRiskMapper) -> None:
    prediction = dict(mapper.predictions[0])
    prediction["uncertainty_label"] = "high"
    prediction["qualitative_response_label"] = "stable_tracking"

    assessment = mapper.assess_prediction(prediction)

    assert assessment.navigation_risk_level in {"medium", "high", "critical", "unsupported"}


def test_out_of_range_synthetic_prediction_is_conservative(mapper: NavigationRiskMapper) -> None:
    prediction = dict(mapper.predictions[-1])
    prediction["query_vx_cmd_mps"] = 0.8
    prediction["prediction_type"] = "out_of_range_conservative"
    prediction["predicted_vx_actual_mps"] = None

    assessment = mapper.assess_prediction(prediction)

    assert assessment.warning_required is True
    assert assessment.warning_category == "out_of_range"
    assert assessment.navigation_risk_level == "unsupported"


def test_every_assessment_includes_allowed_downstream_uses(
    mapper: NavigationRiskMapper,
) -> None:
    for assessment in mapper.assess_all():
        assert "offline_analysis" in assessment.allowed_downstream_uses
        assert "planner_warning_advisory" in assessment.allowed_downstream_uses


def test_every_assessment_includes_disallowed_downstream_uses(
    mapper: NavigationRiskMapper,
) -> None:
    for assessment in mapper.assess_all():
        for disallowed in DISALLOWED_DOWNSTREAM_USES:
            assert disallowed in assessment.disallowed_downstream_uses


def test_every_assessment_preserves_safety_flags(mapper: NavigationRiskMapper) -> None:
    for assessment in mapper.assess_all():
        assert assessment.compensation_allowed is False
        assert assessment.safe_command_adapter_allowed is False
        assert assessment.navigation_warning_ready is True


def test_no_assessment_contains_remote_controller_state(mapper: NavigationRiskMapper) -> None:
    rendered = json.dumps([assessment_to_dict(item) for item in mapper.assess_all()])

    assert "remote_controller_state" not in rendered


def test_missing_battery_state_is_accepted(mapper: NavigationRiskMapper) -> None:
    rendered = json.dumps([assessment_to_dict(item) for item in mapper.assess_all()])

    assert "battery_state" not in rendered


def test_cli_writes_risk_map_and_evaluation_outputs(tmp_path: Path) -> None:
    risk_map_path = tmp_path / "navigation_risk_map_v1.json"
    evaluation_path = tmp_path / "navigation_risk_evaluation_v1.json"

    result = subprocess.run(
        [
            sys.executable,
            str(RISK_SCRIPT),
            "--predictions",
            str(PREDICTIONS_PATH),
            "--risk-map-output",
            str(risk_map_path),
            "--evaluation-output",
            str(evaluation_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert risk_map_path.exists()
    assert evaluation_path.exists()
    risk_map = json.loads(risk_map_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    assert risk_map["risk_map_name"] == "navigation_reliability_risk_mapper_v1"
    assert evaluation["no_real_navigation_outcomes"] is True


def test_cli_exits_nonzero_for_invalid_predictions_path(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RISK_SCRIPT),
            "--predictions",
            str(tmp_path / "missing.json"),
            "--risk-map-output",
            str(tmp_path / "risk.json"),
            "--evaluation-output",
            str(tmp_path / "eval.json"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "missing.json" in result.stderr
