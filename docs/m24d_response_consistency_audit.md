# M24-D Response Consistency Audit

M24-D audits why the S2 response evidence from M19C, M23-C, and M24-C does not agree.

M24-C did not justify adopting the candidate profile. It showed that the clean M24-B refresh differed from the old M19C S2 profile, but it also did not reproduce the M23-C direct-response behavior. This means the profile question is not simply old profile stale versus current profile fresh.

## Main Finding

The three-way overlap velocities are:

- `0.40`
- `0.45`
- `0.50`

At all three velocities, M23-C direct response is closer to M19C than to M24-C. M24-C is near zero at all three overlap velocities, which triggers the labels:

- `m23c_direct_response_not_reproduced`
- `candidate_profile_not_adoption_ready`
- `controlled_replication_required`
- `extraction_method_audit_required`

## What The Disagreement Implies

The disagreement supports an environment-dependent or measurement-pipeline-dependent response concern. It does not support automatic candidate profile adoption. The M24-C candidate profile may still be useful as evidence, but it must remain a candidate until controlled replication and extraction audit explain the near-zero response.

## Before Second Compensation Validation

Before another compensation experiment, the project should either:

- audit M24-B/M24-C extraction and odometer source behavior; or
- rerun a controlled direct-only S2 replication session using the M24-D plan.

## Claim Boundary

M24-D is offline analysis only. It does not execute hardware, overwrite profiles, claim compensation improvement, claim revised compensator physical validation, claim deployment readiness, claim navigation improvement, start GO1/G1 work, or validate cross-platform behavior.
