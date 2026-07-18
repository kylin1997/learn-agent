# 第 4 章：Prompt Engineering 与 Prompt Runtime

> 本章目标：把 Prompt 从“一段写得不错的提示词”升级为可分层、可组合、可测试、可迁移的运行时控制面。读完后，你应该能设计 Outcome-first 的 Agent Prompt，建立验证契约，识别 Prompt 债务，并实现一个按调用场景动态组装的 Prompt Runtime。

## 4.1 学习目标与边界

本章回答两个相连但不同的问题：

1. **Prompt Engineering：应该怎样描述目标、约束、工具策略和输出？**
2. **Prompt Runtime：这一次模型调用究竟应该看到哪些 Prompt section？**

你将学会：

- 把模糊要求改写为可观察的模型行为和成功标准。
- 用 Outcome-first、决策规则、停止规则和验证契约控制开放任务。
- 为主 Agent、压缩、记忆、评审和权限分类设计隔离的专项 Prompt。
- 处理静态/动态边界、优先级、缓存、工具描述和上下文注入。
- 识别并偿还 Prompt 债务。
- 用 GPT-5.6 迁移案例理解“通用原则”与“模型专属控制”的分层。

本章不负责决定调用哪个模型，也不实现 Provider 协议、重试和 fallback；这些属于第 5 章。Prompt 也不能替代 Schema、权限、沙箱或业务校验。

## 4.2 Prompt 是行为控制面，不是文案

普通聊天 Prompt 可能只要求“总结这篇文章”。Agent Prompt 还要持续影响模型：

- 怎样理解用户真正要完成的结果。
- 何时直接回答，何时调查，何时调用工具。
- 如何处理不确定性、失败和权限边界。
- 是否维护计划，何时更新计划。
- 什么证据足以宣布完成。
- 何时停止、求助或移交。
- 最终结果以何种结构交付。

因此，Prompt 是模型侧的**软控制面**。它通过条件上下文改变行为概率，却不能提供硬保证。

```text
Prompt：告诉模型应该如何判断和行动
Runtime：决定本次调用实际注入什么
Policy/Sandbox：强制执行不可突破的边界
Verifier：判断结果是否真的满足目标
```

把四者混在一起，会得到两种坏结果：要么 Prompt 越写越长，仍挡不住危险动作；要么代码硬编码所有路径，失去 Agent 适应环境的价值。

## 4.3 提示工程先做需求建模

写 Prompt 前先回答六个问题：

| 问题 | Prompt 中的表达 | 缺失后果 |
| --- | --- | --- |
| 谁在行动 | 角色、职责、服务对象 | 默认行为漂移 |
| 最终要什么 | 目标、交付物、成功标准 | 做偏、做多或提前结束 |
| 已知什么 | 输入、来源、可信度、上下文 | 基于错误前提推理 |
| 可以怎么做 | 工具、流程、决策规则 | 不用工具或滥用工具 |
| 不能怎么做 | 权限、安全、不变量、范围 | 越权、破坏或过度工程 |
| 如何证明 | 输出格式、证据、验收方式 | 自报完成但无法核验 |

“你是专业、谨慎、强大的 Agent”几乎不可测试。把形容词改成可观察行为：

| 抽象词 | 可观察行为 |
| --- | --- |
| 谨慎 | 修改前读取相关文件；修改后运行范围匹配的验证 |
| 专业 | 对关键结论给出来源、假设和限制 |
| 简洁 | 先给结论；保留证据、风险和下一步；删除重复背景 |
| 自主 | 对本地、可逆、范围内动作直接执行；缺少关键决策时询问 |
| 不过度设计 | 不做范围外重构；不为一次性逻辑新增公共抽象 |

Prompt Engineering 的起点不是修辞技巧，而是可执行需求。

## 4.4 Outcome-first：先定义终点

开放环境中的最佳路径会随代码库、工具结果和中间证据变化。把所有步骤写死，会让模型忽略新证据；什么都不约束，又会造成任务漂移。

Outcome-first 先定义：

1. 交付结果。
2. 成功证据。
3. 不能违反的不变量。
4. 需要授权的动作。
5. 停止条件。

例如，不要只写：

```text
先搜索三个文件，然后修改代码，最后运行测试。
```

改为：

