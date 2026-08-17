# 12 个 Agent 教程知识点目录

## 目标

本目录以 12 个来源工程的**原始章节**为整理单位，把内容相同或相近的章节归到同一个知识点下，并记录这些章节已经明确关联的代码、测试或 Notebook。

本目录不以当前融合教材的 20 章为框架，也不判断某个知识点应该进入教材哪一章。它只回答三个问题：

1. 12 个工程分别有哪些相关章节。
2. 哪些原始章节在讲相同或相近的知识点。
3. 学习该知识点时可以查看哪些代码示例。

## 整理口径

- 原工程章节是最小整理单位，不把原章节拆成新的教材小节。
- 一个原章节确实覆盖多个知识点时，可以在多个知识点下重复引用。
- “代码示例”只列当前资料已经明确关联的源码、测试、项目或原始 Notebook；只知道章节目录但尚未掌握具体文件时，标为“待 Clone 后展开”。
- 当前工作区只保留了 `30-Agents-Every-AI-Engineer-Must-Build`。其他工程先沿用现有文档记录的路径，后续 Clone 后再校验和补全。
- Provider 预执行副本、生成输出、安装脚本、图片、宣传材料和纯环境配置不作为独立知识点。`30-Agents` 的 `__RUN_*` Notebook 与原始 Notebook 内容重复，因此代码列只列原始 Notebook。
- 该索引是第一版知识地图，不代表尚未 Clone 的工程已经完成文件级穷举。

## 来源工程

