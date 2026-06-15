"""M25 full-range velocity profiling contract and planning utilities."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "m25_full_range_velocity_profile_v1"
DEFAULT_EXPLORATION_COMMANDS = [0.35, 0.40, 0.50, 0.60]
DEFAULT_FORMAL_COMMANDS = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
PROFILE_STATUSES = {"planned", "collected", "candidate", "validated", "rejected"}
DECISION_CODES = {
    "below_valid_speed_domain",
    "above_safe_command_limit",
    "safe_command_limit_not_configured",
    "target_outside_reachable_actual_speed_range",
}


class M25ValidationError(ValueError):
    """Validation error with a machine-readable decision code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

    def to_error(self) -> dict[str, str]:
        return {"code": self.code, "message": str(self)}


@dataclass(frozen=True)
class ValidSpeedDomain:
    valid_command_speed_min: float = 0.35
    safe_command_speed_max: float | None = None
    high_priority_actual_speed_min: float = 0.50
    high_priority_actual_speed_max: float = 0.60

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ValidSpeedDomain":
        domain = data.get("valid_speed_domain", data)
        if not isinstance(domain, dict):
            raise M25ValidationError("invalid_domain_config", "valid_speed_domain must be an object")
        return cls(
            valid_command_speed_min=float(domain.get("valid_command_speed_min", 0.35)),
            safe_command_speed_max=(
                None
                if domain.get("safe_command_speed_max") is None
                else float(domain["safe_command_speed_max"])
            ),
            high_priority_actual_speed_min=float(domain.get("high_priority_actual_speed_min", 0.80)),
            high_priority_actual_speed_max=float(domain.get("high_priority_actual_speed_max", 1.00)),
        )

    def validate(self, *, require_safe_max: bool = False) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        for name, value in [
            ("valid_command_speed_min", self.valid_command_speed_min),
            ("high_priority_actual_speed_min", self.high_priority_actual_speed_min),
            ("high_priority_actual_speed_max", self.high_priority_actual_speed_max),
        ]:
            if not _is_positive_finite(value):
                errors.append({"code": "invalid_speed_value", "field": name, "message": "speed must be finite and positive"})
        if self.safe_command_speed_max is None:
            if require_safe_max:
                errors.append({
                    "code": "safe_command_limit_not_configured",
                    "field": "safe_command_speed_max",
                    "message": "safe_command_speed_max is required for executable M25 plans",
                })
        elif not _is_positive_finite(self.safe_command_speed_max):
            errors.append({"code": "invalid_speed_value", "field": "safe_command_speed_max", "message": "speed must be finite and positive"})
        elif self.valid_command_speed_min >= self.safe_command_speed_max:
            errors.append({
                "code": "invalid_domain_order",
                "field": "valid_speed_domain",
                "message": "valid_command_speed_min must be smaller than safe_command_speed_max",
            })
        if self.high_priority_actual_speed_min >= self.high_priority_actual_speed_max:
            errors.append({
                "code": "invalid_high_priority_interval",
                "field": "valid_speed_domain",
                "message": "high-priority actual-speed interval must be ordered",
            })
        return errors

    def require_valid(self, *, require_safe_max: bool = False) -> None:
        errors = self.validate(require_safe_max=require_safe_max)
        if errors:
            first = errors[0]
            raise M25ValidationError(first["code"], first["message"])

    def check_command(self, command_speed: float) -> None:
        if command_speed < self.valid_command_speed_min:
            raise M25ValidationError(
                "below_valid_speed_domain",
                f"command {command_speed:.3f} is below valid_command_speed_min {self.valid_command_speed_min:.3f}",
            )
        if self.safe_command_speed_max is None:
            raise M25ValidationError("safe_command_limit_not_configured", "safe_command_speed_max is not configured")
        if command_speed > self.safe_command_speed_max:
            raise M25ValidationError(
                "above_safe_command_limit",
                f"command {command_speed:.3f} exceeds safe_command_speed_max {self.safe_command_speed_max:.3f}",
            )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class M25Config:
    valid_speed_domain: ValidSpeedDomain = field(default_factory=ValidSpeedDomain)
    surface: str = "S2_marble_floor"
    robot_id: str = "booster_k1_unit_unspecified"
    exploration_command_points: list[float] = field(default_factory=lambda: list(DEFAULT_EXPLORATION_COMMANDS))
    formal_command_grid: list[float] = field(default_factory=lambda: list(DEFAULT_FORMAL_COMMANDS))
    exploration_repeats: int = 3
    formal_repeats: int = 5
    random_seed: int | None = None
    randomization: str = "deterministic_random"

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "M25Config":
        return cls(
            valid_speed_domain=ValidSpeedDomain.from_mapping(data),
            surface=str(data.get("surface", "S2_marble_floor")),
            robot_id=str(data.get("robot_id", "booster_k1_unit_unspecified")),
            exploration_command_points=[float(v) for v in data.get("exploration_command_points", DEFAULT_EXPLORATION_COMMANDS)],
            formal_command_grid=[float(v) for v in data.get("formal_command_grid", DEFAULT_FORMAL_COMMANDS)],
            exploration_repeats=int(data.get("exploration_repeats", 3)),
            formal_repeats=int(data.get("formal_repeats", 5)),
            random_seed=(None if data.get("random_seed") is None else int(data["random_seed"])),
            randomization=str(data.get("randomization", "deterministic_random")),
        )

    def validate(self, *, require_safe_max: bool = False) -> list[dict[str, str]]:
        errors = self.valid_speed_domain.validate(require_safe_max=require_safe_max)
        if self.random_seed is None:
            errors.append({"code": "random_seed_required", "field": "random_seed", "message": "random_seed is required for deterministic randomization"})
        if self.randomization not in {"deterministic_random", "blocked_random"}:
            errors.append({"code": "invalid_randomization", "field": "randomization", "message": "unsupported randomization mode"})
        for field_name, points in [("exploration_command_points", self.exploration_command_points), ("formal_command_grid", self.formal_command_grid)]:
            errors.extend(validate_command_grid(points, self.valid_speed_domain, field_name=field_name, require_safe_max=require_safe_max))
        if self.exploration_repeats < 1 or self.formal_repeats < 1:
            errors.append({"code": "invalid_repeats", "field": "repeats", "message": "repeat counts must be positive"})
        return errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "valid_speed_domain": self.valid_speed_domain.as_dict(),
            "surface": self.surface,
            "robot_id": self.robot_id,
            "exploration_command_points": self.exploration_command_points,
            "formal_command_grid": self.formal_command_grid,
            "exploration_repeats": self.exploration_repeats,
            "formal_repeats": self.formal_repeats,
            "random_seed": self.random_seed,
            "randomization": self.randomization,
        }


