"""Strict hardware-free mock robot adapter for M26-C dry-run flows."""
from __future__ import annotations

from dataclasses import dataclass, field

from calibration_skill.domain.capabilities import CapabilityDescriptor, CapabilityRecord
from calibration_skill.domain.enums import (
    CAPABILITY_BATTERY_TELEMETRY,
    CAPABILITY_BODY_VELOCITY_TELEMETRY,
    CAPABILITY_COMMAND_ACKNOWLEDGEMENT,
    CAPABILITY_COMMAND_TTL,
    CAPABILITY_CONNECT,
    CAPABILITY_DISCONNECT,
    CAPABILITY_DRY_RUN,
    CAPABILITY_EMERGENCY_STOP,
    CAPABILITY_EXPLICIT_STOP,
    CAPABILITY_FIRMWARE_VERSION_REPORTING,
    CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND,
    CAPABILITY_IMU_TELEMETRY,
    CAPABILITY_LOCOMOTION_MODE_TRANSITION,
    CAPABILITY_OPERATOR_CONFIRMATION,
    CAPABILITY_PLATFORM_VERSION_REPORTING,
    CAPABILITY_POSE_ODOMETRY_TELEMETRY,
    CAPABILITY_ROBOT_MODE_OBSERVATION,
    CAPABILITY_SIMULATOR,
    CAPABILITY_STATE_STREAM,
    CAPABILITY_VELOCITY_X,
    CAPABILITY_VELOCITY_Y,
    CAPABILITY_YAW_HEADING_TELEMETRY,
    CAPABILITY_YAW_RATE,
    CapabilitySupport,
    CommandDisposition,
    ConnectionState,
    CoordinateFrame,
    EvidenceLevel,
    ImplementationMaturity,
    MotionLifecycleState,
    PreflightStatus,
    RobotMorphology,
    RobotPlatform,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_ADAPTER_DISCONNECTED,
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_INVALID_FRAME,
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
from calibration_skill.domain.telemetry import TelemetrySample, Twist3D, Vector3
from calibration_skill.ports.factory import ConnectionConfig

MOCK_ADAPTER_VERSION = "m26c.mock.1"


@dataclass
class DeterministicMonotonicClock:
    """Manual monotonic clock for hermetic tests and dry-run composition."""
    current_ns: int = 1_000_000_000
    step_ns: int = 10_000_000

    def now_ns(self) -> int:
        return self.current_ns

    def tick(self) -> int:
        self.current_ns += self.step_ns
        return self.current_ns

    def advance_ns(self, delta_ns: int) -> int:
        if delta_ns < 0:
            raise ValueError("delta_ns must be non-negative")
        self.current_ns += delta_ns
        return self.current_ns


@dataclass(frozen=True)
class MockFailureConfig:
    """Deterministic failure injection switches for MockRobotAdapter."""
    preflight_blocker: bool = False
    connection_failure: bool = False
    locomotion_transition_failure: bool = False
    command_rejection: bool = False
    stale_telemetry: bool = False
    stop_unacknowledged: bool = False


def default_mock_capabilities(*, simulated_imu: bool = False, simulated_battery: bool = False) -> CapabilityDescriptor:
    supported = (
        CAPABILITY_CONNECT,
        CAPABILITY_DISCONNECT,
        CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND,
        CAPABILITY_VELOCITY_X,
        CAPABILITY_VELOCITY_Y,
        CAPABILITY_YAW_RATE,
        CAPABILITY_EXPLICIT_STOP,
        CAPABILITY_LOCOMOTION_MODE_TRANSITION,
        CAPABILITY_ROBOT_MODE_OBSERVATION,
        CAPABILITY_BODY_VELOCITY_TELEMETRY,
        CAPABILITY_POSE_ODOMETRY_TELEMETRY,
        CAPABILITY_YAW_HEADING_TELEMETRY,
        CAPABILITY_COMMAND_ACKNOWLEDGEMENT,
        CAPABILITY_STATE_STREAM,
        CAPABILITY_SIMULATOR,
        CAPABILITY_DRY_RUN,
        CAPABILITY_COMMAND_TTL,
        CAPABILITY_OPERATOR_CONFIRMATION,
        CAPABILITY_PLATFORM_VERSION_REPORTING,
    )
    records: list[CapabilityRecord] = [
        CapabilityRecord(
            capability_id=capability_id,
            support=CapabilitySupport.SUPPORTED,
            evidence=EvidenceLevel.BENCH_VERIFIED,
            maturity=ImplementationMaturity.BENCH_VERIFIED,
            notes="M26-C mock dry-run capability; no hardware evidence claimed.",
        )
        for capability_id in supported
    ]
    records.append(CapabilityRecord(
        capability_id=CAPABILITY_IMU_TELEMETRY,
        support=CapabilitySupport.SUPPORTED if simulated_imu else CapabilitySupport.UNKNOWN,
        evidence=EvidenceLevel.BENCH_VERIFIED if simulated_imu else EvidenceLevel.NONE,
        maturity=ImplementationMaturity.BENCH_VERIFIED if simulated_imu else ImplementationMaturity.NOT_STARTED,
    ))
    records.append(CapabilityRecord(
        capability_id=CAPABILITY_BATTERY_TELEMETRY,
        support=CapabilitySupport.SUPPORTED if simulated_battery else CapabilitySupport.UNSUPPORTED,
        evidence=EvidenceLevel.BENCH_VERIFIED if simulated_battery else EvidenceLevel.NONE,
        maturity=ImplementationMaturity.BENCH_VERIFIED if simulated_battery else ImplementationMaturity.UNSUPPORTED,
    ))
    records.append(CapabilityRecord(
        capability_id=CAPABILITY_EMERGENCY_STOP,
        support=CapabilitySupport.UNSUPPORTED,
        evidence=EvidenceLevel.NONE,
        maturity=ImplementationMaturity.UNSUPPORTED,
        notes="Ordinary mock stop is implemented; emergency-stop port is separate and not claimed.",
    ))
    records.append(CapabilityRecord(
        capability_id=CAPABILITY_FIRMWARE_VERSION_REPORTING,
        support=CapabilitySupport.UNSUPPORTED,
        evidence=EvidenceLevel.NONE,
        maturity=ImplementationMaturity.UNSUPPORTED,
    ))
    return CapabilityDescriptor(platform_id=RobotPlatform.MOCK.value, capabilities=tuple(records))


def default_mock_identity(robot_id: str = "mock-robot") -> RobotIdentity:
    return RobotIdentity(
        platform=RobotPlatform.MOCK,
        morphology=RobotMorphology.SYNTHETIC,
        robot_id=robot_id,
        adapter_name="MockRobotAdapter",
        adapter_version=MOCK_ADAPTER_VERSION,
        sdk_family=None,
        sdk_version=None,
        metadata=(("hardware_free", True), ("m26c_dry_run_only", True)),
    )


@dataclass
class MockRobotAdapter:
    """RobotAdapter-compatible mock that never talks to hardware."""
    config: ConnectionConfig
    clock: DeterministicMonotonicClock
    identity_value: RobotIdentity | None = None
    capabilities_value: CapabilityDescriptor = field(default_factory=default_mock_capabilities)
    failure_config: MockFailureConfig = field(default_factory=MockFailureConfig)
    safety_envelope: SafetyEnvelope | None = None
    operator_authorization: OperatorAuthorization | None = None
    authorized_operation: str = "dry_run_velocity_command"
    _connection_state: ConnectionState = ConnectionState.DISCONNECTED
    _motion_state: MotionLifecycleState = MotionLifecycleState.UNAVAILABLE
    _telemetry_sequence: int = 0
    _receipt_sequence: int = 0
    receipts: list[CommandReceipt] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.config.platform != RobotPlatform.MOCK:
            raise ValueError("MockRobotAdapter requires mock platform ConnectionConfig")
        if self.identity_value is None:
            self.identity_value = default_mock_identity(self.config.robot_id)

    @property
    def identity(self) -> RobotIdentity:
        assert self.identity_value is not None
        return self.identity_value

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
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        if self.failure_config.connection_failure:
            self._connection_state = ConnectionState.FAULTED
            self._motion_state = MotionLifecycleState.FAULTED
            raise RuntimeError("mock connection failure")
        self._connection_state = ConnectionState.CONNECTED
        self._motion_state = MotionLifecycleState.IDLE
        self.clock.tick()

    def disconnect(self) -> None:
        self._connection_state = ConnectionState.DISCONNECTED
        self._motion_state = MotionLifecycleState.UNAVAILABLE
        self.clock.tick()

    def preflight(self) -> PreflightReport:
        checked_ns = self.clock.tick()
        status = PreflightStatus.FAILED if self.failure_config.preflight_blocker else PreflightStatus.PASSED
        detail = "Injected mock preflight blocker" if self.failure_config.preflight_blocker else "Mock dry-run preflight passed"
        return PreflightReport(
            platform=RobotPlatform.MOCK,
            robot_id=self.identity.robot_id,
            checked_monotonic_ns=checked_ns,
            checks=(PreflightCheck("mock.preflight", "Mock preflight", status, detail, "mock-preflight"),),
            safety_policy_ref=self.safety_envelope.policy_id if self.safety_envelope else None,
            evidence_refs=("m26c.mock.preflight",),
        )

    def enter_locomotion_ready(self) -> None:
        if self._connection_state != ConnectionState.CONNECTED:
            raise RuntimeError("mock adapter disconnected")
        if self.failure_config.locomotion_transition_failure:
            self._motion_state = MotionLifecycleState.FAULTED
            raise RuntimeError("mock locomotion transition failure")
        self._motion_state = MotionLifecycleState.LOCOMOTION_READY
        self.clock.tick()

    def send_velocity_command(self, command: VelocityCommand) -> CommandReceipt:
        now_ns = self.clock.tick()
        error = self._command_rejection_error(command, now_ns)
        if error is not None:
            disposition = CommandDisposition.EXPIRED if error.code == ERROR_COMMAND_EXPIRED else CommandDisposition.REJECTED
            receipt = CommandReceipt(
                command_sequence_id=command.sequence_id,
                disposition=disposition,
                received_monotonic_ns=now_ns,
                rejection_error=error,
                adapter_state=self._motion_state.value,
                acknowledgement_evidence="mock-dry-run-rejection",
            )
            self.receipts.append(receipt)
            return receipt
        self._receipt_sequence += 1
        self._motion_state = MotionLifecycleState.MOVING
        receipt = CommandReceipt(
            command_sequence_id=command.sequence_id,
            disposition=CommandDisposition.ACCEPTED,
            adapter_receipt_id=f"mock-receipt-{self._receipt_sequence:04d}",
            received_monotonic_ns=now_ns,
            accepted_monotonic_ns=now_ns,
            adapter_state=self._motion_state.value,
            acknowledgement_evidence="mock-dry-run-accepted-no-physical-motion",
        )
        self.receipts.append(receipt)
        return receipt

    def stop(self) -> CommandReceipt:
        now_ns = self.clock.tick()
        self._receipt_sequence += 1
        if self.failure_config.stop_unacknowledged:
            error = DomainError(
                code=ERROR_STOP_UNACKNOWLEDGED,
                message="Injected mock stop unacknowledged",
                retryable=True,
            )
            receipt = CommandReceipt(
                command_sequence_id=f"mock-stop-{self._receipt_sequence:04d}",
                disposition=CommandDisposition.REJECTED,
                received_monotonic_ns=now_ns,
                rejection_error=error,
                adapter_state=self._motion_state.value,
                acknowledgement_evidence="mock-stop-unacknowledged",
            )
            self.receipts.append(receipt)
            return receipt
        self._motion_state = MotionLifecycleState.SAFE_STOPPED
        receipt = CommandReceipt(
            command_sequence_id=f"mock-stop-{self._receipt_sequence:04d}",
            disposition=CommandDisposition.ACCEPTED,
            adapter_receipt_id=f"mock-stop-receipt-{self._receipt_sequence:04d}",
            received_monotonic_ns=now_ns,
            accepted_monotonic_ns=now_ns,
            adapter_state=self._motion_state.value,
            acknowledgement_evidence="mock-stop-accepted-no-physical-motion",
        )
        self.receipts.append(receipt)
        return receipt

    def restore_safe_state(self) -> None:
        self._motion_state = MotionLifecycleState.SAFE_STOPPED
        self.clock.tick()

    def collect_telemetry_sample(self) -> TelemetrySample:
        self._telemetry_sequence += 1
        now_ns = self.clock.tick()
        received_ns = now_ns
        flags: tuple[str, ...] = ("mock", "dry_run")
        if self.failure_config.stale_telemetry:
            received_ns = max(0, now_ns - 10_000_000_000)
            flags = ("mock", "dry_run", "stale_injected")
        return TelemetrySample(
            robot_id=self.identity.robot_id,
            sample_sequence_id=self._telemetry_sequence,
            received_monotonic_ns=received_ns,
            frame=CoordinateFrame.BODY,
            body_twist=Twist3D(linear=Vector3(0.0, 0.0, 0.0), angular=Vector3(0.0, 0.0, 0.0)),
            heading_rad=0.0,
            robot_mode=self._motion_state.value,
            source_adapter=self.identity.adapter_name,
            quality_flags=flags,
            raw_reference=None,
        )

    def _command_rejection_error(self, command: VelocityCommand, now_ns: int) -> DomainError | None:
        if self._connection_state != ConnectionState.CONNECTED:
            return DomainError(ERROR_ADAPTER_DISCONNECTED, "Mock adapter is disconnected", retryable=True)
        if self._motion_state != MotionLifecycleState.LOCOMOTION_READY:
            return DomainError(
                ERROR_WRONG_MOTION_STATE,
                "Mock adapter is not locomotion_ready",
                retryable=True,
                details={"motion_state": self._motion_state.value},
            )
        if command.is_expired(now_ns):
            return DomainError(ERROR_COMMAND_EXPIRED, "Velocity command expired before mock dispatch", retryable=False)
        if self.safety_envelope is None:
            return DomainError(ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE, "Safety envelope is required", retryable=False)
        safety_errors = self._validate_command_against_safety(command)
        if safety_errors:
            return safety_errors[0]
        if self.safety_envelope.operator_authorization_required:
            if self.operator_authorization is None:
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "Operator authorization is required", retryable=False)
            auth_errors = self.operator_authorization.validate(now_ns)
            if auth_errors:
                return auth_errors[0]
            if not self.operator_authorization.matches_platform(RobotPlatform.MOCK, self.identity.robot_id):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "Authorization platform or robot mismatch", retryable=False)
            if not self.operator_authorization.check_operation(self.authorized_operation):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED, "Authorization does not include operation", retryable=False)
            if (
                self.operator_authorization.safety_policy_id != self.safety_envelope.policy_id
                or self.operator_authorization.safety_policy_hash != self.safety_envelope.policy_hash
            ):
                return DomainError(ERROR_OPERATOR_AUTHORIZATION_EXPIRED, "Authorization safety policy mismatch", retryable=False)
        if self.failure_config.command_rejection:
            return DomainError(ERROR_PRECONDITION_FAILED, "Injected mock command rejection", retryable=False)
        return None

    def _validate_command_against_safety(self, command: VelocityCommand) -> list[DomainError]:
        assert self.safety_envelope is not None
        errors: list[DomainError] = []
        if abs(command.vx_mps) > self.safety_envelope.max_abs_vx_mps:
            errors.append(DomainError(
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                f"|vx|={abs(command.vx_mps):.4f} exceeds max_abs_vx_mps={self.safety_envelope.max_abs_vx_mps}",
                retryable=False,
                details={"field": "vx_mps", "value": command.vx_mps, "max": self.safety_envelope.max_abs_vx_mps},
            ))
        if abs(command.vy_mps) > self.safety_envelope.max_abs_vy_mps:
            errors.append(DomainError(
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                f"|vy|={abs(command.vy_mps):.4f} exceeds max_abs_vy_mps={self.safety_envelope.max_abs_vy_mps}",
                retryable=False,
                details={"field": "vy_mps", "value": command.vy_mps, "max": self.safety_envelope.max_abs_vy_mps},
            ))
        if abs(command.wz_radps) > self.safety_envelope.max_abs_wz_radps:
            errors.append(DomainError(
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                f"|wz|={abs(command.wz_radps):.4f} exceeds max_abs_wz_radps={self.safety_envelope.max_abs_wz_radps}",
                retryable=False,
                details={"field": "wz_radps", "value": command.wz_radps, "max": self.safety_envelope.max_abs_wz_radps},
            ))
        if command.requested_duration_s > self.safety_envelope.max_command_duration_s:
            errors.append(DomainError(
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                "command duration exceeds safety envelope",
                retryable=False,
                details={"field": "requested_duration_s"},
            ))
        if command.frame not in self.safety_envelope.allowed_command_frames:
            errors.append(DomainError(
                ERROR_INVALID_FRAME,
                f"frame {command.frame.value} not allowed",
                retryable=False,
            ))
        if command.safety_policy_id != self.safety_envelope.policy_id:
            errors.append(DomainError(ERROR_INVALID_SAFETY_POLICY, "safety_policy_id mismatch", retryable=False))
        if command.safety_policy_hash != self.safety_envelope.policy_hash:
            errors.append(DomainError(ERROR_INVALID_SAFETY_POLICY, "safety_policy_hash mismatch", retryable=False))
        return errors
