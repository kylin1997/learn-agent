# 30 天主线学习计划

> **版本**：v3.0  
> **制定日期**：2026-08-17  
> **执行周期**：30 天（每日 3~6 小时，核心时间盒 270 分钟）  
> **核心目标**：建立完整的 Agent 知识体系，产出生产级 Agent 项目

## 计划说明

本计划以 **source 工程为主线**，融合教材仅作学后校验对象。

**三大主线**：
- **理论主线**：[`source/hello-agents/`](../source/hello-agents/)（Ch01-16 + Extra，体系最完整，教学递进）
- **工程主线**：[`source/learn-claude-code/`](../source/learn-claude-code/)（**s01-s17 新版主线**，生产级 Harness 渐进构建；`agents/`、`docs/` 为旧 12 章过渡版，不再引用）
- **专题参考**：[`source/ai-agent-book/`](../source/ai-agent-book/)（Ch01-10，上下文工程、记忆、后训练、多模态专题）

**来源分层（A/B/C）与阅读层级**：
- **A 层（精读跟写）**：hello-agents、learn-claude-code、ai-agent-book —— 章节全部进计划，区分**必读（★）**与**扩展（◯）**
- **B 层（源码/架构查阅）**：claude-code-analysis、harness-engineering-from-cc-to-ai-coding、hermes-book、claw0 —— 只在"有必要"的日次加入，标注 📂，每次 15-30 分钟架构查阅，不进精读流程、不占精读时长
- **C 层（定向回源）**：hello-claw、easy-langent、Alice_methodology、ai-agents-in-action-2nd、30-Agents —— 仅定向点位与后续计划

**阅读层级定义**：
- **★ 必读**：走完整"预读→精读跟写→闭卷→实践"流程
- **◯ 扩展**：读章节 README + 直接运行 `code.py`，不安排精读与练习

**每日流程**：参见 [AGENTS.md](../AGENTS.md) 的"每日学习循环"（7 阶段时间盒）。

**进度记录**：每日学习结束后在 [`docs/progress.md`](progress.md) 标记完成状态（✅/⚠️/❌），计划文件本身不再承载进度状态。

**调速规则**：只降速，不跳主题。当日闭卷检查或实践验证不通过时，主题降级为"进行中"，次日继续。

### learn-claude-code 17 章取舍表

> 以根目录 s01-s17 新版主线为准（每章含三语 README + `code.py`），旧 12 章编号不混用。

| 章节 | 层级 | 安排 | 主题 |
|------|------|------|------|
| s01_agent_loop | ★必读 | D3 | 最小 Agent Loop |
| s02_tool_use | ★必读 | D4 | 工具 dispatch map |
| s03_permission | ★必读 | D16 | 权限审批管线 |
| s04_hooks | ★必读 | D17 | Pre/PostToolUse 插口 |
| s05_todo_write | ◯扩展 | D8 | 先计划后执行（与 s10 任务系统互为补充） |
| s06_subagent | ★必读 | D20 | fresh messages[] 子代理 |
| s07_skill_loading | ★必读 | D15/D18 | 技能按需加载 |
| s08_context_compact | ★必读 | D6/D13 | budget-snip-micro-summary 四步压缩 |
| s09_memory | ★必读 | D9 | 记忆三子系统 |
| s10_task_system | ★必读 | D8 | TaskRecord + blockedBy 磁盘持久化任务图 |
| s11_background_tasks | ◯扩展 | D22 | 后台线程 + 通知队列 |
| s12_cron_scheduler | ◯扩展 | D22 | 持久化 cron |
| s13_agent_teams | ★必读 | D20 | 持久队友 + 原子认领 + worktree + 类型协议 |
| s14_mcp_plugin | ★必读 | D19 | MCP 工具发现 + 命名空间 |
| s15_integrated_harness | ★必读 | D26 | 机制归一循环（综合精读） |
| s16_workflow_runtime | ◯扩展 | D26 | 脚本编排 + journal 续跑 |
| s17_goal_loop | ★必读 | D29 | 目标闸门 + 独立判断器 + 自动续轮（收官） |

> 旧版的 teams/protocols/autonomous/worktree 四章已合并入新版 s13，17 章本身无冗余章节，无需排除。

### ai-agent-book 示例运行分层

ai-agent-book 的 chapter1-5、chapter10 下共 40+ 个可运行示例，按以下标准分层：

**P0 必跑（四条同时满足）**：
1. 与当天理论/工程主线主题直接对口
2. 运行成本低：纯 `pip install` + 复用主线 LLM API key，不依赖 docker / 本地模型 / 前端构建 / 大型数据集
3. 自带 quickstart/demo 入口，60-90 分钟内完成"跑通 demo + 读核心代码"（不做深入改造）
4. 跑完能直接回答当天某个核心问题

