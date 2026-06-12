# M24-B S2 Profile Refresh Execution Pack Manifest

Status: `execution_pack_ready`

- Surface: `S2_marble_floor`
- Condition: `direct_refresh`
- Expected trials: 30
- Velocity groups: 6
- Repeats per velocity: 5
- Physical run status: `not_run`
- Profile update status: `not_updated`
- Deployment ready: `false`
- GO1/G1 blocked: `true`

## Included Scripts

- `scripts/run_m24b_s2_profile_refresh_trials.py`
- `scripts/log_m24b_s2_profile_refresh_trial.py`
- `scripts/send_m23b_k1_velocity_command.py`
- `scripts/extract_m24b_s2_profile_refresh_trials.py`
- `scripts/qc_m24b_s2_profile_refresh_session.py`

## Expected Input

- `outputs/compensation_experiments/m24a_s2_profile_refresh_plan.csv`

## Expected Session Layout

```text
data/compensation_experiments/m24b_s2_profile_refresh/<session_id>/
  session_metadata.json
  trial_records.csv
  run_summary.json
  state_logs/
    <trial_id>.csv
    <trial_id>_cmd_log.json
  extracted_results.csv
  extraction_summary.json
  extraction_report.md
  qc_summary.json
  qc_report.md
```

## Boundary

This pack does not execute hardware by itself, does not fabricate physical results, does not overwrite `k1_gold_profile_v1`, does not claim compensation improvement, does not claim deployment readiness, and does not start GO1/G1 work.
