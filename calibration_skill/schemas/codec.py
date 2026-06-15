"""Deterministic JSON codec functions for domain objects.

All serialization uses stable key ordering for hashing.
NaN and Infinity are rejected.
Monotonic timestamps are integer nanoseconds.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from calibration_skill.domain.enums import (
    CommandDisposition,
    CompensationAction,
    ConnectionState,
    CoordinateFrame,
    MotionLifecycleState,
    PreflightStatus,
    ProfileStatus,
    RobotMorphology,
    RobotPlatform,
    SkillOperationStatus,
    TrialStatus,
)
from calibration_skill.domain.errors import DomainError
from calibration_skill.domain.identity import RobotIdentity
from calibration_skill.domain.capabilities import CapabilityDescriptor, CapabilityRecord
from calibration_skill.domain.motion import CommandReceipt, VelocityCommand
from calibration_skill.domain.telemetry import TelemetrySample
from calibration_skill.domain.safety import OperatorAuthorization, PreflightCheck, PreflightReport, SafetyEnvelope
from calibration_skill.domain.calibration import (
    CalibrationProfile,
    CompensationDecision,
    ExecutionAuditRecord,
)


def _check_no_nan_inf(obj: Any, path: str = "$") -> list[str]:
    """Recursively check for NaN or Infinity in a JSON-serializable object."""
    errors: list[str] = []
    if isinstance(obj, float):
        import math
        if math.isnan(obj):
            errors.append(f"{path}: NaN not allowed")
        if math.isinf(obj):
            errors.append(f"{path}: Infinity not allowed")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            errors.extend(_check_no_nan_inf(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            errors.extend(_check_no_nan_inf(value, f"{path}[{i}]"))
    return errors


def canonical_json_dumps(obj: Any) -> str:
    """Serialize to canonical JSON (sorted keys, no whitespace, UTF-8)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def encode_robot_identity(identity: RobotIdentity) -> dict[str, Any]:
    """Encode RobotIdentity to a JSON-safe dict."""
    return identity.to_dict()


def decode_robot_identity(data: dict[str, Any]) -> RobotIdentity:
    """Decode RobotIdentity from a dict."""
    return RobotIdentity(
        platform=RobotPlatform(data["platform"]),
        morphology=RobotMorphology(data["morphology"]),
        robot_id=data["robot_id"],
        adapter_name=data["adapter_name"],
        adapter_version=data["adapter_version"],
        hardware_serial=data.get("hardware_serial"),
        firmware_version=data.get("firmware_version"),
        sdk_family=data.get("sdk_family"),
        sdk_version=data.get("sdk_version"),
        metadata=tuple(sorted(data.get("metadata", {}).items())) if data.get("metadata") else (),
    )


def encode_capability_descriptor(descriptor: CapabilityDescriptor) -> dict[str, Any]:
    """Encode CapabilityDescriptor."""
    return descriptor.to_dict()


def decode_capability_descriptor(data: dict[str, Any]) -> CapabilityDescriptor:
    """Decode CapabilityDescriptor."""
    from calibration_skill.domain.enums import CapabilitySupport, EvidenceLevel, ImplementationMaturity
    records = []
    for c in data.get("capabilities", []):
        records.append(CapabilityRecord(
            capability_id=c["capability_id"],
            support=CapabilitySupport(c.get("support", "unknown")),
            evidence=EvidenceLevel(c.get("evidence", "none")),
            maturity=ImplementationMaturity(c.get("maturity", "not_started")),
            constraints=c.get("constraints"),
            evidence_refs=tuple(c.get("evidence_refs", [])),
            notes=c.get("notes"),
        ))
    return CapabilityDescriptor(
        platform_id=data["platform_id"],
        capabilities=tuple(records),
    )


def encode_velocity_command(cmd: VelocityCommand) -> dict[str, Any]:
    """Encode VelocityCommand."""
    return cmd.to_dict()


def decode_velocity_command(data: dict[str, Any]) -> VelocityCommand:
    """Decode VelocityCommand."""
    return VelocityCommand(
        vx_mps=float(data["vx_mps"]),
        vy_mps=float(data["vy_mps"]),
        wz_radps=float(data["wz_radps"]),
        sequence_id=data["sequence_id"],
        issued_monotonic_ns=int(data["issued_monotonic_ns"]),
        expiry_monotonic_ns=int(data["expiry_monotonic_ns"]),
        requested_duration_s=float(data["requested_duration_s"]),
        frame=CoordinateFrame(data["frame"]),
        safety_policy_id=data["safety_policy_id"],
        safety_policy_hash=data["safety_policy_hash"],
        source=data["source"],
    )


def encode_command_receipt(receipt: CommandReceipt) -> dict[str, Any]:
    """Encode CommandReceipt."""
    return receipt.to_dict()


def decode_command_receipt(data: dict[str, Any]) -> CommandReceipt:
    """Decode CommandReceipt."""
    rejection_error = None
    if data.get("rejection_error"):
        rejection_error = DomainError(
            code=data["rejection_error"]["code"],
            message=data["rejection_error"]["message"],
            retryable=data["rejection_error"].get("retryable", False),
            details=data["rejection_error"].get("details", {}),
        )
    return CommandReceipt(
        command_sequence_id=data["command_sequence_id"],
        disposition=CommandDisposition(data["disposition"]),
        adapter_receipt_id=data.get("adapter_receipt_id"),
        received_monotonic_ns=int(data.get("received_monotonic_ns", 0)),
        accepted_monotonic_ns=data.get("accepted_monotonic_ns"),
        rejection_error=rejection_error,
        adapter_state=data.get("adapter_state"),
        acknowledgement_evidence=data.get("acknowledgement_evidence"),
    )


