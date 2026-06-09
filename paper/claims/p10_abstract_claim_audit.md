# P10 Abstract Claim Audit

## Purpose

P10 creates a confident but bounded Abstract draft v1 with three length variants. This audit verifies that the abstract accurately compresses the manuscript, uses only artifact-backed claims, and avoids prohibited wording.

## Inputs inspected

P8 manuscript assembly, P9 conclusion, all P3-P7 section drafts, claim governance files, output artifacts.

## Abstract claims allowed

- Closed-source command-to-motion mapping is opaque to the user. (supported_by_project_artifact)
- The pipeline has five documented stages. (supported_by_project_artifact)
- Response model produces conservative predictions with categorical uncertainty labels. (supported_by_project_artifact)
- Risk mapping produces advisory assessments with warning metadata. (supported_by_project_artifact)
- Compensation and safe adapter are not implemented. (supported_by_project_artifact)
- Current evaluation: 5 records, 5 predictions, 5 risk assessments. (supported_by_project_artifact)
- Evidence-governed foundation established. (candidate_interpretation)
- Future experiments identified. (future_work_only)

## Confident wording that remains safe

The primary abstract uses confident but bounded phrasing:
- "presents an offline, artifact-governed pipeline" → structural claim, backed
- "produces conservative response predictions" → artifact-backed
- "produces a consistent, reproducible chain of artifacts" → artifact-backed
- "provides an evidence-governed foundation" → interpretive but bounded

No claim asserts superiority, safety improvement, or calibration.

## Claims requiring real navigation trials

Not asserted in the abstract. The boundary sentence correctly mentions "repeated multi-trial experiments required before navigation outcome or safety claims can be evaluated."

## Prohibited abstract wording

The following are absent:
- "novel", "first", "state-of-the-art", "outperforms", "proves", "guarantees"
- "improves navigation safety", "reduces collisions", "safe deployment"
- "calibrated uncertainty", "calibrated probabilities"
- "publication-ready", "deployment-ready", "submission-ready"

## Numeric result audit

All numbers in the primary abstract verified against output artifacts:
- 5 records (4 numeric, 1 qualitative) → `response_model_evaluation_v1.json`
- 5 predictions → `response_model_predictions_v1.json`
- 5 risk assessments, 3 risk levels → `navigation_risk_evaluation_v1.json`

## Difference between abstract claim and publication readiness claim

The abstract summarizes the manuscript's content — it does not assert the manuscript is ready for submission, that results are final, or that the approach is validated for real-world use. The word "draft" appears in the top note. The boundary sentence explicitly identifies required future experiments.

## Claim audit table

| abstract_claim_or_wording | status | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- |
| Command-to-motion mapping is opaque in closed-source robots. | supported_by_project_artifact | P4 intro, M7-M8 docs | "mapping... is opaque to the user" | "proven safety hazard" |
| Five-stage artifact-governed pipeline presented. | supported_by_project_artifact | M13-M18, P5 method | "presents an offline, artifact-governed pipeline" | "validated performance pipeline" |
| Conservative response predictions with categorical uncertainty labels. | supported_by_project_artifact | M15R model + eval | "conservative... with categorical uncertainty and reliability labels" | "calibrated uncertainty estimates" |
| Advisory risk assessments with explicit warning metadata. | supported_by_project_artifact | M16 risk map + eval | "advisory navigation-risk assessments" | "navigation safety improvement" |
| Compensation and safe adapter not implemented. | supported_by_project_artifact | all code safety flags | "compensation... are not implemented" | "ready for compensation" |
| 5 records (4 numeric, 1 qualitative), 5 predictions, 5 risk assessments. | supported_by_project_artifact | dataset v1, model predictions, risk eval | "produces a consistent, reproducible chain" | "comprehensive evaluation" |
| Evidence-governed foundation established. | candidate_interpretation | all M13-P9 + claim governance | "evidence-governed foundation for studying deployment-layer reliability" | "proven approach" |
| Future experiments required before performance/safety claims. | future_work_only | M17 + P6 §4.8 + P7 §7 | "before navigation outcome or safety claims can be evaluated" | "ready for deployment validation" |
