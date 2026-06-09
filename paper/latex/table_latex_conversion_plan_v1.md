# Table LaTeX Conversion Plan v1

## Main paper tables (3)

| table_id | title | source_md | suggested_latex_env | caption_source | width_risk | claim_boundary | priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Method Stage I/O Contract | `paper/tables/main_paper_table_pack_v1.md` (T1) | `table` with `tabularx` or `tabular` | `paper/tables/table_caption_pack_v1.md` (T1) | medium (5 columns + notes) | Structural I/O only; non-goals column | P1_high |
| Table 2 | Current Evaluation Metrics | `paper/tables/main_paper_table_pack_v1.md` (T2) | `table` with `tabular` | `paper/tables/table_caption_pack_v1.md` (T2) | low (3 columns) | Available = structural only | P1_high |
| Table 3 | Claim-Upgrade Requirements | `paper/tables/main_paper_table_pack_v1.md` (T3) | `table` with `tabularx` | `paper/tables/table_caption_pack_v1.md` (T3) | high (compact 2-column) | Prohibited claims marked | P2_medium |

## Appendix tables (selected)

| table | source_md | suggested_latex_env | appendix_or_internal | priority |
| --- | --- | --- | --- | --- |
| Numeric Traceability | `paper/tables/numeric_traceability_table.md` | `longtable` | appendix A | P3_low |
| Citation Audit | `paper/tables/citation_audit_table.md` | `longtable` | appendix B | P3_low |
| Terminology | `paper/tables/terminology_consistency_table.md` | `table` | appendix C | P3_low |
| Claim Upgrade Matrix | `paper/tables/m20_claim_upgrade_evidence_matrix.md` | `longtable` | appendix D | P3_low |

Remaining 7 audit tables: deferred to appendix only if venue page limits permit; otherwise internal documentation only.

## Conversion notes

- Convert Markdown tables to LaTeX `tabular` environments manually or via pandoc.
- Preserve caption claim-boundary wording from caption packs.
- Tables wider than column width should use `tabularx` or `resizebox`.
- Appendix tables may use `longtable` for multi-page support.