```text
目标：修复用户报告的缺陷，并保持改动范围最小。
成功：复现用例由失败变为通过，相关回归测试没有新增失败。
约束：不修改无关模块，不删除或弱化失败测试。
权限：远端写入、发布、不可逆操作或范围扩大必须先确认。
停止：成功证据齐备后结束；关键输入无法获得时报告证据与阻塞点。
```

这不是反对流程。真正有顺序依赖的节点仍应固定，例如数据库迁移必须先备份再变更。区别在于：Prompt 固化不变量与目标，计划根据环境动态生成和更新。

## 4.5 三类规则：不变量、决策与停止

把所有要求都写成“必须”会制造冲突。更清楚的分类是：

### 不变量

用于安全、权限、数据完整性和协议要求。

```text
禁止输出真实密钥。
修改文件前必须读取当前版本。
不得把未验证结果表述为已验证。
```

不变量应尽量由代码侧兜底。Prompt 负责让模型提前做对，Runtime 负责在模型做错时阻止。

### 决策规则

用于存在条件和例外的选择。

```text
本地材料足以回答时优先使用本地材料。
涉及最新事实、外部页面或用户明确要求时使用搜索。
若多个只读查询互不依赖，可并行；存在数据依赖时串行。
```

决策规则应写“何时、为何、例外是什么”，避免空泛的“善用工具”。

### 停止规则

覆盖四类出口：

- 成功停止：交付物和证据齐备。
- 阻塞停止：关键输入缺失且限定调查无法补足。
- 风险停止：下一步越过授权或产生不可接受影响。
- 预算停止：达到时间、轮次、Token 或成本上限。

Prompt 告诉模型如何识别，Loop Runtime 负责计数、超时和强制停止。

## 4.6 验证契约：完成必须有证据

成功标准定义“什么算完成”，验证契约定义“用什么证据判定”。

| 任务 | 可接受证据 | 不能单独证明完成 |
| --- | --- | --- |
| 代码修复 | 复现用例、相关测试、构建或静态检查 | “代码看起来正确” |
| 信息研究 | 直接来源、日期、引用位置、交叉核对 | 搜索摘要或无出处转述 |
| 数据处理 | 行数、约束、抽样、可重复计算 | 脚本退出码为 0 |
| UI 实现 | 目标视口截图、交互测试、控制台检查 | 页面能够打开 |
| 外部操作 | 远端资源 ID、读取回执、幂等记录 | 模型说“已发送” |

可复用的验证契约：

```text
在宣布完成前：
1. 列出每个成功标准对应的证据。
2. 使用独立于生成过程的工具或状态读取进行核验。
3. 区分“已验证”“部分验证”“无法验证”。
4. 不得把缺少验证包装成确定结论。
5. 验证失败时，只修复与失败证据相关的问题，再次核验。
```

验证契约让“请检查一下”从模糊提醒变成可执行协议，也为 Trace 评测提供了检查点。

## 4.7 Prompt 的基本结构

一个可维护的主 Agent Prompt 可以按职责拆分：

```text
[Identity]
角色、职责、服务目标。

[Operating Principles]
先理解再行动、范围控制、证据优先、失败处理。

[Task Contract]
本轮目标、成功标准、输入与交付物。

[Tool Policy]
工具选择条件、调用关系、失败语义。

[Safety and Approval]
不变量、授权边界、需要确认的动作。

[Context Policy]
怎样使用项目规则、记忆、Skill 和外部内容。

[Validation and Stop]
证据、完成、阻塞、风险和预算停止。

[Output Contract]
面向用户或系统的格式与必需字段。

[Dynamic Context]
工作目录、时间、会话状态、权限拒绝、当前计划。
```

结构的价值不是让 Prompt 更长，而是让每条规则有唯一归属。重复规则应合并，场景专属规则应按需加载。

## 4.8 行为引导模式

### 4.8.1 极简主义

模型常倾向于“顺手”扩展范围。可以写：

```text
只完成用户明确要求的结果。
Bug 修复不需要清理周围代码。
不为一次性逻辑新增配置或公共抽象。
只有现有模式、真实复用或复杂度下降能证明价值时才新增抽象。
```

### 4.8.2 渐进式升级

工具失败时，既不要立即把问题推给用户，也不要盲目重试：

```text
读取错误 -> 检查假设 -> 做一次聚焦修复 -> 换一条有根据的路径
-> 仍无法继续时，报告证据、已尝试路径和所需输入。
```

