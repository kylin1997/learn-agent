# 第 5 章：模型运行时、路由与调用可靠性

> 本章目标：把“调用一次模型 API”升级为可替换、可路由、可流式、可降级、可观测的模型运行时。读完后，你应该能定义统一 Provider Adapter、能力驱动路由和结构化事件流，并针对重试、fallback、成本与协议兼容性建立可靠性边界。

## 5.1 学习目标与边界

本章回答：**这一次模型请求应由哪个模型、以什么协议、怎样稳定完成？**

你将学会：

- 区分 Prompt Runtime、Model Runtime、Provider Adapter 和 Router。
- 设计统一消息、工具调用、输出项和流式事件协议。
- 用能力矩阵而不是模型名称做兼容判断。
- 把瞬态错误、请求错误、上下文错误和协议错误分开恢复。
- 设计有预算的重试、语义兼容的 fallback 和幂等控制。
- 按调用场景路由模型并观测 Token、缓存、延迟和成本。
- 为 Adapter、事件流、路由和故障恢复建立契约测试。

本章不重新讲 Prompt 内容，也不负责真正执行客户端工具。Model Runtime 是模型调用的生命周期边界，负责调度 Route、超时、取消、恢复策略、事件转发、用量和 Trace；Provider 请求编码、原始流解析、PTC 协议项和错误归一属于 Adapter。两者都不能越过 Policy 授权或替代 Tool Runtime 执行客户端工具。

## 5.2 为什么不能在 Agent Loop 里直接调用 SDK

Demo 常从一行开始：

```python
client.responses.create(model="some-model", input=messages)
```

Agent 产品很快会遇到：

- 不同 Provider 的消息、工具和流式格式不同。
- 同一 Provider 的不同 API 也有不同协议项。
- 模型能力、上下文、输出上限和参数支持不同。
- 主对话、压缩、记忆、分类和子 Agent 需要不同模型。
- 限流、过载、超时、断流和区域故障需要恢复。
- fallback 模型可能不支持当前工具或上下文。
- 每次调用都要记录来源、用量、缓存、延迟和成本。

如果这些分支进入 Agent Loop，循环会被供应商细节污染。更好的分层是：

```text
Agent Loop
  -> Policy：这次最多允许哪些工具与数据边界
  -> 语义声明：任务需要什么能力、输出和风险等级
  -> Model Router：选择逻辑模型/执行计划
  -> Prompt Runtime：按已选模型能力组装最终 Prompt
  -> Model Runtime：管理调用生命周期与恢复
  -> Provider Adapter：编码请求、解析响应与查询 Provider Run
  -> Provider API
```

上层只依赖内部协议。Provider 可以替换，循环控制不变。

## 5.3 四个核心组件

### 5.3.1 Model Runtime

模型调用总入口，负责 Route 执行、请求生命周期、事件转发、取消、超时、重试/fallback 决策编排、用量汇总和 Trace。它消费 Adapter 归一后的错误与副作用证据，但不解析 Provider 原始协议。

### 5.3.2 Router

根据调用场景、必需能力、风险、延迟、预算、健康状态和用户策略选择模型配置。Router 输出的是**执行计划**，不只是模型字符串。

### 5.3.3 Provider Adapter

把内部消息、工具和参数转换为 Provider 请求；把 Provider 流转换为统一事件；保留 Provider 要求续传的协议项；暴露 Provider Run 查询与可验证的执行状态。Adapter 负责描述事实，不负责决定业务上是否重试或 fallback。

### 5.3.4 Model Registry

保存模型与 Provider 的能力、限制、定价、区域、版本和健康信息。Registry 是路由的事实来源，不应把能力判断散落在 `if model.startswith(...)` 中。

## 5.4 先定义内部协议

### 5.4.1 两阶段请求：先声明语义，再按模型准备

```python
@dataclass
class TaskSemanticRequirements:
    caller: str
    required_capabilities: set[str]
    output_contract: dict | None
    authorized_tool_ids: frozenset[str]
    relevant_tool_ids: frozenset[str]
    latency_class: str
    quality_class: str
    risk_class: str
    effect_class: str          # pure_generation / may_have_effects
    data_policy: dict


@dataclass
class PreparedModelRequest:
    caller: str
    route_id: str
    messages: list[Message]
    tools: list[ToolSchema]
    output_schema: dict | None
    max_output_tokens: int
    idempotency_key: str
    effect_class: str
    metadata: dict
```

阶段一由任务准备层声明 `TaskSemanticRequirements`。Policy 先产出 `authorized_tool_ids`，Prompt Runtime 的相关性筛选只能得到其子集：

```text
relevant_tool_ids ⊆ authorized_tool_ids
```

