# Measurement Module v1

The measurement module is the first standalone stage in the corrected calibration roadmap. Its job is to produce trustworthy robot velocity and yaw-drift evidence before any velocity compensation work begins.

## Purpose

The module turns controlled robot velocity trials into reusable measurement artifacts:

- raw state logs from a validated logger
- per-trial extracted measurements
- QC summaries and reports
- surface-speed response statistics
- calibration or gold profiles for later research phases

For M21-A, Booster K1 is the only physically validated measurement reference. Unitree GO1 and Unitree G1 remain scaffold-only platforms.

## Inputs

- Robot command adapter: prepares the platform-specific command path for a trial schedule.
- State logger: records the validated state source for position and yaw.
- Trial schedule: lists surfaces, commanded speeds, repeats, and deterministic trial IDs.
- Surface configuration: defines the tested environments or surface IDs.

## Outputs

- Raw state logs, such as the Booster K1 ROS2 `/odometer_state` CSV logs.
- Extracted measurements with `measured_actual_velocity` and `yaw_drift_statistic`.
- QC reports that check completeness, extraction status, and evidence readiness.
- Response statistics by surface-speed cell.
- Calibration/gold profile exports for downstream analysis.

## Boundary

The measurement module does not:

- implement velocity compensation
- remap commands
- claim navigation improvement
- claim cross-platform empirical validity unless each platform has its own real dataset
- fabricate measurements from command speed
- mark GO1 or G1 as hardware validated

The next research phase after measurement module closure is to study and implement the velocity compensation principle, then validate it experimentally on Booster K1 before any GO1/G1 generalization.
