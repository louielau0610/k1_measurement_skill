"""Consolidate M13-M16 research pipeline artifacts for M17 reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


EVALUATION_NAME = "research_pipeline_evaluation_v1"


@dataclass(frozen=True)
class ResearchPipelineArtifact:
    path: str
    artifact_type: str
    milestone: str
    exists: bool
    reproducible_by_script: bool
    producer_script: str | None
    description: str
    limitations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResearchPipelineEvaluation:
    evaluation_name: str
    artifacts_count: int
    missing_artifacts_count: int
    dataset_records_count: int
    response_predictions_count: int
    risk_assessments_count: int
    supported_claims: list[str]
    non_claims: list[str]
    available_metrics: list[str]
    unavailable_metrics: list[str]
    limitations: list[str]
    next_experiments: list[str]
    safety_flags: dict[str, Any]
    metrics: dict[str, Any] = field(default_factory=dict)


def load_json(path: str | Path) -> dict[str, Any]:
    payload_path = Path(path)
    with payload_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {payload_path}")
    return payload


def collect_research_artifacts(repo_root: str | Path = ".") -> list[ResearchPipelineArtifact]:
    root = Path(repo_root)
    specs = [
        ("configs/velocity_response_dataset_schema_v1.json", "schema", "M13", False, None, "Velocity response dataset schema v1", []),
        ("outputs/research_datasets/velocity_response_dataset_v1.json", "dataset", "M14", True, "scripts/build_velocity_response_dataset_v1.py", "Velocity response dataset v1", ["single robot", "single environment", "sparse command samples"]),
        ("outputs/research_datasets/velocity_response_dataset_v1_validation_report.json", "validation_report", "M14", True, "scripts/build_velocity_response_dataset_v1.py", "Dataset validation report", []),
        ("outputs/research_models/response_model_predictions_v1.json", "prediction_output", "M15R", True, "scripts/run_velocity_response_model_v1.py", "Response model predictions", ["uncertainty labels are not calibrated probabilities"]),
        ("outputs/research_models/response_model_evaluation_v1.json", "evaluation_output", "M15R", True, "scripts/run_velocity_response_model_v1.py", "Response model structural evaluation", ["exact-source reconstruction is not performance evidence"]),
        ("outputs/research_risk/navigation_risk_map_v1.json", "risk_map", "M16", True, "scripts/run_navigation_risk_mapping_v1.py", "Offline navigation risk map", ["advisory only", "no navigation outcomes"]),
        ("outputs/research_risk/navigation_risk_evaluation_v1.json", "risk_evaluation", "M16", True, "scripts/run_navigation_risk_mapping_v1.py", "Risk-map structural evaluation", ["no collision, near-miss, or success-rate metrics"]),
        ("paper/claims/claim_registry.md", "claim_registry", "P0-M17", False, None, "Conservative claim registry", []),
        ("paper/claims/non_claims.md", "non_claims", "P0-M17", False, None, "Prohibited overclaim list", []),
    ]
    return [
        ResearchPipelineArtifact(
            path=path,
            artifact_type=artifact_type,
            milestone=milestone,
            exists=(root / path).exists(),
            reproducible_by_script=reproducible,
            producer_script=producer,
            description=description,
            limitations=limitations,
        )
        for path, artifact_type, milestone, reproducible, producer, description, limitations in specs
    ]


def evaluate_research_pipeline(repo_root: str | Path = ".") -> ResearchPipelineEvaluation:
    root = Path(repo_root)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Repository root not found: {root}")

    artifacts = collect_research_artifacts(root)
    missing = [artifact.path for artifact in artifacts if not artifact.exists]
    if missing:
        raise FileNotFoundError("Missing required research artifact(s): " + ", ".join(missing))

    dataset = load_json(root / "outputs/research_datasets/velocity_response_dataset_v1.json")
    dataset_report = load_json(root / "outputs/research_datasets/velocity_response_dataset_v1_validation_report.json")
    predictions = load_json(root / "outputs/research_models/response_model_predictions_v1.json")
    model_eval = load_json(root / "outputs/research_models/response_model_evaluation_v1.json")
    risk_map = load_json(root / "outputs/research_risk/navigation_risk_map_v1.json")
    risk_eval = load_json(root / "outputs/research_risk/navigation_risk_evaluation_v1.json")

    records = dataset.get("records", [])
    hybrid_predictions = predictions.get("predictions_by_model", {}).get("uncertainty_aware_hybrid_v1", [])
    assessments = risk_map.get("assessments", [])

    supported_claims = [
        "Measurement v0 source artifacts exist and are represented in the repository.",
        "Velocity response dataset schema v1 and dataset v1 exist.",
        "Response model foundation exists with conservative uncertainty/confidence labels.",
        "Offline navigation-aware risk mapping layer exists.",
        "Pipeline evaluation artifacts exist.",
    ]
    non_claims = [
        "No real navigation safety improvement is demonstrated.",
        "No collision-rate reduction is demonstrated.",
        "No near-miss-rate reduction is demonstrated.",
        "No navigation success-rate improvement is demonstrated.",
        "No velocity compensation readiness is demonstrated.",
        "No safe command adapter readiness is demonstrated.",
        "No publication readiness is claimed.",
    ]
    available_metrics = [
        "dataset_records_count",
        "numeric_records_count",
        "qualitative_only_records_count",
        "response_predictions_count",
        "risk_assessments_count",
        "warnings_count",
        "risk_level_counts",
        "warning_category_counts",
        "exact_source_reconstruction_absolute_error_sanity_check",
    ]
    unavailable_metrics = [
        "generalization_error",
        "calibrated_uncertainty_error",
        "collision_rate",
        "near_miss_rate",
        "navigation_success_rate",
        "real_world_safety_improvement",
        "compensation_performance",
        "safe_command_adapter_performance",
    ]
    limitations = sorted(
        dict.fromkeys(
            list(dataset.get("limitations", []))
            + list(model_eval.get("limitations", []))
            + list(risk_eval.get("limitations", []))
            + [
                "single robot",
                "limited environment coverage",
                "0.1 m/s record is qualitative-only",
                "no full paper manuscript yet",
            ]
        )
    )
    next_experiments = [
        "repeated trials per command velocity",
        "multi-surface velocity response tests",
        "vx plus wz command grid",
        "yaw and lateral drift measurement",
        "response delay and stop-distance logging",
        "navigation task trials with and without advisory risk layer",
        "baseline comparison under a fixed protocol",
    ]
    metrics = {
        "numeric_records_count": model_eval.get("numeric_records_count", 0),
        "qualitative_only_records_count": model_eval.get("qualitative_only_records_count", 0),
        "warnings_count": risk_eval.get("warnings_count", 0),
        "risk_level_counts": risk_eval.get("risk_level_counts", {}),
        "warning_category_counts": risk_eval.get("warning_category_counts", {}),
        "dataset_validation_passed": dataset_report.get("validation_passed", False),
        "publication_readiness": {
            "level": "not_ready_for_full_submission",
            "reason": [
                "no literature review matrix with verified citations yet",
                "no calibrated uncertainty evaluation",
                "no real navigation outcome evaluation",
                "no collision, near-miss, or success-rate metrics",
                "single robot and limited environment coverage",
            ],
        },
    }

    return ResearchPipelineEvaluation(
        evaluation_name=EVALUATION_NAME,
        artifacts_count=len(artifacts),
        missing_artifacts_count=len(missing),
        dataset_records_count=len(records) if isinstance(records, list) else 0,
        response_predictions_count=len(hybrid_predictions) if isinstance(hybrid_predictions, list) else 0,
        risk_assessments_count=len(assessments) if isinstance(assessments, list) else 0,
        supported_claims=supported_claims,
        non_claims=non_claims,
        available_metrics=available_metrics,
        unavailable_metrics=unavailable_metrics,
        limitations=limitations,
        next_experiments=next_experiments,
        safety_flags={
            "measurement_v0_complete": True,
            "real_k1_profile_available": True,
            "compensation_ready": False,
            "navigation_warning_ready": True,
            "safe_command_adapter_ready": False,
        },
        metrics=metrics,
    )


def build_artifact_table(repo_root: str | Path = ".") -> list[dict[str, Any]]:
    rows = []
    for artifact in collect_research_artifacts(repo_root):
        rows.append(
            {
                "chapter_level": _chapter_for_milestone(artifact.milestone),
                "milestone": artifact.milestone,
                "artifact": artifact.description,
                "path": artifact.path,
                "producer_script": artifact.producer_script or "manual/repository artifact",
                "reproducible": artifact.reproducible_by_script,
                "purpose": artifact.description,
                "evidence_type": artifact.artifact_type,
                "limitations": "; ".join(artifact.limitations),
                "exists": artifact.exists,
            }
        )
    return rows


def write_markdown_report(
    evaluation: ResearchPipelineEvaluation,
    artifact_table: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    lines = [
        "# M17 管线评估摘要",
        "",
        "## Current Pipeline Status",
        "",
        f"- Dataset records: {evaluation.dataset_records_count}",
        f"- Response predictions: {evaluation.response_predictions_count}",
        f"- Risk assessments: {evaluation.risk_assessments_count}",
        f"- Publication readiness: {evaluation.metrics['publication_readiness']['level']}",
        "",
        "## Artifact Chain",
        "",
    ]
    for row in artifact_table:
        lines.append(f"- {row['milestone']}: `{row['path']}` ({row['evidence_type']})")
    lines.extend(_list_section("Supported Claims", evaluation.supported_claims))
    lines.extend(_list_section("Non-Claims", evaluation.non_claims))
    lines.extend(_list_section("Available Metrics", evaluation.available_metrics))
    lines.extend(_list_section("Unavailable Metrics", evaluation.unavailable_metrics))
    lines.extend(_list_section("Limitations", evaluation.limitations))
    lines.extend(_list_section("Next Experiments", evaluation.next_experiments))
    _write_text(output_path, "\n".join(lines) + "\n")


def write_json_report(
    evaluation: ResearchPipelineEvaluation,
    artifact_table: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    payload = {
        "milestone": "M17",
        "evaluation_name": evaluation.evaluation_name,
        "artifacts": artifact_table,
        "artifact_counts": {
            "artifacts_count": evaluation.artifacts_count,
            "missing_artifacts_count": evaluation.missing_artifacts_count,
        },
        "dataset_summary": {
            "records_count": evaluation.dataset_records_count,
            "numeric_records_count": evaluation.metrics["numeric_records_count"],
            "qualitative_only_records_count": evaluation.metrics["qualitative_only_records_count"],
        },
        "response_model_summary": {
            "predictions_count": evaluation.response_predictions_count,
            "exact_source_reconstruction_is_sanity_check_only": True,
        },
        "navigation_risk_summary": {
            "risk_assessments_count": evaluation.risk_assessments_count,
            "warnings_count": evaluation.metrics["warnings_count"],
            "risk_level_counts": evaluation.metrics["risk_level_counts"],
            "warning_category_counts": evaluation.metrics["warning_category_counts"],
            "no_real_navigation_outcomes": True,
        },
        "supported_claims": evaluation.supported_claims,
        "non_claims": evaluation.non_claims,
        "available_metrics": evaluation.available_metrics,
        "unavailable_metrics": evaluation.unavailable_metrics,
        "limitations": evaluation.limitations,
        "next_experiments": evaluation.next_experiments,
        "safety_flags": evaluation.safety_flags,
        "publication_readiness": evaluation.metrics["publication_readiness"],
        "fabricated_values": False,
        "fabricated_navigation_outcomes": False,
        "compensation_logic_implemented": False,
        "inverse_command_mapping_implemented": False,
        "navigation_control_implemented": False,
        "safe_command_adapter_implemented": False,
        "ros2_commands_run": False,
        "booster_sdk_movement_commands_run": False,
        "real_robot_commands_run": False,
        "battery_state_required": False,
        "remote_controller_state_allowed": False,
    }
    _write_json(output_path, payload)


def write_artifact_table_markdown(rows: list[dict[str, Any]], output_path: str | Path) -> None:
    lines = [
        "# M17 Method Artifact Table",
        "",
        "| Chapter / Level | Milestone | Artifact | Path | Producer script | Reproducible? | Purpose | Evidence type | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['chapter_level']} | {row['milestone']} | {row['artifact']} | `{row['path']}` | `{row['producer_script']}` | {row['reproducible']} | {row['purpose']} | {row['evidence_type']} | {row['limitations']} |"
        )
    _write_text(output_path, "\n".join(lines) + "\n")


def write_limitations_markdown(evaluation: ResearchPipelineEvaluation, output_path: str | Path) -> None:
    lines = ["# M17 限制与下一步实验", ""]
    lines.extend(_list_section("Current Limitations", evaluation.limitations))
    lines.extend(_list_section("Required Next Experiments", evaluation.next_experiments))
    lines.extend(
        _list_section(
            "Claim Upgrade Conditions",
            [
                "需要 repeated-trial numeric evidence 才能升级 uncertainty claim。",
                "需要真实 navigation outcome metrics 才能讨论 safety improvement。",
                "需要 collision / near-miss / success-rate annotation 才能讨论风险降低。",
                "需要 verified literature review 才能讨论 novelty。",
            ],
        )
    )
    _write_text(output_path, "\n".join(lines) + "\n")


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")


def _write_text(path: str | Path, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _list_section(title: str, items: list[str]) -> list[str]:
    lines = ["", f"## {title}", ""]
    lines.extend(f"- {item}" for item in items)
    return lines


def _chapter_for_milestone(milestone: str) -> str:
    if milestone in {"M13", "M14"}:
        return "Chapter 2 / Dataset"
    if milestone == "M15R":
        return "Chapter 2 / Model"
    if milestone == "M16":
        return "Chapter 3 / Risk"
    return "Research Governance"
