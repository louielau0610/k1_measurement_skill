"""M19-A Repeated Validation Analyzer — pending-data mode when no real logs exist."""
from __future__ import annotations
from dataclasses import asdict
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from k1_measurement.m19_validation_schema import (
    ValidationSummary, PerCommandAggregate, REGION_LABELS, EVIDENCE_LEVELS,
)

INPUT_DIR = Path("data/m19_repeated_validation_inputs")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
COMMAND_VELOCITIES = [0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]

DEFAULT_WEIGHTS = {"alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0}
# Conservative thresholds
DEADZONE_VELOCITY_THRESHOLD = 0.02      # m/s — actual velocity below this = deadzone
UNDER_TRACK_ERROR_THRESHOLD = 0.05       # m/s — tracking error above this = under-track
YAW_DRIFT_HIGH_THRESHOLD = 2.0           # deg/s — yaw drift above this = drift-prone
MIN_VALID_TRIALS_FOR_CLASSIFICATION = 3
MIN_VALID_TRIALS_FOR_RELIABLE = 3

def discover_records(input_dir: Path) -> list[dict]:
    """Discover JSON trial records from input directory."""
    records = []
    if not input_dir.exists():
        return records
    for f in sorted(input_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict) and "trial_id" in data:
                records.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return records

def is_real_evidence(record: dict) -> bool:
    """Reject dummy, simulated, synthetic, test-fixture records."""
    flags = [
        record.get("evidence_type", ""),
        record.get("data_source", ""),
        record.get("trial_id", ""),
    ]
    reject_keywords = ["dummy", "simulated", "synthetic", "test_fixture", "test-fixture", "fixture"]
    for flag in flags:
        if any(kw in str(flag).lower() for kw in reject_keywords):
            return False
    return True

def compute_per_command(records: list[dict], cmd: float, weights: dict) -> PerCommandAggregate:
    """Compute aggregate statistics for one command velocity."""
    matches = [r for r in records if abs(r.get("command_velocity", 0) - cmd) < 0.001]
    valid = [r for r in matches if r.get("valid", False)]
    n_total = len(matches)
    n_valid = len(valid)
    actuals = [r["measured_actual_velocity"] for r in valid if r.get("measured_actual_velocity") is not None]
    yaws = [r.get("yaw_drift_statistic", 0.0) or 0.0 for r in valid]

    mean_actual = sum(actuals) / len(actuals) if actuals else None
    std_actual = (sum((a - mean_actual) ** 2 for a in actuals) / len(actuals)) ** 0.5 if actuals and mean_actual else None
    mean_tracking = mean_actual - cmd if mean_actual is not None else None
    abs_mean_tracking = abs(mean_tracking) if mean_tracking is not None else None
    no_motion_ratio = sum(1 for a in actuals if a < DEADZONE_VELOCITY_THRESHOLD) / len(actuals) if actuals else 0.0
    mean_yaw = sum(yaws) / len(yaws) if yaws else None
    yaw_risk = 1.0 if mean_yaw and abs(mean_yaw) > YAW_DRIFT_HIGH_THRESHOLD else 0.0
    uncertainty = std_actual if std_actual else 1.0

    deadzone_indicator = 1.0 if no_motion_ratio > 0.5 else 0.0
    risk_score = (
        weights["alpha"] * (abs_mean_tracking or 0.0) +
        weights["beta"] * (uncertainty or 1.0) +
        weights["gamma"] * deadzone_indicator +
        weights["delta"] * yaw_risk
    )

    # Conservative region classification
    if n_valid < MIN_VALID_TRIALS_FOR_CLASSIFICATION and n_valid > 0:
        region = "insufficient_evidence"
    elif deadzone_indicator > 0.5:
        region = "deadzone"
    elif yaw_risk > 0.5 and (abs_mean_tracking or 0) < UNDER_TRACK_ERROR_THRESHOLD:
        region = "drift_prone"
    elif abs_mean_tracking and abs_mean_tracking > UNDER_TRACK_ERROR_THRESHOLD and deadzone_indicator < 0.5:
        region = "under_track"
    elif n_valid >= MIN_VALID_TRIALS_FOR_RELIABLE and abs_mean_tracking and abs_mean_tracking <= UNDER_TRACK_ERROR_THRESHOLD and yaw_risk < 0.5 and deadzone_indicator < 0.5:
        region = "reliable"
    else:
        region = "insufficient_evidence"

    evidence = "real_repeated" if n_valid >= 3 else "real_single_or_sparse"

    return PerCommandAggregate(
        command_velocity=cmd, n_total=n_total, n_valid=n_valid,
        mean_actual_velocity=mean_actual, std_actual_velocity=std_actual,
        mean_tracking_error=mean_tracking, abs_mean_tracking_error=abs_mean_tracking,
        no_motion_ratio=no_motion_ratio, mean_yaw_drift=mean_yaw,
        yaw_drift_risk=yaw_risk, uncertainty=uncertainty or 0.0,
        risk_score=risk_score, region_label=region, evidence_level=evidence,
    )

def run_pending_mode(weights: dict) -> ValidationSummary:
    """Generate a pending-mode summary when no real logs exist."""
    per_command = []
    for cmd in COMMAND_VELOCITIES:
        per_command.append(asdict(PerCommandAggregate(
            command_velocity=cmd, n_total=0, n_valid=0,
            mean_actual_velocity=None, std_actual_velocity=None,
            mean_tracking_error=None, abs_mean_tracking_error=None,
            no_motion_ratio=0.0, mean_yaw_drift=None,
            yaw_drift_risk=0.0, uncertainty=0.0, risk_score=0.0,
            region_label="pending_real_data", evidence_level="pending_real_data",
        )))
    return ValidationSummary(
        analysis_timestamp=datetime.now().isoformat(),
        mode="pending_data", total_trials=0, total_valid=0,
        commands_evaluated=0, commands_pending=len(COMMAND_VELOCITIES),
        per_command=per_command,
        notes="No real repeated K1 logs found. Infrastructure ready for future data ingestion.",
        real_repeated_logs_found=False,
    )

def main():
    weights = DEFAULT_WEIGHTS.copy()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = discover_records(INPUT_DIR)
    real_records = [r for r in records if is_real_evidence(r)]

    if not real_records or not any(r.get("valid") for r in real_records):
        print("M19-A: No valid real repeated K1 records found. Running in pending-data mode.")
        summary = run_pending_mode(weights)
    else:
        print(f"M19-A: Found {len(real_records)} real records. Processing...")
        per_command = [compute_per_command(real_records, cmd, weights) for cmd in COMMAND_VELOCITIES]
        valid_cmds = [c for c in per_command if c.n_valid > 0]
        summary = ValidationSummary(
            analysis_timestamp=datetime.now().isoformat(),
            mode="real_data", total_trials=len(real_records),
            total_valid=sum(c.n_valid for c in per_command),
            commands_evaluated=len(valid_cmds),
            commands_pending=len(COMMAND_VELOCITIES) - len(valid_cmds),
            per_command=[asdict(c) for c in per_command],
            real_repeated_logs_found=True,
        )

    summary.to_json(str(OUTPUT_DIR / "repeated_validation_summary.json"))
    # Write pending marker
    (OUTPUT_DIR / "m19_validation_report.md").write_text(
        f"# M19-A Validation Report\n\nMode: {summary.mode}\nTrials: {summary.total_trials}\n"
        f"Valid: {summary.total_valid}\nCommands evaluated: {summary.commands_evaluated}\n"
        f"Commands pending: {summary.commands_pending}\n\n{summary.notes}\n",
        encoding="utf-8",
    )
    print(f"Summary written to {OUTPUT_DIR / 'repeated_validation_summary.json'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
