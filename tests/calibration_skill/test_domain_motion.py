"""Tests for domain motion contracts."""
import math
import pytest
from calibration_skill.domain.enums import CoordinateFrame
from calibration_skill.domain.motion import CommandReceipt, VelocityCommand, validate_lifecycle_transition
from calibration_skill.domain.enums import CommandDisposition, MotionLifecycleState


class TestVelocityCommand:
    def test_valid_construction(self):
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="seq-001",
            issued_monotonic_ns=1000, expiry_monotonic_ns=2000,
            requested_duration_s=5.0,
            frame=CoordinateFrame.BODY,
            safety_policy_id="policy-1",
            safety_policy_hash="abc123",
            source="test",
        )
        assert cmd.vx_mps == 0.5
        assert cmd.sequence_id == "seq-001"

    def test_nan_vx_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=float("nan"), vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_inf_vy_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.0, vy_mps=float("inf"), wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_expiry_before_issue_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=2000, expiry_monotonic_ns=1000,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_expiry_equal_issue_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=1000, expiry_monotonic_ns=1000,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_zero_duration_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
                requested_duration_s=0.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_negative_duration_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
                requested_duration_s=-1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_empty_sequence_id_rejected(self):
        with pytest.raises(ValueError):
            VelocityCommand(
                vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
                sequence_id="", issued_monotonic_ns=1, expiry_monotonic_ns=2,
                requested_duration_s=1.0, frame=CoordinateFrame.BODY,
                safety_policy_id="p", safety_policy_hash="h", source="test",
            )

    def test_is_expired(self):
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1000, expiry_monotonic_ns=2000,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="p", safety_policy_hash="h", source="test",
        )
        assert cmd.is_expired(1500) is False
        assert cmd.is_expired(2000) is True
        assert cmd.is_expired(3000) is True

    def test_no_silent_max_velocity_default(self):
        """VelocityCommand has no default maximum velocity."""
        cmd = VelocityCommand(
            vx_mps=100.0, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="p", safety_policy_hash="h", source="test",
        )
        assert cmd.vx_mps == 100.0  # Accepted by domain; safety envelope validates

    def test_validate_against_envelope(self):
        from calibration_skill.domain.safety import SafetyEnvelope
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="hash1", source="test",
        )
        envelope = SafetyEnvelope(
            policy_id="pol-1", policy_hash="hash1",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.1, max_abs_wz_radps=0.1,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        errors = cmd.validate_against_envelope(envelope)
        assert len(errors) == 0

    def test_velocity_violation_detected(self):
        from calibration_skill.domain.safety import SafetyEnvelope
        cmd = VelocityCommand(
            vx_mps=2.0, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="hash1", source="test",
        )
        envelope = SafetyEnvelope(
            policy_id="pol-1", policy_hash="hash1",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.1, max_abs_wz_radps=0.1,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        errors = cmd.validate_against_envelope(envelope)
        assert len(errors) > 0

    def test_no_clamping(self):
        """Validation reports violations but does not clamp values."""
        from calibration_skill.domain.safety import SafetyEnvelope
        cmd = VelocityCommand(
            vx_mps=2.0, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="hash1", source="test",
        )
        envelope = SafetyEnvelope(
            policy_id="pol-1", policy_hash="hash1",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.1, max_abs_wz_radps=0.1,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        cmd.validate_against_envelope(envelope)
        assert cmd.vx_mps == 2.0  # Not clamped


class TestCommandReceipt:
    def test_valid_construction(self):
        receipt = CommandReceipt(
            command_sequence_id="seq-1",
            disposition=CommandDisposition.ACCEPTED,
            received_monotonic_ns=1000,
        )
        assert receipt.disposition == CommandDisposition.ACCEPTED

    def test_accepted_does_not_imply_motion(self):
        receipt = CommandReceipt(
            command_sequence_id="seq-1",
            disposition=CommandDisposition.ACCEPTED,
            received_monotonic_ns=1000,
        )
        # "accepted" just means the command was valid; does not prove movement
        assert receipt.disposition == CommandDisposition.ACCEPTED


class TestLifecycleTransitions:
    def test_valid_transition(self):
        errors = validate_lifecycle_transition(
            MotionLifecycleState.IDLE,
            MotionLifecycleState.PREPARING,
        )
        assert len(errors) == 0

    def test_invalid_transition(self):
        errors = validate_lifecycle_transition(
            MotionLifecycleState.IDLE,
            MotionLifecycleState.MOVING,
        )
        assert len(errors) > 0

    def test_same_state_allowed(self):
        errors = validate_lifecycle_transition(
            MotionLifecycleState.IDLE,
            MotionLifecycleState.IDLE,
        )
        assert len(errors) == 0
