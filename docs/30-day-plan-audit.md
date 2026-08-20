# 30 天学习计划审计

> 审计日期：2026-08-20
>
> 审计对象：[30 天主线学习计划](30-day-plan.md)、[学习进度记录](progress.md)
>
> 审计边界：12 个来源工程、当前 Agent 工程的重要主题、30 天内的学习负载和验收方式
>
> 学习目标：建立完整知识骨架；独立实现持续演进的 Python Coding Agent；能够定位并局部改造复杂 Coding Agent 和长期运行 Agent 源码

## 结论

当前计划方向正确，知识覆盖较广，但不适合原样执行。

计划能帮助学习者广泛接触 Agent 工程知识，却不能稳定保证以下两个结果：

1. 完成一个持续演进、可以验收的 Python Coding Agent。
2. 获得定位和局部改造复杂 Agent 源码的能力。

主要问题来自学习强度分配。Gateway、可靠运行、安全、评测和 Coding Agent 实战投入不足；模式复刻、后训练和部分重复阅读占用过多时间。建议保留四周学习骨架，重新分配模型运行时、安全、Gateway、评测和源码精读等主题日。

## 合理之处

- 以 12 个来源工程为主，融合教材作为学后校验和发布产物，符合当前学习目标。
- 计划没有要求平均学习 12 个来源，而是区分主线、专题和案例。
- “闭卷复述、源码运行、代码考古、独立重写、测试”的掌握标准有效。
- 计划没有把跑通 Demo 算作掌握。
- W1 至 W4 的总体依赖关系成立：Loop、状态与信息、治理与扩展、常驻与生产。
- 单点实验验证机制，再把通过验证的机制集成到同一个 Agent，适合工程学习。

## 必须优先处理的问题

### 1. 综合项目没有成为学习主线

计划要求每日实践，但没有定义累计项目的周里程碑。D30 才要求演示“TS 类 OpenClaw Agent”，之后又把 Python Coding Agent 放到 30 天以后。这与当前确定的 Python Coding Agent 目标冲突。

应从 D3 开始建立 Python Coding Agent。每天先用小实验隔离验证机制，再把通过验证的代码合入该项目。D30 应演示这一个项目，不再新开 TypeScript 综合项目。

### 2. `claw0` 权重过低

计划只在 D22 安排约 30 分钟查阅 `claw0`，却希望掌握长期运行、Gateway、可靠投递和并发。

`claw0` 用渐进式 Python 实现覆盖 Session、Channel、Gateway 路由、Heartbeat、Cron、可靠投递、重试和并发 Lane。它与长期运行 Agent 源码能力直接对应，应从“按问题查阅”提升为第二工程锚点。重点学习 s03 至 s10；s01 至 s02 只需与 `learn-claude-code` 对照。

