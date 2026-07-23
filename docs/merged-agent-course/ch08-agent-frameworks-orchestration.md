# 第 8 章：Agent 框架与应用编排

> 本章目标：理解 Agent 框架究竟抽象了什么、没有解决什么，并能根据任务拓扑选择直接 Agent Loop、链式组合、状态图或产品平台。读完后，你应该能使用 LangChain 组织模型、工具、中间件和结构化输出，能用 LangGraph 显式建模状态、节点、分支、循环、中断和持久执行，也能判断何时自建轻量框架、何时使用低代码边界案例，以及怎样测试和治理编排层。

## 8.1 学习目标与边界

本章讨论**单个 Agent 应用内部的组件组织和执行编排**。核心问题是：模型、工具、检索、确定性代码、状态持久化、人工审批和错误恢复怎样组成一个可维护应用？

边界如下：

- Agent Loop、ReAct、Plan-and-Solve 等基本范式属于第 3 章，本章只讲怎样将其框架化。
- 会话、事件、状态、检查点和上下文的语义属于第 6 章，本章只讲框架如何承载这些契约。
- 长期记忆和 RAG 分别属于第 7、8 章，本章不因框架中出现 `memory` 或 `retriever` 名称而重讲它们。
- 权限、沙箱和隐私治理属于第 9 章；框架的回调或中间件不能自动构成安全边界。
- 多 Agent 的角色分工、通信协议和团队任务系统属于第 16 章。本章只说明一个 Agent 或子图可以作为编排节点，不展开群体协作。

## 8.2 框架不是 Agent 的本质

一个最小 Agent Loop 只需要模型调用、工具执行和停止条件：

```python
messages = [user_message]

while within_budget():
    response = model.generate(messages, tool_schemas)
    if not response.tool_calls:
        return response.text

    for call in response.tool_calls:
        result = execute_tool(call)
        messages.append(tool_result_message(call.id, result))
```

框架不会创造智能，也不会替应用决定目标、权限和验收标准。它的价值是把不断重复的工程责任变成稳定契约：

- 统一模型和消息接口。
- 声明、注册、调用和观察工具。
- 组合确定性步骤与模型步骤。
- 管理状态更新、分支、循环和并行。
- 提供重试、超时、流式输出和结构化结果。
- 接入持久化、中断、人工审批和恢复。
- 统一 Trace、测试替身和部署接口。

框架代价同样真实：学习曲线、版本变化、隐藏控制流、依赖膨胀、调试跨层和供应商锁定。选择框架的正确问题不是“哪个最流行”，而是“我的复杂度主要在哪里，框架是否让这部分更显式、更可测”。

## 8.3 四层抽象：不要把 SDK、框架、运行时和平台混为一谈

| 层 | 主要职责 | 代表形态 |
| --- | --- | --- |
| Model / Tool SDK | 调用模型 API、声明工具、接收流式事件 | 官方 SDK、协议客户端 |
| Agent Framework | 组件抽象、Agent Loop、链、图、中间件 | LangChain、LangGraph、自建框架 |
| Runtime / Harness | 会话、权限、持久化、任务、观测、恢复 | 服务端运行时、编码 Agent Harness |
| Application Platform | UI、知识库、触发器、发布和运营 | 低代码产品、工作流平台 |

一套产品可能同时使用四层。例如 LangChain 组织 Agent 组件，LangGraph 执行状态图，业务 Harness 负责身份、权限和持久任务，低代码界面让运营人员配置知识源。把这些都叫“框架”，会导致错误期待。

## 8.4 什么时候不用框架

以下情况直接代码通常更合适：

- 只有一个短 Agent Loop 和少量工具。
- 流程简单、边界清楚，十几个函数就能完整表达。
- 需要严格控制依赖、冷启动和二进制大小。
- 目标是学习机制或验证产品问题，而不是搭建通用平台。
- 框架抽象与领域模型不匹配，适配层比业务代码更复杂。

不用框架不等于不要架构。至少仍应拆开模型适配、工具执行、状态、策略和观测。反过来，使用框架也不应把业务领域对象全部改造成框架对象。

一个实用原则：**先用普通函数和清晰数据结构表达业务，再让框架负责组合、调度和生命周期。**

## 8.5 选择编排形态：Loop、Chain、DAG、Graph 与 Durable Workflow

### 8.5.1 直接 Loop

适合步骤由模型动态决定、控制结构简单的工具型 Agent。优点是抽象少；缺点是分支、审批、恢复和复杂测试容易全部挤进一个循环。

### 8.5.2 Chain

```text
input -> classify -> retrieve -> prompt -> model -> parse -> output
```

适合顺序固定、每步输入输出明确的流程。链的优势是可读和可组合；一旦出现多分支、回环和中断，嵌套条件会快速膨胀。

### 8.5.3 DAG

有向无环图适合可并行、最终汇聚的任务，例如同时从多个来源检索，再统一重排。它能表达 fan-out / fan-in，但不适合天然需要迭代的 Agent Loop。

### 8.5.4 State Graph

状态图允许节点、条件边、循环和中断，适合：

- 需要反思、重试或多轮工具调用。
- 分支由结构化状态决定。
- 需要人工审批后恢复。
- 需要查看每一步状态和路径。

### 8.5.5 Durable Workflow

