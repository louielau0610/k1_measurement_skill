# M7 Real K1 Measurement Preparation

## 研究问题

完整项目研究：

```text
v_actual = f(v_cmd, environment, robot_state)
```

M7 仍然只服务 measurement。它准备明天真实 K1 测试需要的 topic discovery、记录模板、baseline plan、报告和静态图，不实现 compensation 或 navigation。

## 为什么需要 M7

M0-M6 已经验证了项目结构、接口契约、metrics、dummy data pipeline、ROS2 discovery skeleton、dry-run baseline 和 report generator。M7 的目标是把真实测试前的现场步骤固定下来，让测试更快、更可读、更可复现。

M7 输出帮助现场完成：

- ROS2 是否可用。
- 当前 K1 ROS2 shell 能看到哪些 topic。
- 哪些 topic 可能是 odom / IMU / battery / robot_state / command 候选。
- message type 是否能被 `ros2 interface show` 检查。
- logger config 应该填写哪些字段。
- ground truth 应该逐 trial 记录哪些列。

## 为什么不是完整 ROS package

当前任务是 measurement preparation，不是部署 ROS node。真实 K1 topic mapping 尚未确认前，创建完整 ROS2 package 会让边界变得过早。本仓库保持 Python-based toolkit，使用 ROS2 CLI 做只读发现和报告。

## 为什么不能猜 topic mapping

真实 topic 名称、message schema、command interface、robot mode、gait、ground-truth 方法和测试距离都依赖现场 K1 环境。M7 只输出候选分类，不把任何 topic 标为 confirmed。

## 如何准备 M8 real baseline

M7 生成 `ros2_topic_discovery_report.json` 和 `ros2_topic_discovery_report.md`。现场人工确认 topic 后，填写 `configs/real_k1_logger_template.yaml`，先做 static logging test，再做一次 smoke forward trial，最后执行完整 baseline：

```text
vx_cmd_mps: 0.1, 0.2, 0.3, 0.4
repeats_per_speed: 3
```

这个 baseline 只测 forward velocity，不测 turning，不测 navigation，不做 compensation。

## measurement artifact 如何支持后续 compensation

后续 compensation 需要可靠的 `speed_gain`、absolute error、relative error、drift、环境标签和置信度。M7 的模板和图表确保第一批真实数据有足够上下文，避免把不完整或 dummy 数据带入下游模型。

## 为什么加入 visualization

Visualization 只作为 report artifact，用来提高测量可读性和实验诊断效率。M7 不创建 dashboard、web UI、frontend 或 RViz plugin。

Expected plot artifacts:

- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `trial_timeseries_plot.png`
- `drift_plot.png`

## 明天期望输出

- `ros2_topic_discovery_report.json`
- `ros2_topic_discovery_report.md`
- `raw_measurement_log.csv`
- `ground_truth_trial_sheet.csv`
- `processed_environment_profile.json`
- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `measurement_report.md`

## 运行命令

```powershell
python scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

如果当前 shell 没有 ROS2：

```powershell
python scripts/validate_ros2_readonly_topics.py --print-only --output-dir outputs/ros2_readonly_validation
```