**P1 选跑**：主题对口但成本较高（完整实验、消融、需额外服务）→ 放每周复盘日（D7/D14/D21/D28）或源码精读日选跑。

**P2 后置**：需要特殊环境（docker、本地 LLM、前端）或偏离 30 天目标 → 列入"后续计划"。

**分层清单**：

| 层级 | 示例 | 安排 |
|------|------|------|
| P0 | chapter1/web-search-agent | D1 |
| P0 | chapter4/active-tool-selection | D4 |
| P0 | chapter2/context-compression | D6 |
| P0 | chapter3/user-memory | D9 |
| P0 | chapter10/parallel-web-research | D20 |
| P0 | chapter1/learning-from-experience | D25 |
| P1 | chapter1/context、chapter1/search-codegen | D7 / D26 |
| P1 | chapter2/kv-cache、chapter2/prompt-engineering（tau_bench 消融） | D13 / D14 |
| P1 | chapter2/agent-skills-ppt | D21（Skills 主题后） |
| P1 | chapter3/retrieval-pipeline、contextual-retrieval、structured-knowledge-extraction、mem0 | D14 |
| P1 | chapter4/active-tool-discovery、execution/perception-tools | D21 |
| P1 | chapter10/book-translation、staged-system-prompt | D28 |
| P2 | chapter2/attention_visualization（Next.js 前端）、local_llm_serving（需 ollama） | 后续计划 |
| P2 | chapter3 其余（agentic-rag、memobase、user-memory-evaluation 等） | 后续计划 |
| P2 | chapter4 collaboration-tools（docker-compose） | 后续计划 |
| P2 | chapter5 全部 12 个业务案例（coding-agent、paper-to-ppt 等） | 后续项目灵感池 |
| P2 | chapter10/voice-werewolf、multi-role-transfer | 后续计划 |

> ch06-ch09 无配套代码示例，不影响分层。

---

## W1: Agent 内核（D1-7）

**周目标**：理解 Agent 核心概念、Agent Loop 机制和工具调用原理，能独立实现最小 Agent。

### D1: Agent 基础与系统架构

**主线学习**：
- 📖 理论：[hello-agents Ch01-02](../source/hello-agents/docs/chapter1/)（初识智能体、发展史）
- 🔧 工程：[learn-claude-code README-zh](../source/learn-claude-code/README-zh.md)（Harness 渐进构建总览 + 七阶段学习路径）
- 📚 专题：[ai-agent-book Ch01](../source/ai-agent-book/book/chapter1.md)（AI Agent 入门，快速浏览作补充）

**核心问题**：
- Agent、Chatbot、Workflow 的边界是什么？
- Harness 在 Agent 系统中扮演什么角色？

**实践产出物**：
- 画出 Agent 系统架构图（模型、工具、环境、控制流）
- 列出 hello-agents 的章节结构，理解教学递进逻辑

**示例运行（P0）**：[ai-agent-book chapter1/web-search-agent](../source/ai-agent-book/chapter1/web-search-agent/)，跑通 quickstart，读 [`agent.py`](../source/ai-agent-book/chapter1/web-search-agent/agent.py) 核心逻辑（60-90 分钟）

**验收标准**：能解释 Agent 的核心特征（自主性、工具使用、环境交互）

**校验对象**：[ch01-agent-and-harness.md](merged-agent-course/ch01-agent-and-harness.md)

---

### D2: LLM 基础与模型行为

**主线学习**：
- 📖 理论：[hello-agents Ch03](../source/hello-agents/docs/chapter3/)（大语言模型基础）
- 🔧 工程：无（今日专注理论）

**核心问题**：
- 模型的概率生成特性会给执行系统带来哪些风险？
- 温度、top_p 等参数如何影响输出？

**实践产出物**：
- 实现一个最小 LLM 调用封装（含重试、超时、错误处理）
- 实验不同参数对输出的影响

**验收标准**：能解释模型的概率生成特性对 Agent 系统的影响

**校验对象**：[ch02-llm-foundations-model-behavior.md](merged-agent-course/ch02-llm-foundations-model-behavior.md)

---

### D3: Agent Loop 与推理范式

**主线学习**：
- 📖 理论：[hello-agents Ch04](../source/hello-agents/docs/chapter4/)（经典范式：ReAct、Plan、Reflection）
- 🔧 工程：[learn-claude-code s01_agent_loop ★](../source/learn-claude-code/s01_agent_loop/)（最小 Agent Loop）

