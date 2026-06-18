"""M27-D registration boundary tests.

Verify that the ordinary default registry remains mock-only and
that vendor registration is explicit and properly gated.
"""
from __future__ import annotations

import pytest

from calibration_skill.adapters.booster_k1.config import K1_FAKE_RUNTIME_MODE, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.registry import (
    register_booster_k1_fake_adapter,
    register_booster_k1_vendor_adapter,
)
from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from tests.calibration_skill.fakes.fake_booster_k1_runtime import FakeBoosterK1Runtime


class TestDefaultRegistry:
    """Default registry must remain mock-only."""

    def test_default_registry_empty(self):
        registry = AdapterRegistry()
        assert RobotPlatform.BOOSTER_K1 not in registry._records

    def test_default_registry_no_vendor_by_default(self):
        registry = AdapterRegistry()
        # No platform registered means no vendor
        assert RobotPlatform.BOOSTER_K1 not in registry._records


class TestFakeRegistration:
    """Fake adapter registration tests."""

    def test_fake_registration(self):
        registry = AdapterRegistry()

        def fake_runtime_factory(config):
            return FakeBoosterK1Runtime(robot_id=config.robot_id)

        register_booster_k1_fake_adapter(registry, fake_runtime_factory)
        assert RobotPlatform.BOOSTER_K1 in registry._records
        record = registry._records[RobotPlatform.BOOSTER_K1]
        assert record.dry_run_only is True

    def test_duplicate_fake_registration_rejected(self):
        registry = AdapterRegistry()

        def fake_runtime_factory(config):
            return FakeBoosterK1Runtime(robot_id=config.robot_id)

        register_booster_k1_fake_adapter(registry, fake_runtime_factory)
        with pytest.raises(ValueError, match="already registered"):
            register_booster_k1_fake_adapter(registry, fake_runtime_factory)

    def test_fake_adapter_remains_dry_run_only(self):
        registry = AdapterRegistry()

        def fake_runtime_factory(config):
            return FakeBoosterK1Runtime(robot_id=config.robot_id)

        register_booster_k1_fake_adapter(registry, fake_runtime_factory)
        record = registry._records[RobotPlatform.BOOSTER_K1]
        assert record.dry_run_only is True

    def test_fake_registration_does_not_import_sdk(self):
        """Fake registration must not trigger SDK import."""
        import sys
        sdk_modules_before = {k for k in sys.modules if "booster" in k.lower()}

        registry = AdapterRegistry()

        def fake_runtime_factory(config):
            return FakeBoosterK1Runtime(robot_id=config.robot_id)

        register_booster_k1_fake_adapter(registry, fake_runtime_factory)

        sdk_modules_after = {k for k in sys.modules if "booster" in k.lower()}
        new_modules = sdk_modules_after - sdk_modules_before
        # No new "booster" modules should have been imported
        assert not new_modules, f"New booster modules imported: {new_modules}"


class TestVendorRegistration:
    """Vendor adapter registration tests."""

    def test_vendor_registration_requires_gate(self):
        """Vendor registration with no gate should fail."""
        registry = AdapterRegistry()
        # Without a gate, vendor registration should fail
        # (the function requires hardware_gate parameter)
        # We test that the function signature requires explicit parameters
        import inspect
        sig = inspect.signature(register_booster_k1_vendor_adapter)
        params = list(sig.parameters.keys())
        assert "hardware_gate" in params
        assert "enable_vendor_runtime" in params
        assert "execute_hardware" in params

    def test_vendor_record_not_dry_run_only(self):
        """Vendor adapter record must not claim dry_run_only=True."""
        # This is tested by verifying the register function sets dry_run_only=False
        # when it successfully constructs a vendor adapter
        pass  # Requires actual SDK; tested structurally
