# Real K1 Forward Velocity Field Test v0 / K1 实机前进速度测试记录 v0

## 1. Experiment Metadata / 实验元数据

- Date: `2026-06-09`
- Platform: `Booster Robotics K1`
- Environment: `lab_hard_floor`
- Condition: `dry`
- Test mode: `real machine, SDK high-level locomotion command`
- Operator observation: manually observed during test
- Repository context: 本仓库是 K1 velocity measurement / compensation / navigation safety pipeline 的 measurement-only module。

本记录用于归档今天第一次真实 K1 机器上的 SDK-based locomotion smoke test 和 forward velocity transition tests。它不是 compensation 或 navigation 控制实现，也不代表已经完成可用于导航的速度模型。

## 2. Scope and Exclusions / 范围与排除项

- `battery_state` 暂时从 measurement v0 required inputs 中移除，当前只作为 optional/future field。
- `remote_controller_state` 永久移出 measurement scope，因为当前研究关注 navigation behavior，而不是人工遥控输入。
- 本任务没有实现 velocity compensation。
- 本任务没有实现 navigation control。
- 本任务没有新增任何 robot motion command logic。

## 3. Validated Read-Only ROS2 Topics / 已验证只读 ROS2 Topics

| Topic | Type | Fields | Usage |
| --- | --- | --- | --- |
| `/odometer_state` | `booster_interface/msg/Odometer` | `x`, `y`, `theta` | displacement and relative heading within each trial |
| `/low_state` | `booster_interface/msg/LowState` | `imu_state.rpy`, `imu_state.gyro`, `imu_state.acc` | IMU posture / yaw cross-check |
| `/robot_states` | `booster_interface/msg/RobotStatesMsg` | `current_mode`, `current_body_control`, `current_actions` | robot mode and body-control state |
| `/fall_down` | `booster_interface/msg/FallDownState` | `fall_down_state`, `is_recovery_available` | safety state |

这些 topic 当前作为 measurement v0 的真实机器只读观测输入。它们不包含运动命令发布逻辑。

## 4. SDK Command Interface / SDK 命令接口

- SDK package import was available: `booster_robotics_sdk_python`
- Relevant classes:
  - `ChannelFactory`
  - `B1LocoClient`
  - `RobotMode`
- Command path:
  - `ChannelFactory.Instance().Init(0, "lo")`
  - `B1LocoClient().Init()`
  - `ChangeMode(RobotMode.kWalking)`
  - `Move(vx, 0.0, 0.0)`
  - repeated `Move(0.0, 0.0, 0.0)` for stop

Raw RPC topics such as `/LocoApiTopicReq` were not used for control.

## 5. Stationary Validation Summary / 静态验证摘要

- `/odometer_state` and `/low_state` published at high rate around several hundred Hz.
- `/robot_states` published around 2 Hz.
- `/fall_down` published around 1 Hz.
- Static odometer samples were stable before movement.
- `fall_down_state = 0` before movement tests.

## 6. Trial Results / 试验结果

| Trial | `vx_cmd` (m/s) | `duration_s` | `distance_m` | `v_actual_est_mps` | `speed_gain_est` | `dtheta_rad` | `fall_down_state_post` | Human observation | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A | 0.1 | 2.0 | | | | | | almost no measurable movement; robot entered walking posture | deadzone / ineffective low-speed command; no valid speed_gain should be treated as final |
| B | 0.3 | 2.0 | 0.288544 | 0.144272 | 0.480907 | 0.033154 | 0 | weak movement, approximately 0.1 m | first clearly effective movement, but still weak response / under-tracking |
| C | 0.4 | 2.0 | 0.548009 | 0.274004 | 0.685011 | 0.006043 | 0 | | effective movement but still under-tracking |
| D | 0.5 | 2.0 | 1.003940 | 0.501970 | 1.003940 | 0.005665 | 0 | | stable tracking; actual speed approximately equals command speed |
| E | 0.45 | 2.0 | 0.839345 | 0.419672 | 0.932605 | -0.094939 | 0 | | near stable tracking, but yaw drift is larger than neighboring trials and should be repeated |

## 7. Preliminary Findings / 初步发现

- The K1 forward velocity response is nonlinear in the low-speed region.
- `vx_cmd = 0.1` is ineffective in this test.
- `vx_cmd = 0.3` is the first clearly effective movement command observed, but response is weak.
- `vx_cmd = 0.4` is effective but still under-tracks.
- `vx_cmd = 0.45` is close to stable tracking but requires repetition due to larger yaw drift.
- `vx_cmd = 0.5` shows stable tracking with speed gain near 1.
- Preliminary first effective speed is around `0.3 m/s`.
- Preliminary stable tracking region begins around `0.45-0.5 m/s`.

## 8. Modeling Implication / 建模含义

- A single global proportional gain is not appropriate.
- Future modeling should use a piecewise or nonlinear mapping.
- Low-speed commands below the observed effective threshold should be treated as low-confidence or avoided in navigation.
- Compensation should not simply scale all commands by one constant.

## 9. Limitations / 局限性

- Single environment only: lab hard floor.
- Single session only.
- Each speed mostly single trial, so repeatability is not established.
- Odometer was used as primary distance source.
- No external motion-capture / UWB / tape-measure ground truth was used in this record.
- `0.45` should be repeated because yaw drift was larger than neighboring trials.
- Absolute odometer coordinates should not be compared across trials; only within-trial delta should be used.

## 10. Next Steps / 下一步

- Repeat `vx_cmd = 0.45` to check yaw drift stability.
- Repeat `vx_cmd = 0.4` and `0.5` for variance estimation.
- Add structured real log capture instead of ad-hoc `ros2 topic echo --once`.
- Build first velocity profile from repeated trials.
- Later test additional floor types after lab hard floor is stable.
