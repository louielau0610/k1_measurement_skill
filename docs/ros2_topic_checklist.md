# ROS2 Topic Checklist

本文档以中文优先记录 K1 测量阶段的 ROS2 topic discovery 流程。M4 只做只读发现和人工核对准备，不启动真实订阅，不发布命令，不移动机器人。

## 手动发现命令

ros2 topic list

ros2 topic info <topic_name>

ros2 topic echo <topic_name>

ros2 interface show <message_type>

## 候选 topic 类型

操作者应重点查找与以下关键词相关的 topic：

- odom
- imu
- low_state
- robot_state
- battery
- cmd
- velocity
- loco

关键词分类只提供候选建议，不代表 topic 已经验证。

## 记录表

| 用途 | 候选 topic | message type | 是否已验证 | 频率 | 备注 |
| --- | --- | --- | --- | --- | --- |
| odom | TBD | TBD | 否 | TBD | 必需，未验证前不能用于真实 logging |
| imu | TBD | TBD | 否 | TBD | 必需，未验证前不能用于真实 logging |
| robot_state | TBD | TBD | 否 | TBD | 必需，未验证前不能用于真实 logging |
| low_state | TBD | TBD | 否 | TBD | 可选 |
| battery | TBD | TBD | 否 | TBD | 可选 |
| command | TBD | TBD | 否 | TBD | 仅记录，不在 discovery 阶段发送 |
| velocity | TBD | TBD | 否 | TBD | 可选 |
| loco | TBD | TBD | 否 | TBD | 可选 |

## 安全警告

- 不要把关键词匹配猜测出的 topic 名称当成最终结论。
- 在 odom、imu 和 robot_state topic 手动验证前，不要启动真实 logging。
- discovery 过程中不要向 command topic 发送任何消息。
- topic discovery 是只读流程。
- 本仓库在 M4 阶段不实现 ROS2 publisher，也不实现真实机器人运动命令。