Router 只依赖这份模型无关的语义声明和 Registry，不依赖已经为某个模型渲染的 Prompt。选出 Route 后，Prompt Runtime 才根据确定的能力组装消息、输出 Schema 和相关工具，形成 `PreparedModelRequest`。这与第 4 章的两阶段协议一致，也避免 Prompt 与路由互相等待。

`caller` 表示谁发起调用，例如 `main_chat`、`compact`、`memory_extract`、`permission_classify`、`review`、`subagent`。它是成本归因和路由策略的关键字段。`effect_class` 则是恢复策略的硬输入：只要请求允许服务端工具或 PTC，就不能标成 `pure_generation`。

### 5.4.2 统一消息与输出项

只抽象纯文本是不够的。Agent 需要表达：

```text
TextPart
ImagePart
ToolCall(id, caller_id?)
ToolResult(call_id)
ProgramItem(id)
ProgramOutput(program_id, child_call_ids)
StructuredOutput
ReasoningItem（仅作为受 Provider 协议约束的 opaque item）
Refusal / SafetyItem
```

内部类型应保留 item ID、`call_id`、顺序、角色和来源。`ToolResult.call_id` 指向对应的 `ToolCall.id`；由程序发起的工具调用还要通过 `ToolCall.caller_id` 指向 `ProgramItem.id`。`ProgramOutput.program_id` 回指程序项，并保留其 `child_call_ids`。这样既能表达普通模型工具调用，也能表达 Programmatic Tool Calling 中“程序产生多个调用并汇总输出”的层级。

不能把程序、工具调用与结果压扁为普通字符串，否则会丢失 caller/call 配对、结构校验、审计和 Provider 续传语义。PTC 的原始类型可能因 Provider 而异，统一 `ProgramItem` / `ProgramOutput` 及关联关系的编码和归一必须落在 Adapter。

### 5.4.3 统一流式事件

```python
class EventType(Enum):
    RESPONSE_STARTED = "response_started"
    TEXT_DELTA = "text_delta"
    REASONING_DELTA = "reasoning_delta"
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_DELTA = "tool_call_delta"
    TOOL_CALL_COMPLETED = "tool_call_completed"
    PROGRAM_STARTED = "program_started"
    PROGRAM_DELTA = "program_delta"
    PROGRAM_COMPLETED = "program_completed"
    PROGRAM_OUTPUT = "program_output"
    OUTPUT_ITEM_COMPLETED = "output_item_completed"
    USAGE = "usage"
    RESPONSE_COMPLETED = "response_completed"
    ERROR = "error"
```

事件要同时服务三个消费者：UI 需要渐进展示，Agent Loop 需要完整语义项，观测系统需要延迟和用量。`PROGRAM_*` 事件和最终 `ProgramItem` / `ProgramOutput` 必须沿用同一程序 ID，子工具事件必须携带 `caller_id`，工具结果必须携带 `call_id`。不要让 UI 直接解析 Provider 原始 SSE，也不要在 Event Stream 层重新猜测这些关联。

## 5.5 Provider Adapter 的双向职责

### 请求方向

Adapter 负责：

- 消息角色与多模态内容编码。
- 已授权相关子集中的工具 Schema、工具选择和结构化输出编码；不得自行补入工具。
- 模型专属参数映射与不支持参数剔除。
- 上下文与输出预算校验。
- 缓存、推理续传和前一响应引用等协议项。
- Programmatic Tool Calling 的程序定义、允许 caller、程序—调用关联与 Provider 专属参数编码。
- 鉴权、端点、区域、代理和请求头。

### 响应方向

Adapter 负责：

- 解析文本、工具参数增量和完整输出项。
- 处理一个响应中的多个并行工具调用。
- 把 PTC 归一为 `ProgramItem`、`ProgramOutput` 与子 `ToolCall`，保留 `caller_id` / `call_id` 关联。
- 保留 `call_id`、item ID、Provider Run ID、finish/stop reason 和 Provider 元数据。
- 归一用量、缓存 Token 和安全中止。
- 把 SDK 异常映射为内部错误分类。
- 在 Provider 支持时查询 Run 状态、服务端工具执行记录和幂等结果，返回可验证的副作用证据。

Adapter 不应做业务路由、权限决策、恢复策略决策或真正执行客户端工具。它的目标是**协议忠实、语义无损和状态可查询**。Model Runtime 根据 Adapter 提供的规范错误与状态证据执行恢复策略；这条边界避免了“Adapter 决定 fallback、Runtime 又声称统一管理生命周期”的职责冲突。

## 5.6 能力矩阵

Provider 配置不应只包含 `base_url` 和 `api_key`。至少需要：

```yaml
id: provider/model-profile
provider: example
model: model-version
api_mode: responses
capabilities:
  streaming: true
  tools: native
  parallel_tool_calls: true
  server_side_tools: true
  programmatic_tool_calling: true
  provider_run_query: true
  structured_output: json_schema
  vision: true
  reasoning_items: opaque_persisted
limits:
  context_tokens: 200000
  max_output_tokens: 32000
pricing:
  input_per_million: 0
  cached_input_per_million: 0
  output_per_million: 0
reliability:
  region: local
  timeout_ms: 120000
  fallback_group: general-tools
```

