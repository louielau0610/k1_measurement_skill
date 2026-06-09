---
name: autoresearch
description: Use for research-grade literature review, citation verification, related-work mapping, claim registry updates, paper evidence tracking, and experiment-planning support for robotics or engineering research projects. Do not use for fabricating citations, unsupported novelty claims, or unverified experimental results.
---

# Autoresearch

Use this skill for research-grade work in `k1_measurement_skill`, especially M13+ literature review, claim tracking, method comparison, dataset schema design, experiment planning, and paper drafting for navigation-aware velocity response calibration of closed-source legged robots.

This skill is instruction-only. Do not run external scripts, add API keys, fabricate citations, fabricate paper claims, run ROS2 commands, call Booster SDK movement commands, or modify robot-control code.

## 1. Clarify Research Target

Before producing research output, identify:

- Research question.
- Target domain and subdomain.
- Task type: literature search, related work synthesis, claim audit, experiment planning, dataset schema design, method comparison, or manuscript support.
- Expected output file path.
- Evidence standard: abstract-only, metadata-verified, full-text-inspected, or project-evidence-backed.

If the task asks for novelty, superiority, or state-of-the-art claims, require a literature comparison and mark the claim as unverified until evidence exists.

## 2. Source Hierarchy

Prefer sources in this order:

1. Peer-reviewed papers.
2. Official conference or journal pages.
3. arXiv preprints, clearly marked as preprint status.
4. Official project pages or official lab pages.
5. Official documentation.
6. Reputable lab, university, or standards pages.

Avoid relying on:

- Unsourced blog posts.
- SEO pages.
- Generated summaries.
- Unverifiable citation lists.
- Memory-only metadata.

When web access is unavailable, do not invent sources. State search status and create a research plan or placeholder matrix instead.

## 3. Citation Verification

For every cited paper, record:

- title
- authors
- year
- venue or preprint status
- DOI if available
- arXiv ID if available
- official URL or PDF URL
- whether metadata was verified
- whether full text was inspected or only abstract/metadata

Never fabricate DOI, arXiv ID, venue, author list, publication year, or paper claims. Never claim a paper was read unless its abstract, official metadata, or full text was actually inspected. Mark `reading_status` explicitly.

## 4. Literature Matrix

Maintain or create:

```text
paper/related_work/literature_matrix.md
```

Required columns:

- citation_key
- title
- authors_year
- venue
- problem
- method
- robot_or_platform
- dataset_or_experiment
- metrics
- key_findings
- limitations
- relevance_to_our_work
- difference_from_our_work
- verified_source
- reading_status

Keep rows concise and citation-safe. If metadata is incomplete, leave fields as `TBD` and mark `reading_status` accordingly.

## 5. Paper Notes

For important papers, create:

```text
paper/related_work/notes/{citation_key}.md
```

Each note must include:

- bibliographic metadata
- research question
- method summary
- assumptions
- experiment setup
- metrics
- results summary
- limitations
- how it affects our project
- safe quotable claims
- citation-ready BibTeX if verified

Separate summary from interpretation. Do not over-quote. Do not copy long passages.

## 6. Claim Registry

Maintain or create:

```text
paper/claims/claim_registry.md
paper/claims/evidence_table.md
paper/claims/non_claims.md
```

Classify every project claim as one of:

- supported by our experiment
- supported by prior work
- plausible but unverified
- planned experiment
- unsupported and must not be stated

Project evidence and literature evidence must remain separate. A claim can be manuscript-ready only when evidence source, evidence type, and confidence are explicit.

## 7. Anti-Hallucination Rules

Always enforce:

- Never invent citations.
- Never invent experimental results.
- Never infer a venue from memory without verification.
- Never claim novelty without literature comparison.
- Explicitly mark uncertainty.
- Separate summary from interpretation.
- Separate paper evidence from project evidence.
- Separate verified facts, cited prior work, project evidence, hypotheses, planned experiments, and unsupported claims.
- Do not claim our method outperforms baselines unless experiments exist.

## 8. Robotics-Specific Research Lens

For this repository, pay special attention to:

- legged robot locomotion
- velocity tracking mismatch
- black-box system identification
- command-to-motion calibration
- sim-to-real calibration
- navigation safety
- local planner and locomotion-controller mismatch
- uncertainty-aware deployment
- field robotics evaluation metrics
- closed-source robot SDK constraints

Prefer comparisons that clarify how navigation-level velocity commands differ from low-level locomotion control, and how measurement artifacts support downstream compensation or warning layers.

## 9. Output Style

Research notes should be concise but complete.

- Use Chinese-first style for project notes and repository documentation.
- Keep paper titles, BibTeX, technical terms, and manuscript drafts in English when appropriate.
- Use tables for comparison and claim tracking.
- Avoid marketing language and unsupported novelty framing.

## 10. Final Quality Checks

Before completing any research task, check:

- Are all citations verified?
- Are unverified claims marked?
- Are project claims separated from literature claims?
- Are URLs, DOI, or arXiv IDs recorded when available?
- Is the output useful for manuscript writing or experiment planning?
- Did the task avoid overclaiming?
- Did the task avoid ROS2 commands, Booster SDK movement commands, and real robot commands?
