# M23-C K1 Before/After Compensation Analysis

Session: `m23b_k1_s2_executable_20260612_121605`
Surface: `S2_marble_floor`
Claim level: `negative_result_requires_compensator_revision`

## Validation
- Extracted trials: 24
- Complete pairs: 12
- QC: 16/16 checks passed
- Desired velocities: 0.4, 0.45, 0.5, 0.55

## Aggregate Results
- Mean absolute error, direct: 0.00791675 m/s
- Mean absolute error, compensated: 0.044004 m/s
- Percent reduction in mean absolute error: -455.834%
- Improved pairs: 0
- Worsened pairs: 12
- No-change pairs: 0
- Mean yaw drift, direct: 0 deg
- Mean yaw drift, compensated: 0 deg
- Invalid rate, direct: 0
- Invalid rate, compensated: 0

## Statistical Analysis
- scipy available: True
- Effect size Cohen dz: -2.88101
- Paired t-test p-value: 7.54141e-07
- Wilcoxon signed-rank p-value: 0.000488281

These statistical tests are descriptive support for n=12 paired trials. The result should be interpreted conservatively.

## Per-Velocity Summary

| Desired velocity | Pairs | Direct mean error | Compensated mean error | Mean improvement |
|---:|---:|---:|---:|---:|
| 0.4 | 3 | 0.006667 | 0.024483 | -0.017816 |
| 0.45 | 3 | 0.0075 | 0.040383 | -0.032883 |
| 0.5 | 3 | 0.008333 | 0.0557 | -0.047367 |
| 0.55 | 3 | 0.009167 | 0.05545 | -0.046283 |

## Pair Results

| Pair | Desired | Direct error | Compensated error | Improvement | Yaw delta |
|---|---:|---:|---:|---:|---:|
| `M23A_S2_marble_floor_V040_P1` | 0.4 | 0.006667 | 0.024483 | -0.017816 | 0 |
| `M23A_S2_marble_floor_V040_P2` | 0.4 | 0.006667 | 0.024483 | -0.017816 | 0 |
| `M23A_S2_marble_floor_V040_P3` | 0.4 | 0.006667 | 0.024483 | -0.017816 | 0 |
| `M23A_S2_marble_floor_V045_P1` | 0.45 | 0.0075 | 0.040383 | -0.032883 | 0 |
| `M23A_S2_marble_floor_V045_P2` | 0.45 | 0.0075 | 0.040383 | -0.032883 | 0 |
| `M23A_S2_marble_floor_V045_P3` | 0.45 | 0.0075 | 0.040383 | -0.032883 | 0 |
| `M23A_S2_marble_floor_V050_P1` | 0.5 | 0.008333 | 0.0557 | -0.047367 | 0 |
| `M23A_S2_marble_floor_V050_P2` | 0.5 | 0.008333 | 0.0557 | -0.047367 | 0 |
| `M23A_S2_marble_floor_V050_P3` | 0.5 | 0.008333 | 0.0557 | -0.047367 | 0 |
| `M23A_S2_marble_floor_V055_P1` | 0.55 | 0.009167 | 0.05545 | -0.046283 | 0 |
| `M23A_S2_marble_floor_V055_P2` | 0.55 | 0.009167 | 0.05545 | -0.046283 | 0 |
| `M23A_S2_marble_floor_V055_P3` | 0.55 | 0.009167 | 0.05545 | -0.046283 | 0 |

## Baseline And Ablation Positioning

The physical direct condition is the direct-command baseline. The physical compensated condition is the M22-C risk-aware inverse lookup output. Scalar gain, nearest lookup, and ordinary interpolation were not executed as physical baselines in this session, so they remain offline context only.

## Claim Boundary

This analysis supports only the stated single Booster K1, single S2 marble floor experiment. It does not claim deployment readiness, navigation improvement, GO1/G1 validation, cross-platform physical validation, or universal K1 generalization.
