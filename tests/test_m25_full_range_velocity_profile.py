"""Tests for M25 full-range velocity profiling contract and planning."""
from __future__ import annotations

import csv
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from k1_measurement.full_range_velocity_profile import (
    M25Config,
    M25ValidationError,
    ValidSpeedDomain,
    audit_historical_rows,
    build_candidate_profile,
    plan_phase,
    validate_collected_session,
    validate_command_grid,
    validate_target_reachability,
)


ROOT = Path(__file__).resolve().parents[1]


def _config(*, safe_max: float | None = 1.0) -> M25Config:
    return M25Config(
        valid_speed_domain=ValidSpeedDomain(safe_command_speed_max=safe_max),
        random_seed=123,
    )


def test_valid_speed_domain_parsing_defaults_and_missing_safe_max() -> None:
    config = M25Config.from_mapping({"valid_speed_domain": {"valid_command_speed_min": 0.35}, "random_seed": 7})
    assert config.valid_speed_domain.valid_command_speed_min == 0.35
    assert config.valid_speed_domain.safe_command_speed_max is None
    errors = config.validate(require_safe_max=True)
    assert any(error["code"] == "safe_command_limit_not_configured" for error in errors)


def test_invalid_domain_order_is_rejected() -> None:
    domain = ValidSpeedDomain(valid_command_speed_min=1.0, safe_command_speed_max=0.9)
    assert domain.validate(require_safe_max=True)[0]["code"] == "invalid_domain_order"


def test_command_grid_validation_rejects_duplicates_nonmonotonic_and_outside_domain() -> None:
    domain = ValidSpeedDomain(valid_command_speed_min=0.35, safe_command_speed_max=1.0)
    errors = validate_command_grid([0.4, 0.4, 0.3], domain, require_safe_max=True)
    codes = {error["code"] for error in errors}
    assert {"duplicate_command_points", "non_monotonic_command_grid", "below_valid_speed_domain"} <= codes


def test_exploration_plan_excludes_points_outside_valid_domain() -> None:
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(valid_command_speed_min=0.55, safe_command_speed_max=0.9),
        exploration_command_points=[0.4, 0.5, 0.6, 0.7, 0.9, 1.0],
        formal_command_grid=[0.6, 0.8, 0.9],
        random_seed=10,
    )
    plan = plan_phase(config, "exploration")
    assert plan["executable"] is False
    assert any(error["code"] in {"below_valid_speed_domain", "above_safe_command_limit"} for error in plan["errors"])


def test_deterministic_randomization_with_fixed_seed() -> None:
    first = plan_phase(_config(), "exploration")
    second = plan_phase(_config(), "exploration")
    assert [row["trial_id"] for row in first["trials"]] == [row["trial_id"] for row in second["trials"]]


def test_exploration_and_formal_plan_generation() -> None:
    exploration = plan_phase(_config(), "exploration")
    formal = plan_phase(_config(), "formal")
    assert exploration["executable"] is True
    assert formal["executable"] is True
    assert exploration["trial_count"] == 12
    assert formal["trial_count"] == 30


