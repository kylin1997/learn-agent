# 第 5 章：会话与上下文管理

> 本章目标：只讨论 Session 与 Context，不再混入长期记忆。读完本章，你应该能区分“完整会话记录”和“本次模型调用看到的上下文”，并能设计一套会话持久化、上下文预算、工具结果落盘、分层压缩和恢复机制。

## 5.1 先把三个概念分开

Agent 学习里最容易混的是 Session、Context、Memory。上一版把它们放在一章里，确实会让重点变浅。这里先只处理前两个：

```text
Session:
  一次任务或对话的完整事件记录。
  关注“发生过什么”。

Context:
  某一次模型调用实际看到的输入窗口。
  关注“现在应该让模型看什么”。

Memory:
  跨会话仍然有用的知识。
  关注“未来还会用到什么”。
```

本章只讲 Session 与 Context。Memory 会在下一章单独展开。

它们的关系是：

```text
完整会话事件流
  -> Session Store 持久保存
  -> Context Manager 选择、裁剪、压缩、预算控制
  -> LLM 当前调用看到的上下文
  -> 新的 assistant/tool/user 事件追加回 Session Store
```

一个常见误区是把 session messages 直接等同于 context messages。小 demo 可以这样做，但真实 Agent 不行。因为 session 越长越完整，context 却必须越短越精确。

## 5.2 为什么上下文是 Agent 的第一瓶颈

LLM 调用本质上是无状态的。它每次只知道你传给它的 system prompt、messages、tools 和附加输入。所谓“模型记得前文”，其实是你把前文重新塞进了上下文窗口。

Agent 比普通聊天更容易撑爆上下文：

- 工具调用会产生大量输出。
- 代码任务会读取很多文件。
- 搜索、grep、日志、测试失败信息都可能很长。
- 多轮任务会累积计划、发现、错误和修复尝试。
- 子 Agent、后台任务、Cron 任务也会产生中间结果。
- 用户希望它能连续工作几十分钟甚至几小时。

如果什么都不处理，很快会遇到 `prompt_too_long` 或成本失控。更麻烦的是：简单截断会丢掉任务目标、权限约束、关键决策和已完成步骤，模型看似还在继续，方向已经偏了。

所以，上下文管理不是优化项，而是 Agent 的生存能力。

## 5.3 Session Store：先完整保存，再决定给模型看什么

上下文压缩不等于删除历史。可靠系统通常会把完整 session 保存下来，再从中构造当前上下文。

最小可行方案是 append-only JSONL：

```jsonl
{"type":"user","content":"帮我分析这个项目"}
{"type":"assistant","content":[{"type":"tool_use","name":"glob","input":{"pattern":"**/*.py"}}]}
{"type":"tool_result","tool_use_id":"toolu_01","content":"..."}
{"type":"assistant","content":"我找到入口文件..."}
```

JSONL 的好处：

- 追加写入，崩溃时不容易损坏整个文件。
- 可以按行重放恢复会话。
- 大文件不必一次性 parse。
- 容易审计、调试和导出。
- 可以把事件流和模型上下文解耦。

`claw0` 的会话教程和 Claude Code 分析都强调类似观点：session storage 更像 append-only transcript，而不是简单的 messages 数组。

一个更完整的 session event 至少应该包含：

| 字段 | 含义 |
| --- | --- |
| `id` | 事件唯一标识 |
| `session_id` | 所属会话 |
| `timestamp` | 发生时间 |
| `role/type` | user、assistant、tool_use、tool_result、system_event |
| `content` | 原始内容或结构化 block |
| `metadata` | 模型、token、工具名、耗时、错误、权限状态 |
| `parent_id` | 可选，用于并行工具或子任务关联 |

学习阶段不必一开始就做数据库，但要先建立一个原则：**Session 是事实记录，Context 是运行时选择。**

## 5.4 Context Manager：模型调用前的编辑器

Context Manager 的目标不是保留最多内容，而是保留下一步最有用的内容。

它的输入包括：

