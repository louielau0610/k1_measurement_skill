# Paper Workspace

This workspace is for research-grade notes, related-work tracking, claim governance, experiment planning, and manuscript preparation.

Do not fabricate citations, DOI, arXiv IDs, venues, author lists, or experimental results. Keep project evidence separate from cited prior work.

## P1 Seed Literature Matrix

P1 adds seed literature search, literature matrix v1, citation verification artifacts, rejected-source logging, and conservative gap candidates. P1 does not write the final related-work section, does not claim novelty, and does not claim publication readiness.

## P2 Gap Analysis and Positioning

P2 analyzes P1 literature clusters against M13-M17 project artifacts, creates contribution candidates, claim-upgrade rules, and paper framing options. P2 does not write the paper manuscript, does not claim final novelty, and does not claim publication readiness.

## M18 Method Skeleton and Claim Audit

M18 creates the paper method skeleton, experiments skeleton, figure specifications, artifact/evidence tables, manuscript scaffold, and strict claim audit. M18 does not write a full paper draft, does not claim final novelty, and does not claim performance superiority or publication readiness.

## P3 Related Work Draft v1

P3 creates a citation-safe Related Work draft v1 that synthesizes P1/P2 literature and respects M18 claim boundaries. The draft uses only verified/partially verified citation keys from `paper/related_work/seed_references.bib`. P3 does not claim final novelty, performance superiority, or publication readiness.

## P4 Introduction and Problem Statement Draft v1

P4 creates a citation-safe Introduction draft, formal Problem Statement, and title/contribution options. P4 synthesizes P1-P3 literature and M18 method skeleton. P4 does not write a final abstract, does not claim final novelty, and does not claim performance superiority or publication readiness.

## P5 Method Section Draft v1

P5 creates an academic Method draft v1 from M13-M18 artifacts with formal notation, algorithmic contracts, artifact traceability, and claim audit. P5 does not implement engineering functionality and does not claim novelty or performance.

## P6 Experiments and Evaluation Draft v1

P6 creates an academic Experiments/Evaluation draft v1 reporting structural evaluation only: dataset evidence, model sanity checks, risk-map assessment, and claim-governed evaluation. P6 does not claim navigation performance or safety improvement.

## P7 Discussion and Limitations Draft v1

P7 creates an academic Discussion and Limitations draft v1 interpreting the pipeline, its limitations, and future work. P7 adds a claim-upgrade requirements table. P7 does not write a final conclusion or claim navigation performance.

## P8 Manuscript Assembly v0

P8 assembles all P3-P7 section drafts into a manuscript v0 and performs a cross-section consistency audit. P8 identifies remaining gaps and recommended next milestones. P8 does not write final abstract or conclusion, and does not claim publication readiness.

## P9 Conclusion Draft v1

P9 creates an academic Conclusion draft v1 completing the manuscript narrative. The conclusion is confident but bounded, summarizing the pipeline, current evidence, and future work without claiming novelty, performance superiority, or publication readiness.

## P10 Abstract Draft v1

P10 creates an academic Abstract draft v1 (193 words primary) with short and extended variants. P10 completes the first full manuscript narrative from Abstract through Conclusion. P10 does not claim final novelty or publication readiness.

## P11 Full Manuscript Claim Audit

P11 performs a comprehensive full-manuscript claim audit and creates a prioritized revision plan. P11 audits 19 claims, 12 numeric items, 16 citation keys. 0 blocking issues found. Submission readiness: not_submission_ready. P11 does not write new manuscript sections and does not claim publication readiness.

## P12 Manuscript Revision v1

P12 creates manuscript v1 assembly, revision changelog, consistency check, and resolves 5/8 Codex-editable P11 audit issues. P12 does not add new scientific results and does not claim publication readiness.

## P13 Reference and BibTeX Cleanup

P13 resolves 8 matrix-only BibTeX entries from verified P1 metadata, adds 3 new manuscript citations to strengthen Related Work §4/§5, and creates comprehensive citation audit reports. P13 does not add new experimental evidence or claim publication readiness.

## M19 Figure Rendering and Table Assets

M19 generates Mermaid figure sources (.mmd) for the method pipeline and evidence chain figures, ready for SVG rendering. M19 does not add new experimental evidence and does not claim publication readiness.

## M19.1 Figure/Table Caption and Integration Assets

M19.1 completes missing figure/table caption packs, table packs (main + appendix), evidence-gap figure spec, integration plan, and figure/table claim audit. M19.1 does not add new experimental evidence and does not claim publication readiness.

## P14 Manuscript v2 Polish

P14 creates polished manuscript v2 assembly integrating M19/M19.1 figure/table assets with proper placement, captions, and appendix separation. P14 does not add new experimental evidence and does not claim publication readiness.

## M20 Future Experiment Protocol

M20 designs the future experiment protocol for real navigation outcome evaluation across 4 tiers with 35 defined metrics, claim-upgrade criteria, schema/validator/tests. Protocol only — no experiments executed.

## M21.1 Data Collection Pack Completion

M21.1 closes M21 completion gaps: navigation task JSON template, validator/test updates, M20/experiment_plan cross-references. Pack-only — no experiments executed.

## P16 Non-Final LaTeX Scaffold

P16 creates non-final LaTeX scaffold: 17 files including main.tex, macros, references.bib, 8 section .tex files, placeholder figures/tables. No PDF built, no submission package.

## P16.1 LaTeX Scaffold Evidence Patch

P16.1 links P16 scaffold into evidence table, updates P16 summary consistency, runs git diff --check. No PDF, no figures, no tables. Not submission ready.

## P17 Figure/Table LaTeX Assets

P17 creates 3 LaTeX table files, copies Mermaid figure sources, and documents rendering status. No PDF built. Not submission ready.

## P18 LaTeX Compile Validation

P18 validates LaTeX scaffold: pdflatex found, structure valid, compile attempted. Full compile blocked by underscore escaping in filenames (documented). P19 should fix and retry.

## P19 LaTeX Path Escaping Recovery

P19 resolves P18 underscore blocker. Smoke PDF built (build_main.pdf, 3pp, 95KB). Full main.tex compilation deferred to P20. Not submission ready.

## M19-A Repeated Real K1 Validation Pack

M19-A implements repeated validation infrastructure: protocol, schema, analyzer, 10 tests. Runs in pending-data mode (no real repeated logs). No robot access attempted.
