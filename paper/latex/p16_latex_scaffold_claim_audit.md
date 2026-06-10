# P16 LaTeX Scaffold Claim Audit

## Purpose
Verify non-final LaTeX scaffold preserves all scientific boundaries.

## Scaffold claims allowed
- A non-final LaTeX skeleton exists (scaffold only).
- BibTeX references copied from verified seed_references.bib.
- Figure/table placeholders document what needs rendering/conversion.

## Claims not allowed
- The manuscript is compiled or submission-ready.
- Figures are rendered (placeholders only).
- Tables are converted (placeholders only).
- The paper is fit for any venue.
- Scientific evidence exists beyond structural/artifact-level.

## Claim audit table
| scaffold_asset | allowed_claim | prohibited_claim | evidence_boundary | next_action |
| --- | --- | --- | --- | --- |
| main.tex | Non-final LaTeX skeleton exists | Manuscript is compilable | Not built | P17: render + convert |
| references.bib | BibTeX copied from verified source | All citations resolve | Untested until PDF build | P18: PDF smoke build |
| Sections 01-06 | Placeholder scaffolds with source refs | Converted final content | Markdown source is authoritative | P17: section conversion |
| Figure placeholders | Document what needs rendering | Figures are rendered | .mmd sources only | P17: SVG rendering |
| Table placeholders | Document what needs conversion | Tables are formatted | Markdown tables only | P17: LaTeX conversion |
