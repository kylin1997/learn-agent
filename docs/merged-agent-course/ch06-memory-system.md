# 第 6 章：长期记忆系统

> 本章目标：把 Memory 从“保存聊天记录”升级为“跨会话的知识管理系统”。读完本章，你应该能判断什么值得记、记在哪里、何时写入、如何召回、如何去重整理，以及为什么长期记忆必须和会话上下文分开设计。

## 6.1 长期记忆解决的不是上下文太长

上下文压缩解决的是当前会话太长的问题。长期记忆解决的是另一个问题：

**哪些信息在未来的会话里仍然有价值？**

这两件事经常被混在一起，但它们的目标完全不同：

```text
Context Compact:
  当前会话放不下了。
  把旧历史压缩成当前可继续工作的状态。

Memory:
  新会话也应该记得。
  把稳定偏好、项目约定、设计决策、排查经验保存下来。
```

如果把压缩摘要当长期记忆，会把大量临时任务进度存进去，污染未来上下文。反过来，如果只做长期记忆，不做上下文压缩，长任务仍然会撑爆窗口。

所以 Memory 必须独立成章。

## 6.2 什么是值得保存的记忆

长期记忆不是聊天记录仓库。它应该保存“未来仍然有用，而且不容易从当前文件直接推导出来”的知识。

适合保存：

- 用户稳定偏好：语言、风格、沟通粒度、工作习惯。
- 项目特殊约定：目录结构、命名规范、部署规则、测试入口。
- 非显而易见的设计决策：为什么选 A 而不是 B。
- 反复出现的反馈：用户多次强调的做事方式。
- 排查经验：某个库版本有坑、某条命令不能用、某个服务需要特殊环境。
- 常用入口：文档在哪、脚本在哪、调试流程是什么。
- 可复用流程：某类任务通常怎么处理。

不适合保存：

- 临时任务进度：正在改第 3 个文件。
- 可以从代码直接查到的事实：某函数当前有 20 行。
- 高频变化数据：今天的测试失败数、当前分支状态。
- AI 自己的系统提示：这是 Prompt Runtime 的职责。
- 未确认的敏感隐私：尤其是个人身份、密钥、账号、健康、财务等信息。
- 模型自己的猜测：未经验证的推断不应该沉淀成记忆。

一句判断标准：

**如果这条信息下周、下个月、下次打开项目时仍然能减少误解或重复探索，它才值得进入 Memory。**

## 6.3 Memory 与 Session Memory 的区别

learn-claude-code 和 Claude Code 分析里都能看到两类“记忆”：

| 类型 | 生命周期 | 解决问题 | 典型内容 |
| --- | --- | --- | --- |
| Session Memory | 单会话 | compact 后如何继续当前任务 | 当前目标、已完成步骤、下一步 |
| User / Project Memory | 跨会话 | 未来任务如何继承稳定知识 | 用户偏好、项目约定、历史坑 |

Session Memory 更接近上一章的会话摘要。它是当前任务的工作状态，不应该变成长期用户画像。

长期 Memory 更像知识库。它可以跨 session 被召回，也应该允许用户查看、编辑、删除和纠正。

如果不分开，会有两个后果：

- 临时状态污染长期记忆：以后每次都召回已经过期的“正在处理第 2 步”。
- 长期偏好被压缩丢失：用户说过多次“我喜欢中文教材风格”，但只存在旧 session 里。

## 6.4 多层记忆架构

Alice 提供了一个清晰的五层记忆模型：

```text
M1 在线上下文
  单次对话中的 messages 和当前状态。

M2 项目记忆
  项目级规则、约定、架构决策。

M3 向量记忆
  历史对话的语义化存储和召回。

M4 结构化存储
  会话列表、消息历史、设置、任务状态。

M5 用户画像
  用户身份、偏好、工作流、表达风格。
```

这五层不是为了显得复杂，而是因为不同信息的生命周期、读写频率和召回方式不同。

