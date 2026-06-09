# Method Artifact Evidence Table

| Method stage | Artifact / file | Producer script | Evidence type | Validation status | Paper use | Current limitation | Claim status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Schema definition | `configs/velocity_response_dataset_schema_v1.json` | manual repository artifact | schema | validated by schema CLI | Define dataset contract | Does not contain experimental results | supported structural/software claim |
| Measurement mapping | `docs/measurement_v0_to_velocity_response_schema_v1_mapping.md` | manual repository artifact | mapping document | inspected in M18 | Explain source-to-schema mapping | Mapping depends on available Measurement v0 fields | supported structural/software claim |
| Dataset construction | `outputs/research_datasets/velocity_response_dataset_v1.json` | `scripts/build_velocity_response_dataset_v1.py` | dataset | validation report exists | Report sparse dataset evidence | single robot; single session; sparse commands | supported structural/software claim |
| Dataset validation | `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` | `scripts/build_velocity_response_dataset_v1.py` | validation report | available | Show schema compliance | Not a performance metric | supported structural/software claim |
| Response modeling | `outputs/research_models/response_model_predictions_v1.json` | `scripts/run_velocity_response_model_v1.py` | prediction output | reproducible | Define response prediction contract | labels are not calibrated probabilities | supported structural/software claim |
| Model evaluation | `outputs/research_models/response_model_evaluation_v1.json` | `scripts/run_velocity_response_model_v1.py` | structural evaluation | reproducible | Report sanity checks | no held-out performance evidence | supported structural/software claim |
| Risk mapping | `outputs/research_risk/navigation_risk_map_v1.json` | `scripts/run_navigation_risk_mapping_v1.py` | advisory risk map | reproducible | Explain warning metadata | no navigation outcome evidence | candidate contribution |
| Risk evaluation | `outputs/research_risk/navigation_risk_evaluation_v1.json` | `scripts/run_navigation_risk_mapping_v1.py` | structural risk evaluation | reproducible | Report risk/warning counts | no collision/near-miss/success metrics | requires more experiment |
| Pipeline evaluation | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | `scripts/generate_research_pipeline_evaluation_v1.py` | pipeline evaluation | reproducible | Summarize artifacts, limitations, non-claims | not publication readiness | supported structural/software claim |
| Literature matrix | `paper/related_work/literature_matrix.md` | manual P1 artifact | literature evidence | verified/partial metadata | Support context claims | not a full systematic review | literature context claim |
| Gap analysis | `paper/positioning/gap_analysis_v1.md` | manual P2 artifact | positioning artifact | inspected in M18 | Organize candidate gaps | not final novelty evidence | candidate contribution |
| Claim registry | `paper/claims/claim_registry.md` | manual governance artifact | claim governance | updated through M18 | Track allowed claims | not a result artifact | supported structural/software claim |
| Non-claims | `paper/claims/non_claims.md` | manual governance artifact | non-claim governance | updated through M18 | Prevent overclaiming | not a result artifact | non-claim |

