# M24-C S2 Profile Refresh Analysis

M24-C analyzes the clean Booster K1 `S2_marble_floor` direct-refresh session `m24b_s2_profile_refresh_clean_20260612_145358`. The purpose is to decide whether the old M19C S2 profile still represents current S2 behavior before any second compensation validation.

## Why M24-C Was Needed

M23-C showed a negative compensation result: direct commands tracked better than compensated commands on S2 marble floor. M23-D diagnosed overcorrection and identity preference. M23-F then found profile mismatch in the revised offline audit and recommended refreshing or confirming the S2 response profile before another compensation experiment.

M24-A designed a direct-only refresh experiment. M24-B created the execution pack and produced a clean 30-trial session. M24-C ingests that clean session and compares it to:

- the old M19C S2 aggregate profile in `k1_gold_profile_v1`;
- the M23-C direct-response evidence from `m23c_k1_before_after_pairs.csv`;
- the new M24-B direct-refresh extracted measurements.

## Analysis Inputs

- Clean session archive: `m24b_s2_profile_refresh_results_m24b_s2_profile_refresh_clean_20260612_145358.tar.gz`
- Clean session path: `data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358/`
- Partial/debug session excluded: `m24b_s2_profile_refresh_20260612_143912`
- Old profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`
- M23-C pairs: `outputs/compensation_experiments/m23c_k1_before_after_pairs.csv`

## Old Vs New Comparison

For each M24-C command velocity, the analysis uses exact old M19C S2 command matches only. If an old profile velocity is unavailable, the comparison is marked unavailable and no interpolation is performed.

For comparable velocities, the mismatch rule is:

```text
profile_mismatch_flag = abs(new_m24c_mean_actual_velocity_mps - old_m19c_s2_mean_actual_velocity_mps) >= 0.03
```

## M23-C Consistency

The consistency check asks whether M24-C resembles the M23-C direct response and differs from M19C. A velocity is considered consistent with profile staleness only if:

- M24-C is within `0.03 m/s` of the M23-C direct mean; and
- M24-C differs from old M19C by at least `0.03 m/s`.

In this analysis, the clean M24-C refresh differs from old M19C, but it also differs strongly from M23-C direct evidence. The decision is therefore:

```text
inconclusive_environment_dependent
```

## Candidate Profile Boundary

M24-C creates `outputs/compensation_experiments/m24c_s2_current_profile_candidate.json` as a candidate/current-profile analysis artifact only. It is not adopted automatically because the evidence does not match the M23-C direct-response behavior.

Before any second compensation validation, the project should collect more controlled S2 refresh data or investigate why the M24-B clean refresh extracted near-zero actual velocity across all commands.

## Claim Boundary

M24-C may claim clean S2 direct-refresh data were analyzed and a candidate profile was produced. It must not claim compensation improvement, revised compensator physical validation, deployment readiness, navigation improvement, GO1/G1 validation, cross-platform validation, or universal K1 generalization.
