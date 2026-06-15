# M25-R Real-Data Collection Readiness

M25-R closes operational gaps before real full-range velocity-profile collection. It does not start M26 response-model fitting.

## Current State

- M25 engineering contract: complete.
- `safe_command_speed_max`: unresolved in the committed template.
- Exploration collection: blocked until safe speed confirmation and preflight pass.
- Formal collection: blocked until safe speed confirmation, preflight pass, and exploration data review or documented override.
- M26 modeling: blocked until real formal profile data exist.

## Safe-Speed Resolution

No authoritative safe maximum was found in repository configuration, SDK adapter constraints, or active safeguards. Historical executed commands are not treated as proof of a robot-wide safe maximum.

Operators must copy and complete:

```text
configs/m25_k1_safe_speed_operator_confirmation_template.yaml
```

Allowed evidence types are:

- `sdk_documentation`
- `validated_robot_configuration`
- `lab_protocol`
- `supervisor_approval`
- `operator_confirmation`

Validate the completed file with:

```powershell
py scripts/validate_m25_safe_speed_confirmation.py --config <completed_confirmation.yaml>
```

## Preflight

The preflight template is:

```text
configs/m25_real_collection_preflight_template.yaml
```

Validate it with:

```powershell
py scripts/validate_m25_real_collection_preflight.py --config configs/m25_real_collection_preflight_template.yaml
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
