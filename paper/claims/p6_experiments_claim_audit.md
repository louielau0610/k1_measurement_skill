# P6 Experiments Claim Audit

## Purpose

P6 creates an academic Experiments/Evaluation draft v1 from M17 pipeline evaluation and current output artifacts. This audit verifies that every reported number comes from a real artifact, every claim is structurally conservative, and no performance or safety wording appears.

## Inputs inspected

- 25 input artifacts including all 8 manuscript/section files, 5 M17-M18 tables, 4 pipeline docs, 10 output artifacts, 5 producer scripts, and 7 claim governance files.

## Evaluation claims allowed

- The evaluation is structural/artifact-level only. (supported_by_project_artifact)
- Dataset v1 contains 5 records: 4 numeric, 1 qualitative-only at 0.10 m/s. (supported_by_project_artifact)
- Exact-source reconstruction MAE is 0.0 — a sanity check, not predictive performance. (sanity_check_only)
- Risk map reports 5 assessments with 5 warnings across 3 risk levels. (structural_validation_only)
- Risk levels are advisory classifications; no navigation outcomes exist. (supported_by_project_artifact)
- All available metrics are structural or distributional counts. (supported_by_project_artifact)
- Performance and safety metrics are unavailable and require future experiments. (supported_by_project_artifact)

## Evaluation claims requiring real navigation trials

- Navigation safety improvement. (requires_navigation_trials)
- Collision-rate reduction. (requires_navigation_trials)
- Near-miss-rate reduction. (requires_navigation_trials)
- Success-rate improvement. (requires_navigation_trials)
- Advisory-layer effectiveness. (requires_navigation_trials)

## Prohibited performance/safety wording

The following are absent from the Experiments draft when used as positive claims:
- "outperforms", "improves safety", "reduces collisions", "validated navigation"
- "calibrated probability" (used only as "not calibrated probability")
- "publication-ready", "deployment-ready"

## Metric availability audit

All reported numbers verified against source artifacts:
- Dataset: 5 records, 4 numeric, 1 qualitative-only — matches `response_model_evaluation_v1.json`
- Risk: 5 assessments, 5 warnings — matches `navigation_risk_evaluation_v1.json`
- Risk levels: critical=1, high=2, medium=2 — matches `navigation_risk_evaluation_v1.json`
- Warning categories: deadzone=1, high_uncertainty=2, under_tracking=1, weak_tracking=1 — matches `navigation_risk_evaluation_v1.json`
- Exact-source MAE: 0.0 — matches `response_model_evaluation_v1.json`
- All unavailable metrics are explicitly listed as "no" or omitted.

## Baseline comparison audit

The draft states baseline hooks are "retained for future comparison readiness" and "not evaluated on held-out data." It explicitly says "no superiority or inferiority claim is made about any model." This satisfies the conservative baseline requirement.

## Difference between artifact validation and performance validation

Throughout the draft, structural validation (§4.2-4.6) is clearly separated from missing performance evaluation (§4.7-4.8). The evaluation summary (§4.9) reinforces this separation with explicit "does not establish" statements.

## Claim audit table

| experiment_claim_or_wording | status | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- |
| Dataset v1: 5 records, 4 numeric, 1 qualitative. | supported_by_project_artifact | `velocity_response_dataset_v1.json` + model eval | "5 records, 4 numeric, 1 qualitative-only" | "comprehensive dataset" |
| Exact-source MAE=0.0 is sanity check only. | sanity_check_only | `response_model_evaluation_v1.json` | "structural sanity check" | "predictive accuracy of 0.0 error" |
| Risk map: 5 assessments, 5 warnings. | structural_validation_only | `navigation_risk_evaluation_v1.json` | "5 advisory risk assessments with 5 warnings" | "navigation risk validated" |
| Risk levels: critical=1, high=2, medium=2. | structural_validation_only | `navigation_risk_evaluation_v1.json` | "risk level distribution" | "risk calibration validated" |
| No navigation outcomes exist. | supported_by_project_artifact | M17 eval + risk eval | "derived from model prediction attributes — not from real navigation outcomes" | "therefore navigation safety is unproven" |
| No collision/near-miss/success metrics. | supported_by_project_artifact | M17 unavailable metrics + risk eval | "no collision, near-miss, or success-rate data exists" | "collision rate is zero" |
| Baseline hooks not evaluated for superiority. | structural_validation_only | model code + model eval | "retained for future comparison readiness... no superiority claim" | "outperforms baselines" |
| Future experiment protocol listed. | future_experiment_required | M17 next experiments | "required before any performance or safety claim" | "planned experiments for next milestone" |
