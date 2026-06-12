# M24-F Corrected S2 Profile Refresh Analysis

- Corrected extraction rows: 30
- Corrected QC pass: `true`
- Corrected profile decision: `corrected_analysis_inconclusive`
- M24-C artifacts superseded: `true`
- Gold profile overwritten: `false`
- Deployment ready: `false`

## Corrected Per-Velocity Summary
| Command | n | Mean Actual | Mean Abs Error | No-Motion Rate |
|---------|---|-------------|----------------|----------------|
| 0.35 | 5 | 0.002785 | 0.347215 | 1.0 |
| 0.4 | 5 | 0.011353 | 0.388647 | 0.8 |
| 0.45 | 5 | 0.039635 | 0.410365 | 0.4 |
| 0.5 | 5 | 0.029037 | 0.470963 | 0.6 |
| 0.55 | 5 | 0.049154 | 0.500846 | 0.2 |
| 0.6 | 5 | 0.082856 | 0.517144 | 0.0 |

## Claim Boundary
M24-F corrects extraction and creates a corrected candidate profile only. It does not adopt a profile, overwrite the K1 gold profile, claim compensation improvement, claim deployment readiness, or start GO1/G1 work.
