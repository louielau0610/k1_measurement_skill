# Safety Protocol

本文档以中文优先定义 K1 测量阶段安全要求。

## 实验前检查

- 机器人必须位于安全开阔区域
- 急停装置必须可用
- 必须有人监督实验过程
- 必须先从低速开始
- 必须先执行 dry-run
- ROS2 topic 必须已验证
- command interface 必须已验证

## 命令安全

任何可能发送运动命令的代码必须包含：

- 人工确认
- 速度上限检查
- 急停提醒
- 默认 dry-run

## 禁止事项

- 禁止在 topic 未验证时发送真实运动命令
- 禁止把占位 topic 当成最终 topic
- 禁止在本仓库实现速度补偿或导航闭环控制
- M4 topic discovery 必须保持只读，不得发布消息
- logger skeleton 在 topic mapping 不完整时必须拒绝真实 logging
- M5 dry-run 必须先通过，才能考虑未来真实执行
- M5 阶段真实 command execution 在本仓库中仍然禁用
- 未来真实执行必须要求 manual confirmation
- 未来真实执行必须确认 emergency stop ready
- 任何真实 command 之前必须验证 command topic
- 必须检查 `vx`、`vy`、`wz` 限制
- 当前 v0 禁止 lateral motion 和 turning
