# 第 1 章：Agent 到底是什么

> 本章目标：先建立整套教材的总地图。读完本章，你应该能区分普通 LLM 应用、Agent、Agent 产品、Harness 这几个概念，并理解后续为什么要学习工具、Prompt Runtime、模型路由、上下文、记忆、权限、Gateway、多 Agent 和可观测性。

## 1.1 先给结论

本课程采用一个核心判断：

**Agent 的智能主要来自模型，Agent 产品的可靠性主要来自 Harness。**

模型负责感知、推理和决定下一步要做什么。Harness 负责给模型提供工作环境：工具、上下文、知识、权限、状态、记忆、执行入口、日志和恢复能力。

所以，当我们说“我要做一个 Agent”，多数情况下并不是在训练一个新模型，而是在构建一套让模型能稳定工作的工程系统。

可以先用一个公式记住：

```text
Agent Product = Model + Harness

Harness = Tools
        + Knowledge
        + Observation
        + Action Interfaces
        + Permissions
        + State
        + Runtime
        + Evaluation
```

这里的 `Model` 是驾驶者，`Harness` 是车、道路、仪表盘、刹车、导航和交通规则。没有模型，系统没有判断力；没有 Harness，模型只能聊天，不能可靠地完成真实任务。

这个判断来自 `learn-claude-code` 的 Harness 工程观，也能解释 Alice、Hermes、OpenClaw、Claude Code 等教程里反复出现的工程模块：它们不是在“给模型补智能”，而是在给模型构建一个可操作、可恢复、可治理的世界。

## 1.2 为什么普通聊天机器人还不是 Agent

普通 LLM 聊天应用的典型模式是：

```text
用户提问 -> 模型回答 -> 对话结束
```

这种系统可以解释问题、给出建议、生成文本，但它通常有四个限制。

第一，它不能真正行动。用户说“帮我整理项目文件”，普通聊天机器人只能告诉你步骤，不能自己读目录、改文件、运行命令。

第二，它没有稳定状态。换一个会话，很多上下文、偏好、任务进度都会丢失。

第三，它没有权限边界。能不能删文件、能不能联网、能不能调用外部 API、能不能花钱执行任务，如果没有一套机制治理，就只能靠模型“自觉”。

第四，它缺少长期反馈。做过一次复杂任务后，下次不一定更好，因为过程经验没有沉淀成可复用知识。

Agent 的关键变化不是“回答更聪明”，而是它进入了一个可以观察和行动的环境。OpenClaw 用“从会说到会做”描述这条演化路径：对话时代的 LLM 知道怎么做，但不能替你做；工具调用让模型可以发起结构化动作；Agent Loop 让模型可以边观察结果边调整下一步。

这也是 LangChain 和 LangGraph 的位置。LangChain 把模型调用、提示词、输出解析、记忆、工具这些能力做成基础组件；LangGraph 进一步处理状态、流程、分支和多智能体协作。它们不是智能本身，而是让模型进入任务环境的工程组件。

## 1.3 Agent、Workflow、Chatbot 的边界

学习 Agent 时，最容易混淆三类东西：Chatbot、Workflow、Agent。

```text
Chatbot:
  主要输出自然语言。
  用户问，模型答。
  系统很少主动行动。

Workflow:
  主要执行预设流程。
  人或开发者提前定义步骤、分支和节点。
  LLM 常作为某个节点的文本处理能力。

Agent:
  模型在循环中根据环境反馈决定下一步。
  步骤不是完全预写死的。
  Harness 提供工具、状态和边界。
```

这三者没有绝对高低。很多生产系统应该用 Workflow，而不是 Agent。比如固定审批流程、固定报表生成、固定客服分类，用 Workflow 更可控、更便宜、更容易测试。

Agent 适合的任务通常有这些特征：

- 用户目标明确，但路径不完全确定。
- 需要多轮观察和行动。
- 工具结果会改变下一步决策。
- 任务可能失败，需要诊断、重试或换路。
- 环境状态会变化，比如代码库、文件系统、远程服务。

如果一个任务的步骤完全确定，Agent 反而可能引入不必要的不确定性。一个成熟工程师不是“所有地方都用 Agent”，而是判断什么时候需要模型在循环里决策，什么时候只需要一个确定性流程。

## 1.4 最小 Agent Loop

很多教程都把 Agent 的核心压缩成一个循环：

```text
messages[] -> LLM -> response
                   |
                   | response contains tool_use?
                   |
            yes -> execute tool -> append tool_result -> loop
            no  -> return final answer
```

伪代码如下：

```python
def agent_loop(messages):
    while True:
        response = call_model(messages, tools=TOOLS)
        messages.append(response)

        if not response.has_tool_call:
            return response.final_text

        results = []
        for tool_call in response.tool_calls:
            result = TOOL_HANDLERS[tool_call.name](tool_call.arguments)
            results.append(result)

        messages.append({"role": "tool", "content": results})
```

