import pytest

from calibration_skill.adapters.booster_k1.registry import (
    register_booster_k1_fake_adapter,
    register_booster_k1_vendor_adapter,
)
from calibration_skill.adapters.booster_k1.vendor_runtime import BoosterK1RuntimeUnavailable
from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from fakes.fake_booster_k1_runtime import FakeBoosterK1Runtime
from test_booster_k1_hardware_gate import valid_gate


def test_default_registry_and_service_do_not_register_vendor_k1():
    assert AdapterRegistry().list_registered_platforms() == ()
    assert build_mock_dry_run_service().registry.list_registered_platforms() == (RobotPlatform.MOCK,)


def test_fake_k1_registration_remains_explicit():
    registry = AdapterRegistry()
    register_booster_k1_fake_adapter(registry, lambda config: FakeBoosterK1Runtime())
    assert registry.list_registered_platforms() == (RobotPlatform.BOOSTER_K1,)


def test_vendor_k1_registration_explicit_and_fail_closed():
    registry = AdapterRegistry()
    register_booster_k1_vendor_adapter(registry)
    config = ConnectionConfig(
        platform=RobotPlatform.BOOSTER_K1,
        robot_id="k1-test",
        extra={
            "now_ns": 1,
            "safety_policy_id": "k1-safe",
            "safety_policy_hash": "hash",
            "hardware_gate": valid_gate(),
        },
    )
    with pytest.raises(BoosterK1RuntimeUnavailable):
        registry.create_adapter(RobotPlatform.BOOSTER_K1, config, dry_run=True)


def test_vendor_registration_rejects_missing_gate():
    registry = AdapterRegistry()
    register_booster_k1_vendor_adapter(registry)
    config = ConnectionConfig(
        platform=RobotPlatform.BOOSTER_K1,
        robot_id="k1-test",
        extra={"now_ns": 1, "safety_policy_id": "k1-safe", "safety_policy_hash": "hash"},
    )
    with pytest.raises(BoosterK1RuntimeUnavailable):
        registry.create_adapter(RobotPlatform.BOOSTER_K1, config, dry_run=True)


def test_cli_manifest_still_not_real_k1_supported():
    from calibration_skill.skill.manifest import build_skill_manifest

    k1 = build_skill_manifest()["platform_support"]["booster_k1"]
    assert k1["status"] != "supported"
    assert k1["dry_run_only"] is False


def test_default_cli_cannot_invoke_k1_real_runtime():
    from calibration_skill.skill.service import SkillService

    service = SkillService(registry=AdapterRegistry())
    request = {
        "schema_version": "1.0.0",
        "request_id": "k1-real",
        "operation": "preflight",
        "platform": "booster_k1",
        "robot_id": "k1-test",
        "dry_run": False,
        "payload": {},
    }
    response = service.handle_request(request)
    assert response["status"] in {"rejected", "failed"}
    assert response["error"]["code"] in {"unsupported_platform", "configuration_invalid"}
