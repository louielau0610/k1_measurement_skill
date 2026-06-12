from __future__ import annotations

import dataclasses
import json
import shutil
import subprocess
import sys
from pathlib import Path

from k1_measurement.research_pipeline_evaluation import (
    build_artifact_table,
    collect_research_artifacts,
    evaluate_research_pipeline,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = REPO_ROOT / "scripts" / "generate_research_pipeline_evaluation_v1.py"


def test_load_expected_m14_m15r_m16_outputs() -> None:
    expected = [
        "outputs/research_datasets/velocity_response_dataset_v1.json",
        "outputs/research_models/response_model_predictions_v1.json",
        "outputs/research_risk/navigation_risk_map_v1.json",
    ]

    assert all((REPO_ROOT / path).exists() for path in expected)


def test_collect_artifact_table() -> None:
    rows = build_artifact_table(REPO_ROOT)

    assert rows
    assert any(row["milestone"] == "M16" for row in rows)


def test_evaluate_research_pipeline() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    assert evaluation.evaluation_name == "research_pipeline_evaluation_v1"
    assert evaluation.artifacts_count >= 9


def test_evaluation_is_json_serializable() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    json.dumps(dataclasses.asdict(evaluation))


def test_dataset_records_count_is_5() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    assert evaluation.dataset_records_count == 5


def test_risk_assessments_count_is_5() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    assert evaluation.risk_assessments_count == 5


def test_publication_readiness_is_not_full_submission_ready() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    assert evaluation.metrics["publication_readiness"]["level"] == "not_ready_for_full_submission"


def test_supported_claims_do_not_include_real_navigation_safety_improvement() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    rendered = " ".join(evaluation.supported_claims).lower()
    assert "real navigation safety improvement" not in rendered


def test_non_claims_include_no_collision_or_success_rate_improvement() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)
    rendered = " ".join(evaluation.non_claims).lower()

    assert "collision-rate reduction" in rendered
    assert "success-rate improvement" in rendered


def test_safety_flags_remain_false_for_downstream_control() -> None:
    evaluation = evaluate_research_pipeline(REPO_ROOT)

    assert evaluation.safety_flags["compensation_ready"] is False
    assert evaluation.safety_flags["safe_command_adapter_ready"] is False


def test_missing_required_artifact_causes_clear_error(tmp_path: Path) -> None:
    repo_copy = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, repo_copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "data", "*.tar.gz"))
    (repo_copy / "outputs" / "research_risk" / "navigation_risk_map_v1.json").unlink()

    try:
        evaluate_research_pipeline(repo_copy)
    except FileNotFoundError as exc:
        assert "navigation_risk_map_v1.json" in str(exc)
    else:
        raise AssertionError("Expected missing artifact failure")


def test_cli_writes_json_and_markdown_outputs(tmp_path: Path) -> None:
    json_output = tmp_path / "report.json"
    markdown_output = tmp_path / "summary.md"
    artifact_output = tmp_path / "artifact_table.md"
    limitations_output = tmp_path / "limitations.md"

    result = subprocess.run(
        [
            sys.executable,
            str(EVAL_SCRIPT),
            "--repo-root",
            str(REPO_ROOT),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
            "--artifact-table-output",
            str(artifact_output),
            "--limitations-output",
            str(limitations_output),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert json_output.exists()
    assert markdown_output.exists()
    assert artifact_output.exists()
    assert limitations_output.exists()


def test_cli_exits_nonzero_for_missing_repo_root(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(EVAL_SCRIPT),
            "--repo-root",
            str(tmp_path / "missing"),
            "--json-output",
            str(tmp_path / "report.json"),
            "--markdown-output",
            str(tmp_path / "summary.md"),
            "--artifact-table-output",
            str(tmp_path / "artifact.md"),
            "--limitations-output",
            str(tmp_path / "limitations.md"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "missing" in result.stderr
