"""Calibration profile export helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class CalibrationProfileExporter(Protocol):
    def export_json(self, profile: dict[str, Any], output_path: Path) -> None: ...

    def export_markdown(self, profile: dict[str, Any], output_path: Path) -> None: ...


class JsonMarkdownProfileExporter:
    def export_json(self, profile: dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

    def export_markdown(self, profile: dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            f"# Calibration Profile\n\nRobot: `{profile.get('robot_id', 'unknown')}`\n",
            encoding="utf-8",
        )
