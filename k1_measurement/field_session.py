"""Real K1 field-test session creation and ground-truth helpers."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from k1_measurement.field_test_pack import GROUND_TRUTH_COLUMNS, write_ground_truth_trial_sheet


PLANNED_VELOCITY_GROUPS = [0.1, 0.2, 0.3, 0.4]
REPEATS_PER_SPEED = 3
SESSION_SUBDIRS = ["raw_ros", "normalized", "processed", "plots", "reports"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _copy_or_write(source: Path, destination: Path, fallback: str = "") -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.copyfile(source, destination)
    else:
        destination.write_text(fallback, encoding="utf-8")


def create_field_session(session_id: str, output_root: str | Path) -> dict[str, Any]:
    """Create a structured real K1 field session directory."""

    if not session_id or any(char in session_id for char in "\\/:*?\"<>|"):
        raise ValueError("session_id must be a non-empty filesystem-safe name")

    root = Path(output_root)
    session_dir = root / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    for subdir in SESSION_SUBDIRS:
        (session_dir / subdir).mkdir(exist_ok=True)

    repo_root = Path(__file__).resolve().parents[1]
    topic_mapping_path = session_dir / "topic_mapping.yaml"
    field_config_path = session_dir / "field_session_config.yaml"
    ground_truth_path = session_dir / "ground_truth_trial_sheet.csv"
    trial_notes_path = session_dir / "trial_notes.md"

    _copy_or_write(repo_root / "configs" / "real_k1_topic_mapping_template.yaml", topic_mapping_path)
    _copy_or_write(repo_root / "configs" / "real_k1_field_session_template.yaml", field_config_path)
    write_ground_truth_trial_sheet(ground_truth_path)
    _copy_or_write(repo_root / "templates" / "real_k1_trial_notes.md", trial_notes_path)

    manifest = {
        "session_id": session_id,
        "created_at": _utc_now(),
        "project_version_or_git_commit": _git_commit(),
        "operator": "TBD",
        "robot_id": "TBD",
        "environment_label": {"floor_type": "TBD", "condition": "TBD", "slope": "TBD"},
        "planned_velocity_groups": PLANNED_VELOCITY_GROUPS,
        "repeats_per_speed": REPEATS_PER_SPEED,
        "paths": {
            "session_dir": str(session_dir),
            "topic_mapping": str(topic_mapping_path),
            "field_session_config": str(field_config_path),
            "ground_truth_trial_sheet": str(ground_truth_path),
            "trial_notes": str(trial_notes_path),
            "raw_ros": str(session_dir / "raw_ros"),
            "normalized": str(session_dir / "normalized"),
            "processed": str(session_dir / "processed"),
            "plots": str(session_dir / "plots"),
            "reports": str(session_dir / "reports"),
        },
    }
    (session_dir / "session_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest


def load_ground_truth_sheet(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def validate_ground_truth_columns(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
    missing = [column for column in GROUND_TRUTH_COLUMNS if column not in columns]
    return {"valid": not missing, "missing_columns": missing, "columns": columns}


def summarize_ground_truth_sheet(
    path: str | Path,
    velocity_groups: list[float] | None = None,
    repeats_per_speed: int = REPEATS_PER_SPEED,
) -> dict[str, Any]:
    rows = load_ground_truth_sheet(path)
    velocity_groups = velocity_groups or PLANNED_VELOCITY_GROUPS
    column_summary = validate_ground_truth_columns(path)
    observed = {
        (str(row.get("vx_cmd_mps", "")), str(row.get("repeat_index", "")))
        for row in rows
    }
    missing_trials = [
        {"vx_cmd_mps": vx, "repeat_index": repeat}
        for vx in velocity_groups
        for repeat in range(1, repeats_per_speed + 1)
        if (str(vx), str(repeat)) not in observed
    ]
    required_ground_truth_fields = ["measured_distance_m", "elapsed_time_s", "floor_type", "condition", "slope"]
    incomplete_fields = [
        {"trial_id": row.get("trial_id", ""), "field": field}
        for row in rows
        for field in required_ground_truth_fields
        if not row.get(field)
    ]
    return {
        "valid_columns": column_summary["valid"],
        "missing_columns": column_summary["missing_columns"],
        "row_count": len(rows),
        "missing_planned_trials": missing_trials,
        "incomplete_ground_truth_fields": incomplete_fields,
    }


def load_session_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    if not isinstance(config, dict):
        raise ValueError("field session config must be a YAML object")
    return config