**核心问题**：
- Agent Loop 如何连接模型、工具、环境反馈和停止判断？
- ReAct、Plan、Reflection 分别改变哪一层控制逻辑？

**实践产出物**：
- 直接运行 `python s01_agent_loop/code.py` 验证行为
- 实现最小 Agent Loop（参考 s01，输入→推理→工具调用→观察→循环）
- 实现 ReAct 模式（Reasoning + Acting）

**验收标准**：能画出一次任务的完整执行路径，能解释 Loop 的停止条件

**校验对象**：[ch03-agent-loop-paradigms-tools.md](merged-agent-course/ch03-agent-loop-paradigms-tools.md)

---

### D4: 工具调用与工具运行时

**主线学习**：
- 📖 理论：[hello-agents Ch07](../source/hello-agents/docs/chapter7/)（构建 Agent 框架 - 工具模块）
- 🔧 工程：[learn-claude-code s02_tool_use ★](../source/learn-claude-code/s02_tool_use/)（工具 dispatch map）
- 📚 专题：[ai-agent-book Ch04](../source/ai-agent-book/book/chapter4.md)（工具专题）
- 📂 B 层（可选，30min）：[claude-code-analysis 04b-tool-call-implementation](../source/claude-code-analysis/analysis/04b-tool-call-implementation.md)，真实 CC 的 Tool Call 源码分析对照

**核心问题**：
- 工具注册、参数校验、错误返回如何实现？
- 工具调用失败时如何可控退出？

**示例运行（P0）**：[ai-agent-book chapter4/active-tool-selection](../source/ai-agent-book/chapter4/active-tool-selection/)，跑通 demo，读核心代码（60-90 分钟）

**实践产出物**：
- 直接运行 `python s02_tool_use/code.py`
- 实现声明式工具注册表（参考 s02）
- 实现工具参数校验和错误返回

**验收标准**：工具调用失败时能可控退出，不陷入死循环

**校验对象**：[ch03-agent-loop-paradigms-tools.md](merged-agent-course/ch03-agent-loop-paradigms-tools.md)（工具部分）

---

### D5: Prompt 工程与行为控制

**主线学习**：
- 📖 理论：[hello-agents Ch03-04](../source/hello-agents/docs/chapter3/)（Prompt 基础、范式提示）
- 🔧 工程：无（今日专注理论，Prompt 实践融入 D3-D4 的 Agent Loop 实现）
- 📂 B 层（可选，30min）：[harness-engineering part2/ch05](../source/harness-engineering-from-cc-to-ai-coding/part2/ch05.md)（系统提示架构）

**核心问题**：
- Prompt 如何把任务、约束、工具和输出要求表达为可测试的行为契约？
- System Prompt 的设计原则是什么？

**实践产出物**：
- 设计一个 Agent 的 System Prompt（含角色、约束、工具描述）
- 实现 Prompt 模板化（变量替换、条件注入）

**验收标准**：能解释 Prompt 如何影响 Agent 行为，能调试 Prompt 问题

**校验对象**：[ch04-prompt-engineering.md](merged-agent-course/ch04-prompt-engineering.md)

---

### D6: 上下文工程基础

**主线学习**：
- 📖 理论：[hello-agents Ch09](../source/hello-agents/docs/chapter9/)（上下文工程）
- 🔧 工程：[learn-claude-code s08_context_compact ★](../source/learn-claude-code/s08_context_compact/)（budget-snip-micro-summary 四步压缩）
- 📚 专题：[ai-agent-book Ch02](../source/ai-agent-book/book/chapter2.md)（上下文工程专题）

**核心问题**：
- 上下文窗口的预算如何分配？
- 上下文压缩的策略有哪些？

**示例运行（P0）**：[ai-agent-book chapter2/context-compression](../source/ai-agent-book/chapter2/context-compression/)，跑通 quickstart.py，读 compression_strategies.py 核心逻辑（60-90 分钟）

**实践产出物**：
- 直接运行 `python s08_context_compact/code.py`
- 实现 Context Builder（按需装配上下文）
- 实现简单的上下文压缩（摘要式或滑动窗口）

**验收标准**：能解释每条上下文的选择和丢弃原因

**校验对象**：[ch06-session-state-context-engineering.md](merged-agent-course/ch06-session-state-context-engineering.md)（上下文部分）

---

### D7: W1 复盘与补漏

**任务**：
- 复盘 W1 所有主题，在 [`docs/progress.md`](progress.md) 标记"已掌握/进行中/未掌握"
- 补学"进行中"和"未掌握"的主题
- 整理 W1 学习笔记和代码
- P1 选跑：[chapter1/context](../source/ai-agent-book/chapter1/context/)

