"""Tests for M23-C K1 before/after compensation analysis."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import analyze_m23c_k1_compensation_results as analysis

SESSION_DIR = ROOT / "data/compensation_experiments/m23b_k1/m23b_k1_s2_executable_20260612_121605"
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
SUMMARY_JSON = OUTPUT_DIR / "m23c_k1_analysis_summary.json"
PAIR_CSV = OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
PER_VELOCITY_CSV = OUTPUT_DIR / "m23c_k1_per_velocity_summary.csv"
REPORT_MD = OUTPUT_DIR / "m23c_k1_analysis_report.md"
CLAIM_BOUNDARY_MD = OUTPUT_DIR / "m23c_k1_claim_boundary.md"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_result_package_ingested_with_provenance() -> None:
    assert SESSION_DIR.exists()
    assert (SESSION_DIR / "extracted_results.csv").exists()
    assert (SESSION_DIR / "trial_records.csv").exists()
    assert (SESSION_DIR / "extraction_summary.json").exists()
    assert (SESSION_DIR / "qc_summary.json").exists()
    assert (SESSION_DIR / "source_archive.tar.gz").exists()
    provenance = json.loads((SESSION_DIR / "source_provenance.json").read_text(encoding="utf-8"))
    assert provenance["source_archive_sha256"] == "D7D24FEDF10B12C9AEC9BDF12CD8C788DF0E88844633F3A9EDCDBBCA1A26B547"


def test_analysis_detects_24_trials_and_12_pairs() -> None:
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    assert summary["validation"]["trial_count"] == 24
    assert summary["validation"]["pair_count"] == 12
    assert summary["validation"]["passed"] is True


def test_pair_metrics_computed() -> None:
    rows = _read_csv(PAIR_CSV)
    assert len(rows) == 12
    for row in rows:
        assert row["direct_abs_error"]
        assert row["compensated_abs_error"]
        assert row["improvement"]
        assert row["yaw_drift_delta"] != ""


def test_per_velocity_summaries_generated() -> None:
    rows = _read_csv(PER_VELOCITY_CSV)
    assert [row["desired_velocity_mps"] for row in rows] == ["0.4", "0.45", "0.5", "0.55"]
    assert all(row["pair_count"] == "3" for row in rows)


def test_analysis_summary_includes_claim_level() -> None:
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    assert summary["claim_level"] == "negative_result_requires_compensator_revision"
    assert summary["aggregate_metrics"]["mean_absolute_error_direct"] < summary["aggregate_metrics"]["mean_absolute_error_compensated"]


def test_report_contains_no_forbidden_positive_claims() -> None:
    text = REPORT_MD.read_text(encoding="utf-8").lower()
    assert "does not claim deployment readiness" in text
    assert "go1/g1 validation" in text
    assert "universal k1 generalization" in text
    assert "deployment_ready\": true" not in text
    assert "go1_g1_validation_claimed\": true" not in text


def test_analysis_handles_missing_scipy_gracefully() -> None:
    stats = analysis.compute_statistical_tests([0.1, -0.2, 0.05], skip_scipy=True)
    assert stats["scipy_available"] is False
    assert stats["paired_t_test"] is None
    assert any("skipped" in note for note in stats["notes"])


def test_output_artifacts_exist() -> None:
    assert SUMMARY_JSON.exists()
    assert PAIR_CSV.exists()
    assert PER_VELOCITY_CSV.exists()
    assert REPORT_MD.exists()
    assert CLAIM_BOUNDARY_MD.exists()


def test_claim_boundary_file_preserves_limits() -> None:
    text = CLAIM_BOUNDARY_MD.read_text(encoding="utf-8")
    assert "Deployment readiness" in text
    assert "GO1 or G1 validation" in text
    assert "Cross-platform physical validation" in text
    assert "deployment_ready=true" not in text
    assert "go1_g1_validation_claimed=true" not in text