能力应区分：

- `native`：Provider 原生且契约测试通过。
- `emulated`：通过文本/XML 等协议模拟。
- `unsupported`：不能安全降级。
- `unknown`：尚未验证，不能默认当作支持。

XML 或文本工具调用模拟能扩大模型覆盖，但解析更脆、调用质量更低。它应作为显式降级能力，而不是伪装成与原生工具调用等价。

## 5.7 路由不是“选最强模型”

### 5.7.1 硬约束先过滤

先排除不满足以下条件的候选：

- 必需模态与工具能力。
- 当前上下文与输出预算。
- 数据驻留和隐私要求。
- 区域、租户、用户允许的 Provider。
- 结构化输出和协议续传要求。
- 当前健康状态与配额。

### 5.7.2 再按软目标排序

在可行候选中权衡：

```text
预计任务成功率
P95 首 Token / 总延迟
预计 Token 与成本
近期错误率与限流
缓存命中机会
用户偏好与质量等级
```

一个简单评分只用于表达思路：

$$
score(m)=w_qQ(m)-w_cC(m)-w_lL(m)-w_eE(m)
$$

其中 $Q$ 是任务质量预测，$C$ 是成本，$L$ 是延迟，$E$ 是近期错误风险。真正生产系统还要先满足硬约束，不能用高质量分数抵消安全或能力缺失。

### 5.7.3 按调用场景配置

| caller | 主要目标 | 常见策略 |
| --- | --- | --- |
| 主对话/复杂编码 | 质量、工具、长上下文 | 强模型，能力完整 |
| 标题/分类 | 低延迟、低成本 | 小模型或规则优先 |
| 上下文压缩 | 长输入、摘要忠实 | 稳定摘要模型，无工具 |
| 记忆提取 | 结构化、便宜 | 低价模型 + Schema |
| 权限分类 | 保守、快、可解释 | 规则优先，模型辅助 |
| 评审/验证 | 独立性、判错能力 | 与生成路径不同配置 |
| 后台批处理 | 吞吐与成本 | 批处理/弹性队列 |

所有任务都用最强模型会浪费成本；所有任务都用便宜模型会把失败成本转移到重试、人工和错误结果。

## 5.8 流式事件是一条协议，不是字符串拼接

Provider 的工具参数可能以多个增量到达：

```text
tool_call_started(id=call_1, name=read_file)
tool_call_delta(id=call_1, arguments='{"pa')
tool_call_delta(id=call_1, arguments='th":"README.md"}')
tool_call_completed(id=call_1)
```

Adapter 应按调用 ID 分别累积，完成后再解析 JSON：

```python
buffers = {}

def on_event(event):
    if event.type == "tool_call_started":
        buffers[event.call_id] = {"name": event.name, "json": ""}
    elif event.type == "tool_call_delta":
        buffers[event.call_id]["json"] += event.delta
    elif event.type == "tool_call_completed":
        raw = buffers.pop(event.call_id)
        emit(ToolCall(
            id=event.call_id,
            name=raw["name"],
            arguments=parse_json(raw["json"]),
        ))
```

流式可靠性还需要：

- 首 Token 超时与流空闲超时分开。
- 心跳与业务事件分开。
- 客户端背压和取消传播。
- 断流时标记响应是否已产生可见输出或完整工具调用。
- 用量可能只在尾事件出现，尾事件缺失时标记为估算。

这些标记用于流重组、UI 和观测，不是副作用证据。服务端工具/PTC 是否实际执行，必须由 Provider Run 查询、工具执行账本或幂等记录确认。

有些系统会在模型尚未完成输出时启动已完整解析的并发安全工具。这样能降低延迟，但必须确认调用边界已闭合、参数已验证，并能在后续流中止时正确取消或收尾。

## 5.9 错误分类决定恢复策略

不要把所有异常都包成 `ModelError` 后统一重试。

| 错误类 | 例子 | 默认动作 |
| --- | --- | --- |
| 瞬态可用性 | 过载、部分 5xx、连接重置 | 退避重试，满足副作用条件时才可 fallback |
| 短期限流 | 突发 429、滚动窗口超限、带 `Retry-After` | 按重置时间退避，计入重试预算 |
| 长期配额耗尽 | 日/月额度、信用余额或项目配额耗尽，虽也可能返回 429 | 不重试同一配额池；切换已授权 profile 或停止 |
| 认证/权限 | 无效密钥、账户或模型权限 | 不盲重试；修复配置或切换合法 profile |
| 请求 | 非法参数、Schema、模型不支持能力 | 修复请求或重新路由 |
| 上下文 | prompt too long | 压缩/裁剪后有限重试 |
| 输出 | max output、结构化输出不完整 | 提高预算、续写或修复输出 |
| 内容/安全 | 安全分类器中止、媒体不合规 | 按策略处理，不用换模型绕过 |
| 流式 | 首 Token 超时、空闲、尾事件丢失 | 判断是否安全重放 |
| 协议 | 非法工具参数、孤立 item、未知事件 | Adapter 修复或明确失败 |
| 客户端取消 | 用户停止、上游超时 | 立即传播取消，不重试 |

