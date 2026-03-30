# Open Questions

> 部分问题在 [REVIEW.md](../REVIEW.md) 中有更详细的分析和建议。

## 产品问题

1. News Report 的核心用户是谁
   既可以是用户 Agent 开发者，也可以直接面向信息消费者

2. Phase 2 的首要价值是什么
   是“更好的 source access”，还是“更好的 briefing generation”？

3. 是否需要维护公共资源目录之外的私有接入层
   很多真正高价值的信息源可能依赖用户自己的账号和订阅。

## 技术问题

1. Source adapter 的最小统一字段是什么
   是只统一 metadata，还是统一到 normalized content block？

2. 第一个运行时应该选 CLI 还是 MCP
   CLI 适合快，MCP 适合集成，但会更早固化协议边界。

3. 什么时候引入缓存
   如果总结成本高，缓存应很早引入；如果先做 schema 验证，缓存可以延后。

## 风险问题

1. 个性化是不是会把系统做偏
   如果太早强调个性化，很容易走向隐式画像和信息茧房。

2. 资源目录会不会沦为普通 awesome list
   如果没有结构化字段、比较标准和后续执行链路，这个风险很高。

3. 这个项目和 RSSHub / Readwise / Inoreader 的差异是否足够大
   必须证明自己不是“另一个聚合器”，而是 Agent-first 的 processing layer。
