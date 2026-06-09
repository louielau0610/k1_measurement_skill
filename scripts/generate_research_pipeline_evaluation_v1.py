"""Generate M17 research pipeline evaluation reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.research_pipeline_evaluation import (
    build_artifact_table,
    evaluate_research_pipeline,
    write_artifact_table_markdown,
    write_json_report,
    write_limitations_markdown,
    write_markdown_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate M17 research pipeline evaluation.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    parser.add_argument("--artifact-table-output", required=True)
    parser.add_argument("--limitations-output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evaluation = evaluate_research_pipeline(args.repo_root)
        artifact_table = build_artifact_table(args.repo_root)
        write_json_report(evaluation, artifact_table, args.json_output)
        write_markdown_report(evaluation, artifact_table, args.markdown_output)
        write_artifact_table_markdown(artifact_table, args.artifact_table_output)
        write_limitations_markdown(evaluation, args.limitations_output)
        summary = {
            "milestone": "M17",
            "evaluation_name": evaluation.evaluation_name,
            "artifacts_count": evaluation.artifacts_count,
            "dataset_records_count": evaluation.dataset_records_count,
            "response_predictions_count": evaluation.response_predictions_count,
            "risk_assessments_count": evaluation.risk_assessments_count,
            "publication_readiness": evaluation.metrics["publication_readiness"]["level"],
            "json_output": args.json_output,
            "markdown_output": args.markdown_output,
            "artifact_table_output": args.artifact_table_output,
            "limitations_output": args.limitations_output,
            "fabricated_values": False,
            "fabricated_navigation_outcomes": False,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"evaluation_passed": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
