# Real K1 Velocity Profile Contract v0 / K1 实机速度 profile 契约 v0

## Purpose / 目的

`real_k1_velocity_profile_v0.json` 是 measurement output contract，不是 compensation module，也不是 navigation controller。它把 2026-06-09 lab hard floor 的真实 K1 前进速度测试结果整理成下游模块可读取的 profile，用于 warning、confidence 和后续建模边界判断。

该 profile 不输出 corrected command velocity，不发布运动命令，不实现自动补偿。

## Source Artifacts / 来源 Artifact

- M9 field-test record: `docs/real_k1_forward_velocity_field_test_v0.md`
- M9 structured data: `outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.yaml`
- M10 analysis summary: `outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json`
- M10 analysis report: `reports/real_k1_forward_velocity_analysis_v0.md`

## Scope / 适用范围

- Platform: `Booster Robotics K1`
- Environment: `lab_hard_floor`
- Condition: `dry`
- Motion axis: forward velocity only
- Command interface: SDK high-level `Move(vx, 0.0, 0.0)`

该 profile 只适用于环境匹配的 lab hard floor 初始测量上下文。其他地面、坡度、湿滑条件或机器人状态变化都需要新的测量 profile。

## Required Measurement Topics / 必要测量 Topics

- `/odometer_state`: `booster_interface/msg/Odometer`
  - Usage: within-trial displacement, relative heading
- `/low_state`: `booster_interface/msg/LowState`
  - Usage: rpy, gyro, acc, yaw cross-check
- `/robot_states`: `booster_interface/msg/RobotStatesMsg`
  - Usage: current_mode, current_body_control, current_actions
- `/fall_down`: `booster_interface/msg/FallDownState`
  - Usage: fall_down_state, is_recovery_available

Profile rules require using only within-trial delta-derived values. Do not compare absolute odometer coordinates across trials.

## Removed / Optional Fields / 移除与可选字段

- `battery_state`: optional/future only.
- `remote_controller_state`: permanently removed because navigation-focused measurement excludes manual-control input.

Downstream modules must not reintroduce `remote_controller_state` as a measurement dependency for this profile.

## Observed Velocity Regions / 已观测速度区域

- `0.1 m/s`: ineffective/deadzone; almost no measurable translation.
- `0.3 m/s`: first effective but weak response.
- `0.4 m/s`: effective but under-tracking.
- `0.45 m/s`: near stable tracking, but yaw drift needs repeat.
- `0.5 m/s`: current stable tracking reference for lab hard floor.

The observed low-speed response is nonlinear. The transition region is currently `0.3-0.45 m/s`; the effective threshold interval is bounded by the observations `0.1-0.3 m/s`.

## Downstream Usage / 下游使用方式

Use this profile for warning and confidence decisions:

- Warn on low target speeds below the observed effective threshold.
- Treat `0.3-0.45 m/s` as transition / low-confidence region.
- Use `0.5 m/s` as the current stable tracking reference only for lab hard floor.
- Use only environment-matching profiles.

Do not use this profile yet for automatic compensation. There are not enough repeated trials to estimate variance or build a reliable compensation model.

Do not use one global proportional gain. Future modeling should use a piecewise or nonlinear mapping.

## Limitations / 局限性

- Single session.
- Single floor type: lab hard floor.
- Mostly one trial per speed.
- Odometer-primary measurement.
- No external ground truth.
- `0.45 m/s` requires repeat because yaw drift was larger than neighboring trials.
- Absolute odometer coordinates should not be compared across trials.

## Next Step / 下一步

Repeat selected speeds later only if needed for compensation or confidence estimation. Do not continue speed testing merely for its own sake. The next useful repeats are `0.45 m/s` for yaw drift stability and `0.4/0.5 m/s` for variance estimation.
