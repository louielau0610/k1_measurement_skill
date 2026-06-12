"""Tests for M24-I: Controlled S2 Replication Analysis.

Tests verify: session ingested, 20 trials, 4 groups, 5 repeats, S2 only,
direct_refresh_controlled only, per-velocity summary, comparisons, valid
decision, candidate profile, gold profile not overwritten, claims absent.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
SESSION_DIR = ROOT / (
    "data/compensation_experiments/m24h_controlled_s2_replication/"
    "m24h_controlled_s2_replication_clean_20260612_171419"
)
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"

VALID_DECISIONS = [
    "response_reproducible_profile_adoption_planning_allowed",
    "response_environment_dependent_keep_identity_only",
    "extraction_or_protocol_issue_persists",
    "insufficient_data",
]


# ---------------------------------------------------------------------------
# Session verification
# ---------------------------------------------------------------------------

class TestSessionVerification:
    def test_session_exists(self) -> None:
        assert SESSION_DIR.is_dir()

    def test_trial_records_20(self) -> None:
        with (SESSION_DIR / "trial_records.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 20

    def test_all_executed(self) -> None:
        with (SESSION_DIR / "trial_records.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        executed = sum(1 for r in rows if r.get("physical_run_status") == "executed")
        assert executed == 20

    def test_four_velocity_groups(self) -> None:
        with (SESSION_DIR / "trial_records.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        vels = {r["command_velocity_mps"] for r in rows}
        assert vels == {"0.4", "0.45", "0.5", "0.55"}

    def test_s2_only(self) -> None:
        with (SESSION_DIR / "trial_records.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        surfaces = {r["surface"] for r in rows}
        assert surfaces == {"S2_marble_floor"}

    def test_direct_refresh_controlled_only(self) -> None:
        with (SESSION_DIR / "trial_records.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        conditions = {r["condition"] for r in rows}
        assert conditions == {"direct_refresh_controlled"}

    def test_extraction_exists(self) -> None:
        assert (SESSION_DIR / "corrected_extracted_results.csv").exists()

    def test_qc_passed(self) -> None:
        qc = json.loads((SESSION_DIR / "qc_summary.json").read_text())
        assert qc["overall_pass"] is True

    def test_metadata_exists(self) -> None:
        assert (SESSION_DIR / "controlled_metadata.json").exists()


# ---------------------------------------------------------------------------
# Analysis outputs
# ---------------------------------------------------------------------------

class TestAnalysisOutputs:
    def test_ingestion_summary_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_ingestion_summary.json").exists()

    def test_per_velocity_summary_exists(self) -> None:
        path = OUTPUT_DIR / "m24i_controlled_s2_per_velocity_summary.csv"
        assert path.exists()
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 4

    def test_m24f_comparison_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_m24f_replication_comparison.csv").exists()

    def test_m19c_comparison_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_old_m19c_comparison.csv").exists()

    def test_m23c_comparison_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_m23c_direct_comparison.csv").exists()

    def test_decision_json_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").exists()

    def test_decision_valid(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["decision"] in VALID_DECISIONS

    def test_profile_candidate_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_controlled_s2_profile_candidate.json").exists()

    def test_report_exists(self) -> None:
        assert (OUTPUT_DIR / "m24i_controlled_s2_replication_report.md").exists()


# ---------------------------------------------------------------------------
# Candidate profile validation
# ---------------------------------------------------------------------------

class TestCandidateProfile:
    def test_candidate_has_warnings(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_profile_candidate.json").read_text())
        warnings = data["warnings"]
        assert "candidate_only" in warnings
        assert "not_gold_profile" in warnings
        assert "not_deployment_ready" in warnings
        assert "do_not_use_for_go1_g1" in warnings

    def test_candidate_status_is_candidate_only(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_profile_candidate.json").read_text())
        assert data["status"] == "candidate_only"


# ---------------------------------------------------------------------------
# Gold profile boundary
# ---------------------------------------------------------------------------

class TestGoldProfileBoundary:
    def test_gold_profile_still_exists(self) -> None:
        assert GOLD_PROFILE.exists()

    def test_decision_says_gold_not_overwritten(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["gold_profile_overwritten"] is False

    def test_decision_says_candidate_not_adopted(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["candidate_profile_adopted"] is False


# ---------------------------------------------------------------------------
# Boundary flags
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_deployment_ready_false(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["deployment_ready"] is False

    def test_go1_g1_blocked(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["go1_g1_blocked"] is True

    def test_compensation_not_validated(self) -> None:
        data = json.loads((OUTPUT_DIR / "m24i_controlled_s2_replication_summary.json").read_text())
        assert data["compensation_validated"] is False

    def test_status_go1_g1_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_no_compensation_improvement_claim(self) -> None:
        text = (OUTPUT_DIR / "m24i_controlled_s2_replication_report.md").read_text(encoding="utf-8")
        assert "compensation improves" not in text.lower()
        assert "compensation improved" not in text.lower()

    def test_docs_exist(self) -> None:
        assert (ROOT / "docs/m24i_controlled_s2_replication_analysis.md").exists()
        assert (ROOT / "docs/m24i_profile_adoption_readiness_boundary.md").exists()
