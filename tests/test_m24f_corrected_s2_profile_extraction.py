"""Tests for M24-F corrected S2 profile refresh extraction and analysis."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_ID = "m24b_s2_profile_refresh_clean_20260612_145358"
SESSION_DIR = ROOT / "data/compensation_experiments/m24b_s2_profile_refresh" / SESSION_ID
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"

EXTRACTED = SESSION_DIR / "corrected_extracted_results.csv"
EXTRACT_SUMMARY = SESSION_DIR / "corrected_extraction_summary.json"
QC_SUMMARY = SESSION_DIR / "corrected_qc_summary.json"
SUMMARY = OUTPUT_DIR / "m24f_corrected_s2_profile_refresh_summary.json"
PER_VELOCITY = OUTPUT_DIR / "m24f_corrected_s2_per_velocity_summary.csv"
COMPARISON = OUTPUT_DIR / "m24f_faulty_vs_corrected_extraction_comparison.csv"
SUPERSESSION = OUTPUT_DIR / "m24f_supersession_notice.json"
DOC = ROOT / "docs/m24f_corrected_extraction_and_profile_analysis.md"
BOUNDARY_DOC = ROOT / "docs/m24f_m24c_supersession_boundary.md"
SCRIPT = ROOT / "scripts/analyze_m24f_corrected_s2_profile_refresh.py"

ALLOWED_DECISIONS = {
    "old_profile_confirmed_current_after_correction",
    "old_profile_stale_current_s2_profile_needed_after_correction",
    "corrected_analysis_inconclusive",
    "corrected_extraction_failed",
}

spec = importlib.util.spec_from_file_location("m24f_analysis", SCRIPT)
m24f_analysis = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m24f_analysis)


def test_corrected_extraction_output_exists_and_has_30_rows() -> None:
    rows = _read_csv(EXTRACTED)
    assert len(rows) == 30
    assert {row["surface"] for row in rows} == {"S2_marble_floor"}
    assert {row["extraction_status"] for row in rows} == {"ok"}
    assert all(row["measured_actual_velocity_mps"] != "" for row in rows)
    assert all(row["yaw_drift_deg"] != "" for row in rows)


def test_corrected_qc_passes_direct_refresh_only() -> None:
    data = json.loads(QC_SUMMARY.read_text(encoding="utf-8"))
    assert data["overall_pass"] is True
    assert data["corrected_extracted_count"] == 30
    assert data["trial_record_count"] == 30
    assert data["condition_values"] == ["direct_refresh"]
    assert data["velocity_group_count"] == 6
    assert set(data["repeats_per_velocity"].values()) == {5}
    assert data["original_faulty_extraction_used"] is False


def test_corrected_velocities_are_not_all_near_zero() -> None:
    rows = _read_csv(PER_VELOCITY)
    assert len(rows) == 6
    means = [abs(float(row["mean_actual_velocity_mps"])) for row in rows]
    assert max(means) >= 0.02
    assert any(float(row["no_motion_rate"]) < 1.0 for row in rows)


def test_faulty_vs_corrected_comparison_catches_large_difference() -> None:
    rows = _read_csv(COMPARISON)
    assert len(rows) == 30
    factors = [abs(float(row["correction_factor"])) for row in rows if row["correction_factor"]]
    diffs = [float(row["absolute_difference_mps"]) for row in rows]
    assert max(factors) > 10.0
    assert max(diffs) > 0.05
    assert any(row["faulty_value_near_zero"] == "True" and row["corrected_value_plausible"] == "True" for row in rows)


def test_corrected_profile_summary_and_decision_boundaries() -> None:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["corrected_extraction_trial_count"] == 30
    assert data["corrected_qc_pass"] is True
    assert data["corrected_profile_decision"] in ALLOWED_DECISIONS
    assert data["corrected_profile_decision"] == "corrected_analysis_inconclusive"
    assert data["m24c_artifacts_superseded"] is True
    assert data["gold_profile_overwritten"] is False
    assert data["candidate_profile_adopted"] is False
    assert data["compensation_improvement_claimed"] is False
    assert data["deployment_ready"] is False
    assert data["go1_g1_blocked"] is True


def test_m24c_supersession_notice_exists() -> None:
    data = json.loads(SUPERSESSION.read_text(encoding="utf-8"))
    assert data["superseded_milestone"] == "M24-C"
    assert data["m24c_artifacts_retained_for_traceability"] is True
    assert data["gold_profile_overwritten"] is False
    assert "m24f_corrected_s2_profile_refresh_summary.json" in data["use_instead"]


def test_gold_profile_not_overwritten_by_analysis_rerun(tmp_path: Path) -> None:
    before = _sha256(GOLD_PROFILE)
    args = _Args(tmp_path)
    result = m24f_analysis.analyze(args)
    after = _sha256(GOLD_PROFILE)
    assert before == after
    assert result["summary"]["gold_profile_overwritten"] is False
    assert result["summary"]["candidate_profile_adopted"] is False


def test_documentation_records_boundaries() -> None:
    assert DOC.exists()
    assert BOUNDARY_DOC.exists()
    text = (DOC.read_text(encoding="utf-8") + "\n" + BOUNDARY_DOC.read_text(encoding="utf-8")).lower()
    assert "does not run hardware" in text
    assert "gold profile remains unchanged" in text or "gold profile overwritten: `false`" in text
    assert "candidate remains a candidate only" in text
    assert "deployment ready: `false`" in text


class _Args:
    def __init__(self, output_dir: Path) -> None:
        self.session_dir = SESSION_DIR
        self.old_profile = GOLD_PROFILE
        self.m23c_pairs = OUTPUT_DIR / "m23c_k1_before_after_pairs.csv"
        self.output_dir = output_dir
        self.profile_mismatch_threshold = 0.03
        self.m23c_consistency_threshold = 0.03
        self.near_optimal_threshold = 0.02


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
