# LaTeX Conversion Plan v1

## Conversion objective

Convert manuscript v2 Markdown assembly into a LaTeX manuscript package suitable for robotics conference or technical report submission.

## Source-to-LaTeX section map

| manuscript_section | markdown_source | future_latex_file | word_count | special_requirements |
| --- | --- | --- | --- | --- |
| Abstract | `00_abstract_draft_v1.md` | `sections/00_abstract.tex` | 193 | No citations |
| Introduction | `01_introduction_draft_v1.md` | `sections/01_introduction.tex` | ~800 | Citations to be preserved |
| Related Work | `02_related_work_draft_v1.md` | `sections/02_related_work.tex` | ~1000 | Citations to be preserved |
| Method | `03_method_draft_v1.md` | `sections/03_method.tex` | ~2500 | Formal notation; Figure 1; Table 1 |
| Experiments | `04_experiments_draft_v1.md` | `sections/04_experiments.tex` | ~2000 | Figure 2; Table 2; numeric traceability |
| Discussion | `05_discussion_limitations_draft_v1.md` | `sections/05_discussion.tex` | ~2500 | Table 3 |
| Conclusion | `06_conclusion_draft_v1.md` | `sections/06_conclusion.tex` | 619 | No citations |

## Figure asset map

| figure | source | format | future_latex_file | rendering_needed |
| --- | --- | --- | --- | --- |
| Figure 1: Method Pipeline | `paper/figures/method_pipeline_figure.mmd` | SVG | `figures/method_pipeline_figure.svg` | mmdc or mermaid.live |
| Figure 2: Evidence Chain | `paper/figures/evidence_chain_figure.mmd` | SVG | `figures/evidence_chain_figure.svg` | mmdc or mermaid.live |
| Figure 3: Evidence Gap (appendix) | `paper/figures/current_evidence_gap_v1.md` | SVG | `figures/current_evidence_gap.svg` | extract Mermaid + render |

## Table asset map

Main paper tables (3):
- Table 1: Method I/O Contract → `tables/table_method_io.tex`
- Table 2: Current Evaluation Metrics → `tables/table_metrics.tex`
- Table 3: Claim-Upgrade Requirements → `tables/table_claim_upgrade.tex`

Appendix tables (11): converted on demand per venue page limits.

## Bibliography map

- Source: `paper/related_work/seed_references.bib` (16 entries).
- Target: `paper/latex/references.bib`.
- Style: venue-dependent (IEEEtran, ACM, or plain).
- All 11 manuscript citation keys verified in .bib.

## Macro/style plan

- Define macros in `macros.tex`.
- Standardize: `\vxcmd`, `\vxactual`, `\uncertlabel`, `\risklevel`.
- Keep claim-boundary comments for reviewers.

## Appendix/supplement plan

- 11 audit/supplement tables → `appendix_tables.tex` or separate supplement PDF.

## Build/check plan

1. `pdflatex main.tex`
2. `bibtex main`
3. `pdflatex main.tex` × 2
4. Check all citations resolve.
5. Check all figure/table references.
6. Check page limits.

## Remaining blockers

| blocker | severity | resolution |
| --- | --- | --- |
| Figures not rendered to SVG | medium | Mermaid CLI or mermaid.live |
| Tables not in LaTeX format | medium | Manual or scripted conversion |
| Final title not selected | low | Author decision |
| Venue not selected | medium | Author decision |
| Real navigation outcomes missing | high | Future experiments |
| Proof all claim boundaries preserved | medium | Pre-submission audit (P16) |

## Future milestone breakdown

- P16: Non-final .tex scaffolds, figure SVG rendering, table LaTeX conversion.
- P17: Full LaTeX compilable draft, PDF build test.
- Final: Submission package assembly (after author/venue decision).
