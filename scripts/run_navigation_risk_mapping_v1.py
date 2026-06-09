"""Run M16 offline navigation-aware risk mapping."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.navigation_risk_mapping import (
    DEFAULT_MODEL_NAME,
    build_risk_evaluation_payload,
    build_risk_map_payload,
    load_response_model_predictions,
)
from k1_measurement.velocity_response_dataset_builder import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline navigation risk mapping v1.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--risk-map-output", required=True)
    parser.add_argument("--evaluation-output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        predictions_payload = load_response_model_predictions(args.predictions)
        risk_map = build_risk_map_payload(args.predictions, predictions_payload, args.model_name)
        evaluation = build_risk_evaluation_payload(args.predictions, predictions_payload, args.model_name)
        write_json(args.risk_map_output, risk_map)
        write_json(args.evaluation_output, evaluation)

        summary = {
            "milestone": "M16",
            "risk_map_name": risk_map["risk_map_name"],
            "source_predictions_path": args.predictions,
            "source_model_name": args.model_name,
            "risk_map_output": args.risk_map_output,
            "evaluation_output": args.evaluation_output,
            "assessments_count": len(risk_map["assessments"]),
            "warnings_count": evaluation["warnings_count"],
            "fabricated_navigation_outcomes": False,
            "compensation_ready": False,
            "safe_command_adapter_ready": False,
            "navigation_warning_ready": True,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"risk_mapping_passed": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
