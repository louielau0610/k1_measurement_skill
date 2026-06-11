# M23-A: K1 Physical Compensation Experiment Design

**Status**: Experiment design only. No hardware execution.
**Physical validation**: `not_started`
**Deployment ready**: `false`

## Objective

Design a paired before/after experiment that tests whether the M22-C offline velocity compensator reduces tracking error on a physical Booster K1 robot, compared to direct (uncompensated) command.

## Hypotheses

- **H0 (null)**: Compensated commands do not reduce absolute velocity tracking error compared to direct commands.
- **H1 (alternative)**: Compensated commands reduce mean absolute velocity tracking error compared to direct commands, without significantly increasing yaw drift or invalid trial rate.

## Experimental Design

### Paired Before/After Structure

For each surface and desired velocity, run a **matched pair** of trials:

1. **Direct command trial**: `u_cmd = v_desired` (baseline)
2. **Compensated command trial**: `u_cmd = offline_compensator(v_desired)` (M22-C output)

Each pair is one comparison unit. Pairs are repeated to estimate within-condition variance.

### Rationale for Paired Design

- Controls for battery state, floor condition, and time drift within each pair.
- Reduces between-trial variance compared to independent groups.
- Enables paired statistical tests (t-test or Wilcoxon) with small sample sizes.

## Surfaces

| Surface | Priority | Rationale |
|---------|----------|-----------|
| `S2_marble_floor` | **Primary** | M19C showed usable response with compensation-relevant behavior (moderate under-tracking, acceptable yaw drift). |
| `S1_lab_hard_floor` | Optional | Higher friction; may show different compensation behavior. |
| `S3_artificial_turf` | Optional | Highest friction; may challenge deadzone and low-speed compensation. |

**Recommendation**: Complete S2_marble_floor first. Expand to S1/S3 only if time and battery permit.

## Desired Velocity Set

Avoid pure deadzone and extreme out-of-range. Use velocities where M19C data shows measurable response:

| v_desired (m/s) | Rationale |
|-----------------|-----------|
| 0.30 | Lower bound — above deadzone, measurable response on S2 |
| 0.35 | Intermediate |
| 0.40 | Mid-range |
| 0.45 | Mid-range |
| 0.50 | Upper-mid range |
| 0.55 | Upper range — near max tested on S2 |

**Excluded**: 0.10–0.25 (deadzone/inconsistent), 0.60+ (out-of-range or high uncertainty).

## Conditions

### Direct Command (Baseline)

- `u_cmd = v_desired`
- No compensation applied.
- Represents current uncalibrated behavior.

### Compensated Command (M22-C)

- `u_cmd = offline_compensator(v_desired, surface=S2_marble_floor, risk_policy=balanced)`
- Uses M22-C Conservative Monotonic Segment Inverse Lookup.
- Risk policy: **balanced** (allows under_track cells; conservative may reject too many on S2).
- Extrapolation: **reject** (default).
- If compensator returns infeasible, record the trial as `infeasible_compensation` and do not force a command.

## Repeats

| Level | Minimum | Recommended |
|-------|---------|-------------|
| Paired repeats per desired velocity | 3 | 5 |
| Total trial pairs (6 velocities × 3 repeats) | 18 | 30 |
| Total individual trials | 36 | 60 |

## Trial Randomization

1. **Randomize desired velocity order**: Shuffle the 6 desired velocities.
2. **Randomize condition order within each pair**: For each repeat, randomly assign which condition (direct or compensated) runs first. If randomization is infeasible on the robot, alternate:
   - Pair 1: direct → compensated
   - Pair 2: compensated → direct
   - etc.
3. **Document randomization seed** for reproducibility.

## Paired Comparison Structure

```
Surface: S2_marble_floor
Desired velocity: 0.40 m/s
Repeat 1:
  Pair 1a: direct  (u_cmd = 0.40)     → measure v_actual_direct
  Pair 1b: compensated (u_cmd = 0.52)  → measure v_actual_compensated
  Compare: |v_actual_direct - 0.40| vs |v_actual_compensated - 0.40|
Repeat 2:
  Pair 2a: compensated (u_cmd = 0.52)  → measure v_actual_compensated
  Pair 2b: direct (u_cmd = 0.40)       → measure v_actual_direct
  ...
```

## Primary Metric

**Absolute velocity tracking error**:

$$\epsilon = |v_{actual} - v_{desired}|$$

Compare per-pair:
- $\epsilon_{direct}$ (baseline)
- $\epsilon_{compensated}$ (M22-C)

