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
