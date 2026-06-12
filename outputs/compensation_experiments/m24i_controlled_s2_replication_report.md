# M24-I Controlled S2 Replication Analysis Report
Generated: 2026-06-12T09:30:41.922342+00:00

## Session Summary
- Session ID: m24h_controlled_s2_replication_clean_20260612_171419
- Trials: 20 (20 executed)
- Velocities: 0.4, 0.45, 0.5, 0.55
- Surface: S2_marble_floor
- Condition: direct_refresh_controlled

## Per-Velocity Controlled Response
| v_cmd | n | mean_actual | std | mean_abs_error | yaw_drift | repeat_var | near_opt |
|-------|---|-------------|-----|----------------|-----------|------------|----------|
| 0.4 | 5 | 0.0282 | 0.0261 | 0.3718 | 1.94 | 0.0261 | no |
| 0.45 | 5 | 0.0633 | 0.0187 | 0.3867 | 3.22 | 0.0187 | no |
| 0.5 | 5 | 0.0546 | 0.0417 | 0.4454 | 1.10 | 0.0417 | no |
| 0.55 | 5 | 0.0880 | 0.0174 | 0.4620 | 1.02 | 0.0174 | no |

## M24-F Replication Comparison
| v | M24-F mean | M24-I mean | diff | match? |
|---|------------|------------|------|--------|
| 0.4 | 0.011353 | 0.028194 | 0.016841 | yes |
| 0.45 | 0.039635 | 0.063342 | 0.023707 | yes |
| 0.5 | 0.029037 | 0.05457 | 0.025533 | yes |
| 0.55 | 0.049154 | 0.087978 | 0.038824 | no |

## Decision
**response_reproducible_profile_adoption_planning_allowed**
Reason: 3/4 velocities match M24-F within 0.03m/s threshold. Controlled S2 response is reproducible enough for profile adoption planning.

## Status Flags
- Gold profile overwritten: False
- Candidate profile adopted: False
- Deployment ready: False
- GO1/G1 blocked: True

## Claim Boundary
- Controlled replication analyzed: ✅
- Profile adoption: candidate only, not adopted
- Compensation validated: ❌
- Deployment ready: ❌
- GO1/G1: ❌