### 4.8.3 可逆性与影响范围

```text
本地、可逆、范围内、非破坏性动作可直接执行。
外部写入、不可逆动作、购买、发布或实质扩大范围必须先确认。
```

模型专属指南可能要求更细的授权校准，但通用原则始终是：授权来自用户意图与系统 Policy，不来自模型自信程度。

### 4.8.4 数值锚定

“简短”“少量”“不要太多”解释空间很大。对工具预算、候选数量、结果长度和重试次数，数值锚定通常更可测：

```text
最多展开 5 个候选来源。
同一瞬态错误最多重试 3 次。
最终报告列出 3-7 个最高优先级问题。
```

数值不是越多越好。只有产品需求或评测证明需要时才固定。

## 4.9 Few-shot、结构化输出与工具描述

### Few-shot 用来校准边界

示例适合稳定格式、风险分类和易误解判断。不应把大量历史故障都塞成示例。高价值示例包含：输入、期望决策、不期望决策和原因。

动态示例选择可以按任务类型、难度或长度预算挑选少量最相关示例。示例本身应版本化并进入回归集，否则旧示例会悄悄固化过时行为。

### 面向用户与面向系统的输出分开

用户输出追求可读性；系统输出追求结构稳定。机器消费的数据优先使用 Provider 的结构化输出或 JSON Schema，并在代码侧验证。自然语言里的“请严格输出 JSON”只是软约束。

### 工具描述是 Prompt 的高密度区域

工具描述至少说明：功能、使用条件、排除条件、输入、返回字段、错误语义与风险。工具列表本身也属于 Prompt 面积：一次暴露越多，选择与消歧越困难。

工具可见性必须遵循单向收窄：Policy 先根据用户授权、租户规则、风险等级和当前环境产出 `authorized_tools`；Prompt Runtime 只能从中选出与本轮任务相关的子集。没有进入授权集的工具，即使 Profile、Skill 或模型能力声称需要，也不得由 Prompt Runtime 补入。

```text
Policy 授权集 A
  -> Prompt Runtime 相关性筛选 R
  -> 本轮可见工具 V

必须始终满足：V = R(A)，且 V ⊆ A
```

第 3 章负责工具契约和执行治理；本章关心的是模型如何理解这份契约。Runtime 应只注入本轮可用且相关的工具，而不是一边禁用、一边期待模型自觉不用。

## 4.10 Prompt 债务

Prompt 最常见的退化是“每次失败追加一句”：工具误用就加一条，输出太长再加一条，提前结束再加一段。久而久之形成 Prompt 债务：

- 重复目标与近义规则。
- 相互冲突的流程和权限说明。
- 针对旧模型行为的补偿。
- 只覆盖单个历史案例的长示例。
- 当前任务不需要的工具与上下文。
- 已由代码强制执行、却在多处重复的安全说明。

Prompt 债务的成本包括：注意力稀释、决策冲突、Token 与延迟、缓存失效，以及“没人敢删”的维护负担。

### 4.10.1 为每一段建立存在理由

每个 section 应能回答：

```text
它保护哪个可复现失败？
哪个评测能证明它有效？
它应常驻还是按需加载？
这条规则是否已由代码强制执行？
模型或产品变化后，它是否仍然必要？
```

回答不了，就是减法审计候选。

### 4.10.2 用单变量评测做减法

偿还债务的顺序：

1. 保存旧模型、旧 Prompt、旧工具集的基线与 Trace。
2. 模型迁移时先只换模型，观察默认行为变化。
3. 每次删除一组重复规则、示例或无关工具。
4. 对剩余真实失败添加最小修复。
5. 比较任务成功、约束遵守、轨迹、Token、延迟和成本。

删除不是文案偏好，而是一次有回归保护的行为变更。

## 4.11 为什么需要 Prompt Runtime

同一个 Agent 的每次调用可能处于不同状态：

- 工具和权限不同。
- 项目规则、Skill 和记忆不同。
- 主对话、压缩、评审或权限分类场景不同。
- CLI、Web、后台任务等渠道不同。
- Token 预算和模型能力不同。

因此，生产系统不应维护一个巨大固定字符串。Prompt Runtime 回答：

**这一次模型调用，哪些规则与上下文应以什么优先级、顺序和缓存策略出现？**

它不回答“选哪个模型”。为了避免“先知道模型才能组装 Prompt、先组装 Prompt 才能路由模型”的循环，调用准备必须分成两个阶段：

