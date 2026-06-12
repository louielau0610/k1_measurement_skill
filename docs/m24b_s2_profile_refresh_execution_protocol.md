# M24-B S2 Profile Refresh Execution Protocol

M24-B is the execution pack for the M24-A direct-only profile refresh design. It prepares the robot-side process for measuring current Booster K1 response on `S2_marble_floor`.

## Physical Setup

- Robot: Booster K1.
- Surface: `S2_marble_floor` only.
- Area: clear straight-line path with enough braking distance.
- State source: ROS2 `/odometer_state`; IMU yaw may be logged as a cross-check.
- Command path: Booster SDK prepare, walking, direct `Move(vx, 0, 0)`, stop.

## Trial Scope

- Conditions: `direct_refresh` only.
- No compensated commands.
- Command velocities: `0.35`, `0.40`, `0.45`, `0.50`, `0.55`, `0.60` m/s.
- Repeats: 5 per command velocity.
- Planned trials: 30.

## Safety Checks

Before each trial:

- Confirm the robot is stable and in a safe start pose.
- Confirm the S2 marble surface is clear.
- Confirm the operator has stop control.
- Confirm the trial shown by the runner matches `direct_refresh`.
- Confirm no profile files are being edited during the run.

The runner defaults to dry-run. Hardware movement requires `--execute` and a per-trial permit prompt unless the operator explicitly disables the prompt.

## Valid Trial

A valid trial has:

- one `trial_records.csv` row marked `executed` and `valid=true`;
- one state log CSV in `state_logs/`;
- `surface=S2_marble_floor`;
- `condition=direct_refresh`;
- non-empty measured actual velocity after extraction;
- non-empty odometer yaw drift after extraction;
- extraction status `ok`.

## Invalid Trial

Mark a trial invalid if:

- the operator skips it;
- the SDK sender fails;
- the logger fails;
- the state log is missing or too short;
- the robot does not execute the intended direct command;
- any compensated condition appears;
- surface is not `S2_marble_floor`.

## Profile Boundary

No K1 profile is updated during M24-B. `k1_gold_profile_v1` must remain unchanged. M24-B can produce logs, extraction outputs, and QC outputs only. Profile comparison and any versioned profile decision belong to M24-C.

## Claim Boundary

M24-B does not claim compensation improvement, deployment readiness, physical compensation validation, or GO1/G1 validation. The revised compensator remains offline-only.
