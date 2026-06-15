"""JSON Schema Draft 2020-12 validation for calibration skill schemas.

Uses the installed jsonschema library with the referencing registry API
supported in jsonschema >= 4.18. All schemas are resolved offline from
local files — no network fetches.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, SchemaError, ValidationError, validate
from referencing import Registry, Resource

from calibration_skill.domain.errors import (
    DomainError,
    ERROR_SCHEMA_VERSION_UNSUPPORTED,
    ERROR_SERIALIZATION_FAILED,
    ERROR_VALIDATION_FAILED,
)
from calibration_skill.schemas.registry import SCHEMA_REGISTRY, SchemaInfo, get_schema_info

_SCHEMA_DIR = Path(__file__).resolve().parent / "v1"

# Cache for loaded schema resources
_schema_cache: dict[str, dict[str, Any]] = {}
_registry: Registry | None = None


def _load_schema_document(schema_id: str) -> dict[str, Any]:
    """Load a schema document from the v1 directory by its schema_id."""
    info = get_schema_info(schema_id)
    if info is None:
        raise KeyError(f"Unknown schema_id: {schema_id}")
    schema_path = _SCHEMA_DIR / f"{schema_id}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_registry() -> Registry:
    """Build a referencing.Registry with all v1 schemas loaded by their $id."""
    global _registry, _schema_cache
    if _registry is not None:
        return _registry

    resources: list[tuple[str, Resource]] = []
    for schema_file in sorted(_SCHEMA_DIR.glob("*.schema.json")):
        with open(schema_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        schema_id_urn = content.get("$id", "")
        if not schema_id_urn:
            raise ValueError(f"Schema {schema_file.name} missing $id")
        # Cache for later use
        schema_key = schema_file.stem.replace(".schema", "")
        _schema_cache[schema_key] = content
        _schema_cache[schema_id_urn] = content
        resource = Resource.from_contents(content)
        resources.append((schema_id_urn, resource))

    _registry = Registry().with_resources(resources)
    return _registry


def get_schema_document(schema_id: str) -> dict[str, Any]:
    """Get a parsed schema document by schema_id."""
    if schema_id not in _schema_cache:
        _schema_cache[schema_id] = _load_schema_document(schema_id)
    return _schema_cache[schema_id]


def validate_schema_documents() -> dict[str, Any]:
    """Validate all registered schema documents against Draft 2020-12 metaschema.

    Returns a dict with validation results for each schema.
    """
    registry = _build_registry()
    results: dict[str, Any] = {
        "schema_count": 0,
        "valid_count": 0,
        "errors": [],
    }

    for schema_id, info in SCHEMA_REGISTRY.items():
        try:
            schema_doc = get_schema_document(schema_id)
            # Validate the schema itself against Draft 2020-12 metaschema
            Draft202012Validator.check_schema(schema_doc)
            # Also verify we can create a validator with $ref resolution
            validator = Draft202012Validator(schema_doc, registry=registry)
            results["schema_count"] += 1
            results["valid_count"] += 1
        except SchemaError as e:
            results["errors"].append({
                "schema_id": schema_id,
                "error": str(e),
            })

    results["all_valid"] = len(results["errors"]) == 0
    return results


def validate_payload(schema_id: str, payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
    """Validate a payload against a registered schema.

    Returns a dict with validation result and any errors.
    """
    info = get_schema_info(schema_id)
    if info is None:
        return {
            "valid": False,
            "schema_id": schema_id,
            "error": f"Unknown schema_id: {schema_id}",
            "error_code": ERROR_SCHEMA_VERSION_UNSUPPORTED,
        }

    registry = _build_registry()
    schema_doc = get_schema_document(schema_id)

    try:
        validator = Draft202012Validator(schema_doc, registry=registry)
        errors = list(validator.iter_errors(payload))
        if errors:
            return {
                "valid": False,
                "schema_id": schema_id,
                "error_count": len(errors),
                "errors": [_format_validation_error(e) for e in errors],
            }
        return {
            "valid": True,
            "schema_id": schema_id,
        }
    except SchemaError as e:
        return {
            "valid": False,
            "schema_id": schema_id,
            "error": f"Schema error: {e}",
            "error_code": ERROR_SERIALIZATION_FAILED,
        }
    except ValidationError as e:
        return {
            "valid": False,
            "schema_id": schema_id,
            "error_count": 1,
            "errors": [_format_validation_error(e)],
        }


def collect_schema_validation_errors(
    schema_id: str, payload: dict[str, Any] | list[Any]
) -> list[DomainError]:
    """Validate a payload and return a list of DomainError objects.

    Unknown schema IDs return schema_version_unsupported.
    """
    result = validate_payload(schema_id, payload)
    if result.get("valid"):
        return []

    errors: list[DomainError] = []
    error_code = result.get("error_code", ERROR_VALIDATION_FAILED)

    if "errors" in result:
        for err_detail in result["errors"]:
            errors.append(DomainError(
                code=error_code,
                message=err_detail.get("message", "Schema validation failed"),
                retryable=False,
                details={
                    "schema_id": schema_id,
                    "json_path": err_detail.get("path", ""),
                    "schema_path": err_detail.get("schema_path", ""),
                },
            ))
    else:
        errors.append(DomainError(
            code=error_code,
            message=result.get("error", "Schema validation failed"),
            retryable=False,
            details={"schema_id": schema_id},
        ))

    return errors


def _format_validation_error(error: ValidationError) -> dict[str, str]:
    """Format a jsonschema ValidationError into a dict."""
    return {
        "message": error.message,
        "path": " -> ".join(str(p) for p in error.absolute_path),
        "schema_path": " -> ".join(str(p) for p in error.absolute_schema_path),
        "validator": error.validator,
    }


def validate_codec_payload(schema_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a codec-produced payload against its schema.

    This is the primary validation path for ensuring codec output
    conforms to the declared schema.
    """
    return validate_payload(schema_id, payload)


# Schema validation for skill envelopes specifically
def validate_skill_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a skill request envelope."""
    return validate_payload("skill_request", payload)


def validate_skill_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a skill response envelope.

    Enforces that success cannot contain a terminal error,
    and rejected/failed must contain a structured error.
    """
    result = validate_payload("skill_response", payload)
    if not result.get("valid"):
        return result

    # Cross-field invariants beyond what JSON Schema can express
    status = payload.get("status")
    has_error = "error" in payload and payload["error"] is not None
    has_result = "result" in payload and payload["result"] is not None

    if status == "success" and has_error:
        result["valid"] = False
        result["cross_field_error"] = "success response must not contain error"
    elif status in ("rejected", "failed") and not has_error:
        result["valid"] = False
        result["cross_field_error"] = f"{status} response must contain error"

    return result
