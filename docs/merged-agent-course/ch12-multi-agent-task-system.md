# 第 12 章：多 Agent、任务系统与团队协作

> 本章目标：理解多 Agent 不是“多开几个模型”，而是任务分解、上下文隔离、结果汇总、权限分层和协作协议。读完本章，你应该能设计 Todo、Task DAG、Subagent、Coordinator、Verifier、Team、Worktree 隔离等机制。

## 12.1 为什么需要多 Agent

单 Agent 能做很多事，但它有天然限制：

- 长任务会造成上下文污染。
- 多个独立研究任务串行执行效率低。
- 同一个模型同时承担实现、审查、验证，容易自我确认。
- 不同任务需要不同工具、权限和 prompt。
- 大项目修改需要隔离工作区和并行验证。

多 Agent 的目标不是“热闹”，而是把复杂任务拆成可控单元。

```text
Lead Agent:
  理解目标、拆解任务、综合结果、对用户负责。

Subagent:
  在有限上下文里完成局部任务。

Verifier:
  独立检查结论、代码或风险。

Team:
  多个角色通过协议和共享状态协作。
```

核心原则：**委托可以分散工作，但最终综合责任不能外包。**

## 12.2 TodoWrite：最小任务系统

`learn-claude-code` s05 从 TodoWrite 开始，这是多 Agent 之前最重要的一步。

Todo 的作用不是给用户展示漂亮清单，而是让 Agent 把长任务外化成状态：

```text
Todo:
  id
  content
  status: pending / in_progress / completed
```

它解决三个问题：

- 防止长任务中忘记目标。
- 让用户看到进度。
- 为后续任务调度提供结构。

TodoWrite 的关键约束是：同一时间只能有一个 `in_progress`。这会迫使 Agent 明确当前焦点。

## 12.3 Task DAG：从清单到依赖图

Todo 是线性清单，但真实任务常有依赖：

```text
调研 API
  -> 修改后端
  -> 修改前端
  -> 写测试
  -> 更新文档

调研现有设计
  -> 评估方案 A
  -> 评估方案 B
  -> 决策
```

Task DAG 让系统表达：

- 哪些任务可以并行。
- 哪些任务必须等待依赖完成。
- 哪些任务失败会阻塞后续。
- 哪些任务可重试或替代。

这和 LangGraph 的状态图相近，但 Task DAG 更偏执行计划，LangGraph 更偏运行流程。

## 12.4 Subagent：上下文隔离的工作单元

Subagent 的价值在于隔离。

主 Agent 不应该把所有探索过程都塞进自己的上下文。对于独立子任务，可以派生子 Agent：

```text
Lead:
  请检查认证模块的错误处理，返回问题列表和证据路径。

Subagent:
  只读取认证相关文件。
  不修改代码。
  返回结构化发现。

Lead:
  综合多个 subagent 结果，决定下一步。
```

Subagent 应该有：

- 明确任务。
- 限定上下文。
- 限定工具。
- 限定输出格式。
- 最大轮次。
- 结果归档。

不能把“你自己看着办”丢给 subagent。委托越清楚，结果越可用。

## 12.5 三种 Agent 派生模式

Harness Engineering 总结了几种模式：

| 模式 | 特点 | 适合场景 |
| --- | --- | --- |
| 标准子 Agent | 受 Lead 派生，完成局部任务 | 文件搜索、局部分析 |
| Fork 模式 | 共享部分上下文，独立探索 | 方案比较、侧问题 |
| Coordinator | 负责分派和综合多个 agent | 大型研究或并行任务 |

Fork 模式要防递归。如果 subagent 又无限派生 subagent，系统会失控。

Coordinator 模式要特别强调：Coordinator 必须自己综合所有结果，不能把综合再委托出去。因为只有它看到全局。

## 12.6 验证 Agent：不要自己审自己

实现者天然倾向于相信自己的改动。验证 Agent 的价值是独立视角。

Verifier 可以做：

- 代码审查。
- 安全审查。
- 测试缺口检查。
- 事实核对。
- 方案反驳。
- 输出格式检查。

