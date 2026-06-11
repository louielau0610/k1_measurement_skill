"""Booster K1 measurement extractor.

Reads state logs from a K1 measurement session and produces extracted
measurements with velocity and yaw drift statistics.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any


EXTRACTION_SUMMARY_FIELDS = [
    "trial_id",
    "command_velocity",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "extraction_status",
    "n_samples",
    "mean_odom_velocity",
    "std_odom_velocity",
    "notes",
]


class BoosterK1MeasurementExtractor:
    """Extract measurements from Booster K1 state logs.

    Reads per-trial state log CSVs and computes:
    - measured_actual_velocity (from odometer displacement)
    - yaw_drift_statistic (from odometer or IMU yaw)
    """

    platform_id = "booster_k1"
    measurement_source = "ros2_odometer_state"
    measurement_method = "odometer_displacement_over_command_window"

    def extract_trial(self, log_path: Path) -> dict[str, Any]:
        """Extract measurement from a single trial log CSV.

        The log is expected to have columns: timestamp, phase, command_velocity,
        odom_x, odom_y, odom_theta, imu_yaw.
        """
        if not log_path.exists():
            raise FileNotFoundError(f"State log not found: {log_path}")

        with log_path.open(newline="", encoding="utf-8-sig") as f:
            samples = list(csv.DictReader(f))

        if not samples:
            raise ValueError(f"Empty state log: {log_path}")

        return _extract_from_samples(samples, log_path)

    def extract_batch(
        self,
        state_log_dir: Path,
        session_dir: Path,
    ) -> dict[str, Any]:
        """Extract measurements from all state logs in a session directory.

        Returns a summary with output paths and per-trial results.
        """
        state_log_dir = Path(state_log_dir)
        if not state_log_dir.exists():
            raise FileNotFoundError(f"State log directory not found: {state_log_dir}")

        log_files = sorted(state_log_dir.glob("*.csv"))
        if not log_files:
            raise ValueError(f"No CSV log files found in {state_log_dir}")

        extracted: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for log_path in log_files:
            trial_id = log_path.stem
            try:
                result = self.extract_trial(log_path)
                result["trial_id"] = trial_id
                extracted.append(result)
            except Exception as exc:
                errors.append({"trial_id": trial_id, "error": str(exc)})

        # Write extracted measurements CSV
        output_csv = session_dir / "extracted_measurements.csv"
        _write_extracted_csv(output_csv, extracted)

        # Write extraction summary
        summary = {
            "extraction_time": datetime.now(timezone.utc).isoformat(),
            "platform": self.platform_id,
            "measurement_source": self.measurement_source,
            "measurement_method": self.measurement_method,
            "total_logs": len(log_files),
            "successfully_extracted": len(extracted),
            "extraction_errors": len(errors),
            "extracted_measurements_path": str(output_csv),
        }

        summary_path = session_dir / "extraction_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        # Write extraction report (markdown)
        report_path = session_dir / "extraction_report.md"
        report_path.write_text(_build_extraction_report(summary, extracted, errors), encoding="utf-8")

        return summary


def _extract_from_samples(
    samples: list[dict[str, str]], log_path: Path
) -> dict[str, Any]:
    """Core extraction logic from parsed CSV samples."""
    command_samples = [s for s in samples if s.get("phase", "") == "command"]
    if not command_samples:
        # Fallback: use all samples
        command_samples = samples

    # Extract command velocity from first sample
    cmd_vel = float(command_samples[0].get("command_velocity", 0))

    # Compute measured actual velocity from odometer displacement
    odom_x_values = []
    odom_y_values = []
    odom_theta_values = []
    imu_yaw_values = []

    for s in command_samples:
        try:
            odom_x_values.append(float(s.get("odom_x", 0)))
            odom_y_values.append(float(s.get("odom_y", 0)))
            odom_theta_values.append(float(s.get("odom_theta", 0)))
        except (ValueError, TypeError):
            pass
        try:
            imu_yaw_values.append(float(s.get("imu_yaw", 0)))
        except (ValueError, TypeError):
            pass

    if len(odom_x_values) < 2:
        return {
            "command_velocity": cmd_vel,
            "measured_actual_velocity": 0.0,
            "yaw_drift_statistic": 0.0,
            "extraction_status": "insufficient_samples",
            "n_samples": len(odom_x_values),
            "mean_odom_velocity": 0.0,
            "std_odom_velocity": 0.0,
            "notes": f"Only {len(odom_x_values)} position samples in {log_path.name}",
        }

    # Compute displacement-based velocity
    dx_total = odom_x_values[-1] - odom_x_values[0]
    dy_total = odom_y_values[-1] - odom_y_values[0]
    displacement = (dx_total ** 2 + dy_total ** 2) ** 0.5

    # Approximate duration from number of samples (assuming ~10Hz)
    duration = len(odom_x_values) / 10.0
    if duration <= 0:
        duration = 6.0  # default command window

    measured_velocity = displacement / duration

    # Compute yaw drift
    yaw_drift = 0.0
    if len(odom_theta_values) >= 2:
        yaw_drift = abs(odom_theta_values[-1] - odom_theta_values[0])
    elif len(imu_yaw_values) >= 2:
        yaw_drift = abs(imu_yaw_values[-1] - imu_yaw_values[0])

    # Compute per-sample velocity for stats
    sample_velocities = []
    for i in range(1, len(odom_x_values)):
        dx = odom_x_values[i] - odom_x_values[i - 1]
        dy = odom_y_values[i] - odom_y_values[i - 1]
        sample_velocities.append((dx ** 2 + dy ** 2) ** 0.5 * 10.0)  # 10Hz → m/s

    mean_vel = mean(sample_velocities) if sample_velocities else 0.0
    std_vel = stdev(sample_velocities) if len(sample_velocities) >= 2 else 0.0

    return {
        "command_velocity": cmd_vel,
        "measured_actual_velocity": round(measured_velocity, 4),
        "yaw_drift_statistic": round(yaw_drift, 4),
        "extraction_status": "ok",
        "n_samples": len(odom_x_values),
        "mean_odom_velocity": round(mean_vel, 4),
        "std_odom_velocity": round(std_vel, 4),
        "notes": "",
    }


def _write_extracted_csv(
    path: Path, records: list[dict[str, Any]]
) -> None:
    """Write extracted measurements to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXTRACTION_SUMMARY_FIELDS)
        writer.writeheader()
        for record in records:
            row = {k: record.get(k, "") for k in EXTRACTION_SUMMARY_FIELDS}
            writer.writerow(row)