当任务持续数小时或数天、跨进程恢复、包含外部副作用和调度时，仅有内存图还不够，需要持久检查点、幂等活动、租约、重试策略和任务运行时。图描述控制流，Durable Runtime 保证它在故障中继续执行。

| 形态 | 动态决策 | 循环 | 持久恢复 | 最适合 |
| --- | --- | --- | --- | --- |
| 直接 Loop | 高 | 天然 | 需自建 | 小型工具 Agent |
| Chain | 低 | 不自然 | 需外部支持 | 固定转换管线 |
| DAG | 中 | 无 | 视引擎而定 | 并行数据流 |
| State Graph | 高 | 支持 | 可接 Checkpointer | 复杂 Agent 应用 |
| Durable Workflow | 中高 | 支持 | 核心能力 | 长任务和外部副作用 |

### 8.5.6 Agent 节点与确定性节点怎样分工

Flow 不等于“把每一步都换成 Agent”。一个可维护的 Agent Flow 往往交替使用模型节点和普通代码节点：

- 需要理解模糊意图、比较开放证据、生成候选方案时，使用 Agent 节点。
- 规则已经明确、输入输出可枚举、结果必须复现时，使用确定性节点。
- Schema 校验、权限裁决、预算、终止条件、幂等、副作用提交和固定业务路由，不应外包给模型自由判断。
- 模型输出进入下一个节点前，先收窄为结构化状态；不要让后续代码解析一段自由文本来决定是否付款、写文件或继续循环。

例如，研究 Agent 可以决定“还缺哪类证据”，但“候选来源是否为空”“是否超过检索上限”“能否访问该租户文档”应由代码判断。来源教程把一个自由执行的单 Agent 拆成多个专用 Agent 后，又在“是否找到来源”处加入普通条件分支；真正值得迁移的不是具体 SDK 写法，而是这个原则：**只在需要语义判断的局部保留自主性，在稳定边界恢复确定性。**

是否应从单 Agent 升级为 Flow，可以观察三类信号：工具和 Prompt 已多到难以选择；不同职责需要不同上下文或权限；某些阶段需要独立测试、重试或审批。拆分后的节点不必全是 Agent，先加入一个确定性控制点，往往比再增加一个“管理 Agent”更有效。

### 8.5.7 认知控制结构在编排层怎样落地

第 3 章已经区分了推理原语与认知控制结构。本节不重复比较 CoT、ReAct、ToT 和 Reflexion，而是说明框架怎样把策略选择、运行信号和确定性路由落实为可测试的状态编排。

一种实现模式是建立结构化共享工作空间：

```text
CognitiveWorkspace
  task: 任务类型、歧义、复杂度
  strategy: 当前策略、子目标、备选策略
  evidence: 中间结果、来源、质量标记、矛盾
  progress: 已执行步骤、失败方法、预算、进展信号
  attention_signal: NONE | KNOWLEDGE_GAP | CONTRADICTION |
                    STAGNATION | LOW_CONFIDENCE | TASK_COMPLETE
```

它不是完整对话历史，也不是让多个 Agent 随意写入的黑板。字段必须有类型、所有权和更新规则；原始工具结果留在工件存储中，工作空间只保存控制流需要的引用和摘要。各模块可以提出信号，但下一步由代码路由：

```text
TASK_COMPLETE  -> RESPOND
CONTRADICTION  -> PLAN_WITH_ALTERNATIVES
STAGNATION     -> CHANGE_STRATEGY_OR_ESCALATE
KNOWLEDGE_GAP  -> RETRIEVE
LOW_CONFIDENCE -> GATHER_MORE_OR_ESCALATE
otherwise      -> NEXT_PLANNED_STEP
```

这里的“注意力”是工程路由器，不是对模型心智的宣称。模型可以负责识别歧义、评价证据或提出策略，但停滞计数、预算、权限、最大重试和最终路由应尽量由可测试代码执行。也不要直接相信模型自报的置信度；应结合检索覆盖、证据冲突、重复动作、评测器结果和历史校准数据形成信号。

这种模式属于**单个 Agent 应用内部的状态与编排**。它可以嵌在一次短 Run 中，也可以由 Durable Workflow 承载；它不等同于第 15 章讨论的长期执行、恢复和治理，也不应被并入 Loop Engineering。

## 8.6 框架设计的最小稳定内核

Hello-Agents 的自建框架材料从 Message、Config、LLM、Agent 基类和 Tool Registry 开始。这条学习路线的价值不在于再造所有生态，而在于暴露最小内核。

### 8.6.1 Message：统一内容协议

消息不能永远只有 `{role, content: str}`。工具调用、多模态、引用、流式增量和供应商特有字段都需要表达。稳定消息层应：

- 用明确 role 和 content block 类型。
- 保存 tool call ID 与 tool result 的对应关系。
- 保留供应商原始响应引用，但不让业务依赖其内部形状。
- 支持序列化和 schema 版本。
- 区分用户可见内容、模型可见内容和运行时事件。

### 8.6.2 Model Adapter：统一能力，不假装完全相同

模型适配层可以统一 `invoke / stream / structured_output / bind_tools` 等能力，但必须暴露能力差异：是否支持并行工具、原生 JSON Schema、图像、缓存、reasoning 参数和最大上下文。所谓“统一接口”不能通过静默丢弃参数实现。

### 8.6.3 Tool Contract：Schema、策略与执行分离

