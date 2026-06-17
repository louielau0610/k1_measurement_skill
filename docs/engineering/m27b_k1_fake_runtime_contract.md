# M27-B K1 Fake Runtime Contract

The fake runtime contract is the only K1 runtime boundary used by M27-B. The
production package defines the protocol in
`calibration_skill/adapters/booster_k1/runtime.py`; tests provide the concrete
fake in `tests/calibration_skill/fakes/fake_booster_k1_runtime.py`.

The protocol surface is intentionally narrow:

- `connect` and `disconnect`
- identity metadata
- current motion state
- prepare and walking mode transitions
- body velocity command receipt
- stop and restore safe state
- odometry, robot state, and optional battery reads
- health check
- deterministic monotonic time through `now_ns`

The test fake supports deterministic call history, deterministic monotonic time,
fake odometry/state sequences, command receipts, stop receipts, and failure
injection for connect, health, command, stop, and telemetry-unavailable cases.

The fake runtime must not open sockets, spawn subprocesses, sleep, read
environment variables, read files, import vendor SDKs, or use wall-clock time.
Tests enforce the ordinary no-socket/no-subprocess/no-sleep boundary.
