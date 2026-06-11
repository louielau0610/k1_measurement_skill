from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from calibration_core.compensation_models import CompensationRequest, ResponseCell
from calibration_core.velocity_compensation import (
    DEFAULT_CONTRACT_CSV,
    DEFAULT_PROFILE,
    build_monotonic_segments,
    compensate_velocity,
    load_cells_from_contract_csv,
    load_cells_from_gold_profile,
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "outputs/compensation_research/offline_velocity_compensator_m22c_summary.json"
AUDIT = ROOT / "outputs/compensation_research/m22c_novelty_positioning_audit.json"


def request(**overrides: object) -> CompensationRequest:
    values = {
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "surface_type": "S1_lab_hard_floor",
        "desired_actual_velocity_mps": 0.4,
        "response_profile_path": ROOT / DEFAULT_PROFILE,
        "contract_csv_path": ROOT / DEFAULT_CONTRACT_CSV,
        "risk_policy": "conservative",
        "extrapolation_policy": "reject",
        "minimum_confidence": 0.5,
        "operator_notes": "test",
    }
    values.update(overrides)
    return CompensationRequest(**values)


def test_request_validation_negative_velocity_returns_invalid_input() -> None:
    decision = compensate_velocity(request(desired_actual_velocity_mps=-0.1))
    assert decision.feasibility_status == "invalid_input"
    assert decision.offline_only is True
    assert decision.deployment_ready is False


def test_gold_profile_loading() -> None:
    cells = load_cells_from_gold_profile(ROOT / DEFAULT_PROFILE)
    assert len(cells) == 24
    assert {cell.platform for cell in cells} == {"booster_k1"}
    assert "S1_lab_hard_floor" in {cell.surface_type for cell in cells}


def test_contract_csv_loading() -> None:
    cells = load_cells_from_contract_csv(ROOT / DEFAULT_CONTRACT_CSV, profile_path=ROOT / DEFAULT_PROFILE)
    assert len(cells) == 24
    assert "lab_hard_floor" in {cell.surface_type for cell in cells}
    assert all(cell.n == 3 for cell in cells)


def test_unsupported_platform_returns_platform_not_calibrated() -> None:
    decision = compensate_velocity(request(platform="unitree_go1", surface_type="lab_hard_floor"))
    assert decision.feasibility_status == "platform_not_calibrated"
    assert "scaffold-only" in decision.reason


def test_unsupported_surface_returns_surface_not_calibrated() -> None:
    decision = compensate_velocity(request(surface_type="unknown_surface"))
    assert decision.feasibility_status == "surface_not_calibrated"


def test_deadzone_desired_velocity_returns_infeasible_deadzone() -> None:
    decision = compensate_velocity(request(desired_actual_velocity_mps=0.1))
    assert decision.feasibility_status == "infeasible_deadzone"


def test_out_of_range_desired_velocity_returns_infeasible_out_of_range() -> None:
    decision = compensate_velocity(
        request(
            surface_type="S2_marble_floor",
            desired_actual_velocity_mps=2.0,
            risk_policy="permissive",
            minimum_confidence=0.0,
        )
    )
    assert decision.feasibility_status == "infeasible_out_of_range"


def test_valid_desired_velocity_can_return_risky_offline_decision() -> None:
    decision = compensate_velocity(
        request(
            surface_type="S2_marble_floor",
            desired_actual_velocity_mps=0.55,
            risk_policy="permissive",
            minimum_confidence=0.0,
        )
    )
    assert decision.feasibility_status in {"ok", "feasible_but_risky"}
    assert decision.recommended_command_velocity_mps is not None
    assert decision.offline_only is True
    assert decision.physical_validation_status == "not_started"
    assert decision.deployment_ready is False


def test_no_extrapolation_by_default() -> None:
    decision = compensate_velocity(
        request(
            surface_type="S2_marble_floor",
            desired_actual_velocity_mps=1.2,
            risk_policy="permissive",
            minimum_confidence=0.0,
        )
    )
    assert decision.feasibility_status == "infeasible_out_of_range"
    assert decision.recommended_command_velocity_mps is None


def test_risk_policy_filtering_is_stricter_under_conservative() -> None:
    conservative = compensate_velocity(request(surface_type="S2_marble_floor", desired_actual_velocity_mps=0.55))
    permissive = compensate_velocity(
        request(
            surface_type="S2_marble_floor",
            desired_actual_velocity_mps=0.55,
            risk_policy="permissive",
            minimum_confidence=0.0,
        )
    )
    assert conservative.feasibility_status in {"insufficient_evidence", "infeasible_deadzone"}
    assert permissive.feasibility_status == "feasible_but_risky"


def test_monotonic_segment_construction_splits_decreases() -> None:
    cells = [
        _cell(0.1, 0.1),
        _cell(0.2, 0.2),
        _cell(0.3, 0.15),
        _cell(0.4, 0.3),
    ]
    segments = build_monotonic_segments(cells)
    assert [len(segment.cells) for segment in segments] == [2, 2]


def test_non_monotonic_ambiguous_handling(tmp_path: Path) -> None:
    profile = {
        "robot_id": "Booster_K1",
        "per_surface_response_statistics": [
            _profile_row("ambiguous_surface", 0.1, 0.1),
            _profile_row("ambiguous_surface", 0.2, 0.3),
            _profile_row("ambiguous_surface", 0.3, 0.1),
            _profile_row("ambiguous_surface", 0.4, 0.3),
        ],
    }
    profile_path = tmp_path / "ambiguous_profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    decision = compensate_velocity(
        request(
            surface_type="ambiguous_surface",
            desired_actual_velocity_mps=0.2,
            response_profile_path=profile_path,
            contract_csv_path=None,
            risk_policy="permissive",
            minimum_confidence=0.0,
        )
    )
    assert decision.feasibility_status == "non_monotonic_ambiguous"


