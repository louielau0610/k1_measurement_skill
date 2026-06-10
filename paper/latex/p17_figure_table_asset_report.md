# P17 Figure/Table Asset Report

## Purpose
Document P17 figure/table conversion status.

## Figure asset status
| figure | source | rendered_svg | status |
| --- | --- | --- | --- |
| Figure 1: Pipeline | `method_pipeline_figure.mmd` | no | Mermaid source copied to latex/figures/; SVG pending mmdc/mermaid.live |
| Figure 2: Evidence | `evidence_chain_figure.mmd` | no | Mermaid source copied to latex/figures/; SVG pending mmdc/mermaid.live |
| Figure 3: Gap | `current_evidence_gap_v1.md` | no | Appendix placeholder; no graphical source |

Mermaid CLI not available. Figures remain source-only. Fallback: copy .mmd to mermaid.live → export SVG.

## Table conversion status
| table | latex_file | status |
| --- | --- | --- |
| Table 1: I/O | `table1_method_io_contract.tex` | converted |
| Table 2: Metrics | `table2_current_evaluation_metrics.tex` | converted |
| Table 3: Claims | `table3_claim_upgrade_requirements.tex` | converted |
| Appendix tables | `appendix_table_conversion_plan_v1.md` | planned (not converted) |

## LaTeX section integration
- Section 03: Table 1 integrated, Figure 1 placeholder kept.
- Section 04: Table 2 integrated, Figure 2 placeholder kept.
- Section 05: Table 3 integrated.
- Section 07: Appendix plan updated.
- All section files preserve `\nonfinalnote` markers.

## Remaining blockers
- Figures not rendered (SVG pending external tool).
- Appendix tables not converted (venue-dependent).
- PDF not built.
- Venue/template not selected.

## P18 readiness
P18 (non-final PDF smoke build) can proceed with placeholder figures. Tables 1-3 are compilable. Figures will show `\figplaceholder` boxes.
