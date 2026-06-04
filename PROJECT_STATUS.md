# Project Status

## 当前阶段

M3: Dummy Data Pipeline completed.

## 当前仓库

`k1_measurement_skill`

## 在大项目中的位置

本仓库是完整 **K1 Velocity Measurement, Compensation and Navigation Safety Pipeline** 的测量阶段前置模块，只负责：

```text
v_x_cmd -> v_x_actual measurement
```

本仓库不实现速度补偿、自主导航、实时闭环控制或真实机器人运动命令。

## Completed

- [x] Project folder created
- [x] Git initialized
- [x] Chinese-first README created
- [x] English reference README created
- [x] Project roadmap created
- [x] AGENTS.md created
- [x] Downstream interface folder created
- [x] Safety protocol placeholder created
- [x] measurement profile JSON schema defined
- [x] dummy profile example created
- [x] raw log schema documented
- [x] downstream interface documented
- [x] schema validation script added
- [x] schema tests added
- [x] actual velocity metric implemented
- [x] speed gain metric implemented
- [x] absolute error metric implemented
- [x] relative error metric implemented
- [x] lateral drift rate metric implemented
- [x] yaw drift rate metric implemented
- [x] tracking RMSE implemented
- [x] trial summary aggregation implemented
- [x] dummy raw log generator implemented
- [x] dummy raw log includes required fields
- [x] profile builder implemented
- [x] dummy raw log can be processed into profile JSON
- [x] generated dummy profile passes schema validation
- [x] profile builder tests passed
- [x] README usage updated
- [x] tests passed
- [x] main branch pushed to GitHub

## Next Milestone

M4: ROS2 Topic Discovery and Logger Skeleton.
