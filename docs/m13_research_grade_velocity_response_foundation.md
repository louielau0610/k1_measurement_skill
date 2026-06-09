# M13 Research-Grade Velocity Response Foundation

M13 defines the research foundation for modeling the measured forward velocity response of the Booster K1 platform. It does not start literature review, does not claim experimental findings, and does not implement downstream compensation or navigation behavior.

## Research Problem

The working measurement problem is:

```text
v_actual = f(v_cmd, environment, robot_state)
```

The immediate research question is whether repeatable field measurements can characterize the difference between commanded forward velocity and realized forward velocity under documented environment and robot-state conditions.

The repository scope remains measurement-first:

- define the data needed for velocity response modeling;
- preserve raw and normalized measurement provenance;
- document environment and robot-state context;
- expose confidence and limitation metadata;
- keep downstream use explicitly separated from measurement artifacts.

## Non-Claims

M13 does not claim that K1 velocity response has been experimentally identified. Existing dummy data and schema fixtures are pipeline checks only.

M13 does not claim publication readiness. Literature review, related-work synthesis, empirical evidence, and final paper drafting remain future work.

## Modeling Plan For Chapter 2

Chapter 2 should formulate velocity response as a measurable input-output relationship rather than as a controller implementation.

Planned structure:

1. Define the measured variables: commanded forward velocity, measured forward velocity, environment descriptors, robot-state descriptors, timing, and trial quality flags.
2. Define the response quantities: mean realized velocity, variance, absolute error, relative error, transient behavior, and trial repeatability.
3. Define data requirements: repeated trials per command value, fixed lateral and yaw commands at zero for the forward baseline, documented ground truth method, and explicit exclusion handling.
4. Define model families only as analysis candidates: lookup/curve fit, piecewise linear response, monotonic regression, uncertainty-aware summary statistics, and environment-conditioned comparison.
5. Define evidence boundaries: analysis-ready datasets may support measurement claims; they do not imply compensation safety, inverse command validity, navigation performance, or publication readiness.

## Dataset Schema V1

The schema at `configs/velocity_response_dataset_schema_v1.json` defines the first research-grade dataset contract. It requires:

- dataset identity, timestamp, and research problem metadata;
- robot metadata without hard-coding unconfirmed K1 topics;
- environment and ground-truth descriptors;
- acquisition provenance for raw logs, normalized logs, and topic mapping;
- forward-only command grid with `vy_cmd_mps = 0` and `wz_cmd_rps = 0`;
- per-trial measured velocity response fields;
- quality metadata, limitations, and exclusions;
- downstream boundary flags fixed to `false`.

`battery_state` is optional inside per-trial `robot_state`. `remote_controller_state` is permanently out of scope and is not present in the schema.

## Validation

The CLI validator at `scripts/validate_velocity_response_dataset_schema.py` checks that the schema is a valid Draft 2020-12 JSON Schema, rejects prohibited schema fields, and confirms that `battery_state` has not become required. It can also validate a dataset JSON file when `--dataset` is supplied.

Required M13 validation command:

```powershell
py scripts/validate_velocity_response_dataset_schema.py --schema configs/velocity_response_dataset_schema_v1.json
```
