import json
from pathlib import Path


def test_m27b_readiness_values_are_fake_runtime_only():
    data = json.loads(Path("outputs/engineering/m27b_readiness.json").read_text(encoding="utf-8"))
    readiness = data["readiness"]
    assert readiness["k1_adapter_migration"]["maturity"] in {"implemented_unverified", "fake_runtime_verified"}
    assert readiness["k1_new_runtime_support"]["maturity"] == "fake_runtime_only"
    assert readiness["k1_hardware_verification"]["maturity"] == "not_started"
    assert readiness["hardware_verification"]["maturity"] == "not_started"
    assert readiness["release"]["maturity"] == "pre_release_only"


def test_m27b_validation_summary_does_not_claim_hardware():
    data = json.loads(Path("outputs/engineering/m27b_validation_summary.json").read_text(encoding="utf-8"))
    assert data["hardware_used"] is False
    assert data["vendor_sdk_imported"] is False
    assert data["default_k1_registration"] is False