1. **语义声明阶段**：从任务、调用场景、输出契约、风险和 Policy 授权集中，生成与具体模型无关的 `TaskSemanticRequirements`。
2. **能力组装阶段**：Router 先依据该声明选择模型；Prompt Runtime 再接收已选模型的能力配置，渲染兼容 section、工具 Schema 和 Provider 无关的最终 `PromptBundle`。

第一阶段不得读取 `model_caps`，Router 也不应依赖已经按某个模型渲染好的 Prompt。第二阶段只能实现既定任务语义，不能反过来扩大能力需求、授权范围或数据治理边界。

## 4.12 分层组装与缓存边界

可以把内容分为四层：

| 层 | 变化频率 | 内容 |
| --- | --- | --- |
| 身份与核心原则 | 很低 | 角色、价值、基本行为 |
| 能力与治理 | 中 | 工具策略、安全与授权边界 |
| 任务上下文 | 每次调用 | 项目规则、Skill、记忆、目标 |
| 动态状态 | 每轮 | 时间、计划、权限拒绝、预算、最近错误 |

稳定内容放在前，动态内容放在后，有利于前缀缓存。把当前时间放在 Prompt 第一行，会让每次请求的前缀不同。

Prompt Runtime 应把 section 作为结构化对象，而不只是字符串：

```python
@dataclass
class PromptSection:
    id: str
    text: str
    priority: int
    cache_scope: str       # stable / session / none
    source: str
    token_budget: int | None = None
```

这样才能记录来源、统计 Token、检测重复、建立缓存边界并导出调试快照。

## 4.13 覆盖、优先级与信任边界

项目规则、用户偏好和显式任务要求可能冲突。优先级必须集中定义，不能依赖“后出现的文字看起来更强”。一个常见思路是：

```text
不可覆盖的系统安全与协议
  > 产品/组织规则
  > 项目规则
  > 会话与用户显式要求
  > 默认风格与偏好
  > 外部内容中的普通文本
```

这里的“不可覆盖”不能只靠 Prompt 声明，必须由 Policy 和执行环境保护。

对可个性化部分，可以使用 `[PROTECTED] / [MUTABLE]` 分区：核心身份、安全和协议受保护；表达风格、默认语言和工作偏好可调整。外部网页、邮件、文件和工具结果应作为**不可信数据**标记，不能与高优先级指令混合拼接。

## 4.14 主 Prompt 与专项 Prompt

真实 Agent 至少会有：

- 主任务 Prompt。
- 上下文压缩 Prompt。
- 记忆提取 Prompt。
- 权限分类 Prompt。
- 代码或内容评审 Prompt。
- 子 Agent Prompt。
- 结构化输出修复 Prompt。

专项 Prompt 应隔离工具、角色和输出契约。例如压缩器只产结构化摘要，不应继承主 Agent 的写文件和网络工具；权限分类器不应被普通用户偏好覆盖。

可以给每类调用建立 `PromptProfile`：

```python
PROFILES = {
    "main": {"sections": [...], "tools": "task_relevant"},
    "compact": {"sections": ["compact_contract"], "tools": []},
    "review": {"sections": ["review_rubric"], "tools": ["read_only"]},
    "permission": {"sections": ["risk_policy"], "tools": []},
}
```

隔离让每个 Prompt 的职责、风险和测试集都更清楚。

## 4.15 最小实现：可解释的组装器