| 层 | 适合存什么 | 读取方式 | 风险 |
| --- | --- | --- | --- |
| M1 在线上下文 | 当前任务状态 | 每轮直接进入 context | 容量有限 |
| M2 项目记忆 | 项目约定、规则、决策 | 项目开始时注入或按需加载 | 文件膨胀、规则冲突 |
| M3 向量记忆 | 海量历史片段 | 相似度或 LLM 选择召回 | 语义相关不等于任务相关 |
| M4 结构化存储 | 会话、任务、设置 | 工具按需查询 | 需要 schema 维护 |
| M5 用户画像 | 稳定偏好和习惯 | 常驻或高优先级注入 | 隐私与过度泛化 |

学习阶段不需要一开始实现五层。但你要知道：长期记忆不是一种存储，而是一组按信息类型分工的机制。

## 6.5 文件系统记忆：最适合学习的起点

`learn-claude-code` s09 选择文件系统记忆，非常适合作为学习实现。

结构如下：

```text
.memory/
  MEMORY.md
  user-pref-language.md
  project-api-layout.md
  bug-lib-v2.md
```

每个记忆文件用 Markdown + YAML frontmatter：

```markdown
---
name: project-api-layout
description: API routes live under services/api
type: project
---

This project keeps API route handlers under `services/api`.

Why it matters:
- API behavior questions should inspect this directory first.
- Do not assume routes live under `app/api` unless the project structure changes.

How to apply:
- When debugging API behavior, start from `services/api`.
- If no relevant file exists there, inspect routing configuration before guessing.
```

`MEMORY.md` 是索引：

```markdown
- [project-api-layout](project-api-layout.md) — API routes live under services/api
- [user-pref-language](user-pref-language.md) — User prefers Chinese learning materials
```

文件系统记忆的优点：

- 透明：用户和开发者能直接看见。
- 可编辑：错误记忆可以手动修正。
- 易审计：每条记忆有独立文件。
- 易调试：不用先引入向量库和复杂检索。
- 适合项目级知识：和代码仓库一起维护很自然。

缺点也很明显：

- 文件多了需要索引和整理。
- 召回质量依赖 name / description。
- 不适合海量历史语义检索。
- 需要处理过期、重复和冲突。

所以文件系统是起点，不是终点。

## 6.6 记忆类型：不要把所有东西放进一个桶

learn-claude-code 把记忆分为四类，很适合作为第一版：

| 类型 | 回答的问题 | 示例 |
| --- | --- | --- |
| `user` | 用户是谁、偏好什么 | 用户喜欢中文、希望教材风格深入 |
| `feedback` | 用户如何评价你的工作方式 | 不要只给导读，要给完整融合文章 |
| `project` | 当前项目有什么长期约定 | `source/` 下 9 个目录是教程来源 |
| `reference` | 信息应该去哪里找 | Loop Engineering 来源是 runoob 章节 |

为什么要分类？

因为不同类型的记忆有不同使用方式。

`user` 记忆可能跨项目都有用，但要注意隐私和泛化边界。  
`project` 记忆只在当前项目有效。  
`feedback` 记忆可以调整协作风格。  
`reference` 记忆更像索引，不一定每次都要全文注入。

如果没有类型，所有记忆都会变成一堆“看起来相关”的文本，召回和应用都会变差。

## 6.7 记忆召回：索引常驻，正文按需

一个常见错误是把所有记忆全文都塞进 prompt。这样做很快会让 memory 本身成为上下文噪声。

更好的方式是两阶段：

```text
阶段一：常驻索引
  让模型知道有哪些记忆。
  索引短小，适合放进 system prompt 或动态 context。

阶段二：按需加载正文
  根据当前任务选择少量相关记忆。
  只把选中的正文注入本轮上下文。
```

例如：

```text
Memory Catalog:
- project-api-layout — API routes live under services/api
- user-pref-language — User prefers Chinese learning materials
- bug-lib-v2 — Avoid library v2 due to known issue

Current task:
Debug an API route returning 500.

Selected:
- project-api-layout
```

召回可以用三种方式：

| 方式 | 优点 | 缺点 |
| --- | --- | --- |
| 关键词匹配 | 简单、便宜、可解释 | 容易漏掉隐含相关 |
| 向量检索 | 适合大量历史 | 语义相关可能不等于任务相关 |
| LLM side-query | 能理解任务相关性 | 多一次调用，有成本和延迟 |

Claude Code 分析里有一个很有启发的选择：用模型根据记忆名称和描述做 side-query，选出最多少量相关记忆，而不是一开始就依赖 embedding。这个思路很适合 Agent，因为“任务相关”往往比“语义相似”更重要。

