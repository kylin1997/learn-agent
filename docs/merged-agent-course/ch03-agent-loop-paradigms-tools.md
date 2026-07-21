# 第 3 章：Agent Loop、经典范式与工具运行时

> 本章目标：从最小工具循环出发，理解 ReAct、Plan-and-Solve、Reflection 等范式如何改变循环控制策略，并实现一个具备工具契约、权限、并发、停止和验证能力的最小运行时。

## 3.1 学习目标与边界

本章回答：**怎样把一次模型生成变成一个可观察、可控制、能与环境交互的任务闭环？**

你将学会：

- 区分固定工作流与由模型动态控制的 Agent。
- 用状态机而不是一段模糊的 `while True` 理解 Agent Loop。
- 比较 ReAct、Plan-and-Solve、Reflection/Reflexion 与 evaluator-optimizer。
- 区分单个推理原语与负责选择、监控和切换原语的认知控制结构。
- 把工具设计成声明式契约，而不只是函数表。
- 处理多工具调用、并发、权限、结果预算、错误和取消。
- 用 Trace、环境状态和验收契约测试 Agent，而不只看最终文本。

本章不负责 Prompt 的完整分层组装，也不展开不同 Provider 的流式协议；它假设模型运行时已经能返回统一的文本、工具调用和停止事件。权限与沙箱将在后续治理章节深化。

## 3.2 从“模型回答”到“模型行动”

没有工具时，模型只能描述应该做什么：

```text
用户：读取 README 并总结。
模型：你可以先打开 README，然后提取项目目标……
```

有工具后，模型可以提出一个结构化动作：

```json
{
  "id": "call_01",
  "name": "read_file",
  "arguments": {"path": "README.md"}
}
```

Harness 执行工具并返回观察：

```json
{
  "tool_call_id": "call_01",
  "status": "ok",
  "content": "# Project ..."
}
```

当观察结果进入下一次模型调用，系统才形成闭环：

```text
理解目标 -> 选择动作 -> 执行动作 -> 观察结果 -> 更新判断 -> ... -> 验证并停止
```

模型负责语义决策，Harness 负责真实执行。两者缺一不可：只有模型，是建议系统；只有固定代码，是工作流；让模型基于环境反馈动态决定下一步，才形成 Agent。

## 3.3 最小 Agent Loop

教学版循环可以很短：

```python
def run_agent(messages, tools):
    while True:
        response = llm.generate(messages=messages, tools=tools.schemas())
        messages.append(response.assistant_message)

        if not response.tool_calls:
            return response.text

        results = tools.execute_all(response.tool_calls)
        messages.append(make_tool_results_message(results))
```

这段代码包含三个稳定职责：

1. 把消息和可用工具交给模型。
2. 把模型提出的工具调用交给工具运行时。
3. 把工具结果写回消息，使下一轮看到真实观察。

新增工具不应该修改主循环。`learn-claude-code` 用 `Schema + Handler Map` 说明了这个不变量：工具数量可以从一个增长到几十个，循环仍只按名字分发。

但生产系统不能只看“有没有工具调用”。循环还必须区分正常完成、输出截断、等待用户、权限拒绝、模型错误、取消、预算耗尽和不可恢复错误。此时，`while True` 应被看作一个状态机的语法外壳。

## 3.4 把循环写成状态机

一个实用状态至少包含：

```python
@dataclass
class AgentState:
    messages: list
    turn: int = 0
    tool_calls: int = 0
    cost_usd: float = 0.0
    last_transition: str = "start"
    attempted_recovery: set[str] = field(default_factory=set)
    abort_signal: object | None = None
    aborted: bool = False
```

状态转移可以显式列出：

| 当前事件 | 条件 | 转移 |
| --- | --- | --- |
| `model_done` | 验收已满足 | `completed` |
| `tool_calls` | Schema 与权限通过 | `execute_tools` |
| `tool_result` | 有新观察 | `next_turn` |
| `needs_input` | 缺少关键决策 | `waiting_user` |
| `max_output` | 还有恢复预算 | `continue_output` |
| `prompt_too_long` | 尚未紧急压缩 | `compact_retry` |
| `transient_error` | 允许重试 | `backoff_retry` |
| `abort` | 用户取消 | `cancelled` |
| `budget_exhausted` | 达到轮次/时间/成本上限 | `budget_stop` |
| `fatal_error` | 无安全恢复路径 | `failed` |

