# Step 2: Velocity Compensation Research Plan

**Status**: Planning only. No implementation has started.
**Prerequisite**: Step 1 measurement module (complete).
**Depends on**: K1 gold profile, measurement contract v1.0.

## Objective

Step 2 studies the **velocity compensation principle** and develops an **implementation design** without physically validating it on the robot. Physical validation is Step 3.

## Research Questions

1. Given a desired actual forward velocity $v_{desired}$, what command velocity $v_{cmd}$ should be sent such that $v_{actual} \approx v_{desired}$?
2. How does the compensation mapping vary across surfaces?
3. How should uncertainty in the forward response model propagate to compensated commands?
4. When is compensation feasible, and when should it be refused?

## Topics to Study

### 1. Forward Response Model

Characterize the forward relationship from K1 measurement data:

$$v_{actual} = f(v_{cmd}, \text{surface})$$

- Use the 72-trial K1 gold profile (8 command velocities × 3 surfaces × 3 repeats).
- Fit per-surface models: linear, piecewise-linear, spline, or lookup-based.
- Report goodness-of-fit and residual statistics.
- Identify velocity regions with high variance or systematic bias.

### 2. Inverse Mapping

Compute the compensated command:

$$v_{cmd\_compensated} = f^{-1}(v_{desired}, \text{surface})$$

- For monotonic response regions: direct inversion.
- For non-monotonic regions: select the command that minimizes $|f(v_{cmd}) - v_{desired}|$.
- Handle edge cases: $v_{desired}$ below minimum achievable velocity, above maximum.

### 3. Interpolation

The K1 profile has only 8 command velocities. For continuous compensation:

- Interpolate between measured points (linear, cubic, or model-based).
- Document interpolation error bounds.
- Consider whether more measurement points are needed before physical validation.

### 4. Monotonicity and Non-Monotonic Cases

- Detect whether $f(v_{cmd})$ is monotonic on each surface.
- For non-monotonic regions (e.g., stick-slip at low speeds), define a selection policy:
  - Conservative: pick the lowest $v_{cmd}$ that achieves at least $v_{desired}$.
  - Minimal-error: pick the $v_{cmd}$ that minimizes tracking error.

### 5. Deadzone Handling

- Estimate the minimum command velocity that produces measurable motion per surface.
- Below deadzone: either refuse compensation or apply a minimum-viable-command policy.
- Document per-surface deadzone estimates with uncertainty.

### 6. Risk-Aware Command Selection

- Use M16 risk region labels (low, moderate, high, unreliable) per surface-speed cell.
- In high-risk or unreliable regions: refuse compensation, fall back to un-compensated command.
- In moderate-risk regions: apply compensation with warning.
- In low-risk regions: apply compensation normally.

### 7. Uncertainty-Aware Compensation

- Propagate response uncertainty ($\sigma_{actual}$) to compensated command uncertainty ($\sigma_{cmd}$).
- Provide confidence labels for compensated commands.
- When uncertainty exceeds threshold: refuse compensation.

## Feasibility Status

| Condition | Required for Compensation | Status |
|-----------|--------------------------|--------|
| Forward response data | Yes | ✅ K1 gold profile available |
| Per-surface measurements | Yes | ✅ 3 surfaces, 72 trials |
| Monotonicity analysis | Yes | ❌ Not yet performed |
| Deadzone characterization | Yes | ❌ Not yet performed |
| Inverse mapping method | Yes | ❌ Not designed |
| Uncertainty propagation | Recommended | ❌ Not designed |
| Risk region integration | Recommended | ❌ Not designed |
| Physical validation | Step 3 | ❌ Step 3 (future) |

## Why K1 Physical Validation Is Step 3, Not Step 2

Step 2 is **desk research and implementation design**. It produces:

- Mathematical formulation of the compensation mapping.
- Python implementation of forward model fitting and inverse computation.
- Unit tests with synthetic and K1 measurement data.
- Documentation of assumptions, limitations, and failure modes.

Step 3 will:

- Deploy the compensator on the physical K1 robot.
- Run compensated trials and measure actual velocities.
- Compare compensated vs. uncompensated tracking error.
- Iterate on the model based on physical results.

Separating design (Step 2) from validation (Step 3) prevents premature claims and ensures the compensator is well-understood before robot testing.

## Why GO1/G1 Generalization Is Step 4

- GO1 and G1 have **different kinematics, different SDKs, and different state sources**.
- They need their **own measurement data** before compensation can be applied.
- The measurement contract (M21-C) defines what GO1/G1 must produce, but no data exists yet.
- After K1 compensation is validated (Step 3), the same methodology can be applied to GO1/G1 — but only after their measurement modules are complete.

## Deliverables (Step 2)

1. Forward response model fitting module.
2. Inverse mapping computation module.
3. Interpolation strategy with error bounds.
4. Monotonicity analysis report.
5. Deadzone estimation per surface.
6. Risk-aware command selection policy.
7. Uncertainty propagation method.
8. Unit tests for all modules.
9. Step 2 research report documenting findings and design decisions.

## What Step 2 Does NOT Do

- ❌ Send compensated commands to a physical robot.
- ❌ Claim compensation works on K1.
- ❌ Claim compensation works on GO1/G1.
- ❌ Implement a real-time compensation node.
- ❌ Integrate with navigation or path planning.
- ❌ Publish a paper claiming compensation novelty.
