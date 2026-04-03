# News Report For User Agent

> 面向用户 Agent 的新闻简报 —— 让 AI 助手帮你高效获取个性化信息

随着个人 AI 助手（如 [OpenClaw](https://github.com/openclaw/openclaw)）的成熟，用户 Agent 越来越需要结构化的信息获取能力。**News Report** 致力于成为面向 Agent 的 [RSSHub](https://rsshub.app/)——为 AI 助手提供发现优质信息源、处理转换内容、生成个性化简报的工具和服务。

## 核心定位

```text
用户 Agent
        |
        v
News Report（信息处理中间件）
- source registry
- normalization
- enrichment
- briefing generation
        |
        v
RSS / API / Newsletter / Podcast / Social / Read-later
```

- **不收集用户信息**：用户可将偏好输入 News Report，通过计算返回个性化结果
- **不限定内容分类**：专注于提供内容处理的工具和技术
- **不直接生产内容**：聚合、转换、总结已有内容

## 项目阶段

### Phase 1：资源收集与社区（当前）

收集已有和新出现的服务、工具，整理分类来分享，了解用户的喜好和需求。

这版仓库已经补上了三个基础层：

- `data/`：资源清单的结构化数据
- `schemas/`：Phase 1 和后续 MVP 可复用的数据模型
- `docs/`：路线图、MVP 规格、开放问题、自动生成目录

### Phase 2：工具开发与整合

设计和开发面向 Agent 的信息处理工具：
- 信息源发现与聚合
- 内容处理与转换（总结、翻译、格式化）
- 简报生成

### Phase 3：服务化部署

- 开源部署，提供优质内容的公开访问
- 按需个性化部署（类似 Hugging Face 模型服务）
- 支持用户组团部署，分摊成本

## 生态资源

### SaaS 信息源服务

| 服务 | 说明 |
|------|------|
| [Inoreader Intelligence Reports](https://www.inoreader.com/blog/2026/03/automated-intelligence-reports-for-insights-delivered-to-you.html) | RSS 阅读器，支持自动化智能报告 |
| [Readwise CLI](https://x.com/readwise/status/2034302848805241282) | 阅读高亮和文章的 CLI 工具，支持 Agent 接入 |

### [Agent Skills](https://agentskills.io) / CLI 工具

| 工具 | 说明 |
|------|------|
| [Podwise CLI](https://github.com/hardhackerlabs/podwise-cli) | 播客转录总结，支持 MCP Server 和 [Agent Skills](https://agentskills.io) |
| [TransCrab](https://github.com/onevcat/transcrab) | OpenClaw-first 翻译管线，将链接转为精美的翻译阅读页 |
| [baoyu-youtube-transcript](https://github.com/jimliu/baoyu-skills) | YouTube 视频字幕下载，支持多语言、章节和说话人识别 |
| [RSSHub](https://github.com/DIYgod/RSSHub) | 万物皆可 RSS，42k+ Stars |

完整资源目录见 [docs/catalog.md](docs/catalog.md)，源数据见 [data/sources.json](data/sources.json)。

## 快速使用

生成资源目录：

```bash
uv run scripts/build_catalog.py
```

生成一个本地 briefing 原型输出：

```bash
uv run scripts/generate_briefing.py examples/briefing-request.json
```

运行测试：

```bash
uv run pytest
```

## 前置依赖和假定

- AI 生态的用户 Memory 会越来越成熟
  - 不管是 Local First 的 [OpenClaw](https://github.com/openclaw/openclaw)，还是各大 Super App
  - 尽管仍有挑战（如 [Karpathy 指出的记忆干扰问题](https://x.com/karpathy/status/2036836816654147718)）
- Agent 需要能缓解用户的信息过载——信息处理总结是 AI 擅长的

## 参考引用

- 前序文章：[阅读产品在AI时代的想象力](https://mp.weixin.qq.com/s/sSP9j-qLZQBJiyLSrCYzWQ)
- [Karpathy: LLM Knowledge Bases](https://x.com/karpathy/status/2039805659525644595) — 用 LLM 构建个人知识库的完整工作流，与本项目方向高度吻合
- 感谢 [One2X](https://one2x.ai) 冠哥之前的产品思考对项目的启发

## License

MIT
