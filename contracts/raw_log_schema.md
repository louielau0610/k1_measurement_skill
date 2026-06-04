# Raw Log Schema

本文档定义 K1 前进速度测量阶段的原始日志字段。原始日志用于记录每次实验采样数据，并作为生成 `processed_environment_profile.json` 的输入。

原始日志不是下游速度补偿接口。下游补偿、安全命令适配和导航安全模块应优先消费经过处理和验证的 `processed_environment_profile.json`。

`odom` 字段在未经外部校验前不能直接视为 ground truth。建议使用外部 ground truth，例如视频尺量、UWB、motion capture 或其他独立 tracking 系统，对 odom 结果进行验证。

## 字段表

| 字段名 | 类型 | 单位 | 是否必需 | 说明 |
| --- | --- | --- | --- | --- |
| `timestamp` | string | ISO 8601 或 Unix time | 是 | 采样时间戳 |
| `trial_id` | string | 无 | 是 | 实验 trial 标识 |
| `vx_cmd` | number | m/s | 是 | 前进速度命令 |
| `vy_cmd` | number | m/s | 是 | 横向速度命令，v0 应为 0 |
| `wz_cmd` | number | rad/s | 是 | 角速度命令，v0 应为 0 |
| `command_phase` | string | 无 | 是 | baseline、command、stop 等阶段 |
| `odom_x` | number | m | 是 | odom 估计 x 位置 |
| `odom_y` | number | m | 是 | odom 估计 y 位置 |
| `odom_yaw` | number | rad | 是 | odom 估计 yaw |
| `odom_vx` | number | m/s | 是 | odom 估计前进速度 |
| `odom_vy` | number | m/s | 是 | odom 估计横向速度 |
| `odom_wz` | number | rad/s | 是 | odom 估计角速度 |
| `imu_acc_x` | number | m/s^2 | 否 | IMU x 加速度 |
| `imu_acc_y` | number | m/s^2 | 否 | IMU y 加速度 |
| `imu_acc_z` | number | m/s^2 | 否 | IMU z 加速度 |
| `imu_gyro_x` | number | rad/s | 否 | IMU x 角速度 |
| `imu_gyro_y` | number | rad/s | 否 | IMU y 角速度 |
| `imu_gyro_z` | number | rad/s | 否 | IMU z 角速度 |
| `battery_level` | number | percent 或 0-1 | 否 | 电池电量，单位需在日志元数据中说明 |
| `robot_mode` | string | 无 | 否 | 机器人状态或运动模式 |
| `floor_type` | string | 无 | 是 | 地面类型：tile、concrete、wood、carpet、rubber、unknown |
| `condition` | string | 无 | 是 | 环境状态：dry、wet、dusty、uneven、unknown |
| `slope` | string | 无 | 是 | 坡度：flat、mild_uphill、mild_downhill、unknown |
| `operator_note` | string | 无 | 否 | 操作者备注 |

## 使用规则

- raw log 只记录测量过程，不是速度补偿接口。
- raw log 会被处理成 `processed_environment_profile.json`。
- 未验证的 odom 不能作为最终 ground truth。
- 推荐使用外部 ground truth 验证实际速度。