- 当前用户请求。
- 最近几轮对话。
- 初始任务目标和关键约束。
- 当前计划和任务状态。
- 工具调用结果。
- 已读文件和文件摘要。
- 项目规则、Skill、相关记忆索引。
- 压缩摘要。
- token 预算和模型上下文窗口。

它的输出是一次模型调用的 messages、system sections、tool definitions 和 attachments。

可以把 Context Manager 想成模型调用前的编辑器：

```text
Session Store
  -> 读取完整历史和近期事件
  -> 识别不可丢信息
  -> 处理工具大输出
  -> 应用 token 预算
  -> 注入摘要和近期状态
  -> 构造本次 LLM 输入
```

这里的关键是“不可丢信息”。例如：

- 用户最初的任务目标。
- 用户明确说过的限制，比如“不要联网”“不要改数据库”。
- 当前工作目录和项目边界。
- 已经完成的关键步骤。
- 失败原因和下一步计划。
- 最近一两轮完整交互。

如果这些丢了，模型可能还会输出内容，但它已经没有稳定方向。

## 5.5 为什么不能简单删除最旧消息

最简单的策略是：超过 token 限制就删掉最旧消息。

这很危险，因为最旧消息里经常有任务锚点：

```text
用户第一轮：
“帮我把这个项目的 Agent 教程融合成一套教材，不能遗漏 9 个目录内容。”
```

如果上下文很长后删掉这条，模型可能继续写文章，却忘了“不能遗漏 9 个目录内容”这个核心约束。

更好的思路是按信息类型处理：

| 信息类型 | 处理方式 |
| --- | --- |
| 初始目标和硬约束 | 保留或写入结构化摘要 |
| 最近几轮对话 | 尽量原样保留 |
| 旧工具结果 | 占位、摘要或落盘 |
| 大文件内容 | 落盘，只留路径、摘要、预览 |
| 重复读取结果 | 只保留最新或最相关的一次 |
| 早期探索路径 | 压缩成结论 |
| 临时错误 | 保留当前相关错误，旧错误摘要化 |

上下文管理的本质不是“删旧”，而是“把不同信息放到合适的层次”。

## 5.6 Token 预算：内容进入上下文前就要拦截

很多人以为上下文管理就是“满了再压缩”。但更稳的做法是：内容进入上下文前就控制大小。

Claude Code 分析里的 token 预算策略很有代表性：

```text
单工具结果级别：
  超过阈值的大结果持久化到磁盘，只给模型预览。

单消息级别：
  一轮并行工具结果总量不能无限增长。

全局 token 级别：
  根据模型窗口、输出预算、系统 prompt 大小，计算剩余可用输入。
```

为什么这很重要？

假设一个 grep 返回 80KB，另一个测试日志 120KB，再加上几个文件读取结果。它们可能都来自“正常工具调用”，但合起来会立刻吃掉上下文窗口。等到 API 报错再处理，已经晚了。

一个实用预算模型：

```text
总上下文窗口
  - 最大输出 token 预留
  - system prompt / tools token
  - 最近对话保留预算
  - 当前用户请求预算
  = 可分配给历史和工具结果的预算
```

工具结果预算可以分两层：

```text
单个结果超过阈值：
  写入 .task_outputs/tool-results/<tool_use_id>.txt
  context 中只放路径 + 前若干字符预览

一轮结果总量超过阈值：
  按大小排序，先持久化最大的结果
  直到总量降到预算内
```

Read 工具、图片、PDF 这类输入要单独处理。比如文件读取工具通常有自己的 offset/limit，不一定适合走通用“持久化后再读取”的路径，否则可能让模型陷入读持久化文件的循环。

## 5.7 工具结果落盘：保留可追溯性，而不是塞满窗口

大工具输出不应该直接进入上下文。更好的模式是：

```xml
<persisted-output>
Output too large. Full output saved to:
  .task_outputs/tool-results/toolu_01.txt

Preview:
前 2000 字符...
</persisted-output>
```

这样模型仍然知道：

- 工具执行过。
- 输出很大。
- 完整内容在哪里。
- 预览里有什么线索。
- 如果确实需要，可以再读取目标文件。

