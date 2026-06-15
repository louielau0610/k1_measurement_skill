"""Tests for M25-R safe-speed resolution and real-data collection readiness."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from k1_measurement.m25_real_collection_preflight import (
    evaluate_exploration_gate,
    evaluate_preflight,
    validate_safe_speed_confirmation,
    write_collection_package,
)
from k1_measurement.full_range_velocity_profile import ValidSpeedDomain


ROOT = Path(__file__).resolve().parents[1]


def test_operator_confirmation_schema_blocks_unresolved_values() -> None:
    result = validate_safe_speed_confirmation(ROOT / "configs/m25_k1_safe_speed_operator_confirmation_template.yaml")
    assert result["valid"] is False
    codes = {error["code"] for error in result["errors"]}
    assert "safe_command_limit_not_configured" in codes
    assert "unresolved_placeholder" in codes


def test_operator_confirmation_rejects_unsupported_evidence_type(tmp_path: Path) -> None:
    confirmation = _write_confirmation(tmp_path, evidence_type="forum_post")
    result = validate_safe_speed_confirmation(confirmation)
    assert result["valid"] is False
    assert any(error["code"] == "unsupported_evidence_type" for error in result["errors"])


def test_preflight_blocked_when_safe_max_unresolved() -> None:
    result = evaluate_preflight(ROOT / "configs/m25_real_collection_preflight_template.yaml")
    assert result["ready"] is False
    codes = {error["code"] for error in result["blocked_reasons"]}
    assert "safe_command_limit_not_configured" in codes
    assert result["resolved_speed_domain"]["safe_command_speed_max"] is None


def test_preflight_ready_with_fixture_only_safe_max(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=1.0)
    result = evaluate_preflight(preflight)
    assert result["ready"] is True
    assert result["exploration_trial_count"] == 21
    assert result["formal_trial_count"] == 55
    assert len(result["config_hash"]) == 64
    assert len(result["plan_hashes"]["exploration"]) == 64


def test_preflight_rejects_command_above_safe_max(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=0.9)
    result = evaluate_preflight(preflight)
    assert result["ready"] is False
    assert any(error["code"] == "above_safe_command_limit" for error in result["blocked_reasons"])


def test_output_directory_validation(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=1.0, logger_output_dir=str(tmp_path / "logs"))
    result = evaluate_preflight(preflight)
    assert result["ready"] is True
    assert (tmp_path / "logs").exists()


def test_unresolved_placeholders_block_preflight(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=1.0, control_mode="TBD")
    result = evaluate_preflight(preflight)
    assert result["ready"] is False
    assert any(error["field"] == "control_mode" for error in result["blocked_reasons"])


def test_collection_packages_and_formal_gate(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=1.0, exploration_review_complete=False)
    exploration, exploration_json, exploration_md = write_collection_package(preflight, "exploration", tmp_path)
    formal, formal_json, formal_md = write_collection_package(preflight, "formal", tmp_path)
    assert exploration["ready"] is True
    assert formal["ready"] is False
    assert any(error["code"] == "formal_blocked_before_exploration_review" for error in formal["blocked_reasons"])
    assert exploration_json.exists() and exploration_md.exists()
    assert formal_json.exists() and formal_md.exists()


def test_exploration_gate_ready_and_missing_high_priority(tmp_path: Path) -> None:
    ready_rows = []
    for command, actual in [(0.4, 0.36), (0.8, 0.82), (0.9, 0.91)]:
        for repeat in range(3):
            ready_rows.append(_gate_row(command, actual + repeat * 0.001))
    ready_csv = _write_rows(tmp_path / "ready.csv", ready_rows)
    ready = evaluate_exploration_gate(ready_csv, ValidSpeedDomain(safe_command_speed_max=1.0))
    assert ready["ready"] is True
    assert ready["decisions"] == ["ready_for_formal_collection"]
    assert ready["m26_model_fitted"] is False

    low_csv = _write_rows(tmp_path / "low.csv", [_gate_row(0.4, 0.35), _gate_row(0.4, 0.36), _gate_row(0.4, 0.37)])
    low = evaluate_exploration_gate(low_csv, ValidSpeedDomain(safe_command_speed_max=1.0))
    assert "high_priority_region_not_covered" in low["decisions"]


def test_exploration_gate_safe_limit_prevents_requested_coverage(tmp_path: Path) -> None:
    rows = [_gate_row(0.7, 0.65), _gate_row(0.7, 0.66), _gate_row(0.7, 0.67)]
    result = evaluate_exploration_gate(_write_rows(tmp_path / "limited.csv", rows), ValidSpeedDomain(safe_command_speed_max=0.7))
    assert "safe_limit_prevents_requested_coverage" in result["decisions"]


def test_cli_exit_codes(tmp_path: Path) -> None:
    blocked = subprocess.run(
        [sys.executable, "scripts/validate_m25_safe_speed_confirmation.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    preflight = _write_preflight(tmp_path, safe_max=1.0)
    ready = subprocess.run(
        [sys.executable, "scripts/validate_m25_real_collection_preflight.py", "--config", str(preflight)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert blocked.returncode == 1
    assert ready.returncode == 0


def test_generated_output_ignore_rules_and_raw_data_policy() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/measurement_sessions/" in text
    assert "m25_resolved_safe_config_for_validation.yaml" in text


def test_serialization_round_trip_and_no_final_m26_model(tmp_path: Path) -> None:
    preflight = _write_preflight(tmp_path, safe_max=1.0)
    result = evaluate_preflight(preflight)
    decoded = json.loads(json.dumps(result))
    assert decoded["ready"] is True
    gate_csv = _write_rows(tmp_path / "gate.csv", [_gate_row(0.4, 0.35), _gate_row(0.4, 0.36), _gate_row(0.4, 0.37)])
    gate = evaluate_exploration_gate(gate_csv, ValidSpeedDomain(safe_command_speed_max=1.0))
    assert gate["m26_model_fitted"] is False


def _write_confirmation(tmp_path: Path, *, safe_max: float = 1.0, evidence_type: str = "operator_confirmation") -> Path:
    path = tmp_path / "confirmation.yaml"
    path.write_text(
        "\n".join([
            "robot_id: k1_fixture",
            "control_mode: velocity",
            "gait_mode: trot",
            f"safe_command_speed_max: {safe_max}",
            f"evidence_type: {evidence_type}",
            "evidence_reference: fixture-only test value",
            "confirmed_by: test_operator",
            "confirmed_at: 2026-06-15T00:00:00Z",
            "notes: fixture only, not real safe-speed evidence",
        ]) + "\n",
        encoding="utf-8",
    )
    return path


def _write_preflight(
    tmp_path: Path,
    *,
    safe_max: float,
    control_mode: str = "velocity",
    logger_output_dir: str | None = None,
    exploration_review_complete: bool = True,
) -> Path:
    confirmation = _write_confirmation(tmp_path, safe_max=safe_max)
    preflight = tmp_path / "preflight.yaml"
    out = logger_output_dir or str(tmp_path / "logs")
    preflight.write_text(
        "\n".join([
            "m25_config_path: configs/m25_full_range_velocity_profile_template.yaml",
            f"safe_speed_confirmation_path: {confirmation}",
            "robot_id: k1_fixture",
            "surface_id: S2_marble_floor",
            f"control_mode: {control_mode}",
            "gait_mode: trot",
            "require_control_mode: true",
            "require_gait_mode: true",
            "trial_duration_sec: 8.0",
            "warmup_duration_sec: 1.0",
            "steady_window_start_sec: 2.0",
            "steady_window_end_sec: 6.0",
            f"logger_output_dir: {out}",
            "required_input_mappings: []",
            "execution_safeguards:",
            "  dry_run_default: true",
            "  require_execute_flag: true",
            "  require_operator_confirmation: true",
            "  emergency_stop_briefing_required: true",
            f"exploration_review_complete: {str(exploration_review_complete).lower()}",
        ]) + "\n",
        encoding="utf-8",
    )
    return preflight


def _gate_row(command: float, actual: float) -> dict[str, str]:
    return {
        "trial_id": f"cmd_{command}_{actual}",
        "command_speed": f"{command}",
        "estimated_actual_speed": f"{actual}",
        "steady_window_duration": "4.0",
        "fit_quality": "0.95",
        "valid": "true",
    }


def _write_rows(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path