来源：[shareAI-lab/claw0](https://github.com/shareAI-lab/claw0)

### 3. 安全学习停留在权限审批

D16 主要覆盖允许、拒绝和审批，没有形成完整安全模型。Python Coding Agent 还需要学习：

- 文件、网络、进程和密钥隔离。
- Prompt Injection 与不可信工具结果。
- 路径穿越、命令注入和参数污染。
- 最小权限、凭据作用域和数据外泄控制。
- 审计、撤销和事故恢复。

这些内容属于 Coding Agent 的基础能力。OWASP 已针对自主 Agent 的计划、行动和跨系统交互整理独立风险框架。

来源：[OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

### 4. 测试与评测开始得太晚

计划到 D23 才正式安排评测。此前实现的机制可能能运行，却没有稳定基线。

评测应从 D3 开始：

- 每加入一个机制，同时增加正常、失败和边界测试。
- 第一周冻结一组小型 Coding Agent 任务。
- 每周比较成功率、错误类型、步骤数、Token、延迟和成本。
- D23 用于系统学习评测理论，不作为第一次建立评测的日期。

30 天内不必运行完整 SWE-bench，但可以借用其方法：固定仓库和问题，通过补丁与测试结果判断任务是否解决。

来源：[SWE-bench](https://github.com/swe-bench)

### 5. 当前机器缺少大部分来源工程

当前 `source/` 状态：

- 完整可读：`ai-agents-in-action-2nd-edition-cn`、`30-Agents-Every-AI-Engineer-Must-Build`。
- 不完整：`easy-langent`。
- 其余 9 个来源缺失。

[来源知识点索引](source-topic-index.md)也记录了大量“待 Clone 后展开”的源码入口。因此，[来源覆盖说明](source-coverage.md)中的“12 个来源均已覆盖”目前只能证明目录级映射，不能证明已经完成文件级和代码级验证。

在当前机器继续执行 source-first 计划前，需要先解决来源工程的可访问性。

## 遗漏或学习强度不足的内容

| 优先级 | 内容 | 当前问题 | 30 天内要求 |
| --- | --- | --- | --- |
| P0 | Coding Agent 仓库工作流 | 缺少仓库侦察、搜索、编辑、Diff、测试、回滚和 worktree 闭环 | 必须实践 |
| P0 | Gateway、身份、Session Key 与路由 | 只有 D22 附带阅读 | 必须实践 |
| P0 | 可靠运行 | 幂等、去重、退避、死信、租约、取消、背压和重启恢复不足 | 必须实践 |
| P0 | 完整安全模型 | 权限审批不能代替沙箱、注入防御、密钥和数据边界 | 必须实践 |
| P0 | 持续评测 | 评测没有伴随机制变更 | 从 D3 开始 |
| P0 | 复杂源码阅读方法 | 只有 D26 集中精读，缺少持续的调用链跟踪和局部修改 | 每周安排 |
| P1 | Loop Engineering | Verifier、Checkpoint、无进展判断、预算和停止控制没有形成独立闭环 | 至少完成最小闭环 |
| P1 | MCP 版本、授权和长任务 | 计划停留在 Server/Client，缺少授权、版本和任务生命周期 | 理论加最小实验 |
| P1 | Human-in-the-loop | 缺少暂停、恢复、取消和重复执行时的幂等设计 | 最小实验 |
| P1 | 多模态与实时交互知识骨架 | 整章后置，与“完整知识骨架”目标不符 | 只学概念，不要求实现 |
| P1 | 生产发布 | D24 只有日志和指标，缺少配置、密钥、限流、版本、灰度、回滚和成本预算 | 建立知识骨架 |
| P2 | A2A/ANP 深入实现 | 与当前 Coding Agent 主目标距离较远 | 理解边界即可 |
| P2 | 后训练和 Agentic RL 实践 | 投入产出比低于安全、评测和可靠运行 | 保留半天理论 |

MCP 已加入无状态核心、扩展、长任务生命周期和更严格的授权要求。学习时应把协议版本和授权边界纳入实验，不能只运行旧版 Server/Client 示例。

来源：[MCP 2026-07-28 更新](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)

A2A 已形成面向独立 Agent 的发现、任务和交互协议。30 天内理解它与 MCP 的边界即可。

来源：[A2A Protocol](https://a2a-protocol.org/v1.0.0/)

## 12 个来源的建议权重

| 来源 | 建议角色 | 调整意见 |
| --- | --- | --- |
| `hello-agents` | 理论骨架主线 | 保留核心章节；低代码操作和多个业务案例不必精读 |
| `learn-claude-code` | 第一工程锚点 | 贯穿 Python Coding Agent 的机制实现 |
| `claw0` | 第二工程锚点 | 提升权重，重点学习 s03 至 s10 |
| `ai-agent-book` | 专题深挖 | 重点 Ch02 至 Ch06、Ch09 至 Ch10；Ch07 至 Ch08 保留概念阅读 |
| `harness-engineering-from-cc-to-ai-coding` | Coding Agent 工程对照 | 用于生产模式和复杂实现解释 |
| `claude-code-analysis` | 大型源码阅读训练 | 练习入口定位、调用链、权限、上下文和组件边界 |
| `hermes-book` | 长期个人 Agent 架构对照 | 重点学习生命周期、记忆、Gateway 和容错 |
| `easy-langent` | Python/LangGraph 定向实践 | 用于状态图、Checkpoint、HITL 和 RAG |
| `ai-agents-in-action-2nd-edition-cn` | 机制补充 | 提高权重，重点学习严格输出、MCP、TDAD、三层 Loop 和认知控制 |
| `Alice_methodology` | 方法论补充 | 定向学习安全、权限、可观测性和产品工程 |
| `hello-claw` | OpenClaw 生态参考 | 只读构建篇中的 Gateway、安全和 Skill；继续排除安装手册 |
| `30-Agents-Every-AI-Engineer-Must-Build` | 模式库 | 从五个独立复刻减为二至三个机制实验 |

当前计划对 `ai-agent-book` 的投入略重，对 `claw0` 和 `ai-agents-in-action-2nd-edition-cn` 的投入偏轻。

## 日程调整建议

已经完成的 D1 至 D3 不需要重学。后续可按以下原则调整：

- 把 D12 的模型运行时提前到 Prompt 和上下文之前。
- 把 D11“记忆与知识边界”并入 D9 至 D10，释放一天学习 Coding Agent 仓库工作流。
- D15 使用 `easy-langent` 学习 LangGraph；Skill Loading 留到 D18。
- D16 学权限管线；D17 改为沙箱、注入防御和信任边界。Hooks 并入 D16 或 D18。
- D20 只完成 Subagent 和任务委托。持久团队与并发协作不要在同一天全部完成。
- D22 改为 Session、Channel、Gateway、身份和路由。
- D23 改为 Heartbeat、Cron、可靠投递、重试和并发。
- 测试与评测分散到每天，原 D23 的理论内容并入 D24。
- D25 将后训练缩短为半天，另一半用于发布、回滚和安全加固。
- D26 对 `learn-claude-code` 做调用链追踪和局部修改。
- D27 改为 `claw0` 源码精读和局部修改；Hello Agents 案例降为选读。
- D28 做累计项目集成回归，不再同时复刻 Coding Agent 和 Multi-Agent。
- D29 做失败注入、安全审计和知识体系整理。
- D30 演示并答辩 Python Coding Agent。

LangGraph 的持久执行要求学习者同时处理检查点、暂停恢复和副作用幂等，而不是只实现一个状态图。

来源：[LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## 进度跟踪问题

当前 [progress.md](progress.md) 存在以下问题：

- 文件仍声明配合 v3.0，学习计划已经是 v4.0。
- D1 至 D5 的主题名称与计划不一致。
- 一个“完成”状态无法区分阅读、闭卷、代码、测试和教材 Review。
- 没有证据链接、实际用时、遗留问题和顺延项。
- 没有累计项目能力矩阵和每周回归结果。

后续进度记录至少需要五类证据：

1. 闭卷结果。
2. 实验或 commit。
3. 测试结果。
4. 源码调用链笔记。
5. 融合教材发现的错误或遗漏。

每日状态用于记录执行情况；能力矩阵用于判断是否掌握。两者不能合并成一个“已掌握”字段。

## D30 验收标准

Python Coding Agent 至少应满足以下条件：

- 能理解陌生仓库并建立文件地图。
- 能搜索、读取和修改代码，生成可审查 Diff。
- 能运行测试，根据失败结果继续修复。
- 高风险命令经过权限和安全边界。
- 会话中断后能够恢复。
- 支持后台任务、定时触发和可靠结果投递。
- 记录结构化 Trace、成本和失败信息。
- 在冻结的小型任务集上通过回归测试。
- 能解释 `learn-claude-code` 和 `claw0` 的一条核心调用链，并分别完成一次边界明确的局部改造实验。

对上游工程的改造应使用临时分支、fork 或独立实验目录，不直接修改 `source/` 中的原始材料。

## 最终判断

计划已经具备可用的学习骨架。调整资源权重、累计项目、可靠运行、安全和持续评测后，它才能支持“Python Coding Agent + 两类复杂源码能力”的目标。

融合教程在 30 天内只做技术正确性、关键结论和遗漏检查。公众号发布所需的结构和语言编辑应放到学习闭环之后，避免写作挤占编码、测试和源码阅读时间。
