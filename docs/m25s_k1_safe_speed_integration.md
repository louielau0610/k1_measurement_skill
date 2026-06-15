# M25-S — K1 Safe-Speed Integration

M25-S integrates the confirmed K1 safe forward command-speed maximum of `0.6 m/s` into the M25/M25-R real-collection workflow.

## Safe-Speed Confirmation

- **File**: `configs/m25_k1_safe_speed_operator_confirmation.yaml`
- **Confirmed value**: `safe_command_speed_max: 0.6` m/s
- **Evidence type**: `operator_confirmation`
- **Confirmed by**: operator
- **Confirmed at**: 2026-06-15
- **Validation**: `py scripts/validate_m25_safe_speed_confirmation.py --config configs/m25_k1_safe_speed_operator_confirmation.yaml --speed-only` → `valid: true`

## Current K1 Valid Command Domain

```
valid_command_speed_min: 0.35 m/s
safe_command_speed_max: 0.60 m/s
high_priority_actual_speed_min: 0.50 m/s
high_priority_actual_speed_max: 0.60 m/s
```

- `0.35 m/s` is an engineering applicability boundary, not a deadzone threshold.
- `0.60 m/s` is the confirmed maximum permitted forward command.
- Commands above `0.60 m/s` are rejected.
- The `0.50-0.60 m/s` region is the high-priority evaluation region.

## Exploration Grid (Current K1)

| Command (m/s) | Repeats |
|---------------|---------|
| 0.35          | 3       |
| 0.40          | 3       |
| 0.50          | 3       |
| 0.60          | 3       |

- **Total**: 4 × 3 = 12 trials
- All points within `[0.35, 0.60]`
- Deterministic randomized order (seed: 250625)

## Formal Grid (Current K1)

| Command (m/s) | Repeats |
|---------------|---------|
| 0.35          | 5       |
| 0.40          | 5       |
| 0.45          | 5       |
| 0.50          | 5       |
| 0.55          | 5       |
| 0.60          | 5       |

- **Total**: 6 × 5 = 30 trials
- Upper region (`0.50-0.60`) has 3 points with 0.05 spacing
- All points within `[0.35, 0.60]`

## Exploration Gate Semantics

The exploration gate evaluates:

- Command coverage across `0.35-0.60`
- Valid repeats at each command point
- Stable-window extraction quality
- Fit quality
- Observed actual-speed ordering
- Upper-range coverage near `0.50-0.60`
- Whether the safe limit prevents further extension

Gate outcomes:

- `ready_for_formal_collection`
- `requires_grid_extension` (only when not at safe limit)
- `requires_grid_refinement`
- `insufficient_valid_trials`
- `high_priority_region_not_covered`
- `safe_limit_prevents_requested_coverage`
- `extraction_quality_failure`

The gate no longer requires coverage of `0.8-1.0 m/s`. Commands above `0.60 m/s` are never recommended.

## Readiness

| Field | Status |
|-------|--------|
| `safe_command_speed_max_resolved` | `true` |
| `safe_command_speed_max` | `0.6` |
| Exploration executable | blocked on control_mode, gait_mode |
| Formal executable | blocked on control_mode, gait_mode, exploration review |
| M26 modeling | blocked until real formal data exist |

## Files

### Created
- `configs/m25_k1_safe_speed_operator_confirmation.yaml`
- `configs/m25_k1_s2_real_collection.yaml`
- `docs/m25s_k1_safe_speed_integration.md`

### Modified
- `k1_measurement/full_range_velocity_profile.py` — Updated defaults, grids, ValidSpeedDomain
- `k1_measurement/m25_real_collection_preflight.py` — Added domain/grid overrides, safe-speed resolution, gate semantics
- `scripts/validate_m25_safe_speed_confirmation.py` — Added `--speed-only` flag
- `configs/m25_full_range_velocity_profile_template.yaml` — Updated for K1 domain
- `outputs/full_range_velocity_profile/m25r_exploration_collection_package.json`
- `outputs/full_range_velocity_profile/m25r_exploration_collection_package.md`
- `outputs/full_range_velocity_profile/m25r_formal_collection_package.json`
- `outputs/full_range_velocity_profile/m25r_formal_collection_package.md`
- `tests/test_m25_full_range_velocity_profile.py` — Added 10 K1-specific tests
- `tests/test_m25_real_collection_preflight.py` — Added 13 K1-specific tests
- `README.md`, `README.en.md`, `PROJECT_STATUS.md`, `TODO.md`

### Preserved (not modified)
- `configs/m25_k1_safe_speed_operator_confirmation_template.yaml` (unresolved template)
- `configs/m25_real_collection_preflight_template.yaml` (generic template)
- Raw measurement sessions
- Historical M19/M23/M24 artifacts

## Scientific Boundary

- No command above `0.6 m/s` was generated.
- No robot motion was automatically executed.
- No actual-speed reachability was assumed.
- No real data were fabricated.
- No M26 model was fitted.
- M26 remains blocked until exploration and formal real-robot data are collected.
- `0.35 m/s` is an applicability boundary, not a deadzone estimate.
- Yaw remains paused.
- Deadzone work remains abandoned.
- The generic architecture supports other robots/configurations with different valid speed domains.
