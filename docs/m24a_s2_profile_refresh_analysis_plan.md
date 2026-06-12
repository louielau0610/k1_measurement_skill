# M24-A S2 Profile Refresh Analysis Plan

M24-C will compare three evidence sources:

- old M19C S2 profile from `k1_gold_profile_v1`;
- M23-C physical direct response from the negative before/after experiment;
- new M24 refresh direct response from current-condition S2 direct trials.

## Per-Velocity Comparison

For each command velocity, compute old-vs-new profile comparison metrics:

- old M19C mean actual velocity;
- M23-C direct mean actual velocity where available;
- new M24 refresh mean actual velocity;
- old uncertainty and new uncertainty;
- absolute difference between old M19C and new refresh;
- profile mismatch flag using `profile_mismatch_threshold_mps`, default `0.03`;
- yaw drift comparison;
- no-motion rate;
- repeat variability;
- direct tracking near-optimal flag.

## Decision Rules

### A. Current Profile Matches M23-C And Differs From M19C

The old profile is stale for S2. Create a versioned `k1_s2_current_profile_v2` from the refresh evidence, and configure the revised offline compensator to use the current profile in later validation. Do not overwrite `k1_gold_profile_v1`.

### B. Current Profile Matches M19C

The M23-C negative result may be due to execution, extraction, or experimental variance. Investigate the M23-C session and extraction before another compensation experiment.

### C. Current Profile Differs From Both

Current K1 response may be unstable or environment-dependent. Compensation should stay identity-only until more data explains the discrepancy.

## Claim Boundary

M24-C may support a profile freshness decision only after real refresh logs pass QC. It must not claim revised compensation improvement or deployment readiness from direct-response refresh data alone.
