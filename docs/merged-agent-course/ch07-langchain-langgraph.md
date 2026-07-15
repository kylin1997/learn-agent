# 第 7 章：LangChain 与 LangGraph 应用开发

> 本章目标：把前面几章的 Agent 基础能力落到应用框架中。读完本章，你应该能理解 LangChain 解决的是“组件化调用”，LangGraph 解决的是“有状态流程控制”，并能判断什么时候用链、什么时候用图、什么时候应该回到自己实现的 Agent Loop。

## 7.1 框架不是 Agent 的本质

学习 Agent 时很容易被框架牵着走：LangChain、LangGraph、RAG、Tool、Memory、AgentExecutor、StateGraph。框架很重要，但它不是 Agent 的本质。

前几章已经建立了底层心智：

- Agent 是由模型、工具、状态、循环、权限和上下文组成的执行系统。
- 工具调用不是魔法，而是 schema、路由、执行和结果回填。
- 记忆不是聊天记录，而是可召回的长期知识。
- Prompt Runtime 决定每次模型调用看到什么。

LangChain 和 LangGraph 的作用，是把这些能力包装成可复用组件和工作流。

可以这样理解：

```text
LangChain:
  把 prompt、model、parser、tool、retriever、memory 组合成可调用组件。

LangGraph:
  把多个组件放进有状态图里，用节点、边、条件、循环、并行来控制流程。

自研 Agent Loop:
  当你需要完全控制权限、上下文、会话、工具执行、并发和产品体验时，回到底层循环。
```

所以学习框架时不要问“它能不能做 Agent”，而要问：它帮我托管了哪些工程复杂度，又隐藏了哪些关键边界？

## 7.2 LangChain 的核心价值：组件化

`easy-langent` 的 LangChain 章节从模型、提示词、输出解析、Memory、Tool、Runnable、Router、RAG 一路讲到应用项目。它的主线其实是组件化。

一个典型 LangChain 应用由这些部件组成：

```text
Input
  -> PromptTemplate
  -> LLM / ChatModel
  -> OutputParser
  -> Tool / Retriever / Memory
  -> Runnable Chain
  -> Application Output
```

每个部件都解决一个局部问题：

| 组件 | 解决什么 |
| --- | --- |
| PromptTemplate | 把变量和提示词模板分开 |
| ChatModel | 屏蔽不同模型调用接口 |
| OutputParser | 把自然语言结果变成结构化输出 |
| Tool | 让模型能调用外部能力 |
| Retriever | 从外部知识库找资料 |
| Memory | 保存会话上下文 |
| Runnable | 统一调用协议，支持串联、并行、重试 |

这和前面几章并不矛盾。LangChain 不是替代 Agent 原理，而是把原理包装成可组合对象。

## 7.3 Runnable：链式工作流的统一接口

LangChain 新版最值得重视的是 Runnable 抽象。它让 prompt、model、parser、retriever、lambda 都能用同一套方式组合。

典型链式结构：

```text
Prompt -> Model -> Parser
```

更复杂一点：

```text
Input
  -> Extract product selling points
  -> Generate marketing copy
  -> Parse final result
```

链式工作流适合这些任务：

- 步骤顺序固定。
- 每一步输入输出比较明确。
- 中间结果可结构化。
- 不需要复杂循环或动态分支。

例如“文章摘要 -> 关键词提取 -> 标题生成”适合链；“读代码 -> 发现问题 -> 决定要不要继续搜索 -> 修改文件 -> 运行测试 -> 根据结果重试”就已经更像图或 Agent Loop。

## 7.4 RouterChain：把任务分发做成显式流程

RouterChain 解决的是动态分发问题：先判断用户意图，再把请求送到对应处理链。

```text
User Query
  -> Router
      -> Order Chain
      -> Refund Chain
      -> Warranty Chain
      -> Default Chain
```

Router 的工程价值不在于“让模型分类”，而在于让系统有可解释的分支：

