# 项目 Review 与建设性意见

*基于 vision.md 的深度调研与分析*

---

## 一、核心立意评价

**定位很好。** "面向 Agent 的 RSSHub" 这个类比准确地捕捉到了一个真实的生态位空缺——现有的新闻聚合工具（Inoreader、Readwise）是为人类设计的，而 AI Agent 需要的是**结构化、可编程、上下文感知**的信息获取接口。目前市场上确实没有一个项目在系统性地做这件事。

---

## 二、需要注意的问题

### 1. Karpathy 的反馈值得深思

Karpathy 指出的问题是："单次提问可以在两个月后仍被 LLM 当作深度兴趣反复提及"——这正是 News Report 需要避免的陷阱。如果 Agent 基于过时或过度权重的用户偏好来筛选新闻，结果可能比信息过载更糟。

**建议：** 在设计个性化算法时，需要考虑：
- 兴趣的**时间衰减**（近期兴趣权重高于历史兴趣）
- 偏好的**显式更新**（让用户主动调整，而非纯粹靠推断）
- **多样性保证**（避免信息茧房）

---

## 三、竞品/相关项目分析

### 已有做法的模式总结

| 项目 | 模式 | 优势 | 局限 |
|------|------|------|------|
| Inoreader Intelligence Reports | SaaS + AI 分析 | 成熟产品，可定时 | 闭源，付费，非 Agent 友好 |
| Podwise CLI | CLI + MCP + Skills | Agent 友好，标准协议 | 仅限播客领域 |
| Readwise CLI | CLI + npm | 结构化数据输出 | 仅限已保存内容 |

**关键观察：** 目前所有项目要么是**面向人类的最终产品**，要么是**单一领域的 Agent 工具**（播客/阅读）。News Report 的机会在于做**跨领域的信息处理中间层**。

---

## 四、建设性建议

### 1. Phase 1 的具体行动

Phase 1 "收集已有和新出现的服务" 目标正确但形式模糊。建议：
- 建一个 `awesome-list` 风格的资源列表（已在 README 中初步搭建）
- 为每个资源标注：**Agent 友好度**（是否有 CLI/MCP/API）、**内容类型**、**是否开源**
- 在 GitHub Discussions 或 Issues 里收集社区反馈

### 2. 技术路线建议

```
Phase 1: Awesome List + 社区
    ↓
Phase 2: MCP Server（核心）
    - 封装多个信息源的统一接口
    - 内容处理 pipeline（总结、翻译、格式化）
    - 用户偏好作为参数输入
    ↓
Phase 3: 部署 + 存储
    - 历史内容缓存（减少重复 API 调用）
    - 公共实例（类似 RSSHub 的公共实例）
```

### 3. 一个具体的 MVP 建议

可以先做一个 MCP Server，聚合 RSSHub + Readwise CLI + Podwise CLI 的输出，提供统一的 `get_briefing(topics, preferences, format)` 接口：

```
用户 Agent 调用:
  news_report.get_briefing(
    topics=["AI", "开源"],
    sources=["hackernews", "podwise"],
    format="summary",
    language="zh",
    max_items=10
  )
```

这个 MVP 小而具体，能快速验证核心价值。

### 4. 商业模式的思考

Vision 提到"按需部署"和"组团部署"，但可能低估了运营成本。AI 总结的 token 消耗不低。建议：

- **缓存复用**：相同信息源的同一篇文章，总结只做一次，结果缓存给所有用户
- **分层服务**：公共热门内容免费，个性化/小众内容按需付费
- **社区贡献**：像 RSSHub 一样，让社区贡献信息源路由

### 5. 前序文章的观点扩展

前序文章《阅读产品在AI时代的想象力》提出的核心观点——"找到当前最适合用户阅读的内容"——非常准确。News Report 可以作为实现这个愿景的**基础设施层**：

- 文章里提到的 "AI Reader" 是面向终端用户的产品
- News Report 是面向 AI Reader 和其他 Agent 的**中间件和工具集**
- 两者是互补关系，不是竞争关系

这个定位可以在 vision.md 中更明确地阐述。