HTTP `429` 本身不足以决定重试。Adapter 还要保留 Provider 错误码、`Retry-After`、配额类型、重置时间和余额信息，区分“稍后窗口会恢复”的短期限流与“需要充值、提额或换配额池”的长期耗尽。

错误分类还应保留可重试性、建议等待、Provider Run ID、请求是否到达、服务端工具/PTC 是否可能执行，以及原始错误的脱敏摘要。错误类型只说明故障原因，能否重放还必须结合副作用证据。

## 5.10 重试：有预算、退避和语义

指数退避加抖动的常见形式：

$$
delay=\min(base\cdot2^{attempt},cap)+U(0,jitter)
$$

若服务返回 `Retry-After`，通常优先尊重。重试还要满足：

- 只重试明确可恢复错误。
- 有最大次数和总时间预算。
- 区分模型调用重试与 Agent 任务重试。
- 记录每次尝试，最终用量不能只算成功请求。
- 避免并发请求同时重试造成惊群。
- 流式已输出内容后，不把整次重放伪装成无缝续写。

```python
async def call_with_retry(request, adapter, policy):
    started = now()
    for attempt in range(policy.max_attempts):
        try:
            return await adapter.call(request)
        except ProviderError as error:
            decision = policy.classify(error, attempt, elapsed=now() - started)
            if decision.action != "retry":
                raise
            await sleep(decision.delay_with_jitter)
    raise RetryBudgetExhausted()
```

`max_output_tokens` 截断也不能自动等价为“提高上限后重放”。**完整重放原请求只允许同时满足两个条件：请求被声明为纯生成，并且运行状态确认没有任何副作用。** 仅凭客户端没收到工具事件，不能证明服务端工具或 PTC 没有执行。

```python
def may_replay_after_truncation(request, effect_evidence):
    return (
        request.effect_class == "pure_generation"
        and effect_evidence == "proven_no_side_effect"
    )
```

满足条件时，可在预算允许范围内提高上限并重放；仍截断时，可保存已接受片段并使用带边界的续写协议。若请求允许服务端工具、PTC 或任何远端写入，或副作用状态为 `unknown`，则禁止自动完整重放：应先查询 Provider Run、幂等记录和外部状态，必要时进入人工对账。连续续写没有实质新 Token 时应停止，避免收益递减。

## 5.11 Fallback 是一次兼容性迁移

Fallback 不只是把 `model=A` 改成 `model=B`。切换前要检查：

- 工具、模态、结构化输出与上下文是否兼容。
- Provider 专属消息项能否安全转换。
- 输出预算和参数是否支持。
- 数据驻留、成本和用户策略是否仍满足。
- 当前流是否已向用户展示部分输出，以及怎样呈现恢复边界。
- Provider Run、幂等记录和外部状态能否证明副作用状态。
- 任务质量是否允许降级。

可以定义 fallback 链：

```yaml
fallback_policy:
  primary: model-a
  candidates: [model-b, model-c]
  trigger: [overloaded, region_unavailable]
  require_capabilities: [streaming, native_tools]
  max_switches: 1
  quality_floor: standard
```

### 语义兼容比 API 兼容更重要

两个模型都接受 OpenAI-compatible 请求，不代表行为等价。工具参数质量、默认主动性、结构化输出稳定性和上下文利用率都可能不同。Fallback 组必须通过同一任务契约测试，而不是只做“能返回 200”的冒烟测试。

### 没收到事件不等于没有执行

“客户端是否收到语义事件”只能说明展示状态，不能证明执行状态。服务端工具或 PTC 可能已经运行，但连接在事件送达前断开；反过来，收到文本也不必然意味着有副作用。因此 fallback 判定必须读取独立证据：

| 副作用证据 | 含义 | 自动 fallback / 完整重放 |
| --- | --- | --- |
| `proven_no_side_effect` | Provider Run 或执行账本证明未执行任何副作用 | 可在其余兼容条件满足时进行 |
| `committed_idempotent` | 已执行，但稳定幂等键证明重复不会产生第二次效果 | 仅按专门恢复策略续查或重试；不能只因换模型而重做 |
| `committed_non_idempotent` | 已发生不可安全重复的效果 | 禁止；对账后继续 |
| `unknown` | 无法确认是否执行 | 禁止；先查询 Provider Run、工具账本或人工介入 |

