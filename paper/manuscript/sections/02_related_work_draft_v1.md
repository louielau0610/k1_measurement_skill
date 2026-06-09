# Related Work Draft v1

> **Status**: draft only — not a final manuscript section.
> **Citation safety**: uses only verified or partially verified citation keys from `paper/related_work/seed_references.bib`.
> **Basis**: synthesizes P1 literature matrix v1 and P2 gap analysis v1.
> **No final novelty claim**. No performance superiority claim. No navigation safety improvement claim.
> This draft is intended for later editing and expansion; additional literature review is needed before submission.

---

## 1. Sim-to-real and learned legged locomotion

Learned locomotion policies have demonstrated agile and robust behaviors on quadruped robots, with much of the progress driven by simulation training and sim-to-real transfer [@TanRSS2018] [@HwangboSciRobot2019]. Tan *et al.* [@TanRSS2018] showed that closing the sim-to-real gap requires careful modeling of actuator dynamics, latency, and domain randomization, while Hwangbo *et al.* [@HwangboSciRobot2019] demonstrated that trained policies can deploy directly on complex hardware such as ANYmal. More recently, LLM-guided domain randomization [@MaRSS2024DrEureka] has been proposed to automate the sim-to-real configuration process for legged locomotion tasks.

These works primarily target the training and deployment of learned locomotion controllers under the assumption that the practitioner has full access to the policy, simulator, and low-level control stack. They do not establish an external, measurement-only calibration pipeline for closed-source robots where the user can only observe command-response behavior through the manufacturer-provided SDK interface. In contrast, our current project focuses on artifact-governed measurement and response modeling under black-box deployment constraints, using externally collected velocity command and odometry records from a closed-source K1 quadruped without modifying or retraining its internal locomotion policy.

## 2. Rapid motor adaptation and deployment adaptation

Several recent works address deployment-time adaptation as a strategy for robust legged locomotion. Kumar *et al.* [@KumarRMA2021] introduced a base-policy plus adaptation-module architecture that learns to compensate for varying terrain, payload, and wear online, deployed on a Unitree A1. Margolis and Agrawal [@MargolisRSS2022] proposed end-to-end RL controllers with adaptive velocity-command curricula and online system identification for high-speed outdoor locomotion on the MIT Mini Cheetah.

These adaptation approaches operate at the controller or policy level and typically require the ability to modify the locomotion controller. They are complementary to, and conceptually distinct from, an external, artifact-governed calibration workflow that measures and labels command-to-motion response mismatch without altering the robot's control stack. Our current M15R response model foundation labels uncertainty and confidence from sparse measurement records, but it does not perform online adaptation, policy modification, or system identification of internal controller parameters.

## 3. Navigation-coupled legged locomotion

The interface between high-level navigation and low-level locomotion has received increasing attention in legged robotics. Fu *et al.* [@FuCVPRW2022] coupled vision-based cost maps with proprioceptive safety signals to constrain legged robot navigation speeds, demonstrating that awareness of low-level walking capability can influence navigation decisions. Fan *et al.* [@FanRSS2021STEP] developed a stochastic traversability evaluation and planning framework (STEP) that assesses terrain risk under uncertainty for safe off-road navigation across wheeled and legged platforms.

These works generally assume access to terrain perception, path planning, and a controllable locomotion stack, and they derive safety or risk signals from perceptual and geometric features of the environment. Our project takes a different, narrower approach: it derives offline advisory risk metadata specifically from externally measured command-to-motion response mismatch, without terrain perception, without a planner, and without controlling the robot's navigation stack. The motivation is that, for closed-source deployment, the command-response relationship itself may carry useful warning information for downstream planning systems.

## 4. Risk- and uncertainty-aware navigation

Risk-aware planning and uncertainty-aware traversability evaluation have been studied across ground and legged robot platforms. STEP [@FanRSS2021STEP] provides a comprehensive framework for reasoning about terrain traversability under localization and sensing uncertainty using CVaR-based tail-risk assessment. This literature supports the broader principle that navigation planning benefits from explicit uncertainty representation.