显式状态转移的价值在于：每次继续和停止都有原因，可以测试、记录和恢复。否则“循环又跑了一轮”无法解释是新证据驱动、盲目重试，还是模型没有意识到自己已完成。

## 3.5 先分清范式属于哪一层

ReAct、Plan-and-Solve、Reflection、Reflexion 和 Evaluator-Optimizer 经常被并列成“Agent 范式”，但它们并不处于同一抽象层。混在一起会让开发者误以为每种方法都必须改写底层 Agent Loop。

| 范式 | 主要归属 | 谁控制下一步 | 状态或记忆 |
| --- | --- | --- | --- |
| ReAct | 动态控制循环 + 提示轨迹策略 | 模型根据最新 Observation 选下一动作 | 当前行动—观察轨迹 |
| Plan-and-Solve | 原始形式是提示策略；工程化后可成为显式计划控制器 | 规划器给出步骤，执行器或调度器推进 | 可选的结构化计划状态 |
| Reflection | 局部反馈修订循环 | 评审反馈触发下一版生成 | 当前任务内的候选与反馈 |
| Reflexion | 反馈修订 + 语言经验记忆 | 新尝试读取历史反馈经验 | 跨尝试或跨 episode 的反思记忆 |
| Evaluator-Optimizer | 预定义 Workflow | 代码固定“生成—评估—优化”拓扑 | rubric、评分与候选版本 |

因此，只有 ReAct 天然要求模型在每次观察后动态控制循环。Plan-and-Solve 可以只是一条 Prompt，也可以把计划物化为 Runtime 状态；Reflection 可以嵌入某个步骤；Evaluator-Optimizer 则是由代码预先规定转移条件的 Workflow 模式，不应因为内部用了模型就自动称为自主 Agent。

### 3.5.1 ReAct：推理与行动交替

ReAct 把 Reasoning 与 Acting 交错为：

```text
Thought -> Action -> Observation -> Thought -> ... -> Answer
```

形式化地，第 $t$ 步由模型策略 $\pi$ 根据问题和历史轨迹生成下一动作：

$$
(th_t,a_t)=\pi(q,(a_1,o_1),\ldots,(a_{t-1},o_{t-1}))
$$

环境执行动作并返回：

$$
o_t=T(a_t)
$$

ReAct 的关键不是把 `Thought:` 打印出来，而是允许新观察即时改变下一步。它适合信息不完备、路径依赖环境反馈的任务，例如搜索、调试、浏览网页和操作软件。

局限也很直接：

- 每个小动作都可能增加一次模型往返，延迟和成本高。
- 轨迹持续增长，错误观察或错误假设会污染后续上下文。
- 没有明确子目标时，模型可能在相似查询间打转。
- 可见“思考”不等于可信推理，敏感内部推理也不应被当作审计依据。

现代原生工具调用通常不需要脆弱的文本 `Action: Search[...]` 解析。应让 Provider Adapter 产出统一 `ToolCall`，保留 ReAct 的控制思想，而不是拘泥于旧格式。

### 3.5.2 Plan-and-Solve：提示策略与计划控制器

Plan-and-Solve 把任务分成规划器和执行器：

```text
问题 -> 生成计划 -> 选择当前步骤 -> 执行 -> 更新状态 -> 下一步骤 -> 验证
```

原始 Plan-and-Solve 研究针对 Zero-shot Chain-of-Thought 的漏步、计算和语义误解问题，先用提示让模型理解问题并拆分子任务，再按计划求解。这个原始形式首先是一种 Prompt 策略，并不天然提供持久状态、工具调度或恢复能力。工程 Agent 若需要跨轮推进，才把计划升级为可更新的 Runtime 状态：

```python
PlanStep(id="inspect", goal="定位失败原因", status="done", evidence=[...])
PlanStep(id="fix", goal="做最小修改", status="in_progress", depends_on=["inspect"])
PlanStep(id="verify", goal="运行相关测试", status="pending", depends_on=["fix"])
```

它适合步骤依赖清楚、需要覆盖检查或长时间协作的任务。优势是可追踪、可恢复、便于提前发现漏项；代价是计划本身需要一次或多次调用，且环境变化后旧计划可能变成束缚。

好的计划不是不可修改的剧本。每获得新证据，都应判断：继续当前步骤、局部修订，还是整体重规划。简单任务不应被强迫先写长计划。

