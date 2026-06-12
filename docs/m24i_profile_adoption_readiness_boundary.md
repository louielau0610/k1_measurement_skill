# M24-I Profile Adoption Readiness Boundary

**Candidate profile**: `m24i_controlled_s2_profile_candidate`
**Status**: `candidate_only` — NOT adopted as gold profile.

## What M24-I Allows

- Controlled S2 replication has been analyzed.
- 3/4 velocities match M24-F within reproducibility threshold.
- A candidate profile has been created for review.
- Profile adoption **planning** is allowed (not adoption itself).

## What M24-I Does NOT Allow

- ❌ Automatic profile adoption.
- ❌ Overwriting `k1_gold_profile_v1.json`.
- ❌ Claiming the candidate profile is validated.
- ❌ Using the candidate profile for compensation without separate validation.
- ❌ Using the candidate profile for GO1/G1.
- ❌ Claiming deployment readiness.

## Adoption Readiness Checklist

Before adopting any S2 profile:

- [ ] Candidate profile reviewed by operator.
- [ ] Candidate profile compared against M19C gold profile.
- [ ] Decision documented: keep identity-only vs. adopt candidate.
- [ ] If adopting: archive old gold profile, update manifest.
- [ ] Compensation validation designed separately (not auto-triggered by profile adoption).

## Current State

```
Gold profile (M19C-E):     UNCHANGED
Candidate profile (M24-I):  CANDIDATE ONLY — NOT ADOPTED
Compensation validation:    NOT RUN
Deployment:                 NOT READY
GO1/G1:                     BLOCKED
```
