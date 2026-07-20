# Agent 学习指南

本指南说明如何使用本工程完成系统学习。主线教材已经融合 `source/` 下 9 个来源工程中的可迁移知识；学习者不需要按来源目录逐份通读。

## 学习目标

学习的终点不是记住框架 API，而是能够设计、实现和验证一个具备以下能力的综合 Agent：

- Agent Loop、工具调用和停止控制
- Prompt Runtime、模型路由和调用可靠性
- 会话、状态、上下文、长期记忆和 RAG
- 权限、沙箱、隐私和审批边界
- Skills、插件和互操作协议
- Gateway、后台任务、Cron 和可靠投递
- Loop Engineering、多 Agent 和任务协作
- 测试、评测、可观测性和产品迭代

## 工程资料怎么使用

| 资料 | 用途 | 使用时机 |
| --- | --- | --- |
| [融合教材目录](merged-agent-course/course-catalog.md) | 进入 20 章主教材，查看 Review 状态 | 每次开始学习时 |
| 本指南 | 安排阶段、学习动作、实践产物和完成标准 | 规划和复盘时 |
| [来源覆盖说明](source-coverage.md) | 查看主题如何合并、来源是否覆盖、哪些内容被排除 | 核查教材依据时 |
| `source/` | 查看原始论证、代码原型和实现差异 | 章末回源或开始实验时 |
| `experiments/` 或 `src/` | 保存本项目自己的实验和综合 Agent | 进入实践后 |

日常学习只需要打开融合教材。覆盖说明属于维护和核查材料，不是第二套教材。

## 三个学习动作

### 主读

阅读融合教材对应章节，理解该主题的完整知识结构。优先关注：

- 这个机制解决什么问题。
- 它管理什么状态，谁拥有控制权。
- 运行时如何执行、失败和恢复。
- 如何测试结果，而不是只看模型是否给出答案。

### 回源

出现以下情况时，再打开章末原文入口：

- 教材中的机制仍然抽象，需要查看真实代码。
- 两个来源采用不同设计，需要比较取舍。
- 准备实现对应能力，需要参考数据结构或执行流程。
- 对教材结论有疑问，需要核查论证上下文。

产品安装、配置命令、低代码点击流程、硬件部署和低成熟度案例不属于必学内容。

### 实践

每学完一组相关章节，就给同一个综合 Agent 增加一项可验证能力。不要为每章建立互不相关的小项目。

每个实践至少记录：

```text
目标：本次要解决什么问题
设计：状态、边界和控制权如何划分
实现：增加了哪些组件
验证：用什么测试证明它有效
结论：哪些假设成立，哪些需要调整
来源：参考了哪些教材章节或原型
```

## 每章学习循环

### 1. 预读

先读“学习目标与边界”“系统地图”和“共同结论”，列出本章准备回答的三个问题。

### 2. 精读

阅读正文和最小实现。遇到抽象概念时，用一个具体任务推演输入、状态变化、工具调用、失败和输出。

### 3. 闭卷检查

不看正文回答“本章自检”。自检题用于检查概念和机制，开放性问题用于检查能否分析边界与取舍。

### 4. 最小实践

实现本章最关键的一个机制，并加入正常路径、失败路径和边界条件测试。

### 5. 复盘与 Review

记录仍然无法解释的内容。只有用户确认章节的结构、深度和表达后，才在教材目录中把该章标记为“已 Review”。

## 五阶段学习路线

五个阶段按能力依赖组织。阶段内可以调整节奏，但不建议跳过阶段产物。

## 阶段一：建立最小 Agent

主读：

1. [Agent、智能体历史与 Harness](merged-agent-course/ch01-agent-and-harness.md)
2. [大语言模型基础与模型行为](merged-agent-course/ch02-llm-foundations-model-behavior.md)
3. [Agent Loop、经典范式与工具运行时](merged-agent-course/ch03-agent-loop-paradigms-tools.md)

