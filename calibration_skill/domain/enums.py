"""Stable domain enumerations for the calibration skill."""
from __future__ import annotations

from enum import Enum


class RobotPlatform(str, Enum):
    """Target robot platforms. Values are stable lowercase strings for serialization."""
    BOOSTER_K1 = "booster_k1"
    UNITREE_G1 = "unitree_g1"
    UNITREE_GO1 = "unitree_go1"
    MOCK = "mock"


class RobotMorphology(str, Enum):
    """Robot morphology classes."""
    BIPED_HUMANOID = "biped_humanoid"
    QUADRUPED = "quadruped"
    SYNTHETIC = "synthetic"


class CoordinateFrame(str, Enum):
    """Reference frame for motion commands and telemetry."""
    BODY = "body"
    ODOM = "odom"
    MAP = "map"
    UNKNOWN = "unknown"


class ConnectionState(str, Enum):
    """Connection lifecycle states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAULTED = "faulted"


class MotionLifecycleState(str, Enum):
    """Motion lifecycle states for a robot."""
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    IDLE = "idle"
    PREPARING = "preparing"
    LOCOMOTION_READY = "locomotion_ready"
    MOVING = "moving"
    STOPPING = "stopping"
    SAFE_STOPPED = "safe_stopped"
    FAULTED = "faulted"


class CapabilitySupport(str, Enum):
    """Whether a capability is supported by a platform."""
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"
    REQUIRES_HARDWARE_VERIFICATION = "requires_hardware_verification"


class EvidenceLevel(str, Enum):
    """Level of evidence for a claim about a platform capability."""
    NONE = "none"
    REPOSITORY_OBSERVED = "repository_observed"
    UPSTREAM_DOCUMENTED = "upstream_documented"
    BENCH_VERIFIED = "bench_verified"
    HARDWARE_VERIFIED = "hardware_verified"


class ImplementationMaturity(str, Enum):
    """Implementation maturity of a component or feature."""
    NOT_STARTED = "not_started"
    LEGACY_EXISTING = "legacy_existing"
    SCAFFOLDED = "scaffolded"
    IMPLEMENTED_UNVERIFIED = "implemented_unverified"
    BENCH_VERIFIED = "bench_verified"
    HARDWARE_VERIFIED = "hardware_verified"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"


class CommandDisposition(str, Enum):
    """Outcome of a command sent to a robot."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class SkillOperationStatus(str, Enum):
    """Status of a skill operation response."""
    SUCCESS = "success"
    REJECTED = "rejected"
    FAILED = "failed"


class PreflightStatus(str, Enum):
    """Overall status of a preflight check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class TrialStatus(str, Enum):
    """Status of a calibration trial."""
    PLANNED = "planned"
    ATTEMPTED = "attempted"
    COMMAND_ACCEPTED = "command_accepted"
    COMMAND_EXECUTED = "command_executed"
    TELEMETRY_VALID = "telemetry_valid"
    TRIAL_VALID = "trial_valid"
    ABORTED = "aborted"
    FAILED = "failed"


class CompensationAction(str, Enum):
    """Action taken by the compensation decision engine."""
    APPLY_COMPENSATION = "apply_compensation"
    IDENTITY_FALLBACK = "identity_fallback"
    REJECT = "reject"
    UNAVAILABLE = "unavailable"


class ProfileStatus(str, Enum):
    """Status of a calibration profile."""
    GOLD = "gold"
    CANDIDATE = "candidate"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


# Known capability identifiers
CAPABILITY_CONNECT = "connect"
CAPABILITY_DISCONNECT = "disconnect"
CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND = "high_level_body_velocity_command"
CAPABILITY_VELOCITY_X = "velocity_x"
CAPABILITY_VELOCITY_Y = "velocity_y"
CAPABILITY_YAW_RATE = "yaw_rate"
CAPABILITY_EXPLICIT_STOP = "explicit_stop"
CAPABILITY_LOCOMOTION_MODE_TRANSITION = "locomotion_mode_transition"
CAPABILITY_ROBOT_MODE_OBSERVATION = "robot_mode_observation"
CAPABILITY_BODY_VELOCITY_TELEMETRY = "body_velocity_telemetry"
CAPABILITY_POSE_ODOMETRY_TELEMETRY = "pose_odometry_telemetry"
CAPABILITY_IMU_TELEMETRY = "imu_telemetry"
CAPABILITY_YAW_HEADING_TELEMETRY = "yaw_heading_telemetry"
CAPABILITY_BATTERY_TELEMETRY = "battery_telemetry"
CAPABILITY_COMMAND_ACKNOWLEDGEMENT = "command_acknowledgement"
CAPABILITY_STATE_STREAM = "state_stream"
CAPABILITY_EMERGENCY_STOP = "emergency_stop"
CAPABILITY_SIMULATOR = "simulator"
CAPABILITY_DRY_RUN = "dry_run"
CAPABILITY_COMMAND_TTL = "command_ttl"
CAPABILITY_OPERATOR_CONFIRMATION = "operator_confirmation"
CAPABILITY_PLATFORM_VERSION_REPORTING = "platform_version_reporting"
CAPABILITY_FIRMWARE_VERSION_REPORTING = "firmware_version_reporting"


ALL_KNOWN_CAPABILITIES: tuple[str, ...] = (
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
    CAPABILITY_IMU_TELEMETRY,
    CAPABILITY_YAW_HEADING_TELEMETRY,
    CAPABILITY_BATTERY_TELEMETRY,
    CAPABILITY_COMMAND_ACKNOWLEDGEMENT,
    CAPABILITY_STATE_STREAM,
    CAPABILITY_EMERGENCY_STOP,
    CAPABILITY_SIMULATOR,
    CAPABILITY_DRY_RUN,
    CAPABILITY_COMMAND_TTL,
    CAPABILITY_OPERATOR_CONFIRMATION,
    CAPABILITY_PLATFORM_VERSION_REPORTING,
    CAPABILITY_FIRMWARE_VERSION_REPORTING,
)


# Allowed motion lifecycle transitions
ALLOWED_LIFECYCLE_TRANSITIONS: dict[MotionLifecycleState, tuple[MotionLifecycleState, ...]] = {
    MotionLifecycleState.UNKNOWN: (
        MotionLifecycleState.UNAVAILABLE,
        MotionLifecycleState.IDLE,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.UNAVAILABLE: (
        MotionLifecycleState.IDLE,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.IDLE: (
        MotionLifecycleState.PREPARING,
        MotionLifecycleState.FAULTED,
        MotionLifecycleState.UNAVAILABLE,
    ),
    MotionLifecycleState.PREPARING: (
        MotionLifecycleState.LOCOMOTION_READY,
        MotionLifecycleState.IDLE,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.LOCOMOTION_READY: (
        MotionLifecycleState.MOVING,
        MotionLifecycleState.IDLE,
        MotionLifecycleState.STOPPING,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.MOVING: (
        MotionLifecycleState.STOPPING,
        MotionLifecycleState.SAFE_STOPPED,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.STOPPING: (
        MotionLifecycleState.SAFE_STOPPED,
        MotionLifecycleState.IDLE,
        MotionLifecycleState.FAULTED,
    ),
    MotionLifecycleState.SAFE_STOPPED: (
        MotionLifecycleState.IDLE,
        MotionLifecycleState.PREPARING,
        MotionLifecycleState.FAULTED,
        MotionLifecycleState.UNAVAILABLE,
    ),
    MotionLifecycleState.FAULTED: (
        MotionLifecycleState.IDLE,
        MotionLifecycleState.UNAVAILABLE,
    ),
}