这比直接截断安全，也比全量塞入上下文便宜。

但落盘有两个注意点：

**第一，路径要稳定可读。**  
模型看到的路径必须在可访问范围内，否则它只知道“有文件”，但无法继续使用。

**第二，替换状态要稳定。**  
如果某个工具结果第一次给模型看的是完整内容，后续突然变成预览，会破坏上下文一致性，也可能影响 prompt cache。真实系统通常会记录哪些结果已经被模型看过，哪些已经替换成落盘引用。

## 5.8 分层压缩：便宜的先跑，贵的后跑

`learn-claude-code` s08 和 Alice 方法论都强调分层压缩。核心思想是：

**能用规则解决的，不要先调用 LLM；只有需要语义理解时才调用 LLM。**

可以设计四层：

```text
L1 Snip
  裁掉中间一部分旧消息，保留开头任务和结尾近期状态。

L2 Micro Compact
  对旧工具结果做占位，保留最近几个完整结果。

L3 Tool Result Budget
  大结果落盘，上下文里只留摘要、预览和路径。

L4 LLM Summary / Auto Compact
  调用模型生成结构化摘要，替换大量历史。
```

实际执行顺序通常不是 L1 到 L4。大结果落盘要尽早做，否则旧结果先被占位后，完整内容就没机会保存了。一个更实用的顺序是：

```text
1. Tool Result Budget：先把大输出落盘。
2. Snip：裁掉安全的中间历史。
3. Micro Compact：旧工具结果占位。
4. Token Check：仍然超阈值时进入 LLM Summary。
5. Reactive Compact：API 仍报 prompt_too_long 时应急压缩。
```

这个顺序体现了一个工程判断：先保全信息，再减少上下文。

## 5.9 Snip：裁中间，不裁锚点

Snip 是最轻量的压缩：当消息数量太多时，保留开头几条和结尾若干条，中间替换成占位。

```text
[初始任务、关键约束]
[snipped 48 messages from conversation middle]
[最近对话、当前状态]
```

它适合处理长会话里已经不再重要的早期探索过程。

但 Snip 有两个边界：

**第一，不能裁掉任务锚点。**  
开头的用户目标和硬约束应该保留，或者先被写入摘要。

**第二，不能拆开 tool_use / tool_result。**  
很多模型 API 要求 assistant 的 tool_use 后面必须有对应 tool_result。如果裁剪时留下孤立的 tool_result 或孤立的 tool_use，下一次请求可能直接无效。

所以 Snip 不是简单数组切片，而是消息结构感知的裁剪。

## 5.10 Micro Compact：旧工具结果占位

工具结果通常是上下文膨胀的主因。Micro Compact 的思路是：保留最近少量工具结果，旧结果替换成占位。

```text
[Earlier tool result compacted. Re-run or read persisted output if needed.]
```

为什么可以这样做？因为旧工具结果的价值通常有衰减：

- 如果结果重要，后续应该已经被模型总结或使用。
- 如果只是探索，保留完整内容价值不大。
- 如果需要重新确认，可以重新调用工具或读取落盘文件。

Micro Compact 不需要 LLM，成本低、可预测。但它不能替代摘要，因为它不理解语义，只是减少体积。

## 5.11 LLM Summary：把历史压成状态

当规则压缩仍然不够时，才调用 LLM 做摘要。

摘要不应该是自由文本，而应该是结构化状态。Alice 的 9 节格式很实用：

```markdown
## 当前任务
## 工作目录
## 进行中的工作
## 挂起的决策
## 最近完成的工作
## 发现的关键信息
## 遇到的问题
## 用户偏好
## 下一步行动
```

这 9 节本质上是“会话恢复协议”。压缩后的 Agent 不需要知道每一句话，但必须知道：

- 用户到底要什么。
- 当前做到哪了。
- 哪些事已经做过。
- 哪些决策不能丢。
- 下一个动作是什么。

一个好的压缩 prompt 应明确禁止工具调用：

```text
你是上下文压缩器。你的职责是把对话历史压缩为结构化摘要。
本任务中只能输出文本，不能调用任何工具。
不要新增事实，不要改变用户约束，不要删除关键路径和文件名。
```

