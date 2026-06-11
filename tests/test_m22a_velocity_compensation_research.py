from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "outputs/compensation_research/velocity_compensation_m22a_summary.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


def test_m22a_research_summary_exists() -> None:
    assert SUMMARY_PATH.exists()
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["phase"] == "velocity_compensation_principle_research"


def test_m22a_implementation_ready_is_false() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["implementation_ready"] is False
    assert summary["velocity_compensation_ready"] is False
    assert summary["k1_compensation_validated"] is False


def test_m22a_recommended_first_method_exists() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    method = summary["recommended_first_method"]
    assert method["name"] == "conservative_piecewise_linear_inverse_mapping"
    assert "no extrapolation" in method["description"]


def test_m22a_rejected_methods_list_exists() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    rejected_names = {item["name"] for item in summary["rejected_methods_for_now"]}
    assert "pchip_like_interpolation" in rejected_names
    assert "learned_regression_or_neural_model" in rejected_names


def test_m22a_feasibility_statuses_cover_required_refusals() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    statuses = set(summary["feasibility_statuses"])
    assert "infeasible_deadzone" in statuses
    assert "infeasible_out_of_range" in statuses
    assert "platform_not_calibrated" in statuses
    assert "surface_not_calibrated" in statuses


def test_no_compensator_module_exists() -> None:
    forbidden = [
        ROOT / "calibration_core/compensator.py",
        ROOT / "k1_measurement/compensator.py",
        ROOT / "platforms/booster_k1/compensator.py",
    ]
    assert not any(path.exists() for path in forbidden)


def test_no_inverse_response_model_module_exists() -> None:
    forbidden = [
        ROOT / "calibration_core/inverse_response_model.py",
        ROOT / "k1_measurement/inverse_response_model.py",
        ROOT / "platforms/booster_k1/inverse_response_model.py",
    ]
    assert not any(path.exists() for path in forbidden)


def test_no_command_remapping_cli_exists() -> None:
    forbidden_names = {
        "remap_velocity_command.py",
        "run_velocity_compensator.py",
        "apply_velocity_compensation.py",
        "run_k1_compensation.py",
    }
    script_names = {path.name for path in (ROOT / "scripts").glob("*.py")}
    assert forbidden_names.isdisjoint(script_names)


def test_measurement_module_closure_flags_remain_unchanged() -> None:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    assert status["measurement_module_v1_complete"] is True
    assert status["booster_k1_reference_ready"] is True
    assert status["measurement_contract_v1_ready"] is True
    assert status["velocity_compensation_ready"] is False
    assert status["unitree_go1_measurement_ready"] is False
    assert status["unitree_g1_measurement_ready"] is False
    assert status["cross_platform_empirical_validation_ready"] is False
