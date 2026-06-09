"""Render method pipeline and evidence chain figures for M19."""
from __future__ import annotations
from pathlib import Path
import json

OUTPUT_DIR = Path("paper/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Method pipeline figure — Mermaid-based SVG via inline rendering
METHOD_MERMAID = """flowchart LR
    A["Measurement v0<br/>artifacts"] --> B["Schema v1<br/>mapping"]
    B --> C["Dataset v1<br/>(5 records)"]
    C --> D["Response model<br/>(uncertainty-aware)"]
    C --> E["Baseline hooks<br/>(3 interfaces)"]
    D --> F["Response predictions<br/>(5 predictions)"]
    E --> F
    F --> G["Navigation risk<br/>mapper"]
    G --> H["Offline risk map<br/>(5 assessments)"]
    C --> V1["Dataset validation<br/>report"]
    F --> V2["Model evaluation<br/>(sanity checks)"]
    H --> V3["Risk evaluation<br/>(warning counts)"]
    V1 --> I["M17 pipeline<br/>evaluation"]
    V2 --> I
    V3 --> I
    I --> J["Claim registry"]
    I --> K["Non-claims"]
    I --> L["M18/M19 claim audit"]
    H -.-> X["<b>PROHIBITED:</b><br/>No compensation<br/>No navigation control<br/>No safe adapter"]
    style X fill:#f88,stroke:#c00,stroke-width:2px
    style D fill:#adf,stroke:#358
    style G fill:#adf,stroke:#358
    style I fill:#ffa,stroke:#a80
"""

EVIDENCE_MERMAID = """flowchart TD
    A["Raw measurement<br/>evidence"] --> B["Dataset validation<br/>(schema compliance)"]
    B --> C["Model prediction<br/>contract"]
    C --> D["Risk map<br/>output"]
    D --> E["Pipeline evaluation<br/>report"]
    E --> F["Supported<br/>structural/software<br/>claims"]
    E --> G["Literature<br/>context claims"]
    E --> H["Candidate<br/>contributions"]
    E --> I["Requires more<br/>experiment"]
    E --> J["Non-claims"]
    J --> K["No navigation<br/>safety improvement"]
    J --> L["No collision<br/>reduction"]
    J --> M["No success-rate<br/>improvement"]
    J --> N["No compensation<br/>readiness"]
    J --> O["No safe<br/>adapter readiness"]
    style A fill:#dfd,stroke:#385
    style F fill:#dfd,stroke:#385
    style G fill:#adf,stroke:#358
    style H fill:#ffa,stroke:#a80
    style I fill:#fca,stroke:#c80
    style J fill:#faa,stroke:#c00
    style K fill:#fcc,stroke:#c00
    style L fill:#fcc,stroke:#c00
    style M fill:#fcc,stroke:#c00
    style N fill:#fcc,stroke:#c00
    style O fill:#fcc,stroke:#c00
"""

def save_mermaid_figure(mermaid_code: str, output_path: Path, title: str, caption: str):
    """Save a Mermaid diagram as a text-based SVG placeholder and metadata."""
    # Store the Mermaid source for external rendering
    mmd_path = output_path.with_suffix(".mmd")
    mmd_path.write_text(mermaid_code, encoding="utf-8")

    # Create metadata JSON with rendering instructions
    meta = {
        "figure_title": title,
        "caption": caption,
        "mermaid_source": str(mmd_path.name),
        "rendering_note": "Render with mermaid-cli (mmdc) or https://mermaid.live for final SVG/PNG.",
        "rendered": False,
        "format": "mermaid",
    }
    meta_path = output_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"[OK] Mermaid source: {mmd_path}")
    print(f"[OK] Metadata: {meta_path}")

# Generate figures
print("=== Method Pipeline Figure ===")
save_mermaid_figure(
    METHOD_MERMAID,
    OUTPUT_DIR / "method_pipeline_figure",
    "Artifact-Governed Velocity Response Pipeline",
    "Pipeline overview for offline K1 velocity response analysis. Measurement artifacts are converted into schema-governed dataset records, used by a conservative response model, mapped into advisory navigation-risk metadata, and audited through claim governance. The figure explicitly excludes compensation, inverse command mapping, navigation control, and safe command adapter execution."
)

print("\n=== Evidence Chain Figure ===")
save_mermaid_figure(
    EVIDENCE_MERMAID,
    OUTPUT_DIR / "evidence_chain_figure",
    "Evidence Chain and Claim Governance",
    "Evidence chain for the current research pipeline. Raw measurement evidence is converted to validated datasets, model prediction contracts, advisory risk maps, and pipeline evaluation reports. Claim governance separates supported structural/software claims from literature context, candidate contributions, claims requiring more experiment, and prohibited non-claims."
)

print("\n=== M19 Figure Generation Complete ===")
print("To render SVGs: copy .mmd files to https://mermaid.live or use mmdc CLI.")
