"""Shared risk-region classifier wrapper."""
from __future__ import annotations

from typing import Any


def classify_calibration_region(record: dict[str, Any], thresholds: dict[str, float] | None = None) -> str:
    from scripts.classify_m19c_risk_regions import classify_region as classify_m19c_region

    return classify_m19c_region(record, thresholds)


classify_region = classify_calibration_region
