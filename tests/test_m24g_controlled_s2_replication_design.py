"""Tests for M24-G controlled S2 replication design."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/compensation_experiments"
PLAN_CSV = OUTPUT_DIR / "m24g_controlled_s2_replication_plan.csv"
PLAN_JSON = OUTPUT_DIR / "m24g_controlled_s2_replication_plan.json"
PLAN_MD = OUTPUT_DIR / "m24g_controlled_s2_replication_plan.md"
MANIFEST_JSON = OUTPUT_DIR / "m24g_controlled_replication_design_manifest.json"
MANIFEST_MD = OUTPUT_DIR / "m24g_controlled_replication_design_manifest.md"
SCHEMA_DOC = ROOT / "docs/m24g_controlled_replication_metadata_schema.md"
CLAIM_BOUNDARY = ROOT / "docs/m24g_claim_boundary.md"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"

REQUIRED_VELOCITIES = ["0.40", "0.45", "0.50", "0.55"]
REQUIRED_METADATA_FIELDS = [
    "session_id",
    "surface",
    "robot_id",
    "firmware_software_notes",
    "battery_level",
    "warm_up_status",
    "start_pose_label",
    "path_label",
    "operator_reset_confirmation",
    "trial_distance_path_clearance_confirmation",
    "command_velocity_mps",
    "desired_velocity_mps",
    "repeat_index",
    "extraction_window_method",
    "notes",
]


def test_controlled_plan_outputs_exist() -> None:
    assert PLAN_CSV.exists()
    assert PLAN_JSON.exists()
    assert PLAN_MD.exists()
    assert MANIFEST_JSON.exists()
    assert MANIFEST_MD.exists()


def test_controlled_plan_s2_only_direct_controlled_only() -> None:
    rows = _read_csv(PLAN_CSV)
    assert rows
    assert {row["surface"] for row in rows} == {"S2_marble_floor"}
    assert {row["condition"] for row in rows} == {"direct_refresh_controlled"}


def test_required_velocities_and_repeats_are_correct() -> None:
    rows = _read_csv(PLAN_CSV)
    commands = sorted({row["command_velocity_mps"] for row in rows})
    assert commands == REQUIRED_VELOCITIES
    counts = Counter(row["command_velocity_mps"] for row in rows)
    assert counts == {velocity: 5 for velocity in REQUIRED_VELOCITIES}
    assert len(rows) == 20


def test_no_compensated_rows_exist() -> None:
    rows = _read_csv(PLAN_CSV)
    assert {row["compensated_command"] for row in rows} == {"false"}
    assert "compensated" not in {row["condition"] for row in rows}
    assert all("no compensated commands" in row["notes"] for row in rows)


def test_metadata_schema_contains_required_fields() -> None:
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    for field in REQUIRED_METADATA_FIELDS:
        assert field in text
    assert "optional" in text.lower()
    assert "must not be fabricated" in text


def test_design_manifest_boundary_flags() -> None:
    data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert data["planned_surface"] == "S2_marble_floor"
    assert data["planned_condition"] == "direct_refresh_controlled"
    assert data["planned_velocities_mps"] == [0.4, 0.45, 0.5, 0.55]
    assert data["planned_repeats_per_velocity"] == 5
    assert data["planned_core_trial_count"] == 20
    assert data["physical_run_status"] == "not_run"
    assert data["profile_adoption_status"] == "not_adopted"
    assert data["deployment_ready"] is False
    assert data["go1_g1_blocked"] is True


def test_plan_summary_blocks_profile_adoption_and_deployment() -> None:
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    assert data["physical_run_status"] == "not_run"
    assert data["new_physical_data"] is False
    assert data["profile_adoption_status"] == "not_adopted"
    assert data["m24f_candidate_profile_adopted"] is False
    assert data["gold_profile_overwritten"] is False
    assert data["revised_compensator_status"] == "offline_only"
    assert data["compensation_validation_status"] == "blocked_pending_controlled_replication"
    assert data["deployment_ready"] is False
    assert data["go1_g1_blocked"] is True


def test_gold_profile_not_overwritten() -> None:
    before = _sha256(GOLD_PROFILE)
    after = _sha256(GOLD_PROFILE)
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    assert before == after
    assert data["gold_profile_overwritten"] is False


def test_claim_boundary_says_design_only() -> None:
    text = CLAIM_BOUNDARY.read_text(encoding="utf-8").lower()
    assert "design-only" in text
    assert "does not execute hardware" in text
    assert "does not create new physical measurements" in text
    assert "deployment_ready=false" in text
    assert "go1_g1_blocked=true" in text


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
