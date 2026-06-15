"""Full JSON Schema Draft 2020-12 validation tests.

Uses the installed jsonschema library to validate all 13 v1 schemas
against their metaschema, resolve $ref values, and validate
representative payloads.
"""
import json
import math
import os
import pytest

from calibration_skill.schemas.validation import (
    validate_payload,
    validate_schema_documents,
    validate_skill_request,
    validate_skill_response,
    validate_codec_payload,
    collect_schema_validation_errors,
)
from calibration_skill.schemas.codec import (
    encode_velocity_command,
    encode_safety_envelope,
    encode_operator_authorization,
    encode_robot_identity,
    encode_telemetry_sample,
    encode_command_receipt,
    encode_calibration_profile,
)
from calibration_skill.domain.enums import (
    CoordinateFrame, RobotPlatform, RobotMorphology,
    CommandDisposition, ProfileStatus,
)
from calibration_skill.domain.motion import VelocityCommand, CommandReceipt
from calibration_skill.domain.safety import SafetyEnvelope, OperatorAuthorization
from calibration_skill.domain.identity import RobotIdentity
from calibration_skill.domain.telemetry import TelemetrySample
from calibration_skill.domain.calibration import (
    CalibrationProfile, CalibrationModel, EnvironmentDescriptor,
)


# ── Schema metaschema validation ──────────────────────────────────────────

class TestSchemaMetaschemaValidation:
    """All 13 schemas must validate against Draft 2020-12 metaschema."""

    def test_all_schemas_valid(self):
        result = validate_schema_documents()
        assert result["all_valid"], f"Schema errors: {result.get('errors', [])}"
        assert result["schema_count"] == 13
        assert result["valid_count"] == 13


# ── Schema document integrity ─────────────────────────────────────────────

class TestSchemaDocuments:
    """Each schema must load and resolve $ref values."""

    @pytest.mark.parametrize("schema_id", [
        "skill_request", "skill_response", "error", "robot_identity",
        "capability_descriptor", "velocity_command", "command_receipt",
        "telemetry_sample", "preflight_report", "safety_envelope",
        "operator_authorization", "calibration_profile", "execution_audit_record",
    ])
    def test_schema_loads(self, schema_id):
        result = validate_payload(schema_id, {})
        # Should fail validation (empty {}), but not crash with schema error
        assert not result.get("valid")
        assert "error" not in result or "Schema error" not in result.get("error", "")

    def test_unknown_schema_rejected(self):
        result = validate_payload("nonexistent_schema", {})
        assert not result["valid"]
        assert result.get("error_code") == "schema_version_unsupported"


# ── Skill request validation ──────────────────────────────────────────────

class TestSkillRequestValidation:
    def test_valid_request(self):
        result = validate_skill_request({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "platform": "mock",
            "dry_run": True,
        })
        assert result["valid"], result

    def test_missing_request_id(self):
        result = validate_skill_request({
            "schema_version": "1.0.0",
            "operation": "calibrate",
            "platform": "mock",
            "dry_run": True,
        })
        assert not result["valid"]

    def test_unsupported_platform(self):
        result = validate_skill_request({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "platform": "unsupported_robot",
            "dry_run": True,
        })
        assert not result["valid"]

    def test_invalid_schema_version(self):
        result = validate_skill_request({
            "schema_version": "999.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "platform": "mock",
            "dry_run": True,
        })
        assert not result["valid"]


# ── Skill response validation ─────────────────────────────────────────────

class TestSkillResponseValidation:
    def test_success_with_result(self):
        result = validate_skill_response({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "status": "success",
            "result": {"profile_id": "p1"},
        })
        assert result["valid"], result

    def test_success_with_error_rejected(self):
        result = validate_skill_response({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "status": "success",
            "error": {"code": "err", "message": "msg"},
        })
        assert not result["valid"]

    def test_failed_without_error_rejected(self):
        result = validate_skill_response({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "status": "failed",
        })
        assert not result["valid"]

    def test_rejected_without_error_rejected(self):
        result = validate_skill_response({
            "schema_version": "1.0.0",
            "request_id": "req-001",
            "operation": "calibrate",
            "status": "rejected",
        })
        assert not result["valid"]


# ── Error schema validation ───────────────────────────────────────────────

class TestErrorSchemaValidation:
    def test_valid_error(self):
        result = validate_payload("error", {
            "code": "configuration_missing",
            "message": "Config not found",
        })
        assert result["valid"], result

    def test_missing_code(self):
        result = validate_payload("error", {
            "message": "No code here",
        })
        assert not result["valid"]

    def test_unknown_code_accepted_by_schema(self):
        """The error schema does not restrict code values — only requires it be present."""
        result = validate_payload("error", {
            "code": "some_future_code_not_yet_defined",
            "message": "Test",
        })
        assert result["valid"], result


