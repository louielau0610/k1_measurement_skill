# M17 管线评估与论文式报告准备

M17 的目标是把 M13 到 M16 的 research pipeline artifact 统一评估和整理，为后续 M18 / P1 的论文方法组织、图表和 claim audit 做准备。M17 不是完整论文草稿，也不是真实导航性能评估。

## 为什么需要 M17

当前仓库已经包含 schema、dataset、response model、risk map 和 claim-control artifact。进入论文写作前，需要先明确哪些 artifact 存在、哪些可以脚本复现、哪些证据可以支持结构性 claim、哪些指标仍然不可用。

## Consolidated Artifacts

- M13 / M13.1: schema v1、schema validation、Measurement v0 bridge。
- M14: velocity response dataset v1、validation report、future trial template。
- M15R: response model predictions、limited evaluation、baseline hooks。
- M16: navigation-aware risk map、risk evaluation。
- P0-M17: claim registry、evidence table、non-claims。

## 当前证据支持什么

当前证据支持结构性 / 软件 artifact claim：

- Measurement v0 artifact 存在；
- dataset schema v1 和 dataset v1 存在；
- response model foundation 存在；
- offline navigation-aware risk mapping layer 存在；
- pipeline evaluation artifact 存在。

这些 claim 不等价于真实导航性能提升。

## 当前证据不支持什么

当前证据不支持：

- real navigation safety improvement；
- collision reduction；
- near-miss reduction；
- success-rate improvement；
- compensation readiness；
- safe command adapter readiness；
- publication readiness。

## Evaluation 类型区分

- structural/software validation：脚本、schema、JSON artifact 和测试是否可运行。
- dataset evidence：Measurement v0 是否被整理为研究数据集。
- response-model sanity checks：exact-source reconstruction 只能说明结构一致性。
- risk-map readiness evaluation：warning distribution 和 risk category 是否可计算。
- real navigation outcome evaluation：尚未进行，不能由当前 artifact 推断。

## 为什么不是导航性能评估

M16 risk map 没有真实导航任务 outcome，没有 collision / near-miss / success-rate annotation，也没有 A/B navigation trial。因此 M17 只能报告 pipeline readiness 和下一步实验需求。

## 如何准备 M18 / P1

M18 可以使用 M17 artifact table、limitations 和 claim registry 组织 method skeleton、figures 和 claim audit。P1 可以在不混淆项目证据和文献证据的前提下启动 literature search 和 literature matrix v1。

## Future Experiments

后续实验应包含 repeated trials、multi-surface tests、vx + wz command grid、yaw/lateral drift、response delay、stop-distance logging，以及在固定 protocol 下的 navigation task outcomes。

## Prohibited Claims

在完成真实导航实验和文献审查前，不得声称 publication readiness、导航安全提升、collision / near-miss / success-rate 改善、速度补偿可用或 safe command adapter 可用。
