# Manuscript v1 Revision Changelog

## Purpose

Track all changes applied in the P12 manuscript revision v1 from the P11 audit.

## Inputs

P11 full-manuscript claim audit, P11 revision plan, all section drafts, P8/P10 assembly.

## P11 issues addressed

| issue_id | P11_priority | action_taken | target_file | resolved_now | deferred_reason |
| --- | --- | --- | --- | --- | --- |
| R-01 | P1_high | Updated organization placeholder to reference draft v1 files (03_method_draft_v1.md, 04_experiments_draft_v1.md, 05_discussion_limitations_draft_v1.md, 06_conclusion_draft_v1.md). | `01_introduction_draft_v1.md` §7 | yes | — |
| R-02 | P1_high | Removed stale P4-future reference; updated to "P10 manuscript assembly and additional literature." | `02_related_work_draft_v1.md` Known limitations | yes | — |
| R-04 | P2_medium | Measurement v0 doc paths verified — all current. No changes needed. | `03_method_draft_v1.md` §3.3 | yes (no action) | — |
| R-06 | P2_medium | Figure reference note already present in Method §3: "(specification at paper/figures/method_pipeline_figure_spec.md)." No additional changes needed. | `03_method_draft_v1.md` §3 | yes (no action) | — |
| R-05 | P2_medium | Heading levels verified consistent across section drafts. No changes needed for P12. | `05_discussion_limitations_draft_v1.md` §5.15 | yes (no action) | — |
| R-07 | P3_low | Heading level review deferred to LaTeX conversion milestone. | `manuscript_v0_assembly.md` | deferred | LaTeX export concern — review in M19 |
| R-08 | P3_low | Final title selection deferred. 7 candidate titles remain options. | `00_title_and_contribution_options_v1.md` | deferred | Title selection requires post-revision review |

## P11 issues deferred

| issue_id | priority | reason |
| --- | --- | --- |
| R-03 | P1_high | Adding 1-2 verified citations to Related Work §4, §5 requires literature search — deferred to literature expansion milestone. |
| — | evidence_gap | No real navigation outcomes — requires future experiments. |
| — | evidence_gap | No held-out evaluation — requires repeated trials. |
| — | evidence_gap | Single robot/surface/session — requires multi-session data. |
| — | citation_gap | 8 missing BibTeX entries — deferred to P13 Reference/BibTeX cleanup. |
| — | figure_gap | 2 figures unrendered (specs only) — deferred to M19. |

## Files edited

- `paper/manuscript/sections/01_introduction_draft_v1.md` — §7 organization placeholder updated.
- `paper/manuscript/sections/02_related_work_draft_v1.md` — Known limitations stale reference removed.

## Citation/BibTeX decisions

**Option 1 (conservative cleanup) selected.** The 8 matrix-only entries remain documented as matrix-only. Their BibTeX entries are deferred to P13. No new citations were added to manuscript sections. All 8 cited keys remain traceable to `seed_references.bib`.

## Claim-boundary preservation

No claim was upgraded. No new claim was added. The same 15+ prohibited claims remain absent from all sections. Submission readiness remains `not_submission_ready`.

## Remaining evidence gaps

All 6 high-severity evidence gaps from P11 remain:
- No real navigation outcome evidence.
- No held-out command evaluation.
- Single robot/surface/session.
- Sparse command grid.
- No calibrated uncertainty.
- No collision/near-miss/success-rate metrics.

## Recommended next milestones

1. **P13**: Reference/BibTeX cleanup and literature expansion.
2. **M19**: Figure rendering and table formatting.
3. **Experimental expansion**: Multi-trial, multi-surface K1 data collection.
4. **Future**: Navigation task trials and performance/safety evaluation.
