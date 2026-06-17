import json
from pathlib import Path


def test_m27c_readiness_values_are_boundary_only():
    data = json.loads(Path("outputs/engineering/m27c_readiness.json").read_text(encoding="utf-8"))
    readiness = data["readiness"]
    assert readiness["k1_adapter_migration"]["maturity"] == "fake_runtime_verified"
    assert readiness["k1_new_runtime_support"]["maturity"] == "fake_runtime_only"
    assert readiness["k1_vendor_runtime_boundary"]["maturity"] == "bench_verified"
    assert readiness["k1_vendor_runtime"]["maturity"] == "not_implemented"
    assert readiness["k1_hardware_gate"]["maturity"] == "bench_verified"
    assert readiness["k1_hardware_verification"]["maturity"] == "not_started"
    assert readiness["hardware_verification"]["maturity"] == "not_started"
    assert readiness["release"]["maturity"] == "pre_release_only"


def test_m27c_vendor_status_is_disabled():
    data = json.loads(Path("outputs/engineering/m27c_vendor_runtime_status.json").read_text(encoding="utf-8"))
    assert data["vendor_runtime_implemented"] is False
    assert data["hardware_enabled"] is False
    assert data["ordinary_runtime_import_safe"] is True


def test_m27c_validation_summary_no_hardware():
    data = json.loads(Path("outputs/engineering/m27c_validation_summary.json").read_text(encoding="utf-8"))
    assert data["hardware_used"] is False
    assert data["vendor_sdk_imported"] is False
    assert data["default_k1_real_registration"] is False
