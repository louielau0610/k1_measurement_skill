# P7 Discussion Claim Audit

## Purpose

P7 creates a conservative Discussion and Limitations draft v1. This audit verifies that every interpretive statement is appropriately qualified, every limitation is complete, every future-work item is clearly separated from current results, and no conclusion or safety claim is made.

## Inputs inspected

- 40+ input artifacts including all P3-P6 manuscript sections, M17/M18 evaluation docs, all claim governance files, and key output artifacts from outputs/.

## Discussion claims allowed

- Pipeline demonstrates artifact-governed structural transformation. (supported_by_project_artifact)
- Deployment-layer modeling differs from controller training and direct compensation. (candidate_interpretation, supported_by_literature)
- Categorical uncertainty labels are useful under sparse evidence but not calibrated. (supported_by_project_artifact)
- Risk mapping is advisory interpretation, not control. (supported_by_project_artifact)
- Claim governance separates structural from performance claims. (supported_by_project_artifact)

## Interpretation claims that must remain tentative

- Deployment-layer response modeling is a distinct and underexplored gap. (candidate_interpretation; requires more literature)
- Advisory risk warnings would improve planner decisions. (future_work_only; requires navigation trials)
- Categorical labels are appropriately conservative. (candidate_interpretation; requires calibration comparison)

## Claims requiring real navigation trials

- Risk warnings correspond to real navigation risk. (requires_navigation_trials)
- Advisory layer improves navigation outcomes. (requires_navigation_trials)
- Deadzone/under-tracking warnings predict collision likelihood. (requires_navigation_trials)

## Prohibited performance/safety wording

The following are absent from the Discussion draft as positive claims:
- "outperforms", "improves safety", "reduces collision", "validated navigation"
- "calibrated uncertainty" (used only in negating/future-work context)
- "publication-ready", "deployment-ready"
- "final conclusion" (explicitly stated as not written)

## Limitation completeness audit

All five P6 limitation categories are addressed in §6:
- Dataset limitations (§6.1): single robot, sparse commands, qualitative-only, single session
- Model limitations (§6.2): rule-based, sanity check, no held-out eval, no calibration
- Risk-mapping limitations (§6.3): advisory, heuristic, no outcome validation
- System/scope limitations (§6.4): no compensation/inverse/control/safe adapter
- Generalization limitations (§6.5): single platform, no cross-robot/cross-surface

## Future-work wording audit

All future-work items (§7.1-7.4) use future-tense or conditional language ("is needed", "should be collected", "would be compared", "should be considered only after"). No future-work item is stated as already implemented or as a committed plan. The discussion summary (§8) explicitly states "This discussion is not a final conclusion."

## Difference between discussion interpretation and conclusion claim

The Discussion draft interprets what the current pipeline implies, acknowledges what it does not prove, and identifies what future evidence is needed — it does not assert final findings, does not claim the pipeline is ready for deployment, and does not state that the work is complete. The final paragraph explicitly defers conclusion writing to P8 manuscript assembly.

## Claim audit table

| discussion_claim_or_wording | status | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- |
| Pipeline transforms measurement into risk map artifacts. | supported_by_project_artifact | M13-M18 + P5-P6 | "demonstrates that an offline, artifact-governed pipeline can transform..." | "validates the pipeline for deployment" |
| Deployment-layer modeling differs from controller-centric work. | candidate_interpretation | P1-P2 lit + P3 draft | "differs from locomotion policy training... from direct velocity compensation" | "first black-box deployment analysis" |
| Categorical labels avoid false precision under sparse data. | candidate_interpretation | M15R model + M17 eval | "categorical labels offer several advantages under sparse data" | "uncertainty is well-calibrated" |
| Labels are not calibrated probabilities. | supported_by_project_artifact | M15R + P6 metrics | "not calibrated probabilities... not validated against repeated trials" | "calibrated uncertainty estimates" |
| Risk mapping is advisory, not control. | supported_by_project_artifact | M16 code + M17 eval | "does not control the robot... does not trigger automatic compensation" | "ready for safe command adaptation" |
| Claim governance prevents overstating evidence. | supported_by_project_artifact | all claim governance docs | "enforce a clear separation between structural claims... prohibited claims" | "publication-ready claim framework" |
| Single robot, surface, session limitation. | supported_by_project_artifact | dataset v1 + P6 metrics | "single K1... single indoor floor surface... single test session" | "comprehensive dataset" |
| Future work: expansion, navigation trials, calibration, adaptation. | future_work_only | M17 next experiments + P6 §4.8 | "The most immediate priority is expanding the measurement base" | "planned for next release" |
| This discussion is not a final conclusion. | supported_by_project_artifact | draft text §8 | "not a final conclusion... should be written only after full manuscript assembly" | "manuscript conclusion" |
