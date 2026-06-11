# Velocity Compensation Design Options

This document compares inverse mapping options for the first velocity compensator. It is a research/design artifact only.

## Recommendation

The first implementation should use conservative piecewise linear inverse mapping over valid monotonic segments, with risk filtering and no extrapolation by default.

Candidate cells should be filtered before inversion:

- prefer `reliable` cells
- allow explicitly acceptable cells only with warning
- avoid `deadzone`, `unstable`, and `drift_prone` cells by default
- reject targets outside the measured feasible range
- return structured feasibility status instead of forcing a command

PCHIP-like interpolation may be considered later after monotonicity and overshoot risks are controlled. Neural models should be deferred because the current K1 dataset is small and physical validation has not been performed.

## A. Nearest-Neighbor Lookup

Assumptions:

- measured command points are representative
- discrete command outputs are acceptable

Advantages:

- simple and transparent
- no interpolation artifacts
- easy to explain in safety reviews

Risks:

- coarse output because K1 has only eight command speeds
- may jump between commands
- may select a risky cell unless filtered first

Required data:

- per-surface measured response statistics
- risk labels and uncertainty estimates

Suitability for current K1 dataset:

- useful as a baseline and fallback

First implementation:

- not the primary method, but useful when interpolation is impossible

## B. Linear Interpolation

Assumptions:

- local response between two measured points is approximately linear
- the selected points are on a monotonic segment

Advantages:

- transparent
- minimal assumptions
- works with sparse data
- easy to bound to measured ranges

Risks:

- invalid if the selected segment is non-monotonic
- can cross through a risky region if filtering is careless
- does not smooth uncertainty by itself

Required data:

- ordered surface-speed response cells
- monotonic segment detection
- risk and uncertainty filtering

Suitability for current K1 dataset:

- best first fit because the dataset is small and the method is inspectable

First implementation:

- recommended over valid monotonic segments only

## C. Monotonic Piecewise Interpolation

Assumptions:

- response can be segmented into locally monotonic regions
- inverse lookup is only performed inside those regions

Advantages:

- handles deadzones and jumps better than a single global model
- avoids pretending the full response is smooth
- supports clear infeasibility statuses

Risks:

- segment boundaries must be chosen conservatively
- sparse data can make segments short
- noisy repeated trials may obscure monotonicity

Required data:

- per-surface aggregate response statistics
- uncertainty estimates
- region labels

Suitability for current K1 dataset:

- strong fit for the first implementation when combined with linear interpolation

First implementation:

- recommended as the governing structure

## D. PCHIP-Like Shape-Preserving Interpolation

Assumptions:

- measured response is monotonic on the interpolation domain
- shape preservation is enough to avoid overshoot

Advantages:

- smoother than linear interpolation
- can preserve monotonicity when inputs satisfy the assumptions

Risks:

- inappropriate on non-monotonic or sparse risky data
- may give a false sense of precision
- inverse behavior still needs careful feasibility checks

Required data:

- denser monotonic measurements or strong monotonic evidence
- overshoot tests

Suitability for current K1 dataset:

- possible future option, not first implementation

First implementation:

- defer

## E. Constrained Optimization Over Measured Candidates

Assumptions:

- selecting from measured candidates is acceptable
- objective can combine tracking error, uncertainty, and risk

Advantages:

- naturally risk-aware
- avoids interpolation between unsafe cells
- clear fallback when monotonic inversion fails

Risks:

- discrete and possibly conservative
- objective weights can hide value judgments
- may pick high command values for low desired speeds unless deadzone rules block it

Required data:

- measured candidate table
- risk labels
- uncertainty and yaw-drift metrics

Suitability for current K1 dataset:

- useful as a fallback or audit policy

First implementation:

- optional fallback after piecewise inverse lookup refuses a target

## F. Learned Regression / Neural Model

Assumptions:

- enough data exists to learn a general response function
- train/test splits reflect real operating conditions

Advantages:

- can model complex nonlinear behavior with enough data
- may eventually include richer robot state

Risks:

- current K1 dataset is too small
- hard to audit for safety
- can extrapolate invisibly
- requires physical validation before trust

Required data:

- much larger multi-session datasets
- validation across surfaces, robot state, and battery conditions

Suitability for current K1 dataset:

- poor for first implementation

First implementation:

- defer

## Deadzone Handling

The K1 gold profile contains deadzone-labeled low command cells where repeated trials produced near-zero measured motion. Low desired velocities may therefore be infeasible: a command below the minimum effective command may not move the robot, while jumping to the next moving command can overshoot or enter a risky region.

The first compensator should define a per-surface minimum effective command from measured cells that are not deadzone and pass risk filtering. For desired velocities below the minimum feasible actual velocity, it should return `infeasible_deadzone`. It may optionally include the nearest feasible target as advisory information, but it must not silently increase the command.

Blindly increasing command can be unsafe if the first moving region is drift-prone or unstable.

## Non-Monotonic and Unstable Response Handling

Measured response may be non-monotonic because of actuator nonlinearities, gait transitions, surface interaction, odometer noise, or stick-slip behavior. A global inverse would be unsafe in this setting.

The first design should:

- split each surface response into monotonic candidate segments
- filter out unstable and drift-prone cells by default
- prefer low-uncertainty cells
- include yaw drift in feasibility and confidence
- reject targets that cannot be reached without using risky cells

Compensation must be risk-aware, not merely error-minimizing.