def load_config(path: str | Path) -> M25Config:
    with Path(path).open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise M25ValidationError("invalid_config", "configuration must be a YAML object")
    return M25Config.from_mapping(data)


def validate_command_grid(
    points: list[float],
    domain: ValidSpeedDomain,
    *,
    field_name: str = "command_grid",
    require_safe_max: bool = False,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not points:
        return [{"code": "empty_command_grid", "field": field_name, "message": "command grid must not be empty"}]
    if require_safe_max and domain.safe_command_speed_max is None:
        errors.append({"code": "safe_command_limit_not_configured", "field": "safe_command_speed_max", "message": "safe maximum is required"})
    if len(points) != len(set(points)):
        errors.append({"code": "duplicate_command_points", "field": field_name, "message": "command grid contains duplicate points"})
    if points != sorted(points):
        errors.append({"code": "non_monotonic_command_grid", "field": field_name, "message": "canonical command grid must be strictly increasing"})
    for point in points:
        if not _is_positive_finite(point):
            errors.append({"code": "invalid_speed_value", "field": field_name, "message": "command point must be finite and positive"})
            continue
        if point < domain.valid_command_speed_min:
            errors.append({"code": "below_valid_speed_domain", "field": field_name, "message": f"{point:.3f} is below valid command domain"})
        if domain.safe_command_speed_max is not None and point > domain.safe_command_speed_max:
            errors.append({"code": "above_safe_command_limit", "field": field_name, "message": f"{point:.3f} exceeds safe command maximum"})
    return errors


def plan_phase(config: M25Config, phase: str) -> dict[str, Any]:
    require_safe_max = True
    errors = config.validate(require_safe_max=require_safe_max)
    if errors:
        return _blocked_plan(config, phase, errors)
    if phase == "exploration":
        points = _inside_domain(config.exploration_command_points, config.valid_speed_domain)
        repeats = config.exploration_repeats
        purpose = "coverage_exploration"
    elif phase == "formal":
        points = _inside_domain(config.formal_command_grid, config.valid_speed_domain)
        repeats = config.formal_repeats
        purpose = "formal_profile_collection"
    else:
        raise ValueError(f"unknown phase: {phase}")
    trials = _build_trials(points, repeats, config, phase)
    randomized = _randomize_trials(trials, int(config.random_seed), config.randomization)
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone": "M25",
        "phase": phase,
        "purpose": purpose,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "planned",
        "executable": True,
        "errors": [],
        "valid_speed_domain": config.valid_speed_domain.as_dict(),
        "surface": config.surface,
        "robot_id": config.robot_id,
        "random_seed": config.random_seed,
        "randomization": config.randomization,
        "command_points_mps": points,
        "repeats_per_command": repeats,
        "trial_count": len(randomized),
        "trials": randomized,
        "high_priority_actual_speed_region": [
            config.valid_speed_domain.high_priority_actual_speed_min,
            config.valid_speed_domain.high_priority_actual_speed_max,
        ],
        "claim_boundary": "planning only; no hardware execution and no compensation performance claim",
    }


