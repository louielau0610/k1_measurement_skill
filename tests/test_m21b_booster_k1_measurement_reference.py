"""Tests for M21-B: Booster K1 Measurement Reference Implementation Hardening.

Tests cover:
- K1 session metadata builder
- Session directory layout generation
- Trial plan generation
- Dry-run does not move hardware
- Execute requires explicit flag
- Permit mode default
- Split-process requirement recorded
- Fixture extraction
- Fixture QC
- Manifest validation after M21-B
- Compensation_ready remains false
- No GO1/G1 validation claim
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platforms.booster_k1.session import (
    BoosterK1Session,
    build_session_directory,
    SESSION_METADATA_FIELDS,
    TRIAL_RECORD_FIELDS,
    TRIAL_PLAN_FIELDS,
)
from platforms.booster_k1.measurement_runner import BoosterK1MeasurementRunner
from platforms.booster_k1.measurement_extractor import BoosterK1MeasurementExtractor
from platforms.booster_k1.measurement_qc import BoosterK1MeasurementQC
from platforms.booster_k1.measurement_logger import BoosterK1MeasurementLogger
from calibration_core.trial_scheduler import TrialScheduler
from tests.fixtures.fixture_helpers import build_fixture_session_dir

MANIFEST_PATH = ROOT / "outputs/measurement_v1/booster_k1_reference_manifest.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


# ---------------------------------------------------------------------------
# Session metadata builder tests
# ---------------------------------------------------------------------------

class TestK1SessionMetadata:
    def test_session_metadata_all_required_fields_present(self) -> None:
        session = BoosterK1Session(surface="S1_lab_hard_floor")
        metadata = session.build_metadata()
        for field in SESSION_METADATA_FIELDS:
            assert field in metadata, f"Missing field: {field}"

    def test_session_metadata_split_process_required(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert metadata["split_process_required"] is True

    def test_session_metadata_hardware_validated_reference(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert metadata["hardware_validated_reference"] is True

    def test_session_metadata_platform_is_booster_k1(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert metadata["platform"] == "booster_k1"

    def test_session_metadata_limitations_no_compensation_claim(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert any("no velocity compensation" in lim for lim in metadata["limitations"])

    def test_session_metadata_limitations_no_go1_g1_claim(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert any("no GO1/G1" in lim for lim in metadata["limitations"])

    def test_custom_session_id_is_preserved(self) -> None:
        session = BoosterK1Session(session_id="my_custom_session")
        assert session.session_id == "my_custom_session"
        metadata = session.build_metadata()
        assert metadata["session_id"] == "my_custom_session"

    def test_load_metadata_roundtrip(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "test_session"
        session = BoosterK1Session(
            session_id="roundtrip_test",
            surface="S2_marble_floor",
            base_dir=session_dir,
        )
        session.write_metadata()
        loaded = BoosterK1Session.load_metadata(session.session_dir)
        assert loaded["session_id"] == "roundtrip_test"
        assert loaded["surface"] == "S2_marble_floor"

    def test_from_metadata_reconstructs_session(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "test_session"
        session = BoosterK1Session(
            session_id="reconstruct_test",
            base_dir=session_dir,
        )
        session.write_metadata()
        reconstructed = BoosterK1Session.from_metadata(session.session_dir)
        assert reconstructed.session_id == "reconstruct_test"
        assert reconstructed.platform_id == "booster_k1"


# ---------------------------------------------------------------------------
# Session directory layout tests
# ---------------------------------------------------------------------------

class TestSessionDirectoryLayout:
    def test_ensure_session_dir_creates_layout(self, tmp_path: Path) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        session_dir = session.ensure_session_dir()
        assert session_dir.exists()
        assert (session_dir / "state_logs").is_dir()

    def test_write_metadata_creates_file(self, tmp_path: Path) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        path = session.write_metadata()
        assert path.exists()
        assert path.name == "session_metadata.json"

    def test_write_trial_plan_creates_csv(self, tmp_path: Path) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        trials = [
            {
                "trial_id": "K1_S1_B1_U020_R1",
                "surface_id": "S1_lab_hard_floor",
                "surface_type": "lab_hard_floor",
                "command_velocity": 0.2,
                "block_index": 1,
                "repeat_index": 1,
                "state_log_path": "state_logs/K1_S1_B1_U020_R1.csv",
            }
        ]
        path = session.write_trial_plan(trials)
        assert path.exists()
        assert path.name == "trial_plan.csv"

    def test_build_session_directory_convenience(self, tmp_path: Path) -> None:
        session = build_session_directory(
            session_id="convenience_test",
            base_dir=tmp_path,
        )
        assert session.session_dir.exists()
        assert (session.session_dir / "state_logs").is_dir()


# ---------------------------------------------------------------------------
# Trial plan generation tests
# ---------------------------------------------------------------------------

class TestTrialPlanGeneration:
    def test_plan_trials_generates_deterministic_plan(self) -> None:
        session = BoosterK1Session(surface="S1_lab_hard_floor")
        runner = BoosterK1MeasurementRunner(session=session)
        trials = runner.plan_trials(surfaces=["S1_lab_hard_floor"])
        assert len(trials) > 0
        # Each trial should have required attributes
        for t in trials:
            assert t.platform == "booster_k1"
            assert t.command_velocity > 0

    def test_plan_trials_with_custom_speeds(self) -> None:
        session = BoosterK1Session(speeds=[0.2, 0.4], repeats=2)
        runner = BoosterK1MeasurementRunner(session=session)
        trials = runner.plan_trials(
            surfaces=["S1_lab_hard_floor"],
            speeds=[0.2, 0.4],
            repeats=2,
        )
        # 1 surface × 2 speeds × 2 repeats = 4 trials
        assert len(trials) == 4

    def test_trial_scheduler_surface_independent_blocks(self) -> None:
        scheduler = TrialScheduler()
        trials = scheduler.build_trials(
            surfaces=["S1", "S2"],
            speeds=[0.2, 0.4],
            repeats=2,
            platform="booster_k1",
        )
        # 2 surfaces × 2 speeds × 2 repeats = 8 trials
        assert len(trials) == 8
        trial_ids = [t.trial_id for t in trials]
        assert len(set(trial_ids)) == len(trial_ids), "Trial IDs must be unique"


# ---------------------------------------------------------------------------
# Dry-run / execute safety tests
# ---------------------------------------------------------------------------

class TestDryRunSafety:
    def test_dry_run_does_not_move_hardware(self, tmp_path: Path) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        runner = BoosterK1MeasurementRunner(session=session, execute=False)
        result = runner.run(surfaces=["S1_lab_hard_floor"])
        assert result["dry_run"] is True
        assert result["hardware_executed"] is False

    def test_execute_requires_explicit_flag(self, tmp_path: Path) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        # Default constructor: execute=False
        runner = BoosterK1MeasurementRunner(session=session)
        assert runner.execute is False

    def test_permit_mode_is_default(self) -> None:
        session = BoosterK1Session()
        runner = BoosterK1MeasurementRunner(session=session)
        assert runner.permit is True

    def test_permit_can_be_disabled(self) -> None:
        session = BoosterK1Session()
        runner = BoosterK1MeasurementRunner(session=session, permit=False)
        assert runner.permit is False

    def test_dry_run_prints_trial_plan(self, tmp_path: Path, capsys) -> None:
        session = BoosterK1Session(base_dir=tmp_path)
        runner = BoosterK1MeasurementRunner(session=session)
        runner.run(surfaces=["S1_lab_hard_floor"])
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "No hardware was moved" in captured.out
        assert "--execute" in captured.out


# ---------------------------------------------------------------------------
# Split-process requirement tests
# ---------------------------------------------------------------------------

class TestSplitProcessRequirement:
    def test_runner_records_split_process_required(self) -> None:
        session = BoosterK1Session()
        runner = BoosterK1MeasurementRunner(session=session)
        assert runner.split_process_required is True

    def test_logger_records_split_process_required(self, tmp_path: Path) -> None:
        logger = BoosterK1MeasurementLogger(output_dir=tmp_path)
        assert logger.split_process_required is True

    def test_session_metadata_split_process_required(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert metadata["split_process_required"] is True


# ---------------------------------------------------------------------------
# Fixture extraction tests
# ---------------------------------------------------------------------------

class TestFixtureExtraction:
    def _fixture_session(self, tmp_path: Path) -> Path:
        return build_fixture_session_dir(tmp_path)

    def test_extract_trial_from_fixture_log(self, tmp_path: Path) -> None:
        fixture_session = self._fixture_session(tmp_path)
        log_path = fixture_session / "state_logs" / "K1_S1_lab_hard_floor_B1_U020_R1.csv"
        extractor = BoosterK1MeasurementExtractor()
        result = extractor.extract_trial(log_path)
        assert "command_velocity" in result
        assert "measured_actual_velocity" in result
        assert "yaw_drift_statistic" in result
        assert "extraction_status" in result
        assert result["extraction_status"] == "ok"

    def test_extract_batch_from_fixture(self, tmp_path: Path) -> None:
        fixture_session = self._fixture_session(tmp_path)
        extractor = BoosterK1MeasurementExtractor()
        summary = extractor.extract_batch(
            fixture_session / "state_logs",
            fixture_session,
        )
        assert summary["successfully_extracted"] == 6
        assert summary["extraction_errors"] == 0
        assert (fixture_session / "extracted_measurements.csv").exists()
        assert (fixture_session / "extraction_summary.json").exists()
        assert (fixture_session / "extraction_report.md").exists()

    def test_extract_nonexistent_log_raises(self) -> None:
        extractor = BoosterK1MeasurementExtractor()
        with pytest.raises(FileNotFoundError):
            extractor.extract_trial(Path("/nonexistent/trial.csv"))

    def test_fixture_data_is_marked_as_test_only(self, tmp_path: Path) -> None:
        fixture_session = self._fixture_session(tmp_path)
        metadata = json.loads(
            (fixture_session / "session_metadata.json").read_text(encoding="utf-8")
        )
        assert any("fixture" in lim.lower() or "test" in lim.lower()
                   for lim in metadata.get("limitations", []))


# ---------------------------------------------------------------------------
# Fixture QC tests
# ---------------------------------------------------------------------------

class TestFixtureQC:
    def _fixture_session(self, tmp_path: Path) -> Path:
        return build_fixture_session_dir(tmp_path)

    def test_qc_passes_on_valid_fixture(self, tmp_path: Path) -> None:
        fixture_session = self._fixture_session(tmp_path)
        # First extract so QC has measurements to check
        extractor = BoosterK1MeasurementExtractor()
        extractor.extract_batch(fixture_session / "state_logs", fixture_session)

        qc = BoosterK1MeasurementQC()
        summary = qc.run_qc(fixture_session)
        assert summary["overall_pass"] is True
        assert len(summary["errors"]) == 0

    def test_qc_detects_missing_metadata(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "incomplete_session"
        session_dir.mkdir()
        qc = BoosterK1MeasurementQC()
        summary = qc.run_qc(session_dir)
        assert summary["overall_pass"] is False
        assert any("session_metadata.json:missing" in e for e in summary["errors"])

    def test_qc_writes_output_files(self, tmp_path: Path) -> None:
        fixture_session = self._fixture_session(tmp_path)
        extractor = BoosterK1MeasurementExtractor()
        extractor.extract_batch(fixture_session / "state_logs", fixture_session)

        qc = BoosterK1MeasurementQC()
        qc.run_qc(fixture_session)
        assert (fixture_session / "qc_summary.json").exists()
        assert (fixture_session / "qc_report.md").exists()

    def test_qc_detects_duplicate_trial_ids(self, tmp_path: Path) -> None:
        """Build a session with duplicate trial IDs and verify QC catches it."""
        import csv
        session_dir = tmp_path / "dupe_session"
        session_dir.mkdir()
        (session_dir / "state_logs").mkdir()

        # Write minimal metadata
        (session_dir / "session_metadata.json").write_text(json.dumps({
            "session_id": "dupe_test",
            "platform": "booster_k1",
            "robot_model": "Booster K1",
            "robot_id": "Booster_K1",
            "surface": "S1_lab_hard_floor",
            "speeds": [0.2],
            "repeats": 1,
            "block_order": "randomized",
            "timing": {},
            "command_source": "booster_sdk",
            "state_sources": ["/odometer_state"],
            "measurement_source": "ros2_odometer_state",
            "extraction_method": "odometer",
            "split_process_required": True,
            "hardware_validated_reference": True,
            "created_at": "2026-06-11T00:00:00Z",
            "operator_notes": "",
            "limitations": [],
        }))

        # Write trial plan
        with (session_dir / "trial_plan.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["trial_id", "surface_id", "surface_type", "command_velocity", "block_index", "repeat_index", "state_log_path"])
            w.writeheader()
            w.writerow({"trial_id": "DUP_001", "surface_id": "S1", "surface_type": "hard", "command_velocity": "0.2", "block_index": "1", "repeat_index": "1", "state_log_path": ""})

        # Write trial records with duplicates
        with (session_dir / "trial_records.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "trial_id", "session_id", "robot_id", "environment_id",
                "surface_type", "command_velocity", "block_index", "repeat_index",
                "idle_sec", "command_sec", "stop_sec", "state_log_path",
                "valid", "invalid_reason", "timestamp", "notes",
            ])
            w.writeheader()
            w.writerow({"trial_id": "DUP_001", "session_id": "dupe", "robot_id": "K1", "environment_id": "env", "surface_type": "hard", "command_velocity": "0.2", "block_index": "1", "repeat_index": "1", "idle_sec": "2", "command_sec": "6", "stop_sec": "2", "state_log_path": "", "valid": "true", "invalid_reason": "", "timestamp": "", "notes": ""})
            w.writerow({"trial_id": "DUP_001", "session_id": "dupe", "robot_id": "K1", "environment_id": "env", "surface_type": "hard", "command_velocity": "0.2", "block_index": "1", "repeat_index": "1", "idle_sec": "2", "command_sec": "6", "stop_sec": "2", "state_log_path": "", "valid": "true", "invalid_reason": "", "timestamp": "", "notes": ""})

        qc = BoosterK1MeasurementQC()
        summary = qc.run_qc(session_dir)
        assert any("duplicate_trial_ids" in e for e in summary["errors"])


# ---------------------------------------------------------------------------
# Manifest validation tests
# ---------------------------------------------------------------------------

class TestManifestAfterM21B:
    def test_manifest_still_valid_after_m21b_changes(self) -> None:
        from calibration_core.measurement_manifest import load_manifest, validate_measurement_manifest
        manifest = load_manifest(MANIFEST_PATH)
        summary = validate_measurement_manifest(manifest, ROOT)
        assert summary["valid"] is True
        assert summary["extracted_measurement_rows"] == 72

    def test_compensation_ready_remains_false(self) -> None:
        from calibration_core.measurement_manifest import load_manifest
        manifest = load_manifest(MANIFEST_PATH)
        assert manifest["velocity_compensation_ready"] is False

    def test_no_go1_g1_validation_claim_in_manifest(self) -> None:
        from calibration_core.measurement_manifest import load_manifest
        manifest = load_manifest(MANIFEST_PATH)
        assert manifest["empirical_cross_platform_claim"] is False

    def test_no_go1_g1_validation_claim_in_status(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False
        assert status["velocity_compensation_ready"] is False


# ---------------------------------------------------------------------------
# Measurement logger tests
# ---------------------------------------------------------------------------

class TestMeasurementLogger:
    def test_logger_supports_position_and_yaw(self, tmp_path: Path) -> None:
        logger = BoosterK1MeasurementLogger(output_dir=tmp_path)
        assert logger.supports_position() is True
        assert logger.supports_yaw() is True

    def test_logger_start_trial_returns_path(self, tmp_path: Path) -> None:
        logger = BoosterK1MeasurementLogger(output_dir=tmp_path / "logs")
        path = logger.start_trial("test_trial")
        assert path.name == "test_trial.csv"
        assert path.parent == tmp_path / "logs"

    def test_logger_records_split_process(self, tmp_path: Path) -> None:
        logger = BoosterK1MeasurementLogger(output_dir=tmp_path)
        assert logger.split_process_required is True

    def test_logger_active_state(self, tmp_path: Path) -> None:
        logger = BoosterK1MeasurementLogger(output_dir=tmp_path)
        assert logger.is_active() is False
        logger.start_trial("test")
        assert logger.is_active() is True
        logger.stop_trial()
        assert logger.is_active() is False


# ---------------------------------------------------------------------------
# CLI integration tests (dry-run only, no hardware)
# ---------------------------------------------------------------------------

class TestCLIIntegration:
    def test_run_measurement_cli_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_booster_k1_measurement.py",
                "--surface", "S1_lab_hard_floor",
                "--session-id", "cli_test_dry",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "DRY RUN" in result.stdout
        assert "No hardware was moved" in result.stdout

    def test_extract_cli_rejects_missing_dir(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/extract_booster_k1_measurements.py",
                "--session-dir", "nonexistent_dir_xyz",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_qc_cli_rejects_missing_dir(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/qc_booster_k1_measurement_session.py",
                "--session-dir", "nonexistent_dir_xyz",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_run_measurement_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_booster_k1_measurement.py", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "--execute" in result.stdout
        assert "--no-permit" in result.stdout
        assert "--surface" in result.stdout


# ---------------------------------------------------------------------------
# Session metadata JSON structure tests
# ---------------------------------------------------------------------------

class TestSessionMetadataJSON:
    def test_metadata_is_valid_json(self) -> None:
        session = BoosterK1Session()
        session.ensure_session_dir()
        path = session.write_metadata()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert data["session_id"] == session.session_id

    def test_metadata_timing_fields(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert "timing" in metadata
        assert "idle_sec" in metadata["timing"]
        assert "command_sec" in metadata["timing"]


# ---------------------------------------------------------------------------
# Compensation readiness boundary tests
# ---------------------------------------------------------------------------

class TestCompensationReadinessBoundary:
    def test_measurement_module_status_compensation_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_manifest_compensation_ready_false(self) -> None:
        from calibration_core.measurement_manifest import load_manifest
        manifest = load_manifest(MANIFEST_PATH)
        assert manifest["velocity_compensation_ready"] is False

    def test_no_navigation_improvement_claimed(self) -> None:
        from calibration_core.measurement_manifest import load_manifest
        manifest = load_manifest(MANIFEST_PATH)
        assert manifest["navigation_improvement_claimed"] is False

    def test_session_metadata_no_compensation_in_limitations(self) -> None:
        session = BoosterK1Session()
        metadata = session.build_metadata()
        assert any("no velocity compensation" in lim for lim in metadata["limitations"])


# ---------------------------------------------------------------------------
# GO1/G1 boundary tests
# ---------------------------------------------------------------------------

class TestGO1G1Boundary:
    def test_no_go1_measurement_ready(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False

    def test_no_g1_measurement_ready(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_g1_measurement_ready"] is False

    def test_k1_is_only_validated_platform_in_status(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert "validated_platforms" in status
        assert "booster_k1" in status["validated_platforms"]
        assert "unitree_go1" not in status.get("validated_platforms", [])
        assert "unitree_g1" not in status.get("validated_platforms", [])
