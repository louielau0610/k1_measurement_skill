"""M26-C dry-run runtime composition for mock-only skill execution."""
from __future__ import annotations

from calibration_skill.adapters.mock import DeterministicMonotonicClock, MockFailureConfig, MockRobotAdapter, default_mock_capabilities
from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.ports.factory import ConnectionConfig
from calibration_skill.skill.service import SkillService


def build_mock_dry_run_service(
    *,
    clock: DeterministicMonotonicClock | None = None,
    failure_config: MockFailureConfig | None = None,
) -> SkillService:
    """Build a SkillService with only the mock adapter registered."""
    registry = AdapterRegistry()
    shared_clock = clock or DeterministicMonotonicClock()
    failures = failure_config or MockFailureConfig()

    def create(config: ConnectionConfig) -> MockRobotAdapter:
        return MockRobotAdapter(config=config, clock=shared_clock, failure_config=failures)

    registry.register(config_platform_mock(), create, default_mock_capabilities())
    return SkillService(registry=registry)


def config_platform_mock():
    from calibration_skill.domain.enums import RobotPlatform
    return RobotPlatform.MOCK
