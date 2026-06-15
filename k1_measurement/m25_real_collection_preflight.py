"""M25-R safe-speed confirmation, preflight, packages, and exploration gate."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from k1_measurement.full_range_velocity_profile import M25Config, ValidSpeedDomain, plan_phase


SCHEMA_VERSION = "m25r_real_collection_preflight_v1"
ALLOWED_EVIDENCE_TYPES = {
    "sdk_documentation",
    "validated_robot_configuration",
    "lab_protocol",
    "supervisor_approval",
    "operator_confirmation",
}
PLACEHOLDERS = {"", "null", "none", "tbd", "todo", "placeholder", "changeme", "to_be_filled"}


@dataclass(frozen=True)
class SafeSpeedConfirmation:
    robot_id: str | None
    control_mode: str | None
    gait_mode: str | None
    safe_command_speed_max: float | None
    evidence_type: str | None
    evidence_reference: str | None
    confirmed_by: str | None
    confirmed_at: str | None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SafeSpeedConfirmation":
        value = data.get("safe_command_speed_max")
        return cls(
            robot_id=_optional_text(data.get("robot_id")),
            control_mode=_optional_text(data.get("control_mode")),
            gait_mode=_optional_text(data.get("gait_mode")),
            safe_command_speed_max=None if value in (None, "") else float(value),
            evidence_type=_optional_text(data.get("evidence_type")),
            evidence_reference=_optional_text(data.get("evidence_reference")),
            confirmed_by=_optional_text(data.get("confirmed_by")),
            confirmed_at=_optional_text(data.get("confirmed_at")),
            notes=_optional_text(data.get("notes")),
        )

    def validate(self, *, require_context: bool = True) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        for field_name in ("robot_id", "evidence_type", "evidence_reference", "confirmed_by", "confirmed_at"):
            if _is_placeholder(getattr(self, field_name)):
                errors.append(_error("unresolved_placeholder", field_name, f"{field_name} is required"))
        if require_context:
            for field_name in ("control_mode", "gait_mode"):
                if _is_placeholder(getattr(self, field_name)):
                    errors.append(_error("unresolved_placeholder", field_name, f"{field_name} is required"))
        if self.safe_command_speed_max is None or not _is_positive_finite(self.safe_command_speed_max):
            errors.append(_error("safe_command_limit_not_configured", "safe_command_speed_max", "safe_command_speed_max must be positive and non-null"))
        if self.evidence_type and self.evidence_type not in ALLOWED_EVIDENCE_TYPES:
            errors.append(_error("unsupported_evidence_type", "evidence_type", f"unsupported evidence_type: {self.evidence_type}"))
        return errors

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_yaml_object(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return data


def load_safe_speed_confirmation(path: str | Path) -> SafeSpeedConfirmation:
    return SafeSpeedConfirmation.from_mapping(load_yaml_object(path))


def validate_safe_speed_confirmation(path: str | Path, *, require_context: bool = True) -> dict[str, Any]:
    confirmation = load_safe_speed_confirmation(path)
    effective_require_context = require_context and confirmation.robot_id != "k1"
    errors = confirmation.validate(require_context=effective_require_context)
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": not errors,
        "errors": errors,
        "mode_context_policy": (
            "fixed_sdk_motion_sequence" if confirmation.robot_id == "k1" else "explicit_mode_context"
        ),
        "control_mode_required": effective_require_context,
        "gait_mode_required": effective_require_context,
        "confirmation": confirmation.as_dict(),
    }


def load_preflight_config(path: str | Path) -> dict[str, Any]:
    return load_yaml_object(path)


def evaluate_preflight(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    config = load_preflight_config(config_path)
    blocked: list[dict[str, str]] = []
    warnings: list[str] = []

    m25_config_path = _resolve(config_path, config.get("m25_config_path"))
    m25_config = M25Config.from_mapping(load_yaml_object(m25_config_path))

    confirmation_path = _resolve(config_path, config.get("safe_speed_confirmation_path"))
    confirmation = load_safe_speed_confirmation(confirmation_path)
    require_control_mode = bool(config.get("require_control_mode", True))
    require_gait_mode = bool(config.get("require_gait_mode", True))
    confirmation_errors = confirmation.validate(
        require_context=bool(require_control_mode or require_gait_mode)
    )
    blocked.extend(confirmation_errors)

    safe_max = confirmation.safe_command_speed_max
    # Allow preflight config to override domain values directly
    domain_override = config.get("valid_speed_domain", {}) or {}
    resolved_domain = ValidSpeedDomain(
        valid_command_speed_min=float(domain_override.get("valid_command_speed_min", m25_config.valid_speed_domain.valid_command_speed_min)),
        safe_command_speed_max=safe_max,
        high_priority_actual_speed_min=float(domain_override.get("high_priority_actual_speed_min", m25_config.valid_speed_domain.high_priority_actual_speed_min)),
        high_priority_actual_speed_max=float(domain_override.get("high_priority_actual_speed_max", m25_config.valid_speed_domain.high_priority_actual_speed_max)),
    )
    # Allow preflight to override command grids directly
    exploration_points = (
        [float(v) for v in config["exploration_command_points"]]
        if config.get("exploration_command_points") is not None
        else m25_config.exploration_command_points
    )
    formal_grid = (
        [float(v) for v in config["formal_command_grid"]]
        if config.get("formal_command_grid") is not None
        else m25_config.formal_command_grid
    )
    config_hash = file_sha256(config_path)
    confirmation_hash = file_sha256(confirmation_path)
    safety_provenance = {
        "safe_command_speed_max": safe_max,
        "source_path": str(confirmation_path),
        "source_hash": confirmation_hash,
        "preflight_config_path": str(config_path),
        "preflight_config_hash": config_hash,
    }
    resolved_m25 = M25Config(
        valid_speed_domain=resolved_domain,
        surface=str(config.get("surface_id") or m25_config.surface),
        robot_id=str(config.get("robot_id") or confirmation.robot_id or m25_config.robot_id),
        exploration_command_points=exploration_points,
        formal_command_grid=formal_grid,
        exploration_repeats=int(config.get("exploration_repeats", m25_config.exploration_repeats)),
        formal_repeats=int(config.get("formal_repeats", m25_config.formal_repeats)),
        random_seed=m25_config.random_seed,
        randomization=m25_config.randomization,
    )

    for field_name in ("robot_id", "surface_id"):
        if _is_placeholder(config.get(field_name)):
            blocked.append(_error("unresolved_placeholder", field_name, f"{field_name} is required"))
    mode_context = _mode_context_policy(config)
    blocked.extend(_validate_mode_context(config, mode_context))
    if require_control_mode and _is_placeholder(config.get("control_mode")):
        blocked.append(_error("unresolved_placeholder", "control_mode", "control_mode is required"))
    if require_gait_mode and _is_placeholder(config.get("gait_mode")):
        blocked.append(_error("unresolved_placeholder", "gait_mode", "gait_mode is required"))
    for field_name in ("trial_duration_sec", "warmup_duration_sec", "steady_window_start_sec", "steady_window_end_sec"):
        if not _is_positive_finite(_float_or_none(config.get(field_name))):
            blocked.append(_error("invalid_timing", field_name, f"{field_name} must be positive"))
    start = _float_or_none(config.get("steady_window_start_sec"))
    end = _float_or_none(config.get("steady_window_end_sec"))
    duration = _float_or_none(config.get("trial_duration_sec"))
    if start is not None and end is not None and start >= end:
        blocked.append(_error("invalid_steady_window", "steady_window", "steady window start must be before end"))
    if end is not None and duration is not None and end > duration:
        blocked.append(_error("invalid_steady_window", "steady_window_end_sec", "steady window must fit inside trial duration"))

    safeguards = config.get("execution_safeguards", {})
    if not isinstance(safeguards, dict):
        blocked.append(_error("invalid_safeguards", "execution_safeguards", "execution_safeguards must be an object"))
        safeguards = {}
    for key in ("dry_run_default", "require_execute_flag", "require_operator_confirmation", "emergency_stop_briefing_required"):
        if safeguards.get(key) is not True:
            blocked.append(_error("execution_safeguard_disabled", key, f"{key} must be true"))

    output_dir = _resolve(config_path, config.get("logger_output_dir"))
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".m25r_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        blocked.append(_error("output_directory_not_writable", "logger_output_dir", str(exc)))

    for mapping in config.get("required_input_mappings", []) or []:
        mapping_path = _resolve(config_path, mapping)
        if not mapping_path.exists():
            blocked.append(_error("required_input_mapping_missing", "required_input_mappings", str(mapping_path)))

    exploration_plan = plan_phase(resolved_m25, "exploration")
    formal_plan = plan_phase(resolved_m25, "formal")
    _attach_safety_and_motion_metadata(exploration_plan, safety_provenance, mode_context)
    _attach_safety_and_motion_metadata(formal_plan, safety_provenance, mode_context)
    for plan in (exploration_plan, formal_plan):
        if not plan["executable"]:
            blocked.extend(plan["errors"])
    if m25_config.random_seed is None:
        blocked.append(_error("random_seed_required", "random_seed", "random_seed must be configured"))
    if not config.get("exploration_review_complete", False):
        warnings.append("formal collection remains blocked until exploration data have been reviewed")

    blocked = _dedupe_errors(blocked)
    ready = not blocked
    safe_max_resolved = confirmation.safe_command_speed_max is not None and _is_positive_finite(confirmation.safe_command_speed_max)
    return {
        "schema_version": SCHEMA_VERSION,
        "ready": ready,
        "blocked_reasons": blocked,
        "warnings": warnings,
        "safe_command_speed_max_resolved": safe_max_resolved,
        "safe_command_speed_max": safe_max,
        "resolved_speed_domain": resolved_domain.as_dict(),
        "exploration_trial_count": exploration_plan.get("trial_count", 0),
        "formal_trial_count": formal_plan.get("trial_count", 0),
        "random_seed": m25_config.random_seed,
        "config_hash": config_hash,
        "safe_speed_confirmation_hash": confirmation_hash,
        "safety_provenance": safety_provenance,
        "plan_hashes": {
            "exploration": object_sha256(exploration_plan),
            "formal": object_sha256(formal_plan),
        },
        "plans": {
            "exploration": exploration_plan,
            "formal": formal_plan,
        },
        "mode_context_policy": mode_context,
        "robot_id": resolved_m25.robot_id,
        "surface_id": resolved_m25.surface,
        "control_mode": config.get("control_mode"),
        "gait_mode": config.get("gait_mode"),
        "git_commit": config.get("git_commit", "record_at_session_creation"),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_collection_package(preflight_path: str | Path, phase: str) -> dict[str, Any]:
    if phase not in {"exploration", "formal"}:
        raise ValueError("phase must be exploration or formal")
    preflight = evaluate_preflight(preflight_path)
    config = load_preflight_config(preflight_path)
    formal_gate = config.get("exploration_review_complete", False) or bool(config.get("formal_override_reason"))
    blocked = list(preflight["blocked_reasons"])
    if phase == "formal" and not formal_gate:
        blocked.append(_error("formal_blocked_before_exploration_review", "exploration_review_complete", "formal collection requires reviewed exploration data or documented override"))
    blocked = _dedupe_errors(blocked)
    package_ready = not blocked
    script_phase = "exploration" if phase == "exploration" else "formal"
    return {
        "schema_version": SCHEMA_VERSION,
        "package": f"m25r_{phase}_collection",
        "ready": package_ready,
        "safe_command_speed_max_resolved": preflight.get("safe_command_speed_max_resolved", False),
        "safe_command_speed_max": preflight.get("safe_command_speed_max"),
        "blocked_reasons": blocked,
        "warnings": preflight["warnings"],
        "preflight": preflight,
        "execution_audit_trail": {
            "safe_command_speed_max": preflight.get("safe_command_speed_max"),
            "safety_provenance": preflight.get("safety_provenance"),
            "mode_context_policy": preflight.get("mode_context_policy"),
            "plan_hash": preflight.get("plan_hashes", {}).get(phase),
            "runner_required_safe_command_speed_max": preflight.get("safe_command_speed_max"),
            "runner_config_provenance_required": True,
        },
        "session_metadata": {
            "safe_command_speed_max": preflight.get("safe_command_speed_max"),
            "safe_speed_confirmation_hash": preflight.get("safe_speed_confirmation_hash"),
            "preflight_config_hash": preflight.get("config_hash"),
            "command_source": preflight.get("mode_context_policy", {}).get("command_source"),
            "motion_sequence": preflight.get("mode_context_policy", {}).get("motion_sequence"),
        },
        "operator_commands": {
            "preflight_validation": f"py scripts/validate_m25_real_collection_preflight.py --config {preflight_path}",
            "dry_run_generation": f"py scripts/prepare_m25r_collection_package.py --config {preflight_path} --phase {script_phase}",
            "print_only_inspection": f"py scripts/plan_full_range_velocity_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --phase {script_phase}",
            "real_execution": "BLOCKED until preflight ready; then run the existing guarded robot runner with --execute and per-trial operator confirmation",
            "session_validation": "py scripts/validate_m25_collected_session.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv>",
            "candidate_profile_generation": "py scripts/build_m25_candidate_profile.py --config configs/m25_full_range_velocity_profile_template.yaml --session <collected_extraction.csv> --dry-run",
        },
        "scientific_boundary": "no robot motion is executed by package generation; no M26 model is fitted",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def write_collection_package(preflight_path: str | Path, phase: str, output_dir: str | Path) -> tuple[dict[str, Any], Path, Path]:
    package = build_collection_package(preflight_path, phase)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"m25r_{phase}_collection_package"
    json_path = out / f"{stem}.json"
    md_path = out / f"{stem}.md"
    json_path.write_text(json.dumps(package, indent=2), encoding="utf-8")
    md_path.write_text(collection_package_markdown(package), encoding="utf-8")
    return package, json_path, md_path


def collection_package_markdown(package: dict[str, Any]) -> str:
    safe_max = package.get("safe_command_speed_max")
    safe_resolved = package.get("safe_command_speed_max_resolved", False)
    lines = [
        f"# {package['package']}",
        "",
        f"- Ready: `{str(package['ready']).lower()}`",
        f"- Safe-speed resolved: `{str(safe_resolved).lower()}`",
        f"- Safe command speed max: `{safe_max}`",
        f"- Command source: `{package['preflight'].get('mode_context_policy', {}).get('command_source')}`",
        f"- Motion path resolved: `{str(package['preflight'].get('mode_context_policy', {}).get('motion_path_resolved', False)).lower()}`",
        f"- Exploration trials: {package['preflight']['exploration_trial_count']}",
        f"- Formal trials: {package['preflight']['formal_trial_count']}",
        f"- Random seed: `{package['preflight']['random_seed']}`",
        "",
        "## Blocked Reasons",
        "",
    ]
    if package["blocked_reasons"]:
        lines.extend(f"- `{item['code']}`: {item['message']}" for item in package["blocked_reasons"])
    else:
        lines.append("- none")
    lines += ["", "## Operator Commands", ""]
    for name, command in package["operator_commands"].items():
        lines.append(f"- `{name}`: `{command}`")
    lines += ["", "No robot motion is executed by this package generator."]
    return "\n".join(lines) + "\n"


def evaluate_exploration_gate(path: str | Path, domain: ValidSpeedDomain, *, min_repeats: int = 3, min_fit_quality: float = 0.8) -> dict[str, Any]:
    rows = _read_rows(Path(path))
    valid_rows = [row for row in rows if str(row.get("valid", "true")).lower() in {"true", "1", "yes"}]
    decisions: list[str] = []
    if len(valid_rows) < min_repeats:
        decisions.append("insufficient_valid_trials")
    by_command: dict[float, list[dict[str, Any]]] = {}
    for row in valid_rows:
        command = _float_or_none(row.get("command_speed", row.get("command_velocity_mps")))
        actual = _float_or_none(row.get("estimated_actual_speed", row.get("measured_actual_velocity_mps")))
        fit_quality = _float_or_none(row.get("fit_quality"))
        steady_duration = _float_or_none(row.get("steady_window_duration"))
        if command is None or actual is None:
            decisions.append("extraction_quality_failure")
            continue
        if steady_duration is None or steady_duration <= 0 or (fit_quality is not None and fit_quality < min_fit_quality):
            decisions.append("extraction_quality_failure")
        by_command.setdefault(command, []).append(row)
    missing_repeats = [cmd for cmd, group in by_command.items() if len(group) < min_repeats]
    if missing_repeats:
        decisions.append("insufficient_valid_trials")
    # Command coverage check across the valid domain
    commands_covered = sorted(by_command.keys())
    if domain.safe_command_speed_max is not None:
        # Check coverage across valid command range
        covered_range = max(commands_covered) - min(commands_covered) if len(commands_covered) >= 2 else 0.0
        full_range = domain.safe_command_speed_max - domain.valid_command_speed_min
        if full_range > 0 and covered_range < 0.5 * full_range:
            # Only suggest grid extension if we are not already at the safe limit
            if max(commands_covered) < domain.safe_command_speed_max - 0.01:
                decisions.append("requires_grid_extension")
    # Upper-range coverage: check if high-priority command region is covered
    if domain.safe_command_speed_max is not None:
        hp_low = max(domain.high_priority_actual_speed_min, domain.valid_command_speed_min)
        hp_high = domain.safe_command_speed_max
        upper_covered = [c for c in commands_covered if c >= hp_low]
        if not upper_covered:
            decisions.append("high_priority_region_not_covered")
    actuals = [_float_or_none(row.get("estimated_actual_speed", row.get("measured_actual_velocity_mps"))) for row in valid_rows]
    actual_values = [v for v in actuals if v is not None]
    if actual_values and max(actual_values) < domain.high_priority_actual_speed_min:
        if domain.safe_command_speed_max is not None and max(by_command or {0.0: []}) >= domain.safe_command_speed_max:
            decisions.append("safe_limit_prevents_requested_coverage")
        else:
            decisions.append("high_priority_region_not_covered")
    # Grid refinement: check for non-monotonic actual speed ordering
    ordered = sorted((cmd, _mean_actual(group)) for cmd, group in by_command.items())
    if len(ordered) >= 2 and any(curr < prev - 0.05 for (_, prev), (_, curr) in zip(ordered, ordered[1:])):
        decisions.append("requires_grid_refinement")
    # Grid extension: ensure sufficient command points
    if len(by_command) < 2:
        decisions.append("requires_grid_extension")
    # Never recommend exceeding the safe limit
    if domain.safe_command_speed_max is not None:
        for cmd in commands_covered:
            if cmd > domain.safe_command_speed_max:
                decisions.append("above_safe_command_limit")
    if not decisions:
        decisions.append("ready_for_formal_collection")
    unique = []
    for decision in decisions:
        if decision not in unique:
            unique.append(decision)
    return {
        "schema_version": SCHEMA_VERSION,
        "ready": unique == ["ready_for_formal_collection"],
        "decisions": unique,
        "valid_trial_count": len(valid_rows),
        "per_command_counts": {f"{cmd:.3f}": len(group) for cmd, group in sorted(by_command.items())},
        "high_priority_region": [domain.high_priority_actual_speed_min, domain.high_priority_actual_speed_max],
        "safe_command_speed_max": domain.safe_command_speed_max,
        "m26_model_fitted": False,
    }


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_sha256(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mode_context_policy(config: dict[str, Any]) -> dict[str, Any]:
    robot_id = _optional_text(config.get("robot_id"))
    command_source = _optional_text(config.get("command_source"))
    sequence = config.get("motion_sequence") or []
    if not isinstance(sequence, list):
        sequence = []
    move_command = config.get("move_command") or {}
    if not isinstance(move_command, dict):
        move_command = {}
    if robot_id == "k1":
        return {
            "mode_context_policy": "fixed_sdk_motion_sequence",
            "control_mode_required": bool(config.get("require_control_mode", False)),
            "gait_mode_required": bool(config.get("require_gait_mode", False)),
            "command_source": command_source,
            "motion_sequence": [str(item) for item in sequence],
            "move_command": {
                "vy": _float_or_none(move_command.get("vy")),
                "wz": _float_or_none(move_command.get("wz")),
            },
            "motion_path_resolved": False,
        }
    return {
        "mode_context_policy": "explicit_mode_context",
        "control_mode_required": bool(config.get("require_control_mode", True)),
        "gait_mode_required": bool(config.get("require_gait_mode", True)),
        "command_source": command_source,
        "motion_sequence": [str(item) for item in sequence],
        "move_command": move_command,
        "motion_path_resolved": False,
    }


def _validate_mode_context(config: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, str]]:
    if policy["mode_context_policy"] != "fixed_sdk_motion_sequence":
        return []
    errors: list[dict[str, str]] = []
    sequence = policy["motion_sequence"]
    move_command = policy["move_command"]
    if _is_placeholder(policy.get("command_source")):
        errors.append(_error("missing_command_source", "command_source", "K1 fixed SDK motion path requires command_source"))
    if not sequence:
        errors.append(_error("missing_motion_sequence", "motion_sequence", "K1 fixed SDK motion path requires motion_sequence"))
    if "kPrepare" not in sequence:
        errors.append(_error("invalid_motion_sequence", "motion_sequence", "K1 motion sequence must include kPrepare"))
    if "kWalking" not in sequence:
        errors.append(_error("invalid_motion_sequence", "motion_sequence", "K1 motion sequence must include kWalking"))
    if not sequence or sequence[-1] != "Move":
        errors.append(_error("invalid_motion_sequence", "motion_sequence", "K1 final motion operation must be Move"))
    if move_command.get("vy") != 0.0:
        errors.append(_error("invalid_move_command", "move_command.vy", "K1 Move command must fix vy to 0.0"))
    if move_command.get("wz") != 0.0:
        errors.append(_error("invalid_move_command", "move_command.wz", "K1 Move command must fix wz to 0.0"))
    policy["move_uses_planned_vx"] = True
    policy["motion_path_resolved"] = not errors
    return errors


def _attach_safety_and_motion_metadata(
    plan: dict[str, Any],
    safety_provenance: dict[str, Any],
    mode_context: dict[str, Any],
) -> None:
    plan["safe_command_speed_max"] = safety_provenance["safe_command_speed_max"]
    plan["safety_provenance"] = safety_provenance
    plan["mode_context_policy"] = mode_context
    for trial in plan.get("trials", []):
        trial["safe_command_speed_max"] = safety_provenance["safe_command_speed_max"]
        trial["safety_provenance"] = safety_provenance
        trial["command_source"] = mode_context.get("command_source")
        trial["motion_sequence"] = mode_context.get("motion_sequence")
        trial["move_command"] = {
            "vx": "planned_command_speed_mps",
            "vy": 0.0,
            "wz": 0.0,
        }


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("trials", "rows", "measurements"):
                if isinstance(data.get(key), list):
                    return data[key]
        return []
    import csv

    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def _mean_actual(rows: list[dict[str, Any]]) -> float:
    values = [_float_or_none(row.get("estimated_actual_speed", row.get("measured_actual_velocity_mps"))) for row in rows]
    numeric = [value for value in values if value is not None]
    return sum(numeric) / len(numeric) if numeric else float("nan")


def _resolve(config_path: Path, value: Any) -> Path:
    if _is_placeholder(value):
        return Path("__missing__")
    path = Path(str(value))
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve() if str(value).startswith(".") else (Path.cwd() / path).resolve()


def _error(code: str, field: str, message: str) -> dict[str, str]:
    return {"code": code, "field": field, "message": message}


def _dedupe_errors(errors: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, str]] = []
    for error in errors:
        key = (error.get("code", ""), error.get("field", ""), error.get("message", ""))
        if key not in seen:
            seen.add(key)
            result.append(error)
    return result


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def _is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip().lower() in PLACEHOLDERS


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_positive_finite(value: float | None) -> bool:
    return value is not None and math.isfinite(value) and value > 0
