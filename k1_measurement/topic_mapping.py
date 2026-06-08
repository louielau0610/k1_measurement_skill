"""Configurable real K1 topic mapping validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


MAPPING_SECTIONS = ["odom", "imu", "battery", "robot_state", "command"]
REQUIRED_SECTION_KEYS = ["topic", "message_type", "timestamp_field", "required", "confirmed", "notes"]
TBD_VALUES = {"", "TBD", "tbd", None}


def load_topic_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        mapping = yaml.safe_load(file) or {}
    if not isinstance(mapping, dict):
        raise ValueError("topic mapping must be a YAML object")
    return mapping


def is_tbd(value: Any) -> bool:
    return value in TBD_VALUES


def confirmed_topics(mapping: dict[str, Any]) -> list[str]:
    topics: list[str] = []
    for section_name in MAPPING_SECTIONS:
        section = mapping.get(section_name, {})
        if isinstance(section, dict) and section.get("confirmed") is True and not is_tbd(section.get("topic")):
            topics.append(str(section["topic"]))
    return topics


def validate_topic_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    """Validate topic mapping without assuming any real K1 topic names."""

    errors: list[str] = []
    warnings: list[str] = []
    sections: dict[str, Any] = {}

    for section_name in MAPPING_SECTIONS:
        section = mapping.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"{section_name}: section missing or not an object")
            sections[section_name] = {"valid": False, "required": True}
            continue

        required = section.get("required") is True
        section_errors: list[str] = []
        section_warnings: list[str] = []

        for key in REQUIRED_SECTION_KEYS:
            if key not in section:
                section_errors.append(f"missing key {key}")

        if required:
            if is_tbd(section.get("topic")):
                section_errors.append("required topic remains TBD")
            if is_tbd(section.get("message_type")):
                section_errors.append("required message_type remains TBD")
            if is_tbd(section.get("timestamp_field")):
                section_errors.append("required timestamp_field remains TBD")
            if section.get("confirmed") is not True:
                section_errors.append("required section is not confirmed")
        else:
            for key, value in section.items():
                if key != "notes" and is_tbd(value):
                    section_warnings.append(f"optional field {key} remains TBD")

        for key, value in section.items():
            if required and key not in REQUIRED_SECTION_KEYS and is_tbd(value):
                section_warnings.append(f"field {key} remains TBD")

        errors.extend(f"{section_name}: {item}" for item in section_errors)
        warnings.extend(f"{section_name}: {item}" for item in sorted(set(section_warnings)))
        sections[section_name] = {
            "valid": not section_errors,
            "required": required,
            "confirmed": section.get("confirmed") is True,
            "topic": section.get("topic"),
            "message_type": section.get("message_type"),
            "errors": section_errors,
            "warnings": sorted(set(section_warnings)),
        }

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "sections": sections,
        "confirmed_topics": confirmed_topics(mapping),
    }