def build_markdown_plan(plan: dict[str, Any]) -> str:
    lines = [
        f"# M25 {plan['phase'].title()} Velocity Profile Plan",
        "",
        f"- Status: `{plan['status']}`",
        f"- Executable: `{str(plan['executable']).lower()}`",
        f"- Surface: `{plan.get('surface', '')}`",
        f"- Robot: `{plan.get('robot_id', '')}`",
        f"- Random seed: `{plan.get('random_seed')}`",
        f"- Trial count: {plan.get('trial_count', 0)}",
        "",
    ]
    if plan.get("errors"):
        lines += ["## Blocking Errors", ""]
        for error in plan["errors"]:
            lines.append(f"- `{error['code']}`: {error['message']}")
        return "\n".join(lines) + "\n"
    lines += [
        "## Command Points",
        "",
    ]
    for point in plan["command_points_mps"]:
        lines.append(f"- {point:.2f} m/s")
    lines += [
        "",
        "## Trials",
        "",
        "| Order | Trial ID | Command | Repeat |",
        "|-------|----------|---------|--------|",
    ]
    for trial in plan["trials"]:
        lines.append(f"| {trial['order_index']} | {trial['trial_id']} | {trial['command_speed_mps']:.2f} | {trial['repeat_index']} |")
    lines += [
        "",
        "No robot motion is executed by this planning artifact.",
    ]
    return "\n".join(lines) + "\n"


def write_plan_artifacts(plan: dict[str, Any], output_dir: Path, name: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{name}.json"
    md_path = output_dir / f"{name}.md"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_plan(plan), encoding="utf-8")
    return json_path, md_path


def validate_collected_session(path: str | Path, domain: ValidSpeedDomain) -> dict[str, Any]:
    rows = _read_rows(Path(path))
    valid_rows = 0
    errors: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        command = _float_from(row, "command_speed", "command_velocity_mps")
        actual = _float_from(row, "estimated_actual_speed", "measured_actual_velocity_mps")
        trial_errors: list[str] = []
        if command is None:
            trial_errors.append("missing_command_speed")
        else:
            try:
                domain.check_command(command)
            except M25ValidationError as exc:
                trial_errors.append(exc.code)
        if actual is None or not math.isfinite(actual):
            trial_errors.append("missing_estimated_actual_speed")
        if _text(row.get("valid", "true")).lower() in {"false", "0", "no"}:
            trial_errors.append("trial_marked_invalid")
        if trial_errors:
            errors.append({"code": "invalid_trial", "row": str(index), "message": ",".join(trial_errors)})
        else:
            valid_rows += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(path),
        "row_count": len(rows),
        "valid_trial_count": valid_rows,
        "invalid_trial_count": len(errors),
        "valid": not errors,
        "errors": errors,
    }


