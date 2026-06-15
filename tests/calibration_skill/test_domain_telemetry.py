"""Tests for domain telemetry contracts."""
import math
import pytest
from calibration_skill.domain.telemetry import (
    Pose3D, Quaternion, TelemetrySample, Twist3D, Vector3,
)


class TestVector3:
    def test_default_zero(self):
        v = Vector3()
        assert v.x == 0.0 and v.y == 0.0 and v.z == 0.0

    def test_nan_rejected(self):
        with pytest.raises(ValueError):
            Vector3(x=float("nan"))

    def test_inf_rejected(self):
        with pytest.raises(ValueError):
            Vector3(y=float("inf"))


class TestQuaternion:
    def test_default_identity(self):
        q = Quaternion()
        assert q.w == 1.0

    def test_zero_norm_rejected(self):
        with pytest.raises(ValueError):
            Quaternion(x=0.0, y=0.0, z=0.0, w=0.0)


class TestTelemetrySample:
    def test_valid_construction(self):
        sample = TelemetrySample(
            robot_id="k1-01",
            sample_sequence_id=1,
            received_monotonic_ns=1000,
        )
        assert sample.robot_id == "k1-01"
        assert sample.pose is None

    def test_age_calculation(self):
        sample = TelemetrySample(
            robot_id="k1",
            sample_sequence_id=0,
            received_monotonic_ns=1000,
        )
        assert sample.age_ns(1500) == 500
        assert sample.age_ns(1000) == 0

    def test_future_timestamp_age_zero(self):
        sample = TelemetrySample(
            robot_id="k1",
            sample_sequence_id=0,
            received_monotonic_ns=2000,
        )
        assert sample.age_ns(1000) == 0

    def test_is_stale(self):
        sample = TelemetrySample(
            robot_id="k1",
            sample_sequence_id=0,
            received_monotonic_ns=1000,
        )
        assert sample.is_stale(1500, 1000) is False
        assert sample.is_stale(2500, 1000) is True

    def test_missing_data_not_fabricated_as_zero(self):
        sample = TelemetrySample(
            robot_id="k1",
            sample_sequence_id=0,
            received_monotonic_ns=1000,
        )
        assert sample.heading_rad is None  # Not 0.0
        assert sample.battery_voltage is None  # Not 0.0

    def test_zero_values_preserved(self):
        sample = TelemetrySample(
            robot_id="k1",
            sample_sequence_id=0,
            received_monotonic_ns=1000,
            heading_rad=0.0,
        )
        assert sample.heading_rad == 0.0  # Zero is a valid measurement
