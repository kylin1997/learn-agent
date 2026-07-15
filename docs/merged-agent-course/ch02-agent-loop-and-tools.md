# 第 2 章：Agent Loop 与工具调用

> 本章目标：理解 Agent 最小闭环如何从“模型回答”升级为“模型行动”，以及工具系统为什么不能只是函数表。读完本章，你应该能设计一个最小 Agent Loop，并知道生产级工具系统需要哪些元数据。

## 2.1 Agent Loop 是整个系统的心脏

一个最小 Agent Loop 可以很短：

```python
while True:
    response = llm.call(messages, tools=tools)
    messages.append(response)

    if not response.has_tool_call:
        break

    tool_results = execute_tools(response.tool_calls)
    messages.append(tool_results)
```

这个循环的意义不在代码行数，而在职责分离：

- 模型负责判断：下一步是否需要工具、调用哪个工具、传什么参数。
- Harness 负责执行：检查权限、调用工具、捕获错误、把结果写回上下文。
- 下一轮模型基于工具结果继续判断。

`learn-claude-code` 的 s01 把这个模式压缩到“while + stop_reason”。`claw0` 的 s01 也从同一个最小循环开始。Alice 方法论则提醒我们：生产系统里的循环不只是这几行，它还要处理上下文压缩、动态工具集、流式输出、终止条件、后台任务和渠道 fallback。

最小循环是地基，不是整栋楼。

## 2.2 为什么工具调用改变了一切

没有工具时，模型只能输出语言：

```text
用户：读取 README 并总结
模型：你可以打开 README，然后阅读其中内容……
```

有工具后，模型可以请求行动：

```json
{
  "name": "read_file",
  "input": {
    "path": "README.md"
  }
}
```

Harness 执行后，把结果喂回模型：

```json
{
  "type": "tool_result",
  "tool_use_id": "...",
  "content": "# Project ..."
}
```

于是模型不再靠猜，而是能基于真实观察继续推理。这是 Agent 和普通聊天的分界线。

OpenClaw 把这条演化讲得很清楚：Function Calling 让 AI 从“告诉你方法”变成“发起动作”；Agent Loop 进一步让动作结果回到下一轮推理，形成观察、思考、行动、再观察的迭代。

## 2.3 最小工具系统：Schema + Handler Map

教学版工具系统可以非常简单：

```python
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    }
]

TOOL_HANDLERS = {
    "read_file": run_read_file,
}
```

循环中只需要按名字查表：

```python
for call in response.tool_calls:
    handler = TOOL_HANDLERS[call.name]
    output = handler(**call.input)
    results.append(make_tool_result(call.id, output))
```

这就是 `learn-claude-code` s02 的核心：加工具不改循环，只加工具定义和处理函数。

这个设计有两个好处：

1. Agent Loop 保持稳定。循环不关心具体有哪些工具。
2. 工具扩展变得便宜。新增工具就是新增 schema 和 handler。

但这只是入门版。生产级工具系统还要回答更多问题。

## 2.4 工具不是函数，而是声明式契约

Alice 方法论里有一个关键判断：**工具不是函数，是声明式契约。**

函数只告诉系统“怎么执行”。工具契约还要告诉系统：

- 这个工具什么时候应该被模型调用？
- 输入参数怎么验证？
- 这个工具是只读还是会修改状态？
- 是否可能造成不可逆影响？
- 是否可以和其他工具并发执行？
- 子 Agent 能不能使用？
- 结果太大时怎么处理？
- 执行前是否需要用户批准？

一个更完整的工具声明应该包含：

```text
name
description
input_schema
is_read_only
is_destructive
is_concurrency_safe
requires_permission
max_result_size
execute(input, context)
```

其中 `description` 非常重要。它不是给人看的注释，而是给模型看的使用说明书。好的工具描述应该说明：

- 这个工具是什么。
- 什么时候用。
- 什么时候不要用。
- 返回什么格式。

例如“搜索网络”这个工具，如果只写 `Search the web`，模型会滥用；如果写清楚“仅在需要最新信息、知识截止日期之后的信息或多来源对比时使用；本地文件能回答时不要使用”，调用质量会明显更好。

## 2.5 工具执行链路

生产级工具调用通常不是“模型说调用，系统就调用”。更可靠的链路是：

```text
模型返回 tool_use
    |
    v
解析工具名和参数
    |
    v
Schema 验证
    |
    v
工具级输入校验
    |
    v
PreToolUse Hooks
    |
    v
权限检查
    |
    v
执行工具
    |
    v
结果裁剪 / 大结果落盘
    |
    v
PostToolUse Hooks
    |
    v
写回 tool_result
```

这个链路里每一步都有存在理由。

Schema 验证防止模型输出结构错误。工具级校验处理路径越界、参数不合法、资源不存在等问题。Hooks 给用户或插件留扩展点。权限检查阻止危险操作。大结果落盘保护上下文窗口。

Claude Code 的工具系统比教学版复杂得多，原因就在这里。它不只是执行工具，而是在执行前后建立了一条完整的治理管线。

## 2.6 多工具调用与并发

模型可能一次返回多个工具调用：

```text
读取 README.md
读取 pyproject.toml
搜索所有 Python 文件
```

最简单的做法是按顺序执行。这样安全，但慢。

更高效的做法是按并发安全性分批：

```text
[read README, read pyproject, glob *.py, edit file, read result]

batch 1: read README + read pyproject + glob *.py  并发
batch 2: edit file                                串行
batch 3: read result                              并发或串行均可
```

这里的关键是 `is_concurrency_safe`。只读工具通常安全，写文件、执行命令、修改任务状态通常要谨慎。但有些工具是否安全取决于输入：写不同文件可能可以并发，写同一个文件就不行。

