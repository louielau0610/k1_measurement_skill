"""Cross-platform calibration skill core."""

from calibration_core.command_adapter import RobotCommandAdapter
from calibration_core.compensation_models import CompensationDecision, CompensationRequest, MonotonicSegment, ResponseCell
from calibration_core.measurement_extractor import MeasurementExtractor
from calibration_core.measurement_manifest import MeasurementManifest, validate_measurement_manifest
from calibration_core.measurement_pipeline import MeasurementPipeline
from calibration_core.measurement_schema import TrialMeasurement, validate_aggregate_record, validate_trial_measurement
from calibration_core.platform_registry import PlatformEntry, get_platform, get_platform_registry, list_platforms
from calibration_core.profile_exporter import CalibrationProfileExporter, JsonMarkdownProfileExporter
from calibration_core.profile_loader import load_k1_gold_profile, load_profile
from calibration_core.response_analyzer import summarize_response
from calibration_core.risk_classifier import classify_calibration_region
from calibration_core.state_logger import RobotStateLogger
from calibration_core.trial_scheduler import TrialScheduler, TrialSpec
from calibration_core.velocity_compensation import compensate_velocity

__all__ = [
    "CalibrationProfileExporter",
    "CompensationDecision",
    "CompensationRequest",
    "JsonMarkdownProfileExporter",
    "MeasurementExtractor",
    "MeasurementManifest",
    "MeasurementPipeline",
    "MonotonicSegment",
    "PlatformEntry",
    "ResponseCell",
    "RobotCommandAdapter",
    "RobotStateLogger",
    "TrialMeasurement",
    "TrialScheduler",
    "TrialSpec",
    "classify_calibration_region",
    "compensate_velocity",
    "get_platform",
    "get_platform_registry",
    "list_platforms",
    "load_k1_gold_profile",
    "load_profile",
    "summarize_response",
    "validate_aggregate_record",
    "validate_measurement_manifest",
    "validate_trial_measurement",
]
