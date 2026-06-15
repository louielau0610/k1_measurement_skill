# m25r_formal_collection

- Ready: `false`
- Safe-speed resolved: `true`
- Safe command speed max: `0.6`
- Exploration trials: 12
- Formal trials: 30
- Random seed: `250625`

## Blocked Reasons

- `unresolved_placeholder`: control_mode is required
- `unresolved_placeholder`: gait_mode is required
- `formal_blocked_before_exploration_review`: formal collection requires reviewed exploration data or documented override

## Operator Commands

- `preflight_validation`: `py scripts/validate_m25_real_collection_preflight.py --config configs\m25_k1_s2_real_collection.yaml`
- `dry_run_generation`: `py scripts/prepare_m25r_collection_package.py --config configs\m25_k1_s2_real_collection.yaml --phase formal`
- `print_only_inspection`: `py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase formal`
- `real_execution`: `BLOCKED until preflight ready; then run the existing guarded robot runner with --execute and per-trial operator confirmation`
- `session_validation`: `py scripts/validate_m25_collected_session.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv>`
- `candidate_profile_generation`: `py scripts/build_m25_candidate_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv> --dry-run`

No robot motion is executed by this package generator.
