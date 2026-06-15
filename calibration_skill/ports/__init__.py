"""Ports layer: abstract interfaces for external dependencies.

All interfaces use typing.Protocol. No vendor SDK imports.
No concrete implementations are provided here.
"""
from calibration_skill.ports.robot import RobotAdapter
from calibration_skill.ports.telemetry import TelemetryStream
from calibration_skill.ports.authorization import OperatorAuthorizationProvider
from calibration_skill.ports.emergency_stop import EmergencyStop
from calibration_skill.ports.storage import ProfileRepository
from calibration_skill.ports.audit import AuditSink
from calibration_skill.ports.clock import MonotonicClock
from calibration_skill.ports.factory import AdapterFactory, ConnectionConfig

__all__ = [
    "RobotAdapter",
    "TelemetryStream",
    "OperatorAuthorizationProvider",
    "EmergencyStop",
    "ProfileRepository",
    "AuditSink",
    "MonotonicClock",
    "AdapterFactory",
    "ConnectionConfig",
]