def build_candidate_profile(path: str | Path, config: M25Config) -> dict[str, Any]:
    rows = _read_rows(Path(path))
    valid_trials = []
    excluded = []
    for row in rows:
        command = _float_from(row, "command_speed", "command_velocity_mps")
        actual = _float_from(row, "estimated_actual_speed", "measured_actual_velocity_mps")
        if command is None or actual is None:
            excluded.append({"trial_id": row.get("trial_id", ""), "reason": "missing_velocity_field"})
            continue
        try:
            config.valid_speed_domain.check_command(command)
        except M25ValidationError as exc:
            excluded.append({"trial_id": row.get("trial_id", ""), "reason": exc.code})
            continue
        if _text(row.get("valid", "true")).lower() in {"false", "0", "no"}:
            excluded.append({"trial_id": row.get("trial_id", ""), "reason": "trial_marked_invalid"})
            continue
        valid_trials.append({"command_speed": command, "estimated_actual_speed": actual, "trial_id": row.get("trial_id", "")})
    actuals = [trial["estimated_actual_speed"] for trial in valid_trials]
    commands = sorted({trial["command_speed"] for trial in valid_trials})
    return {
        "schema_version": SCHEMA_VERSION,
        "profile_status": "candidate" if valid_trials else "rejected",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_session": str(path),
        "valid_speed_domain": config.valid_speed_domain.as_dict(),
        "observed_actual_speed_min": min(actuals) if actuals else None,
        "observed_actual_speed_max": max(actuals) if actuals else None,
        "high_priority_actual_speed_region": [
            config.valid_speed_domain.high_priority_actual_speed_min,
            config.valid_speed_domain.high_priority_actual_speed_max,
        ],
        "training_command_points": commands,
        "number_of_repeats": _repeat_counts(valid_trials),
        "per_point_uncertainty": _per_point_uncertainty(valid_trials),
        "surface": config.surface,
        "robot_identifier": config.robot_id,
        "extraction_version": "m25_contract_v1",
        "session_metadata": {"source": str(path)},
        "valid_trial_count": len(valid_trials),
        "excluded_trial_count": len(excluded),
        "excluded_trials": excluded,
        "validated_without_real_formal_data": False,
        "claim_boundary": "candidate profile only; not validated and not a compensation-performance claim",
    }


def validate_target_reachability(profile: dict[str, Any], target_actual_speed: float) -> None:
    low = profile.get("observed_actual_speed_min")
    high = profile.get("observed_actual_speed_max")
    if low is None or high is None or not (float(low) <= target_actual_speed <= float(high)):
        raise M25ValidationError(
            "target_outside_reachable_actual_speed_range",
            "target actual speed is outside the observed reachable interval",
        )


