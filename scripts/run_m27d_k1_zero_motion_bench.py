#!/usr/bin/env python
"""M27-D Booster K1 Zero-Motion Bench Runner.

Standalone script for running a zero-motion bench validation session
against the real Booster K1 hardware via the isolated SDK binding.

This script is NOT reachable from the ordinary default CLI.
It requires explicit --execute-hardware to trigger any SDK import.

Usage (do not run unless all safety gates are confirmed):
  py -3.12 scripts/run_m27d_k1_zero_motion_bench.py \
    --robot-id K1_001 \
    --hardware-session-id m27d-bench-001 \
    --safety-policy-id m27d-zero-motion-policy \
    --safety-policy-hash abc123 \
    --evidence-reference m27d-bench-2026-06-18 \
    --gate-expiry-monotonic-ns 999999999999999 \
    --output-dir outputs/engineering/m27d_bench_results \
    --operator-confirmed-hardware \
    --physical-estop-confirmed \
    --clear-test-area-confirmed \
    --battery-state-confirmed \
    --network-isolation-confirmed \
    --manual-operator-present \
    --enable-vendor-runtime \
    --execute-hardware
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# No SDK imports at module level
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# --- Result statuses ---
STATUS_NOT_EXECUTED = "not_executed"
STATUS_BLOCKED_BY_GATE = "blocked_by_gate"
STATUS_SDK_UNAVAILABLE = "sdk_unavailable"
STATUS_SDK_IMPORT_FAILED = "sdk_import_failed"
STATUS_BINDING_CONSTRUCTION_FAILED = "binding_construction_failed"
STATUS_CONNECTION_FAILED = "connection_failed"
STATUS_READ_ONLY_CHECKS_FAILED = "read_only_checks_failed"
STATUS_STOP_UNACKNOWLEDGED = "stop_unacknowledged"
STATUS_SAFE_STATE_UNVERIFIED = "safe_state_unverified"
STATUS_BENCH_PASSED = "bench_passed"


@dataclass
class BenchTraceEvent:
    event_sequence: int
    event_type: str
    monotonic_ns: int
    success: bool
    structured_error: dict[str, object] | None = None
    evidence_reference: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "event_sequence": self.event_sequence,
            "event_type": self.event_type,
            "monotonic_ns": self.monotonic_ns,
            "success": self.success,
            "structured_error": self.structured_error,
            "evidence_reference": self.evidence_reference,
        }


@dataclass
class BenchResult:
    status: str
    evidence_reference: str
    started_at: str
    finished_at: str
    gate_evidence: dict[str, object] = field(default_factory=dict)
    sdk_detection: dict[str, object] = field(default_factory=dict)
    runtime_trace: list[dict[str, object]] = field(default_factory=list)
    telemetry_snapshot: dict[str, object] = field(default_factory=dict)
    identity: dict[str, object] = field(default_factory=dict)
    stop_command_attempted: bool = False
    stop_command_accepted: bool = False
    internal_command_state: str = ""
    internal_safe_state_claim: bool = False
    physical_safe_state_observed: bool = False
    physical_safe_state_observation_source: str = "none"
    physical_safe_state_verification: str = "unavailable"
    errors: list[str] = field(default_factory=list)

    def to_summary(self) -> dict[str, object]:
        return {
            "status": self.status,
            "evidence_reference": self.evidence_reference,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "stop_command_attempted": self.stop_command_attempted,
            "stop_command_accepted": self.stop_command_accepted,
            "internal_command_state": self.internal_command_state,
            "internal_safe_state_claim": self.internal_safe_state_claim,
            "physical_safe_state_observed": self.physical_safe_state_observed,
            "physical_safe_state_observation_source": self.physical_safe_state_observation_source,
            "physical_safe_state_verification": self.physical_safe_state_verification,
            "errors": self.errors,
        }


def _now_ns() -> int:
    return time.monotonic_ns()


def _timestamp_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_to_dict(error: Exception) -> dict[str, object]:
    """Serialize an exception without tracebacks, secrets, or raw SDK objects."""
    from calibration_skill.adapters.booster_k1.errors import sanitize_vendor_message

    result: dict[str, object] = {
        "type": type(error).__name__,
        "message": sanitize_vendor_message(error),
    }
    if hasattr(error, "to_dict"):
        try:
            result["structured"] = error.to_dict()  # type: ignore[union-attr]
        except Exception:
            pass
    return result


def _sanitize_dict(data: dict[str, object]) -> dict[str, object]:
    """Remove potentially unsafe keys from a dictionary."""
    forbidden_keys = {
        "password", "secret", "token", "credential", "api_key",
        "memory_address", "traceback", "raw_sdk_object",
    }
    return {k: v for k, v in data.items() if not any(fk in k.lower() for fk in forbidden_keys)}


def build_hardware_gate(args: argparse.Namespace) -> Any:
    """Construct the BoosterK1HardwareGate from CLI arguments."""
    from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE

    return BoosterK1HardwareGate(
        allow_hardware=args.operator_confirmed_hardware,
        operator_confirmed_hardware=args.operator_confirmed_hardware,
        hardware_session_id=args.hardware_session_id,
        safety_policy_id=args.safety_policy_id,
        safety_policy_hash=args.safety_policy_hash,
        expected_robot_id=args.robot_id,
        expected_adapter_mode=K1_VENDOR_RUNTIME_MODE,
        require_physical_estop_confirmation=args.physical_estop_confirmed,
        require_clear_test_area_confirmation=args.clear_test_area_confirmed,
        require_battery_state_confirmation=args.battery_state_confirmed,
        require_network_isolation_confirmation=args.network_isolation_confirmed,
        require_manual_operator_present=args.manual_operator_present,
        evidence_reference=args.evidence_reference,
        expires_monotonic_ns=args.gate_expiry_monotonic_ns,
    )


def run_bench(args: argparse.Namespace) -> BenchResult:
    """Execute the zero-motion bench sequence."""
    from calibration_skill.adapters.booster_k1.vendor_runtime import (
        BoosterK1RuntimeUnavailable,
        detect_booster_sdk_availability,
    )
    from calibration_skill.adapters.booster_k1.vendor_binding import (
        detect_booster_sdk_availability_detailed,
    )
    from calibration_skill.domain.errors import DomainError

    result = BenchResult(
        status=STATUS_NOT_EXECUTED,
        evidence_reference=args.evidence_reference,
        started_at=_timestamp_iso(),
        finished_at="",
    )
    trace: list[BenchTraceEvent] = []
    seq = 0

    def add_trace(event_type: str, success: bool, error: Exception | None = None) -> None:
        nonlocal seq
        seq += 1
        trace.append(BenchTraceEvent(
            event_sequence=seq,
            event_type=event_type,
            monotonic_ns=_now_ns(),
            success=success,
            structured_error=_error_to_dict(error) if error else None,
            evidence_reference=args.evidence_reference,
        ))

    # Phase 1: Validate arguments and construct gate
    try:
        gate = build_hardware_gate(args)
        result.gate_evidence = _sanitize_dict({
            "robot_id": args.robot_id,
            "hardware_session_id": args.hardware_session_id,
            "safety_policy_id": args.safety_policy_id,
            "gate_expiry_monotonic_ns": args.gate_expiry_monotonic_ns,
            "operator_confirmed_hardware": args.operator_confirmed_hardware,
            "physical_estop_confirmed": args.physical_estop_confirmed,
            "clear_test_area_confirmed": args.clear_test_area_confirmed,
            "battery_state_confirmed": args.battery_state_confirmed,
            "network_isolation_confirmed": args.network_isolation_confirmed,
            "manual_operator_present": args.manual_operator_present,
        })
    except Exception as exc:
        result.status = STATUS_BLOCKED_BY_GATE
        result.errors.append(f"Gate construction failed: {_error_to_dict(exc)['message']}")
        add_trace("gate_construction", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    add_trace("gate_construction", True)

    # Phase 2: Validate gate
    try:
        gate_errors = gate.validate(
            now_ns=_now_ns(),
            expected_robot_id=args.robot_id,
            expected_safety_policy_id=args.safety_policy_id,
            expected_safety_policy_hash=args.safety_policy_hash,
        )
        if gate_errors:
            result.status = STATUS_BLOCKED_BY_GATE
            result.errors.extend(str(e) for e in gate_errors)
            add_trace("gate_validation", False, gate_errors[0] if gate_errors else None)
            result.finished_at = _timestamp_iso()
            result.runtime_trace = [t.to_dict() for t in trace]
            return result
    except Exception as exc:
        result.status = STATUS_BLOCKED_BY_GATE
        result.errors.append(f"Gate validation failed: {_error_to_dict(exc)['message']}")
        add_trace("gate_validation", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    add_trace("gate_validation", True)

    # Phase 3: Detect SDK without importing
    sdk_status = detect_booster_sdk_availability()
    sdk_detection = detect_booster_sdk_availability_detailed()
    result.sdk_detection = sdk_detection.to_dict()

    if not sdk_status.sdk_importable_without_importing:
        result.status = STATUS_SDK_UNAVAILABLE
        result.errors.append("Booster K1 SDK not discoverable")
        add_trace("sdk_detection", False)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    add_trace("sdk_detection", True)

    # Phase 4: Check --execute-hardware
    if not args.execute_hardware:
        result.status = STATUS_BLOCKED_BY_GATE
        result.errors.append("--execute-hardware is required for SDK import")
        add_trace("execute_hardware_check", False)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    add_trace("execute_hardware_check", True)

    # Phase 5: Check --enable-vendor-runtime
    if not args.enable_vendor_runtime:
        result.status = STATUS_BLOCKED_BY_GATE
        result.errors.append("--enable-vendor-runtime is required")
        add_trace("enable_vendor_runtime_check", False)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    add_trace("enable_vendor_runtime_check", True)

    # Phase 6: Import SDK and construct binding/runtime
    runtime = None
    try:
        from calibration_skill.adapters.booster_k1.vendor_runtime import create_booster_k1_vendor_runtime

        runtime = create_booster_k1_vendor_runtime(
            hardware_gate=gate,
            now_ns=_now_ns(),
            expected_robot_id=args.robot_id,
            expected_safety_policy_id=args.safety_policy_id,
            expected_safety_policy_hash=args.safety_policy_hash,
            enable_vendor_runtime=True,
            execute_hardware=True,
            interface=getattr(args, "interface", "lo"),
        )
        add_trace("binding_construction", True)
    except BoosterK1RuntimeUnavailable as exc:
        result.status = STATUS_BINDING_CONSTRUCTION_FAILED
        result.errors.append(_error_to_dict(exc)["message"])
        add_trace("binding_construction", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result
    except DomainError as exc:
        result.status = STATUS_BINDING_CONSTRUCTION_FAILED
        result.errors.append(_error_to_dict(exc)["message"])
        add_trace("binding_construction", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result
    except ImportError as exc:
        result.status = STATUS_SDK_IMPORT_FAILED
        result.errors.append(f"SDK import failed: {_error_to_dict(exc)['message']}")
        add_trace("sdk_import", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result
    except Exception as exc:
        result.status = STATUS_BINDING_CONSTRUCTION_FAILED
        result.errors.append(f"Binding construction failed: {_error_to_dict(exc)['message']}")
        add_trace("binding_construction", False, exc)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    if runtime is None:
        result.status = STATUS_BINDING_CONSTRUCTION_FAILED
        result.errors.append("Runtime construction returned None")
        add_trace("binding_construction", False)
        result.finished_at = _timestamp_iso()
        result.runtime_trace = [t.to_dict() for t in trace]
        return result

    # Phases 7-16: Run bench sequence with try/finally
    try:
        # Phase 7: Connect
        try:
            runtime.connect(timeout_s=10.0)
            add_trace("connect", True)
        except Exception as exc:
            result.status = STATUS_CONNECTION_FAILED
            result.errors.append(f"Connection failed: {_error_to_dict(exc)['message']}")
            add_trace("connect", False, exc)
            result.finished_at = _timestamp_iso()
            result.runtime_trace = [t.to_dict() for t in trace]
            return result

        # Phase 8: Read identity
        try:
            identity = runtime.identity_metadata()
            result.identity = _sanitize_dict(dict(identity))
            add_trace("read_identity", True)
        except Exception as exc:
            result.errors.append(f"Identity read failed: {_error_to_dict(exc)['message']}")
            add_trace("read_identity", False, exc)

        # Phase 9: Read initial motion state
        try:
            motion_state = runtime.current_motion_state()
            add_trace("read_motion_state", True)
        except Exception as exc:
            result.errors.append(f"Motion state read failed: {_error_to_dict(exc)['message']}")
            add_trace("read_motion_state", False, exc)

        # Phase 10: Read robot state
        try:
            robot_state = runtime.read_robot_state()
            result.telemetry_snapshot["robot_state"] = _sanitize_dict({
                "motion_state": robot_state.motion_state.value,
                "mode_name": robot_state.mode_name,
                "source_monotonic_ns": robot_state.source_monotonic_ns,
            })
            add_trace("read_robot_state", True)
        except Exception as exc:
            result.errors.append(f"Robot state read failed: {_error_to_dict(exc)['message']}")
            add_trace("read_robot_state", False, exc)

        # Phase 11: Read odometry if available
        try:
            odom = runtime.read_odometry()
            if odom is not None:
                result.telemetry_snapshot["odometry"] = {
                    "x_m": odom.x_m,
                    "y_m": odom.y_m,
                    "z_m": odom.z_m,
                    "yaw_rad": odom.yaw_rad,
                    "available": True,
                }
                add_trace("read_odometry", True)
            else:
                result.telemetry_snapshot["odometry"] = {"available": False}
                add_trace("read_odometry", True)
        except Exception as exc:
            result.errors.append(f"Odometry read failed: {_error_to_dict(exc)['message']}")
            result.telemetry_snapshot["odometry"] = {"available": False, "error": _error_to_dict(exc)["message"]}
            add_trace("read_odometry", False, exc)

        # Phase 12: Read battery if available
        try:
            battery = runtime.read_battery_state()
            if battery is not None:
                result.telemetry_snapshot["battery"] = _sanitize_dict(dict(battery))
                add_trace("read_battery", True)
            else:
                result.telemetry_snapshot["battery"] = {"available": False}
                add_trace("read_battery", True)
        except Exception as exc:
            result.errors.append(f"Battery read failed: {_error_to_dict(exc)['message']}")
            result.telemetry_snapshot["battery"] = {"available": False}
            add_trace("read_battery", False, exc)

        # Phase 13: Health check
        try:
            health = runtime.health_check()
            result.telemetry_snapshot["health"] = {
                "healthy": health.healthy,
                "detail": health.detail,
                "scope": health.scope,
                "communication_verified": health.communication_verified,
            }
            add_trace("health_check", health.healthy)
        except Exception as exc:
            result.errors.append(f"Health check failed: {_error_to_dict(exc)['message']}")
            result.telemetry_snapshot["health"] = {"healthy": False, "error": _error_to_dict(exc)["message"]}
            add_trace("health_check", False, exc)

        # Phase 14: Issue explicit stop/zero command
        stop_ok = False
        try:
            result.stop_command_attempted = True
            stop_receipt = runtime.stop()
            result.stop_command_accepted = bool(stop_receipt.accepted)
            result.internal_command_state = stop_receipt.internal_command_state
            if stop_receipt.accepted:
                stop_ok = True
                add_trace("stop_command", True)
            else:
                result.errors.append(f"Stop unacknowledged: {stop_receipt.detail}")
                add_trace("stop_command", False)
        except Exception as exc:
            result.errors.append(f"Stop command failed: {_error_to_dict(exc)['message']}")
            add_trace("stop_command", False, exc)

        # Phase 15: Record internal state, then require independent physical evidence.
        try:
            final_state = runtime.current_motion_state()
            result.internal_command_state = final_state.value
            result.internal_safe_state_claim = final_state in (
                MotionLifecycleState.SAFE_STOPPED,
                MotionLifecycleState.IDLE,
            )
            add_trace("read_internal_command_state", True)
        except Exception as exc:
            result.errors.append(f"Internal state read failed: {_error_to_dict(exc)['message']}")
            add_trace("read_internal_command_state", False, exc)

        try:
            post_stop_odom = runtime.read_odometry()
            if post_stop_odom is not None and all(
                value is not None and abs(value) <= 1e-9
                for value in (post_stop_odom.vx_mps, post_stop_odom.vy_mps, post_stop_odom.wz_radps)
            ):
                result.physical_safe_state_observed = True
                result.physical_safe_state_observation_source = "post_stop_odometry_velocity"
                result.physical_safe_state_verification = "verified"
                add_trace("physical_safe_state_verification", True)
            else:
                result.physical_safe_state_observed = False
                result.physical_safe_state_observation_source = "none"
                result.physical_safe_state_verification = "unavailable"
                add_trace("physical_safe_state_verification", False)
        except Exception as exc:
            result.physical_safe_state_observed = False
            result.physical_safe_state_observation_source = "none"
            result.physical_safe_state_verification = "unavailable"
            result.errors.append(f"Physical safe-state observation failed: {_error_to_dict(exc)['message']}")
            add_trace("physical_safe_state_verification", False, exc)

        # Determine final status
        if not stop_ok:
            result.status = STATUS_STOP_UNACKNOWLEDGED
        elif not result.physical_safe_state_observed:
            result.status = STATUS_SAFE_STATE_UNVERIFIED
        elif result.errors:
            result.status = STATUS_READ_ONLY_CHECKS_FAILED
        else:
            result.status = STATUS_BENCH_PASSED

    except Exception as exc:
        result.errors.append(f"Bench sequence error: {exc}")
        add_trace("bench_error", False, exc)
        if result.status == STATUS_NOT_EXECUTED:
            result.status = STATUS_READ_ONLY_CHECKS_FAILED

    finally:
        # Phase 16: Restore safe state and disconnect
        if runtime is not None:
            try:
                runtime.restore_safe_state()
                add_trace("restore_safe_state", True)
            except Exception as exc:
                add_trace("restore_safe_state", False, exc)

            try:
                runtime.disconnect()
                add_trace("disconnect", True)
            except Exception as exc:
                add_trace("disconnect", False, exc)

        result.runtime_trace = [t.to_dict() for t in trace]
        result.finished_at = _timestamp_iso()

    return result


def write_artifacts(result: BenchResult, output_dir: Path) -> None:
    """Write structured bench artifacts to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # m27d_manifest.json
    manifest = {
        "milestone": "M27-D",
        "bench_type": "zero_motion_bench",
        "evidence_reference": result.evidence_reference,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "status": result.status,
    }
    (output_dir / "m27d_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    # m27d_gate_evidence.json
    (output_dir / "m27d_gate_evidence.json").write_text(
        json.dumps(result.gate_evidence, indent=2, sort_keys=True), encoding="utf-8"
    )

    # m27d_sdk_detection.json
    (output_dir / "m27d_sdk_detection.json").write_text(
        json.dumps(result.sdk_detection, indent=2, sort_keys=True), encoding="utf-8"
    )

    # m27d_runtime_trace.jsonl
    with open(output_dir / "m27d_runtime_trace.jsonl", "w", encoding="utf-8") as f:
        for event in result.runtime_trace:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    # m27d_telemetry_snapshot.json
    (output_dir / "m27d_telemetry_snapshot.json").write_text(
        json.dumps(result.telemetry_snapshot, indent=2, sort_keys=True), encoding="utf-8"
    )

    # m27d_result_summary.json
    (output_dir / "m27d_result_summary.json").write_text(
        json.dumps(result.to_summary(), indent=2, sort_keys=True), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="M27-D Booster K1 Zero-Motion Bench Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script requires explicit operator confirmation for all safety gates.
No confirmation defaults to true. --execute-hardware is required for
any SDK import or SDK object construction.
        """.strip(),
    )

    # Required identification
    parser.add_argument("--robot-id", required=True, help="Expected robot identifier")
    parser.add_argument("--hardware-session-id", required=True, help="Unique hardware session identifier")
    parser.add_argument("--safety-policy-id", required=True, help="Safety policy identifier")
    parser.add_argument("--safety-policy-hash", required=True, help="Safety policy content hash")
    parser.add_argument("--evidence-reference", required=True, help="Evidence reference string")
    parser.add_argument("--gate-expiry-monotonic-ns", type=int, required=True, help="Gate expiry in monotonic nanoseconds")
    parser.add_argument("--output-dir", required=True, help="Output directory for bench artifacts")

    # Required safety confirmations (all default to False)
    parser.add_argument("--operator-confirmed-hardware", action="store_true", default=False,
                        help="Operator confirms real hardware is connected")
    parser.add_argument("--physical-estop-confirmed", action="store_true", default=False,
                        help="Physical E-stop is confirmed functional")
    parser.add_argument("--clear-test-area-confirmed", action="store_true", default=False,
                        help="Test area is confirmed clear")
    parser.add_argument("--battery-state-confirmed", action="store_true", default=False,
                        help="Battery state is confirmed adequate")
    parser.add_argument("--network-isolation-confirmed", action="store_true", default=False,
                        help="Network isolation is confirmed")
    parser.add_argument("--manual-operator-present", action="store_true", default=False,
                        help="Manual operator is confirmed present")

    # Vendor runtime and hardware execution flags
    parser.add_argument("--enable-vendor-runtime", action="store_true", default=False,
                        help="Enable vendor runtime (required for real SDK)")
    parser.add_argument("--execute-hardware", action="store_true", default=False,
                        help="Execute hardware (required for any SDK import)")

    # Optional
    parser.add_argument("--interface", default="lo", help="Network interface (default: lo)")

    # Suppressed arguments (not shown in help)

    args = parser.parse_args(argv)

    print("=" * 60)
    print("M27-D Booster K1 Zero-Motion Bench Runner")
    print("=" * 60)
    print(f"  Robot ID: {args.robot_id}")
    print(f"  Session: {args.hardware_session_id}")
    print(f"  Evidence: {args.evidence_reference}")
    print(f"  Output: {args.output_dir}")
    print(f"  Enable vendor runtime: {args.enable_vendor_runtime}")
    print(f"  Execute hardware: {args.execute_hardware}")
    print(f"  Zero-motion: enforced (only Move(0,0,0) permitted)")
    print()

    # Run bench
    result = run_bench(args)

    # Write artifacts
    output_dir = Path(args.output_dir)
    try:
        write_artifacts(result, output_dir)
        print(f"\nArtifacts written to: {output_dir}")
    except Exception as exc:
        print(f"ERROR writing artifacts: {exc}", file=sys.stderr)
        return 1

    # Report
    print(f"\nBench Result: {result.status}")
    if result.errors:
        print("Errors:")
        for err in result.errors:
            print(f"  - {err}")

    if result.status == STATUS_BENCH_PASSED:
        print("\n  BENCH PASSED - Zero-motion verification complete.")
        return 0
    else:
        print(f"\n  BENCH INCOMPLETE - Status: {result.status}")
        return 1


# Late import for type hint
from calibration_skill.domain.enums import MotionLifecycleState

if __name__ == "__main__":
    raise SystemExit(main())