- 每个分支可以有不同 prompt。
- 每个分支可以使用不同工具。
- 每个分支可以有不同输出格式。
- 默认链可以兜底未知意图。

但 Router 也有风险：

- 分类错误会把任务送错链。
- 路由标签必须稳定，否则分支匹配失败。
- 复杂业务不能只靠一次分类，可能需要多轮澄清。

所以 RouterChain 要配合输出解析、错误处理和兜底链，而不是让模型自由生成分支名。

## 7.5 RAG：不是让模型“知道更多”，而是让回答可追溯

RAG 的表面价值是补充模型知识，但更深的价值是事实校验和来源约束。

典型 RAG 流程：

```text
Documents
  -> Load
  -> Split
  -> Embed
  -> Vector Store
  -> Retrieve
  -> Rerank / Filter
  -> Prompt with Context
  -> Answer with Sources
```

`easy-langent` 的 RAG 章节强调文档加载、切分、向量库、检索、生成链路。放到 Agent 体系里，RAG 是一种外部知识工具，它不应该和长期记忆混为一谈。

| 机制 | 主要用途 |
| --- | --- |
| RAG | 查询外部文档和知识库 |
| Memory | 保存用户、项目、历史经验 |
| Session Context | 维持当前任务连续性 |
| Tool | 执行外部动作或获取实时信息 |

RAG 适合：

- 企业知识库问答。
- 文档助手。
- 规章制度查询。
- 技术文档搜索。
- 需要来源引用的事实回答。

不适合：

- 强流程任务。
- 需要执行动作的任务。
- 信息高度结构化且应走数据库查询的任务。
- 需要强一致事务的业务逻辑。

## 7.6 LangGraph：从链到有状态图

LangChain 的链适合线性流程，LangGraph 解决更复杂的状态流转。

LangGraph 的核心概念：

```text
State:
  图里的共享黑板，保存当前任务数据。

Node:
  一个处理单元，可以是 LLM、工具、检索、规则函数。

Edge:
  节点间跳转规则，可以固定、条件、循环。

Graph:
  把状态、节点、边编译成可执行流程。
```

这和 Agent Loop 的关系很紧密。Agent Loop 是隐式循环；LangGraph 把循环、分支、并行显式画出来。

一个简单状态图：

```text
Input
  -> Analyze
  -> Retrieve
  -> Generate
  -> Review
  -> END
```

一个带条件的图：

```text
Analyze
  -> if need_search: Search
  -> if enough_info: Answer
  -> if uncertain: AskUser
```

当你发现链里出现大量 `if/else`、重试、循环、状态字段时，就应该考虑 LangGraph。

## 7.7 State 是共享黑板，不是全局变量

LangGraph 的 State 很像多 Agent 系统里的共享黑板。它保存流程中每个节点需要读写的数据。

好的 State 设计应该：

- 字段少而明确。
- 每个字段有生命周期。
- 节点只写自己负责的字段。
- 不把大文本全部塞进去。
- 对可选字段有默认值或缺省处理。

坏的 State 设计会变成全局垃圾桶：

```text
state["everything"] = all_messages + all_docs + all_outputs
```

这样图虽然能跑，但每个节点都耦合全局状态，后期很难调试。

更好的做法：

```text
state = {
  "query": 用户请求,
  "retrieved_docs": 检索结果摘要,
  "draft": 当前草稿,
  "review_notes": 审查意见,
  "final_answer": 最终输出,
  "errors": 错误列表
}
```

这和第 5 章上下文管理的原则一致：状态要服务下一步，不要保留一切。

## 7.8 节点边界：LLM、工具、数据处理要分开

`easy-langent` 在 LangGraph 基础章节里反复强调：节点是功能单元，不同节点应承担不同职责。

一个好的图通常会拆成：

- LLM 节点：理解、生成、判断。
- 工具节点：检索、调用 API、读写文件。
- 数据节点：格式转换、去重、过滤、校验。
- 控制节点：决定下一步去哪里。

不要让一个节点做所有事：