如果 Provider 提供 Run 查询接口，Adapter 应以 Run ID 查询服务端工具/PTC 状态并归一为上述证据；如果没有查询能力，不能把“流为空”降格为 `proven_no_side_effect`。幂等性也必须由 Provider 或 Tool Runtime 的记录证明，不能由调用名称猜测。

### 何时不应 fallback

- 安全或内容策略拒绝，不能通过换 Provider 绕过。
- 请求本身非法，换模型只会重复失败。
- 备用模型不满足数据治理或必要能力。
- 服务端工具或 PTC 的副作用状态为 `unknown`。
- 已提交非幂等副作用，或无法证明幂等键覆盖了重复执行。
- 高风险任务的质量下限无法保证。

## 5.12 幂等、重放与重复计费

纯模型生成通常没有外部副作用，但请求可能触发内置工具、程序化工具或远端状态写入。Runtime 必须在发送前知道请求是 `pure_generation` 还是 `may_have_effects`，并在故障后取得独立的 `effect_evidence`。发送前分类描述风险上限，发送后证据描述实际状态，两者缺一不可。

幂等策略包括：

- 为同一逻辑请求使用稳定的 idempotency key。
- 为每次物理尝试生成 attempt ID。
- 工具调用保留稳定 `call_id` 和父请求关联。
- 保存 Provider Run ID；响应未知时由 Adapter 查询状态，再决定是否重放。
- PTC 保留 `ProgramItem.id -> ToolCall.caller_id -> ToolResult.call_id` 的完整链路。
- 统计所有尝试的 Token 和费用，避免成本漏算。

对无法幂等的副作用，或证据仍为 `unknown` 的请求，宁可停止并请求人工确认，也不要用通用重试器自动重复。幂等键只在 Provider 或工具执行端真正识别、持久化并返回同一结果时才有效；仅在客户端请求头里生成一个 UUID 并不会自动获得幂等性。

## 5.13 模型专属参数应留在 Adapter

内部请求表达语义意图：

```python
ExecutionPolicy(
    quality="high",
    latency="interactive",
    verbosity="medium",
    reasoning_budget="balanced",
)
```

Adapter 再映射为当前模型支持的参数。以 GPT-5.6 为例，官方当前提供 `text.verbosity`、多档 `reasoning.effort`、`reasoning.context`、Pro mode、显式缓存和 Programmatic Tool Calling。它们都需要在 GPT-5.6 代表任务上校准，不能由通用 Prompt 假设存在。特别是 PTC 的请求编码、允许调用者、原始程序事件解析、`ProgramItem` / `ProgramOutput` 归一和 caller/call 关联全部属于 Adapter；Model Runtime 只消费统一事件并管理生命周期。

持久化推理、输出 item 和程序化调用关系应作为 opaque Provider 协议项保存。应用可以决定保留范围，但不能把未知字段随意转成文本、降权或摘要后仍声称协议等价。

如果某模型不支持某个内部意图，Adapter 应明确：降级、忽略并告警，或返回能力错误。静默丢弃高风险参数会让行为变化难以诊断。

## 5.14 成本不是单价乘最终 Token

一次 Agent 任务的真实成本包括：

```text
主模型调用
+ 重试与失败请求
+ 上下文压缩
+ 记忆提取
+ 权限分类
+ 评审/Reflection
+ 子 Agent 并发
+ Provider 内置工具费用
+ 缓存写入与读取
```

每次调用至少记录：

```text
request_id / attempt_id / session_id
caller / task_type
provider / model / region
prompt_profile / toolset_version
input / cached_input / cache_write / output / reasoning tokens
time_to_first_token / duration
retry_count / fallback_from / fallback_to
stop_reason / error_class
estimated_cost / pricing_version
```

`caller` 能回答“钱花在哪里”，`attempt_id` 能回答“失败重试花了多少”，`pricing_version` 能让历史估算可追溯。

### 成本优化的优先顺序

1. 消除无价值调用和重复上下文。
2. 提高缓存命中与工具结果压缩。
3. 为低风险辅助任务使用更合适模型。
4. 减少盲目重试和无收益 Reflection。
5. 最后再做单价优化。

只追求便宜模型，可能因成功率下降而增加总调用和人工成本。

## 5.15 可靠性机制

### 超时分层

- 连接超时：未建立连接。
- 首 Token 超时：连接建立但迟迟无输出。
- 流空闲超时：流中途停止进展。
- 总请求超时：整体超过任务预算。

不同超时应有不同阈值和恢复策略。长推理请求不能简单沿用标题生成的总超时。

### 熔断与健康

对持续过载或错误的 Provider，短时间熔断并进行半开探测，避免每个请求都经历完整超时。健康状态应按模型、区域和错误类细分。

### 限流与背压

