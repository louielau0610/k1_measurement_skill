"""Port interface for adapter factories."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.robot import RobotAdapter


@dataclass(frozen=True)
class ConnectionConfig:
    """Configuration for connecting to a robot.

    No silent platform selection. No default network interface.
    """
    platform: RobotPlatform
    robot_id: str
    network_interface: str | None = None
    dds_domain_id: int | None = None
    udp_port: int | None = None
    timeout_s: float = 10.0
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.robot_id or not self.robot_id.strip():
            raise ValueError("robot_id must be non-empty")
        if self.timeout_s <= 0:
            raise ValueError(f"timeout_s must be positive, got {self.timeout_s}")


class AdapterFactory(Protocol):
    """Creates platform adapters from configuration.

    Must not silently select a platform or default network interface.
    """

    def supports_platform(self, platform: RobotPlatform) -> bool:
        """Check if a platform is supported without importing its SDK."""
        ...

    def create_adapter(self, config: ConnectionConfig) -> RobotAdapter:
        """Create and return a configured adapter.

        May import vendor SDK here.
        Must not connect automatically.
        """
        ...

    def list_supported_platforms(self) -> list[RobotPlatform]:
        """List all platforms with available adapters.

        Must not require vendor SDKs to be installed.
        """
        ...
