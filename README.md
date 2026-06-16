# K1 速度测量工具包

## M26-B 统一领域契约与模式

M26-B 实现平台无关的契约层：纯领域值对象、不变式验证、错误分类、能力与成熟度模型、硬件端口接口、确定性 JSON 编解码器、版本化 JSON Schema。

新增 `calibration_skill` 包（`domain/`、`ports/`、`schemas/`），可在无任何厂商 SDK 的情况下独立导入和测试。

关键 M26-B 产物：

- `calibration_skill/domain/` — 纯平台无关值对象和不变式
- `calibration_skill/ports/` — 抽象 Protocol 接口
- `calibration_skill/schemas/v1/` — 13 个版本化 JSON Schema（v1.0.0）
- `docs/engineering/m26b_error_taxonomy.md` — 错误分类
- `outputs/engineering/m26b_readiness.json` — 就绪追踪（使用 ImplementationMaturity 模型）
- `scripts/validate_engineering_artifacts.py` — 工程产物验证器

**重要**：M26-B 不实现任何适配器。现有 K1 适配器未迁移。G1/GO1 适配器尚未实现。新架构下无平台适配器可运行。

## M26-A 工程重置与多平台架构冻结

M26-A 暂停所有非工程实验分支，将仓库重新定位为**工程级、agent 可调用的腿式机器人速度标定技能**，明确支持以下目标平台：

1. **Booster K1** — 双足人形机器人（硬件验证参考实现）
2. **Unitree G1** — 双足人形机器人（仅脚手架）
3. **Unitree GO1** — 四足机器人（仅脚手架）

M26-A 是纯文档、盘点、架构和迁移规划里程碑，**不连接机器人、不发送运动命令、不安装 SDK、不执行物理测试、不修改金标定、不改变补偿模型行为**。

关键工程文档：

- `docs/engineering/m26a_program_reset.md` — 工程重置声明
- `docs/engineering/current_repository_inventory.md` — 仓库盘点
- `docs/engineering/current_dependency_map.md` — 当前依赖关系图
- `docs/engineering/target_multi_platform_skill_architecture.md` — 目标架构
- `docs/engineering/target_end_to_end_use_chain.md` — 端到端使用链
- `docs/engineering/preliminary_core_contracts.md` — 核心接口契约
- `docs/engineering/platform_capability_matrix.md` — 平台能力矩阵
- `docs/engineering/multi_platform_migration_plan.md` — 迁移计划
- `docs/adr/` — 架构决策记录（ADR-0001 至 ADR-0005）
- `outputs/engineering/m26a_repository_audit.json` — 机器可读审计
- `outputs/engineering/m26a_platform_capability_matrix.json` — 平台能力矩阵 JSON
- `outputs/engineering/m26a_readiness.json` — 工程就绪追踪

**暂停的工作**：M25 数据采集、M26-M28 建模/补偿/验证、yaw drift 研究、deadzone 研究、论文工作（P 系列）、在线 yaw 调整、物理补偿实验。

**G1/GO1 就绪声明**：在物理验收里程碑完成之前，不得声称 G1 或 GO1 运行时支持。

## M25-T K1 SDK 运动路径与安全上限统一

M25-T 将 K1 preflight 对齐到已确认的 SDK 命令路径：`booster_sdk_kPrepare_kWalking_Move`。当前 K1 adapter 的固定执行序列是 `kPrepare -> kWalking -> Move(vx, 0.0, 0.0)`；`control_mode` 和 `gait_mode` 只是可选元数据，不再作为当前 K1 配置的执行阻塞项。这里不把 `kWalking` 描述为用户可选 gait，它只是固定验证序列的一部分。

`safe_command_speed_max` 仍由 `configs/m25_k1_safe_speed_operator_confirmation.yaml` 提供，当前 K1 实验配置为 `0.6 m/s`。exploration package 已可执行就绪（仍需真实操作流程确认），formal package 仍在 exploration review gate 前阻塞。探索计划为 `[0.35, 0.40, 0.50, 0.60]` × 3 = 12 次，正式计划为 `[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]` × 5 = 30 次。

## M25 当前主线：全范围纵向速度画像

M25 将当前主动路线重定向到 K1 纵向 `command velocity -> measured actual velocity` 的全范围画像。适用命令域由显式工程配置给出：

```text
[valid_command_speed_min, safe_command_speed_max]
```

