# TODO

## M0 Repository Initialization

- [x] 创建项目目录结构
- [x] 初始化 Git 仓库
- [x] 创建中文优先 README
- [x] 创建英文参考 README
- [x] 创建 ROADMAP、PROJECT_STATUS、AGENTS
- [x] 创建基础 Python package 和测试入口

## M1 Interface Contracts

- [x] 明确 `processed_environment_profile.json` schema
- [x] 明确 raw log 字段定义
- [x] 增加 schema validation
- [x] 增加 profile 版本字段
- [x] 写清下游模块的置信度和外推风险检查要求
- [x] 创建 dummy profile 示例
- [x] 增加 schema validation 单元测试
- [x] 更新 README、PROJECT_STATUS 和 TODO

## M2 Metrics Core

- [x] implement velocity measurement metrics
- [x] test actual velocity calculation
- [x] test speed gain
- [x] test absolute and relative error
- [x] test lateral drift rate
- [x] test yaw drift rate
- [x] test tracking RMSE
- [x] test trial summary aggregation

## M3 Dummy Data Pipeline

- [x] generate dummy raw measurement log
- [x] process dummy raw log into dummy processed environment profile
- [x] validate generated profile against JSON schema
- [x] use `metrics.py` functions in `profile_builder.py`
- [x] add tests for profile builder
- [x] keep dummy data clearly separated from real robot data

## M4 ROS2 Topic Discovery and Logger Skeleton

- [x] discover available ROS2 topics
- [x] classify candidate odom, imu, robot_state, battery, command topics
- [x] create topic mapping template
- [x] keep logger in dry-run or skeleton mode
- [x] refuse to start real logging if topic mapping is incomplete
- [x] do not implement real robot movement commands

## M5 Dry-run Forward Baseline Trial Manager

- [x] generate full trial plan from `config/experiment_forward_v0.yaml`
- [x] dry-run baseline execution
- [x] command_runner stays dry-run by default
- [x] safety checks for vx, vy, wz
- [x] reject real execution until command interface is verified
- [x] add tests for trial manager and command runner

## M6 Measurement Report Generator

- [ ] generate report from dummy processed profile
- [ ] summarize velocity profile
- [ ] summarize confidence and limitations
- [ ] include downstream usage notes
- [ ] warn that dummy data is not real robot data
- [ ] add tests for report generator

## M7 Measurement Report

- [ ] 汇总实验配置
- [ ] 汇总环境标签
- [ ] 汇总速度误差统计
- [ ] 输出图表
- [ ] 明确 profile 置信度和适用范围
