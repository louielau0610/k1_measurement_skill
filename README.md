# K1 速度测量工具包

## 项目定位

`k1_measurement_skill` 是 **K1 Velocity Measurement, Compensation, and Navigation Safety Pipeline** 的测量优先模块。大项目关心的问题是：

```text
v_actual = f(v_cmd, environment, robot_state)
```

本仓库只负责把 K1 的前进速度测量流程做得可重复、可检查、可用于后续建模。它不是完整 ROS2 package，不实现速度补偿、不实现导航、不发布真实机器人运动命令，也不硬编码尚未确认的 K1 topic。

```text
measurement -> compensation -> navigation safety
```

当前仓库只覆盖第一步 measurement。后续 compensation 和 navigation safety 必须基于真实测量数据、环境标签、ground truth 和置信度判断，不能使用 dummy artifact 作为真实 K1 结论。

## 当前状态

- M0-M6 completed。
- M7 in progress: Real K1 Measurement Preparation Pack。
- 真实 K1 ROS2 topic mapping 仍为 TBD，需要在明天的 K1 ROS2 shell 中确认。
- 现有 dummy raw log、dummy profile、dummy report 只用于验证数据流水线，不是 K1 实测发现。

M7 的目标是让真实测试前的准备更快、更清楚、更可复现：

- ROS2 availability check
- real K1 topic discovery
- candidate topic classification
- message type inspection
- logger configuration template
- forward velocity baseline plan
- ground-truth recording template
- field-test checklist
- static visualization artifacts

## 仓库边界

本仓库保持为 Python-based K1 velocity measurement toolkit，包含配置、脚本、分析、可视化 artifact 和报告生成能力。M7 不创建完整 ROS2 package layout。

M7 discovery tools 只执行 ROS2 CLI 只读检查：

- `ros2 --help`
- `ros2 topic list`
- `ros2 topic list -t`
- optional `ros2 interface show <message_type>`

这些工具不会发布到 `cmd_vel` 或任何运动 topic。候选 topic 只来自保守关键词分类，不代表人工确认。

## M7 快速流程

在真实 K1 ROS2 shell 中运行：

```powershell
python scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

没有 ROS2 的开发环境中可先运行 dry-run report：

```powershell
python scripts/validate_ros2_readonly_topics.py --print-only --output-dir outputs/ros2_readonly_validation
```

生成报告后，人工确认候选 odom / IMU / battery / robot_state / command topics，再填写：

```text
configs/real_k1_logger_template.yaml
```

前进速度 baseline 保持原始速度组：

```text
0.1, 0.2, 0.3, 0.4 m/s
每个速度 3 次
```

## 关键 artifact

- `outputs/ros2_readonly_validation/ros2_topic_discovery_report.json`
- `outputs/ros2_readonly_validation/ros2_topic_discovery_report.md`
- `configs/real_k1_logger_template.yaml`
- `configs/forward_velocity_baseline_plan.yaml`
- `templates/ground_truth_trial_sheet.csv`
- `docs/real_k1_field_test_checklist.md`
- `docs/m7_real_k1_measurement_preparation.md`

可视化只作为测量报告 artifact，用于提升可读性和诊断效率，不是 dashboard、frontend 或 RViz plugin：

- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `trial_timeseries_plot.png`
- `drift_plot.png`

## 验证命令

```powershell
python -m pytest
python -m pytest tests/test_ros2_readonly_validator.py -q
python -m pytest tests/test_visualization.py -q
python -m compileall k1_measurement scripts tests
python scripts/validate_ros2_readonly_topics.py --print-only --output-dir outputs/ros2_readonly_validation
```
