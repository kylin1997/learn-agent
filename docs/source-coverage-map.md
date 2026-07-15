# 教程覆盖地图

本文件记录 9 份教程的角色定位，以及学习方案中如何合并重复内容。

## 目录与侧重点

| 教程目录 | 主要侧重点 | 在学习方案中的位置 |
| --- | --- | --- |
| `source/easy-langent` | LangChain、LangGraph、RAG、课程项目、应用落地 | 阶段 1、3、5 |
| `source/hermes-book` | Hermes Agent 源码、长期个人 Agent、Gateway、记忆、测试、生命周期 | 阶段 1、2、3、4、7、8、10 |
| `source/Alice_methodology` | 桌面 Agent 工程方法论、权限、记忆、多 Agent、自进化、人格化 | 阶段 1、2、3、4、6、7、9、10 |
| `source/hello-claw` | OpenClaw 使用、配置、运维、Skill 场景、构建方案 | 阶段 1、6、7、8、9、10 |
| `source/claw0` | 从零构建 Agent Gateway，强调渠道、路由、主动性、可靠投递 | 阶段 2、4、8 |
| `source/harness-engineering-from-cc-to-ai-coding` | Claude Code 源码模式、上下文、权限、缓存、多 Agent、工程原则 | 阶段 1、2、3、4、6、7、9、10 |
| `source/claude-code-analysis` | Claude Code 静态源码分析、安全、组件、竞品、证据索引 | 阶段 2、3、4、6、7、9、10 |
| `source/learn-claude-code` | Claude Code 式 Harness 的 20 节渐进实现 | 阶段 1、2、4、6、7、9 |
| `source/hello-agents` | Datawhale 系统性 Agent 教程，覆盖基础、范式、低代码、框架、记忆/RAG、上下文工程、MCP/A2A/ANP、Agentic RL、评估、旅行助手、Deep Research、赛博小镇和毕业项目 | 阶段 1、2、3、4、5、6、7、8、9、10 |

## 重复主题合并规则

### Agent Loop

合并来源：

- `learn-claude-code` s01
- `claw0` s01
- `Alice_methodology` Ch03
- `Hermes` Ch03-Ch04
- `harness` Ch03
- `claude-code-analysis` 架构章节
- `hello-agents` Ch01/Ch02/Ch04/Ch07

学习方式：

- 以 `learn-claude-code` 的最小循环为实现主线。
- 用 `claw0` 看 Gateway 场景下的循环。
- 用 `Hermes`、`Alice`、`harness`、`claude-code-analysis` 做生产级对照。

### 工具系统

合并来源：

- `learn-claude-code` s02
- `claw0` s02
- `Alice_methodology` Ch04
- `Hermes` Ch06-Ch07
- `harness` Ch02/Ch04/Ch08
- `claude-code-analysis` Tool Call
- `easy-langent` Ch03
- `hello-agents` Ch04/Ch07/Ch09 和 Extra09

学习方式：

- 先实现 schema + handler map。
- 再补权限、并发、安全调度、工具提示词、LangChain tool。

### Prompt 与模型路由

合并来源：

- `easy-langent` Ch02
- `Alice_methodology` Ch11/Ch14
- `Hermes` Ch05/Ch17/Ch18
- `harness` Part2
- `claude-code-analysis` Prompt 管理
- `learn-claude-code` s10
- `hello-agents` Ch03/Ch04/Ch07/Ch09 和 Extra09

学习方式：

- 先掌握模板和输出解析。
- 再实现 runtime prompt assembler。
- 最后加 provider router、fallback、缓存友好结构。

### 上下文与记忆

合并来源：

- `learn-claude-code` s08-s09
- `claw0` s03/s06
- `Alice_methodology` Ch05 和记忆博客
- `Hermes` Ch10-Ch12
- `harness` Part3/Part4/Ch24
- `claude-code-analysis` Memory、Context、Session Storage
- `easy-langent` Ch03/Ch04
- `hello-agents` Ch08/Ch09、Extra02、Extra09

