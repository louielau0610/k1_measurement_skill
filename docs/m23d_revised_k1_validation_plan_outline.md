# M23-D Revised K1 Validation Plan Outline

## Status

This is an outline only. It does not run hardware and does not implement the revised compensator.

## Revised Offline Compensator

Create a revised offline compensator that includes:

- identity fallback;
- benefit gate;
- correction magnitude limit;
- profile mismatch detection;
- explicit non-deployment status.

## Candidate Follow-Up Experiment

Rerun only selected K1 S2 velocities where M23-C showed clear worsening:

- 0.40 m/s
- 0.45 m/s
- 0.50 m/s
- 0.55 m/s

Keep the experiment small until the revised compensator has offline evidence that it will not repeat the M23-C failure.

## Conditions

Include:

- identity baseline: `u_cmd = v_desired`;
- benefit-gated compensated condition;
- optional old M23-C compensated command as a non-primary reference only if safety review allows it.

## Comparison

Compare the revised experiment against:

- same-session identity baseline;
- M23-C negative result;
- offline predictions from the revised compensator.

## Gate To Physical Execution

Before any physical run:

1. Run offline replay of M23-C direct/compensated results.
2. Confirm identity is selected for identity-preferred cases.
3. Confirm command corrections are bounded by `max_correction_mps`.
4. Confirm `deployment_ready=false`.
5. Confirm operator protocol and trial plan are regenerated.

## Required Future Milestone

New physical evidence should be handled in a future M23-E or M24 milestone. No GO1/G1 work should proceed until K1 revised-compensator validation is complete.
