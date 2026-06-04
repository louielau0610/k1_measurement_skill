"""Markdown report generation for K1 measurement profiles."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any


DUMMY_WARNING_TEXT = "Dummy data only"


def load_profile(profile_path: str) -> dict[str, Any]:
    """Load a processed environment profile JSON file."""

    path = Path(profile_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            profile = json.load(file)
    except FileNotFoundError:
        raise
    except JSONDecodeError as exc:
        raise ValueError(f"invalid profile JSON: {exc}") from exc

    if not isinstance(profile, dict):
        raise ValueError("profile JSON must contain an object")
    return profile


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _format_number(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.6g}"
    return str(value)


def _warnings(profile: dict[str, Any]) -> list[str]:
    warnings = profile.get("quality", {}).get("warnings", [])
    if isinstance(warnings, list):
        return [str(item) for item in warnings]
    return [str(warnings)]


def _contains_dummy_warning(profile: dict[str, Any]) -> bool:
    return any(DUMMY_WARNING_TEXT.lower() in warning.lower() for warning in _warnings(profile))


def generate_markdown_report(profile: dict[str, Any]) -> str:
    """Generate a Chinese-first Markdown measurement report."""

    metadata = profile.get("metadata", {})
    environment = profile.get("environment", {})
    valid_range = profile.get("valid_speed_range", {})
    velocity_profile = profile.get("velocity_profile", [])
    quality = profile.get("quality", {})
    downstream = profile.get("downstream_usage", {})
    warnings = _warnings(profile)
    is_dummy = _contains_dummy_warning(profile)

    lines: list[str] = [
        "# K1 Measurement Report",
        "",
        "## 数据声明",
        "",
        "本报告由 `processed_environment_profile.json` 生成，属于测量阶段输出摘要。",
    ]
    if is_dummy:
        lines.extend(
            [
                "",
                "**警告：该 profile 包含 dummy-data warning，因此本报告不是真实 K1 测量结果。**",
                "",
                "Dummy report 不得用于速度补偿、导航或任何机器人安全决策。",
            ]
        )
    else:
        lines.append("如果输入 profile 来自真实实验，仍需人工检查置信度、环境标签和 warnings。")

    lines.extend(
        [
            "",
            "## 实验元数据",
            "",
            f"- robot: {metadata.get('robot', 'unknown')}",
            f"- skill_version: {metadata.get('skill_version', 'unknown')}",
            f"- experiment_name: {metadata.get('experiment_name', 'unknown')}",
            f"- profile_id: {metadata.get('profile_id', 'unknown')}",
            f"- created_at: {metadata.get('created_at', 'unknown')}",
            f"- repository_role: {metadata.get('repository_role', 'unknown')}",
            f"- full_project: {metadata.get('full_project', 'unknown')}",
            f"- schema_version: {profile.get('schema_version', 'unknown')}",
            "",
            "## 环境标签",
            "",
            f"- floor_type: {environment.get('floor_type', 'unknown')}",
            f"- condition: {environment.get('condition', 'unknown')}",
            f"- slope: {environment.get('slope', 'unknown')}",
            f"- notes: {environment.get('notes', '')}",
            "",
            "## 有效速度范围",
            "",
            f"- min_vx_cmd_mps: {valid_range.get('min_vx_cmd_mps', 'unknown')}",
            f"- max_vx_cmd_mps: {valid_range.get('max_vx_cmd_mps', 'unknown')}",
            "",
            "## 速度画像摘要",
            "",
            "| v_x_cmd (m/s) | v_x_actual_mean (m/s) | v_x_actual_std (m/s) | speed_gain_mean | speed_gain_std | absolute_error_mean (m/s) | relative_error_mean | n_trials |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for point in velocity_profile:
        lines.append(
            "| "
            + " | ".join(
                [
                    _format_number(point.get("vx_cmd_mps", "")),
                    _format_number(point.get("vx_actual_mean_mps", "")),
                    _format_number(point.get("vx_actual_std_mps", "")),
                    _format_number(point.get("speed_gain_mean", "")),
                    _format_number(point.get("speed_gain_std", "")),
                    _format_number(point.get("absolute_error_mean_mps", "")),
                    _format_number(point.get("relative_error_mean", "")),
                    str(point.get("n_trials", "")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 质量与置信度",
            "",
            f"- confidence: {quality.get('confidence', 'unknown')}",
            f"- ground_truth_method: {quality.get('ground_truth_method', 'unknown')}",
            f"- odom_validated: {_bool_text(quality.get('odom_validated', 'unknown'))}",
            "- warnings:",
        ]
    )
    lines.extend([f"  - {warning}" for warning in warnings] or ["  - none"])

    lines.extend(
        [
            "",
            "## 下游使用说明",
            "",
            f"- recommended_for_compensation: {_bool_text(downstream.get('recommended_for_compensation', 'unknown'))}",
            f"- extrapolation_allowed: {_bool_text(downstream.get('extrapolation_allowed', 'unknown'))}",
            f"- downstream notes: {downstream.get('notes', '')}",
            "",
            "本仓库不实现 velocity compensation。",
            "下游模块必须检查 environment match、valid speed range、confidence、n_trials 和 extrapolation risk。",
            "如果 `recommended_for_compensation` 为 false，下游补偿模块不得使用该 profile。",
            "",
            "## 局限性",
            "",
            "- odom 未经外部验证前不能视为 ground truth。",
            "- dummy data 不能代表真实 K1 行为。",
            "- 当前 shell 中 M4.5 未检测到 ROS2，因此没有真实 ROS2 topic 被验证。",
            "- 当前流程没有执行真实机器人运动。",
            "- 本仓库没有实现 compensation model。",
            "",
            "## 下一步",
            "",
            "- 在 ROS2 可用的 K1 shell 中重新运行 M4.5。",
            "- 识别 odom / imu / robot_state topics。",
            "- 使用静止机器人数据验证 logger。",
            "- 使用人工控制行走数据验证 logger。",
            "- 完成上述验证后，才考虑低速真实测量实验。",
            "",
        ]
    )
    return "\n".join(lines)


def save_markdown_report(report: str, output_path: str) -> None:
    """Save Markdown report as UTF-8."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def generate_report_from_profile(profile_path: str, output_path: str) -> str:
    """Load profile, generate report, save report, and return output path."""

    profile = load_profile(profile_path)
    report = generate_markdown_report(profile)
    save_markdown_report(report, output_path)
    return str(output_path)


def render_markdown_summary(profile: dict[str, Any]) -> str:
    """Backward-compatible alias for older callers."""

    return generate_markdown_report(profile)