工具至少包含：

```text
Tool Definition
  name / description / input schema / output schema

Tool Policy
  actor / scope / permission / approval / rate limit

Tool Executor
  validate / execute / timeout / cancel / idempotency

Tool Observation
  call ID / result / error / duration / side-effect metadata
```

框架可以统一注册和调用，但权限判断必须由可信策略层执行。

### 8.6.4 Agent：组合策略，不变成上帝对象

Agent 基类可以声明模型、工具、Prompt、输出和运行入口；会话存储、权限、检索、日志和部署不应全部作为它的可变字段。依赖通过 Runtime Context 注入，比隐藏在全局单例中更易测试。

### 8.6.5 Exceptions 与事件

区分可重试的网络错误、模型拒绝、工具参数错误、权限拒绝、业务失败、超时和取消。只捕获一个 `Exception` 再告诉模型“重试”会制造副作用和无限循环。

## 8.7 LangChain：组件化与标准 Agent 入口

LangChain 适合在应用层统一模型、消息、工具、Retriever、结构化输出和中间件。当前 Python v1 的标准 Agent 入口是 `create_agent`，其底层运行在 LangGraph 之上；对于确定性数据流，Runnable 仍提供可组合调用接口。

### 8.7.1 Runnable：统一调用语义

Runnable 的关键价值不是管道运算符本身，而是让组件共享一组调用能力：同步 `invoke`、异步 `ainvoke`、批处理、流式输出、配置和 Trace。

```python
prompt = build_prompt_component()
model = build_model_component()
parser = build_parser_component()

chain = prompt | model | parser
result = chain.invoke({"topic": "Agent 编排"})
```

线性组合适合纯转换。若中间步骤需要复杂条件、循环、持久化或人工介入，应升级为显式图，而不是在 `RunnableLambda` 里隐藏一整套状态机。

### 8.7.2 `create_agent`：标准工具循环

一个最小示意：

```python
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def search_docs(query: str) -> str:
    """Search authorized project documentation."""
    return retrieve_authorized_docs(query)


agent = create_agent(
    model="provider:model-name",
    tools=[search_docs],
    system_prompt="Use tools when external evidence is required.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "退款政策是什么？"}]
})
```

`create_agent` 封装的是标准模型-工具循环。产品仍需决定工具权限、知识 ACL、最大步骤、成本、输出验收和用户身份。

### 8.7.3 Structured Output

模型输出用于路由或写数据库时，应使用 JSON Schema、TypedDict 或 Pydantic 等结构化契约，而不是用字符串 `split()` 提取标签。

```python
class RouteDecision(TypedDict):
    route: Literal["policy", "order", "handoff"]
    reason: str
    confidence: float
```

结构化输出仍要做业务校验：合法枚举、置信阈值、字段关系和默认分支。Schema 约束格式，不保证事实正确。

### 8.7.4 Middleware：在边界处扩展

LangChain Middleware 可以围绕模型和工具调用实现动态 Prompt、模型路由、重试、PII 处理、人工审批、日志和终止控制。适合横切关注点，但要防止“所有逻辑都放中间件”：

- 业务步骤应保留为节点或领域服务。
- 安全策略由可信代码判断，中间件只是执行接入点。
- 多个中间件的顺序必须文档化和测试。
- Middleware 随 Agent 作为节点嵌入更大 LangGraph 时，行为仍会生效，需避免重复包裹。

### 8.7.5 Runtime Context：依赖不是状态

数据库连接、用户 ID、权限服务、Trace Writer 和配置属于运行依赖，不应塞进可持久化 Agent State。Runtime Context 让工具和中间件按调用获取这些依赖，也便于测试时替换。

```text
State:
  这次流程中会演进、需要保存的业务数据

Runtime Context:
  用户身份、连接、服务客户端、运行配置等依赖
```

## 8.8 LangGraph：用状态图表达控制流

LangGraph 的核心不是“画图”，而是把状态更新和下一步路由变成显式协议。

### 8.8.1 State：共享数据契约

```python
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages


class SupportState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: Literal["policy", "order", "unknown"] | None
    evidence_ids: list[str]
    answer: str | None
    attempts: int
```

State 应只放节点之间必须共享、需要恢复或观察的数据。模型客户端、数据库连接和完整大文件不应进入 State。

每个字段要明确更新语义。默认更新通常是覆盖；消息或列表可能需要 reducer 追加。若没有定义 reducer，并行节点对同一字段写入会产生冲突或丢失。

### 8.8.2 Node：返回局部更新

```python
def classify(state: SupportState) -> dict:
    decision = classify_structured(state["messages"][-1])
    return {"intent": decision["route"]}
```

节点应职责单一、输入输出明确。不要原地修改完整 State 再返回；局部更新更容易追踪、测试和并行合并。

一个好节点通常只做一类工作：模型决策、工具调用、纯数据转换、验证或人工交互。把模型、检索、工具副作用和最终格式化全部放进一个节点，会让图只剩装饰作用。

### 8.8.3 Edge：用确定性路由解释流程

普通边表达固定顺序，条件边根据 State 选择下一节点。路由函数应返回受限标签：

```python
def route_intent(state: SupportState) -> str:
    if state["intent"] == "policy":
        return "retrieve_policy"
    if state["intent"] == "order":
        return "query_order"
    return "request_clarification"
```

