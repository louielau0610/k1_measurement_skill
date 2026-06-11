# Velocity Compensation Algorithm Specification v1

**Spec version**: `compensation_algorithm_spec_v1.0`
**Algorithm name**: Conservative Monotonic Segment Inverse Lookup
**Status**: Specification only — no implementation exists yet.
**`implementation_ready`**: `false`
**`compensation_ready`**: `false`

## Purpose

This document defines the first velocity compensation algorithm in precise engineering terms. It specifies inputs, outputs, processing steps, policies, and default thresholds. No implementation code is produced in this milestone.

## Algorithm Name

**Conservative Monotonic Segment Inverse Lookup**

The algorithm performs piecewise linear inverse interpolation over validated monotonic response segments, with risk filtering, deadzone awareness, and no extrapolation by default.

## Input Contract

When implemented, the compensator shall accept the following input fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string | ✅ | Platform identifier (e.g., `booster_k1`) |
| `robot_model` | string | ✅ | Robot model name |
| `robot_id` | string | ✅ | Individual robot identifier |
| `surface_type` | string | ✅ | Surface type (e.g., `lab_hard_floor`) |
| `desired_actual_velocity_mps` | float | ✅ | Desired actual forward velocity in m/s |
| `measurement_contract_version` | string | ✅ | Contract version (e.g., `measurement_v1.0`) |
| `response_profile_path` | string | ✅ | Path to response statistics or gold profile |
| `allowed_region_labels` | list[string] | ❌ | Region labels allowed for compensation |
| `risk_policy` | string | ❌ | `conservative`, `balanced`, or `permissive` |
| `extrapolation_policy` | string | ❌ | `reject` (default) or `nearest_bound` |
| `minimum_confidence` | float | ❌ | Minimum confidence threshold |
| `operator_notes` | string | ❌ | Free-text operator notes |

### Default Policies

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `extrapolation_policy` | `reject` | Refuse desired velocities outside measured range |
| `risk_policy` | `conservative` | Accept only reliable cells |
| `allowed_region_labels` | `["reliable"]` | Default under conservative; may add `under_track` under balanced |
| `minimum_confidence` | `0.5` | Minimum confidence for any cell used |

## Output Contract

When implemented, the compensator shall produce the following output fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Contract version |
| `platform` | string | Platform identifier |
| `robot_model` | string | Robot model |
| `surface_type` | string | Surface type |
| `desired_actual_velocity_mps` | float | Input desired velocity |
| `recommended_command_velocity_mps` | float | Compensated command velocity (or 0 if infeasible) |
| `expected_actual_velocity_mps` | float | Predicted actual velocity for the recommended command |
| `expected_tracking_error_mps` | float | expected − desired |
| `expected_relative_error` | float | error / desired |
| `selected_segment` | string | Identifier of the selected monotonic segment |
| `source_points` | list[dict] | The measurement points used for interpolation |
| `region_label` | string | Risk region label of the selected cell |
| `risk_score` | float | Risk score of the selected cell |
| `confidence` | float | Confidence in the recommendation |
| `feasibility_status` | string | See feasibility statuses below |
| `reason` | string | Human-readable explanation |
| `warnings` | list[string] | Active warnings |
| `limitations` | list[string] | Known limitations of this recommendation |

## Feasibility Statuses

| Status | Meaning |
|--------|---------|
| `ok` | Compensation computed successfully within reliable region |
| `feasible_but_risky` | Compensation computed but risk/uncertainty is elevated |
| `infeasible_deadzone` | Desired velocity is below the minimum effective velocity |
| `infeasible_out_of_range` | Desired velocity exceeds the measured valid range |
| `insufficient_evidence` | Not enough measurement data for this surface-speed cell |
| `non_monotonic_ambiguous` | Response is non-monotonic and no single segment is clearly best |
| `platform_not_calibrated` | Platform has no measurement profile |
| `surface_not_calibrated` | Surface has no measurement data |
| `invalid_input` | Input validation failed (negative velocity, missing fields, etc.) |

## Algorithm Steps

### Step 1: Load Measurement Data
Load the measurement_v1.0 contract CSV or gold profile for the specified platform and surface.

### Step 2: Filter by Platform and Surface
Filter rows matching `platform` and `surface_type`. If no rows match, return `surface_not_calibrated`.

### Step 3: Remove Insufficient Evidence Cells
Remove aggregate cells where:
- `n < minimum_cell_repeats` (default 3)
- `evidence_level` is below threshold
- Cell has fewer than `minimum_segment_points` valid trial measurements

If no cells remain, return `insufficient_evidence`.

