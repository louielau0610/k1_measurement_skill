# M21 Data Collection Pack Claim Audit

## Purpose

Verify that M21 templates and checklists do not overclaim and preserve all safety boundaries.

## What M21 supports

- Future experimenters have templates, checklists, and a folder/logging convention.
- Templates enforce placeholder-only values until real trials are conducted.
- Validator detects unsafe readiness flags and disallowed fields.
- Handoff matrix links templates to downstream pipeline stages.

## What M21 does not support

- Any completed experiment evidence.
- Any navigation outcome, collision, near-miss, or success-rate data.
- Compensation, inverse command mapping, safe command adapter execution.
- Publication readiness.

## Claim-safety rules for future experimenters

All M21 checklists include self-check items preventing:
- Collision rate reduction claims without statistical demonstration.
- Navigation safety improvement claims without outcome trials.
- Calibrated uncertainty claims without calibration protocol.
- Compensation/safe adapter readiness claims (not implemented).

## Prohibited interpretations

- Templates do not imply experiments were run.
- Placeholders are not real data.
- Checklist completion does not constitute navigation outcome evidence.

## Claim audit table

| asset | allowed_use | prohibited_use | evidence_boundary | action_needed_before_claim |
| --- | --- | --- | --- | --- |
| Pre-session checklist | Prepare future session | Claim session was conducted | No data collected | Fill and timestamp during real session |
| Trial sheet template | Guide per-trial documentation | Report trial results as completed | Placeholder values only | Fill with real data during trial |
| JSON templates | Provide schema-compatible structure | Use as completed experiment records | Placeholder values only | Fill after real trials |
| Post-session checklist | Validate future session data | Claim session was successful | No outcome data | Complete after real session |
| All templates | Data collection preparation | Navigation outcome or safety evidence | Protocol-only | Real experiments + analysis |
