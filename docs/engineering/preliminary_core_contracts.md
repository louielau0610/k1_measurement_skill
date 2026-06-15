# Preliminary Core Contracts — M26-A

**Date**: 2026-06-15
**Status**: Specification only (not implemented)
**Branch**: `engineering/m26a-program-reset-audit`

## Purpose

This document specifies preliminary interfaces and semantics for the core
contracts of the multi-platform calibration skill. These are **specifications**,
not implementations. They define the contract surface that all platform adapters
must satisfy.

## Contract Definitions

### RobotAdapter

```python
class RobotAdapter(Protocol):
    """Abstract interface for platform-specific robot control."""

    def connect(self, config: ConnectionConfig) -> None: ...
    def disconnect(self) -> None: ...
    def is_connected(self) -> bool: ...
    def get_identity(self) -> RobotIdentity: ...
    def get_capabilities(self) -> CapabilityDescriptor: ...
    def enter_motion_mode(self) -> None: ...
    def exit_motion_mode(self) -> None: ...
    def send_velocity(self, command: VelocityCommand) -> CommandReceipt: ...
    def stop(self) -> CommandReceipt: ...
    def emergency_stop(self) -> CommandReceipt: ...
    def get_telemetry_stream(self) -> TelemetryStream: ...
```

**Semantics**:
- `connect`: Establish communication. Must be idempotent (safe to call when already connected).
- `disconnect`: Graceful teardown. Must send stop before disconnecting if in motion mode.
- `send_velocity`: Validate against safety envelope before sending. Return receipt immediately.
- `stop`: Send zero-velocity command. Must be callable from any state.
- `emergency_stop`: Highest-priority stop. Must bypass normal command queue.
- `get_telemetry_stream`: Return live telemetry stream. Must raise if not connected.

### AdapterFactory

```python
class AdapterFactory(Protocol):
    """Creates platform adapters from configuration."""

    def supports_platform(self, identity: RobotIdentity) -> bool: ...
    def create_adapter(self, config: ConnectionConfig) -> RobotAdapter: ...
    def list_supported_platforms(self) -> list[RobotIdentity]: ...
```

**Semantics**:
- `supports_platform`: Check without creating adapter. Must not import vendor SDK.
- `create_adapter`: Create and return configured adapter. May import vendor SDK here.
- `list_supported_platforms`: Return identities of all registered platforms.

### CapabilityDescriptor

```python
@dataclass(frozen=True)
class CapabilityDescriptor:
    platform_id: str
    robot_model: str
    firmware_version: str | None
    supported_capabilities: dict[str, CapabilityStatus]
    # CapabilityStatus: verified_existing | upstream_documented | planned |
    #                    unsupported | unknown | requires_hardware_verification

    def has_capability(self, name: str) -> bool: ...
    def get_status(self, name: str) -> CapabilityStatus: ...
```

**Semantics**:
- Immutable after creation.
- `has_capability` returns True only for `verified_existing` status.
- Unknown capabilities must be explicitly queried, not assumed.

### RobotIdentity

```python
@dataclass(frozen=True)
class RobotIdentity:
    platform_id: str          # e.g., "booster_k1", "unitree_g1", "unitree_go1"
    robot_model: str          # e.g., "Booster K1", "Unitree G1", "Unitree GO1"
    morphology: str           # "biped_humanoid" | "quadruped"
    serial_number: str | None
    firmware_version: str | None
    sdk_version: str | None
```

**Semantics**:
- Immutable. Set once during connection.
- `platform_id` must match a registered platform.
- `morphology` must be one of the two supported classes.

### ConnectionConfig

```python
@dataclass(frozen=True)
class ConnectionConfig:
    platform_id: str
    network_interface: str | None     # e.g., "eth0", "192.168.123.10"
    dds_domain_id: int | None         # For DDS-based platforms
    udp_port: int | None              # For UDP-based platforms
    timeout_seconds: float
    extra: dict[str, Any]             # Platform-specific parameters
```

**Semantics**:
- Immutable. Validated at creation time.
- Platform-specific parameters go in `extra`, not as top-level fields.
- `timeout_seconds` applies to connection establishment, not command execution.

### MotionLifecycle

```python
class MotionLifecycle(Protocol):
    """Manages robot motion mode transitions."""

    def prepare(self) -> None: ...
    def enter_locomotion(self) -> None: ...
    def exit_locomotion(self) -> None: ...
    def get_current_mode(self) -> str: ...
    def is_locomotion_ready(self) -> bool: ...
```