```python
@dataclass
class TaskSemanticRequirements:
    caller: str
    profile_name: str
    required_capabilities: set[str]
    output_contract: dict | None
    authorized_tool_ids: frozenset[str]
    relevant_tool_ids: frozenset[str]
    quality_class: str
    latency_class: str
    risk_class: str


def declare_requirements(profile_name, context, registry, policy):
    """阶段一：只声明任务语义，不读取具体模型能力。"""
    authorized = policy.authorized_tools(context, registry.tools())
    relevant = relevant_tool_subset(context, authorized)
    assert tool_ids(relevant) <= tool_ids(authorized)

    return TaskSemanticRequirements(
        caller=context.caller,
        profile_name=profile_name,
        required_capabilities=infer_required_capabilities(context, relevant),
        output_contract=context.output_contract,
        authorized_tool_ids=frozenset(tool_ids(authorized)),
        relevant_tool_ids=frozenset(tool_ids(relevant)),
        quality_class=context.quality_class,
        latency_class=context.latency_class,
        risk_class=context.risk_class,
    )


def assemble_prompt(requirements, route, context, registry):
    """阶段二：路由完成后，按已选模型能力组装最终 Prompt。"""
    profile = registry.profile(requirements.profile_name)
    static_sections = []

    for section_id in profile.section_order:
        rendered = registry.render(section_id, context)
        if rendered.enabled(context, route.capabilities):
            static_sections.append(rendered)

    dynamic_sections = []
    if context.project_rules:
        dynamic_sections.append(make_section(
            "project_rules", context.project_rules, source="project"
        ))
    if context.relevant_memories:
        dynamic_sections.append(make_section(
            "memories", context.relevant_memories, source="memory"
        ))
    if context.active_skill:
        dynamic_sections.append(make_section(
            "skill", context.active_skill.instructions, source="skill"
        ))
    dynamic_sections.append(make_section(
        "runtime", render_runtime_state(context), source="runtime"
    ))

    tools = registry.resolve_tools(requirements.relevant_tool_ids)
    assert tool_ids(tools) <= requirements.authorized_tool_ids
    ensure_route_supports(requirements, route, tools)

    result = enforce_priority_and_budget(
        static_sections + dynamic_sections,
        context.token_budget,
    )
    return PromptBundle(
        system_blocks=split_cache_scopes(result),
        tools=tools,
        output_schema=requirements.output_contract,
        manifest=build_manifest(result),
    )


requirements = declare_requirements("main", context, registry, policy)
route = router.select(requirements)       # 先路由
bundle = assemble_prompt(requirements, route, context, registry)  # 后组装
```

`manifest` 应记录 section ID、版本、来源、Token、缓存范围和是否被裁剪。这里刻意使用 `rendered` 和 `make_section(...)` 两个不同名字：前者是已渲染对象，后者才是构造函数，避免把循环变量误当函数调用。出问题时，团队才能回答“这次模型到底看到了什么”。

还要对两个不变量做运行时断言：`relevant_tool_ids ⊆ authorized_tool_ids`，以及所选 Route 满足 `required_capabilities`。第一个防止 Prompt Runtime 扩权，第二个防止能力适配静默改变任务语义。

## 4.16 GPT-5.6 案例：通用原则与专属控制分层

OpenAI 的 GPT-5.6 官方模型指南提供了一个很有代表性的 Prompt 减法案例：在一组内部编码 Agent 评测中，更精简的系统 Prompt 使评测分数约提高 10%–15%，总 Token 减少 41%–66%，成本减少 33%–67%。官方同时强调这些范围只具有方向性，必须在自己的代表任务上验证，不能外推成普遍收益承诺。

这个案例支持的是通用方法：

- 从一个已经工作的 Prompt 和工具集建立基线。
- 每次只删一组重复指令、示例或工具。
- 每条规则只表达一次。
- 只暴露任务相关工具。
- 只有当示例编码产品要求或修复已测量缺口时才保留。

GPT-5.6 还提供 `text.verbosity`、`reasoning.effort`、`reasoning.context`、Pro mode、显式 Prompt Cache 和 Programmatic Tool Calling 等能力。这些不应被写成通用 Prompt 技巧：

| 控制 | 所属层 | 通用教材中的正确位置 |
| --- | --- | --- |
| 目标、约束、证据、成功标准 | Prompt | 跨模型保持稳定 |
| `text.verbosity` | Provider 请求参数 | 第 5 章 Adapter 配置 |
| `reasoning.effort` / Pro mode | 模型计算策略 | 路由与评测选择 |
| `reasoning.context` | Provider 多轮协议 | Adapter 保留/续传协议项 |
| 显式 Prompt Cache | Provider 缓存协议 | Runtime 输出缓存边界，Adapter 编码 |
| Programmatic Tool Calling | Provider 工具运行能力 | 能力声明；由 Provider Adapter 编码并保留程序—调用事件关系 |

Outcome-first 在这里仍成立：即使启用更高推理预算或 Pro mode，Prompt 仍应给出目标、相关上下文、约束、证据、成功标准和输出格式，而不是写“请更努力思考”。

