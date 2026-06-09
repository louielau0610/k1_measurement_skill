"""Run M15R velocity response model predictions and limited evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.research_dataset_schema import (
    load_velocity_response_schema,
    validate_velocity_response_record,
    validate_velocity_response_schema,
)
from k1_measurement.velocity_response_dataset_builder import write_json
from k1_measurement.velocity_response_model import (
    MODEL_NAMES,
    VelocityResponseModel,
    evaluation_to_dict,
    extract_velocity_response_records,
    load_velocity_response_dataset,
    prediction_to_dict,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run velocity response model v1.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--predictions-output")
    parser.add_argument("--evaluation-output")
    parser.add_argument("--query-vx", type=float, action="append")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema = load_velocity_response_schema(args.schema)
        dataset = load_velocity_response_dataset(args.dataset)
        validation_errors = validate_velocity_response_schema(schema)
        validation_errors.extend(validate_velocity_response_record(dataset, schema))
        if validation_errors:
            print(
                json.dumps({"validation_passed": False, "errors": validation_errors}, indent=2),
                file=sys.stderr,
            )
            return 1

        model = VelocityResponseModel.from_dataset(dataset)
        records = extract_velocity_response_records(dataset)
        queries = args.query_vx or sorted(float(record["vx_cmd_mps"]) for record in records)
        predictions_by_model: dict[str, list[dict[str, Any]]] = {}
        for model_name in MODEL_NAMES:
            predictions_by_model[model_name] = [
                prediction_to_dict(prediction)
                for prediction in model.predict_many(queries, model_name=model_name)
            ]

        predictions_output = {
            "dataset_path": args.dataset,
            "schema_path": args.schema,
            "models_included": MODEL_NAMES,
            "query_velocities_mps": queries,
            "predictions_by_model": predictions_by_model,
            "safety_readiness_flags": {
                "compensation_ready": False,
                "safe_command_adapter_ready": False,
                "navigation_warning_ready": True,
            },
            "limitations": dataset.get("limitations", []),
            "fabricated_values": False,
            "compensation_logic_implemented": False,
            "inverse_command_mapping_implemented": False,
            "navigation_control_implemented": False,
            "safe_command_adapter_implemented": False,
        }
        evaluation = evaluation_to_dict(model.evaluate_on_dataset())
        evaluation["dataset_path"] = args.dataset
        evaluation["model_names"] = MODEL_NAMES
        evaluation["m16_readiness_note"] = (
            "M16 may consume uncertainty/confidence labels for risk mapping, "
            "but must not treat them as calibrated probabilities."
        )

        if args.predictions_output:
            write_json(args.predictions_output, predictions_output)
        if args.evaluation_output:
            write_json(args.evaluation_output, evaluation)

        summary = {
            "milestone": "M15R",
            "dataset_path": args.dataset,
            "models_included": MODEL_NAMES,
            "query_velocities_mps": queries,
            "records_count": len(records),
            "numeric_records_count": len(model.numeric_records),
            "qualitative_only_records_count": len(model.qualitative_only_records),
            "predictions_output": args.predictions_output,
            "evaluation_output": args.evaluation_output,
            "validation_passed": True,
            "fabricated_values": False,
            "compensation_ready": False,
            "safe_command_adapter_ready": False,
            "navigation_warning_ready": True,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"validation_passed": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
