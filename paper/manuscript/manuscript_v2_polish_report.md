# Manuscript v2 Polish Report

## Purpose

Document all changes applied in the P14 manuscript v2 polish after M19/M19.1 figure/table integration.

## Inputs inspected

Manuscript v1 assembly, all section drafts, M19 figure sources, M19.1 caption/table/integration packs, P11/P12 claim audits.

## Figure/table integration changes

| change_id | category | target_location | change_summary | reason | claim_risk | status |
| --- | --- | --- | --- | --- | --- | --- |
| V2-01 | figure_integration | Method §3 | Added Figure 1 placeholder and caption reference | M19 figure source complete; integration plan specifies Method §3 | low | done |
| V2-02 | figure_integration | Experiments §4 | Added Figure 2 placeholder and caption reference | M19 figure source complete; integration plan specifies Experiments §4 | low | done |
| V2-03 | table_integration | Method §3 | Added Table 1 (I/O contract) reference | M19.1 main-paper table pack provides condensed table | low | done |
| V2-04 | table_integration | Experiments §4 | Added Table 2 (current metrics) reference | M19.1 main-paper table pack provides condensed table | low | done |
| V2-05 | table_integration | Discussion §5 | Added Table 3 (claim-upgrade) reference | M19.1 main-paper table pack provides condensed table | low | done |
| V2-06 | structure | assembly | Added Main-Paper Figure/Table Plan section | Consolidates figure/table inventory from integration plan | low | done |
| V2-07 | structure | assembly | Added Appendix/Supplement Plan section | Separates audit tables from main-paper tables per M19.1 | low | done |

## Prose polish changes

- Section body text preserved from P3-P9 drafts — no substantial prose changes.
- Figure/table placeholders inserted at recommended locations from the M19.1 integration plan.
- Remaining evidence gaps updated to reflect M19.1 status (figures are `.mmd` source only; not yet SVG).

## Main-paper vs appendix decisions

Per M19.1 integration plan and appendix table pack:
- **Main paper**: Figures 1-2, Tables 1-3 (5 assets total).
- **Appendix**: Figure 3 (optional evidence gap), 11 audit/supplement tables.
- **Internal only**: Section status table, revision priority table — referenced but not included as manuscript content.

## Claim-boundary preservation

All P11/P12/P13 claim boundaries preserved:
- 0 claim wording changes.
- 0 claim upgrades.
- All prohibited claims remain absent.
- Evidence gaps documented, not hidden.

## Remaining evidence gaps

All 7 evidence gaps from manuscript v1 remain:
- No real navigation outcomes, no held-out evaluation, single robot/surface/session, sparse command grid, no calibrated uncertainty, no collision/success metrics, figures source-only.

## Remaining formatting tasks

- Render figures to SVG using Mermaid CLI or mermaid.live.
- Format main-paper tables for LaTeX (tabular/booktabs).
- Convert manuscript from Markdown to LaTeX.
- Final citation formatting per venue style.
- Select final title from candidate options.

## Recommended next milestones

1. **M20**: Future experiment protocol for real navigation outcome evaluation.
2. **P15**: LaTeX template conversion and final figure rendering.
3. **Future**: Real-robot multi-trial experiments before performance/safety claims.