这个循环解释了 Agent 为什么能“做事”：

- 模型看到当前消息和工具列表。
- 模型决定要不要调用工具。
- Harness 执行工具。
- 工具结果被写回上下文。
- 模型基于新观察继续判断。

但这个循环只是真相的第一层。Alice 方法论提醒我们：简单 while loop 只是 1% 的真相，真正的难点在状态、权限、上下文、并发、记忆、多 Agent 信息流和可观测性。一个玩具 Agent 可以只有一个循环；一个能长期协作的 Agent 必须有一整套 Harness。

## 1.5 Harness 到底包含什么

把 9 份教程合在一起看，Harness 至少包含 10 类能力。

**工具系统**  
工具是模型可以调用的动作。最小工具可以是 `read`、`write`、`edit`、`exec`，也可以是搜索、浏览器、数据库、日历、邮件、MCP 工具。工具的重点不是函数能跑，而是它要对模型可理解、对系统可治理。

**Prompt Runtime**  
Prompt 不应该是一段硬编码字符串。真正的 Agent 会在运行时组装身份、规则、任务、工具、Skill、记忆、当前工作目录和动态环境信息。

**模型调用层**  
模型调用层回答“这一次请求应该发给哪个模型，以及失败时怎么办”。它包含 provider 抽象、模型选择、fallback、重试、限流、API key 轮换、成本记录和流式返回。

**会话与上下文管理**  
Agent 需要知道当前对话发生了什么。最小方案是内存里的 `messages[]`，更可靠的方案是追加式 JSONL 或数据库。上下文管理要处理 token 预算、压缩、工具大结果落盘和恢复。

**长期记忆**  
上下文解决当前会话，记忆解决跨会话延续。记忆可以分成会话摘要、项目记忆、用户记忆、技能记忆等类型。

**权限与沙箱**  
一个能读写文件、执行命令、访问网络的 Agent 必须有边界。权限系统不是补丁，而是主干。

**Skill、MCP 与插件**  
Tool 给 Agent 手，Skill 给 Agent 工作方法，MCP 和插件扩展 Agent 的能力边界。

**Gateway 与多入口**  
如果 Agent 能同时接入 Telegram、飞书、Slack、Web、TUI、Cron，它就需要 Gateway，把不同平台的消息统一成内部格式。

**主动性与可靠投递**  
长期个人 Agent 需要心跳、定时任务、后台任务、消息队列、投递失败重试和进程恢复。

**多 Agent 与任务系统**  
当任务太大、上下文需要隔离、或者需要并行推进时，就需要任务图、子 Agent、团队协议和 worktree 隔离。

## 1.6 一张系统地图

把这些能力放在一起，可以得到一张简化版 Agent 产品地图：

```text
用户 / 定时器 / 外部渠道
        |
        v
入口层：CLI / TUI / Web / Gateway / Cron
        |
        v
Runtime：会话生命周期、配置、模块协调
        |
        v
Agent Loop：组装上下文 -> 调模型 -> 执行工具 -> 写回结果
        |
        +--> Tool System：文件、Shell、浏览器、API、MCP
        +--> Prompt Runtime：身份、规则、任务、记忆、Skill
        +--> Model Router：provider、fallback、重试、成本
        +--> Context Manager：token 预算、压缩、结果落盘
        +--> Memory：用户、项目、会话、技能
        +--> Permission / Sandbox：审批、规则、隔离、防注入
        +--> Task / Multi-Agent：任务图、子 Agent、团队协议
        |
        v
事件流 / 日志 / 可观测性 / 持久化 / 评估
```

这张地图是后续章节的目录。之后每一章都只是把其中一个模块展开。

## 1.7 判断一个 Agent 产品是否成熟

可以用 8 个问题做初步评估：

1. 它能不能调用工具，并把结果写回下一轮推理？
2. 它是否有明确的权限和沙箱边界？
3. 它是否能跨多轮任务保存状态，而不是只依赖模型“记得”？
4. 它遇到上下文超限时是否能压缩和恢复？
5. 它是否区分当前上下文和长期记忆？
6. 它是否支持按需加载知识，而不是把所有文档塞进 prompt？
7. 它是否有错误恢复、重试、fallback 和日志？
8. 它是否能被测试、观测和审计？

如果这些问题大多没有答案，那它更像一个 demo；如果都有清晰设计，它才开始接近可长期运行的 Agent 产品。

## 1.8 不同教程在本章的共同结论

9 份教程的角度不同，但在第一性问题上高度一致。

`learn-claude-code` 强调：Agency 来自模型，工程师主要构建 Harness。

`Alice_methodology` 强调：Agent 产品难在状态管理、结构隔离、权限、记忆和可观测性。

