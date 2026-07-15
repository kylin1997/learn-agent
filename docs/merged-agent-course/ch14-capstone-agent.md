# 第 14 章：综合项目：构建自己的 Agent

> 本章目标：把前 13 章融合成一个可逐步实现的综合项目。读完本章，你应该能规划一个学习型个人编码/研究助理，从最小 Agent Loop 逐步扩展到工具、权限、记忆、Gateway、Cron、多 Agent 和观测。

## 14.1 项目定位

最终项目建议做一个“学习型个人编码/研究助理”。

它不是为了追求一次做完所有功能，而是把所有章节知识串成一条可执行路线：

```text
能对话
  -> 能用工具
  -> 能管理上下文
  -> 能记住项目
  -> 能安全执行
  -> 能接入外部能力
  -> 能常驻运行
  -> 能并行协作
  -> 能被测试和观测
```

项目目标：

- 支持本地项目学习和代码任务。
- 支持长会话和上下文压缩。
- 支持项目记忆和用户偏好。
- 支持 Skills 和 MCP。
- 支持基本权限和沙箱。
- 支持 CLI，后续接 Gateway。
- 支持任务计划、子 Agent 和验证。
- 支持日志、测试和可观测性。

## 14.2 总体架构

```text
User / Channel
  -> Gateway / CLI
  -> Session Manager
  -> Loop Controller
      -> Goal / Budget / Stop Policy
      -> State Store / Checkpoint
      -> Prompt Runtime
      -> Agent Loop
          -> Tool Dispatcher
          -> Permission System
          -> Context Manager
          -> Memory System
          -> Skill Loader
          -> Model Router
      -> Independent Verifier
      -> Retry / Escalate / Stop
  -> Delivery / Response

Background:
  Cron
  Memory consolidation
  Subagents
  Observability
```

每个模块对应前面章节：

| 模块 | 对应章节 |
| --- | --- |
| Agent Loop | 1-2 |
| Prompt Runtime | 3 |
| Model Router | 4 |
| Session / Context | 5 |
| Memory | 6 |
| LangGraph / RAG | 7 |
| Security | 8 |
| Skills / MCP | 9 |
| Gateway / Cron | 10 |
| Loop Engineering | 11 |
| Multi-Agent | 12 |
| Engineering | 13 |

第 11 章负责把这些模块连接成可持续执行系统；闭环可以在单次会话内完成，也可以跨运行持续推进。综合项目不应只实现“再次运行”，还要明确 verifier、外部状态、检查点、停止条件、预算和人工审批边界。

## 14.3 里程碑 1：最小 Agent Loop

先实现：

- messages 列表。
- system prompt。
- model call。
- tool_use 解析。
- tool result 回填。
- 循环直到 final answer。

验收：

- 用户能问问题。
- Agent 能调用一个简单工具。
- 工具结果能进入下一轮模型调用。
- transcript 可保存。

不要一开始就接所有工具。一个 `read_file`、一个 `list_files`、一个 `write_file` 就够。

## 14.4 里程碑 2：工具与权限

增加：

- 工具 registry。
- schema 校验。
- handler map。
- PermissionResult。
- PreToolUse hook。
- 敏感路径 deny list。
- 文件写入确认。

验收：

- 读操作可直接执行。
- 写操作按模式确认。
- 危险命令被拒绝。
- 权限决策写入日志。

## 14.5 里程碑 3：Prompt Runtime 与模型路由

增加：

- prompt section。
- 动态上下文注入。
- 工具描述。
- 专项 prompt。
- provider 抽象。
- fallback。
- token 和成本记录。

验收：

- system prompt 由 section 组装。
- 动态信息在末尾。
- 不同任务可选择不同模型。
- provider 失败能降级。

## 14.6 里程碑 4：会话、上下文和记忆

增加：

- JSONL session store。
- context builder。
- tool result budget。
- 大结果落盘。
- 9 节 compact summary。
- `.memory/` 文件系统记忆。
- MEMORY.md 索引。
- 相关记忆召回。

验收：

- 长会话不会轻易爆上下文。
- Resume 能恢复当前任务。
- 用户偏好能跨会话召回。
- 临时任务状态不会污染长期记忆。

## 14.7 里程碑 5：Skills、MCP 与 RAG

增加：