**验收标准**：W1 所有主题达到"已掌握"或明确的后续计划

---

## W2: 信息运行时（D8-14）

**周目标**：理解会话状态、任务系统、记忆系统、RAG 和模型运行时的设计与实现。

### D8: 会话与任务状态

**主线学习**：
- 📖 理论：[hello-agents Ch09](../source/hello-agents/docs/chapter9/)（会话管理部分）
- 🔧 工程：[learn-claude-code s10_task_system ★](../source/learn-claude-code/s10_task_system/)（TaskRecord + blockedBy 磁盘持久化任务图）
- 🔧 扩展：[learn-claude-code s05_todo_write ◯](../source/learn-claude-code/s05_todo_write/)（先计划后执行，读 README + 跑 code.py 即可）

**核心问题**：
- 会话记录、执行状态如何保存？
- Agent 重启后如何恢复任务？任务间依赖（blockedBy）如何表达？

**实践产出物**：
- 直接运行 `python s10_task_system/code.py` 和 `python s05_todo_write/code.py`
- 实现会话记录（追加式事件日志）
- 实现状态归约（从事件流重建状态）

**验收标准**：Agent 重启后能恢复任务状态

**校验对象**：[ch06-session-state-context-engineering.md](merged-agent-course/ch06-session-state-context-engineering.md)（会话部分）

---

### D9: 长期记忆系统

**主线学习**：
- 📖 理论：[hello-agents Ch08](../source/hello-agents/docs/chapter8/)（记忆与检索 - 记忆部分）
- 🔧 工程：[learn-claude-code s09_memory ★](../source/learn-claude-code/s09_memory/)（记忆三子系统）
- 📚 专题：[ai-agent-book Ch03](../source/ai-agent-book/book/chapter3.md)（记忆专题）

**核心问题**：
- 记忆的存储结构如何设计（含元数据）？
- 记忆检索的策略有哪些？

**示例运行（P0）**：[ai-agent-book chapter3/user-memory](../source/ai-agent-book/chapter3/user-memory/)，跑通示例，读核心代码（60-90 分钟）

**实践产出物**：
- 直接运行 `python s09_memory/code.py`
- 实现记忆存储（含来源、作用域、时间戳）
- 实现记忆检索（语义检索或关键词检索）

**验收标准**：每条记忆可追溯来源和更新时间

**校验对象**：[ch07-memory-knowledge-systems.md](merged-agent-course/ch07-memory-knowledge-systems.md)（记忆部分）

---

### D10: RAG 与知识检索

**主线学习**：
- 📖 理论：[hello-agents Ch08](../source/hello-agents/docs/chapter8/)（记忆与检索 - RAG 部分）
- 🔧 工程：无（今日专注理论）
- 📚 专题：[ai-agent-book Ch03](../source/ai-agent-book/book/chapter3.md)（检索专题）

**核心问题**：
- 文档切分和向量化策略是什么？
- 检索-重排-生成的流程如何实现？

**实践产出物**：
- 实现文档切分和向量化
- 实现检索-重排-生成流程

**验收标准**：能解释检索结果的相关性，能调优检索参数

**校验对象**：[ch07-memory-knowledge-systems.md](merged-agent-course/ch07-memory-knowledge-systems.md)（RAG 部分）

---

### D11: 记忆与知识的边界

**主线学习**：
- 📖 理论：[hello-agents Ch08](../source/hello-agents/docs/chapter8/)（记忆治理）
- 🔧 工程：无（今日专注理论）
- 📚 专题：[ai-agent-book Ch03](../source/ai-agent-book/book/chapter3.md)（记忆 vs 知识）

**核心问题**：
- 为什么记忆和知识不能混成一个无边界向量库？
- 如何设计分离存储、统一检索的架构？

**实践产出物**：
- 设计记忆与知识的分离存储方案
- 实现统一的检索接口

**验收标准**：能解释记忆和知识的边界和共享机制

**校验对象**：[ch07-memory-knowledge-systems.md](merged-agent-course/ch07-memory-knowledge-systems.md)（治理部分）

### D12: 模型路由与调用可靠性

**主线学习**：
- 📖 理论：[hello-agents Ch03](../source/hello-agents/docs/chapter3/)（模型调用基础回顾）
- 📂 B 层（主材料，约 60min）：[hermes-book part6/ch17-config-profiles、ch18-model-abstraction](../source/hermes-book/part6/ch17-config-profiles.md)（Provider 兼容层、配置与成本追踪）
- 📚 专题：[ai-agent-book Ch02](../source/ai-agent-book/book/chapter2.md)（模型调用部分）

**核心问题**：
- 模型选择、重试、降级的策略是什么？
- 如何实现 Provider Router？

