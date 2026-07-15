# 9 个来源工程覆盖审计

> 本表用于检查 `source/` 下 9 个教程工程是否已经被融合进教材。第 1-14 章均已生成；第 11 章是基于用户提供文章和公开资料新增的独立专题，并把 9 个来源中分散的调度、状态、验证、安全与可观测性内容重新串联起来。

## 覆盖结论

| 来源工程 | 是否覆盖 | 主要落点 |
| --- | --- | --- |
| `source/learn-claude-code` | 已覆盖 | 第 1、2、3、5、6、8、9、10、12、13、14 章 |
| `source/Alice_methodology` | 已覆盖 | 第 1、2、3、4、5、6、8、9、12、13、14 章 |
| `source/hermes-book` | 已覆盖 | 第 1、2、3、4、5、6、9、10、12、13、14 章 |
| `source/easy-langent` | 已覆盖 | 第 1、2、3、5、7、12、14 章 |
| `source/claw0` | 已覆盖 | 第 1、2、5、10、14 章 |
| `source/harness-engineering-from-cc-to-ai-coding` | 已覆盖 | 第 1、2、3、4、5、6、8、9、12、13、14 章 |
| `source/claude-code-analysis` | 已覆盖 | 第 1、2、3、4、5、6、8、9、12、13、14 章 |
| `source/hello-claw` | 已覆盖 | 第 1、8、9、10、13、14 章 |
| `source/hello-agents` | 已覆盖 | 第 1、2、3、4、5、6、7、8、9、10、12、13、14 章 |

## 按工程展开

### learn-claude-code

| 内容 | 教材落点 |
| --- | --- |
| s01 Agent Loop | 第 1、2、14 章 |
| s02 Tool Use | 第 2、14 章 |
| s03 Permission | 第 8、14 章 |
| s04 Hooks | 第 8、13 章 |
| s05 TodoWrite | 第 12、14 章 |
| s06 Subagent | 第 12、14 章 |
| s07 Skill Loading | 第 9、14 章 |
| s08 Context Compact | 第 5、14 章 |
| s09 Memory | 第 6、14 章 |
| s10 System Prompt | 第 3、14 章 |
| s11 Error Recovery | 第 4、13、14 章 |
| s12 Task System | 第 12、14 章 |
| s13 Background Tasks | 第 10、14 章 |
| s14 Cron Scheduler | 第 10、14 章 |
| s15 Agent Teams | 第 12、14 章 |
| s16 Team Protocols | 第 12、14 章 |
| s17 Autonomous Agents | 第 12、14 章 |
| s18 Worktree Isolation | 第 12、14 章 |
| s19 MCP Tools | 第 9、14 章 |
| s20 Comprehensive Agent | 第 13、14 章 |

### Alice_methodology

| 内容 | 教材落点 |
| --- | --- |
| 哲学、架构、Agent Loop、工具系统 | 第 1、2、14 章 |
| 上下文与记忆、记忆博客 | 第 5、6 章 |
| 多 Agent、共建博客、活人感设计 | 第 12、14 章 |
| 权限、安全 | 第 8 章 |
| MCP、Skills、自我进化 | 第 9 章 |
| 模型路由、提示词 | 第 3、4 章 |
| 可观测性、工程范式、快速发布 | 第 13、14 章 |

### hermes-book

| 内容 | 教材落点 |
| --- | --- |
| 设计赌注、仓库地图、请求旅程、AIAgent 核心 | 第 1、2、14 章 |
| Prompt、配置、模型抽象 | 第 3、4 章 |
| Tool、Tool Profiles、Skill、Delegation | 第 2、9、12 章 |
| SessionDB、Memory Provider、Context Compression | 第 5、6 章 |
| CLI/TUI、Gateway、Cron、Terminal Backends | 第 10 章 |
| Concurrency、Lifecycle、Runtime Defense、Testing | 第 10、13 章 |
| Philosophy | 第 1、14 章 |

### easy-langent

| 内容 | 教材落点 |
| --- | --- |
| 基础概念、模型、Prompt、输出解析 | 第 1、3 章 |
| Memory、Tool | 第 2、5、6 章 |
| Runnable、Router、RAG | 第 7 章 |
| 中期综合实践 | 第 7、14 章 |
| LangGraph 基础 | 第 7 章 |
| LangGraph 多智能体 | 第 7、12 章 |
| 谁是卧底游戏智能体与项目目录 | 第 7、14 章 |

### claw0