核心问题：

- Agent、Chatbot、Workflow 和 Hybrid System 的边界是什么。
- 模型的概率生成特性会给执行系统带来哪些风险。
- Agent Loop 如何连接模型、工具、环境反馈和停止判断。
- ReAct、Plan、Reflection 和 Evaluator-Optimizer 分别改变哪一层控制逻辑。

实践产物：

- 一个本地只读 Agent。
- 一个声明式工具注册表和工具执行管线。
- 工具参数校验、错误返回、权限占位和最大步数限制。

完成标准：

- 能画出一次任务从输入到结束的完整执行路径。
- 能解释模型能力与系统授权为什么必须分离。
- Agent 在工具失败、参数错误和循环超限时能够可控退出。

## 阶段二：建立稳定的认知运行时

主读：

4. [Prompt Engineering 与 Prompt Runtime](merged-agent-course/ch04-prompt-engineering-runtime.md)
5. [模型运行时、路由与调用可靠性](merged-agent-course/ch05-model-runtime-routing-reliability.md)
6. [会话、状态与上下文工程](merged-agent-course/ch06-session-state-context-engineering.md)
7. [长期记忆系统](merged-agent-course/ch07-long-term-memory.md)
8. [RAG 与外部知识系统](merged-agent-course/ch08-rag-knowledge-systems.md)

核心问题：

- Prompt 如何从一段文本变成运行时契约和装配系统。
- 模型选择、重试、降级和结构化输出如何影响可靠性。
- 会话记录、执行状态、模型上下文和长期记忆分别保存什么。
- Agent 如何选择当前需要的信息，并说明选择和丢弃原因。
- 长期记忆与外部知识库如何更新、召回、去重和遗忘。

实践产物：

- Prompt Assembler 和 Provider Router。
- 追加式事件日志、状态归约、检查点和恢复流程。
- 可记录选择理由的 Context Builder。
- 长期记忆召回和带证据的 RAG 原型。

完成标准：

- Agent 重启后可以恢复任务，而不是依赖聊天摘要猜测状态。
- 模型调用失败时有明确重试、降级和终止策略。
- 每条长期记忆和知识结论都能追溯来源、版本和更新时间。

## 阶段三：加入框架、治理与扩展能力

主读：

9. [Agent 框架与应用编排](merged-agent-course/ch09-agent-frameworks-orchestration.md)
10. [权限、安全、沙箱与隐私治理](merged-agent-course/ch10-security-permission-sandbox-privacy.md)
11. [Skills 与插件系统](merged-agent-course/ch11-skills-plugins.md)
12. [MCP、A2A、ANP 与 Agent 互操作](merged-agent-course/ch12-agent-interoperability.md)

核心问题：

- 什么时候使用框架，什么时候保留直接、可控的实现。
- 权限判断应该位于工具执行链的什么位置。
- Tool、Skill、Plugin 和协议提供的远程能力有什么边界。
- 外部内容、工具结果和跨 Agent 消息如何穿过信任边界。

实践产物：

- 一个 LangGraph 或等价状态图应用。
- 权限结果模型、审批门和最小沙箱策略。
- 一个标准 Skill 和一个 MCP 工具接入示例。
- 外部输入的来源标记、参数校验和审计日志。

完成标准：

- 高风险副作用必须经过可追溯授权。
- Skill 和协议能力可以独立启停，不侵入 Agent 核心循环。
- 不可信内容不能直接改变系统权限、工具策略或长期记忆。

## 阶段四：走向常驻运行和多 Agent

主读：

13. [Gateway、多渠道、身份与路由](merged-agent-course/ch13-gateway-channel-identity-routing.md)
14. [后台任务、Cron、投递与运行时韧性](merged-agent-course/ch14-background-cron-delivery-resilience.md)
15. [Loop Engineering](merged-agent-course/ch15-loop-engineering.md)
16. [多 Agent、任务系统与团队协作](merged-agent-course/ch16-multi-agent-task-team.md)

