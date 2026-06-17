"""K1 adapter configuration and hardware gate contracts."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import CoordinateFrame
from calibration_skill.domain.errors import DomainError
from calibration_skill.domain.safety import SafetyEnvelope
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_HARDWARE_GATE_EXPIRED,
    ERROR_K1_HARDWARE_GATE_INCOMPLETE,
)

K1_FAKE_RUNTIME_MODE = "fake_booster_runtime"
K1_VENDOR_RUNTIME_MODE = "vendor_runtime_placeholder"


def _require_non_empty(value: str, name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _require_finite_non_negative(value: float, name: str) -> None:
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be finite")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True)
class BoosterK1AdapterConfig:
    """Explicit K1 adapter configuration with no silent safety defaults."""
    robot_id: str
    connection_profile_id: str
    runtime_mode: str
    dry_run: bool
    allow_hardware: bool = False
    safety_policy_id: str = ""
    safety_policy_hash: str = ""
    max_abs_vx_mps: float | None = None
    max_abs_vy_mps: float | None = None
    max_abs_wz_radps: float | None = None
    command_timeout_s: float | None = None
    telemetry_timeout_s: float | None = None
    stop_timeout_s: float | None = None
    operator_authorization_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    legacy_forward_only: bool = True

    def __post_init__(self) -> None:
        _require_non_empty(self.robot_id, "robot_id")
        _require_non_empty(self.connection_profile_id, "connection_profile_id")
        _require_non_empty(self.runtime_mode, "runtime_mode")
        _require_non_empty(self.safety_policy_id, "safety_policy_id")
        _require_non_empty(self.safety_policy_hash, "safety_policy_hash")
        if not self.dry_run:
            raise ValueError("M27-B K1 adapter requires dry_run=true")
        if self.allow_hardware:
            raise ValueError("M27-B K1 adapter rejects allow_hardware=true")
        for name in (
            "max_abs_vx_mps",
            "max_abs_vy_mps",
            "max_abs_wz_radps",
            "command_timeout_s",
            "telemetry_timeout_s",
            "stop_timeout_s",
        ):
            value = getattr(self, name)
            if value is None:
                raise ValueError(f"{name} must be explicit")
            _require_finite_non_negative(float(value), name)
        if self.command_timeout_s == 0:
            raise ValueError("command_timeout_s must be positive")
        if self.telemetry_timeout_s == 0:
            raise ValueError("telemetry_timeout_s must be positive")
        if self.stop_timeout_s == 0:
            raise ValueError("stop_timeout_s must be positive")
        if self.legacy_forward_only and (self.max_abs_vy_mps != 0.0 or self.max_abs_wz_radps != 0.0):
            raise ValueError("legacy_forward_only requires explicit zero vy/wz limits")

    def to_safety_envelope(self) -> SafetyEnvelope:
        """Return the safety envelope represented by this config."""
        assert self.max_abs_vx_mps is not None
        assert self.max_abs_vy_mps is not None
        assert self.max_abs_wz_radps is not None
        assert self.command_timeout_s is not None
        assert self.telemetry_timeout_s is not None
        assert self.stop_timeout_s is not None
        return SafetyEnvelope(
            policy_id=self.safety_policy_id,
            policy_hash=self.safety_policy_hash,
            max_abs_vx_mps=self.max_abs_vx_mps,
            max_abs_vy_mps=self.max_abs_vy_mps,
            max_abs_wz_radps=self.max_abs_wz_radps,
            max_command_duration_s=self.command_timeout_s,
            max_telemetry_age_ms=self.telemetry_timeout_s * 1000.0,
            stop_timeout_s=self.stop_timeout_s,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=self.operator_authorization_required,
        )


@dataclass(frozen=True)
class BoosterK1HardwareGate:
    """Explicit real-hardware gate for future K1 vendor runtime work."""
    allow_hardware: bool
    operator_confirmed_hardware: bool
    hardware_session_id: str
    safety_policy_id: str
    safety_policy_hash: str
    expected_robot_id: str
    expected_adapter_mode: str
    require_physical_estop_confirmation: bool
    require_clear_test_area_confirmation: bool
    require_battery_state_confirmation: bool
    require_network_isolation_confirmation: bool
    require_manual_operator_present: bool
    evidence_reference: str
    expires_monotonic_ns: int

    def __post_init__(self) -> None:
        for name in (
            "hardware_session_id",
            "safety_policy_id",
            "safety_policy_hash",
            "expected_robot_id",
            "expected_adapter_mode",
            "evidence_reference",
        ):
            _require_non_empty(str(getattr(self, name)), name)
        if self.expires_monotonic_ns <= 0:
            raise ValueError("expires_monotonic_ns must be positive")

    def validate(self, *, now_ns: int, expected_robot_id: str, expected_safety_policy_id: str, expected_safety_policy_hash: str) -> list[DomainError]:
        """Validate the gate with an explicit monotonic timestamp."""
        errors: list[DomainError] = []
        if now_ns >= self.expires_monotonic_ns:
            errors.append(DomainError(
                ERROR_K1_HARDWARE_GATE_EXPIRED,
                "K1 hardware gate has expired",
                retryable=False,
                details={"expires_monotonic_ns": self.expires_monotonic_ns, "now_ns": now_ns},
            ))
        required_flags = {
            "allow_hardware": self.allow_hardware,
            "operator_confirmed_hardware": self.operator_confirmed_hardware,
            "require_physical_estop_confirmation": self.require_physical_estop_confirmation,
            "require_clear_test_area_confirmation": self.require_clear_test_area_confirmation,
            "require_battery_state_confirmation": self.require_battery_state_confirmation,
            "require_network_isolation_confirmation": self.require_network_isolation_confirmation,
            "require_manual_operator_present": self.require_manual_operator_present,
        }
        missing = [name for name, enabled in required_flags.items() if enabled is not True]
        if missing:
            errors.append(DomainError(
                ERROR_K1_HARDWARE_GATE_INCOMPLETE,
                "K1 hardware gate is incomplete",
                retryable=False,
                details={"missing_confirmations": tuple(missing)},
            ))
        mismatches: dict[str, object] = {}
        if self.expected_robot_id != expected_robot_id:
            mismatches["expected_robot_id"] = self.expected_robot_id
        if self.safety_policy_id != expected_safety_policy_id:
            mismatches["safety_policy_id"] = self.safety_policy_id
        if self.safety_policy_hash != expected_safety_policy_hash:
            mismatches["safety_policy_hash"] = "mismatch"
        if self.expected_adapter_mode != K1_VENDOR_RUNTIME_MODE:
            mismatches["expected_adapter_mode"] = self.expected_adapter_mode
        if mismatches:
            errors.append(DomainError(
                ERROR_K1_HARDWARE_GATE_INCOMPLETE,
                "K1 hardware gate does not match requested runtime",
                retryable=False,
                details=mismatches,
            ))
        return errors

    def is_valid(self, *, now_ns: int, expected_robot_id: str, expected_safety_policy_id: str, expected_safety_policy_hash: str) -> bool:
        return not self.validate(
            now_ns=now_ns,
            expected_robot_id=expected_robot_id,
            expected_safety_policy_id=expected_safety_policy_id,
            expected_safety_policy_hash=expected_safety_policy_hash,
        )
