from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.domain.enums import (
    ALL_KNOWN_CAPABILITIES,
    CAPABILITY_DRY_RUN,
    CAPABILITY_VELOCITY_Y,
    CAPABILITY_YAW_RATE,
    CapabilitySupport,
    EvidenceLevel,
    RobotPlatform,
)


def test_all_required_capability_keys_present():
    descriptor = booster_k1_capabilities()
    assert descriptor.platform_id == RobotPlatform.BOOSTER_K1.value
    actual = {record.capability_id for record in descriptor.capabilities}
    assert set(ALL_KNOWN_CAPABILITIES) <= actual


def test_no_capability_claims_hardware_verified():
    descriptor = booster_k1_capabilities()
    assert all(record.evidence != EvidenceLevel.HARDWARE_VERIFIED for record in descriptor.capabilities)
    assert all(record.maturity.value != "hardware_verified" for record in descriptor.capabilities)


def test_lateral_and_yaw_are_conservative():
    descriptor = booster_k1_capabilities()
    assert descriptor.get_capability(CAPABILITY_VELOCITY_Y).support == CapabilitySupport.UNSUPPORTED
    assert descriptor.get_capability(CAPABILITY_YAW_RATE).support == CapabilitySupport.UNSUPPORTED


def test_dry_run_supported_by_fake_runtime():
    descriptor = booster_k1_capabilities()
    assert descriptor.get_capability(CAPABILITY_DRY_RUN).support == CapabilitySupport.SUPPORTED