模型可以生成结构化路由决策，但最终标签校验和兜底由代码完成。

### 8.8.4 Loop：循环必须有单调进展与上限

反思、查询改写和工具重试都可形成回边。每个循环至少要有：

- `attempts` 或预算递减。
- 可观察的进展信号。
- 最大轮次和超时。
- 无进展、重复动作或证据不足的停止条件。
- 失败出口和用户可理解的结果。

“让模型决定是否继续”不是完整停止策略。

### 8.8.5 Parallel 与 Reducer

并行适合独立检索、独立分析和 map-reduce。只有无依赖、无冲突副作用的节点才应并行。并行分支写同一字段时，Reducer 必须满足明确的合并语义，最好具备结合性和确定性。

### 8.8.6 Subgraph

子图用于封装可复用流程，例如“检索-验证-回答”或“审批后执行”。边界应使用最小输入输出 schema；不要让父图和子图共享一个不断膨胀的全局 State。

## 8.9 最小 LangGraph 实现

下面的示例把本章核心机制放进同一个最小闭环：`evidence` 使用 reducer 合并多轮检索结果；证据不足时最多改写查询两次；Checkpointer 按稳定 `thread_id` 保存状态；生成答案后通过 `interrupt()` 暂停，外部再用 `Command(resume=...)` 恢复。示例不涉及多 Agent。

```python
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class AppState(TypedDict):
    question: str
    query: str
    # 多次检索只返回增量，reducer 负责确定性合并。
    evidence: Annotated[list[dict], operator.add]
    attempts: int
    answer: str
    approved: bool | None


MAX_ATTEMPTS = 3


def retrieve_node(state: AppState) -> dict:
    evidence = retrieve_authorized_evidence(state["query"])
    return {
        "evidence": evidence,
        "attempts": state["attempts"] + 1,
    }


def route_after_retrieve(state: AppState) -> Literal["answer", "refine", "clarify"]:
    if state["evidence"]:
        return "answer"
    if state["attempts"] < MAX_ATTEMPTS:
        return "refine"
    return "clarify"


def refine_node(state: AppState) -> dict:
    refined = refine_query_with_schema(
        question=state["question"],
        previous_query=state["query"],
        attempt=state["attempts"],
    )
    return {"query": refined}


def answer_node(state: AppState) -> dict:
    return {"answer": generate_grounded_answer(state["question"], state["evidence"])}


def clarify_node(state: AppState) -> dict:
    return {"answer": "在限定检索次数内没有找到足够证据，请补充资料范围。"}


def review_node(state: AppState) -> dict:
    # interrupt 之前不执行外部副作用；恢复时该节点会从头重跑。
    decision = interrupt({
        "question": state["question"],
        "draft_answer": state["answer"],
        "evidence_count": len(state["evidence"]),
    })
    approved = bool(decision.get("approved", False))
    if approved:
        return {"approved": True}
    return {
        "approved": False,
        "answer": f"人工未批准当前答案：{decision.get('feedback', '未提供原因')}",
    }


graph = StateGraph(AppState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("refine", refine_node)
graph.add_node("answer", answer_node)
graph.add_node("clarify", clarify_node)
graph.add_node("review", review_node)

graph.add_edge(START, "retrieve")
graph.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {"answer": "answer", "refine": "refine", "clarify": "clarify"},
)
graph.add_edge("refine", "retrieve")  # 有上限、有进展字段的循环
graph.add_edge("answer", "review")
graph.add_edge("review", END)
graph.add_edge("clarify", END)

# 教学示例使用内存 Checkpointer；生产环境应替换为耐久后端。
app = graph.compile(checkpointer=InMemorySaver())

# thread_id 是保存、查找和恢复同一条执行线程的稳定键。
config = {"configurable": {"thread_id": "support-thread-42"}}

first = app.invoke(
    {
        "question": "企业版退款时限是什么？",
        "query": "企业版退款时限",
        "evidence": [],
        "attempts": 0,
        "answer": "",
        "approved": None,
    },
    config=config,
)

# first 在 review_node 处返回 __interrupt__。使用同一个 thread_id 恢复，
# Command(resume=...) 的值会成为 interrupt() 的返回值。
resumed = app.invoke(
    Command(resume={"approved": True, "feedback": "证据充分"}),
    config=config,
)
```

这段代码没有把框架当成安全系统：`retrieve_authorized_evidence` 仍由应用提供。循环的单调进展由 `attempts` 表达，`MAX_ATTEMPTS` 提供硬停止；`operator.add` 只合并各轮新增证据；Checkpointer 与 `thread_id` 让中断状态可恢复。`InMemorySaver` 仅用于教学，进程退出后数据会消失，生产环境必须换成耐久 Checkpointer。若从历史检查点重放，检查点之后的节点会重新执行，因此外部副作用仍需幂等。

## 8.10 持久化、中断与人工介入

### 8.10.1 Checkpointer 保存的是图状态

LangGraph 编译时接入 Checkpointer，可以按 thread 保存步骤快照，支持恢复、历史查看、分叉和故障重试。它对应第 6 章的执行状态持久化，不自动等于第 7 章的长期记忆。

生产环境应使用耐久 Checkpointer，并明确 `thread_id`、租户和清理策略。内存保存器只适合测试或本地演示。

### 8.10.2 Interrupt 会重新进入节点

