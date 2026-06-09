"""Project-specific validation helpers for velocity response research records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_DISALLOWED_FIELDS = {
    "remote_controller_state",
    "hand_controller_state",
    "unconfirmed_ros2_topic",
}

DEFAULT_REQUIRED_RECORD_FIELDS = {
    "vx_cmd_mps",
    "measurement_source",
    "localization_source",
    "environment_label",
}

DEFAULT_EITHER_OR_GROUPS = (
    ("robot_model", "robot_id"),
    ("vx_actual_mps_mean", "qualitative_response_label"),
    ("confidence_label", "confidence_score"),
    ("trial_count", "sample_count"),
)

REQUIRED_SCHEMA_SECTIONS = {
    "schema_version",
    "dataset_id",
    "created_at",
    "research_problem",
    "robot",
    "environment",
    "acquisition",
    "command_grid",
    "trials",
    "quality",
    "downstream_boundaries",
}


def load_velocity_response_schema(path: str | Path) -> dict[str, Any]:
    schema_path = Path(path)
    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {schema_path}")
    return schema


def validate_velocity_response_schema(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = schema.get("required")
    properties = schema.get("properties")

    if not isinstance(required, list):
        errors.append("Schema root must define a required field list.")
    if not isinstance(properties, dict):
        errors.append("Schema root must define a properties object.")

    if isinstance(required, list):
        missing_required = sorted(REQUIRED_SCHEMA_SECTIONS.difference(required))
        if missing_required:
            errors.append(
                "Schema root required list is missing section(s): "
                + ", ".join(missing_required)
            )

    if isinstance(properties, dict):
        missing_properties = sorted(REQUIRED_SCHEMA_SECTIONS.difference(properties))
        if missing_properties:
            errors.append(
                "Schema root properties are missing section(s): "
                + ", ".join(missing_properties)
            )

    disallowed = get_disallowed_fields(schema)
    missing_disallowed = sorted(DEFAULT_DISALLOWED_FIELDS.difference(disallowed))
    if missing_disallowed:
        errors.append(
            "Schema validation metadata must disallow field(s): "
            + ", ".join(missing_disallowed)
        )

    battery_required_paths = _find_required_field_paths(schema, "battery_state")
    if battery_required_paths:
        errors.append(
            "battery_state must remain optional; found required reference at "
            + ", ".join(battery_required_paths)
        )

    return errors


def validate_velocity_response_record(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not isinstance(record, dict):
        return ["Velocity response record must be a JSON object."]

    for field_path, field_name in _iter_disallowed_record_fields(
        record,
        get_disallowed_fields(schema),
    ):
        errors.append(f"Disallowed field '{field_name}' found at {field_path}.")

    for field_name in _get_required_record_fields(schema):
        if field_name not in record:
            errors.append(f"Missing required record field: {field_name}.")

    for group in _get_either_or_groups(schema):
        if not any(field in record for field in group):
            errors.append(
                "Missing required alternative field group: one of "
                + ", ".join(group)
                + "."
            )

    false_only_fields = _get_false_only_fields(schema)
    for field_name in sorted(false_only_fields):
        if field_name in record and record[field_name] is not False:
            errors.append(f"Field {field_name} must be false when present.")

    return errors


def assert_velocity_response_record_valid(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> None:
    errors = validate_velocity_response_record(record, schema)
    if errors:
        raise ValueError("; ".join(errors))


def get_disallowed_fields(schema: dict[str, Any]) -> set[str]:
    metadata = schema.get("x_project_validation", {})
    if not isinstance(metadata, dict):
        return set(DEFAULT_DISALLOWED_FIELDS)

    disallowed = metadata.get("disallowed_fields", [])
    if not isinstance(disallowed, list):
        return set(DEFAULT_DISALLOWED_FIELDS)

    return {str(field) for field in disallowed}.union(DEFAULT_DISALLOWED_FIELDS)


def _get_required_record_fields(schema: dict[str, Any]) -> set[str]:
    metadata = schema.get("x_project_validation", {})
    if isinstance(metadata, dict):
        fields = metadata.get("minimum_viable_record_fields")
        if isinstance(fields, list):
            return {str(field) for field in fields}
    return set(DEFAULT_REQUIRED_RECORD_FIELDS)


def _get_either_or_groups(schema: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    metadata = schema.get("x_project_validation", {})
    if isinstance(metadata, dict):
        groups = metadata.get("either_or_field_groups")
        if isinstance(groups, list):
            parsed_groups: list[tuple[str, ...]] = []
            for group in groups:
                if isinstance(group, list) and group:
                    parsed_groups.append(tuple(str(field) for field in group))
            if parsed_groups:
                return tuple(parsed_groups)
    return DEFAULT_EITHER_OR_GROUPS


def _get_false_only_fields(schema: dict[str, Any]) -> set[str]:
    metadata = schema.get("x_project_validation", {})
    if isinstance(metadata, dict):
        fields = metadata.get("false_only_record_fields")
        if isinstance(fields, list):
            return {str(field) for field in fields}
    return set()


def _iter_disallowed_record_fields(
    value: Any,
    disallowed_fields: set[str],
    path: str = "<root>",
) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path != "<root>" else key
            if key in disallowed_fields:
                found.append((child_path, key))
            found.extend(_iter_disallowed_record_fields(child, disallowed_fields, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_iter_disallowed_record_fields(child, disallowed_fields, f"{path}[{index}]"))
    return found


def _find_required_field_paths(
    value: Any,
    field_name: str,
    path: str = "<root>",
) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        required = value.get("required")
        if isinstance(required, list) and field_name in required:
            paths.append(f"{path}.required")
        for key, child in value.items():
            child_path = f"{path}.{key}" if path != "<root>" else key
            paths.extend(_find_required_field_paths(child, field_name, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_find_required_field_paths(child, field_name, f"{path}[{index}]"))
    return paths
