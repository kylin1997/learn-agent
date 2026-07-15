# 第 4 章：模型路由、Provider 抽象与调用可靠性

> 本章目标：把“模型调用”从一次 API 请求升级为可替换、可降级、可观测的模型调用层。读完本章，你应该能解释为什么 Prompt Runtime 和模型路由要分开，并能设计一个统一 Provider 接口。

## 4.1 为什么模型调用层不能写死

最初的 LLM 应用通常这样写：

```python
client.chat.completions.create(
    model="gpt-4",
    messages=messages,
)
```

这对 demo 足够。但 Agent 产品会很快遇到问题：

- 用户想换模型。
- 不同 Provider 的 API 格式不同。
- 有些模型支持原生工具调用，有些不支持。
- 有些模型有 reasoning 字段，有些没有。
- 某个服务商限流或过载，需要 fallback。
- 不同任务应该用不同模型。
- 需要记录 token、耗时、成本、调用来源。

如果 Agent Loop 直接调用某个厂商 API，核心循环会被 Provider 细节污染。每支持一个新模型，就要修改循环代码。

所以需要模型路由层。

## 4.2 模型路由层的职责

模型路由层回答的问题是：

**这一次请求应该发给哪个模型，以及如何稳定拿到结果？**

它不负责决定 prompt 里有什么。那是 Prompt Runtime 的职责。

一个模型路由层至少包含：

- Provider 抽象。
- 模型配置。
- API 适配。
- 工具调用格式适配。
- 流式事件统一。
- 错误分类。
- 重试与退避。
- fallback 模型切换。
- token 和成本记录。
- 代理和网络配置。

对 Agent Loop 来说，最好只看到一个统一接口：

```python
async for chunk in llm.stream(messages, tools, model_id):
    handle_chunk(chunk)
```

底层是 OpenAI、Anthropic、Gemini、本地模型，主循环都不应该关心。

## 4.3 统一事件接口

不同 Provider 的返回格式差异很大。路由层应该把它们归一成统一事件：

```text
text               普通文本 token
reasoning          思考内容或 reasoning token
tool_call_delta    工具调用参数片段
tool_call          完整工具调用
usage              token 用量
done               流结束
error              错误事件
```

Agent Loop 只消费统一事件。这样底层 Provider 可以自由替换。

Alice 的模型路由章节采用类似思路：对外暴露统一 `llm.stream(messages, tools, modelId)`，对内按 Provider 类型分发到 OpenAI 兼容、Anthropic 原生、Gemini 等适配器。

## 4.4 Provider 配置应该包含什么

每个 Provider 至少需要声明：

```yaml
id: deepseek
name: DeepSeek
api_type: openai_compatible
base_url: https://api.deepseek.com/v1
supports_tools: true
max_context_tokens: 128000
is_overseas: false
```

常见字段包括：

- `id`：内部唯一标识。
- `name`：展示名称。
- `api_type`：API 类型，例如 openai compatible、anthropic、gemini。
- `base_url`：服务端点。
- `supports_tools`：是否支持原生工具调用。
- `supports_streaming`：是否支持流式返回。
- `supports_reasoning`：是否有 reasoning 内容。
- `max_context_tokens`：上下文窗口。
- `default_max_output_tokens`：默认输出预算。
- `is_overseas`：是否需要代理。
- `cost_profile`：输入输出 token 单价。

这些字段不是装饰，它们会影响运行时决策。

例如上下文窗口决定是否需要更早压缩；是否支持工具决定是否需要 XML 工具调用模拟；单价决定哪些后台任务应该用便宜模型。

## 4.5 工具调用格式适配

不同模型的工具调用格式并不一致。

OpenAI 兼容 API 通常使用 function calling。Anthropic 使用 `tool_use` 块。Gemini 有自己的 function call 格式。部分本地模型没有原生工具调用能力。

路由层需要把这些格式统一为内部结构：

```python
ToolCall(
    id="...",
    name="read_file",
    arguments={"path": "README.md"},
)
```

如果模型不支持原生工具调用，可以用文本协议模拟，例如 XML：

