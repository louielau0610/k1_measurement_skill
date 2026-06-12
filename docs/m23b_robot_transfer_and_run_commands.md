# M23-B Robot Transfer and Run Commands

**Status**: Transfer instructions only. No physical results.

Use these commands to transfer the M23-B execution pack to the Booster K1 robot and run the experiment.

M23-A hotfix note: the pre-hotfix plan had blank compensated command values, so `m23b_k1_s2_sync3_20260612_104753` is direct-baseline-only/debug. Formal before/after runs must use `outputs/compensation_experiments/m23a_executable_trial_plan.csv`.

> Replace `<K1_IP>` with the robot's IP address and `<session_id>` with your session identifier.

## 1. Transfer Scripts to Robot

From your development machine (PowerShell):

```powershell
# Set robot IP
$K1_IP = "<K1_IP>"

# Create remote directory
ssh robot@$K1_IP "mkdir -p ~/k1_measurement_skill/scripts ~/k1_measurement_skill/outputs/compensation_experiments"

# Transfer runner script
scp scripts/run_m23b_k1_compensation_trials.py robot@${K1_IP}:~/k1_measurement_skill/scripts/

# Transfer logger script
scp scripts/log_m23b_k1_compensation_trial.py robot@${K1_IP}:~/k1_measurement_skill/scripts/

# Transfer SDK command script (M23-B hotfix)
scp scripts/send_m23b_k1_velocity_command.py robot@${K1_IP}:~/k1_measurement_skill/scripts/

# Transfer executable trial plan
scp outputs/compensation_experiments/m23a_executable_trial_plan.csv robot@${K1_IP}:~/k1_measurement_skill/outputs/compensation_experiments/
```

## 2. On the Robot: Source Environment

```bash
ssh robot@<K1_IP>
cd ~/k1_measurement_skill
source /opt/booster/BoosterRos2Interface/install/setup.bash
```

## 3. Dry-Run (Always First)

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_dry_check
```

Verify the executable direct/compensated pairs appear and no compensated command is blank.

## 4. Execute Trials

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute
```

For each trial, in a **separate terminal** (sourced ROS2 environment):

```bash
python scripts/log_m23b_k1_compensation_trial.py \
  --trial-id <TRIAL_ID> \
  --pair-id <PAIR_ID> \
  --condition <direct|compensated> \
  --desired-velocity <VALUE> \
  --command-velocity <VALUE> \
  --output-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/state_logs/
```

In a **third terminal** (Booster SDK), send the velocity command:

```bash
# Example: Booster SDK command path
# kPrepare → kWalking → Move(<command_velocity>, 0, 0)
```

## 5. Resume After Interruption

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute \
  --start-from-trial-id M23A_S2_marble_floor_V040_comp_R2 \
  --skip-existing
```

## 6. Post-Run Extraction

```bash
python scripts/extract_m23b_k1_compensation_trials.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

## 7. Post-Run QC

```bash
python scripts/qc_m23b_k1_compensation_session.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

## 8. Bring Results Back

```powershell
# From development machine (PowerShell)
$K1_IP = "<K1_IP>"
$SESSION = "m23b_s2_marble_run1"

scp -r robot@${K1_IP}:~/k1_measurement_skill/data/compensation_experiments/m23b_k1/${SESSION}/ data/compensation_experiments/m23b_k1/${SESSION}/
```

Or tar on the robot first:

```bash
# On robot
cd ~/k1_measurement_skill
tar -czf m23b_results.tar.gz data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/

# Then scp the tarball
```

## Claim Boundary

These are **execution instructions only**. No physical results are included in this pack. M23-C will analyze collected data after robot execution.
## Hotfix2 Notes

The runner now synchronizes subprocesses automatically:

1. logger first;
2. `--logger-startup-sec` delay, default `0.5`;
3. SDK command subprocess while logger is still running;
4. executed only if both subprocesses return `0`.

SDK environment overrides:

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute \
  --sdk-python /path/to/python-that-imports-sdk
```

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute \
  --sdk-python python3 \
  --sdk-env-setup "source /some/sdk/setup.bash"
```

Manual two-terminal testing confirmed the split-process architecture is valid, but these sessions remain invalid/debug and must not be used for M23-C:

- `m23b_k1_s2_20260612_095811`
- failed auto-subprocess sessions before hotfix2
