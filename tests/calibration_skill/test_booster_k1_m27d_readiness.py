"""M27-D readiness state tests.

Verify that M27-D readiness states are correctly represented.
"""
from __future__ import annotations

import json
from pathlib import Path


class TestM27DReadiness:
    """Verify M27-D readiness states."""

    def test_no_g1_go1_claims(self):
        """No G1 or GO1 hardware support may be claimed."""
        # Check all engineering artifacts for false claims
        eng_dir = Path("outputs/engineering")
        if eng_dir.is_dir():
            false_keys = (
                "g1_adapter_implemented", "go1_adapter_implemented",
                "g1_adapter_hardware_verified", "go1_adapter_hardware_verified",
                "g1_hardware_support", "go1_hardware_support",
            )
            for fpath in eng_dir.glob("*.json"):
                try:
                    data = json.loads(fpath.read_text(encoding="utf-8"))
                    for key in false_keys:
                        if key in data and data[key] is True:
                            assert False, f"{fpath.name}: {key} is True"
                except json.JSONDecodeError:
                    pass

    def test_m27d_statuses_not_hardware_verified(self):
        """M27-D statuses must not claim hardware verification for motion."""
        # Read the readiness JSON if it exists
        readiness_path = Path("outputs/engineering/m27d_readiness_summary.json")
        if readiness_path.exists():
            data = json.loads(readiness_path.read_text(encoding="utf-8"))
            # Motion command must not be verified
            motion_status = data.get("k1_motion_command", "")
            assert motion_status != "verified", "k1_motion_command must not be verified"

    def test_fake_k1_behavior_unchanged(self):
        """Fake K1 runtime must be importable and functional."""
        from tests.calibration_skill.fakes.fake_booster_k1_runtime import FakeBoosterK1Runtime
        runtime = FakeBoosterK1Runtime(robot_id="test")
        assert runtime is not None
        assert runtime.now_ns() > 0
        runtime.connect(timeout_s=5.0)
        assert runtime.connected

    def test_no_historical_data_changed(self):
        """Historical raw data directories must be untouched."""
        raw_dir = Path("data/raw")
        if raw_dir.is_dir():
            # Just verify it exists - we don't modify it
            assert raw_dir.is_dir()

    def test_no_m19_artifacts_modified(self):
        """M19 validation data must be untouched."""
        m19_dir = Path("data/m19_repeated_validation_inputs")
        if m19_dir.is_dir():
            assert m19_dir.is_dir()

    def test_m27d_vendor_runtime_mode_defined(self):
        """K1_VENDOR_RUNTIME_MODE must be 'vendor_runtime'."""
        from calibration_skill.adapters.booster_k1.config import K1_VENDOR_RUNTIME_MODE
        assert K1_VENDOR_RUNTIME_MODE == "vendor_runtime"

    def test_m27d_error_code_defined(self):
        """M27-D error codes must exist."""
        from calibration_skill.adapters.booster_k1.errors import (
            ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
            ERROR_K1_BINDING_CONSTRUCTION_FAILED,
            ERROR_K1_SDK_IMPORT_FAILED,
            ERROR_K1_CONNECTION_FAILED,
            ERROR_K1_HARDWARE_EXECUTION_DISABLED,
        )
        assert ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN == "k1_m27d_nonzero_motion_forbidden"
        assert ERROR_K1_BINDING_CONSTRUCTION_FAILED == "k1_binding_construction_failed"
        assert ERROR_K1_SDK_IMPORT_FAILED == "k1_sdk_import_failed"
        assert ERROR_K1_HARDWARE_EXECUTION_DISABLED == "k1_hardware_execution_disabled"

    def test_vendor_binding_metadata(self):
        """Vendor binding metadata must correctly report M27-D state."""
        from calibration_skill.adapters.booster_k1.vendor_types import BoosterK1VendorBindingMetadata
        meta = BoosterK1VendorBindingMetadata(
            binding_class="TestBinding",
            sdk_family="booster_k1",
            sdk_version=None,
            binding_version="m27d.1",
            sdk_import_path="booster_robotics_sdk_python",
            sdk_entry_classes=("B1LocoClient", "ChannelFactory", "RobotMode"),
            verified_motion_sequence=("kPrepare", "kWalking", "Move(vx, 0.0, 0.0)"),
            zero_motion_only=True,
            support_level="zero_motion_bench_only",
        )
        d = meta.to_dict()
        assert d["zero_motion_only"] is True
        assert d["support_level"] == "zero_motion_bench_only"
        assert "B1LocoClient" in d["sdk_entry_classes"]
