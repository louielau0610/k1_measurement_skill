"""Explicit K1 fake-runtime registration helper."""
from __future__ import annotations

from collections.abc import Callable

from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.adapters.booster_k1.config import BoosterK1AdapterConfig, K1_FAKE_RUNTIME_MODE
from calibration_skill.adapters.registry import AdapterFactoryRecord, AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig

K1RuntimeFactory = Callable[[BoosterK1AdapterConfig], object]


def register_booster_k1_fake_adapter(
    registry: AdapterRegistry,
    runtime_factory: K1RuntimeFactory,
) -> None:
    """Register the K1 fake adapter in an explicit test registry only."""
    if RobotPlatform.BOOSTER_K1 in registry._records:
        raise ValueError("adapter factory already registered for platform booster_k1")

    def create(config: ConnectionConfig) -> BoosterK1Adapter:
        k1_config = _config_from_connection(config)
        runtime = runtime_factory(k1_config)
        return BoosterK1Adapter(config=k1_config, runtime=runtime)  # type: ignore[arg-type]

    registry._records[RobotPlatform.BOOSTER_K1] = AdapterFactoryRecord(
        platform=RobotPlatform.BOOSTER_K1,
        creator=create,
        capabilities=booster_k1_capabilities(),
        dry_run_only=True,
    )


def _config_from_connection(config: ConnectionConfig) -> BoosterK1AdapterConfig:
    if config.platform != RobotPlatform.BOOSTER_K1:
        raise ValueError("K1 fake adapter requires booster_k1 ConnectionConfig")
    extra = dict(config.extra)
    runtime_mode = str(extra.get("runtime_mode", K1_FAKE_RUNTIME_MODE))
    allow_hardware = bool(extra.get("allow_hardware", False))
    dry_run = bool(extra.get("dry_run", True))
    if runtime_mode != K1_FAKE_RUNTIME_MODE or allow_hardware or not dry_run:
        raise ValueError("M27-B K1 registration accepts only dry-run fake runtime configs")
    return BoosterK1AdapterConfig(
        robot_id=config.robot_id,
        connection_profile_id=str(extra["connection_profile_id"]),
        runtime_mode=runtime_mode,
        dry_run=dry_run,
        allow_hardware=allow_hardware,
        safety_policy_id=str(extra["safety_policy_id"]),
        safety_policy_hash=str(extra["safety_policy_hash"]),
        max_abs_vx_mps=float(extra["max_abs_vx_mps"]),
        max_abs_vy_mps=float(extra["max_abs_vy_mps"]),
        max_abs_wz_radps=float(extra["max_abs_wz_radps"]),
        command_timeout_s=float(extra["command_timeout_s"]),
        telemetry_timeout_s=float(extra["telemetry_timeout_s"]),
        stop_timeout_s=float(extra["stop_timeout_s"]),
        operator_authorization_required=bool(extra.get("operator_authorization_required", True)),
        metadata=dict(extra.get("metadata", {})),
        legacy_forward_only=bool(extra.get("legacy_forward_only", True)),
    )
