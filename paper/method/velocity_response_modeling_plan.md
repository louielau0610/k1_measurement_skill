# Velocity Response Modeling Plan

This plan supports Chapter 2 method formulation. It is a research design artifact, not a literature review and not an experimental result.

## Core Formulation

```text
v_actual = f(v_cmd, environment, robot_state)
```

The model target is the measured forward velocity response of K1 under documented test conditions. The first baseline keeps lateral velocity and yaw-rate commands at zero so the response surface is limited to forward velocity tracking.

## Variables

| variable | role | source | status |
| --- | --- | --- | --- |
| `vx_cmd_mps` | input | trial command plan | planned |
| `vx_actual_mean_mps` | response | normalized log plus ground truth | planned |
| `vx_actual_std_mps` | uncertainty summary | normalized log plus ground truth | planned |
| `environment` | condition | field notes and session metadata | planned |
| `robot_state.mode` | condition | confirmed topic mapping or manual metadata | planned |
| `robot_state.gait` | condition | confirmed topic mapping or manual metadata | planned |
| `robot_state.battery_state` | optional condition | confirmed topic mapping if available | optional |

`remote_controller_state` is not part of the research plan.

## Candidate Analyses

- command-response curve summary by command value;
- per-command repeatability and variance;
- absolute and relative velocity error;
- environment-conditioned response comparison after enough real datasets exist;
- uncertainty-aware reporting that separates measured facts from downstream interpretation.

These analyses may inform future compensation research, but M13 does not implement compensation or inverse command mapping.

## Evidence Boundary

A dataset that passes schema validation is structurally ready for analysis. It is not automatically evidence of a real K1 result, a validated compensation policy, a navigation safety guarantee, or publication readiness.
