"""Platform-agnostic measurement extraction interface."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class MeasurementExtractor(Protocol):
    def extract_trial(self, log_path: Path, analysis_window: tuple[float, float]) -> dict[str, Any]: ...

    def extract_batch(self, log_dir: Path) -> list[dict[str, Any]]: ...