```text
bad_node:
  读文件 + 调模型 + 改状态 + 决定分支 + 写输出
```

这样会让流程不可观察，也难以单测。

好的节点像函数，图像流程：

```text
retrieve_node:
  输入 query
  输出 retrieved_docs

draft_node:
  输入 query + retrieved_docs
  输出 draft

review_node:
  输入 draft
  输出 review_notes
```

## 7.9 多 Agent 应用：什么时候用 LangGraph

LangGraph 很适合多 Agent 协作，因为它可以显式表达角色、顺序、状态共享和循环条件。

常见模式：

| 模式 | 结构 | 适合场景 |
| --- | --- | --- |
| Sequence | A -> B -> C | 写作、审查、润色 |
| Supervisor | 主管路由到专家 | 客服、复杂任务分派 |
| Peer-to-peer | 多角色共享状态轮流行动 | 游戏、模拟、协同探索 |
| Subgraph | 主图调用子图 | 复用复杂流程 |

`easy-langent` 的“谁是卧底”游戏智能体，就是一个很好的图式 Agent 示例：状态里保存玩家、词语、发言、投票、胜负，节点分别负责词语生成、角色分配、发言、投票、裁决和总结。

这个案例的价值不在游戏本身，而在于它说明：**当任务有明确状态机时，图比自由 Agent Loop 更清楚。**

## 7.10 框架应用的边界

LangChain / LangGraph 适合快速构建应用，但也有边界：

- 权限系统通常需要你自己补。
- 上下文压缩策略需要深度定制。
- 工具执行安全不能只依赖框架。
- 长期记忆写入边界需要产品判断。
- 生产可观测性和成本控制要单独设计。
- 多渠道 Gateway、Cron、投递队列不是框架默认解决的问题。

所以可以采用两层思路：

```text
应用层：
  LangChain / LangGraph 快速搭建业务流程。

Harness 层：
  自己控制权限、会话、上下文、记忆、工具安全、模型路由、观测。
```

这也是本课程的融合结论：框架让你更快开始，Harness 让你能稳定长期运行。

## 7.11 最小实践路线

建议按四步练习：

1. 用 LangChain 写一个 `Prompt -> Model -> Parser` 的线性链。
2. 加一个 Router，把不同用户意图分发到不同链。
3. 做一个小型 RAG：加载 Markdown 文档，检索并带来源回答。
4. 用 LangGraph 重写一个有状态流程，例如“草稿 -> 审查 -> 修改 -> 终稿”。

每一步都要问自己：

- 哪些状态由框架保存？
- 哪些上下文进入模型？
- 哪些错误有重试或降级？
- 哪些输出需要结构化解析？
- 哪些行为需要权限控制？

## Hello-Agents 融合补充

`hello-agents` 对本章有两个补充价值：一是把“框架”从 LangChain / LangGraph 扩展到更完整的生态比较；二是给出多个端到端项目，让框架不只停留在抽象层。

第 5 章介绍 Coze、Dify、FastGPT、n8n 等低代码平台。这些平台不等同于 LangChain / LangGraph，但它们解决的是同一类问题的应用侧入口：如何把模型、知识库、工具、流程、触发器和 UI 快速拼成一个可用 Agent。它们适合学习者快速验证需求，也适合业务方做原型；但当你需要更细的权限控制、复杂状态机、可测试流程和团队协作时，仍然要回到代码框架或自建 Harness。

第 6 章把 AutoGen、AgentScope、CAMEL、LangGraph 放在一起比较。这里可以形成一个判断标准：

- AutoGen 更强调对话式多 Agent 协作。
- CAMEL 更强调角色设定与群体交互研究。
- AgentScope 更偏实验组织、可视化和多 Agent 管理。
- LangGraph 更适合把 Agent 流程显式建模为状态图。

这说明选择框架时不应该只问“哪个最流行”，而要问：你的核心复杂度来自链式编排、图式状态、多角色协作、实验管理，还是产品工程？

