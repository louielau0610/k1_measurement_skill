# K1 速度测量 Skill

## 项目定位

本仓库 `k1_measurement_skill` 是完整项目 **K1 Velocity Measurement, Compensation and Navigation Safety Pipeline** 的第一阶段前置测量模块。

完整项目要解决的问题是：Booster Robotics K1 的速度命令 `v_cmd` 与实际执行速度 `v_actual` 可能不一致。在导航任务中，这种误差会累积成位置误差、轨迹漂移和碰撞风险。

本仓库只负责：

```text
v_x_cmd -> v_x_actual measurement
```

本仓库不实现速度补偿、自主导航、实时闭环控制、真实机器人运动命令，也不硬编码未经验证的 K1 ROS2 topic 名称。

## 大项目整体设计

```text
速度命令（Velocity Command）
    ->
速度测量模块（Measurement Skill）
    ->
环境相关速度画像（Environment-specific Velocity Profile）
    ->
速度误差模型（Velocity Error Model）
    ->
速度命令补偿层（Velocity Command Compensation Layer）
    ->
导航安全层（Navigation Safety Layer）
```

## 当前仓库范围

当前版本：**K1 Forward Velocity Tracking Measurement Skill v0**

- 只测前进速度
- 不测转向
- 不测横向移动
- 不做自主导航
- 不做实时补偿
- 使用人工环境标签
- 支持 dummy data pipeline、schema validation、dry-run trial plan 和 measurement report
- 真实 K1 logging 仍需等待 ROS2 topic 人工验证

## 数据接口契约（Data Interface Contract）

`processed_environment_profile.json` 是本仓库最重要的下游数据契约。它连接当前测量 skill 与未来的速度补偿、命令安全适配、导航安全和仿真验证模块。

Schema:

```text
contracts/measurement_profile_schema.json
```

下游模块使用 profile 前必须检查环境匹配、有效速度范围、置信度、样本数量、ground truth 方法、odom 是否验证、是否允许外推和 warnings。

本仓库不实现 `compensate_velocity()`。

## 核心测量指标（Core Measurement Metrics）

```text
v_x_actual = (x_end - x_start) / (t_end - t_start)
speed_gain = v_x_actual / v_x_cmd
e_abs = v_x_actual - v_x_cmd
e_rel = (v_x_actual - v_x_cmd) / v_x_cmd
lateral_drift_rate = |y_end - y_start| / (t_end - t_start)
yaw_drift_rate = |yaw_end - yaw_start| / (t_end - t_start)
RMSE = sqrt(mean((v_actual_i - v_cmd)^2))
```

这些指标只描述测量结果，不执行速度补偿。

## M3 Dummy Data Pipeline

M3 建立 dummy 数据流水线，用于在连接真实 K1 ROS2 topic 之前验证仓库内部数据流程。dummy raw log 和 dummy profile 都不是真实机器人数据，不能用于速度补偿、导航或安全决策。

## M4 ROS2 Topic Discovery and Logger Skeleton

M4 提供只读 topic discovery 和 logger skeleton。`scripts/discover_ros2_topics.py` 只运行只读 `ros2 topic list`，关键词分类只是候选建议，不代表人工验证完成。

如果 ROS2 未安装，discovery 脚本会安全退出并返回 0。

## M5 Dry-run Forward Baseline Trial Manager

M5 生成并验证前进速度 baseline 实验计划。该阶段只运行 dry-run，不发布 ROS2 command，不移动机器人，不使用真实 K1 command topic。

真实执行仍然禁用，直到 K1 command interface 被人工验证。

## M6 Measurement Report Generator

M6 从 `processed_environment_profile.json` 生成 Markdown 测量报告。报告总结环境标签、速度画像、置信度、局限性和下游使用说明。

报告仍然是 measurement-only 输出，不实现速度补偿。由 dummy profile 生成的报告必须视为 dummy output，不能用于真实机器人补偿、导航或安全决策。

## v0 Dry-run Workflow

按顺序运行：

```powershell
py scripts/check_environment.py
py scripts/generate_dummy_raw_log.py
py scripts/process_trial_logs.py
py scripts/validate_profile_schema.py data/processed/dummy_processed_environment_profile.json
py scripts/generate_measurement_report.py
py scripts/run_forward_baseline.py --dry-run
py -m pytest
py -m compileall k1_measurement scripts
```

在部分 Windows 环境中，`py` 可用于替代 `python`。`data/raw` 和 `data/processed` 中的生成文件可能被 Git 忽略。`reports/dummy_measurement_report.md` 如果来自 dummy profile，也只是 dummy output。

## 安全声明

本仓库在以下条件全部满足之前，必须不得向 K1 发送真实运动命令：

- 机器人处于安全开阔区域
- 急停装置可用
- 机器人处于正确运动模式
- ROS2 topic 名称已确认
- command interface 已确认
- 有人工监督实验过程

任何可能发送运动命令的文件必须默认 dry-run，并包含人工确认、速度限制检查和急停提醒。

## 当前开发状态

当前状态见 [PROJECT_STATUS.md](PROJECT_STATUS.md)。