`valid_command_speed_min` 是补偿器适用下界，不是 deadzone 估计；`safe_command_speed_max` 已确认为 `0.6 m/s`（由操作者确认）。当前 K1 实验配置的有效命令域为 `[0.35, 0.60] m/s`，高优先级评估区间为 `0.50-0.60 m/s`。命令速度不得超出 `0.6 m/s`。

M25 主动路线已放弃 deadzone 研究；yaw drift / yaw compensation 暂停并从 M25 目标、模型特征、验证指标和 benefit gate 中移除。M25 只建立测量、计划、profile contract 和候选 profile 基础，不声明补偿效果。

关键文档和入口：

- `docs/m25_full_range_velocity_profiling.md`
- `docs/m25_repository_cleanup_manifest.md`
- `configs/m25_full_range_velocity_profile_template.yaml`
- `k1_measurement/full_range_velocity_profile.py`
- `scripts/plan_full_range_velocity_profile.py`

后续路线：M26 比较全范围单调响应模型，M27 实现或最终确定 inverse velocity compensation，M28 做全范围 direct-vs-compensated 真实机器人验证。

## M25-R 采集就绪闭环

M25-R 新增 safe-speed 操作者确认、真实采集 preflight、保持阻塞的 exploration/formal collection package，以及 exploration-to-formal gate。

## M25-S K1 安全速度集成

M25-S 将已确认的 K1 安全前向命令速度上限 `0.6 m/s` 集成到 M25/M25-R 真实采集流程中。当前 exploration plan 为 4 个命令点 × 3 次重复 = 12 次试验，formal plan 为 6 × 5 = 30 次试验。安全速度已确认，但完整执行 preflight 仍因 control_mode/gait_mode 等操作字段未解析而阻塞。

从这里开始：

- `docs/m25r_real_data_collection_readiness.md`
- `docs/m25s_k1_safe_speed_integration.md`
- `configs/m25_k1_safe_speed_operator_confirmation.yaml`
- `configs/m25_k1_s2_real_collection.yaml`
- `configs/m25_real_collection_preflight_template.yaml`

在真实 formal profile 数据可用之前，不得启动 M26 response-model fitting。

## M14 研究数据集 v1

M14 现在可以从 Measurement v0 artifact 构造 `outputs/research_datasets/velocity_response_dataset_v1.json`，并生成 validation report 与 future trial template。M14 只做数据集构造和校验，不实现建模、速度补偿、导航控制或 safe command adapter，也不声称 publication readiness。

## M15R 不确定性感知响应模型基础

M15R 新增保守的 response model foundation 和最小 baseline hooks，用于从 M14 数据集生成 prediction contract、uncertainty/confidence 标签和 limited evaluation。M15R 不实现速度补偿、反向命令映射、导航控制或 safe command adapter，也不声称 publication readiness。

## M16 离线导航风险映射

M16 消费 M15R response model predictions，生成离线 navigation-aware reliability / risk assessments 和 warning metadata。M16 只支持 advisory 分析，不实现速度补偿、反向命令映射、导航控制或 safe command adapter，也不声称真实导航安全提升。

## M17 管线评估报告

M17 将 M13-M16 artifact 汇总为 paper-style evaluation outputs，包括 JSON evaluation report、Markdown summary、artifact table、limitations 和 next-experiments。M17 不是真实导航性能评估，不实现速度补偿、反向命令映射、导航控制或 safe command adapter，也不声称 publication readiness。

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
# M26-C Mock Adapter 与 Dry-Run Skill Service

M26-C 在 M26-B 合约层之上新增第一个可执行但完全 hardware-free 的 skill
层：显式 mock-only `AdapterRegistry`、确定性的 `MockRobotAdapter`、
dry-run `SkillService`，以及带内存审计记录的 `dry_run_end_to_end` 流程。

关键 M26-C 产物：

- `calibration_skill/adapters/registry.py`
- `calibration_skill/adapters/mock.py`
- `calibration_skill/skill/service.py`
- `calibration_skill/runtime/dry_run.py`
- `docs/engineering/m26c_mock_adapter_and_skill_service.md`
- `docs/engineering/m26c_dry_run_end_to_end.md`
- `outputs/engineering/m26c_readiness.json`

**边界**：M26-C 仅支持 mock 平台与 dry-run。它不迁移 K1，不实现 G1/GO1，
不连接硬件，不打开 socket，不启动 DDS，不发送 UDP，也不导入 vendor SDK
runtime。新架构下仍不声明 K1/G1/GO1 runtime support、hardware verification
或 release readiness。
