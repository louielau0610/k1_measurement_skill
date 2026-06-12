"""Tests for M24-B S2 profile refresh execution pack."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_m24b_s2_profile_refresh_trials.py"
LOGGER = ROOT / "scripts/log_m24b_s2_profile_refresh_trial.py"
EXTRACTOR = ROOT / "scripts/extract_m24b_s2_profile_refresh_trials.py"
QC = ROOT / "scripts/qc_m24b_s2_profile_refresh_session.py"
MANIFEST_JSON = ROOT / "outputs/compensation_experiments/m24b_execution_pack_manifest.json"
MANIFEST_MD = ROOT / "outputs/compensation_experiments/m24b_execution_pack_manifest.md"
TRANSFER_DOC = ROOT / "docs/m24b_robot_transfer_and_run_commands.md"
PROTOCOL_DOC = ROOT / "docs/m24b_s2_profile_refresh_execution_protocol.md"
GOLD_PROFILE = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"


spec = importlib.util.spec_from_file_location("run_m24b", RUNNER)
run_m24b = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_m24b)


def test_runner_rejects_non_direct_refresh_conditions(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path / "bad_condition.csv", condition="compensated")
    rc = run_m24b.main(["--trial-plan", str(plan), "--surface", "S2_marble_floor"])
    assert rc == 1


def test_runner_rejects_non_s2_surfaces(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path / "bad_surface.csv", surface="S1_lab_floor")
    rc = run_m24b.main(["--trial-plan", str(plan), "--surface", "S2_marble_floor"])
    assert rc == 1


def test_runner_dry_run_does_not_execute_hardware(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path / "ok.csv")
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--trial-plan",
            str(plan),
            "--surface",
            "S2_marble_floor",
            "--base-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert "No hardware was moved" in result.stdout
    assert not any(tmp_path.glob("*/session_metadata.json"))


def test_extractor_creates_required_output_schema_using_fixture_logs(tmp_path: Path) -> None:
    session = tmp_path / "m24b_fixture"
    state_logs = session / "state_logs"
    state_logs.mkdir(parents=True)
    _write_metadata(session)
    trial = _trial("M24A_S2_marble_floor_V040_R1", "M24A_S2_marble_floor_V040", "0.40")
    _write_records(session, [trial])
    subprocess.run(
        [
            sys.executable,
            str(LOGGER),
            "--trial-id",
            trial["trial_id"],
            "--refresh-group-id",
            trial["refresh_group_id"],
            "--condition",
            "direct_refresh",
            "--desired-velocity",
            "0.40",
            "--command-velocity",
            "0.40",
            "--output-dir",
            str(state_logs),
            "--mock",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    result = subprocess.run(
        [sys.executable, str(EXTRACTOR), "--session-dir", str(session)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    rows = _read_csv(session / "extracted_results.csv")
    assert len(rows) == 1
    required = [
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
    for field in required:
        assert field in rows[0]
    assert rows[0]["extraction_status"] == "ok"


def test_qc_detects_30_trials_6_groups_and_5_repeats(tmp_path: Path) -> None:
    session = _write_complete_qc_session(tmp_path)
    result = subprocess.run(
        [sys.executable, str(QC), "--session-dir", str(session)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    summary = json.loads((session / "qc_summary.json").read_text(encoding="utf-8"))
    assert summary["executed_trial_count"] == 30
    assert summary["velocity_group_count"] == 6
    assert summary["expected_repeats_per_velocity"] == 5
    assert summary["overall_pass"] is True


def test_qc_rejects_compensated_conditions(tmp_path: Path) -> None:
    session = _write_complete_qc_session(tmp_path)
    rows = _read_csv(session / "trial_records.csv")
    rows[0]["condition"] = "compensated"
    _write_csv(session / "trial_records.csv", rows, list(rows[0].keys()))
    result = subprocess.run(
        [sys.executable, str(QC), "--session-dir", str(session)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    summary = json.loads((session / "qc_summary.json").read_text(encoding="utf-8"))
    assert "compensated_condition_present" in summary["errors"]


def test_manifest_exists_and_says_not_run() -> None:
    assert MANIFEST_JSON.exists()
    assert MANIFEST_MD.exists()
    data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert data["physical_run_status"] == "not_run"
    assert data["profile_update_status"] == "not_updated"
    assert data["deployment_ready"] is False
    assert data["go1_g1_blocked"] is True


def test_docs_include_robot_transfer_commands() -> None:
    text = TRANSFER_DOC.read_text(encoding="utf-8")
    assert "scp" in text
    assert "source /opt/booster/BoosterRos2Interface/install/setup.bash" in text
    assert "--execute" in text
    assert "m24b_s2_profile_refresh_YYYYMMDD_HHMMSS" in text
    assert PROTOCOL_DOC.exists()


def test_no_k1_gold_profile_overwrite_and_boundaries() -> None:
    data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert GOLD_PROFILE.exists()
    assert data["claim_boundary"]["k1_gold_profile_overwritten"] is False
    assert data["claim_boundary"]["compensation_improvement_claimed"] is False
    assert data["claim_boundary"]["deployment_ready"] is False
    assert data["claim_boundary"]["go1_g1_validation"] is False


def test_split_process_import_boundaries() -> None:
    runner_lines = RUNNER.read_text(encoding="utf-8").splitlines()
    logger_text = LOGGER.read_text(encoding="utf-8")
    assert not _has_import(runner_lines, "rclpy")
    assert not _has_import(runner_lines, "B1LocoClient")
    assert "B1LocoClient" not in logger_text
    assert "ChannelFactory" not in logger_text


def _write_plan(path: Path, *, surface: str = "S2_marble_floor", condition: str = "direct_refresh") -> Path:
    fields = [
        "trial_id",
        "surface",
        "command_velocity_mps",
        "desired_velocity_mps",
        "condition",
        "repeat_index",
        "refresh_group_id",
        "physical_run_status",
        "notes",
    ]
    row = _trial("M24A_S2_marble_floor_V040_R1", "M24A_S2_marble_floor_V040", "0.40")
    row["surface"] = surface
    row["condition"] = condition
    _write_csv(path, [row], fields)
    return path


def _write_complete_qc_session(tmp_path: Path) -> Path:
    session = tmp_path / "m24b_complete"
    session.mkdir()
    _write_metadata(session)
    velocities = ["0.35", "0.40", "0.45", "0.50", "0.55", "0.60"]
    records = []
    extracted = []
    for velocity in velocities:
        group = f"M24A_S2_marble_floor_V{int(float(velocity) * 100):03d}"
        for repeat in range(1, 6):
            trial_id = f"{group}_R{repeat}"
            record = _trial(trial_id, group, velocity)
            records.append(record)
            extracted.append({
                "trial_id": trial_id,
                "refresh_group_id": group,
                "surface": "S2_marble_floor",
                "command_velocity_mps": velocity,
                "desired_velocity_mps": velocity,
                "measured_actual_velocity_mps": str(float(velocity) - 0.01),
                "tracking_error_mps": "-0.01",
                "yaw_drift_deg": "0.2",
                "imu_yaw_drift_deg": "0.2",
                "extraction_status": "ok",
                "invalid_reason": "",
                "state_log_path": f"state_logs/{trial_id}.csv",
                "physical_run_status": "executed",
                "notes": "test fixture",
            })
    _write_records(session, records)
    _write_csv(session / "extracted_results.csv", extracted, list(extracted[0].keys()))
    return session


def _write_metadata(session: Path) -> None:
    (session / "session_metadata.json").write_text(json.dumps({
        "session_id": session.name,
        "profile_update_status": "not_updated",
        "deployment_ready": False,
        "go1_g1_blocked": True,
    }), encoding="utf-8")


def _trial(trial_id: str, group: str, velocity: str) -> dict[str, str]:
    return {
        "trial_id": trial_id,
        "refresh_group_id": group,
        "session_id": "fixture",
        "surface": "S2_marble_floor",
        "desired_velocity_mps": velocity,
        "condition": "direct_refresh",
        "command_velocity_mps": velocity,
        "state_log_path": f"state_logs/{trial_id}.csv",
        "valid": "true",
        "invalid_reason": "",
        "timestamp": "2026-06-12T00:00:00+00:00",
        "physical_run_status": "executed",
        "notes": "test fixture",
        "repeat_index": "1",
    }


def _write_records(session: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "trial_id",
        "refresh_group_id",
        "session_id",
        "surface",
        "desired_velocity_mps",
        "condition",
        "command_velocity_mps",
        "state_log_path",
        "valid",
        "invalid_reason",
        "timestamp",
        "physical_run_status",
        "notes",
    ]
    _write_csv(session / "trial_records.csv", rows, fields)


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _has_import(lines: list[str], module_name: str) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"import {module_name}") or stripped.startswith(f"from {module_name}"):
            return True
    return False