def test_cli_json_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/offline_compensate_velocity.py",
            "--platform",
            "unitree_g1",
            "--surface",
            "lab_hard_floor",
            "--desired-velocity",
            "0.4",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    decision = json.loads(result.stdout)
    assert decision["feasibility_status"] == "platform_not_calibrated"
    assert decision["offline_only"] is True


def test_batch_sweep_output(tmp_path: Path) -> None:
    prefix = tmp_path / "sweep"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/batch_offline_compensation_sweep.py",
            "--platform",
            "booster_k1",
            "--surface",
            "S1_lab_hard_floor",
            "--output-prefix",
            str(prefix),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["offline_prototype_only"] is True
    assert prefix.with_suffix(".csv").exists()
    assert prefix.with_suffix(".json").exists()
    assert prefix.with_suffix(".md").exists()


def test_summary_flags() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["implementation_status"] == "offline_prototype_complete"
    assert summary["deployment_ready"] is False
    assert summary["compensation_ready"] is False
    assert summary["physical_validation_status"] == "not_started"


def test_novelty_audit_exists_and_does_not_overclaim() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["current_novelty_status"] == "engineering_novelty_plausible_but_requires_K1_physical_validation"
    assert audit["paper_claim_level"] == "idea_and_system_design_only"
    assert audit["physical_validation"] == "not_started"
    assert audit["deployment_ready"] is False
    assert "generic feedforward compensation" in audit["not_novel_by_itself"]


def test_no_hardware_execution_or_validation_claims() -> None:
    forbidden_scripts = {
        "run_k1_compensation.py",
        "execute_compensated_velocity.py",
        "start_compensation_node.py",
    }
    scripts = {path.name for path in (ROOT / "scripts").glob("*.py")}
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert forbidden_scripts.isdisjoint(scripts)
    assert summary["physical_validation_status"] == "not_started"
    assert summary["deployment_ready"] is False
    assert summary["scaffold_only_platforms"] == ["unitree_go1", "unitree_g1"]


def _cell(command: float, actual: float) -> ResponseCell:
    return ResponseCell(
        platform="booster_k1",
        robot_model="Booster K1",
        surface_type="synthetic",
        command_velocity_mps=command,
        mean_actual_velocity_mps=actual,
        n=3,
        std_actual_velocity_mps=0.0,
        mean_yaw_drift_deg=0.0,
        response_uncertainty=0.0,
        no_motion_ratio=0.0,
        region_label="reliable",
        risk_score=0.0,
        confidence=1.0,
    )


def _profile_row(surface: str, command: float, actual: float) -> dict[str, object]:
    return {
        "surface_id": surface,
        "command_velocity": command,
        "n": 3,
        "mean_actual_velocity": actual,
        "std_actual_velocity": 0.0,
        "no_motion_ratio": 0.0,
        "mean_yaw_drift_deg": 0.0,
        "response_uncertainty": 0.0,
        "region_label": "reliable",
        "risk_score": 0.0,
    }
