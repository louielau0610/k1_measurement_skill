# M23-A Physical Compensation Result Schema

**Status**: Schema definition only. No physical results exist yet.

Defines the data schema that M23-B (execution) and M23-C (analysis) must fill with real K1 trial data.

## Trial Result Fields

| # | Field | Type | Unit | Description |
|---|-------|------|------|-------------|
| 1 | `trial_id` | string | — | Unique trial identifier |
| 2 | `pair_id` | string | — | Pair identifier linking direct and compensated trials |
| 3 | `surface` | string | — | Surface identifier (e.g., `S2_marble_floor`) |
| 4 | `desired_velocity_mps` | float | m/s | Desired actual velocity |
| 5 | `condition` | string | — | `direct` or `compensated` |
| 6 | `command_velocity_mps` | float | m/s | Command velocity sent to robot |
| 7 | `measured_actual_velocity_mps` | float | m/s | Extracted actual velocity |
| 8 | `absolute_tracking_error_mps` | float | m/s | `|measured - desired|` |
| 9 | `relative_tracking_error` | float | — | `(measured - desired) / desired` |
| 10 | `yaw_drift_deg` | float | degrees | Yaw drift during command window |
| 11 | `imu_yaw_drift_deg` | float | degrees | IMU yaw drift (if available) |
| 12 | `extraction_status` | string | — | `ok`, `invalid_trial`, `missing_log`, etc. |
| 13 | `invalid_reason` | string | — | Reason if trial invalid |
| 14 | `state_log_path` | string | — | Path to per-trial state log CSV |
| 15 | `compensation_decision_path` | string | — | Path to compensator JSON decision (compensated trials only) |
| 16 | `physical_run_status` | string | — | `executed`, `skipped`, `aborted`, `infeasible_compensation` |
| 17 | `notes` | string | — | Operator notes |

## Compensation Decision Fields (for compensated trials)

Each compensated trial references a compensator decision JSON with fields from M22-C:

| Field | Description |
|-------|-------------|
| `recommended_command_velocity_mps` | Command velocity computed by compensator |
| `expected_actual_velocity_mps` | Predicted actual velocity |
| `expected_tracking_error_mps` | Predicted error |
| `feasibility_status` | `ok`, `feasible_but_risky`, `infeasible_deadzone`, etc. |
| `region_label` | Risk region of selected cell |
| `risk_score` | Risk score |
| `confidence` | Confidence in recommendation |
| `reason` | Human-readable explanation |
| `warnings` | Active warnings |

## Pair-Level Summary Fields

After both trials in a pair are complete, compute:

| Field | Formula |
|-------|---------|
| `error_direct_mps` | `|measured_direct - desired|` |
| `error_compensated_mps` | `|measured_compensated - desired|` |
| `error_difference_mps` | `error_direct - error_compensated` (positive = improvement) |
| `percent_reduction` | `100 * error_difference / error_direct` |
| `yaw_drift_direct_deg` | Yaw drift in direct trial |
| `yaw_drift_compensated_deg` | Yaw drift in compensated trial |
| `yaw_drift_difference_deg` | `yaw_drift_compensated - yaw_drift_direct` |
| `pair_valid` | Both trials valid and extracted successfully |

## Analysis Output Schema

To be produced by M23-C:

```json
{
  "experiment_id": "m23a_k1_compensation_s2_marble",
  "surface": "S2_marble_floor",
  "pairs_total": 18,
  "pairs_valid": 18,
  "pairs_with_improvement": 15,
  "mean_error_direct_mps": 0.085,
  "mean_error_compensated_mps": 0.042,
  "mean_error_difference_mps": 0.043,
  "median_error_difference_mps": 0.038,
  "percent_mean_reduction": 50.6,
  "wilcoxon_p_value": 0.002,
  "effect_size": 0.78,
  "yaw_drift_mean_direct_deg": 3.2,
  "yaw_drift_mean_compensated_deg": 3.5,
  "yaw_drift_change_deg": 0.3,
  "infeasible_compensation_count": 0,
  "invalid_trial_count": 0,
  "claim_level": "compensation_reduces_tracking_error_single_surface"
}
```

> **Note**: Values above are illustrative schema examples only — not physical results.
