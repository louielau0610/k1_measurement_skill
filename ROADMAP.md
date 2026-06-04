# Roadmap

本文档以中文优先描述 K1 速度测量、补偿与导航安全完整项目的阶段规划。

## Stage 0: Measurement Skill

目标：

```text
v_x_cmd -> v_x_actual
```

当前仓库 `k1_measurement_skill` 只实现这一阶段。重点是安全地采集前进速度命令与实际执行速度之间的关系，并输出可被下游模块消费的环境相关速度画像。

## Stage 1: Environment Profile Builder

目标是把多次实验日志整理成环境相关 profile。

示例输出：

- `tile_dry_flat_profile.json`
- `carpet_dry_flat_profile.json`
- `rubber_dry_flat_profile.json`

这些 profile 应包含速度范围、样本数量、统计误差、置信度和环境标签。

## Stage 2: Velocity Error Model

目标：

```text
v_x_actual = f(v_x_cmd, environment, battery, robot_state)
```

该阶段根据测量 profile 建立速度误差模型。本仓库不实现该阶段，只为该阶段提供数据接口。

## Stage 3: Velocity Compensation Layer

目标：

```text
v_x_cmd_compensated = f_inverse(v_x_desired, environment)
```

该阶段根据目标速度和环境 profile 计算补偿后的速度命令。本仓库不实现补偿逻辑。

## Stage 4: Safe Command Adapter

目标：

```text
desired_velocity -> checked_velocity -> compensated_command
```

该阶段负责命令安全检查、速度限制、环境匹配检查和补偿命令输出。

## Stage 5: Navigation Safety Integration

目标是降低导航中的 overshooting、undershooting、collision risk 和 poor trajectory tracking。

该阶段会把速度补偿和安全命令适配集成到导航系统中。
