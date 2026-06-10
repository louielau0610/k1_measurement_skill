# P17 Figure/Table Claim Audit

## Purpose
Verify P17 figure/table assets preserve all boundaries.

## Format assets created
- 3 LaTeX table files from existing Markdown sources.
- Mermaid figure sources copied to latex/figures/.
- Appendix conversion plan.

## Claims allowed
- LaTeX table files exist (non-final, derived from existing sources).
- Figure sources are available for future rendering.
- Tables preserve claim boundaries from source packs.

## Claims not allowed
- Figures are rendered (not rendered).
- Tables add new data or claims (from existing sources only).
- This constitutes a submission package or publication readiness.

## Claim audit table
| asset | allowed_claim | prohibited_claim | evidence_boundary | next_action |
| --- | --- | --- | --- | --- |
| Table 1 (.tex) | Non-final LaTeX table exists | Final formatted table | From main_paper_table_pack_v1.md | Layout polish |
| Table 2 (.tex) | Non-final LaTeX table exists | Comprehensive evaluation | Structural metrics only | Layout polish |
| Table 3 (.tex) | Non-final LaTeX table exists | Claims are upgradeable now | Prohibited marked | Layout polish |
| Figure .mmd copies | Source available for rendering | Figures are rendered | .mmd sources only | SVG rendering (P18/mermaid.live) |
