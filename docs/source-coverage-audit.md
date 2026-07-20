# 9 个来源工程覆盖审计

> 本审计按新版 20 章口径检查 `source/` 下 9 个教程工程。覆盖指可迁移的原理、机制、代表实现和成熟案例已经进入教材；产品安装、配置命令、重复翻译和低成熟度项目清单不要求进入正文。

## 覆盖结论

| 来源工程 | 结论 | 新版主要落点 |
| --- | --- | --- |
| `source/learn-claude-code` | 已覆盖 | 1、3、4、6、7、10-12、14-17、19、20 |
| `source/Alice_methodology` | 已覆盖 | 1、3-7、10-12、15、16、18-20 |
| `source/hermes-book` | 已覆盖 | 1、3-7、11、13-17、19、20 |
| `source/easy-langent` | 已覆盖 | 1-4、6、8、9、16、20 |
| `source/claw0` | 已覆盖 | 1、3、6、7、13-15、19、20 |
| `source/harness-engineering-from-cc-to-ai-coding` | 已覆盖 | 1、3-7、10、11、15-20 |
| `source/claude-code-analysis` | 已覆盖 | 1、3-7、10-12、16、17、19、20 |
| `source/hello-claw` | 已覆盖可迁移内容 | 1、10、11、13、14、16、19、20 |
| `source/hello-agents` | 已覆盖可迁移内容 | 1-20 |

20 章正文已经生成，第 1、6 章已经过用户 Review，其余章节等待逐章 Review。审计通过不代表每章已经定稿。

## 按来源展开

### learn-claude-code

| 来源内容 | 新版落点 |
| --- | --- |
| s01 Agent Loop、s02 Tool Use | 第 3 章 |
| s03 Permission、s04 Hooks | 第 10 章 |
| s05 TodoWrite、s06 Subagent、s12 Task、s15-s18 Team/Autonomous/Worktree | 第 16 章；治理部分进入第 15、17、19 章 |
| s07 Skill Loading、s19 MCP | 第 11、12 章 |
| s08 Context Compact | 第 6 章 |
| s09 Memory | 第 7 章 |
| s10 System Prompt | 第 4 章 |
| s11 Error Recovery | 第 5、14、19 章 |
| s13 Background Tasks、s14 Cron | 第 14 章 |
| s20 Comprehensive Agent | 第 20 章 |

### Alice_methodology

| 来源内容 | 新版落点 |
| --- | --- |
| 哲学、架构、Agent Loop、工具系统 | 第 1、3、20 章 |
| 上下文、记忆与记忆博客 | 第 6、7 章 |
| 多 Agent、共建与人格/交互方法 | 第 16、20 章 |
| 权限、安全 | 第 10 章 |
| MCP、Skills | 第 11、12 章 |
| 模型路由、Prompt | 第 4、5 章 |
| 自我进化 | 第 18 章 |
| 可观测、工程范式、快速发布 | 第 17、19、20 章 |

### hermes-book

| 来源内容 | 新版落点 |
| --- | --- |
| 设计赌注、仓库地图、请求旅程、AIAgent 核心 | 第 1、3、20 章 |
| Prompt、配置、模型抽象 | 第 4、5 章 |
| Tool、Tool Profiles | 第 3、10 章 |
| Skill、Delegation | 第 11、16 章 |
| SessionDB、Memory Provider、Context Compression | 第 6、7 章 |
| CLI/TUI、Gateway | 第 13 章 |
| Cron、Concurrency、Lifecycle、Runtime Defense | 第 14、15、19 章 |
| Testing | 第 17、19 章 |

### easy-langent

| 来源内容 | 新版落点 |
| --- | --- |
| 基础概念、模型、Prompt、输出解析 | 第 1-4 章 |
| Memory、Tool、会话 | 第 3、6、7 章 |
| Runnable、Router、RAG | 第 8、9 章 |
| LangGraph State、Node、Edge、Checkpoint、Human-in-the-loop | 第 6、9 章 |
| LangGraph 多智能体 | 第 9、16 章 |
| 课程项目与游戏 Agent | 第 9、20 章，以代表模式覆盖，不逐项写成功能清单 |

### claw0

| 来源内容 | 新版落点 |
| --- | --- |
| s01 Agent Loop、s02 Tool Use | 第 3 章 |
| s03 Sessions、s06 Intelligence | 第 6、7 章 |
| s04 Channels、s05 Gateway Routing | 第 13 章 |
| s07 Heartbeat/Cron、s08 Delivery、s09 Resilience、s10 Concurrency | 第 14、15、19 章 |
| workspace 示例 | 第 7、11、20 章 |

### harness-engineering-from-cc-to-ai-coding

