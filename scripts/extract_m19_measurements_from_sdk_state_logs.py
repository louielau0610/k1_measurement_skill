"""Extract M19 measurement annotations from SDK state logs when data is sufficient."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

OUTPUT_CSV = Path("data/m19_repeated_validation_inputs/m19_sdk_extracted_measurements.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
DEFAULT_LOG_DIR = Path("data/m19_sdk_state_logs")
WINDOW_START_SEC = 1.0
WINDOW_END_SEC = 6.0

OUTPUT_FIELDS = [
    "trial_id",
    "measurement_source",
    "measurement_method",
    "distance_m",
    "time_sec",
    "measured_actual_velocity",
    "start_yaw_deg",
    "end_yaw_deg",
    "yaw_drift_statistic",
    "measurement_confidence",
    "annotation_notes",
]


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def yaw_to_deg(row: dict[str, str]) -> float | None:
    yaw_deg = parse_float(row.get("yaw_deg"))
    if yaw_deg is not None:
        return yaw_deg
    yaw_rad = parse_float(row.get("yaw_rad"))
    if yaw_rad is not None:
        return math.degrees(yaw_rad)
    return None


def wrapped_yaw_diff_deg(start_deg: float, end_deg: float) -> float:
    """Return smallest signed yaw difference in degrees."""
    return (end_deg - start_deg + 180.0) % 360.0 - 180.0


def forward_displacement_m(start: dict[str, float], end: dict[str, float], start_yaw_deg: float) -> float:
    dx = end["x"] - start["x"]
    dy = end["y"] - start["y"]
    yaw = math.radians(start_yaw_deg)
    return dx * math.cos(yaw) + dy * math.sin(yaw)


def select_window(samples: list[dict[str, str]], start_sec: float, end_sec: float) -> list[dict[str, str]]:
    selected = []
    for row in samples:
        t_rel = parse_float(row.get("t_rel"))
        if t_rel is None:
            continue
        if start_sec <= t_rel <= end_sec:
            selected.append(row)
    selected.sort(key=lambda row: parse_float(row.get("t_rel")) or 0.0)
    return selected


def extract_trial_measurement(samples: list[dict[str, str]], start_sec: float = WINDOW_START_SEC, end_sec: float = WINDOW_END_SEC) -> tuple[dict[str, Any] | None, str | None]:
    window = select_window(samples, start_sec, end_sec)
    usable = []
    for row in window:
        x = parse_float(row.get("x"))
        y = parse_float(row.get("y"))
        yaw = yaw_to_deg(row)
        t_rel = parse_float(row.get("t_rel"))
        if x is None or y is None or yaw is None or t_rel is None:
            continue
        usable.append({"t_rel": t_rel, "x": x, "y": y, "yaw_deg": yaw})
    if len(usable) < 2:
        return None, "insufficient_position_or_yaw_samples"
    start = usable[0]
    end = usable[-1]
    time_sec = end["t_rel"] - start["t_rel"]
    if time_sec <= 0:
        return None, "nonpositive_analysis_window_duration"
    distance = forward_displacement_m(start, end, start["yaw_deg"])
    yaw_drift = abs(wrapped_yaw_diff_deg(start["yaw_deg"], end["yaw_deg"]))
    return {
        "distance_m": distance,
        "time_sec": time_sec,
        "measured_actual_velocity": distance / time_sec,
        "start_yaw_deg": start["yaw_deg"],
        "end_yaw_deg": end["yaw_deg"],
        "yaw_drift_statistic": yaw_drift,
    }, None


def read_log_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def discover_log_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if not input_path.exists():
        return []
    return sorted(input_path.glob("*.csv"))


def extract_from_logs(input_path: Path, output_csv: Path = OUTPUT_CSV, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    log_files = discover_log_files(input_path)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in log_files:
        for row in read_log_csv(path):
            trial_id = row.get("trial_id") or path.stem
            row["trial_id"] = trial_id
            grouped[trial_id].append(row)

    output_rows = []
    blocked = []
    for trial_id in sorted(grouped):
        measurement, reason = extract_trial_measurement(grouped[trial_id])
        if measurement is None:
            blocked.append({"trial_id": trial_id, "reason": reason})
            continue
        output_rows.append(
            {
                "trial_id": trial_id,
                "measurement_source": "sdk_state_log",
                "measurement_method": "forward_projection_window_1_6s",
                "distance_m": measurement["distance_m"],
                "time_sec": measurement["time_sec"],
                "measured_actual_velocity": measurement["measured_actual_velocity"],
                "start_yaw_deg": measurement["start_yaw_deg"],
                "end_yaw_deg": measurement["end_yaw_deg"],
                "yaw_drift_statistic": measurement["yaw_drift_statistic"],
                "measurement_confidence": "high",
                "annotation_notes": "extracted_from_sdk_state_log",
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "input_path": str(input_path),
        "log_files_found": len(log_files),
        "trials_seen": len(grouped),
        "measurements_extracted": len(output_rows),
        "blocked_trials": blocked,
        "output_csv": str(output_csv),
        "statistics_computed": False,
        "empirical_response_analysis_blocked": len(output_rows) == 0,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19_sdk_extraction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report = (
        "# M19 SDK Measurement Extraction Report\n\n"
        f"Input path: `{input_path}`\n\n"
        f"Log files found: {summary['log_files_found']}\n\n"
        f"Trials seen: {summary['trials_seen']}\n\n"
        f"Measurements extracted: {summary['measurements_extracted']}\n\n"
        f"Blocked trials: {len(blocked)}\n\n"
        "No empirical response statistics are computed by this extractor.\n"
    )
    (output_dir / "m19_sdk_extraction_report.md").write_text(report, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = extract_from_logs(args.input, args.output_csv, args.output_dir)
    print(f"M19 SDK extraction measurements_extracted={summary['measurements_extracted']}")
    print(f"M19 SDK extraction output={summary['output_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
