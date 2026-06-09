# Introduction Draft v1

> **Status**: draft only — not a final manuscript section.
> **Citation safety**: uses only verified/partially verified citation keys from `paper/related_work/seed_references.bib`.
> **Basis**: synthesizes P1 seed literature, P2 gap analysis, P3 Related Work draft, M18 method skeleton/claim audit, and M13-M17 project artifacts.
> **Not an abstract**. Not a final novelty claim. Not a full manuscript.

---

## 1. Deployment motivation

Legged robots are increasingly deployed through high-level velocity command interfaces, where a planner or operator sends linear and angular velocity targets and expects the platform to track them [@TanRSS2018] [@HwangboSciRobot2019]. Command-conditioned locomotion policies and sim-to-real transfer pipelines have enabled rapid progress in robot agility and outdoor robustness [@MargolisRSS2022] [@MaRSS2024DrEureka]. However, deployment performance depends not only on the quality of a trained locomotion controller, but also on how faithfully commanded motion is executed on the real hardware under the specific deployment environment, floor surface, battery state, and payload.

For closed-source robots or SDK-driven platforms, this relationship is particularly opaque: the user operates through a manufacturer-provided interface (such as a DDS/ROS2 velocity command topic and an odometry feedback topic) but does not have access to the internal controller, state estimator parameters, or low-level actuator models. Under these conditions, the connection between commanded velocity and actual robot motion is a black-box system whose characteristics may vary with command magnitude, direction, and environment.

## 2. Problem: command-to-motion mismatch

When high-level velocity commands do not match executed motion — whether through under-tracking, over-tracking, deadzone behavior, or lateral/yaw drift — downstream navigation systems may assume a more reliable response than the robot actually provides [@FuCVPRW2022]. A planner that expects a commanded forward velocity to produce a certain displacement within a given time window may overestimate the robot's capability, leading to accumulated positioning error or, in the worst case, navigation decisions that the platform cannot execute.

This project studies the problem as a measurable deployment-layer response characteristic. Rather than modifying the robot's internal controller or training a new locomotion policy, the project treats the closed-source K1 quadruped as a measurement subject: externally commanded velocities and externally observed odometry are collected, structured through a research data schema, and analyzed to produce response predictions and advisory risk assessments. The current evaluation is limited to structural pipeline validation and does not yet include real navigation outcome metrics.

## 3. Candidate gap: closed-source deployment-layer response calibration

Prior work addresses several adjacent problems. Sim-to-real transfer research models actuator dynamics, latency, and domain randomization to close the reality gap during policy training [@TanRSS2018] [@HwangboSciRobot2019]. Rapid motor adaptation and online system identification allow policies to adjust to changing terrain, payload, and wear at deployment time [@KumarRMA2021] [@MargolisRSS2022]. Navigation-coupled locomotion work integrates terrain perception, proprioceptive signals, and footstep planning to constrain navigation decisions [@FuCVPRW2022] [@FanRSS2021STEP]. Risk-aware traversability frameworks assess environmental uncertainty for safe path planning [@FanRSS2021STEP].

These works generally assume the practitioner can modify the locomotion policy, access internal model parameters, or integrate perception and planning pipelines — assumptions that may not hold for closed-source, SDK-only deployment scenarios. The current seed literature does not yet establish a directly equivalent artifact-governed pipeline that operates purely at the external command-response interface of a closed-source legged robot. This motivates the present repository as a candidate contribution in the space of deployment-layer response calibration, recognizing that broader system-identification and commercial-SDK literature review is required before any final gap or novelty claim can be made.

## 4. Approach overview

This repository currently implements an artifact-governed pipeline that proceeds through five stages:

