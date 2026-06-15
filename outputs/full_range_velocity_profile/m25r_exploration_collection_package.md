# m25r_exploration_collection

- Ready: `true`
- Safe-speed resolved: `true`
- Safe command speed max: `0.6`
- Command source: `booster_sdk_kPrepare_kWalking_Move`
- Motion path resolved: `true`
- Exploration trials: 12
- Formal trials: 30
- Random seed: `250625`

## Blocked Reasons

- none

## Operator Commands

- `preflight_validation`: `py scripts/validate_m25_real_collection_preflight.py --config configs\m25_k1_s2_real_collection.yaml`
- `dry_run_generation`: `py scripts/prepare_m25r_collection_package.py --config configs\m25_k1_s2_real_collection.yaml --phase exploration`
- `print_only_inspection`: `py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase exploration`
- `real_execution`: `BLOCKED until preflight ready; then run the existing guarded robot runner with --execute and per-trial operator confirmation`
- `session_validation`: `py scripts/validate_m25_collected_session.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv>`
- `candidate_profile_generation`: `py scripts/build_m25_candidate_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv> --dry-run`

No robot motion is executed by this package generator.