`interrupt()` 让图保存状态并等待外部输入，适合审批、补充信息或人工编辑。恢复时节点会从开头重新执行到 interrupt，因此 interrupt 之前的副作用必须幂等，或移动到 interrupt 之后的独立节点。

```python
from langgraph.types import interrupt


def approval_node(state):
    approved = interrupt({
        "action": state["proposed_action"],
        "risk": state["risk_summary"],
    })
    return {"approved": bool(approved)}
```

中断载荷应可序列化，不要把数据库连接或复杂运行对象塞进去。人工批准的是具体动作与参数，不是模糊的“允许 Agent 继续”。

### 8.10.3 Replay 与副作用

重放会重新执行检查点之后的节点，包括模型调用和外部 API。发送邮件、扣款、写数据库等节点必须使用幂等键和外部提交记录。框架能恢复控制流，不能替外部系统撤销副作用。

## 8.11 错误处理：重试、降级和补偿不是一回事

| 策略 | 适用情况 | 不适用情况 |
| --- | --- | --- |
| Retry | 超时、限流、短暂网络错误 | 权限拒绝、无效参数、确定性业务失败 |
| Fallback | 等价能力的备用模型或工具 | 语义不同却假装结果等价 |
| Clarify | 用户输入缺失或歧义 | 系统内部错误 |
| Compensate | 已发生外部副作用需要业务补偿 | 可以直接原子回滚的本地更新 |
| Escalate | 高风险、证据冲突、预算耗尽 | 普通可恢复瞬时错误 |

重试策略包含最大次数、指数退避、抖动、可重试错误集合和总时间预算。工具调用若可能产生副作用，重试前必须查询前一次是否已经提交。

错误应该进入结构化状态或事件，不要只变成一段自然语言塞回模型。模型需要知道“工具暂时不可用”还是“调用被权限系统拒绝”，两者的下一步完全不同。

## 8.12 Middleware 与节点的边界

适合 Middleware 的横切逻辑：

- Trace、指标和审计。
- 模型选择、速率限制和统一超时。
- Prompt 的受控动态片段。
- 工具错误转换和敏感信息处理。
- 通用人工审批钩子。

适合节点或领域服务的业务逻辑：

- 订单审核、文档检索、报告生成。
- 业务状态迁移和规则校验。
- 需要在图上看到的决策和失败出口。
- 会影响后续路径的结构化结果。

若一个故障只能通过阅读五层 Middleware 才能理解，编排已经失去可观察性。中间件应少而有序，每层的输入输出和副作用都可测试。

## 8.13 自建框架：学机制，也要控制野心

自建轻量框架适合：

- 教学，需要看清 Agent Loop 和工具协议。
- 领域约束强，通用框架抽象不合适。
- 对依赖、性能、数据面或运行环境有严格要求。
- 只需要一个小而稳定的能力子集。

第一版建议只做：

```text
Message schema
Model adapter
Tool definition + registry + executor
Agent loop + stop policy
Structured output validation
Runtime context
Events / tracing
Explicit error taxonomy
```

不要一开始复制所有 Provider、Memory、RAG、MCP、工作流 UI 和多 Agent 特性。每增加一个抽象，都要回答：它消除了哪种真实重复或风险？

“万物皆工具”是有效的教学简化：Memory、RAG 或协议能力都能通过工具进入 Agent Loop。但在生产内部，它们仍有不同生命周期、权限和数据契约。统一调用入口不等于抹平领域边界。

## 8.14 可视化平台：区分 Agent 应用与通用工作流自动化

“低代码平台”至少包含两类不同产品形态，不能用一组功能断言概括。

| 类别 | 核心对象 | 典型控制流 | 主要价值 |
| --- | --- | --- | --- |
| Agent 应用平台 | 模型、Prompt、知识、工具、会话、Agent 运行 | 模型决策与受控工作流结合 | 快速装配面向用户的 Agent 应用 |
| 通用工作流自动化平台 | 事件、触发器、连接器、数据映射、任务步骤 | 以确定性流程和系统集成为主，模型只是可选节点 | 编排跨系统业务自动化 |

Agent 应用平台更接近本章的 Application Platform 层，重点是把模型交互、知识访问、工具和应用入口组合起来。通用工作流自动化平台更接近集成与任务编排层，重点是响应事件、连接业务系统并可靠传递数据。二者可以互相调用：Agent 把确定性副作用委托给工作流，工作流在需要语言理解时调用 Agent；但不应把每个自动化步骤都拟人化为 Agent，也不应让 Agent 自由接管原本确定性的业务事务。

是否采用可视化平台，应按实际能力逐项验证，而不是根据产品类别推断。至少检查：配置能否导出和版本化、关键节点能否自动测试、身份与凭据怎样隔离、失败怎样重试和补偿、长任务怎样恢复、Trace 能否关联到外部副作用，以及迁移时能否取回数据和流程定义。平台负责装配和运营入口，不替代 Agent 原理、权限服务、沙箱和生产治理。

## 8.15 框架选型方法

先列出应用真正的复杂度：

