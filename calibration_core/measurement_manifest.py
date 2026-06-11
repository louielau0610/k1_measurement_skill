"""Measurement module artifact manifest utilities."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_MANIFEST_FIELDS = [
    "dataset_id",
    "platform",
    "robot_model",
    "robot_id",
    "session_id",
    "surfaces",
    "speeds",
    "repeats",
    "state_log_dir",
    "trial_records_path",
    "extracted_measurements_path",
    "qc_summary_path",
    "response_statistics_path",
    "profile_path",
    "validation_status",
    "limitations",
]


@dataclass(frozen=True)
class MeasurementManifest:
    dataset_id: str
    platform: str
    robot_model: str
    robot_id: str
    session_id: str
    surfaces: list[str]
    speeds: list[float]
    repeats: int
    state_log_dir: str
    trial_records_path: str
    extracted_measurements_path: str
    qc_summary_path: str
    response_statistics_path: str
    profile_path: str
    validation_status: str
    limitations: list[str]
    empirical_cross_platform_claim: bool = False
    velocity_compensation_ready: bool = False
    navigation_improvement_claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_manifest_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def validate_measurement_manifest(
    manifest: dict[str, Any],
    root: Path = Path("."),
    *,
    require_k1_reference: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest]
    errors.extend(f"missing_required_field:{field}" for field in missing)

    for field in ("surfaces", "speeds", "limitations"):
        if field in manifest and not isinstance(manifest[field], list):
            errors.append(f"{field}:must_be_list")
    if "repeats" in manifest:
        try:
            if int(manifest["repeats"]) <= 0:
                errors.append("repeats:must_be_positive")
        except (TypeError, ValueError):
            errors.append("repeats:must_be_integer")

    if manifest.get("velocity_compensation_ready") is not False:
        errors.append("velocity_compensation_ready:must_be_false")
    if manifest.get("empirical_cross_platform_claim") is not False:
        errors.append("empirical_cross_platform_claim:must_be_false")

    path_fields = [
        "state_log_dir",
        "trial_records_path",
        "extracted_measurements_path",
        "qc_summary_path",
        "response_statistics_path",
        "profile_path",
    ]
    resolved_paths: dict[str, str] = {}
    for field in path_fields:
        value = manifest.get(field)
        if not isinstance(value, str) or not value:
            continue
        path = resolve_manifest_path(root, value)
        resolved_paths[field] = str(path)
        if not path.exists():
            errors.append(f"{field}:missing:{value}")

    extracted_rows = []
    extracted_path_value = manifest.get("extracted_measurements_path")
    extracted_path = resolve_manifest_path(root, extracted_path_value) if isinstance(extracted_path_value, str) else None
    if extracted_path and extracted_path.exists():
        extracted_rows = read_csv_rows(extracted_path)
        if require_k1_reference and len(extracted_rows) != 72:
            errors.append(f"extracted_measurements_path:expected_72_rows:found_{len(extracted_rows)}")
        bad_status = sorted({row.get("extraction_status", "") for row in extracted_rows if row.get("extraction_status") != "ok"})
        if bad_status:
            errors.append(f"extracted_measurements_path:non_ok_status:{','.join(bad_status)}")
        if require_k1_reference:
            cell_counts: dict[tuple[str, str], int] = {}
            for row in extracted_rows:
                trial_id = row.get("trial_id", "")
                surface = row.get("surface_id") or _surface_from_trial_id(trial_id)
                speed = _canonical_speed(row.get("command_velocity", ""))
                cell_counts[(surface, speed)] = cell_counts.get((surface, speed), 0) + 1
            expected_surfaces = [str(surface) for surface in manifest.get("surfaces", [])]
            expected_speeds = [_canonical_speed(speed) for speed in manifest.get("speeds", [])]
            incomplete = [
                f"{surface}@{speed}:n={cell_counts.get((surface, speed), 0)}"
                for surface in expected_surfaces
                for speed in expected_speeds
                if cell_counts.get((surface, speed), 0) != 3
            ]
            if incomplete:
                errors.append("surface_speed_cells:not_n3:" + ";".join(incomplete))

    profile_path_value = manifest.get("profile_path")
    profile_path = resolve_manifest_path(root, profile_path_value) if isinstance(profile_path_value, str) else None
    if require_k1_reference and profile_path and profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        if profile.get("robot_id") != "Booster_K1":
            errors.append("profile_path:not_booster_k1_gold_profile")
        if not profile.get("region_labels"):
            errors.append("profile_path:missing_region_labels")

    return {
        "valid": not errors,
        "errors": errors,
        "dataset_id": manifest.get("dataset_id"),
        "platform": manifest.get("platform"),
        "validation_status": manifest.get("validation_status"),
        "extracted_measurement_rows": len(extracted_rows),
        "compensation_ready": manifest.get("velocity_compensation_ready"),
        "resolved_paths": resolved_paths,
    }


def _surface_from_trial_id(trial_id: str) -> str:
    if "_B" not in trial_id:
        return ""
    without_block = trial_id.split("_B", 1)[0]
    return without_block.split("_", 1)[1] if "_" in without_block else ""


def _canonical_speed(value: Any) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)
