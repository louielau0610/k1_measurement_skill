# M20 Cross-Platform Calibration Core

M20 introduces a reusable calibration skill core for multiple robot platforms while preserving the evidence boundary from M19C.

## Scope

The core provides shared interfaces and utilities for:

- command adapters
- state loggers
- measurement extractors
- trial scheduling
- measurement schemas
- response summaries
- risk-region classification
- calibration profile export and loading
- platform registration

This milestone does not add Unitree G1 or Unitree GO1 empirical data, response curves, compensation, navigation behavior, or cross-platform validation claims.

## Platforms

| Platform | Status | Evidence boundary |
| --- | --- | --- |
| `booster_k1` | `hardware_validated_reference` | Wraps the completed M19C ROS2 `/odometer_state` K1 measurement path and `k1_gold_profile_v1`. |
| `unitree_g1` | `scaffold_only` | Defines adapter/logger/extractor locations only; all hardware and extraction methods raise `NotImplementedError`. |
| `unitree_go1` | `scaffold_only` | Defines adapter/logger/extractor locations only; all hardware and extraction methods raise `NotImplementedError`. |

Booster K1 remains the only validated hardware reference. Unitree platform support is intentionally limited to planning scaffolds until real logs and source validation are added.

## Booster K1 Reference

The K1 platform wrapper points to the M19C validated path:

- ROS2 setup: `source /opt/booster/BoosterRos2Interface/install/setup.bash`
- primary state source: `/odometer_state`
- secondary yaw source: `/low_state.imu_state.rpy`
- command path: `kPrepare -> kWalking -> Move(vx, 0, 0)`
- profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`

The K1 adapter does not execute motion by default. Live movement remains in the existing robot-side M19C runner.

## CLI Tools

```bash
py scripts/list_calibration_platforms.py
py scripts/show_calibration_profile.py --platform booster_k1
py scripts/generate_cross_platform_trial_plan.py --platform booster_k1 --repeats 3 --output outputs/real_k1_validation_m19/m20_booster_k1_trial_plan.csv
py scripts/validate_calibration_profile.py --profile outputs/real_k1_validation_m19/k1_gold_profile_v1.json
```

Trial plans are deterministic and plan-only. Generating a trial plan does not imply that a non-K1 platform has measurement support.

## Claim Boundary

M20 makes the M19C K1 profile reusable by a calibration skill layer. It does not:

- fabricate Unitree measurements
- infer measurements from command speed
- claim cross-platform generalization
- compute new empirical response statistics
- validate compensation or navigation

Future platforms must first provide real state logs, measurement extraction evidence, and QC before they can be marked as hardware validated.