这类专项 prompt 要和主 Agent prompt 隔离。

## 5.12 压缩的递归与互斥陷阱

压缩本身可能调用 LLM。如果不加保护，就会出现递归：

```text
主对话上下文太长
  -> 触发压缩
    -> 压缩调用 LLM
      -> 压缩调用本身也被识别为上下文太长
        -> 再次触发压缩
```

所以压缩系统必须有显式状态：

- `is_compacting = true` 时不能再次触发 compact。
- compact 调用不能使用普通工具。
- compact 失败要有重试上限。
- 多个压缩策略不能同时改同一份消息列表。
- reactive compact 不能无限重试。

这些问题在小 demo 里几乎看不出来，但在生产长任务里一定会遇到。症状通常很难排查：摘要重复、工具结果断裂、消息结构损坏、任务突然失忆。

## 5.13 Reactive Compact：API 报错后的应急路径

即使有预算和预压缩，仍然可能遇到 API 返回上下文过长。原因包括：

- token 估算不准。
- provider 的计数方式和本地估算不同。
- 工具结果在最后一轮突然暴涨。
- system prompt、tools、attachments 额外占用预算。

这时需要 reactive compact：收到 `prompt_too_long` 后，执行更激进的压缩，然后重试一次。

一个合理策略：

```text
1. 保存完整 transcript。
2. 保留最近少量消息。
3. 对更早部分生成结构化摘要。
4. 保证 tool_use / tool_result 成对。
5. 重试 API 调用。
6. 只允许有限次数重试。
```

Reactive compact 是安全网，不应该成为常规路径。如果经常触发，说明前面的预算和压缩阈值需要调整。

## 5.14 会话恢复：Resume 不是把所有历史塞回去

Resume 的目标不是把完整 session 原样塞回上下文，而是恢复足够状态，让 Agent 能继续工作。

恢复时可以分三层：

```text
完整 transcript:
  永久保存，用于审计、回放、调试。

session summary:
  压缩后的当前状态，用于恢复工作。

recent tail:
  最近若干轮完整消息，用于保留局部细节。
```

恢复后的上下文可能长这样：

```text
[System Prompt]
[Session Summary: 9 sections]
[Recent Messages: last N turns]
[Current User Request]
```

如果用户问“刚才做了什么”，可以从 summary 和 recent tail 回答；如果需要追溯更早细节，再读取 transcript，而不是一开始就全量注入。

## 5.15 Context 与 Memory 的边界

虽然本章不展开长期记忆，但需要先把边界讲清：

| 信息 | 放在 Context / Session | 放在 Memory |
| --- | --- | --- |
| 当前任务下一步 | 是 | 否 |
| 本轮工具输出 | 是 | 通常否 |
| 任务中间状态 | 是 | 否 |
| 用户长期偏好 | 可临时出现 | 是 |
| 项目长期约定 | 可注入 | 是 |
| 过去踩过的长期坑 | 可召回 | 是 |
| 临时错误日志 | 是，或落盘 | 否 |
| 可复用流程 | 可在当前任务出现 | Skill 或 Memory |

判断标准：

**这条信息是当前任务需要，还是未来也会稳定有用？**

当前任务需要的是 context；未来稳定有用的才进入 memory。

## 5.16 最小实现建议

如果你要实现会话与上下文管理，第一版可以这样做：

1. 用 JSONL 保存完整 session event。
2. 每次模型调用前从 session 构造 context，而不是直接传全量历史。
3. 保留初始任务、硬约束和最近若干轮。
4. 给工具结果设置单结果和单轮总量预算。
5. 大工具结果落盘，只在上下文里放路径和预览。
6. 对旧工具结果做占位。
7. 超过阈值时生成 9 节结构化摘要。
8. 压缩调用禁止工具，并加 `is_compacting` 互斥。
9. API 报上下文过长时做一次 reactive compact。
10. Resume 时加载 summary + recent tail，而不是完整 transcript。

不要一开始就做复杂检索。先把 session、context、compact 三者边界理清，系统就已经比大多数 demo 稳很多。

