# K1 Measurement Report

## 数据声明

本报告由 `processed_environment_profile.json` 生成，属于测量阶段输出摘要。

**警告：该 profile 包含 dummy-data warning，因此本报告不是真实 K1 测量结果。**

Dummy report 不得用于速度补偿、导航或任何机器人安全决策。

## 实验元数据

- robot: Booster K1
- skill_version: measurement_v0
- experiment_name: k1_forward_velocity_tracking_baseline_v0
- profile_id: dummy_tile_dry_flat_measurement_v0_generated
- created_at: 2026-06-04T09:53:00.690996+00:00
- repository_role: measurement_predecessor
- full_project: K1 Velocity Measurement, Compensation and Navigation Safety Pipeline
- schema_version: 0.1.0

## 环境标签

- floor_type: tile
- condition: dry
- slope: flat
- notes: Dummy profile generated from dummy raw log only. Not real robot data.

## 有效速度范围

- min_vx_cmd_mps: 0.1
- max_vx_cmd_mps: 0.4

## 速度画像摘要

| v_x_cmd (m/s) | v_x_actual_mean (m/s) | v_x_actual_std (m/s) | speed_gain_mean | speed_gain_std | absolute_error_mean (m/s) | relative_error_mean | n_trials |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1 | 0.0798431 | 0.000655349 | 0.798431 | 0.00655349 | -0.0201569 | -0.201569 | 5 |
| 0.2 | 0.160284 | 0.000665024 | 0.801419 | 0.00332512 | -0.0397162 | -0.198581 | 5 |
| 0.3 | 0.238897 | 0.00184861 | 0.796325 | 0.00616203 | -0.0611026 | -0.203675 | 5 |
| 0.4 | 0.319933 | 0.00152479 | 0.799831 | 0.00381197 | -0.0800674 | -0.200169 | 5 |

## 质量与置信度

- confidence: low
- ground_truth_method: unknown
- odom_validated: false
- warnings:
  - Dummy data only; not collected from a real K1 robot.
  - Do not use this profile for compensation or navigation.

## 下游使用说明

- recommended_for_compensation: false
- extrapolation_allowed: false
- downstream notes: Dummy data only. This generated profile is for pipeline validation only.

本仓库不实现 velocity compensation。
下游模块必须检查 environment match、valid speed range、confidence、n_trials 和 extrapolation risk。
如果 `recommended_for_compensation` 为 false，下游补偿模块不得使用该 profile。

## 局限性

- odom 未经外部验证前不能视为 ground truth。
- dummy data 不能代表真实 K1 行为。
- 当前 shell 中 M4.5 未检测到 ROS2，因此没有真实 ROS2 topic 被验证。
- 当前流程没有执行真实机器人运动。
- 本仓库没有实现 compensation model。

## 下一步

- 在 ROS2 可用的 K1 shell 中重新运行 M4.5。
- 识别 odom / imu / robot_state topics。
- 使用静止机器人数据验证 logger。
- 使用人工控制行走数据验证 logger。
- 完成上述验证后，才考虑低速真实测量实验。
