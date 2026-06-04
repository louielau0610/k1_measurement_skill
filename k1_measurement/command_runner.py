"""Dry-run command runner skeleton for K1 forward velocity measurement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VelocityCommand:
    """Forward-only velocity command used by the measurement plan."""

    vx_mps: float
    vy_mps: float = 0.0
    wz_radps: float = 0.0


class CommandSafetyError(ValueError):
    """Raised when a command violates measurement-stage safety constraints."""


class CommandRunner:
    """Command runner that defaults to dry-run and never sends robot commands yet."""

    def __init__(self, max_vx_cmd_mps: float = 0.4, dry_run: bool = True) -> None:
        self.max_vx_cmd_mps = max_vx_cmd_mps
        self.dry_run = dry_run

    def validate(self, command: VelocityCommand, manual_confirmed: bool = False) -> None:
        if command.vx_mps < 0:
            raise CommandSafetyError("Only non-negative forward velocity is allowed in v0.")
        if command.vx_mps > self.max_vx_cmd_mps:
            raise CommandSafetyError("Forward velocity exceeds configured safety limit.")
        if command.vy_mps != 0.0 or command.wz_radps != 0.0:
            raise CommandSafetyError("v0 does not allow lateral motion or turning.")
        if not self.dry_run and not manual_confirmed:
            raise CommandSafetyError(
                "Manual confirmation, emergency-stop readiness, and verified topics are required."
            )

    def run(self, command: VelocityCommand, manual_confirmed: bool = False) -> dict[str, object]:
        """Validate a command and return a dry-run record.

        TODO: Add a real robot interface only after ROS2 command topics and message types
        are verified in a safe test area.
        """

        self.validate(command, manual_confirmed=manual_confirmed)
        return {
            "dry_run": self.dry_run,
            "sent_to_robot": False,
            "vx_mps": command.vx_mps,
            "vy_mps": command.vy_mps,
            "wz_radps": command.wz_radps,
            "safety_reminder": "Confirm emergency stop and open test area before real commands.",
        }
