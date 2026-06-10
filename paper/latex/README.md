# LaTeX Planning README

> **Planning only. No final LaTeX manuscript or submission package exists.** This directory contains planning documents for future LaTeX conversion.

## Purpose

Plan the conversion of manuscript v2 (`paper/manuscript/manuscript_v2_assembly.md`) and its figure/table assets into a LaTeX-ready manuscript package for a future submission venue.

## P16 Scaffold Status

P16 has created a non-final LaTeX scaffold (17 files). All .tex files are marked non-final. No PDF built.

## Current status

| component | status |
| --- | --- |
| Manuscript v2 (Markdown) | complete (P14) |
| LaTeX sections | scaffold created (8 .tex files) — non-final |
| Figure rendering | Mermaid .mmd sources ready (M19); SVG not rendered |
| Table conversion | Markdown tables exist; LaTeX format pending |
| BibTeX | 16 entries in seed_references.bib (P13) |
| PDF built | no |
| Submission package | not created |
| Submission readiness | **not_submission_ready** |

## Planned LaTeX folder structure

```
paper/latex/
    README.md                          # this file
    latex_conversion_plan_v1.md        # main conversion plan
    venue_template_options_v1.md       # venue/template matrix
    figure_rendering_plan_v1.md        # figure SVG/PDF rendering plan
    table_latex_conversion_plan_v1.md  # table LaTeX conversion plan
    submission_readiness_checklist_v1.md
    p15_latex_planning_claim_audit.md
    sections/                          # future .tex section files
    figures/                           # future rendered figures
    tables/                            # future LaTeX tables
```

## Source manuscript mapping

| manuscript section | future LaTeX file |
| --- | --- |
| Abstract (§0) | `sections/00_abstract.tex` |
| Introduction (§1) | `sections/01_introduction.tex` |
| Related Work (§2) | `sections/02_related_work.tex` |
| Method (§3) | `sections/03_method.tex` |
| Experiments (§4) | `sections/04_experiments.tex` |
| Discussion (§5) | `sections/05_discussion.tex` |
| Conclusion (§6) | `sections/06_conclusion.tex` |

## Figure rendering plan

See `figure_rendering_plan_v1.md`. Figures are Mermaid .mmd source files (M19). Final SVG rendering requires Mermaid CLI (`mmdc`) or mermaid.live.

## Table conversion plan

See `table_latex_conversion_plan_v1.md`. Main-paper tables (3) and appendix tables (11+) to be converted to LaTeX `table` environments.

## BibTeX plan

- Copy `paper/related_work/seed_references.bib` to `paper/latex/references.bib`.
- Verify all 11 manuscript citation keys resolve.
- Select bibliography style per target venue.

## Claim-governance plan

- All claim audits remain active during conversion.
- No performance/safety claims added by formatting.
- Evidence gaps preserved.

## What P15 does not do

- Write .tex manuscript files.
- Render figures to SVG/PNG.
- Convert tables to LaTeX format.
- Build a PDF.
- Create a submission package.
- Claim publication readiness.

## Recommended next steps

1. P16: Create non-final .tex section scaffolds from planning documents.
2. P17: Figure SVG rendering and table LaTeX conversion.
3. Final venue selection (author decision).
4. Manuscript v3 after real experiments.
