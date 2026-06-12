# M24-C S2 Profile Refresh Analysis Report

## Session Summary
- Session ID: `m24b_s2_profile_refresh_clean_20260612_145358`
- Trial count: 30
- Executed/skipped/invalid: 30/0/0
- Velocity groups: 6
- Profile status decision: `inconclusive_environment_dependent`
- Candidate profile: `outputs/compensation_experiments/m24c_s2_current_profile_candidate.json`

## Refreshed Direct Response

| Command | n | Mean Actual | Mean Abs Error | No-Motion Rate | Mean Yaw Drift |
|---------|---|-------------|----------------|----------------|----------------|
| 0.35 | 5 | 0.000744 | 0.349256 | 1.0 | 0.731094 |
| 0.4 | 5 | 0.000672 | 0.399328 | 1.0 | 0.337484 |
| 0.45 | 5 | 0.001837 | 0.448163 | 1.0 | 1.444346 |
| 0.5 | 5 | 0.000825 | 0.499175 | 1.0 | 0.50591 |
| 0.55 | 5 | -0.000372 | 0.550372 | 1.0 | 0.608871 |
| 0.6 | 5 | 0.000709 | 0.599291 | 1.0 | 0.391663 |

## Old M19C Vs New M24-C

| Command | Old Mean | New Mean | Abs Diff | Mismatch | Status |
|---------|----------|----------|----------|----------|--------|
| 0.35 | 0.354026 | 0.000744 | 0.353282 | True | compared |
| 0.4 | 0.363734 | 0.000672 | 0.363062 | True | compared |
| 0.45 | 0.498215 | 0.001837 | 0.496378 | True | compared |
| 0.5 | 0.63431 | 0.000825 | 0.633485 | True | compared |
| 0.55 |  | -0.000372 |  |  | old_velocity_unavailable |
| 0.6 | 0.644957 | 0.000709 | 0.644248 | True | compared |

## M23-C Consistency Check

| Velocity | M23-C Direct | M24-C Refresh | Old M19C | M24-C vs M23-C | M24-C vs M19C | Staleness Consistent |
|----------|--------------|---------------|----------|----------------|----------------|----------------------|
| 0.4 | 0.393333 | 0.000672 | 0.363734 | 0.392661 | 0.363062 | False |
| 0.45 | 0.4425 | 0.001837 | 0.498215 | 0.440663 | 0.496378 | False |
| 0.5 | 0.491667 | 0.000825 | 0.63431 | 0.490842 | 0.633485 | False |
| 0.55 | 0.540833 | -0.000372 |  | 0.541205 |  | False |

## Decision
`inconclusive_environment_dependent`

Next recommended milestone: Collect more controlled S2 refresh data before compensation validation

## Candidate Profile Warning
The candidate profile is not a gold profile, is not deployment ready, requires review before adoption, does not validate compensation, and must not be used for GO1/G1.

## Claim Boundary
M24-C analyzes clean S2 direct-refresh physical data and creates a candidate current S2 profile. It does not claim compensation improvement, revised compensator physical validation, deployment readiness, navigation improvement, GO1/G1 validation, cross-platform validation, or universal K1 generalization.