好的 Verifier prompt 应该只读、挑剔、证据优先：

```text
你是验证 Agent。不要修改文件。
只报告有证据的问题。
按严重程度排序。
如果没有发现问题，明确说明剩余风险。
```

验证不是形式，而是降低自我确认偏差。

## 12.7 多 Agent 通信：共享状态还是消息协议

多 Agent 协作有两种基本通信方式：

```text
共享状态:
  所有角色读写同一个 state。
  适合 LangGraph、游戏、流程协作。

消息协议:
  Agent 之间通过任务、报告、mailbox 通信。
  适合异步团队和长任务。
```

共享状态要防止字段污染。消息协议要防止信息丢失和重复。

一个结构化报告可以包含：

```text
status: success / blocked / failed
summary:
evidence:
files_read:
risks:
next_recommendation:
```

不要让 subagent 只返回一段散文，否则 Lead 很难综合。

## 12.8 Team：角色不是装饰

Alice 的多 Agent 和“活人感”章节强调角色设计。角色不是为了好玩，而是为了稳定行为边界。

例如：

- Researcher：只做资料收集。
- Architect：负责方案结构。
- Executor：实现代码。
- Reviewer：找问题。
- Writer：整理文档。

每个角色应该有：

- 职责。
- 禁止事项。
- 可用工具。
- 输出格式。
- 交接协议。

角色越清晰，协作越稳定。

## 12.9 Worktree 隔离

多 Agent 如果都改同一个工作区，很容易冲突。

Worktree 隔离的思路：

```text
Lead workspace:
  用户主工作区。

Agent workspace A:
  方案 A 实验。

Agent workspace B:
  方案 B 实验。

Merge / Review:
  Lead 比较结果，选择合并。
```

它适合：

- 并行实现多个方案。
- 让验证 Agent 在干净环境运行测试。
- 避免子 Agent 误改用户工作区。

但 worktree 也带来成本：依赖安装、环境变量、端口、数据库、临时文件都要隔离。

## 12.10 多 Agent 的失败模式

常见失败：

- 委托任务太模糊。
- 子 Agent 工具权限过大。
- Lead 没有综合，只拼接结果。
- 多个 Agent 重复做同一件事。
- 验证 Agent 读取了不完整上下文。
- 多工作区改动无法合并。
- Agent 之间互相等待。

防护方式：

- 任务要小而明确。
- 输出要结构化。
- 工具权限按角色最小化。
- Lead 保留全局计划。
- 关键结论要求证据路径。
- 并行任务要有超时和取消。

## 12.11 最小实现建议

第一版可以这样做：

1. 实现 TodoWrite。
2. 支持 `task` 工具，派生只读 subagent。
3. Subagent 输入必须包含目标、范围、输出格式。
4. Subagent 输出结构化报告。
5. Lead 负责综合，不把综合外包。
6. 对关键实现增加 verifier。
7. 并行任务限制数量。
8. 大改动再引入 worktree 隔离。

## Hello-Agents 融合补充

`hello-agents` 第 6 章把 AutoGen、AgentScope、CAMEL、LangGraph 放在多 Agent 框架视角下讲解，能补足本章的“工程选择”问题。多 Agent 不只有一种组织方式：

- 对话协作：多个角色通过消息轮流推进。
- 图式协作：不同节点负责不同步骤，状态在图中流转。
- 任务分解：Lead 拆任务，子 Agent 独立执行，再汇总。
- 环境仿真：多个智能体在共享世界中行动、记忆和互动。

第 13 章的智能旅行助手用角色分工来做产品任务：规划、预算、景点、交通、住宿等能力可以拆成不同模块。第 14 章的自动化深度研究智能体则更接近任务系统：TODO 驱动、搜索、笔记、工具注册、报告生成，强调从目标到证据再到报告的链路。第 15 章的赛博小镇是另一类多 Agent：重点不是完成一个任务，而是维持一个多人格、多记忆、多关系的长期环境。

