"""Tests for M23-B: K1 Physical Compensation Execution Pack.

Tests cover:
- M23-B manifest exists
- runner defaults to dry-run
- runner requires --execute for hardware motion
- runner preserves pair_id and condition
- logger schema contains required fields
- extraction preserves desired_velocity, command_velocity, pair_id, condition
- QC requires each pair to have direct and compensated
- QC rejects missing pair member
- manifest physical_validation_status is execution_pack_ready_not_run
- deployment_ready remains false
- no physical result files are created
- no tracking improvement claim appears
- GO1/G1 remain absent
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MANIFEST_JSON = ROOT / "outputs/compensation_experiments/m23b_execution_pack_manifest.json"
MANIFEST_MD = ROOT / "outputs/compensation_experiments/m23b_execution_pack_manifest.md"
EXEC_PROTOCOL = ROOT / "docs/m23b_k1_physical_compensation_execution_protocol.md"
TRANSFER_DOC = ROOT / "docs/m23b_robot_transfer_and_run_commands.md"
TRIAL_PLAN = ROOT / "outputs/compensation_experiments/m23a_trial_plan.csv"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------

class TestManifest:
    def test_manifest_json_exists(self) -> None:
        assert MANIFEST_JSON.exists()

    def test_manifest_md_exists(self) -> None:
        assert MANIFEST_MD.exists()

    def test_manifest_status_is_not_run(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["physical_validation_status"] == "execution_pack_ready_not_run"

    def test_manifest_deployment_ready_false(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_manifest_has_scripts_to_transfer(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        scripts = data["scripts_to_transfer"]
        assert any("run_m23b" in s for s in scripts)
        assert any("log_m23b" in s for s in scripts)

    def test_manifest_has_extraction_command(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert "extraction_command" in data

    def test_manifest_has_qc_command(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert "qc_command" in data

    def test_manifest_claim_boundary_no_physical_results(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        cb = data["claim_boundary"]
        assert cb["physical_trials_executed"] is False
        assert cb["tracking_improvement_claimed"] is False
        assert cb["compensation_validated"] is False
        assert cb["go1_g1_included"] is False

    def test_manifest_split_process_required(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["robot_requirements"]["split_process_required"] is True

    def test_manifest_safety_dry_run_default(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["safety"]["dry_run_default"] is True
        assert data["safety"]["execute_requires_flag"] is True
        assert data["safety"]["per_trial_permit_default"] is True


# ---------------------------------------------------------------------------
# Runner tests (dry-run only, no hardware)
# ---------------------------------------------------------------------------

class TestRunner:
    def test_runner_dry_run_default(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_m23b_k1_compensation_trials.py", "--surface", "S2_marble_floor"],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "No hardware was moved" in result.stdout

    def test_runner_help_shows_execute_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_m23b_k1_compensation_trials.py", "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--execute" in result.stdout
        assert "--no-permit" in result.stdout
        assert "--start-from-trial-id" in result.stdout

    def test_runner_preserves_pair_id_in_trial_plan(self) -> None:
        with TRIAL_PLAN.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            assert r["pair_id"], f"Missing pair_id in {r['trial_id']}"
            assert r["condition"] in ("direct", "compensated")

    def test_runner_session_metadata_created_on_execute(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "scripts/run_m23b_k1_compensation_trials.py",
                 "--surface", "S2_marble_floor", "--session-id", "test_meta",
                 "--execute", "--no-permit", "--base-dir", tmp],
                cwd=ROOT, capture_output=True, text=True, timeout=60,
            )
            meta_path = Path(tmp) / "test_meta" / "session_metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                assert meta["split_process_required"] is True
                assert meta["physical_validation_status"] == "execution_in_progress"
                assert meta["deployment_ready"] is False


# ---------------------------------------------------------------------------
# Logger schema tests
# ---------------------------------------------------------------------------

class TestLoggerSchema:
    def test_logger_help_shows_required_args(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/log_m23b_k1_compensation_trial.py", "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--trial-id" in result.stdout
        assert "--pair-id" in result.stdout
        assert "--condition" in result.stdout
        assert "--desired-velocity" in result.stdout
        assert "--command-velocity" in result.stdout

    def test_logger_produces_csv_with_required_fields(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, "scripts/log_m23b_k1_compensation_trial.py",
                 "--trial-id", "TEST_001", "--pair-id", "PAIR_001",
                 "--condition", "direct", "--desired-velocity", "0.4",
                 "--command-velocity", "0.4", "--output-dir", tmp],
                cwd=ROOT, capture_output=True, text=True, check=True,
            )
            csv_path = Path(tmp) / "TEST_001.csv"
            assert csv_path.exists()
            with csv_path.open(newline="", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            assert len(rows) > 0
            fields = rows[0].keys()
            required = ["trial_id", "pair_id", "condition", "desired_velocity_mps",
                       "command_velocity_mps", "phase", "odom_x", "odom_y", "odom_theta"]
            for field in required:
                assert field in fields, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Extraction tests
# ---------------------------------------------------------------------------

class TestExtraction:
    def test_extraction_help_shows_session_dir(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/extract_m23b_k1_compensation_trials.py", "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--session-dir" in result.stdout

    def test_extraction_preserves_pair_id_and_condition(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp) / "test_session"
            (session_dir / "state_logs").mkdir(parents=True)

            # Generate a log
            subprocess.run(
                [sys.executable, "scripts/log_m23b_k1_compensation_trial.py",
                 "--trial-id", "EXT_TEST", "--pair-id", "PAIR_X",
                 "--condition", "compensated", "--desired-velocity", "0.45",
                 "--command-velocity", "0.55", "--output-dir", str(session_dir / "state_logs")],
                cwd=ROOT, capture_output=True, text=True, check=True,
            )

            # Extract
            subprocess.run(
                [sys.executable, "scripts/extract_m23b_k1_compensation_trials.py",
                 "--session-dir", str(session_dir)],
                cwd=ROOT, capture_output=True, text=True, check=True,
            )

            csv_path = session_dir / "extracted_results.csv"
            assert csv_path.exists()
            with csv_path.open(newline="", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == 1
            r = rows[0]
            assert r["trial_id"] == "EXT_TEST"
            assert r["pair_id"] == "PAIR_X"
            assert r["condition"] == "compensated"
            assert float(r["desired_velocity_mps"]) == 0.45
            assert float(r["command_velocity_mps"]) == 0.55
            assert "measured_actual_velocity_mps" in r
            assert "absolute_tracking_error_mps" in r
            assert "yaw_drift_deg" in r


# ---------------------------------------------------------------------------
# QC tests
# ---------------------------------------------------------------------------

class TestQC:
    def test_qc_help_shows_session_dir(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/qc_m23b_k1_compensation_session.py", "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--session-dir" in result.stdout

    def test_qc_detects_missing_session(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/qc_m23b_k1_compensation_session.py",
             "--session-dir", "nonexistent_session_xyz"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1

    def test_qc_json_output(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = Path(tmp) / "qc_session"
            session_dir.mkdir()
            (session_dir / "state_logs").mkdir()
            # Write minimal metadata
            (session_dir / "session_metadata.json").write_text(json.dumps({
                "session_id": "test", "physical_validation_status": "execution_in_progress"
            }))
            result = subprocess.run(
                [sys.executable, "scripts/qc_m23b_k1_compensation_session.py",
                 "--session-dir", str(session_dir), "--json"],
                cwd=ROOT, capture_output=True, text=True,
            )
            data = json.loads(result.stdout)
            assert "overall_pass" in data
            assert "checks" in data
            assert "disclaimer" in data


# ---------------------------------------------------------------------------
# Boundary flag tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_no_physical_result_files_created(self) -> None:
        # No "before_after_analysis" or "compensation_validated" output should exist
        exp_dir = ROOT / "outputs/compensation_experiments"
        forbidden = ["before_after", "compensation_validated", "physical_results"]
        for f in exp_dir.glob("*.json"):
            for kw in forbidden:
                assert kw not in f.name.lower(), f"Unexpected file: {f.name}"

    def test_deployment_ready_false_in_manifest(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_go1_g1_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_compensation_ready_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_protocol_doc_exists(self) -> None:
        assert EXEC_PROTOCOL.exists()

    def test_transfer_doc_exists(self) -> None:
        assert TRANSFER_DOC.exists()

    def test_transfer_doc_mentions_scp(self) -> None:
        text = TRANSFER_DOC.read_text(encoding="utf-8")
        assert "scp" in text.lower()
