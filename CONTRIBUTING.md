# Contributing

这个仓库当前更像一个“产品定义 + 资源 registry + MVP 设计”的工作区，贡献时请优先保持结构化，而不是只追加零散观点。

## 资源录入原则

新增资源时，优先补到 `data/sources.json`，而不是只改 `README.md`。

每条资源至少回答这些问题：

- 它解决的是什么问题
- 它提供什么接口：`rss`、`api`、`cli`、`mcp`、`web`
- 它处理的内容类型是什么
- 它是否对 Agent 友好
- 它的限制是什么

## 文档改动原则

- `vision.md` 只保留长期愿景
- `docs/phase1-roadmap.md` 记录近期执行计划
- `docs/mvp-spec.md` 记录接口和系统边界
- `docs/open-questions.md` 记录还没定的关键问题

## 推荐流程

1. 先改 `data/` 或 `schemas/`
2. 运行 `python3 scripts/build_catalog.py`
3. 再更新相关文档

## 暂不建议的改动

- 过早引入复杂依赖
- 在没有统一 schema 前直接接很多 source adapter
- 直接把“个性化排序”绑定到隐式用户画像


## 语言约定

- 代码、schema、commit message 用英文
- 面向社区的文档（vision.md、README.md、REVIEW.md）可以中英双语