- Skill catalog。
- Skill load。
- Skill references 按需读取。
- MCP client。
- MCP 工具统一命名。
- 简单 RAG 文档检索。

验收：

- 用户点名 Skill 时能加载。
- MCP 工具进入统一工具池。
- MCP 工具仍走权限系统。
- RAG 回答带来源。

## 14.8 里程碑 6：Gateway、Cron 与后台任务

增加：

- `InboundMessage` / `OutboundMessage`。
- CLI channel。
- 一个外部 channel 或 WebSocket。
- BindingTable。
- DeliveryQueue。
- Cron job。
- main / cron / heartbeat lane。

验收：

- 多渠道消息进入统一 Agent。
- session key 不串线。
- 定时任务能触发。
- 发送失败能重试。

## 14.9 里程碑 7：Loop Controller 与可恢复执行

增加：

- `LoopSpecification`：目标、范围、不变量、预算和停止条件。
- `LoopController`：选择工作、启动执行、验证结果和决定下一轮。
- 外部 `StateStore` 与每轮 checkpoint。
- 独立 verifier 和结构化 verdict。
- no-progress、不可重试失败和人工审批 gate。
- 执行中断后的恢复与幂等保护。

验收：

- 新会话能从外部状态继续未完成任务。
- runner 或 verifier 中断后不会把任务误判为成功。
- 连续无改善、预算耗尽或高风险操作会可靠停止。
- 每轮都能回溯目标、动作、验证证据和停止原因。

## 14.10 里程碑 8：多 Agent 与验证

增加：

- TodoWrite。
- `task` subagent。
- verifier agent。
- 并发限制。
- 结构化 subagent report。
- 可选 worktree 隔离。

验收：

- Lead 能拆任务。
- Subagent 能独立研究并返回证据。
- Verifier 能发现风险。
- Lead 综合后再回复用户。

## 14.11 里程碑 9：测试、观测和产品化

增加：

- 单元测试。
- 行为回归案例。
- 权限测试。
- context compact 测试。
- trace / metrics / logs。
- 配置校验。
- doctor 命令。
- 场景评分表。

验收：

- 关键模块有测试。
- 每次模型和工具调用可追踪。
- 错误恢复路径有上限。
- 用户能查看配置、任务、队列、记忆。

## 14.12 不要一次做完

综合项目最容易失败的方式是一次性做全功能。

正确节奏：

```text
每个里程碑:
  先做最小可运行
  再加安全边界
  再加测试
  再写文档
  再进入下一层
```

每一层都应该能独立演示。

如果某层还不能解释清楚，就不要急着往上堆。

## 14.13 项目交付物

建议最终交付：

- `README.md`：项目目标、运行方式、能力清单。
- `docs/architecture.md`：系统架构。
- `docs/security.md`：权限、沙箱、隐私。
- `docs/memory.md`：记忆策略。
- `docs/evals.md`：评测和测试。
- `examples/`：典型任务。
- `.env.example`：配置变量。
- `tests/`：测试集。
- `experiments/`：学习实验。

## 14.14 学习顺序建议

最有效的学习方式不是先读完所有资料，而是“读一章，做一层”：

```text
读第 1-2 章 -> 做最小 Loop 和工具
读第 3-4 章 -> 做 prompt 和 model router
读第 5-6 章 -> 做 session、compact、memory
读第 8 章 -> 做权限和安全
读第 9 章 -> 做 Skill / MCP
读第 10 章 -> 做 Gateway / Cron
读第 11 章 -> 做 verifier、state、checkpoint 和 stop condition
读第 12 章 -> 做 subagent
读第 13 章 -> 补测试和观测
```

第 7 章的 LangChain / LangGraph 可以穿插：当你想快速做 RAG 或状态工作流时，用它做应用层实验。

## Hello-Agents 融合补充

`hello-agents` 的综合项目内容可以直接作为本章的项目池。第 13 章智能旅行助手适合做“面向用户的产品型 Agent”：它有明确场景、结构化输入、角色分工、外部工具和前端呈现。第 14 章自动化深度研究智能体适合做“知识工作型 Agent”：它以 TODO、搜索、笔记、报告为主线，强调证据管理和产出质量。第 15 章赛博小镇适合做“多 Agent 环境型项目”：它考验长期记忆、角色状态、后台任务和前后端联动。

