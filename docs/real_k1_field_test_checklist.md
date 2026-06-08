# Real K1 Field-Test Checklist

## M8 Concrete Commands

### Step A: create session

```powershell
py scripts/create_real_k1_field_session.py --session-id 20260609_k1_forward_baseline --output-root data/real_k1_sessions
```

### Step B: run topic discovery

```powershell
py scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

### Step C: fill topic_mapping.yaml

Edit:

```text
data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

### Step D: validate mapping

```powershell
py scripts/validate_real_k1_topic_mapping.py --mapping data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

### Step E: run static logger

```powershell
py scripts/start_real_k1_field_logger.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline --duration-sec 30
```

### Step F: inspect logs

Review `logger_run_summary.json` and files under `raw_ros/`.

### Step G: run smoke trial

Run one manually supervised forward trial only after mapping and static logs are checked.

### Step H: run full baseline

```text
0.1 m/s x 3
0.2 m/s x 3
0.3 m/s x 3
0.4 m/s x 3
```

### Step I: normalize logs

```powershell
py scripts/normalize_real_k1_logs.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline
```

### Step J: generate report and plots

Use the normalized CSV and processed profile workflow to create the first real measurement report and static plots.

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

M7 discovery tools 和 M8 field logger 不发布运动命令，不自动 sample 全部 topic，不确认任何真实 topic 名称。候选分类只是关键词辅助，最终 topic mapping 必须由现场人工确认。
