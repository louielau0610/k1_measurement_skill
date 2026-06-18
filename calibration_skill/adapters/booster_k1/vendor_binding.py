"""Vendor binding for the Booster K1 SDK.

M27-D: Implements BoosterK1VendorBindingProtocol using the verified
Booster SDK imports discovered in the repository.

Verified SDK imports (from scripts/send_m23b_k1_velocity_command.py
and scripts/run_m19c_ros2_odometer_trials.py):
    from B1LocoClient import B1LocoClient
    from ChannelFactory import ChannelFactory
    from RobotMode import RobotMode

Verified motion sequence: kPrepare -> kWalking -> Move(vx, 0.0, 0.0)

This binding enforces zero-motion for M27-D and must not send any
nonzero velocity command.
"""
from __future__ import annotations

import importlib
import time
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate
from calibration_skill.adapters.booster_k1.errors import (
    BoosterK1DomainError,
    ERROR_K1_BINDING_CONSTRUCTION_FAILED,
    ERROR_K1_BINDING_OPERATION_FAILED,
    ERROR_K1_CONNECTION_FAILED,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
    ERROR_K1_SDK_IMPORT_FAILED,
    ERROR_K1_SDK_UNAVAILABLE,
    ERROR_K1_VENDOR_RUNTIME_DISABLED,
    ERROR_K1_HARDWARE_EXECUTION_DISABLED,
    sanitize_vendor_message,
)
from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.adapters.booster_k1.vendor_types import (
    BoosterK1VendorBindingMetadata,
    BoosterK1VendorSDKDetection,
)
from calibration_skill.domain.enums import MotionLifecycleState
from calibration_skill.domain.errors import DomainError

# --- Verified SDK entry points ---
# These are the exact import paths verified in the repository by
# scripts/send_m23b_k1_velocity_command.py and
# scripts/run_m19c_ros2_odometer_trials.py.
PACKAGE_PROBE_MODULE = "booster_robotics_sdk_python"
VERIFIED_SDK_ENTRY_MODULE = PACKAGE_PROBE_MODULE
VERIFIED_DIRECT_ENTRY_MODULES = ("B1LocoClient", "ChannelFactory", "RobotMode")
VERIFIED_SDK_CLASSES = ("B1LocoClient", "ChannelFactory", "RobotMode")
VERIFIED_MOTION_SEQUENCE = ("kPrepare", "kWalking", "Move(vx, 0.0, 0.0)")

# M27-D zero-motion tolerance (exact comparison with tiny epsilon for float safety)
_ZERO_MOTION_EPSILON = 1e-9

BINDING_VERSION = "m27d.1"


def detect_booster_sdk_availability_detailed() -> BoosterK1VendorSDKDetection:
    """Detect Booster SDK evidence without importing direct SDK modules."""
    errors: list[str] = []
    try:
        package_spec = importlib.util.find_spec(PACKAGE_PROBE_MODULE)
        package_probe_discoverable = package_spec is not None
    except Exception as exc:
        package_probe_discoverable = False
        errors.append(
            f"find_spec({PACKAGE_PROBE_MODULE}) raised "
            f"{exc.__class__.__name__}: {sanitize_vendor_message(exc)}"
        )

    direct_specs: dict[str, bool] = {}
    for module_name in VERIFIED_DIRECT_ENTRY_MODULES:
        try:
            direct_specs[module_name] = importlib.util.find_spec(module_name) is not None
        except Exception as exc:
            direct_specs[module_name] = False
            errors.append(
                f"find_spec({module_name}) raised "
                f"{exc.__class__.__name__}: {sanitize_vendor_message(exc)}"
            )

    direct_discoverable = all(direct_specs.get(name, False) for name in VERIFIED_DIRECT_ENTRY_MODULES)

    return BoosterK1VendorSDKDetection(
        sdk_import_path=",".join(VERIFIED_DIRECT_ENTRY_MODULES),
        discoverable=direct_discoverable,
        detection_method="package_probe_and_direct_module_find_spec",
        sdk_entry_classes=VERIFIED_SDK_CLASSES,
        verified_imports_found=False,
        detection_errors=tuple(errors),
        package_probe_module=PACKAGE_PROBE_MODULE,
        package_probe_discoverable=package_probe_discoverable,
        direct_entry_modules=VERIFIED_DIRECT_ENTRY_MODULES,
        direct_entry_module_specs=direct_specs,
        direct_entry_modules_discoverable=direct_discoverable,
        direct_imports_attempted=False,
        direct_imports_verified=False,
    )


