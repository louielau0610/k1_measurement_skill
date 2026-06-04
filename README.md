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

本仓库只实现其中的 **速度测量模块（Measurement Skill）**。

## 当前仓库范围

当前版本：**K1 Forward Velocity Tracking Measurement Skill v0**

v0 范围：

- 只测前进速度
- 不测转向
- 不测横向移动
- 不做自主导航
- 不做实时补偿
- 使用人工环境标签
- 先完成 ROS2 topic discovery 和 logging skeleton
- 后续支持外部 ground truth 校验

## 核心研究问题

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

```yaml
floor_type: tile | concrete | wood | carpet | rubber | unknown
condition: dry | wet | dusty | uneven | unknown
slope: flat | mild_uphill | mild_downhill | unknown
```

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

下游模块使用 profile 前必须检查 `schema_version`、环境匹配、有效速度范围、置信度、样本数量、ground truth 方法、odom 是否验证、是否允许外推和 warnings。

本仓库不实现速度补偿，也不提供 `compensate_velocity()`。补偿逻辑属于未来下游项目范围。

## 核心测量指标（Core Measurement Metrics）

M2 实现纯测量指标计算层。这些指标只描述实验观测结果，不执行速度补偿，也不生成机器人运动命令。后续 profile builder 会把这些指标聚合进 `processed_environment_profile.json`。

```text
v_x_actual = (x_end - x_start) / (t_end - t_start)
speed_gain = v_x_actual / v_x_cmd
e_abs = v_x_actual - v_x_cmd
e_rel = (v_x_actual - v_x_cmd) / v_x_cmd
lateral_drift_rate = |y_end - y_start| / (t_end - t_start)
yaw_drift_rate = |yaw_end - yaw_start| / (t_end - t_start)
RMSE = sqrt(mean((v_actual_i - v_cmd)^2))
```

## M3 Dummy Data Pipeline

M3 建立 dummy 数据流水线，用于在连接真实 K1 ROS2 topic 之前验证仓库内部数据流程。

dummy raw log 不是真实机器人数据。由 dummy raw log 生成的 dummy profile 不能用于速度补偿、导航或任何真实机器人决策。

默认流程：

```powershell
py scripts/generate_dummy_raw_log.py
py scripts/process_trial_logs.py
py scripts/validate_profile_schema.py data/processed/dummy_processed_environment_profile.json
py -m pytest
```

## M4 ROS2 Topic Discovery and Logger Skeleton

M4 为未来真实 K1 集成做准备，但仍然保持安全、只读和非侵入。

`scripts/discover_ros2_topics.py` 只检测 `ros2` 命令是否存在，并在可用时运行只读命令 `ros2 topic list`。它只根据关键词对 topic 名称做候选分类，不代表人工验证完成。

真实 logging 至少需要人工验证 odom、imu 和 robot_state topic，并更新 `config/topic_mapping_template.yaml`。默认模板状态是 incomplete，logger skeleton 会拒绝不完整 mapping。

本里程碑不发布 ROS2 command，不启动真实 ROS2 subscription，不移动机器人，也不实现速度补偿。

使用命令：

```powershell
py scripts/discover_ros2_topics.py
py scripts/discover_ros2_topics.py --save config/discovered_topics.yaml
py -m pytest
py -m compileall k1_measurement scripts
```

如果开发环境没有安装 ROS2，discovery 脚本会安全退出并返回 0。这在普通开发环境中是可以接受的。

## M5 Dry-run Forward Baseline Trial Manager

M5 生成并验证前进速度 baseline 实验计划，用于在真实 K1 测试之前检查实验调度和安全限制。

该阶段只运行 dry-run：

- 不发布 ROS2 command
- 不移动机器人
- 不使用真实 K1 command topic
- 不启动真实 ROS2 subscription
- 不实现速度补偿

真实执行在当前仓库中仍然被禁用，直到未来里程碑中 K1 command interface 被人工验证。

使用命令：

```powershell
py scripts/run_forward_baseline.py --dry-run
py scripts/run_forward_baseline.py --print-only
py -m pytest
py -m compileall k1_measurement scripts
```

在部分 Windows 环境中，`py` 可用于替代不可用的 `python` launcher。

## 计划输出文件

- `raw_measurement_log.csv`
- `processed_environment_profile.json`
- `velocity_error_plot.png`
- `measurement_report.md`

其中 `processed_environment_profile.json` 是最重要的下游接口文件。

## 使用方式

在 Windows 环境中，如果 `python` launcher 不可用，可以使用 `py`：

```powershell
py scripts/validate_profile_schema.py
py -m pytest
py -m compileall k1_measurement scripts
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
