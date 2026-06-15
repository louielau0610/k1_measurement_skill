"""Structured domain error taxonomy for the calibration skill."""
from __future__ import annotations

from dataclasses import dataclass, field


# Error code constants
ERROR_CONFIGURATION_MISSING = "configuration_missing"
ERROR_CONFIGURATION_INVALID = "configuration_invalid"
ERROR_UNSUPPORTED_PLATFORM = "unsupported_platform"
ERROR_CAPABILITY_UNAVAILABLE = "capability_unavailable"
ERROR_CAPABILITY_UNVERIFIED = "capability_unverified"
ERROR_PRECONDITION_FAILED = "precondition_failed"
ERROR_ADAPTER_DISCONNECTED = "adapter_disconnected"
ERROR_WRONG_MOTION_STATE = "wrong_motion_state"
ERROR_OPERATOR_AUTHORIZATION_REQUIRED = "operator_authorization_required"
ERROR_OPERATOR_AUTHORIZATION_EXPIRED = "operator_authorization_expired"
ERROR_COMMAND_EXPIRED = "command_expired"
ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE = "command_outside_safety_envelope"
ERROR_TELEMETRY_UNAVAILABLE = "telemetry_unavailable"
ERROR_TELEMETRY_STALE = "telemetry_stale"
ERROR_STOP_UNACKNOWLEDGED = "stop_unacknowledged"
ERROR_SCHEMA_VERSION_UNSUPPORTED = "schema_version_unsupported"
ERROR_SERIALIZATION_FAILED = "serialization_failed"
ERROR_PROVENANCE_INVALID = "provenance_invalid"
ERROR_INTERNAL_ERROR = "internal_error"
ERROR_VALIDATION_FAILED = "validation_failed"

# Additional domain-internal error codes
ERROR_INVALID_IDENTIFIER = "invalid_identifier"
ERROR_INVALID_TIMESTAMP = "invalid_timestamp"
ERROR_INVALID_DURATION = "invalid_duration"
ERROR_INVALID_TIMEOUT = "invalid_timeout"
ERROR_NON_FINITE_VALUE = "non_finite_value"
ERROR_INVALID_QUATERNION = "invalid_quaternion"
ERROR_INVALID_ENUM_VALUE = "invalid_enum_value"
ERROR_INVALID_FRAME = "invalid_frame"
ERROR_INVALID_SAFETY_POLICY = "invalid_safety_policy"


@dataclass(frozen=True)
class DomainError:
    """A structured domain error.

    All domain validation failures produce a DomainError with a stable code.
    Vendor-specific exception objects must not be embedded directly.
    """
    code: str
    message: str
    retryable: bool = False
    details: dict[str, object] = field(default_factory=dict)
    cause_type: str | None = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict[str, object]:
        """Serialize to a dictionary. Does not include traceback by default."""
        result: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.details:
            result["details"] = self.details
        return result


def domain_error(
    code: str,
    message: str,
    *,
    retryable: bool = False,
    details: dict[str, object] | None = None,
    cause_type: str | None = None,
) -> DomainError:
    """Create a DomainError with the given code and message."""
    return DomainError(
        code=code,
        message=message,
        retryable=retryable,
        details=details or {},
        cause_type=cause_type,
    )


def validation_error(
    message: str,
    *,
    details: dict[str, object] | None = None,
) -> DomainError:
    """Create a validation error."""
    return DomainError(
        code=ERROR_VALIDATION_FAILED,
        message=message,
        retryable=False,
        details=details or {},
    )