| 维度 | 需要问的问题 |
| --- | --- |
| 控制流 | 固定链、并行 DAG、动态 Loop 还是有状态图？ |
| 持久性 | 是否跨进程、跨天恢复？ |
| 人工介入 | 是否需要暂停、审批、修改状态再继续？ |
| 工具 | 数量、并行、权限、副作用和协议复杂度如何？ |
| 数据 | RAG、长期记忆和结构化系统怎样接入？ |
| 可观测性 | 能否查看节点、状态、工具和模型级 Trace？ |
| 测试 | 能否替换模型、冻结路由、回放状态和做契约测试？ |
| 运维 | 部署、扩缩容、队列、重试和版本迁移由谁负责？ |
| 团队 | 团队能否理解和维护抽象？ |
| 锁定 | 框架对象是否渗透领域模型，迁移成本多大？ |

然后用一个小型代表流程做 Spike：实现正常路径、一次工具失败、一次审批中断和一次恢复。只跑“Hello World”无法暴露框架真正的代价。

## 8.16 生产约束

### 8.16.1 版本与依赖

- 锁定直接和间接依赖，记录 Python / Node 运行版本。
- 框架升级先读迁移说明，在固定 Trace 与评测集上回归。
- 隔离 Provider 适配，避免业务代码到处导入供应商类。
- 持久 State 和事件必须有 schema 版本；代码升级不能让旧线程无法恢复。
- 对弃用 API 设迁移窗口，不在业务高峰自动升级。

### 8.16.2 预算与停止

运行配置至少限制：模型调用数、工具调用数、循环次数、输入输出 token、单步超时、总时长和并行度。预算由运行时扣减，不能让模型自行增加。

### 8.16.3 取消与背压

用户取消应传播到模型流、工具任务和并行分支。慢消费者需要背压或丢弃非关键进度事件；不能让流式日志耗尽内存。后台任务有租约和心跳，失联后由运行时安全接管。

### 8.16.4 观测

一次 Run 至少关联：

- 图版本、节点路径和 State revision。
- 模型、Prompt、工具和中间件版本。
- 每步输入输出摘要、耗时、token 和成本。
- 重试、Fallback、中断、审批和恢复。
- 外部副作用的幂等键与提交状态。

Trace 内容按敏感级别脱敏；可观测性不能成为数据泄露通道。

### 8.16.5 安全

框架中的 Tool、Middleware、Callback 和 Retriever 都在应用进程内运行时，它们不是沙箱。第三方集成按代码供应链审查。高风险工具在框架外层经过权限服务和隔离执行环境，不能只靠 Tool 描述里的“请谨慎使用”。

## 8.17 常见失败模式

| 失败模式 | 根因 | 修复方向 |
| --- | --- | --- |
| 简单任务被十层抽象包裹 | 先选框架后找问题 | 从普通函数开始，只抽象真实变化点 |
| State 变成全局垃圾桶 | 没有字段所有权和边界 | 最小 schema、子图、Runtime Context 分离 |
| 节点原地修改整个 State | 更新语义不透明 | 返回局部更新，定义 reducer |
| 路由靠解析自由文本 | 输出契约不稳定 | 结构化输出、枚举校验和默认分支 |
| 图里看不到真实业务 | 大节点隐藏全部逻辑 | 按模型、工具、验证和副作用拆节点 |
| Agent 无限循环 | 没有单调进展和预算 | attempt、停止条件、总预算和失败出口 |
| 重试重复发送或写入 | 副作用无幂等 | 幂等键、提交查询、补偿节点 |
| interrupt 后动作执行两次 | 不理解节点会重放 | 副作用移到中断后或确保幂等 |
| Middleware 顺序改变行为 | 隐藏的横切依赖 | 显式顺序、组合测试、减少层数 |
| Checkpointer 被当长期记忆 | 命名混淆生命周期 | 状态、Store 和长期记忆分离 |
| 框架升级后旧线程不能恢复 | State schema 无版本 | 迁移器、兼容读取和回放测试 |
| Provider Fallback 改变语义 | 只看“能返回文本” | 能力矩阵和等价性测试 |
| 低代码流程无法审查 | 配置不版本化 | 导出、diff、环境 promotion 和契约测试 |
| 以为框架自动安全 | 把 Hook 当权限边界 | 外部策略服务、沙箱和审批 |

## 8.18 测试与验收

### 8.18.1 组件契约测试

- Model Adapter 正确保留工具调用 ID、结构化输出和错误类型。
- Tool Schema 能拒绝缺字段、越界值和未知参数。
- Tool Executor 正确处理超时、取消、幂等和权限拒绝。
- Middleware 在预期顺序执行，不重复注入或吞掉错误。
- Provider 替换后，业务层看到的领域输出契约不变。

### 8.18.2 节点与路由测试

节点使用假的模型、检索器和工具做纯输入输出测试。条件边覆盖每个标签、非法标签和默认出口。循环测试至少覆盖：一次成功、多次改善、无进展、预算耗尽和取消。

```python
def test_unknown_route_goes_to_clarification():
    state = {"intent": "unknown", "messages": []}
    assert route_intent(state) == "request_clarification"
```

### 8.18.3 图拓扑测试

- START 到 END 至少存在一条合法路径。
- 高风险副作用前必经审批节点。
- 失败节点都有明确出口。
- 所有循环都有上限。
- 并行写字段都有 reducer。
- 子图输入输出符合最小 schema。

可以导出图结构做快照，但不要只依赖图片；还应对节点和边集合做机器断言。

### 8.18.4 持久化与恢复测试

