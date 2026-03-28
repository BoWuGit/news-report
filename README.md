# News Report For User Agent

> 面向用户 Agent 的新闻简报基础设施

News Report 想做的是“面向 Agent 的 RSSHub”，但不只停留在 RSS 聚合。
它更像一层信息处理中间件：帮助用户 Agent 发现信息源、拉取内容、做结构化转换，并按用户偏好生成可消费的 briefing。

## 核心定位

```text
用户 Agent / AI Reader
        |
        v
News Report
- source registry
- normalization
- enrichment
- briefing generation
        |
        v
RSS / API / Newsletter / Podcast / Social / Read-later
```

边界很重要：

- 不直接做面向终端用户的阅读器
- 不保存或出售用户画像
- 不限定垂类，重点做 Agent 可编程的信息处理层
- 不重新生产原始内容，重点在聚合、转换、排序、总结

## 当前阶段

项目现在处于 `Phase 1`：把想法沉淀成一个可维护的资源库和可执行的产品定义。

这版仓库已经补上了三个基础层：

- `data/`：资源清单的结构化数据
- `schemas/`：Phase 1 和后续 MVP 可复用的数据模型
- `docs/`：路线图、MVP 规格、开放问题、自动生成目录

## 仓库结构

```text
.
├── README.md
├── vision.md
├── REVIEW.md
├── CONTRIBUTING.md
├── data/
│   └── sources.json
├── docs/
│   ├── catalog.md
│   ├── mvp-spec.md
│   ├── open-questions.md
│   └── phase1-roadmap.md
├── examples/
│   └── briefing-request.json
├── news_report/
│   ├── adapters.py
│   ├── briefing.py
│   └── catalog.py
├── schemas/
│   ├── briefing-request.schema.json
│   ├── briefing-response.schema.json
│   └── source.schema.json
├── scripts/
│   ├── build_catalog.py
│   └── generate_briefing.py
└── tests/
    └── test_briefing.py
```

## Phase 1 目标

`Phase 1` 不是直接做一个大而全的产品，而是回答四个更硬的问题：

1. 哪些信息源和工具真正对 Agent 友好
2. 哪些输入输出字段值得统一抽象
3. 哪些场景值得做成第一个 `briefing` 接口
4. 哪些链路能先靠低成本实现，避免过早投入重型基础设施

## 已收录方向

当前先收录三类对象：

- 信息源 SaaS 和聚合服务
- Agent 友好的 CLI / MCP / Skills
- 可接入 briefing pipeline 的转换工具

资源目录见 [docs/catalog.md](docs/catalog.md)，源数据见 [data/sources.json](data/sources.json)。

## 快速使用

生成资源目录：

```bash
python3 scripts/build_catalog.py
```

这个脚本会：

- 校验 `data/sources.json` 中的必填字段和基本格式
- 按资源类型输出 `docs/catalog.md`

生成一个本地 briefing 原型输出：

```bash
python3 scripts/generate_briefing.py examples/briefing-request.json
```

这个原型会：

- 校验请求字段
- 从 `data/sources.json` 选择 source
- 生成标准化 briefing JSON
- 给出每条结果的推荐理由和分数拆解

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 后续开发建议

建议优先往这三个方向推进：

1. 扩展 `sources.json`，把资源收集做成真正可比较的 registry
2. 基于 `briefing-request.schema.json` 先做一个本地 CLI 或 MCP 原型
3. 给每个 source 补充统一的 adapter 契约，逐步形成 Agent-friendly ingestion layer

## 参考引用

- 前序文章：[阅读产品在AI时代的想象力](https://mp.weixin.qq.com/s/sSP9j-qLZQBJiyLSrCYzWQ)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [RSSHub](https://rsshub.app/)
- [mcp.so](https://mcp.so/)

## License

MIT
