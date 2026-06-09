"""Offline analysis for real K1 forward velocity transition trials."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_INPUT_YAML = Path("outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.yaml")
DEFAULT_OUTPUT_CSV = Path("outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.csv")
DEFAULT_OUTPUT_JSON = Path("outputs/real_k1_field_tests/forward_velocity_transition_summary_v0.json")
DEFAULT_OUTPUT_REPORT = Path("reports/real_k1_forward_velocity_analysis_v0.md")
DEFAULT_OUTPUT_PLOT = Path("reports/real_k1_forward_velocity_curve_v0.png")

REQUIRED_TOP_LEVEL_FIELDS = [
    "schema_version",
    "date",
    "platform",
    "environment",
    "command_interface",
    "measurement_scope",
    "trials",
    "preliminary_findings",
    "limitations",
]

EXPECTED_TRIAL_IDS = [
    "vx_0_1_smoke",
    "vx_0_3_transition",
    "vx_0_4_effective",
    "vx_0_5_stable",
    "vx_0_45_transition_upper",
]

CSV_COLUMNS = [
    "trial_id",
    "vx_cmd_mps",
    "duration_s",
    "commanded_distance_m",
    "distance_m",
    "v_actual_est_mps",
    "speed_gain_est",
    "distance_error_m",
    "relative_distance_error",
    "dtheta_rad",
    "abs_dtheta_rad",
    "fall_down_state_post",
    "tracking_category",
    "interpretation",
]


def load_yaml_record(path: str | Path) -> dict[str, Any]:
    """Load the real K1 field-test YAML record."""

    with Path(path).open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError("YAML record must be an object")
    return data


def validate_record(record: dict[str, Any]) -> None:
    """Validate top-level structure and expected trial IDs."""

    missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record]
    if missing:
        raise ValueError(f"missing top-level fields: {missing}")

    trials = record.get("trials")
    if not isinstance(trials, list):
        raise ValueError("trials must be a list")
    if len(trials) != 5:
        raise ValueError("expected exactly 5 trials")

    trial_ids = [trial.get("trial_id") for trial in trials if isinstance(trial, dict)]
    if trial_ids != EXPECTED_TRIAL_IDS:
        raise ValueError(f"unexpected trial IDs or order: {trial_ids}")


def tracking_category(trial: dict[str, Any]) -> str:
    """Assign a coarse response category from observed trial fields."""

    if trial.get("movement_observed") == "almost_none" or trial.get("distance_m") is None:
        return "ineffective_or_deadzone"

    speed_gain = trial.get("speed_gain_est")
    if speed_gain is None:
        return "ineffective_or_deadzone"
    speed_gain = float(speed_gain)

    if speed_gain < 0.6:
        return "weak_response"
    if speed_gain < 0.85:
        return "under_tracking"
    if speed_gain <= 1.15:
        return "stable_tracking"
    return "over_tracking"


def analyze_trial(trial: dict[str, Any]) -> dict[str, Any]:
    """Compute derived metrics for one trial without inventing missing values."""

    analyzed = dict(trial)
    vx_cmd = float(trial["vx_cmd_mps"])
    duration = float(trial["duration_s"])
    commanded_distance = vx_cmd * duration
    distance = trial.get("distance_m")
    dtheta = trial.get("dtheta_rad")

    analyzed["commanded_distance_m"] = commanded_distance
    analyzed["distance_error_m"] = None if distance is None else float(distance) - commanded_distance
    analyzed["relative_distance_error"] = (
        None if analyzed["distance_error_m"] is None else analyzed["distance_error_m"] / commanded_distance
    )
    analyzed["abs_dtheta_rad"] = None if dtheta is None else abs(float(dtheta))
    analyzed["tracking_category"] = tracking_category(trial)
    return analyzed


def analyze_record(record: dict[str, Any]) -> dict[str, Any]:
    """Build analyzed trial rows and summary metrics."""

    validate_record(record)
    trials = [analyze_trial(trial) for trial in record["trials"]]
    valid_gain_trials = [trial for trial in trials if trial.get("speed_gain_est") is not None]
    valid_yaw_trials = [trial for trial in trials if trial.get("abs_dtheta_rad") is not None]
    best_tracking = min(
        valid_gain_trials,
        key=lambda trial: abs(float(trial["speed_gain_est"]) - 1.0),
    )
    highest_yaw = max(valid_yaw_trials, key=lambda trial: float(trial["abs_dtheta_rad"]))
    findings = record["preliminary_findings"]

    return {
        "metadata": {
            "schema_version": record["schema_version"],
            "date": record["date"],
            "platform": record["platform"],
            "environment": record["environment"],
            "command_interface": record["command_interface"],
            "measurement_scope": record["measurement_scope"],
        },
        "analyzed_trials": trials,
        "first_effective_command_speed_mps": findings.get("first_effective_vx_cmd_mps"),
        "stable_tracking_region": findings.get("stable_tracking_region_mps"),
        "best_tracking_trial": {
            "trial_id": best_tracking["trial_id"],
            "vx_cmd_mps": best_tracking["vx_cmd_mps"],
            "speed_gain_est": best_tracking["speed_gain_est"],
            "abs_speed_gain_error": abs(float(best_tracking["speed_gain_est"]) - 1.0),
        },
        "highest_yaw_drift_trial": {
            "trial_id": highest_yaw["trial_id"],
            "vx_cmd_mps": highest_yaw["vx_cmd_mps"],
            "dtheta_rad": highest_yaw["dtheta_rad"],
            "abs_dtheta_rad": highest_yaw["abs_dtheta_rad"],
        },
        "modeling_recommendation": {
            "global_gain_model_recommended": findings.get("global_gain_model_recommended"),
            "recommended_model": findings.get("recommended_model"),
            "notes": [
                "A single global proportional gain is not appropriate.",
                "Use a piecewise or nonlinear mapping for low-speed transition behavior.",
                "Commands below the observed effective threshold should be low-confidence or avoided in navigation.",
            ],
        },
        "limitations": record["limitations"],
    }


def _format_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return value


def write_csv(trials: list[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for trial in trials:
            writer.writerow({column: _format_csv_value(trial.get(column)) for column in CSV_COLUMNS})


def write_json(summary: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def render_markdown_report(summary: dict[str, Any]) -> str:
    metadata = summary["metadata"]
    trials = summary["analyzed_trials"]
    removed = metadata["measurement_scope"].get("removed_or_optional", {})
    battery_status = removed.get("battery_state", {}).get("status", "unknown")
    remote_status = removed.get("remote_controller_state", {}).get("status", "unknown")

    lines = [
        "# Real K1 Forward Velocity Analysis v0 / K1 实机前进速度分析 v0",
        "",
        "## 实验输入",
        "",
        f"- date: `{metadata['date']}`",
        f"- platform: `{metadata['platform']}`",
        f"- floor_type: `{metadata['environment'].get('floor_type')}`",
        f"- condition: `{metadata['environment'].get('condition')}`",
        f"- SDK client: `{metadata['command_interface'].get('client')}`",
        "",
        "## 数据来源",
        "",
        "- Input YAML: `outputs/real_k1_field_tests/forward_velocity_transition_trials_v0.yaml`",
        "- This is an offline measurement analysis artifact.",
        f"- `battery_state` is `{battery_status}`.",
        f"- `remote_controller_state` is `{remote_status}` from measurement scope.",
        "",
        "## 速度响应表",
        "",
        "| trial_id | vx_cmd | v_actual_est | speed_gain | distance_error | rel_error | abs_dtheta | category |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for trial in trials:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(trial["trial_id"]),
                    _fmt(trial.get("vx_cmd_mps")),
                    _fmt(trial.get("v_actual_est_mps")),
                    _fmt(trial.get("speed_gain_est")),
                    _fmt(trial.get("distance_error_m")),
                    _fmt(trial.get("relative_distance_error")),
                    _fmt(trial.get("abs_dtheta_rad")),
                    str(trial.get("tracking_category")),
                ]
            )
            + " |"
        )

    best = summary["best_tracking_trial"]
    yaw = summary["highest_yaw_drift_trial"]
    lines.extend(
        [
            "",
            "## 低速死区判断",
            "",
            "- `0.1 m/s` was ineffective.",
            "- `0.3 m/s` was first clearly effective but weak.",
            "- Preliminary first effective speed is around `0.3 m/s`.",
            "",
            "## tracking gain 分析",
            "",
            "- `0.4 m/s` was effective but under-tracking.",
            "- `0.45 m/s` was near stable tracking but had larger yaw drift and should be repeated.",
            "- `0.5 m/s` showed stable tracking with speed gain near 1.",
            f"- Best tracking trial by gain error: `{best['trial_id']}` with speed_gain `{best['speed_gain_est']}`.",
            "",
            "## yaw drift 分析",
            "",
            f"- Highest yaw drift trial: `{yaw['trial_id']}` with abs_dtheta `{_fmt(yaw['abs_dtheta_rad'])}` rad.",
            "- The `0.45 m/s` trial should be repeated because yaw drift was larger than neighboring trials.",
            "",
            "## 建模启示",
            "",
            "- A single global proportional gain is not appropriate.",
            "- A piecewise or nonlinear mapping is recommended.",
            "- Low-speed commands below the observed effective threshold should be treated as low-confidence or avoided in navigation.",
            "- Compensation should not simply scale all commands by one constant.",
            "",
            "## 当前限制",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["limitations"])
    lines.extend(
        [
            "",
            "## 下一步建议",
            "",
            "- Repeat `vx_cmd = 0.45` to check yaw drift stability.",
            "- Repeat `vx_cmd = 0.4` and `0.5` for variance estimation.",
            "- Add structured real log capture instead of ad-hoc `ros2 topic echo --once`.",
            "- Build first velocity profile from repeated trials.",
            "- Later test additional floor types after lab hard floor is stable.",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown_report(summary: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown_report(summary), encoding="utf-8")


def write_plot(trials: list[dict[str, Any]], path: str | Path) -> None:
    """Write one matplotlib figure with command reference and observed valid points."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    valid_trials = [
        trial
        for trial in trials
        if trial.get("v_actual_est_mps") is not None and trial.get("vx_cmd_mps") is not None
    ]
    x = [float(trial["vx_cmd_mps"]) for trial in valid_trials]
    y = [float(trial["v_actual_est_mps"]) for trial in valid_trials]
    reference = sorted(set(x + y + [0.0]))

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(reference, reference, linestyle="--", label="command reference y=x")
    ax.scatter(x, y, label="observed valid trials")
    ax.plot(x, y, linestyle="-", alpha=0.5)
    ax.set_xlabel("vx_cmd_mps")
    ax.set_ylabel("v_actual_est_mps")
    ax.set_title("Real K1 Forward Velocity Response v0")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def run_analysis(
    input_yaml: str | Path = DEFAULT_INPUT_YAML,
    output_csv: str | Path = DEFAULT_OUTPUT_CSV,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_report: str | Path = DEFAULT_OUTPUT_REPORT,
    output_plot: str | Path = DEFAULT_OUTPUT_PLOT,
) -> dict[str, Any]:
    record = load_yaml_record(input_yaml)
    summary = analyze_record(record)
    write_csv(summary["analyzed_trials"], output_csv)
    write_json(summary, output_json)
    write_markdown_report(summary, output_report)
    write_plot(summary["analyzed_trials"], output_plot)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze real K1 forward velocity transition trials.")
    parser.add_argument("--input-yaml", default=str(DEFAULT_INPUT_YAML))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-report", default=str(DEFAULT_OUTPUT_REPORT))
    parser.add_argument("--output-plot", default=str(DEFAULT_OUTPUT_PLOT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_analysis(
        input_yaml=args.input_yaml,
        output_csv=args.output_csv,
        output_json=args.output_json,
        output_report=args.output_report,
        output_plot=args.output_plot,
    )
    print("Real K1 forward velocity analysis complete.")
    print(f"Trials analyzed: {len(summary['analyzed_trials'])}")
    print(f"Best tracking trial: {summary['best_tracking_trial']['trial_id']}")
    print(f"Highest yaw drift trial: {summary['highest_yaw_drift_trial']['trial_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
