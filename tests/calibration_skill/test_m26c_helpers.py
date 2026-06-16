"""Shared fixtures for M26-C tests."""
from __future__ import annotations

from calibration_skill.domain.enums import CoordinateFrame, RobotPlatform
from calibration_skill.domain.motion import VelocityCommand
from calibration_skill.domain.safety import OperatorAuthorization, SafetyEnvelope
from calibration_skill.schemas.codec import (
    encode_operator_authorization,
    encode_safety_envelope,
    encode_velocity_command,
)


def safety_envelope(required: bool = True) -> SafetyEnvelope:
    return SafetyEnvelope(
        policy_id="mock-policy",
        policy_hash="mock-hash",
        max_abs_vx_mps=0.5,
        max_abs_vy_mps=0.4,
        max_abs_wz_radps=0.8,
        max_command_duration_s=2.0,
        max_telemetry_age_ms=100.0,
        stop_timeout_s=1.0,
        allowed_command_frames=(CoordinateFrame.BODY,),
        operator_authorization_required=required,
    )


def velocity_command(
    *,
    sequence_id: str = "cmd-1",
    issued_ns: int = 1_000_000_000,
    expiry_ns: int = 2_000_000_000,
    vx: float = 0.1,
    vy: float = 0.0,
    wz: float = 0.0,
    frame: CoordinateFrame = CoordinateFrame.BODY,
) -> VelocityCommand:
    return VelocityCommand(
        vx_mps=vx,
        vy_mps=vy,
        wz_radps=wz,
        sequence_id=sequence_id,
        issued_monotonic_ns=issued_ns,
        expiry_monotonic_ns=expiry_ns,
        requested_duration_s=0.5,
        frame=frame,
        safety_policy_id="mock-policy",
        safety_policy_hash="mock-hash",
        source="m26c-test",
    )


def authorization(
    *,
    operation: str = "dry_run_velocity_command",
    expiry_ns: int = 3_000_000_000,
    robot_id: str = "mock-robot",
) -> OperatorAuthorization:
    return OperatorAuthorization(
        authorization_id="auth-1",
        operator_id="operator-1",
        platform=RobotPlatform.MOCK,
        robot_id=robot_id,
        issued_monotonic_ns=500_000_000,
        expiry_monotonic_ns=expiry_ns,
        authorized_operations=(operation,),
        safety_policy_id="mock-policy",
        safety_policy_hash="mock-hash",
        evidence_reference="simulated-operator-confirmation",
    )


def request(
    operation: str,
    *,
    request_id: str = "req-1",
    dry_run: bool = True,
    platform: str = "mock",
    payload: dict | None = None,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "operation": operation,
        "platform": platform,
        "robot_id": "mock-robot",
        "dry_run": dry_run,
        "payload": payload or {},
        "caller_metadata": {"test": "m26c"},
    }


def command_payload(operation: str = "dry_run_velocity_command") -> dict:
    return {
        "safety_envelope": encode_safety_envelope(safety_envelope()),
        "velocity_command": encode_velocity_command(velocity_command()),
        "operator_authorization": encode_operator_authorization(authorization(operation=operation)),
    }
