# M23-A Physical Validation Claim Boundary

**Status**: M23-A is experiment design only. Physical validation has not started.

## What M23-A Does

- Defines the paired before/after experiment structure.
- Specifies surfaces, desired velocities, repeats, randomization.
- Defines primary and secondary success metrics.
- Specifies the analysis plan with statistical tests.
- Generates trial plan CSV and JSON artifacts.
- Creates the result schema that M23-B/M23-C will fill.

## What M23-A Does NOT Do

- ❌ Execute any robot hardware.
- ❌ Send commands to K1.
- ❌ Run any physical trial.
- ❌ Generate any physical velocity data.
- ❌ Claim tracking improvement.
- ❌ Claim compensation works on K1.
- ❌ Claim deployment readiness.
- ❌ Claim GO1 or G1 calibration.

## Future Milestones

### M23-B (Future): K1 Physical Compensation Execution

- Execute the M23-A trial plan on physical Booster K1.
- Record ROS2 state logs for all trials.
- Extract measured velocities and yaw drift.
- Flag invalid trials with explicit reasons.

### M23-C (Future): K1 Compensation Before/After Analysis

- Load trial results per the M23-A result schema.
- Compute paired error comparisons.
- Run statistical tests (Wilcoxon signed-rank).
- Generate before/after plots.
- Determine claim level based on result quality.

## Claim Escalation Rules

| Condition | Claim Allowed |
|-----------|---------------|
| M23-A only (design) | No physical claims |
| M23-B complete (data collected) | Descriptive statistics only; no improvement claim |
| M23-C with significant result (p < 0.05) on S2 | "Compensation reduces tracking error on marble floor (single robot, single surface)" |
| M23-C with non-significant result | "Suggestive but inconclusive; more data needed" |
| M23-C on multiple surfaces | Broader claim; requires S1/S3 data |
| Real-time ROS2 node deployed | Not in scope for calibration skill |

## Current Claim Boundary

```
┌─────────────────────────────────────────────────────┐
│  M23-A: EXPERIMENT DESIGN ONLY                      │
│                                                     │
│  ✅ Experiment designed                              │
│  ✅ Trial plan generated                             │
│  ✅ Result schema defined                            │
│  ❌ Physical trials executed                         │
│  ❌ Tracking improvement validated                   │
│  ❌ Deployment ready                                 │
│  ❌ GO1/G1 calibrated                                │
│                                                     │
│  Next: M23-B — execute trials on physical K1        │
└─────────────────────────────────────────────────────┘
```
