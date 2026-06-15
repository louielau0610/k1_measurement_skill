# m25r_formal_collection

- Ready: `false`
- Exploration trials: 0
- Formal trials: 0
- Random seed: `250625`

## Blocked Reasons

- `unresolved_placeholder`: evidence_type is required
- `unresolved_placeholder`: evidence_reference is required
- `unresolved_placeholder`: confirmed_by is required
- `unresolved_placeholder`: confirmed_at is required
- `unresolved_placeholder`: control_mode is required
- `unresolved_placeholder`: gait_mode is required
- `safe_command_limit_not_configured`: safe_command_speed_max must be positive and non-null
- `safe_command_limit_not_configured`: safe_command_speed_max is required for executable M25 plans
- `safe_command_limit_not_configured`: safe maximum is required
- `formal_blocked_before_exploration_review`: formal collection requires reviewed exploration data or documented override

## Operator Commands

- `preflight_validation`: `py scripts/validate_m25_real_collection_preflight.py --config configs\m25_real_collection_preflight_template.yaml`
- `dry_run_generation`: `py scripts/prepare_m25r_collection_package.py --config configs\m25_real_collection_preflight_template.yaml --phase formal`
- `print_only_inspection`: `py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase formal`
- `real_execution`: `BLOCKED until preflight ready; then run the existing guarded robot runner with --execute and per-trial operator confirmation`
- `session_validation`: `py scripts/validate_m25_collected_session.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv>`
- `candidate_profile_generation`: `py scripts/build_m25_candidate_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv> --dry-run`

No robot motion is executed by this package generator.
