# M19R-C Prep SDK State Logger Protocol

M19R-C-prep prioritizes SDK state logging because the current ROS CLI shell cannot resolve the Booster motion-state message type, while the Python SDK appears to expose odometer, IMU, low-state, frame, and transform APIs.

## Acceptable SDK State Sources

Priority 1: `B1LocoClient.GetFrameTransform(src, dst, transform)` when it returns 0 and exposes position/yaw-bearing transform fields.

Priority 2: `B1OdometerStateSubscriber` when it yields timestamped position and heading samples.

Priority 3: `B1LowStateSubscriber` / `ImuState` when yaw can be recovered and paired with a position source.

Manual video annotation remains a fallback, not the preferred path, because SDK state logs can provide timestamped position and yaw from the robot interface.

## Measurement Computation

For each trial, use SDK state samples in the analysis window `[1.0, 6.0]` seconds after command start.

Actual velocity is computed from forward displacement projected onto the starting yaw:

```text
distance_m = dot([x_end - x_start, y_end - y_start], [cos(yaw_start), sin(yaw_start)])
measured_actual_velocity = distance_m / time_sec
```

Yaw drift is the absolute wrapped yaw change:

```text
yaw_drift_statistic = abs(wrap_to_180(yaw_end_deg - yaw_start_deg))
```

## Evidence Boundary

Prior M19 execution-only trials cannot be retroactively converted into empirical measurements unless matching SDK logs, parseable raw logs, or valid video/manual measurement evidence exists. Command velocity must never be copied into `measured_actual_velocity`.

## Decision Gate

The full M19C measurement run is ready only when a standing SDK smoke log confirms a usable state source with enough timestamped position and yaw fields, and a short dynamic smoke trial can be logged safely. This prep milestone does not compute response statistics, validate the risk map, or claim M19 empirical completion.