### Step 4: Apply Risk Filtering
Filter or downgrade cells according to the selected risk policy. See risk filtering document for details.

If no cells remain after filtering, return `insufficient_evidence` with an explicit note that risk filtering removed all candidates.

### Step 5: Detect Deadzone
Identify cells where `no_motion_ratio > 0` or `mean_actual_velocity_mps < no_motion_velocity_threshold_mps`.

Compute:
- `minimum_effective_command_velocity_mps`: lowest command velocity that produces measurable motion
- `minimum_effective_actual_velocity_mps`: corresponding actual velocity

### Step 6: Sort Remaining Cells
Sort valid cells by `command_velocity_mps` ascending.

### Step 7: Build Monotonic Segments
Scan sorted cells and group consecutive cells where `mean_actual_velocity_mps` is non-decreasing into monotonic segments.

For each segment:
- Record start and end command velocities
- Record start and end actual velocities
- Record the cells that compose the segment
- Assign the segment's risk as the maximum risk of its constituent cells

### Step 8: Handle Deadzone (desired below minimum effective velocity)
If `desired_actual_velocity_mps < minimum_effective_actual_velocity_mps`:
- Under `conservative` policy: return `infeasible_deadzone`
- Under `balanced`/`permissive` policy with `extrapolation_policy = nearest_bound`: return the minimum effective command as a suggestion with `feasible_but_risky`

### Step 9: Handle Out-of-Range (desired above maximum measured velocity)
If `desired_actual_velocity_mps > max(mean_actual_velocity_mps)`:
- Under `extrapolation_policy = reject` (default): return `infeasible_out_of_range`
- Under `extrapolation_policy = nearest_bound`: return the highest valid recommendation with `feasible_but_risky`

### Step 10: Find Bracketing Segments
Find all monotonic segments where:
- `segment_min_actual <= desired_actual_velocity_mps <= segment_max_actual`

If no segment brackets the desired velocity exactly, find the nearest segment (above or below) and apply the extrapolation policy.

### Step 11: Select Best Segment
Among candidate segments:
1. Eliminate segments with risk score above policy threshold.
2. Eliminate segments with confidence below `minimum_confidence`.
3. Choose the segment with the lowest risk score.
4. If tied, choose the segment with the highest confidence.
5. If still tied, choose the segment closest to the desired velocity.

If no segment qualifies, return `non_monotonic_ambiguous` or `insufficient_evidence`.

### Step 12: Compute Inverse Interpolation
Within the selected segment, find the two bracketing measurement points `(cmd_a, actual_a)` and `(cmd_b, actual_b)` where:
- `actual_a <= desired_actual_velocity_mps <= actual_b`

Compute the compensated command velocity using piecewise linear inverse interpolation:

$$v_{cmd\_recommended} = cmd_a + (cmd_b - cmd_a) \times \frac{v_{desired} - actual_a}{actual_b - actual_a}$$

If the segment contains only one point, use that point's command velocity directly.

### Step 13: Compute Expected Actual Velocity
Using the forward response (mean_actual_velocity_mps at the interpolated command), compute:

$$v_{actual\_expected} = actual_a + (actual_b - actual_a) \times \frac{v_{cmd\_recommended} - cmd_a}{cmd_b - cmd_a}$$

### Step 14: Return Structured Result
Assemble the output contract with all fields populated. Include the feasibility status, reason string, warnings list, and limitations list.

## Deadzone Policy

### Computing Minimum Effective Command Velocity

The minimum effective command velocity is the lowest `command_velocity_mps` for which:
- `n >= minimum_cell_repeats`
- `no_motion_ratio < 1.0` (at least some trials produced motion)
- The cell passes risk filtering for the current policy

### Computing Minimum Effective Actual Velocity

The minimum effective actual velocity is the `mean_actual_velocity_mps` at the minimum effective command velocity.

### Classifying Deadzone-Infeasible

A desired velocity is deadzone-infeasible when:
- `desired_actual_velocity_mps < minimum_effective_actual_velocity_mps`
- OR the only cells that could achieve it have `no_motion_ratio > 0` and policy is conservative

### Nearest Feasible Suggestion (Optional)

Under balanced or permissive policies, the compensator may return `feasible_but_risky` with the minimum effective command as `recommended_command_velocity_mps`. The reason must clearly state this is a deadzone-boundary suggestion.

### Why Low Desired Velocity Should Not Be Blindly Mapped

