# P18 Build Validation Report

## Purpose
Validate whether the non-final LaTeX scaffold can compile and document the result.

## Inputs inspected
P16 scaffold, P17 tables/figures, all section .tex files, macros, references.bib.

## Tool availability
| tool | status |
| --- | --- |
| pdflatex | FOUND (MiKTeX) |
| latexmk | FOUND |
| bibtex | FOUND |

## Preflight checks
- main.tex: valid structure, all section inputs present.
- Section .tex files: 8 files present.
- Table .tex files: 3 files present, correctly referenced.
- references.bib: 16 entries copied from seed_references.bib.
- Figure .mmd sources: copied to latex/figures/.

## Minimal compile-safety edits
- macros.tex: simplified \figplaceholder and \nonfinalnote for safety.
- Section and table files: attempted underscore escaping in file paths.
- Full scaffold: compilation fails due to pervasive underscore characters in artifact filenames (e.g., `method_pipeline_figure.mmd`, `figure_caption_pack_v1.md`) which LaTeX interprets as math subscripts.

## Build result
- **PDF built: false**
- **Build failure reason**: Underscore escaping in file paths. Multiple `.tex` files contain filenames with underscores in captions and table cells. The `\_` escape is incompatible with `\textbf{}` and `\caption{}` contexts.
- **Resolution path**: Replace all underscores in filename references with non-breaking variants (e.g., hyphens), or use `\path{}` / `\url{}` from the `url` or `hyperref` package, or move path references to table notes/verbatim environments.

## Citation/BibTeX validation
- references.bib: 16 entries present.
- Citation keys in .tex files: placeholder scaffolds only (no `\cite{}` calls).
- FULL BIBTEX BUILD NOT ATTEMPTED (pdflatex failed before bibtex stage).

## Figure/table compile status
- Table 1-3: structurally valid but contain underscores in filenames.
- Figure placeholders: compile-safe after macro fix.
- Full compilation requires underscore resolution pass.

## Remaining blockers
- Underscore escaping in artifact filenames (non-blocking for content, blocking for LaTeX compile).
- Figures not rendered (SVG pending mmdc).
- Final title/author/venue not selected.

## P19/submission boundary
P18 confirms: LaTeX tooling exists, scaffold structure is valid, but filename formatting prevents full compile. P19 should resolve underscore issues and retry the full build.

## Claim boundary
This report documents build validation only. No scientific evidence was added or claimed.
