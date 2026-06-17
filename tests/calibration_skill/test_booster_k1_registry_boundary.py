import pytest

from calibration_skill.adapters.booster_k1.registry import register_booster_k1_fake_adapter
from calibration_skill.adapters.mock import default_mock_capabilities
from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from fakes.fake_booster_k1_runtime import FakeBoosterK1Runtime


def k1_connection(**extra_overrides):
    extra = {
        "connection_profile_id": "fake-profile",
        "runtime_mode": "fake_booster_runtime",
        "dry_run": True,
        "allow_hardware": False,
        "safety_policy_id": "k1-safe",
        "safety_policy_hash": "hash",
        "max_abs_vx_mps": 0.6,
        "max_abs_vy_mps": 0.0,
        "max_abs_wz_radps": 0.0,
        "command_timeout_s": 0.5,
        "telemetry_timeout_s": 1.0,
        "stop_timeout_s": 0.5,
    }
    extra.update(extra_overrides)
    return ConnectionConfig(platform=RobotPlatform.BOOSTER_K1, robot_id="k1-test", extra=extra)


def test_k1_not_registered_by_default_and_default_service_mock_only():
    registry = AdapterRegistry()
    assert registry.list_registered_platforms() == ()
    assert RobotPlatform.BOOSTER_K1 not in build_mock_dry_run_service().registry.list_registered_platforms()


def test_standard_register_still_rejects_k1():
    registry = AdapterRegistry()
    with pytest.raises(ValueError, match="only accepts mock"):
        registry.register(RobotPlatform.BOOSTER_K1, lambda cfg: None, default_mock_capabilities())  # type: ignore[arg-type]


def test_explicit_fake_registration_works_and_create_adapter():
    registry = AdapterRegistry()
    register_booster_k1_fake_adapter(registry, lambda config: FakeBoosterK1Runtime(robot_id=config.robot_id))
    adapter = registry.create_adapter(RobotPlatform.BOOSTER_K1, k1_connection(), dry_run=True)
    assert adapter.identity.platform == RobotPlatform.BOOSTER_K1
    assert registry.list_registered_platforms() == (RobotPlatform.BOOSTER_K1,)


def test_duplicate_explicit_registration_rejected():
    registry = AdapterRegistry()
    register_booster_k1_fake_adapter(registry, lambda config: FakeBoosterK1Runtime())
    with pytest.raises(ValueError, match="already registered"):
        register_booster_k1_fake_adapter(registry, lambda config: FakeBoosterK1Runtime())


def test_real_hardware_config_rejected():
    registry = AdapterRegistry()
    register_booster_k1_fake_adapter(registry, lambda config: FakeBoosterK1Runtime())
    with pytest.raises(ValueError, match="dry-run fake runtime"):
        registry.create_adapter(RobotPlatform.BOOSTER_K1, k1_connection(allow_hardware=True), dry_run=True)


def test_cli_manifest_remains_mock_only_for_default_runtime():
    from calibration_skill.skill.manifest import build_skill_manifest

    manifest = build_skill_manifest()
    assert manifest["safety_requirements"]["platform_must_be"] == "mock"
    assert manifest["platform_support"]["booster_k1"]["status"] != "supported"