本地队列应感知请求数、Token 速率和用户优先级。流式消费者处理过慢时要有背压或有界缓冲，不能无限积压事件。

### 配置与密钥

密钥、端点、代理、区域和模型 Profile 分离。日志和错误中不得泄漏密钥；配置热更新要有版本与回滚。

## 5.16 最小实现：路由、适配与可靠调用

```python
def prepare_call_plan(task, context, policy, prompt_runtime, router, registry):
    # 阶段一：Policy 先定授权上界，再声明模型无关的任务语义。
    authorized = policy.authorized_tools(context, registry.tools())
    requirements = prompt_runtime.declare_requirements(task, context, authorized)
    assert requirements.relevant_tool_ids <= requirements.authorized_tool_ids

    # Router 只读取语义需求；确定候选模型后，才按各自能力组装 Prompt。
    routes = router.plan(requirements, registry.snapshot())
    prepared_routes = []
    for route in routes:
        bundle = prompt_runtime.assemble(
            requirements=requirements,
            model_caps=route.capabilities,
            context=context,
        )
        assert tool_ids(bundle.tools) <= requirements.authorized_tool_ids
        prepared_routes.append(PreparedModelRequest(
            caller=requirements.caller,
            route_id=route.id,
            messages=materialize_messages(bundle, context.history),
            tools=bundle.tools,
            output_schema=bundle.output_schema,
            max_output_tokens=route.max_output_tokens,
            idempotency_key=context.idempotency_key,
            effect_class=requirements.effect_class,
            metadata={"prompt_manifest": bundle.manifest},
        ))
    return PreparedCallPlan(requirements, routes, prepared_routes)


class ModelRuntime:
    def __init__(self, adapters, recovery_policy, telemetry):
        self.adapters = adapters
        self.recovery_policy = recovery_policy
        self.telemetry = telemetry

    async def stream(self, plan):
        for route, request in plan.route_requests():
            adapter = self.adapters[route.provider]
            encoded = adapter.encode(request, route.profile)

            for attempt in self.recovery_policy.attempts(route):
                try:
                    async for event in self._run_once(
                        encoded, adapter, route, request, attempt
                    ):
                        self.telemetry.observe(event, request, route)
                        yield event
                    return
                except AttemptFailure as failure:
                    decision = self.recovery_policy.decide(
                        error=failure.error,
                        effect_class=request.effect_class,
                        effect_evidence=failure.effect_evidence,
                        idempotency_key=request.idempotency_key,
                        output_was_presented=failure.output_was_presented,
                        attempt=attempt,
                    )
                    if decision.action == "retry_same_route":
                        await sleep(decision.delay)
                        continue
                    if decision.action == "fallback":
                        break
                    if failure.effect_evidence == "unknown":
                        raise ReconciliationRequired(failure.error)
                    raise failure.error

        raise FallbackExhausted()

    async def _run_once(self, encoded, adapter, route, request, attempt):
        handle = await adapter.open_run(encoded, attempt)
        output_was_presented = False
        try:
            async for raw in handle.events():
                event = adapter.normalize(raw)  # 包括 ProgramItem/ProgramOutput 关联
                output_was_presented |= event.is_user_visible
                yield event
        except Exception as raw_error:
            error = adapter.classify_error(raw_error)
            evidence = await adapter.query_effect_evidence(
                provider_run_id=handle.provider_run_id,
                idempotency_key=request.idempotency_key,
            )  # 无法查询时必须返回 unknown
            raise AttemptFailure(error, evidence, output_was_presented)
```

`output_was_presented` 只用于决定 UI 怎样标记部分响应，绝不能作为“是否执行过”的证据。`recovery_policy` 只有在错误允许恢复且 `effect_evidence` 满足前述矩阵时，才可返回 `retry_same_route` 或 `fallback`；对 `unknown` 必须进入查询、对账或人工介入。

这个骨架还明确了职责：任务准备层完成 Policy、语义声明、路由和按能力组装；Model Runtime 编排生命周期与恢复；Adapter 编码协议、归一事件/错误并查询 Provider Run。真正实现还要处理取消、尾事件缺失、用量聚合，以及查询接口自身失败时的保守降级。

## 5.17 生产约束

### API 演进

Provider SDK、模型别名、参数和事件会变化。固定生产版本；对未知事件保留原始元数据并报警；升级 Adapter 时跑完整契约测试。

### 数据治理

数据区域、租户隔离、保留策略和 Zero Data Retention 等要求应在阶段一进入 `TaskSemanticRequirements`，Router 在选择模型前将其作为硬约束。不能先发送数据，再以“fallback”解释。

### 质量下限

每个路由与 fallback 组都要有任务级质量门槛。健康只表示服务可用，不表示模型适合当前任务。

### 费用一致性

Provider 用量可能延迟、缺失或口径不同。保留原始 usage 与内部归一值，标记估算；账单对账不能只依赖客户端 Tokenizer。