所以工具契约里最好允许 `is_concurrency_safe(input)` 是一个函数，而不只是固定布尔值。

## 2.7 工具结果不是越完整越好

初学者容易犯一个错误：工具返回什么，就完整塞进上下文。

这在小 demo 里没问题，在真实项目里会很快撑爆 token。比如：

- `grep` 返回几万行。
- `find` 扫出整个仓库。
- `cat` 读了一个大日志。
- 浏览器抓取了整页 HTML。

正确做法是给工具结果设预算：

```text
工具执行完成
    |
    v
结果是否超过 max_result_size?
    |
    +-- 否：直接写回 tool_result
    |
    +-- 是：完整内容落盘，tool_result 只返回摘要、预览和文件路径
```

这样模型仍然知道“结果在哪里”，需要细节时可以再读，而不是一次性把上下文填满。

这也是后面上下文压缩章节的前置知识：工具系统如果不控制输出，上下文管理会非常被动。

## 2.8 工具、服务和内部机制要分开

Alice 的系统地图强调：工具层和服务层不能混。

**工具** 是 AI 可见、可调用、会进入对话历史的能力。比如读文件、搜索网页、创建任务。

**服务** 是框架内部使用、AI 不应该直接感知的能力。比如自动压缩、日志写入、记忆提取、心跳调度、后台队列。

判断一个能力是否应该做成工具，可以问一个问题：

**如果 AI 主动触发这个功能，是用户期望的行为吗？**

如果是，做成工具。如果不是，做成服务。

把所有内部机制都暴露为工具会带来三个问题：

- 工具列表变长，模型选择更困难。
- 内部状态可能被模型误触发。
- 对话历史被大量内部调用污染。

结构隔离不是洁癖，而是让模型只看该看的东西。

## 2.9 最小实现建议

如果你要自己实现第一个 Agent Loop，可以按这个顺序来：

1. 只实现一个 `bash` 或 `read_file` 工具。
2. 跑通 while loop：模型请求工具，系统执行，结果写回。
3. 增加 `TOOL_HANDLERS`，把工具执行改成查表。
4. 增加文件工具：`read_file`、`write_file`、`edit_file`、`glob`。
5. 增加路径安全检查，确保文件操作只能在工作区内。
6. 增加权限检查，把危险操作拦下来。
7. 增加工具结果大小限制。
8. 最后再考虑并发执行。

不要一开始就实现完整 Claude Code 式工具系统。先让最小闭环跑起来，再加保护层。

## Hello-Agents 融合补充

`hello-agents` 的第四章把经典 Agent 范式拆成 ReAct、Plan-and-Solve、Reflection 三条线，对本章很有补充价值。ReAct 对应“思考-行动-观察”的工具循环；Plan-and-Solve 把一次任务拆成规划阶段和执行阶段；Reflection 则把失败或低质量结果变成下一轮改进输入。它提醒我们：Agent Loop 不是只有一种形态，循环里可以嵌入规划、反思和状态管理。

它的第七章进一步把这些范式框架化：`SimpleAgent` 对应最小对话与工具调用，`ReActAgent` 对应显式工具循环，`ReflectionAgent` 和 `PlanAndSolveAgent` 对应更高级的循环策略。Extra09 的工程踩坑还补充了一个很实用的工具设计判断：工具既不能是无边界的万能入口，也不应该被拆成过度原子化的小碎片，应该找到“刚刚好”的 Goldilocks 区。

## 本章自检

1. Agent Loop 的最小结构是什么？
2. 为什么工具结果必须写回上下文？
3. 为什么新增工具不应该修改主循环？
4. 工具 schema 和 handler map 分别解决什么问题？
5. 为什么工具不是函数，而是契约？
6. `description` 为什么会影响模型行为？
7. 哪些工具可以并发，哪些工具不应该并发？
8. 工具结果太大时应该怎么办？
9. 工具和服务的边界是什么？
10. 为什么权限检查应该在工具执行链路里？

## 开放性问题

1. 如果工具调用失败，Agent 应该优先重试、换工具、询问用户，还是停止？你会如何设计判断顺序？
2. 工具越多是否一定让 Agent 更强？工具数量、工具描述质量和选择准确率之间有什么关系？
3. 哪些工具必须是确定性程序，哪些工具可以由模型辅助判断？

## 原文入口

- [learn-claude-code s01: Agent Loop](../../source/learn-claude-code/s01_agent_loop/README.md)
- [learn-claude-code s02: Tool Use](../../source/learn-claude-code/s02_tool_use/README.md)
- [Hello-Agents Ch04: 智能体经典范式构建](../../source/hello-agents/docs/chapter4/第四章%20智能体经典范式构建.md)
- [Hello-Agents Ch07: 构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [Hello-Agents Extra09: Agent 应用开发踩坑](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)
- [Alice 方法论: Agent 主循环](../../source/Alice_methodology/chapters/03-agent-loop.md)
- [Alice 方法论: 工具系统](../../source/Alice_methodology/chapters/04-tool-system.md)
- [claw0 s01: Agent 循环](../../source/claw0/sessions/zh/s01_agent_loop.md)
- [claw0 s02: 工具使用](../../source/claw0/sessions/zh/s02_tool_use.md)
- [Hermes: 请求旅程](../../source/hermes-book/src/part2/ch03-request-journey.md)
- [Hermes: AIAgent 内核](../../source/hermes-book/src/part2/ch04-aiagent-core.md)
- [Hermes: 工具系统](../../source/hermes-book/src/part3/ch06-tool-system.md)
- [Harness Engineering: 工具系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch02.md)
- [Harness Engineering: Agent Loop](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch03.md)
- [Claude Code 分析: Tool Call 机制](../../source/claude-code-analysis/analysis/04b-tool-call-implementation.md)
