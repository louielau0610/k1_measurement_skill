# Experiment Plan

Use this file for planned experiments only. Do not record planned experiments as completed results.

## Planned Experiments

| experiment_id | question | protocol | required_artifacts | status | notes |
| --- | --- | --- | --- | --- | --- |
| future_velocity_response_repeats_v1 | Which missing schema fields and uncertainty estimates are needed for stronger response models? | Repeat selected `vx_cmd_mps` values with documented localization, environment labels, and per-trial response metrics. | dataset schema v1 records, repeated trial logs, validation report | planned | Populate missing fields such as lateral drift, response delay, stop distance, and repeated-trial variance; do not record planned values as results. |
| future_uncertainty_calibration_v1 | How much repeated numeric evidence is required to calibrate uncertainty labels and compare baselines fairly? | Collect repeated numeric response records across selected speeds and environments, then evaluate exact-source, holdout, and interpolation behavior. | repeated velocity response dataset records, baseline comparison report, claim audit | planned | Do not treat M15R label outputs as calibrated probabilities or performance superiority evidence. |

Status options:

- planned
- ready
- running
- completed
- blocked
- cancelled
