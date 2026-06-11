# M22-A Research Basis

M22-A records the principle and design basis for velocity compensation before implementation.

## Control Principle

Feedforward compensation uses an estimate of the system response to choose an input that should reduce tracking error. In this project, the measured forward response is:

```text
v_actual = f(u_cmd, surface, platform)
```

The compensation target is an inverse command:

```text
u_compensated = f_inverse(v_desired, surface, platform)
```

This is an inverse-model or feedforward command-remapping problem. It is not a feedback controller, navigation stack, or path planner.

## Deadzone and Input Nonlinearity

Deadzone behavior is an input nonlinearity: some low commands produce little or no measured motion. The K1 gold profile includes deadzone-labeled low-speed cells, so the first compensator must explicitly handle infeasible low desired velocities.

Deadzone handling should be conservative:

- identify the minimum effective command per surface
- return `infeasible_deadzone` below the feasible measured range
- optionally report the nearest feasible measured velocity
- avoid automatic command jumps into drift-prone or unstable regions

## Interpolation Basis

The K1 dataset is sparse: eight command speeds, three surfaces, three repeats per cell. A first implementation should prioritize inspectability over smoothness.

Shape-preserving monotonic interpolation, including PCHIP-like methods, can be useful when the response is monotonic and sufficiently sampled. However, non-monotonic measured data and risk-labeled cells require conservative handling. For M22-A, PCHIP is a later option rather than the first implementation target.

## Measurement Dependency

Compensation requires measurement data because the inverse map must be grounded in observed behavior. The measurement contract v1.0 and K1 gold profile provide the required inputs for Booster K1 only:

- platform and robot identity
- surface labels
- command velocity
- measured actual velocity
- repeated-trial uncertainty
- yaw drift
- risk or region label

GO1 and G1 do not have validated measurement profiles, so they must return `platform_not_calibrated` or `surface_not_calibrated` in any future compensation API until Step 4 data exists.

## First K1 Design Target

The next implementation milestone should specify an offline, dry-run K1 compensator that:

- consumes `measurement_v1.0` contract data or the K1 gold profile
- operates per surface
- uses only K1 measured data
- performs inverse lookup on reliable or explicitly acceptable monotonic segments
- avoids extrapolation by default
- rejects deadzone targets when necessary
- returns structured feasibility status
- includes expected actual velocity, expected error, confidence, and risk reason
- remains offline until Step 3 physical validation

## Phase Gate

M22-A does not implement any code that remaps commands. It only documents the principle, compares options, and defines a decision framework for M22-B.
