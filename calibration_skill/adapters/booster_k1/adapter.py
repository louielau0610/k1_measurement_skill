"""Booster K1 adapter supporting both fake and vendor runtime modes.

M27-D: Refactored to distinguish fake_booster_runtime and vendor_runtime.
Fake mode remains dry-run-only as in M27-B. Vendor mode requires
dry_run=False, allow_hardware=True, and a validated hardware gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.adapters.booster_k1.config import (
    BoosterK1AdapterConfig,
    K1_FAKE_RUNTIME_MODE,
    K1_VENDOR_RUNTIME_MODE,
    BoosterK1HardwareGate,
)
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_HARDWARE_GATE_CLOSED,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_RUNTIME_MODE_UNSUPPORTED,
    ERROR_K1_RUNTIME_UNHEALTHY,
    ERROR_K1_UNSUPPORTED_AXIS,
)
from calibration_skill.adapters.booster_k1.identity import booster_k1_identity
from calibration_skill.adapters.booster_k1.runtime import BoosterK1RuntimeProtocol
from calibration_skill.domain.capabilities import CapabilityDescriptor
from calibration_skill.domain.enums import (
    CommandDisposition,
    ConnectionState,
    CoordinateFrame,
    MotionLifecycleState,
    PreflightStatus,
    RobotPlatform,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_ADAPTER_DISCONNECTED,
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_INVALID_SAFETY_POLICY,
    ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
    ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
    ERROR_PRECONDITION_FAILED,
    ERROR_STOP_UNACKNOWLEDGED,
    ERROR_WRONG_MOTION_STATE,
)
from calibration_skill.domain.identity import RobotIdentity
from calibration_skill.domain.motion import CommandReceipt, VelocityCommand
from calibration_skill.domain.safety import OperatorAuthorization, PreflightCheck, PreflightReport, SafetyEnvelope
from calibration_skill.domain.telemetry import Pose3D, Quaternion, TelemetrySample, Twist3D, Vector3


@dataclass
class BoosterK1Adapter:
    """RobotAdapter-compatible K1 adapter supporting fake and vendor runtimes."""
    config: BoosterK1AdapterConfig
    runtime: BoosterK1RuntimeProtocol
    capabilities_value: CapabilityDescriptor = field(default_factory=booster_k1_capabilities)
    operator_authorization: OperatorAuthorization | None = None
    authorized_operation: str = "k1_fake_runtime_velocity_command"
    cleanup_on_command_failure: bool = True
    _connection_state: ConnectionState = ConnectionState.DISCONNECTED
    _motion_state: MotionLifecycleState = MotionLifecycleState.UNAVAILABLE
    _receipt_sequence: int = 0

    def __post_init__(self) -> None:
        self._validate_runtime_mode()
        self._identity = booster_k1_identity(self.config, self.runtime.identity_metadata())
        self.safety_envelope = self.config.to_safety_envelope()

    def _validate_runtime_mode(self) -> None:
        """Validate runtime mode and hardware configuration."""
        mode = self.config.runtime_mode
        if mode == K1_FAKE_RUNTIME_MODE:
            # M27-B fake runtime: must be dry-run, no hardware
            if not self.config.dry_run or self.config.allow_hardware:
                raise ValueError("M27-B BoosterK1Adapter requires dry_run=true and allow_hardware=false for fake runtime")
            self.authorized_operation = "k1_fake_runtime_velocity_command"
        elif mode == K1_VENDOR_RUNTIME_MODE:
            # M27-D vendor runtime: requires dry_run=False, allow_hardware=True
            if self.config.dry_run or not self.config.allow_hardware:
                raise ValueError("M27-D BoosterK1Adapter requires dry_run=false and allow_hardware=true for vendor runtime")
            self.authorized_operation = "k1_vendor_runtime_velocity_command"
        else:
            raise ValueError(f"Unsupported K1 runtime mode: {mode}")

    @property
    def is_vendor_mode(self) -> bool:
        return self.config.runtime_mode == K1_VENDOR_RUNTIME_MODE

    @property
    def identity(self) -> RobotIdentity:
        return self._identity

    @property
    def capabilities(self) -> CapabilityDescriptor:
        return self.capabilities_value

    @property
    def connection_state(self) -> ConnectionState:
        return self._connection_state

    @property
    def motion_state(self) -> MotionLifecycleState:
        return self._motion_state

    def configure_command_context(
        self,
        safety_envelope: SafetyEnvelope,
        authorization: OperatorAuthorization | None,
        operation: str,
    ) -> None:
        self.safety_envelope = safety_envelope
        self.operator_authorization = authorization
        self.authorized_operation = operation

    def connect(self, timeout_s: float = 10.0) -> None:
        self.runtime.connect(timeout_s=timeout_s)
        self._connection_state = ConnectionState.CONNECTED
        self._motion_state = self.runtime.current_motion_state()

    def disconnect(self) -> None:
        self.runtime.disconnect()
        self._connection_state = ConnectionState.DISCONNECTED
        self._motion_state = MotionLifecycleState.UNAVAILABLE

    def preflight(self) -> PreflightReport:
        now_ns = self.runtime.now_ns()
        checks: list[PreflightCheck] = []

        if self.is_vendor_mode:
            # Vendor mode preflight checks
            checks.append(self._check(
                "k1.vendor_hardware",
                "K1 vendor hardware gate",
                not self.config.dry_run and self.config.allow_hardware,
                "K1 vendor mode configured with hardware enabled.",
                "K1 vendor mode requires hardware enabled.",
                ERROR_K1_HARDWARE_GATE_CLOSED,
            ))
            checks.append(self._check(
                "k1.runtime_mode",
                "K1 runtime mode",
                self.config.runtime_mode == K1_VENDOR_RUNTIME_MODE,
                "Vendor Booster runtime selected.",
                "Vendor runtime mode expected.",
                ERROR_K1_RUNTIME_MODE_UNSUPPORTED,
            ))
            evidence_refs = ("m27d_vendor_runtime_preflight",)
        else:
            # Fake mode preflight checks (M27-B compatible)
            checks.append(self._check(
                "k1.dry_run",
                "K1 dry-run gate",
                self.config.dry_run and not self.config.allow_hardware,
                "M27-B K1 adapter is dry-run fake-runtime only.",
                "Hardware mode is not permitted in M27-B.",
                ERROR_K1_HARDWARE_GATE_CLOSED,
            ))
            checks.append(self._check(
                "k1.runtime_mode",
                "K1 runtime mode",
                self.config.runtime_mode == K1_FAKE_RUNTIME_MODE,
                "Fake Booster runtime selected.",
                "Only fake_booster_runtime is supported in M27-B.",
                ERROR_K1_RUNTIME_MODE_UNSUPPORTED,
            ))
            evidence_refs = ("m27b_fake_runtime_preflight",)

        health = self.runtime.health_check()
        checks.append(self._check(
            "k1.runtime_health",
            "K1 runtime health",
            health.healthy,
            health.detail or "Runtime health check passed.",
            health.detail or "Runtime health check failed.",
            ERROR_K1_RUNTIME_UNHEALTHY,
        ))
        return PreflightReport(
            platform=RobotPlatform.BOOSTER_K1,
            robot_id=self.config.robot_id,
            checked_monotonic_ns=now_ns,
            checks=tuple(checks),
            safety_policy_ref=self.safety_envelope.policy_id,
            evidence_refs=evidence_refs,
        )

    def enter_locomotion_ready(self) -> None:
        if self._connection_state != ConnectionState.CONNECTED:
            raise RuntimeError("K1 fake adapter disconnected")
        self._motion_state = MotionLifecycleState.PREPARING
        self.runtime.enter_prepare_mode()
        self.runtime.enter_walking_mode()
        self._motion_state = MotionLifecycleState.LOCOMOTION_READY

    def send_velocity_command(self, command: VelocityCommand) -> CommandReceipt:
        now_ns = self.runtime.now_ns()
        error = self._command_rejection_error(command, now_ns)
        if error is not None:
            receipt = self._rejected_receipt(command.sequence_id, now_ns, error)
            if self.cleanup_on_command_failure and error.code not in {ERROR_ADAPTER_DISCONNECTED, ERROR_COMMAND_EXPIRED}:
                self.runtime.stop()
            return receipt

        runtime_receipt = self.runtime.send_body_velocity(vx_mps=command.vx_mps, vy_mps=0.0, wz_radps=0.0)
        if not runtime_receipt.accepted:
            error = DomainError(
                ERROR_PRECONDITION_FAILED,
                runtime_receipt.detail or "Runtime rejected K1 velocity command",
                retryable=False,
            )
            return self._rejected_receipt(command.sequence_id, runtime_receipt.received_monotonic_ns, error)

        self._motion_state = MotionLifecycleState.MOVING
        evidence_prefix = "m27d-vendor" if self.is_vendor_mode else "m27b-fake"
        return CommandReceipt(
            command_sequence_id=command.sequence_id,
            disposition=CommandDisposition.ACCEPTED,
            adapter_receipt_id=runtime_receipt.runtime_receipt_id,
            received_monotonic_ns=runtime_receipt.received_monotonic_ns,
            accepted_monotonic_ns=runtime_receipt.received_monotonic_ns,
            adapter_state=self._motion_state.value,
            acknowledgement_evidence=f"{evidence_prefix}-runtime-receipt-no-physical-motion",
        )

    def stop(self) -> CommandReceipt:
        runtime_receipt = self.runtime.stop()
        evidence_prefix = "m27d-vendor" if self.is_vendor_mode else "m27b-fake"
        if not runtime_receipt.accepted:
            error = DomainError(ERROR_STOP_UNACKNOWLEDGED, runtime_receipt.detail or "K1 stop unacknowledged", retryable=True)
            return CommandReceipt(
                command_sequence_id=runtime_receipt.runtime_receipt_id,
                disposition=CommandDisposition.REJECTED,
                received_monotonic_ns=runtime_receipt.received_monotonic_ns,
                rejection_error=error,
                adapter_state=self._motion_state.value,
                acknowledgement_evidence=f"{evidence_prefix}-runtime-stop-unacknowledged",
            )
        self._motion_state = MotionLifecycleState.SAFE_STOPPED
        return CommandReceipt(
            command_sequence_id=runtime_receipt.runtime_receipt_id,
            disposition=CommandDisposition.ACCEPTED,
            adapter_receipt_id=runtime_receipt.runtime_receipt_id,
            received_monotonic_ns=runtime_receipt.received_monotonic_ns,
            accepted_monotonic_ns=runtime_receipt.received_monotonic_ns,
            adapter_state=self._motion_state.value,
            acknowledgement_evidence=f"{evidence_prefix}-runtime-stop-accepted",
        )

    def restore_safe_state(self) -> None:
        self.runtime.restore_safe_state()
        self._motion_state = MotionLifecycleState.SAFE_STOPPED

    def collect_telemetry_sample(self) -> TelemetrySample:
        state = self.runtime.read_robot_state()
        odom = self.runtime.read_odometry()
        battery = self.runtime.read_battery_state()
        battery_percentage = state.battery_percentage
        battery_voltage = state.battery_voltage
        if battery is not None:
            battery_percentage = battery.get("battery_percentage", battery_percentage)
            battery_voltage = battery.get("battery_voltage", battery_voltage)
        pose = None
        body_twist = None
        heading_rad = None
        sample_sequence = 0
        received_ns = state.source_monotonic_ns
        if self.is_vendor_mode:
            flags = ["m27d_vendor_runtime"]
            evidence = "m27d-vendor-runtime-telemetry"
        else:
            flags = ["m27b_fake_runtime", "no_hardware"]
            evidence = "m27b-fake-runtime-telemetry"
        if odom is not None:
            sample_sequence = odom.sequence_id
            received_ns = odom.sample_monotonic_ns
            heading_rad = odom.yaw_rad
            pose = Pose3D(position=Vector3(odom.x_m, odom.y_m, odom.z_m), orientation=Quaternion())
            body_twist = Twist3D(
                linear=Vector3(odom.vx_mps or 0.0, odom.vy_mps or 0.0, 0.0),
                angular=Vector3(0.0, 0.0, odom.wz_radps or 0.0),
            )
        else:
            flags.append("odometry_unavailable")
        return TelemetrySample(
            robot_id=self.config.robot_id,
            sample_sequence_id=sample_sequence,
            received_monotonic_ns=received_ns,
            frame=CoordinateFrame.BODY,
            pose=pose,
            body_twist=body_twist,
            heading_rad=heading_rad,
            battery_voltage=battery_voltage,
            battery_percentage=battery_percentage,
            robot_mode=state.mode_name,
            source_adapter=self.identity.adapter_name,
            quality_flags=tuple(flags),
            raw_reference=None,
        )

    def _command_rejection_error(self, command: VelocityCommand, now_ns: int) -> DomainError | None:
        if self._connection_state != ConnectionState.CONNECTED:
            return DomainError(ERROR_ADAPTER_DISCONNECTED, "K1 fake adapter is disconnected", retryable=True)
        if self._motion_state != MotionLifecycleState.LOCOMOTION_READY:
            return DomainError(ERROR_WRONG_MOTION_STATE, "K1 fake adapter is not locomotion_ready", retryable=True)
        if command.is_expired(now_ns):
            return DomainError(ERROR_COMMAND_EXPIRED, "K1 fake command expired before dispatch", retryable=False)
        if self.config.legacy_forward_only and (command.vy_mps != 0.0 or command.wz_radps != 0.0):
            return DomainError(
                ERROR_K1_UNSUPPORTED_AXIS,
                "M27-B K1 skeleton supports only legacy forward vx commands",
                retryable=False,
                details={"vy_mps": command.vy_mps, "wz_radps": command.wz_radps},
            )
        safety_errors = self.safety_envelope.validate_command(command)
        if safety_errors:
            return safety_errors[0]
        if command.safety_policy_id != self.config.safety_policy_id or command.safety_policy_hash != self.config.safety_policy_hash:
            return DomainError(ERROR_INVALID_SAFETY_POLICY, "K1 command safety policy mismatch", retryable=False)
        if self.safety_envelope.operator_authorization_required:
            if self.operator_authorization is None:
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "K1 command requires operator authorization", retryable=False)
            auth_errors = self.operator_authorization.validate(now_ns)
            if auth_errors:
                return auth_errors[0]
            if not self.operator_authorization.matches_platform(RobotPlatform.BOOSTER_K1, self.config.robot_id):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "K1 authorization platform or robot mismatch", retryable=False)
            if not self.operator_authorization.check_operation(self.authorized_operation):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "K1 authorization does not include operation", retryable=False)
            if (
                self.operator_authorization.safety_policy_id != self.safety_envelope.policy_id
                or self.operator_authorization.safety_policy_hash != self.safety_envelope.policy_hash
            ):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_EXPIRED, "K1 authorization safety policy mismatch", retryable=False)
        return None

    def _rejected_receipt(self, sequence_id: str, now_ns: int, error: DomainError) -> CommandReceipt:
        disposition = CommandDisposition.EXPIRED if error.code == ERROR_COMMAND_EXPIRED else CommandDisposition.REJECTED
        return CommandReceipt(
            command_sequence_id=sequence_id,
            disposition=disposition,
            received_monotonic_ns=now_ns,
            rejection_error=error,
            adapter_state=self._motion_state.value,
            acknowledgement_evidence="m27b-fake-runtime-rejection-no-physical-motion",
        )

    def _check(
        self,
        check_id: str,
        name: str,
        passed: bool,
        pass_detail: str,
        fail_detail: str,
        error_code: str,
    ) -> PreflightCheck:
        return PreflightCheck(
            check_id=check_id,
            name=name,
            status=PreflightStatus.PASSED if passed else PreflightStatus.FAILED,
            detail=pass_detail if passed else fail_detail,
            evidence_ref=error_code if not passed else "m27b_fake_runtime",
        )