学习方式：

- 会话持久化、上下文压缩、长期记忆分三层学习；在融合教材中拆成“会话与上下文管理”和“长期记忆系统”两章。
- 先做简单 JSONL，再做 compact，最后做 memory recall。

### 安全与权限

合并来源：

- `learn-claude-code` s03-s04
- `Alice_methodology` Ch07/Ch12
- `hello-claw` 安全章节
- `harness` Part5
- `claude-code-analysis` 安全、隐私、Sandbox
- `hello-agents` Ch09 的 TerminalTool 安全机制、Extra09 工具踩坑

学习方式：

- 先实现权限结果模型。
- 再加入规则、分类器、沙箱、提示注入防御。

### Skill、MCP、插件

合并来源：

- `learn-claude-code` s07/s19 和 `skills/`
- `Alice_methodology` Ch08-Ch10
- `Hermes` Ch08-Ch09
- `hello-claw` Skill 实战与附录 D
- `harness` Ch22-Ch23
- `claude-code-analysis` Skills/MCP/隐藏功能
- `hello-agents` Ch10、Extra05、Extra08、Extra10、Extra11

学习方式：

- 先写 Skill。
- 再接 MCP。
- 最后比较 Plugin、Feature Flag、自进化。

### Gateway、Cron 与常驻 Agent

合并来源：

- `claw0` s04-s10
- `hello-claw` 领养篇和构建篇
- `Hermes` Ch13-Ch21
- `learn-claude-code` s13-s14
- `hello-agents` Ch05 的 n8n 工作流、Ch13/Ch15 的 Web 应用和后台任务实践

学习方式：

- 统一消息格式。
- 路由到 Agent。
- 加心跳、Cron、投递队列、重试、并发 lane。

### Loop Engineering

本主题是放在 Gateway、Cron 与主动 Agent 之后的独立外部补充章。它不把 Agent Loop 再讲一遍，而是把 9 份教程中分散的调度、状态、验证、隔离、安全和可观测性知识，组织成跨运行的反馈控制系统。

合并来源：

- `learn-claude-code` s08、s12-s18 的上下文压缩、任务、后台运行、自主 Agent 与 worktree 隔离
- `claw0` s07-s10 的调度、投递、韧性和并发
- `Hermes` Ch19-Ch22 的并发、生命周期、防御和测试
- `harness` Part 6-7 的 Agent 编排、评测和工程实践
- `hello-agents` Ch09、Ch12、Extra10 的上下文工程、评估和自进化
- 用户提供的三篇 X 文章，以及 OpenAI、ChatGPT、Anthropic、Addy Osmani 等公开资料

学习方式：

- 先区分内层 Agent Loop、运行 Harness 和外层 Loop Engineering。
- 再设计 verifier、外部状态、检查点、停止条件和失败恢复。
- 最后从人工可验证流程出发，逐步升级为可调度、可恢复、可审计的最小可信 Loop。

### 多 Agent 与任务系统

合并来源：

- `learn-claude-code` s05-s06/s12-s18
- `Alice_methodology` Ch06 和多 Agent 博客
- `Hermes` Ch09
- `harness` Ch20-Ch20c
- `claude-code-analysis` Multi-Agent
- `hello-claw` 多智能体场景
- `easy-langent` LangGraph 多智能体实践
- `hello-agents` Ch06/Ch13/Ch14/Ch15/Ch16 和共创项目

学习方式：

- 先做 TodoWrite 和任务图。
- 再做 subagent。
- 最后做 team、mailbox、自主认领、worktree 隔离。

## 读法约定

- 中文版本优先。
- 同一教程中的英文、日文翻译不重复学习，除非中文缺失。
- 旧版课程只用于章节映射，不和新版重复计入。
- 应用项目不只看 README，重要项目要走读代码。
- 每次学习新主题时，先在本文件确认覆盖来源，再写笔记。