迁移时，先保存旧配置基线，再只替换模型；`reasoning.effort` 等参数以当前配置为基线逐档比较。持久化推理只适合目标、假设和优先级仍稳定的多轮任务；当它们发生变化，应降低旧推理的影响。手动管理历史时，Provider 要求保留的响应项必须按协议原样续传，不能被普通摘要器随意改写。

这就是分层的价值：**通用 Prompt 表达产品意图，Model Runtime 表达某个模型怎样最合适地执行。**

## 4.17 生产约束

### Token 与缓存预算

给每类 section 和工具 Schema 设置预算。稳定前缀、动态后缀和外部上下文分别统计；缓存命中率不能只看“启用了缓存”，还要看动态内容是否破坏前缀。

### Prompt Injection

外部内容必须与指令分区，工具结果要标明来源和可信度。对高风险动作，模型即使声称外部内容可信，也必须经过独立权限与数据流检查。

### 版本与可观测性

分别记录语义需求快照、路由结果、Prompt profile、section 版本、模型、Policy 授权工具、最终可见工具和组装 manifest。支持导出最终请求的脱敏快照，并能按 section 查看 Token。这样才能判断偏差发生在需求声明、路由还是能力组装阶段。

### 多语言与协议

用户语言、项目规则语言和工具 Schema 语言可能不同。关键不变量应避免含糊翻译；机器输出依赖 Schema，不依赖自然语言字段猜测。

### 变更发布

Prompt 变更应像代码一样评审、灰度和回滚。模型升级、Prompt 改动、工具变更与评分标准不要同时上线，否则无法归因。

## 4.18 常见失败模式

**一条 Prompt 承担所有场景。** 压缩器、评审器和主 Agent 互相继承不该有的行为。

**只写抽象品质。** “谨慎、专业、高质量”没有行为锚点。

**用绝对流程代替 Outcome。** 环境变化后仍机械执行旧步骤。

**验证要求太弱。** “检查结果”退化成模型重读自己的答案。

**工具描述只有一句话。** 模型不知道使用条件、排除场景和错误语义。

**所有上下文常驻。** 无关 Skill、记忆、工具和历史稀释关键目标。

**动态信息放在前缀。** 时间、会话 ID 等让缓存持续失效。

**把安全只写在 Prompt。** 没有权限和沙箱兜底。

**Prompt 只加不删。** 历史补丁形成冲突与维护恐惧。

**把 Provider 参数写成通用指令。** 换模型后规则失效或产生反效果。

**组装 Prompt 后才推断路由需求。** 模型能力参与组装，组装结果又决定模型，形成不可解释的循环依赖。

**Prompt Runtime 自行补工具。** 相关性筛选越过 Policy 授权集，把“模型可能会用”误当成“系统允许使用”。

## 4.19 测试与验收

Prompt 测试至少覆盖：

| 类型 | 检查内容 | 示例指标 |
| --- | --- | --- |
| 组装单元测试 | section 条件、顺序、优先级、预算 | Prompt 快照与 manifest |
| 两阶段协议测试 | 语义声明不依赖模型；路由后才做能力组装 | 固定需求快照、Route/Bundle 契约 |
| 权限收窄测试 | 可见工具始终是授权集的子集 | 越权工具注入率为 0 |
| 行为测试 | 是否按目标、边界和停止规则行动 | 任务成功率、越界率 |
| 工具测试 | 是否选对工具与参数 | 工具选择/参数通过率 |
| 注入测试 | 是否把外部数据当指令 | 攻击成功率、危险调用率 |
| 输出测试 | Schema、字段和证据完整性 | 解析通过率、缺字段率 |
| 缓存测试 | 静态前缀是否稳定 | cached token、命中率 |
| 迁移测试 | 换模型后的行为变化 | 与旧基线的分层差异 |

一个 Prompt 变更的验收报告应同时包含：

```text
任务成功
约束遵守
验证证据完整性
工具轨迹
停止原因
输入/输出 Token
缓存读写
延迟与成本
主要失败分类
```

如果最终文本更漂亮但危险调用增加、证据减少或成本翻倍，就不能算整体改进。

## 4.20 系统地图

