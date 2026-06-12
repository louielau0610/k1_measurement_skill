"""Tests for M23-E revised offline compensator."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import SUPPORTED_EMPIRICAL_PLATFORM
from calibration_core.revised_velocity_compensation import RevisedCompensationRequest, revised_compensate_velocity

OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
SUMMARY = OUTPUT_DIR / "m23e_revised_compensator_summary.json"
SWEEP_CSV = OUTPUT_DIR / "m23e_revised_compensator_sweep.csv"
SWEEP_JSON = OUTPUT_DIR / "m23e_revised_compensator_sweep.json"
REPORT = OUTPUT_DIR / "m23e_revised_compensator_report.md"
DOC = ROOT / "docs/m23e_revised_offline_compensator.md"


def _request(**kwargs) -> RevisedCompensationRequest:
    data = {
        "platform": SUPPORTED_EMPIRICAL_PLATFORM,
        "surface_type": "S2_marble_floor",
        "desired_actual_velocity_mps": 0.50,
    }
    data.update(kwargs)
    return RevisedCompensationRequest(**data)


def test_identity_fallback_when_direct_error_good_enough() -> None:
    decision = revised_compensate_velocity(_request())
    assert decision.feasibility_status == "identity_preferred"
    assert decision.final_command_velocity_mps == decision.desired_actual_velocity_mps
    assert decision.expected_direct_error_mps <= 0.02
    assert decision.deployment_ready is False


def test_benefit_gate_rejects_insufficient_expected_benefit() -> None:
    decision = revised_compensate_velocity(_request(
        physical_context_csv_path=None,
        direct_error_good_enough_mps=0.0,
        minimum_expected_benefit_mps=1.0,
    ))
    assert decision.feasibility_status == "compensation_not_beneficial"
    assert decision.benefit_gate_passed is False
    assert decision.final_command_velocity_mps == decision.identity_command_velocity_mps


def test_correction_magnitude_limit_rejects_overcorrection_by_default() -> None:
    decision = revised_compensate_velocity(_request(
        physical_context_csv_path=None,
        direct_error_good_enough_mps=0.0,
        minimum_expected_benefit_mps=0.0,
        max_correction_mps=0.01,
    ))
    assert decision.feasibility_status == "overcorrection_risk"
    assert decision.correction_magnitude_mps > 0.01
    assert decision.correction_limited is False


def test_optional_clamping_behavior() -> None:
    decision = revised_compensate_velocity(_request(
        physical_context_csv_path=None,
        direct_error_good_enough_mps=0.0,
        minimum_expected_benefit_mps=0.0,
        max_correction_mps=0.01,
        allow_clamping=True,
    ))
    assert decision.feasibility_status == "feasible_but_clamped"
    assert decision.correction_limited is True
    assert abs(decision.final_command_velocity_mps - decision.desired_actual_velocity_mps) <= 0.0100001


def test_profile_mismatch_detection() -> None:
    decision = revised_compensate_velocity(_request())
    assert decision.profile_mismatch_suspected is True
    assert "profile_mismatch_suspected" in decision.warnings


def test_revised_cli_json_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/revised_offline_compensate_velocity.py",
            "--platform", "booster_k1",
            "--surface", "S2_marble_floor",
            "--desired-velocity", "0.50",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert data["feasibility_status"] == "identity_preferred"
    assert data["deployment_ready"] is False
    assert data["physical_validation_status"] == "not_started"


def test_revised_sweep_output_files_and_summary() -> None:
    assert SUMMARY.exists()
    assert SWEEP_CSV.exists()
    assert SWEEP_JSON.exists()
    assert REPORT.exists()
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["identity_fallback_count"] == 4
    assert data["harmful_m23c_commands_selected"] == 0
    assert data["all_final_commands_identity"] is True


def test_m23c_failure_mode_avoided_offline() -> None:
    rows = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    assert all(row["final_command_velocity_mps"] == row["identity_command_velocity_mps"] for row in rows)
    assert all(row["candidate_compensated_command_velocity_mps"] != row["final_command_velocity_mps"] for row in rows)


def test_no_go1_g1_validation_claim_or_hardware_execution() -> None:
    text = DOC.read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "no GO1/G1 validation" in text
    assert summary["hardware_execution"] is False
    assert summary["physical_validation_status"] == "not_started"
    assert summary["deployment_ready"] is False
    assert not (ROOT / "scripts/run_m23e_k1_revised_compensation_trials.py").exists()