| 工程 | 上游项目 |
| --- | --- |
| `easy-langent` | [datawhalechina/easy-langent](https://github.com/datawhalechina/easy-langent) |
| `hermes-book` | [ZhangHanDong/hermes-book](https://github.com/ZhangHanDong/hermes-book) |
| `Alice_methodology` | [itshen/Alice_methodology](https://github.com/itshen/Alice_methodology) |
| `hello-claw` | [datawhalechina/hello-claw](https://github.com/datawhalechina/hello-claw) |
| `claw0` | [shareAI-lab/claw0](https://github.com/shareAI-lab/claw0) |
| `harness-engineering-from-cc-to-ai-coding` | [ZhangHanDong/harness-engineering-from-cc-to-ai-coding](https://github.com/ZhangHanDong/harness-engineering-from-cc-to-ai-coding) |
| `claude-code-analysis` | [liuup/claude-code-analysis](https://github.com/liuup/claude-code-analysis) |
| `learn-claude-code` | [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) |
| `hello-agents` | [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) |
| `ai-agents-in-action-2nd-edition-cn` | [yixiangshijie/ai-agents-in-action-2nd-edition-cn](https://github.com/yixiangshijie/ai-agents-in-action-2nd-edition-cn) |
| `ai-agent-book` | [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) |
| `30-Agents-Every-AI-Engineer-Must-Build` | [PacktPublishing/30-Agents-Every-AI-Engineer-Must-Build](https://github.com/PacktPublishing/30-Agents-Every-AI-Engineer-Must-Build) |

## 知识点总览

1. Agent 基础、发展史与系统架构
2. LLM 基础、模型抽象与 Provider 运行时
3. Prompt、System Prompt 与行为控制
4. Agent Loop、推理、规划与反思
5. 工具调用与工具运行时
6. 会话、任务状态与恢复
7. 上下文工程、压缩、预算与缓存
8. 长期记忆与记忆治理
9. RAG、知识检索与结构化知识
10. Agent 框架、工作流与状态图编排
11. 权限、Hooks、安全、沙箱与隐私
12. Skills 与插件系统
13. MCP、A2A、ANP 与协议互操作
14. 多 Agent、委托、任务与团队协作
15. Channel、Gateway、身份与路由
16. 后台任务、Heartbeat、Cron 与可靠投递
17. 并发、生命周期、错误恢复与运行时韧性
18. 长任务、自治运行与跨运行 Loop
19. 多模态、实时交互、GUI 与 Web Agent
20. 测试、评测、验证与基准
21. 部署、可观测性与生产迭代
22. 后训练、经验学习与 Agent 自进化
23. Coding Agent 与软件开发 Agent
24. 数据分析、通用推理与验证 Agent
25. 对话、内容创作与推荐 Agent
26. Deep Research、旅行助手与综合应用
27. 伦理、公平、可解释与高影响决策
28. 医疗与科学研究 Agent
29. 金融与法律 Agent
30. 教育与集体智能 Agent
31. 具身智能与物理行动环境
32. Agent Society、未来架构与人机协作

## 1. Agent 基础、发展史与系统架构

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | `docs/chapter1/第一章 初识智能体.md`；`docs/chapter2/第二章 智能体发展史.md` | 待 Clone 后展开 |
| `Alice_methodology` | `chapters/00-preface.md`；`chapters/01-philosophy.md`；`chapters/02-architecture.md` | 待 Clone 后展开 |
| `hermes-book` | `part1/ch01-design-bets.md`；`part1/ch02-repo-map.md` | 章节中的 Hermes 仓库结构，待 Clone 后展开源码入口 |
| `easy-langent` | `docs/guide/chapter1.md`：LangChain 与 LangGraph 的边界 | 待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part1/ch01.md`：AI 编码 Agent 技术栈 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/01-architecture-overview.md`；`analysis/05-differentiators-and-comparison.md` | `analysis/07-code-evidence-index.md` 提供源码证据索引 |
| `learn-claude-code` | `README-zh.md`：渐进构建 Agent Harness | `s01_agent_loop/` 至 `s17_goal_loop/`（s01-s17 新版共 17 章）的渐进实现，待 Clone 后展开文件级入口 |
| `claw0` | `README.zh.md`：从最小循环到常驻 Agent | `sessions/zh/s01_agent_loop.md` 至 `s10_concurrency.md` 的配套最小实现 |
| `hello-claw` | `docs/cn/build/chapter1/index.md`：架构设计哲学与总体架构 | 待 Clone 后展开 |
| `ai-agent-book` | `book/chapter1.md`：Agent、Harness 与工作流基础 | `chapter1/` 配套实验，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch01：Agent 定义、五层模型和多 Agent 概览 | `code/chapter_01/`，待 Clone 后核验 |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter01/README.md`：Foundations of Agent Engineering | `chapter01/ch01_foundations_of_agent_engineering.ipynb`；`mock_llm.py`；`utils.py` |

## 2. LLM 基础、模型抽象与 Provider 运行时

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | `docs/chapter3/第三章 大语言模型基础.md` | 待 Clone 后展开 |
| `easy-langent` | `docs/guide/chapter2.md`：LangChain 模型、Prompt 与输出解析 | 待 Clone 后展开 |
| `Alice_methodology` | `chapters/11-llm-routing.md`：模型路由 | 待 Clone 后展开 |
| `hermes-book` | `part6/ch17-config-profiles.md`；`part6/ch18-model-abstraction.md` | Provider 兼容层、配置和成本追踪实现，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part2/ch06b.md`：API 通信层；`part2/ch07.md`：模型调优与 A/B 测试；`part6/ch21.md`：Effort、Fast Mode 与 Thinking | 待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch02：LLM、Agents SDK、类型化输出、Trace 与工具 | `code/chapter_02/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter02/README.md`：Agent Engineer's Toolkit；`chapter04/README.md` 中的成本路由与熔断 | `chapter02/ch02_agent_toolkit.ipynb`；`chapter02/mock_llm_layer.py`；`supporting/llm_provider.py`；`chapter04/ch04_agent_deployment.ipynb`；`chapter04/agent_utils.py`；`chapter04/mock_llm.py` |

## 3. Prompt、System Prompt 与行为控制

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s15_integrated_harness/code.py`：`assemble_system_prompt(context)` 分层组装 | `s15_integrated_harness/` 同章节实现（旧版 s10_system_prompt 已并入新版集成 Harness） |
| `Alice_methodology` | `chapters/14-prompts.md` | 待 Clone 后展开 |
| `hermes-book` | `part2/ch05-prompt-system.md` | Prompt 组装实现，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part2/ch05.md`：系统提示架构；`part2/ch06.md`：行为引导；`part2/ch08.md`：工具提示词；`part5/ch19.md`：用户指令覆盖层 | 待 Clone 后展开 |
| `hello-agents` | Ch03 的 Prompt 基础；Ch04 的 ReAct、Plan-and-Solve 与 Reflection 提示 | 待 Clone 后展开 |
| `ai-agent-book` | `book/chapter2.md` 中的 Prompt 与上下文设计 | `chapter2/prompt-engineering/README.md` |
| `ai-agents-in-action-2nd-edition-cn` | Ch02 的 Prompt、类型化输出和工具描述 | `code/chapter_02/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter03/README.md`：The Art of Agent Prompting | `chapter03/ch03_agent_prompting.ipynb`；`mock_llm.py`；`utils.py` |

## 4. Agent Loop、推理、规划与反思

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s01_agent_loop/README.md` | `s01_agent_loop/` 同目录最小循环实现，待 Clone 后展开 |
| `claw0` | `sessions/zh/s01_agent_loop.md` | 同章节配套最小实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/03-agent-loop.md` | 待 Clone 后展开 |
| `hermes-book` | `part2/ch03-request-journey.md`；`part2/ch04-aiagent-core.md` | AIAgent 内核和请求循环源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part1/ch03.md`：Agent Loop；`part1/ch04b.md`：Plan Mode | 待 Clone 后展开 |
| `hello-agents` | Ch04：ReAct、Plan-and-Solve、Reflection；Ch07：自建 Agent 框架 | 待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch05：CoT、ReAct、ToT、Reflexion 与 Sequential Thinking；Ch09：内部循环、Task Loop 与 Meta Loop；Ch10：认知与元认知控制 | `code/chapter_05/`、`code/chapter_09/`；`code/chapter_10/01_cognitive_workspace.py` |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter05/README.md`：Autonomous Decision-Making、Planning、Memory-Augmented Agent | `chapter05/ch05_foundational_architectures.ipynb`；`color_logger.py`；`mock_llm.py`；`resilience.py` |

## 5. 工具调用与工具运行时

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s02_tool_use/README.md` | `s02_tool_use/` 同目录实现，待 Clone 后展开 |
| `claw0` | `sessions/zh/s02_tool_use.md` | 同章节配套最小实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/04-tool-system.md` | 待 Clone 后展开 |
| `hermes-book` | `part3/ch06-tool-system.md`；`part3/ch07-tool-profiles.md` | 工具注册、执行和 Profile 源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part1/ch02.md`：工具系统；`part1/ch04.md`：权限、并发、流式与中断 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04b-tool-call-implementation.md` | 对应 Tool Call 源码由 `analysis/07-code-evidence-index.md` 反查 |
| `hello-agents` | Ch07：构建 Agent 框架中的工具模块 | 待 Clone 后展开 |
| `ai-agent-book` | `book/chapter4.md`：感知、执行、协作工具与主动工具发现 | `chapter4/` 配套实验，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter07/README.md`：Tool-Using Agent、Chain-of-Agents、Agentic Workflow | `chapter07/ch07_tool_orchestration.ipynb` |

## 6. 会话、任务状态与恢复

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `claw0` | `sessions/zh/s03_sessions.md` | 同章节 Session 最小实现，待 Clone 后展开 |
| `easy-langent` | `docs/guide/chapter3.md`：会话历史；Ch06-Ch07 的 LangGraph thread、checkpoint 与 resume | `project/WhoIsTheSpyBaocaiLi/spy_game/runner.py`；`engine_nodes.py` |
| `hello-claw` | `docs/cn/build/chapter5/index.md`：消息、Session 与 Lane；`chapter6/index.md`：会话键与隔离 | 待 Clone 后展开 |
| `hermes-book` | `part4/ch10-session-db.md`；`part2/ch03-request-journey.md` | SessionDB 与 Run 记录源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part3/ch10.md`：压缩后的文件、Skill、计划和状态恢复；`part4/ch14.md`：状态快照与变化归因 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04i-session-storage-resume.md` | `src/commands/branch/branch.ts`；`src/utils/toolResultStorage.ts` |
| `ai-agent-book` | `book/chapter5.md`：Sessionless 状态、环境恢复和故障终止 | `chapter5/` 配套实验，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch10：认知工作空间、注意力和门控状态 | `code/chapter_10/01_cognitive_workspace.py` |

## 7. 上下文工程、压缩、预算与缓存

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch09：上下文工程；`Extra02-上下文工程补充知识.md`；`Extra09-Agent应用开发实践踩坑与经验分享.md` | 待 Clone 后展开 |
| `learn-claude-code` | `s08_context_compact/README.md` | `s08_context_compact/` 同目录实现；`tests/test_compaction_tool_pairs.py` |
| `Alice_methodology` | `chapters/05-context-memory.md` | 待 Clone 后展开 |
| `claw0` | `sessions/zh/s03_sessions.md`；`s06_intelligence.md` | 待 Clone 后展开 |
| `hermes-book` | `part4/ch12-context-compression.md` | 上下文压缩实现，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part3/ch09.md`：自动压缩；`ch10.md`：恢复；`ch11.md`：微压缩；`ch12.md`：Token 预算；`part4/ch13.md`：Prompt 缓存；`ch14.md`：缓存中断；`ch15.md`：缓存友好装配；`part7/ch26.md`：上下文卫生；`ch28.md`：缓存和压缩失效 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04f-context-management.md`；`analysis/04i-session-storage-resume.md` | `src/utils/toolResultStorage.ts` |
| `ai-agent-book` | `book/chapter2.md`：KV Cache、Skills、压缩、时间和状态提示 | `chapter2/kv-cache/README.md`；`context-compression/README.md`；`system-hint/README.md`；`agent-skills-ppt/README.md` |
| `ai-agents-in-action-2nd-edition-cn` | Ch10：认知工作空间、停滞与知识边界 | `code/chapter_10/01_cognitive_workspace.py` |

## 8. 长期记忆与记忆治理

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s09_memory/README.md` | `s09_memory/` 同目录实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/05-context-memory.md`；`blog/blog-04-memory-system.md` | 待 Clone 后展开 |
| `claw0` | `sessions/zh/s06_intelligence.md` | `workspace/MEMORY.md` 工作区记忆示例 |
| `hermes-book` | `part4/ch11-memory-provider.md` | Memory Provider 源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch24.md`：跨会话记忆、持久学习与作用域 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04-agent-memory.md` | `src/services/extractMemories/extractMemories.ts`；`src/memdir/findRelevantMemories.ts`；`memoryTypes.ts` |
| `hello-agents` | Ch08：记忆与检索 | `code/chapter8/06_Memory_Consolidation_Demo.py`；`09_Memory_Types_Deep_Dive.py`；`08_Agent_Tool_Integration.py` |
| `ai-agent-book` | `book/chapter3.md`：用户记忆与知识库 | `chapter3/user-memory/README.md`；`user-memory-evaluation/README.md`；`mem0/README.md`；`memobase/README.md` |
| `ai-agents-in-action-2nd-edition-cn` | Ch06：语义记忆、关系记忆、混合记忆、压缩与遗忘 | `code/chapter_06/04_hybrid_memory_agent.py` |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch05：Memory-Augmented Agent；Ch17：记忆巩固与未来 Agent | `chapter05/ch05_foundational_architectures.ipynb`；`chapter17/ch17_future_agents.ipynb`；`mock_engine.py`；`resilience.py` |

## 9. RAG、知识检索与结构化知识

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch08：记忆与检索；Ch14：自动化深度研究智能体 | `code/chapter8/04_RAGTool_MarkItDown_Pipeline.py`；`08_Agent_Tool_Integration.py`；`Co-creation-projects/Shawnxyxy-HealthRecordAgent/backend/rag/retriever.py` |
| `easy-langent` | `docs/guide/chapter4.md`：链式工作流与 RAG | `project/AgenticRag/README.md`；`PersonalMemoryAssistant/README.md`；`MedicalRag/README.md` |
| `hello-claw` | `docs/cn/university/knowledge-base/index.md` | 待 Clone 后展开 |
| `ai-agent-book` | `book/chapter3.md`：稀疏/稠密检索、RAG、结构化索引与知识图谱 | `chapter3/retrieval-pipeline/README.md`；`contextual-retrieval/README.md`；`contextual-retrieval-for-user-memory/README.md`；`agentic-rag/README.md`；`agentic-rag-for-user-memory/README.md`；`structured-index/README.md`；`structured-knowledge-extraction/README.md` |
| `ai-agents-in-action-2nd-edition-cn` | Ch06：RAG、混合检索与知识记忆；Ch11：RAG 应用蓝图 | `code/chapter_06/`、`code/chapter_11/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | `chapter06/README.md`：Knowledge Retrieval、Document Intelligence、Scientific Research Agent | `chapter06/ch06_knowledge_agents.ipynb`；`agent_utils.py` |

## 10. Agent 框架、工作流与状态图编排

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `easy-langent` | Ch01：LangChain/LangGraph 边界；Ch03：进阶组件；Ch04：链式工作流；Ch05：综合应用；Ch06：LangGraph 基础；Ch07：LangGraph 进阶；Ch08：图式游戏编排 | `project/DataAgent/backend/src/agent.py`；`project/WhoIsTheSpyBaocaiLi/spy_game/graph_build.py`；`runner.py`；`engine_nodes.py` |
| `hello-agents` | Ch05：低代码平台；Ch06：框架开发实践；Ch07：构建 Agent 框架 | `code/chapter6/Langgraph/Dialogue_System.py`；`AgentScopeDemo/README.md`；`AutoGenDemo/README.md`；`CAMEL/DigitalBookWriting.py` |
| `ai-agent-book` | Ch01：Workflow 与 Harness；Ch05：Agent 应用和生成式界面 | `chapter1/`、`chapter5/` 配套实验，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch04：Agent、Flow 和多 Agent 架构；Ch10：认知架构；Ch11：五层实践蓝图 | `code/chapter_04/`、`chapter_10/`、`chapter_11/`，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part1/ch03.md`：从 Loop 到 Harness | 待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch02：框架工具箱；Ch07：Chain-of-Agents 与 Agentic Workflow | `chapter02/ch02_agent_toolkit.ipynb`；`chapter07/ch07_tool_orchestration.ipynb` |

## 11. 权限、Hooks、安全、沙箱与隐私

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s03_permission/README.md`；`s04_hooks/README.md` | 同章节目录实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/07-permission.md`；`chapters/12-security.md` | 待 Clone 后展开 |
| `hermes-book` | `part3/ch07-tool-profiles.md`；`part5/ch16-terminal-backends.md` | 工具审批与执行环境抽象，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part5/ch16.md`：权限系统；`ch17.md`：YOLO 分类器；`ch17b.md`：提示注入防御；`ch18.md`：Hooks；`ch18b.md`：多平台沙箱；`ch19.md`：用户指令覆盖 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/02-security-analysis.md`；`02-user-data-and-usage.md`；`03-privacy-avoidance.md`；`04e-sandbox-implementation.md`；`06-extra-findings.md` | 由 `analysis/07-code-evidence-index.md` 反查 Sandbox、权限和隐私源码 |
| `hello-claw` | `docs/cn/adopt/chapter10/index.md`：威胁模型；`build/chapter7/index.md`：入口信任边界；`build/chapter9/index.md`：WASM/Docker 沙箱；`university/security/index.md` | 待 Clone 后展开 |
| `hello-agents` | Ch09 与 Extra09 中的上下文注入、工具和工程安全 | 待 Clone 后展开 |
| `ai-agent-book` | Ch05：Coding Agent 执行安全、环境隔离与故障恢复 | `chapter5/` 配套实验，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch04：Agent Flow Guardrails；Ch07：Grounding 与 Critic Guardrails | `code/chapter_04/`、`code/chapter_07/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch04：零信任、注入防御与合规；Ch09：Security-Hardened Agent | `chapter04/ch04_agent_deployment.ipynb`；`agent_utils.py`；`chapter09/ch09_software_dev_agents.ipynb`；`compliance_engine.py`；`state_models.py` |

## 12. Skills 与插件系统

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s07_skill_loading/README.md` | `skills/agent-builder/SKILL.md`；`s07_skill_loading/` 同目录实现 |
| `Alice_methodology` | `chapters/09-skills.md`；Ch10 的可进化 Skill | 待 Clone 后展开 |
| `claw0` | `sessions/zh/s06_intelligence.md`：Skill 发现 | `workspace/skills/example-skill/SKILL.md` |
| `hermes-book` | `part3/ch08-skill-system.md` | Skill System 源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch22.md`：技能系统；`ch22b.md`：插件系统；`part5/ch19.md`：指令作用域 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04c-skills-implementation.md` | 由源码证据索引反查 Skills 实现 |
| `hello-claw` | `docs/cn/build/skill-practice/index.md`；`appendix/appendix-d.md`：技能开发、发布和插件生命周期 | 待 Clone 后展开 |
| `hello-agents` | `Extra05-AgentSkills解读.md`；`Extra08-如何写出好的Skill.md` | 待 Clone 后展开 |
| `easy-langent` | `docs/tmp/chapter9.md`：Skills 与动态工具暴露 | 待 Clone 后展开 |
| `ai-agent-book` | Ch02：Agent Skills 与渐进式披露 | `chapter2/agent-skills-ppt/README.md` |

## 13. MCP、A2A、ANP 与协议互操作

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s14_mcp_plugin/README.md` | `s14_mcp_plugin/` 同目录实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/08-mcp.md` | 待 Clone 后展开 |
| `hermes-book` | `part5/ch14-gateway.md` 中的协议适配层 | 待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch20.md` 中的 MCP 就绪检查 | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04d-mcp-implementation.md` | 由源码证据索引反查 MCP 实现 |
| `hello-claw` | `docs/cn/build/chapter8/index.md`：轻量 Agent 的 MCP 取舍 | 待 Clone 后展开 |
| `hello-agents` | Ch10：MCP、A2A 与 ANP | `code/chapter10/report.md`；其余协议示例待 Clone 后展开 |
| `easy-langent` | `project/MCPChat/README.md` | MCPChat 项目目录，待 Clone 后展开 |
| `ai-agent-book` | Ch04：MCP 与协作工具 | `chapter4/` 配套实验，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch03：MCP Server、传输、工具封装和 Client 消费 | `code/chapter_03/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch01 的 MCP/A2A 与 Agent 能力级别 | `chapter01/ch01_foundations_of_agent_engineering.ipynb` |

## 14. 多 Agent、委托、任务与团队协作

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s05_todo_write`；`s06_subagent`；`s10_task_system`；`s13_agent_teams`（合并旧版 teams/protocols/autonomous/worktree 四章）；`s16_workflow_runtime` | 各章节同目录实现，待 Clone 后展开 |
| `Alice_methodology` | `chapters/06-multi-agent.md`；`blog/blog-05-multi-agent.md` | 待 Clone 后展开 |
| `hermes-book` | `part3/ch09-delegation.md` | 子代理与委托源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch20.md`：Agent 派生与编排；`ch20b.md`：Teams 与多进程；`ch20c.md`：远程多 Agent | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/04h-multi-agent.md` | 由源码证据索引反查 Multi-Agent 实现 |
| `easy-langent` | Ch07：LangGraph 多智能体、人工中断和循环优化 | 多 Agent 示例待 Clone 后展开 |
| `hello-agents` | Ch06：框架开发中的多 Agent；Ch14：Deep Research 协作 | `code/chapter6/AgentScopeDemo/`、`AutoGenDemo/`、`CAMEL/` |
| `hello-claw` | `docs/cn/university/one-person-company/index.md` | 待 Clone 后展开 |
| `claw0` | `s05_gateway_routing.md`：多 Agent 路由；`s10_concurrency.md`：隔离 Lane | `s05_gateway_routing.py`；`s10_concurrency.py` |
| `ai-agent-book` | Ch10：上下文共享、多 Agent 拓扑、虚拟文件系统和 Agent Society | `chapter10/README.md` 及配套实验 |
| `ai-agents-in-action-2nd-edition-cn` | Ch04：多 Agent 控制、通信、协调和 Handoff；Ch07：评估器治理 | `code/chapter_04/`、`code/chapter_07/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch07：Chain-of-Agents；Ch14：Supervisor 与合规协作；Ch15：Collective Intelligence | `chapter07/ch07_tool_orchestration.ipynb`；`chapter14/ch14_financial_legal_agents.ipynb`；`chapter15/ch15_education_and_knowledge_agents.ipynb` |

## 15. Channel、Gateway、身份与路由

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `claw0` | `sessions/zh/s03_sessions.md`；`s04_channels.md`；`s05_gateway_routing.md` | `s04_channels.py`；`s05_gateway_routing.py` |
| `hermes-book` | `part5/ch13-cli-tui.md`；`part5/ch14-gateway.md`；`part2/ch03-request-journey.md` | CLI/TUI、Gateway 与请求路由源码，待 Clone 后展开 |
| `hello-claw` | `build/chapter1/index.md`：统一消息循环；`build/chapter6/index.md`：统一网关；`build/chapter7/index.md`：入口信任边界；`appendix/appendix-g.md`：dmScope、identityLinks 与 bindings | 待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part5/ch16-terminal-backends.md`：本地、Docker、SSH 与云端执行入口 | 待 Clone 后展开 |

## 16. 后台任务、Heartbeat、Cron 与可靠投递

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s11_background_tasks/README.md`；`s12_cron_scheduler/README.md` | 同章节目录实现，待 Clone 后展开 |
| `claw0` | `s07_heartbeat_cron.md`；`s08_delivery.md` | `s08_delivery.py`；Heartbeat/Cron 配套实现待 Clone 后展开 |
| `hermes-book` | `part5/ch15-cron.md` | Cron 调度源码，待 Clone 后展开 |
| `hello-claw` | `build/chapter1/index.md`：heartbeat 与分层容错；`build/chapter5/index.md`：消息循环 | 待 Clone 后展开 |
| `ai-agent-book` | Ch04：事件驱动与异步 Agent | `chapter4/` 配套实验，待 Clone 后展开 |

## 17. 并发、生命周期、错误恢复与运行时韧性

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | `s16_workflow_runtime/README.md`：schema 校验重试、journal 与 resume 断点恢复；`s17_goal_loop/README.md`：评估失败处理 | `s16_workflow_runtime/`；`s17_goal_loop/` 同目录实现（旧版 s11_error_recovery 已并入新版各章），待 Clone 后展开 |
| `claw0` | `s09_resilience.md`；`s10_concurrency.md` | `s10_concurrency.py`；恢复实现待 Clone 后展开 |
| `hermes-book` | `part6/ch19-concurrency.md`；`ch20-lifecycle.md`；`ch21-runtime-defense.md`；`ch22-testing.md` | 并发、生命周期和运行时防御源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part1/ch04.md`；`part6/ch20c.md`；`part7/ch26.md`；`ch28.md` | 待 Clone 后展开 |
| `ai-agent-book` | Ch05：故障检测、恢复与终止 | `chapter5/` 配套实验，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch04：熔断与部署韧性；Ch05、Ch15-Ch17 的 resilience 模块 | `chapter04/ch04_agent_deployment.ipynb`；`chapter05/resilience.py`；`chapter15/resilience.py`；`chapter16/resilience.py`；`chapter17/resilience.py` |

## 18. 长任务、自治运行与跨运行 Loop

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | s10 Task System；s11 Background Tasks；s12 Cron；s13 Agent Teams；s16 Workflow Runtime；s17 Goal Loop | 各章节同目录实现，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch20c.md`：远程多 Agent 状态机；`part7/ch26.md`：循环熔断和上下文恢复 | 待 Clone 后展开 |
| `hermes-book` | Ch12 Context Compression；Ch19 Concurrency；Ch20 Lifecycle；Ch21 Runtime Defense；Ch22 Testing | 待 Clone 后展开 |
| `hello-agents` | Ch09 上下文工程；Ch12 性能评估；Extra10 Agent 自进化 | 待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch09：内部循环、Task Loop、Meta Loop、终止门和研究状态；Ch10：停滞与知识边界 | `code/chapter_09/`；`code/chapter_10/01_cognitive_workspace.py` |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch05：自主决策与计划；Ch13：科学实验反馈 Loop | `chapter05/ch05_foundational_architectures.ipynb`；`chapter13/ch13_healthcare_scientific_agents.ipynb` |

## 19. 多模态、实时交互、GUI 与 Web Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | `Extra06-GUIAgent科普与实战.md`；`Extra11-WebAgent科普与实战.md` | 待 Clone 后展开 |
| `ai-agent-book` | Ch09：语音三范式、实时交互、Computer Use 与机器人 | `chapter9/live-audio/README.md`；`streaming-speech/README.md`；`end-to-end-speech/README.md`；`phone-agent/README.md`；`controllable-tts/README.md` |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch11：Vision-Language、Audio Processing 与 Physical World Sensing Agent | `chapter11/ch11_multimodal_agents.ipynb`；`agent_logger.py`；`mock_backends.py` |

## 20. 测试、评测、验证与基准

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hermes-book` | `part6/ch22-testing.md` | 测试体系源码，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part7/ch25.md`：Harness 工程原则；`ch27.md`：生产模式；`ch29.md`：可观测性；`appendix/f-e2e-traces.md` | 待 Clone 后展开 |
| `hello-agents` | Ch11 的模型评估；Ch12：BFCL、GAIA、数据生成与性能评估；Extra09：工程踩坑 | 待 Clone 后展开 |
| `ai-agent-book` | Ch06：评测环境、模型与 Harness 联合评估、指标、榜单和成本 | `chapter6/README.md` 及配套实验 |
| `ai-agents-in-action-2nd-edition-cn` | Ch07：TDAD、Grounding、Critic、Phoenix 与 Annotation；Ch10：置信门、停滞与知识边界 | `code/chapter_07/`、`code/chapter_10/`，待 Clone 后展开 |
| `easy-langent` | Ch07：流程重试、人工中断与循环优化 | 待 Clone 后展开 |
| `claw0` | Ch09 Resilience；Ch10 Concurrency | 对应最小实现，待 Clone 后展开 |
| `claude-code-analysis` | `analysis/02-user-data-and-usage.md`；`06b-negative-keyword-analysis.md`；`07-code-evidence-index.md` | 源码证据索引本身用于验证分析结论 |
| `hello-claw` | `adopt/lobster-review.md`；`university/ci-cd-assistant/index.md` | 待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch08：Verification and Validation Agent；Ch12：公平性监测和解释校准 | `chapter08/ch08_data_analysis_reasoning_agents.ipynb`；`config.py`；`mock_llm.py`；`utils.py`；`chapter12/ch12_01_ethical_reasoning_agent.ipynb`；`ch12_02_explainable_agent.ipynb` |

## 21. 部署、可观测性与生产迭代

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `Alice_methodology` | `chapters/13-observability.md`；`chapters/15-engineering-patterns.md`；`blog/blog-06-co-building.md`；`blog/blog-07-rapid-release.md` | 待 Clone 后展开 |
| `hermes-book` | Ch17 Config/Profiles；Ch18 Model Abstraction；Ch20 Lifecycle；Ch21 Runtime Defense | 待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | Ch25 Harness 原则；Ch27 生产模式；Ch28 失效模式；Ch29 可观测性；附录 E2E Trace | 待 Clone 后展开 |
| `claude-code-analysis` | `analysis/02-user-data-and-usage.md`；`03-privacy-avoidance.md`；`05-differentiators-and-comparison.md`；`08-competitive-comparison.md` | 待 Clone 后展开 |
| `hello-agents` | Extra09：Agent 应用开发实践踩坑与经验 | 待 Clone 后展开 |
| `ai-agent-book` | Ch06：成本、评测环境与运行指标 | `chapter6/README.md` 及配套实验 |
| `ai-agents-in-action-2nd-edition-cn` | Ch07：Trace、实验与反馈；Ch08：Web/API/Docker 部署和生产治理 | `code/chapter_07/`；`code/chapter_08/`，待 Clone 后核验 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch04：Deployment、成本、熔断、零信任和公平审计 | `chapter04/ch04_agent_deployment.ipynb`；`agent_utils.py`；`mock_llm.py` |

## 22. 后训练、经验学习与 Agent 自进化

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `Alice_methodology` | `chapters/10-self-evolution.md` | 待 Clone 后展开 |
| `hello-agents` | Ch11：Agentic RL；Extra10：Agent 自进化；Ch12：评估门禁 | 待 Clone 后展开 |
| `ai-agent-book` | Ch07：预训练、SFT、RL 与工具调用内化；Ch08：经验学习、Prompt/工具自改进、工作流编译和自进化评估 | `chapter8/gaia-experience/README.md`；`self-evolution-eval/README.md`；`chapter7/` 其他训练实验待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch07：评估反馈与 Annotation | `code/chapter_07/`，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | Ch24：持久学习；Ch25、Ch27、Ch29：受评测和观测约束的改进 | 待 Clone 后展开 |
| `learn-claude-code` | s07 Skill Loading；s10 Task System | 同章节实现，待 Clone 后展开 |
| `claude-code-analysis` | Agent Memory、Skills 和用户反馈分析章节 | 记忆提取与 Skill 源码入口见前述知识点 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch09：Self-Improving Agent；Ch17：自构架、伦理漂移和记忆巩固 | `chapter09/ch09_software_dev_agents.ipynb`；`self_improving.py`；`agent_nodes.py`；`chapter17/ch17_future_agents.ipynb`；`mock_engine.py` |

## 23. Coding Agent 与软件开发 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `learn-claude-code` | README 与 s01-s17 组成的 Claude Code 式 Harness 渐进实现 | 各阶段同目录实现，待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | 全书以 AI Coding Agent 为主线；Ch30：构建代码审查 Agent | `part7/ch30.md` 配套代码，待 Clone 后展开 |
| `claude-code-analysis` | 架构、Tool Call、Context、Sandbox、Skills、MCP、Multi-Agent 等实现分析 | `analysis/07-code-evidence-index.md` 及其中指向的 `src/` 文件 |
| `ai-agent-book` | Ch05：Coding Agent、代码元能力、执行安全、恢复和生成式界面 | `chapter5/` 配套实验，待 Clone 后展开 |
| `hello-claw` | `university/ci-cd-assistant/index.md` | 待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch09：Code-Generation、Security-Hardened、Self-Improving Agent | `chapter09/ch09_software_dev_agents.ipynb`；`agent_nodes.py`；`compliance_engine.py`；`self_improving.py`；`state_models.py`；`mock_llm.py`；`utils.py` |

## 24. 数据分析、通用推理与验证 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `easy-langent` | Ch05 的综合应用和 Data Agent 项目 | `project/DataAgent/backend/src/agent.py` |
| `ai-agents-in-action-2nd-edition-cn` | Ch05 的规划与推理；Ch07 的 Critic 与验证 | `code/chapter_05/`、`code/chapter_07/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch08：Data Analysis、Verification and Validation、General Problem Solver | `chapter08/ch08_data_analysis_reasoning_agents.ipynb`；`color_logger.py`；`config.py`；`mock_llm.py`；`utils.py` |

## 25. 对话、内容创作与推荐 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch06-Ch07 中的对话框架和 Agent 应用 | `code/chapter6/Langgraph/Dialogue_System.py`；`CAMEL/DigitalBookWriting.py` |
| `ai-agents-in-action-2nd-edition-cn` | Ch11：客服与应用蓝图 | `code/chapter_11/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch10：Conversational、Content Creation、Recommendation Agent | `chapter10/ch10_conversational_and_content_creation_agents.ipynb`；`mock_llm.py` |

## 26. Deep Research、旅行助手与综合应用

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch13：智能旅行助手；Ch14：自动化深度研究智能体；Ch15：赛博小镇；Ch16：毕业设计 | 各章配套项目待 Clone 后展开 |
| `easy-langent` | Ch05：智能体应用设计与实现；Ch08：图式游戏编排 | DataAgent、WhoIsTheSpy 等项目入口见前述知识点 |
| `learn-claude-code` | `s15_integrated_harness/README.md`：综合集成 Harness | `s15_integrated_harness/` 同目录实现（旧版 s20_comprehensive 已并入新版 s15），待 Clone 后展开 |
| `claw0` | `README.zh.md`：从零重建常驻 Agent | s01-s10 完整渐进实现 |
| `harness-engineering-from-cc-to-ai-coding` | Ch30：代码审查 Agent | 待 Clone 后展开 |
| `hello-claw` | `adopt/lobster-review.md`；`university/one-person-company/index.md` | 待 Clone 后展开 |
| `ai-agent-book` | Ch05：Coding Agent、动态 UI 与媒体工作流案例 | `chapter5/` 配套项目，待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch09：Deep Research Task Loop；Ch11：客服、RAG 与 Deep Research 蓝图 | `code/chapter_09/`、`code/chapter_11/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch05-Ch16 的 30 类 Agent 架构案例 | `chapter05/` 至 `chapter16/` 的原始 Notebook，按具体领域见后续知识点 |

## 27. 伦理、公平、可解释与高影响决策

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `Alice_methodology` | Ch12：安全治理中的高影响决策边界 | 待 Clone 后展开 |
| `ai-agents-in-action-2nd-edition-cn` | Ch04 的 Guardrails；Ch07 的 Grounding、Critic 与反馈治理 | `code/chapter_04/`、`code/chapter_07/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch04：公平审计；Ch12：Ethical Reasoning 与 Explainable Agent | `chapter12/ch12_01_ethical_reasoning_agent.ipynb`；`ch12_02_explainable_agent.ipynb`；`ethical_core.py`；`explainability_core.py`；`synthetic_data.py`；`mock_llm.py`；`utils.py` |

## 28. 医疗与科学研究 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch14：自动化深度研究；健康记录 Agent 共创项目 | `Co-creation-projects/Shawnxyxy-HealthRecordAgent/backend/rag/retriever.py` |
| `easy-langent` | 医疗 RAG 项目 | `project/MedicalRag/README.md` |
| `ai-agents-in-action-2nd-edition-cn` | Ch11 的 RAG 与研究蓝图 | `code/chapter_11/`，待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch06：Scientific Research Agent；Ch13：Healthcare Intelligence 与 Scientific Discovery Agent | `chapter06/ch06_knowledge_agents.ipynb`；`chapter13/ch13_healthcare_scientific_agents.ipynb` |

## 29. 金融与法律 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch14：Financial Advisory 与 Legal Intelligence Agent | `chapter14/ch14_financial_legal_agents.ipynb`；`mock_data.py`；`mock_llm.py` |

## 30. 教育与集体智能 Agent

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Ch15：赛博小镇中的群体协作；Ch16：毕业设计 | 配套项目待 Clone 后展开 |
| `ai-agent-book` | Ch10：多 Agent、虚拟文件系统和 Agent Society | `chapter10/README.md` 及配套实验 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch15：Education Intelligence 与 Collective Intelligence Agent | `chapter15/ch15_education_and_knowledge_agents.ipynb`；`mock_llm.py`；`resilience.py` |

## 31. 具身智能与物理行动环境

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `hello-agents` | Extra06 GUI Agent；Extra11 Web Agent | 待 Clone 后展开 |
| `hello-claw` | `build/chapter10/index.md`：硬件与部署环境 | 待 Clone 后展开 |
| `ai-agent-book` | Ch09：Computer Use、机器人、VLA 与实时行动 | `chapter9/` 中的交互实验；机器人实验待 Clone 后展开 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch11：Physical World Sensing；Ch16：Embodied Intelligence 与 Domain-Transforming Integration Agent | `chapter11/ch11_multimodal_agents.ipynb`；`chapter16/ch16_embodied_agents.ipynb`；`mock_layer.py`；`resilience.py` |

## 32. Agent Society、未来架构与人机协作

| 来源工程 | 原工程章节 | 对应代码示例 |
| --- | --- | --- |
| `Alice_methodology` | `chapters/16-alive-agent.md`：人格一致性、记忆、子 Agent 和人机交互 | 待 Clone 后展开 |
| `hermes-book` | `part7/ch23-philosophy.md`：长期个人 Agent 的设计哲学 | 待 Clone 后展开 |
| `harness-engineering-from-cc-to-ai-coding` | `part6/ch23.md`：Feature Flag 下的未来能力推测 | 待 Clone 后展开；该章属于推测性材料，需要单独校验 |
| `claude-code-analysis` | `analysis/05-differentiators-and-comparison.md`；`06-extra-findings.md`；`08-competitive-comparison.md` | `analysis/07-code-evidence-index.md`；产品比较结论需按版本复核 |
| `ai-agent-book` | Ch10：Agent Society、共享上下文和虚拟文件系统 | `chapter10/README.md` 及配套实验 |
| `30-Agents-Every-AI-Engineer-Must-Build` | Ch17：自构架、Agent Society、伦理漂移、记忆巩固和人机协作谱 | `chapter17/ch17_future_agents.ipynb`；`mock_engine.py`；`resilience.py` |

## 后续补全规则

每新增或恢复一个来源工程时，按以下顺序维护本目录：

1. 对照该工程目录，补齐所有有知识内容的原始章节。
2. 把章节归入已有知识点；只有无法合理归类时才新增知识点。
3. 展开“待 Clone 后展开”的代码目录，补充具体源码、测试和 Notebook 路径。
4. 同一代码文件服务多个知识点时允许重复引用，不复制代码内容。
5. 记录纯安装、生成输出或重复运行副本的排除原因，但不把它们提升为知识点。
6. 本目录只维护来源章节聚类；教材内容、学习顺序和 Review 状态仍由各自现有文档负责。
