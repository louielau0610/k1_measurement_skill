# Downstream Usage Boundary v0 / 下游使用边界 v0

## Purpose / 目的

本文说明 downstream compensation / navigation-safety modules 可以从 measurement v0 profile 中假设什么，以及不能假设什么。当前 profile 是 measurement output contract，不是补偿器、导航控制器或运动命令生成器。

## Allowed Downstream Uses / 允许用途

- Read `outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json`.
- Identify whether a target velocity lies in observed deadzone, transition, or stable region.
- Surface warnings such as `target speed below observed effective threshold`.
- Use `0.5 m/s` as a lab-hard-floor stable reference only.
- Use current profile for design decisions and safety annotations.
- Use readiness flags to gate downstream behavior.

## Disallowed Downstream Uses / 禁止用途

- Do not automatically rescale command velocity using one global gain.
- Do not assume `0.1 m/s` can be fixed by simple multiplication.
- Do not claim low-speed deadzone is solved.
- Do not use the profile as a universal K1 model.
- Do not issue movement commands from this repository.
- Do not use manual-controller state as a measurement input.
- Do not reintroduce `battery_state` as a required v0 measurement input.
- Do not treat this single-session profile as compensation-grade calibration.

## Interface Contract Summary / 接口契约摘要

- Input artifact: `outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json`
- Output semantics:
  - observed regions
  - thresholds
  - readiness flags
  - limitations
- No corrected command output.

The profile may be consumed as structured context by downstream modules. It must not be used to generate executable robot commands inside `k1_measurement_skill`.

## Recommended Downstream Design / 推荐下游设计

- Build warning/confidence layer first.
- Add compensation only after repeated trials and variance estimation.
- Keep environment-specific profiles; do not merge unrelated floors or sessions without an explicit model.
- Use external ground truth if compensation is required.
- Keep controller-level low-speed deadzone elimination separate from measurement.

## Decision Table / 决策表

| Target velocity | Downstream interpretation |
| --- | --- |
| below `0.3 m/s` | low confidence / observed ineffective risk |
| `0.3` to `0.45 m/s` | transition / under-tracking likely |
| `0.45` to `0.5 m/s` | near-stable to stable in current profile |
| beyond observed range | unknown / requires new test |

## Practical Notes / 实用说明

`navigation_warning_ready = true` means downstream warning logic may already flag low-speed targets as unreliable in matching conditions. It does not mean navigation control is implemented here.

`compensation_ready = false` means downstream modules must not infer a corrected velocity curve from this v0 profile alone.