### 3.5.3 Tree-of-Thought：为分支探索设置硬预算

Tree-of-Thought（ToT）不是“让模型多想几个答案”，而是把候选思路物化为可扩展、可评分和可剪枝的搜索状态：

```text
当前状态
  -> 扩展 b 个候选
  -> 按约束与评分淘汰不可行、重复和低价值分支
  -> 只保留 k 个候选继续深入
  -> 命中解、预算或无进展条件后停止
```

它适合存在多个可行路径、局部选择会影响最终结果，且中间候选能够被评价的任务，例如约束规划、复杂诊断和方案搜索。若任务只有一条明显路径，或者中间状态无法可靠评分，ToT 只会把一次不确定生成扩成一棵昂贵的树。

实现前应明确四个预算：最大深度 `max_depth`、每层分支数 `branching_factor`、保留宽度 `beam_width` 和总评估次数 `max_evaluations`。剪枝也不能只依赖模型的主观分数。优先使用硬约束、环境测试、重复状态检测和可验证启发式，再用模型比较剩余候选。否则生成模型与评估模型可能共享同一种偏差，把正确分支提前剪掉。

ToT 的 Trace 至少要记录父节点、候选动作、评分依据、淘汰原因和累计预算。这样才能区分“没有找到解”与“正确分支因错误评分被剪掉”。

### 3.5.4 Reflection 与 Reflexion：反馈循环是否进入记忆

Reflection 常见结构是：

```text
执行 -> 评审 -> 反馈 -> 修订 -> 再验证
```

令第 $i$ 轮产物为 $O_i$，评审反馈为 $F_i$：

$$
F_i=\pi_{review}(task,O_i,evidence)
$$

$$
O_{i+1}=\pi_{refine}(task,O_i,F_i)
$$

Reflection 通常把反馈限制在当前任务的修订循环。Reflexion 进一步把任务反馈转成语言经验，写入可供后续 episode 或再次尝试读取的记忆。两者都用反馈改善下一次策略，但 Reflexion 多出“反馈记忆如何写入、选择和失效”这一层；如果反馈只在当前 Prompt 中传一次，就不应把它称为 Reflexion。

只让同一个模型阅读自己的答案并说“请反思”，很容易得到泛泛批评或自我确认。强 Reflection 应至少引入一种独立信号：

- 单元测试、编译器或静态分析。
- 参考答案、业务规则或结构化评分器。
- 与生成阶段不同的评审 Prompt 或模型。
- 环境回放、用户反馈或可复现实验。

Reflection 是典型的以成本换质量策略。必须设置最大轮数、最小改进阈值和停止条件，避免“永远还能再润色一点”。

Reflexion 还需要把“失败经验”写成有边界的记录，而不是保存一段泛泛自评：

```yaml
attempt_id: attempt_03
strategy: 先按文件名猜测测试入口
evidence: pytest 返回路径不存在
failure_type: invalid_assumption
next_change: 先读取项目测试配置再选择入口
scope: current_task
```

只有环境证据、评测器或用户反馈确认的失败才有资格进入记录。模型自己说“这个方法不好”不构成证据。再次尝试前应检查新策略是否真的改变了关键变量；任务通过验收、达到尝试上限、连续改进低于阈值、重复已失败策略或再无独立证据可获取时，都应停止 Reflexion。跨任务保存这些经验时，还要经过第 7 章的长期记忆写入门槛。

### 3.5.5 Evaluator-Optimizer：预定义 Workflow

Evaluator-Optimizer 与 Reflection 的表面轨迹相近，但控制权不同：应用代码预先固定“生成器 -> 评估器 -> 是否通过 -> 优化器”的拓扑，评估器只返回评分与反馈，不能自由改变整个流程。因此它属于预定义 Workflow 模式。生成器产出候选，评估器按明确 rubric 给出通过/失败与可执行反馈，优化器只修复未通过项。

它适合成功标准清楚、迭代能显著改善结果的任务，如代码审查、报告合规、SQL 安全和结构化抽取。若评估标准本身模糊，评估器只会制造更多自然语言噪声。

### 3.5.6 范式可以组合，但不要无条件叠加

一个长任务可以把计划物化为控制状态，在每个不确定步骤内用 ReAct，交付前再进入由代码控制的 Evaluator-Optimizer Workflow。组合后的控制流是：