def test_exploration_and_formal_plan_with_legacy_large_domain() -> None:
    """Generic planner supports larger domains for non-K1 configurations."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(
            valid_command_speed_min=0.35,
            safe_command_speed_max=1.0,
            high_priority_actual_speed_min=0.80,
            high_priority_actual_speed_max=1.00,
        ),
        exploration_command_points=[0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
        formal_command_grid=[0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00],
        random_seed=123,
    )
    exploration = plan_phase(config, "exploration")
    formal = plan_phase(config, "formal")
    assert exploration["executable"] is True
    assert formal["executable"] is True
    assert exploration["trial_count"] == 21
    assert formal["trial_count"] == 55


def test_formal_default_is_denser_around_high_priority_region() -> None:
    formal_points = _config().formal_command_grid
    high_priority = [p for p in formal_points if 0.50 <= p <= 0.60]
    lower = [p for p in formal_points if p < 0.50]
    assert len(high_priority) == 3
    assert len(lower) == 3
    assert min(round(b - a, 2) for a, b in zip(high_priority, high_priority[1:])) == 0.05
    assert max(round(b - a, 2) for a, b in zip(lower, lower[1:])) == 0.05


def test_candidate_profile_status_and_reachability_fields(tmp_path: Path) -> None:
    session = _write_rows(tmp_path / "session.csv", [
        {"trial_id": "t1", "command_speed": "0.4", "estimated_actual_speed": "0.36", "valid": "true"},
        {"trial_id": "t2", "command_speed": "0.4", "estimated_actual_speed": "0.38", "valid": "true"},
    ])
    profile = build_candidate_profile(session, _config())
    assert profile["profile_status"] == "candidate"
    assert profile["observed_actual_speed_min"] == 0.36
    assert profile["observed_actual_speed_max"] == 0.38
    with pytest.raises(M25ValidationError) as exc:
        validate_target_reachability(profile, 0.5)
    assert exc.value.code == "target_outside_reachable_actual_speed_range"


def test_historical_trial_filtering(tmp_path: Path) -> None:
    historical = _write_rows(tmp_path / "historical.csv", [
        {"trial_id": "low", "command_speed": "0.2", "estimated_actual_speed": "0.0"},
        {"trial_id": "ok", "command_speed": "0.4", "estimated_actual_speed": "0.35"},
        {"trial_id": "missing", "command_speed": "0.5", "estimated_actual_speed": ""},
    ])
    audit = audit_historical_rows([historical], ValidSpeedDomain(safe_command_speed_max=1.0))
    assert audit["valid_speed_rows_retained"] == 1
    reasons = audit["sessions"][0]["exclusion_reasons"]
    assert reasons["below_valid_speed_domain"] == 1
    assert reasons["missing_actual_speed"] == 1
    assert audit["deadzone_inference_performed"] is False


def test_session_validation_cli_success_and_failure(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text(
        "valid_speed_domain:\n  valid_command_speed_min: 0.35\n  safe_command_speed_max: 1.0\n"
        "random_seed: 5\nformal_command_grid: [0.4]\nexploration_command_points: [0.4]\n",
        encoding="utf-8",
    )
    ok = _write_rows(tmp_path / "ok.csv", [{"trial_id": "t1", "command_speed": "0.4", "estimated_actual_speed": "0.37", "valid": "true"}])
    bad = _write_rows(tmp_path / "bad.csv", [{"trial_id": "t1", "command_speed": "1.2", "estimated_actual_speed": "1.0", "valid": "true"}])
    good_result = subprocess.run(
        [sys.executable, "scripts/validate_m25_collected_session.py", "--config", str(config), "--session", str(ok)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    bad_result = subprocess.run(
        [sys.executable, "scripts/validate_m25_collected_session.py", "--config", str(config), "--session", str(bad)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert good_result.returncode == 0
    assert bad_result.returncode == 1
    assert "above_safe_command_limit" in bad_result.stderr


def test_config_and_profile_serialization_round_trip(tmp_path: Path) -> None:
    session = _write_rows(tmp_path / "session.csv", [{"trial_id": "t1", "command_speed": "0.4", "estimated_actual_speed": "0.36", "valid": "true"}])
    profile = build_candidate_profile(session, _config())
    encoded = json.dumps(profile)
    decoded = json.loads(encoded)
    assert decoded["schema_version"] == "m25_full_range_velocity_profile_v1"
    assert decoded["profile_status"] == "candidate"


def test_no_deadzone_or_yaw_compensation_import_in_active_m25_pipeline() -> None:
    module = importlib.import_module("k1_measurement.full_range_velocity_profile")
    text = Path(module.__file__).read_text(encoding="utf-8")
    assert "yaw_compensation" not in text
    assert "yaw_drift" not in text
    assert "infeasible_deadzone" not in text


def test_validate_collected_session_reports_contract_errors(tmp_path: Path) -> None:
    session = _write_rows(tmp_path / "session.csv", [{"trial_id": "t1", "command_speed": "0.2", "estimated_actual_speed": "0.1", "valid": "true"}])
    result = validate_collected_session(session, ValidSpeedDomain(safe_command_speed_max=1.0))
    assert result["valid"] is False
    assert "below_valid_speed_domain" in result["errors"][0]["message"]


# --- M25-S K1-specific tests ---


def test_k1_safe_speed_max_0_6_accepted() -> None:
    """Commands exactly at 0.6 m/s are accepted."""
    domain = ValidSpeedDomain(safe_command_speed_max=0.6)
    domain.check_command(0.6)  # must not raise


def test_k1_rejects_command_above_0_6() -> None:
    """Commands above 0.6 m/s are rejected."""
    domain = ValidSpeedDomain(safe_command_speed_max=0.6)
    with pytest.raises(M25ValidationError) as exc:
        domain.check_command(0.61)
    assert exc.value.code == "above_safe_command_limit"


def test_k1_rejects_command_0_7_and_above() -> None:
    """0.70, 0.80, 0.90, 1.00 are all rejected."""
    domain = ValidSpeedDomain(safe_command_speed_max=0.6)
    for speed in [0.70, 0.80, 0.90, 1.00]:
        with pytest.raises(M25ValidationError) as exc:
            domain.check_command(speed)
        assert exc.value.code == "above_safe_command_limit"


def test_k1_lower_applicability_boundary_0_35() -> None:
    """Commands below 0.35 m/s are rejected."""
    domain = ValidSpeedDomain(valid_command_speed_min=0.35, safe_command_speed_max=0.6)
    with pytest.raises(M25ValidationError) as exc:
        domain.check_command(0.34)
    assert exc.value.code == "below_valid_speed_domain"
    domain.check_command(0.35)  # must not raise


def test_k1_exploration_grid() -> None:
    """K1 exploration grid is [0.35, 0.40, 0.50, 0.60]."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(safe_command_speed_max=0.6),
        exploration_command_points=[0.35, 0.40, 0.50, 0.60],
        formal_command_grid=[0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
        random_seed=250625,
    )
    plan = plan_phase(config, "exploration")
    assert plan["executable"] is True
    assert plan["trial_count"] == 12
    assert plan["command_points_mps"] == [0.35, 0.40, 0.50, 0.60]
    assert all(p <= 0.6 for p in plan["command_points_mps"])


