# M24-G Controlled Replication Analysis Plan

M24-G defines the analysis plan for M24-I or a later controlled-replication analysis milestone. No M24-G artifact performs empirical analysis.

## Inputs for Later Analysis

- M19C old S2 profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`
- M23-C direct baseline: `outputs/compensation_experiments/m23c_k1_before_after_pairs.csv`
- M24-F corrected refresh: `outputs/compensation_experiments/m24f_corrected_s2_profile_refresh_summary.json`
- M24-G/H controlled replication result: future controlled session extraction and QC outputs

## Comparison Method

Later analysis should compare per-velocity direct-response means, repeat variability, no-motion rate, yaw drift, and extraction/QC status across the old profile, M23-C direct baseline, corrected M24-F refresh, and controlled replication.

The controlled replication should be analyzed only if:

- The session uses `S2_marble_floor`.
- The condition is `direct_refresh_controlled`.
- Required core velocities are present.
- Required repeats pass QC.
- Required metadata are complete or explicitly reviewed.
- Corrected command-window extraction is used.

## Decision Categories

- `response_reproducible_profile_adoption_possible`: controlled replication is internally consistent and agrees with one response profile closely enough for a versioned adoption review.
- `response_environment_dependent_keep_identity_only`: controlled replication confirms that S2 direct response differs materially across sessions or environments; compensation should remain blocked or identity-only.
- `extraction_or_protocol_issue_persists`: controlled replication has logger, extraction, reset, path, or metadata defects that prevent response interpretation.
- `insufficient_data`: too few valid controlled trials or incomplete metadata.

## Boundary

M24-G does not make any of these decisions. It only defines how later analysis should make them after real controlled data exist.