```xml
<tool_call>
  <name>read_file</name>
  <input>{"path": "README.md"}</input>
</tool_call>
```

这是一种降级方案。它质量不如原生工具调用，因为模型必须主动遵守格式，解析也更脆。但它能让不支持工具调用的模型继续参与 Agent Loop。

这体现了一个重要工程原则：**功能质量可以降级，系统不要轻易崩溃。**

## 4.6 不同任务应该用不同模型

Agent 产品里并不是所有 LLM 调用都一样重要。

| 场景 | 需求 | 推荐策略 |
| --- | --- | --- |
| 主对话 | 质量最高、推理最强 | 使用最好的可用模型 |
| 代码修改 | 代码能力、上下文长度 | 使用代码能力强的模型 |
| 记忆提取 | 便宜、稳定、结构化 | 使用低价模型 |
| 权限分类 | 快、保守 | 使用低延迟模型或规则优先 |
| 上下文压缩 | 长上下文、摘要稳定 | 使用擅长摘要的模型 |
| 标题生成 | 快、便宜 | 使用小模型 |
| 图像/多模态 | 专门能力 | 使用多模态模型 |

如果所有任务都用最强模型，成本会高；如果所有任务都用便宜模型，主体验会差。模型路由层的价值，就是让不同场景有不同默认模型。

Hermes 的 smart model routing、Alice 的多场景模型配置、Claude Code 的 fast mode / effort / thinking 机制，都在解决类似问题。

## 4.7 错误分类与恢复

生产环境里，模型 API 失败是常态，不是异常。

常见错误包括：

- 429：限流。
- 529 或 overloaded：服务过载。
- prompt too long：上下文超限。
- max tokens：输出被截断。
- timeout：网络或服务超时。
- auth error：密钥失效或额度不足。
- invalid tool schema：工具定义不合法。
- malformed tool call：模型返回的工具调用结构错误。

不要把所有错误都当成一种 exception。不同错误需要不同恢复策略：

```text
429 / 529
  -> 指数退避 + 抖动 + 可选 fallback

prompt too long
  -> reactive compact + 重试

max tokens
  -> 提高输出 token 或注入续写提示

auth error
  -> 切换 key / profile，或提示用户配置

malformed tool call
  -> 请求模型修复格式，或返回 tool error
```

`learn-claude-code` s11 讲得很清楚：错误不是终点，是重试的起点。但重试不能盲目，必须先分类。

## 4.8 Fallback 不是简单换模型

Fallback 听起来简单：主模型挂了就换备用模型。但真实系统要考虑：

- 备用模型是否支持同样的工具调用格式？
- 备用模型上下文窗口是否足够？
- 备用模型是否支持当前 reasoning/thinking 参数？
- 当前 messages 是否包含只有某个 Provider 支持的字段？
- 切换后是否要重组 prompt？
- 成本和质量是否仍然可接受？

所以 fallback 应该基于模型能力，而不是只基于模型名称。

可以给每个模型维护能力声明：

```yaml
capabilities:
  tools: native
  streaming: true
  reasoning: false
  vision: false
  context_tokens: 128000
```

路由时按能力选择，而不是硬编码。

## 4.9 调用日志与成本观测

每次 LLM 调用都应该记录：

```text
caller       谁发起的：main_chat / compact / memory / permission / subagent
model_id     使用哪个模型
provider     哪个服务商
session_id   哪个会话
prompt_tokens
completion_tokens
duration_ms
retry_count
fallback_used
error_type
cost_estimate
```

`caller` 尤其重要。很多 Agent 成本问题不是主对话造成的，而是后台记忆提取、压缩、权限分类、子 Agent 并发造成的。没有 caller 字段，你只能看到“token 用很多”，却不知道花在哪里。

这就是为什么模型路由层天然和可观测性绑定。它是所有 LLM 调用经过的入口，最适合记录成本、延迟和失败率。

## 4.10 模型路由的常见错误

**错误一：核心循环直接调用某个 Provider SDK。**  
这会让后续扩展很痛苦。

