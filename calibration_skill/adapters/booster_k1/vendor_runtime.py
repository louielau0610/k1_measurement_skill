"""Booster K1 vendor runtime with isolated SDK binding for M27-D.

M27-D replaces the M27-C placeholder with a runtime backed by an
injected vendor binding. The runtime normalizes SDK responses into
domain types and enforces zero-motion.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    BoosterK1DomainError,
    ERROR_K1_HARDWARE_GATE_INCOMPLETE,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_HARDWARE_EXECUTION_DISABLED,
    ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
    ERROR_K1_SDK_UNAVAILABLE,
    ERROR_K1_VENDOR_RUNTIME_DISABLED,
    ERROR_K1_VENDOR_RUNTIME_DISCONNECTED,
    ERROR_K1_VENDOR_RUNTIME_FORBIDDEN,
    ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
    ERROR_K1_VENDOR_RUNTIME_NOT_LOCOMOTION_READY,
)
from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
    BoosterK1RuntimeProtocol,
)
from calibration_skill.adapters.booster_k1.vendor_types import (
    BoosterK1VendorBindingProtocol,
)
from calibration_skill.domain.errors import DomainError
from calibration_skill.domain.motion import CommandReceipt
from calibration_skill.domain.enums import MotionLifecycleState

BOOSTER_SDK_MODULE = "booster_robotics_sdk_python"

# M27-D zero-motion tolerance
_ZERO_MOTION_EPSILON = 1e-9


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
    package_probe_discoverable: bool = False
    direct_entry_modules_discoverable: bool = False

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
            "package_probe_discoverable": self.package_probe_discoverable,
            "direct_entry_modules_discoverable": self.direct_entry_modules_discoverable,
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
    """Real Booster K1 runtime backed by an injected vendor binding.

    M27-D implementation that wraps the vendor binding with:
    - clock injection via time.monotonic_ns()
    - vendor enum normalization into MotionLifecycleState
    - SDK receipt normalization into BoosterK1RuntimeCommandReceipt
    - odometry normalization into BoosterK1RuntimeOdometry
    - robot state normalization into BoosterK1RuntimeState
    - connect/disconnect lifecycle idempotence
    - rejection of commands while disconnected
    - rejection of commands before locomotion-ready state
    - zero-motion enforcement
    - safe restoration on failures
    """

    def __init__(self, binding: BoosterK1VendorBindingProtocol, status: BoosterK1VendorRuntimeStatus | None = None, clock_fn: Any = None) -> None:
        self._binding = binding
        self.status = status or detect_booster_sdk_availability()
        self._clock = clock_fn or time.monotonic_ns
        self._connected = False
        self._locomotion_ready = False
        self._receipt_counter = 0

    # --- BoosterK1RuntimeProtocol implementation ---

    def now_ns(self) -> int:
        return self._clock()

    def connect(self, *, timeout_s: float) -> None:
        """Connect to the robot via the vendor binding. Idempotent."""
        if self._connected:
            return
        try:
            self._binding.connect(timeout_s=timeout_s)
            self._connected = True
            self._locomotion_ready = False
        except Exception:
            self._connected = False
            self._locomotion_ready = False
            raise

    def disconnect(self) -> None:
        """Disconnect from the robot. Idempotent and safe."""
        try:
            if self._connected:
                self._binding.disconnect()
        except Exception:
            pass
        finally:
            self._connected = False
            self._locomotion_ready = False

    def identity_metadata(self) -> dict[str, object]:
        self._require_connected()
        return self._binding.identity_metadata()

    def current_motion_state(self) -> MotionLifecycleState:
        return self._binding.current_motion_state()

    def enter_prepare_mode(self) -> None:
        self._require_connected()
        self._binding.enter_prepare_mode()
        self._locomotion_ready = False

    def enter_walking_mode(self) -> None:
        self._require_connected()
        self._binding.enter_walking_mode()
        self._locomotion_ready = True

    def send_body_velocity(
        self, *, vx_mps: float, vy_mps: float, wz_radps: float
    ) -> BoosterK1RuntimeCommandReceipt:
        """Send body velocity command. M27-D: zero-motion only."""
        self._require_connected()
        self._require_locomotion_ready()

        # M27-D zero-motion enforcement (runtime boundary)
        if not self._is_zero_motion(vx_mps, vy_mps, wz_radps):
            raise BoosterK1DomainError(
                ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
                "M27-D zero-motion: nonzero velocity commands are forbidden",
                retryable=False,
                details={
                    "vx_mps": vx_mps,
                    "vy_mps": vy_mps,
                    "wz_radps": wz_radps,
                    "zero_epsilon": _ZERO_MOTION_EPSILON,
                },
            )

        try:
            return self._binding.send_body_velocity(
                vx_mps=vx_mps,
                vy_mps=vy_mps,
                wz_radps=wz_radps,
            )
        except BoosterK1DomainError:
            raise
        except Exception as exc:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"k1-runtime-receipt-{self._next_receipt()}",
                received_monotonic_ns=self.now_ns(),
                detail=f"Vendor binding error: {exc.__class__.__name__}",
            )

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        """Issue explicit stop command."""
        if not self._connected:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"k1-runtime-stop-{self._next_receipt()}",
                received_monotonic_ns=self.now_ns(),
                detail="Runtime disconnected; stop not sent",
            )
        try:
            receipt = self._binding.stop()
            self._locomotion_ready = False
            return receipt
        except Exception:
            self._locomotion_ready = False
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"k1-runtime-stop-{self._next_receipt()}",
                received_monotonic_ns=self.now_ns(),
                detail="Stop attempt failed at binding boundary",
            )

    def restore_safe_state(self) -> None:
        """Restore robot to safe state. Best-effort, never raises."""
        try:
            self._binding.restore_safe_state()
        except Exception:
            pass
        finally:
            self._locomotion_ready = False

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        """Read odometry if available."""
        if not self._connected:
            return None
        try:
            return self._binding.read_odometry()
        except Exception:
            return None

    def read_robot_state(self) -> BoosterK1RuntimeState:
        """Read robot state."""
        if not self._connected:
            return BoosterK1RuntimeState(
                motion_state=MotionLifecycleState.UNAVAILABLE,
                mode_name="disconnected",
                source_monotonic_ns=self.now_ns(),
            )
        try:
            return self._binding.read_robot_state()
        except Exception:
            return BoosterK1RuntimeState(
                motion_state=MotionLifecycleState.UNAVAILABLE,
                mode_name="error",
                source_monotonic_ns=self.now_ns(),
            )

    def read_battery_state(self) -> dict[str, float] | None:
        """Read battery state if available."""
        if not self._connected:
            return None
        try:
            return self._binding.read_battery_state()
        except Exception:
            return None

    def health_check(self) -> BoosterK1RuntimeHealth:
        """Check runtime health."""
        now_ns = self.now_ns()
        if not self._connected:
            return BoosterK1RuntimeHealth(
                healthy=False,
                checked_monotonic_ns=now_ns,
                detail="K1 vendor runtime is disconnected",
            )
        try:
            return self._binding.health_check()
        except Exception as exc:
            return BoosterK1RuntimeHealth(
                healthy=False,
                checked_monotonic_ns=now_ns,
                detail=f"Health check failed: {exc.__class__.__name__}",
            )

    # --- Internal helpers ---

    def _require_connected(self) -> None:
        if not self._connected:
            raise BoosterK1DomainError(
                ERROR_K1_VENDOR_RUNTIME_DISCONNECTED,
                "K1 vendor runtime is not connected",
                retryable=True,
            )

    def _require_locomotion_ready(self) -> None:
        if not self._locomotion_ready:
            raise BoosterK1DomainError(
                ERROR_K1_VENDOR_RUNTIME_NOT_LOCOMOTION_READY,
                "K1 vendor runtime is not in locomotion-ready state",
                retryable=True,
            )

    @staticmethod
    def _is_zero_motion(vx_mps: float, vy_mps: float, wz_radps: float) -> bool:
        return (
            abs(vx_mps) <= _ZERO_MOTION_EPSILON
            and abs(vy_mps) <= _ZERO_MOTION_EPSILON
            and abs(wz_radps) <= _ZERO_MOTION_EPSILON
        )

    def _next_receipt(self) -> int:
        self._receipt_counter += 1
        return self._receipt_counter


# --- Standalone detection and factory functions ---

def detect_booster_sdk_availability() -> BoosterK1VendorRuntimeStatus:
    """Detect package probe and direct entry modules without importing them."""
    from calibration_skill.adapters.booster_k1.vendor_binding import (
        detect_booster_sdk_availability_detailed,
    )

    detection = detect_booster_sdk_availability_detailed()
    found = detection.direct_entry_modules_discoverable
    reason = (
        "Direct SDK entry modules discoverable; M27-D.1 zero-motion binding available"
        if found
        else "Direct SDK entry modules not discoverable"
    )
    return BoosterK1VendorRuntimeStatus(
        sdk_family="booster_k1",
        sdk_importable_without_importing=found,
        detection_method=detection.detection_method,
        ordinary_runtime_import_safe=True,
        vendor_runtime_implemented=True,
        hardware_gate_required=True,
        hardware_enabled=False,
        reason=reason,
        package_probe_discoverable=detection.package_probe_discoverable,
        direct_entry_modules_discoverable=detection.direct_entry_modules_discoverable,
    )


def create_booster_k1_vendor_runtime(
    *,
    hardware_gate: BoosterK1HardwareGate | None,
    now_ns: int,
    expected_robot_id: str,
    expected_safety_policy_id: str,
    expected_safety_policy_hash: str,
    future_implementation_enabled: bool = False,
    enable_vendor_runtime: bool = False,
    execute_hardware: bool = False,
    status: BoosterK1VendorRuntimeStatus | None = None,
    interface: str = "lo",
    clock_fn: Any = None,
) -> BoosterK1VendorRuntime:
    """Construct a vendor runtime backed by the real SDK binding.

    Evaluates conditions in mandated order:
    1. hardware gate exists
    2. gate is complete and unexpired
    3. robot ID matches
    4. safety policy ID and hash match
    5. adapter mode is the real vendor mode
    6. vendor runtime is explicitly enabled
    7. SDK is discoverable
    8. explicit SDK import succeeds
    9. vendor binding construction succeeds
    10. runtime object is returned

    No SDK import or SDK object construction occurs before steps 1-6 pass.
    """
    # Step 1: hardware gate exists
    if hardware_gate is None:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_HARDWARE_GATE_MISSING,
            "K1 vendor runtime requires an explicit hardware gate",
            retryable=False,
        ), status)

    # Steps 2-4: gate validation (includes robot ID, policy ID, policy hash)
    gate_errors = hardware_gate.validate(
        now_ns=now_ns,
        expected_robot_id=expected_robot_id,
        expected_safety_policy_id=expected_safety_policy_id,
        expected_safety_policy_hash=expected_safety_policy_hash,
    )
    if gate_errors:
        raise BoosterK1RuntimeUnavailable(gate_errors[0], status)

    # Step 5: adapter mode check (done via expected_adapter_mode in gate)

    # Step 6: vendor runtime explicitly enabled
    if not enable_vendor_runtime and not future_implementation_enabled:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
            "K1 vendor runtime is not explicitly enabled",
            retryable=False,
        ), status)

    # Step 7: hardware execution explicitly enabled
    if not execute_hardware:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_HARDWARE_EXECUTION_DISABLED,
            "K1 hardware execution is not explicitly enabled",
            retryable=False,
        ), status)

    runtime_status = status or detect_booster_sdk_availability()

    # Step 8: direct SDK entry modules discoverable
    if not runtime_status.sdk_importable_without_importing:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_SDK_UNAVAILABLE,
            "Booster K1 direct SDK entry modules are unavailable; ordinary package remains no-vendor",
            retryable=False,
        ), runtime_status)

    # Steps 9-10: import SDK and construct binding
    from calibration_skill.adapters.booster_k1.vendor_binding import create_vendor_binding

    try:
        binding = create_vendor_binding(
            hardware_gate=hardware_gate,
            now_ns=now_ns,
            expected_robot_id=expected_robot_id,
            expected_safety_policy_id=expected_safety_policy_id,
            expected_safety_policy_hash=expected_safety_policy_hash,
            enable_vendor_runtime=enable_vendor_runtime or future_implementation_enabled,
            execute_hardware=execute_hardware,
            interface=interface,
            clock_fn=clock_fn,
        )
    except BoosterK1RuntimeUnavailable:
        raise
    except BoosterK1DomainError:
        raise
    except Exception as exc:
        raise BoosterK1RuntimeUnavailable(DomainError(
            ERROR_K1_SDK_UNAVAILABLE,
            f"Failed to construct K1 vendor binding: {exc}",
            retryable=False,
            cause_type=type(exc).__name__,
        ), runtime_status) from exc

    # Step 10: return runtime
    return BoosterK1VendorRuntime(binding=binding, status=runtime_status, clock_fn=clock_fn)


def dry_run_package_forbidden_error() -> DomainError:
    return DomainError(
        ERROR_K1_VENDOR_RUNTIME_FORBIDDEN,
        "K1 vendor runtime is forbidden in the ordinary dry-run package",
        retryable=False,
        details={"required_adapter_mode": K1_VENDOR_RUNTIME_MODE},
    )
