"""Booster K1 odometer measurement extraction wrapper."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from scripts.extract_m19_measurements_from_ros2_odometer_logs import extract_from_logs, extract_trial_measurement


class BoosterK1OdometerExtractor:
    platform_id = "booster_k1"
    measurement_source = "ros2_odometer_state"

    def extract_trial(self, log_path: Path) -> dict[str, Any]:
        with log_path.open(newline="", encoding="utf-8-sig") as f:
            samples = list(csv.DictReader(f))
        measurement, reason = extract_trial_measurement(samples)
        if measurement is None:
            raise ValueError(f"unable to extract Booster K1 odometer measurement: {reason}")
        return measurement

    def extract_batch(self, log_dir: Path, output_csv: Path, output_dir: Path) -> dict[str, Any]:
        return extract_from_logs(log_dir, output_csv, output_dir)
