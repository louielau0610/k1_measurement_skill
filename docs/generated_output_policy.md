# Generated Output Policy

This repository keeps source contracts, scientific summaries, and reproducibility manifests under version control, while local execution scratch files stay untracked.

## Tracked Source Artifact

Configuration templates, schemas, scripts, tests, and documentation that define behavior are tracked. Examples include `configs/*.yaml`, `contracts/*.json`, `scripts/*.py`, and `docs/*.md`.

## Tracked Scientific Summary

Small summary artifacts may be tracked when they preserve milestone decisions, validation status, or auditability. Examples include curated JSON/Markdown reports under `outputs/` that are referenced by README, status files, or tests.

## Untracked Raw Session

Local real-robot session directories under `data/measurement_sessions/` are ignored by default. They may contain raw logs, operator notes, local paths, and large files. They must not be automatically deleted. If a raw session becomes official evidence, promote it deliberately through a documented data-ingestion step rather than relying on incidental Git status.

## Reproducible Generated Output

Regenerable scratch files such as temporary M25 safe-speed validation configs, fixture CSVs, write probes, cache files, and local preflight probes should remain untracked. `.gitignore` covers the known M25-R scratch patterns.

## Temporary Local Artifact

Timestamp-only reruns, pytest-created local sessions, and dry-run scratch outputs should be removed or ignored only when ownership is clear. Unknown-ownership files are preserved and documented in `docs/m25r_working_tree_classification.md`.

## Migration Rule

Do not newly ignore files that are already intentionally tracked unless a separate migration commit documents why the tracked artifact is no longer part of the scientific record.
