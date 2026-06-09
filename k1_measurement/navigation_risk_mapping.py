"""Offline navigation-aware reliability and risk mapping for response predictions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


RISK_MAP_NAME = "navigation_reliability_risk_mapper_v1"
DEFAULT_MODEL_NAME = "uncertainty_aware_hybrid_v1"

ALLOWED_DOWNSTREAM_USES = [
    "offline_analysis",
    "research_evaluation",
    "planner_warning_advisory",
    "human_review",
]

DISALLOWED_DOWNSTREAM_USES = [
    "automatic_compensation",
    "inverse_command_mapping",
    "real_time_navigation_control",
    "safe_command_adapter_execution",
    "robot_motion_commanding",
]


@dataclass(frozen=True)
class NavigationRiskAssessment:
    query_vx_cmd_mps: float
    model_name: str
    prediction_type: str
    qualitative_response_label: str | None
    predicted_vx_actual_mps: float | None
    uncertainty_label: str
    confidence_label: str
    tracking_reliability_label: str
    navigation_risk_level: str
    warning_required: bool
    warning_category: str
    risk_reasons: list[str]
    allowed_downstream_uses: list[str]
    disallowed_downstream_uses: list[str]
    source_record_ids: list[str]
    compensation_allowed: bool
    safe_command_adapter_allowed: bool
    navigation_warning_ready: bool
    limitations: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NavigationRiskMapEvaluation:
    risk_map_name: str
    predictions_path: str
    assessments_count: int
    warnings_count: int
    risk_level_counts: dict[str, int]
    warning_category_counts: dict[str, int]
    limitations: list[str]
    metrics: dict[str, Any]


def load_response_model_predictions(path: str | Path) -> dict[str, Any]:
    predictions_path = Path(path)
    with predictions_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"Response model predictions must be a JSON object: {predictions_path}")
    return payload


def extract_predictions(
    predictions_payload: dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[dict[str, Any]]:
    grouped = predictions_payload.get("predictions_by_model")
    if not isinstance(grouped, dict):
        raise ValueError("Predictions payload must contain predictions_by_model.")
    predictions = grouped.get(model_name)
    if not isinstance(predictions, list):
        raise ValueError(f"Predictions payload does not contain model: {model_name}")
    result: list[dict[str, Any]] = []
    for index, prediction in enumerate(predictions):
        if not isinstance(prediction, dict):
            raise ValueError(f"Prediction {index} for {model_name} is not an object.")
        result.append(prediction)
    return result


class NavigationRiskMapper:
    def __init__(
        self,
        predictions_payload: dict[str, Any],
        predictions: list[dict[str, Any]],
        model_name: str,
    ) -> None:
        self.predictions_payload = predictions_payload
        self.predictions = predictions
        self.model_name = model_name

    @classmethod
    def from_predictions_payload(
        cls,
        predictions_payload: dict[str, Any],
        model_name: str = DEFAULT_MODEL_NAME,
    ) -> "NavigationRiskMapper":
        return cls(predictions_payload, extract_predictions(predictions_payload, model_name), model_name)

    def assess_prediction(self, prediction: dict[str, Any]) -> NavigationRiskAssessment:
        prediction_type = str(prediction.get("prediction_type", "unsupported"))
        label = _optional_str(prediction.get("qualitative_response_label"))
        uncertainty = str(prediction.get("uncertainty_label", "high"))
        confidence = str(prediction.get("confidence_label", "unknown"))
        reasons: list[str] = []
        warning_category = "none"
        tracking = "limited"
        risk = "medium"
        warning_required = False

        if "out_of_range" in prediction_type:
            tracking = "unsupported"
            risk = "unsupported"
            warning_required = True
            warning_category = "out_of_range"
            reasons.append("prediction is outside measured command range")
        elif "unsupported" in prediction_type:
            tracking = "unsupported"
            risk = "unsupported"
            warning_required = True
            warning_category = "unsupported_prediction"
            reasons.append("prediction is unsupported by available response model output")
        elif _contains_any(label, ["deadzone", "ineffective", "no_motion", "almost_none"]):
            tracking = "unreliable"
            risk = "critical"
            warning_required = True
            warning_category = "deadzone_or_no_motion"
            reasons.append("qualitative response indicates deadzone or ineffective motion")
        elif _contains_any(label, ["weak"]):
            tracking = "weak"
            risk = "high"
            warning_required = True
            warning_category = "weak_tracking"
            reasons.append("qualitative response indicates weak tracking")
        elif _contains_any(label, ["under_tracking", "under-tracking"]):
            tracking = "limited"
            risk = "high"
            warning_required = True
            warning_category = "under_tracking"
            reasons.append("qualitative response indicates under-tracking")
        elif _contains_any(label, ["near_stable", "repeat", "further_validation", "yaw"]):
            tracking = "limited"
            risk = "medium"
            warning_required = True
            warning_category = "high_uncertainty"
            reasons.append("response needs repeat or further validation")
        elif _contains_any(label, ["stable"]):
            tracking = "reliable_reference"
            risk = "low"
            warning_required = False
            warning_category = "none"
            reasons.append("source label indicates stable reference under current dataset scope")

        if "qualitative" in prediction_type and risk not in {"critical", "unsupported"}:
            risk = _max_risk(risk, "high")
            warning_required = True
            warning_category = "qualitative_only"
            reasons.append("prediction is qualitative-only")

        if uncertainty in {"high", "medium_high"}:
            risk = _max_risk(risk, "medium")
            warning_required = True
            if warning_category == "none":
                warning_category = "high_uncertainty"
            reasons.append(f"uncertainty label is {uncertainty}")

        if confidence in {"low", "unknown"}:
            risk = _max_risk(risk, "medium")
            warning_required = True
            if warning_category == "none":
                warning_category = "high_uncertainty"
            reasons.append(f"confidence label is {confidence}")

        if prediction.get("compensation_allowed") is False:
            reasons.append("compensation is not an allowed downstream use")
        if prediction.get("safe_command_adapter_allowed") is False:
            reasons.append("safe command adapter execution is not an allowed downstream use")

        limitations = [
            str(item) for item in prediction.get("limitations", []) if isinstance(item, str)
        ]
        limitations.extend(
            [
                "offline advisory risk mapping only",
                "no real navigation outcomes are represented",
                "uncertainty_and_confidence_are_labels_not_calibrated_probabilities",
            ]
        )

        return NavigationRiskAssessment(
            query_vx_cmd_mps=float(prediction.get("query_vx_cmd_mps")),
            model_name=str(prediction.get("model_name", self.model_name)),
            prediction_type=prediction_type,
            qualitative_response_label=label,
            predicted_vx_actual_mps=_optional_float(prediction.get("predicted_vx_actual_mps")),
            uncertainty_label=uncertainty,
            confidence_label=confidence,
            tracking_reliability_label=tracking,
            navigation_risk_level=risk,
            warning_required=warning_required,
            warning_category=warning_category,
            risk_reasons=sorted(dict.fromkeys(reasons)),
            allowed_downstream_uses=list(ALLOWED_DOWNSTREAM_USES),
            disallowed_downstream_uses=list(DISALLOWED_DOWNSTREAM_USES),
            source_record_ids=[
                str(item) for item in prediction.get("source_record_ids", []) if isinstance(item, str)
            ],
            compensation_allowed=False,
            safe_command_adapter_allowed=False,
            navigation_warning_ready=bool(prediction.get("navigation_warning_ready", True)),
            limitations=sorted(dict.fromkeys(limitations)),
            metadata={
                "risk_map_name": RISK_MAP_NAME,
                "source_prediction_metadata": prediction.get("metadata", {}),
            },
        )

    def assess_all(self) -> list[NavigationRiskAssessment]:
        return [self.assess_prediction(prediction) for prediction in self.predictions]

    def evaluate(self) -> NavigationRiskMapEvaluation:
        assessments = self.assess_all()
        risk_counts: dict[str, int] = {}
        warning_counts: dict[str, int] = {}
        for assessment in assessments:
            risk_counts[assessment.navigation_risk_level] = (
                risk_counts.get(assessment.navigation_risk_level, 0) + 1
            )
            warning_counts[assessment.warning_category] = (
                warning_counts.get(assessment.warning_category, 0) + 1
            )

        return NavigationRiskMapEvaluation(
            risk_map_name=RISK_MAP_NAME,
            predictions_path=str(self.predictions_payload.get("predictions_path", "outputs/research_models/response_model_predictions_v1.json")),
            assessments_count=len(assessments),
            warnings_count=sum(1 for assessment in assessments if assessment.warning_required),
            risk_level_counts=dict(sorted(risk_counts.items())),
            warning_category_counts=dict(sorted(warning_counts.items())),
            limitations=[
                "structural readiness evaluation only",
                "no real navigation outcomes exist yet",
                "no collision, near-miss, or success-rate metrics exist yet",
                "uncertainty labels are not calibrated probabilities",
            ],
            metrics={
                "available_metrics": [
                    "assessments_count",
                    "warnings_count",
                    "risk_level_counts",
                    "warning_category_counts",
                ],
                "unavailable_metrics": [
                    "collision_rate",
                    "near_miss_rate",
                    "navigation_success_rate",
                    "real_world_safety_improvement",
                ],
                "no_real_navigation_outcomes": True,
                "fabricated_navigation_outcomes": False,
                "no_safety_improvement_claim": True,
            },
        )


def assessment_to_dict(assessment: NavigationRiskAssessment) -> dict[str, Any]:
    return asdict(assessment)


def evaluation_to_dict(evaluation: NavigationRiskMapEvaluation) -> dict[str, Any]:
    return asdict(evaluation)


def build_risk_map_payload(
    predictions_path: str | Path,
    predictions_payload: dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, Any]:
    mapper = NavigationRiskMapper.from_predictions_payload(predictions_payload, model_name)
    assessments = [assessment_to_dict(assessment) for assessment in mapper.assess_all()]
    return {
        "risk_map_name": RISK_MAP_NAME,
        "source_predictions_path": str(predictions_path),
        "source_model_name": model_name,
        "assessments": assessments,
        "safety_readiness_flags": {
            "compensation_ready": False,
            "safe_command_adapter_ready": False,
            "navigation_warning_ready": True,
        },
        "allowed_downstream_uses": list(ALLOWED_DOWNSTREAM_USES),
        "disallowed_downstream_uses": list(DISALLOWED_DOWNSTREAM_USES),
        "limitations": [
            "offline advisory risk mapping only",
            "no real navigation outcomes are represented",
            "uncertainty_and_confidence_are_labels_not_calibrated_probabilities",
            "sparse single-robot dataset",
            "missing yaw/lateral/delay/stop-distance metrics",
        ],
        "fabricated_navigation_outcomes": False,
        "compensation_logic_implemented": False,
        "inverse_command_mapping_implemented": False,
        "navigation_control_implemented": False,
        "safe_command_adapter_implemented": False,
    }


def build_risk_evaluation_payload(
    predictions_path: str | Path,
    predictions_payload: dict[str, Any],
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, Any]:
    mapper = NavigationRiskMapper.from_predictions_payload(predictions_payload, model_name)
    evaluation = evaluation_to_dict(mapper.evaluate())
    evaluation["predictions_path"] = str(predictions_path)
    evaluation["available_metrics"] = evaluation["metrics"]["available_metrics"]
    evaluation["unavailable_metrics"] = evaluation["metrics"]["unavailable_metrics"]
    evaluation["m17_readiness"] = {
        "can_evaluate_warning_distribution": True,
        "requires_real_navigation_trials_for_outcome_metrics": True,
        "must_not_claim_navigation_safety_improvement": True,
    }
    evaluation["no_real_navigation_outcomes"] = True
    evaluation["fabricated_navigation_outcomes"] = False
    evaluation["no_safety_improvement_claim"] = True
    return evaluation


def _contains_any(value: str | None, needles: list[str]) -> bool:
    if value is None:
        return False
    lowered = value.lower()
    return any(needle in lowered for needle in needles)


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_float(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def _max_risk(current: str, minimum: str) -> str:
    order = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3,
        "unsupported": 3,
    }
    return current if order.get(current, 0) >= order.get(minimum, 0) else minimum
