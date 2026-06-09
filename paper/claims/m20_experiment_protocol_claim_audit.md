# M20 Experiment Protocol Claim Audit

## Purpose

Verify that the M20 future experiment protocol does not overclaim, does not fabricate results, and does not claim completed experiments.

## Protocol claims allowed

- A future experiment protocol has been designed. (supported_structural_claim)
- The protocol defines 4 experiment tiers with clear evidence requirements. (supported_structural_claim)
- Specific metrics are defined for velocity response, model evaluation, and navigation outcome measurement. (supported_structural_claim)
- Claim-upgrade criteria are defined for each claim type. (supported_structural_claim)
- Compensation, safe command adapter, and navigation control remain out of scope. (supported_structural_claim)

## Protocol claims not allowed

- The experiments have been executed (not executed).
- The protocol demonstrates any performance, safety, or navigation improvement (protocol only, no data).
- Collision/near-miss/success-rate metrics have been measured (not measured).
- The protocol proves the approach works (not proven).

## Claim-upgrade mapping

| claim_type | current_status | M20_protocol_requirement | required_future_data | allowed_current_wording | prohibited_current_wording |
| --- | --- | --- | --- | --- | --- |
| Structural pipeline | supported | Already met | None | "artifact-governed pipeline exists" | "validated performance pipeline" |
| Predictive quality | not supported | Tier 1 + Tier 2 | Held-out MAE/RMSE on repeated trials | "predictive quality has not been evaluated" | "model predicts accurately" |
| Advisory risk usefulness | not demonstrated | Tier 3 + Tier 4 | Navigation outcome correlation with risk warnings | "advisory correlation has not been evaluated" | "advisory warnings improve navigation" |
| Navigation safety improvement | prohibited | Tier 3 + Tier 4 + formal safety metrics | Statistically meaningful reduction in collision/near-miss rates | "safety improvement has not been evaluated" | "reduces collisions" |
| Calibrated uncertainty | prohibited | Repeated trials + calibration protocol | Calibrated confidence intervals | "uncertainty labels are categorical, not calibrated" | "calibrated uncertainty estimates" |
| Compensation readiness | out of scope | Future separate project | Implementation + validation + real robot evaluation | "compensation is not implemented" | "compensation-ready" |
| Safe command adapter | out of scope | Future separate project | Implementation + safety validation + controlled trials | "safe command adapter is not implemented" | "safe command adapter ready" |
