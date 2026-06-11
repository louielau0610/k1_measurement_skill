"""Tests for M21-C: Measurement Data Contract.

Tests cover:
- trial schema validation
- aggregate schema validation
- session metadata validation
- invalid extraction status handling
- invalid trial requires reason
- velocity unit fields
- yaw degree fields
- command velocity not copied as measured velocity
- legacy field mapping
- K1 legacy CSV conversion
- contract CSV validation
- session directory validation
- missing path handling
- status enum validation
- compensation_ready remains false
- no GO1/G1 validation claim
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

from calibration_core.measurement_contract import (
    MEASUREMENT_CONTRACT_VERSION,
    TRIAL_CONTRACT_FIELDS,
    AGGREGATE_CONTRACT_FIELDS,
    SESSION_METADATA_CONTRACT_FIELDS,
    VALID_EXTRACTION_STATUSES,
    COORDINATE_CONVENTION,
    validate_trial_measurement,
    validate_aggregate_response,
    validate_session_metadata,
    validate_measurement_csv,
    validate_response_statistics_csv,
    validate_session_directory,
    build_validation_report,
)
from calibration_core.measurement_contract_mapping import (
    map_legacy_trial_row,
    map_legacy_aggregate_row,
    map_legacy_session_metadata,
    LEGACY_TO_CONTRACT_TRIAL,
    LEGACY_TO_CONTRACT_AGGREGATE,
)

MANIFEST_PATH = ROOT / "outputs/measurement_v1/booster_k1_reference_manifest.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"
CONTRACT_CSV = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv"

# ---------------------------------------------------------------------------
# Helper: build a minimal valid trial row
# ---------------------------------------------------------------------------

def _valid_trial_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "schema_version": MEASUREMENT_CONTRACT_VERSION,
        "dataset_id": "test_dataset",
        "session_id": "test_session",
        "trial_id": "TEST_001",
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "robot_id": "Booster_K1",
        "surface_type": "lab_hard_floor",
        "environment_id": "test_env",
        "command_velocity_mps": 0.5,
        "measured_actual_velocity_mps": 0.45,
        "tracking_error_mps": -0.05,
        "relative_tracking_error": -0.1,
        "yaw_drift_deg": 2.5,
        "imu_yaw_drift_deg": 2.3,
        "state_source": "/odometer_state",
        "command_source": "booster_sdk",
        "measurement_source": "ros2_odometer_state",
        "measurement_method": "odometer_displacement",
        "analysis_window_start_sec": 3.0,
        "analysis_window_end_sec": 8.0,
        "state_log_path": "state_logs/TEST_001.csv",
        "raw_log_path": "unavailable",
        "extraction_status": "ok",
        "confidence": "high",
        "invalid_reason": "",
        "created_at": "2026-06-11T00:00:00Z",
    }
    row.update(overrides)
    return row


# ---------------------------------------------------------------------------
# Trial schema validation
# ---------------------------------------------------------------------------

class TestTrialSchemaValidation:
    def test_valid_trial_passes(self) -> None:
        result = validate_trial_measurement(_valid_trial_row())
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_required_field_detected(self) -> None:
        row = _valid_trial_row()
        del row["command_velocity_mps"]
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("command_velocity_mps" in e for e in result["errors"])

    def test_all_27_fields_recognized(self) -> None:
        row = _valid_trial_row()
        for field in TRIAL_CONTRACT_FIELDS:
            assert field in row, f"Field {field} missing from valid row"

    def test_non_numeric_velocity_detected(self) -> None:
        row = _valid_trial_row(command_velocity_mps="fast")
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("command_velocity_mps:not_numeric" in e for e in result["errors"])

    def test_schema_version_field_present(self) -> None:
        row = _valid_trial_row()
        assert row["schema_version"] == MEASUREMENT_CONTRACT_VERSION


# ---------------------------------------------------------------------------
# Extraction status enum validation
# ---------------------------------------------------------------------------

class TestExtractionStatusEnum:
    def test_valid_statuses_pass(self) -> None:
        for status in VALID_EXTRACTION_STATUSES:
            kwargs: dict[str, object] = {"extraction_status": status}
            if status == "invalid_trial":
                kwargs["invalid_reason"] = "robot error"
            row = _valid_trial_row(**kwargs)
            result = validate_trial_measurement(row)
            assert result["valid"] is True, f"Status '{status}' should be valid"

    def test_invalid_status_detected(self) -> None:
        row = _valid_trial_row(extraction_status="garbage_status")
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("extraction_status:invalid_enum" in e for e in result["errors"])

    def test_all_expected_enums_present(self) -> None:
        expected = {"ok", "invalid_trial", "missing_log", "insufficient_samples",
                     "missing_state_source", "extraction_error", "not_extracted"}
        assert VALID_EXTRACTION_STATUSES == expected


# ---------------------------------------------------------------------------
# Invalid trial requires reason
# ---------------------------------------------------------------------------

class TestInvalidTrialRequiresReason:
    def test_invalid_trial_without_reason_detected(self) -> None:
        row = _valid_trial_row(extraction_status="invalid_trial", invalid_reason="")
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("invalid_trial:missing_reason" in e for e in result["errors"])

    def test_invalid_trial_with_reason_passes(self) -> None:
        row = _valid_trial_row(
            extraction_status="invalid_trial",
            invalid_reason="robot slipped on surface",
        )
        result = validate_trial_measurement(row)
        # Still fails because missing fields? Let's check - it should have invalid reason
        # But extraction_status is invalid_trial which means measured_actual might be 0
        # The contract doesn't require measurement to be nonzero for invalid trials
        # Main check: no "missing_reason" error
        assert not any("missing_reason" in e for e in result["errors"])

    def test_ok_status_with_empty_reason_passes(self) -> None:
        row = _valid_trial_row(extraction_status="ok", invalid_reason="")
        result = validate_trial_measurement(row)
        assert result["valid"] is True


# ---------------------------------------------------------------------------
# Command velocity not copied as measured
# ---------------------------------------------------------------------------

class TestCommandVelocityNotCopied:
    def test_identical_values_detected(self) -> None:
        row = _valid_trial_row(
            command_velocity_mps=0.5,
            measured_actual_velocity_mps=0.5,
        )
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("command_velocity_copied_as_measured" in e for e in result["errors"])

    def test_different_values_pass(self) -> None:
        row = _valid_trial_row(
            command_velocity_mps=0.5,
            measured_actual_velocity_mps=0.45,
        )
        result = validate_trial_measurement(row)
        assert result["valid"] is True

    def test_zero_command_identical_ok(self) -> None:
        row = _valid_trial_row(
            command_velocity_mps=0.0,
            measured_actual_velocity_mps=0.0,
        )
        result = validate_trial_measurement(row)
        # Zero command velocity means robot wasn't moving; identical is OK
        assert result["valid"] is True


# ---------------------------------------------------------------------------
# Velocity unit fields
# ---------------------------------------------------------------------------

class TestVelocityUnitFields:
    def test_command_velocity_field_name_has_mps(self) -> None:
        assert "command_velocity_mps" in TRIAL_CONTRACT_FIELDS
        assert "command_velocity" not in TRIAL_CONTRACT_FIELDS

    def test_measured_velocity_field_name_has_mps(self) -> None:
        assert "measured_actual_velocity_mps" in TRIAL_CONTRACT_FIELDS
        assert "measured_actual_velocity" not in TRIAL_CONTRACT_FIELDS

    def test_tracking_error_field_name_has_mps(self) -> None:
        assert "tracking_error_mps" in TRIAL_CONTRACT_FIELDS

    def test_aggregate_velocity_fields_have_mps(self) -> None:
        for field in ["mean_actual_velocity_mps", "std_actual_velocity_mps",
                       "mean_tracking_error_mps", "mean_abs_tracking_error_mps"]:
            assert field in AGGREGATE_CONTRACT_FIELDS, f"Missing: {field}"


# ---------------------------------------------------------------------------
# Yaw degree fields
# ---------------------------------------------------------------------------

class TestYawDegreeFields:
    def test_yaw_drift_field_has_deg(self) -> None:
        assert "yaw_drift_deg" in TRIAL_CONTRACT_FIELDS

    def test_imu_yaw_drift_field_has_deg(self) -> None:
        assert "imu_yaw_drift_deg" in TRIAL_CONTRACT_FIELDS

    def test_aggregate_yaw_fields_have_deg(self) -> None:
        for field in ["mean_yaw_drift_deg", "std_yaw_drift_deg", "max_yaw_drift_deg"]:
            assert field in AGGREGATE_CONTRACT_FIELDS, f"Missing: {field}"


# ---------------------------------------------------------------------------
# Aggregate schema validation
# ---------------------------------------------------------------------------

class TestAggregateSchemaValidation:
    def _valid_agg_row(self, **overrides: object) -> dict[str, object]:
        row: dict[str, object] = {
            "schema_version": MEASUREMENT_CONTRACT_VERSION,
            "dataset_id": "test_dataset",
            "platform": "booster_k1",
            "robot_model": "Booster K1",
            "surface_type": "lab_hard_floor",
            "command_velocity_mps": 0.5,
            "n": 3,
            "mean_actual_velocity_mps": 0.45,
            "std_actual_velocity_mps": 0.02,
            "median_actual_velocity_mps": 0.45,
            "min_actual_velocity_mps": 0.42,
            "max_actual_velocity_mps": 0.47,
            "mean_tracking_error_mps": -0.05,
            "mean_abs_tracking_error_mps": 0.05,
            "relative_tracking_error": -0.1,
            "under_tracking_ratio": 0.8,
            "no_motion_ratio": 0.0,
            "mean_yaw_drift_deg": 2.5,
            "std_yaw_drift_deg": 0.5,
            "max_yaw_drift_deg": 3.0,
            "response_uncertainty": 0.02,
            "risk_score": 0.15,
            "region_label": "nominal",
            "evidence_level": "high",
            "limitations": "test",
        }
        row.update(overrides)
        return row

    def test_valid_aggregate_passes(self) -> None:
        result = validate_aggregate_response(self._valid_agg_row())
        assert result["valid"] is True

    def test_missing_field_detected(self) -> None:
        row = self._valid_agg_row()
        del row["n"]
        result = validate_aggregate_response(row)
        assert result["valid"] is False
        assert any("n" in e for e in result["errors"])

    def test_n_must_be_positive(self) -> None:
        row = self._valid_agg_row(n=0)
        result = validate_aggregate_response(row)
        assert result["valid"] is False
        assert any("n:must_be_positive" in e for e in result["errors"])

    def test_all_25_aggregate_fields_recognized(self) -> None:
        row = self._valid_agg_row()
        for field in AGGREGATE_CONTRACT_FIELDS:
            assert field in row, f"Missing aggregate field: {field}"


# ---------------------------------------------------------------------------
# Session metadata validation
# ---------------------------------------------------------------------------

class TestSessionMetadataValidation:
    def _valid_meta(self, **overrides: object) -> dict[str, object]:
        meta: dict[str, object] = {
            "schema_version": MEASUREMENT_CONTRACT_VERSION,
            "session_id": "test_session",
            "dataset_id": "test_dataset",
            "platform": "booster_k1",
            "robot_model": "Booster K1",
            "robot_id": "Booster_K1",
            "surfaces": ["S1_lab_hard_floor"],
            "speeds_mps": [0.2, 0.4],
            "repeats": 2,
            "block_order": "randomized",
            "timing": {"idle_sec": 2.0, "command_sec": 6.0, "stop_sec": 2.0},
            "command_source": "booster_sdk",
            "state_sources": ["/odometer_state"],
            "coordinate_convention": {
                "body_x": "forward",
                "body_y": "left",
                "body_z": "up",
                "yaw_internal_unit": "radians",
                "yaw_export_unit": "degrees",
            },
            "state_frame": "odom",
            "body_frame": "base_link",
            "measurement_method": "odometer_displacement",
            "analysis_window": {"start_sec": 3.0, "end_sec": 8.0},
            "hardware_validated_reference": True,
            "operator_notes": "",
            "limitations": ["test"],
            "created_at": "2026-06-11T00:00:00Z",
        }
        meta.update(overrides)
        return meta

    def test_valid_metadata_passes(self) -> None:
        result = validate_session_metadata(self._valid_meta())
        assert result["valid"] is True

    def test_missing_field_detected(self) -> None:
        meta = self._valid_meta()
        del meta["platform"]
        result = validate_session_metadata(meta)
        assert result["valid"] is False

    def test_wrong_body_x_detected(self) -> None:
        meta = self._valid_meta()
        meta["coordinate_convention"] = {"body_x": "backward", "body_y": "left", "body_z": "up"}
        result = validate_session_metadata(meta)
        assert result["valid"] is False
        assert any("body_x" in e for e in result["errors"])

    def test_wrong_body_y_detected(self) -> None:
        meta = self._valid_meta()
        meta["coordinate_convention"] = {"body_x": "forward", "body_y": "right", "body_z": "up"}
        result = validate_session_metadata(meta)
        assert result["valid"] is False

    def test_surfaces_must_be_list(self) -> None:
        meta = self._valid_meta()
        meta["surfaces"] = "S1_lab_hard_floor"
        result = validate_session_metadata(meta)
        assert result["valid"] is False

    def test_repeats_must_be_positive(self) -> None:
        meta = self._valid_meta()
        meta["repeats"] = 0
        result = validate_session_metadata(meta)
        assert result["valid"] is False


# ---------------------------------------------------------------------------
# Legacy field mapping
# ---------------------------------------------------------------------------

class TestLegacyFieldMapping:
    def test_command_velocity_maps_to_mps(self) -> None:
        legacy = {"trial_id": "T01", "command_velocity": "0.5", "measured_actual_velocity": "0.45"}
        row = map_legacy_trial_row(legacy)
        assert row["command_velocity_mps"] == 0.5
        assert row["measured_actual_velocity_mps"] == 0.45

    def test_yaw_drift_maps_to_deg(self) -> None:
        legacy = {"trial_id": "T01", "yaw_drift_statistic": "3.2"}
        row = map_legacy_trial_row(legacy)
        assert row["yaw_drift_deg"] == 3.2

    def test_imu_yaw_drift_maps_to_deg(self) -> None:
        legacy = {"trial_id": "T01", "imu_yaw_drift_deg": "1.5"}
        row = map_legacy_trial_row(legacy)
        assert row["imu_yaw_drift_deg"] == 1.5

    def test_confidence_maps_from_measurement_confidence(self) -> None:
        legacy = {"trial_id": "T01", "measurement_confidence": "high"}
        row = map_legacy_trial_row(legacy)
        assert row["confidence"] == "high"

    def test_tracking_error_is_derived(self) -> None:
        legacy = {"trial_id": "T01", "command_velocity": "0.5", "measured_actual_velocity": "0.45"}
        row = map_legacy_trial_row(legacy)
        assert row["tracking_error_mps"] == pytest.approx(-0.05)
        assert row["relative_tracking_error"] == pytest.approx(-0.1)

    def test_state_log_path_derived_from_trial_id(self) -> None:
        legacy = {"trial_id": "M19C_S1_B1_U020_R1"}
        row = map_legacy_trial_row(legacy)
        assert "m19c_ros2_odometer_logs" in str(row["state_log_path"])
        assert "M19C_S1_B1_U020_R1" in str(row["state_log_path"])

    def test_raw_log_path_defaults_to_unavailable(self) -> None:
        legacy = {"trial_id": "T01"}
        row = map_legacy_trial_row(legacy)
        assert row["raw_log_path"] == "unavailable"

    def test_legacy_aggregate_mapping(self) -> None:
        legacy = {
            "surface_id": "S1_lab_hard_floor",
            "command_velocity": "0.5",
            "n": "3",
            "mean_actual_velocity": "0.45",
        }
        row = map_legacy_aggregate_row(legacy)
        assert row["command_velocity_mps"] == 0.5
        assert row["mean_actual_velocity_mps"] == 0.45


# ---------------------------------------------------------------------------
# K1 legacy CSV conversion (real file)
# ---------------------------------------------------------------------------

class TestK1LegacyCSVConversion:
    def test_contract_csv_exists(self) -> None:
        assert CONTRACT_CSV.exists(), f"Contract CSV not found: {CONTRACT_CSV}"

    def test_contract_csv_has_72_rows(self) -> None:
        with CONTRACT_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 72

    def test_contract_csv_all_rows_valid(self) -> None:
        result = validate_measurement_csv(CONTRACT_CSV)
        assert result["valid"] is True
        assert result["valid_rows"] == 72
        assert result["invalid_rows"] == 0

    def test_contract_csv_has_all_required_columns(self) -> None:
        with CONTRACT_CSV.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
        for field in TRIAL_CONTRACT_FIELDS:
            assert field in columns, f"Missing column: {field}"

    def test_contract_csv_no_command_copy(self) -> None:
        with CONTRACT_CSV.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            cmd = float(row["command_velocity_mps"])
            meas = float(row["measured_actual_velocity_mps"])
            if cmd != 0:
                assert abs(cmd - meas) > 1e-9, f"Copy detected in {row['trial_id']}"


# ---------------------------------------------------------------------------
# Contract CSV validation (synthetic)
# ---------------------------------------------------------------------------

class TestContractCSVValidation:
    def test_validate_empty_csv(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.csv"
        path.write_text("schema_version\n")
        result = validate_measurement_csv(path)
        assert result["valid"] is False
        assert result["total_rows"] == 0

    def test_validate_nonexistent_csv(self) -> None:
        result = validate_measurement_csv(Path("/nonexistent/contract.csv"))
        assert result["valid"] is False
        assert any("file_not_found" in e for e in result["errors"])

    def test_validate_valid_csv(self, tmp_path: Path) -> None:
        path = tmp_path / "valid.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=TRIAL_CONTRACT_FIELDS)
            w.writeheader()
            w.writerow(_valid_trial_row())
        result = validate_measurement_csv(path)
        assert result["valid"] is True
        assert result["valid_rows"] == 1

    def test_validate_csv_with_one_bad_row(self, tmp_path: Path) -> None:
        path = tmp_path / "mixed.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=TRIAL_CONTRACT_FIELDS)
            w.writeheader()
            w.writerow(_valid_trial_row(trial_id="good"))
            # Make a bad row: non-numeric velocity
            bad = _valid_trial_row(trial_id="bad", command_velocity_mps="not_a_number")
            w.writerow(bad)
        result = validate_measurement_csv(path)
        assert result["valid"] is False
        assert result["valid_rows"] == 1
        assert result["invalid_rows"] == 1


# ---------------------------------------------------------------------------
# Session directory validation
# ---------------------------------------------------------------------------

class TestSessionDirectoryValidation:
    def test_nonexistent_directory(self) -> None:
        result = validate_session_directory(Path("/nonexistent/session"))
        assert result["valid"] is False

    def test_minimal_valid_session_directory(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "minimal_session"
        session_dir.mkdir()
        (session_dir / "state_logs").mkdir()

        # Write valid session metadata
        meta = {
            "schema_version": MEASUREMENT_CONTRACT_VERSION,
            "session_id": "test",
            "dataset_id": "test",
            "platform": "booster_k1",
            "robot_model": "Booster K1",
            "robot_id": "Booster_K1",
            "surfaces": ["S1"],
            "speeds_mps": [0.2],
            "repeats": 1,
            "block_order": "sequential",
            "timing": {"idle_sec": 2.0, "command_sec": 6.0, "stop_sec": 2.0},
            "command_source": "sdk",
            "state_sources": ["/odom"],
            "coordinate_convention": {
                "body_x": "forward", "body_y": "left", "body_z": "up",
                "yaw_internal_unit": "radians", "yaw_export_unit": "degrees",
            },
            "state_frame": "odom",
            "body_frame": "base_link",
            "measurement_method": "test",
            "analysis_window": {"start_sec": 3.0, "end_sec": 8.0},
            "hardware_validated_reference": False,
            "operator_notes": "",
            "limitations": ["test"],
            "created_at": "2026-06-11T00:00:00Z",
        }
        (session_dir / "session_metadata.json").write_text(json.dumps(meta))

        # Write valid measurements CSV
        with (session_dir / "extracted_measurements.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TRIAL_CONTRACT_FIELDS)
            w.writeheader()
            w.writerow(_valid_trial_row())

        result = validate_session_directory(session_dir)
        assert result["valid"] is True

    def test_session_dir_missing_metadata(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "no_meta"
        session_dir.mkdir()
        result = validate_session_directory(session_dir)
        assert result["valid"] is False
        assert any("session_metadata.json:missing" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# Response statistics CSV validation
# ---------------------------------------------------------------------------

class TestResponseStatisticsCSVValidation:
    def test_validate_nonexistent(self) -> None:
        result = validate_response_statistics_csv(Path("/nonexistent/stats.csv"))
        assert result["valid"] is False

    def test_validate_valid_stats(self, tmp_path: Path) -> None:
        path = tmp_path / "stats.csv"
        row = {
            "schema_version": MEASUREMENT_CONTRACT_VERSION,
            "dataset_id": "test",
            "platform": "booster_k1",
            "robot_model": "Booster K1",
            "surface_type": "lab_hard_floor",
            "command_velocity_mps": "0.5",
            "n": "3",
            "mean_actual_velocity_mps": "0.45",
            "std_actual_velocity_mps": "0.02",
            "median_actual_velocity_mps": "0.45",
            "min_actual_velocity_mps": "0.42",
            "max_actual_velocity_mps": "0.47",
            "mean_tracking_error_mps": "-0.05",
            "mean_abs_tracking_error_mps": "0.05",
            "relative_tracking_error": "-0.1",
            "under_tracking_ratio": "0.8",
            "no_motion_ratio": "0.0",
            "mean_yaw_drift_deg": "2.5",
            "std_yaw_drift_deg": "0.5",
            "max_yaw_drift_deg": "3.0",
            "response_uncertainty": "0.02",
            "risk_score": "0.15",
            "region_label": "nominal",
            "evidence_level": "high",
            "limitations": "test",
        }
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(row.keys()))
            w.writeheader()
            w.writerow(row)
        result = validate_response_statistics_csv(path)
        assert result["valid"] is True


# ---------------------------------------------------------------------------
# Coordinate convention
# ---------------------------------------------------------------------------

class TestCoordinateConvention:
    def test_convention_body_x_forward(self) -> None:
        assert COORDINATE_CONVENTION["body_x"] == "forward"

    def test_convention_body_y_left(self) -> None:
        assert COORDINATE_CONVENTION["body_y"] == "left"

    def test_convention_body_z_up(self) -> None:
        assert COORDINATE_CONVENTION["body_z"] == "up"

    def test_convention_yaw_export_degrees(self) -> None:
        assert COORDINATE_CONVENTION["yaw_export_unit"] == "degrees"


# ---------------------------------------------------------------------------
# Build validation report helper
# ---------------------------------------------------------------------------

class TestBuildValidationReport:
    def test_returns_structured_dict(self) -> None:
        report = build_validation_report(True, [], warnings=["w1"])
        assert report["valid"] is True
        assert report["errors"] == []
        assert report["warnings"] == ["w1"]
        assert report["contract_version"] == MEASUREMENT_CONTRACT_VERSION

    def test_accepts_extra_kwargs(self) -> None:
        report = build_validation_report(False, ["e1"], trial_id="T01")
        assert report["trial_id"] == "T01"


# ---------------------------------------------------------------------------
# Missing path handling
# ---------------------------------------------------------------------------

class TestMissingPathHandling:
    def test_both_log_paths_empty_detected(self) -> None:
        row = _valid_trial_row(state_log_path="", raw_log_path="")
        result = validate_trial_measurement(row)
        assert result["valid"] is False
        assert any("missing_log_paths" in e for e in result["errors"])

    def test_state_log_path_only_is_ok(self) -> None:
        row = _valid_trial_row(state_log_path="logs/test.csv", raw_log_path="")
        result = validate_trial_measurement(row)
        assert result["valid"] is True

    def test_raw_log_path_only_is_ok(self) -> None:
        row = _valid_trial_row(state_log_path="", raw_log_path="bags/test.bag")
        result = validate_trial_measurement(row)
        assert result["valid"] is True


# ---------------------------------------------------------------------------
# Compensation readiness / phase gate tests
# ---------------------------------------------------------------------------

class TestCompensationReadiness:
    def test_manifest_compensation_ready_false(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert manifest["velocity_compensation_ready"] is False

    def test_status_compensation_ready_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_contract_json_compensation_ready_false(self) -> None:
        contract = json.loads(
            (ROOT / "outputs/measurement_v1/measurement_contract_v1.json").read_text(encoding="utf-8")
        )
        assert contract["phase_gates"]["velocity_compensation_ready"] is False


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

    def test_contract_json_go1_g1_false(self) -> None:
        contract = json.loads(
            (ROOT / "outputs/measurement_v1/measurement_contract_v1.json").read_text(encoding="utf-8")
        )
        assert contract["phase_gates"]["unitree_go1_measurement_ready"] is False
        assert contract["phase_gates"]["unitree_g1_measurement_ready"] is False

    def test_manifest_cross_platform_false(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert manifest["empirical_cross_platform_claim"] is False


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestCLIIntegration:
    def test_validate_contract_cli_measurements(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_measurement_contract.py",
                "--measurements",
                "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        # CLI returns 0 for pass, 1 for fail
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_validate_contract_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_measurement_contract.py", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "--measurements" in result.stdout
        assert "--session-dir" in result.stdout
        assert "--metadata" in result.stdout

    def test_convert_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/convert_measurements_to_contract.py", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "--input" in result.stdout
        assert "--output" in result.stdout
        assert "--platform" in result.stdout

    def test_validate_contract_cli_json_output(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_measurement_contract.py",
                "--measurements",
                "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv",
                "--json",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        assert data["valid"] is True


# ---------------------------------------------------------------------------
# Session metadata contract fields completeness
# ---------------------------------------------------------------------------

class TestSessionMetadataContractFields:
    def test_all_required_fields_listed(self) -> None:
        required_session_fields = {
            "schema_version", "session_id", "dataset_id", "platform",
            "robot_model", "robot_id", "surfaces", "speeds_mps", "repeats",
            "block_order", "timing", "command_source", "state_sources",
            "coordinate_convention", "state_frame", "body_frame",
            "measurement_method", "analysis_window",
            "hardware_validated_reference", "operator_notes",
            "limitations", "created_at",
        }
        assert set(SESSION_METADATA_CONTRACT_FIELDS) == required_session_fields
