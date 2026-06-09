# Figure Rendering Plan v1

| source_figure | intended_final_filename | preferred_format | caption_source | finalization_status |
| --- | --- | --- | --- | --- |
| `paper/figures/method_pipeline_figure.mmd` | `paper/latex/figures/method_pipeline_figure.svg` | SVG | `figure_caption_pack_v1.md` (F1) | PENDING mmdc/mermaid.live |
| `paper/figures/evidence_chain_figure.mmd` | `paper/latex/figures/evidence_chain_figure.svg` | SVG | `figure_caption_pack_v1.md` (F2) | PENDING mmdc/mermaid.live |
| `paper/figures/current_evidence_gap_v1.md` | `paper/latex/figures/current_evidence_gap.svg` | SVG | `figure_caption_pack_v1.md` (F3) | PENDING mmdc/mermaid.live |

## Rendering commands (when tools available)
- `mmdc -i method_pipeline_figure.mmd -o method_pipeline_figure.svg`
- `mmdc -i evidence_chain_figure.mmd -o evidence_chain_figure.svg`
- Or: copy .mmd to https://mermaid.live → export SVG

## Claim safety
All 3 figures verified claim-safe per M19.1 audit. Prohibited paths and claim categories explicitly marked. No figure shows compensation, navigation control, or safe adapter as available evidence.
