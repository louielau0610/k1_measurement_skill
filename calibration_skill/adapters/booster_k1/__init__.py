"""Booster K1 fake-runtime adapter skeleton for M27-B.

This package is intentionally hardware-free. It does not import the Booster SDK
and it does not register itself at import time.
"""
from __future__ import annotations

from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.adapters.booster_k1.config import BoosterK1AdapterConfig
from calibration_skill.adapters.booster_k1.identity import booster_k1_identity
from calibration_skill.adapters.booster_k1.runtime import BoosterK1RuntimeProtocol

__all__ = [
    "BoosterK1Adapter",
    "BoosterK1AdapterConfig",
    "BoosterK1RuntimeProtocol",
    "booster_k1_capabilities",
    "booster_k1_identity",
]
