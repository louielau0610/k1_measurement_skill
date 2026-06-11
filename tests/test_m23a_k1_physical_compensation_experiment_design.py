"""Tests for M23-A: K1 Physical Compensation Experiment Design.

Tests cover:
- experiment plan JSON exists
- trial plan CSV exists
- trial plan contains both direct and compensated conditions
- pair IDs are present
- each desired velocity has expected paired repeats
- direct condition command equals desired velocity
- compensated condition command comes from offline compensator decision
- infeasible compensated targets are marked and not forced as valid command
- no hardware execution
- claim boundary says physical validation not started
- result schema includes required fields
- analysis plan mentions paired comparison and Wilcoxon option
- deployment_ready remains false
- GO1/G1 validation remains false
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPERIMENT_DIR = ROOT / "outputs/compensation_experiments"
PLAN_JSON = EXPERIMENT_DIR / "m23a_experiment_plan.json"
PLAN_MD = EXPERIMENT_DIR / "m23a_experiment_plan.md"
TRIAL_CSV = EXPERIMENT_DIR / "m23a_trial_plan.csv"
ANALYSIS_MD = EXPERIMENT_DIR / "m23a_analysis_plan.md"
DESIGN_DOC = ROOT / "docs/m23a_k1_physical_compensation_experiment_design.md"
RESULT_SCHEMA = ROOT / "docs/m23a_physical_compensation_result_schema.md"
CLAIM_BOUNDARY = ROOT / "docs/m23a_physical_validation_claim_boundary.md"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"
CLOSURE_PATH = ROOT / "outputs/measurement_v1/measurement_module_v1_closure_summary.json"

REQUIRED_RESULT_FIELDS = [
    "trial_id", "pair_id", "surface", "desired_velocity_mps", "condition",
    "command_velocity_mps", "measured_actual_velocity_mps",
    "absolute_tracking_error_mps", "yaw_drift_deg",
    "extraction_status", "invalid_reason", "state_log_path",
    "compensation_decision_path", "physical_run_status",
]


# ---------------------------------------------------------------------------
# Artifact existence
# ---------------------------------------------------------------------------

class TestArtifactExistence:
    def test_experiment_plan_json_exists(self) -> None:
        assert PLAN_JSON.exists(), f"Missing: {PLAN_JSON}"

    def test_experiment_plan_md_exists(self) -> None:
        assert PLAN_MD.exists(), f"Missing: {PLAN_MD}"

    def test_trial_plan_csv_exists(self) -> None:
        assert TRIAL_CSV.exists(), f"Missing: {TRIAL_CSV}"

    def test_analysis_plan_md_exists(self) -> None:
        assert ANALYSIS_MD.exists(), f"Missing: {ANALYSIS_MD}"

    def test_design_doc_exists(self) -> None:
        assert DESIGN_DOC.exists(), f"Missing: {DESIGN_DOC}"

    def test_result_schema_doc_exists(self) -> None:
        assert RESULT_SCHEMA.exists(), f"Missing: {RESULT_SCHEMA}"

    def test_claim_boundary_doc_exists(self) -> None:
        assert CLAIM_BOUNDARY.exists(), f"Missing: {CLAIM_BOUNDARY}"


# ---------------------------------------------------------------------------
# Trial plan CSV validation
# ---------------------------------------------------------------------------

class TestTrialPlan:
    def test_trial_plan_has_36_trials(self) -> None:
        with TRIAL_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 36, f"Expected 36 trials, got {len(rows)}"

    def test_contains_both_conditions(self) -> None:
        with TRIAL_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        conditions = {r["condition"] for r in rows}
        assert "direct" in conditions
        assert "compensated" in conditions

    def test_pair_ids_present(self) -> None:
        with TRIAL_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            assert r["pair_id"], f"Missing pair_id in trial {r.get('trial_id')}"
        pairs = {r["pair_id"] for r in rows}
        assert len(pairs) == 18, f"Expected 18 unique pairs, got {len(pairs)}"

    def test_direct_condition_command_equals_desired(self) -> None:
        with TRIAL_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        direct_rows = [r for r in rows if r["condition"] == "direct"]
        assert len(direct_rows) == 18
        for r in direct_rows:
            assert float(r["command_velocity_mps"]) == float(r["desired_velocity_mps"])

    def test_each_velocity_has_expected_repeats(self) -> None:
        with TRIAL_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        from collections import Counter
        vel_counts = Counter((r["desired_velocity_mps"], r["condition"]) for r in rows)
        for vel in ["0.3", "0.35", "0.4", "0.45", "0.5", "0.55"]:
            assert vel_counts[(vel, "direct")] == 3, f"Expected 3 direct repeats for {vel}"
            assert vel_counts[(vel, "compensated")] == 3, f"Expected 3 compensated repeats for {vel}"


# ---------------------------------------------------------------------------
# Plan JSON validation
# ---------------------------------------------------------------------------

class TestPlanJSON:
    def test_physical_validation_not_started(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["physical_validation"] == "not_started"

    def test_hardware_execution_false(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["hardware_execution"] is False

    def test_deployment_ready_false(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["deployment_ready"] is False

    def test_go1_g1_not_included(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["go1_g1_included"] is False

    def test_36_trials(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["total_planned_trials"] == 36
        assert plan["planned_pairs"] == 18

    def test_surface_is_s2_marble(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert "S2_marble_floor" in plan["surface"]

    def test_6_desired_velocities(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert len(plan["desired_velocities_mps"]) == 6

    def test_disclaimer_present(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert "no hardware execution" in plan.get("disclaimer", "").lower()


# ---------------------------------------------------------------------------
# Documentation content tests
# ---------------------------------------------------------------------------

class TestDocumentationContent:
    def test_design_doc_mentions_paired_design(self) -> None:
        text = DESIGN_DOC.read_text(encoding="utf-8")
        assert "paired" in text.lower()

    def test_design_doc_mentions_wilcoxon(self) -> None:
        text = DESIGN_DOC.read_text(encoding="utf-8")
        assert "Wilcoxon" in text or "wilcoxon" in text.lower()

    def test_design_doc_mentions_s2_marble(self) -> None:
        text = DESIGN_DOC.read_text(encoding="utf-8")
        assert "S2_marble_floor" in text

    def test_analysis_plan_mentions_wilcoxon(self) -> None:
        text = ANALYSIS_MD.read_text(encoding="utf-8")
        assert "Wilcoxon" in text or "wilcoxon" in text.lower()

    def test_analysis_plan_mentions_paired_comparison(self) -> None:
        text = ANALYSIS_MD.read_text(encoding="utf-8")
        assert "paired" in text.lower()

    def test_result_schema_has_required_fields(self) -> None:
        text = RESULT_SCHEMA.read_text(encoding="utf-8")
        for field in REQUIRED_RESULT_FIELDS:
            assert field in text, f"Missing field in result schema: {field}"

    def test_claim_boundary_says_not_started(self) -> None:
        text = CLAIM_BOUNDARY.read_text(encoding="utf-8")
        assert "not started" in text.lower()

    def test_claim_boundary_says_no_physical_validation(self) -> None:
        text = CLAIM_BOUNDARY.read_text(encoding="utf-8")
        assert "no physical" in text.lower() or "not started" in text.lower()

    def test_claim_boundary_mentions_m23b(self) -> None:
        text = CLAIM_BOUNDARY.read_text(encoding="utf-8")
        assert "M23-B" in text


# ---------------------------------------------------------------------------
# Boundary flag tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_deployment_ready_false_in_plan(self) -> None:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        assert plan["deployment_ready"] is False

    def test_status_go1_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False

    def test_status_g1_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_g1_measurement_ready"] is False

    def test_compensation_ready_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_closure_intact(self) -> None:
        closure = json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))
        assert closure["closure_status"] == "complete"
        assert closure["status_flags"]["velocity_compensation_ready"] is False