| 来源内容 | 新版落点 |
| --- | --- |
| Part 1：架构、工具、Agent Loop | 第 1、3 章 |
| Part 2：系统提示、行为引导、工具提示 | 第 4 章 |
| Part 3：压缩、Token 预算 | 第 6 章 |
| Part 4：记忆、规则覆盖、缓存 | 第 4、6、7 章 |
| Part 5：权限、分类器、Hooks、项目规则 | 第 10 章 |
| Part 6：Agent 编排、Effort、Skill、Memory | 第 5、7、11、16 章 |
| Part 7：工程、测试、观测、发布 | 第 17-20 章 |
| 附录：环境变量、Feature Flag、Trace | 第 19 章 |

### claude-code-analysis

| 来源内容 | 新版落点 |
| --- | --- |
| 架构总览、组件分析 | 第 1、3、20 章 |
| Agent Memory、Context、Session Resume | 第 6、7 章 |
| Tool Call、Prompt、模型调用 | 第 3-5 章 |
| 安全、隐私、Sandbox | 第 10 章 |
| Skills、MCP | 第 11、12 章 |
| Multi-Agent | 第 16 章 |
| 测试证据、竞品和源码索引 | 第 17、19、20 章 |

### hello-claw

| 来源内容 | 新版落点 |
| --- | --- |
| 构建篇中的底层架构、网关、Session、并发 | 第 1、13、14、19 章 |
| 安全与沙箱 | 第 10 章 |
| Skill 开发、发布与 ClawHub | 第 11 章 |
| 多智能体场景 | 第 16、20 章 |
| 场景点评与评测模板 | 第 17、20 章 |
| 产品安装、日常配置、硬件部署和命令手册 | 明确排除，不进入主教材 |

### hello-agents

| 来源内容 | 新版落点 |
| --- | --- |
| Ch01-Ch02：定义、类型与历史 | 第 1 章 |
| Ch03：LLM 基础 | 第 2、4、5 章 |
| Ch04：ReAct、Plan-and-Solve、Reflection | 第 3 章 |
| Ch05：低代码平台 | 第 9 章只提炼编排边界；点击操作明确排除 |
| Ch06-Ch07：框架开发 | 第 3、9、16、20 章 |
| Ch08：记忆与检索 | 第 7、8 章 |
| Ch09、Extra02：上下文工程 | 第 4、6、19 章 |
| Ch10：MCP、A2A、ANP | 第 12 章 |
| Ch11、Extra12：Agentic RL 与后训练 | 第 18 章 |
| Ch12：性能评估、BFCL、GAIA、数据生成 | 第 17 章 |
| Ch13-Ch15：旅行、Deep Research、赛博小镇 | 第 8、9、16、20 章的代表案例 |
| Ch16、Co-creation projects | 第 20 章以成熟模式和项目方法覆盖，不逐项收录 |
| Extra05、Extra08：Agent Skills | 第 11 章 |
| Extra09：工程踩坑 | 第 3-6、10、17、19 章 |
| Extra10：Agent 自进化 | 第 18 章 |
| Extra06、Extra11：GUI/Web Agent | 第 9、20 章的行动环境案例 |
| 安装指南、环境配置、FAQ、低代码点击步骤 | 明确排除，不进入主教材 |

## 新版章节覆盖矩阵

| 章节 | 本地来源覆盖重点 |
| --- | --- |
| 1-5 | 基础心智、LLM、Loop/工具、Prompt、模型运行时 |
| 6-9 | 会话/状态/上下文、长期记忆、RAG、框架编排 |
| 10-12 | 安全治理、Skills/Plugin、MCP/A2A/ANP |
| 13-16 | Gateway、后台韧性、Loop Engineering、多 Agent |
| 17-20 | 评测、自进化/后训练、生产工程、代表案例与综合项目 |

第 15 章还使用用户提供的三篇 X 文章及 Anthropic 等公开资料。外部资料负责补足 Loop Engineering 的独立理论，不改变 9 个本地来源的覆盖口径。

## 未进入正文的内容

以下内容经过筛选后不进入主教材，不属于遗漏：

- 同一章节的英文、日文或其他重复翻译。
- OpenClaw、Dify、n8n 等产品的安装、配置、点击和命令手册。
- 硬件部署、环境排错和课程 FAQ。
- “龙虾大学”等产品学习路径与宣传性内容。
- 大量共创项目的功能清单和低成熟度实现；只保留能说明架构取舍的代表案例。
- 未公开实现细节、未经证实的产品推测和容易过时的营销结论。

## 检查结论

9 个来源工程中的可迁移知识已经分配到新版 20 章，重复主题已经合并，Skills/互操作、Gateway/后台韧性、评测/生产工程等旧版混合主题已经拆开。后续逐章 Review 时仍需核对概念深度、案例准确性和章间重复；若发现来源遗漏，应同时更新本审计与对应章节。
