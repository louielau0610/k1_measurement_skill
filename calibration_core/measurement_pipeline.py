"""Orchestration scaffold for the measurement module."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from calibration_core.profile_exporter import JsonMarkdownProfileExporter
from calibration_core.response_analyzer import summarize_response
from calibration_core.trial_scheduler import TrialScheduler, TrialSpec


StageCallable = Callable[..., Any]


@dataclass
class MeasurementPipeline:
    """Hardware-optional measurement pipeline orchestration.

    The default implementation plans deterministically and records stage
    boundaries. Hardware execution and platform-specific extraction are injected
    by callers when running on a real robot.
    """

    platform: str
    robot_model: str
    scheduler: TrialScheduler = field(default_factory=TrialScheduler)
    runner: StageCallable | None = None
    extractor: StageCallable | None = None
    qc_runner: StageCallable | None = None
    response_analyzer: StageCallable | None = None
    profile_exporter: JsonMarkdownProfileExporter = field(default_factory=JsonMarkdownProfileExporter)

    def plan_trials(
        self,
        surfaces: list[str],
        speeds: list[float],
        repeats: int,
        *,
        prefix: str = "CAL",
        block_order: list[list[float]] | None = None,
    ) -> list[TrialSpec]:
        return self.scheduler.build_trials(
            surfaces,
            speeds,
            repeats,
            block_order=block_order,
            platform=self.platform,
            prefix=prefix,
        )

    def run_trials(self, trials: list[TrialSpec], *, dry_run: bool = True, **kwargs: Any) -> dict[str, Any]:
        if self.runner is None or dry_run:
            return {
                "stage": "run_trials",
                "platform": self.platform,
                "trial_count": len(trials),
                "dry_run": True,
                "hardware_executed": False,
            }
        return self.runner(trials=trials, **kwargs)

    def extract_measurements(self, input_path: Path, output_path: Path, **kwargs: Any) -> dict[str, Any]:
        if self.extractor is None:
            return {
                "stage": "extract_measurements",
                "platform": self.platform,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "extracted": False,
                "reason": "no extractor configured",
            }
        return self.extractor(input_path=input_path, output_path=output_path, **kwargs)

    def run_qc(self, measurements_path: Path, **kwargs: Any) -> dict[str, Any]:
        if self.qc_runner is None:
            return {
                "stage": "run_qc",
                "platform": self.platform,
                "measurements_path": str(measurements_path),
                "qc_executed": False,
                "reason": "no qc runner configured",
            }
        return self.qc_runner(measurements_path=measurements_path, **kwargs)

    def analyze_response(self, records: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        if self.response_analyzer is not None:
            return self.response_analyzer(records=records, **kwargs)
        return {"stage": "analyze_response", "platform": self.platform, **summarize_response(records)}

    def export_profile(self, profile: dict[str, Any], json_path: Path, markdown_path: Path | None = None) -> dict[str, Any]:
        self.profile_exporter.export_json(profile, json_path)
        if markdown_path is not None:
            self.profile_exporter.export_markdown(profile, markdown_path)
        return {
            "stage": "export_profile",
            "platform": self.platform,
            "json_path": str(json_path),
            "markdown_path": str(markdown_path) if markdown_path else None,
        }
