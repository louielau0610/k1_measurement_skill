# K1 速度测量 Skill

## 项目定位

本仓库 `k1_measurement_skill` 是完整项目 **K1 Velocity Measurement, Compensation and Navigation Safety Pipeline** 的第一阶段前置测量模块。

完整项目要解决的问题是：对 Booster Robotics K1 来说，速度命令 `v_cmd` 与机器人实际执行速度 `v_actual` 可能并不一致。在导航任务中，这种误差会持续累积，导致位置误差、轨迹漂移，甚至增加碰撞风险。

本仓库当前只负责测量阶段：建立前进速度命令 `v_x_cmd` 与实际前进速度 `v_x_actual` 之间的关系。它不实现速度补偿、不实现自主导航、不实现实时闭环控制，也不直接下发未经验证的真实机器人运动命令。

## 大项目整体设计

完整项目流水线如下：

```text
速度命令（Velocity Command）
    ->
速度测量模块（Measurement Skill）
    ->
环境相关速度画像（Environment-specific Velocity Profile）
    ->
速度误差模型（Velocity Error Model）
    ->
速度命令补偿层（Velocity Command Compensation Layer）
    ->
导航安全层（Navigation Safety Layer）
```

本仓库只实现其中的 **速度测量模块（Measurement Skill）**。本阶段的输出会为后续速度误差建模、速度命令补偿、安全命令适配和导航安全验证提供基础数据。

## 当前仓库范围

当前版本：

**K1 Forward Velocity Tracking Measurement Skill v0**

v0 范围：

- 只测前进速度
- 不测转向
- 不测横向移动
- 不做自主导航
- 不做实时补偿
- 使用人工环境标签
- 先完成 ROS2 topic discovery 和 logging
- 后续支持外部 ground truth 校验

## 核心研究问题

给定：

```text
v_x_cmd
```

测量：

```text
v_x_actual
```

当前映射关系：

```text
v_x_cmd -> v_x_actual
```

未来下游补偿模块可能使用：

```text
v_x_desired -> v_x_cmd_compensated
```

但本仓库必须保持测量职责边界，不能实现速度补偿逻辑。

## 第一版实验变量

第一版前进速度命令集合：

```text
v_x_cmd ∈ {0.1, 0.2, 0.3, 0.4} m/s
```

每个速度应在相同环境条件下重复多次实验，以获得均值、方差、置信度和样本数量等统计信息。

## 环境标签

实验数据必须带有人工标注的环境标签：

```yaml
floor_type: tile | concrete | wood | carpet | rubber | unknown
condition: dry | wet | dusty | uneven | unknown
slope: flat | mild_uphill | mild_downhill | unknown
```

这些标签会被写入测量 profile，供下游模块判断环境是否匹配。

## 数据接口契约（Data Interface Contract）

`processed_environment_profile.json` 是本仓库最重要的下游数据契约。它把当前测量 skill 与未来的速度补偿、命令安全适配、导航安全和仿真验证模块连接起来。

M1 已定义严格 JSON Schema：

```text
contracts/measurement_profile_schema.json
```

示例 dummy profile：

```text
examples/dummy_processed_environment_profile.json
```

下游模块使用 profile 前必须检查：

- `schema_version`
- `environment` 是否匹配当前部署环境
- `valid_speed_range` 是否覆盖目标速度
- `quality.confidence`
- `velocity_profile[].n_trials`
- `quality.ground_truth_method`
- `quality.odom_validated`
- `downstream_usage.extrapolation_allowed`
- `quality.warnings`

下游模块不能默认认为 profile 是高置信度，也不能在速度超出有效范围、环境不匹配、样本量不足或存在安全关键 warning 时盲目使用。

本仓库不实现速度补偿，也不提供 `compensate_velocity()`。补偿逻辑属于未来下游项目范围。

## 计划输出文件

计划生成的关键文件包括：

- `raw_measurement_log.csv`
- `processed_environment_profile.json`
- `velocity_error_plot.png`
- `measurement_report.md`

其中 `processed_environment_profile.json` 是最重要的下游接口文件。

## 与后续项目的接口

本仓库面向后续项目的核心接口是：

```text
processed_environment_profile.json
```

该文件会被以下下游模块消费：

- velocity compensation model
- safe command adapter
- navigation safety layer
- simulation validation pipeline

下游模块使用 profile 前必须检查 confidence、valid speed range、environment match、sample size 和 extrapolation risk。

## 使用方式

在 Windows 环境中，如果 `python` launcher 不可用，可以使用 `py`：

```powershell
py scripts/validate_profile_schema.py
py -m pytest
py -m compileall k1_measurement scripts
```

如果当前 shell 中 `python` 可用，也可以运行：

```powershell
python scripts/validate_profile_schema.py
python -m pytest
python -m compileall k1_measurement scripts
```

## 安全声明

本仓库在以下条件全部满足之前，必须不得向 K1 发送真实运动命令：

- 机器人处于安全开阔区域
- 急停装置可用
- 机器人处于正确运动模式
- ROS2 topic 名称已确认
- command interface 已确认
- 有人工监督实验过程

任何可能发送运动命令的文件必须默认 dry-run，并包含人工确认、速度限制检查和急停提醒。

## 当前开发状态

当前状态见 [PROJECT_STATUS.md](PROJECT_STATUS.md)。
