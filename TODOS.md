# TODOS

> 由 /plan-ceo-review 生成于 2026-03-31，分支 feat-briefing-adapter-foundation

## P1

### MCP Server 封装
把 `generate_briefing()` 封装为 MCP Tool，让 Agent 通过 MCP 协议直接调用。
这是项目"面向 Agent 的 RSSHub"定位的核心交付形态。
- 工作量：M（人工约 3 天）→ AI 辅助约 30 分钟
- 依赖：至少 1 个真实 adapter 跑通
- 上下文：当前 CLI 是验证工具，MCP 是最终交付。架构已支持，只需在 CLI 外面包一层。

### LLM 摘要集成
用 AI 模型生成每条推荐的 `why_it_matters`，替代当前 `format_why()` 的字符串拼接。
- 工作量：S（人工约 1 天）→ AI 辅助约 15 分钟
- 依赖：真实 adapter 跑通
- 上下文：当前 `format_why()` 在 `briefing.py:141` 是硬编码规则拼接，产出文本不够自然。需要选择 LLM provider（本地模型或 API）。

### 第二个真实 Adapter（Hacker News API）
验证 `SourceAdapter` Protocol 的通用性。HN API 免费、无需认证、返回结构化 JSON。
- 工作量：S（人工约半天）→ AI 辅助约 15 分钟
- 依赖：Adapter Protocol 已定义
- 上下文：如果 Protocol 能同时支持 RSS（RSSHub）和 JSON API（HN），说明抽象层设计正确。

## P2

### 内容去重
多源聚合后同一内容可能从不同源出现。基于 URL 归一化或 title 相似度去重。
- 工作量：S
- 依赖：多个真实 adapter 工作后才有意义
- 上下文：当前 `rerank_with_diversity()` 的 diversity penalty 部分缓解了这个问题，但不是真正的去重。

### Async Adapter 支持
adapter 数量超过 5 个后 `ThreadPoolExecutor` 并发可能不够高效，考虑迁移到 `asyncio` + `httpx.AsyncClient`。
- 工作量：M
- 依赖：adapter 数量增长到 5+ 后评估
- 上下文：当前设计用同步 `httpx.Client` + `ThreadPoolExecutor`，简单可靠。async 迁移需要改 adapter 接口签名。

## P1.5（2026-04-12 实践发现）

> 基于通过 CDP 抓取 X + 即刻 timeline 的实际操作得出

### CDP Browser Adapter（社交媒体时间线）
通过 Chrome DevTools Protocol 连接用户已登录的浏览器，抓取需要认证的社交媒体内容（X、即刻、小红书等）。
- 原型已创建：`news_report/adapters/cdp_browser.py`
- 工作量：M（需要处理不同站点的 DOM 结构差异）
- 关键挑战：
  - 即刻 web 版虚拟滚动/lazy loading 导致内容获取有限
  - 不同站点的 DOM 结构差异大，需要站点专属提取逻辑
  - 需要考虑 a11y tree snapshot vs JS DOM 提取的选择
- 上下文：bb-browser 可以作为运行时依赖，但提取逻辑和标准化应在 news-report 内部

### SourceAdapter Protocol 扩展：engagement 字段
社交媒体内容的评分需要考虑互动数据（点赞、转发、评论、浏览），当前 `compute_score` 只有 source_quality/topic_match 等维度，缺少 engagement 信号。
- 工作量：S
- 建议：在 score_breakdown 中增加 `engagement` 维度，作为社交媒体源的加权信号

### 内容分类/过滤增强
实际时间线中混杂大量日常生活帖（烤鱼、喝东西），需要自动区分"要闻"和"闲聊"。
- 工作量：M
- 方向：简单规则 + LLM 分类结合，或者让用户配置关注的内容类型

### 广告识别与过滤
X timeline 中有广告帖（标记"广告"/"Promoted"），需要自动过滤。
- 工作量：S
- 上下文：已在 cdp_browser.py 原型中实现基础的文本匹配过滤
