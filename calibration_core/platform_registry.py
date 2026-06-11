"""Registry for cross-platform calibration backends."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PlatformEntry:
    platform_id: str
    robot_model: str
    command_adapter_class: type[Any]
    state_logger_class: type[Any]
    extractor_class: type[Any]
    supported_state_sources: tuple[str, ...]
    validation_status: str
    hardware_validated_reference: bool
    config_path: Path

    def summary(self) -> dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "robot_model": self.robot_model,
            "supported_state_sources": list(self.supported_state_sources),
            "validation_status": self.validation_status,
            "hardware_validated_reference": self.hardware_validated_reference,
            "config_path": str(self.config_path),
        }


def get_platform_registry() -> dict[str, PlatformEntry]:
    from platforms.booster_k1 import (
        BoosterK1CommandAdapter,
        BoosterK1OdometerExtractor,
        BoosterK1Ros2OdometerLogger,
    )
    from platforms.unitree_g1 import UnitreeG1CommandAdapter, UnitreeG1ScaffoldExtractor, UnitreeG1ScaffoldLogger
    from platforms.unitree_go1 import UnitreeGo1CommandAdapter, UnitreeGo1ScaffoldExtractor, UnitreeGo1ScaffoldLogger

    return {
        "booster_k1": PlatformEntry(
            platform_id="booster_k1",
            robot_model="Booster K1",
            command_adapter_class=BoosterK1CommandAdapter,
            state_logger_class=BoosterK1Ros2OdometerLogger,
            extractor_class=BoosterK1OdometerExtractor,
            supported_state_sources=("/odometer_state", "/low_state.imu_state.rpy"),
            validation_status="hardware_validated_reference",
            hardware_validated_reference=True,
            config_path=Path("platforms/booster_k1/config.yaml"),
        ),
        "unitree_g1": PlatformEntry(
            platform_id="unitree_g1",
            robot_model="Unitree G1",
            command_adapter_class=UnitreeG1CommandAdapter,
            state_logger_class=UnitreeG1ScaffoldLogger,
            extractor_class=UnitreeG1ScaffoldExtractor,
            supported_state_sources=(),
            validation_status="scaffold_only",
            hardware_validated_reference=False,
            config_path=Path("platforms/unitree_g1/config.yaml"),
        ),
        "unitree_go1": PlatformEntry(
            platform_id="unitree_go1",
            robot_model="Unitree GO1",
            command_adapter_class=UnitreeGo1CommandAdapter,
            state_logger_class=UnitreeGo1ScaffoldLogger,
            extractor_class=UnitreeGo1ScaffoldExtractor,
            supported_state_sources=(),
            validation_status="scaffold_only",
            hardware_validated_reference=False,
            config_path=Path("platforms/unitree_go1/config.yaml"),
        ),
    }


def list_platforms() -> list[PlatformEntry]:
    return [get_platform_registry()[key] for key in sorted(get_platform_registry())]


def get_platform(platform_id: str) -> PlatformEntry:
    registry = get_platform_registry()
    try:
        return registry[platform_id]
    except KeyError as exc:
        available = ", ".join(sorted(registry))
        raise KeyError(f"unknown platform_id {platform_id!r}; available: {available}") from exc
