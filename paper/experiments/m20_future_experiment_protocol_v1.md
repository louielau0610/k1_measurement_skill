# M20 Future Experiment Protocol v1

> **Protocol only — no experiments have been executed.** This document defines the future experimental protocol needed to upgrade the manuscript from structural/artifact-level evidence toward real robot/navigation outcome evidence. No results are reported.

## Purpose

Define the minimum future experimental protocol required to upgrade the K1 velocity response research pipeline from structural validation to performance, safety, and generalization evaluation.

## Current evidence boundary

The manuscript v2 currently provides structural/artifact-level evidence only. All performance, safety, and generalization claims require future experiments as listed below.

## Experiment tier overview

| tier | purpose | required before claiming |
| --- | --- | --- |
| Tier 1 | Repeated velocity response characterization | Predictive model quality |
| Tier 2 | Held-out command response evaluation | Predictive model accuracy |
| Tier 3 | Real navigation outcome evaluation | Advisory risk usefulness |
| Tier 4 | Before/after advisory comparison | Navigation outcome improvement |

## Tier 1: Repeated velocity response characterization

**Purpose**: Strengthen command-to-motion response evidence with repeated trials to estimate variability.

**Design**:
- Command grid: expand from 5 to at least 8-10 forward velocity points (0.05 to 0.60 m/s).
- Optional: add lateral (`v_y`) and angular (`omega_z`) command dimensions.
- Repeated trials: at least 3-5 trials per command velocity.
- Trial duration: 5-10 seconds per trial (uniform across commands).
- Warm-up: 2-3 stabilization trials before data collection.
- Reset: return to start position between trials.
- Surface labels: document floor type, condition, and session identifier.
- Raw log provenance: all trials logged to read-only ROS2 rosbag.

**Metrics collected**: commanded velocity, measured actual velocity, tracking error, signed/absolute error, response ratio, response delay, stop distance, lateral drift, yaw drift, qualitative response label, uncertainty/reliability label, trial validity.

**Deliverables**: expanded dataset v2 with repeated-trial records and variability estimates.

## Tier 2: Held-out command response evaluation

**Purpose**: Evaluate response-model generalization to command points not used for model fitting.

**Design**:
- Split command grid into fit (60%), validation (20%), held-out (20%) sets.
- Fit model on fit set only.
- Report held-out MAE and RMSE on numeric records.
- Report qualitative label agreement on qualitative-only records.
- Explicitly separate exact-source reconstruction (sanity check, MAE=0.0 expected on fit set) from held-out predictive evaluation.
- Stratify errors by uncertainty label where possible.

**Claim boundary**: Held-out evaluation supports a predictive quality claim. It does not support a calibrated uncertainty claim (requires additional repeated evidence).

## Tier 3: Real navigation outcome evaluation

**Purpose**: Evaluate whether advisory risk labels correlate with downstream navigation outcomes.

**Design**:
- Define 3-5 fixed navigation tasks (e.g., corridor traversal, obstacle avoidance, precision approach).
- Repeated trials: at least 5 trials per task.
- Log: commanded trajectory, actual trajectory, collision events, near-miss events, task completion status, interventions, aborts.
- Advisory condition: risk labels available to the analysis/reviewer (not real-time control).
- Control/baseline condition: no advisory risk labels used.

**Metrics**: task success rate, failure category, collision count, near-miss count, minimum obstacle distance, path deviation, completion time, intervention count, stop/abort count.

**Claim boundary**: Correlation between risk warnings and navigation outcomes can be evaluated. Navigation safety improvement remains unclaimed unless statistically meaningful reduction in collision/near-miss/success-rate metrics is demonstrated.

## Tier 4: Before/after advisory comparison

**Purpose**: Evaluate whether advisory risk labels change planning/operator behavior.

**Design**:
- Baseline condition: planner/operator without advisory risk labels.
- Advisory condition: planner/operator with access to advisory risk labels (offline or analysis-only).
- Compare navigation outcome metrics between conditions.
- Define what is allowed in advisory condition (analysis, warning display, manual decision support) vs. what is prohibited (automatic compensation, safe adapter execution, real-time control).

**Metrics**: same as Tier 3, with before/after statistical comparison.

**Claim boundary**: Advisory usefulness can be evaluated if outcome metrics improve under advisory condition. Safety improvement requires formal safety metric definitions and statistically meaningful comparison.

## Required metrics

See `paper/experiments/m20_metric_definitions_v1.md` for full metric definitions.

## Data logging and provenance requirements

- All trials logged via read-only ROS2 rosbag (same protocol as Measurement v0).
- Each trial recorded with: robot ID, session ID, surface type, command velocity, timestamps.
- Raw logs archived before processing.
- Processed records include source file provenance.

## Trial validity and exclusion rules

- Trial invalid if: robot collision during trial, logging interruption, command topic dropout, odometry gap > 1s.
- Exclusion recorded with reason. Excluded trials not used for evaluation but counted in trial coverage.

## Claim-upgrade criteria

See `paper/tables/m20_claim_upgrade_evidence_matrix.md` for detailed upgrade criteria.

## What remains out of scope

- Velocity compensation implementation.
- Inverse command mapping.
- Safe command adapter logic.
- Navigation control.
- Real-time robot command adaptation.
- Any modification to the K1 SDK or internal controller.

## Recommended execution order

1. Tier 1 (repeated trials) — establishes variability evidence.
2. Tier 2 (held-out evaluation) — evaluates model on new command points.
3. Tier 3 (navigation outcomes) — tests advisory warning/outcome correlation.
4. Tier 4 (before/after comparison) — evaluates advisory impact.

## How M20 connects to future manuscript v3

Results from Tiers 1-4 would be integrated into a future manuscript v3:
- Expanded dataset with repeated trials and variability.
- Held-out prediction error metrics.
- Navigation outcome results with advisory/no-advisory comparison.
- Upgraded claims where evidence supports them. Claims that remain unsupported stay documented as non-claims.