def audit_historical_rows(paths: list[Path], domain: ValidSpeedDomain) -> dict[str, Any]:
    sessions = []
    total_retained = 0
    total_excluded = 0
    for path in paths:
        if not path.exists():
            sessions.append({"path": str(path), "status": "missing", "valid_speed_rows_retained": 0, "rows_excluded": 0, "exclusion_reasons": {"missing": 1}})
            total_excluded += 1
            continue
        rows = _read_rows(path)
        retained = 0
        reasons: dict[str, int] = {}
        for row in rows:
            command = _float_from(row, "command_speed", "command_velocity_mps", "command_velocity")
            actual = _float_from(row, "estimated_actual_speed", "measured_actual_velocity_mps", "measured_actual_velocity")
            reason = None
            if command is None:
                reason = "missing_command_speed"
            elif command < domain.valid_command_speed_min:
                reason = "below_valid_speed_domain"
            elif domain.safe_command_speed_max is not None and command > domain.safe_command_speed_max:
                reason = "above_safe_command_limit"
            elif actual is None:
                reason = "missing_actual_speed"
            if reason:
                reasons[reason] = reasons.get(reason, 0) + 1
                total_excluded += 1
            else:
                retained += 1
                total_retained += 1
        sessions.append({
            "path": str(path),
            "status": "historical_reference_only",
            "row_count": len(rows),
            "valid_speed_rows_retained": retained,
            "rows_excluded": sum(reasons.values()),
            "exclusion_reasons": reasons,
            "extraction_compatibility": "compatible_if_required_m25_velocity_fields_are_present",
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "historical_use_policy": "historical_reference_only",
        "sessions_inspected": len(sessions),
        "valid_speed_rows_retained": total_retained,
        "rows_excluded": total_excluded,
        "sessions": sessions,
        "deadzone_inference_performed": False,
    }


def _blocked_plan(config: M25Config, phase: str, errors: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone": "M25",
        "phase": phase,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked",
        "executable": False,
        "errors": errors,
        "valid_speed_domain": config.valid_speed_domain.as_dict(),
        "surface": config.surface,
        "robot_id": config.robot_id,
        "random_seed": config.random_seed,
        "randomization": config.randomization,
        "command_points_mps": [],
        "repeats_per_command": 0,
        "trial_count": 0,
        "trials": [],
    }


def _build_trials(points: list[float], repeats: int, config: M25Config, phase: str) -> list[dict[str, Any]]:
    trials = []
    for point in points:
        group = f"M25_{phase}_V{int(round(point * 100)):03d}"
        for repeat in range(1, repeats + 1):
            trials.append({
                "trial_id": f"{group}_R{repeat}",
                "phase": phase,
                "surface": config.surface,
                "robot_id": config.robot_id,
                "command_speed_mps": point,
                "repeat_index": repeat,
                "group_id": group,
                "physical_run_status": "planned",
                "notes": "direct command profiling only; no compensation in M25 planning",
            })
    return trials


def _randomize_trials(trials: list[dict[str, Any]], seed: int, mode: str) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    ordered = list(trials)
    if mode == "blocked_random":
        grouped: dict[float, list[dict[str, Any]]] = {}
        for trial in ordered:
            grouped.setdefault(trial["command_speed_mps"], []).append(trial)
        ordered = []
        commands = list(grouped)
        rng.shuffle(commands)
        for command in commands:
            group = grouped[command]
            rng.shuffle(group)
            ordered.extend(group)
    else:
        rng.shuffle(ordered)
    for index, trial in enumerate(ordered, start=1):
        trial["order_index"] = index
    return ordered


def _inside_domain(points: list[float], domain: ValidSpeedDomain) -> list[float]:
    safe_max = domain.safe_command_speed_max
    return [point for point in points if point >= domain.valid_command_speed_min and safe_max is not None and point <= safe_max]


def _is_positive_finite(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("trials", "rows", "measurements", "extracted_trials"):
                if isinstance(data.get(key), list):
                    return data[key]
        if isinstance(data, list):
            return data
        raise M25ValidationError("invalid_session_file", "JSON session must contain a list of rows")
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def _float_from(row: dict[str, Any], *fields: str) -> float | None:
    for field in fields:
        value = row.get(field)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _repeat_counts(trials: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for trial in trials:
        key = f"{trial['command_speed']:.3f}"
        counts[key] = counts.get(key, 0) + 1
    return counts


def _per_point_uncertainty(trials: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    values: dict[str, list[float]] = {}
    for trial in trials:
        values.setdefault(f"{trial['command_speed']:.3f}", []).append(trial["estimated_actual_speed"])
    result: dict[str, dict[str, Any]] = {}
    for command, actuals in values.items():
        result[command] = {
            "n": len(actuals),
            "mean_actual_speed": statistics.fmean(actuals),
            "std_actual_speed": statistics.stdev(actuals) if len(actuals) >= 2 else 0.0,
        }
    return result
