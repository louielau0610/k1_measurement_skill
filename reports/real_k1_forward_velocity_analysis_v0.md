# Real K1 Forward Velocity Analysis v0 / K1 实机前进速度分析 v0

## 实验输入

- date: `2026-06-09`
- platform: `Booster Robotics K1`
- floor_type: `lab_hard_floor`
- condition: `dry`
- SDK client: `B1LocoClient`

## 数据来源

- Input YAML: `outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.yaml`
- This is an offline measurement analysis artifact.
- `battery_state` is `optional_future_only`.
- `remote_controller_state` is `permanently_removed` from measurement scope.

## 速度响应表

| trial_id | vx_cmd | v_actual_est | speed_gain | distance_error | rel_error | abs_dtheta | category |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| vx_0_1_smoke | 0.1 |  |  |  |  |  | ineffective_or_deadzone |
| vx_0_3_transition | 0.3 | 0.144272 | 0.480907 | -0.311456 | -0.519093 | 0.033154 | weak_response |
| vx_0_4_effective | 0.4 | 0.274004 | 0.685011 | -0.251991 | -0.314989 | 0.006043 | under_tracking |
| vx_0_5_stable | 0.5 | 0.50197 | 1.00394 | 0.00394 | 0.00394 | 0.005665 | stable_tracking |
| vx_0_45_transition_upper | 0.45 | 0.419672 | 0.932605 | -0.060655 | -0.0673944 | 0.094939 | stable_tracking |

## 低速死区判断

- `0.1 m/s` was ineffective.
- `0.3 m/s` was first clearly effective but weak.
- Preliminary first effective speed is around `0.3 m/s`.

## tracking gain 分析

- `0.4 m/s` was effective but under-tracking.
- `0.45 m/s` was near stable tracking but had larger yaw drift and should be repeated.
- `0.5 m/s` showed stable tracking with speed gain near 1.
- Best tracking trial by gain error: `vx_0_5_stable` with speed_gain `1.00394`.

## yaw drift 分析

- Highest yaw drift trial: `vx_0_45_transition_upper` with abs_dtheta `0.094939` rad.
- The `0.45 m/s` trial should be repeated because yaw drift was larger than neighboring trials.

## 建模启示

- A single global proportional gain is not appropriate.
- A piecewise or nonlinear mapping is recommended.
- Low-speed commands below the observed effective threshold should be treated as low-confidence or avoided in navigation.
- Compensation should not simply scale all commands by one constant.

## 当前限制

- single_environment_lab_hard_floor
- single_session
- mostly_single_trial_per_speed
- odometer_primary_no_external_ground_truth
- absolute_odom_coordinates_should_not_be_compared_across_trials
- vx_0_45_yaw_drift_requires_repeat

## 下一步建议

- Repeat `vx_cmd = 0.45` to check yaw drift stability.
- Repeat `vx_cmd = 0.4` and `0.5` for variance estimation.
- Add structured real log capture instead of ad-hoc `ros2 topic echo --once`.
- Build first velocity profile from repeated trials.
- Later test additional floor types after lab hard floor is stable.
