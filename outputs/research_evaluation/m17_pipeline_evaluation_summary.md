# M17 管线评估摘要

## Current Pipeline Status

- Dataset records: 5
- Response predictions: 5
- Risk assessments: 5
- Publication readiness: not_ready_for_full_submission

## Artifact Chain

- M13: `configs/velocity_response_dataset_schema_v1.json` (schema)
- M14: `outputs/research_datasets/velocity_response_dataset_v1.json` (dataset)
- M14: `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` (validation_report)
- M15R: `outputs/research_models/response_model_predictions_v1.json` (prediction_output)
- M15R: `outputs/research_models/response_model_evaluation_v1.json` (evaluation_output)
- M16: `outputs/research_risk/navigation_risk_map_v1.json` (risk_map)
- M16: `outputs/research_risk/navigation_risk_evaluation_v1.json` (risk_evaluation)
- P0-M17: `paper/claims/claim_registry.md` (claim_registry)
- P0-M17: `paper/claims/non_claims.md` (non_claims)

## Supported Claims

- Measurement v0 source artifacts exist and are represented in the repository.
- Velocity response dataset schema v1 and dataset v1 exist.
- Response model foundation exists with conservative uncertainty/confidence labels.
- Offline navigation-aware risk mapping layer exists.
- Pipeline evaluation artifacts exist.

## Non-Claims

- No real navigation safety improvement is demonstrated.
- No collision-rate reduction is demonstrated.
- No near-miss-rate reduction is demonstrated.
- No navigation success-rate improvement is demonstrated.
- No velocity compensation readiness is demonstrated.
- No safe command adapter readiness is demonstrated.
- No publication readiness is claimed.

## Available Metrics

- dataset_records_count
- numeric_records_count
- qualitative_only_records_count
- response_predictions_count
- risk_assessments_count
- warnings_count
- risk_level_counts
- warning_category_counts
- exact_source_reconstruction_absolute_error_sanity_check

## Unavailable Metrics

- generalization_error
- calibrated_uncertainty_error
- collision_rate
- near_miss_rate
- navigation_success_rate
- real_world_safety_improvement
- compensation_performance
- safe_command_adapter_performance

## Limitations

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

## Next Experiments

- repeated trials per command velocity
- multi-surface velocity response tests
- vx plus wz command grid
- yaw and lateral drift measurement
- response delay and stop-distance logging
- navigation task trials with and without advisory risk layer
- baseline comparison under a fixed protocol
