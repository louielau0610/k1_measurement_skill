"""Fail-closed Booster K1 vendor runtime placeholder for M27-C."""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_HARDWARE_GATE_INCOMPLETE,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_SDK_UNAVAILABLE,
    ERROR_K1_VENDOR_RUNTIME_DISABLED,
    ERROR_K1_VENDOR_RUNTIME_FORBIDDEN,
    ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
)
from calibration_skill.domain.errors import DomainError
from calibration_skill.domain.motion import CommandReceipt
from calibration_skill.domain.enums import MotionLifecycleState

BOOSTER_SDK_MODULE = "booster_robotics_sdk"


@dataclass(frozen=True)
class BoosterK1VendorRuntimeStatus:
    sdk_family: str
    sdk_importable_without_importing: bool
    detection_method: str
    ordinary_runtime_import_safe: bool
    vendor_runtime_implemented: bool
    hardware_gate_required: bool
    hardware_enabled: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "sdk_family": self.sdk_family,
            "sdk_importable_without_importing": self.sdk_importable_without_importing,
            "detection_method": self.detection_method,
            "ordinary_runtime_import_safe": self.ordinary_runtime_import_safe,
            "vendor_runtime_implemented": self.vendor_runtime_implemented,
            "hardware_gate_required": self.hardware_gate_required,
            "hardware_enabled": self.hardware_enabled,
            "reason": self.reason,
        }


class BoosterK1RuntimeUnavailable(RuntimeError):
    """Structured fail-closed runtime error without traceback serialization."""

    def __init__(self, error: DomainError, status: BoosterK1VendorRuntimeStatus | None = None) -> None:
        super().__init__(error.message)
        self.error = error
        self.status = status

    def to_dict(self) -> dict[str, object]:
        result = {"error": self.error.to_dict()}
        if self.status is not None:
            result["status"] = self.status.to_dict()
        return result


class BoosterK1VendorRuntime:
    """Placeholder runtime whose methods fail closed until M27-D."""

    def __init__(self, status: BoosterK1VendorRuntimeStatus) -> None:
        self.status = status

    def _unavailable(self) -> None:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
            "Booster K1 vendor runtime is not implemented in M27-C",
            retryable=False,
        ), self.status)

    def connect(self, *, timeout_s: float) -> None:
        self._unavailable()

    def disconnect(self) -> None:
        self._unavailable()

    def identity_metadata(self) -> dict[str, object]:
        self._unavailable()

    def current_motion_state(self) -> MotionLifecycleState:
        self._unavailable()

    def enter_prepare_mode(self) -> None:
        self._unavailable()

    def enter_walking_mode(self) -> None:
        self._unavailable()

    def send_body_velocity(self, *, vx_mps: float, vy_mps: float, wz_radps: float) -> CommandReceipt:
        self._unavailable()

    def stop(self) -> CommandReceipt:
        self._unavailable()

    def restore_safe_state(self) -> None:
        self._unavailable()


def detect_booster_sdk_availability() -> BoosterK1VendorRuntimeStatus:
    """Detect whether the future SDK module is discoverable without importing it."""
    found = importlib.util.find_spec(BOOSTER_SDK_MODULE) is not None
    reason = "SDK module discoverable but M27-C placeholder remains disabled" if found else "SDK module not discoverable"
    return BoosterK1VendorRuntimeStatus(
        sdk_family="booster_k1",
        sdk_importable_without_importing=found,
        detection_method="importlib.util.find_spec",
        ordinary_runtime_import_safe=True,
        vendor_runtime_implemented=False,
        hardware_gate_required=True,
        hardware_enabled=False,
        reason=reason,
    )


def create_booster_k1_vendor_runtime(
    *,
    hardware_gate: BoosterK1HardwareGate | None,
    now_ns: int,
    expected_robot_id: str,
    expected_safety_policy_id: str,
    expected_safety_policy_hash: str,
    future_implementation_enabled: bool = False,
    status: BoosterK1VendorRuntimeStatus | None = None,
) -> BoosterK1VendorRuntime:
    """Fail closed before constructing any real runtime object."""
    runtime_status = status or detect_booster_sdk_availability()
    if hardware_gate is None:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_HARDWARE_GATE_MISSING,
            "K1 vendor runtime requires an explicit hardware gate",
            retryable=False,
        ), runtime_status)
    gate_errors = hardware_gate.validate(
        now_ns=now_ns,
        expected_robot_id=expected_robot_id,
        expected_safety_policy_id=expected_safety_policy_id,
        expected_safety_policy_hash=expected_safety_policy_hash,
    )
    if gate_errors:
        raise BoosterK1RuntimeUnavailable(gate_errors[0], runtime_status)
    if not runtime_status.sdk_importable_without_importing:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_SDK_UNAVAILABLE,
            "Booster K1 SDK is unavailable; ordinary package remains no-vendor",
            retryable=False,
        ), runtime_status)
    if not future_implementation_enabled:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
            "M27-C defines the K1 vendor boundary but does not implement real runtime startup",
            retryable=False,
        ), runtime_status)
    raise BoosterK1RuntimeUnavailable(DomainError(
        ERROR_K1_VENDOR_RUNTIME_DISABLED,
        "K1 vendor runtime is disabled by M27-C policy",
        retryable=False,
    ), runtime_status)


def dry_run_package_forbidden_error() -> DomainError:
    return DomainError(
        ERROR_K1_VENDOR_RUNTIME_FORBIDDEN,
        "K1 vendor runtime is forbidden in the ordinary dry-run package",
        retryable=False,
        details={"required_adapter_mode": K1_VENDOR_RUNTIME_MODE},
    )