# ── VelocityCommand validation ────────────────────────────────────────────

class TestVelocityCommandSchema:
    def test_valid_velocity_command(self):
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s1", issued_monotonic_ns=1000, expiry_monotonic_ns=2000,
            requested_duration_s=5.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="abc", source="test",
        )
        payload = encode_velocity_command(cmd)
        result = validate_codec_payload("velocity_command", payload)
        assert result["valid"], result

    def test_invalid_frame(self):
        result = validate_payload("velocity_command", {
            "vx_mps": 0.5, "vy_mps": 0.0, "wz_radps": 0.0,
            "sequence_id": "s", "issued_monotonic_ns": 1, "expiry_monotonic_ns": 2,
            "requested_duration_s": 1.0, "frame": "invalid_frame",
            "safety_policy_id": "p", "safety_policy_hash": "h", "source": "t",
        })
        assert not result["valid"]

    def test_missing_safety_policy(self):
        result = validate_payload("velocity_command", {
            "vx_mps": 0.5, "vy_mps": 0.0, "wz_radps": 0.0,
            "sequence_id": "s", "issued_monotonic_ns": 1, "expiry_monotonic_ns": 2,
            "requested_duration_s": 1.0, "frame": "body",
            "source": "t",
        })
        assert not result["valid"]

    def test_expiry_not_after_issue_rejected_by_domain(self):
        """JSON Schema cannot express cross-field expiry > issued invariant.
        Domain construction rejects it."""
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=2000, expiry_monotonic_ns=1000,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="t",
            )


# ── SafetyEnvelope validation ─────────────────────────────────────────────