```text
Plan
  -> Step 1: ReAct until evidence
  -> Step 2: deterministic workflow
  -> Step 3: ReAct until evidence
  -> Evaluate
  -> Refine only failed criteria
```

每增加一种范式，都增加模型调用、状态和失败路径。设计时先问它改变的是 Prompt、动态控制循环、反馈记忆还是预定义 Workflow，再判断它是否针对一个已观察到的失败模式。

### 3.5.7 推理原语不等于认知架构

CoT、ReAct、ToT、规划和 Reflexion 都是解决某类问题的推理原语。它们告诉系统“怎样处理”，却不会自动判断当前任务该选哪一种、正在使用的方法是否有效，以及何时应该切换。认知架构补的是这层选择与监控，不是再发明一种更长的推理文本。

可以从五类可观察失败反推缺失的控制机制：

| 运行表现 | 真正缺失的能力 | 运行时应增加的信号或动作 |
| --- | --- | --- |
| 引用了低质量材料，却给出自信结论 | 证据质量评估 | 记录来源质量、一致性与验收结果；不通过则补证或降级 |
| 重复相同查询或工具路径 | 进展与停滞感知 | 比较新证据、状态差异和失败策略；切换策略或停止 |
| 新证据推翻前提后仍执行旧计划 | 模型更新 | 发出矛盾信号，修订任务表示和计划 |
| 没有证据仍坚持猜测 | 知识边界检测 | 进入补证、表达不确定或交还用户的门控 |
| 能执行单个工具，却不会组合步骤 | 任务与依赖分析 | 识别子目标、依赖和可并行路径，再选择规划或搜索 |

这些信号应落在结构化运行状态中，并由代码控制路由。置信度不能只取模型自报数字；至少还要结合检索质量、证据一致性、测试结果和历史校准。系统也不需要暴露隐藏思维链来实现监控，Trace 记录策略、动作、观察、评分依据、状态差异和停止原因即可。

这里讨论的是当前任务内部的认知控制。第 6 章会说明这些信号如何形成一次运行的共享状态与上下文视图；第 15 章的 Loop Engineering 则处理跨运行的恢复、持续执行和人的控制权，三者不能混为一个循环。

## 3.6 工具不是函数，而是声明式契约

最小工具系统由 Schema 和 Handler Map 构成：

```python
TOOL_SCHEMAS = {
    "read_file": {
        "description": "Read a UTF-8 text file inside the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    }
}

TOOL_HANDLERS = {"read_file": run_read_file}
```

生产级工具还要声明 Runtime 无法从函数签名推断的属性：

```text
name
description
input_schema
is_read_only(input)
is_destructive(input)
is_concurrency_safe(input)
requires_permission(input, context)
timeout_ms
max_result_size
execute(input, context)
```

这些元数据让框架能够自动完成校验、权限、调度、结果裁剪和审计。工具契约同时服务三个读者：模型据此选择，Runtime 据此治理，开发者据此维护。

### 3.6.1 工具粒度的 Goldilocks 区

工具过于宽泛，例如一个无边界 shell，会增加误用和安全风险；工具过于原子化，例如把文件操作拆成大量相似微工具，会增加选择难度和往返次数。

合适粒度通常满足：

- 对模型来说是一个语义清楚的动作。
- 输入、输出和副作用可以完整描述。
- Runtime 能独立校验和授权。
- 失败后能给出可行动的错误，而不是模糊异常。

### 3.6.2 工具描述是局部 Prompt

好的 `description` 应说明：是什么、何时用、何时不用、返回什么、失败语义和风险。它不是开发者注释，而是影响模型工具选择的“微型行为控制器”。

但描述不能替代代码约束。即使写了“只能读工作区”，Handler 仍必须做路径解析和边界检查。

## 3.7 工具执行管线

一个可靠调用应经过：

```text
接收 ToolCall
  -> 查找工具与版本
  -> JSON Schema 验证
  -> 语义校验（路径、范围、资源状态）
  -> PreToolUse Hook
  -> 权限决策（allow / ask / deny）
  -> 获取并发锁或资源租约
  -> 带超时和取消信号执行
  -> 标准化成功/错误结果
  -> 裁剪、摘要或大结果落盘
  -> PostToolUse Hook
  -> 记录审计与指标
  -> 写回匹配 call_id 的 ToolResult
```