1. **Measurement v0 artifacts**: real K1 forward-velocity field measurements are collected under a read-only ROS2 logging protocol and validated through a research measurement profile.
2. **Velocity response dataset schema and dataset v1**: measurement records are structured through a JSON schema and consolidated into a sparse dataset of five command-response records with source provenance.
3. **Uncertainty-aware response model foundation**: a conservative hybrid response model produces velocity predictions, uncertainty labels, and confidence labels from the sparse dataset — without claiming calibrated probabilities.
4. **Navigation-aware reliability and risk mapping**: response predictions are translated into offline advisory risk categories, producing warning-level metadata for downstream interpretation.
5. **Pipeline evaluation and claim governance**: a paper-style evaluation package consolidates pipeline artifacts, separates supported structural claims from unsupported performance/safety claims, and documents unavailable metrics and required future experiments.

The current pipeline provides structural evidence for the existence and reproducibility of the artifact chain. It does not yet evaluate real navigation outcomes, report collision or success metrics, or calibrate uncertainty labels. The pipeline is measurement-only and advisory: it does not implement velocity compensation, inverse command mapping, navigation control, or safe command adaptation.

## 5. Current contributions as tentative contributions

The work currently contributes:

- **An artifact-governed measurement-to-model-to-risk-map pipeline** for black-box command-response characterization of a closed-source legged robot, with explicit separation between structural evidence and unsupported performance claims.
- **A sparse-evidence velocity response dataset and model contract** that labels uncertainty and confidence from five real K1 command-response records, with schema-level guardrails against fabricating or overinterpreting weak evidence.
- **An offline advisory risk interpretation layer** that maps response mismatch and uncertainty into navigation-relevant warning metadata, while clearly documenting that these labels are not calibrated probabilities and do not constitute navigation control.
- **A claim-governed evaluation package** that tracks project evidence, prior-work evidence, candidate gaps, prohibited claims, and upgrade conditions across milestones, enabling incremental drafting without overclaiming.

All contributions remain tentative and are positioned as candidate contributions, not final novelty. Each requires additional literature review, expanded measurement data, and/or real navigation outcome experiments before being upgraded.

## 6. Scope and limitations

The current repository operates under the following scope:

- **Single robot**: one K1 closed-source quadruped unit.
- **Sparse command set**: five forward-velocity commands from Measurement v0.
- **Single environment**: one indoor floor surface, one session.
- **No calibrated uncertainty**: M15R labels are metadata flags, not calibrated probability estimates.
- **No real navigation outcomes**: collision rate, near-miss rate, success rate, and navigation safety metrics are explicitly documented as unavailable.
- **No compensation**: velocity compensation logic is not implemented and remains a future milestone.
- **No safe command adapter**: safe command adaptation is not implemented.
- **No navigation controller**: the repository does not send navigation commands to a robot.

These limitations are structural to the current research stage and are essential context for interpreting every claim in this and subsequent drafts.

## 7. Paper organization placeholder

> **Draft note**: The following is a planned organization outline, not a finalized structure. It may be revised after P5 (Method draft) and P6 (Experiments draft).

The remainder of a potential future manuscript is planned as follows. Section 2 reviews related work across sim-to-real locomotion, adaptation, navigation-coupled planning, risk-aware evaluation, and black-box command-response calibration (draft v1 available at `paper/manuscript/sections/02_related_work_draft_v1.md`). Section 3 describes the method pipeline and its five stages (skeleton available at `paper/manuscript/sections/03_method_skeleton.md`). Section 4 presents the current experimental evidence, separating structural validation from missing navigation outcomes (skeleton available at `paper/manuscript/sections/04_experiments_skeleton.md`). Sections 5-7 address discussion, limitations, and conclusion as planned scaffolding content only.

## Known limitations of this draft

1. **Citation coverage reflects P3 limitations**: only 8 verified/partially verified seed references are available in `seed_references.bib`. Broader black-box system identification, commercial SDK calibration, and field robotics evaluation literature is needed.
2. **Contribution statements remain tentative**: all contribution bullets use candidate language and are not ready for final manuscript claims.
3. **No abstract exists**: this Introduction draft is not a substitute for a paper abstract, which should be written last, after all sections are drafted and evidence is reviewed.
4. **Organization section is a placeholder**: the "Paper organization" paragraph is planned content only and will need revision after P5 and P6.
5. **This draft does not establish final novelty or publication readiness** and is intended for revision after additional literature review and experiments.