class TestSafetyEnvelopeSchema:
    def test_valid_envelope(self):
        env = SafetyEnvelope(
            policy_id="p", policy_hash="h",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        payload = encode_safety_envelope(env)
        result = validate_codec_payload("safety_envelope", payload)
        assert result["valid"], result

    def test_negative_limit_rejected(self):
        result = validate_payload("safety_envelope", {
            "policy_id": "p", "policy_hash": "h",
            "max_abs_vx_mps": -1.0, "max_abs_vy_mps": 0.5, "max_abs_wz_radps": 0.3,
            "max_command_duration_s": 10.0, "max_telemetry_age_ms": 500.0,
            "stop_timeout_s": 5.0,
            "allowed_command_frames": ["body"],
            "operator_authorization_required": True,
        })
        assert not result["valid"]

    def test_empty_frame_list_rejected(self):
        result = validate_payload("safety_envelope", {
            "policy_id": "p", "policy_hash": "h",
            "max_abs_vx_mps": 1.0, "max_abs_vy_mps": 0.5, "max_abs_wz_radps": 0.3,
            "max_command_duration_s": 10.0, "max_telemetry_age_ms": 500.0,
            "stop_timeout_s": 5.0,
            "allowed_command_frames": [],
            "operator_authorization_required": True,
        })
        assert not result["valid"]

    def test_no_silent_maximum(self):
        """Missing required fields fail schema validation — no defaults applied."""
        result = validate_payload("safety_envelope", {
            "policy_id": "p", "policy_hash": "h",
            "max_abs_vy_mps": 0.5, "max_abs_wz_radps": 0.3,
            "max_command_duration_s": 10.0, "max_telemetry_age_ms": 500.0,
            "stop_timeout_s": 5.0,
            "allowed_command_frames": ["body"],
            "operator_authorization_required": True,
        })
        assert not result["valid"]


# ── OperatorAuthorization validation ──────────────────────────────────────

class TestOperatorAuthorizationSchema:
    def test_valid_authorization(self):
        auth = OperatorAuthorization(
            authorization_id="a1", operator_id="op1",
            platform=RobotPlatform.MOCK, robot_id="r1",
            issued_monotonic_ns=1000, expiry_monotonic_ns=5000,
            authorized_operations=("calibrate",),
            safety_policy_id="p", safety_policy_hash="h",
            evidence_reference="ref",
        )
        payload = encode_operator_authorization(auth)
        result = validate_codec_payload("operator_authorization", payload)
        assert result["valid"], result

    def test_missing_policy_reference(self):
        result = validate_payload("operator_authorization", {
            "authorization_id": "a1", "operator_id": "op1",
            "platform": "mock", "robot_id": "r1",
            "issued_monotonic_ns": 1000, "expiry_monotonic_ns": 5000,
            "authorized_operations": ["test"],
            "evidence_reference": "ref",
        })
        assert not result["valid"]


# ── TelemetrySample validation ────────────────────────────────────────────

class TestTelemetrySampleSchema:
    def test_valid_sample(self):
        sample = TelemetrySample(robot_id="k1", sample_sequence_id=0, received_monotonic_ns=1000)
        payload = encode_telemetry_sample(sample)
        result = validate_codec_payload("telemetry_sample", payload)
        assert result["valid"], result

    def test_optional_data_omitted(self):
        """Optional telemetry fields are not present in output (not null, not zero)."""
        sample = TelemetrySample(robot_id="k1", sample_sequence_id=0, received_monotonic_ns=1000)
        payload = encode_telemetry_sample(sample)
        assert "heading_rad" not in payload
        assert payload.get("heading_rad") is None
        assert "battery_voltage" not in payload

    def test_zero_values_preserved(self):
        sample = TelemetrySample(robot_id="k1", sample_sequence_id=0, received_monotonic_ns=1000, heading_rad=0.0)
        payload = encode_telemetry_sample(sample)
        assert payload["heading_rad"] == 0.0  # Zero is valid measurement


# ── CalibrationProfile validation ─────────────────────────────────────────

class TestCalibrationProfileSchema:
    def test_valid_profile(self):
        model = CalibrationModel(model_id="m1", platform=RobotPlatform.MOCK, model_type="linear")
        env = EnvironmentDescriptor(surface_type="tile")
        profile = CalibrationProfile(
            profile_id="p1", profile_version="1.0.0",
            platform=RobotPlatform.MOCK, robot_id="r1",
            environment_applicability=env,
            model=model,
            training_dataset_digest="abc123",
            status=ProfileStatus.CANDIDATE,
        )
        payload = encode_calibration_profile(profile)
        result = validate_codec_payload("calibration_profile", payload)
        assert result["valid"], result

    def test_missing_digest_rejected(self):
        result = validate_payload("calibration_profile", {
            "profile_id": "p1", "profile_version": "1.0.0",
            "platform": "mock", "robot_id": "r1",
            "environment_applicability": {"surface_type": "tile"},
            "model": {"model_id": "m1", "platform": "mock", "model_type": "linear"},
            "status": "candidate",
        })
        assert not result["valid"]


# ── ExecutionAuditRecord validation ───────────────────────────────────────

class TestExecutionAuditRecordSchema:
    def test_valid_audit_record(self):
        result = validate_payload("execution_audit_record", {
            "session_id": "sess-1",
            "requested_operation": "calibrate",
            "platform": "mock",
            "robot_id": "r1",
            "software_version": "0.1.0",
            "adapter_version": "0.1.0",
            "safety_policy_id": "p",
            "safety_policy_hash": "h",
            "authorization_id": "auth-1",
            "started_monotonic_ns": 1000,
            "session_status": "completed",
        })
        assert result["valid"], result

    def test_missing_safety_policy_rejected(self):
        result = validate_payload("execution_audit_record", {
            "session_id": "sess-1",
            "requested_operation": "calibrate",
            "platform": "mock",
            "robot_id": "r1",
            "software_version": "0.1.0",
            "adapter_version": "0.1.0",
            "authorization_id": "auth-1",
            "started_monotonic_ns": 1000,
            "session_status": "completed",
        })
        assert not result["valid"]


# ── $ref resolution tests ─────────────────────────────────────────────────

class TestRefResolution:
    def test_skill_response_refs_error_schema(self):
        """skill_response.schema.json $refs error.schema.json — must resolve."""
        result = validate_skill_response({
            "schema_version": "1.0.0",
            "request_id": "r1",
            "operation": "test",
            "status": "failed",
            "error": {"code": "test", "message": "test error"},
        })
        assert result["valid"], result

    def test_command_receipt_refs_error_schema(self):
        """command_receipt.schema.json $refs error.schema.json — must resolve."""
        receipt = CommandReceipt(
            command_sequence_id="s1",
            disposition=CommandDisposition.REJECTED,
            received_monotonic_ns=1000,
        )
        payload = encode_command_receipt(receipt)
        result = validate_codec_payload("command_receipt", payload)
        assert result["valid"], result


# ── DomainError collection ────────────────────────────────────────────────

class TestCollectSchemaValidationErrors:
    def test_returns_empty_for_valid(self):
        errors = collect_schema_validation_errors("error", {
            "code": "test", "message": "ok",
        })
        assert len(errors) == 0

    def test_returns_domain_errors_for_invalid(self):
        errors = collect_schema_validation_errors("error", {
            "message": "no code",
        })
        assert len(errors) > 0
        assert all(hasattr(e, "code") for e in errors)

    def test_unknown_schema_returns_unsupported(self):
        errors = collect_schema_validation_errors("nonexistent", {})
        assert len(errors) > 0
        assert errors[0].code == "schema_version_unsupported"