def test_k1_formal_grid_and_total() -> None:
    """K1 formal grid has 6 points × 5 repeats = 30 trials."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(safe_command_speed_max=0.6),
        exploration_command_points=[0.35, 0.40, 0.50, 0.60],
        formal_command_grid=[0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
        random_seed=250625,
    )
    plan = plan_phase(config, "formal")
    assert plan["executable"] is True
    assert plan["trial_count"] == 30
    assert plan["command_points_mps"] == [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    assert all(p <= 0.6 for p in plan["command_points_mps"])


def test_k1_no_command_above_0_6_in_plans() -> None:
    """All generated K1 trial commands are within [0.35, 0.60]."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(safe_command_speed_max=0.6),
        random_seed=250625,
    )
    for phase in ("exploration", "formal"):
        plan = plan_phase(config, phase)
        if plan["executable"]:
            for trial in plan["trials"]:
                assert 0.35 <= trial["command_speed_mps"] <= 0.6


def test_k1_high_priority_region_0_50_to_0_60() -> None:
    """High-priority region is 0.50–0.60 for K1 configuration."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(
            safe_command_speed_max=0.6,
            high_priority_actual_speed_min=0.50,
            high_priority_actual_speed_max=0.60,
        ),
        random_seed=250625,
    )
    plan = plan_phase(config, "formal")
    region = plan.get("high_priority_actual_speed_region", [])
    assert region == [0.50, 0.60]
    # Upper region points (0.50, 0.55, 0.60) are the denser part
    upper = [p for p in plan["command_points_mps"] if p >= 0.50]
    assert len(upper) == 3


def test_k1_deterministic_randomized_ordering() -> None:
    """K1 exploration plan has deterministic randomized ordering."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(safe_command_speed_max=0.6),
        random_seed=250625,
    )
    plan1 = plan_phase(config, "exploration")
    plan2 = plan_phase(config, "exploration")
    assert [t["trial_id"] for t in plan1["trials"]] == [t["trial_id"] for t in plan2["trials"]]
    # Verify randomization is not just sorted order
    speeds = [t["command_speed_mps"] for t in plan1["trials"]]
    assert speeds != sorted(speeds)


def test_generic_planner_supports_larger_domains() -> None:
    """Generic planner still supports larger speed domains for other configs."""
    config = M25Config(
        valid_speed_domain=ValidSpeedDomain(
            valid_command_speed_min=0.35,
            safe_command_speed_max=1.0,
            high_priority_actual_speed_min=0.80,
            high_priority_actual_speed_max=1.00,
        ),
        exploration_command_points=[0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
        formal_command_grid=[0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00],
        random_seed=123,
    )
    plan = plan_phase(config, "exploration")
    assert plan["executable"] is True
    assert plan["trial_count"] == 21
    assert 1.0 in plan["command_points_mps"]


def _write_rows(path: Path, rows: list[dict[str, str]]) -> Path:
    fields = sorted({field for row in rows for field in row})
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path
