# Velocity Compensation Algorithm Specification v1 — Reference

**Spec version**: `compensation_algorithm_spec_v1.0`
**Algorithm**: Conservative Monotonic Segment Inverse Lookup
**Status**: Specification only. `implementation_ready = false`

This is the machine-readable companion to `docs/velocity_compensation_algorithm_spec.md`. See that document for the complete specification with rationale, policies, and examples.

## Quick Reference

### Algorithm at a Glance

1. Load measurement data for platform + surface.
2. Filter: remove insufficient evidence, high-risk, deadzone cells.
3. Sort remaining cells by command velocity.
4. Build monotonic segments.
5. Handle deadzone (desired below minimum) → `infeasible_deadzone`
6. Handle out-of-range (desired above maximum) → `infeasible_out_of_range`
7. Find bracketing monotonic segments.
8. Select best segment (lowest risk, highest confidence).
9. Piecewise linear inverse interpolation.
10. Return structured result.

### Feasibility Statuses

| Status | When |
|--------|------|
| `ok` | Successful, reliable compensation |
| `feasible_but_risky` | Computed but risk/uncertainty elevated |
| `infeasible_deadzone` | Below minimum effective velocity |
| `infeasible_out_of_range` | Above measured range, no extrapolation |
| `insufficient_evidence` | Not enough data after filtering |
| `non_monotonic_ambiguous` | Multiple candidate segments, can't disambiguate |
| `platform_not_calibrated` | No profile for platform |
| `surface_not_calibrated` | No data for surface |
| `invalid_input` | Input validation failed |

### Risk Policies

| Policy | Accepted Labels | Max Risk | Min Repeats |
|--------|----------------|----------|-------------|
| Conservative | `reliable` | 0.3 | 3 |
| Balanced | `reliable`, `under_track` | 0.6 | 2 |
| Permissive | all except deadzone | 1.0 | 1 |

### Numerical Defaults

| Parameter | Default |
|-----------|---------|
| `no_motion_velocity_threshold_mps` | 0.02 |
| `yaw_drift_high_threshold_deg` | 5.0 |
| `uncertainty_high_threshold_mps` | 0.08 |
| `minimum_segment_points` | 2 |
| `minimum_cell_repeats` | 3 |
| `minimum_confidence` | 0.5 |
| `extrapolation_allowed` | false |

### Output Fields

`recommended_command_velocity_mps`, `expected_actual_velocity_mps`, `expected_tracking_error_mps`, `feasibility_status`, `region_label`, `risk_score`, `confidence`, `reason`, `warnings`, `limitations`

### Phase Gates

- `implementation_ready = false`
- `compensation_ready = false`
- `k1_compensation_validated = false`

### Next

**M22-C**: Offline velocity compensator prototype — implement this specification as a Python module.