**实践产出物**：
- 实现 Provider Router（支持多模型切换）
- 实现重试、降级、熔断机制

**验收标准**：模型调用失败时有明确的降级策略

**校验对象**：[ch05-model-runtime-routing-reliability.md](merged-agent-course/ch05-model-runtime-routing-reliability.md)

---

### D13: 上下文压缩与缓存

**主线学习**：
- 📖 理论：[hello-agents Ch09](../source/hello-agents/docs/chapter9/)（上下文压缩深入）
- 🔧 工程：[learn-claude-code s08_context_compact ★](../source/learn-claude-code/s08_context_compact/)（四步压缩实现精读）
- 📚 专题：[ai-agent-book Ch02](../source/ai-agent-book/book/chapter2.md)（KV Cache、压缩专题）

**核心问题**：
- 压缩后如何保证关键信息不丢失？
- Prompt 缓存（KV Cache）如何复用？

**实践产出物**：
- 优化上下文压缩（保留关键信息）
- 实现 Prompt 缓存机制
- P1 选跑：[chapter2/kv-cache](../source/ai-agent-book/chapter2/kv-cache/)

**验收标准**：压缩后关键信息不丢失，缓存命中率可测量

**校验对象**：[ch06-session-state-context-engineering.md](merged-agent-course/ch06-session-state-context-engineering.md)（压缩部分）

---

### D14: W2 复盘与补漏

**任务**：同 D7（P1 选跑：kv-cache 消融、prompt-engineering、chapter3 检索系列）

---

## W3: 架构治理（D15-21）

**周目标**：理解 Agent 框架、权限安全、协议互操作和多 Agent 协作。

### D15: Agent 框架与状态图编排

**主线学习**：
- 📖 理论：[hello-agents Ch05-06](../source/hello-agents/docs/chapter5/)（低代码平台、框架开发）
- 🔧 工程：[learn-claude-code s07_skill_loading ★](../source/learn-claude-code/s07_skill_loading/)（框架能力：技能按需加载）
- 📂 C 层（可选）：[easy-langent](../source/easy-langent/docs/guide/chapter1.md)（LangChain/LangGraph 边界，轻量框架对照）

**核心问题**：
- 什么时候使用框架，什么时候保留直接实现？
- LangGraph 等状态图框架的核心概念是什么？

**实践产出物**：
- 直接运行 `python s07_skill_loading/code.py`
- 用 LangGraph 或等价框架实现一个状态图 Agent
- 对比框架 vs 手写 Loop 的优劣

**验收标准**：能解释什么时候用框架，什么时候保留直接实现

**校验对象**：[ch08-agent-frameworks-orchestration.md](merged-agent-course/ch08-agent-frameworks-orchestration.md)

---

### D16: 权限与安全基础

**主线学习**：
- 📖 理论：无（今日专注工程）
- 🔧 工程：[learn-claude-code s03_permission ★](../source/learn-claude-code/s03_permission/)（权限审批管线）
- 📂 B 层（可选，30min）：[claude-code-analysis 02-security-analysis](../source/claude-code-analysis/analysis/02-security-analysis.md)（真实 CC 权限与沙箱对照）

**核心问题**：
- 权限判断应该位于工具执行链的什么位置？
- 权限结果模型如何设计？

**实践产出物**：
- 直接运行 `python s03_permission/code.py`
- 实现权限结果模型（允许/拒绝/需审批）
- 实现审批门（用户确认后执行）

**验收标准**：权限判断位于工具执行链的正确位置

**校验对象**：[ch09-security-permission-sandbox-privacy.md](merged-agent-course/ch09-security-permission-sandbox-privacy.md)（权限部分）

---

### D17: Hooks 与扩展机制

**主线学习**：
- 📖 理论：无（今日专注工程）
- 🔧 工程：[learn-claude-code s04_hooks ★](../source/learn-claude-code/s04_hooks/)（Pre/PostToolUse 插口）

**核心问题**：
- Hooks 如何在不修改核心逻辑的情况下扩展功能？
- Hooks 的执行顺序和优先级如何设计？

**实践产出物**：
- 直接运行 `python s04_hooks/code.py`
- 实现 Hooks 系统（前置/后置 Hook）
- 实现至少 2 个自定义 Hook

**验收标准**：能通过 Hooks 扩展 Agent 行为

**校验对象**：[ch09-security-permission-sandbox-privacy.md](merged-agent-course/ch09-security-permission-sandbox-privacy.md)（Hooks 部分）

### D18: Skills 与插件系统

