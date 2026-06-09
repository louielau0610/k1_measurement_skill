# P5 Method Claim Audit

## Purpose

P5 creates an academic Method draft v1 from M13-M18 artifacts. This audit verifies that every method statement is conservative, every citation is traceable, every algorithm is consistent with code, and no prohibited wording appears.

## Inputs inspected

- `.agents/skills/autoresearch/SKILL.md`
- `paper/manuscript/manuscript_scaffold.md`
- `paper/manuscript/sections/00_title_and_contribution_options_v1.md`
- `paper/manuscript/sections/01_introduction_draft_v1.md`
- `paper/manuscript/sections/01_problem_statement_v1.md`
- `paper/manuscript/sections/02_related_work_draft_v1.md`
- `paper/manuscript/sections/03_method_skeleton.md`
- `paper/manuscript/sections/04_experiments_skeleton.md`
- `paper/manuscript/sections/README.md`
- `paper/method/method_outline.md`
- `paper/figures/method_pipeline_figure_spec.md`
- `paper/figures/evidence_chain_figure_spec.md`
- `paper/tables/method_artifact_evidence_table.md`
- `paper/tables/current_metrics_and_missing_evidence_table.md`
- 5 docs/ files (M13-M17)
- 5 k1_measurement/ Python modules
- 5 scripts/ Python scripts
- 10 output artifacts in outputs/
- All P1-P4 claim governance files

## Method claims allowed

- The pipeline is an offline, artifact-governed, five-stage process. (supported_by_project_artifact)
- Measurement v0 provides real K1 command-response evidence from read-only logging. (supported_by_project_artifact)
- Dataset v1 is constructed under schema v1 with direct/derived/qualitative field categories. (supported_by_project_artifact)
- `uncertainty_aware_hybrid_v1` is a rule-based, not ML, model. (supported_by_project_artifact)
- Uncertainty labels are categorical reliability markers, not calibrated probabilities. (supported_by_project_artifact)
- The risk mapper produces advisory assessments, not control commands. (supported_by_project_artifact)
- Claim governance separates structural evidence from performance claims. (supported_by_project_artifact)
- Baseline hooks are retained for comparison readiness, not as performance evidence. (supported_by_project_artifact)

## Method claims requiring more experiment

- Prediction accuracy on held-out data. (requires_more_experiment)
- Calibrated uncertainty estimates. (requires_more_experiment)
- Navigation outcome impact of advisory risk labels. (requires_more_experiment)
- Multi-session or multi-surface generalization. (requires_more_experiment)

## Method claims requiring more literature

- Novelty relative to other black-box system identification methods. (requires_more_literature)
- Novelty of artifact governance in robotics method papers. (requires_more_literature)

## Prohibited wording

The following terms are absent from the Method draft when used as positive claims:
- "novel", "first", "state-of-the-art", "outperforms", "proves", "guarantees", "solves"
- "calibrated uncertainty" (used only as "not calibrated probabilities")
- "safe" (used only in "safe command adapter" as explicitly excluded)
- "validated navigation improvement"

## Algorithm wording audit

- Algorithm 1 (dataset construction): consistent with `k1_measurement/velocity_response_dataset_builder.py` and `docs/measurement_v0_to_velocity_response_schema_v1_mapping.md`. No-fabrication policy correctly stated.
- Algorithm 2 (response prediction): consistent with `k1_measurement/velocity_response_model.py` handling rules. Exact-match described as structural sanity check, not accuracy claim.
- Algorithm 3 (risk mapping): consistent with `k1_measurement/navigation_risk_mapping.py`. All disallowed downstream uses match the code constant `DISALLOWED_DOWNSTREAM_USES`.

## Artifact traceability audit

All output paths, producer scripts, and validation artifacts referenced in §3.8 match files present in the repository. The artifact evidence table at `paper/tables/method_artifact_evidence_table.md` provides a more detailed mapping.

## Citation safety audit

The Method draft does not directly cite prior work (method claims are artifact-backed, not literature-backed). If future revisions add comparative statements, they must use only keys from `seed_references.bib` and remain conservative.

## Difference between method description and performance claim

The Method draft describes what the pipeline does (transforms, computes, records, validates) and what it explicitly does not do (compensate, control, guarantee safety). It does not claim that the pipeline improves any navigation outcome metric. The distinction between structural validation (§3.7) and unavailable performance metrics (§3.9) is maintained throughout.

## Claim audit table

| method_claim_or_wording | status | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- |
| Five-stage pipeline exists and is reproducible. | supported_by_project_artifact | M13-M18 + script artifacts | "offline, artifact-governed pipeline" | "validated performance pipeline" |
| K1 is treated as a closed-source system. | supported_by_project_artifact | M7-M8 docs, P4 problem statement | "treated as a closed-source command-execution system" | "therefore unsafe by design" |
| Dataset v1 preserves qualitative labels without numeric fabrication. | supported_by_project_artifact | dataset validation report + no-fabrication schema rules | "preserved... omitted rather than fabricated" | "complete velocity response characterization" |
| Model is rule-based, not ML. | supported_by_project_artifact | `k1_measurement/velocity_response_model.py` | "lightweight, rule-based model" | "learned velocity response model" |
| Uncertainty labels are categorical, not calibrated probabilities. | supported_by_project_artifact | M15R model outputs + M17 limitations | "categorical reliability marker, not a calibrated probability" | "calibrated uncertainty estimates" |
| Risk mapper is offline and advisory. | supported_by_project_artifact | `k1_measurement/navigation_risk_mapping.py` + disallowed uses | "advisory navigation risk assessment" | "navigation safety controller" |
| Compensation and safe adapter are not implemented. | supported_by_project_artifact | M17 non-claims + all prediction safety flags | "no automatic compensation... no safe command adapter execution" | "compensation-ready" |
| Baseline hooks retained for future comparison. | supported_by_project_artifact | `k1_measurement/velocity_response_model.py` MODEL_NAMES | "retained as comparison hooks for future evaluation" | "competitive baselines" |
| Real navigation outcomes not available. | supported_by_project_artifact | M17 evaluation report + metrics table | "collision rate... are documented as unavailable" | "navigation safety evidence" |
| Method does not implement or promise compensation. | supported_by_project_artifact | All code safety flags + M18 audit | "does not implement velocity compensation" | "compensation can be added straightforwardly" |
