"""M26-C supported skill operation names."""

OP_PREFLIGHT = "preflight"
OP_DRY_RUN_VELOCITY_COMMAND = "dry_run_velocity_command"
OP_DRY_RUN_COLLECT_TELEMETRY = "dry_run_collect_telemetry"
OP_DRY_RUN_STOP = "dry_run_stop"
OP_DRY_RUN_END_TO_END = "dry_run_end_to_end"

SUPPORTED_OPERATIONS: tuple[str, ...] = (
    OP_PREFLIGHT,
    OP_DRY_RUN_VELOCITY_COMMAND,
    OP_DRY_RUN_COLLECT_TELEMETRY,
    OP_DRY_RUN_STOP,
    OP_DRY_RUN_END_TO_END,
)

COMMAND_OPERATIONS: tuple[str, ...] = (
    OP_DRY_RUN_VELOCITY_COMMAND,
    OP_DRY_RUN_END_TO_END,
)