**Semantics**:
- `prepare`: Platform-specific initialization (e.g., motor calibration, standing).
- `enter_locomotion`: Transition to walk/trot mode.
- `exit_locomotion`: Return to safe standing/sitting.
- `get_current_mode`: Must reflect actual robot state, not cached assumption.
- `is_locomotion_ready`: Must verify with robot, not just track internal state.

### VelocityCommand

```python
@dataclass(frozen=True)
class VelocityCommand:
    vx_mps: float                     # Forward velocity (m/s)
    vy_mps: float                     # Lateral velocity (m/s)
    wz_radps: float                   # Yaw rate (rad/s)
    sequence_id: int                  # Monotonic sequence number
    issued_monotonic_ns: int          # Issue timestamp (monotonic clock)
    expiry_monotonic_ns: int          # Expiry timestamp (monotonic clock)
    requested_duration_s: float       # Requested execution duration
    frame: str                        # Reference frame ("body" | "odom")
    safety_policy_id: str             # Identifies the safety policy applied
    safety_policy_hash: str           # Hash of the safety policy content
    source: str                       # Origin of command ("skill", "cli", "test")

    def is_expired(self, clock: MonotonicClock) -> bool: ...
    def validate(self, envelope: SafetyEnvelope) -> list[str]: ...
```

**Semantics**:
- **No silent maximum velocity default.** The safety envelope must be explicitly supplied.
- `is_expired`: True if current monotonic time > expiry_monotonic_ns.
- `validate`: Returns list of violation descriptions; empty list = valid.
- `frame`: "body" for robot-centric, "odom" for world-frame commands.
- Commands must not be sent if expired.
- Sequence IDs must be monotonically increasing per session.

### CommandReceipt

```python
@dataclass(frozen=True)
class CommandReceipt:
    command: VelocityCommand
    status: str                       # "accepted" | "rejected" | "expired" | "error"
    receipt_monotonic_ns: int         # When receipt was generated
    robot_timestamp_ns: int | None    # Robot's reported timestamp (if available)
    rejection_reasons: list[str]      # Reasons if rejected
    platform_specific: dict[str, Any] # Platform-specific receipt data
```

**Semantics**:
- `status == "accepted"` does not guarantee execution; only that the command was valid.
- `rejection_reasons` must be populated when status is "rejected".
- Receipt must be generated before any hardware communication.

### TelemetrySample

```python
@dataclass(frozen=True)
class TelemetrySample:
    platform_id: str
    sample_monotonic_ns: int          # When sample was received (monotonic clock)
    robot_timestamp_ns: int | None    # Robot's reported timestamp
    vx_mps: float | None              # Measured forward velocity
    vy_mps: float | None              # Measured lateral velocity
    wz_radps: float | None            # Measured yaw rate
    pose_x_m: float | None            # Odometry X position
    pose_y_m: float | None            # Odometry Y position
    heading_rad: float | None         # Heading / yaw
    imu_accel_x: float | None
    imu_accel_y: float | None
    imu_accel_z: float | None
    imu_gyro_x: float | None
    imu_gyro_y: float | None
    imu_gyro_z: float | None
    battery_voltage: float | None
    battery_percentage: float | None
    robot_mode: str | None
    extra: dict[str, Any]             # Platform-specific fields
```

**Semantics**:
- All fields except `platform_id` and `sample_monotonic_ns` are optional.
- A sample is "stale" if `clock.now() - sample_monotonic_ns > staleness_threshold`.
- Normalization from platform-specific formats happens in the adapter layer.

### TelemetryStream

```python
class TelemetryStream(Protocol):
    """Abstract interface for telemetry acquisition."""

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_active(self) -> bool: ...
    def get_latest(self) -> TelemetrySample | None: ...
    def get_recent(self, duration_ns: int) -> list[TelemetrySample]: ...
    def get_staleness_threshold_ns(self) -> int: ...
```

**Semantics**:
- `get_latest`: Return most recent sample or None if no data.
- `get_recent`: Return samples within the last `duration_ns` nanoseconds.
- Staleness threshold is platform-configurable.
- Stream must be stoppable from any state.

### PreflightReport

