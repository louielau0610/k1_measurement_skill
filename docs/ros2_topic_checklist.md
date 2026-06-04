# ROS2 Topic Checklist

本文档以中文优先记录 K1 测量阶段的 ROS2 topic discovery 流程。

## 基础命令

```bash
ros2 topic list
ros2 topic info <topic_name>
ros2 topic echo <topic_name>
ros2 interface show <message_type>
```

## 检查项目

- 确认 odom topic 名称和 message type
- 确认 imu topic 名称和 message type
- 确认 battery topic 名称和 message type
- 确认 robot state 或 low state topic 名称和 message type
- 确认 command topic 名称、message type 和安全限制
- 在确认 command interface 前，所有运动命令代码必须保持 dry-run
