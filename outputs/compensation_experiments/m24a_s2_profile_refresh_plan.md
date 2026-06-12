# M24-A S2 Profile Refresh Plan

Generated: 2026-06-12T05:40:21.090378+00:00
Surface: `S2_marble_floor`
Condition: `direct_refresh`
Repeats per command velocity: 5
Physical profile refresh status: `not_run`
Deployment ready: `false`

M24-A is a design-only profile refresh plan. No hardware has been run, no refreshed physical results exist, and the K1 gold profile is not overwritten.

## Command Velocities
- 0.35 m/s
- 0.40 m/s
- 0.45 m/s
- 0.50 m/s
- 0.55 m/s
- 0.60 m/s

## Profile Mismatch Metrics

- Threshold: 0.03 m/s
- Old M19C mean actual velocity
- New refresh mean actual velocity
- Difference and absolute difference
- Old and new uncertainty
- Profile mismatch flag
- Yaw drift comparison
- No-motion rate
- Repeat variability
- Direct tracking near-optimal flag

## Trial Plan

| Trial ID | Group | Command | Repeat | Status |
|----------|-------|---------|--------|--------|
| M24A_S2_marble_floor_V035_R1 | M24A_S2_marble_floor_V035 | 0.35 | 1 | planned |
| M24A_S2_marble_floor_V035_R2 | M24A_S2_marble_floor_V035 | 0.35 | 2 | planned |
| M24A_S2_marble_floor_V035_R3 | M24A_S2_marble_floor_V035 | 0.35 | 3 | planned |
| M24A_S2_marble_floor_V035_R4 | M24A_S2_marble_floor_V035 | 0.35 | 4 | planned |
| M24A_S2_marble_floor_V035_R5 | M24A_S2_marble_floor_V035 | 0.35 | 5 | planned |
| M24A_S2_marble_floor_V040_R1 | M24A_S2_marble_floor_V040 | 0.40 | 1 | planned |
| M24A_S2_marble_floor_V040_R2 | M24A_S2_marble_floor_V040 | 0.40 | 2 | planned |
| M24A_S2_marble_floor_V040_R3 | M24A_S2_marble_floor_V040 | 0.40 | 3 | planned |
| M24A_S2_marble_floor_V040_R4 | M24A_S2_marble_floor_V040 | 0.40 | 4 | planned |
| M24A_S2_marble_floor_V040_R5 | M24A_S2_marble_floor_V040 | 0.40 | 5 | planned |
| M24A_S2_marble_floor_V045_R1 | M24A_S2_marble_floor_V045 | 0.45 | 1 | planned |
| M24A_S2_marble_floor_V045_R2 | M24A_S2_marble_floor_V045 | 0.45 | 2 | planned |
| M24A_S2_marble_floor_V045_R3 | M24A_S2_marble_floor_V045 | 0.45 | 3 | planned |
| M24A_S2_marble_floor_V045_R4 | M24A_S2_marble_floor_V045 | 0.45 | 4 | planned |
| M24A_S2_marble_floor_V045_R5 | M24A_S2_marble_floor_V045 | 0.45 | 5 | planned |
| M24A_S2_marble_floor_V050_R1 | M24A_S2_marble_floor_V050 | 0.50 | 1 | planned |
| M24A_S2_marble_floor_V050_R2 | M24A_S2_marble_floor_V050 | 0.50 | 2 | planned |
| M24A_S2_marble_floor_V050_R3 | M24A_S2_marble_floor_V050 | 0.50 | 3 | planned |
| M24A_S2_marble_floor_V050_R4 | M24A_S2_marble_floor_V050 | 0.50 | 4 | planned |
| M24A_S2_marble_floor_V050_R5 | M24A_S2_marble_floor_V050 | 0.50 | 5 | planned |
| M24A_S2_marble_floor_V055_R1 | M24A_S2_marble_floor_V055 | 0.55 | 1 | planned |
| M24A_S2_marble_floor_V055_R2 | M24A_S2_marble_floor_V055 | 0.55 | 2 | planned |
| M24A_S2_marble_floor_V055_R3 | M24A_S2_marble_floor_V055 | 0.55 | 3 | planned |
| M24A_S2_marble_floor_V055_R4 | M24A_S2_marble_floor_V055 | 0.55 | 4 | planned |
| M24A_S2_marble_floor_V055_R5 | M24A_S2_marble_floor_V055 | 0.55 | 5 | planned |
| M24A_S2_marble_floor_V060_R1 | M24A_S2_marble_floor_V060 | 0.60 | 1 | planned |
| M24A_S2_marble_floor_V060_R2 | M24A_S2_marble_floor_V060 | 0.60 | 2 | planned |
| M24A_S2_marble_floor_V060_R3 | M24A_S2_marble_floor_V060 | 0.60 | 3 | planned |
| M24A_S2_marble_floor_V060_R4 | M24A_S2_marble_floor_V060 | 0.60 | 4 | planned |
| M24A_S2_marble_floor_V060_R5 | M24A_S2_marble_floor_V060 | 0.60 | 5 | planned |

## Boundaries

- Direct command only; no compensated command is planned in M24-A/M24-B.
- The objective is to compare current direct response against the old M19C S2 response profile.
- M24-A cannot claim compensation improvement, physical validation, deployment readiness, or GO1/G1 validation.
