# M21 Data Collection Handoff Matrix

| source_template | future_filled_artifact | downstream_pipeline_stage | required_validation | claim_enabled_after_validation | claim_not_enabled | notes |
| --- | --- | --- | --- | --- | --- | --- |
| Session template | Experiment record (JSON) | M20 schema validation | Schema validator + disallowed field check | Structural record exists | Any performance/safety claim | Placeholder values until real session |
| Trial sheet template | Velocity response trial record | M14-style dataset builder | Schema v1 validation | Dataset construction | Predictive accuracy | Metrics filled after processing |
| Trial sheet template | Response prediction input | M15R-style response model | No fabrication check | Prediction generation | Calibrated uncertainty | Labels are categorical |
| Trial sheet template | Risk map input | M16-style risk mapper | Safety flag check | Advisory assessment generation | Navigation safety improvement | Risk map is advisory only |
| Navigation task sheet | Navigation outcome record | M20 Tier 3/4 evaluation | Outcome metrics from raw logs | Outcome correlation analysis | Safety/collision reduction | No compensation/control |
| Logging manifest | Session provenance record | M17-style pipeline evaluation | Checksum + manifest completeness | Artifact traceability | Publication readiness | Provenance only |
| Post-session checklist | Pipeline handoff package | All downstream stages | All validations passed | Pipeline reproducibility | Any new claim type | Checklist completion != evidence |
