# M8 Real K1 Field Logging Workflow

## M8 比 M7 多了什么

M7 准备 topic discovery、候选分类、配置模板和现场 checklist。M8 把这些准备步骤推进到可执行的 real field logging workflow：

- 创建真实测试 session 目录。
- 校验人工确认后的 topic mapping。
- 使用 `ros2 bag record` 做只读多 topic logging。
- 复制 ground-truth trial sheet 并检查列和 planned trials。
- 生成 session manifest。
- 在有 exported CSV logs 时，保守归一化为测量流水线可读格式。
- 为 first real report 和 plots 准备 session 内路径。

M8 仍然不是完整 ROS2 package，不发布运动命令，不实现 compensation 或 navigation。

## Step A: 创建 Session

```powershell
py scripts/create_real_k1_field_session.py --session-id 20260609_k1_forward_baseline --output-root data/real_k1_sessions
```

生成目录：

```text
data/real_k1_sessions/20260609_k1_forward_baseline/
|-- session_manifest.json
|-- topic_mapping.yaml
|-- field_session_config.yaml
|-- ground_truth_trial_sheet.csv
|-- trial_notes.md
|-- raw_ros/
|-- normalized/
|-- processed/
|-- plots/
`-- reports/
```

## Step B: 在真实 K1 ROS2 shell 运行 M7 Discovery

```powershell
py scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

复查 `ros2_topic_discovery_report.md`，只把人工确认后的 topic 和 message fields 写入 session 的 `topic_mapping.yaml`。

## Step C: 填写 Topic Mapping

编辑：

```text
data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

不要猜 topic、message type、timestamp field、robot mode、gait 或 command schema。未确认字段保持 `TBD`。

## Step D: 校验 Mapping

```powershell
py scripts/validate_real_k1_topic_mapping.py --mapping data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

Required sections 如果仍为 `TBD` 或 `confirmed: false`，命令会返回 controlled validation failure，不会把 mapping 当成可用。

## Step E: 启动静态 Logger

```powershell
py scripts/start_real_k1_field_logger.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline --duration-sec 30
```

该命令只构造并运行：

```text
ros2 bag record -o <session_dir>/raw_ros/rosbag <confirmed topics...>
```

不会发布任何 movement command。

## Step F: Smoke Trial 和 Full Baseline

先做一次 smoke forward trial，检查 raw log 完整性、timestamp、odom、IMU、battery、robot mode 字段。确认后执行完整 baseline：

```text
0.1 m/s x 3
0.2 m/s x 3
0.3 m/s x 3
0.4 m/s x 3
```

ground truth 数据填入 session 内 `ground_truth_trial_sheet.csv`。

## Step G: Normalize Logs

如果 raw ROS data 已导出为 CSV 并放在 `raw_ros/*.csv`：

```powershell
py scripts/normalize_real_k1_logs.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline
```

输出：

```text
normalized/raw_measurement_log.csv
normalized/normalization_report.json
```

如果没有 parseable CSV，normalizer 会生成 placeholder report，说明缺少 raw export，而不是静默失败或伪造数据。

## Step H: 生成 Report 和 Plots

归一化 CSV 可作为后续真实 processing 的输入。现有 dummy pipeline 仍保持不变；真实 pipeline 需要在确认字段完整后，将 session 内 normalized CSV 转成 processed profile，再生成：

- `processed/processed_environment_profile.json`
- `plots/velocity_error_plot.png`
- `plots/speed_gain_plot.png`
- `plots/trial_timeseries_plot.png`
- `reports/measurement_report.md`

## 如何解释 Missing Data

M8 normalizer 不发明缺失值。topic mapping 中仍为 `TBD` 的字段、raw CSV 不存在的字段、ground-truth sheet 未填写的字段，会在 normalized CSV 中留空，并在 normalization report 中保留上下文。留空字段意味着该 session 还不能作为可靠 compensation 输入。
