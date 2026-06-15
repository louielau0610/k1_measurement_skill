"""Tests for domain safety contracts."""
import pytest
from calibration_skill.domain.enums import CoordinateFrame, PreflightStatus, RobotPlatform
from calibration_skill.domain.safety import (
    OperatorAuthorization, PreflightCheck, PreflightReport, SafetyEnvelope,
)


class TestSafetyEnvelope:
    def test_valid_construction(self):
        envelope = SafetyEnvelope(
            policy_id="pol-1", policy_hash="abc",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        assert envelope.policy_id == "pol-1"

    def test_no_silent_numerical_defaults(self):
        """SafetyEnvelope requires explicit values."""
        with pytest.raises(TypeError):
            SafetyEnvelope()  # type: ignore

    def test_empty_policy_id_rejected(self):
        with pytest.raises(ValueError):
            SafetyEnvelope(
                policy_id="", policy_hash="h",
                max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
                max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
                stop_timeout_s=5.0,
                allowed_command_frames=(CoordinateFrame.BODY,),
                operator_authorization_required=True,
            )

    def test_negative_max_vx_rejected(self):
        with pytest.raises(ValueError):
            SafetyEnvelope(
                policy_id="p", policy_hash="h",
                max_abs_vx_mps=-1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
                max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
                stop_timeout_s=5.0,
                allowed_command_frames=(CoordinateFrame.BODY,),
                operator_authorization_required=True,
            )

    def test_zero_duration_rejected(self):
        with pytest.raises(ValueError):
            SafetyEnvelope(
                policy_id="p", policy_hash="h",
                max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
                max_command_duration_s=0.0, max_telemetry_age_ms=500.0,
                stop_timeout_s=5.0,
                allowed_command_frames=(CoordinateFrame.BODY,),
                operator_authorization_required=True,
            )

    def test_empty_allowed_frames_rejected(self):
        with pytest.raises(ValueError):
            SafetyEnvelope(
                policy_id="p", policy_hash="h",
                max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
                max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
                stop_timeout_s=5.0,
                allowed_command_frames=(),
                operator_authorization_required=True,
            )

    def test_policy_hash_mismatch(self):
        from calibration_skill.domain.motion import VelocityCommand
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="wrong", source="test",
        )
        envelope = SafetyEnvelope(
            policy_id="pol-1", policy_hash="correct",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.1, max_abs_wz_radps=0.1,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        errors = envelope.validate_command(cmd)
        assert len(errors) > 0


class TestOperatorAuthorization:
    def test_valid_construction(self):
        auth = OperatorAuthorization(
            authorization_id="auth-1", operator_id="op-1",
            platform=RobotPlatform.BOOSTER_K1, robot_id="k1-01",
            issued_monotonic_ns=1000, expiry_monotonic_ns=10000,
            authorized_operations=("calibrate",),
            safety_policy_id="pol-1", safety_policy_hash="hash",
            evidence_reference="ref-1",
        )
        assert auth.authorization_id == "auth-1"

    def test_is_valid(self):
        auth = OperatorAuthorization(
            authorization_id="a1", operator_id="op1",
            platform=RobotPlatform.MOCK, robot_id="r1",
            issued_monotonic_ns=1000, expiry_monotonic_ns=5000,
            authorized_operations=("test",),
            safety_policy_id="p", safety_policy_hash="h",
            evidence_reference="e",
        )
        assert auth.is_valid(2000) is True
        assert auth.is_valid(5000) is False
        assert auth.is_valid(500) is False

    def test_is_expired(self):
        auth = OperatorAuthorization(
            authorization_id="a1", operator_id="op1",
            platform=RobotPlatform.MOCK, robot_id="r1",
            issued_monotonic_ns=1000, expiry_monotonic_ns=5000,
            authorized_operations=("test",),
            safety_policy_id="p", safety_policy_hash="h",
            evidence_reference="e",
        )
        assert auth.is_expired(6000) is True
        assert auth.is_expired(2000) is False

    def test_expiry_before_issue_rejected(self):
        with pytest.raises(ValueError):
            OperatorAuthorization(
                authorization_id="a1", operator_id="op1",
                platform=RobotPlatform.MOCK, robot_id="r1",
                issued_monotonic_ns=5000, expiry_monotonic_ns=1000,
                authorized_operations=("test",),
                safety_policy_id="p", safety_policy_hash="h",
                evidence_reference="e",
            )


class TestPreflightReport:
    def test_overall_status_passed(self):
        check = PreflightCheck(check_id="c1", name="Check 1", status=PreflightStatus.PASSED)
        report = PreflightReport(
            platform=RobotPlatform.MOCK, robot_id="r1",
            checked_monotonic_ns=1000, checks=(check,),
        )
        assert report.overall_status == PreflightStatus.PASSED
        assert report.is_ready is True

    def test_overall_status_failed(self):
        passed = PreflightCheck(check_id="c1", name="OK", status=PreflightStatus.PASSED)
        failed = PreflightCheck(check_id="c2", name="Fail", status=PreflightStatus.FAILED)
        report = PreflightReport(
            platform=RobotPlatform.MOCK, robot_id="r1",
            checked_monotonic_ns=1000, checks=(passed, failed),
        )
        assert report.overall_status == PreflightStatus.FAILED
        assert report.is_ready is False
        assert len(report.blockers) == 1

    def test_warnings_distinct_from_blockers(self):
        warn = PreflightCheck(check_id="c1", name="Warn", status=PreflightStatus.WARNING)
        report = PreflightReport(
            platform=RobotPlatform.MOCK, robot_id="r1",
            checked_monotonic_ns=1000, checks=(warn,),
        )
        assert report.overall_status == PreflightStatus.WARNING
        assert len(report.warnings) == 1
        assert len(report.blockers) == 0
        assert report.is_ready is True  # Warnings do not block
