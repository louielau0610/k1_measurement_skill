# Raw Log Schema

本文档以中文优先描述原始测量日志字段。建议初始格式为 CSV，每一行对应一个采样时刻。

## 字段

- `timestamp`
- `trial_id`
- `vx_cmd`
- `vy_cmd`
- `wz_cmd`
- `odom_x`
- `odom_y`
- `odom_yaw`
- `odom_vx`
- `odom_vy`
- `odom_wz`
- `imu_acc_x`
- `imu_acc_y`
- `imu_acc_z`
- `imu_gyro_x`
- `imu_gyro_y`
- `imu_gyro_z`
- `battery_level`
- `robot_mode`
- `floor_type`
- `condition`
- `slope`

## 说明

`odom` 字段在未经外部校验前不能直接视为 ground truth。所有环境字段应来自人工标注或明确的实验记录。
