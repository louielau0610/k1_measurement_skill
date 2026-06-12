"""Tests for M24-A S2 current-condition profile refresh design."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
PLAN_CSV = OUTPUT_DIR / "m24a_s2_profile_refresh_plan.csv"
PLAN_JSON = OUTPUT_DIR / "m24a_s2_profile_refresh_plan.json"
PLAN_MD = OUTPUT_DIR / "m24a_s2_profile_refresh_plan.md"
DESIGN_DOC = ROOT / "docs/m24a_s2_profile_refresh_design.md"
RESULT_SCHEMA = ROOT / "docs/m24a_s2_profile_refresh_result_schema.md"
ANALYSIS_PLAN = ROOT / "docs/m24a_s2_profile_refresh_analysis_plan.md"
CLAIM_BOUNDARY = ROOT / "docs/m24a_profile_refresh_claim_boundary.md"
PROJECT_STATUS = ROOT / "PROJECT_STATUS.md"

EXPECTED_VELOCITIES = ["0.35", "0.40", "0.45", "0.50", "0.55", "0.60"]
REQUIRED_SCHEMA_FIELDS = [
    "trial_id",
    "refresh_group_id",
    "surface",
    "command_velocity_mps",
    "desired_velocity_mps",
    "measured_actual_velocity_mps",
    "tracking_error_mps",
    "yaw_drift_deg",
    "imu_yaw_drift_deg",
    "extraction_status",
    "invalid_reason",
    "state_log_path",
    "physical_run_status",
    "notes",
]


def _rows() -> list[dict[str, str]]:
    with PLAN_CSV.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_refresh_plan_csv_exists() -> None:
    assert PLAN_CSV.exists()
    assert PLAN_JSON.exists()
    assert PLAN_MD.exists()
    assert DESIGN_DOC.exists()


def test_refresh_plan_includes_s2_only() -> None:
    rows = _rows()
    assert rows
    assert {row["surface"] for row in rows} == {"S2_marble_floor"}


def test_refresh_plan_direct_refresh_condition_only() -> None:
    rows = _rows()
    assert {row["condition"] for row in rows} == {"direct_refresh"}
    assert "compensated" not in {row["condition"] for row in rows}


def test_command_velocities_are_present() -> None:
    rows = _rows()
    commands = sorted({row["command_velocity_mps"] for row in rows})
    assert commands == EXPECTED_VELOCITIES
    assert sorted({row["desired_velocity_mps"] for row in rows}) == EXPECTED_VELOCITIES


def test_repeats_are_correct() -> None:
    rows = _rows()
    counts = Counter(row["command_velocity_mps"] for row in rows)
    assert counts == {velocity: 5 for velocity in EXPECTED_VELOCITIES}
    assert len(rows) == 30
    assert {row["physical_run_status"] for row in rows} == {"planned"}


def test_result_schema_contains_required_fields() -> None:
    text = RESULT_SCHEMA.read_text(encoding="utf-8")
    for field in REQUIRED_SCHEMA_FIELDS:
        assert field in text


def test_analysis_plan_includes_old_vs_new_profile_comparison() -> None:
    text = ANALYSIS_PLAN.read_text(encoding="utf-8")
    assert "old M19C S2 profile" in text
    assert "new M24 refresh" in text
    assert "old-vs-new profile comparison" in text
    assert "k1_s2_current_profile_v2" in text


def test_claim_boundary_says_no_physical_run() -> None:
    text = CLAIM_BOUNDARY.read_text(encoding="utf-8").lower()
    assert "design only" in text
    assert "no hardware has been run" in text
    assert "no profile has been refreshed yet" in text


def test_deployment_ready_remains_false() -> None:
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    assert data["deployment_ready"] is False
    assert data["hardware_execution"] is False
    assert data["physical_profile_refresh_status"] == "not_run"
    assert data["gold_profile_overwritten"] is False


def test_go1_g1_remain_blocked() -> None:
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    status = PROJECT_STATUS.read_text(encoding="utf-8")
    assert data["go1_g1_blocked"] is True
    assert "go1_g1_blocked=true" in status
    assert "GO1/G1 work is started" in CLAIM_BOUNDARY.read_text(encoding="utf-8")


def test_profile_mismatch_metrics_documented() -> None:
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    metrics = data["profile_mismatch_metrics"]
    assert metrics["profile_mismatch_threshold_mps"] == 0.03
    assert "old_m19c_mean_actual_velocity_mps" in metrics
    assert "new_refresh_mean_actual_velocity_mps" in metrics
    assert "profile_mismatch_flag" in metrics
