# Velocity Compensation Feasibility Status Specification

**Spec version**: `compensation_algorithm_spec_v1.0`
**Status**: Specification only.

## Purpose

Defines the feasibility statuses returned by the velocity compensator. Each status indicates whether compensation was successful, and if not, why.

## Status Definitions

### `ok`

Compensation computed successfully. The desired velocity falls within a validated, monotonic, low-risk response segment. The recommended command velocity was computed using piecewise linear inverse interpolation between two reliable measurement points.

**Conditions**:
- Desired velocity is within measured range
- Bracketing segment is monotonic
- Segment passes risk filtering for the active policy
- Confidence >= minimum_confidence
- No warnings generated

### `feasible_but_risky`

Compensation computed, but risk or uncertainty is elevated. The recommendation should be used with caution.

**Conditions** (any of):
- Selected segment has moderate risk (under_track or drift_prone under balanced policy)
- Yaw drift is moderate (2.5°–5.0°)
- Response uncertainty is moderate (0.04–0.08 m/s)
- Nearest-bound suggestion was used for deadzone or out-of-range
- Only one measurement point available for interpolation (no bracketing pair)

**Warnings**: Must include the specific risk factors.

### `infeasible_deadzone`

Desired velocity is below the minimum effective actual velocity for this surface. The robot cannot reliably achieve such a low velocity with the current command interface.

**Conditions**:
- `desired_actual_velocity_mps < minimum_effective_actual_velocity_mps`
- OR the only cells that could bracket the desired velocity have `no_motion_ratio > 0`

**Recommendation**: `recommended_command_velocity_mps = 0.0` (under conservative policy) or nearest feasible command with `feasible_but_risky` (under balanced/permissive).

### `infeasible_out_of_range`

Desired velocity exceeds the maximum measured actual velocity for this surface. No measurement data exists to validate compensation in this range.

**Conditions**:
- `desired_actual_velocity_mps > max(mean_actual_velocity_mps)` across all valid cells
- `extrapolation_policy = reject`

**Recommendation**: Under `extrapolation_policy = nearest_bound`, the highest valid recommendation may be returned with `feasible_but_risky`.

### `insufficient_evidence`

Not enough measurement data to compute compensation for this surface-speed combination.

**Conditions** (any of):
- After risk filtering, no cells remain
- `n < minimum_cell_repeats` for all relevant cells
- Fewer than `minimum_segment_points` valid measurement points available
- No cells bracket the desired velocity after filtering

### `non_monotonic_ambiguous`

The response is non-monotonic in the desired velocity region, and no single segment is clearly the best choice. Multiple command velocities could produce the same actual velocity, and the compensator cannot disambiguate without additional policy guidance.

**Conditions**:
- Multiple monotonic segments bracket the desired velocity
- After risk and confidence filtering, more than one segment remains
- Segments have comparable risk scores (within 0.1)

**Recommendation**: The caller should either: (1) tighten the risk policy, (2) provide additional surface data, or (3) accept the ambiguity and pick one segment manually.

### `platform_not_calibrated`

The specified platform has no measurement profile. No response data exists to compute compensation.

**Conditions**:
- Platform not found in measurement registry
- OR platform is scaffold-only (e.g., `unitree_go1`, `unitree_g1`)

### `surface_not_calibrated`

The specified surface has no measurement data for this platform. The platform may be calibrated on other surfaces, but not this one.

**Conditions**:
- Surface not found in the platform's measurement profile
- Zero rows match `platform` + `surface_type`

### `invalid_input`

Input validation failed. The compensator cannot process the request as provided.

**Conditions** (any of):
- `desired_actual_velocity_mps < 0` (negative velocity)
- Required fields missing from input
- `surface_type` is empty or invalid
- Measurement contract version mismatch
- Response profile path does not exist or is unreadable

## Status Hierarchy

From best to worst:

1. `ok`
2. `feasible_but_risky`
3. `non_monotonic_ambiguous`
4. `infeasible_deadzone`
5. `infeasible_out_of_range`
6. `insufficient_evidence`
7. `surface_not_calibrated`
8. `platform_not_calibrated`
9. `invalid_input`

The compensator should return the best achievable status given the data and policies.
