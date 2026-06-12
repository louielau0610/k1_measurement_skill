# M23-D Compensation Failure Mode Report

Source: `outputs/compensation_experiments/m23c_k1_analysis_summary.json`
Pairs analyzed: 12
Direct outperformed compensated pairs: 12
Compensated command lower than direct pairs: 12
Claim level inherited from M23-C: `negative_result_requires_compensator_revision`

## Main Diagnosis

Direct commands were already near optimal; the compensator lowered commands and increased tracking error in every pair.

## Failure Mode Labels
- `compensation_not_beneficial`
- `identity_preferred`
- `overcorrection_risk`
- `profile_mismatch_suspected`
- `revision_required`

## Per-Velocity Failure Modes

| Desired | Direct error | Comp error | Delta | Command delta | Direct wins | Labels |
|---:|---:|---:|---:|---:|---:|---|
| 0.4 | 0.006667 | 0.024483 | 0.017816 | -0.0181156 | 3 | identity_preferred;compensation_not_beneficial;overcorrection_risk;revision_required |
| 0.45 | 0.0075 | 0.040383 | 0.032883 | -0.0334387 | 3 | identity_preferred;compensation_not_beneficial;overcorrection_risk;profile_mismatch_suspected;revision_required |
| 0.5 | 0.008333 | 0.0557 | 0.047367 | -0.0481751 | 3 | identity_preferred;compensation_not_beneficial;overcorrection_risk;profile_mismatch_suspected;revision_required |
| 0.55 | 0.009167 | 0.05545 | 0.046283 | -0.0470652 | 3 | identity_preferred;compensation_not_beneficial;overcorrection_risk;profile_mismatch_suspected;revision_required |

## Boundary

M23-D is diagnosis and planning only. No hardware was executed, no revised compensator was implemented, and no compensation improvement or deployment-readiness claim is made.
