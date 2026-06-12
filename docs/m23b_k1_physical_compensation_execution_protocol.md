# M23-B K1 Physical Compensation Execution Protocol

**Status**: Execution pack only. No physical results exist yet.
**Physical validation**: `execution_pack_ready_not_run`
**Deployment ready**: `false`

## Preflight Checklist

Before moving the robot, verify:

- [ ] Booster K1 is charged (>50% battery).
- [ ] Surface `S2_marble_floor` is clear of obstacles.
- [ ] ROS2 environment is sourced: `source /opt/booster/BoosterRos2Interface/install/setup.bash`
- [ ] `/odometer_state` topic publishes at expected frequency (confirm with `ros2 topic hz /odometer_state`).
- [ ] Trial plan CSV is on the robot: `outputs/compensation_experiments/m23a_trial_plan.csv`
- [ ] Execution scripts are on the robot (see transfer document).
- [ ] Operator understands per-trial permit workflow.
- [ ] Stop procedure is understood (see below).

## Environment Setup

On the Booster K1 robot shell:

```bash
# Source the Booster ROS2 environment
source /opt/booster/BoosterRos2Interface/install/setup.bash

# Verify odometer publishes
ros2 topic echo /odometer_state --once

# Navigate to the calibration workspace
cd ~/k1_measurement_skill
```

## Robot-Side Script Transfer

See `docs/m23b_robot_transfer_and_run_commands.md` for exact `scp` commands.

Scripts to transfer:
- `scripts/run_m23b_k1_compensation_trials.py` — trial runner
- `scripts/log_m23b_k1_compensation_trial.py` — ROS2 state logger
- `outputs/compensation_experiments/m23a_trial_plan.csv` — trial plan

## Trial Execution Procedure

### 1. Dry-Run (Always First)

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_dry_check
```

This prints the trial plan without moving hardware. Verify:
- All 36 trials appear.
- Direct and compensated conditions are correctly listed.
- Pair IDs match expectations.

### 2. Execute with Per-Trial Permit

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute
```

For each trial:
1. Runner prints trial info (ID, pair, condition, desired velocity, command velocity).
2. Runner prompts: `Execute this trial? [y/N]`
3. Operator types `y` to proceed.
4. **Start ROS2 logger** (separate terminal):
   ```bash
   python scripts/log_m23b_k1_compensation_trial.py \
     --trial-id M23A_S2_marble_floor_V040_dire_R1 \
     --pair-id M23A_S2_marble_floor_V040_P1 \
     --condition direct \
     --desired-velocity 0.40 \
     --command-velocity 0.40 \
     --output-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/state_logs/
   ```
5. **Send velocity command** via Booster SDK (separate terminal or script).
6. Wait for trial duration (idle 2s + command 6s + stop 2s = 10s).
7. Stop logger.
8. Runner records trial outcome in `trial_records.csv` (append-only).

### Per-Trial Permit Behavior

- Default: each trial requires `y` confirmation.
- To disable permits: `--no-permit` (use with extreme caution).
- Skipped trials are recorded with `invalid_reason = "operator_skipped"`.

## Split-Process Architecture

**CRITICAL**: The SDK command process and ROS2 logger process must never share the same Python runtime.

```
Terminal 1 (SDK Command)          Terminal 2 (ROS2 Logger)
─────────────────────────         ─────────────────────────
Booster SDK native                rclpy + subscription
kPrepare → kWalking               /odometer_state
Move(vx, 0, 0)                    /low_state
                                  → writes trial CSV
```

The runner script prompts the operator to start/stop each process. It does NOT directly call rclpy or SDK APIs.

## Stop Procedure

1. If a trial produces unexpected robot behavior, operator aborts immediately.
2. Record the trial as invalid with `invalid_reason = "operator_aborted"`.
3. If 2 consecutive trials are invalid, pause and diagnose.
4. If yaw drift exceeds 15° in 3+ consecutive compensated trials, stop and reassess compensation policy.
5. If battery drops below 20%, pause and recharge.
6. After completing all planned pairs, stop and proceed to extraction.

## Invalid Trial Rules

A trial is invalid if:
- Operator skips the permit prompt.
- Operator aborts during execution.
- Robot collides or slips.
- State log is missing or corrupted after the trial.
- ROS2 odometer data is unavailable.
- Compensator returns infeasible and operator chooses not to force.

All invalid trials are recorded with explicit `invalid_reason` in `trial_records.csv`.

## Battery Interruption Handling

- If battery < 20%: complete current trial, then pause.
- Record battery state in session metadata if possible.
- Resume from `--start-from-trial-id` with `--skip-existing` to avoid duplicating completed trials.
- Mark interrupted pairs in session notes.

## Post-Run Extraction

After all trials complete:

```bash
python scripts/extract_m23b_k1_compensation_trials.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

This produces:
- `extracted_results.csv` — per-trial extracted measurements
- `extraction_summary.json` — extraction batch summary
- `extraction_report.md` — human-readable report

## Post-Run QC

```bash
python scripts/qc_m23b_k1_compensation_session.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

This checks:
- Session metadata, trial records, state logs present
- Each pair has one direct + one compensated trial
- No command velocity copied as measured velocity
- Invalid trials have explicit reasons

## Claim Boundary

| Claim | Status |
|-------|--------|
| Execution pack created | ✅ M23-B |
| Physical trials executed | ❌ Not yet (requires robot operator) |
| Tracking improvement analyzed | ❌ M23-C (future) |
| Deployment ready | ❌ Not claimed |
| GO1/G1 validation | ❌ Not claimed |