`ToolContext` 应显式注入工作目录、会话 ID、用户身份、权限回调、取消信号、密钥访问器和事件发射器，避免工具依赖不可测试的全局变量。

工具结果必须保留 `tool_call_id`。中断产生孤立调用时，应注入一个合成错误结果或按 Provider 协议修复消息，不能把不完整的调用—结果对直接送回模型。

## 3.8 多工具调用与并发

模型可能一轮提出多个调用。全部串行安全但慢，全部并行会破坏有依赖或有副作用的动作。

一个实用算法是按原顺序分连续批次：

```text
[read A, read B, glob *.py, write C, read C]
  -> batch 1: read A + read B + glob *.py  并发
  -> batch 2: write C                       独占
  -> batch 3: read C                        并发
```

并发安全不等于只读。创建不同任务记录可能可并发；读取一个正在被写入的资源可能不安全。因此 `is_concurrency_safe(input)` 最好允许按参数判断，并结合资源键：

```python
lock_key = tool.resource_key(call.arguments)  # 例如 workspace:file:path
```

即使调用独立，也要设置全局并发上限、Provider 限流和取消传播。并行的目标是降低墙钟时间，不是让系统在错误时更快地产生更多副作用。

## 3.9 工具结果与上下文预算

工具返回越完整不一定越好。搜索、日志、文件树和网页抓取很容易产生数万行内容，挤占后续决策所需上下文。

结果处理可以分三层：

1. 工具自身提供分页、范围、字段选择和 `limit`。
2. Runtime 设置单工具与单轮聚合上限。
3. 超限内容落盘或存入对象存储，向模型返回摘要、预览、统计与可继续读取的引用。

```json
{
  "status": "truncated",
  "summary": "Found 128 matching files; showing first 20.",
  "preview": ["..."],
  "artifact": "artifacts/tool-call-42.txt",
  "next": {"offset": 20}
}
```

摘要不能吞掉错误码、关键证据或继续操作所需字段。对于文件读取类工具，还要避免“结果落盘后模型再次读取又再次落盘”的递归陷阱。

## 3.10 工具、服务与内部机制

不是所有系统能力都该暴露给模型。

**工具**是模型可选择、会进入行动轨迹的能力，例如读文件、搜索和创建工单。

**服务**是 Runtime 自动执行的内部机制，例如日志、上下文预算统计、心跳、缓存和队列续租。

判断标准是：**模型主动触发它，是否是任务语义的一部分？**

自动压缩通常是服务；“把这段对话总结成用户指定文档”才是工具。把内部机制全暴露为工具会增加选择噪声、状态污染和越权风险。

## 3.11 最小实现：带治理的循环

下面的伪代码保留关键边界：

```python
async def agent_loop(task, model_runtime, prompt_runtime, registry, policy, verifier, budget):
    state = AgentState(messages=[user_message(task)])

    while budget.allows(state):
        if state.aborted:
            return finish("cancelled", state)

        # Policy 先给出授权上限；Prompt Runtime 只能从中选择相关子集。
        authorized = policy.authorized_tools(state, registry)
        relevant = prompt_runtime.relevant_tool_subset(state, authorized)
        prompt = prompt_runtime.prompt_for(state, tools=relevant)
        response = await model_runtime.stream_to_response(prompt, relevant)
        state.messages.append(response.message)
        state.turn += 1

        if response.stop_reason == "max_output":
            recovery = await model_runtime.plan_output_recovery(response)
            if recovery.safe_to_continue:
                continue
            return finish("incomplete_output", state)

        if not response.tool_calls:
            verdict = await verifier.verify_completion(task, state, response)
            if verdict.passed:
                return finish("completed", state, evidence=verdict.evidence)
            if verdict.recoverable:
                state.messages.append(feedback_message(verdict))
                continue
            return finish("unverified", state, evidence=verdict.evidence)

        batches = registry.partition(response.tool_calls)
        for batch in batches:
            # 执行点重新检查权限，防止会话期间授权状态变化。
            results = await registry.execute_batch(
                batch, policy=policy, authorized=authorized,
                abort_signal=state.abort_signal
            )
            state.messages.append(tool_results_message(results))
            state.tool_calls += len(results)

    return finish("budget_exhausted", state)
```

