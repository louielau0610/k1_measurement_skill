"""Booster K1 adapter-specific domain error codes."""
from __future__ import annotations

import re

ERROR_K1_HARDWARE_GATE_CLOSED = "k1_hardware_gate_closed"
ERROR_K1_RUNTIME_MODE_UNSUPPORTED = "k1_runtime_mode_unsupported"
ERROR_K1_UNSUPPORTED_AXIS = "k1_unsupported_axis"
ERROR_K1_RUNTIME_UNHEALTHY = "k1_runtime_unhealthy"
ERROR_K1_SDK_UNAVAILABLE = "k1_sdk_unavailable"
ERROR_K1_HARDWARE_GATE_MISSING = "k1_hardware_gate_missing"
ERROR_K1_HARDWARE_GATE_EXPIRED = "k1_hardware_gate_expired"
ERROR_K1_HARDWARE_GATE_INCOMPLETE = "k1_hardware_gate_incomplete"
ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED = "k1_vendor_runtime_not_implemented"
ERROR_K1_VENDOR_RUNTIME_DISABLED = "k1_vendor_runtime_disabled"
ERROR_K1_VENDOR_RUNTIME_FORBIDDEN = "k1_vendor_runtime_forbidden"

# M27-D zero-motion and binding error codes
ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN = "k1_m27d_nonzero_motion_forbidden"
ERROR_K1_BINDING_CONSTRUCTION_FAILED = "k1_binding_construction_failed"
ERROR_K1_SDK_IMPORT_FAILED = "k1_sdk_import_failed"
ERROR_K1_CONNECTION_FAILED = "k1_connection_failed"
ERROR_K1_READ_ONLY_CHECK_FAILED = "k1_read_only_check_failed"
ERROR_K1_STOP_UNACKNOWLEDGED = "k1_m27d_stop_unacknowledged"
ERROR_K1_SAFE_STATE_UNVERIFIED = "k1_m27d_safe_state_unverified"
ERROR_K1_HARDWARE_EXECUTION_DISABLED = "k1_hardware_execution_disabled"
ERROR_K1_VENDOR_RUNTIME_DISCONNECTED = "k1_vendor_runtime_disconnected"
ERROR_K1_VENDOR_RUNTIME_NOT_LOCOMOTION_READY = "k1_vendor_runtime_not_locomotion_ready"
ERROR_K1_BINDING_OPERATION_FAILED = "k1_binding_operation_failed"


_MEMORY_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")
_SECRET_TOKEN_RE = re.compile(
    r"(?i)(password|passwd|secret|token|credential|api[_-]?key)\s*[:=]\s*[^,\s;]+"
)


def sanitize_vendor_message(value: object, *, max_length: int = 180) -> str:
    """Return a short vendor message safe for structured artifacts."""
    text = str(value)
    text = text.replace("\r", " ").replace("\n", " ")
    text = _MEMORY_ADDRESS_RE.sub("0x<redacted>", text)
    text = _SECRET_TOKEN_RE.sub(r"\1=<redacted>", text)
    text = text.replace("Traceback (most recent call last):", "Traceback <redacted>:")
    text = " ".join(text.split())
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text


class BoosterK1DomainError(Exception):
    """Base exception for Booster K1 domain errors.

    Wraps a DomainError for structured error handling while being
    a proper Exception subclass that can be raised and caught.
    """

    def __init__(self, code: str, message: str, *, retryable: bool = False, details: dict[str, object] | None = None, cause_type: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details or {}
        self.cause_type = cause_type

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "code": self.code,
            "message": sanitize_vendor_message(self.message),
            "retryable": self.retryable,
        }
        if self.details:
            result["details"] = self.details
        if self.cause_type:
            result["cause_type"] = self.cause_type
        return result

    def to_domain_error(self):
        """Convert to a DomainError dataclass."""
        from calibration_skill.domain.errors import DomainError
        return DomainError(
            code=self.code,
            message=self.message,
            retryable=self.retryable,
            details=self.details,
            cause_type=self.cause_type,
        )
