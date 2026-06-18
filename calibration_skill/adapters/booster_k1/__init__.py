"""Booster K1 adapter for fake-runtime and vendor-runtime modes.

M27-D: This package supports both fake and vendor runtime modes.
It does not import the Booster SDK at package import time.
It does not register itself at import time.
"""
from __future__ import annotations

from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.capabilities import booster_k1_capabilities
from calibration_skill.adapters.booster_k1.config import (
    BoosterK1AdapterConfig,
    BoosterK1HardwareGate,
    K1_FAKE_RUNTIME_MODE,
    K1_VENDOR_RUNTIME_MODE,
)
from calibration_skill.adapters.booster_k1.identity import booster_k1_identity
from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeProtocol,
    BoosterK1RuntimeState,
)
from calibration_skill.adapters.booster_k1.vendor_types import (
    BoosterK1VendorBindingProtocol,
    BoosterK1VendorBindingMetadata,
    BoosterK1VendorSDKDetection,
)

__all__ = [
    "BoosterK1Adapter",
    "BoosterK1AdapterConfig",
    "BoosterK1HardwareGate",
    "BoosterK1RuntimeCommandReceipt",
    "BoosterK1RuntimeHealth",
    "BoosterK1RuntimeOdometry",
    "BoosterK1RuntimeProtocol",
    "BoosterK1RuntimeState",
    "BoosterK1VendorBindingMetadata",
    "BoosterK1VendorBindingProtocol",
    "BoosterK1VendorSDKDetection",
    "K1_FAKE_RUNTIME_MODE",
    "K1_VENDOR_RUNTIME_MODE",
    "booster_k1_capabilities",
    "booster_k1_identity",
]
