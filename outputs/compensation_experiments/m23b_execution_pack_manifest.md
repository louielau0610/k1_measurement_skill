# M23-B K1 Physical Compensation Execution Pack Manifest

**Status**: `execution_pack_ready_not_run`
**Deployment ready**: `false`

## Pack Contents

### Scripts to Transfer to Robot

| Script | Purpose |
|--------|---------|
| `scripts/run_m23b_k1_compensation_trials.py` | Trial runner — dry-run/execute, auto-launches logger + SDK subprocesses |
| `scripts/log_m23b_k1_compensation_trial.py` | ROS2 state logger — subscribes to `/odometer_state`, `/low_state` |
| `scripts/send_m23b_k1_velocity_command.py` | Booster SDK command — `kPrepare` → `kWalking` → `Move(vx,0,0)` at 10 Hz |

### Input Trial Plan

`outputs/compensation_experiments/m23a_trial_plan.csv` — 36 trials (18 direct + 18 compensated), 18 pairs.

### Expected Robot-Side Output Layout

```
data/compensation_experiments/m23b_k1/<session_id>/
├── session_metadata.json
├── trial_records.csv
├── state_logs/
│   ├── M23A_S2_marble_floor_V030_dire_R1.csv
│   └── ...
├── extracted_results.csv
├── extraction_summary.json
├── extraction_report.md
└── qc_summary.json
```

## Commands

### Dry-Run (always first)

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

- ✅ Dry-run by default (no hardware movement without `--execute`)
- ✅ `--execute` required for motor movement
- ✅ Per-trial permit prompt (`[y/N]`) by default
- ✅ Split-process enforced (ROS2 logger ≠ SDK command process)
- ✅ Append-only trial records
- ✅ Invalid trials recorded with explicit reason
- ✅ Infeasible compensated targets skipped, not forced

## Claim Boundary

| Claim | Status |
|-------|--------|
| Execution pack created | ✅ M23-B |
| Physical trials executed | ❌ Requires robot operator |
| Tracking improvement analyzed | ❌ M23-C (future) |
| Compensation validated | ❌ Not claimed |
| Deployment ready | ❌ Not claimed |
| GO1/G1 included | ❌ Not included |

## Next Phase

**M23-C**: K1 compensation before/after analysis — load extracted results, compute paired error comparisons, run statistical tests, determine claim level.
## Hotfix2 Addendum

Hotfix2 synchronized orchestration:

- logger subprocess launches first;
- runner waits `--logger-startup-sec` (default `0.5`);
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

Claim boundary remains unchanged: no tracking improvement claim, no compensation validation claim, and `deployment_ready=false`.
