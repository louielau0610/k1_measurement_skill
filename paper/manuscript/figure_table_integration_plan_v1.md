# Figure/Table Integration Plan v1

## Purpose

Plan for integrating M19/M19.1 figure assets and table packs into the manuscript v1 assembly and future v2.

## Inputs inspected

M19 figure sources (.mmd), M19 figure specs, M19.1 evidence-gap figure spec, figure caption pack, main-paper table pack, appendix table pack, table caption pack, manuscript v1 assembly, P11/P12 claim audits.

## Figure inventory

| figure | source | format | rendered | main/appendix |
| --- | --- | --- | --- | --- |
| Figure 1: Method Pipeline | `method_pipeline_figure.mmd` | Mermaid | source only | main |
| Figure 2: Evidence Chain | `evidence_chain_figure.mmd` | Mermaid | source only | main |
| Figure 3: Evidence Gap Boundary | `current_evidence_gap_v1.md` | Mermaid | source only | appendix |

## Table inventory

| table | source | main/appendix |
| --- | --- | --- |
| Table 1: Method I/O Contract | `main_paper_table_pack_v1.md` (Table 1) | main |
| Table 2: Current Evaluation Metrics | `main_paper_table_pack_v1.md` (Table 2) | main |
| Table 3: Claim-Upgrade Requirements | `main_paper_table_pack_v1.md` (Table 3) | main or appendix |
| Tables A1-D1: Audit tables | `appendix_table_pack_v1.md` | appendix |

## Manuscript insertion points

- **Figure 1** → Method §3 (Overview). The pipeline figure illustrates the five-stage flow described in the Method draft.
- **Figure 2** → Experiments §4 or Discussion §5. The evidence chain figure visualizes how evidence flows into claim governance.
- **Figure 3** → Appendix or Discussion §6/§7. The evidence gap figure provides a transparent boundary map.
- **Table 1** → Method §3. The I/O contract table supports the Method stage descriptions.
- **Table 2** → Experiments §4. The metrics table summarizes current and missing evidence.
- **Table 3** → Discussion §5 or Appendix. The claim-upgrade table supports the Discussion's evidence-governance narrative.

## Caption claim audit summary

All captions in `figure_caption_pack_v1.md` and `table_caption_pack_v1.md` pass claim-safety checks:
- No "improves safety," "reduces collision," "proves," "guarantees," "state-of-the-art," "outperforms."
- All prohibited claims are documented as missing or prohibited, not as achieved.
- Uncertainty is consistently labeled "categorical, not calibrated probability."

## Rendering instructions

1. Install Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli` (if available).
2. Render Figure 1: `mmdc -i paper/figures/method_pipeline_figure.mmd -o paper/figures/method_pipeline_figure.svg`
3. Render Figure 2: `mmdc -i paper/figures/evidence_chain_figure.mmd -o paper/figures/evidence_chain_figure.svg`
4. Extract and render Figure 3 Mermaid code from `current_evidence_gap_v1.md`.
5. Embed rendered SVGs in LaTeX manuscript v2.

## Remaining work before LaTeX conversion

- Render all 3 figures to SVG/PNG using Mermaid CLI or mermaid.live.
- Format main-paper tables for LaTeX (tabular/booktabs).
- Select appendix tables based on venue page limits.
- Convert manuscript from Markdown to LaTeX.
- Final citation formatting.

## What M19.1 deliberately does not do

- Does not render figures to SVG/PNG (requires external rendering tool).
- Does not convert manuscript to LaTeX.
- Does not create a submission package.
- Does not add new experimental evidence or new manuscript sections.
- Does not claim publication readiness.