第 16 章毕业设计和共创项目给了一个很好的交付标准：项目不只是代码，还包括问题定义、运行方式、依赖、数据样例、Notebook、评估方式和复盘说明。对学习者来说，最终综合项目可以不追求“大而全”，但一定要做到：

- 能演示一个真实任务闭环。
- 能说明用了哪些 Agent 能力层。
- 能展示失败案例和改进记录。
- 能复现运行环境。
- 能解释安全、上下文、记忆和评测选择。

Hello-Agents 第 11、12 章的 Agentic-RL 与性能评估可以作为进阶方向。初版综合项目不必一开始就训练模型，但可以先保留数据结构：记录任务轨迹、工具调用、用户反馈、失败类型和评分结果。这样后续无论是改 prompt、换模型、加 RAG、做微调，还是尝试强化学习，都有可用的证据基础。

如果把本课程的综合项目与 `hello-agents` 对齐，可以得到三条推荐路线：

```text
实用路线：
  旅行助手 / 研究助手 / 文件处理助手。

工程路线：
  自建 Harness + MCP + Skill + 评测系统。

探索路线：
  多 Agent 世界 / 自进化 Skill / WebAgent。
```

选择哪条路线不重要，重要的是最终能讲清楚：这个 Agent 为什么需要自主性，它的工具边界在哪里，它如何处理上下文和记忆，它怎么证明自己可靠。

## 系统地图

```text
Capstone Agent
  -> Core Loop
  -> Tool + Permission
  -> Prompt + Model Router
  -> Session + Context + Memory
  -> Skill + MCP + RAG
  -> Gateway + Cron
  -> Loop Controller + Verifier + State
  -> Multi-Agent
  -> Tests + Observability
```

## 共同结论

1. 综合项目要按能力层推进，不要一次堆全功能。
2. 每个模块都应该有来源章节、最小实现和验收标准。
3. 安全、上下文和观测不是后补项，而是每层都要带着做。
4. 最终目标不是复刻某个教程，而是形成自己的 Agent 工程判断。

## 本章自检

1. 为什么综合项目应该从最小 Agent Loop 开始？
2. 哪些模块必须在接入 Gateway 前完成？
3. 为什么记忆和上下文要早于多 Agent？
4. 每个里程碑的验收标准应该如何设计？
5. 什么时候应该引入 LangGraph，而不是继续手写流程？

## 开放性问题

1. 如果你只能先做三个模块，哪三个最能体现 Agent 的核心价值？为什么？
2. 这个综合项目更像“个人工具”还是“平台底座”？不同定位会如何改变架构？
3. 当实现复杂度和学习价值冲突时，哪些地方应该简化，哪些地方不能省？

## 原文入口

- [learn-claude-code s20: Comprehensive Agent](../../source/learn-claude-code/s20_comprehensive/README.md)
- [easy-langent 综合项目](../../source/easy-langent/docs/guide/chapter5.md)
- [easy-langent 项目索引](../../source/easy-langent/docs/projects.md)
- [Hermes 项目总览](../../source/hermes-book/README.md)
- [Hermes 设计赌注](../../source/hermes-book/src/part1/ch01-design-bets.md)
- [Alice 方法论总览](../../source/Alice_methodology/README.md)
- [Alice 工程范式](../../source/Alice_methodology/chapters/15-engineering-patterns.md)
- [hello-claw 构建篇](../../source/hello-claw/docs/cn/build/index.md)
- [hello-claw 学习资源](../../source/hello-claw/docs/cn/appendix/appendix-a.md)
- [claw0 全系列](../../source/claw0/README.zh.md)
- [Claude Code 分析总览](../../source/claude-code-analysis/README.md)
- [hello-agents 项目总览](../../source/hello-agents/README.md)
- [hello-agents Ch13: 智能旅行助手](../../source/hello-agents/docs/chapter13/第十三章%20智能旅行助手.md)
- [hello-agents Ch14: 自动化深度研究智能体](../../source/hello-agents/docs/chapter14/第十四章%20自动化深度研究智能体.md)
- [hello-agents Ch15: 构建赛博小镇](../../source/hello-agents/docs/chapter15/第十五章%20构建赛博小镇.md)
- [hello-agents Ch16: 毕业设计](../../source/hello-agents/docs/chapter16/第十六章%20毕业设计.md)
- [hello-agents 共创项目](../../source/hello-agents/Co-creation-projects/README.md)