```text
Product Intent
  -> Prompt Engineering
     角色 / Outcome / 不变量 / 决策 / 验证 / 停止 / 输出
  -> Policy
     依据用户授权 / 租户规则 / 风险产出 authorized_tools
  -> 阶段一：TaskSemanticRequirements
     caller / 必需能力 / 输出契约 / 风险 / 相关工具子集
  -> Model Router + Registry
     选择 Route，返回确定的模型能力
  -> 阶段二：Prompt Runtime
     选择兼容 section -> 解冲突 -> 控预算 -> 划缓存边界
  -> PromptBundle + Manifest + Tool Schemas
  -> Model Runtime
     管理 Route 执行 / 超时 / 取消 / 恢复 / 用量与 Trace
  -> Provider Adapter
     按 Provider 能力编码参数和协议，归一响应
  -> Agent Loop / Tool Runtime / Verifier
  -> Trace + Evals
  -> 反馈到 Prompt 债务审计
```

## 4.21 共同结论

1. Prompt 是 Agent 的软控制面，目标是把不确定生成约束为可观察行为。
2. 好 Prompt 先定义 Outcome、证据和边界，再决定必要流程。
3. 调用准备遵循两阶段协议：先声明模型无关的任务语义并路由，再按已选模型能力组装 Prompt。
4. 主 Prompt 与专项 Prompt 必须隔离，工具描述也是行为控制的一部分。
5. Prompt 优化既做加法也做减法；每一段都应有失败案例和回归证据。
6. 模型专属参数由 Provider Adapter 管理，不能污染跨模型的产品意图。
7. Policy 决定工具授权上界；Prompt Runtime 只能做相关性收窄，不能扩大权限。

## 4.22 本章自检

1. Prompt Engineering 与 Prompt Runtime 分别回答什么问题？
2. 为什么“谨慎完成”不是可测试要求？
3. Outcome-first 的五个核心要素是什么？
4. 不变量、决策规则和停止规则应该怎样区分？
5. 验证契约与成功标准有什么差别？
6. Few-shot 示例什么时候值得占用上下文？
7. 工具描述为什么既属于工具契约又属于 Prompt？
8. Prompt 债务怎样形成，如何有证据地删除？
9. 稳定前缀与动态后缀为什么影响缓存？
10. GPT-5.6 的 `reasoning.effort` 为什么不应写进通用 Prompt？
11. 两阶段协议怎样消除 Prompt 组装与模型路由的循环依赖？
12. 为什么相关工具集必须是 Policy 授权集的子集？

## 4.23 开放性问题

1. 哪些规则应该永远常驻，哪些应按任务或失败动态加载？
2. 当用户要求与项目规则冲突时，Runtime 应如何解释并向用户呈现优先级？
3. 一个 Prompt 在多数任务上提升、少数高风险任务上退化时，应如何决策？
4. 如何自动发现两条语义重复或潜在冲突的 Prompt 规则？
5. Prompt section 的 Token 预算应按固定上限、任务风险还是模型上下文动态分配？
6. Provider 提供持久化推理后，哪些状态仍必须由应用显式维护？
7. 如何证明删除一个旧模型补丁没有把低频故障重新带回生产？
8. 当工具描述既要精确又要精简时，应怎样确定最小充分信息？

## 4.24 原文入口

### 本地来源

- [learn-claude-code s10：System Prompt](../../source/learn-claude-code/s10_system_prompt/README.md)
- [Hello-Agents Ch03：大语言模型基础](../../source/hello-agents/docs/chapter3/第三章%20大语言模型基础.md)
- [Hello-Agents Ch04：智能体经典范式构建](../../source/hello-agents/docs/chapter4/第四章%20智能体经典范式构建.md)
- [Hello-Agents Ch07：构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [Alice 方法论：提示词工程](../../source/Alice_methodology/chapters/14-prompts.md)
- [Hermes：提示词系统](../../source/hermes-book/src/part2/ch05-prompt-system.md)
- [Harness Engineering：系统提示词架构](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch05.md)
- [Harness Engineering：通过提示词引导行为](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06.md)
- [Harness Engineering：工具提示词作为微型驾驭器](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch08.md)
- [Claude Code 分析：Prompt 管理机制](../../source/claude-code-analysis/analysis/04g-prompt-management.md)
- [easy-langent：LangChain 核心组件实操](../../source/easy-langent/docs/guide/chapter2.md)

### 官方资料

- [OpenAI：Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [OpenAI：GPT-5.6 Model Guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6)
- [Anthropic：Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Anthropic：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

### 辅助阅读

- [Datawhale：OpenAI Prompt 指南中文解读](https://mp.weixin.qq.com/s/lSvGH3nCK9oWf8wOyeCTGA)
