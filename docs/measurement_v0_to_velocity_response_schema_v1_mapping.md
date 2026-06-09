# Measurement v0 到 Velocity Response Schema v1 映射

本文定义现有 Measurement v0 artifact 如何映射到 M13 velocity response dataset schema v1。本文是 M13.1 的桥接文档，用于准备 M14 的 dataset construction；它不是 M14 实现，不引入补偿、反向命令映射、导航控制或 safe command adapter。

## 来源 Artifact

现有 Measurement v0 的主要来源文件包括：

- `outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json`
- `outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.csv`
- `outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json`
- `outputs/real_k1_field_tests/measurement_v0_closure_summary.json`
- `docs/real_k1_forward_velocity_field_test_v0.md`
- `docs/real_k1_velocity_profile_contract_v0.md`
- `reports/real_k1_forward_velocity_analysis_v0.md`

这些文件可以作为 M14 构造研究数据集的输入，但不能自动变成补偿模型、导航控制器或论文级结论。

## 映射原则

- 可以直接映射的字段只来自已经存在的结构化 artifact。
- 只能定性映射的字段必须保留 qualitative 标签，不能伪造数值。
- 不可用字段必须标记为 unavailable 或 limitation，不能补写。
- 缺失的响应维度，例如 yaw drift、lateral drift、response delay、stop distance，不能伪造。
- qualitative label 只允许在数值测量不可用，或 Measurement v0 已经提供定性结论时使用。
- 不能从 Measurement v0 推断 compensation readiness。
- 不能从 Measurement v0 推断 safe command adapter readiness。
- `battery_state` 是可选字段，不是 schema v1 的必填项。
- `remote_controller_state` 不属于研究数据集输入范围。

## 映射表

| schema field | source from Measurement v0 | mapping type: direct / derived / qualitative / unavailable | notes |
| --- | --- | --- | --- |
| `robot_model` | `real_k1_velocity_profile_v0.json.platform` | direct | 可映射为 K1 平台描述。 |
| `robot_id` | none | unavailable | v0 artifact 未提供稳定 robot id，不能伪造。 |
| `vx_cmd_mps` | `trial_points[].vx_cmd_mps` 或 trial CSV | direct | 仅限已记录的前进速度命令。 |
| `vx_actual_mps_mean` | `trial_points[].v_actual_est_mps` | derived | 只有字段存在且非 null 时才可映射；缺失时不能补值。 |
| `qualitative_response_label` | `trial_points[].tracking_category` / `interpretation` | qualitative | 数值不可用时可使用定性响应标签。 |
| `measurement_source` | source artifact path | direct | 记录来源 JSON/CSV/Markdown artifact。 |
| `localization_source` | `measurement_topics.odometer` / limitations | qualitative | v0 主要依赖 odometer，未提供外部 ground truth。 |
| `environment_label` | `environment.floor_type` + `environment.condition` | derived | 可组合为 lab hard floor / dry 等环境标签。 |
| `confidence_label` | `limitations` / trial repeat count | qualitative | 可给低置信度或需要重复试验标签，但不能声称 calibration-grade。 |
| `confidence_score` | none | unavailable | v0 未定义数值置信分数，不能伪造。 |
| `trial_count` | trial grouping by command value | derived | 多数速度点只有单次试验，应保留 limitation。 |
| `sample_count` | normalized logs if available | unavailable | 当前 profile contract 不直接提供逐样本计数。 |
| `battery_state` | excluded/optional topics | unavailable | 保持 optional/future only。 |
| `remote_controller_state` | explicitly removed | unavailable | 永久 out of scope，不映射。 |
| `yaw_drift` | `dtheta_rad` if explicitly present | derived | 只有已有字段可用；缺失响应维度不能伪造。 |
| `lateral_drift` | none | unavailable | v0 未提供，不能伪造。 |
| `response_delay` | none | unavailable | v0 未提供，不能伪造。 |
| `stop_distance` | none | unavailable | v0 未提供，不能伪造。 |
| `compensation_ready` | `downstream_usage.compensation_ready` | direct | 必须保持 false，不能从数据集推断为 true。 |
| `navigation_control_ready` | none | unavailable | Measurement v0 不实现 navigation control。 |
| `safe_command_adapter_ready` | `downstream_usage.safe_command_adapter_ready` | direct | 必须保持 false。 |

## 对 M14 的准备

M13.1 将 Measurement v0 artifact 的可映射字段、定性字段和不可用字段分开。M14 可以在这个边界内构造 dataset records，但必须继续保留来源路径、限制说明和不可用字段，不得把缺失测量写成实验结果。
