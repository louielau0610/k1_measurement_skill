# Velocity Compensation Principle

M22-A starts Step 2 of the roadmap: research and design for velocity compensation. It does not implement a compensator, command remapping, or any robot experiment.

## Forward Response

The measurement module estimates the forward response:

```text
u_cmd -> v_actual
```

where `u_cmd` is the commanded forward velocity and `v_actual` is the measured forward velocity from the validated state source. For Booster K1, the current evidence is the M19C-E gold profile built from 72 ROS2 odometer trials across three surfaces.

The forward response is surface-dependent. A command that works on one surface may land in a deadzone, drift-prone region, or unstable region on another surface. This is why compensation must consume measured response data and risk labels rather than relying on nominal command speed.

## Inverse Compensation Target

The intended compensation problem is the inverse lookup:

```text
v_desired -> u_compensated
```

The target is to recommend a command velocity that is expected to produce a desired actual velocity on a specific platform and surface. This is feedforward command remapping: it changes the input command before execution based on a measured response model.

It is not navigation. It does not choose paths, avoid obstacles, reason about goals, or claim a navigation improvement. Navigation systems may eventually consume a compensated command interface, but that is outside M22-A.

## Formal Problem Statement

Given:

- platform
- robot model
- surface
- desired actual velocity
- measured response profile
- risk labels
- uncertainty estimates

Compute:

- recommended command velocity
- expected actual velocity
- expected error
- confidence
- feasibility status
- risk reason

The eventual API should support these feasibility statuses:

- `ok`
- `feasible_but_risky`
- `infeasible_deadzone`
- `infeasible_out_of_range`
- `insufficient_evidence`
- `platform_not_calibrated`
- `surface_not_calibrated`

## Why Measurement Comes First

Inverse compensation is only meaningful after the forward response is measured. Without real measured data, a compensator would be guessing. In particular:

- deadzone behavior cannot be inferred from command speed alone
- yaw drift and unstable cells must affect feasibility
- uncertainty must be estimated from repeated measurements
- each platform and surface needs its own evidence

Step 1 closed the measurement module and established Booster K1 as the only validated measurement reference. GO1 and G1 do not yet have validated measurement data, so they cannot receive compensation claims.

## Phase Boundary

Step 2 is research and design. It may specify algorithms, feasibility rules, and test expectations, but M22-A does not create a compensator implementation.

Step 3 is physical Booster K1 validation. Only after a dry-run algorithm is implemented and tested offline should compensated commands be evaluated on hardware.

Step 4 is GO1/G1 generalization. It requires platform-specific measurement modules and real data before applying the compensation method.