Report:
- Mean absolute error (MAE)
- Median absolute error
- Maximum absolute error
- Per-velocity breakdown
- Percent reduction: $100 \times (1 - \epsilon_{comp} / \epsilon_{direct})$

## Secondary Metrics

| Metric | Purpose |
|--------|---------|
| `yaw_drift_deg` | Verify compensation does not worsen yaw stability |
| `invalid_trial_rate` | Count trials lost to slip, collision, or sensor failure |
| `no_motion_rate` | Count trials where no measurable motion occurred |
| `compensated_cmd_risk_status` | How often the compensator returns risky/infeasible |
| `command_magnitude_increase` | How much larger compensated commands are than direct |
| `yaw_drift_change` | Per-pair difference in yaw drift |

## Success Condition

Compensated condition is considered successful if:

1. **Mean absolute tracking error is lower** for compensated vs. direct.
2. **Yaw drift does not significantly increase** (no systematic worsening).
3. **Invalid trial rate does not increase** (compensation does not cause more failures).
4. **Infeasible targets are rejected** rather than forced (no dangerous extrapolation).

## Invalid Trial Rules

A trial is invalid if:
- Robot collides with obstacle.
- Robot slips or loses traction (operator judgment).
- State log is corrupted or missing.
- ROS2 odometer data is unavailable for the command window.
- Operator aborts the trial.

Invalid trials are recorded with explicit `invalid_reason`. They are excluded from paired analysis for that desired velocity but documented in the trial log.

## Yaw Drift Guard

If `yaw_drift_deg > 15°` during a compensated trial:
- Flag the trial as `high_yaw_drift_warning`.
- Do not automatically invalidate, but note in analysis.
- If > 3 trials exceed this threshold for a given velocity, reconsider compensation for that velocity.

## Stop Procedure

1. Complete all planned pairs for a surface.
2. If battery < 20%, pause and recharge.
3. If 2 consecutive invalid trials occur, investigate cause before continuing.
4. If yaw drift systematically exceeds 15° for > 50% of compensated trials, stop and reassess.

## Data Collection Requirements

Per trial:
- ROS2 `/odometer_state` log (CSV, same format as M19C)
- ROS2 `/low_state.imu_state.rpy` log (if available)
- Trial metadata: trial_id, pair_id, surface, desired_velocity, condition, command_velocity, timestamp
- Operator notes

## Extraction and QC Plan

1. Extract `measured_actual_velocity_mps` using the M21-B measurement extractor.
2. Extract `yaw_drift_deg` per trial.
3. Run M21-B QC on the session directory.
4. Validate against measurement contract v1.0.
5. Flag any trials with `extraction_status != ok`.

## Analysis Plan

### Paired Error Comparison

For each desired velocity, compute per-pair error difference:

$$\Delta\epsilon_{pair} = \epsilon_{direct} - \epsilon_{compensated}$$

Positive $\Delta\epsilon$ means compensation improved tracking.

### Per-Surface Summary

Aggregate all pairs on a surface:
- Mean $\Delta\epsilon$
- Median $\Delta\epsilon$
- Percent of pairs where compensation improved tracking
- Mean yaw drift difference

### Per-Desired-Velocity Summary

For each velocity, report:
- Mean direct error
- Mean compensated error
- Percent reduction
- Number of infeasible compensated targets

### Statistical Tests

- **Paired t-test**: If error differences are approximately normal.
- **Wilcoxon signed-rank test**: Small-sample/nonparametric alternative (recommended for n=3–5 pairs).
- **Effect size**: Cohen's d or rank-biserial correlation.

### Claim Levels

| Result | Claim Level |
|--------|-------------|
| $\Delta\epsilon > 0$ significant (p < 0.05) on S2 | Compensation reduces tracking error on marble floor (single surface, single robot) |
| $\Delta\epsilon > 0$ but not significant | Suggestive but inconclusive; more data needed |
| $\Delta\epsilon \leq 0$ | Compensation does not help on this surface; investigate response model |
| Multi-surface significant improvement | Broader claim; requires S1/S3 data |

### Before/After Plots

To be generated in M23-C:
- Bar chart: mean absolute error per velocity (direct vs compensated)
- Scatter plot: paired errors
- Box plot: error distribution per condition per velocity
- Yaw drift comparison

## Claim Boundaries

| Claim | Status |
|-------|--------|
| Experiment designed | ✅ M23-A |
| Physical trials executed | ❌ M23-B (future) |
| Tracking improvement validated | ❌ M23-C (future) |
| Deployment ready | ❌ Not claimed |
| GO1/G1 compensation | ❌ Not claimed (Step 4) |
