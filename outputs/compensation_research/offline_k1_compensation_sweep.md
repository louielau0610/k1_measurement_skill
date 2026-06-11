# Offline K1 Compensation Sweep

Scope: offline prototype only. This is not physical validation and not deployment-ready compensation.

| desired_actual_velocity_mps | recommended_command_velocity_mps | feasibility_status | reason |
| --- | --- | --- | --- |
| 0.1 | None | infeasible_deadzone | desired velocity 0.100 is below minimum effective actual velocity 0.302 |
| 0.2 | None | infeasible_deadzone | desired velocity 0.200 is below minimum effective actual velocity 0.302 |
| 0.3 | None | infeasible_deadzone | desired velocity 0.300 is below minimum effective actual velocity 0.302 |
| 0.35 | None | insufficient_evidence | risk policy conservative removed all candidate cells |
| 0.4 | None | insufficient_evidence | risk policy conservative removed all candidate cells |
| 0.45 | None | insufficient_evidence | risk policy conservative removed all candidate cells |
| 0.5 | None | insufficient_evidence | risk policy conservative removed all candidate cells |
| 0.6 | None | insufficient_evidence | risk policy conservative removed all candidate cells |
