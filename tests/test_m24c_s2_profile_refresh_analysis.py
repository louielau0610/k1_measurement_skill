"""Tests for M24-C S2 profile refresh analysis."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_ID = "m24b_s2_profile_refresh_clean_20260612_145358"
PARTIAL_SESSION_ID = "m24b_s2_profile_refresh_20260612_143912"
SESSION_DIR = ROOT / "data/compensation_experiments/m24b_s2_profile_refresh" / SESSION_ID
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
SCRIPT = ROOT / "scripts/analyze_m24c_s2_profile_refresh.py"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"

SUMMARY = OUTPUT_DIR / "m24c_s2_profile_refresh_summary.json"
INGESTION = OUTPUT_DIR / "m24c_ingestion_summary.json"
PER_VELOCITY = OUTPUT_DIR / "m24c_s2_per_velocity_summary.csv"
OLD_NEW = OUTPUT_DIR / "m24c_s2_old_vs_new_profile_comparison.csv"
M23C_CHECK = OUTPUT_DIR / "m24c_s2_m23c_consistency_check.csv"
CANDIDATE = OUTPUT_DIR / "m24c_s2_current_profile_candidate.json"
REPORT = OUTPUT_DIR / "m24c_s2_profile_refresh_report.md"

ALLOWED_DECISIONS = {
    "old_profile_stale_current_s2_profile_needed",
    "old_profile_confirmed_current",
    "inconclusive_environment_dependent",
    "analysis_invalid_missing_data",
}

spec = importlib.util.spec_from_file_location("m24c", SCRIPT)
m24c = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m24c)


def test_clean_session_package_ingestion_and_partial_exclusion() -> None:
    ingestion = json.loads(INGESTION.read_text(encoding="utf-8"))
    assert ingestion["archive_filename"] == "m24b_s2_profile_refresh_results_m24b_s2_profile_refresh_clean_20260612_145358.tar.gz"
    assert ingestion["session_id"] == SESSION_ID
    assert ingestion["clean_session_used"] is True
    assert ingestion["partial_debug_session_excluded"] == PARTIAL_SESSION_ID
    assert ingestion["no_fabricated_data"] is True
    assert ingestion["gold_profile_overwritten"] is False


def test_clean_session_verified_30_trials_six_groups_five_repeats() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["session_id"] == SESSION_ID
    assert summary["trial_count"] == 30
    assert summary["executed_count"] == 30
    assert summary["skipped_count"] == 0
    assert summary["invalid_count"] == 0
    assert summary["velocity_group_count"] == 6
    assert set(summary["repeats_per_velocity"].values()) == {5}
    assert summary["validation"]["surface_values"] == ["S2_marble_floor"]
    assert summary["validation"]["condition_values"] == ["direct_refresh"]
    assert summary["validation"]["qc_overall_pass"] is True


def test_per_velocity_summary_generated() -> None:
    rows = _read_csv(PER_VELOCITY)
    assert len(rows) == 6
    assert {row["surface"] for row in rows} == {"S2_marble_floor"}
    assert {row["condition"] for row in rows} == {"direct_refresh"}
    assert {int(row["n"]) for row in rows} == {5}


def test_old_vs_new_comparison_and_m23c_consistency_generated() -> None:
    old_new = _read_csv(OLD_NEW)
    m23c = _read_csv(M23C_CHECK)
    assert len(old_new) == 6
    assert len(m23c) == 4
    assert sum(row["old_profile_available"] == "True" for row in old_new) == 5
    assert "old_velocity_unavailable" in {row["comparison_status"] for row in old_new}


def test_profile_status_decision_is_allowed() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["profile_status_decision"] in ALLOWED_DECISIONS
    assert summary["profile_status_decision"] == "inconclusive_environment_dependent"


def test_current_profile_candidate_exists_with_warnings() -> None:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    assert candidate["candidate_label"] == "k1_s2_current_profile_candidate_m24c"
    assert candidate["source_session_id"] == SESSION_ID
    assert candidate["source_trial_count"] == 30
    assert "not_gold_profile" in candidate["warnings"]
    assert "not_deployment_ready" in candidate["warnings"]
    assert "requires_review_before_adoption" in candidate["warnings"]
    assert "does_not_validate_compensation" in candidate["warnings"]
    assert "do_not_use_for_go1_g1" in candidate["warnings"]


def test_gold_profile_file_is_not_modified_by_analysis_rerun(tmp_path: Path) -> None:
    before = _sha256(GOLD_PROFILE)
    result = m24c.analyze(
        session_dir=SESSION_DIR,
        old_profile=GOLD_PROFILE,
        m23c_pairs=OUTPUT_DIR / "m23c_k1_before_after_pairs.csv",
        output_dir=tmp_path,
        archive=ROOT / "m24b_s2_profile_refresh_results_m24b_s2_profile_refresh_clean_20260612_145358.tar.gz",
        profile_mismatch_threshold=0.03,
        near_optimal_threshold=0.02,
        m23c_consistency_threshold=0.03,
    )
    after = _sha256(GOLD_PROFILE)
    assert before == after
    assert result["summary"]["gold_profile_overwritten"] is False


def test_report_claim_boundaries_and_go1_g1_blocked() -> None:
    text = REPORT.read_text(encoding="utf-8").lower()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "does not claim compensation improvement" in text
    assert "deployment readiness" in text
    assert "go1/g1 validation" in text
    assert summary["deployment_ready"] is False
    assert summary["go1_g1_validation"] is False


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
