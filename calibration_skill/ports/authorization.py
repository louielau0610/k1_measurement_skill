"""Port interface for operator authorization."""
from __future__ import annotations

from typing import Protocol

from calibration_skill.domain.enums import RobotPlatform
from calibration_skill.domain.safety import OperatorAuthorization


class OperatorAuthorizationProvider(Protocol):
    """Abstract interface for operator authorization.

    Defines how an authorization is requested or resolved
    without embedding UI logic in the domain layer.
    """

    def request_authorization(
        self,
        platform: RobotPlatform,
        robot_id: str,
        operations: tuple[str, ...],
        safety_policy_id: str,
        safety_policy_hash: str,
        duration_ns: int,
        operator_id: str,
    ) -> OperatorAuthorization:
        """Request operator authorization for the given operations.

        Returns an OperatorAuthorization if granted.
        Raises if the operator denies or the request times out.
        """
        ...

    def validate_authorization(
        self,
        authorization: OperatorAuthorization,
        now_ns: int,
    ) -> bool:
        """Check if an authorization is still valid at the given time."""
        ...
