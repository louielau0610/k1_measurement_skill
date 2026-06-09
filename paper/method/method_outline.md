# Method Outline

Working title:

Navigation-Aware Velocity Response Calibration for Closed-Source Legged Robots

## Method Scope

- Measurement module:
- Velocity profile contract:
- Downstream warning/confidence layer:
- Downstream compensation adapter:
- M13 velocity response foundation:
  - research problem: `v_actual = f(v_cmd, environment, robot_state)`
  - dataset schema v1: `configs/velocity_response_dataset_schema_v1.json`
  - modeling plan: `paper/method/velocity_response_modeling_plan.md`
- M14 dataset construction layer:
  - Measurement v0 artifacts are converted into `outputs/research_datasets/velocity_response_dataset_v1.json`
  - dataset construction precedes M15 baseline response modeling
  - unavailable response dimensions remain explicit limitations, not fabricated values
- M15R response model foundation:
  - uncertainty-aware hybrid response model
  - minimal baseline hooks for future comparison
  - uncertainty/confidence labels are not calibrated probabilities
- M16 navigation-aware risk mapping:
  - response prediction is mapped to tracking reliability
  - tracking reliability is mapped to offline risk level
  - advisory warning output is generated without navigation control
- M17 pipeline evaluation:
  - method artifacts are organized into evaluation reports and artifact tables
  - outputs should support later manuscript drafting without becoming final paper prose
- M18 paper method skeleton:
  - skeleton path: `paper/manuscript/sections/03_method_skeleton.md`
  - stages: measurement artifact construction -> velocity response dataset construction -> uncertainty-aware response modeling -> navigation-aware risk mapping -> claim-governed evaluation
  - this remains bullet-point method structure, not final manuscript prose

## Boundaries

This repository currently covers measurement and profile export only. Compensation and navigation safety belong to downstream projects unless explicitly re-scoped.

M18 preserves this boundary: no compensation, no inverse command mapping, no navigation control, and no safe command adapter logic are introduced.
