"""Tests for M24-D response consistency audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
SUMMARY = OUTPUT_DIR / "m24d_response_consistency_summary.json"
REPORT = OUTPUT_DIR / "m24d_response_consistency_report.md"
DISAGREEMENT = OUTPUT_DIR / "m24d_pairwise_profile_disagreement.csv"
ASSUMPTION_CSV = OUTPUT_DIR / "m24d_measurement_assumption_audit.csv"
ASSUMPTION_MD = OUTPUT_DIR / "m24d_measurement_assumption_audit.md"
DIAGNOSIS = OUTPUT_DIR / "m24d_response_consistency_diagnosis.json"
ADOPTION = OUTPUT_DIR / "m24d_profile_adoption_decision.json"
CONTROLLED_PLAN = ROOT / "docs/m24d_controlled_s2_replication_plan.md"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"

ALLOWED_DECISIONS = {
    "do_not_adopt_candidate_profile_yet",
    "adopt_candidate_profile_as_versioned_experimental_profile",
    "refresh_profile_again_under_controlled_conditions",
    "investigate_extraction_before_profile_decision",
}


def test_m24d_summary_exists() -> None:
    assert SUMMARY.exists()
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["audit_id"] == "m24d_response_consistency_audit"
    assert data["overlapping_velocity_set"] == [0.4, 0.45, 0.5]


def test_pairwise_disagreement_csv_exists() -> None:
    rows = _read_csv(DISAGREEMENT)
    assert len(rows) == 3
    assert {row["m23c_closer_to"] for row in rows} == {"M19C"}
    assert all("m23c_direct_response_not_reproduced" in row["disagreement_labels"] for row in rows)


def test_measurement_assumption_audit_exists() -> None:
    assert ASSUMPTION_CSV.exists()
    assert ASSUMPTION_MD.exists()
    rows = _read_csv(ASSUMPTION_CSV)
    assumptions = {row["assumption"] for row in rows}
    assert "extraction_method" in assumptions
    assert "battery_warmup_environment_recorded" in assumptions


def test_profile_adoption_decision_is_allowed_and_candidate_not_adopted() -> None:
    data = json.loads(ADOPTION.read_text(encoding="utf-8"))
    assert data["profile_adoption_decision"] in ALLOWED_DECISIONS
    assert data["profile_adoption_decision"] == "investigate_extraction_before_profile_decision"
    assert data["candidate_profile_adopted"] is False
    assert data["second_compensation_validation_blocked"] is True


def test_gold_profile_not_overwritten() -> None:
    before = _sha256(GOLD_PROFILE)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    adoption = json.loads(ADOPTION.read_text(encoding="utf-8"))
    after = _sha256(GOLD_PROFILE)
    assert before == after
    assert summary["gold_profile_overwritten"] is False
    assert adoption["gold_profile_overwritten"] is False


def test_report_boundaries_no_improvement_no_deployment_go1_blocked() -> None:
    text = REPORT.read_text(encoding="utf-8").lower()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "does not claim compensation improvement" in text
    assert "deployment readiness" in text
    assert "go1/g1 validation" in text
    assert summary["deployment_ready"] is False
    assert summary["go1_g1_blocked"] is True


def test_controlled_replication_plan_exists_and_no_hardware_execution() -> None:
    assert CONTROLLED_PLAN.exists()
    text = CONTROLLED_PLAN.read_text(encoding="utf-8")
    assert "direct_refresh" in text
    assert "No compensated commands" in text
    assert "does not validate revised compensation" in text
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "no hardware execution" in summary["claim_boundary"]


def test_diagnosis_labels_present() -> None:
    diagnosis = json.loads(DIAGNOSIS.read_text(encoding="utf-8"))
    labels = set(diagnosis["diagnosis_labels"])
    assert "candidate_profile_not_adoption_ready" in labels
    assert "controlled_replication_required" in labels
    assert "extraction_method_audit_required" in labels


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
