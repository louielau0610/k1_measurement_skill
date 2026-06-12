# M24-H Controlled S2 Replication Execution Pack Manifest

**Physical run status**: `not_run`
**Profile adoption**: `not_adopted`
**Deployment ready**: `false`
**GO1/G1 blocked**: `true`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_m24h_controlled_s2_replication_trials.py` | Controlled runner — strict S2/direct only, auto subprocesses |
| `scripts/extract_m24h_controlled_s2_replication_trials.py` | Corrected extractor — command-phase window with trim |
| `scripts/qc_m24h_controlled_s2_replication_session.py` | QC — 20 trials, 4 groups × 5 repeats, no compensated |
| `scripts/log_m23b_k1_compensation_trial.py` | Reused ROS2 state logger |
| `scripts/send_m23b_k1_velocity_command.py` | Reused Booster SDK command sender |

## Input Plan

`outputs/compensation_experiments/m24g_controlled_s2_replication_plan.csv` — 20 trials: 4 velocities × 5 repeats.

## Metadata Template

`outputs/compensation_experiments/m24h_controlled_metadata_template.json` — copy to robot, fill before/between trials.

## Expected Session Layout

```
data/compensation_experiments/m24h_controlled_s2_replication/<session_id>/
├── session_metadata.json
├── trial_records.csv
├── controlled_metadata.json
├── state_logs/
│   ├── M24G_CORE_S2_marble_floor_V040_R1.csv
│   └── ...
├── corrected_extracted_results.csv
├── corrected_extraction_summary.json
├── corrected_extraction_report.md
├── qc_summary.json
└── qc_report.md
```

## Constraints

- Surface: `S2_marble_floor` only
- Condition: `direct_refresh_controlled` only
- Velocities: 0.40, 0.45, 0.50, 0.55
- Repeats: 5 per velocity = 20 trials
- Compensated commands: FORBIDDEN
- Extraction: corrected command-phase window with 1s trim

## Claim Boundary

- Physical trials executed: ❌
- Tracking improvement claimed: ❌
- Profile adopted: ❌
- Deployment ready: ❌
- GO1/G1 included: ❌