def _import_verified_sdk():
    """Import the verified Booster SDK entry classes.

    Returns (B1LocoClient, ChannelFactory, RobotMode) or raises.
    Uses the exact direct import modules verified in the repository.
    """
    errors: list[str] = []
    resolved: dict[str, Any] = {}
    module_by_class = {
        "B1LocoClient": "B1LocoClient",
        "ChannelFactory": "ChannelFactory",
        "RobotMode": "RobotMode",
    }
    for class_name, module_name in module_by_class.items():
        try:
            module = importlib.import_module(module_name)
            resolved[class_name] = getattr(module, class_name)
        except ImportError as exc:
            errors.append(f"import {module_name}: {sanitize_vendor_message(exc)}")
        except AttributeError as exc:
            errors.append(f"{class_name} missing from {module_name}: {sanitize_vendor_message(exc)}")
        except Exception as exc:
            errors.append(
                f"import {module_name}: {exc.__class__.__name__}: "
                f"{sanitize_vendor_message(exc)}"
            )

    if errors:
        raise ImportError("; ".join(errors))

    return resolved["B1LocoClient"], resolved["ChannelFactory"], resolved["RobotMode"]


def _read_sdk_version() -> str | None:
    try:
        module = importlib.import_module(PACKAGE_PROBE_MODULE)
        return getattr(module, "__version__", None)
    except Exception:
        return None


def _is_zero_motion(vx_mps: float, vy_mps: float, wz_radps: float) -> bool:
    """Check whether all velocity components are within zero tolerance."""
    return (
        abs(vx_mps) <= _ZERO_MOTION_EPSILON
        and abs(vy_mps) <= _ZERO_MOTION_EPSILON
        and abs(wz_radps) <= _ZERO_MOTION_EPSILON
    )


