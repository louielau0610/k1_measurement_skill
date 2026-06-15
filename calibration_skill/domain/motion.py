"""Motion domain contracts: velocity commands, command receipts, lifecycle."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import (
    ALLOWED_LIFECYCLE_TRANSITIONS,
    CommandDisposition,
    CoordinateFrame,
    MotionLifecycleState,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_INVALID_DURATION,
    ERROR_INVALID_FRAME,
    ERROR_INVALID_SAFETY_POLICY,
    ERROR_INVALID_TIMESTAMP,
    ERROR_NON_FINITE_VALUE,
    validation_error,
)


def _require_finite(value: float, name: str) -> list[str]:
    """Check that a value is finite (not NaN, not ±inf)."""
    errors: list[str] = []
    if math.isnan(value):
        errors.append(f"{name} is NaN")
    if math.isinf(value):
        errors.append(f"{name} is infinite")
    return errors


def _require_positive(value: float, name: str) -> list[str]:
    """Check that a value is strictly positive."""
    errors: list[str] = []
    errors.extend(_require_finite(value, name))
    if value <= 0:
        errors.append(f"{name} must be positive, got {value}")
    return errors


def _require_non_negative(value: float, name: str) -> list[str]:
    """Check that a value is non-negative and finite."""
    errors: list[str] = []
    errors.extend(_require_finite(value, name))
    if value < 0:
        errors.append(f"{name} must be non-negative, got {value}")
    return errors


def _require_non_empty(value: str, name: str) -> list[str]:
    """Check that a string is non-empty."""
    if not value or not value.strip():
        return [f"{name} must be a non-empty string"]
    return []


@dataclass(frozen=True)
class VelocityCommand:
    """Immutable velocity command for a legged robot.

    All fields are explicit. No silent defaults for maximum velocity,
    command duration, or safety policy.
    """
    vx_mps: float
    vy_mps: float
    wz_radps: float
    sequence_id: str
    issued_monotonic_ns: int
    expiry_monotonic_ns: int
    requested_duration_s: float
    frame: CoordinateFrame
    safety_policy_id: str
    safety_policy_hash: str
    source: str

    def __post_init__(self) -> None:
        errors: list[str] = []
        errors.extend(_require_finite(self.vx_mps, "vx_mps"))
        errors.extend(_require_finite(self.vy_mps, "vy_mps"))
        errors.extend(_require_finite(self.wz_radps, "wz_radps"))
        errors.extend(_require_non_empty(self.sequence_id, "sequence_id"))
        errors.extend(_require_positive(self.requested_duration_s, "requested_duration_s"))
        errors.extend(_require_non_empty(self.safety_policy_id, "safety_policy_id"))
        errors.extend(_require_non_empty(self.safety_policy_hash, "safety_policy_hash"))
        errors.extend(_require_non_empty(self.source, "source"))

        if self.issued_monotonic_ns < 0:
            errors.append(f"issued_monotonic_ns must be non-negative, got {self.issued_monotonic_ns}")
        if self.expiry_monotonic_ns <= self.issued_monotonic_ns:
            errors.append(
                f"expiry_monotonic_ns ({self.expiry_monotonic_ns}) must be strictly "
                f"greater than issued_monotonic_ns ({self.issued_monotonic_ns})"
            )

        if errors:
            raise ValueError("; ".join(errors))

    def is_expired(self, now_ns: int) -> bool:
        """Check if the command has expired at the given monotonic time."""
        return now_ns >= self.expiry_monotonic_ns

    def validate(self) -> list[DomainError]:
        """Validate all fields, returning domain errors."""
        errors: list[DomainError] = []
        if math.isnan(self.vx_mps) or math.isinf(self.vx_mps):
            errors.append(DomainError(code=ERROR_NON_FINITE_VALUE, message="vx_mps is not finite", retryable=False))
        if math.isnan(self.vy_mps) or math.isinf(self.vy_mps):
            errors.append(DomainError(code=ERROR_NON_FINITE_VALUE, message="vy_mps is not finite", retryable=False))
        if math.isnan(self.wz_radps) or math.isinf(self.wz_radps):
            errors.append(DomainError(code=ERROR_NON_FINITE_VALUE, message="wz_radps is not finite", retryable=False))
        if not self.sequence_id.strip():
            errors.append(validation_error("sequence_id is empty"))
        if self.issued_monotonic_ns < 0:
            errors.append(DomainError(code=ERROR_INVALID_TIMESTAMP, message="issued_monotonic_ns is negative", retryable=False))
        if self.expiry_monotonic_ns <= self.issued_monotonic_ns:
            errors.append(DomainError(code=ERROR_INVALID_TIMESTAMP, message="expiry must be after issue time", retryable=False))
        if self.requested_duration_s <= 0 or math.isnan(self.requested_duration_s) or math.isinf(self.requested_duration_s):
            errors.append(DomainError(code=ERROR_INVALID_DURATION, message="requested_duration_s must be positive and finite", retryable=False))
        if not self.safety_policy_id.strip():
            errors.append(validation_error("safety_policy_id is empty"))
        if not self.safety_policy_hash.strip():
            errors.append(validation_error("safety_policy_hash is empty"))
        return errors

    def validate_against_envelope(self, envelope: Any) -> list[DomainError]:
        """Validate this command against a SafetyEnvelope. Import deferred to avoid circular deps."""
        from calibration_skill.domain.safety import SafetyEnvelope
        if not isinstance(envelope, SafetyEnvelope):
            return [validation_error("Invalid safety envelope type")]
        return envelope.validate_command(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vx_mps": self.vx_mps,
            "vy_mps": self.vy_mps,
            "wz_radps": self.wz_radps,
            "sequence_id": self.sequence_id,
            "issued_monotonic_ns": self.issued_monotonic_ns,
            "expiry_monotonic_ns": self.expiry_monotonic_ns,
            "requested_duration_s": self.requested_duration_s,
            "frame": self.frame.value,
            "safety_policy_id": self.safety_policy_id,
            "safety_policy_hash": self.safety_policy_hash,
            "source": self.source,
        }


@dataclass(frozen=True)
class CommandReceipt:
    """Receipt for a velocity command.

    A receipt only proves what its fields explicitly describe.
    It does not imply physical movement occurred merely because a command was accepted.
    """
    command_sequence_id: str
    disposition: CommandDisposition
    adapter_receipt_id: str | None = None
    received_monotonic_ns: int = 0
    accepted_monotonic_ns: int | None = None
    rejection_error: DomainError | None = None
    adapter_state: str | None = None
    acknowledgement_evidence: str | None = None

    def __post_init__(self) -> None:
        if not self.command_sequence_id or not self.command_sequence_id.strip():
            raise ValueError("command_sequence_id must be non-empty")
        if self.received_monotonic_ns < 0:
            raise ValueError("received_monotonic_ns must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "command_sequence_id": self.command_sequence_id,
            "disposition": self.disposition.value,
            "received_monotonic_ns": self.received_monotonic_ns,
        }
        if self.adapter_receipt_id is not None:
            result["adapter_receipt_id"] = self.adapter_receipt_id
        if self.accepted_monotonic_ns is not None:
            result["accepted_monotonic_ns"] = self.accepted_monotonic_ns
        if self.rejection_error is not None:
            result["rejection_error"] = self.rejection_error.to_dict()
        if self.adapter_state is not None:
            result["adapter_state"] = self.adapter_state
        if self.acknowledgement_evidence is not None:
            result["acknowledgement_evidence"] = self.acknowledgement_evidence
        return result


def validate_lifecycle_transition(
    from_state: MotionLifecycleState,
    to_state: MotionLifecycleState,
) -> list[DomainError]:
    """Validate whether a lifecycle transition is allowed.

    Returns empty list if allowed, list of errors if rejected.
    Platform-specific lifecycle details belong in adapters.
    """
    if from_state == to_state:
        return []  # No-op transitions are allowed
    allowed = ALLOWED_LIFECYCLE_TRANSITIONS.get(from_state, ())
    if to_state in allowed:
        return []
    return [DomainError(
        code="invalid_lifecycle_transition",
        message=f"Transition from {from_state.value} to {to_state.value} is not allowed",
        retryable=False,
        details={"from": from_state.value, "to": to_state.value},
    )]
