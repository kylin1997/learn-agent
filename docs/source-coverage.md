# 来源覆盖说明

本文件记录 `source/` 下 12 个教程工程如何合并进 20 章主教材，并检查可迁移内容是否存在遗漏。它同时提供两种查询方向：

- 从教材章节查主要来源和合并范围。
- 从来源工程反查内容进入了哪些章节。

本文件不安排学习顺序。学习方法和阶段产物见[《Agent 学习指南》](agent-learning-guide.md)，章节入口和 Review 状态见[《融合版 Agent 教材目录》](merged-agent-course/course-catalog.md)。

## 覆盖口径

“已覆盖”表示来源中的可迁移原理、运行机制、代表实现和成熟案例已经进入对应章节。它不要求复制原文，也不要求收录每个产品操作和项目功能。

纳入教材：

- Agent 的通用概念、架构和工程方法。
- 能解释运行机制的数据结构、控制流和代码原型。
- 能帮助比较设计取舍的成熟案例。
- 与主题密切相关的论文、标准和官方工程资料。

不纳入教材：

- 重复翻译和内容相同的多语言版本。
- OpenClaw、Dify、n8n 等产品的安装、配置、点击和命令手册。
- 硬件部署、环境排错、课程 FAQ 和宣传性学习路径。
- “龙虾大学”等场景集合的完整功能清单。
- 低成熟度共创项目、未经证实的产品推测和容易过时的营销结论。

## 12 个来源的定位