**主线学习**：
- 📖 理论：[hello-agents Extra05、Extra08](../source/hello-agents/docs/)（Skills 解读、如何写出好的 Skill）
- 🔧 工程：[learn-claude-code s07_skill_loading ★](../source/learn-claude-code/s07_skill_loading/)（Skill 发现与加载深入）
- 📂 B 层（可选，30min）：[claude-code-analysis 04c-skills-implementation](../source/claude-code-analysis/analysis/04c-skills-implementation.md)

**核心问题**：
- Tool vs Skill vs Plugin 的边界是什么？
- Skill 发现和加载机制如何实现？

**实践产出物**：
- 实现一个标准 Skill（含 SKILL.md 和执行逻辑）
- 实现 Skill 发现和加载机制

**验收标准**：能解释 Tool vs Skill vs Plugin 的边界

**校验对象**：[ch10-skills-plugins.md](merged-agent-course/ch10-skills-plugins.md)

---

### D19: MCP 与协议互操作

**主线学习**：
- 📖 理论：[hello-agents Ch10](../source/hello-agents/docs/chapter10/)（智能体通信协议）
- 🔧 工程：[learn-claude-code s14_mcp_plugin ★](../source/learn-claude-code/s14_mcp_plugin/)（MCP 工具发现 + 命名空间）
- 📂 B 层（可选，30min）：[claude-code-analysis 04d-mcp-implementation](../source/claude-code-analysis/analysis/04d-mcp-implementation.md)

**核心问题**：
- MCP 的传输层和工具封装机制是什么？
- MCP Server 和 Client 如何实现？

**实践产出物**：
- 直接运行 `python s14_mcp_plugin/code.py`
- 实现一个 MCP Server（暴露工具）
- 实现一个 MCP Client（消费工具）

**验收标准**：能解释 MCP 的传输层和工具封装机制

**校验对象**：[ch11-agent-interoperability.md](merged-agent-course/ch11-agent-interoperability.md)

---

### D20: 多 Agent 与任务协作

**主线学习**：
- 📖 理论：[hello-agents Ch06](../source/hello-agents/docs/chapter6/)（框架开发中的多 Agent）
- 🔧 工程：[learn-claude-code s06_subagent ★](../source/learn-claude-code/s06_subagent/)（fresh messages[] 子代理）、[s13_agent_teams ★](../source/learn-claude-code/s13_agent_teams/)（持久队友 + 原子认领 + worktree + 类型协议）
- 📚 专题：[ai-agent-book Ch10](../source/ai-agent-book/book/chapter10.md)（多 Agent 专题）
- 📖 扩展：[hello-agents Ch15 ◯](../source/hello-agents/docs/chapter15/)（赛博小镇，浏览多 Agent 应用形态即可）

**核心问题**：
- 多 Agent 拓扑的选型依据是什么？
- 子 Agent 派生和任务委托如何实现？

**示例运行（P0）**：[ai-agent-book chapter10/parallel-web-research](../source/ai-agent-book/chapter10/parallel-web-research/)，跑通并行研究 demo，读核心代码（60-90 分钟）

**实践产出物**：
- 直接运行 `python s06_subagent/code.py` 和 `python s13_agent_teams/code.py`
- 实现子 Agent 派生（主 Agent 委托任务给子 Agent）
- 实现多 Agent 通信协议

**验收标准**：能解释多 Agent 拓扑的选型依据

**校验对象**：[ch16-multi-agent-task-team.md](merged-agent-course/ch16-multi-agent-task-team.md)

---

### D21: W3 复盘与补漏

**任务**：同 D7（P1 选跑：agent-skills-ppt、active-tool-discovery、execution/perception-tools）

---

## W4: 常驻化与生产化（D22-28）

**周目标**：理解后台任务、测试评测、生产部署和源码精读。

### D22: 后台任务与定时调度

**主线学习**：
- 📖 理论：无（今日专注工程）
- 🔧 扩展：[learn-claude-code s11_background_tasks ◯](../source/learn-claude-code/s11_background_tasks/)、[s12_cron_scheduler ◯](../source/learn-claude-code/s12_cron_scheduler/)（读 README + 跑 code.py）
- 📂 B 层（30min）：[claw0 README.zh](../source/claw0/README.zh.md)（常驻式 harness：心跳 + cron + IM 通道 + delivery 架构）

**核心问题**：
- 后台任务队列如何实现？
- Cron 调度器如何设计？常驻式 Agent 与请求式 Agent 的架构差异？

**实践产出物**：
- 直接运行 `python s11_background_tasks/code.py` 和 `python s12_cron_scheduler/code.py`
- 实现后台任务队列（异步执行）
- 实现 Cron 调度器（定时触发任务）

**验收标准**：任务失败时有重试和告警机制

