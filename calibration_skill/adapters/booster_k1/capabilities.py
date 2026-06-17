"""Conservative Booster K1 capability descriptor for fake-runtime M27-B."""
from __future__ import annotations

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
    EvidenceLevel,
    ImplementationMaturity,
    RobotPlatform,
)

FAKE_RUNTIME_NOTE = "M27-B fake-runtime verification only; no K1 hardware evidence is claimed."


def _supported(capability_id: str, *, notes: str = FAKE_RUNTIME_NOTE) -> CapabilityRecord:
    return CapabilityRecord(
        capability_id=capability_id,
        support=CapabilitySupport.SUPPORTED,
        evidence=EvidenceLevel.BENCH_VERIFIED,
        maturity=ImplementationMaturity.BENCH_VERIFIED,
        evidence_refs=("m27b_fake_runtime_tests",),
        notes=notes,
    )


def _unsupported(capability_id: str, *, notes: str) -> CapabilityRecord:
    return CapabilityRecord(
        capability_id=capability_id,
        support=CapabilitySupport.UNSUPPORTED,
        evidence=EvidenceLevel.NONE,
        maturity=ImplementationMaturity.UNSUPPORTED,
        notes=notes,
    )


def _unknown(capability_id: str, *, notes: str) -> CapabilityRecord:
    return CapabilityRecord(
        capability_id=capability_id,
        support=CapabilitySupport.UNKNOWN,
        evidence=EvidenceLevel.NONE,
        maturity=ImplementationMaturity.NOT_STARTED,
        notes=notes,
    )


def booster_k1_capabilities() -> CapabilityDescriptor:
    """Return K1 capabilities for the fake runtime, never hardware verified."""
    records = [
        _supported(CAPABILITY_CONNECT),
        _supported(CAPABILITY_DISCONNECT),
        _supported(CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND),
        _supported(CAPABILITY_VELOCITY_X, notes="Forward velocity maps to fake prepare -> walking -> Move(vx, 0.0, 0.0)."),
        _unsupported(CAPABILITY_VELOCITY_Y, notes="Legacy M27-A evidence covers forward-only vx commands."),
        _unsupported(CAPABILITY_YAW_RATE, notes="Legacy M27-A evidence covers forward-only vx commands."),
        _supported(CAPABILITY_EXPLICIT_STOP),
        _supported(CAPABILITY_LOCOMOTION_MODE_TRANSITION),
        _supported(CAPABILITY_ROBOT_MODE_OBSERVATION),
        _supported(CAPABILITY_BODY_VELOCITY_TELEMETRY),
        _supported(CAPABILITY_POSE_ODOMETRY_TELEMETRY),
        _unknown(CAPABILITY_IMU_TELEMETRY, notes="No fake IMU contract is claimed in M27-B."),
        _supported(CAPABILITY_YAW_HEADING_TELEMETRY, notes="Fake odometry can include heading; no hardware heading claim."),
        _unknown(CAPABILITY_BATTERY_TELEMETRY, notes="Battery data is optional fake state only."),
        _supported(CAPABILITY_COMMAND_ACKNOWLEDGEMENT, notes="Receipt only proves fake runtime acceptance."),
        _supported(CAPABILITY_STATE_STREAM),
        _unsupported(CAPABILITY_EMERGENCY_STOP, notes="Emergency-stop behavior is not modeled in M27-B."),
        _supported(CAPABILITY_SIMULATOR),
        _supported(CAPABILITY_DRY_RUN),
        _supported(CAPABILITY_COMMAND_TTL),
        _supported(CAPABILITY_OPERATOR_CONFIRMATION),
        _unknown(CAPABILITY_PLATFORM_VERSION_REPORTING, notes="Runtime metadata may provide a fake platform version."),
        _unknown(CAPABILITY_FIRMWARE_VERSION_REPORTING, notes="Firmware version is optional fake metadata only."),
    ]
    return CapabilityDescriptor(platform_id=RobotPlatform.BOOSTER_K1.value, capabilities=tuple(records))
