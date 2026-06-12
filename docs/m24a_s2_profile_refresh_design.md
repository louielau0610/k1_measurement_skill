# M24-A S2 Current-Condition Profile Refresh Design

M24-A designs a small Booster K1 measurement refresh experiment for `S2_marble_floor`. It exists because the M23-C physical before/after experiment produced a negative compensation result: direct commands tracked the requested velocities better than the compensated commands. M23-D diagnosed overcorrection and identity preference, and M23-F found that every audited target velocity had suspected profile mismatch.

The likely engineering question is whether the old M19C S2 profile still represents the current Booster K1 response on the current marble-floor setup. A stale profile can make an inverse compensator choose commands that are mathematically consistent with old data but harmful for current behavior.

## Objective

Measure the current direct-command S2 response before another compensation validation. The refresh should answer:

- Does current direct K1/S2 behavior match the old M19C S2 profile?
- Does it match the direct-response behavior observed in M23-C?
- Is direct tracking already near optimal for the tested S2 command range?

## Scope

- Platform: Booster K1 only.
- Surface: `S2_marble_floor`.
- Commands: `0.35`, `0.40`, `0.45`, `0.50`, `0.55`, optionally `0.60` m/s.
- Repeats: minimum 3 per command; recommended 5 if battery and time allow.
- Condition: `direct_refresh` only.
- No compensated commands are part of M24-A or M24-B profile refresh.

## Profile Mismatch Metrics

For each command velocity, M24-C should compute:

- old M19C mean actual velocity;
- new refresh mean actual velocity;
- difference: `new_refresh_mean_actual_velocity_mps - old_m19c_mean_actual_velocity_mps`;
- absolute difference;
- old uncertainty;
- new uncertainty;
- profile mismatch flag.

Default threshold:

```text
profile_mismatch_threshold_mps = 0.03
```

This threshold should remain configurable. M24-C should also report yaw drift comparison, no-motion rate, repeat variability, and whether direct tracking remains near optimal.

## Claim Boundary

M24-A can claim only that a refresh experiment has been designed. It cannot claim that hardware has been run, that the S2 profile has been refreshed, that revised compensation improves tracking, that deployment is ready, or that GO1/G1 are validated.

## Gold Profile Versioning

`k1_gold_profile_v1` must not be overwritten by a refresh without explicit versioning. If M24-C shows the old profile is stale, the appropriate output is a new profile such as `k1_s2_current_profile_v2`, with provenance linking it to the M24 refresh evidence. Preserving `k1_gold_profile_v1` keeps M19C evidence auditable and prevents silent downstream behavior changes.
