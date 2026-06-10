# P19 LaTeX Recovery Claim Audit

## Compile-recovery claims allowed
- Non-final PDF smoke build succeeded (build_main.pdf, 3 pages).
- All 3 tables render correctly in PDF.
- Abstract renders correctly.
- Underscore escaping resolved via `\_`.

## Claims not allowed
- The full manuscript has been compiled.
- The PDF is submission-ready.
- The PDF represents final formatted output.

## Claim audit table
| asset | allowed_claim | prohibited_claim | evidence_boundary | next_action |
| --- | --- | --- | --- | --- |
| build_main.pdf | Non-final smoke PDF exists | Submission-ready PDF | 3 pages, placeholder content | P20: full content |
| Table 1-3 | Tables compile and render | Final formatted tables | Standard tabular, hline | P20: polish |
| Abstract | Abstract compiles correctly | Final published abstract | 193 words | P20: full content |
| Underscore fix | `\_` escaping works in tables | All path issues resolved | Works in current files | P20: verify all files |
