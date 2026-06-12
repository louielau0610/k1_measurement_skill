# M24-B Robot Transfer And Run Commands

M24-B prepares a direct-only Booster K1 `S2_marble_floor` profile refresh session. It does not run hardware inside the repository, does not update `k1_gold_profile_v1`, and does not claim compensation improvement.

Use a session ID like:

```bash
SESSION_ID=m24b_s2_profile_refresh_$(date +%Y%m%d_%H%M%S)
```

Naming convention: `m24b_s2_profile_refresh_YYYYMMDD_HHMMSS`

## Copy Files To K1

From Windows or the workstation:

```bash
scp outputs/compensation_experiments/m24a_s2_profile_refresh_plan.csv robot@K1_HOST:~/k1_measurement_skill/outputs/compensation_experiments/
scp scripts/run_m24b_s2_profile_refresh_trials.py robot@K1_HOST:~/k1_measurement_skill/scripts/
scp scripts/log_m24b_s2_profile_refresh_trial.py robot@K1_HOST:~/k1_measurement_skill/scripts/
scp scripts/send_m23b_k1_velocity_command.py robot@K1_HOST:~/k1_measurement_skill/scripts/
scp scripts/extract_m24b_s2_profile_refresh_trials.py robot@K1_HOST:~/k1_measurement_skill/scripts/
scp scripts/qc_m24b_s2_profile_refresh_session.py robot@K1_HOST:~/k1_measurement_skill/scripts/
```

## Source Robot Environment

On K1:

```bash
cd ~/k1_measurement_skill
source /opt/ros/humble/setup.bash
source /opt/booster/BoosterRos2Interface/install/setup.bash
```

Use the SDK Python interpreter that can import the Booster SDK. Confirm it before running:

```bash
python3 -c "import sys; print(sys.executable)"
python3 -c "import booster_robotics_sdk_python"
```

## Dry Run

```bash
python3 scripts/run_m24b_s2_profile_refresh_trials.py \
  --trial-plan outputs/compensation_experiments/m24a_s2_profile_refresh_plan.csv \
  --surface S2_marble_floor \
  --interface eth0 \
  --session-id "$SESSION_ID"
```

## Execute The 30-Trial Refresh

Hardware movement requires `--execute`. The default per-trial permit prompt stays enabled.

```bash
python3 scripts/run_m24b_s2_profile_refresh_trials.py \
  --trial-plan outputs/compensation_experiments/m24a_s2_profile_refresh_plan.csv \
  --surface S2_marble_floor \
  --interface eth0 \
  --session-id "$SESSION_ID" \
  --sdk-python python3 \
  --logger-startup-sec 0.5 \
  --execute
```

Expected session directory:

```bash
data/compensation_experiments/m24b_s2_profile_refresh/$SESSION_ID/
```

## Extract

```bash
python3 scripts/extract_m24b_s2_profile_refresh_trials.py \
  --session-dir "data/compensation_experiments/m24b_s2_profile_refresh/$SESSION_ID"
```

## QC

```bash
python3 scripts/qc_m24b_s2_profile_refresh_session.py \
  --session-dir "data/compensation_experiments/m24b_s2_profile_refresh/$SESSION_ID"
```

## Package And Copy Results Back

```bash
tar -czf "$SESSION_ID.tar.gz" \
  "data/compensation_experiments/m24b_s2_profile_refresh/$SESSION_ID"
scp "$SESSION_ID.tar.gz" USER@WINDOWS_HOST:/mnt/c/Users/86138/Desktop/
```

The package should contain `session_metadata.json`, `trial_records.csv`, `state_logs/`, `extracted_results.csv`, `extraction_summary.json`, `extraction_report.md`, `qc_summary.json`, and `qc_report.md`.

## Boundary

Do not run compensated commands in M24-B. Do not overwrite `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`. Do not claim deployment readiness or GO1/G1 validation from this direct-refresh session.
