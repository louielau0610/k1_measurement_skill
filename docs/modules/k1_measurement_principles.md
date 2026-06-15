# k1_measurement 原理文档

## 设计目标

`k1_measurement` 的目标是把 K1 前向速度测量流程做成可重复、可检查、可被下游补偿和论文分析使用的 artifact pipeline。它不是完整 ROS2 package，也不是真实运动控制层。

## 核心原则

- 测量优先：真实数据、环境标签、ground truth 和置信度比补偿结论更基础。
- 只读 discovery：ROS2 topic discovery 和 interface inspection 只能读取信息，不能发布运动命令。
- 保守 topic 处理：candidate topic 只是候选，必须人工确认后才能进入 mapping。
- dummy 与 real 分离：dummy raw log/profile/report 只能验证流水线，不能作为真实 K1 发现。
- 输出契约稳定：profile、dataset、risk map、report 的字段变化会影响下游，应配套测试和文档更新。

## 主要数据结构

- Field session：包含 topic mapping、ground truth sheet、logger summary 和 normalized logs。
- Measurement profile：把 trial 级速度测量转成环境 profile。
- Velocity response dataset：把 measurement artifact 整理成建模 record。
- Response prediction：对 `(v_cmd, environment, robot_state)` 的实际速度响应做保守估计。
- Navigation risk map：只输出 advisory risk，不声称真实导航安全提升。

## 安全边界

`command_runner.py` 和 `logger_node.py` 必须保持保守：默认 dry-run、速度限制、人工确认和拒绝不完整配置。任何新增真实运动能力都必须同时更新安全协议、测试和本模块文档。

## 算法意图

- `metrics.py` 提供小而可测的数值函数，复杂统计应组合这些基础函数。
- `ros2_readonly_validator.py` 用保守关键词分类 topic，分类结果只是 field review 输入。
- `velocity_response_model.py` 以有限数据做不确定性感知响应预测，不应过度外推。
- `navigation_risk_mapping.py` 把模型输出转换成 warning/risk metadata，不替代控制器。
- `visualization.py` 优先使用 matplotlib；不可用时 fallback 写简化 PNG，保证报告生成不中断。

## 扩展规则

- 新增测量 artifact 字段时，先更新 schema/contract，再更新 builder、validator、tests 和实现文档行号。
- 新增 ROS2 相关能力时，先证明只读或显式安全确认；不要把 topic 名称写死成真实结论。
- 新增报告或图像输出时，保证缺失输入可跳过或给出明确 warning。
## M25 Full-Range Velocity Principles

M25 treats the valid command-speed domain as an explicit configuration contract, not as a discovered deadzone threshold. `safe_command_speed_max` must be externally validated before executable plans can be produced. The high-priority 0.80-1.00 m/s region is sampled densely but does not define the full supported range.

The active M25 module only models longitudinal command speed versus measured actual speed. Historical yaw fields may remain in raw logs, but M25 does not use yaw drift as a feature, objective, metric, quality gate, or roadmap target. Candidate profiles expose observed actual-speed reachability and must reject unreachable targets unless a future milestone adds an explicit extrapolation policy.
