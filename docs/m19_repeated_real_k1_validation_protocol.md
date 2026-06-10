# M19-A Repeated Real K1 Validation Protocol

> **Infrastructure only. No robot access. No repeated real logs exist yet.**

## Purpose

Define the repeated validation protocol for the K1 velocity response pipeline. Real repeated trials will be performed manually later by the user. The infrastructure is ready to ingest real data when available.

## Experiment design (future manual execution)

- 1 physical Booster K1 robot.
- 1 baseline environment first (documented surface type).
- 8 command velocities: 0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60 m/s.
- Preferred: 5 repeated trials per command velocity.
- Minimum acceptable: 3 valid trials per command velocity.
- Minimum baseline experiment size: 8 speeds * 5 trials = 40 trials.

## Required trial fields

Each future trial record must include:
- trial_id, session_id, robot_id, environment_id, environment_description, surface_type
- command_velocity (m/s), measured_actual_velocity (m/s)
- yaw_drift_statistic (deg/s), trial_duration_sec
- valid (bool), invalid_reason (string or null)
- raw_log_path, normalized_record_path
- timestamp (ISO date), notes

## Optional extensions (future work)

- Single K1 across multiple surfaces/environments.
- Multi-K1 validation (cross-robot).
- Cross-platform validation.

## Claim boundaries

- Single-K1 evidence supports only a platform-specific case study.
- Does not prove cross-robot generalization.
- Multi-robot validation is not required for current milestone.
- Compensation controller and safe command adapter are outside M19-A scope.

## Current status

- M19-A infrastructure implemented.
- Repeated real K1 validation: **PENDING**.
- No repeated real logs found in repository.
- Analyzer runs in pending-data mode.
