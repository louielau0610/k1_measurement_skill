# M21 Pre-Session Checklist v1

> Complete before the first trial of any future K1 data collection session. All items are yes/no or TO_BE_FILLED.

## Protocol version check

- [ ] M20 protocol version confirmed (v1.0.0).
- [ ] M21 data collection pack version confirmed (v1).
- [ ] Experiment tier identified (1/2/3/4).

## Site and environment

- [ ] Surface type documented: TO_BE_FILLED.
- [ ] Workspace clear of hazards.
- [ ] Lighting adequate for video recording (if used).
- [ ] Test area dimensions: TO_BE_FILLED (SITE_SPECIFIC).

## Robot and hardware

- [ ] Robot model: TO_BE_FILLED.
- [ ] Robot battery charged: TO_BE_FILLED.
- [ ] `battery_state` recording method: OPTIONAL_IF_AVAILABLE.
- [ ] No `remote_controller_state` will be recorded.
- [ ] Robot in operational mode (not firmware update).
- [ ] Emergency stop accessible and tested.

## Sensor and logging readiness

- [ ] ROS2 network available (read-only subscriber only).
- [ ] Command topic identified: TO_BE_FILLED.
- [ ] Odometry topic identified: TO_BE_FILLED.
- [ ] IMU topic (optional): TO_BE_FILLED.
- [ ] Rosbag recording tested.
- [ ] Storage sufficient for all trials.
- [ ] Backup storage plan confirmed.

## Command grid review

- [ ] Forward velocity grid: TO_BE_FILLED (from design matrix).
- [ ] Held-out split defined (if Tier 2): TO_BE_FILLED.
- [ ] Trial order randomized or planned.

## Navigation task review (if Tiers 3/4)

- [ ] Task definitions printed: TO_BE_FILLED.
- [ ] Obstacle/course layout documented: TO_BE_FILLED.
- [ ] Baseline/advisory condition assigned per task.

## Operator roles

- [ ] Operator 1 (command issuer): TO_BE_FILLED.
- [ ] Operator 2 (logger): TO_BE_FILLED.
- [ ] Safety spotter: TO_BE_FILLED.

## Safety boundary reminders

- [ ] No velocity compensation will be attempted.
- [ ] No inverse command mapping will be attempted.
- [ ] No navigation control will be attempted.
- [ ] No safe command adapter will be used.
- [ ] Advisory risk labels are advisory only (Tiers 3/4).

## Pre-session confirmation

- [ ] All items above checked. Session authorized to begin.
- [ ] Session ID: TO_BE_FILLED.
- [ ] Date: TO_BE_FILLED.
- [ ] Operator signature: TO_BE_FILLED.
