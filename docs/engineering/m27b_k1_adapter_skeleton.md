# M27-B K1 Adapter Skeleton

M27-B adds the first new-architecture Booster K1 adapter skeleton under
`calibration_skill/adapters/booster_k1/`. The adapter is limited to an injected
fake runtime and remains outside the default CLI runtime.

Implemented files:

- `config.py` defines `BoosterK1AdapterConfig` with explicit robot ID, profile
  ID, runtime mode, dry-run flag, safety policy, velocity limits, timeouts, and
  operator-authorization policy.
- `capabilities.py` defines the conservative K1 capability descriptor. Supported
  capabilities are marked `bench_verified` only because the available evidence
  is fake-runtime test evidence. No capability is hardware verified.
- `identity.py` maps explicit config and optional runtime metadata into
  `RobotIdentity(platform=booster_k1, morphology=biped_humanoid)`.
- `runtime.py` defines `BoosterK1RuntimeProtocol` and small fake-runtime data
  value objects.
- `adapter.py` implements `BoosterK1Adapter` against only the injected runtime
  protocol.
- `registry.py` provides explicit fake registration for test registries. It is
  not imported or called by default runtime composition.

Lifecycle mapping:

```text
prepare -> walking -> Move(vx, 0.0, 0.0)
```

This mapping is treated as repository-evidenced from M27-A audits, but M27-B
still proves it only through deterministic fake runtime tests.

M27-B does not connect to K1, import Booster SDK, open sockets, start DDS, send
UDP, or claim hardware readiness. M27-C is required before any real SDK runtime
integration.
