# M14 速度响应数据集 v1

M14 的目标是把 Measurement v0 的结构化 artifact 转换为 research-grade velocity response dataset v1。这个阶段只做数据构造和校验，不做 baseline model、不做 uncertainty-aware model、不做速度补偿、不做导航控制，也不实现 safe command adapter。

## 为什么需要数据集层

Measurement v0 已经给出真实 K1 在单一实验环境下的前进速度响应证据，但这些 artifact 分散在 profile、summary、CSV、报告和 closure 文件中。M15 之前需要一个稳定的数据集层，把来源、可直接映射字段、可推导字段、定性字段和不可用字段分开，避免后续建模误把缺失值当作实验结果。

## 使用的 Measurement v0 来源

- `outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json`
- `outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json`
- `outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.csv`
- `outputs/real_k1_field_tests/measurement_v0_closure_summary.json`

构造器优先读取结构化 JSON 和 CSV，不从任意 prose 中解析数值。

## 构造规则

- Direct fields：来自结构化 artifact 的显式字段，例如 robot model、trial id、`vx_cmd_mps`、duration、tracking category。
- Derived fields：由结构化字段确定性得到，例如 `records_count`、environment label、trial count、localization source。
- Qualitative fields：来自 Measurement v0 已有解释的标签，例如 deadzone、weak response、under-tracking、stable tracking。
- Unavailable fields：Measurement v0 没有提供且不能安全推导的字段，例如 lateral drift、response delay、stop distance、uncertainty statistics。

不可用字段必须写入 limitation 或 unavailable list，不能伪造成数值。

## 映射摘要

| dataset v1 field | Measurement v0 source | type | notes |
| --- | --- | --- | --- |
| `robot_model` | `real_k1_velocity_profile_v0.json.platform` | direct | K1 平台描述。 |
| `vx_cmd_mps` | `trial_points[].vx_cmd_mps` | direct | 已记录命令速度。 |
| `vx_actual_mps_mean` | `trial_points[].v_actual_est_mps` | derived | 仅在 source 非 null 时写入。 |
| `qualitative_response_label` | `trial_points[].interpretation` | qualitative | 数值缺失时仍可保留定性响应。 |
| `environment_label` | profile environment | derived | floor type + condition。 |
| `localization_source` | odometer topic / limitations | qualitative | odometer-primary, no external ground truth。 |
| `confidence_label` | limitations and repeat flags | qualitative | 单 session / 单 trial 限制必须保留。 |
| `battery_state` | optional topic status | unavailable | 保持 optional，不作为必填。 |
| `remote_controller_state` | removed topic status | unavailable | out of scope，不进入数据集。 |
| `lateral_drift_m` | none | unavailable | 不伪造。 |
| `response_delay_s` | none | unavailable | 不伪造。 |
| `stop_distance_m` | none | unavailable | 不伪造。 |

## Schema v1 符合性

数据集通过 `k1_measurement.research_dataset_schema` 校验：

- schema hardening metadata 有效；
- dataset object 包含 `records`；
- 每条 record 满足最小可用字段；
- disallowed fields 递归拒绝；
- `battery_state` 不作为必填；
- compensation / inverse mapping / navigation control / safe command adapter readiness 不被打开。

## M15 使用方式

M15 baseline response models 可以读取 `outputs/research_datasets/velocity_response_dataset_v1.json` 中的 records。M15 可以使用已有 `vx_actual_mps_mean` 的点做初始 response curve，也可以把只有定性响应的点作为分类边界或低置信度区域。

M15 不能假设：

- 当前数据集有足够 repeated trials；
- 当前数据集支持 uncertainty-aware model；
- 当前数据集支持 compensation readiness；
- 当前数据集支持 safe command adapter readiness；
- 当前数据集支持 navigation control。

## 为什么边界仍然关闭

`compensation_ready=false`，因为 Measurement v0 主要是单 session、少量速度点、mostly single trial。它不足以输出 corrected command velocity。

`safe_command_adapter_ready=false`，因为本仓库没有实现 command adapter，也没有足够验证覆盖。

`navigation_warning_ready=true`，因为 warning / confidence 使用可以消费定性低速风险区域，但这不是 navigation control。

## 当前数据集限制

- single session；
- lab hard floor only；
- mostly single trial per speed；
- odometer-primary, no external ground truth；
- missing lateral drift, response delay, stop distance, and repeated-trial uncertainty；
- `0.45 m/s` yaw drift requires repeat before stronger claims。
