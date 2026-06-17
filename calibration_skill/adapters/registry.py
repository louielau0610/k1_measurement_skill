"""Explicit adapter registry for M26-C dry-run composition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from calibration_skill.domain.capabilities import CapabilityDescriptor, negotiate_capabilities
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_CAPABILITY_UNAVAILABLE,
    ERROR_UNSUPPORTED_PLATFORM,
)
from calibration_skill.ports.factory import ConnectionConfig
from calibration_skill.ports.robot import RobotAdapter

AdapterCreator = Callable[[ConnectionConfig], RobotAdapter]


@dataclass(frozen=True)
class AdapterFactoryRecord:
    """A registered adapter factory and its static capability descriptor."""
    platform: RobotPlatform
    creator: AdapterCreator
    capabilities: CapabilityDescriptor
    dry_run_only: bool = True


@dataclass
class AdapterRegistry:
    """Explicit, in-memory adapter registry.

    M26-C does not scan files, entry points, or hardware adapters.
    """
    _records: dict[RobotPlatform, AdapterFactoryRecord] = field(default_factory=dict)

    def register(
        self,
        platform: RobotPlatform,
        creator: AdapterCreator,
        capabilities: CapabilityDescriptor,
        *,
        dry_run_only: bool = True,
    ) -> None:
        if platform in self._records:
            raise ValueError(f"adapter factory already registered for platform {platform.value}")
        if platform != RobotPlatform.MOCK:
            raise ValueError("M26-C registry only accepts mock adapter factories")
        self._records[platform] = AdapterFactoryRecord(
            platform=platform,
            creator=creator,
            capabilities=capabilities,
            dry_run_only=dry_run_only,
        )

    def list_registered_platforms(self) -> tuple[RobotPlatform, ...]:
        return tuple(sorted(self._records.keys(), key=lambda p: p.value))

    def resolve(self, platform: RobotPlatform) -> AdapterFactoryRecord:
        record = self._records.get(platform)
        if record is None:
            raise LookupError(f"unsupported platform for M26-C: {platform.value}")
        return record

    def create_adapter(
        self,
        platform: RobotPlatform,
        config: ConnectionConfig,
        *,
        dry_run: bool,
        required_capabilities: tuple[str, ...] = (),
    ) -> RobotAdapter:
        errors = self.validate_request(platform, config, dry_run=dry_run, required_capabilities=required_capabilities)
        if errors:
            raise ValueError(errors[0].message)
        return self.resolve(platform).creator(config)

    def validate_request(
        self,
        platform: RobotPlatform,
        config: ConnectionConfig | None,
        *,
        dry_run: bool,
        required_capabilities: tuple[str, ...] = (),
    ) -> list[DomainError]:
        if platform != RobotPlatform.MOCK and platform not in self._records:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message=f"M26-C supports only mock dry-run platform, got {platform.value}",
                retryable=False,
                details={"platform": platform.value},
            )]
        if config is None:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message="explicit ConnectionConfig is required",
                retryable=False,
            )]
        if config.platform != platform:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message="ConnectionConfig platform does not match requested platform",
                retryable=False,
                details={"requested": platform.value, "config": config.platform.value},
            )]
        if not dry_run:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message="adapter creation requires explicit dry_run=true",
                retryable=False,
            )]
        try:
            record = self.resolve(platform)
        except LookupError:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message=f"no adapter factory registered for platform {platform.value}",
                retryable=False,
                details={"platform": platform.value},
            )]
        if record.dry_run_only and not dry_run:
            return [DomainError(
                code=ERROR_UNSUPPORTED_PLATFORM,
                message="dry-run-only adapter requires dry_run=true",
                retryable=False,
            )]
        negotiation = negotiate_capabilities(record.capabilities, required_capabilities)
        if not negotiation.satisfied:
            return negotiation.errors()
        if not required_capabilities and record.capabilities.platform_id != platform.value:
            return [DomainError(
                code=ERROR_CAPABILITY_UNAVAILABLE,
                message="registered capability descriptor does not match platform",
                retryable=False,
            )]
        return []
