# M21 Future Data Collection Pack v1

> **Data collection pack only — no experiments have been executed.** This document provides practical templates, checklists, and workflows for future K1 velocity response and navigation outcome data collection. All values are placeholders.

## Purpose

Convert the M20 future experiment protocol into execution-ready data collection materials for future experimenters. This pack covers pre-session, in-trial, post-trial, and post-session workflows, folder conventions, data integrity checks, and pipeline handoff.

## Scope and non-goals

**Scope**: templates, checklists, naming conventions, logging plans, operator guides, data integrity procedures, handoff workflow.
**Not in scope**: actual experiment execution, ROS2 commands, robot movement scripts, compensation, navigation control, safe command adapter.

## Required pre-session materials

Before the first trial, the experimenter must have:
- This data collection pack (M21).
- M20 future experiment protocol (tiers, metrics, design matrix).
- Printed/electronic pre-session checklist (`m21_pre_session_checklist_v1.md`).
- Printed/electronic trial sheet template (`m21_trial_sheet_template_v1.md`).
- Navigation task sheet template if applicable (`m21_navigation_task_sheet_template_v1.md`).
- Logging manifest template (`m21_logging_manifest_template_v1.md`).
- Post-session validation checklist (`m21_post_session_validation_checklist_v1.md`).
- JSON session template (`examples/future_experiments/m21_future_session_template.json`).

## Folder structure

```
data/future_experiments/
    {session_id}/
        raw/
            rosbag_{trial_id}.bag
            rosbag_{trial_id}.yaml
        processed/
            {trial_id}_normalized.json
            {trial_id}_metrics.json
        video/
            {trial_id}_video.mp4            (OPTIONAL)
        metadata/
            session_manifest.json
            session_metadata.json
            session_checksums.txt           (TO_BE_FILLED)
        notes/
            {trial_id}_operator_notes.md
            session_notes.md
        validation/
            schema_validation_report.json
            exclusion_log.md
            claim_safety_self_check.md
```

## File naming convention

- Session ID: `K1_{YYYYMMDD}_{surface}_{session_number}` (e.g., `K1_20270115_hardfloor_01`)
- Trial ID: `{session_id}_vx{xx}_{trial_number}` (e.g., `K1_20270115_hardfloor_01_vx030_03`)
- Navigation task ID: `{session_id}_nav{task_number}_{condition}` (e.g., `K1_20270115_hardfloor_01_nav01_advisory`)

## Session setup workflow

1. Complete pre-session checklist.
2. Create session folder structure.
3. Verify robot and logging readiness.
4. Review command grid and navigation tasks.
5. Conduct warm-up trials (not recorded as data).
6. Begin data collection per trial workflow.

## Trial execution workflow

1. Select command condition from trial sheet.
2. Verify logging is active (read-only ROS2 rosbag).
3. Execute trial per protocol (operator issues velocity command).
4. Record trial start/end timestamps.
5. Fill trial sheet during/after trial.
6. Log operator notes immediately.
7. Run post-trial validity check.

## Post-trial workflow

1. Verify raw log present and non-zero.
2. Fill trial sheet fields.
3. Mark trial validity.
4. Document exclusion reason if invalid.
5. Move to next trial or end session.

## Post-session workflow

1. Complete post-session validation checklist.
2. Verify all trial IDs accounted for.
3. Run schema validation on session data.
4. Document all exclusions.
5. Run claim-safety self-check.
6. Archive session data.

## Data integrity checks

- Raw log files non-zero and readable.
- Trial count matches command grid plan.
- No `remote_controller_state` in any record.
- All downstream readiness flags remain false.
- Checksums generated (TO_BE_FILLED with actual tool).

## Handoff to pipeline

After post-session validation:
1. Normalized trial records → M14-style dataset builder.
2. Dataset records → M15R-style response model.
3. Response predictions → M16-style risk mapper.
4. Navigation outcome data → M20-style evaluation.
5. All artifacts → M17-style pipeline evaluation.

## Claim-safety checklist

Before any claim is made after future data collection:
- [ ] No collision rate reduction claim until statistically demonstrated.
- [ ] No navigation safety improvement claim until outcome trials show significant effect.
- [ ] No calibrated uncertainty claim without calibration protocol.
- [ ] No compensation readiness claim (compensation not implemented).
- [ ] No safe command adapter claim (not implemented).
- [ ] No publication readiness claim.
- [ ] All reported numbers traceable to source artifacts.

## Recommended execution order

1. M20 protocol review.
2. M21 pack review and printing of checklists.
3. Pre-session setup.
4. Tier 1 trials (repeated velocity response).
5. Tier 1 post-session validation.
6. Tier 2 trials (held-out split).
7. Tier 3 trials (navigation outcome, baseline condition).
8. Tier 4 trials (navigation outcome, advisory condition).
9. Full post-session validation and pipeline handoff.
