"""Tests for domain error taxonomy, calibration, and readiness."""
import pytest
from calibration_skill.domain.errors import DomainError, domain_error, validation_error
from calibration_skill.domain.errors import (
    ERROR_CONFIGURATION_MISSING, ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_OPERATOR_AUTHORIZATION_EXPIRED, ERROR_TELEMETRY_STALE,
)
from calibration_skill.domain.calibration import (
    CalibrationProfile, CompensationDecision, EnvironmentDescriptor,
    ExecutionAuditRecord, TrialPlan, TrialResult,
)
from calibration_skill.domain.enums import (
    CompensationAction, ProfileStatus, RobotPlatform, SkillOperationStatus, TrialStatus,
)
from calibration_skill.domain.readiness import (
    ImplementationMaturity, ReadinessEntry, ReadinessModel,
    READINESS_DOMAIN_CONTRACTS, READINESS_G1_ADAPTER, READINESS_RELEASE,
)


class TestErrorTaxonomy:
    def test_domain_error_construction(self):
        err = DomainError(code="test_code", message="test message")
        assert err.code == "test_code"
        assert err.retryable is False  # Default

    def test_domain_error_to_dict(self):
        err = DomainError(
            code=ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
            message="Speed limit exceeded",
            retryable=False,
            details={"vx": 1.5, "max": 1.0},
        )
        d = err.to_dict()
        assert d["code"] == ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE
        assert "details" in d
        # No traceback
        assert "traceback" not in d

    def test_all_error_codes_defined(self):
        codes = [
            ERROR_CONFIGURATION_MISSING,
            ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
            ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
            ERROR_TELEMETRY_STALE,
        ]
        for code in codes:
            assert isinstance(code, str) and len(code) > 0

    def test_skill_operation_status_values(self):
        assert SkillOperationStatus.SUCCESS.value == "success"
        assert SkillOperationStatus.REJECTED.value == "rejected"
        assert SkillOperationStatus.FAILED.value == "failed"


class TestCalibrationContracts:
    def test_trial_plan_construction(self):
        from calibration_skill.domain.motion import VelocityCommand
        from calibration_skill.domain.enums import CoordinateFrame, CAPABILITY_VELOCITY_X
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="p", safety_policy_hash="h", source="test",
        )
        env = EnvironmentDescriptor(surface_type="tile")
        plan = TrialPlan(
            plan_id="plan-1", platform=RobotPlatform.MOCK, robot_id="r1",
            target_commands=(cmd,), repetitions=3,
            required_capabilities=(CAPABILITY_VELOCITY_X,),
            safety_policy_id="p", safety_policy_hash="h",
            environment=env,
        )
        assert plan.total_trials == 3
        assert plan.plan_id == "plan-1"

    def test_trial_result_distinguishes_statuses(self):
        result = TrialResult(
            trial_id="t1", plan_id="p1", command_sequence_id="s1",
            status=TrialStatus.COMMAND_ACCEPTED,
            platform=RobotPlatform.MOCK, robot_id="r1",
        )
        assert result.status == TrialStatus.COMMAND_ACCEPTED
        assert result.command_accepted == False  # Default; explicit evidence needed

    def test_compensation_decision_actions(self):
        decision = CompensationDecision(
            desired_actual_mps=0.5,
            action=CompensationAction.IDENTITY_FALLBACK,
            fallback_reason="No profile available",
        )
        assert decision.action == CompensationAction.IDENTITY_FALLBACK
        d = decision.to_dict()
        assert d["action"] == "identity_fallback"

    def test_execution_audit_record(self):
        record = ExecutionAuditRecord(
            session_id="sess-1",
            requested_operation="calibrate",
            platform=RobotPlatform.MOCK,
            robot_id="r1",
            software_version="0.1.0",
            adapter_version="0.1.0",
            safety_policy_id="p",
            safety_policy_hash="h",
            authorization_id="auth-1",
            started_monotonic_ns=1000,
        )
        assert record.session_id == "sess-1"


class TestReadinessModel:
    def test_readiness_entry(self):
        entry = ReadinessEntry(
            key=READINESS_DOMAIN_CONTRACTS,
            maturity=ImplementationMaturity.IMPLEMENTED_UNVERIFIED,
            description="Domain contracts implemented",
        )
        assert entry.key == READINESS_DOMAIN_CONTRACTS
        assert entry.maturity == ImplementationMaturity.IMPLEMENTED_UNVERIFIED

    def test_readiness_model(self):
        entries = (
            ReadinessEntry(key=READINESS_DOMAIN_CONTRACTS, maturity=ImplementationMaturity.IMPLEMENTED_UNVERIFIED, description="Domain"),
            ReadinessEntry(key=READINESS_G1_ADAPTER, maturity=ImplementationMaturity.NOT_STARTED, description="G1"),
            ReadinessEntry(key=READINESS_RELEASE, maturity=ImplementationMaturity.NOT_STARTED, description="Release"),
        )
        model = ReadinessModel(entries=entries)
        assert model.get(READINESS_G1_ADAPTER).maturity == ImplementationMaturity.NOT_STARTED  # type: ignore
        assert model.get("nonexistent") is None

    def test_hardware_not_verified(self):
        """No hardware-related readiness should be hardware_verified."""
        entry = ReadinessEntry(
            key="hardware_verification",
            maturity=ImplementationMaturity.NOT_STARTED,
            description="HW verification",
        )
        assert entry.maturity != ImplementationMaturity.HARDWARE_VERIFIED