```python
@dataclass(frozen=True)
class PreflightReport:
    platform_id: str
    timestamp_utc: str
    checks: list[PreflightCheck]
    overall_status: str              # "passed" | "failed" | "warning"
    operator_notes: str

@dataclass(frozen=True)
class PreflightCheck:
    check_id: str
    name: str
    status: str                      # "passed" | "failed" | "warning" | "skipped"
    detail: str
    evidence_ref: str | None         # Reference to supporting evidence
```

**Semantics**:
- All checks must be explicitly enumerated.
- "skipped" status requires a reason in detail.
- Overall "failed" blocks progression to OperatorConfirmation.

### OperatorAuthorization

```python
@dataclass(frozen=True)
class OperatorAuthorization:
    operator_id: str
    authorized_at_utc: str
    expires_at_utc: str
    authorized_scope: list[str]       # e.g., ["velocity_calibration", "forward_only"]
    max_speed_mps: float
    max_duration_s: float
    confirmation_method: str          # "cli_prompt" | "physical_button" | "key_file"
    evidence_hash: str                # Hash of the authorization record
```

**Semantics**:
- Authorization expires at `expires_at_utc`. No commands after expiry.
- `authorized_scope` limits what the operator has explicitly permitted.
- `max_speed_mps` overrides safety envelope maximum if more restrictive.

### SafetyEnvelope

```python
@dataclass(frozen=True)
class SafetyEnvelope:
    policy_id: str
    policy_hash: str
    max_vx_mps: float
    max_vy_mps: float
    max_wz_radps: float
    max_command_duration_s: float
    staleness_threshold_ns: int
    requires_operator_confirmation: bool
    allowed_frames: list[str]

    def validate_command(self, command: VelocityCommand) -> list[str]: ...
```

**Semantics**:
- No implicit defaults for maximum values.
- `policy_hash` must match the hash in VelocityCommand.
- Validation returns list of violations; empty list = valid.
- Frame validation ensures commands are in an allowed reference frame.

### EmergencyStop

```python
class EmergencyStop(Protocol):
    """Hardware-level emergency stop mechanism."""

    def trigger(self, reason: str) -> CommandReceipt: ...
    def is_triggered(self) -> bool: ...
    def reset(self) -> None: ...      # Requires explicit operator action
```

**Semantics**:
- `trigger`: Send highest-priority stop. Must work even if normal command path is blocked.
- `is_triggered`: True if emergency stop is active.
- `reset`: Must require explicit operator action; cannot be called programmatically without authorization.

### TrialPlan

```python
@dataclass(frozen=True)
class TrialPlan:
    plan_id: str
    platform_id: str
    surface_type: str
    commands: list[VelocityCommand]
    repeats: int
    randomization: str                # "blocked" | "fully_randomized"
    safety_envelope: SafetyEnvelope
    operator_authorization: OperatorAuthorization
```

**Semantics**:
- Immutable after creation.
- Commands must be validated against safety envelope at plan creation time.
- Randomization strategy determines trial execution order.

### TrialResult

```python
@dataclass(frozen=True)
class TrialResult:
    trial_id: str
    plan_id: str
    command: VelocityCommand
    receipt: CommandReceipt
    telemetry: list[TelemetrySample]
    validation_status: str            # "valid" | "invalid" | "anomaly"
    quality_metrics: dict[str, float]
    notes: str
```

**Semantics**:
- `validation_status == "valid"` requires telemetry covering the full command duration.
- Quality metrics include at minimum: mean actual velocity, tracking RMSE, telemetry coverage ratio.

### CalibrationDataset

```python
@dataclass(frozen=True)
class CalibrationDataset:
    dataset_id: str
    platform_id: str
    surface_type: str
    trials: list[TrialResult]
    created_at_utc: str
    provenance: dict[str, str]        # Maps artifact to hash

    def filter_valid(self) -> CalibrationDataset: ...
    def get_command_points(self) -> list[float]: ...
```

**Semantics**:
- Immutable. `filter_valid` returns a new dataset.
- Provenance must include hashes of all input artifacts.

### CalibrationModel

```python
@dataclass(frozen=True)
class CalibrationModel:
    model_id: str
    platform_id: str
    surface_type: str
    model_type: str                   # "monotonic_segment_lookup" | "polynomial" | etc.
    parameters: dict[str, Any]
    training_dataset_id: str
    validation_metrics: dict[str, float]
    domain_min_mps: float
    domain_max_mps: float

    def predict_actual(self, command_velocity_mps: float) -> float: ...
    def inverse_predict(self, desired_actual_mps: float) -> float: ...
    def is_in_domain(self, velocity_mps: float) -> bool: ...
```