第 13、14、15 章分别提供了智能旅行助手、自动化深度研究智能体、赛博小镇三个综合案例。它们共同说明：框架的价值不是替你思考产品，而是让你把产品拆成可组合模块。例如旅行助手要组合结构化数据模型、角色分工、MCP 工具和前端；深度研究 Agent 要组合 TODO、搜索、笔记、工具注册和报告生成；赛博小镇则要组合 NPC 记忆、后台批处理、Web 服务和游戏端交互。

所以本章的框架学习可以升级为三层：

```text
低代码平台：
  快速验证应用形态。

开发框架：
  管理链、图、工具、记忆、检索、多 Agent。

产品 Harness：
  接管权限、会话、观测、部署、评测和长期演进。
```

如果只停在第一层，容易做出 Demo；如果只停在第二层，容易做出实验；要做长期可用的 Agent 产品，还需要第三层。

## 系统地图

```text
LangChain
  -> Prompt / Model / Parser / Tool / Retriever / Memory
  -> Runnable chain
  -> Router / Retry / Fallback

LangGraph
  -> State
  -> Node
  -> Edge
  -> Conditional / Loop / Parallel / Subgraph

Agent Application
  -> RAG
  -> Workflow
  -> Multi-agent
  -> Domain product
```

## 共同结论

1. LangChain 适合组件化，LangGraph 适合状态化流程。
2. RAG 是外部知识检索，不等于长期记忆。
3. 图结构让流程可观察、可测试、可复用，但不自动解决安全和权限。
4. 当应用需要强控制、强安全、长会话和多渠道时，框架之外还需要 Harness 层。

## 本章自检

1. LangChain 的 Runnable 抽象解决了什么问题？
2. RouterChain 为什么需要稳定输出标签？
3. RAG 和 Memory 的边界是什么？
4. LangGraph 的 State 为什么不应该变成全局垃圾桶？
5. 什么情况下链式流程应该升级为图式流程？

## 开放性问题

1. 如果一个任务既有固定流程又需要模型动态决策，你会把哪些部分放进 LangGraph，哪些部分保留在 Agent Loop？
2. RAG 系统召回了错误文档时，责任应该由检索器、prompt、reranker 还是最终模型承担？为什么？
3. 当 LangGraph 的状态越来越复杂时，你如何判断是继续拆子图，还是退回更通用的任务系统？

## 原文入口

- [easy-langent Ch03: LangChain 进阶组件](../../source/easy-langent/docs/guide/chapter3.md)
- [easy-langent Ch04: RAG 与应用系统设计](../../source/easy-langent/docs/guide/chapter4.md)
- [easy-langent Ch05: 中期综合实践](../../source/easy-langent/docs/guide/chapter5.md)
- [easy-langent Ch06: LangGraph 基础](../../source/easy-langent/docs/guide/chapter6.md)
- [easy-langent Ch07: LangGraph 多智能体](../../source/easy-langent/docs/guide/chapter7.md)
- [easy-langent Ch08: 谁是卧底游戏智能体](../../source/easy-langent/docs/guide/chapter8.md)
- [easy-langent 项目索引](../../source/easy-langent/docs/projects.md)
- [hello-agents Ch05: 基于低代码平台的智能体搭建](../../source/hello-agents/docs/chapter5/第五章%20基于低代码平台的智能体搭建.md)
- [hello-agents Ch06: 框架开发实践](../../source/hello-agents/docs/chapter6/第六章%20框架开发实践.md)
- [hello-agents Ch13: 智能旅行助手](../../source/hello-agents/docs/chapter13/第十三章%20智能旅行助手.md)
- [hello-agents Ch14: 自动化深度研究智能体](../../source/hello-agents/docs/chapter14/第十四章%20自动化深度研究智能体.md)
- [hello-agents Ch15: 构建赛博小镇](../../source/hello-agents/docs/chapter15/第十五章%20构建赛博小镇.md)
- [hello-agents 共创项目](../../source/hello-agents/Co-creation-projects/README.md)
