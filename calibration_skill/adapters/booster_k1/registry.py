"""Explicit K1 registration helpers for M27-D.

M27-D: Vendor registration now wraps a properly constructed
BoosterK1VendorRuntime inside a BoosterK1Adapter with appropriate
execution class. Fake registration remains unchanged.
"""
from __future__ import annotations

from collections.abc import Callable

from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.adapters.booster_k1.config import (
    BoosterK1AdapterConfig,
    BoosterK1HardwareGate,
    K1_FAKE_RUNTIME_MODE,
    K1_VENDOR_RUNTIME_MODE,
)
from calibration_skill.adapters.booster_k1.vendor_runtime import create_booster_k1_vendor_runtime
from calibration_skill.adapters.registry import AdapterFactoryRecord, AdapterRegistry
from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig

K1RuntimeFactory = Callable[[BoosterK1AdapterConfig], object]


def register_booster_k1_fake_adapter(
    registry: AdapterRegistry,
    runtime_factory: K1RuntimeFactory,
) -> None:
    """Register the K1 fake adapter in an explicit test registry only."""
    if not hasattr(registry, '_records'):
        raise ValueError("Registry does not have _records; use a public registration API")
    if RobotPlatform.BOOSTER_K1 in registry._records:
        raise ValueError("adapter factory already registered for platform booster_k1")

    def create(config: ConnectionConfig) -> BoosterK1Adapter:
        k1_config = _config_from_connection_fake(config)
        runtime = runtime_factory(k1_config)
        return BoosterK1Adapter(config=k1_config, runtime=runtime)  # type: ignore[arg-type]

    registry._records[RobotPlatform.BOOSTER_K1] = AdapterFactoryRecord(
        platform=RobotPlatform.BOOSTER_K1,
        creator=create,
        capabilities=booster_k1_capabilities(),
        dry_run_only=True,
    )


def register_booster_k1_vendor_adapter(
    registry: AdapterRegistry,
    *,
    hardware_gate: BoosterK1HardwareGate | None = None,
    enable_vendor_runtime: bool = False,
    execute_hardware: bool = False,
    interface: str = "lo",
) -> BoosterK1Adapter | None:
    """Register a vendor-backed K1 adapter.

    M27-D: When called with a valid hardware gate and all flags enabled,
    constructs the real vendor runtime and wraps it in a BoosterK1Adapter.
    The resulting record is NOT dry-run-only.

    When called without a hardware gate (M27-C backward compat),
    the function registers a fail-closed factory that raises on creation.
    """
    if RobotPlatform.BOOSTER_K1 in registry._records:
        raise ValueError("adapter factory already registered for platform booster_k1")

    # M27-C backward compat: without a gate, register fail-closed placeholder
    if hardware_gate is None:
        def create(config: ConnectionConfig):
            extra = dict(config.extra)
            gate = extra.get("hardware_gate")
            if gate is not None and not isinstance(gate, BoosterK1HardwareGate):
                raise ValueError("hardware_gate must be a BoosterK1HardwareGate")
            return create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=int(extra.get("now_ns", 0)),
                expected_robot_id=config.robot_id,
                expected_safety_policy_id=str(extra.get("safety_policy_id", "")),
                expected_safety_policy_hash=str(extra.get("safety_policy_hash", "")),
                enable_vendor_runtime=bool(extra.get("enable_vendor_runtime", False)),
                execute_hardware=bool(extra.get("execute_hardware", False)),
            )

        registry._records[RobotPlatform.BOOSTER_K1] = AdapterFactoryRecord(
            platform=RobotPlatform.BOOSTER_K1,
            creator=create,
            capabilities=booster_k1_capabilities(),
            dry_run_only=True,
        )
        return None

    # M27-D: full vendor mode with explicit gate
    # Build a vendor adapter config
    config = BoosterK1AdapterConfig(
        robot_id=hardware_gate.expected_robot_id,
        connection_profile_id="k1_vendor_live",
        runtime_mode=K1_VENDOR_RUNTIME_MODE,
        dry_run=False,
        allow_hardware=True,
        safety_policy_id=hardware_gate.safety_policy_id,
        safety_policy_hash=hardware_gate.safety_policy_hash,
        max_abs_vx_mps=0.0,
        max_abs_vy_mps=0.0,
        max_abs_wz_radps=0.0,
        command_timeout_s=5.0,
        telemetry_timeout_s=2.0,
        stop_timeout_s=5.0,
        operator_authorization_required=True,
        legacy_forward_only=True,
        metadata={"m27d_vendor_mode": True, "zero_motion_only": True},
    )

    runtime = create_booster_k1_vendor_runtime(
        hardware_gate=hardware_gate,
        now_ns=0,
        expected_robot_id=hardware_gate.expected_robot_id,
        expected_safety_policy_id=hardware_gate.safety_policy_id,
        expected_safety_policy_hash=hardware_gate.safety_policy_hash,
        enable_vendor_runtime=enable_vendor_runtime,
        execute_hardware=execute_hardware,
        interface=interface,
    )

    adapter = BoosterK1Adapter(config=config, runtime=runtime)

    def create_from_config(cfg: ConnectionConfig) -> BoosterK1Adapter:
        return adapter

    registry._records[RobotPlatform.BOOSTER_K1] = AdapterFactoryRecord(
        platform=RobotPlatform.BOOSTER_K1,
        creator=create_from_config,
        capabilities=booster_k1_capabilities(),
        dry_run_only=False,
    )

    return adapter


def _config_from_connection_fake(config: ConnectionConfig) -> BoosterK1AdapterConfig:
    if config.platform != RobotPlatform.BOOSTER_K1:
        raise ValueError("K1 fake adapter requires booster_k1 ConnectionConfig")
    extra = dict(config.extra)
    runtime_mode = str(extra.get("runtime_mode", K1_FAKE_RUNTIME_MODE))
    allow_hardware = bool(extra.get("allow_hardware", False))
    dry_run = bool(extra.get("dry_run", True))
    if runtime_mode != K1_FAKE_RUNTIME_MODE or runtime_mode == K1_VENDOR_RUNTIME_MODE or allow_hardware or not dry_run:
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
