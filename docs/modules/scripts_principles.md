# scripts 原理文档

## 设计目标

`scripts/` 把库代码变成可执行研究流程。脚本层应该薄、明确、可重复：解析参数、调用库函数、写 artifact、输出报告。复杂业务逻辑应优先下沉到 `k1_measurement/`、`calibration_core/` 或 `platforms/`，以便测试复用。

## 脚本分类

- Session/采集：创建 session、运行 logger、执行 smoke/baseline/replication trial。
- Discovery/校验：只读 ROS2 discovery、topic mapping、profile/schema/contract/manifest 校验。
- 抽取/QC：从 state logs 或 ROS2 odometer logs 抽取测量并生成 QC。
- 分析/建模/补偿：生成 response dataset、模型预测、风险映射、补偿 sweep 和验证审计。
- 计划/报告：生成 trial plan、completion pack、Markdown/JSON/CSV artifact 和展示输出。

## 核心原则

- CLI 是编排层，不是隐藏业务逻辑的地方。
- 脚本必须写出可追溯 artifact：输入路径、输出路径、summary/report、必要时附 hash 或 provenance。
- 涉及真实机器人运动的脚本必须默认 dry-run 或要求显式确认。
- 分析脚本必须区分 direct/compensated、old/new profile、faulty/corrected extraction，避免把实验版本混淆。
- QC 脚本应尽早失败并给出可读报告，而不是让后续分析默默消费坏数据。

## 安全边界

`send_m23b_k1_velocity_command.py` 和所有 `run_*_trials.py` 是最高风险脚本。新增或修改这类脚本时，必须检查：

- 是否默认 dry-run。
- 是否有人工确认。
- 是否有限速。
- 是否提醒急停。
- 是否记录 command log。
- 是否避免硬编码未确认 topic。

## 扩展规则

- 新 CLI 参数改变输出 artifact 时，同步更新实现文档和相关 docs。
- 新实验 milestone 脚本应提供 plan、execution、QC、analysis 四类入口，或明确说明缺哪一类。
- 重复逻辑超过一个脚本时，应提取到库模块并补测试。
- 修复含 BOM 的脚本时，刷新本实现文档中对应编码注意。
## M25 CLI Principles

M25 scripts are deterministic, planning-first, and hardware-inert. They report machine-readable JSON errors, return nonzero exit codes for blocked executable plans or invalid sessions, and never execute robot motion. The planner records the random seed in generated artifacts so trial ordering is reproducible.

## M25-R CLI Principles

M25-R scripts distinguish planning inspection from executable readiness. Blocked preflight/package commands intentionally return nonzero while still writing inspectable artifacts where appropriate. Temporary fixture safe-speed values are allowed only in tests and validation commands; they must not be committed as real evidence.

## M26-E Release-Gate Principles

M26-E release scripts are local engineering gates, not publishing tools. They must be deterministic, hardware-free, and conservative about claims. A dirty initial repository is a failure, an unexpected final repository mutation is a failure, and scripts must report the mutation rather than repairing it.

The release gate may write only an explicitly requested summary path. Build checks are conditional on local build tooling and must not install missing build tools from the internet. Vendor SDKs, ROS2, DDS, sockets, UDP, and hardware adapters remain outside the dry-run package boundary.
