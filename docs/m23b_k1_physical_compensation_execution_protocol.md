# M23-B K1 Physical Compensation Execution Protocol

**Status**: Execution pack only. No physical results are claimed by this repository.  
**Physical validation**: `execution_pack_ready_not_run`  
**Deployment ready**: `false`

## M23-B Hotfix History

The original M23-B runner only printed SDK command instructions, so early runs could record trials as executed even when the robot did not move. The hotfix runner launches the SDK command subprocess and marks a trial executed only if both the logger and SDK subprocesses return `0`.

Invalid/debug sessions:

- `m23b_k1_s2_20260612_095811`
- failed auto-subprocess sessions before hotfix2
- `m23b_k1_s2_sync3_20260612_104753`

Do not use invalid/debug sessions for M23-C analysis.

## M23-A Trial Plan Hotfix

The pre-hotfix M23-A trial plan populated direct-baseline commands but left all compensated `command_velocity_mps` cells blank. Session `m23b_k1_s2_sync3_20260612_104753` is therefore direct-baseline-only/debug, not a complete before/after compensation experiment.

Formal M23-B before/after execution must use:

```text
outputs/compensation_experiments/m23a_executable_trial_plan.csv
```

The executable plan contains only complete direct/compensated pairs whose compensated command comes from the M22-C offline compensator and whose `compensator_status` is `ok` or `feasible_but_risky`. Infeasible compensated targets remain documented in the full traceability plan but are excluded from paired comparison.

## Preflight Checklist

Before moving the robot, verify:

- [ ] Booster K1 is charged above 50 percent.
- [ ] Surface `S2_marble_floor` is clear of obstacles.
- [ ] ROS2 environment is sourced: `source /opt/booster/BoosterRos2Interface/install/setup.bash`.
- [ ] `/odometer_state` publishes at expected frequency.
- [ ] Executable trial plan CSV is on the robot: `outputs/compensation_experiments/m23a_executable_trial_plan.csv`.
- [ ] Execution scripts are on the robot.
- [ ] Operator understands per-trial permit workflow.
- [ ] Stop procedure is understood.

## Environment Setup

On the Booster K1 robot shell:

```bash
source /opt/booster/BoosterRos2Interface/install/setup.bash
ros2 topic echo /odometer_state --once
cd ~/k1_measurement_skill
```

## Robot-Side Transfer

See `docs/m23b_robot_transfer_and_run_commands.md` for exact `scp` commands.

Scripts and artifacts to transfer:

- `scripts/run_m23b_k1_compensation_trials.py`
- `scripts/log_m23b_k1_compensation_trial.py`
- `scripts/send_m23b_k1_velocity_command.py`
- `outputs/compensation_experiments/m23a_executable_trial_plan.csv`

## Trial Execution Procedure

### Dry-Run

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_dry_check
```

Verify the executable direct/compensated pairs appear and no compensated command is blank.

### Execute

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute
```

The runner automatically launches both subprocesses per trial:

1. ROS2 logger subprocess: `log_m23b_k1_compensation_trial.py`.
2. SDK command subprocess: `send_m23b_k1_velocity_command.py`.

The runner launches the logger first, waits `--logger-startup-sec`, then launches the SDK command while the logger is still running. A trial is marked executed only if both subprocesses return `0`.

## SDK Environment Options

If SDK imports fail in the automatic subprocess, run the SDK script with the same Python interpreter that succeeded in the manual smoke test, or pass that interpreter with `--sdk-python`.

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute \
  --sdk-python /path/to/python-that-imports-sdk
```

If shell setup is needed:

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute \
  --sdk-python python3 \
  --sdk-env-setup "source /some/sdk/setup.bash"
```

## Per-Trial Permit Behavior

- Default: each trial requires `y` confirmation.
- To disable permits: `--no-permit`.
- Skipped trials are recorded with `invalid_reason = "operator_skipped"`.

## Split-Process Architecture

The SDK command process and ROS2 logger process must not share the same Python runtime. The runner orchestrates subprocesses only; it does not import `rclpy` or Booster SDK APIs.

## Stop Procedure

1. If a trial produces unexpected robot behavior, abort immediately.
2. Record the trial as invalid with `invalid_reason = "operator_aborted"`.
3. If two consecutive trials are invalid, pause and diagnose.
4. If yaw drift exceeds 15 degrees in three consecutive compensated trials, stop and reassess.
5. If battery drops below 20 percent, pause and recharge.

## Invalid Trial Rules

A trial is invalid if:

- operator skips the permit prompt;
- operator aborts during execution;
- robot collides or slips;
- state log is missing or corrupted;
- ROS2 odometer data is unavailable;
- a compensator target is infeasible and excluded.

All invalid trials are recorded with explicit `invalid_reason` in `trial_records.csv`.

## Post-Run Extraction

```bash
python scripts/extract_m23b_k1_compensation_trials.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

## Post-Run QC

```bash
python scripts/qc_m23b_k1_compensation_session.py \
  --session-dir data/compensation_experiments/m23b_k1/m23b_s2_marble_run1/
```

QC checks session metadata, trial records, state logs, direct/compensated pair completeness, command/measurement separation, and explicit invalid reasons.

## Claim Boundary

| Claim | Status |
|-------|--------|
| Execution pack created | M23-B |
| Physical trials executed | Requires robot operator |
| Tracking improvement analyzed | M23-C future |
| Compensation validated | Not claimed |
| Deployment ready | Not claimed |
| GO1/G1 validation | Not claimed |

Hotfix2 and the executable-plan hotfix do not claim tracking improvement, physical validation, or deployment readiness.
