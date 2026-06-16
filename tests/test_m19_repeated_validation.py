"""Tests for M19-A repeated validation infrastructure."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from k1_measurement.m19_validation_schema import ValidationSummary, PerCommandAggregate, RepeatedTrialRecord
from scripts.analyze_m19_repeated_validation import (
    discover_records, is_real_evidence, compute_per_command, run_pending_mode,
    DEFAULT_WEIGHTS, COMMAND_VELOCITIES, OUTPUT_DIR, INPUT_DIR,
)

def test_schema_validation():
    s = ValidationSummary(analysis_timestamp="2025", mode="pending_data", total_trials=0, total_valid=0, commands_evaluated=0, commands_pending=8)
    assert s.mode == "pending_data"
    assert not s.real_repeated_logs_found

def test_aggregate_defaults():
    agg = PerCommandAggregate(command_velocity=0.30, n_total=0, n_valid=0, mean_actual_velocity=None, std_actual_velocity=None, mean_tracking_error=None, abs_mean_tracking_error=None, no_motion_ratio=0.0, mean_yaw_drift=None, yaw_drift_risk=0.0, uncertainty=0.0, risk_score=0.0, region_label="pending_real_data", evidence_level="pending_real_data")
    assert agg.region_label == "pending_real_data"

def test_discover_empty_dir():
    with tempfile.TemporaryDirectory() as td:
        recs = discover_records(Path(td))
        assert len(recs) == 0

def test_reject_dummy_record():
    rec = {"trial_id": "dummy_001", "evidence_type": "dummy", "valid": True, "command_velocity": 0.3, "measured_actual_velocity": 0.28}
    assert not is_real_evidence(rec)

def test_accept_real_record():
    rec = {"trial_id": "real_001", "valid": True, "command_velocity": 0.3, "measured_actual_velocity": 0.28}
    assert is_real_evidence(rec)

def test_pending_mode_summary():
    summary = run_pending_mode(DEFAULT_WEIGHTS)
    assert summary.mode == "pending_data"
    assert summary.total_trials == 0
    assert summary.commands_pending == 8
    assert len(summary.per_command) == 8

def test_compute_per_command():
    records = [{"command_velocity": 0.3, "valid": True, "measured_actual_velocity": 0.28, "yaw_drift_statistic": 0.5},
               {"command_velocity": 0.3, "valid": True, "measured_actual_velocity": 0.29, "yaw_drift_statistic": 0.6},
               {"command_velocity": 0.3, "valid": True, "measured_actual_velocity": 0.27, "yaw_drift_statistic": 0.4}]
    agg = compute_per_command(records, 0.30, DEFAULT_WEIGHTS)
    assert agg.n_total == 3
    assert agg.n_valid == 3
    assert agg.mean_actual_velocity is not None
    assert abs(agg.mean_actual_velocity - 0.28) < 0.01

def test_region_classification_reliable():
    records = [{"command_velocity": 0.4, "valid": True, "measured_actual_velocity": 0.39, "yaw_drift_statistic": 0.5},
               {"command_velocity": 0.4, "valid": True, "measured_actual_velocity": 0.40, "yaw_drift_statistic": 0.4},
               {"command_velocity": 0.4, "valid": True, "measured_actual_velocity": 0.38, "yaw_drift_statistic": 0.3}]
    agg = compute_per_command(records, 0.40, DEFAULT_WEIGHTS)
    assert agg.region_label in ("reliable", "insufficient_evidence")

def test_region_classification_deadzone():
    records = [{"command_velocity": 0.10, "valid": True, "measured_actual_velocity": 0.0, "yaw_drift_statistic": 0.0},
               {"command_velocity": 0.10, "valid": True, "measured_actual_velocity": 0.01, "yaw_drift_statistic": 0.0},
               {"command_velocity": 0.10, "valid": True, "measured_actual_velocity": 0.0, "yaw_drift_statistic": 0.0}]
    agg = compute_per_command(records, 0.10, DEFAULT_WEIGHTS)
    assert agg.region_label == "deadzone"

def test_analyzer_runs_pending(tmp_path, monkeypatch):
    import scripts.analyze_m19_repeated_validation as am
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setattr(am, "INPUT_DIR", tmp_path / "inputs")
    assert am.main() == 0