1. 每个关键节点后注入崩溃，再从最近检查点恢复。
2. interrupt 后使用不同审批结果恢复，路径符合预期。
3. Replay 不重复不可幂等副作用。
4. 旧 schema 的检查点可由新代码读取或迁移。
5. 两个并发请求更新同一 thread 时不会静默覆盖。

### 8.18.5 端到端评测

固定代表任务集，记录：任务完成率、错误路由率、平均模型调用数、工具失败恢复率、人工升级率、p95 延迟、token、成本和副作用错误数。升级框架、模型或 Prompt 时用同一数据集回归。

### 8.18.6 低代码验收

- 工作流配置可导出并进入版本管理。
- 开发、测试和生产环境的变量与凭据分离。
- 关键节点能用固定输入做自动化验证。
- 平台不可用时有数据导出和迁移路径。
- 高风险动作由外部权限系统批准。

## 8.19 验收标准示例

一个中等复杂度的单 Agent 应用可以设定：

- 所有结构化路由输出都经过 schema 和枚举校验。
- 所有循环有最大步数、总时间和 token 上限。
- 所有外部副作用都带幂等键；恢复测试不产生重复提交。
- 高风险工具路径 100% 经过审批或确定性策略节点。
- 每个节点、条件边和失败出口都有自动化测试。
- 固定评测集上的任务完成率不低于无框架基线，p95 延迟和成本在预算内。
- 升级框架后，旧活动线程能够恢复或被显式迁移。
- Trace 能从最终答案定位到模型调用、工具结果、状态版本和审批记录。

具体数字应由业务风险和基线决定，不能用统一阈值代替场景判断。

## 8.20 系统地图

```text
Application Domain
  goals / policies / acceptance / business entities
  -> Orchestration Contract
       state schema
       nodes / chains / edges / loops
       structured decisions
       stop and budget policy
  -> Framework Layer
       LangChain
         model / message / tool / retriever / middleware / Runnable
       LangGraph
         StateGraph / reducer / conditional edge / subgraph
         checkpointer / interrupt / replay
       or Lightweight Custom Framework
         adapter / registry / executor / events
  -> Runtime / Harness
       identity / permission / sandbox / persistence
       scheduling / observability / deployment
  -> External Systems
       model providers / tools / databases / knowledge sources

Visual Platforms
  -> Agent Application Platform
       model / prompt / knowledge / tool / conversation
  -> General Workflow Automation Platform
       event / trigger / connector / deterministic task
  -> both call governed runtime and permission contracts
```

## 8.21 与相邻章节的接口

- 第 6 章定义 State、Event、Checkpoint 和 Context 的语义；LangGraph 等框架只是承载机制。
- 第 7 章的记忆与外部知识系统可以通过 Store、Retriever、Tool 或 Middleware 接入，但必须保持来源、生命周期和治理边界。
- 第 7 章的 Retriever 可以成为 Runnable、Tool 或图节点；检索证据契约不依赖具体框架。
- 第 9 章提供权限和沙箱；本章的 Tool Registry 只负责发现和调用入口。
- 第 11、12 章的 Skill、插件和协议可以扩展框架能力，但第三方能力必须接受同一策略与观测。
- 第 16 章可以把 Agent 或子图作为团队节点；本章不把多个节点拟人化为多个 Agent。
- 第 17、19 章将编排 Trace、评测集和部署约束扩展为完整生产体系。

## 8.22 共同结论

融合各来源后，可以得到十二条稳定结论：

1. 框架封装工程重复，不定义 Agent 的目标、智能和责任边界。
2. 简单 Agent Loop 应保持简单；复杂度出现后再升级为链、图或 Durable Workflow。
3. SDK、Agent Framework、Runtime Harness 和低代码平台是不同层。
4. 稳定框架内核是消息、模型适配、工具契约、状态、事件和错误分类。
5. LangChain 擅长组件化和标准 Agent 入口，LangGraph 擅长显式状态与控制流。
6. State 保存会演进的业务数据，Runtime Context 提供依赖，两者不能混用。
7. 节点返回局部更新，边使用受限标签，循环必须有单调进展和硬上限。
8. Checkpointer 解决图状态恢复，不自动提供长期记忆。
9. Interrupt、Replay 和 Retry 都要求外部副作用幂等。
10. Middleware 适合横切逻辑，核心业务步骤仍应在图或领域服务中可见。
11. 低代码是应用装配层，必须补上版本、测试、权限和迁移能力。
12. 框架选型最终要通过代表流程、故障恢复和可量化评测，而不是功能清单决定。

## 8.23 本章自检

1. Agent Framework、Runtime Harness 和低代码平台分别解决什么问题？
2. 什么情况下直接 Agent Loop 比引入框架更合适？
3. Chain、DAG、State Graph 和 Durable Workflow 的适用边界是什么？
4. 一个自建框架的最小稳定内核包括哪些组件？
5. Model Adapter 为什么不应掩盖不同供应商的能力差异？
6. LangChain Runnable 和 `create_agent` 分别适合什么层次？
7. Structured Output 为什么仍需要业务校验？
8. LangGraph State 与 Runtime Context 有何区别？
9. 为什么节点应返回局部更新而不是原地修改整个 State？
10. 条件边和循环应有哪些确定性保护？
11. interrupt 前的副作用为什么必须幂等？
12. Checkpointer 为什么不是长期记忆系统？
13. 哪些逻辑适合 Middleware，哪些应保留为节点？
14. 如何用代表流程评估框架，而不是只跑 Hello World？

