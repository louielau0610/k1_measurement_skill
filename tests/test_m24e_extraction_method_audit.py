"""Tests for M24-E: Extraction Method Audit and Raw Log Reanalysis.

Tests cover:
- audit script runs on session logs
- reextracted trial metrics output exists
- extraction method comparison output exists
- M24-C crosscheck output exists
- anomaly summary exists
- extraction audit decision is valid
- gold profile not overwritten
- candidate profile not adopted
- report does not claim compensation improvement
- deployment_ready=false
- GO1/G1 blocked
- no hardware execution
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AUDIT_SCRIPT = ROOT / "scripts/audit_m24e_extraction_method.py"
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"

REQUIRED_OUTPUTS = [
    "m24e_reextracted_trial_metrics.csv",
    "m24e_extraction_method_comparison.csv",
    "m24e_m24c_crosscheck.csv",
    "m24e_extraction_anomaly_summary.json",
    "m24e_extraction_anomaly_report.md",
    "m24e_extraction_audit_decision.json",
    "m24e_extraction_audit_decision.md",
    "m24e_m24c_crosscheck.md",
]

VALID_DECISIONS = [
    "m24c_extraction_confirmed_discrepancy_physical_or_environmental",
    "m24c_extraction_likely_faulty_reextract_required",
    "m24c_extraction_inconclusive_need_manual_log_review",
    "analysis_invalid_missing_raw_logs",
]

STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


# ---------------------------------------------------------------------------
# Audit script tests
# ---------------------------------------------------------------------------

class TestAuditScript:
    def test_script_exists(self) -> None:
        assert AUDIT_SCRIPT.exists(), f"Missing: {AUDIT_SCRIPT}"

    def test_script_runs_on_session(self, tmp_path: Path) -> None:
        """Audit should run successfully on the M24-B session."""
        result = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--output-dir", str(tmp_path)],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, f"Audit failed: {result.stderr}"

    def test_script_help(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--session-dir" in result.stdout
        assert "--output-dir" in result.stdout


# ---------------------------------------------------------------------------
# Output existence
# ---------------------------------------------------------------------------

class TestOutputExistence:
    def test_all_outputs_exist(self) -> None:
        for fname in REQUIRED_OUTPUTS:
            path = OUTPUT_DIR / fname
            assert path.exists(), f"Missing output: {fname}"

    def test_reextracted_metrics_not_empty(self) -> None:
        path = OUTPUT_DIR / "m24e_reextracted_trial_metrics.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 0, "Re-extracted metrics should not be empty"
        # Should have 30 trials × 5 methods = 150 rows
        assert len(rows) >= 30, f"Expected >= 30 rows, got {len(rows)}"

    def test_extraction_method_comparison_not_empty(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_method_comparison.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 4, "Should have comparison rows for multiple velocities"

    def test_crosscheck_not_empty(self) -> None:
        path = OUTPUT_DIR / "m24e_m24c_crosscheck.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) >= 20, f"Crosscheck should have many rows, got {len(rows)}"


# ---------------------------------------------------------------------------
# Audit decision tests
# ---------------------------------------------------------------------------

class TestAuditDecision:
    def test_decision_json_exists_and_valid(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["decision"] in VALID_DECISIONS, f"Invalid decision: {data['decision']}"
        assert "reason" in data

    def test_gold_profile_not_overwritten(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["gold_profile_overwritten"] is False

    def test_candidate_profile_not_adopted(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["candidate_profile_adopted"] is False

    def test_deployment_ready_false(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_go1_g1_blocked(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["go1_g1_blocked"] is True

    def test_decision_is_reextract_required(self) -> None:
        """Based on the observed 0/30 reproduction rate, decision should indicate extraction fault."""
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "reextract" in data["decision"] or "faulty" in data["decision"] or \
               "inconclusive" in data["decision"] or "missing_raw_logs" in data["decision"], \
            f"Unexpected decision: {data['decision']}"


# ---------------------------------------------------------------------------
# Anomaly summary tests
# ---------------------------------------------------------------------------

class TestAnomalySummary:
    def test_anomaly_summary_has_labels(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_anomaly_summary.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "labels_assigned" in data
        assert len(data["labels_assigned"]) > 0

    def test_anomaly_summary_reports_trial_count(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_anomaly_summary.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["total_trials_audited"] >= 30


# ---------------------------------------------------------------------------
# Cross-check tests
# ---------------------------------------------------------------------------

class TestCrossCheck:
    def test_crosscheck_reproduced_field_exists(self) -> None:
        path = OUTPUT_DIR / "m24e_m24c_crosscheck.csv"
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            assert "reproduced" in r, "Crosscheck must have 'reproduced' field"


# ---------------------------------------------------------------------------
# Boundary flag tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_no_compensation_improvement_claim(self) -> None:
        """Audit outputs must not claim compensation improvement."""
        for fname in ["m24e_extraction_audit_decision.md", "m24e_extraction_anomaly_report.md"]:
            path = OUTPUT_DIR / fname
            if path.exists():
                text = path.read_text(encoding="utf-8")
                assert "compensation improves" not in text.lower()
                assert "compensation improved" not in text.lower()

    def test_no_deployment_readiness_claim(self) -> None:
        path = OUTPUT_DIR / "m24e_extraction_audit_decision.md"
        text = path.read_text(encoding="utf-8")
        assert "deployment ready: **True**" not in text

    def test_no_go1_g1_validation(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_compensation_ready_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_documentation_exists(self) -> None:
        assert (ROOT / "docs/m24e_extraction_method_audit.md").exists()
        assert (ROOT / "docs/m24e_raw_log_reanalysis_boundary.md").exists()

    def test_doc_mentions_extraction_fault(self) -> None:
        text = (ROOT / "docs/m24e_extraction_method_audit.md").read_text(encoding="utf-8")
        assert "extraction" in text.lower()
        assert "fault" in text.lower() or "reproduced" in text.lower()
