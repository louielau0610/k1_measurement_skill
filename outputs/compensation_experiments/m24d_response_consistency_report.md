# M24-D Response Consistency Report

- Overlap velocities: [0.4, 0.45, 0.5]
- Discrepancy pattern: `systematic_m24c_near_zero_nonreproduction`
- Adoption decision: `investigate_extraction_before_profile_decision`
- Candidate profile adopted: `false`
- Deployment ready: `false`
- GO1/G1 blocked: `true`

## Pairwise Disagreement

| Velocity | M19C | M23-C Direct | M24-C | M19-M23 | M19-M24 | M23-M24 | Labels |
|----------|------|--------------|-------|---------|---------|---------|--------|
| 0.4 | 0.363734 | 0.393333 | 0.000672 | 0.029599 | 0.363062 | 0.392661 | m19c_m24c_disagree;m23c_direct_response_not_reproduced;m23c_closer_to_m19c_than_m24c;m24c_no_motion_all_repeats;m24c_direct_not_near_optimal |
| 0.45 | 0.498215 | 0.4425 | 0.001837 | 0.055715 | 0.496378 | 0.440663 | m19c_m24c_disagree;m23c_direct_response_not_reproduced;m23c_closer_to_m19c_than_m24c;m24c_no_motion_all_repeats;m24c_direct_not_near_optimal |
| 0.5 | 0.63431 | 0.491667 | 0.000825 | 0.142643 | 0.633485 | 0.490842 | m19c_m24c_disagree;m23c_direct_response_not_reproduced;m23c_closer_to_m19c_than_m24c;m24c_no_motion_all_repeats;m24c_direct_not_near_optimal |

## Finding
M24-C is not adoption-ready because it differs from old M19C and does not reproduce M23-C direct-response behavior.

## Claim Boundary
This report does not claim compensation improvement, revised compensator physical validation, deployment readiness, navigation improvement, GO1/G1 validation, or cross-platform validation.
