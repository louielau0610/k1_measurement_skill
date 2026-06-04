# Downstream Interface

本文档以中文优先描述测量模块与下游模块之间的接口。

## 核心接口文件

`processed_environment_profile.json` 是本仓库输出给下游模块的核心接口文件。

它会被以下模块消费：

- velocity compensation model
- safe command adapter
- navigation safety layer
- simulation validation pipeline

## 下游检查要求

下游模块使用 profile 前必须检查：

- confidence
- speed range
- environment match
- sample size
- extrapolation risk

下游模块不能默认认为 profile 是高置信度，也不能在环境不匹配、样本量不足或速度超出有效范围时直接使用该 profile。

## 边界

本仓库只提供测量 profile，不提供补偿命令、不提供导航控制、不提供实时闭环控制。