**Semantics**:
- `predict_actual`: Forward model: command → predicted actual.
- `inverse_predict`: Inverse model: desired actual → required command. May raise if outside domain.
- `is_in_domain`: True if velocity is within the model's valid range.

### CalibrationProfile

```python
@dataclass(frozen=True)
class CalibrationProfile:
    profile_id: str
    platform_id: str
    surface_type: str
    model: CalibrationModel
    safety_envelope: SafetyEnvelope
    created_at_utc: str
    valid_until_utc: str | None
    provenance_chain: list[str]       # Ordered list of artifact hashes
    status: str                       # "gold" | "candidate" | "deprecated" | "experimental"
```

**Semantics**:
- "gold" status profiles must not be overwritten.
- Provenance chain allows full traceability from raw data to profile.
- `valid_until_utc` enforces profile refresh policy.

### CompensationDecision

```python
@dataclass(frozen=True)
class CompensationDecision:
    desired_actual_mps: float
    compensated_command_mps: float
    model_id: str
    profile_id: str
    confidence: float
    risk_level: str                   # "low" | "medium" | "high" | "rejected"
    fallback_applied: bool
    fallback_reason: str | None
    decision_monotonic_ns: int
```

**Semantics**:
- `compensated_command_mps` must be within safety envelope.
- `confidence < minimum_confidence` must trigger fallback.
- "rejected" risk level means no command should be sent.

### ExecutionAuditRecord

```python
@dataclass(frozen=True)
class ExecutionAuditRecord:
    session_id: str
    platform_id: str
    started_at_utc: str
    completed_at_utc: str | None
    commands_sent: list[CommandReceipt]
    emergency_stops: list[CommandReceipt]
    safety_violations: list[str]
    operator_authorizations: list[OperatorAuthorization]
    profile_used: str | None
    provenance_hashes: dict[str, str]
    session_status: str               # "completed" | "aborted" | "emergency_stopped"
```

**Semantics**:
- Immutable. Written at session completion.
- Must include all commands, emergency stops, and violations.
- Provenance hashes cover all input configurations.

### MonotonicClock

```python
class MonotonicClock(Protocol):
    """Monotonic time source for command sequencing and expiry."""

    def now_ns(self) -> int: ...
    def elapsed_since_ns(self, timestamp_ns: int) -> int: ...
    def is_after_ns(self, timestamp_ns: int) -> bool: ...
```

**Semantics**:
- `now_ns`: Monotonically increasing nanosecond timestamp.
- Must use a monotonic source (e.g., `time.monotonic_ns()`).
- Must not use system clock (which can jump).
- Must be injectable for testing.

## Expected Behavior: Edge Cases

### Telemetry is Stale

1. Before command: command is rejected (fail-closed).
2. During execution: transition to Stop → SafeState.
3. Staleness duration logged in audit record.
4. Operator notified if in interactive mode.

### Command Expires

1. Expired commands must not be sent to robot.
2. If command expires mid-execution: send stop, record expiry.
3. No automatic retry. Operator decides whether to re-issue.

### Adapter Disconnects

1. Transition to EmergencyStop.
2. Attempt safe-state restoration via any available channel.
3. Log disconnection details.
4. Notify operator.
5. Session marked as "aborted".

### Platform Capability Unavailable

1. Detected during CapabilityDiscovery.
2. If required capability: fail preflight, do not proceed.
3. If optional capability: log warning, continue with reduced functionality.
4. Capability gap recorded in audit record.

### Robot in Wrong Mode

1. Detected during Preflight or before command execution.
2. Do not send motion commands.
3. Attempt mode transition if safe to do so.
4. Fail with clear error if transition not possible.

### Stop Acknowledgement Missing

1. After stop timeout: escalate to EmergencyStop.
2. If EmergencyStop also unacknowledged: trigger platform-specific hardware stop.
3. Log all attempts and acknowledgements.
4. Mark session as "emergency_stopped".

### Operator Authorization Expires

1. Mid-session expiry: complete current trial, then Stop → SafeState.
2. No new trials until re-authorized.
3. Expiry logged in audit record.
4. Re-authorization creates new OperatorAuthorization record.
