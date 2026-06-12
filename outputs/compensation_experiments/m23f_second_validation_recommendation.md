# M23-F Second K1 Validation Recommendation

Readiness category: `ready_for_profile_refresh_before_validation`

## Answers

- Rerun same S2 velocities: True
- Validate identity non-worsening: True
- Refresh S2 profile before compensation experiment: True
- Choose different surface: optional_after_profile_refresh
- Deadzone/low-speed targets: remain_excluded

## Profile Refresh
- rerun a small S2 direct-response measurement set
- compare current direct response to the M19C gold profile
- write a versioned refreshed profile if mismatch is confirmed
- do not overwrite k1_gold_profile_v1.json in place

## Boundary

recommendation only; no physical improvement, deployment, navigation, or GO1/G1 claim
