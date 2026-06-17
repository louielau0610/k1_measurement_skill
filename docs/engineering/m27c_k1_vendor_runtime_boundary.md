# M27-C K1 Vendor Runtime Boundary

M27-C creates a fail-closed boundary for future Booster K1 vendor runtime work.
The boundary lives in `calibration_skill/adapters/booster_k1/vendor_runtime.py`.

The module is safe to import in ordinary runtime paths because it does not
import the real Booster SDK. Availability detection uses
`importlib.util.find_spec("booster_robotics_sdk")`, which checks discovery
metadata without importing or constructing SDK objects.

M27-C exports:

- `BoosterK1VendorRuntimeStatus`
- `BoosterK1RuntimeUnavailable`
- `BoosterK1VendorRuntime`
- `detect_booster_sdk_availability()`
- `create_booster_k1_vendor_runtime()`

The placeholder fails closed for every creation path:

- missing hardware gate -> structured gate-missing error
- incomplete hardware gate -> structured gate-incomplete error
- expired hardware gate -> structured gate-expired error
- missing SDK -> structured SDK-unavailable error
- valid-looking gate plus importable SDK -> not implemented in M27-C

No K1 hardware execution is enabled by this milestone. M27-D must define the
bench integration procedure before any real SDK object or hardware-facing
runtime can be created.
