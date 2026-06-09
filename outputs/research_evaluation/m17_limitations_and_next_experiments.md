# M17 限制与下一步实验


## Current Limitations

- 0.1 m/s record is qualitative-only
- absolute_odom_coordinates_should_not_be_compared_across_trials
- limited environment coverage
- missing_response_dimensions_not_fabricated
- mostly_single_trial_per_speed
- no collision, near-miss, or success-rate metrics exist yet
- no full paper manuscript yet
- no real navigation outcomes exist yet
- no_compensation_or_safe_command_adapter_authority
- no_compensation_readiness_inferred
- no_safe_command_adapter_readiness_inferred
- odometer_primary_no_external_ground_truth
- single robot
- single_environment_lab_hard_floor
- single_session
- structural readiness evaluation only
- uncertainty labels are not calibrated probabilities
- uncertainty_and_confidence_are_labels_not_calibrated_probabilities
- vx_0_45_yaw_drift_requires_repeat

## Required Next Experiments

- repeated trials per command velocity
- multi-surface velocity response tests
- vx plus wz command grid
- yaw and lateral drift measurement
- response delay and stop-distance logging
- navigation task trials with and without advisory risk layer
- baseline comparison under a fixed protocol

## Claim Upgrade Conditions

- 需要 repeated-trial numeric evidence 才能升级 uncertainty claim。
- 需要真实 navigation outcome metrics 才能讨论 safety improvement。
- 需要 collision / near-miss / success-rate annotation 才能讨论风险降低。
- 需要 verified literature review 才能讨论 novelty。