### 灰度发布

路由策略、模型版本和 Prompt 变更分别灰度。用 shadow traffic 或离线回放比较质量，但敏感数据和有副作用工具不能未经治理复制。

## 5.18 常见失败模式

**核心循环直连某个 SDK。** Provider 分支污染所有上层逻辑。

**只统一文本，不统一工具与协议项。** 切换 Provider 后调用—结果对损坏。

**压扁 PTC 层级。** `ProgramItem`、子 `ToolCall.caller_id` 与 `ToolResult.call_id` 失去关联，无法续传、审计或判断执行状态。

**按模型名称硬编码能力。** 别名升级或自定义端点后判断失真。

**所有错误统一重试。** 非法请求、认证和安全拒绝被无意义放大。

**把所有 429 当短期限流。** 长期配额耗尽被反复退避，既不恢复也浪费预算。

**流式参数边到边解析 JSON。** 半个 JSON 被当成完整工具调用。

**Fallback 只检查 API 兼容。** 备用模型缺工具、上下文或质量能力。

**用“没有收到事件”证明没有副作用。** 服务端工具或 PTC 可能已执行，自动 fallback 导致重复动作。

**输出截断后无条件完整重放。** 非纯生成请求或副作用状态未知时，工具可能重复执行。

**已输出内容后静默重放。** 用户看到重复文本，且展示状态与执行状态被混为一谈。

**成本只记成功请求。** 重试、后台调用和缓存写入成为盲区。

**把最高推理预算当默认最优。** 延迟与成本上升，质量未必有显著收益。

**把安全拒绝当可用性故障。** 通过换模型绕过策略边界。

## 5.19 测试与验收

### Adapter 契约测试

- 每种消息角色、多模态内容和工具 Schema 编码正确。
- 文本、多工具调用、结构化输出和安全项无损归一。
- `ProgramItem`、`ProgramOutput`、子调用及 caller/call 关系无损归一。
- call ID、item 顺序、Provider Run ID 与停止原因保留。
- 未知事件可观测，不能静默吞掉。
- Provider 专属续传项能完成多轮回放。
- Run 查询能把“未执行、已幂等提交、已非幂等提交、未知”映射为规范副作用证据。

### 流式测试

- 随机切分文本和工具 JSON 增量，最终结果一致。
- 两个工具调用交错到达，缓冲区不串线。
- PTC 程序事件与子工具事件交错到达，`caller_id` / `call_id` 不串线。
- 尾事件缺失、空闲超时和用户取消能正确收尾。
- 慢消费者下内存有界，取消能穿透连接。

### 路由测试

- 必需能力缺失的模型不会入选。
- 语义声明不读取模型能力，最终 Prompt 只在 Route 确定后组装。
- 最终工具集始终是 Policy 授权集的子集。
- 数据区域和预算约束优先于质量评分。
- 健康状态变化时路由可解释、可复现。
- 每个 caller 使用预期的默认 Profile。

### 故障注入

| 故障 | 期望 |
| --- | --- |
| 短期限流 429 + Retry-After | 按服务端建议退避，计入预算 |
| 长期配额耗尽 429 | 不重试同一配额池；切换合法 profile 或停止 |
| 连续过载 | 熔断或切换兼容 fallback |
| 非法 Schema | 不重试，返回请求错误 |
| prompt too long | 触发一次压缩/裁剪恢复 |
| 流中断且已有文本 | 标记部分输出，不静默重放 |
| 流为空但 Provider Run 状态未知 | 不 fallback、不重放，先查询或对账 |
| 纯生成被截断且证明无副作用 | 预算允许时可提高上限后重放 |
| 非纯生成输出被截断 | 即使未收到事件也禁止自动完整重放 |
| 调用可能有副作用且状态未知 | 停止自动重试，查询状态或人工介入 |

### 验收指标

```text
任务成功率与结构化输出通过率
Provider/模型/区域错误率
P50/P95 首 Token与总延迟
重试率、fallback 率、熔断时长
输入/输出/缓存 Token
单任务总成本与 caller 分布
取消传播时延
协议解析错误与未知事件数
```

只有“请求能成功返回”远远不够。验收必须同时覆盖语义兼容、故障行为和成本可解释性。

## 5.20 系统地图

```text
Agent Loop
  -> Policy
     授权工具 / 数据边界 / 风险上界
  -> 阶段一：TaskSemanticRequirements
     caller / 必需能力 / 输出契约 / effect_class / 相关工具子集
  -> Router + Model Registry
     硬约束过滤 -> 质量/延迟/成本/健康排序 -> fallback 计划
  -> 阶段二：Prompt Runtime
     按各 Route 的确定能力生成 PreparedModelRequest
  -> Model Runtime
     调用生命周期 / 超时 / 取消 / 恢复决策 / 用量与 Trace
  -> Provider Adapter
     编码消息、PTC 与模型参数 -> 归一事件/错误 -> 查询 Provider Run
  -> Recovery Policy + Effect Evidence
     重试 / 熔断 / fallback / 幂等 / 对账
  -> Event Stream
     ProgramItem / ProgramOutput / caller-call + 其他统一事件
     -> UI + Agent Loop + Telemetry
  -> Usage & Trace
     质量 / 延迟 / Token / 缓存 / 成本 / 错误
```

