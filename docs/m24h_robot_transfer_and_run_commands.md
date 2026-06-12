# M24-H Robot Transfer and Run Commands

**Status**: Transfer instructions. No physical results included.

Replace `<K1_IP>` with the robot's IP address.

## 1. Transfer Files to Robot

```powershell
$K1_IP = "<K1_IP>"
ssh robot@$K1_IP "mkdir -p ~/k1_measurement_skill/scripts ~/k1_measurement_skill/outputs/compensation_experiments"

scp scripts/run_m24h_controlled_s2_replication_trials.py robot@${K1_IP}:~/k1_measurement_skill/scripts/
scp scripts/extract_m24h_controlled_s2_replication_trials.py robot@${K1_IP}:~/k1_measurement_skill/scripts/
scp scripts/qc_m24h_controlled_s2_replication_session.py robot@${K1_IP}:~/k1_measurement_skill/scripts/
scp scripts/log_m23b_k1_compensation_trial.py robot@${K1_IP}:~/k1_measurement_skill/scripts/
scp scripts/send_m23b_k1_velocity_command.py robot@${K1_IP}:~/k1_measurement_skill/scripts/
scp outputs/compensation_experiments/m24g_controlled_s2_replication_plan.csv robot@${K1_IP}:~/k1_measurement_skill/outputs/compensation_experiments/
scp outputs/compensation_experiments/m24h_controlled_metadata_template.json robot@${K1_IP}:~/k1_measurement_skill/outputs/compensation_experiments/
```

## 2. On Robot: Source Environment

```bash
ssh robot@<K1_IP>
cd ~/k1_measurement_skill
source /opt/booster/BoosterRos2Interface/install/setup.bash
```

## 3. Edit Metadata

```bash
nano outputs/compensation_experiments/m24h_controlled_metadata_template.json
# Fill: robot_id, warmup_status, start_pose_label, path_label, battery_level_start
```

## 4. Dry-Run

```bash
python scripts/run_m24h_controlled_s2_replication_trials.py
```

## 5. Execute

```bash
python scripts/run_m24h_controlled_s2_replication_trials.py \
  --execute \
  --session-id m24h_controlled_s2_replication_YYYYMMDD_HHMMSS \
  --metadata-file outputs/compensation_experiments/m24h_controlled_metadata_template.json
```

Use actual date/time for session ID.

## 6. Post-Run Extraction (Corrected)

```bash
python scripts/extract_m24h_controlled_s2_replication_trials.py \
  --session-dir data/compensation_experiments/m24h_controlled_s2_replication/<session_id>/
```

## 7. QC

```bash
python scripts/qc_m24h_controlled_s2_replication_session.py \
  --session-dir data/compensation_experiments/m24h_controlled_s2_replication/<session_id>/
```

## 8. Bring Results Back

```bash
# On robot
cd ~/k1_measurement_skill
tar -czf m24h_results.tar.gz data/compensation_experiments/m24h_controlled_s2_replication/<session_id>/

# From Windows
scp robot@${K1_IP}:~/k1_measurement_skill/m24h_results.tar.gz .
```

## Session Naming Convention

`m24h_controlled_s2_replication_YYYYMMDD_HHMMSS`
