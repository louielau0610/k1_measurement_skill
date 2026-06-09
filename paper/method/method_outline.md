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

## Boundaries

This repository currently covers measurement and profile export only. Compensation and navigation safety belong to downstream projects unless explicitly re-scoped.
