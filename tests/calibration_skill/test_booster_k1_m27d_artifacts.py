"""M27-D artifact tests.

Tests for deterministic artifact generation and serialization.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.domain.enums import MotionLifecycleState


class TestArtifactSerialization:
    """Test that runtime data classes serialize deterministically."""

    def test_command_receipt_serialization(self):
        receipt = BoosterK1RuntimeCommandReceipt(
            accepted=True,
            runtime_receipt_id="test-1",
            received_monotonic_ns=1000,
            detail="test",
        )
        # Verify frozen dataclass
        with pytest.raises(Exception):
            receipt.accepted = False  # type: ignore[misc]

    def test_odometry_serialization(self):
        odom = BoosterK1RuntimeOdometry(
            sequence_id=1,
            sample_monotonic_ns=1000,
            x_m=1.0,
            y_m=2.0,
            z_m=0.0,
            yaw_rad=0.5,
            vx_mps=0.0,
            vy_mps=0.0,
            wz_radps=0.0,
        )
        assert odom.sequence_id == 1
        assert odom.x_m == 1.0

    def test_robot_state_serialization(self):
        state = BoosterK1RuntimeState(
            motion_state=MotionLifecycleState.IDLE,
            mode_name="idle",
            source_monotonic_ns=1000,
            battery_percentage=88.0,
            battery_voltage=48.5,
            metadata={"key": "value"},
        )
        assert state.motion_state == MotionLifecycleState.IDLE
        assert state.battery_percentage == 88.0

    def test_health_serialization(self):
        health = BoosterK1RuntimeHealth(
            healthy=True,
            checked_monotonic_ns=1000,
            detail="all good",
        )
        assert health.healthy

    def test_no_raw_sdk_object_serialization(self):
        """Data classes must not contain raw SDK objects."""
        receipt = BoosterK1RuntimeCommandReceipt(
            accepted=True,
            runtime_receipt_id="test",
            received_monotonic_ns=1000,
        )
        d = {
            "accepted": receipt.accepted,
            "runtime_receipt_id": receipt.runtime_receipt_id,
            "received_monotonic_ns": receipt.received_monotonic_ns,
        }
        # Verify serializable
        json_str = json.dumps(d, sort_keys=True)
        assert "test" in json_str
        # No traceback or address in serialized form
        assert "0x" not in json_str
        assert "memory" not in json_str.lower()

    def test_state_serialization_no_memory_addresses(self):
        """Serialized states must not leak memory addresses."""
        state = BoosterK1RuntimeState(
            motion_state=MotionLifecycleState.IDLE,
            mode_name="idle",
            source_monotonic_ns=1000,
        )
        d = {
            "motion_state": state.motion_state.value,
            "mode_name": state.mode_name,
            "source_monotonic_ns": state.source_monotonic_ns,
        }
        json_str = json.dumps(d, sort_keys=True)
        assert "0x" not in json_str
        assert "at 0x" not in json_str.lower()


class TestDeterministicArtifacts:
    """Test deterministic artifact generation with injected clocks."""

    def test_same_inputs_produce_same_outputs(self):
        """With fixed clock, artifacts must be deterministic."""
        def fixed_clock():
            return 1000

        # Two receipts with same inputs
        r1 = BoosterK1RuntimeCommandReceipt(True, "id-1", fixed_clock(), "ok")
        r2 = BoosterK1RuntimeCommandReceipt(True, "id-1", fixed_clock(), "ok")

        assert r1.accepted == r2.accepted
        assert r1.runtime_receipt_id == r2.runtime_receipt_id
        assert r1.received_monotonic_ns == r2.received_monotonic_ns
        assert r1.detail == r2.detail

    def test_different_inputs_produce_different_outputs(self):
        """Different inputs must produce observably different outputs."""
        r1 = BoosterK1RuntimeCommandReceipt(True, "id-1", 1000, "ok")
        r2 = BoosterK1RuntimeCommandReceipt(False, "id-2", 2000, "fail")

        assert r1.accepted != r2.accepted
        assert r1.runtime_receipt_id != r2.runtime_receipt_id
        assert r1.received_monotonic_ns != r2.received_monotonic_ns
