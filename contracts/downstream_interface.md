# Downstream Interface

本文档定义 K1 测量仓库与未来下游模块之间的数据接口。本文档中文优先，JSON 字段名保持英文。

## 核心接口文件

下游接口文件是：

```text
processed_environment_profile.json
```

该文件由本仓库的测量日志处理流程生成，用于描述特定环境下的前进速度命令与实际速度之间的统计关系。

## 未来消费模块

该 profile 会被未来模块消费：

- velocity compensation model
- safe command adapter
- navigation safety layer
- simulation validation pipeline

## 下游必须检查的字段

下游模块在使用 profile 前必须检查：

- `schema_version`
- `environment match`
- `valid_speed_range`
- `confidence`
- `n_trials`
- `ground_truth_method`
- `odom_validated`
- `extrapolation_allowed`
- `warnings`

## 使用规则

下游模块不得盲目把 profile 用于速度补偿，除非同时满足：

1. profile 的环境标签与当前部署环境匹配。
2. 期望速度位于 `valid_speed_range` 内。
3. `confidence` 达到当前任务可接受标准。
4. `n_trials` 样本数量足够。
5. 如果需要外推，`extrapolation_allowed` 必须为 `true`。
6. `warnings` 不包含安全关键问题。

如果任一条件不满足，下游模块必须拒绝使用该 profile，或进入人工审核、低速验证、仿真验证等更保守流程。

## 当前仓库边界

本仓库不实现 `compensate_velocity()`。

未来补偿模块可能像下面这样消费 profile：

```python
profile = load_environment_profile("tile_dry_flat_profile.json")
vx_cmd = compensate_velocity(vx_desired=0.3, profile=profile)
```

但这是未来下游工作，不属于当前 `k1_measurement_skill` 仓库范围。本仓库只定义并验证测量 profile 的数据契约。