`Hermes` 强调：长期个人 Agent 要有学习闭环、CLI-first、多入口、长期记忆和可运行在任何地方的工程约束。

`hello-claw` 强调：Agent 从“会说”走向“会做”，需要 Agent Loop、提示词系统、工具系统、消息循环、统一网关和安全沙箱。

`claw0` 强调：从一个 while loop 出发，逐步叠加工具、会话、渠道、网关、智能层、心跳、投递、弹性和并发。

`easy-langent` 强调：应用开发需要基础组件和流程框架。简单任务用 LangChain 快速搭建，复杂状态流程用 LangGraph 管控。

`harness-engineering-from-cc-to-ai-coding` 强调：Claude Code 不是普通 CLI，而是完整 AI Coding Agent 技术栈，工具、提示词、权限、缓存、多 Agent 都是体系化设计。

`claude-code-analysis` 强调：Claude Code 是本地 Agent 平台，不只是聊天程序；它有入口、REPL、执行内核、工具权限、记忆持久化和扩展层。

合并后，我们得到一个更稳的学习口径：

**不要一上来问“我要用哪个框架做 Agent”。先问：我要给模型构建一个怎样的工作环境？这个环境需要哪些工具、状态、权限、记忆和入口？**

## Hello-Agents 融合补充

`hello-agents` 给本章补上了一条更适合初学者的“概念到实践”路径：它先从传统智能体定义、任务环境、感知与行动讲起，再过渡到 LLM 驱动的新范式，并明确区分 Workflow 和 Agent。这个视角能帮助我们把本章的 Harness 观点放回更大的历史脉络里：早期智能体强调规则和环境交互，现代 LLM Agent 则把语言模型变成推理与决策核心，但仍然离不开环境、工具、状态和行动循环。

它的 5 分钟智能体示例也能作为本课程的“最小体验版”：先定义可用工具和输出格式，再接入 LLM，最后执行行动循环。也就是说，`hello-agents` 不只是补充定义，而是把“Agent = 任务环境 + 感知 + 决策 + 行动”的基本模型落到了可运行代码上。

## 本章自检

1. Agent 和普通 LLM 应用有什么区别？
2. 为什么说大多数开发者实际是在做 Harness，而不是训练 Agent？
3. Agent Loop 的最小结构是什么？
4. 为什么一个简单 while loop 还远远不够？
5. Tool、Skill、MCP、Plugin 的边界分别是什么？
6. Context 和 Memory 有什么区别？
7. 为什么权限系统不是附加功能？
8. Gateway 解决什么问题？
9. 什么情况下才需要多 Agent？
10. 如果要做自己的 Agent，第一步应该画哪张系统地图？

## 开放性问题

1. 如果一个系统能调用工具但没有长期状态，它算不算 Agent？你的判断标准是什么？
2. Harness 层应该尽量厚还是尽量薄？不同产品阶段答案会如何变化？
3. 当模型能力越来越强，Agent 工程里哪些部分仍然不能交给模型自由决定？

## 原文入口

- [learn-claude-code: 真正的 Agent Harness 工程](../../source/learn-claude-code/README-zh.md)
- [Hello-Agents: 项目介绍](../../source/hello-agents/README.md)
- [Hello-Agents Ch01: 初识智能体](../../source/hello-agents/docs/chapter1/第一章%20初识智能体.md)
- [Hello-Agents Ch02: 智能体发展史](../../source/hello-agents/docs/chapter2/第二章%20智能体发展史.md)
- [Alice 方法论: Agent 为什么难做](../../source/Alice_methodology/chapters/00-preface.md)
- [Alice 方法论: 五大设计哲学](../../source/Alice_methodology/chapters/01-philosophy.md)
- [Alice 方法论: 系统地图](../../source/Alice_methodology/chapters/02-architecture.md)
- [Hermes: 不只是另一个 Agent](../../source/hermes-book/src/part1/ch01-design-bets.md)
- [Hermes: 仓库地图](../../source/hermes-book/src/part1/ch02-repo-map.md)
- [easy-langent: LangChain 与 LangGraph 框架认知](../../source/easy-langent/docs/guide/chapter1.md)
- [hello-claw: 架构设计哲学](../../source/hello-claw/docs/cn/build/chapter1/index.md)
- [claw0: 从零到一构建 AI Agent Gateway](../../source/claw0/README.zh.md)
- [Harness Engineering: AI 编码 Agent 的完整技术栈](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch01.md)
- [Claude Code 分析: 软件架构与程序入口](../../source/claude-code-analysis/analysis/01-architecture-overview.md)

## 本章在全书中的位置

本章建立总地图。下一章进入 **Agent Loop 与工具调用**，用最小代码理解“模型决定、Harness 执行、结果写回、继续循环”的闭环。
