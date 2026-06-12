"""Tests for M23-F revised offline audit and readiness recommendation."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"

AUDIT_SUMMARY = OUTPUT_DIR / "m23f_revised_offline_audit_summary.json"
AUDIT_REPORT = OUTPUT_DIR / "m23f_revised_offline_audit_report.md"
AUDIT_TABLE = OUTPUT_DIR / "m23f_decision_audit_table.csv"
RECOMMENDATION_JSON = OUTPUT_DIR / "m23f_second_validation_recommendation.json"
RECOMMENDATION_MD = OUTPUT_DIR / "m23f_second_validation_recommendation.md"
AUDIT_DOC = ROOT / "docs/m23f_revised_offline_audit.md"
READINESS_DOC = ROOT / "docs/m23f_second_k1_validation_readiness.md"

VALID_READINESS = {
    "not_ready_revise_more",
    "ready_for_identity_fallback_validation",
    "ready_for_selected_compensation_validation",
    "ready_for_profile_refresh_before_validation",
}


def test_audit_summary_exists() -> None:
    assert AUDIT_SUMMARY.exists()
    data = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    assert data["decision_count"] == 4


def test_harmful_command_avoidance_identity_and_profile_counts_present() -> None:
    data = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    assert data["harmful_command_avoided_count"] == 4
    assert data["identity_fallback_count"] == 4
    assert data["profile_mismatch_suspected_count"] == 4


def test_readiness_category_is_valid() -> None:
    data = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    assert data["readiness_category"] in VALID_READINESS
    assert data["readiness_category"] == "ready_for_profile_refresh_before_validation"


def test_second_validation_recommendation_exists() -> None:
    assert RECOMMENDATION_JSON.exists()
    assert RECOMMENDATION_MD.exists()
    rec = json.loads(RECOMMENDATION_JSON.read_text(encoding="utf-8"))
    assert rec["refresh_s2_profile_before_compensation_experiment"] is True
    assert rec["validate_identity_non_worsening"] is True
    assert rec["deadzone_low_speed_targets"] == "remain_excluded"


def test_decision_audit_table_exists() -> None:
    assert AUDIT_TABLE.exists()
    with AUDIT_TABLE.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    assert all(row["harmful_command_avoided"] == "True" for row in rows)
    assert all(row["identity_fallback"] == "True" for row in rows)


def test_report_does_not_claim_physical_improvement() -> None:
    text = AUDIT_REPORT.read_text(encoding="utf-8").lower()
    assert "no hardware was executed" in text
    assert "does not prove physical improvement" in text
    assert "deployment ready: false" in text
    assert "physical improvement claimed" not in text


def test_deployment_ready_false_and_no_hardware_execution() -> None:
    data = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    assert data["deployment_ready"] is False
    assert data["hardware_execution"] is False
    rec = json.loads(RECOMMENDATION_JSON.read_text(encoding="utf-8"))
    assert rec["deployment_ready"] is False
    assert rec["physical_validation_status"] == "not_started"


def test_go1_g1_remain_blocked() -> None:
    data = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    rec = json.loads(RECOMMENDATION_JSON.read_text(encoding="utf-8"))
    assert data["go1_g1_blocked"] is True
    assert rec["go1_g1_blocked"] is True
    assert "GO1/G1 remain blocked" in AUDIT_DOC.read_text(encoding="utf-8")
    assert "validate GO1/G1" in READINESS_DOC.read_text(encoding="utf-8")


def test_no_hardware_runner_created() -> None:
    forbidden = [
        ROOT / "scripts/run_m23f_k1_validation.py",
        ROOT / "scripts/run_m23f_k1_physical_validation.py",
        ROOT / "scripts/run_m23f_go1_validation.py",
        ROOT / "scripts/run_m23f_g1_validation.py",
    ]
    assert not any(path.exists() for path in forbidden)