def _build_extraction_report(
    summary: dict[str, Any],
    extracted: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> str:
    """Build a Markdown extraction report."""
    lines = [
        "# Booster K1 Measurement Extraction Report",
        "",
        f"- **Platform**: {summary['platform']}",
        f"- **Measurement source**: {summary['measurement_source']}",
        f"- **Method**: {summary['measurement_method']}",
        f"- **Extraction time**: {summary['extraction_time']}",
        f"- **Total logs processed**: {summary['total_logs']}",
        f"- **Successfully extracted**: {summary['successfully_extracted']}",
        f"- **Extraction errors**: {summary['extraction_errors']}",
        "",
        "## Extracted Measurements",
        "",
    ]

    if extracted:
        lines.append("| Trial ID | v_cmd (m/s) | v_actual (m/s) | Yaw Drift | Status | N Samples |")
        lines.append("|----------|-------------|----------------|-----------|--------|-----------|")
        for rec in extracted:
            lines.append(
                f"| {rec.get('trial_id', '?')} "
                f"| {rec.get('command_velocity', 0):.2f} "
                f"| {rec.get('measured_actual_velocity', 0):.4f} "
                f"| {rec.get('yaw_drift_statistic', 0):.4f} "
                f"| {rec.get('extraction_status', '?')} "
                f"| {rec.get('n_samples', 0)} |"
            )
    else:
        lines.append("_No measurements extracted._")

    if errors:
        lines.append("")
        lines.append("## Extraction Errors")
        lines.append("")
        for err in errors:
            lines.append(f"- **{err['trial_id']}**: {err['error']}")

    return "\n".join(lines) + "\n"