**校验对象**：[ch14-background-cron-delivery-resilience.md](merged-agent-course/ch14-background-cron-delivery-resilience.md)、[ch13-gateway-channel-identity-routing.md](merged-agent-course/ch13-gateway-channel-identity-routing.md)（通道与路由部分）

---

### D23: 测试与评测

**主线学习**：
- 📖 理论：[hello-agents Ch11-12](../source/hello-agents/docs/chapter11/)（Agentic RL、性能评估）
- 🔧 工程：无（今日专注理论）
- 📚 专题：[ai-agent-book Ch06](../source/ai-agent-book/book/chapter6.md)（评测专题）
- 📂 C 层（可选，定向）：[ai-agents-in-action-2nd-edition-cn](../source/ai-agents-in-action-2nd-edition-cn/)（测试评测相关章节定向回源）

**核心问题**：
- Agent 的测试策略是什么（单元测试、集成测试、E2E 测试）？
- 如何设计评测指标和基准测试？

**实践产出物**：
- 为 Agent 核心机制编写单元测试
- 实现一个评测脚本

**验收标准**：核心机制有正常路径、失败路径和边界条件测试

**校验对象**：[ch17-agent-testing-evaluation-benchmarks.md](merged-agent-course/ch17-agent-testing-evaluation-benchmarks.md)

---

### D24: 可观测性与生产部署

**主线学习**：
- 📖 理论：[hello-agents Extra09](../source/hello-agents/docs/)（Agent 应用开发实践踩坑）
- 📂 B 层（可选，30min）：[harness-engineering part7/ch29](../source/harness-engineering-from-cc-to-ai-coding/part7/ch29.md)（可观测性）

**核心问题**：
- 结构化日志如何设计（含 Trace ID、上下文信息）？
- 指标采集的关键指标有哪些？

**实践产出物**：
- 实现结构化日志
- 实现指标采集（Token 用量、延迟、错误率）

**验收标准**：能通过日志和指标定位问题

**校验对象**：[ch18-production-observability-product-iteration.md](merged-agent-course/ch18-production-observability-product-iteration.md)

---

### D25: 后训练与自进化

**主线学习**：
- 📖 理论：[hello-agents Ch11](../source/hello-agents/docs/chapter11/)（Agentic RL）
- 🔧 工程：无（今日专注理论）
- 📚 专题：[ai-agent-book Ch07-08](../source/ai-agent-book/book/chapter7.md)（后训练、经验学习专题）

**核心问题**：
- Agentic RL 的核心概念是什么？
- 经验学习和自进化如何实现？

**示例运行（P0）**：[ai-agent-book chapter1/learning-from-experience](../source/ai-agent-book/chapter1/learning-from-experience/)，跑通 quick_demo.py，读 rl_agent.py / llm_agent.py 核心逻辑（60-90 分钟）

**实践产出物**：
- 阅读 ai-agent-book Ch08 的经验学习案例
- 设计一个简单的经验学习机制

**验收标准**：能解释 Agentic RL 和经验学习的核心概念

**校验对象**：[ch19-agent-self-evolution-post-training.md](merged-agent-course/ch19-agent-self-evolution-post-training.md)

---

### D26: 源码精读 - learn-claude-code + Coding Agent 专题

**任务**：
- 精读 [learn-claude-code s15_integrated_harness ★](../source/learn-claude-code/s15_integrated_harness/)（机制归一循环，综合精读）
- 扩展：[s16_workflow_runtime ◯](../source/learn-claude-code/s16_workflow_runtime/)（读 README + 跑 code.py，journal 续跑概念记入笔记）
- 📂 B 层：[claude-code-analysis 01-architecture-overview](../source/claude-code-analysis/analysis/01-architecture-overview.md) + [07-code-evidence-index](../source/claude-code-analysis/analysis/07-code-evidence-index.md)（真实 CC 架构对照）；[harness-engineering part1/ch01、ch03](../source/harness-engineering-from-cc-to-ai-coding/part1/ch01.md)（技术栈与从 Loop 到 Harness）
- 📚 专题：[ai-agent-book Ch05](../source/ai-agent-book/book/chapter5.md)（Coding Agent 与代码生成，为后续 Python Coding Agent 项目做准备）
- 对比自己的实现，找出差距；记录可借鉴的设计决策
- P1 选跑：[chapter1/search-codegen](../source/ai-agent-book/chapter1/search-codegen/)

**产出物**：源码精读笔记（设计模式、权衡取舍、可改进点）+ Coding Agent 专题笔记

**校验对象**：[ch15-loop-engineering.md](merged-agent-course/ch15-loop-engineering.md)

---

### D27: 源码精读 - hello-agents

