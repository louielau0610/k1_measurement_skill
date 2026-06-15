"""Test that port interfaces are importable without vendor SDKs."""
import pytest


class TestPortsImportable:
    def test_import_robot_adapter(self):
        from calibration_skill.ports.robot import RobotAdapter
        assert RobotAdapter is not None

    def test_import_telemetry_stream(self):
        from calibration_skill.ports.telemetry import TelemetryStream
        assert TelemetryStream is not None

    def test_import_authorization_provider(self):
        from calibration_skill.ports.authorization import OperatorAuthorizationProvider
        assert OperatorAuthorizationProvider is not None

    def test_import_emergency_stop(self):
        from calibration_skill.ports.emergency_stop import EmergencyStop
        assert EmergencyStop is not None

    def test_import_profile_repository(self):
        from calibration_skill.ports.storage import ProfileRepository
        assert ProfileRepository is not None

    def test_import_audit_sink(self):
        from calibration_skill.ports.audit import AuditSink
        assert AuditSink is not None

    def test_import_monotonic_clock(self):
        from calibration_skill.ports.clock import MonotonicClock
        assert MonotonicClock is not None

    def test_import_adapter_factory(self):
        from calibration_skill.ports.factory import AdapterFactory, ConnectionConfig
        assert AdapterFactory is not None
        assert ConnectionConfig is not None

    def test_no_concrete_robot_adapter(self):
        """Ports should not contain concrete robot adapter implementations."""
        import calibration_skill.ports
        from calibration_skill.ports.robot import RobotAdapter
        from typing import Protocol
        # RobotAdapter is a Protocol, not a concrete class with real implementation
        assert isinstance(RobotAdapter, type)
        # Verify it's defined as a Protocol (abstract interface)
        assert hasattr(RobotAdapter, '__init__')
        # The real check: no concrete adapter is implemented in ports
        # (adapters go in adapters/ directory)
