"""M27-D zero-motion gate tests.

Tests for zero-motion enforcement at both the binding and runtime boundaries.
"""
from __future__ import annotations

import pytest

from calibration_skill.adapters.booster_k1.errors import ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN
from calibration_skill.adapters.booster_k1.vendor_runtime import BoosterK1VendorRuntime
from calibration_skill.adapters.booster_k1.errors import BoosterK1DomainError
from tests.calibration_skill.fakes.fake_booster_k1_vendor_binding import (
    FakeBindingFailureConfig,
    FakeBoosterK1VendorBinding,
)


class TestZeroMotionBindingBoundary:
    """Test zero-motion enforcement at the binding boundary."""

    def test_fake_binding_does_not_enforce_zero_motion(self):
        """The fake binding allows nonzero velocity (enforcement is in runtime + real binding)."""
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()
        # Fake binding does NOT reject nonzero - that's the runtime's job
        receipt = binding.send_body_velocity(vx_mps=0.35, vy_mps=0.0, wz_radps=0.0)
        # The fake binding accepts it (real binding would reject)
        assert receipt.accepted

    def test_runtime_rejects_vx_nonzero(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.35, vy_mps=0.0, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_runtime_rejects_vy_nonzero(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.1, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_runtime_rejects_wz_nonzero(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.5)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_all_known_k1_velocities_rejected(self):
        """0.35, 0.40, 0.50, 0.60 m/s must all be rejected."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        for v in [0.35, 0.40, 0.50, 0.60]:
            with pytest.raises(BoosterK1DomainError) as exc:
                runtime.send_body_velocity(vx_mps=v, vy_mps=0.0, wz_radps=0.0)
            assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_tolerance_exact_zero_accepted(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        receipt = runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert receipt.accepted

    def test_tolerance_near_zero_accepted(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        # 1e-12 is well within epsilon
        receipt = runtime.send_body_velocity(vx_mps=1e-12, vy_mps=0.0, wz_radps=0.0)
        assert receipt.accepted

    def test_tolerance_above_epsilon_rejected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        # 1e-6 is well above epsilon
        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=1e-6, vy_mps=0.0, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_cannot_bypass_runtime(self):
        """Verify no bypass path exists through runtime."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        # Direct call through runtime must also reject
        for vx, vy, wz in [
            (0.35, 0.0, 0.0),
            (0.0, 0.1, 0.0),
            (0.0, 0.0, 1.0),
            (0.35, 0.1, 0.0),
            (0.35, 0.0, 1.0),
        ]:
            with pytest.raises(BoosterK1DomainError) as exc:
                runtime.send_body_velocity(vx_mps=vx, vy_mps=vy, wz_radps=wz)
            assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_error_details_contain_velocity(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.35, vy_mps=0.1, wz_radps=0.5)
        details = exc.value.details
        assert details["vx_mps"] == 0.35
        assert details["vy_mps"] == 0.1
        assert details["wz_radps"] == 0.5