**任务**：
- 精读 [hello-agents Ch07](../source/hello-agents/docs/chapter7/)（自建 Agent 框架）和 [Ch14](../source/hello-agents/docs/chapter14/)（Deep Research）
- 扩展：[Ch13 ◯](../source/hello-agents/docs/chapter13/)（智能旅行助手，浏览综合应用形态即可）
- 对比自己的实现，找出差距；记录可借鉴的设计决策

**产出物**：源码精读笔记

---

### D28: W4 复盘与补漏

**任务**：同 D7（P1 选跑：book-translation、staged-system-prompt）

---

## D29-30: 毕业复盘

### D29: 知识体系整合

**任务**：
- 精读 [learn-claude-code s17_goal_loop ★](../source/learn-claude-code/s17_goal_loop/)（目标闸门 + 独立判断器 + 自动续轮，体系收官章），运行 `python s17_goal_loop/code.py`
- 📂 C 层（可选）：[Alice_methodology](../source/Alice_methodology/chapters/)（复盘方法论）
- 绘制完整的 Agent 知识体系图（从内核到生产化）
- 整理 30 天学习笔记，形成知识图谱
- 标记仍需深入的专题（列入后续计划）

**产出物**：Agent 知识体系图 + 学习笔记索引

---

### D30: 项目毕业答辩

**任务**：
- 📖 扩展：[hello-agents Ch16 ◯](../source/hello-agents/docs/chapter16/)（毕业设计参考）
- 📂 定向参考：[claw0](../source/claw0/)、[hello-claw](../source/hello-claw/)（OpenClaw 类常驻 Agent 项目参考）；[30-Agents](../source/30-Agents-Every-AI-Engineer-Must-Build/)（项目灵感池）
- 演示综合 Agent 项目（TS 类 OpenClaw Agent）
- 讲解核心设计决策和权衡
- 回答预设问题（由 quiz-master 生成）

**产出物**：项目 README（含架构图、核心机制说明、使用示例）

**验收标准**：
- 能清晰讲解 Agent Loop、工具调用、上下文压缩、权限门等核心机制
- 能回答"为什么这样设计"而不是"如何实现"

**校验对象**：[ch20-cases-capstone-agent.md](merged-agent-course/ch20-cases-capstone-agent.md)

---

## 后续计划（30 天后）

30 天主线完成后，进入专题深入阶段：

1. **专题参考**：根据兴趣和工作需要，深入 [ai-agent-book](../source/ai-agent-book/) 的特定专题（[Ch09 多模态与实时交互](../source/ai-agent-book/book/chapter9.md) 安排在 30 天主线之外，在此阶段精读；ch12-multimodal 教材校验同步后置）
2. **实战项目**：启动 Python Coding Agent 项目，应用 30 天所学；[30-Agents-Every-AI-Engineer-Must-Build](../source/30-Agents-Every-AI-Engineer-Must-Build/) 的 30 个 Agent 构建案例作灵感池
3. **源码级精通**：hermes-book、harness-engineering-from-cc-to-ai-coding 两大 B 层工程源码展开；Claude Code、OpenClaw 源码级精读
4. **教材修订**：持续校验和修订 [`docs/merged-agent-course/`](merged-agent-course/)，形成可发布的学习成果

---

## 计划调整记录

| 日期 | 版本 | 调整内容 | 原因 |
|------|------|----------|------|
| 2026-08-17 | v1.0 | 初始版本（以教材为主线） | 从对话落盘 |
| 2026-08-17 | v2.0 | 重写为以 source 为主线 | 用户反馈：应该是 source 为主线，教材仅作校验 |
| 2026-08-17 | v2.1 | 补全 ai-agent-book 章节覆盖 | 章节核查：Ch01→D1、Ch04→D4、Ch05→D26、Ch09→后续计划 |
| 2026-08-17 | v3.0 | learn-claude-code 切换为 s01-s17 新版主线（17 章全映射，区分必读★/扩展◯）；补排 s10→D8、s17→D29；hello-agents 补 Ch13/15/16；教材补 ch13/ch15/ch20 映射；B 层四工程择要点位；进度状态迁移至 progress.md | 用户 review 通过：按 A/B/C 分层与必读/扩展层级重构 |

---

**维护说明**：
- 每周日复盘时，根据实际进度调整后续计划
- 每日学习结束后，在 [`docs/progress.md`](progress.md) 标记完成状态（✅/⚠️/❌）
- 调速规则严格执行：只降速，不跳主题
- 每天学习完成后，必须对照"校验对象"列的教材章节进行双向校验
- 📂 标注的 B/C 层材料为架构查阅，不计入精读时长，时间不够时优先裁剪