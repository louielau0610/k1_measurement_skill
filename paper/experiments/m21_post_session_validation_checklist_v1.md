# M21 Post-Session Validation Checklist v1

> Complete after each session before handoff to pipeline stages.

## Trial accounting

- [ ] All planned trial IDs accounted for.
- [ ] Valid trials: TO_BE_FILLED.
- [ ] Excluded trials: TO_BE_FILLED.
- [ ] Exclusion reasons documented per trial.

## Raw log integrity

- [ ] All raw rosbag files present and non-zero.
- [ ] Raw log count matches trial count.

## Metadata completeness

- [ ] Session manifest completed.
- [ ] Trial sheets completed for all trials.
- [ ] Navigation task sheets completed (if applicable).
- [ ] Operator notes present for all trials.

## Schema compliance

- [ ] Schema validation run on session data.
- [ ] No schema errors (or errors documented).
- [ ] No `remote_controller_state` in any record.
- [ ] All downstream readiness flags remain false.
- [ ] `battery_state` optional — missing is acceptable.

## Derived metrics

- [ ] All derived metrics computed from raw logs only.
- [ ] No fabricated values.
- [ ] Qualitative labels preserved where numeric absent.

## Claim-safety confirmation

- [ ] No collision rate reduction claimed.
- [ ] No navigation safety improvement claimed.
- [ ] No calibrated uncertainty claimed.
- [ ] No compensation readiness claimed.
- [ ] No safe command adapter readiness claimed.
- [ ] No publication readiness claimed.

## Handoff readiness

- [ ] Session data ready for M14-style dataset construction.
- [ ] Session data compatible with M20 schema.
- [ ] Post-session notes archived.
- [ ] All placeholders that remain unfilled are documented.

## Sign-off

- [ ] Session ID: TO_BE_FILLED.
- [ ] Date: TO_BE_FILLED.
- [ ] Operator signature: TO_BE_FILLED.