## 系统地图

```text
User / Tool / Assistant Events
  -> Session Store
      保存完整 transcript
      支持恢复、审计、调试

Context Manager
  -> 读取 session
  -> 保留任务锚点和近期状态
  -> 应用工具结果预算
  -> 执行 snip / micro compact / summary
  -> 输出本次 LLM 调用上下文

LLM Call
  -> 产生新消息或工具调用
  -> 追加回 Session Store
```

## 共同结论

这一主题在 9 份教程里的共同结论是：

1. Session 和 Context 不是一回事：前者要完整，后者要精确。
2. 上下文管理要从入口预算开始，而不是等到报错才压缩。
3. 压缩应该分层：规则优先，LLM 摘要最后使用。
4. 压缩是专项任务，必须有互斥、禁工具和失败熔断。
5. Resume 依赖 summary + recent tail，而不是把完整历史重新塞回模型。

## Hello-Agents 融合补充

`hello-agents` 第九章把“上下文工程”讲得更系统：上下文不是单纯的窗口容量问题，而是有效信息的选择、写入、压缩和隔离问题。它的 `ContextBuilder` 把对话历史、任务、记忆、工具信息组合成可控上下文；`NoteTool` 则把任务状态、阻塞点、阶段总结等中间状态结构化保存，避免一切都堆在 messages 里。

Extra02 还补充了上下文工程的四类风险：Context Poisoning、Context Distraction、Context Confusion、Context Clash。放到本章里，它们分别对应“错误信息进入上下文”“上下文太多稀释注意力”“无关信息干扰判断”“上下文片段互相冲突”。这让我们判断压缩策略时不只看 token 数，还要看上下文质量。

## 本章自检

1. Session 和 Context 的区别是什么？
2. 为什么完整保存历史不等于让模型看到完整历史？
3. 为什么不能简单删除最旧消息？
4. 工具结果为什么要在进入上下文前做预算？
5. 大工具结果落盘后，模型还需要看到哪些信息？
6. Snip 为什么不能拆开 tool_use / tool_result？
7. LLM Summary 为什么应该使用结构化格式？
8. 压缩为什么会递归？如何防止？
9. Reactive Compact 适合什么时候触发？
10. Resume 为什么不是全量恢复？

## 开放性问题

1. 上下文压缩时，哪些信息宁愿多花 token 也不能丢？你会如何识别这些信息？
2. 如果压缩摘要和原始 transcript 发生冲突，恢复会话时应该相信谁？
3. 工具结果落盘后，模型需要具备怎样的“重新读取”能力，才能不因为预览而误判？

## 原文入口

- [learn-claude-code s08: Context Compact](../../source/learn-claude-code/s08_context_compact/README.md)
- [Hello-Agents Ch09: 上下文工程](../../source/hello-agents/docs/chapter9/第九章%20上下文工程.md)
- [Hello-Agents Extra02: 上下文工程补充知识](../../source/hello-agents/Extra-Chapter/Extra02-上下文工程补充知识.md)
- [Hello-Agents Extra09: 上下文不是内存容量问题](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)
- [Alice 方法论: 上下文与记忆](../../source/Alice_methodology/chapters/05-context-memory.md)
- [claw0 s03: 会话与上下文保护](../../source/claw0/sessions/zh/s03_sessions.md)
- [claw0 s06: 智能层](../../source/claw0/sessions/zh/s06_intelligence.md)
- [Hermes: SessionDB](../../source/hermes-book/src/part4/ch10-session-db.md)
- [Hermes: 上下文压缩](../../source/hermes-book/src/part4/ch12-context-compression.md)
- [Harness Engineering: 自动压缩](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch09.md)
- [Harness Engineering: 微压缩](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch11.md)
- [Harness Engineering: Token 预算策略](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch12.md)
- [Claude Code 分析: Context 管理](../../source/claude-code-analysis/analysis/04f-context-management.md)
- [Claude Code 分析: Session Storage / Resume](../../source/claude-code-analysis/analysis/04i-session-storage-resume.md)