这个版本仍不完整，但已经具备五个生产不变量：预算、停止原因、动态工具集、受治理执行和独立验收。`authorized` 是 Policy 给出的能力上限，`relevant` 只能是它的子集；Prompt Runtime 可以隐藏无关工具以降低选择噪声，却无权把未授权工具重新加入模型可见集合。`plan_output_recovery` 还必须遵守第 5 章的恢复契约：只有纯生成且确认无副作用时才可完整重放，副作用状态未知时 `safe_to_continue` 必须为假。

## 3.12 生产约束

### 停止与取消

至少覆盖正常完成、等待用户、最大轮次、时间/Token/成本预算、用户取消和不可恢复错误。取消信号必须穿透模型流、工具、子任务和锁等待。

### 权限与副作用

只读不必然低风险，读取密钥同样危险；可逆也不等于可以擅自执行。权限决策应考虑用户、资源、动作、参数、环境和影响范围，并在执行点再次检查。

### 幂等与重放

模型或网络重试可能重复调用。发送消息、付款和创建远端资源应使用幂等键；Runtime 必须区分“请求未到达”“执行成功但响应丢失”和“明确失败”。

### 状态一致性

对话记录、工具实际状态和计划状态可能分叉。关键写操作后要读取或校验真实状态；恢复会话时不能只相信自然语言摘要。

### 可观测性

事件流应至少包含模型开始/结束、文本增量、工具开始/进度/结束、权限、压缩、重试、用量和最终停止原因。可观察性与把内部推理全文塞回上下文是两回事。

## 3.13 常见失败模式

**只以“没有工具调用”判断完成。** 模型可能提前放弃、等待输入或输出被截断。

**ReAct 轨迹无限增长。** 每轮保留重复计划文字和大结果，最终把有效上下文挤掉。

**计划写完就不再更新。** 新证据与旧计划冲突，Agent 仍机械执行。

**无证据 Reflection。** 同一个模型反复评价自己，得到自信但不可验证的改写。

**工具只做 Schema 验证。** 参数类型正确，但路径越界、业务状态或权限不合法。

**把只读等同并发安全。** 忽略限流、资源锁和读取中的一致性要求。

**大结果完整回灌。** 一次日志或搜索结果耗尽上下文。

**错误结果伪装成普通文本。** 模型无法区分“没有结果”和“工具失败”。

**盲目重试副作用。** 响应丢失后重复发送、创建或支付。

**万能工具吞掉专用工具。** Shell 或浏览器能做一切，导致轨迹难审计、参数难校验。

## 3.14 测试与验收

测试应覆盖 Loop、工具契约和环境结果三层。

| 测试层 | 关键用例 | 验收 |
| --- | --- | --- |
| 单元 | Schema、路径、权限、超时、结果裁剪 | 每个分支确定可复现 |
| 调度 | 连续并发批次、资源冲突、取消 | 顺序正确，无竞态副作用 |
| 协议 | call_id 配对、孤立结果、错误结构 | Provider 消息始终合法 |
| 行为 | 是否选对工具、是否漏步骤 | 代表任务成功率与轨迹评分 |
| 故障注入 | 429、超时、半成功、进程中断 | 不重复危险动作，可恢复或明确停止 |
| 端到端 | 环境初始态 -> 任务 -> 最终态 | 状态断言与证据通过 |

典型验收任务：

1. 要求读取两个独立文件并总结，验证只读调用并发且结果都被使用。
2. 要求修改文件并运行测试，验证“读取—修改—验证”依赖顺序。
3. 工具返回 10 MB 日志，验证落盘、摘要和按需续读。
4. 写工具执行成功但响应超时，验证幂等重试不会重复写入。
5. 模型连续三次调用同一失败工具，验证重复检测与预算停止。
6. 在危险参数上触发权限询问，验证拒绝后不会绕路执行同一副作用。

评测不要只看最终答案。还要检查工具选择、参数、顺序、权限节点、重复调用、证据和停止原因。

## 3.15 系统地图

```text
User Goal
  -> Prompt Runtime：本轮目标、规则与工具说明
  -> Model Runtime：统一返回文本 / ToolCall / StopReason
  -> Agent State Machine：决定继续、恢复、等待或停止
  -> Tool Runtime：校验 -> 权限 -> 调度 -> 执行 -> 结果治理
  -> Environment：产生真实观察和副作用
  -> Verifier：检查目标状态与证据
  -> State Machine：完成 / 修订 / 求助 / 失败
```

