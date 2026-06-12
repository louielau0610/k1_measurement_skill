# M23-B K1 Physical Compensation Execution Pack Manifest

**Status**: `execution_pack_ready_not_run`  
**Deployment ready**: `false`

## Pack Contents

### Scripts To Transfer To Robot

| Script | Purpose |
|--------|---------|
| `scripts/run_m23b_k1_compensation_trials.py` | Trial runner, dry-run/execute, auto-launches logger + SDK subprocesses |
| `scripts/log_m23b_k1_compensation_trial.py` | ROS2 state logger, subscribes to `/odometer_state` and `/low_state` |
| `scripts/send_m23b_k1_velocity_command.py` | Booster SDK command, `kPrepare` to `kWalking` to `Move(vx,0,0)` at 10 Hz |

### Input Trial Plan

Formal execution input: `outputs/compensation_experiments/m23a_executable_trial_plan.csv` - executable direct/compensated pairs only.

Traceability input: `outputs/compensation_experiments/m23a_trial_plan.csv` - includes infeasible compensated rows that must not be run as paired before/after trials.

M23-A hotfix note: the pre-hotfix plan had blank compensated `command_velocity_mps` values. Session `m23b_k1_s2_sync3_20260612_104753` is direct-baseline-only/debug and must not be used for M23-C before/after analysis.

### Expected Robot-Side Output Layout

```text
data/compensation_experiments/m23b_k1/<session_id>/
  session_metadata.json
  trial_records.csv
  state_logs/
  extracted_results.csv
  extraction_summary.json
  extraction_report.md
  qc_summary.json
```

## Commands

### Dry-Run

```bash
python scripts/run_m23b_k1_compensation_trials.py --surface S2_marble_floor
```

### Execute

```bash
python scripts/run_m23b_k1_compensation_trials.py \
  --surface S2_marble_floor \
  --session-id m23b_s2_marble_run1 \
  --execute
```

### Extract

```bash
python scripts/extract_m23b_k1_compensation_trials.py \
  --session-dir data/compensation_experiments/m23b_k1/<session_id>/
```

### QC

```bash
python scripts/qc_m23b_k1_compensation_session.py \
  --session-dir data/compensation_experiments/m23b_k1/<session_id>/
```

## Safety Features

- Dry-run by default, no hardware movement without `--execute`.
- `--execute` required for motor movement.
- Per-trial permit prompt (`[y/N]`) by default.
- Split-process enforced: ROS2 logger and SDK command process are separate.
- Append-only trial records.
- Invalid trials recorded with explicit reason.
- Infeasible compensated targets excluded from the executable plan, not forced.

## Hotfix2 Addendum

Hotfix2 synchronized orchestration:

- logger subprocess launches first;
- runner waits `--logger-startup-sec`, default `0.5`;
- SDK command subprocess launches while logger is still running;
- both return codes are recorded;
- trial is executed only if logger and SDK both return `0`.

SDK environment options:

- `--sdk-python`
- `--sdk-env-setup`
- `--command-timeout-sec`
- `--logger-timeout-sec`

Invalid/debug sessions:

- `m23b_k1_s2_20260612_095811`
- failed auto-subprocess sessions before hotfix2
- `m23b_k1_s2_sync3_20260612_104753`

## Claim Boundary

| Claim | Status |
|-------|--------|
| Execution pack created | M23-B |
| Physical trials executed | Requires robot operator |
| Tracking improvement analyzed | M23-C future |
| Compensation validated | Not claimed |
| Deployment ready | Not claimed |
| GO1/G1 included | Not included |

Claim boundary remains unchanged: no tracking improvement claim, no compensation validation claim, and `deployment_ready=false`.

## Next Phase

**M23-C**: K1 compensation before/after analysis after executable-pair physical data pass extraction and QC.
