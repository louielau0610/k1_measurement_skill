# M24-D Controlled S2 Replication Plan

M24-D recommends controlled replication before adopting the M24-C candidate profile or running another compensation validation.

## Scope

- Robot: Booster K1 only.
- Surface: `S2_marble_floor` only.
- Condition: `direct_refresh` only.
- No compensated commands.
- Do not overwrite `k1_gold_profile_v1`.

## Velocity Set

Primary overlapping velocities:

- `0.40`
- `0.45`
- `0.50`
- `0.55`

Optional context velocities:

- `0.35`
- `0.60`

Use 5 repeats per velocity.

## Controls

- Standardize start pose before every trial.
- Standardize path length and clear endpoint.
- Use a written reset procedure between trials.
- Keep the same extraction window as M24-B/M24-C.
- Record battery state if available.
- Record robot warm-up state and elapsed time since power-on.
- Record surface condition, debris, and any visible slip.
- Record whether odometer x/y/theta change during each command phase.

## Outputs

The replicated session should include trial records, raw state logs, extraction output, QC output, and a short operator note for every invalid or unexpected trial.

## Boundary

This replication plan is for direct-response diagnosis only. It does not validate revised compensation, deployment readiness, navigation improvement, GO1/G1, or cross-platform behavior.