**错误二：只抽象文本输出，不抽象工具调用。**  
Agent 的核心是 tool use。工具调用格式必须统一。

**错误三：所有任务用同一个模型。**  
成本和体验都会受影响。

**错误四：错误只做简单 retry。**  
prompt too long 和 429 不是同一种错误，不能同样处理。

**错误五：fallback 不检查能力。**  
备用模型不支持工具调用时，Agent Loop 会直接坏掉。

**错误六：没有调用日志。**  
后续无法优化成本，也无法定位故障。

## 4.11 最小实现建议

第一版模型路由可以很简单：

1. 定义 `ProviderConfig`。
2. 定义统一 `StreamChunk`。
3. 实现一个 OpenAI 兼容适配器。
4. 实现一个 Anthropic 适配器。
5. 把两者输出统一成 `text / tool_call / usage / done`。
6. 加上 429/529 指数退避。
7. 记录每次调用的 `caller/model/duration/tokens`。
8. 最后再加 fallback。

不要一开始就支持所有模型。先保证接口边界正确。

## Hello-Agents 融合补充

`hello-agents` 第七章的 `HelloAgentsLLM` 设计为本章提供了一个轻量模型抽象样例：它支持多 provider、本地模型调用和自动检测机制，让应用层可以用统一接口发起模型调用，而不用把 OpenAI、ModelScope、Ollama、本地 vLLM 等差异散落在 Agent Loop 里。这个实现和本章的 Provider 抽象是一致的：模型调用边界越早收口，后续 fallback、日志、成本统计和能力检查越容易做。

第十一章 Agentic-RL 则提醒我们：模型路由之外还有一条“提升模型能力”的路线。SFT、LoRA、GRPO、奖励函数和评估不属于在线路由本身，但会影响路由策略：当某个垂直任务有足够数据和奖励信号时，训练小模型或专用模型可能比每次调用强通用模型更经济。

## 本章自检

1. Prompt Runtime 和模型路由分别回答什么问题？
2. 为什么 Agent Loop 不应该直接调用 Provider SDK？
3. Provider 配置至少需要哪些字段？
4. 为什么工具调用格式也要被抽象？
5. XML 工具调用模拟的优缺点是什么？
6. 为什么不同任务应该使用不同模型？
7. 429、prompt too long、max tokens 分别应该如何恢复？
8. Fallback 为什么要检查模型能力？
9. LLM 调用日志里为什么要记录 caller？
10. 你的第一个模型路由层应该支持哪些最小能力？

## 开放性问题

1. 一个任务应该优先选择便宜模型还是强模型？你会如何把风险、成本和延迟放进同一个决策框架？
2. Fallback 模型和主模型输出风格不同，会不会破坏用户体验？系统应该如何缓冲这种差异？
3. 模型路由策略应该由用户配置、系统自动判断，还是二者结合？边界在哪里？

## 原文入口

- [Alice 方法论: 模型路由](../../source/Alice_methodology/chapters/11-llm-routing.md)
- [Hello-Agents Ch07: HelloAgentsLLM 多 Provider 抽象](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [Hello-Agents Ch11: Agentic-RL](../../source/hello-agents/docs/chapter11/第十一章%20Agentic-RL.md)
- [learn-claude-code s11: Error Recovery](../../source/learn-claude-code/s11_error_recovery/README.md)
- [Hermes: 模型抽象与 Provider 兼容层](../../source/hermes-book/src/part6/ch18-model-abstraction.md)
- [Hermes: 配置与 Profiles](../../source/hermes-book/src/part6/ch17-config-profiles.md)
- [Harness Engineering: API 通信层](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06b.md)
- [Harness Engineering: 模型特定调优与 A/B 测试](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch07.md)
- [Harness Engineering: Effort、Fast Mode 与 Thinking](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch21.md)
- [hello-claw: 模型管理](../../source/hello-claw/docs/cn/adopt/chapter5/index.md)
- [hello-claw: 模型提供商选型指南](../../source/hello-claw/docs/cn/appendix/appendix-e.md)
