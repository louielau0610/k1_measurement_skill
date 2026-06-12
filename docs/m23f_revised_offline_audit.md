# M23-F Revised Offline Audit

## Status

M23-F is an offline audit only. It does not execute hardware, claim physical improvement, claim deployment readiness, or start GO1/G1 work.

## What Was Audited

The audit reads:

- M23-C pair results: `outputs/compensation_experiments/m23c_k1_before_after_pairs.csv`
- M23-E revised sweep: `outputs/compensation_experiments/m23e_revised_compensator_sweep.csv`
- M23-E summary: `outputs/compensation_experiments/m23e_revised_compensator_summary.json`

It checks whether the revised offline compensator would avoid the harmful commands observed in the M23-C physical experiment.

## Audit Result

- Harmful M23-C commands avoided: 4/4 tested target velocities
- Identity fallback count: 4
- Profile mismatch suspected count: 4
- Benefit gate blocks all compensation: true
- Candidate beneficial count: 0
- Readiness category: `ready_for_profile_refresh_before_validation`

## Why The Revised Compensator Is Safer Than M22-C

M22-C accepted lower compensated commands for the tested S2 velocities. In physical M23-C data, those lower commands worsened tracking error.

M23-E/M23-F avoids that failure offline by:

- selecting identity where direct tracking was already accurate;
- rejecting candidates with negative expected benefit;
- preserving `deployment_ready=false`;
- flagging profile mismatch on every tested velocity.

This is safer than blind inverse lookup, but it is not physical validation.

## Is Identity Fallback Too Conservative?

For the audited S2 velocities, identity fallback is not over-conservative because no candidate compensation case had positive expected benefit. The direct baseline was already near-optimal, and the M22-C candidates matched the harmful M23-C compensated commands.

The audit does not prove identity fallback is best on all surfaces or velocities. It only shows that identity fallback is appropriate for the observed M23-C failure region.

## What Second K1 Validation Should Test

A second K1 validation should test whether the revised system avoids the known failure mode:

1. Rerun the same S2 velocities from M23-C.
2. Verify that the revised compensator chooses identity for identity-preferred cases.
3. Verify that identity fallback does not worsen tracking relative to the M23-C direct baseline.
4. Refresh the S2 response profile before any new selected-compensation experiment.
5. Keep deadzone and low-speed infeasible targets excluded.

## GO1/G1 Boundary

GO1/G1 remain blocked. The revised K1 compensator must first pass K1-specific offline audit, profile refresh if needed, and physical revalidation before any cross-platform extension.