A low desired velocity (e.g., 0.01 m/s) should not be mapped to a higher command velocity (e.g., 0.10 m/s) if:
- That command velocity is in a drift-prone region (high yaw drift > 5°)
- That command velocity has high response uncertainty (> 0.08 m/s)
- The robot may lurch or become unstable at the boundary

The compensator must refuse rather than silently produce an unsafe recommendation.

## Non-Monotonic Policy

### Detecting Non-Monotonic Regions

Scan sorted cells by `command_velocity_mps`. A non-monotonic region exists when:
- `mean_actual_velocity_mps` decreases as `command_velocity_mps` increases
- OR the same command velocity maps to significantly different actual velocities (bimodal response)

### Splitting Monotonic Segments

When non-monotonicity is detected:
1. Split at each point where `mean_actual_velocity_mps[i+1] < mean_actual_velocity_mps[i]`.
2. Each resulting segment is independently monotonic.
3. Mark segments with only 1 point as low-confidence.

### Handling Multiple Candidate Segments

When multiple monotonic segments bracket the desired velocity:
1. Apply risk filtering to eliminate unsafe segments.
2. Apply confidence filtering.
3. Select the lowest-risk, highest-confidence segment.
4. If ambiguous, return `non_monotonic_ambiguous`.

### Why Global Inverse Interpolation Is Unsafe

Global inverse interpolation (fitting a single function across all command velocities) is unsafe because:
- Non-monotonic response regions cause the inverse to be ambiguous (one desired velocity → multiple possible commands)
- Polynomial or spline fits can oscillate between measured points
- Extrapolation behavior is unpredictable
- Uncertainty is not localized

Piecewise linear interpolation within validated monotonic segments avoids these risks.

## Risk Policies

### Conservative (Default)

| Rule | Action |
|------|--------|
| Region label = `reliable` | ✅ Accept |
| Region label = `under_track` | ❌ Reject unless `allowed_region_labels` explicitly includes it |
| Region label = `unstable` | ❌ Reject |
| Region label = `drift_prone` | ❌ Reject |
| Region label = `deadzone` | ❌ Reject |
| `yaw_drift_deg > yaw_drift_high_threshold_deg` | ❌ Reject |
| `response_uncertainty > uncertainty_high_threshold_mps` | ❌ Reject |
| `no_motion_ratio > 0` | ❌ Reject |
| `n < minimum_cell_repeats` | ❌ Reject |

### Balanced

| Rule | Action |
|------|--------|
| Region label = `reliable` | ✅ Accept |
| Region label = `under_track` | ⚠️ Accept if uncertainty and yaw drift are moderate |
| Region label = `unstable` | ❌ Reject |
| Region label = `drift_prone` | ⚠️ Accept with explicit warning if uncertainty is low |
| Region label = `deadzone` | ❌ Reject |
| Yaw drift moderate (2.5°–5.0°) | ⚠️ Warn |
| Response uncertainty moderate (0.04–0.08 m/s) | ⚠️ Warn |
| `n >= minimum_cell_repeats` | ✅ Accept |

### Permissive

| Rule | Action |
|------|--------|
| Any region label except `deadzone` | ⚠️ May return `feasible_but_risky` |
| Region label = `deadzone` | ❌ Still reject (no motion means no compensation possible) |
| Yaw drift any value | ⚠️ Warn if high |
| `n >= minimum_cell_repeats` | ✅ Accept |
| Insufficient evidence cells | ❌ Still reject (cannot compensate without data) |

## Numerical Defaults

These are specification defaults. Implementations may override with documented justification.

| Parameter | Default | Unit |
|-----------|---------|------|
| `no_motion_velocity_threshold_mps` | `0.02` | m/s |
| `under_track_relative_threshold` | `0.20` | — |
| `over_response_relative_threshold` | `0.20` | — |
| `yaw_drift_high_threshold_deg` | `5.0` | degrees |
| `uncertainty_high_threshold_mps` | `0.08` | m/s |
| `minimum_segment_points` | `2` | count |
| `minimum_cell_repeats` | `3` | count |
| `minimum_confidence` | `0.5` | — |
| `extrapolation_allowed` | `false` | — |

## Non-Goals

This specification does NOT cover:
- Real-time compensation loops
- ROS2 node implementation
- Multi-surface blending
- Dynamic surface detection
- Battery-state-aware compensation
- Payload-aware compensation
- Navigation integration
- Online learning or adaptation

## Phase Gates

| Gate | Value |
|------|-------|
| `implementation_ready` | `false` |
| `compensation_ready` | `false` |
| `k1_compensation_validated` | `false` |

## Next Milestone

**M22-C**: Offline velocity compensator prototype — implement this specification as a Python module without robot execution.
