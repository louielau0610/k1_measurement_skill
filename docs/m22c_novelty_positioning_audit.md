# M22-C Novelty and Positioning Audit

M22-C implements an offline prototype. It is not a physical validation milestone and does not claim deployment-ready compensation.

## Not Novel By Itself

- Generic feedforward compensation
- Generic inverse-model compensation
- Generic deadzone compensation
- Generic velocity tracking for robots
- Interpolation over measured response points

## Project-Specific Framing

The defensible contribution is a practical engineering framework:

- measurement-contract-driven compensation
- black-box SDK-level velocity command remapping
- surface-aware legged robot velocity response profiles
- risk-aware inverse lookup using deadzone, yaw drift, uncertainty, and region labels
- a cross-platform measurement contract foundation for Booster K1, Unitree GO1, and Unitree G1

The framework operates above the robot's low-level locomotion controller. It uses measured command-to-actual response data and refuses unsupported surfaces or platforms.

## Current Novelty Status

`engineering_novelty_plausible_but_requires_K1_physical_validation`

## Paper Claim Level

`idea_and_system_design_only`

## Physical Validation

`not_started`

M22-C creates an offline decision prototype only. K1 physical validation is Step 3. GO1/G1 generalization is Step 4 and requires their own measurement data first.
