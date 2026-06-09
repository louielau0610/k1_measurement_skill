# Table Caption Pack v1

## Main Paper Tables

| table_id | short_title | intended_location | source_file | caption | claim_boundary_note | status |
| --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Method Stage I/O Contract | Method §3 | `paper/tables/main_paper_table_pack_v1.md` (Table 1) | Input/output contract for the five-stage artifact-governed velocity response pipeline. Each stage lists its input, output, producer script, and explicit non-goals. The table documents what the method implements and what it deliberately excludes. | Structural pipeline description only. Does not validate performance or safety. | draft (condensed from source) |
| Table 2 | Current Evaluation Metrics | Experiments §4 | `paper/tables/main_paper_table_pack_v1.md` (Table 2) | Summary of currently available structural metrics and unavailable performance/safety metrics for the K1 velocity response pipeline. Available metrics are artifact-backed; unavailable metrics require future experiments before being claimed. | Available metrics are structural only. Unavailable metrics are explicitly documented. | draft (condensed from source) |
| Table 3 | Evidence Boundary / Claim-Upgrade Requirements | Discussion §5 or Appendix | `paper/tables/main_paper_table_pack_v1.md` (Table 3) | Claim-upgrade requirements mapping each claim type to its current status and the evidence required before upgrading. Documents which claims are supported, which require more experiments, and which remain prohibited until evidence exists. | Prohibited claims are explicitly marked. No claim is shown as supported without evidence. | draft (condensed from source) |

## Appendix Tables

| table_id | short_title | intended_location | source_file | caption | claim_boundary_note | status |
| --- | --- | --- | --- | --- | --- | --- |
| Table A1 | Numeric Traceability | Appendix A | `paper/tables/numeric_traceability_table.md` | Traceability of all numeric values reported in the manuscript to their source artifacts. Each row documents the metric, its manuscript location, source artifact, and interpretation boundary. | All numbers verified against output artifacts. Interpretation boundaries documented. | complete |
| Table B1 | Citation Audit | Appendix B | `paper/tables/citation_audit_table.md` | Full citation audit for all literature entries. Documents presence in seed references, verification status, manuscript usage, and safety of each citation. | No rejected or unverified sources cited. Partially verified sources used only for context. | complete (P13 updated) |
| Table C1 | Manuscript Section Status | Appendix C | `paper/tables/manuscript_section_status_table.md` | Status of each manuscript section, including current draft version, evidence source, citation status, and next action. | All sections drafted. Abstract and Conclusion complete. | complete |
| Table D1 | Terminology Consistency | Appendix D | `paper/tables/terminology_consistency_table.md` | Standardized terminology used throughout the manuscript with preferred terms, allowed variants, and discouraged variants. | Terms are consistent across all sections. No terminology drift. | complete |