## 6.8 召回质量比召回数量更重要

记忆召回不是越多越好。召回过多会带来三个问题：

- 噪声变多，模型注意力分散。
- 过期或冲突记忆影响当前决策。
- token 成本上升，挤占真正任务上下文。

所以召回应该遵循：

```text
不确定就少选。
优先选高置信度、高相关、低过期风险的记忆。
每轮限制数量，例如最多 3-5 条。
正文长度限制，例如每条最多 200 行或若干 KB。
```

这和搜索结果很像。10 条一般相关的记忆，不如 2 条确切相关的记忆。

## 6.9 记忆写入：什么时候写比怎么存更难

记忆系统最难的不是存储，而是写入边界。

一个常见陷阱是：对话中每出现一句“有用的话”，就立刻写入 memory。

这会造成自我强化：

```text
模型刚生成一个猜测
  -> 写入记忆
  -> 下一轮召回这条“记忆”
  -> 模型把自己的猜测当成历史事实
  -> 继续强化
```

更好的写入时机是：

- 一轮任务结束后。
- stop hook 或收尾阶段异步触发。
- 从压缩前快照提取，避免 compact 丢信息。
- 写入前查看已有记忆，避免重复。
- 对不确定信息要求用户确认，或标记低置信度。

`learn-claude-code` 的教学版在每轮结束后提取；Claude Code 分析里则提到通过 stop hook fire-and-forget 触发提取和 Dream 整理。这些设计都在强调同一件事：**不要把记忆写入放在主推理过程中同步、无条件执行。**

## 6.10 记忆提取 Prompt：不是摘要，而是筛选

记忆提取不是“总结对话”。它要做的是筛选：哪些信息值得长期保存？

一个好的提取 prompt 应该包含：

```text
任务：
从对话中提取未来仍然有用的用户偏好、项目约定、反馈或参考入口。

只保存：
- 稳定偏好
- 项目特殊约定
- 非显而易见的设计决策
- 反复出现的反馈
- 可复用排查线索

不要保存：
- 临时任务进度
- 可以从代码直接查到的信息
- 未验证的猜测
- 敏感隐私
- 已有记忆覆盖的信息

输出 JSON 数组：
[{name, type, description, body}]

如果没有新记忆，输出 []。
```

它的输出应该结构化，方便程序写文件、去重和审计。

要特别注意：记忆提取 prompt 应该看到已有记忆索引。否则它会不断写入重复记忆。

## 6.11 记忆去重、冲突和过期

Memory 一旦长期运行，必然出现三类问题：

**重复。**  
用户多次表达同一偏好，系统写了多条相似记忆。

**冲突。**  
用户之前喜欢详细解释，现在希望简短；项目旧目录结构迁移了。

**过期。**  
某个 bug 只存在于旧版本库，后来升级后不再成立。

解决方式是低频整理，也就是 `Dream` 或 consolidation：

```text
触发条件：
- 距离上次整理超过一定时间。
- 最近有足够多新会话或新记忆。
- 当前没有其他整理任务运行。
- 拿到文件锁，防止并发写。

整理任务：
- 合并重复记忆。
- 标记或删除过期记忆。
- 解决冲突，保留更新版本。
- 重建 MEMORY.md 索引。
```

整理应该低频进行，因为它会改写长期知识库。越是长期的东西，越要谨慎。

对于冲突记忆，最好不要偷偷合并成一个模糊结论。例如：

```text
旧记忆：用户喜欢详细解释。
新记忆：用户现在要求最终回答更简洁。
```

更好的处理是保留时间和适用场景：

```text
用户在学习材料中喜欢深入解释；在任务完成汇报中偏好简洁摘要。
```

## 6.12 用户画像：身份、工作流、表达风格

Alice 把用户画像拆成三个维度：

- `identity.md`：用户是谁，领域、技术栈、背景。
- `workflow.md`：用户怎么工作，常用流程、协作习惯。
- `voice.md`：用户喜欢怎样沟通，语言、详略、语气。

这个拆分很有价值，因为三类信息更新频率不同。

身份信息通常稳定，但隐私风险最高。  
工作流偏好会随项目变化。  
表达风格可能在一次反馈后就要调整。