| 来源工程 | 主要价值 | 覆盖结论 | 上游项目 |
| --- | --- | --- | --- |
| `source/easy-langent` | LangChain、LangGraph、RAG、课程项目和应用编排 | 可迁移内容已覆盖 | [datawhalechina/easy-langent](https://github.com/datawhalechina/easy-langent) |
| `source/hermes-book` | Hermes 源码、长期个人 Agent、Gateway、记忆、生命周期和测试 | 已覆盖 | [ZhangHanDong/hermes-book](https://github.com/ZhangHanDong/hermes-book) |
| `source/Alice_methodology` | 桌面 Agent 方法论、权限、记忆、多 Agent、自进化和交互设计 | 已覆盖 | [itshen/Alice_methodology](https://github.com/itshen/Alice_methodology) |
| `source/hello-claw` | OpenClaw 架构、安全、Skill、运维和多 Agent 场景 | 可迁移内容已覆盖，操作手册已排除 | [datawhalechina/hello-claw](https://github.com/datawhalechina/hello-claw) |
| `source/claw0` | 从零构建 Agent Gateway，包含渠道、路由、主动任务和可靠投递 | 已覆盖 | [shareAI-lab/claw0](https://github.com/shareAI-lab/claw0) |
| `source/harness-engineering-from-cc-to-ai-coding` | Claude Code 工程模式、上下文、权限、缓存、多 Agent 和生产实践 | 已覆盖 | [ZhangHanDong/harness-engineering-from-cc-to-ai-coding](https://github.com/ZhangHanDong/harness-engineering-from-cc-to-ai-coding) |
| `source/claude-code-analysis` | Claude Code 静态分析、安全、组件、实现证据和竞品对照 | 已覆盖 | [liuup/claude-code-analysis](https://github.com/liuup/claude-code-analysis) |
| `source/learn-claude-code` | Claude Code 式 Agent Harness 的渐进实现 | 已覆盖 | [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) |
| `source/hello-agents` | Agent 基础、范式、框架、记忆/RAG、上下文、协议、后训练、评测和综合项目 | 可迁移内容已覆盖 | [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) |
| `source/ai-agents-in-action-2nd-edition-cn` | 三层 Loop、认知控制结构、TDAD、混合记忆、多 Agent 协调、MCP 与综合案例 | 原书第 2-7、9-11 章已去重融合；第 1、8 章及操作性附录按用户决定排除 | [yixiangshijie/ai-agents-in-action-2nd-edition-cn](https://github.com/yixiangshijie/ai-agents-in-action-2nd-edition-cn) |
| `source/ai-agent-book` | 上下文工程、记忆与知识、工具、评估、后训练、自我进化、实时交互和多 Agent | 10 章可迁移机制已去重融合；教学实验按原理取证，不整套移植 | [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) |
| `source/30-Agents-Every-AI-Engineer-Must-Build` | 30 类 Agent 架构的横向模式库、领域约束、验证、公平性、解释和具身行动案例 | 17 个主题章节按机制去重融合；公平与解释治理、多时间尺度控制和统一约束包络补入正文，重复运行副本和虚构业务数字排除 | [PacktPublishing/30-Agents-Every-AI-Engineer-Must-Build](https://github.com/PacktPublishing/30-Agents-Every-AI-Engineer-Must-Build) |


## 20 章来源映射

| 章 | 主题 | 主要本地来源  |
| --- | --- | --- |
| 1 | Agent、历史与 Harness | 既有来源的基础定义、架构和产品边界；`ai-agent-book` Ch01 补充“模型 + 上下文 + 工具”与 Harness 竞争力；`30-Agents` Ch01/05 作为认知循环和基础架构对照 |
| 2 | LLM 基础与模型行为 | `hello-agents` Ch03、`easy-langent` 模型基础、`ai-agents-in-action` Ch02 及各工程的模型使用经验 |
| 3 | Agent Loop、范式与工具 | 既有 Loop 来源、`ai-agents-in-action` Ch05/10、`ai-agent-book` Ch04/05，以及 `30-Agents` Ch05/07/08 的决策、计划、工具和验证模式 |
| 4 | 提示工程 | 既有 Prompt 来源、OpenAI 官方 Prompt 指南、`ai-agents-in-action` Ch02、`ai-agent-book` Ch02 和 `30-Agents` Ch03 的指令设计部分；隐藏思维链不作为审计证据 |
| 5 | 模型运行时与路由 | 既有运行时来源；各模型参数、Provider 差异、路由、重试、降级和调用协议；`30-Agents` Ch02/04 的多模型路由和熔断作为对照 |
| 6 | 会话、状态与上下文工程 | 既有 Session/Context 来源、`ai-agents-in-action` Ch10，以及 `ai-agent-book` Ch02 的静态前缀、轨迹、缓存、动态装配和压缩 |
| 7 | 记忆与外部知识系统 | 原第 7、8 章全部来源；`ai-agent-book` Ch03 补用户记忆、RAG、结构化索引、知识图谱和评估；`30-Agents` Ch05/06/10/13/15 的记忆、检索和领域知识案例按机制取证 |
| 8 | 框架与应用编排 | `easy-langent`、`hello-agents`、`ai-agents-in-action` Ch04/10、`30-Agents` Ch02/07/14/15 及各来源中的状态图和代表应用 |
| 9 | 安全、权限、沙箱与隐私 | 既有安全来源及 `ai-agents-in-action` Ch04/07、`ai-agent-book` Ch02/04；`30-Agents` Ch04/09/12/14/16 补公平性、可解释治理、合规门和物理安全约束 |
| 10 | Skills 与插件 | `learn-claude-code`、`Alice_methodology`、`hermes-book`、`hello-claw`、`harness-engineering`、`claude-code-analysis`、`hello-agents`、`ai-agent-book` Ch02 |
| 11 | MCP、A2A、ANP 与互操作 | 既有协议来源、`ai-agents-in-action` Ch03 和 `ai-agent-book` Ch04 的 MCP/协作工具边界 |
| 12 | 多模态、实时交互与行动环境 | `ai-agent-book` Ch09、`hello-agents` Extra06/Extra11、`30-Agents` Ch11/16，以及各来源中的 GUI、Web、流式、中断、具身控制和行动安全机制 |
| 13 | Gateway、多渠道、身份与路由 | `claw0`、`hello-claw`、`hermes-book` 及常驻 Agent 的渠道实现 |
| 14 | 后台任务、Cron、投递与韧性 | `learn-claude-code`、`claw0`、`hello-claw`、`hermes-book` |
| 15 | Loop Engineering | 12 个来源中分散的状态、验证、调度、隔离和恢复机制；`ai-agents-in-action` Ch09/10 提供三层 Loop、外置任务状态和停滞信号 |
| 16 | 多 Agent、任务系统与团队协作 | 既有多 Agent 来源、`ai-agents-in-action` Ch04/07、`ai-agent-book` Ch10，以及 `30-Agents` Ch07/14/15 的链式协调、Supervisor 和共识案例 |
| 17 | 测试、评测与基准 | 既有评测来源、`ai-agents-in-action` Ch07/10、`ai-agent-book` Ch06，以及 `30-Agents` Ch04/08/12 的验证代理、公平性分片和置信校准 |
| 18 | 生产工程与可观测性 | 既有生产来源、生产反馈入口、版本发布、SLO、灰度和回滚机制；`30-Agents` Ch04/12 的公平性监测和解释失败作为治理信号 |
| 19 | 自进化与后训练 | `Alice_methodology`、`harness-engineering`、`hello-agents`、`ai-agents-in-action` Ch07、`ai-agent-book` Ch07/08，以及 `30-Agents` Ch09/17 的受控自改进案例 |
| 20 | 案例与综合项目 | 12 个来源中的代表案例、工程模式和综合 Agent 路线；`30-Agents` 的 30 类架构只作为可组合模式库，不复制成 30 个项目 |

## 按来源反查

### `learn-claude-code`

| 来源内容 | 教材落点 |
| --- | --- |
| s01 Agent Loop、s02 Tool Use | 第 3 章 |
| s03 Permission、s04 Hooks | 第 9 章 |
| s05 TodoWrite、s06 Subagent、s12 Task、s15-s18 Team/Autonomous/Worktree | 第 15-18、20 章，以第 16 章为主 |
| s07 Skill Loading、s19 MCP | 第 10、11 章 |
| s08 Context Compact、s09 Memory、s10 System Prompt | 第 4、6、7 章 |
| s11 Error Recovery | 第 5、14、18 章 |
| s13 Background Tasks、s14 Cron | 第 14 章 |
| s20 Comprehensive Agent | 第 20 章 |

### `Alice_methodology`

| 来源内容 | 教材落点 |
| --- | --- |
| 哲学、架构、Agent Loop、工具系统 | 第 1、3、20 章 |
| 上下文、记忆和记忆博客 | 第 6、7 章 |
| 多 Agent、共建和交互方法 | 第 16、20 章 |
| 权限、安全 | 第 9 章 |
| MCP、Skills | 第 10、11 章 |
| 模型路由、Prompt | 第 4、5 章 |
| 自我进化 | 第 19 章 |
| 可观测性、工程范式和快速发布 | 第 17、18、20 章 |

### `hermes-book`

| 来源内容 | 教材落点 |
| --- | --- |
| 设计赌注、仓库地图、请求旅程和 AIAgent 核心 | 第 1、3、20 章 |
| Prompt、配置和模型抽象 | 第 4、5 章 |
| Tool、Tool Profiles | 第 3、9 章 |
| Skill、Delegation | 第 10、16 章 |
| SessionDB、Memory Provider、Context Compression | 第 6、7 章 |
| CLI/TUI、Gateway | 第 13 章 |
| Cron、Concurrency、Lifecycle、Runtime Defense | 第 14、15、18 章 |
| Testing | 第 17、18 章 |

### `easy-langent`

| 来源内容 | 教材落点 |
| --- | --- |
| 基础概念、模型、Prompt 和输出解析 | 第 1-4 章 |
| Memory、Tool 和会话 | 第 3、6、7 章 |
| Runnable、Router 和 RAG | 第 7、8 章 |
| LangGraph State、Node、Edge、Checkpoint 和 Human-in-the-loop | 第 6、8 章 |
| LangGraph 多智能体 | 第 8、16 章 |
| 课程项目和游戏 Agent | 第 8、20 章，以代表模式覆盖 |

### `claw0`

| 来源内容 | 教材落点 |
| --- | --- |
| s01 Agent Loop、s02 Tool Use | 第 3 章 |
| s03 Sessions、s06 Intelligence | 第 6、7 章 |
| s04 Channels、s05 Gateway Routing | 第 13 章 |
| s07 Heartbeat/Cron、s08 Delivery、s09 Resilience、s10 Concurrency | 第 14、15、18 章 |
| workspace 示例 | 第 7、10、20 章 |

### `harness-engineering-from-cc-to-ai-coding`

| 来源内容 | 教材落点 |
| --- | --- |
| Part 1：架构、工具和 Agent Loop | 第 1、3 章 |
| Part 2：系统提示、行为引导和工具提示 | 第 4 章 |
| Part 3：压缩和 Token 预算 | 第 6 章 |
| Part 4：记忆、规则覆盖和缓存 | 第 4、6、7 章 |
| Part 5：权限、分类器、Hooks 和项目规则 | 第 9 章 |
| Part 6：Agent 编排、Effort、Skill 和 Memory | 第 5、7、10、16 章 |
| Part 7：工程、测试、观测和发布 | 第 17-20 章 |
| 附录：环境变量、Feature Flag 和 Trace | 第 18 章 |

### `claude-code-analysis`

| 来源内容 | 教材落点 |
| --- | --- |
| 架构总览和组件分析 | 第 1、3、20 章 |
| Agent Memory、Context 和 Session Resume | 第 6、7 章 |
| Tool Call、Prompt 和模型调用 | 第 3-5 章 |
| 安全、隐私和 Sandbox | 第 9 章 |
| Skills、MCP | 第 10、11 章 |
| Multi-Agent | 第 16 章 |
| 测试证据、竞品和源码索引 | 第 17、18、20 章 |

### `hello-claw`

| 来源内容 | 教材落点 |
| --- | --- |
| 构建篇中的底层架构、网关、Session 和并发 | 第 1、13、14、18 章 |
| 安全与沙箱 | 第 9 章 |
| Skill 开发、发布和 ClawHub | 第 10 章 |
| 多智能体场景 | 第 16、20 章 |
| 场景点评和评测模板 | 第 17、20 章 |
| 安装、日常配置、硬件部署和命令手册 | 排除，不进入主教材 |

### `hello-agents`

| 来源内容 | 教材落点 |
| --- | --- |
| Ch01-Ch02：定义、类型和历史 | 第 1 章 |
| Ch03：LLM 基础 | 第 2、4、5 章 |
| Ch04：ReAct、Plan-and-Solve、Reflection | 第 3 章 |
| Ch05：低代码平台 | 第 8 章提炼编排边界，点击操作排除 |
| Ch06-Ch07：框架开发 | 第 3、8、16、20 章 |
| Ch08：记忆与检索 | 第 7 章 |
| Ch09、Extra02：上下文工程 | 第 4、6、18 章 |
| Ch10：MCP、A2A、ANP | 第 11 章 |
| Ch11、Extra12：Agentic RL 与后训练 | 第 19 章 |
| Ch12：性能评估、BFCL、GAIA 和数据生成 | 第 17 章 |
| Ch13-Ch15：旅行、Deep Research 和赛博小镇 | 第 7、8、16、20 章的代表案例 |
| Ch16、Co-creation projects | 第 20 章提炼成熟模式和项目方法 |
| Extra05、Extra08：Agent Skills | 第 10 章 |
| Extra09：工程踩坑 | 第 3-6、9、17、18 章 |
| Extra10：Agent 自进化 | 第 19 章 |
| Extra06、Extra11：GUI/Web Agent | 第 12、20 章的行动环境案例 |
| 安装指南、环境配置、FAQ 和低代码点击步骤 | 排除，不进入主教材 |

### `ai-agents-in-action-2nd-edition-cn`

下表是该来源的正式处理结果，同时记录正文、代码和附属资源的去向或排除理由。原书第 1、8 章由用户明确决定不进入主教材；这里仍记录排除理由，避免以后误判为遗漏。

| 来源内容 | 教材落点或处理结果 |
| --- | --- |
| 关于本书 | 只用于来源身份、版本和上游代码审计，不进入正文 |
| Ch01：Agent 定义、五层模型和多 Agent 概览 | 与现有第 1、3、11、16 章重复，按用户决定不进入主教材 |
| Ch02：LLM、Prompt、Agents SDK、类型化输出、Trace 和工具 | 第 2、4、5 章；第 4 章补严格 Schema，其余基础内容由既有正文覆盖并只保留原文入口 |
| Ch03：MCP 架构、Server、传输、工具封装和消费 | 第 11 章；补内部工具到 MCP Server 的迁移及不同 Host 风险，安装和旧传输口径排除 |
| Ch04：多 Agent 控制、通信、协调、Handoff 和 Guardrail | 第 8、9、16 章 |
| Ch05：CoT、ReAct、ToT、Reflexion 和 Sequential Thinking | 第 3 章；补 ToT 预算、失败记录和认知控制边界，隐藏思维链、玩具题材和重复案例排除 |
| Ch06：RAG、混合检索、语义/关系记忆、压缩和遗忘 | 第 7 章 |
| Ch07：TDAD、Grounding、Critic、Phoenix 和 Annotation | 第 7、9、16-19 章；产品界面和有缺陷的循环代码不复用 |
| Ch08：Web/API/Docker 部署和生产治理 | 现有第 9、13、14、18 章已覆盖得更深，按用户决定不进入主教材 |
| Ch09：内部、任务和元循环，研究状态、终止门、编排与协作 | 第 15、20 章；第 15 章是三层 Loop 与跨运行控制的主要落点 |
| Ch10：认知工作空间、注意力、门控、停滞和知识边界 | 第 3、6、8、15、17、20 章；内部认知循环不并入 Loop Engineering |
| Ch11：五层实践技巧、客服、RAG 和 Deep Research 蓝图 | 第 20 章新增三个业务蓝图；分散检查项与既有正文重复，不再逐章添加 |
| 附录 A-B | 代码环境、Node/npm 和 MCP 安装排错属于操作手册，排除 |
| `code/chapter_02` 至 `chapter_07`、`chapter_09` 至 `chapter_11` | 只选择能解释机制的结构；第 7、9、10 章代码存在控制流或状态问题，默认重写而非移植 |
| `code/chapter_08` | 与原书第 8 章一并按用户决定排除，不作为第 18、20 章来源 |
| `code/chapter_12`、`demo_project`、`bonus_projects` | A2A 孤立草稿、重复示例和图像生成项目排除；MCP 差异案例只作入口 |
| Chroma 生成数据、示例剧本、空文件和本地配置 | 生成物、许可不明语料和无知识内容文件排除 |
| 原书图片和站点资源 | 不直接复用出版插图；需要时按概念重新绘制原创 SVG/Draw.io，导航和宣传素材排除 |

### `ai-agent-book`

该来源以 `book/chapter1.md` 至 `book/chapter10.md` 为中文正文，配套实验位于 `chapter1/` 至 `chapter10/`。教材吸收机制与工程判断，不要求复制 92 个实验，也不把依赖特定服务、外部仓库或硬件的复现步骤视为必学内容。

| 来源内容 | 教材落点或处理结果 |
| --- | --- |
| Ch01：Agent = LLM + 上下文 + 工具、Harness、工作流模式 | 第 1-3、8 章；历史与基础定义去重，Harness 责任边界保留 |
| Ch02：KV Cache、Prompt、Skills、压缩、时间与状态提示 | 第 4、6、10 章；Prompt 行为设计进入第 4 章，动态装配、缓存和压缩进入第 6 章 |
| Ch03：用户记忆、RAG、稀疏/稠密检索、结构化索引和知识图谱 | 第 7 章；按“两个存储域、共享检索层”统一组织 |
| Ch04：感知、执行、协作工具，MCP，事件驱动与主动工具发现 | 第 3、10、11、14 章；安装和服务配置排除 |
| Ch05：Coding Agent、代码元能力、Sessionless、执行安全、故障恢复、动态 UI 与媒体工作流 | 第 3、6、8、9、12、14、20 章；具体业务 demo 只作机制案例，不逐个收录 |
| Ch06：评测环境、模型与 Harness 联合评估、指标、榜单、成本 | 第 17、18 章；实验环境和统计方法保留，榜单数值不作为长期结论 |
| Ch07：预训练、SFT、RL、工具调用内化和多模态后训练 | 第 19 章；训练环境、tool-result token masking、RLVP 和 on-policy distillation 进入原理部分 |
| Ch08：经验学习、Prompt/工具自改进、工作流编译、自进化评估 | 第 19 章；所有自动修改必须通过第 17、18 章的评测与发布门禁 |
| Ch09：语音三范式、实时交互、Computer Use 与机器人 | 第 12、17 章；机器人只保留规划/控制边界，VLA 训练、仿真和硬件部署排除 |
| Ch10：上下文共享、多 Agent 拓扑、虚拟文件系统和 Agent 社会 | 第 16 章；Agent society 作为研究边界，不当作生产默认方案 |
| `chapter1/` 至 `chapter10/` 配套实验 | 选择能解释数据结构、控制流、评测协议和失败模式的代码作为原文入口；不整套移植 |
| 外部仓库、API Key、模型服务、PDF/EPUB 构建与多语言版本 | 运行配置、构建流程和重复翻译排除；中文 `book/` 作为正文基准 |
| VLA、机器人硬件、语音模型训练及大规模训练项目 | 只保留 Agent 系统接口和评测边界；训练复现、硬件采购和部署不进入主教材 |
| 图片、生成脚本和宣传素材 | 不直接复用；确需配图时按本教程概念重新绘制 |

### `30-Agents-Every-AI-Engineer-Must-Build`

该来源由 17 个主题章节构成：Ch01-Ch04 建立基础与工程工具，Ch05-Ch16 展开 30 类 Agent 架构，Ch17 是未来方向实验。仓库包含 18 个原始 Notebook（Ch12 分为伦理与可解释两个 Notebook）和 86 个预执行运行变体。教材把它作为**架构模式与领域约束案例库**，不按 30 个名称重复排课。

| 来源内容 | 教材落点或处理结果 |
| --- | --- |
| Ch01：Agent 演进、认知循环、MCP/A2A 和能力级别 | 第 1、3、11 章；基础定义和协议概览与既有正文去重，勘误后的图只作校对，不直接复用 |
| Ch02：LangChain/LangGraph、模型路由、向量检索和工具集成 | 第 3、5、7、8 章；框架演示和厂商清单只作代码入口，不维护第二套工具选型指南 |
| Ch03：两层 Prompt、PTCF、Few-shot、ToT 和协作提示 | 第 4、16 章；任务契约和冲突检查保留，“展示思维链”不作为可观测性或审计方案 |
| Ch04：成本路由、熔断、微服务、零信任和公平性审计 | 第 5、9、17、18 章；公平性进入决策治理与分片评测，部署产品清单排除 |
| Ch05：自主决策、计划和记忆增强 Agent | 第 3、7、15、20 章；作为三类基础架构对照，不重新定义 Agent Loop |
| Ch06：知识检索、文档理解和科学研究 Agent | 第 7、12、20 章；RAG、OCR 和研究管线按机制去重，示例语料和安装步骤排除 |
| Ch07：工具 Agent、Chain-of-Agents 和 Agentic Workflow | 第 3、8、16、20 章；确定性工作流与多 Agent 协调的边界保留 |
| Ch08：数据分析、验证与通用问题求解 Agent | 第 3、16、17、20 章；Claim -> Evidence -> Verdict 管线作为验证案例，玩具数据不进入正文 |
| Ch09：代码生成、安全强化和自改进 Agent | 第 9、17、19、20 章；自改进必须沿用评测、审批、灰度和回滚门禁，不直接采用自动修改演示 |
| Ch10：对话、内容创作和推荐 Agent | 第 4、6、7、9、20 章；健康、内容和推荐案例只提炼分层防护与验证模式，不把模拟输出当领域证据 |
| Ch11：视觉语言、音频和物理传感 Agent | 第 12、17、20 章；多模态管线、传感器时间戳和降级模式保留，模型/设备配置排除 |
| Ch12：伦理推理、公平性监测、解释、反事实和置信校准 | 第 9、17、18、20 章；补“决策—硬门—证据—解释—申诉”治理闭环，伦理规则不能替代人的价值选择 |
| Ch13：医疗智能和科学发现 Agent | 第 7、9、15、17、20 章；FHIR、贝叶斯更新、知识缺口和实验反馈只作高风险领域案例，不作为医疗建议 |
| Ch14：金融顾问和法律智能 Agent | 第 8、9、16、17、20 章；Supervisor、合规门和引用复核保留，模拟市场与法律数据不作事实来源 |
| Ch15：教育智能和集体智能 Agent | 第 7、8、16、17、20 章；学生状态、知识追踪和共识引擎只作领域模式，投票不替代独立证据验证 |
| Ch16：具身智能和跨域集成 Agent | 第 9、12、16、20 章；多时间尺度控制、世界模型契约、硬安全门和统一约束包络进入第 12 章，硬件复现排除 |
| Ch17：自构架、Agent society、伦理漂移、记忆巩固和人机协作谱 | 第 7、16、19、20 章；作为研究问题和模拟实验，不当作生产默认架构 |
| 原始 Notebook 与章节 Python 文件 | 用于核对数据结构、控制流和失败路径；不把教学代码整套移植到本项目 |
| 86 个 `__RUN_*` Notebook、`LLM_COMPARISON*` 和 Provider 依赖文件 | 相同教学内容的运行输出、版本快照和环境配置；只用于比较执行差异，不重复计入知识覆盖 |
| `USECASE.md` 中的虚构企业、收入和效果数字 | 可用于理解约束和利益相关者，不作为真实生产成效或统计证据 |
| Errata、图片和 `chapter16/Git-2.53.0.2-64-bit.exe` | Errata 用于校对来源自身；出版图片、宣传资产和无关安装程序不进入教材 |

## 重复主题合并规则

### Agent 基础、历史与边界

- 使用 `hello-agents` 建立通用定义、PEAS、历史和 Workflow/Agent 边界。
- 使用 `learn-claude-code`、`Alice_methodology`、`hermes-book` 等工程来源解释 Model 与 Harness 的职责分工。
- 产品案例只证明架构取舍，不把产品定义当成通用学术定义。

### Agent Loop 与工具

- 使用 `learn-claude-code` 和 `claw0` 的最小循环建立实现骨架。
- 合并 `Alice_methodology`、`hermes-book`、`harness-engineering` 和 `claude-code-analysis` 中的生产约束。
- Tool Schema、Handler、权限、并发、Hook 和 Tool Result 进入同一条执行管线，避免分散重复讲解。

### Prompt 与模型运行时

- 第 4 章只处理任务定义、指令层级、示例、约束、输出契约和行为控制。
- 第 5 章处理 Provider、模型路由、流式事件、重试、fallback、成本和可靠性。
- Prompt 的动态组装、上下文选择、缓存友好分层和压缩属于第 6 章的 Context Builder。
- 模型专属参数留在 Provider 适配层，不写成跨模型通用原则。

### 会话、状态、上下文、记忆与外部知识

- 第 6 章区分会话记录、执行状态和本次模型上下文。
- 第 7 章把记忆和外部知识放在同一信息供给架构中讲解，但保留不同的写入来源、生命周期、权限、删除和评估语义。
- 记忆与知识可以共享召回、重排和上下文供给层，不能混入一个没有边界的向量库。
- 聊天摘要不能代替任务状态、长期记忆或外部知识证据。

### 框架、治理、扩展与行动环境

- 第 8 章用 LangChain、LangGraph 和代表应用解释编排抽象，不写成 API 手册。
- 第 9 章集中处理权限、审批、沙箱、提示注入、隐私，以及高影响决策的公平、解释、申诉和补救治理。
- 第 10 章处理 Skill 与 Plugin；第 11 章处理 MCP、A2A、ANP 等跨系统协议。
- 第 12 章处理语音、流式事件、打断、Computer Use 和动态行动环境；具身案例只吸收多时间尺度控制、世界模型和统一约束包络，不展开机器人硬件部署。

### Gateway、后台运行与 Loop Engineering

- 第 13 章处理渠道适配、身份、租户、Session Key 和路由。
- 第 14 章处理 Cron、Heartbeat、队列、投递、幂等、重试和恢复。
- 第 15 章把分散在 12 个来源中的状态、验证、隔离和调度知识组织成跨运行控制系统，不重复讲一次 Agent Loop。

### 多 Agent、评测、自进化与生产

- 第 16 章以任务边界、通信、验证和隔离为主线，不按多 Agent 产品形态分类堆叠。
- 第 17 章建立测试与评测证据，第 18 章把能力带入生产并形成可信运行反馈，第 19 章才讨论有证据、发布门禁和回滚能力的改进。
- 第 20 章使用代表案例验证方法，并给出综合 Agent 的里程碑路线；领域 Agent 名称拆回环境、控制结构、证据门禁和适应方式，不按名称建立平行项目。

## 外部补充

本地来源不能完整覆盖的主题可以补充论文、标准和官方工程资料：

- 第 4 章使用 OpenAI 官方 Prompt 指南补充 Prompt 债务、任务契约和模型专属控制。
- 第 11 章使用协议规范和官方文档校准 MCP、A2A、ANP。
- 第 12 章使用实时 API、语音和 Computer Use 的官方资料校准事件与行动协议。
- 第 15 章使用用户提供的三篇 X 文章，以及 Anthropic、OpenAI 等公开资料建立 Loop Engineering 专题。
- 第 17 章使用评测论文补足评价方法，第 18 章使用生产可靠性一手资料，第 19 章使用强化学习和后训练论文补足理论基础。

外部资料用于补足缺口，不能替代本地来源覆盖检查。

## 补充路径审计

旧学习方案曾为前 9 个来源列出 185 个来源路径。按新版 20 个主章节重新核对后，143 个具体路径已经保留在章末“原文入口”中，其余 42 项在本节归类。第 10-12 个来源由本文件的反向映射完成逐章、代码目录和资产级审计。重构前的旧版章节已经删除，不计入新版主教材覆盖。

本节只用于覆盖复核，不是学习者的必读清单。

### 覆盖证据：24 项

| 来源路径 | 对应内容与教材落点 |
| --- | --- |
| `source/Alice_methodology/chapters/16-alive-agent.md` | 人格一致性、记忆、子 Agent 角色和人机交互设计进入第 7、16、20 章 |
| `source/claude-code-analysis/analysis/05-differentiators-and-comparison.md` | 统一内核、权限、记忆和长会话治理进入第 1、6、9、16、18、20 章 |
| `source/claude-code-analysis/analysis/06-extra-findings.md` | Trust 边界、Unicode 攻击、隐私脱敏和状态传播用于第 9、16、18 章校对 |
| `source/claude-code-analysis/analysis/07-code-evidence-index.md` | 作为内核、权限、会话、记忆、隐私和协作实现的源码证据索引 |
| `source/claude-code-analysis/analysis/08-competitive-comparison.md` | 产品比较中的可迁移取舍进入第 18、20 章，使用时需要标注版本 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch04.md` | 工具权限、并发、流式和中断机制进入第 3、9、17 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch04b.md` | Plan Mode 的状态机、计划持久化和意图对齐进入第 3、4、6 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch10.md` | 压缩后的文件、Skill、计划和运行状态恢复进入第 6 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part4/ch14.md` | Prompt Cache 中断检测、状态快照和变化归因进入第 4-6、18 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part4/ch15.md` | 缓存友好装配、Skill 预算和运行时优化进入第 4-6、18 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch18.md` | Hooks、自定义拦截点和执行治理进入第 3、9、18 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch18b.md` | 多平台沙箱、文件与网络隔离进入第 9 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch19.md` | 用户指令覆盖层、作用域和循环引用治理进入第 4、9、10 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20c.md` | 远程多 Agent 规划、状态机、轮询和错误处理进入第 15、16、18 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch24.md` | 跨会话记忆、持久学习和作用域进入第 7、19 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch26.md` | 上下文预算、上下文卫生、压缩恢复和循环熔断进入第 6、15、18 章 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch28.md` | 缓存脆弱性、压缩损失、工具截断和 Feature Flag 复杂性用于第 6、17、18、20 章校对 |
| `source/hello-agents/Extra-Chapter/Extra11-WebAgent科普与实战.md` | Web Agent 的行动环境、感知和安全边界进入第 12、20 章 |
| `source/hello-claw/docs/cn/adopt/chapter10/index.md` | 威胁模型和安全原则进入第 9 章，具体配置命令排除 |
| `source/hello-claw/docs/cn/build/chapter9/index.md` | WASM/Docker 沙箱、密钥保护和注入防御进入第 9 章 |
| `source/hello-claw/docs/cn/build/skill-practice/index.md` | Skill 边界、目录、Frontmatter、发现和触发机制进入第 10 章 |
| `source/hermes-book/src/part5/ch13-cli-tui.md` | CLI/TUI 交互层和控制面进入第 13、18、20 章 |
| `source/hermes-book/src/part5/ch16-terminal-backends.md` | 本地、Docker、SSH 和云端沙箱等执行环境抽象进入第 8、9、13、18、20 章 |
| `source/learn-claude-code/s05_todo_write/README.md` | TodoWrite、任务外部化和进度约束进入第 16 章 |

### 排除或索引性来源：11 项

| 来源路径 | 处理结果 |
| --- | --- |
| `source/claude-code-analysis/analysis/09-final-summary.md` | 属于前文重复总结，由具体分析章节覆盖 |
| `source/claude-code-analysis/analysis/10-src-file-tree.md` | 属于静态仓库导航附录，容易随版本过时 |
| `source/claude-code-analysis/analysis/11-hidden-features-and-easter-eggs.md` | 隐藏功能、未发布能力和彩蛋清单排除；通用 Feature Flag 方法由第 18 章其他来源覆盖 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch23.md` | 以未发布 Feature Flag 推断产品路线，按未经证实且容易过时的产品推测排除 |
| `source/hello-agents/Co-creation-projects/README.md` | 共创项目索引不直接进入正文，成熟模式由第 20 章代表案例覆盖 |
| `source/hello-agents/README.md` | 来源工程导航索引，不作为独立知识内容重复计入 |
| `source/hello-claw/docs/cn/adopt/intro/index.md` | 产品介绍、热度描述和宣传性学习路径排除 |
| `source/hello-claw/docs/cn/adopt/chapter1/index.md` | 一键安装、Quick Setup 和积分操作排除 |
| `source/hello-claw/docs/cn/build/chapter10/index.md` | 硬件选型、功耗和部署方案排除 |
| `source/hello-claw/docs/cn/university/multi-claw-hiclaw/index.md` | 主体是 OpenClaw 安装、配置和排错；通用多 Agent 模式由第 16 章其他来源覆盖 |
| `source/hello-claw/docs/cn/university/group-debate/index.md` | 主体是飞书应用、实例和角色配置；通用多 Agent 模式由第 16 章其他来源覆盖 |

### 目录级处理规则：7 项

| 来源路径模式 | 处理规则 |
| --- | --- |
| `source/Alice_methodology/blog/*.md` | 作为博客集合；有独立机制的文章单列，其余作为章节补充 |
| `source/claude-code-analysis/analysis/components/*.md` | 作为组件分析集合，按组件主题映射到对应章节 |
| `source/easy-langent/project/**/README.md` | 作为项目案例池，只选择能证明架构取舍的成熟项目 |
| `source/harness-engineering-from-cc-to-ai-coding/book/src/appendix/*.md` | 作为附录集合，配置、环境变量和 Trace 内容按需取证 |
| `source/hello-claw/docs/cn/appendix/*.md` | 作为产品附录集合；安装和命令手册排除，通用工程机制单独取证 |
| `source/hello-claw/docs/cn/university/*.md` | 按 `source/hello-claw/docs/cn/university/**/*.md` 递归处理整个场景案例池；产品配置、宣传和低成熟度项目排除，通用模式由其他来源交叉验证 |
| `source/learn-claude-code/skills/**` | 作为 Skill 样例目录，选择代表性 `SKILL.md` 支撑第 10 章 |

## 当前审计结论

- 12 个来源工程中的可迁移知识已经分配到新版 20 章；第 10 个来源的原书第 1、8 章按用户决定排除，第 11 个来源的操作性复现和硬件训练内容按覆盖口径排除，第 12 个来源的重复运行副本、虚构业务数字、环境配置和无关安装程序排除。
- 重复主题已经按机制合并；多语言版本和同类案例不重复计入。
- 安装配置、硬件部署、低代码点击、宣传内容和低成熟度项目已按规则排除，不属于遗漏。
- 20 章正文已经生成，仍需按教材目录记录的进度逐章检查深度、准确性、章间重复和案例质量。
- Review 中发现来源遗漏时，应同时修改对应章节和本文件；只修改措辞或例子时，不需要更新覆盖关系。
