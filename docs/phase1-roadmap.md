# Phase 1 Roadmap

## 目标

把项目从“概念说明”推进到“可执行的方向判断工具”。

Phase 1 的交付不应该是一个复杂系统，而应该是下面四项：

- 一个持续扩展的资源 registry
- 一套稳定的数据字段和评估维度
- 一个足够清晰的 MVP 规格
- 一组明确的开放问题，帮助后续快速判断该不该做

## 当前优先级

### P0

- 扩展 `data/sources.json` 到至少 20 个高质量条目
- 给每个条目补全 `interface_types`、`content_types`、`agent_friendly`
- 明确第一版 briefing 的输入输出 schema

### P1

- 定义 source adapter 的统一契约
- 选 2 到 3 个数据源做真实接入样例
- 验证缓存层是否必须在 MVP 阶段出现

### P2

- 评估是否用 MCP Server 作为首个运行时形态
- 评估公共实例和按需部署的成本模型

## 评估维度

每个资源建议按下面维度打标签：

- `interface_types`: 是否可编程
- `content_types`: 覆盖什么内容
- `agent_friendly`: Agent 接入难度
- `open_source`: 是否便于生态协作
- `pricing`: 是否适合复用和验证
- `stage`: 是否还在持续活跃

## Phase 1 完成标准

满足下面条件时，可以认为 Phase 1 基本完成：

1. 已经收集到一批可比较的资源，而不是零散链接
2. 已经形成一个可讲清楚的 MVP 输入输出模型
3. 已经知道第一个 demo 应该接哪些 source
4. 已经知道哪些假设最危险，需要在 Phase 2 验证
