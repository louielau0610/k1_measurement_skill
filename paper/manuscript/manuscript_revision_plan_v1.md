# Manuscript Revision Plan v1

## Revision objective

Transform the manuscript v0 assembly into a cleaner, more polished manuscript v1 by applying Codex-editable fixes identified in the P11 full-manuscript claim audit. Experiment-dependent fixes are deferred to future experimental milestones.

## P0 — Blocking issues (0)

**No blocking issues identified.** All sections are drafted, all claims are artifact-backed, all citations are traceable, and no prohibited wording appears. The manuscript is structurally complete but evidence-incomplete for performance/safety claims — which is expected and correctly documented.

## P1 — High-priority revisions (3)

| priority | category | target_file | target_section | issue | recommended_edit | requires_new_experiment | requires_new_literature | expected_impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1_high | claim_wording | `01_introduction_draft_v1.md` | §7 | Organization placeholder references outdated skeleton paths. | Update to reference actual draft v1 files (P3-P6). | no | no | high — fixes internal inconsistency |
| P1_high | claim_wording | `02_related_work_draft_v1.md` | Known limitations | References P4 as future milestone; P4 is completed. | Update limitation note to reflect current milestone status. | no | no | medium — avoids stale roadmap references |
| P1_high | missing_citation | `02_related_work_draft_v1.md` | §4, §5 | Sections 4 and 5 each rely primarily on one citation (FanRSS2021STEP). | Add 1-2 verified citations per section after literature expansion. | no | yes — literature search | high — strengthens discussion sections |

## P2 — Medium-priority revisions (3)

| priority | category | target_file | target_section | issue | recommended_edit | requires_new_experiment | requires_new_literature | expected_impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P2_medium | section_structure | `03_method_draft_v1.md` | §3.3 | Measurement v0 description references doc paths that could be cross-checked. | Verify all doc paths are current; update if files have moved. | no | no | low — documentation accuracy |
| P2_medium | writing_clarity | `05_discussion_limitations_draft_v1.md` | §5.15 | Discussion Summary header says "§5.15" in assembly but is a top-level summary. | Ensure heading level is consistent with other top-level subsections. | no | no | medium — heading consistency |
| P2_medium | figure_reference | `03_method_draft_v1.md` | §3 | Method pipeline figure is referenced by spec path only. | Add "(planned: see method_pipeline_figure_spec.md)" if not rendered. | no | no | low — make reference explicit |

## P3 — Low-priority revisions (2)

| priority | category | target_file | target_section | issue | recommended_edit | requires_new_experiment | requires_new_literature | expected_impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3_low | formatting | manuscript_v0_assembly.md | throughout | Section heading numbering may need adjustment for LaTeX export. | Review heading levels when converting to LaTeX in future milestone. | no | no | low — LaTeX conversion concern |
| P3_low | writing_clarity | `00_title_and_contribution_options_v1.md` | — | Title options are tentative; final title not selected. | Select final title before submission (P12 or later). | no | no | low — metadata completeness |

## Edits Codex can perform now

All P1 and P2 items except those marked `requires_new_literature=true` can be performed in P12:
- Update Introduction §7 to reference draft v1 files
- Update Related Work limitations to reflect current milestone status
- Cross-check doc paths in Method §3.3
- Fix heading consistency in Discussion Summary
- Add explicit figure reference note in Method §3

## Edits requiring new experiments

All performance/safety/generalization claims require experimental expansion:
- Repeated multi-trial K1 data collection
- Held-out command evaluation
- Multi-surface/multi-session data
- Navigation task trials with outcome metrics
- Baseline comparison on expanded dataset

These are deferred to future experimental milestones (post-P12).

## Edits requiring new literature

- Add 8 missing BibTeX entries for matrix-only papers
- Broaden system-identification and commercial-SDK calibration literature review
- Strengthen Related Work §4 and §5 citation support

These are deferred to literature expansion milestone.

## Recommended next milestones

1. **P12**: Manuscript revision v1 — apply Codex-editable fixes from this plan.
2. **M19**: Figure rendering and table formatting.
3. **Literature expansion**: Add missing BibTeX entries; broaden system-ID review.
4. **Experimental expansion**: Multi-trial, multi-surface K1 data collection.
5. **Future**: Navigation task trials and performance/safety evaluation.
