# Numeric Traceability Table

| number_or_metric | manuscript_location | exact_or_summary_wording | source_artifact | source_field_or_context | safe_to_report | interpretation_boundary | prohibited_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 records | Experiments §4.3, Abstract, Conclusion | "5 records" / "five dataset records" | `response_model_evaluation_v1.json` | `records_count: 5` | yes | Covers only forward v_x from one session. | "comprehensive dataset" |
| 4 numeric records | Experiments §4.3, Abstract | "4 numeric records" | `response_model_evaluation_v1.json` | `numeric_records_count: 4` | yes | At commands 0.30-0.50 m/s. | "sufficient for model validation" |
| 1 qualitative-only | Experiments §4.3, Abstract | "1 qualitative-only record at 0.10 m/s" | `response_model_evaluation_v1.json` | `qualitative_only_records_count: 1` | yes | Deadzone; no numeric actual velocity. | "0.1 m/s tracking error" |
| 5 predictions | Experiments §4.4, Abstract | "5 predictions" / "five response predictions" | `response_model_predictions_v1.json` | prediction array length | yes | Covers same 5 command points. | "comprehensive prediction coverage" |
| 5 risk assessments | Experiments §4.5, Abstract | "5 risk assessments" | `navigation_risk_evaluation_v1.json` | `assessments_count: 5` | yes | Advisory only; not outcome-validated. | "validated navigation risk" |
| 5 warnings | Experiments §4.5, Abstract | "5 warnings" | `navigation_risk_evaluation_v1.json` | `warnings_count: 5` | yes | Advisory only; not outcome-validated. | "5 safety warnings validated" |
| critical=1, high=2, medium=2 | Experiments §4.5, Discussion §5.4 | "1 critical, 2 high-risk, 2 medium-risk" | `navigation_risk_evaluation_v1.json` | `risk_level_counts` | yes | Distribution reflects model-internal evaluation. | "calibrated risk distribution" |
| deadzone=1, high_uncertainty=2, under_tracking=1, weak_tracking=1 | Experiments §4.5 | "4 warning categories" | `navigation_risk_evaluation_v1.json` | `warning_category_counts` | yes | Heuristic from prediction attributes. | "validated warning categories" |
| exact-source MAE=0.0 | Experiments §4.4, Method §3.5 | "absolute reconstruction error is 0.0 m/s" | `response_model_evaluation_v1.json` | `exact_source_reconstruction_absolute_error_mean: 0.0` | yes | Structural sanity check only; not predictive accuracy. | "predictive accuracy of 0.0 m/s" |
| 0.10 m/s deadzone | Experiments §4.3, Method §3.4 | "0.10 m/s... deadzone" | `response_model_evaluation_v1.json` | qualitative record at vx=0.1 | yes | Actual displacement too small to measure. | "tracking error at 0.1 m/s" |
| 0.30, 0.40, 0.45, 0.50 m/s | Experiments §4.3, Discussion §6.1 | "0.30, 0.40, 0.45, and 0.50 m/s" | `response_model_evaluation_v1.json` | numeric records | yes | Single trial each; no variability estimate. | "validated across command range" |
| 16 unavailable metrics | Experiments §4.7 | "16 metrics documented as unavailable" | `experiment_metrics_status_table.md` | rows with available_now=no | yes | All require future experiments. | "metrics are zero or absent" |
