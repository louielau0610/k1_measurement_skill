# M19 Figure Rendering Report

## Purpose

Document the figure rendering process for M19. Converts method pipeline and evidence chain figure specifications (`.md` specs) into rendered assets (`.mmd` Mermaid source files) ready for final SVG/PNG export.

## Inputs inspected

- `paper/figures/method_pipeline_figure_spec.md`
- `paper/figures/evidence_chain_figure_spec.md`

## Figure generation process

1. **Script**: `scripts/generate_m19_figures.py` reads the Mermaid diagram definitions from figure specs.
2. **Output**: `.mmd` Mermaid source files generated in `paper/figures/`.
3. **Metadata**: `.meta.json` files generated with captions and rendering instructions.
4. **Final rendering**: Use Mermaid CLI (`mmdc`) or https://mermaid.live to produce `.svg` or `.png` files from `.mmd` sources.

## Generated assets

| figure | mmd_source | meta_json | spec_source | status |
| --- | --- | --- | --- | --- |
| Method pipeline | `method_pipeline_figure.mmd` | `method_pipeline_figure.meta.json` | `method_pipeline_figure_spec.md` | ready for rendering |
| Evidence chain | `evidence_chain_figure.mmd` | `evidence_chain_figure.meta.json` | `evidence_chain_figure_spec.md` | ready for rendering |

## Figure contents

### Method pipeline figure
- **Title**: "Artifact-Governed Velocity Response Pipeline"
- **Nodes**: 12 nodes (Measurement v0 through claim audit)
- **Flow**: left-to-right pipeline stages with validation lane
- **Safety markers**: red "PROHIBITED" boundary node listing all excluded capabilities
- **Style**: data flow nodes in blue, validation nodes in yellow, prohibited node in red

### Evidence chain figure
- **Title**: "Evidence Chain and Claim Governance"
- **Nodes**: 15 nodes (raw evidence through claim categories)
- **Flow**: top-down evidence chain branching into claim governance categories
- **Claim categories**: supported (green), literature (blue), candidate (yellow), requires experiment (orange), prohibited (red)
- **Safety claim markers**: 5 red nodes explicitly listing prohibited claims

## Claim safety in figures

Both figures were designed to satisfy the M18/M19 claim audit requirements:
- Method pipeline figure explicitly labels the PROHIBITED execution paths.
- Evidence chain figure color-codes prohibited claim categories in red.
- No figure shows compensation, navigation control, safe adapter, collision metrics, or success-rate metrics as available evidence.
- Both figures align with the claim boundary: "structural/artifact-level evidence only."

## Post-generation steps

1. Render SVGs: `mmdc -i paper/figures/method_pipeline_figure.mmd -o paper/figures/method_pipeline_figure.svg`
2. Render SVGs: `mmdc -i paper/figures/evidence_chain_figure.mmd -o paper/figures/evidence_chain_figure.svg`
3. Embed in LaTeX or reference in manuscript v1 assembly.
