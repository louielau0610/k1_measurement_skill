# Problem Statement v1

## 1. Problem motivation

For a closed-source legged robot deployment, the user commands high-level velocity targets (e.g., forward velocity) through an SDK-provided ROS2 topic. The robot's internal locomotion controller translates these commands into joint-level actuation, and the resulting motion is observed through an odometry feedback topic. The mapping from commanded velocity to actual executed motion is not transparent to the user: actuator dynamics, internal control structure, gait transitions, and environmental interactions shape this mapping in ways that may produce systematic mismatch between what is commanded and what the robot achieves.

This mismatch is a deployment-layer problem, not a controller-design problem. When the mismatch is unmeasured or unmodeled, downstream navigation and planning systems may operate on inaccurate assumptions about the robot's motion capability.

## 2. System boundary

```
External (user-accessible):                 Internal (closed-source / SDK-opaque):
┌─────────────────────────┐                ┌──────────────────────────────────┐
│ velocity command topic  │ ── v_cmd ──>  │ locomotion controller            │
│                         │                │   + state estimator               │
│ odometry feedback topic │ <── v_actual ─ │   + actuator drivers              │
│                         │                │   + gait / mode logic             │
│ measurement environment │               │   + sensor processing             │
└─────────────────────────┘                └──────────────────────────────────┘
```

**Observable**: `v_cmd = [v_x^cmd, v_y^cmd, omega_z^cmd]` (commanded body-frame velocity).  
**Observable**: `v_actual = [v_x^actual, v_y^actual, omega_z^actual]` (odometry-derived executed velocity).  
**Observable**: environment descriptor (floor type, session identifier).  
**Not observable**: internal controller state, gain schedule, actuator model, state estimator internals.

The robot is treated as a black-box velocity response system. No internal model, policy, or controller access is assumed.

## 3. Formal variables

```
Command input:  x = [v_x^cmd, v_y^cmd, omega_z^cmd, env, state_optional]
Response output: y = [v_x^actual, v_y^actual, omega_z^actual, r_label, u_label, rho]
```

- `v_x^cmd, v_y^cmd, omega_z^cmd`: commanded body-frame linear and angular velocities.
- `env`: environment descriptor (floor type, session tag).
- `state_optional`: battery, gait, or payload metadata when available (not required).
- `v_x^actual, v_y^actual, omega_z^actual`: odometry-derived actual velocities.
- `r_label`: qualitative response label (e.g., deadzone, weak tracking, under-tracking, stable tracking).
- `u_label`: uncertainty/confidence label (conservative metadata flag).
- `rho`: advisory risk level derived from response and uncertainty labels.

## 4. Response modeling target

```
f(x) -> predicted response + uncertainty label
```

Given command input `x`, the model predicts:

- Predicted actual velocity (point estimate where numeric evidence exists).
- Qualitative response category (for deadzone and qualitative records).
- Uncertainty/confidence label (not a calibrated probability).

The current M15R implementation processes sparse forward-velocity evidence (five records). `v_y` and `omega_z` are schema-supported fields reserved for future measurement expansion.

## 5. Risk mapping target

```
g( f(x) ) -> advisory risk assessment
```

Given model predictions, the risk mapping layer assigns:

- A conservative risk category per command condition.
- Warning metadata: whether the command velocity is near a deadzone, under-tracking, or high-uncertainty.
- Allowed downstream uses (e.g., structural pipeline evidence) and disallowed downstream uses (e.g., navigation control input).

The risk mapping output is offline and advisory. It does not control a robot, modify velocity commands, or trigger safety interventions.

## 6. Current implemented scope

- **Available**: forward velocity evidence (`v_x`) from five Measurement v0 command conditions on one K1 unit, one indoor floor surface.
- **Available**: M15R response predictions, uncertainty labels, and confidence labels (not calibrated).
- **Available**: M16 offline advisory risk map with warning-level metadata.
- **Available**: M17 pipeline evaluation separating structural claims from unsupported performance/safety claims.
- **Not available**: lateral velocity (`v_y`) and angular velocity (`omega_z`) measurement evidence.
- **Not available**: multi-surface, multi-session, or multi-unit K1 data.
- **Not available**: calibrated uncertainty estimates.
- **Not available**: navigation outcome metrics (collision, near-miss, success rate).
- **Not implemented**: velocity compensation, inverse command mapping, safe command adapter, navigation controller.

## 7. Current evidence

Five command-response records derived from real K1 Measurement v0 field tests. Each record captures:

- Commanded forward velocity.
- Odometry-derived actual forward velocity.
- Floor type and session metadata.
- Qualitative response assessment (deadzone, weak tracking, under-tracking, stable).
- Sparse uncertainty/confidence labels.

Evidence is sufficient for structural pipeline validation (schema compliance, model output generation, risk map construction) but insufficient for performance evaluation, calibration, or generalization claims.

## 8. What remains outside scope

The following are explicitly outside the current scope and are documented as future work or permanently excluded:

- Controller modification (not possible under closed-source constraint).
- Policy training or sim-to-real transfer (not the project's objective).
- Real-time robot control or command adaptation.
- Navigation outcome evaluation (requires separate protocol, trials, and metrics).
- Compensation or safe command adaptation (requires expanded evidence and outcome validation).

## 9. Future evidence needed

To upgrade any candidate contribution beyond tentative status, the following evidence is needed:

- Repeated velocity-response trials per command velocity (multi-trial, multi-session).
- Multi-surface K1 response collection.
- Expanded command grid including `v_y` and `omega_z`.
- Additional metrics: delay, stop-distance, yaw drift, lateral drift.
- Hold-out prediction evaluation.
- Uncertainty calibration trials.
- Real navigation task trials with outcome metrics (collision, near-miss, success rate).
- Baseline comparisons under a fixed protocol.