这些案例说明，多 Agent 的本质不只是“让多个模型互相聊天”，而是为复杂系统建立分工边界。每个 Agent 应该有明确输入、输出、状态、工具权限和失败处理。没有边界的多 Agent 会把单 Agent 的不可控放大；有边界的多 Agent 才能把复杂任务拆成可验证的小单元。

第 16 章和共创项目还给出毕业设计与项目模板，这对多 Agent 学习很有价值：如果一个项目无法写清楚 README、依赖、运行方式、数据结构和演示 Notebook，往往说明 Agent 分工也还没有想清楚。

## 系统地图

```text
Lead Agent
  -> Todo / Task DAG
  -> Subagent A
  -> Subagent B
  -> Verifier
  -> Synthesis
  -> User

Isolation
  -> Context
  -> Tools
  -> Permissions
  -> Worktree
```

## 共同结论

1. 多 Agent 的核心是分工、隔离和综合，不是数量。
2. Lead 必须对最终结论负责。
3. Subagent 要小任务、少上下文、明确输出。
4. 验证 Agent 可以降低自我确认偏差。
5. Worktree 是并行修改的安全边界，但不是一开始就需要。

## 本章自检

1. TodoWrite 和 Task DAG 分别解决什么问题？
2. Subagent 为什么要限制上下文和工具？
3. Coordinator 为什么不能把综合工作再委托出去？
4. Verifier 的只读约束有什么价值？
5. Worktree 隔离适合什么时候引入？

## 开放性问题

1. 一个复杂任务应该拆成几个 subagent？判断“拆得太细”和“拆得不够”的标准是什么？
2. 如果两个 subagent 给出相反结论，Lead 应该如何决策？
3. 多 Agent 协作中，哪些信息应该共享，哪些信息应该隔离？

## 原文入口

- [learn-claude-code s05: TodoWrite](../../source/learn-claude-code/s05_todo_write/README.md)
- [learn-claude-code s06: Subagent](../../source/learn-claude-code/s06_subagent/README.md)
- [learn-claude-code s12: Task System](../../source/learn-claude-code/s12_task_system/README.md)
- [learn-claude-code s15: Agent Teams](../../source/learn-claude-code/s15_agent_teams/README.md)
- [learn-claude-code s16: Team Protocols](../../source/learn-claude-code/s16_team_protocols/README.md)
- [learn-claude-code s17: Autonomous Agents](../../source/learn-claude-code/s17_autonomous_agents/README.md)
- [learn-claude-code s18: Worktree Isolation](../../source/learn-claude-code/s18_worktree_isolation/README.md)
- [Alice 方法论: 多 Agent](../../source/Alice_methodology/chapters/06-multi-agent.md)
- [Alice 多 Agent 博客](../../source/Alice_methodology/blog/blog-05-multi-agent.md)
- [Hermes: Delegation](../../source/hermes-book/src/part3/ch09-delegation.md)
- [Harness Engineering Ch20: Agent 派生与编排](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20.md)
- [Claude Code 分析: Multi-Agent](../../source/claude-code-analysis/analysis/04h-multi-agent.md)
- [easy-langent Ch07: LangGraph 多智能体](../../source/easy-langent/docs/guide/chapter7.md)
- [hello-agents Ch06: 框架开发实践](../../source/hello-agents/docs/chapter6/第六章%20框架开发实践.md)
- [hello-agents Ch13: 智能旅行助手](../../source/hello-agents/docs/chapter13/第十三章%20智能旅行助手.md)
- [hello-agents Ch14: 自动化深度研究智能体](../../source/hello-agents/docs/chapter14/第十四章%20自动化深度研究智能体.md)
- [hello-agents Ch15: 构建赛博小镇](../../source/hello-agents/docs/chapter15/第十五章%20构建赛博小镇.md)
- [hello-agents Ch16: 毕业设计](../../source/hello-agents/docs/chapter16/第十六章%20毕业设计.md)
- [hello-agents 共创项目](../../source/hello-agents/Co-creation-projects/README.md)
