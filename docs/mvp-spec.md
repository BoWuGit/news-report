# MVP Spec

## 目标

第一个 MVP 不做“万能新闻系统”，只做一件事：

输入一组主题、信息源和用户偏好，返回一个结构化 briefing。

## 建议形态

首个 MVP 优先考虑这两种形态之一：

- 本地 CLI：实现成本低，适合快速验证接口和输出结构
- MCP Server：更贴近 Agent 集成形态，但会增加协议和运行时成本

建议顺序是先 CLI，后 MCP。

## 核心接口

```json
{
  "topics": ["AI", "open source"],
  "sources": ["rsshub", "podwise", "readwise"],
  "language": "zh-CN",
  "max_items": 10,
  "summary_style": "concise",
  "user_profile": {
    "explicit_preferences": ["agent tools", "developer workflows"],
    "blocked_topics": ["crypto trading"],
    "time_decay_days": 30,
    "diversity_floor": 0.2
  }
}
```

## 输出草案

```json
{
  "generated_at": "2026-03-28T10:00:00Z",
  "query": {
    "topics": ["AI", "open source"],
    "sources": ["rsshub", "podwise", "readwise"]
  },
  "items": [
    {
      "title": "Example item",
      "source": "podwise",
      "content_type": "podcast",
      "url": "https://example.com/item",
      "why_it_matters": "Relevance explanation for the user agent.",
      "summary": "Short actionable summary.",
      "score": 0.86,
      "tags": ["agent tools", "audio"]
    }
  ],
  "coverage": {
    "fetched_sources": 3,
    "returned_items": 1
  }
}
```

## 非目标

MVP 暂时不解决这些问题：

- 完整用户画像存储
- 社交网络上的实时抓取
- 重型推荐系统
- 公共多租户部署

## 关键实现原则

- 用户偏好优先显式输入，不默认长期记忆
- 输出必须解释“为什么推荐给这个用户”
- 去重、摘要、翻译是通用能力，排序策略可以后置
- 对同一原始内容，尽量只做一次重处理，后续复用缓存