@dataclass
class BoosterK1VendorBinding:
    """Real Booster K1 SDK binding.

    Wraps the verified SDK imports with normalized operations.
    Enforces zero-motion for M27-D.
    No raw SDK objects escape through public methods.

    Lifecycle:
        constructed -> connect() -> [operations] -> disconnect()
    """

    interface: str = "lo"
    now_ns_fn: Any = None  # Callable[[], int] - injectable clock

    # Internal SDK handles (not exposed)
    _client: Any = field(default=None, init=False, repr=False)
    _channel: Any = field(default=None, init=False, repr=False)
    _connected: bool = field(default=False, init=False, repr=False)
    _motion_state: MotionLifecycleState = field(default=MotionLifecycleState.UNAVAILABLE, init=False)
    _receipt_counter: int = field(default=0, init=False, repr=False)
    _sdk_version: str | None = field(default=None, init=False, repr=False)

    # SDK classes (set during construction via import)
    _B1LocoClient: Any = field(default=None, init=False, repr=False)
    _ChannelFactory: Any = field(default=None, init=False, repr=False)
    _RobotMode: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.now_ns_fn is None:
            self.now_ns_fn = time.monotonic_ns

    @property
    def metadata(self) -> BoosterK1VendorBindingMetadata:
        return BoosterK1VendorBindingMetadata(
            binding_class=self.__class__.__name__,
            sdk_family="booster_k1",
            sdk_version=self._sdk_version,
            binding_version=BINDING_VERSION,
            sdk_import_path=",".join(VERIFIED_DIRECT_ENTRY_MODULES),
            sdk_entry_classes=VERIFIED_SDK_CLASSES,
            direct_entry_modules=VERIFIED_DIRECT_ENTRY_MODULES,
            verified_motion_sequence=VERIFIED_MOTION_SEQUENCE,
            zero_motion_only=True,
            support_level="zero_motion_bench_only",
            note="M27-D.1 zero-motion binding; direct imports verified only after hardware gates pass",
        )

    @staticmethod
    def create_with_sdk_import(
        *,
        interface: str = "lo",
        now_ns_fn: Any = None,
    ) -> "BoosterK1VendorBinding":
        """Factory: import verified SDK and construct binding.

        This is the only code path that may import the Booster SDK.
        It must only be called after all gates pass.
        """
        try:
            B1LocoClient_cls, ChannelFactory_cls, RobotMode_enum = _import_verified_sdk()
        except ImportError as exc:
            raise BoosterK1DomainError(
                ERROR_K1_SDK_IMPORT_FAILED,
                f"Failed to import verified Booster SDK: {exc}",
                retryable=False,
                details={
                    "sdk_module": VERIFIED_SDK_ENTRY_MODULE,
                    "direct_entry_modules": list(VERIFIED_DIRECT_ENTRY_MODULES),
                    "sdk_classes": list(VERIFIED_SDK_CLASSES),
                },
                cause_type=type(exc).__name__,
            ) from exc

        binding = BoosterK1VendorBinding(interface=interface, now_ns_fn=now_ns_fn)
        binding._B1LocoClient = B1LocoClient_cls
        binding._ChannelFactory = ChannelFactory_cls
        binding._RobotMode = RobotMode_enum
        binding._sdk_version = _read_sdk_version()
        return binding

    # --- Protocol methods ---

    def connect(self, *, timeout_s: float) -> None:
        """Initialize SDK channel and client. Idempotent."""
        if self._connected:
            return
        try:
            self._channel = self._ChannelFactory.Instance()
            self._channel.Init(0, self.interface)
            self._client = self._B1LocoClient()
            self._client.Init()
            self._connected = True
            self._motion_state = MotionLifecycleState.IDLE
        except Exception as exc:
            self._connected = False
            self._client = None
            self._channel = None
            raise BoosterK1DomainError(
                ERROR_K1_CONNECTION_FAILED,
                f"K1 SDK connection failed: {sanitize_vendor_message(exc)}",
                retryable=True,
                details={"interface": self.interface, "timeout_s": timeout_s},
                cause_type=type(exc).__name__,
            ) from exc

    def disconnect(self) -> None:
        """Close SDK channel. Idempotent, safe to call multiple times."""
        self._connected = False
        self._client = None
        self._channel = None
        self._motion_state = MotionLifecycleState.UNAVAILABLE

    def identity_metadata(self) -> dict[str, object]:
        self._require_connected()
        return {
            "sdk_family": "booster_k1",
            "sdk_version": self._sdk_version or "unknown",
            "sdk_module": VERIFIED_SDK_ENTRY_MODULE,
            "binding_version": BINDING_VERSION,
            "interface": self.interface,
            "connected": self._connected,
        }

    def current_motion_state(self) -> MotionLifecycleState:
        return self._motion_state

    def enter_prepare_mode(self) -> None:
        """Transition to kPrepare mode.

        The verified repository code uses:
            client.RobotMode(RobotMode.kPrepare)
        """
        self._require_connected()
        try:
            self._client.RobotMode(self._RobotMode.kPrepare)
            self._motion_state = MotionLifecycleState.PREPARING
        except Exception as exc:
            raise BoosterK1DomainError(
                ERROR_K1_BINDING_OPERATION_FAILED,
                f"K1 enter_prepare_mode failed: {sanitize_vendor_message(exc)}",
                retryable=True,
                details={"operation": "kPrepare"},
                cause_type=type(exc).__name__,
            ) from exc

    def enter_walking_mode(self) -> None:
        """Transition to kWalking mode.

        The verified repository code uses:
            client.RobotMode(RobotMode.kWalking)
        """
        self._require_connected()
        try:
            self._client.RobotMode(self._RobotMode.kWalking)
            self._motion_state = MotionLifecycleState.LOCOMOTION_READY
        except Exception as exc:
            raise BoosterK1DomainError(
                ERROR_K1_BINDING_OPERATION_FAILED,
                f"K1 enter_walking_mode failed: {sanitize_vendor_message(exc)}",
                retryable=True,
                details={"operation": "kWalking"},
                cause_type=type(exc).__name__,
            ) from exc

    def send_body_velocity(
        self,
        *,
        vx_mps: float,
        vy_mps: float,
        wz_radps: float,
    ) -> BoosterK1RuntimeCommandReceipt:
        """Send body velocity command. M27-D: zero-motion only.

        The verified repository code uses:
            client.Move(vx, 0.0, 0.0)

        For M27-D, only (0.0, 0.0, 0.0) is permitted.
        """
        self._require_connected()

        # --- M27-D zero-motion enforcement ---
        if not _is_zero_motion(vx_mps, vy_mps, wz_radps):
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

        self._receipt_counter += 1
        now_ns = self.now_ns_fn()
        try:
            self._client.Move(float(vx_mps), float(vy_mps), float(wz_radps))
            return BoosterK1RuntimeCommandReceipt(
                accepted=True,
                runtime_receipt_id=f"k1-vendor-receipt-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail="M27-D.1 zero command accepted; physical stopping not independently verified",
                zero_command_accepted=True,
                physical_stop_verified=False,
                internal_command_state=self._motion_state.value,
            )
        except Exception as exc:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"k1-vendor-receipt-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail=f"SDK Move failed: {sanitize_vendor_message(exc)}",
                internal_command_state=self._motion_state.value,
            )

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        """Issue explicit stop/zero command.

        Uses Move(0.0, 0.0, 0.0) as verified in the repository.
        """
        self._require_connected()
        self._receipt_counter += 1
        now_ns = self.now_ns_fn()
        try:
            self._client.Move(0.0, 0.0, 0.0)
            self._motion_state = MotionLifecycleState.SAFE_STOPPED
            return BoosterK1RuntimeCommandReceipt(
                accepted=True,
                runtime_receipt_id=f"k1-vendor-stop-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail="M27-D.1 stop command accepted via Move(0,0,0); physical stop not independently verified",
                zero_command_accepted=True,
                stop_command_accepted=True,
                physical_stop_verified=False,
                internal_command_state=self._motion_state.value,
            )
        except Exception as exc:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"k1-vendor-stop-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail=f"SDK stop failed: {sanitize_vendor_message(exc)}",
                internal_command_state=self._motion_state.value,
            )

    def restore_safe_state(self) -> None:
        """Restore robot to safe non-moving state. Best-effort."""
        try:
            if self._client is not None:
                try:
                    self._client.Move(0.0, 0.0, 0.0)
                except Exception:
                    pass
        finally:
            self._motion_state = MotionLifecycleState.SAFE_STOPPED

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        """Read odometry. Returns None when unavailable.

        The verified repository subscribes to /odometer_state via ROS2.
        Direct SDK odometry reading is not yet verified for the binding.
        Returns None to indicate unavailable until hardware bench verifies.
        """
        self._require_connected()
        # Odometry is typically available via ROS2 /odometer_state topic,
        # not through the direct SDK client API. Return structured None.
        return None

    def read_robot_state(self) -> BoosterK1RuntimeState:
        """Read robot state. Returns best-effort state from SDK.

        The verified repository subscribes to /robot_states via ROS2.
        Direct SDK GetMode() evidence is provisional and optional only.
        """
        self._require_connected()
        now_ns = self.now_ns_fn()
        try:
            # Attempt to read mode from SDK if available
            mode = getattr(self._client, "GetMode", None)
            if mode is not None:
                raw_mode = mode()
                mode_name = str(raw_mode)
            else:
                mode_name = "unknown"
        except Exception:
            mode_name = "unavailable"

        return BoosterK1RuntimeState(
            motion_state=self._motion_state,
            mode_name=mode_name,
            source_monotonic_ns=now_ns,
            battery_percentage=None,
            battery_voltage=None,
            metadata={
                "sdk_family": "booster_k1",
                "binding_version": BINDING_VERSION,
                "reading_method": "sdk_optional_unverified_GetMode" if hasattr(self._client, "GetMode") else "inferred",
                "get_mode_verified": False,
                "physical_safe_state_evidence": False,
            },
        )

    def read_battery_state(self) -> dict[str, float] | None:
        """Read battery state. Returns None when unavailable.

        Direct SDK battery reading is not yet verified.
        Returns None until hardware bench verifies.
        """
        self._require_connected()
        return None

    def health_check(self) -> BoosterK1RuntimeHealth:
        """Check binding readiness; transport communication is not verified."""
        now_ns = self.now_ns_fn()
        if not self._connected:
            return BoosterK1RuntimeHealth(
                healthy=False,
                checked_monotonic_ns=now_ns,
                detail="K1 vendor binding is not connected",
                scope="binding_readiness",
                communication_verified=False,
            )
        if self._client is None:
            return BoosterK1RuntimeHealth(
                healthy=False,
                checked_monotonic_ns=now_ns,
                detail="K1 vendor binding has no active client",
                scope="binding_readiness",
                communication_verified=False,
            )
        return BoosterK1RuntimeHealth(
            healthy=True,
            checked_monotonic_ns=now_ns,
            detail=(
                "binding object and client handle are present; transport "
                "communication was not independently verified"
            ),
            scope="binding_readiness",
            communication_verified=False,
        )

    # --- Internal helpers ---

    def _require_connected(self) -> None:
        if not self._connected:
            raise BoosterK1DomainError(
                ERROR_K1_CONNECTION_FAILED,
                "K1 vendor binding is not connected",
                retryable=True,
            )


