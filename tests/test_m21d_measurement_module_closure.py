"""Tests for M21-D: Measurement Module Closure.

Tests cover:
- closure summary schema
- closure status flags
- closure artifact path existence
- validation CLI
- K1 contract row count still 72
- K1 contract validation still passes
- compensation_ready remains false
- GO1/G1 readiness remains false
- next phase set correctly
- no compensator module introduced
- no command remapping introduced
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CLOSURE_SUMMARY = ROOT / "outputs/measurement_v1/measurement_module_v1_closure_summary.json"
CLOSURE_REPORT = ROOT / "outputs/measurement_v1/measurement_module_v1_closure_report.md"
CLOSURE_DOC = ROOT / "docs/measurement_module_v1_closure.md"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"
MANIFEST_PATH = ROOT / "outputs/measurement_v1/booster_k1_reference_manifest.json"
CONTRACT_CSV = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv"
CONTRACT_VAL = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_validation.json"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"
STEP2_PLAN = ROOT / "docs/step2_velocity_compensation_research_plan.md"


# ---------------------------------------------------------------------------
# Closure summary schema tests
# ---------------------------------------------------------------------------

class TestClosureSummarySchema:
    def test_closure_summary_exists(self) -> None:
        assert CLOSURE_SUMMARY.exists(), f"Missing: {CLOSURE_SUMMARY}"

    def test_closure_summary_has_required_keys(self) -> None:
        data = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        required = [
            "closure_version", "closure_date", "closure_status",
            "status_flags", "milestone_lineage", "key_artifact_paths",
            "k1_contract_validation", "test_validation",
            "known_limitations", "next_step",
        ]
        for key in required:
            assert key in data, f"Missing key: {key}"

    def test_closure_summary_status_is_complete(self) -> None:
        data = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        assert data["closure_status"] == "complete"

    def test_closure_summary_has_all_milestones(self) -> None:
        data = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        lineage = data["milestone_lineage"]
        expected = {"M19C-E", "M20", "M21-A", "M21-B", "M21-C", "M21-D"}
        found = {m["milestone"] for m in lineage}
        assert found == expected, f"Missing milestones: {expected - found}"

    def test_closure_summary_k1_contract_72_rows(self) -> None:
        data = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        cv = data["k1_contract_validation"]
        assert cv["total_rows"] == 72
        assert cv["valid_rows"] == 72
        assert cv["validation_passed"] is True


# ---------------------------------------------------------------------------
# Closure status flags
# ---------------------------------------------------------------------------

class TestClosureStatusFlags:
    def test_status_module_v1_complete(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["measurement_module_v1_status"] == "complete"
        assert status["measurement_module_v1_complete"] is True

    def test_status_booster_k1_ready(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["booster_k1_reference_ready"] is True

    def test_status_contract_ready(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["measurement_contract_v1_ready"] is True

    def test_closure_summary_flags_consistent(self) -> None:
        closure = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        flags = closure["status_flags"]
        assert flags["measurement_module_v1_complete"] is True
        assert flags["booster_k1_measurement_reference_ready"] is True
        assert flags["measurement_contract_v1_ready"] is True
        assert flags["velocity_compensation_ready"] is False
        assert flags["unitree_go1_measurement_ready"] is False
        assert flags["unitree_g1_measurement_ready"] is False

    def test_closure_doc_flags_consistent(self) -> None:
        text = CLOSURE_DOC.read_text(encoding="utf-8")
        assert "measurement_module_v1_complete" in text
        assert "velocity_compensation_ready" in text
        assert "unitree_go1_measurement_ready" in text
        assert "true" in text
        assert "false" in text


# ---------------------------------------------------------------------------
# Closure artifact path existence
# ---------------------------------------------------------------------------

class TestClosureArtifactExistence:
    @pytest.mark.parametrize("artifact_path,label", [
        (CLOSURE_SUMMARY, "closure_summary"),
        (CLOSURE_REPORT, "closure_report"),
        (CLOSURE_DOC, "closure_documentation"),
        (STATUS_PATH, "module_status"),
        (MANIFEST_PATH, "k1_manifest"),
        (GOLD_PROFILE, "k1_gold_profile"),
        (CONTRACT_CSV, "k1_contract_csv"),
        (CONTRACT_VAL, "k1_contract_validation"),
        (STEP2_PLAN, "step2_plan"),
    ])
    def test_artifact_exists(self, artifact_path: Path, label: str) -> None:
        assert artifact_path.exists(), f"Missing {label}: {artifact_path}"


# ---------------------------------------------------------------------------
# Validation CLI tests
# ---------------------------------------------------------------------------

class TestClosureValidationCLI:
    def test_closure_cli_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_measurement_module_closure.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
        assert "PASSED" in result.stdout

    def test_closure_cli_json_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_measurement_module_closure.py", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        assert data["valid"] is True
        assert len(data["errors"]) == 0

    def test_closure_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_measurement_module_closure.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--json" in result.stdout


# ---------------------------------------------------------------------------
# K1 contract row count
# ---------------------------------------------------------------------------

class TestK1ContractRowCount:
    def test_contract_csv_has_72_rows(self) -> None:
        with CONTRACT_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 72, f"Expected 72 rows, got {len(rows)}"

    def test_contract_validation_passes(self) -> None:
        from calibration_core.measurement_contract import validate_measurement_csv
        result = validate_measurement_csv(CONTRACT_CSV)
        assert result["valid"] is True
        assert result["valid_rows"] == 72


# ---------------------------------------------------------------------------
# Compensation readiness remains false
# ---------------------------------------------------------------------------

class TestCompensationReadinessFalse:
    def test_status_compensation_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_manifest_compensation_false(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert manifest["velocity_compensation_ready"] is False

    def test_closure_summary_compensation_false(self) -> None:
        closure = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        assert closure["status_flags"]["velocity_compensation_ready"] is False

    def test_closure_report_states_compensation_not_ready(self) -> None:
        text = CLOSURE_REPORT.read_text(encoding="utf-8")
        assert "Why Compensation Is Not Ready Yet" in text


# ---------------------------------------------------------------------------
# GO1/G1 readiness remains false
# ---------------------------------------------------------------------------

class TestGO1G1ReadinessFalse:
    def test_status_go1_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False

    def test_status_g1_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_g1_measurement_ready"] is False

    def test_closure_summary_go1_g1_false(self) -> None:
        closure = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        assert closure["status_flags"]["unitree_go1_measurement_ready"] is False
        assert closure["status_flags"]["unitree_g1_measurement_ready"] is False

    def test_manifest_cross_platform_false(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert manifest["empirical_cross_platform_claim"] is False


# ---------------------------------------------------------------------------
# Next phase set correctly
# ---------------------------------------------------------------------------

class TestNextPhase:
    def test_status_next_phase_is_compensation_research(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert "velocity_compensation" in status["next_phase"].lower()

    def test_closure_summary_next_step_is_step2(self) -> None:
        closure = json.loads(CLOSURE_SUMMARY.read_text(encoding="utf-8"))
        assert "Step 2" in closure["next_step"]
        assert "velocity" in closure["next_step"].lower()
        assert "compensation" in closure["next_step"].lower()

    def test_step2_plan_exists(self) -> None:
        assert STEP2_PLAN.exists(), f"Missing Step 2 plan: {STEP2_PLAN}"

    def test_step2_plan_is_planning_only(self) -> None:
        text = STEP2_PLAN.read_text(encoding="utf-8")
        assert "Planning only" in text
        assert "No implementation has started" in text


# ---------------------------------------------------------------------------
# No compensator module introduced
# ---------------------------------------------------------------------------

class TestNoCompensatorModule:
    def test_no_compensator_py(self) -> None:
        assert not (ROOT / "calibration_core/compensator.py").exists(), \
            "compensator.py should not exist in Step 1"

    def test_no_inverse_response_model_py(self) -> None:
        assert not (ROOT / "calibration_core/inverse_response_model.py").exists(), \
            "inverse_response_model.py should not exist in Step 1"

    def test_no_command_remapping_module(self) -> None:
        assert not (ROOT / "calibration_core/command_remapping.py").exists(), \
            "command_remapping.py should not exist in Step 1"

    def test_no_compensation_in_scripts(self) -> None:
        scripts_dir = ROOT / "scripts"
        for py_file in scripts_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            text = py_file.read_text(encoding="utf-8")
            # Scripts may mention "compensation" in help text or descriptions
            # but should not implement compensation logic
            if "compensat" in text.lower():
                # Allow mention in docs/comments but not functional implementation
                assert "def compensate" not in text, \
                    f"Unexpected compensation function in {py_file.name}"


# ---------------------------------------------------------------------------
# Module status update verification
# ---------------------------------------------------------------------------

class TestModuleStatusUpdate:
    def test_status_changed_to_complete(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["measurement_module_v1_status"] == "complete"
        # Old value "consolidated_reference_ready" should be gone
        assert status["measurement_module_v1_status"] != "consolidated_reference_ready"

    def test_status_has_closure_artifacts(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert "closure_artifacts" in status
        ca = status["closure_artifacts"]
        assert "closure_summary" in ca
        assert "closure_report" in ca
        assert "step2_plan" in ca

    def test_show_measurement_module_status_cli_reflects_complete(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/show_measurement_module_status.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should show "complete" not "consolidated_reference_ready"
        assert "complete" in result.stdout.lower()