对于本项目，可能的用户画像记忆是：

```text
用户正在系统学习 Agent，希望基于 9 份教程融合成完整教材。
用户不希望只看导读，更希望看到可直接学习的汇总文章。
用户希望章节内容有深度，浅层概括不够。
用户希望结构是正文讲解 + 系统地图 + 共同结论 + 原文入口。
```

这些信息能显著影响后续写作质量，所以适合保存。但如果包含隐私身份或敏感信息，就需要更高门槛。

## 6.13 项目记忆：让 Agent 不必每次重新认识项目

项目记忆保存当前项目的长期事实和约定。

例如本项目可以有这样的 project memory：

```markdown
---
name: learn-agent-course-structure
description: The merged Agent course is built from 8 tutorial directories under source/
type: project
---

This project builds a merged Agent learning course from the 8 tutorial directories under `source/`.

Writing rules:
- The merged chapters should be complete learning articles, not reading guides.
- Each chapter should include source links.
- Overlapping topics across tutorials should be merged.
- Missing but necessary topics may be added from external sources.
- Loop Engineering is a standalone chapter after Gateway / channels / Cron / proactive agents.
```

这类记忆能减少重复解释，也能让下一次打开项目时延续当前约定。

项目记忆特别适合文件系统，因为用户可以直接审阅和修改。

## 6.14 记忆与隐私、安全

长期记忆有一个天然风险：它会让系统“记住”用户。记住得越多，越需要边界。

基本原则：

```text
默认少记。
敏感信息不自动记。
未经确认的个人信息不写入长期记忆。
允许用户查看、编辑、删除记忆。
每条记忆说明来源或原因。
记忆召回应限制范围，不跨项目滥用。
```

尤其要避免把以下内容自动写入：

- API key、token、密码。
- 身份证、地址、电话号码。
- 健康、财务、法律等高敏感信息。
- 用户没有明确希望长期保存的私密事实。

记忆系统不只是技术模块，也是信任系统。

## 6.15 记忆如何进入 Prompt Runtime

长期记忆最终要被模型使用，通常有三条路径：

```text
路径一：索引注入
  MEMORY.md 清单进入 system prompt 或动态 context。

路径二：相关正文注入
  当前任务选择少量记忆全文，进入 user turn 或 context section。

路径三：工具按需读取
  模型看到索引后，主动读取某条记忆文件。
```

索引适合稳定、短小、可缓存。正文适合按需加载。工具读取适合大记忆或不确定相关性。

这里要注意和第 3 章的 Prompt Runtime 配合：Memory section 不应该无脑常驻全文，否则 prompt 会越来越大。更好的设计是：

```text
Stable Prompt Prefix:
  Agent identity
  Operating principles
  Tool policy

Dynamic Context:
  Memory index
  Selected memory snippets
  Current session summary
```

记忆是上下文的一部分，但不是上下文本身。

## 6.16 文件记忆、向量记忆与结构化数据库如何组合

学习阶段可以只用文件系统。系统变大后，可以组合三种存储：

| 存储 | 适合内容 | 召回方式 |
| --- | --- | --- |
| Markdown 文件 | 项目规则、用户偏好、人工可读知识 | 索引 + LLM 选择 |
| 向量库 | 大量历史片段、语义检索 | embedding 相似度 + rerank |
| 数据库 | 会话、任务、设置、权限、状态 | 精确查询 |

不要把所有内容都向量化。向量检索适合“我记得以前聊过类似事情”，不适合“用户偏好最终回答要简洁”这种精确规则。

也不要把所有内容都写进结构化数据库。项目约定和设计决策需要可读性，Markdown 往往更合适。

正确问题不是“用哪种记忆技术最好”，而是：

**这类信息未来如何被使用？按这个使用方式选择存储。**

## 6.17 最小实现建议

如果你要实现第一版长期记忆系统，可以这样做：

1. 建立 `.memory/` 目录。
2. 每条记忆一个 Markdown 文件，带 `name`、`description`、`type` frontmatter。
3. 自动生成 `MEMORY.md` 索引。
4. 每轮开始只注入索引，不注入全部正文。
5. 根据当前任务选择最多 3-5 条相关记忆正文。
6. 选择失败时降级到关键词匹配。
7. 每轮结束后从压缩前快照提取新记忆。
8. 提取 prompt 必须看到已有索引，并允许输出空数组。
9. 记忆写入前做去重和类型校验。
10. 低频整理重复、冲突和过期记忆。
11. 敏感信息默认不自动写入。
12. 让用户可以直接查看和编辑记忆文件。