def create_vendor_binding(
    *,
    hardware_gate: BoosterK1HardwareGate | None,
    now_ns: int,
    expected_robot_id: str,
    expected_safety_policy_id: str,
    expected_safety_policy_hash: str,
    enable_vendor_runtime: bool = False,
    execute_hardware: bool = False,
    interface: str = "lo",
    clock_fn: Any = None,
) -> BoosterK1VendorBinding:
    """Construction-order factory for the vendor binding.

    Evaluates conditions in mandated order:
    1. hardware gate exists
    2. gate is complete and unexpired
    3. robot ID matches
    4. safety policy ID and hash match
    5. vendor runtime is explicitly enabled
    6. hardware execution is explicitly enabled
    7. SDK is discoverable
    8. explicit SDK import succeeds
    9. vendor binding construction succeeds
    10. binding object is returned

    No SDK import occurs before steps 1-6 pass.
    """
    # Step 1: hardware gate exists
    if hardware_gate is None:
        raise BoosterK1DomainError(
            ERROR_K1_HARDWARE_GATE_MISSING,
            "Booster K1 vendor binding requires an explicit hardware gate",
            retryable=False,
        )

    # Step 2-4: gate validation
    gate_errors = hardware_gate.validate(
        now_ns=now_ns,
        expected_robot_id=expected_robot_id,
        expected_safety_policy_id=expected_safety_policy_id,
        expected_safety_policy_hash=expected_safety_policy_hash,
    )
    if gate_errors:
        raise BoosterK1DomainError(
            gate_errors[0].code,
            gate_errors[0].message,
            retryable=gate_errors[0].retryable,
            details=gate_errors[0].details,
        )

    # Step 5: adapter mode is vendor_runtime (validated by hardware gate).

    # Step 6: vendor runtime explicitly enabled
    if not enable_vendor_runtime:
        raise BoosterK1DomainError(
            ERROR_K1_VENDOR_RUNTIME_DISABLED,
            "Booster K1 vendor runtime is not explicitly enabled",
            retryable=False,
        )

    # Step 7: hardware execution explicitly enabled
    if not execute_hardware:
        raise BoosterK1DomainError(
            ERROR_K1_HARDWARE_EXECUTION_DISABLED,
            "Booster K1 hardware execution is not explicitly enabled",
            retryable=False,
        )

    # Step 8: direct SDK entry modules discoverable
    detection = detect_booster_sdk_availability_detailed()
    if not detection.direct_entry_modules_discoverable:
        raise BoosterK1DomainError(
            ERROR_K1_SDK_UNAVAILABLE,
            "Booster K1 direct SDK entry modules are not discoverable",
            retryable=False,
            details={"detection": detection.to_dict()},
        )

    # Steps 9-10: import SDK and construct binding
    try:
        binding = BoosterK1VendorBinding.create_with_sdk_import(
            interface=interface,
            now_ns_fn=clock_fn,
        )
    except BoosterK1DomainError:
        raise
    except Exception as exc:
        raise BoosterK1DomainError(
            ERROR_K1_BINDING_CONSTRUCTION_FAILED,
            f"Failed to construct Booster K1 vendor binding: {exc}",
            retryable=False,
            cause_type=type(exc).__name__,
        ) from exc

    # Step 10: return
    return binding
