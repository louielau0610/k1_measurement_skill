"""Agent-callable JSON CLI for the hardware-free calibration skill."""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any

from calibration_skill.domain.enums import SkillOperationStatus
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_CONFIGURATION_INVALID,
    ERROR_INTERNAL_ERROR,
    ERROR_SCHEMA_VERSION_UNSUPPORTED,
    ERROR_SERIALIZATION_FAILED,
)
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from calibration_skill.schemas.codec import canonical_json_dumps
from calibration_skill.schemas.validation import validate_skill_request
from calibration_skill.skill.envelopes import response_envelope
from calibration_skill.skill.manifest import EXIT_CODES, build_skill_manifest, operation_catalog
from calibration_skill.skill.operations import SUPPORTED_OPERATIONS


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "manifest":
            return _emit(build_skill_manifest(), args)
        if args.command == "operations":
            return _emit({"operations": operation_catalog()}, args)
        if args.command == "examples":
            return _emit(_example_request(args.operation), args)
        if args.command == "validate":
            return _validate(args)
        if args.command == "invoke":
            return _invoke(args)
        parser.error("unknown command")
        return EXIT_CODES["usage_error"]
    except BrokenPipeError:
        return EXIT_CODES["output_write_failure"]
    except Exception as exc:
        if getattr(args, "show_traceback", False):
            traceback.print_exc(file=sys.stderr)
        else:
            print(f"internal error: {exc}", file=sys.stderr)
        response = _error_response(ERROR_INTERNAL_ERROR, "internal error", cause=type(exc).__name__)
        _write_json_stdout(response, pretty=getattr(args, "pretty", False))
        return EXIT_CODES["internal_error"]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="calibration-skill", description="M26-D mock-only calibration skill CLI")
    parser.set_defaults(pretty=False, compact=False, output="-", create_dirs=False, show_traceback=False)
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("manifest", "operations"):
        p = sub.add_parser(name)
        _add_output_args(p)

    p = sub.add_parser("examples")
    p.add_argument("--operation", required=True, choices=SUPPORTED_OPERATIONS)
    _add_output_args(p)

    for name in ("validate", "invoke"):
        p = sub.add_parser(name)
        p.add_argument("--input", required=True, help="'-' for stdin or path to JSON request")
        _add_output_args(p)
        p.add_argument("--show-traceback", action="store_true")
    return parser


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", default="-", help="'-' for stdout or path to JSON output")
    parser.add_argument("--pretty", action="store_true", help="Pretty deterministic JSON")
    parser.add_argument("--compact", action="store_true", help="Compact deterministic JSON")
    parser.add_argument("--create-dirs", action="store_true", help="Create parent directories for file output")


def _validate(args: argparse.Namespace) -> int:
    payload, error_response, error_code = _read_request(args.input)
    if error_response is not None:
        return _emit(error_response, args, exit_code=error_code)
    assert payload is not None
    validation_error = _request_validation_error(payload)
    if validation_error is not None:
        response = response_envelope(
            str(payload.get("request_id") or "unknown"),
            str(payload.get("operation") or "unknown"),
            SkillOperationStatus.REJECTED,
            error=validation_error,
        )
        return _emit(response, args, exit_code=EXIT_CODES["request_rejected"])
    response = response_envelope(
        str(payload["request_id"]),
        str(payload["operation"]),
        SkillOperationStatus.SUCCESS,
        result={
            "operation": payload["operation"],
            "schema_version": payload["schema_version"],
            "valid": True,
            "dry_run_only": True,
        },
    )
    return _emit(response, args)


def _invoke(args: argparse.Namespace) -> int:
    payload, error_response, error_code = _read_request(args.input)
    if error_response is not None:
        return _emit(error_response, args, exit_code=error_code)
    assert payload is not None
    service = build_mock_dry_run_service()
    response = service.handle_request(payload)
    exit_code = EXIT_CODES["success"] if response.get("status") == "success" else EXIT_CODES["request_rejected"]
    return _emit(response, args, exit_code=exit_code)


def _request_validation_error(payload: dict[str, Any]) -> DomainError | None:
    if payload.get("schema_version") != "1.0.0":
        return DomainError(
            ERROR_SCHEMA_VERSION_UNSUPPORTED,
            "Unsupported schema_version",
            retryable=False,
            details={"supported": "1.0.0", "actual": payload.get("schema_version")},
        )
    validation = validate_skill_request(payload)
    if not validation.get("valid"):
        return DomainError(ERROR_CONFIGURATION_INVALID, "Skill request schema validation failed", details=validation)
    if payload.get("operation") not in SUPPORTED_OPERATIONS:
        return DomainError(ERROR_CONFIGURATION_INVALID, f"Unknown operation {payload.get('operation')}", retryable=False)
    if payload.get("dry_run") is not True:
        return DomainError(ERROR_CONFIGURATION_INVALID, "dry_run=true is required", retryable=False)
    if payload.get("platform") != "mock":
        return DomainError(ERROR_CONFIGURATION_INVALID, "M26-D CLI supports only mock platform", retryable=False)
    if payload.get("operation") in ("dry_run_velocity_command", "dry_run_end_to_end"):
        if "safety_envelope" not in (payload.get("payload") or {}):
            return DomainError(ERROR_CONFIGURATION_INVALID, "safety_envelope is required for command operations")
    return None


