# M15R 不确定性感知速度响应模型基础

M15R 的目标是在 M14 数据集之后建立保守的 response model foundation。它把 `velocity_response_dataset_v1.json` 转换为 prediction contract、uncertainty/confidence 标签和有限 evaluation artifact。M15R 不实现速度补偿、反向命令映射、导航控制或 safe command adapter。

## 为什么压缩 standalone baseline-only M15

当前数据集只有 5 个 command velocity record，其中 `0.1 m/s` 还是 qualitative-only。单独做 baseline-only milestone 容易过度工程化，也可能让后续研究重点偏离不确定性和 navigation-aware risk mapping。因此 M15R 先实现保守的 proposed model interface，同时保留最小 baseline hooks 以便未来论文比较。

## 为什么仍保留 baseline hooks

未来 paper evaluation 需要说明 proposed method 相对简单方法的差异。M15R 保留：

- `nearest_lookup_baseline_v1`
- `naive_global_gain_baseline_v1`
- `piecewise_linear_baseline_v1`

这些只是 comparison hooks，不是完整 baseline-only 研究阶段。

## Dataset 输入

输入为：

- `outputs/research_datasets/velocity_response_dataset_v1.json`
- `configs/velocity_response_dataset_schema_v1.json`

CLI 会先通过 `k1_measurement.research_dataset_schema` 校验 dataset，再生成 predictions 和 limited evaluation。

## Output Contract

每个 prediction 包含 query velocity、model name、prediction type、可能的 numeric prediction、qualitative label、uncertainty label、confidence label、source record ids、nearest command points、interpolation/extrapolation flags、limitations 和 safety flags。

`compensation_allowed=false`，`safe_command_adapter_allowed=false`，`navigation_warning_ready=true` 会随每个 prediction 输出。

## Proposed Model

`uncertainty_aware_hybrid_v1` 是轻量 rule-based model，不是 ML model。

处理规则：

- exact numeric source：返回 source numeric velocity，标记为 structural sanity check。
- exact qualitative source：不生成 numeric prediction，保留 qualitative label。
- bounded interpolation：只在两侧都是 numeric source record 时做线性插值。
- mixed evidence：一侧 qualitative、一侧 numeric 时不做 numeric interpolation，返回 nearest evidence 和 high uncertainty。
- out-of-range：不做 aggressive extrapolation，不返回 numeric prediction。

## Baseline Hooks

`nearest_lookup_baseline_v1` 返回最近 command point 的 source evidence，可能是 numeric，也可能是 qualitative-only。

`naive_global_gain_baseline_v1` 只使用 numeric records 计算全局 gain。它忽略 deadzone、environment 和 uncertainty，因此只作为弱 baseline。

`piecewise_linear_baseline_v1` 只使用 numeric records 做区间内插值，不对 numeric range 外 extrapolate。

## Uncertainty / Confidence

M15R 只输出 labels，不输出 calibrated probabilities。允许的 uncertainty labels 为 `low`、`medium`、`medium_high`、`high`。允许的 confidence labels 为 `high`、`medium`、`low`、`unknown`。

这些标签来自 sparse dataset、qualitative-only evidence、single-session limitation 和 interpolation/extrapolation status。它们不能被解释为概率校准结果。

## 为什么还不是最终 proposed method

当前模型没有 repeated trials、没有外部 ground truth、没有 calibrated uncertainty、没有跨环境验证，也没有 navigation task evaluation。exact-source reconstruction 只用于结构 sanity check，不证明模型质量或 superiority。

## M16 如何使用

M16 可以把 M15R 的 prediction type、uncertainty label、confidence label 和 source limitations 转换为 navigation-aware risk mapping 输入。M16 仍不能把这些输出当成 compensation command、navigation controller 或 safe command adapter。

## Limitations

- sparse dataset；
- single robot；
- limited environment coverage；
- missing lateral drift, response delay, stop distance, and repeated-trial uncertainty；
- `0.1 m/s` is qualitative-only；
- no calibrated probabilistic uncertainty；
- no publication readiness claim。
