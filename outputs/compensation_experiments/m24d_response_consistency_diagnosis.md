# M24-D Response Consistency Diagnosis

## Labels
- `environment_dependent_response`
- `profile_staleness_possible`
- `m23c_direct_response_not_reproduced`
- `candidate_profile_not_adoption_ready`
- `controlled_replication_required`
- `extraction_method_audit_required`
- `operator_reset_or_path_effect_possible`
- `robot_state_or_warmup_effect_possible`

## Hypotheses
- `environment_dependent_response`: Supported by large disagreement among M19C, M23-C, and M24-C direct-response estimates.
- `profile_staleness_possible`: M24-C differs from old M19C for all old-profile comparable velocities, but this is not sufficient for adoption.
- `m23c_direct_response_not_reproduced`: M24-C differs from M23-C direct behavior at 3/3 three-way overlap velocities.
- `candidate_profile_not_adoption_ready`: M24-C decision is inconclusive_environment_dependent.
- `controlled_replication_required`: A repeat controlled direct-refresh session is needed before profile adoption.
- `extraction_method_audit_required`: M24-C near-zero velocity across all commands requires extraction-window/source review.
- `operator_reset_or_path_effect_possible`: Starting pose/path reset is not encoded in the aggregate artifacts.
- `robot_state_or_warmup_effect_possible`: Battery, warm-up, and environment state are not encoded in the aggregate artifacts.

Candidate profile adoption supported: `false`

These are evidence-bounded hypotheses, not proven root causes.
