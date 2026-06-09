# M20 Navigation Outcome Protocol v1

> **Protocol only — no navigation trials have been executed.** This defines how future navigation outcome experiments should be conducted.

## Purpose

Define the protocol for Tier 3 and Tier 4 navigation outcome experiments. The protocol separates advisory risk labeling from compensation and control.

## Navigation task setup

- Fixed start and goal positions per task.
- Known obstacle layout (documented in task spec).
- Flat indoor surface (multi-surface extension in Tier 1).
- Robot velocity commands issued by operator or pre-planned path.
- All trials logged via read-only ROS2 rosbag.

## Baseline condition

- No advisory risk labels available.
- Operator/planner uses standard navigation commands only.
- Record all Tier 3 navigation outcome metrics.

## Advisory condition

- Advisory risk labels available as pre-trip or in-trip information.
- Labels may be displayed as: warning indicators, risk-level color codes, or text advisories.
- Operator may use labels for manual decision support (e.g., reducing commanded velocity in high-risk regime).

## Allowed advisory usage

- Display of risk warning categories to operator/analyst.
- Pre-trip velocity selection informed by risk warnings.
- Post-trip analysis of risk/outcome correlation.
- Manual decision support based on risk information.

## Disallowed control/compensation usage

- Automatic velocity compensation based on risk level.
- Automatic command adaptation or inverse mapping.
- Real-time navigation control based on risk mapper output.
- Safe command adapter execution.
- Any closed-loop control that modifies robot commands without operator approval.

## Outcome definitions

| outcome | definition |
| --- | --- |
| success | Task completed within time limit, within path constraints, without collision |
| failure | Task not completed, collision occurred, or constraints violated |
| abort | Operator-initiated stop before task completion |

## Collision/near-miss definitions

| event | definition |
| --- | --- |
| collision | Physical contact between robot and obstacle/environment, confirmed by video or sensor log |
| near-miss | Robot passes within threshold distance of obstacle (e.g., < 0.2 m) without contact |

## Path deviation

Root-mean-square distance between planned/commanded trajectory and actual odometry trajectory, computed over the task duration.

## Intervention/abort definition

| event | definition |
| --- | --- |
| intervention | Operator manually overrides robot command during task |
| abort | Operator issues stop command and terminates task before completion |

## Trial exclusion criteria

- Logging failure or data corruption during trial.
- Robot hardware fault or battery depletion during trial.
- External interference (e.g., person walking into test area).
- Excluded trials recorded with reason but not used in outcome analysis.

## Analysis plan

- Compare navigation outcome metrics between baseline and advisory conditions.
- Report descriptive statistics (mean, CI, effect size).
- Avoid claiming safety improvement unless statistically meaningful difference in collision/near-miss/success-rate metrics.
- Report risk-warning exposure and warning-to-outcome association.

## Claim boundary

This protocol evaluates correlation between advisory risk labels and navigation outcomes. It does not implement compensation, safe command adaptation, or real-time navigation control. Navigation safety improvement is not claimed unless collision/near-miss/success-rate metrics show statistically meaningful improvement under the advisory condition.