def _read_request(input_arg: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, int]:
    try:
        if input_arg == "-":
            text = sys.stdin.read()
        else:
            path = Path(input_arg)
            if not path.exists():
                response = _error_response(ERROR_CONFIGURATION_INVALID, f"input file not found: {input_arg}")
                return None, response, EXIT_CODES["usage_error"]
            text = path.read_text(encoding="utf-8")
        return json.loads(text), None, EXIT_CODES["success"]
    except json.JSONDecodeError as exc:
        return None, _error_response(ERROR_SERIALIZATION_FAILED, f"malformed JSON: {exc.msg}"), EXIT_CODES["malformed_input_json"]


def _emit(obj: dict[str, Any], args: argparse.Namespace, *, exit_code: int = 0) -> int:
    text = _json_text(obj, pretty=args.pretty and not args.compact)
    output = getattr(args, "output", "-")
    if output == "-":
        sys.stdout.write(text + "\n")
        return exit_code
    try:
        path = Path(output)
        if path.parent and not path.parent.exists():
            if getattr(args, "create_dirs", False):
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                print(f"output parent does not exist: {path.parent}", file=sys.stderr)
                return EXIT_CODES["output_write_failure"]
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text + "\n", encoding="utf-8")
        tmp.replace(path)
        return exit_code
    except Exception as exc:
        print(f"output write failed: {exc}", file=sys.stderr)
        return EXIT_CODES["output_write_failure"]


def _write_json_stdout(obj: dict[str, Any], *, pretty: bool) -> None:
    sys.stdout.write(_json_text(obj, pretty=pretty) + "\n")


def _json_text(obj: dict[str, Any], *, pretty: bool) -> str:
    if pretty:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)
    return canonical_json_dumps(obj)


def _error_response(code: str, message: str, *, cause: str | None = None) -> dict[str, Any]:
    details = {"cause_type": cause} if cause else {}
    return response_envelope(
        "unknown",
        "unknown",
        SkillOperationStatus.REJECTED,
        error=DomainError(code=code, message=message, retryable=False, details=details),
    )


def _example_request(operation: str) -> dict[str, Any]:
    from calibration_skill.schemas.codec import (
        encode_operator_authorization,
        encode_safety_envelope,
        encode_velocity_command,
    )
    from calibration_skill.domain.enums import CoordinateFrame, RobotPlatform
    from calibration_skill.domain.motion import VelocityCommand
    from calibration_skill.domain.safety import OperatorAuthorization, SafetyEnvelope

    payload: dict[str, Any] = {}
    if operation in ("dry_run_velocity_command", "dry_run_end_to_end"):
        safety = SafetyEnvelope(
            policy_id="mock-policy",
            policy_hash="mock-hash",
            max_abs_vx_mps=0.5,
            max_abs_vy_mps=0.4,
            max_abs_wz_radps=0.8,
            max_command_duration_s=2.0,
            max_telemetry_age_ms=100.0,
            stop_timeout_s=1.0,
            allowed_command_frames=(CoordinateFrame.BODY,),
            operator_authorization_required=True,
        )
        command = VelocityCommand(
            vx_mps=0.1,
            vy_mps=0.0,
            wz_radps=0.0,
            sequence_id="example-command-1",
            issued_monotonic_ns=1_000_000_000,
            expiry_monotonic_ns=2_000_000_000,
            requested_duration_s=0.5,
            frame=CoordinateFrame.BODY,
            safety_policy_id="mock-policy",
            safety_policy_hash="mock-hash",
            source="m26d-example",
        )
        auth = OperatorAuthorization(
            authorization_id="example-auth-1",
            operator_id="example-operator",
            platform=RobotPlatform.MOCK,
            robot_id="mock-robot",
            issued_monotonic_ns=500_000_000,
            expiry_monotonic_ns=3_000_000_000,
            authorized_operations=(operation,),
            safety_policy_id="mock-policy",
            safety_policy_hash="mock-hash",
            evidence_reference="simulated-operator-confirmation",
        )
        payload = {
            "safety_envelope": encode_safety_envelope(safety),
            "velocity_command": encode_velocity_command(command),
            "operator_authorization": encode_operator_authorization(auth),
        }
    return {
        "schema_version": "1.0.0",
        "request_id": f"example-{operation}",
        "operation": operation,
        "platform": "mock",
        "robot_id": "mock-robot",
        "dry_run": True,
        "payload": payload,
        "caller_metadata": {"example": "m26d"},
    }


if __name__ == "__main__":
    raise SystemExit(main())
