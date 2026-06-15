# M25 Full-Range Velocity Profiling

M25 refocuses the active project on longitudinal command speed versus measured actual speed across the complete configured valid command domain:

```text
[valid_command_speed_min, safe_command_speed_max]
```

The lower boundary is an engineering applicability boundary for the future velocity compensator. It is not a deadzone estimate. Deadzone research, deadzone compensation, yaw drift modeling, yaw compensation, and yaw-based validation gates are out of scope for the active M25 pipeline.

## Active Pipeline

```text
valid-speed measurement
-> full-range command-to-actual velocity profile
-> monotonic response model
-> inverse velocity compensation
-> full-range direct-vs-compensated validation
```

M25 implements the measurement/profile foundation only. It does not finalize inverse compensation, does not mark profiles as validated without real formal data, and does not claim compensation success.

## Configuration Contract

The default template is `configs/m25_full_range_velocity_profile_template.yaml`:

```yaml
valid_speed_domain:
  valid_command_speed_min: 0.35
  safe_command_speed_max: null
  high_priority_actual_speed_min: 0.80
  high_priority_actual_speed_max: 1.00
```

`safe_command_speed_max` must come from a validated robot configuration, SDK adapter, or operator-provided configuration. The repository does not guess this value. Executable plans are blocked while it is missing, using the machine-readable code `safe_command_limit_not_configured`.

Other rejection codes include:

- `below_valid_speed_domain`
- `above_safe_command_limit`
- `target_outside_reachable_actual_speed_range`

Targets outside the observed actual-speed reachability interval are rejected. The planner does not silently clip unreachable targets.

## Experiment Planning

The reusable implementation is `k1_measurement/full_range_velocity_profile.py`.

Phase A, exploration, covers the configured command domain using three repeats per command by default. The template command points are:

```text
0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00
```

Phase B, formal collection, uses five repeats per command by default with denser sampling around the high-priority 0.80-1.00 m/s actual-speed region:

```text
0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00
```

The high-priority interval is not the full applicability range and is not assumed reachable. Additional points above 1.0 m/s are permitted only when `safe_command_speed_max` explicitly allows them.

## Stable-Speed Extraction Contract

M25 profile rows must describe longitudinal actual speed. A valid extracted trial should include:

- `command_speed`
- `estimated_actual_speed`
- `steady_window_start`
- `steady_window_end`
- `steady_window_duration`
- `sample_count`
- `fit_method`
- `fit_quality`
- `speed_variability`
- `valid`
- `invalid_reasons`
- `source_session_id`
- `trial_id`

The preferred estimator is a fitted slope from displacement along the motion direction over a validated steady-state window. Existing raw yaw fields may remain in historical logs, but M25 ignores them for model features, objectives, quality scores, and validation gates.

## Candidate Profile Contract

Candidate profiles contain:

- command speed domain
- observed actual speed domain
- high-priority actual-speed region
- training command points
- repeats and per-point uncertainty
- session metadata
- surface and robot identifier
- extraction version
- profile status

Supported profile statuses are `planned`, `collected`, `candidate`, `validated`, and `rejected`. M25-produced profiles remain candidate or rejected unless real formal collection and validation have occurred.

## CLI Commands

```powershell
py scripts/validate_m25_full_range_velocity_config.py --config configs/m25_full_range_velocity_profile_template.yaml
py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase exploration
py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase formal
py scripts/validate_m25_collected_session.py --config configs/m25_full_range_velocity_profile_template.yaml --session path/to/extracted.csv
py scripts/build_m25_candidate_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --session path/to/extracted.csv --dry-run
py scripts/audit_m25_historical_compatibility.py --config configs/m25_full_range_velocity_profile_template.yaml
```

Planning commands generate JSON and Markdown artifacts under `outputs/full_range_velocity_profile/`. They never execute robot motion.

## Next Milestones

- M26 compares full-range monotonic response models after M25 data collection.
- M27 implements or finalizes inverse velocity compensation.
- M28 performs full-range direct-versus-compensated real-robot validation.

## M25-R Readiness Closure

M25-R adds the safe-speed confirmation and real-collection preflight layer. The committed project still leaves `safe_command_speed_max: null`; executable real-robot collection remains blocked until an operator or supervisor completes `configs/m25_k1_safe_speed_operator_confirmation_template.yaml` with evidence.

Readiness artifacts:

- `configs/m25_k1_safe_speed_operator_confirmation_template.yaml`
- `configs/m25_real_collection_preflight_template.yaml`
- `docs/m25r_real_data_collection_readiness.md`
- `scripts/validate_m25_safe_speed_confirmation.py`
- `scripts/validate_m25_real_collection_preflight.py`
- `scripts/prepare_m25r_collection_package.py`
- `scripts/evaluate_m25_exploration_gate.py`

M25-R also keeps formal collection blocked until exploration extraction has been reviewed or a documented override is provided. M26 modeling remains blocked until real formal profile data are available.
