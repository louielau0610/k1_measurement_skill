# K1 Velocity Measurement Skill

This repository is the measurement-stage predecessor of the larger **K1 Velocity Measurement, Compensation and Navigation Safety Pipeline**.

The larger project addresses a practical robotics issue on Booster Robotics K1: commanded forward velocity (`v_cmd`) can differ from actual executed velocity (`v_actual`). During navigation, this mismatch can accumulate into position error, trajectory drift, and collision risk.

This repository implements only:

```text
v_x_cmd -> v_x_actual measurement
```

It does not implement velocity compensation, autonomous navigation, real-time closed-loop control, real robot movement commands, or hard-coded unverified ROS2 topic names.

The primary downstream interface is:

```text
processed_environment_profile.json
```

This profile is intended for later modules such as velocity compensation models, safe command adapters, navigation safety layers, and simulation validation pipelines. Downstream users must check confidence, valid speed range, environment match, sample size, and extrapolation risk before using a profile.

## Data Interface Contract

`processed_environment_profile.json` is the downstream contract between this measurement repository and future compensation or navigation safety modules.

The schema is defined in:

```text
contracts/measurement_profile_schema.json
```

A dummy validation-only example is provided at:

```text
examples/dummy_processed_environment_profile.json
```

This repository does not implement compensation. Future downstream modules may consume the profile, but they must validate schema version, environment match, speed range, confidence, trial count, ground-truth method, odom validation status, extrapolation policy, and warnings before use.
