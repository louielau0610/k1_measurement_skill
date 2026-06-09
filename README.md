# K1 速度测量工具包

## M14 研究数据集 v1

M14 现在可以从 Measurement v0 artifact 构造 `outputs/research_datasets/velocity_response_dataset_v1.json`，并生成 validation report 与 future trial template。M14 只做数据集构造和校验，不实现建模、速度补偿、导航控制或 safe command adapter，也不声称 publication readiness。

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
- M7 complete: Real K1 Measurement Preparation Pack。
- M8 current milestone: Real K1 Field Logging and Forward Baseline Execution Support。
- 真实 K1 ROS2 topic mapping 仍为 TBD，需要在明天的 K1 ROS2 shell 中确认。
- 现有 dummy raw log、dummy profile、dummy report 只用于验证数据流水线，不是 K1 实测发现。

M8 让项目进入 real field logging workflow ready 状态：

- 创建真实测试 session 目录。
- 校验人工确认后的 topic mapping。
- 使用 `ros2 bag record` 启动只读多 topic logging。
- 记录 ground-truth trial metadata。
- 生成 session manifest。
- 在 exported CSV logs 可用时归一化到测量 pipeline 兼容格式。
- 生成或引用 first real measurement artifacts 和 plots。

## 仓库边界

本仓库保持为 Python-based K1 velocity measurement toolkit，包含配置、脚本、分析、可视化 artifact 和报告生成能力。M8 不创建完整 ROS2 package layout。

M7/M8 工具只做只读 discovery 和 logging：

- `ros2 --help`
- `ros2 topic list`
- `ros2 topic list -t`
- optional `ros2 interface show <message_type>`
- `ros2 bag record -o <session_dir>/raw_ros/rosbag <confirmed topics...>`

这些工具不会发布到 `cmd_vel` 或任何运动 topic。候选 topic 只来自保守关键词分类，不代表人工确认。

## M8 快速流程

创建 session：

```powershell
py scripts/create_real_k1_field_session.py --session-id 20260609_k1_forward_baseline --output-root data/real_k1_sessions
```

在真实 K1 ROS2 shell 中运行 discovery：

```powershell
py scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

填写并校验 mapping：

```powershell
py scripts/validate_real_k1_topic_mapping.py --mapping data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

启动静态 logger：

```powershell
py scripts/start_real_k1_field_logger.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline --duration-sec 30
```

归一化 exported CSV logs：

```powershell
py scripts/normalize_real_k1_logs.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline
```

前进速度 baseline 保持原始速度组：

```text
0.1, 0.2, 0.3, 0.4 m/s
每个速度 3 次
```

## 关键 Artifact

- `data/real_k1_sessions/<session_id>/session_manifest.json`
- `data/real_k1_sessions/<session_id>/topic_mapping.yaml`
- `data/real_k1_sessions/<session_id>/ground_truth_trial_sheet.csv`
- `data/real_k1_sessions/<session_id>/logger_run_summary.json`
- `data/real_k1_sessions/<session_id>/normalized/normalization_report.json`
- `data/real_k1_sessions/<session_id>/normalized/raw_measurement_log.csv`
- `docs/m8_real_k1_field_logging_workflow.md`
- `docs/real_k1_field_test_checklist.md`

可视化只作为测量报告 artifact，用于提升可读性和诊断效率，不是 dashboard、frontend 或 RViz plugin：

- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `trial_timeseries_plot.png`
- `drift_plot.png`

## 验证命令

```powershell
py -m pytest
py -m compileall k1_measurement scripts tests
py scripts/create_real_k1_field_session.py --session-id test_m8_session --output-root outputs/m8_field_session_test
py scripts/validate_real_k1_topic_mapping.py --mapping outputs/m8_field_session_test/test_m8_session/topic_mapping.yaml
```

默认 template mapping 仍包含 `TBD`，所以 mapping validator 会以 controlled validation failure 返回，而不是 Python crash。

## M13 研究级速度响应基础

M13 将研究问题固定为：

```text
v_actual = f(v_cmd, environment, robot_state)
```

新增内容：

- `docs/m13_research_grade_velocity_response_foundation.md`
- `paper/method/velocity_response_modeling_plan.md`
- `configs/velocity_response_dataset_schema_v1.json`
- `scripts/validate_velocity_response_dataset_schema.py`
- `outputs/research_foundation/m13_research_foundation_summary.json`

M13 只定义研究问题、建模计划、数据集 schema、schema 校验 CLI 和测试。M13 不启动文献综述，不启动 P1，不撰写完整论文草稿，不实现速度补偿、反向命令映射、导航控制或 safe command adapter。`battery_state` 保持可选，`remote_controller_state` 永久不进入范围。
