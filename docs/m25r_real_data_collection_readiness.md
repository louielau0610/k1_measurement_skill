# M25-R Real-Data Collection Readiness

M25-R closes operational gaps before real full-range velocity-profile collection. M25-S has now resolved the safe-speed confirmation. M26 response-model fitting remains blocked.

## Current State (as of M25-S)

- M25 engineering contract: complete.
- `safe_command_speed_max`: confirmed at `0.6 m/s` via M25-S operator confirmation.
- Exploration collection: blocked on unresolved operational fields (control_mode, gait_mode).
- Formal collection: blocked on operational fields and exploration data review.
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

Validate the confirmed file (speed-only):

```powershell
py scripts/validate_m25_safe_speed_confirmation.py --config configs/m25_k1_safe_speed_operator_confirmation.yaml --speed-only
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

The committed template is expected to fail closed because safe speed, control mode, and gait mode are unresolved.

## Collection Packages

Generate package artifacts with:

```powershell
py scripts/prepare_m25r_collection_package.py --config configs/m25_real_collection_preflight_template.yaml --phase exploration
py scripts/prepare_m25r_collection_package.py --config configs/m25_real_collection_preflight_template.yaml --phase formal
```

The generated packages contain exact operator commands for preflight validation, dry-run generation, print-only inspection, real execution handoff, session validation, and candidate-profile generation. Package generation does not execute robot motion.

## Exploration Gate

After exploration extraction exists, evaluate:

```powershell
py scripts/evaluate_m25_exploration_gate.py --config <resolved_m25_config.yaml> --results <exploration_extracted.csv>
```

The gate may return `ready_for_formal_collection`, `requires_grid_extension`, `requires_grid_refinement`, `insufficient_valid_trials`, `high_priority_region_not_covered`, `safe_limit_prevents_requested_coverage`, or `extraction_quality_failure`. It does not fit or select an M26 model.

## Scientific Boundary

M25-R fabricates no real data, invents no safe maximum, executes no robot motion, validates no profile, and selects no compensation model.