范式跨越不同层：ReAct 位于动态控制循环；Plan-and-Solve 原始形式是提示策略，计划物化后才进入状态控制；ToT 是带预算的候选搜索；Reflection 是局部反馈修订循环；Reflexion 再增加反馈记忆；Evaluator-Optimizer 的拓扑由代码预先定义，属于 Workflow。认知控制结构位于这些原语之上，根据证据、进展、矛盾和知识边界选择或切换策略。

## 3.16 共同结论

1. Agent Loop 的本质是模型决策与环境反馈构成的闭环。
2. ReAct、Plan-and-Solve、ToT、Reflection/Reflexion 与 Evaluator-Optimizer 分属动态控制、提示/计划、候选搜索、反馈记忆和预定义 Workflow，不应被当作同层替代品。
3. 工具是带元数据、权限和结果语义的契约，不是裸函数。
4. 生产循环必须显式管理状态、预算、取消、幂等、错误和停止原因。
5. 最终完成应由环境证据与验收契约确认，不能只由模型自报。
6. 推理原语解决“怎样处理”，认知控制结构解决“何时使用、是否有效、何时切换”。

## 3.17 本章自检

1. 工作流与 Agent 的关键区别是什么？
2. 为什么工具结果必须回到下一轮上下文？
3. ReAct 为什么属于动态控制循环，主要成本是什么？
4. Plan-and-Solve 何时只是一种提示策略，何时会成为计划控制器？
5. ToT 为什么必须同时设置分支、深度、保留宽度和评估预算？
6. Reflection 与 Reflexion 在反馈记忆上有什么区别？
7. 哪些条件应终止 Reflexion，而不是继续生成另一轮自评？
8. Evaluator-Optimizer 为什么属于预定义 Workflow？
9. 推理原语与认知控制结构分别解决什么问题？
10. 工具契约应包含哪些函数签名无法表达的元数据？
11. `is_read_only` 与 `is_concurrency_safe` 为什么不能画等号？
12. Prompt Runtime 为什么只能缩小 Policy 的工具授权集？
13. 为什么“模型不再调用工具”不足以证明任务完成？

## 3.18 开放性问题

1. Agent 应在什么条件下从 ReAct 切换为显式规划？
2. 计划的粒度如何同时兼顾可追踪性与执行灵活性？
3. 当评审模型与执行模型意见冲突时，谁应拥有最终决定权？
4. 工具数量增长时，动态裁剪、工具搜索和分层命名哪种策略更有效？
5. 如何自动检测 Agent 正在重复相同策略，而不是进行有价值的重试？
6. 对“执行成功但响应丢失”的外部 API，怎样设计通用恢复协议？
7. 哪些工具结果应该进入对话历史，哪些只应保存在审计 Trace？
8. 环境具有并发写入时，Agent 的观察应采用强一致、最终一致还是带版本快照？

## 3.19 原文入口

### 本地来源

- [《AI Agents in Action（第二版）》第 5 章：Agent 推理与规划](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/5.智能体推理与规划.md)
- [《AI Agents in Action（第二版）》第 10 章：认知与元认知 Agent](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/10.探索会思考、监控和适应的认知智能体.md)
- [learn-claude-code s01：Agent Loop](../../source/learn-claude-code/s01_agent_loop/README.md)
- [learn-claude-code s02：Tool Use](../../source/learn-claude-code/s02_tool_use/README.md)
- [Hello-Agents Ch04：智能体经典范式构建](../../source/hello-agents/docs/chapter4/第四章%20智能体经典范式构建.md)
- [Hello-Agents Ch07：构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [Alice 方法论：Agent 主循环](../../source/Alice_methodology/chapters/03-agent-loop.md)
- [Alice 方法论：工具系统](../../source/Alice_methodology/chapters/04-tool-system.md)
- [Hermes：请求旅程](../../source/hermes-book/src/part2/ch03-request-journey.md)
- [Hermes：AIAgent 内核](../../source/hermes-book/src/part2/ch04-aiagent-core.md)
- [Hermes：工具系统](../../source/hermes-book/src/part3/ch06-tool-system.md)
- [Harness Engineering：工具系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch02.md)
- [Harness Engineering：Agent Loop](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch03.md)
- [Claude Code 分析：Tool Call 机制](../../source/claude-code-analysis/analysis/04b-tool-call-implementation.md)

### 论文与官方资料

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Anthropic：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI：Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