## 5.21 共同结论

1. Model Runtime 是所有模型调用的统一生命周期边界，Agent Loop 不应感知 Provider 细节。
2. Adapter 负责 Provider 编解码、PTC、输出项/事件/错误归一和 Run 状态查询；它不决定业务恢复策略。
3. 调用准备先声明模型无关的语义需求并路由，再按已选模型能力组装 Prompt；Policy 授权集始终是工具可见性上界。
4. 路由先满足能力、安全与数据硬约束，再优化质量、延迟和成本。
5. 重试、输出截断重放和 fallback 都必须结合副作用证据与幂等性；`unknown` 一律禁止自动重放或切换。
6. 模型专属参数留在 Adapter，并通过代表任务评测校准。
7. 成本与可靠性必须按 caller、attempt 和完整任务链路观测。

## 5.22 本章自检

1. Prompt Runtime 与 Model Runtime 的职责边界是什么？
2. Router、Adapter 和 Registry 分别负责什么？
3. 为什么只统一文本响应不足以支持 Agent？
4. 能力矩阵中的 `native`、`emulated`、`unsupported` 有何区别？
5. 工具参数流为什么必须按 call ID 累积到完成后再解析？
6. 哪些错误适合重试，哪些错误不应重试？
7. Fallback 为什么是一场兼容性迁移？
8. 已有部分流式输出时，为什么不能静默重放整个请求？
9. `caller` 和 `attempt_id` 对成本分析有什么价值？
10. 模型专属推理与缓存参数为什么应由 Adapter 管理？
11. `ProgramItem`、`ProgramOutput`、`caller_id` 和 `call_id` 分别表达什么关系？
12. 为什么客户端没有收到事件不能证明服务端没有执行工具？
13. 输出截断后，完整重放原请求必须满足哪两个条件？
14. 如何区分短期限流 429 与长期配额耗尽 429？
15. Model Runtime 与 Adapter 在错误恢复中的职责怎样分工？

## 5.23 开放性问题

1. Router 的质量预测应来自离线基准、在线历史，还是针对当前请求的动态分类？
2. 当最便宜模型需要更多重试时，怎样估算任务级期望成本？
3. 不同 Provider 的 reasoning item 无法互转时，跨 Provider fallback 应保留多少历史？
4. 流式输出已展示给用户后，怎样设计可理解的恢复体验？
5. 模型别名自动升级与生产可复现性之间应如何取舍？
6. 哪些模型能力可以安全模拟，哪些能力缺失必须直接拒绝路由？
7. 如何为 fallback 组定义可执行的“质量下限”？
8. 当数据治理、低延迟和高质量三者冲突时，谁应拥有策略优先权？
9. Provider 不提供 Run 查询时，哪些任务可以接受 `unknown` 状态，哪些必须禁用服务端工具？
10. 跨 Provider fallback 时，如何证明幂等键覆盖了两个 Provider 的执行边界？

## 5.24 原文入口

### 本地来源

- [《AI Agents in Action（第二版）》第 2 章：核心组件](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/2.核心组件.md)
- [Hello-Agents Ch07：构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [learn-claude-code s11：Error Recovery](../../source/learn-claude-code/s11_error_recovery/README.md)
- [Alice 方法论：模型路由](../../source/Alice_methodology/chapters/11-llm-routing.md)
- [Hermes：模型抽象与 Provider 兼容层](../../source/hermes-book/src/part6/ch18-model-abstraction.md)
- [Hermes：配置与 Profiles](../../source/hermes-book/src/part6/ch17-config-profiles.md)
- [Harness Engineering：API 通信层](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06b.md)
- [Harness Engineering：模型特定调优与 A/B 测试](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch07.md)
- [Harness Engineering：Effort、Fast Mode 与 Thinking](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch21.md)
- [Claude Code 分析：API 重试实现](../../source/claude-code-analysis/src/services/api/withRetry.ts)
- [easy-langent：LangChain 核心组件实操](../../source/easy-langent/docs/guide/chapter2.md)

### 官方资料

- [OpenAI：GPT-5.6 Model Guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6)
- [OpenAI：Streaming API Responses](https://developers.openai.com/api/docs/guides/streaming-responses)
- [OpenAI：Model Selection](https://developers.openai.com/api/docs/guides/model-selection)
- [Anthropic：Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Google Gemini API：Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
