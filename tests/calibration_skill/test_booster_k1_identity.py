from calibration_skill.adapters.booster_k1.identity import booster_k1_identity
from calibration_skill.domain.enums import RobotMorphology, RobotPlatform

from test_booster_k1_config import valid_config


def test_identity_uses_explicit_config_and_runtime_metadata():
    identity = booster_k1_identity(
        valid_config(robot_id="explicit-k1"),
        {
            "hardware_serial": "serial",
            "firmware_version": "firmware",
            "sdk_family": "fake_booster",
            "sdk_version": "fake",
        },
    )
    assert identity.robot_id == "explicit-k1"
    assert identity.platform == RobotPlatform.BOOSTER_K1
    assert identity.morphology == RobotMorphology.BIPED_HUMANOID
    assert identity.adapter_name == "BoosterK1Adapter"
    assert identity.hardware_serial == "serial"


def test_identity_mapping_does_not_query_runtime_on_import(monkeypatch):
    import socket

    def fail(*args, **kwargs):
        raise AssertionError("hardware query not allowed")

    monkeypatch.setattr(socket, "socket", fail)
    import calibration_skill.adapters.booster_k1.identity as identity_module

    assert identity_module.BOOSTER_K1_ADAPTER_NAME == "BoosterK1Adapter"
