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

- [ ] implement velocity measurement metrics
- [ ] test actual velocity calculation
- [ ] test speed gain
- [ ] test absolute and relative error
- [ ] test lateral drift rate
- [ ] test yaw drift rate
- [ ] test tracking RMSE
- [ ] test trial summary aggregation

## M3 Dummy Data Pipeline

- [ ] 生成 dummy raw log
- [ ] 处理 dummy trial logs
- [ ] 输出 dummy `processed_environment_profile.json`
- [ ] 生成 dummy plot
- [ ] 生成 dummy measurement report

## M4 ROS2 Discovery

- [ ] 记录 `ros2 topic list`
- [ ] 检查候选 odom、imu、battery、robot state topic
- [ ] 记录 message type
- [ ] 验证 command topic 前保持 dry-run
- [ ] 更新 topic checklist

## M5 Logger Prototype

- [ ] 创建 ROS2 logger 节点原型
- [ ] 支持只订阅已验证 topic
- [ ] 写入 raw CSV
- [ ] 保留环境标签
- [ ] 不把 odom 默认当成 ground truth

## M6 Forward Baseline

- [ ] 在安全区域进行 dry-run
- [ ] 人工确认急停可用
- [ ] 低速开始
- [ ] 每个 `v_x_cmd` 重复多次
- [ ] 保存原始日志和实验记录

## M7 Measurement Report

- [ ] 汇总实验配置
- [ ] 汇总环境标签
- [ ] 汇总速度误差统计
- [ ] 输出图表
- [ ] 明确 profile 置信度和适用范围
