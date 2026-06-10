# P18 LaTeX Build Claim Audit

## Build claims allowed
- LaTeX tooling was detected and is available.
- Preflight checks confirm scaffold structure is valid.
- Full compilation blocked by underscore escaping in filenames (format issue, not content issue).

## Build claims not allowed
- The manuscript compiled successfully.
- A PDF was built.
- The scaffold is submission-ready.

## Claim audit table
| build_asset | allowed_claim | prohibited_claim | evidence_boundary | next_action |
| --- | --- | --- | --- | --- |
| pdflatex detection | Tool available | Build successful | Tool found but compile failed | Fix underscores |
| main.tex preflight | Structure valid | Compiles | Section inputs present | Fix paths |
| Table files | 3 tables created | Compile-safe | Underscores in paths block compile | Fix or use path/url |
| references.bib | 16 entries present | BibTeX resolves | Not tested (pdflatex failed first) | Test after compile fix |
| Smoke build | Attempted | Successful | Failed — underscore escaping | P19: fix and retry |