| 内容 | 教材落点 |
| --- | --- |
| s01 Agent Loop | 第 1、2 章 |
| s02 Tool Use | 第 2 章 |
| s03 Sessions | 第 5 章 |
| s04 Channels | 第 10 章 |
| s05 Gateway Routing | 第 10 章 |
| s06 Intelligence | 第 4、5 章 |
| s07 Heartbeat / Cron | 第 10 章 |
| s08 Delivery | 第 10 章 |
| s09 Resilience | 第 10、13 章 |
| s10 Concurrency | 第 10、13 章 |
| workspace 示例 | 第 1、6、9、14 章 |

### harness-engineering-from-cc-to-ai-coding

| 内容 | 教材落点 |
| --- | --- |
| Part1：架构、工具、Agent Loop | 第 1、2 章 |
| Part2：系统提示词、行为引导、工具提示词 | 第 3 章 |
| Part3：压缩、token 预算 | 第 5 章 |
| Part4：记忆、规则覆盖 | 第 6、8 章 |
| Part5：权限、分类器、Hooks、CLAUDE.md | 第 8 章 |
| Part6：Agent 编排、Effort、技能、记忆 | 第 4、6、9、12 章 |
| Part7：工程化、测试、观测、发布 | 第 13、14 章 |
| 附录：索引、环境变量、Feature Flags、Trace | 第 13、14 章 |

### claude-code-analysis

| 内容 | 教材落点 |
| --- | --- |
| 架构总览、组件分析 | 第 1、2、14 章 |
| 安全、隐私、用户数据 | 第 8 章 |
| Agent Memory、Context、Session Resume | 第 5、6 章 |
| Tool Call、Prompt、Skills、MCP、Sandbox | 第 2、3、8、9 章 |
| Multi-Agent | 第 12 章 |
| 竞品比较、隐藏功能、最终总结 | 第 13、14 章 |
| 证据索引、源码树 | 第 13、14 章 |

### hello-claw

| 内容 | 教材落点 |
| --- | --- |
| 项目简介、教程定位、应用场景 | 第 1、13、14 章 |
| 构建篇：OpenClaw 底层、网关、安全沙箱 | 第 8、10、14 章 |
| 技能实战与 ClawHub | 第 9 章 |
| 附录 A：学习资源 | 第 14 章 |
| 附录 D：技能开发与发布 | 第 9 章 |
| 附录 G：配置文件 | 第 10、13 章 |
| 场景点评与评测模板 | 第 13 章 |

### hello-agents

| 内容 | 教材落点 |
| --- | --- |
| README、Preface、Ch01 初识智能体、Ch02 智能体发展史 | 第 1 章 |
| Ch03 大语言模型基础 | 第 3、4 章 |
| Ch04 智能体经典范式构建 | 第 2 章 |
| Ch05 基于低代码平台的智能体搭建 | 第 7、10 章 |
| Ch06 框架开发实践 | 第 7、12 章 |
| Ch07 构建你的 Agent 框架 | 第 2、4、14 章 |
| Ch08 记忆与检索 | 第 6、7 章 |
| Ch09 上下文工程 | 第 5、8、13 章 |
| Ch10 智能体通信协议 | 第 9 章 |
| Ch11 Agentic-RL | 第 4、13、14 章 |
| Ch12 智能体性能评估 | 第 13 章 |
| Ch13 智能旅行助手 | 第 7、10、12、14 章 |
| Ch14 自动化深度研究智能体 | 第 7、12、14 章 |
| Ch15 构建赛博小镇 | 第 6、7、10、12、14 章 |
| Ch16 毕业设计、Co-creation projects | 第 13、14 章 |
| Extra02 上下文工程补充 | 第 5 章 |
| Extra05 AgentSkills 解读、Extra08 如何写出好的 Skill | 第 9 章 |
| Extra09 Agent 应用开发实践踩坑与经验分享 | 第 2、3、5、8、13 章 |
| Extra10 Agent 自进化、Extra11 WebAgent 科普与实战 | 第 9、10、14 章 |

## 外部补充章节

- 第 11 章 `Loop Engineering：从单次循环到可持续执行系统` 已生成。
- 本章以用户提供的三篇 X 原文为核心；在用户登录后已逐篇读取全文，并使用可访问镜像交叉核对，同时补充 OpenAI、ChatGPT、Anthropic 和 Addy Osmani 等公开资料。
- 本章属于外部专题补充，不改变 9 个本地来源工程的覆盖口径；它负责把本地教程已有的 Agent Loop、Cron、任务系统、上下文、验证、权限、隔离和观测能力组织成跨运行闭环。

## 检查结论

第 1-14 章已经全部生成，9 个来源工程的主题均已纳入融合教材。第 11 章额外补上 Loop Engineering 的独立视角，并与第 10 章的触发与调度、第 12 章的多 Agent 分工、第 13 章的评测与可观测性形成连续学习路径。
