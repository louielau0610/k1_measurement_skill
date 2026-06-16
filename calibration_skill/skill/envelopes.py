"""Skill request and response envelope helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import RobotPlatform, SkillOperationStatus
from calibration_skill.domain.errors import DomainError
from calibration_skill.schemas.registry import CURRENT_SCHEMA_VERSION


@dataclass(frozen=True)
class SkillRequestEnvelope:
    schema_version: str
    request_id: str
    operation: str
    platform: RobotPlatform
    dry_run: bool
    robot_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    issued_at: str | None = None
    caller_metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillRequestEnvelope":
        return cls(
            schema_version=data.get("schema_version", ""),
            request_id=data.get("request_id", ""),
            operation=data.get("operation", ""),
            platform=RobotPlatform(data.get("platform", "")),
            dry_run=bool(data.get("dry_run", False)),
            robot_id=data.get("robot_id"),
            payload=data.get("payload") or {},
            issued_at=data.get("issued_at"),
            caller_metadata=data.get("caller_metadata") or {},
        )


def response_envelope(
    request_id: str,
    operation: str,
    status: SkillOperationStatus,
    *,
    result: dict[str, Any] | None = None,
    error: DomainError | None = None,
    warnings: tuple[str, ...] = (),
    audit_reference: str | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "request_id": request_id,
        "operation": operation,
        "status": status.value,
        "warnings": list(warnings),
    }
    if result is not None:
        response["result"] = result
    if error is not None:
        response["error"] = error.to_dict()
    if audit_reference is not None:
        response["audit_reference"] = audit_reference
    return response
