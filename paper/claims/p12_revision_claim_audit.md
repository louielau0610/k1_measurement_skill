# P12 Revision Claim Audit

## Purpose

Verify that P12 manuscript revision v1 preserves all P11 claim boundaries and does not introduce new overclaims.

## Inputs inspected

P11 audit, P11 revision plan, all section drafts, manuscript v1 assembly, changelog, consistency check.

## Claim changes made

No claim content was changed. P12 edits were limited to:
- Updating stale file references in Introduction §7.
- Removing stale milestone references in Related Work limitations.

## Claims unchanged from P11

All 19 claims from the P11 claim matrix remain identical in content and classification. No claim was upgraded, downgraded, or reworded for strength.

## Risks eliminated

- **Stale reference risk**: Introduction §7 no longer references outdated skeleton paths (03_method_skeleton.md, 04_experiments_skeleton.md). Now references actual draft v1 files.
- **Inconsistent milestone reference**: Related Work limitations no longer references a completed P4 as a future milestone.

These were low-risk consistency issues; their resolution improves manuscript v1 clarity but does not affect claim safety.

## Risks remaining

All 6 high-severity evidence gaps from P11 remain:
- No real navigation outcome evidence.
- No held-out command evaluation.
- Single robot/surface/session.
- Sparse command grid.
- No calibrated uncertainty.
- No collision/near-miss/success-rate metrics.

These require future experiments. No wording changes in P12 reduce or disguise these gaps.

## Submission-readiness boundary

Submission readiness: **not_submission_ready**. The revision improves manuscript clarity and internal consistency but does not add or validate any performance, safety, or generalization evidence.

## Prohibited claims still prohibited

All 15+ prohibited claims from M18/P11 remain absent. No new wordings introduced that could be interpreted as overclaiming.

## Claim audit table

| claim_or_wording | previous_status | P12_action | new_status | evidence | still_requires |
| --- | --- | --- | --- | --- | --- |
| Organization section references | stale (outdated skeleton paths) | updated | current (draft v1 paths) | P3-P10 section files | — |
| Related Work limitations milestone reference | stale (P4 referenced as future) | updated | current (P10 assembly referenced) | P10 milestone | — |
| All 19 P11 claims | per P11 matrix | unchanged | identical to P11 | per P11 matrix | per P11 matrix |
| All 12 numeric items | verified in P11 | unchanged | identical to P11 | source artifacts | none added |
| Not submission ready | not_submission_ready | unchanged | not_submission_ready | P11/P8 audits | experiments |
| No final novelty | not claimed | unchanged | not claimed | — | literature |
| No performance superiority | not claimed | unchanged | not claimed | — | experiments |
| No navigation safety improvement | not claimed | unchanged | not claimed | — | experiments |
| No publication readiness | not claimed | unchanged | not claimed | — | revision + experiments |