def encode_telemetry_sample(sample: TelemetrySample) -> dict[str, Any]:
    """Encode TelemetrySample."""
    return sample.to_dict()


def decode_telemetry_sample(data: dict[str, Any]) -> TelemetrySample:
    """Decode TelemetrySample."""
    from calibration_skill.domain.telemetry import Pose3D, Quaternion, Twist3D, Vector3

    pose = None
    if data.get("pose"):
        p = data["pose"]
        pos = Vector3(**p["position"]) if p.get("position") else Vector3()
        orient_data = p.get("orientation", {})
        orient = Quaternion(
            x=orient_data.get("x", 0.0),
            y=orient_data.get("y", 0.0),
            z=orient_data.get("z", 0.0),
            w=orient_data.get("w", 1.0),
        )
        pose = Pose3D(position=pos, orientation=orient)

    body_twist = None
    if data.get("body_twist"):
        bt = data["body_twist"]
        lin = Vector3(**bt["linear"]) if bt.get("linear") else Vector3()
        ang = Vector3(**bt["angular"]) if bt.get("angular") else Vector3()
        body_twist = Twist3D(linear=lin, angular=ang)

    imu_accel = None
    if data.get("imu_accel"):
        imu_accel = Vector3(**data["imu_accel"])

    imu_gyro = None
    if data.get("imu_gyro"):
        imu_gyro = Vector3(**data["imu_gyro"])

    return TelemetrySample(
        robot_id=data["robot_id"],
        sample_sequence_id=int(data["sample_sequence_id"]),
        received_monotonic_ns=int(data["received_monotonic_ns"]),
        frame=CoordinateFrame(data.get("frame", "unknown")),
        source_timestamp_ns=data.get("source_timestamp_ns"),
        pose=pose,
        body_twist=body_twist,
        imu_accel=imu_accel,
        imu_gyro=imu_gyro,
        heading_rad=data.get("heading_rad"),
        battery_voltage=data.get("battery_voltage"),
        battery_percentage=data.get("battery_percentage"),
        robot_mode=data.get("robot_mode"),
        source_adapter=data.get("source_adapter"),
        quality_flags=tuple(data.get("quality_flags", [])),
        raw_reference=data.get("raw_reference"),
    )


def encode_safety_envelope(envelope: SafetyEnvelope) -> dict[str, Any]:
    """Encode SafetyEnvelope."""
    return envelope.to_dict()


def decode_safety_envelope(data: dict[str, Any]) -> SafetyEnvelope:
    """Decode SafetyEnvelope."""
    return SafetyEnvelope(
        policy_id=data["policy_id"],
        policy_hash=data["policy_hash"],
        max_abs_vx_mps=float(data["max_abs_vx_mps"]),
        max_abs_vy_mps=float(data["max_abs_vy_mps"]),
        max_abs_wz_radps=float(data["max_abs_wz_radps"]),
        max_command_duration_s=float(data["max_command_duration_s"]),
        max_telemetry_age_ms=float(data["max_telemetry_age_ms"]),
        stop_timeout_s=float(data["stop_timeout_s"]),
        allowed_command_frames=tuple(CoordinateFrame(f) for f in data["allowed_command_frames"]),
        operator_authorization_required=bool(data["operator_authorization_required"]),
    )


def encode_operator_authorization(auth: OperatorAuthorization) -> dict[str, Any]:
    """Encode OperatorAuthorization."""
    return auth.to_dict()


def decode_operator_authorization(data: dict[str, Any]) -> OperatorAuthorization:
    """Decode OperatorAuthorization."""
    return OperatorAuthorization(
        authorization_id=data["authorization_id"],
        operator_id=data["operator_id"],
        platform=RobotPlatform(data["platform"]),
        robot_id=data["robot_id"],
        issued_monotonic_ns=int(data["issued_monotonic_ns"]),
        expiry_monotonic_ns=int(data["expiry_monotonic_ns"]),
        authorized_operations=tuple(data["authorized_operations"]),
        safety_policy_id=data["safety_policy_id"],
        safety_policy_hash=data["safety_policy_hash"],
        evidence_reference=data["evidence_reference"],
    )


def encode_preflight_report(report: PreflightReport) -> dict[str, Any]:
    """Encode PreflightReport."""
    return report.to_dict()


def encode_calibration_profile(profile: CalibrationProfile) -> dict[str, Any]:
    """Encode CalibrationProfile (includes content digest)."""
    return profile.to_dict_with_digest()


def encode_compensation_decision(decision: CompensationDecision) -> dict[str, Any]:
    """Encode CompensationDecision."""
    return decision.to_dict()


def encode_execution_audit_record(record: ExecutionAuditRecord) -> dict[str, Any]:
    """Encode ExecutionAuditRecord."""
    return record.to_dict()


def encode_domain_error(error: DomainError) -> dict[str, Any]:
    """Encode DomainError (no traceback)."""
    return error.to_dict()


# Round-trip codec pairs (encode, decode)
CODECS: dict[str, tuple[Callable[[Any], dict[str, Any]], Callable[[dict[str, Any]], Any]]] = {
    "robot_identity": (encode_robot_identity, decode_robot_identity),
    "capability_descriptor": (encode_capability_descriptor, decode_capability_descriptor),
    "velocity_command": (encode_velocity_command, decode_velocity_command),
    "command_receipt": (encode_command_receipt, decode_command_receipt),
    "telemetry_sample": (encode_telemetry_sample, decode_telemetry_sample),
    "safety_envelope": (encode_safety_envelope, decode_safety_envelope),
    "operator_authorization": (encode_operator_authorization, decode_operator_authorization),
}
