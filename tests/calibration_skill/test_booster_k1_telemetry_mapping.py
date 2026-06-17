from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.runtime import BoosterK1RuntimeOdometry
from fakes.fake_booster_k1_runtime import FakeBoosterK1FailureConfig, FakeBoosterK1Runtime
from test_booster_k1_config import valid_config


def test_fake_odometry_normalizes_body_twist_pose_and_battery():
    runtime = FakeBoosterK1Runtime(odometry_sequence=[
        BoosterK1RuntimeOdometry(
            sequence_id=7,
            sample_monotonic_ns=1_200_000_000,
            x_m=2.0,
            y_m=3.0,
            z_m=0.4,
            yaw_rad=0.5,
            vx_mps=0.4,
            vy_mps=0.0,
            wz_radps=0.0,
        )
    ])
    sample = BoosterK1Adapter(config=valid_config(), runtime=runtime).collect_telemetry_sample()
    assert sample.sample_sequence_id == 7
    assert sample.pose.position.x == 2.0
    assert sample.body_twist.linear.x == 0.4
    assert sample.heading_rad == 0.5
    assert sample.battery_percentage == 88.0
    assert "no_hardware" in sample.quality_flags


def test_missing_odometry_is_explicit_quality_flag_not_fabricated_pose():
    runtime = FakeBoosterK1Runtime(failures=FakeBoosterK1FailureConfig(telemetry_unavailable=True))
    sample = BoosterK1Adapter(config=valid_config(), runtime=runtime).collect_telemetry_sample()
    assert sample.pose is None
    assert sample.body_twist is None
    assert "odometry_unavailable" in sample.quality_flags
