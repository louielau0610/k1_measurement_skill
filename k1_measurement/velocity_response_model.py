"""Conservative velocity response model foundation for research datasets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


MODEL_NAMES = [
    "uncertainty_aware_hybrid_v1",
    "nearest_lookup_baseline_v1",
    "naive_global_gain_baseline_v1",
    "piecewise_linear_baseline_v1",
]


@dataclass(frozen=True)
class VelocityResponsePrediction:
    query_vx_cmd_mps: float
    model_name: str
    prediction_type: str
    predicted_vx_actual_mps: float | None
    qualitative_response_label: str | None
    uncertainty_label: str
    confidence_label: str
    source_record_ids: list[str]
    nearest_command_points_mps: list[float]
    interpolation_used: bool
    extrapolation_used: bool
    limitations: list[str]
    compensation_allowed: bool
    safe_command_adapter_allowed: bool
    navigation_warning_ready: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VelocityResponseModelEvaluation:
    model_name: str
    dataset_path: str
    records_count: int
    numeric_records_count: int
    qualitative_only_records_count: int
    evaluated_queries_count: int
    metrics: dict[str, Any]
    limitations: list[str]


def load_velocity_response_dataset(path: str | Path) -> dict[str, Any]:
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)
    if not isinstance(dataset, dict):
        raise ValueError(f"Velocity response dataset must be a JSON object: {dataset_path}")
    return dataset


def extract_velocity_response_records(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    records = dataset.get("records")
    if not isinstance(records, list):
        raise ValueError("Velocity response dataset must contain a records list.")
    result: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Velocity response dataset record {index} is not an object.")
        result.append(record)
    return result


class VelocityResponseModel:
    def __init__(self, dataset: dict[str, Any], records: list[dict[str, Any]]) -> None:
        self.dataset = dataset
        self.records = sorted(records, key=lambda item: float(item["vx_cmd_mps"]))
        self.numeric_records = [
            record for record in self.records if isinstance(record.get("vx_actual_mps_mean"), int | float)
        ]
        self.qualitative_only_records = [
            record for record in self.records if not isinstance(record.get("vx_actual_mps_mean"), int | float)
        ]

    @classmethod
    def from_dataset(cls, dataset: dict[str, Any]) -> "VelocityResponseModel":
        return cls(dataset, extract_velocity_response_records(dataset))

    def predict(
        self,
        query_vx_cmd_mps: float,
        model_name: str = "uncertainty_aware_hybrid_v1",
    ) -> VelocityResponsePrediction:
        if model_name == "uncertainty_aware_hybrid_v1":
            return self._predict_hybrid(query_vx_cmd_mps)
        if model_name == "nearest_lookup_baseline_v1":
            return self._predict_nearest_lookup(query_vx_cmd_mps)
        if model_name == "naive_global_gain_baseline_v1":
            return self._predict_global_gain(query_vx_cmd_mps)
        if model_name == "piecewise_linear_baseline_v1":
            return self._predict_piecewise_linear(query_vx_cmd_mps)
        raise ValueError(f"Unsupported velocity response model: {model_name}")

    def predict_many(
        self,
        query_vx_cmds_mps: list[float],
        model_name: str = "uncertainty_aware_hybrid_v1",
    ) -> list[VelocityResponsePrediction]:
        return [self.predict(query, model_name=model_name) for query in query_vx_cmds_mps]

    def evaluate_on_dataset(self) -> VelocityResponseModelEvaluation:
        numeric_errors: list[float] = []
        for record in self.numeric_records:
            query = float(record["vx_cmd_mps"])
            prediction = self.predict(query)
            actual = float(record["vx_actual_mps_mean"])
            if prediction.predicted_vx_actual_mps is not None:
                numeric_errors.append(abs(prediction.predicted_vx_actual_mps - actual))

        metrics: dict[str, Any] = {
            "available_metrics": [
                "exact_source_reconstruction_absolute_error_sanity_check"
            ],
            "unavailable_metrics": [
                "generalization_error",
                "cross_validation_error",
                "calibrated_uncertainty_error",
                "navigation_risk_reduction",
            ],
            "numeric_error_evaluation_possible": bool(numeric_errors),
            "exact_source_reconstruction_only": True,
            "superiority_claim_supported": False,
            "publication_readiness_claim_supported": False,
        }
        if numeric_errors:
            metrics["exact_source_reconstruction_absolute_error_mean"] = sum(numeric_errors) / len(
                numeric_errors
            )
            metrics["exact_source_reconstruction_absolute_error_max"] = max(numeric_errors)

        return VelocityResponseModelEvaluation(
            model_name="uncertainty_aware_hybrid_v1",
            dataset_path=str(self.dataset.get("dataset_path", "outputs/research_datasets/velocity_response_dataset_v1.json")),
            records_count=len(self.records),
            numeric_records_count=len(self.numeric_records),
            qualitative_only_records_count=len(self.qualitative_only_records),
            evaluated_queries_count=len(self.records),
            metrics=metrics,
            limitations=_model_limitations(self.dataset),
        )

    def _predict_hybrid(self, query: float) -> VelocityResponsePrediction:
        exact = self._exact_record(query)
        if exact is not None:
            if _has_numeric_response(exact):
                return self._prediction(
                    query,
                    "uncertainty_aware_hybrid_v1",
                    "exact_numeric_source",
                    float(exact["vx_actual_mps_mean"]),
                    _label(exact),
                    "medium",
                    _normalized_confidence(exact.get("confidence_label"), default="medium"),
                    [record_id(exact)],
                    [float(exact["vx_cmd_mps"])],
                    False,
                    False,
                    ["Exact source reconstruction is a structural sanity check, not performance evidence."],
                    {"source_confidence_label": exact.get("confidence_label")},
                )
            return self._prediction(
                query,
                "uncertainty_aware_hybrid_v1",
                "exact_qualitative_source",
                None,
                _label(exact),
                "high",
                "low",
                [record_id(exact)],
                [float(exact["vx_cmd_mps"])],
                False,
                False,
                ["No numeric actual velocity is available for this command point."],
                {"source_confidence_label": exact.get("confidence_label")},
            )

        lower, upper = self._bracketing_records(query, self.records)
        if lower is None or upper is None:
            nearest = self._nearest_records(query, count=1)
            return self._prediction(
                query,
                "uncertainty_aware_hybrid_v1",
                "out_of_range_conservative",
                None,
                _label(nearest[0]) if nearest else None,
                "high",
                "low",
                [record_id(item) for item in nearest],
                [float(item["vx_cmd_mps"]) for item in nearest],
                False,
                True,
                ["Out-of-range prediction is unsupported by Measurement v0 data."],
                {},
            )

        if _has_numeric_response(lower) and _has_numeric_response(upper):
            predicted = _linear_interpolate(
                query,
                float(lower["vx_cmd_mps"]),
                float(lower["vx_actual_mps_mean"]),
                float(upper["vx_cmd_mps"]),
                float(upper["vx_actual_mps_mean"]),
            )
            return self._prediction(
                query,
                "uncertainty_aware_hybrid_v1",
                "bounded_interpolation",
                predicted,
                _label(upper),
                "medium_high",
                "medium",
                [record_id(lower), record_id(upper)],
                [float(lower["vx_cmd_mps"]), float(upper["vx_cmd_mps"])],
                True,
                False,
                ["Interpolation is based on sparse Measurement v0 data."],
                {},
            )

        nearest = self._nearest_records(query, count=2)
        return self._prediction(
            query,
            "uncertainty_aware_hybrid_v1",
            "nearest_mixed_evidence",
            None,
            _label(nearest[0]) if nearest else None,
            "high",
            "low",
            [record_id(item) for item in nearest],
            [float(item["vx_cmd_mps"]) for item in nearest],
            False,
            False,
            ["Mixed qualitative/numeric evidence does not support numeric interpolation."],
            {},
        )

    def _predict_nearest_lookup(self, query: float) -> VelocityResponsePrediction:
        nearest = self._nearest_records(query, count=1)
        if not nearest:
            return self._unsupported_prediction(query, "nearest_lookup_baseline_v1")
        record = nearest[0]
        return self._prediction(
            query,
            "nearest_lookup_baseline_v1",
            "nearest_lookup_numeric" if _has_numeric_response(record) else "nearest_lookup_qualitative",
            float(record["vx_actual_mps_mean"]) if _has_numeric_response(record) else None,
            _label(record),
            "high",
            "low",
            [record_id(record)],
            [float(record["vx_cmd_mps"])],
            False,
            False,
            ["Nearest lookup is discontinuous and only reports nearest source evidence."],
            {},
        )

    def _predict_global_gain(self, query: float) -> VelocityResponsePrediction:
        usable = [
            record for record in self.numeric_records if float(record.get("vx_cmd_mps", 0)) > 0
        ]
        if len(usable) < 2:
            return self._unsupported_prediction(query, "naive_global_gain_baseline_v1")
        gains = [float(record["vx_actual_mps_mean"]) / float(record["vx_cmd_mps"]) for record in usable]
        gain = sum(gains) / len(gains)
        nearest = self._nearest_records(query, count=2)
        return self._prediction(
            query,
            "naive_global_gain_baseline_v1",
            "global_gain_numeric_baseline",
            gain * query,
            None,
            "high",
            "low",
            [record_id(item) for item in usable],
            [float(item["vx_cmd_mps"]) for item in nearest],
            False,
            query < min(float(item["vx_cmd_mps"]) for item in usable)
            or query > max(float(item["vx_cmd_mps"]) for item in usable),
            ["Global gain baseline ignores deadzone, environment, sparse data, and uncertainty."],
            {"global_gain": gain, "numeric_records_used": len(usable)},
        )

    def _predict_piecewise_linear(self, query: float) -> VelocityResponsePrediction:
        exact = self._exact_record(query)
        if exact is not None and _has_numeric_response(exact):
            return self._prediction(
                query,
                "piecewise_linear_baseline_v1",
                "exact_numeric_source",
                float(exact["vx_actual_mps_mean"]),
                _label(exact),
                "medium",
                "medium",
                [record_id(exact)],
                [float(exact["vx_cmd_mps"])],
                False,
                False,
                ["Exact source reconstruction is not model performance evidence."],
                {},
            )
        lower, upper = self._bracketing_records(query, self.numeric_records)
        if lower is None or upper is None:
            return self._prediction(
                query,
                "piecewise_linear_baseline_v1",
                "piecewise_out_of_range_unavailable",
                None,
                None,
                "high",
                "low",
                [],
                [],
                False,
                True,
                ["Piecewise linear baseline does not extrapolate outside numeric source range."],
                {},
            )
        predicted = _linear_interpolate(
            query,
            float(lower["vx_cmd_mps"]),
            float(lower["vx_actual_mps_mean"]),
            float(upper["vx_cmd_mps"]),
            float(upper["vx_actual_mps_mean"]),
        )
        return self._prediction(
            query,
            "piecewise_linear_baseline_v1",
            "piecewise_linear_interpolation",
            predicted,
            _label(upper),
            "medium_high",
            "medium",
            [record_id(lower), record_id(upper)],
            [float(lower["vx_cmd_mps"]), float(upper["vx_cmd_mps"])],
            True,
            False,
            ["Piecewise linear baseline depends on sparse numeric source records."],
            {},
        )

    def _exact_record(self, query: float) -> dict[str, Any] | None:
        for record in self.records:
            if abs(float(record["vx_cmd_mps"]) - query) < 1e-9:
                return record
        return None

    def _bracketing_records(
        self, query: float, records: list[dict[str, Any]]
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        lower = None
        upper = None
        for record in records:
            vx_cmd = float(record["vx_cmd_mps"])
            if vx_cmd < query:
                lower = record
            elif vx_cmd > query and upper is None:
                upper = record
                break
        return lower, upper

    def _nearest_records(self, query: float, count: int) -> list[dict[str, Any]]:
        return sorted(
            self.records,
            key=lambda record: (abs(float(record["vx_cmd_mps"]) - query), float(record["vx_cmd_mps"])),
        )[:count]

    def _unsupported_prediction(self, query: float, model_name: str) -> VelocityResponsePrediction:
        return self._prediction(
            query,
            model_name,
            "unsupported",
            None,
            None,
            "high",
            "unknown",
            [],
            [],
            False,
            False,
            ["Insufficient numeric source records for this baseline."],
            {},
        )

    def _prediction(
        self,
        query: float,
        model_name: str,
        prediction_type: str,
        predicted: float | None,
        qualitative_label: str | None,
        uncertainty_label: str,
        confidence_label: str,
        source_record_ids: list[str],
        nearest_points: list[float],
        interpolation_used: bool,
        extrapolation_used: bool,
        limitations: list[str],
        metadata: dict[str, Any],
    ) -> VelocityResponsePrediction:
        base_limitations = _model_limitations(self.dataset)
        return VelocityResponsePrediction(
            query_vx_cmd_mps=query,
            model_name=model_name,
            prediction_type=prediction_type,
            predicted_vx_actual_mps=predicted,
            qualitative_response_label=qualitative_label,
            uncertainty_label=uncertainty_label,
            confidence_label=confidence_label,
            source_record_ids=source_record_ids,
            nearest_command_points_mps=nearest_points,
            interpolation_used=interpolation_used,
            extrapolation_used=extrapolation_used,
            limitations=sorted(dict.fromkeys(limitations + base_limitations)),
            compensation_allowed=False,
            safe_command_adapter_allowed=False,
            navigation_warning_ready=bool(self.dataset.get("navigation_warning_ready", True)),
            metadata=metadata,
        )


def prediction_to_dict(prediction: VelocityResponsePrediction) -> dict[str, Any]:
    return asdict(prediction)


def evaluation_to_dict(evaluation: VelocityResponseModelEvaluation) -> dict[str, Any]:
    return asdict(evaluation)


def record_id(record: dict[str, Any]) -> str:
    return str(record.get("record_id") or record.get("trial_id") or "unknown_record")


def _has_numeric_response(record: dict[str, Any]) -> bool:
    return isinstance(record.get("vx_actual_mps_mean"), int | float)


def _label(record: dict[str, Any]) -> str | None:
    label = record.get("qualitative_response_label")
    return str(label) if isinstance(label, str) else None


def _linear_interpolate(query: float, x0: float, y0: float, x1: float, y1: float) -> float:
    if abs(x1 - x0) < 1e-12:
        return y0
    ratio = (query - x0) / (x1 - x0)
    return y0 + ratio * (y1 - y0)


def _normalized_confidence(value: Any, default: str) -> str:
    if isinstance(value, str) and "low" in value:
        return "low"
    if isinstance(value, str) and "medium" in value:
        return "medium"
    if isinstance(value, str) and "high" in value:
        return "high"
    return default


def _model_limitations(dataset: dict[str, Any]) -> list[str]:
    values = dataset.get("limitations", [])
    limitations = [str(item) for item in values] if isinstance(values, list) else []
    limitations.extend(
        [
            "uncertainty_and_confidence_are_labels_not_calibrated_probabilities",
            "no_compensation_or_safe_command_adapter_authority",
        ]
    )
    return sorted(dict.fromkeys(limitations))
