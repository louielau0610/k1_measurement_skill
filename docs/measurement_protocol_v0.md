# Measurement Protocol v0

本文档以中文优先描述 K1 前进速度测量 v0 实验协议。

## 范围

v0 只测试前进速度，不测试转向、不测试横向移动、不实现补偿、不实现自主导航。

## 重复实验

每个 `v_x_cmd` 应在相同环境下重复多次，记录每次 trial 的时间戳、命令速度、估计实际速度和环境标签。

## 环境标签

每次实验必须记录人工环境标签：

- `floor_type`
- `condition`
- `slope`

## Ground Truth

推荐使用外部 ground truth，例如 motion capture、视觉定位、标定过的里程计对照或其他独立测量系统。

`odom` 在未经验证前不能被直接视为 ground truth。它可以作为机器人内部估计来源，但必须与外部测量或独立校验结果对比后再用于结论。

## M2 核心指标

测量分析阶段使用 `k1_measurement.metrics` 中的纯 Python 指标函数。它们只计算测量结果，不执行速度补偿、不发布 ROS2 命令。

- `v_x_actual = (x_end - x_start) / (t_end - t_start)`
- `speed_gain = v_x_actual / v_x_cmd`
- `e_abs = v_x_actual - v_x_cmd`
- `e_rel = (v_x_actual - v_x_cmd) / v_x_cmd`
- `lateral_drift_rate = |y_end - y_start| / (t_end - t_start)`
- `yaw_drift_rate = |yaw_end - yaw_start| / (t_end - t_start)`
- `RMSE = sqrt(mean((v_actual_i - v_cmd)^2))`

## M3 Dummy Data Pipeline

在真实 K1 ROS2 topic 接入之前，可以使用 dummy 数据流水线验证格式和处理流程：

```bash
py scripts/generate_dummy_raw_log.py
py scripts/process_trial_logs.py
py scripts/validate_profile_schema.py data/processed/dummy_processed_environment_profile.json
```

生成的数据只用于开发验证，不是真实机器人数据，不能用于补偿、导航或安全决策。
