"""Tests for domain capabilities module."""
from calibration_skill.domain.capabilities import (
    CapabilityDescriptor,
    CapabilityRecord,
    negotiate_capabilities,
)
from calibration_skill.domain.enums import (
    CAPABILITY_CONNECT,
    CAPABILITY_VELOCITY_X,
    CAPABILITY_YAW_RATE,
    CapabilitySupport,
    EvidenceLevel,
    ImplementationMaturity,
)


class TestCapabilityRecord:
    def test_valid_construction(self):
        record = CapabilityRecord(capability_id=CAPABILITY_VELOCITY_X)
        assert record.capability_id == CAPABILITY_VELOCITY_X
        assert record.support == CapabilitySupport.UNKNOWN

    def test_empty_id_rejected(self):
        import pytest
        with pytest.raises(ValueError):
            CapabilityRecord(capability_id="")


class TestCapabilityDescriptor:
    def test_get_capability_found(self):
        record = CapabilityRecord(
            capability_id=CAPABILITY_VELOCITY_X,
            support=CapabilitySupport.SUPPORTED,
            evidence=EvidenceLevel.HARDWARE_VERIFIED,
            maturity=ImplementationMaturity.HARDWARE_VERIFIED,
        )
        descriptor = CapabilityDescriptor(
            platform_id="booster_k1",
            capabilities=(record,),
        )
        found = descriptor.get_capability(CAPABILITY_VELOCITY_X)
        assert found is not None
        assert found.support == CapabilitySupport.SUPPORTED

    def test_get_capability_not_found(self):
        descriptor = CapabilityDescriptor(platform_id="test")
        assert descriptor.get_capability("nonexistent") is None

    def test_has_capability_only_true_for_supported(self):
        supported = CapabilityRecord(capability_id="c1", support=CapabilitySupport.SUPPORTED)
        unknown = CapabilityRecord(capability_id="c2", support=CapabilitySupport.UNKNOWN)
        descriptor = CapabilityDescriptor(
            platform_id="test",
            capabilities=(supported, unknown),
        )
        assert descriptor.has_capability("c1") is True
        assert descriptor.has_capability("c2") is False
        assert descriptor.has_capability("c3") is False


class TestNegotiateCapabilities:
    def test_all_satisfied(self):
        record = CapabilityRecord(
            capability_id=CAPABILITY_CONNECT,
            support=CapabilitySupport.SUPPORTED,
        )
        descriptor = CapabilityDescriptor(
            platform_id="test",
            capabilities=(record,),
        )
        result = negotiate_capabilities(descriptor, (CAPABILITY_CONNECT,))
        assert result.satisfied is True
        assert len(result.required_missing) == 0

    def test_missing_capability(self):
        descriptor = CapabilityDescriptor(platform_id="test")
        result = negotiate_capabilities(descriptor, (CAPABILITY_CONNECT,))
        assert result.satisfied is False
        assert CAPABILITY_CONNECT in result.required_missing

    def test_unsupported_capability(self):
        record = CapabilityRecord(
            capability_id=CAPABILITY_YAW_RATE,
            support=CapabilitySupport.UNSUPPORTED,
        )
        descriptor = CapabilityDescriptor(
            platform_id="test",
            capabilities=(record,),
        )
        result = negotiate_capabilities(descriptor, (CAPABILITY_YAW_RATE,))
        assert result.satisfied is False
        assert CAPABILITY_YAW_RATE in result.required_missing

    def test_unknown_capability(self):
        record = CapabilityRecord(
            capability_id=CAPABILITY_VELOCITY_X,
            support=CapabilitySupport.UNKNOWN,
        )
        descriptor = CapabilityDescriptor(
            platform_id="test",
            capabilities=(record,),
        )
        result = negotiate_capabilities(descriptor, (CAPABILITY_VELOCITY_X,))
        assert result.satisfied is False
        assert CAPABILITY_VELOCITY_X in result.required_unknown

    def test_requires_hardware_verification(self):
        record = CapabilityRecord(
            capability_id=CAPABILITY_CONNECT,
            support=CapabilitySupport.REQUIRES_HARDWARE_VERIFICATION,
        )
        descriptor = CapabilityDescriptor(
            platform_id="test",
            capabilities=(record,),
        )
        result = negotiate_capabilities(descriptor, (CAPABILITY_CONNECT,))
        assert result.satisfied is False
        assert CAPABILITY_CONNECT in result.requires_hardware_verification

    def test_no_mutation(self):
        record = CapabilityRecord(capability_id="c1", support=CapabilitySupport.SUPPORTED)
        descriptor = CapabilityDescriptor(platform_id="test", capabilities=(record,))
        original = descriptor.get_capability("c1")
        negotiate_capabilities(descriptor, ("c1",))
        after = descriptor.get_capability("c1")
        assert original is not None and after is not None
        assert original.support == after.support
