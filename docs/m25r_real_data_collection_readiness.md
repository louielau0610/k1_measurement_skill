# M25-R Real-Data Collection Readiness

M25-R closes operational gaps before real full-range velocity-profile collection. M25-S has now resolved the safe-speed confirmation. M26 response-model fitting remains blocked.

## Current State (as of M25-T)

- M25 engineering contract: complete.
- `safe_command_speed_max`: confirmed at `0.6 m/s` via M25-S operator confirmation.
- K1 motion path: resolved as `kPrepare -> kWalking -> Move(vx, 0.0, 0.0)` via `booster_sdk_kPrepare_kWalking_Move`.
- K1 `control_mode` and `gait_mode`: optional metadata for the current adapter, not execution blockers.
- Exploration collection package: ready, with 12 planned trials and no control/gait blocker.
- Formal collection package: blocked until exploration data review or documented override.
- M26 modeling: blocked until real formal profile data exist.

## Safe-Speed Resolution

The K1 safe forward command-speed maximum has been confirmed as `0.6 m/s`. The confirmation file is:

```text
configs/m25_k1_safe_speed_operator_confirmation.yaml
```

The unresolved template remains preserved at:

```text
configs/m25_k1_safe_speed_operator_confirmation_template.yaml
```

Validate the confirmed file:

```powershell
py scripts/validate_m25_safe_speed_confirmation.py --config configs/m25_k1_safe_speed_operator_confirmation.yaml
```

## Preflight

The concrete K1/S2 real-collection configuration is:

```text
configs/m25_k1_s2_real_collection.yaml
```

The generic template remains preserved at:

```text
configs/m25_real_collection_preflight_template.yaml
```

Validate the K1 config:

```powershell
py scripts/validate_m25_real_collection_preflight.py --config configs/m25_k1_s2_real_collection.yaml
```

The committed generic template is expected to fail closed because safe speed and generic mode context remain unresolved. The concrete K1 config uses the adapter-specific fixed SDK motion-sequence policy.

## Collection Packages

Generate package artifacts with:

```powershell
py scripts/prepare_m25r_collection_package.py --config configs/m25_real_collection_preflight_template.yaml --phase exploration
py scripts/prepare_m25r_collection_package.py --config configs/m25_real_collection_preflight_template.yaml --phase formal
```

For the current K1/S2 package, use `configs/m25_k1_s2_real_collection.yaml`. The generated packages contain exact operator commands for preflight validation, dry-run generation, print-only inspection, real execution handoff, session validation, and candidate-profile generation. Package generation does not execute robot motion. The package metadata includes the validated safe-speed hash and requires the runner to use the same resolved `0.6 m/s` limit.

## Exploration Gate

After exploration extraction exists, evaluate:

```powershell
py scripts/evaluate_m25_exploration_gate.py --config <resolved_m25_config.yaml> --results <exploration_extracted.csv>
```

The gate may return `ready_for_formal_collection`, `requires_grid_extension`, `requires_grid_refinement`, `insufficient_valid_trials`, `high_priority_region_not_covered`, `safe_limit_prevents_requested_coverage`, or `extraction_quality_failure`. It does not fit or select an M26 model.

## Scientific Boundary

M25-R/M25-T fabricates no real data, invents no safe maximum, invents no mode or gait name, executes no robot motion, validates no profile, reintroduces no yaw/deadzone gate, and selects no compensation model.