第一版不需要向量库。先把“什么该记、何时写、如何召回、如何删改”做好，后面再加 embedding 才有意义。

## 系统地图

```text
Conversation / Session Transcript
  -> Memory Extractor
      判断是否有长期价值
      输出结构化 memory candidates

Memory Store
  -> .memory/*.md
  -> MEMORY.md index
  -> optional vector DB / structured DB

Memory Retrieval
  -> 读取索引
  -> 选择相关记忆
  -> 注入 Prompt Runtime

Dream / Consolidation
  -> 去重
  -> 合并
  -> 处理冲突和过期
  -> 重建索引
```

## 共同结论

9 份教程在长期记忆上的共同结论可以合并成五点：

1. Memory 不是 session 历史，也不是 context compact。
2. 记忆只保存未来稳定有用的信息，不保存临时任务状态。
3. 最好的学习起点是文件系统记忆：透明、可编辑、易调试。
4. 召回应少而准：索引常驻，正文按需。
5. 记忆写入和整理比存储更难，必须处理重复、冲突、过期和隐私。

## Hello-Agents 融合补充

`hello-agents` 第八章把记忆与检索放在同一章讨论，补充了本章需要的应用层视角：它区分工作记忆、情景记忆、语义记忆和感知记忆，并用 `MemoryTool`、`MemoryManager`、RAG 工具和向量数据库展示“记住用户事实”和“检索外部知识”如何协同。它还把遗忘机制讲得很具体：可以基于重要性、时间或容量删除记忆，也可以把工作记忆转化为情景记忆，再从情景记忆提炼语义记忆。

这给本章一个很重要的补充：长期记忆不仅要考虑“写入什么”，还要考虑“如何遗忘”和“如何升级”。不是所有记忆都永久存在，记忆系统应当有生命周期。

## 本章自检

1. 长期记忆和上下文压缩分别解决什么问题？
2. 什么信息值得写入 Memory？什么不应该写？
3. Session Memory 和 User / Project Memory 有什么区别？
4. 为什么索引应该常驻，而正文应该按需加载？
5. LLM side-query 选择记忆相比向量检索有什么优势？
6. 为什么不能在对话中即时把所有内容写入记忆？
7. 记忆提取 prompt 和摘要 prompt 有什么区别？
8. Dream / consolidation 解决哪些问题？
9. 用户画像为什么可以拆成 identity、workflow、voice？
10. 为什么记忆系统也是隐私和信任系统？

## 开放性问题

1. 记忆系统应该默认自动写入，还是默认等待用户确认？不同产品场景下答案会如何变化？
2. 当旧记忆和新反馈冲突时，系统应该覆盖、合并、保留版本，还是询问用户？
3. 你如何判断一条“项目事实”应该存在 Memory 中，而不是每次从代码里重新读取？

## 原文入口

- [learn-claude-code s09: Memory](../../source/learn-claude-code/s09_memory/README.md)
- [Hello-Agents Ch08: 记忆与检索](../../source/hello-agents/docs/chapter8/第八章%20记忆与检索.md)
- [Hello-Agents Ch15: 赛博小镇记忆系统](../../source/hello-agents/docs/chapter15/第十五章%20构建赛博小镇.md)
- [Alice 方法论: 上下文与记忆](../../source/Alice_methodology/chapters/05-context-memory.md)
- [Alice 博客: 分层记忆](../../source/Alice_methodology/blog/blog-04-memory-system.md)
- [Hermes: Memory Provider](../../source/hermes-book/src/part4/ch11-memory-provider.md)
- [Harness Engineering: 跨会话记忆](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch24.md)
- [Claude Code 分析: Agent Memory](../../source/claude-code-analysis/analysis/04-agent-memory.md)
- [Claude Code 分析: Context 管理](../../source/claude-code-analysis/analysis/04f-context-management.md)
- [Claude Code 分析: Session Storage / Resume](../../source/claude-code-analysis/analysis/04i-session-storage-resume.md)
