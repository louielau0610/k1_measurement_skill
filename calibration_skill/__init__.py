"""Calibration Skill — Engineering-grade legged robot velocity calibration.

Package structure:
- domain/  : Pure platform-independent value objects and invariants
- ports/   : Abstract interfaces (Protocols) for external dependencies
- schemas/ : Versioned external contracts and deterministic JSON codecs

No vendor SDK imports. No hardware I/O. No network I/O.
"""
from calibration_skill import domain, ports, schemas

__version__ = "0.1.0"
__all__ = ["domain", "ports", "schemas"]
