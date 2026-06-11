from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from calibration_core.measurement_schema import validate_trial_measurement
from calibration_core.platform_registry import get_platform, get_platform_registry
from calibration_core.profile_loader import load_k1_gold_profile
from calibration_core.trial_scheduler import TrialScheduler
from platforms.unitree_g1 import UnitreeG1CommandAdapter, UnitreeG1ScaffoldExtractor
from platforms.unitree_go1 import UnitreeGo1CommandAdapter, UnitreeGo1ScaffoldExtractor
from scripts.generate_cross_platform_trial_plan import build_plan
from scripts.validate_calibration_profile import validate_profile

ROOT = Path(__file__).resolve().parents[1]


def test_measurement_schema_accepts_numeric_trial_record() -> None:
    record = {
        "robot_id": "Booster_K1",
        "robot_model": "Booster K1",
        "platform": "booster_k1",
        "trial_id": "K1_S1_B1_U020_R1",
        "session_id": "session",
        "environment_id": "S1_lab_hard_floor",
        "surface_type": "lab_hard_floor",
        "command_velocity": "0.2",
        "measured_actual_velocity": "0.18",
        "yaw_drift_statistic": "1.5",
        "measurement_source": "ros2_odometer_state",
        "measurement_method": "forward_projection",
        "extraction_status": "ok",
        "confidence": "high",
        "state_log_path": "data/log.csv",
        "timestamp": "2026-06-11T00:00:00",
    }
    assert validate_trial_measurement(record) == []


def test_measurement_schema_reports_missing_required_field() -> None:
    assert "measured_actual_velocity" in validate_trial_measurement({"trial_id": "missing_fields"})


def test_trial_scheduler_is_deterministic_and_preserves_blocks() -> None:
    trials = TrialScheduler().build_trials(
        ["surface_a"],
        [0.2, 0.4],
        repeats=2,
        block_order=[[0.4, 0.2], [0.2, 0.4]],
        platform="booster_k1",
        prefix="K1",
    )
    assert [trial.trial_id for trial in trials] == [
        "K1_surface_a_B1_U040_R1",
        "K1_surface_a_B1_U020_R1",
        "K1_surface_a_B2_U020_R2",
        "K1_surface_a_B2_U040_R2",
    ]


def test_platform_registry_marks_only_booster_k1_as_validated_reference() -> None:
    registry = get_platform_registry()
    assert set(registry) == {"booster_k1", "unitree_g1", "unitree_go1"}
    assert registry["booster_k1"].hardware_validated_reference is True
    assert registry["booster_k1"].validation_status == "hardware_validated_reference"
    assert registry["unitree_g1"].hardware_validated_reference is False
    assert registry["unitree_go1"].hardware_validated_reference is False


def test_k1_gold_profile_loader_and_validation_preserve_region_labels() -> None:
    profile = load_k1_gold_profile()
    assert profile["robot_id"] == "Booster_K1"
    assert len(profile["tested_surfaces"]) == 3
    assert len(profile["speed_list"]) == 8
    assert "deadzone" in set(profile["region_labels"].values())
    summary = validate_profile(ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
    assert summary["valid"] is True
    assert summary["aggregate_rows"] == 24
    assert summary["region_label_count"] == 24
    assert summary["empirical_analysis_generated"] is False


def test_unitree_scaffolds_cannot_claim_validation_or_fake_measurements(tmp_path: Path) -> None:
    for platform_id, adapter_cls, extractor_cls in [
        ("unitree_g1", UnitreeG1CommandAdapter, UnitreeG1ScaffoldExtractor),
        ("unitree_go1", UnitreeGo1CommandAdapter, UnitreeGo1ScaffoldExtractor),
    ]:
        entry = get_platform(platform_id)
        assert entry.validation_status == "scaffold_only"
        assert entry.hardware_validated_reference is False
        with pytest.raises(NotImplementedError):
            adapter_cls().send_velocity(0.2)
        with pytest.raises(NotImplementedError):
            extractor_cls().extract_trial(tmp_path / "missing.csv")


def test_list_platforms_cli_output() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/list_calibration_platforms.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "booster_k1" in result.stdout
    assert "unitree_g1" in result.stdout
    assert "hardware_validated_reference=true" in result.stdout
    assert "hardware_validated_reference=false" in result.stdout


def test_cross_platform_trial_plan_generation_for_scaffold_is_plan_only(tmp_path: Path) -> None:
    rows = build_plan("unitree_g1", ["mat"], [0.2, 0.4], repeats=2)
    assert len(rows) == 4
    assert all(row["plan_only"] is True for row in rows)
    assert all(row["hardware_validated_reference"] is False for row in rows)
    output = tmp_path / "plan.csv"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_cross_platform_trial_plan.py",
            "--platform",
            "booster_k1",
            "--surfaces",
            "S1_lab_hard_floor",
            "--speeds",
            "0.2,0.4",
            "--repeats",
            "1",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "trial_count: 2" in result.stdout
    with output.open(newline="", encoding="utf-8") as f:
        written = list(csv.DictReader(f))
    assert [row["trial_id"] for row in written] == [
        "K1_S1_lab_hard_floor_B1_U020_R1",
        "K1_S1_lab_hard_floor_B1_U040_R1",
    ]


def test_profile_validation_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_calibration_profile.py",
            "--profile",
            "outputs/real_k1_validation_m19/k1_gold_profile_v1.json",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)
    assert summary["valid"] is True
    assert summary["empirical_analysis_generated"] is False
