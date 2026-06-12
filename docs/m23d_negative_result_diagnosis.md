# M23-D Negative Result Diagnosis

## Context

M23-C analyzed the first physical Booster K1 before/after compensation experiment on `S2_marble_floor`.

- Session: `m23b_k1_s2_executable_20260612_121605`
- Trials analyzed: 24
- Complete pairs: 12
- Desired velocities: 0.40, 0.45, 0.50, 0.55 m/s
- Robot-side extraction: 24/24 trials, 0 errors
- Robot-side QC: 16/16 checks passed

The result was negative:

- Mean direct absolute error: 0.00791675 m/s
- Mean compensated absolute error: 0.044004 m/s
- Percent error reduction: -455.834 percent
- Improved pairs: 0
- Worsened pairs: 12
- Mean yaw drift direct: 0.0 deg
- Mean yaw drift compensated: 0.0 deg
- Claim level: `negative_result_requires_compensator_revision`

## Why The Result Is Negative

The compensated condition increased velocity tracking error in every pair. This means the current M22-C inverse lookup did not reduce the measured error it was designed to reduce. The yaw metric did not materially worsen, but yaw stability does not rescue the velocity result: the compensation objective was tracking-error reduction.

## Why Direct Command Was Already Near-Optimal

The direct command baseline was already very accurate in the tested velocity range. Mean direct error was below 0.01 m/s for all tested velocities. For this S2 physical session, sending `u_cmd = v_desired` was already close to the desired actual velocity.

When the baseline is this accurate, a compensator should usually leave the command unchanged unless it can predict a meaningful benefit. The current compensator did not have that benefit gate.

## Why The Current Compensator Worsened Performance

For all 12 pairs, the compensated command was lower than the direct command. The robot then undershot the desired velocity more than it did under direct control. This is an overcorrection failure in the practical sense: the compensator changed a near-good command in the wrong direction for the current physical condition.

The likely mechanism is profile mismatch. The offline response profile suggested that lower commands would better reach the desired actual velocities, but the physical M23-B direct trials showed direct commands were already close to target. The current profile or policy was therefore stale, too conservative, or insufficiently conditioned on the current robot/surface state.

## Failure Modes

M23-D labels the observed failure with these proposed diagnosis/status labels:

- `identity_preferred`: direct command is already sufficiently accurate.
- `compensation_not_beneficial`: compensated error exceeds direct error.
- `overcorrection_risk`: command remapping changes a good command and worsens error.
- `profile_mismatch_suspected`: current physical direct behavior differs from the response profile used by the compensator.
- `revision_required`: the compensator should not be advanced without redesign and revalidation.

## Paper Interpretation

The negative result weakens any claim that the naive or current inverse lookup already improves physical K1 tracking. The paper must not claim tracking improvement from M23-C.

The result does not invalidate the project. It strengthens the research motivation for a benefit-aware compensation skill: a real calibration system must know when to compensate and when to preserve identity control. The failure is useful because it exposes a concrete safety and performance requirement before deployment.

## Why This Is Not A Project Failure

The measurement, execution, extraction, QC, and analysis pipeline worked. The system detected a negative result instead of fabricating success. That is exactly what cautious physical validation is supposed to do.

The failed compensator is an algorithmic result, not a pipeline failure. It gives a clear next design target: add identity fallback, benefit gating, correction magnitude limits, and profile mismatch detection.

## Required Revision

A revised compensator is required before any further physical validation or platform extension. The revised design must be offline-only until revalidated on K1, and GO1/G1 work must remain blocked until the K1 revised compensator passes a new physical experiment.
