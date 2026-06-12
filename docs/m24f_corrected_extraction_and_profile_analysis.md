# M24-F Corrected Extraction and Profile Analysis

M24-F corrects the S2 profile-refresh extraction for the clean M24-B session `m24b_s2_profile_refresh_clean_20260612_145358`.

The corrected extractor uses the command phase only and excludes the first and last second of that phase. It reads existing ROS2 odometer logs, computes forward displacement from odometer `x`, `y`, and `theta`, and writes corrected measurements without modifying the original M24-B/M24-C outputs.

## Artifacts

- `scripts/extract_m24f_corrected_s2_profile_refresh_trials.py`
- `scripts/qc_m24f_corrected_s2_profile_refresh_session.py`
- `scripts/analyze_m24f_corrected_s2_profile_refresh.py`
- `data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358/corrected_extracted_results.csv`
- `data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358/corrected_qc_summary.json`
- `outputs/compensation_experiments/m24f_corrected_s2_profile_refresh_summary.json`
- `outputs/compensation_experiments/m24f_corrected_s2_current_profile_candidate.json`
- `outputs/compensation_experiments/m24f_faulty_vs_corrected_extraction_comparison.csv`

## Result

- Corrected trial count: 30
- Velocity groups: 6
- Repeats per velocity: 5
- Corrected QC pass: `true`
- Corrected profile decision: `corrected_analysis_inconclusive`
- M24-C artifacts superseded: `true`
- Gold profile overwritten: `false`
- Candidate profile adopted: `false`
- Deployment ready: `false`
- GO1/G1 blocked: `true`

## Boundary

M24-F does not run hardware, fabricate physical results, overwrite `k1_gold_profile_v1`, adopt the corrected candidate profile, claim compensation improvement, claim deployment readiness, or start GO1/G1 work.
