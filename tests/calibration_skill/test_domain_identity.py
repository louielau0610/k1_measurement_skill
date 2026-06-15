"""Tests for domain identity module."""
import pytest
from calibration_skill.domain.enums import RobotMorphology, RobotPlatform
from calibration_skill.domain.identity import RobotIdentity


class TestRobotIdentity:
    def test_valid_construction(self):
        identity = RobotIdentity(
            platform=RobotPlatform.BOOSTER_K1,
            morphology=RobotMorphology.BIPED_HUMANOID,
            robot_id="k1-unit-01",
            adapter_name="booster_k1_adapter",
            adapter_version="1.0.0",
        )
        assert identity.platform == RobotPlatform.BOOSTER_K1
        assert identity.robot_id == "k1-unit-01"

    def test_empty_robot_id_rejected(self):
        with pytest.raises(ValueError):
            RobotIdentity(
                platform=RobotPlatform.MOCK,
                morphology=RobotMorphology.SYNTHETIC,
                robot_id="",
                adapter_name="mock",
                adapter_version="1.0.0",
            )

    def test_whitespace_robot_id_rejected(self):
        with pytest.raises(ValueError):
            RobotIdentity(
                platform=RobotPlatform.MOCK,
                morphology=RobotMorphology.SYNTHETIC,
                robot_id="   ",
                adapter_name="mock",
                adapter_version="1.0.0",
            )

    def test_empty_adapter_name_rejected(self):
        with pytest.raises(ValueError):
            RobotIdentity(
                platform=RobotPlatform.MOCK,
                morphology=RobotMorphology.SYNTHETIC,
                robot_id="test",
                adapter_name="",
                adapter_version="1.0.0",
            )

    def test_optional_fields_default_none(self):
        identity = RobotIdentity(
            platform=RobotPlatform.MOCK,
            morphology=RobotMorphology.SYNTHETIC,
            robot_id="test",
            adapter_name="mock",
            adapter_version="1.0.0",
        )
        assert identity.hardware_serial is None
        assert identity.firmware_version is None

    def test_validate_returns_empty_for_valid(self):
        identity = RobotIdentity(
            platform=RobotPlatform.MOCK,
            morphology=RobotMorphology.SYNTHETIC,
            robot_id="test",
            adapter_name="mock",
            adapter_version="1.0.0",
        )
        assert identity.validate() == []

    def test_frozen_immutable(self):
        identity = RobotIdentity(
            platform=RobotPlatform.MOCK,
            morphology=RobotMorphology.SYNTHETIC,
            robot_id="test",
            adapter_name="mock",
            adapter_version="1.0.0",
        )
        with pytest.raises(Exception):
            identity.robot_id = "changed"  # type: ignore

    def test_to_dict_includes_all_fields(self):
        identity = RobotIdentity(
            platform=RobotPlatform.BOOSTER_K1,
            morphology=RobotMorphology.BIPED_HUMANOID,
            robot_id="k1-01",
            adapter_name="k1_adapter",
            adapter_version="2.0.0",
            hardware_serial="SN123",
        )
        d = identity.to_dict()
        assert d["platform"] == "booster_k1"
        assert d["hardware_serial"] == "SN123"
