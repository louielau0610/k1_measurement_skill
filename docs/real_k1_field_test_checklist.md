# Real K1 Field-Test Checklist

## 明天执行顺序

1. Connect to K1.
2. Enter ROS2-enabled shell.
3. Run ROS2 availability check.
4. Run topic discovery.
5. Review candidate odom / IMU / battery / robot_state / command topics.
6. Fill `configs/real_k1_logger_template.yaml`.
7. Run static logging test.
8. Check timestamp, odom, IMU, robot mode, and battery fields.
9. Run one smoke forward trial.
10. Inspect raw log completeness.
11. Run full baseline:
    - 0.1 m/s x 3
    - 0.2 m/s x 3
    - 0.3 m/s x 3
    - 0.4 m/s x 3
12. Process raw logs.
13. Generate first real measurement report.
14. Review plots and speed_gain summary.

## 现场记录

- topic mapping 必须人工确认后再写入 config。
- ground truth distance 和 elapsed time 必须逐 trial 记录。
- floor_type、condition、slope 使用人工环境标签。
- raw log 必须包含 trial_id、timestamp、command、odom、IMU、battery、robot mode 相关字段。
- dummy report 不能当作真实 K1 发现。

## M7 只读边界

M7 discovery tools 不发布运动命令，不自动 sample 全部 topic，不确认任何真实 topic 名称。候选分类只是关键词辅助，最终 topic mapping 必须由现场人工确认。
