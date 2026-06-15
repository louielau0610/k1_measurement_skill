"""Safety domain contracts: safety envelope, operator authorization, preflight."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import (
    CoordinateFrame,
    PreflightStatus,
    RobotPlatform,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_INVALID_DURATION,
    ERROR_INVALID_FRAME,
    ERROR_INVALID_SAFETY_POLICY,
    ERROR_INVALID_TIMEOUT,
    ERROR_NON_FINITE_VALUE,
    ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
    ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
    validation_error,
)


def _require_finite(value: float, name: str) -> list[str]:
    errors: list[str] = []
    if math.isnan(value):
        errors.append(f"{name} is NaN")
    if math.isinf(value):
        errors.append(f"{name} is infinite")
    return errors


def _require_non_negative_finite(value: float, name: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_finite(value, name))
    if value < 0:
        errors.append(f"{name} must be non-negative, got {value}")
    return errors


def _require_strictly_positive_finite(value: float, name: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_finite(value, name))
    if value <= 0:
        errors.append(f"{name} must be strictly positive, got {value}")
    return errors


@dataclass(frozen=True)
class SafetyEnvelope:
    """Safety envelope for velocity commands. No silent numerical defaults.

    All limits must be explicitly provided and finite.
    """
    policy_id: str
    policy_hash: str
    max_abs_vx_mps: float
    max_abs_vy_mps: float
    max_abs_wz_radps: float
    max_command_duration_s: float
    max_telemetry_age_ms: float
    stop_timeout_s: float
    allowed_command_frames: tuple[CoordinateFrame, ...]
    operator_authorization_required: bool

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.policy_id or not self.policy_id.strip():
            errors.append("policy_id must be non-empty")
        if not self.policy_hash or not self.policy_hash.strip():
            errors.append("policy_hash must be non-empty")
        errors.extend(_require_non_negative_finite(self.max_abs_vx_mps, "max_abs_vx_mps"))
        errors.extend(_require_non_negative_finite(self.max_abs_vy_mps, "max_abs_vy_mps"))
        errors.extend(_require_non_negative_finite(self.max_abs_wz_radps, "max_abs_wz_radps"))
        errors.extend(_require_strictly_positive_finite(self.max_command_duration_s, "max_command_duration_s"))
        errors.extend(_require_strictly_positive_finite(self.max_telemetry_age_ms, "max_telemetry_age_ms"))
        errors.extend(_require_strictly_positive_finite(self.stop_timeout_s, "stop_timeout_s"))
        if not self.allowed_command_frames:
            errors.append("allowed_command_frames must not be empty")
        if errors:
            raise ValueError("; ".join(errors))

    def validate_command(self, command: Any) -> list[DomainError]:
        """Validate a VelocityCommand against this safety envelope. Returns violations, does not clamp."""
        from calibration_skill.domain.motion import VelocityCommand
        if not isinstance(command, VelocityCommand):
            return [validation_error("Expected a VelocityCommand")]

        errors: list[DomainError] = []

        # Velocity bounds
        if abs(command.vx_mps) > self.max_abs_vx_mps:
            errors.append(DomainError(
                code=ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                message=f"|vx|={abs(command.vx_mps):.4f} exceeds max_abs_vx_mps={self.max_abs_vx_mps}",
                retryable=False,
                details={"field": "vx_mps", "value": command.vx_mps, "max": self.max_abs_vx_mps},
            ))
        if abs(command.vy_mps) > self.max_abs_vy_mps:
            errors.append(DomainError(
                code=ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                message=f"|vy|={abs(command.vy_mps):.4f} exceeds max_abs_vy_mps={self.max_abs_vy_mps}",
                retryable=False,
                details={"field": "vy_mps", "value": command.vy_mps, "max": self.max_abs_vy_mps},
            ))
        if abs(command.wz_radps) > self.max_abs_wz_radps:
            errors.append(DomainError(
                code=ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                message=f"|wz|={abs(command.wz_radps):.4f} exceeds max_abs_wz_radps={self.max_abs_wz_radps}",
                retryable=False,
                details={"field": "wz_radps", "value": command.wz_radps, "max": self.max_abs_wz_radps},
            ))

        # Duration
        if command.requested_duration_s > self.max_command_duration_s:
            errors.append(DomainError(
                code=ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                message=f"duration={command.requested_duration_s}s exceeds max={self.max_command_duration_s}s",
                retryable=False,
                details={"field": "requested_duration_s", "value": command.requested_duration_s, "max": self.max_command_duration_s},
            ))

        # Frame
        if command.frame not in self.allowed_command_frames:
            errors.append(DomainError(
                code=ERROR_INVALID_FRAME,
                message=f"frame {command.frame.value} not in allowed frames",
                retryable=False,
                details={"frame": command.frame.value, "allowed": [f.value for f in self.allowed_command_frames]},
            ))

        # Policy matching
        if command.safety_policy_id != self.policy_id:
            errors.append(DomainError(
                code=ERROR_INVALID_SAFETY_POLICY,
                message=f"command safety_policy_id '{command.safety_policy_id}' does not match envelope '{self.policy_id}'",
                retryable=False,
                details={"expected": self.policy_id, "actual": command.safety_policy_id},
            ))
        if command.safety_policy_hash != self.policy_hash:
            errors.append(DomainError(
                code=ERROR_INVALID_SAFETY_POLICY,
                message="command safety_policy_hash does not match envelope",
                retryable=False,
            ))

        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_hash": self.policy_hash,
            "max_abs_vx_mps": self.max_abs_vx_mps,
            "max_abs_vy_mps": self.max_abs_vy_mps,
            "max_abs_wz_radps": self.max_abs_wz_radps,
            "max_command_duration_s": self.max_command_duration_s,
            "max_telemetry_age_ms": self.max_telemetry_age_ms,
            "stop_timeout_s": self.stop_timeout_s,
            "allowed_command_frames": [f.value for f in self.allowed_command_frames],
            "operator_authorization_required": self.operator_authorization_required,
        }


@dataclass(frozen=True)
class OperatorAuthorization:
    """Operator authorization for robot motion operations.

    Expired authorization must never be treated as valid.
    """
    authorization_id: str
    operator_id: str
    platform: RobotPlatform
    robot_id: str
    issued_monotonic_ns: int
    expiry_monotonic_ns: int
    authorized_operations: tuple[str, ...]
    safety_policy_id: str
    safety_policy_hash: str
    evidence_reference: str

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.authorization_id or not self.authorization_id.strip():
            errors.append("authorization_id must be non-empty")
        if not self.operator_id or not self.operator_id.strip():
            errors.append("operator_id must be non-empty")
        if not self.robot_id or not self.robot_id.strip():
            errors.append("robot_id must be non-empty")
        if self.issued_monotonic_ns < 0:
            errors.append(f"issued_monotonic_ns must be non-negative, got {self.issued_monotonic_ns}")
        if self.expiry_monotonic_ns <= self.issued_monotonic_ns:
            errors.append("expiry_monotonic_ns must be strictly greater than issued_monotonic_ns")
        if not self.authorized_operations:
            errors.append("authorized_operations must not be empty")
        if not self.safety_policy_id or not self.safety_policy_id.strip():
            errors.append("safety_policy_id must be non-empty")
        if not self.safety_policy_hash or not self.safety_policy_hash.strip():
            errors.append("safety_policy_hash must be non-empty")
        if errors:
            raise ValueError("; ".join(errors))

    def is_valid(self, now_ns: int) -> bool:
        """Check if authorization is valid at the given monotonic time."""
        return self.issued_monotonic_ns <= now_ns < self.expiry_monotonic_ns

    def is_expired(self, now_ns: int) -> bool:
        """Check if authorization has expired."""
        return now_ns >= self.expiry_monotonic_ns

    def validate(self, now_ns: int) -> list[DomainError]:
        """Validate authorization at the given time."""
        errors: list[DomainError] = []
        if self.is_expired(now_ns):
            errors.append(DomainError(
                code=ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
                message=f"Authorization {self.authorization_id} expired at {self.expiry_monotonic_ns}, now={now_ns}",
                retryable=False,
                details={"authorization_id": self.authorization_id, "expiry_ns": self.expiry_monotonic_ns, "now_ns": now_ns},
            ))
        elif now_ns < self.issued_monotonic_ns:
            errors.append(DomainError(
                code=ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
                message=f"Authorization {self.authorization_id} not yet valid (issued at {self.issued_monotonic_ns}, now={now_ns})",
                retryable=False,
            ))
        return errors

    def check_operation(self, operation: str) -> bool:
        """Check if an operation is authorized."""
        return operation in self.authorized_operations

    def matches_platform(self, platform: RobotPlatform, robot_id: str) -> bool:
        """Check if authorization matches the given platform and robot."""
        return self.platform == platform and self.robot_id == robot_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "operator_id": self.operator_id,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "issued_monotonic_ns": self.issued_monotonic_ns,
            "expiry_monotonic_ns": self.expiry_monotonic_ns,
            "authorized_operations": list(self.authorized_operations),
            "safety_policy_id": self.safety_policy_id,
            "safety_policy_hash": self.safety_policy_hash,
            "evidence_reference": self.evidence_reference,
        }


@dataclass(frozen=True)
class PreflightCheck:
    """A single preflight check result."""
    check_id: str
    name: str
    status: PreflightStatus
    detail: str = ""
    evidence_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.check_id or not self.check_id.strip():
            raise ValueError("check_id must be non-empty")
        if not self.name or not self.name.strip():
            raise ValueError("name must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "check_id": self.check_id,
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
        }
        if self.evidence_ref is not None:
            result["evidence_ref"] = self.evidence_ref
        return result


@dataclass(frozen=True)
class PreflightReport:
    """Preflight report with individual checks, blockers, and warnings.

    Warnings are distinct from blockers.
    A report with blockers cannot be represented as ready.
    """
    platform: RobotPlatform
    robot_id: str
    checked_monotonic_ns: int
    checks: tuple[PreflightCheck, ...] = field(default_factory=tuple)
    safety_policy_ref: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.robot_id or not self.robot_id.strip():
            raise ValueError("robot_id must be non-empty")

    @property
    def blockers(self) -> tuple[PreflightCheck, ...]:
        """Checks that failed (blockers)."""
        return tuple(c for c in self.checks if c.status == PreflightStatus.FAILED)

    @property
    def warnings(self) -> tuple[PreflightCheck, ...]:
        """Checks that produced warnings."""
        return tuple(c for c in self.checks if c.status == PreflightStatus.WARNING)

    @property
    def overall_status(self) -> PreflightStatus:
        """Overall status: failed if any blocker, warning if any warning, passed otherwise."""
        if self.blockers:
            return PreflightStatus.FAILED
        if self.warnings:
            return PreflightStatus.WARNING
        return PreflightStatus.PASSED

    @property
    def is_ready(self) -> bool:
        """A report with blockers cannot be represented as ready."""
        return len(self.blockers) == 0

    @property
    def required_operator_actions(self) -> tuple[str, ...]:
        """Actions the operator must take before proceeding."""
        actions: list[str] = []
        for check in self.blockers:
            actions.append(f"[{check.check_id}] {check.name}: {check.detail}")
        return tuple(actions)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "checked_monotonic_ns": self.checked_monotonic_ns,
            "overall_status": self.overall_status.value,
            "checks": [c.to_dict() for c in self.checks],
            "blocker_count": len(self.blockers),
            "warning_count": len(self.warnings),
            "is_ready": self.is_ready,
            "required_operator_actions": list(self.required_operator_actions),
        }
        if self.safety_policy_ref is not None:
            result["safety_policy_ref"] = self.safety_policy_ref
        if self.evidence_refs:
            result["evidence_refs"] = list(self.evidence_refs)
        return result