核心问题：

- 多渠道消息如何统一，同时保持身份、租户和会话隔离。
- 后台任务如何处理重复触发、重试、投递失败和进程重启。
- Loop Engineering 如何管理跨运行目标、状态、验证和停止决策。
- 多 Agent 是否带来可测量收益，任务如何切分和验收。

实践产物：

- 统一消息模型、Gateway Router 和可靠投递队列。
- Cron 或 Heartbeat 触发的可恢复后台任务。
- 带外部状态、Verifier、Checkpoint 和停止条件的最小可信 Loop。
- 一个具备任务边界和独立验收的 Lead/Worker 实验。

完成标准：

- 相同事件重复到达不会产生重复副作用。
- 长任务中断后能够从可信检查点恢复。
- 系统能够识别无进展、预算耗尽和验证失败并停止。
- 多 Agent 的引入有质量、延迟或隔离方面的证据。

## 阶段五：评测、进化与生产化

主读：

17. [Agent 测试、评测与基准体系](merged-agent-course/ch17-agent-testing-evaluation-benchmarks.md)
18. [Agent 自进化与后训练](merged-agent-course/ch18-agent-self-evolution-post-training.md)
19. [生产工程、可观测性与产品迭代](merged-agent-course/ch19-production-observability-product-iteration.md)
20. [代表案例与综合 Agent 项目](merged-agent-course/ch20-cases-capstone-agent.md)

核心问题：

- 如何评测轨迹、工具使用、恢复能力和最终结果。
- Prompt、Skill、Memory 或模型更新需要什么证据和回滚机制。
- Trace、Metric、Log 和用户反馈分别回答什么问题。
- 综合 Agent 如何从实验进入可维护、可运营的产品状态。

实践产物：

- 冻结的回归任务集和分层测试方案。
- 可撤销的 Prompt、Skill 或 Memory 改进实验。
- 运行仪表、成本与延迟基线、版本和发布策略。
- 第 20 章定义的综合 Agent 项目。

完成标准：

- 每次能力更新都能与基线比较，并能回退。
- 关键运行可以按任务、模型、工具和事件追踪。
- 综合 Agent 通过正常、失败、中断恢复和对抗性输入测试。

## 综合 Agent 的演进顺序

综合项目从第一阶段开始，不等到第 20 章才启动：

| 阶段 | 增量 |
| --- | --- |
| 一 | 本地只读 Agent Loop 和工具执行 |
| 二 | Prompt、模型路由、状态、上下文、记忆和 RAG |
| 三 | 框架编排、权限、沙箱、Skills 和 MCP |
| 四 | Gateway、后台任务、可靠投递、可信 Loop 和多 Agent |
| 五 | 评测、自进化、可观测性和产品化验收 |

实现细节和最终里程碑以[第 20 章](merged-agent-course/ch20-cases-capstone-agent.md)为准。

## 学习记录模板

建议在 `docs/learning-notes/` 下按主题保存笔记：

```markdown
# 主题

## 核心问题

## 我的解释

## 运行过程或状态图

## 最小实验与验证结果

## 失败案例

## 仍待回答的问题

## 教材与原文入口
```

## 使用 Codex 辅助学习

可以直接提出以下类型的任务：

- “带我学习第 3 章，先提问，不要直接给答案。”
- “用一个真实任务推演这段运行机制。”
- “检查我对本章开放性问题的回答，指出推理缺口。”
- “根据本章设计一个最小实验，先给验收标准。”
- “比较章末两个来源在这个机制上的实现取舍。”
- “我已经确认本章，请同步教材目录中的 Review 状态。”

学习过程中发现内容过浅、跳跃、重复或缺少证据时，应先修订对应章节。只有主题边界、章节顺序或来源覆盖发生变化时，才同步修改本指南或来源覆盖说明。
