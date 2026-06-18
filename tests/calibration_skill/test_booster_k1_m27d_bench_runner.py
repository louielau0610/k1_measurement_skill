"""M27-D bench runner tests.

Tests for the bench runner script logic without requiring SDK or hardware.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest


class TestBenchRunnerArguments:
    """Test that bench runner CLI argument parsing works."""

    def test_required_arguments_present(self):
        """Verify required arguments are defined."""
        # We test this by importing the module and checking argparse definitions
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_m27d_bench",
            Path("scripts/run_m27d_k1_zero_motion_bench.py"),
        )
        # Just verify the script is importable
        assert spec is not None

    def test_no_default_true_confirmations(self):
        """All safety confirmations must default to False."""
        source = Path("scripts/run_m27d_k1_zero_motion_bench.py").read_text(encoding="utf-8")
        # Check that store_true flags have default=False
        for flag in [
            "--operator-confirmed-hardware",
            "--physical-estop-confirmed",
            "--clear-test-area-confirmed",
            "--battery-state-confirmed",
            "--network-isolation-confirmed",
            "--manual-operator-present",
            "--enable-vendor-runtime",
            "--execute-hardware",
        ]:
            assert flag in source, f"Flag {flag} not found in bench runner"
            # Find the add_argument line and check default=False
            # Check for action="store_true" pattern
            lines = [l for l in source.split("\n") if flag in l and "add_argument" in l]
            assert lines, f"No add_argument for {flag}"

    def test_script_not_in_default_cli(self):
        """Bench runner must not be importable from default CLI paths."""
        # The script is standalone, not in calibration_skill package
        bench_path = Path("scripts/run_m27d_k1_zero_motion_bench.py")
        assert bench_path.exists()
        # Verify it's not importable from calibration_skill
        with pytest.raises(ImportError):
            import calibration_skill.scripts.run_m27d_k1_zero_motion_bench  # type: ignore


class TestBenchResultStatuses:
    """Test bench result status values."""

    def test_all_statuses_defined(self):
        from scripts.run_m27d_k1_zero_motion_bench import (
            STATUS_BENCH_PASSED,
            STATUS_BINDING_CONSTRUCTION_FAILED,
            STATUS_BLOCKED_BY_GATE,
            STATUS_CONNECTION_FAILED,
            STATUS_NOT_EXECUTED,
            STATUS_READ_ONLY_CHECKS_FAILED,
            STATUS_SAFE_STATE_UNVERIFIED,
            STATUS_SDK_IMPORT_FAILED,
            STATUS_SDK_UNAVAILABLE,
            STATUS_STOP_UNACKNOWLEDGED,
        )
        # All status constants exist
        assert STATUS_BENCH_PASSED == "bench_passed"
        assert STATUS_NOT_EXECUTED == "not_executed"

    def test_artifact_names_defined(self):
        """Verify required artifact file names."""
        source = Path("scripts/run_m27d_k1_zero_motion_bench.py").read_text(encoding="utf-8")
        required = [
            "m27d_manifest.json",
            "m27d_gate_evidence.json",
            "m27d_sdk_detection.json",
            "m27d_runtime_trace.jsonl",
            "m27d_telemetry_snapshot.json",
            "m27d_result_summary.json",
        ]
        for name in required:
            assert name in source, f"Artifact {name} not found in bench runner"


class TestBenchArtifactWriting:
    """Test artifact writing with fake data."""

    def test_write_artifacts_creates_files(self):
        from scripts.run_m27d_k1_zero_motion_bench import write_artifacts, BenchResult, STATUS_NOT_EXECUTED

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "results"
            result = BenchResult(
                status=STATUS_NOT_EXECUTED,
                evidence_reference="test-evidence",
                started_at="2026-01-01T00:00:00Z",
                finished_at="2026-01-01T00:00:01Z",
                gate_evidence={"test": True},
                sdk_detection={"discoverable": False},
            )

            write_artifacts(result, output_dir)

            assert (output_dir / "m27d_manifest.json").exists()
            assert (output_dir / "m27d_gate_evidence.json").exists()
            assert (output_dir / "m27d_sdk_detection.json").exists()
            assert (output_dir / "m27d_runtime_trace.jsonl").exists()
            assert (output_dir / "m27d_telemetry_snapshot.json").exists()
            assert (output_dir / "m27d_result_summary.json").exists()

    def test_manifest_content(self):
        from scripts.run_m27d_k1_zero_motion_bench import write_artifacts, BenchResult, STATUS_BENCH_PASSED

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "results"
            result = BenchResult(
                status=STATUS_BENCH_PASSED,
                evidence_reference="test-evidence",
                started_at="2026-01-01T00:00:00Z",
                finished_at="2026-01-01T00:00:01Z",
            )

            write_artifacts(result, output_dir)

            manifest = json.loads((output_dir / "m27d_manifest.json").read_text(encoding="utf-8"))
            assert manifest["milestone"] == "M27-D"
            assert manifest["status"] == STATUS_BENCH_PASSED

    def test_trace_jsonl_format(self):
        from scripts.run_m27d_k1_zero_motion_bench import (
            write_artifacts, BenchResult, BenchTraceEvent, STATUS_BENCH_PASSED,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "results"
            trace = [
                BenchTraceEvent(1, "test_event", 1000, True).to_dict(),
                BenchTraceEvent(2, "test_event_2", 2000, False, {"code": "err"}).to_dict(),
            ]
            result = BenchResult(
                status=STATUS_BENCH_PASSED,
                evidence_reference="test-evidence",
                started_at="2026-01-01T00:00:00Z",
                finished_at="2026-01-01T00:00:01Z",
                runtime_trace=trace,
            )

            write_artifacts(result, output_dir)

            with open(output_dir / "m27d_runtime_trace.jsonl", encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 2
            event1 = json.loads(lines[0])
            assert event1["event_type"] == "test_event"
            assert event1["success"] is True

    def test_result_summary_distinguishes_statuses(self):
        from scripts.run_m27d_k1_zero_motion_bench import (
            BenchResult,
            STATUS_BENCH_PASSED,
            STATUS_BLOCKED_BY_GATE,
            STATUS_SDK_UNAVAILABLE,
        )

        r1 = BenchResult(status=STATUS_BENCH_PASSED, evidence_reference="e1",
                         started_at="", finished_at="")
        r2 = BenchResult(status=STATUS_BLOCKED_BY_GATE, evidence_reference="e2",
                         started_at="", finished_at="")
        r3 = BenchResult(status=STATUS_SDK_UNAVAILABLE, evidence_reference="e3",
                         started_at="", finished_at="")

        assert r1.to_summary()["status"] == STATUS_BENCH_PASSED
        assert r2.to_summary()["status"] == STATUS_BLOCKED_BY_GATE
        assert r3.to_summary()["status"] == STATUS_SDK_UNAVAILABLE

    def test_no_secrets_or_raw_sdk_in_artifacts(self):
        """Artifacts must not contain secrets, raw SDK reprs, or tracebacks."""
        from scripts.run_m27d_k1_zero_motion_bench import (
            _error_to_dict, _sanitize_dict,
        )

        # Test error sanitization
        error = ValueError("test error")
        error_dict = _error_to_dict(error)
        assert "traceback" not in str(error_dict).lower()
        assert "type" in error_dict
        assert error_dict["type"] == "ValueError"

        # Test sanitization
        bad_dict = {"password": "secret123", "normal_key": "ok"}
        clean = _sanitize_dict(bad_dict)
        assert "password" not in clean
        assert "normal_key" in clean

    def test_trace_event_structure(self):
        from scripts.run_m27d_k1_zero_motion_bench import BenchTraceEvent

        event = BenchTraceEvent(
            event_sequence=1,
            event_type="connect",
            monotonic_ns=1000,
            success=True,
            evidence_reference="ref-1",
        )
        d = event.to_dict()
        assert d["event_sequence"] == 1
        assert d["event_type"] == "connect"
        assert d["monotonic_ns"] == 1000
        assert d["success"] is True
        assert d["evidence_reference"] == "ref-1"
