"""Tests for deterministic JSON codecs."""
import json
import pytest
from calibration_skill.domain.enums import (
    CommandDisposition, CoordinateFrame, RobotMorphology, RobotPlatform,
)
from calibration_skill.domain.identity import RobotIdentity
from calibration_skill.domain.motion import CommandReceipt, VelocityCommand
from calibration_skill.domain.safety import SafetyEnvelope
from calibration_skill.domain.telemetry import TelemetrySample
from calibration_skill.schemas.codec import (
    canonical_json_dumps,
    decode_command_receipt,
    decode_robot_identity,
    decode_safety_envelope,
    decode_velocity_command,
    encode_command_receipt,
    encode_robot_identity,
    encode_safety_envelope,
    encode_velocity_command,
)


class TestRobotIdentityCodec:
    def test_round_trip(self):
        original = RobotIdentity(
            platform=RobotPlatform.BOOSTER_K1,
            morphology=RobotMorphology.BIPED_HUMANOID,
            robot_id="k1-01",
            adapter_name="k1_adapter",
            adapter_version="2.0.0",
        )
        encoded = encode_robot_identity(original)
        decoded = decode_robot_identity(encoded)
        assert decoded.platform == original.platform
        assert decoded.robot_id == original.robot_id
        assert decoded.adapter_name == original.adapter_name

    def test_no_nan_in_output(self):
        identity = RobotIdentity(
            platform=RobotPlatform.MOCK,
            morphology=RobotMorphology.SYNTHETIC,
            robot_id="test",
            adapter_name="mock",
            adapter_version="1.0.0",
        )
        encoded = encode_robot_identity(identity)
        json_str = json.dumps(encoded)
        assert "NaN" not in json_str
        assert "Infinity" not in json_str


class TestVelocityCommandCodec:
    def test_round_trip(self):
        original = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="seq-1", issued_monotonic_ns=1000, expiry_monotonic_ns=2000,
            requested_duration_s=5.0, frame=CoordinateFrame.BODY,
            safety_policy_id="pol-1", safety_policy_hash="abc", source="test",
        )
        encoded = encode_velocity_command(original)
        decoded = decode_velocity_command(encoded)
        assert decoded.vx_mps == original.vx_mps
        assert decoded.sequence_id == original.sequence_id
        assert decoded.frame == original.frame

    def test_stable_enum_values(self):
        cmd = VelocityCommand(
            vx_mps=0.5, vy_mps=0.0, wz_radps=0.0,
            sequence_id="s", issued_monotonic_ns=1, expiry_monotonic_ns=2,
            requested_duration_s=1.0, frame=CoordinateFrame.ODOM,
            safety_policy_id="p", safety_policy_hash="h", source="test",
        )
        encoded = encode_velocity_command(cmd)
        assert encoded["frame"] == "odom"  # Stable lowercase string


class TestCommandReceiptCodec:
    def test_round_trip(self):
        original = CommandReceipt(
            command_sequence_id="seq-1",
            disposition=CommandDisposition.ACCEPTED,
            received_monotonic_ns=1000,
        )
        encoded = encode_command_receipt(original)
        decoded = decode_command_receipt(encoded)
        assert decoded.disposition == original.disposition


class TestSafetyEnvelopeCodec:
    def test_round_trip(self):
        original = SafetyEnvelope(
            policy_id="pol-1", policy_hash="abc",
            max_abs_vx_mps=1.0, max_abs_vy_mps=0.5, max_abs_wz_radps=0.3,
            max_command_duration_s=10.0, max_telemetry_age_ms=500.0,
            stop_timeout_s=5.0,
            allowed_command_frames=(CoordinateFrame.BODY, CoordinateFrame.ODOM),
            operator_authorization_required=True,
        )
        encoded = encode_safety_envelope(original)
        decoded = decode_safety_envelope(encoded)
        assert decoded.policy_id == original.policy_id
        assert decoded.max_abs_vx_mps == original.max_abs_vx_mps


class TestCanonicalJson:
    def test_deterministic_output(self):
        obj = {"b": 2, "a": 1}
        s1 = canonical_json_dumps(obj)
        s2 = canonical_json_dumps(obj)
        assert s1 == s2
        # Keys should be sorted
        assert s1 == '{"a":1,"b":2}'
