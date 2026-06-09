# M19.1 Figure/Table Claim Audit

## Purpose

Verify that all M19.1 figure/table assets respect manuscript claim boundaries and do not introduce overclaims.

## Inputs inspected

M19 figure sources (.mmd), M19.1 evidence-gap figure spec, figure caption pack, main table pack, appendix table pack, table caption pack, P11/P12 claim audits.

## Figure claim boundaries

All 3 figure specifications (Figure 1 pipeline, Figure 2 evidence chain, Figure 3 evidence gap) satisfy claim safety:
- Prohibited execution paths marked in red (Figure 1).
- Prohibited claims color-coded in red (Figure 2).
- Missing evidence framed as transparent boundary map (Figure 3).
- No figure shows compensation, navigation control, safe adapter, collision metrics, or success-rate metrics as available evidence.

## Table claim boundaries

Main-paper tables (Tables 1-3) satisfy claim safety:
- Table 1: Structural I/O contracts only; non-goals column explicitly lists exclusions.
- Table 2: Available metrics clearly separated from "no" entries; held-out MAE marked as "sanity check only."
- Table 3: Prohibited claim types explicitly marked; upgrade requirements documented.

## Caption safety audit

All 10 captions (3 figure + 3 main table + 4 appendix table) scanned for prohibited wording. Results: **0 violations**.

Scanned terms: "improves safety," "reduces collision," "proves," "guarantees," "state-of-the-art," "outperforms," "safe command adapter ready," "navigation control ready," "publication-ready," "deployment-ready," "calibrated uncertainty" (as positive claim).

## Numeric consistency check

All numbers in Main Paper Table Pack (Table 2) verified against P11 numeric traceability:
- 5 records (4 numeric, 1 qualitative) → confirmed
- 5 predictions → confirmed
- 5 risk assessments (critical=1, high=2, medium=2) → confirmed
- 5 warnings → confirmed
- Exact-source MAE=0.0 → confirmed, marked as "sanity check only"

## Prohibited visual interpretations

The following visual interpretations are avoided in all figures:
- No arrow from risk map to "improved navigation" or "reduced collisions."
- No green/positive coloring for unavailable metrics.
- No claim that the evidence gap will be closed in future work.
- No "ready for deployment" or "validated pipeline" labeling.

## Remaining figure/table risks

- Figures are Mermaid source only (.mmd) — final rendering quality depends on external rendering tool.
- Appendix table pack is comprehensive but venue-dependent; some tables may be removed for page limits.
- Main-paper tables are condensed from source tables; source tables should be cross-checked if condensed versions are used in final submission.

## Submission-readiness boundary

**Not submission ready.** Figure/table assets are prepared but not rendered. Manuscript requires LaTeX conversion, figure SVG rendering, and table formatting before submission.

## Claim audit table

| asset | claim_risk | evidence_source | allowed_caption_wording | prohibited_caption_wording | action_needed |
| --- | --- | --- | --- | --- | --- |
| Figure 1 (Method Pipeline) | low | M19 .mmd + spec | "Pipeline overview... advisory navigation-risk metadata... prohibited downstream paths" | "validated pipeline," "proven navigation safety" | render SVG |
| Figure 2 (Evidence Chain) | low | M19 .mmd + spec | "Claim governance separates... prohibited non-claims including..." | "all claims are supported," "publication-ready" | render SVG |
| Figure 3 (Evidence Gap) | low | M19.1 spec | "Available evidence... Missing evidence... future experiments required" | "evidence proves safety," "gap will be closed" | extract + render Mermaid |
| Table 1 (I/O Contract) | low | method artifacts | "Input/output contract... explicit non-goals" | "validates performance," "compensation-ready" | condense for LaTeX |
| Table 2 (Metrics) | low | experiment metrics table | "Available metrics are structural only" | "comprehensive evaluation," "calibrated metrics" | condense for LaTeX |
| Table 3 (Claim-Upgrade) | low | claim-upgrade table | "Prohibited claims remain prohibited until evidence exists" | "claims can be upgraded," "near-ready" | condense for LaTeX |