## 8.24 开放性问题

1. 当 Agent Loop 越来越复杂时，什么信号说明应该升级为状态图，而不是继续增加循环内条件？
2. 框架提供的高级抽象在多大程度上应进入业务代码，怎样设计防腐层降低迁移成本？
3. 模型路由、重试和 Fallback 放在 Middleware、图节点还是独立模型网关中，各有什么可观察性差异？
4. 对长任务，LangGraph Checkpointer 与通用 Durable Workflow 引擎应怎样分工？
5. 图 State 的 schema 应如何演进，才能让数月前暂停的任务在新代码上安全恢复？
6. 当一个节点内部仍包含不可观察的模型循环时，怎样判断节点边界是否过粗？
7. 低代码平台生成的工作流怎样进行语义 diff，而不只是比较大段 JSON？
8. 是否应该允许模型动态创建或修改图结构？如果允许，哪些边和节点必须由静态策略锁定？
9. 框架级 Middleware 越来越多时，怎样证明它们的组合仍满足安全和业务不变量？
10. 自建框架达到什么规模后，继续维护的成本会高于迁移到成熟生态？
11. 如何设计跨框架的 Agent 应用契约，使同一领域流程可以在 LangGraph、其他工作流引擎或自建 Runtime 上运行？
12. 当框架升级同时改变默认 Prompt、工具循环和持久化行为时，怎样隔离并定位回归来源？

## 8.25 原文入口

### 本地来源

- [easy-langent 第 3 章：LangChain 进阶组件](../../source/easy-langent/docs/guide/chapter3.md)
- [easy-langent 第 4 章：链式工作流与 RAG](../../source/easy-langent/docs/guide/chapter4.md)
- [easy-langent 第 5 章：综合应用实践](../../source/easy-langent/docs/guide/chapter5.md)
- [easy-langent 第 6 章：LangGraph 基础](../../source/easy-langent/docs/guide/chapter6.md)
- [easy-langent 第 7 章：LangGraph 进阶](../../source/easy-langent/docs/guide/chapter7.md)
- [easy-langent 第 8 章：图式游戏编排](../../source/easy-langent/docs/guide/chapter8.md)
- [easy-langent：谁是卧底图构建](../../source/easy-langent/project/WhoIsTheSpyBaocaiLi/spy_game/graph_build.py)
- [easy-langent：数据 Agent 的 LangChain Agent 入口](../../source/easy-langent/project/DataAgent/backend/src/agent.py)
- [Hello-Agents 第 5 章：低代码平台](../../source/hello-agents/docs/chapter5/%E7%AC%AC%E4%BA%94%E7%AB%A0%20%E5%9F%BA%E4%BA%8E%E4%BD%8E%E4%BB%A3%E7%A0%81%E5%B9%B3%E5%8F%B0%E7%9A%84%E6%99%BA%E8%83%BD%E4%BD%93%E6%90%AD%E5%BB%BA.md)
- [Hello-Agents 第 6 章：框架开发实践](../../source/hello-agents/docs/chapter6/%E7%AC%AC%E5%85%AD%E7%AB%A0%20%E6%A1%86%E6%9E%B6%E5%BC%80%E5%8F%91%E5%AE%9E%E8%B7%B5.md)
- [Hello-Agents 第 7 章：构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/%E7%AC%AC%E4%B8%83%E7%AB%A0%20%E6%9E%84%E5%BB%BA%E4%BD%A0%E7%9A%84Agent%E6%A1%86%E6%9E%B6.md)
- [Hello-Agents：LangGraph 示例](../../source/hello-agents/code/chapter6/Langgraph/Dialogue_System.py)
- [Hello-Agents：AgentScope 示例](../../source/hello-agents/code/chapter6/AgentScopeDemo/README.md)
- [Hello-Agents：AutoGen 示例](../../source/hello-agents/code/chapter6/AutoGenDemo/README.md)
- [Hello-Agents：CAMEL 示例](../../source/hello-agents/code/chapter6/CAMEL/DigitalBookWriting.py)
- [Hermes Book：模型抽象](../../source/hermes-book/src/part6/ch18-model-abstraction.md)
- [learn-claude-code：最小 Agent Loop](../../source/learn-claude-code/s01_agent_loop/README.md)
- [harness-engineering：从 Loop 到 Harness](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch03.md)
- [AI Agents in Action 第 4 章：Agent 与 Flow 的边界](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/4.架构与构建多智能体系统.md)
- [AI Agents in Action 第 10 章：推理原语与认知架构](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/10.探索会思考、监控和适应的认知智能体.md)
- [AI Agents in Action 第 11 章：五层实践与应用蓝图](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/11.构建智能体系统的实用技巧.md)
- [深入理解 AI Agent：第 1 章 工作流模式与 Harness](../../source/ai-agent-book/book/chapter1.md)
- [深入理解 AI Agent：第 5 章 Agent 应用与生成式界面](../../source/ai-agent-book/book/chapter5.md)

### 外部资料

- [LangChain 官方：Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain 官方：Middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [LangChain 官方：Runtime](https://docs.langchain.com/oss/python/langchain/runtime)
- [LangGraph 官方：Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph 官方：Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph 官方：Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
