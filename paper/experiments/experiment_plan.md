# Experiment Plan

Use this file for planned experiments only. Do not record planned experiments as completed results.

M18 experiment skeleton:

- `paper/manuscript/sections/04_experiments_skeleton.md`
- Current evidence is limited to structural/software validation, sparse dataset evidence, model sanity checks, and risk-map readiness evaluation.
- Missing evidence includes real navigation outcome metrics, calibrated uncertainty, generalization metrics, and before/after advisory comparisons.

## Planned Experiments

| experiment_id | question | protocol | required_artifacts | status | notes |
| --- | --- | --- | --- | --- | --- |
| future_velocity_response_repeats_v1 | Which missing schema fields and uncertainty estimates are needed for stronger response models? | Repeat selected `vx_cmd_mps` values with documented localization, environment labels, and per-trial response metrics. | dataset schema v1 records, repeated trial logs, validation report | planned | Populate missing fields such as lateral drift, response delay, stop distance, and repeated-trial variance; do not record planned values as results. |
| future_uncertainty_calibration_v1 | How much repeated numeric evidence is required to calibrate uncertainty labels and compare baselines fairly? | Collect repeated numeric response records across selected speeds and environments, then evaluate exact-source, holdout, and interpolation behavior. | repeated velocity response dataset records, baseline comparison report, claim audit | planned | Do not treat M15R label outputs as calibrated probabilities or performance superiority evidence. |
| future_navigation_risk_evaluation_v1 | Do M16 warning categories match real navigation task outcomes? | Run controlled navigation trials only after an approved protocol exists, then compare warnings against task outcomes. | navigation trial logs, risk map, outcome annotations, claim audit | planned | Evaluate warning correctness and command-region risk classification; do not fabricate collision, near-miss, success-rate, or safety-improvement metrics. |
| future_performance_claim_upgrade_v1 | What evidence is required to move from structural/software claims to performance claims? | Run repeated trials, baseline comparisons, and navigation outcome evaluations under a fixed protocol. | repeated datasets, model outputs, risk maps, navigation outcome logs, evidence table update | planned | Required before any safety-improvement, collision-reduction, near-miss-reduction, or success-rate claim. |
| future_m19_figure_and_protocol_assets_v1 | What figure assets and experiment protocols are required before manuscript drafting? | Convert M18 figure specs and experiment skeleton into generated figures and protocol checklists. | M18 figure specs, method skeleton, experiment skeleton, claim audit | planned | Do not convert planned experiments into results. |

Status options:

- planned
- ready
- running
- completed
- blocked
- cancelled
