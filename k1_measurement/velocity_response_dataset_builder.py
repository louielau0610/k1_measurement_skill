"""Build velocity response research datasets from Measurement v0 artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from k1_measurement.research_dataset_schema import (
    load_velocity_response_schema,
    validate_velocity_response_record,
    validate_velocity_response_schema,
)


PROFILE_FILE = "real_k1_velocity_profile_v0.json"
SUMMARY_FILE = "forward_velocity_transition_summary_v0.json"
TRIALS_CSV_FILE = "forward_velocity_transition_trials_v0.csv"
MEASUREMENT_CLOSURE_FILE = "measurement_v0_closure_summary.json"


def load_measurement_v0_artifacts(root: str | Path) -> dict[str, Any]:
    measurement_root = Path(root)
    if not measurement_root.exists():
        raise FileNotFoundError(f"Measurement v0 root not found: {measurement_root}")
    if not measurement_root.is_dir():
        raise NotADirectoryError(f"Measurement v0 root is not a directory: {measurement_root}")

    artifacts: dict[str, Any] = {
        "root": str(measurement_root),
        "source_artifacts_used": [],
        "source_artifacts_missing": [],
    }

    for key, filename in (
        ("profile", PROFILE_FILE),
        ("summary", SUMMARY_FILE),
        ("closure", MEASUREMENT_CLOSURE_FILE),
    ):
        path = measurement_root / filename
        if path.exists():
            artifacts[key] = _load_json(path)
            artifacts["source_artifacts_used"].append(str(path))
        else:
            artifacts["source_artifacts_missing"].append(str(path))

    csv_path = measurement_root / TRIALS_CSV_FILE
    if csv_path.exists():
        artifacts["trials_csv"] = _load_csv(csv_path)
        artifacts["source_artifacts_used"].append(str(csv_path))
    else:
        artifacts["source_artifacts_missing"].append(str(csv_path))

    if "profile" not in artifacts and "summary" not in artifacts:
        raise FileNotFoundError(
            "Measurement v0 root must contain real_k1_velocity_profile_v0.json "
            "or forward_velocity_transition_summary_v0.json."
        )

    return artifacts


def build_velocity_response_dataset_v1(
    measurement_root: str | Path,
    schema_path: str | Path,
) -> dict[str, Any]:
    schema = load_velocity_response_schema(schema_path)
    artifacts = load_measurement_v0_artifacts(measurement_root)
    profile = artifacts.get("profile", {})
    summary = artifacts.get("summary", {})
    closure = artifacts.get("closure", {})

    source_date = _first_string(
        profile.get("source", {}).get("date") if isinstance(profile, dict) else None,
        summary.get("metadata", {}).get("date") if isinstance(summary, dict) else None,
        closure.get("date") if isinstance(closure, dict) else None,
        "UNKNOWN_SOURCE_DATE",
    )
    environment = _environment_from_sources(profile, summary)
    platform = _first_string(
        profile.get("platform") if isinstance(profile, dict) else None,
        summary.get("metadata", {}).get("platform") if isinstance(summary, dict) else None,
        "Booster K1",
    )
    limitations = _collect_limitations(profile, summary)
    downstream = _downstream_flags(profile, closure)
    records = _build_records(profile, summary, artifacts, platform, environment)

    dataset = {
        "schema_version": "velocity_response_dataset_v1",
        "dataset_id": "measurement_v0_velocity_response_dataset_v1",
        "created_at": f"{source_date}T00:00:00Z" if _is_date(source_date) else source_date,
        "dataset_role": "research_dataset_constructed_from_measurement_v0",
        "measurement_source": str(Path(measurement_root)),
        "source_schema": str(schema_path),
        "robot_model": platform,
        "environment_label": environment["label"],
        "localization_source": _localization_source(profile, summary),
        "records_count": len(records),
        "records": records,
        "source_artifacts_used": artifacts["source_artifacts_used"],
        "source_artifacts_missing": artifacts["source_artifacts_missing"],
        "direct_fields_populated": [
            "robot_model",
            "vx_cmd_mps",
            "measurement_source",
            "environment_label",
            "duration_s",
            "trial_id",
        ],
        "derived_fields_populated": [
            "created_at",
            "records_count",
            "trial_count",
            "localization_source",
        ],
        "qualitative_fields_populated": [
            "qualitative_response_label",
            "confidence_label",
            "limitations",
        ],
        "unavailable_fields": [
            "battery_state",
            "confidence_score",
            "sample_count",
            "vx_actual_mps_std",
            "vy_actual_mps_mean",
            "vy_actual_mps_std",
            "wz_actual_radps_mean",
            "wz_actual_radps_std",
            "tracking_error_mps",
            "lateral_drift_m",
            "response_delay_s",
            "stop_distance_m",
        ],
        "limitations": limitations,
        "fabricated_values": False,
        "compensation_ready": False,
        "inverse_command_mapping_ready": False,
        "navigation_control_ready": False,
        "safe_command_adapter_ready": False,
        "navigation_warning_ready": downstream["navigation_warning_ready"],
        "m15_readiness": {
            "baseline_response_models_ready": True,
            "requires_repeated_trials_for_uncertainty": True,
            "must_respect_single_session_limit": True,
        },
    }
    validate_built_dataset(dataset, schema)
    return dataset


def build_future_trial_template(schema_path: str | Path) -> dict[str, Any]:
    schema = load_velocity_response_schema(schema_path)
    template = {
        "schema_version": "velocity_response_future_trial_template_v1",
        "dataset_id": "TO_BE_FILLED_BY_FUTURE_TRIAL",
        "measurement_source": "TO_BE_FILLED_BY_FUTURE_TRIAL",
        "robot_model": "Booster K1",
        "environment_label": "TO_BE_FILLED_BY_FUTURE_TRIAL",
        "localization_source": "TO_BE_FILLED_BY_FUTURE_TRIAL",
        "records": [
            {
                "record_id": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "trial_id": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "robot_model": "Booster K1",
                "vx_cmd_mps": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "vy_cmd_mps": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "wz_cmd_radps": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "vx_actual_mps_mean": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "vx_actual_mps_std": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "vy_actual_mps_mean": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "vy_actual_mps_std": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "wz_actual_radps_mean": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "wz_actual_radps_std": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "tracking_error_mps": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "lateral_drift_m": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "yaw_drift_rad": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "response_delay_s": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "stop_distance_m": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "qualitative_response_label": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "measurement_source": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "localization_source": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "environment_label": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "confidence_label": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "trial_count": "TO_BE_FILLED_BY_FUTURE_TRIAL",
                "battery_state": "TO_BE_FILLED_BY_FUTURE_TRIAL_OPTIONAL",
                "compensation_ready": False,
                "inverse_command_mapping_ready": False,
                "navigation_control_ready": False,
                "safe_command_adapter_ready": False,
            }
        ],
        "template_only": True,
        "measured_data": False,
    }
    validate_built_dataset(template, schema)
    return template


def validate_built_dataset(
    dataset: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors = validate_velocity_response_schema(schema)
    errors.extend(validate_velocity_response_record(dataset, schema))
    return errors


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")


def build_validation_report(
    dataset: dict[str, Any],
    validation_errors: list[str],
    dataset_path: str | Path,
    schema_path: str | Path,
    source_measurement_root: str | Path,
) -> dict[str, Any]:
    return {
        "milestone": "M14",
        "dataset_path": str(dataset_path),
        "schema_path": str(schema_path),
        "source_measurement_root": str(source_measurement_root),
        "records_count": dataset.get("records_count", 0),
        "validation_passed": not validation_errors,
        "validation_errors": validation_errors,
        "source_artifacts_used": dataset.get("source_artifacts_used", []),
        "source_artifacts_missing": dataset.get("source_artifacts_missing", []),
        "direct_fields_populated": dataset.get("direct_fields_populated", []),
        "derived_fields_populated": dataset.get("derived_fields_populated", []),
        "qualitative_fields_populated": dataset.get("qualitative_fields_populated", []),
        "unavailable_fields": dataset.get("unavailable_fields", []),
        "fabricated_values": False,
        "compensation_ready": False,
        "safe_command_adapter_ready": False,
        "navigation_warning_ready": True,
        "limitations": dataset.get("limitations", []),
        "m15_readiness": dataset.get("m15_readiness", {}),
    }


def _build_records(
    profile: dict[str, Any],
    summary: dict[str, Any],
    artifacts: dict[str, Any],
    platform: str,
    environment: dict[str, str],
) -> list[dict[str, Any]]:
    profile_points = profile.get("trial_points", []) if isinstance(profile, dict) else []
    summary_trials = summary.get("analyzed_trials", []) if isinstance(summary, dict) else []
    summary_by_id = {
        str(trial.get("trial_id")): trial
        for trial in summary_trials
        if isinstance(trial, dict) and trial.get("trial_id")
    }
    csv_by_id = {
        str(row.get("trial_id")): row
        for row in artifacts.get("trials_csv", [])
        if isinstance(row, dict) and row.get("trial_id")
    }

    records: list[dict[str, Any]] = []
    for point in sorted(profile_points, key=lambda item: (item.get("vx_cmd_mps", 0), item.get("trial_id", ""))):
        if not isinstance(point, dict):
            continue
        trial_id = str(point.get("trial_id", "unknown_trial"))
        summary_trial = summary_by_id.get(trial_id, {})
        csv_trial = csv_by_id.get(trial_id, {})
        vx_cmd = point.get("vx_cmd_mps")
        record = {
            "record_id": f"measurement_v0_{trial_id}",
            "trial_id": trial_id,
            "robot_model": platform,
            "vx_cmd_mps": vx_cmd,
            "qualitative_response_label": _first_string(
                point.get("interpretation"),
                summary_trial.get("interpretation"),
                csv_trial.get("interpretation"),
                point.get("tracking_category"),
                "measurement_v0_qualitative_response",
            ),
            "measurement_source": "outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json",
            "localization_source": _localization_source(profile, summary),
            "environment_label": environment["label"],
            "confidence_label": _confidence_label(point, summary_trial),
            "trial_count": 1,
            "source_provenance": {
                "profile_json": "outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json",
                "summary_json": "outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json",
                "trials_csv": "outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.csv",
            },
            "field_categories": {
                "direct": ["trial_id", "vx_cmd_mps", "duration_s", "tracking_category"],
                "derived": ["trial_count", "confidence_label"],
                "qualitative": ["qualitative_response_label"],
                "unavailable": [],
            },
            "compensation_ready": False,
            "inverse_command_mapping_ready": False,
            "navigation_control_ready": False,
            "safe_command_adapter_ready": False,
        }
        for source_key, record_key in (
            ("duration_s", "duration_s"),
            ("distance_m", "distance_m"),
            ("v_actual_est_mps", "vx_actual_mps_mean"),
            ("speed_gain_est", "speed_gain_est"),
            ("dtheta_rad", "yaw_drift_rad"),
        ):
            value = point.get(source_key)
            if isinstance(value, int | float):
                record[record_key] = value
                if record_key != "duration_s":
                    record["field_categories"]["derived"].append(record_key)

        if "vx_actual_mps_mean" not in record:
            record["field_categories"]["unavailable"].append("vx_actual_mps_mean")
        if "yaw_drift_rad" not in record:
            record["field_categories"]["unavailable"].append("yaw_drift_rad")
        records.append(record)
    return records


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _environment_from_sources(profile: dict[str, Any], summary: dict[str, Any]) -> dict[str, str]:
    env = profile.get("environment", {}) if isinstance(profile, dict) else {}
    if not env and isinstance(summary, dict):
        env = summary.get("metadata", {}).get("environment", {})
    floor = _first_string(env.get("floor_type") if isinstance(env, dict) else None, "unknown_floor")
    condition = _first_string(env.get("condition") if isinstance(env, dict) else None, "unknown_condition")
    return {"floor_type": floor, "condition": condition, "label": f"{floor}_{condition}"}


def _localization_source(profile: dict[str, Any], summary: dict[str, Any]) -> str:
    topics = profile.get("measurement_topics", {}) if isinstance(profile, dict) else {}
    odometer = topics.get("odometer", {}) if isinstance(topics, dict) else {}
    if odometer.get("topic"):
        return "odometer_primary_no_external_ground_truth"
    scope = summary.get("metadata", {}).get("measurement_scope", {}) if isinstance(summary, dict) else {}
    required_topics = scope.get("required_topics", {}) if isinstance(scope, dict) else {}
    if "odometer" in required_topics:
        return "odometer_primary_no_external_ground_truth"
    return "unknown_localization_source"


def _collect_limitations(profile: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for source in (profile, summary):
        limitations = source.get("limitations", []) if isinstance(source, dict) else []
        if isinstance(limitations, list):
            values.extend(str(item) for item in limitations)
    values.extend(
        [
            "no_compensation_readiness_inferred",
            "no_safe_command_adapter_readiness_inferred",
            "missing_response_dimensions_not_fabricated",
        ]
    )
    return sorted(dict.fromkeys(values))


def _downstream_flags(profile: dict[str, Any], closure: dict[str, Any]) -> dict[str, bool]:
    downstream = profile.get("downstream_usage", {}) if isinstance(profile, dict) else {}
    status = closure.get("status", {}) if isinstance(closure, dict) else {}
    return {
        "compensation_ready": False,
        "safe_command_adapter_ready": False,
        "navigation_warning_ready": bool(
            downstream.get("navigation_warning_ready", status.get("navigation_warning_ready", True))
        ),
    }


def _confidence_label(point: dict[str, Any], summary_trial: dict[str, Any]) -> str:
    interpretation = str(point.get("interpretation") or summary_trial.get("interpretation") or "")
    if "deadzone" in interpretation or "ineffective" in interpretation:
        return "qualitative_only_no_numeric_velocity"
    if "repeat" in interpretation or point.get("requires_repeat_due_to_yaw_drift"):
        return "repeat_required"
    return "single_session_single_trial_low_confidence"


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return ""


def _is_date(value: str) -> bool:
    parts = value.split("-")
    return len(parts) == 3 and all(part.isdigit() for part in parts)
