"""Tests for M23-D negative-result diagnosis and revision plan."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
DIAGNOSIS_DOC = ROOT / "docs/m23d_negative_result_diagnosis.md"
REQUIREMENTS_DOC = ROOT / "docs/revised_velocity_compensator_requirements.md"
PAPER_DOC = ROOT / "docs/m23d_paper_interpretation_after_negative_result.md"
PLAN_DOC = ROOT / "docs/m23d_revised_k1_validation_plan_outline.md"
DIAGNOSIS_SUMMARY = OUTPUT_DIR / "m23d_negative_result_diagnosis_summary.json"
FAILURE_TABLE = OUTPUT_DIR / "m23d_failure_mode_table.csv"
FAILURE_SUMMARY = OUTPUT_DIR / "m23d_failure_mode_summary.json"
FAILURE_REPORT = OUTPUT_DIR / "m23d_failure_mode_report.md"


def test_diagnosis_summary_exists() -> None:
    assert DIAGNOSIS_SUMMARY.exists()
    data = json.loads(DIAGNOSIS_SUMMARY.read_text(encoding="utf-8"))
    assert data["claim_level"] == "negative_result_requires_compensator_revision"


def test_diagnosis_summary_revision_required_and_not_deployment_ready() -> None:
    data = json.loads(DIAGNOSIS_SUMMARY.read_text(encoding="utf-8"))
    assert data["revision_required"] is True
    assert data["deployment_ready"] is False
    assert data["hardware_execution"] is False


def test_failure_mode_table_exists_and_has_identity_preferred() -> None:
    assert FAILURE_TABLE.exists()
    with FAILURE_TABLE.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    assert all(row["identity_preferred"] == "True" for row in rows)
    assert all("revision_required" in row["failure_mode_labels"] for row in rows)


def test_failure_mode_summary_labels_main_reason() -> None:
    data = json.loads(FAILURE_SUMMARY.read_text(encoding="utf-8"))
    assert data["direct_outperforms_compensated_pairs"] == 12
    assert data["compensated_command_lower_than_direct_pairs"] == 12
    assert "identity_preferred" in data["failure_mode_labels"]
    assert "Direct commands were already near optimal" in data["main_reason"]
    assert FAILURE_REPORT.exists()


def test_revised_requirements_include_required_guards() -> None:
    text = REQUIREMENTS_DOC.read_text(encoding="utf-8")
    assert "Identity Fallback" in text
    assert "Benefit Gate" in text
    assert "Correction Magnitude Limit" in text
    assert "max_correction_mps = 0.05" in text
    assert "profile_mismatch_suspected" in text


def test_paper_interpretation_does_not_claim_improvement() -> None:
    text = PAPER_DOC.read_text(encoding="utf-8").lower()
    assert "should not claim tracking improvement yet" in text
    assert "does not improve" not in text  # avoid universal claim beyond M23-C context
    assert "deployment readiness" in text


def test_go1_g1_validation_remains_future_work() -> None:
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "GO1/G1 work remains blocked" in status
    assert "deployment readiness remains false" in status.lower()
    assert "GO1/G1 validation" in PAPER_DOC.read_text(encoding="utf-8")


def test_no_hardware_execution_and_no_revised_implementation() -> None:
    summary = json.loads(FAILURE_SUMMARY.read_text(encoding="utf-8"))
    assert summary["hardware_execution"] is False
    assert summary["revised_compensator_implemented"] is False
    forbidden_paths = [
        ROOT / "calibration_core/revised_velocity_compensator.py",
        ROOT / "scripts/run_revised_velocity_compensator.py",
        ROOT / "scripts/run_m23e_k1_revised_compensation_trials.py",
    ]
    assert not any(path.exists() for path in forbidden_paths)


def test_plan_outline_requires_future_validation_not_execution() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    assert "does not run hardware" in text
    assert "M23-E or M24" in text
    assert "No GO1/G1 work" in text