Our M15R/M16 pipeline produces uncertainty/confidence labels and advisory risk categories from response model predictions, inspired by but not equivalent to the calibrated risk frameworks found in the traversability literature. A critical limitation is that our current labels are not calibrated probabilities: they are derived from sparse single-session K1 measurement evidence and are intended as conservative metadata flags, not as safety guarantees. Further experiments are required to evaluate whether these response-derived labels can be calibrated and to assess their correspondence with established risk metrics.

## 5. Field robotics metrics and evaluation

Field robotics evaluation protocols emphasize repeatable outcome metrics such as success rate, collision rate, near-miss rate, and traversability scores. Prior work such as STEP [@FanRSS2021STEP] includes field validation across extreme terrain, and the broader traversability- and navigation-evaluation literature defines metric categories against which deployment claims should be measured.

Our current M17 pipeline evaluation is structural rather than performance evaluation: it validates that the measurement-to-dataset-to-model-to-risk-map artifact chain is internally consistent and reproducible, but it does not report real navigation outcomes. Collision, near-miss, success-rate, and navigation-safety metrics are explicitly recorded as unavailable and as required evidence for any future performance or safety claim. The field robotics metrics literature provides the vocabulary for what would constitute an adequate evaluation, and it reinforces the conservative position that structural validation alone does not constitute navigation performance evidence.

## 6. Black-box command-response calibration and deployment-layer mismatch

Command-response modeling, system identification, and external calibration have been addressed in several adjacent robotics domains. Tan *et al.* [@TanRSS2018] performed system identification of actuator and latency parameters as part of their sim-to-real pipeline. Yang *et al.* [@YangRAL2022] proposed online kinematic calibration for legged robots using velocity prediction errors within a state estimator. Margolis and Agrawal [@MargolisRSS2022] incorporated online system identification into their RL controller to handle deployment-domain shift.

These works motivate the value of characterizing and compensating for deployment mismatch, but they typically assume access to the robot's internal model parameters, state estimator, or controller structure. The current seed literature does not yet establish a directly equivalent artifact-governed pipeline that operates purely at the deployment command-response interface of a closed-source legged robot — measuring commands and odometry externally, validating sparse evidence through a research schema, and deriving conservative response predictions and risk labels without internal access. This motivates further literature review in black-box system identification and commercial quadruped SDK calibration before any final gap or novelty claim can be made.

## 7. Positioning of the current work

The work in this repository currently implements a conservative, artifact-governed pipeline that transforms real K1 forward-velocity measurement artifacts into dataset records, response predictions, uncertainty/confidence labels, advisory risk assessments, and claim-governed evaluation artifacts. The pipeline is measurement-only: it does not implement velocity compensation, inverse command mapping, navigation control, or safe command adaptation.

The project is positioned as a set of candidate contributions, not as final novelty. The current evidence — five sparse single-session command-response records, conservative model outputs, and structural pipeline validation — is sufficient to support the existence of the pipeline but insufficient to support performance, safety, or generalization claims. Additional literature review, multi-session measurement, and real navigation outcome experiments are required before the candidate contributions can be upgraded.

## Known limitations of this draft

1. **Citation coverage is limited to 8 verified/partially verified seed references.** The P1 literature matrix contains 16 entries, but only 8 have verified BibTeX entries in `seed_references.bib`. Eight additional matrix entries (RudinCoRL2021, MargolisCoRL2022, DaoArxiv2026, GangapurwalaArxiv2020, GrandiaTRO2023, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025) lack BibTeX entries and are not cited in this draft. These should be added to the BibTeX file and the draft expanded after verification.
2. **Sections 4 and 5 have the thinnest citation support** — both currently rely primarily on a single verified source [@FanRSS2021STEP]. Broader traversability risk and field evaluation literature review is needed.
3. **No cross-comparison with commercial quadruped SDK calibration literature.** P1 did not surface papers that specifically address calibration workflows for commercial closed-source robot SDKs.
4. **This draft does not establish a novelty claim** and is not ready for a final manuscript submission. It is a structural first pass intended to be revised after P10 manuscript assembly and additional literature and after additional literature and experiments.
