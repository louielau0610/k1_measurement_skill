import pytest

from calibration_skill.adapters.mock import MockRobotAdapter, default_mock_capabilities
from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig


def _factory(config):
    from calibration_skill.adapters.mock import DeterministicMonotonicClock
    return MockRobotAdapter(config=config, clock=DeterministicMonotonicClock())


def test_register_mock_factory_and_create_adapter():
    registry = AdapterRegistry()
    registry.register(RobotPlatform.MOCK, _factory, default_mock_capabilities())
    config = ConnectionConfig(platform=RobotPlatform.MOCK, robot_id="mock-robot")
    adapter = registry.create_adapter(RobotPlatform.MOCK, config, dry_run=True)
    assert adapter.identity.platform == RobotPlatform.MOCK
    assert registry.list_registered_platforms() == (RobotPlatform.MOCK,)


def test_duplicate_registration_rejected():
    registry = AdapterRegistry()
    registry.register(RobotPlatform.MOCK, _factory, default_mock_capabilities())
    with pytest.raises(ValueError, match="already registered"):
        registry.register(RobotPlatform.MOCK, _factory, default_mock_capabilities())


def test_unknown_platform_rejected():
    registry = AdapterRegistry()
    config = ConnectionConfig(platform=RobotPlatform.MOCK, robot_id="mock-robot")
    errors = registry.validate_request(RobotPlatform.MOCK, config, dry_run=True)
    assert errors[0].code == "unsupported_platform"


def test_real_platform_registration_and_creation_rejected():
    registry = AdapterRegistry()
    with pytest.raises(ValueError, match="only accepts mock"):
        registry.register(RobotPlatform.BOOSTER_K1, _factory, default_mock_capabilities())
    config = ConnectionConfig(platform=RobotPlatform.BOOSTER_K1, robot_id="k1")
    errors = registry.validate_request(RobotPlatform.BOOSTER_K1, config, dry_run=True)
    assert errors[0].code == "unsupported_platform"


def test_explicit_connection_config_and_dry_run_required():
    registry = AdapterRegistry()
    registry.register(RobotPlatform.MOCK, _factory, default_mock_capabilities())
    assert registry.validate_request(RobotPlatform.MOCK, None, dry_run=True)[0].code == "unsupported_platform"
    config = ConnectionConfig(platform=RobotPlatform.MOCK, robot_id="mock-robot")
    assert registry.validate_request(RobotPlatform.MOCK, config, dry_run=False)[0].code == "unsupported_platform"
