"""Port interface for robot adapters."""
from __future__ import annotations

from typing import Protocol

from calibration_skill.domain.enums import ConnectionState, MotionLifecycleState
from calibration_skill.domain.identity import RobotIdentity
from calibration_skill.domain.capabilities import CapabilityDescriptor
from calibration_skill.domain.motion import CommandReceipt, VelocityCommand
from calibration_skill.domain.safety import PreflightReport


class RobotAdapter(Protocol):
    """Abstract interface for platform-specific robot control.

    All methods make timeout and failure semantics explicit.
    No concrete implementation is provided here.
    """

    @property
    def identity(self) -> RobotIdentity:
        """Get the robot's identity. Must be available after construction."""
        ...

    @property
    def capabilities(self) -> CapabilityDescriptor:
        """Get the robot's capability descriptor."""
        ...

    @property
    def connection_state(self) -> ConnectionState:
        """Current connection state."""
        ...

    def connect(self, timeout_s: float = 10.0) -> None:
        """Establish communication with the robot.

        Must be idempotent (safe to call when already connected).
        Raises on timeout or connection failure.
        """
        ...

    def disconnect(self) -> None:
        """Graceful teardown. Must send stop before disconnecting if in motion mode."""
        ...

    def preflight(self) -> PreflightReport:
        """Run preflight checks. Returns a report with blockers and warnings."""
        ...

    @property
    def motion_state(self) -> MotionLifecycleState:
        """Current motion lifecycle state."""
        ...

    def enter_locomotion_ready(self) -> None:
        """Transition to locomotion-ready state.

        Platform-specific sequence (e.g., kPrepare -> kWalking for K1).
        Raises if the transition fails or times out.
        """
        ...

    def send_velocity_command(self, command: VelocityCommand) -> CommandReceipt:
        """Send a velocity command to the robot.

        Must validate against safety envelope before sending.
        Must return a receipt immediately (does not wait for completion).
        Raises if the command is rejected or the adapter is in wrong state.
        """
        ...

    def stop(self) -> CommandReceipt:
        """Send zero-velocity stop command. Must be callable from any state."""
        ...

    def restore_safe_state(self) -> None:
        """Restore the robot to a safe state (safe standing/sitting)."""
        ...
