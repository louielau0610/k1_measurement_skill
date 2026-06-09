# Experiment Plan

Use this file for planned experiments only. Do not record planned experiments as completed results.

## Planned Experiments

| experiment_id | question | protocol | required_artifacts | status | notes |
| --- | --- | --- | --- | --- | --- |
| future_velocity_response_repeats_v1 | Which missing schema fields and uncertainty estimates are needed for stronger response models? | Repeat selected `vx_cmd_mps` values with documented localization, environment labels, and per-trial response metrics. | dataset schema v1 records, repeated trial logs, validation report | planned | Populate missing fields such as lateral drift, response delay, stop distance, and repeated-trial variance; do not record planned values as results. |
| future_uncertainty_calibration_v1 | How much repeated numeric evidence is required to calibrate uncertainty labels and compare baselines fairly? | Collect repeated numeric response records across selected speeds and environments, then evaluate exact-source, holdout, and interpolation behavior. | repeated velocity response dataset records, baseline comparison report, claim audit | planned | Do not treat M15R label outputs as calibrated probabilities or performance superiority evidence. |
| future_navigation_risk_evaluation_v1 | Do M16 warning categories match real navigation task outcomes? | Run controlled navigation trials only after an approved protocol exists, then compare warnings against task outcomes. | navigation trial logs, risk map, outcome annotations, claim audit | planned | Evaluate warning correctness and command-region risk classification; do not fabricate collision, near-miss, success-rate, or safety-improvement metrics. |

Status options:

- planned
- ready
- running
- completed
- blocked
- cancelled
