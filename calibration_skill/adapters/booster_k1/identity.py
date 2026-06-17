"""K1 identity mapping for the fake-runtime adapter skeleton."""
from __future__ import annotations

from collections.abc import Mapping

from calibration_skill.adapters.booster_k1.config import BoosterK1AdapterConfig
from calibration_skill.domain.enums import RobotMorphology, RobotPlatform
from calibration_skill.domain.identity import RobotIdentity

BOOSTER_K1_ADAPTER_NAME = "BoosterK1Adapter"
BOOSTER_K1_ADAPTER_VERSION = "m27b.fake-runtime.1"


def booster_k1_identity(
    config: BoosterK1AdapterConfig,
    runtime_metadata: Mapping[str, object] | None = None,
) -> RobotIdentity:
    """Return explicit K1 identity without import-time or hardware queries."""
    metadata = dict(runtime_metadata or {})
    identity_metadata = {
        "runtime_mode": config.runtime_mode,
        "dry_run": str(config.dry_run),
        "hardware_verified": "false",
        "m27b_fake_runtime_only": "true",
    }
    return RobotIdentity(
        platform=RobotPlatform.BOOSTER_K1,
        morphology=RobotMorphology.BIPED_HUMANOID,
        robot_id=config.robot_id,
        adapter_name=BOOSTER_K1_ADAPTER_NAME,
        adapter_version=BOOSTER_K1_ADAPTER_VERSION,
        hardware_serial=_optional_str(metadata.get("hardware_serial")),
        firmware_version=_optional_str(metadata.get("firmware_version")),
        sdk_family=_optional_str(metadata.get("sdk_family")),
        sdk_version=_optional_str(metadata.get("sdk_version")),
        metadata=tuple(sorted(identity_metadata.items())),
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
