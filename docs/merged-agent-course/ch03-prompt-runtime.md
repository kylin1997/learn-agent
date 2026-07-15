# 第 3 章：Prompt Runtime 与提示工程

> 本章目标：把 prompt 从“写一段提示词”升级为“可设计、可组合、可测试、可演进的控制系统”。读完本章，你应该能从提示工程视角设计 Agent 的角色、任务、约束、示例、工具说明、输出格式和专项 prompt，并理解这些内容为什么最终要落到 Prompt Runtime 里动态组装。

## 3.1 Prompt 在 Agent 里到底控制什么

在普通聊天场景里，prompt 往往像一段请求：“请帮我总结这篇文章”。但在 Agent 里，prompt 的地位完全不同。

Agent 不是只生成一段文本，它会：

- 判断用户真正要完成什么。
- 拆解任务步骤。
- 选择是否调用工具。
- 决定调用哪个工具。
- 解释工具结果。
- 判断是否继续循环。
- 在失败时选择重试、换路、压缩、求助或停止。
- 遵守权限、安全、输出格式和项目约定。

所以 Agent prompt 不是文案，而是 **行为控制面**。它不是让模型“知道一些背景”，而是在持续影响模型每一步的决策概率。

这也是为什么 Claude Code、Alice、Hermes、Harness Engineering 这些教程都没有把 system prompt 当成一个固定字符串处理。它们共同指向一个结论：

**Agent 的 prompt 工程，本质是把模型的不确定生成，约束成可预期的工程行为。**

这句话里有三个关键词：

- “不确定生成”：模型不是执行确定性程序，而是在概率空间里生成下一步。
- “约束”：prompt 不是保证，但能提高正确行为概率，降低错误行为概率。
- “工程行为”：目标不是写出漂亮提示词，而是让 Agent 稳定完成任务。

## 3.2 提示工程不是玄学，而是需求建模

很多人学习提示工程时，会背一些技巧：给角色、给步骤、给例子、要求 JSON、让模型思考。技巧有用，但如果只记技巧，很容易写出看似完整、实际脆弱的 prompt。

更好的入口是把提示工程看成需求建模。每个 prompt 都应该回答六个问题：

| 问题 | 对应 prompt 内容 | 失误后果 |
| --- | --- | --- |
| 你是谁 | 角色、职责、价值观 | 模型不知道该以什么身份行动 |
| 要做什么 | 任务目标、成功标准 | 模型可能做偏、做多或做少 |
| 有什么输入 | 用户请求、上下文、文件、记忆 | 模型可能基于错误信息推理 |
| 可以怎么做 | 工具、流程、策略 | 模型可能不用工具或乱用工具 |
| 不能怎么做 | 安全边界、权限、反模式 | 模型可能越权、破坏数据或过度工程 |
| 输出什么 | 格式、粒度、语气、验收标准 | 模型输出不可消费或不可测试 |

比如一句“你是一个代码助手，请帮用户修改代码”几乎没有工程价值。它缺少任务边界、失败策略、工具策略、权限边界、输出约定。

更像 Agent 的 prompt 会写成：

```text
你是一个本地编码 Agent。你的目标是完成用户明确提出的代码任务。

工作方式：
- 先理解现有代码，再修改。
- 修改前读取相关文件。
- 对多步任务维护简短计划。
- 修改后运行与改动范围匹配的验证。

范围控制：
- 不做用户没有要求的重构。
- 不引入新的框架或依赖，除非现有项目已经使用或用户明确要求。
- 不执行难以撤销或影响远端系统的操作，除非用户明确授权。

输出：
- 完成后说明改了什么、如何验证、还有什么风险。
```

这段仍然不复杂，但已经把“角色、流程、边界、输出”都说清楚了。提示工程的第一层能力，就是把模糊意图变成可执行规范。

## 3.3 从提示词技巧到 Agent 提示词结构

提示工程常见技巧可以归纳为八类。它们在 Agent 里不是孤立技巧，而是会分别落到不同 prompt section 或专项 prompt 中。

| 技巧 | 在 Agent 中的用途 | 应落入哪里 |
| --- | --- | --- |
| 明确角色 | 定义职责、工作风格、边界 | identity section |
| 明确目标 | 避免做偏、做过头 | task / session section |
| 拆解步骤 | 引导多步任务执行 | workflow section / Skill |
| 给约束 | 控制风险和范围 | policy / permission section |
| 给例子 | 稳定输出格式和判断标准 | examples section |
| 指定输出格式 | 让结果可解析、可复用 | output schema /专项 prompt |
| 让模型使用工具 | 建立工具选择条件 | tools section / tool description |
| 评测迭代 | 让 prompt 可改进 | eval cases / regression set |

例如 OpenAI 官方提示工程材料强调清晰指令、复杂任务拆分、结构化输出和系统化测试；Anthropic 官方文档也强调在 prompt engineering 之前先定义成功标准和可经验测试方式。把这些放进 Agent 语境，结论就更明确：

**不要先写 prompt，先写成功标准。**

比如“让 Agent 更聪明”不是成功标准；“当用户要求修改一个函数时，Agent 必须先读取目标文件，修改后运行相关测试，并在失败后诊断原因”才是成功标准。

## 3.4 好 prompt 的基本骨架

一个可维护的 Agent 主 prompt 可以按下面的骨架设计：

```text
[Identity]
你是谁，你服务什么目标，你默认怎样行动。

[Operating Principles]
做事原则：先理解再修改、保持范围、验证结果、遇到失败先诊断。

[Task Handling]
如何处理简单任务、多步任务、不确定任务、长任务。

[Tool Policy]
什么时候用工具，什么时候不用；工具之间的优先级；工具失败怎么办。

[Safety and Permission]
哪些行为必须确认，哪些行为禁止，哪些可以自由执行。

[Context Policy]
如何使用项目规则、会话摘要、记忆、Skill、外部资料。

[Output Policy]
对用户如何汇报，什么情况下简短，什么情况下详细，格式如何稳定。

[Dynamic Context]
当前时间、工作目录、项目状态、权限拒绝、最近计划等运行时信息。
```

这个骨架不是越长越好。它的价值在于把不同问题分到不同位置，避免一个段落承担所有职责。

最常见的失败 prompt 是这样的：

```text
你是一个强大的 Agent。你可以使用工具。请一步一步思考，谨慎完成任务，
不要犯错，输出要清晰。
```

这类 prompt 看似合理，实际几乎不可测试。什么叫强大？什么叫谨慎？什么时候使用工具？什么叫不要犯错？输出清晰到什么程度？

工程化 prompt 要尽量把抽象形容词替换成可观察行为：

| 抽象写法 | 工程化写法 |
| --- | --- |
| 谨慎修改 | 修改前读取相关文件，修改后运行与改动范围匹配的验证 |
| 不要过度设计 | 不为一次性逻辑抽象公共模块；三处以内相似代码优先保持直写 |
| 善用工具 | 需要最新信息、外部事实或用户明确要求时使用搜索；本地文件足够时不联网 |
| 输出清晰 | 最终回复包含改动摘要、验证结果、未完成事项 |
| 不要问太多 | 只有缺少关键输入且合理假设风险较高时才询问用户 |

这就是 Harness Engineering 里“行为引导模式”的核心：prompt 写得越具体，模型越容易把它落实到行为。

## 3.5 行为引导：用 prompt 改变模型的默认倾向

模型有一些默认倾向。比如它会倾向于多做一点、解释多一点、看到失败就换方案或重复重试、看到万能工具就滥用万能工具。

Agent prompt 的任务之一，是把这些默认倾向调到适合产品的范围。

### 极简主义指令

编码 Agent 很容易过度工程：顺手重构、加配置、加抽象、改命名、补注释。极简主义指令不是让 Agent 偷懒，而是让它把精力集中在用户要求的任务上。

可复用写法：

```text
不要在任务范围之外添加功能、重构或“顺手改进”。
Bug 修复不需要清理周围代码。
简单功能不需要额外配置项。
一次性逻辑不需要抽象 helper。
三处以内相似代码优先保持直写，除非现有代码已有明确抽象模式。
```

这里关键不是“不许抽象”，而是给出判断锚点。没有锚点时，模型会回到训练数据里常见的“抽象更专业”的模式。

### 渐进式升级

工具失败时，模型常见两种极端：立刻问用户，或者盲目重试。渐进式升级把失败处理写成协议：

```text
当一种做法失败时：
1. 先读取错误信息，确认失败原因。
2. 检查你的假设是否错误。
3. 尝试一个聚焦修复。
4. 不要盲目重复完全相同的操作。
5. 只有调查后仍无法继续时，才向用户说明卡点并请求输入。
```

这个模式能显著提升 Agent 的自主性，因为它把“失败”变成下一步推理输入，而不是任务终点。

### 可逆性与影响范围

Agent 可以自由做本地、可逆、小范围的事，比如读取文件、编辑工作区文件、运行测试。但对于难以撤销或影响他人的动作，prompt 必须建立确认框架：

```text
执行操作前评估两个维度：
- 可逆性：是否容易撤销？
- 影响范围：是否影响本地之外的人、系统或数据？

本地、可逆、小范围操作可以直接执行。
难以撤销、影响远端或对他人可见的操作必须先确认。
```

这个原则后面会在权限、安全和沙箱章节继续展开。这里先记住一点：prompt 可以提醒模型判断风险，但最终安全不能只靠 prompt，必须由权限系统兜底。

## 3.6 示例驱动：few-shot 不是越多越好

示例是提示工程里非常有用的手段，但在 Agent 里要谨慎。示例会占 token，也会强烈影响模型行为。如果示例覆盖面不对，模型会把局部模式误当成通用规则。

什么时候适合给示例？

- 输出格式必须稳定，例如 JSON、表格、审查报告。
- 判断标准容易误解，例如风险分级、权限分类。
- 工具调用格式复杂，例如多参数工具。
- 任务风格需要校准，例如“简洁但不遗漏”。

什么时候不适合给很多示例？

- 任务开放度很高，示例会限制探索。
- 示例彼此矛盾。
- 示例只是装饰，没有明确可复用结构。
- 示例很长，挤占真正上下文。

一个好的示例通常由三部分组成：

```text
输入：
用户说：“帮我修一下登录错误。”

期望行为：
- 先询问或检查错误复现信息。
- 读取相关登录代码。
- 修改最小范围。
- 运行相关测试。

不期望行为：
- 直接重写整个登录模块。
- 未读取代码就猜测原因。
- 修改鉴权策略但不说明风险。
```

这类示例不是给模型看“漂亮答案”，而是校准决策边界。

## 3.7 输出格式：自然语言、Markdown 与结构化输出

Agent 有两类输出：

- 给用户看的输出。
- 给系统消费的输出。

这两类输出应该分开设计。给用户看的输出可以自然、简洁、有解释；给系统消费的输出应该结构稳定、字段明确、容易解析。

例如上下文压缩 prompt，就不应该让模型“总结一下历史”。更好的方式是要求固定章节：

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

这 9 节格式来自 Alice 和 learn-claude-code 的共同实践。它的价值是把摘要从自由写作变成结构化状态转移，减少遗漏，便于后续恢复。

如果输出要被程序读取，应优先使用 JSON schema 或严格字段格式。比如记忆提取可以要求：

```json
[
  {
    "name": "project-api-layout",
    "type": "project",
    "description": "API routes live under services/api",
    "body": "This project keeps API route handlers under services/api. Prefer checking this directory first when API behavior is involved."
  }
]
```

但要注意：只在真正需要机器读取时才要求 JSON。用户最终回复没必要强行 JSON 化，否则可读性会变差。

## 3.8 工具描述也是提示工程

工具的 `description` 是 prompt 密度最高的地方之一。很多 Agent 误用工具，不是模型“笨”，而是工具描述太薄。

一个工具描述至少要回答：

1. 工具是什么。
2. 什么时候应该用。
3. 什么时候不应该用。
4. 输入是什么。
5. 输出是什么。
6. 有哪些风险、前置条件或替代工具。

比如搜索工具不应该只写：

```text
Search the web.
```

更好的写法：

```text
通过搜索引擎获取外部和最新信息。

适用：
- 用户明确要求搜索、查找、核实。
- 问题涉及新闻、价格、政策、版本、产品规格等可能变化的信息。
- 需要多个来源交叉验证。

不适用：
- 本地文件已经提供足够信息。
- 问题是纯代码库内部问题。

返回：
- 标题、链接、摘要、来源。
```

Harness Engineering 把这种设计称为“工具提示词作为微型驾驭器”。系统 prompt 负责全局原则，工具 prompt 负责局部行为。

对于万能工具尤其要加偏好矩阵。比如 shell 工具很强，但它不应该替代专用文件读取、搜索、编辑工具：

```text
文件搜索优先使用专用搜索工具。
读取文件优先使用文件读取工具。
编辑文件优先使用文件编辑工具。
只有专用工具无法完成，或用户明确要求命令行方式时，才使用 shell。
```

这能把模型的工具流量导向更安全、更结构化、更可审计的工具。

## 3.9 主 prompt 与专项 prompt

真实 Agent 里不只有一个 prompt。

至少会有这些专项 prompt：

- 主对话 prompt：负责理解任务、调用工具、和用户协作。
- 上下文压缩 prompt：负责把历史变成结构化状态。
- 记忆提取 prompt：负责判断什么值得长期保存。
- 权限分类 prompt：负责判断操作风险。
- 代码审查 prompt：负责发现缺陷和测试缺口。
- 子 Agent prompt：负责局部研究、实现或验证。
- 输出修复 prompt：负责把模型输出修成可解析格式。

专项 prompt 必须和主 prompt 隔离。压缩 prompt 不应该继承普通工具权限；记忆提取 prompt 不应该把自己生成的内容立刻写回对话；权限分类 prompt 不应该被用户偏好覆盖。

一个成熟 Agent 的 Prompt Runtime，实际上是在为不同调用场景选择不同 prompt。

```text
User Turn
  -> Main Agent Prompt
      -> Tool Call
      -> Context Compact Prompt
      -> Memory Extraction Prompt
      -> Permission Classification Prompt
      -> Subagent Prompt
```

如果所有场景共用同一个 system prompt，系统会混乱：压缩任务可能尝试调用工具，记忆提取可能受普通对话语气影响，子 Agent 可能拿到不该有的上下文。

## 3.10 为什么需要 Prompt Runtime

前面讲的是提示工程。现在回到 Runtime。

Agent 每次模型调用看到的内容都不是固定的。它会随着这些因素变化：

- 当前工具是否启用。
- 当前项目目录是什么。
- 是否存在项目规则。
- 是否加载了某个 Skill。
- 是否召回了相关记忆。
- 是否处于压缩、审查、权限分类等专项场景。
- 当前渠道是 CLI、Web、Slack 还是后台任务。
- 当前模型支持什么能力。
- 当前 token 预算是否紧张。

如果这些内容全部写进一段硬编码 prompt，系统会很快失控：

- 新增一个能力就要改整段 prompt。
- 静态内容和动态内容混在一起，缓存命中率变差。
- 工具描述、项目规则、记忆、Skill 相互污染。
- 难以测试某个 section 是否生效。
- 难以解释某次模型调用为什么看到这些内容。

所以生产级 Agent 需要的不是“一段好 prompt”，而是 **Prompt Runtime**。

Prompt Runtime 回答一个问题：

**这一次模型调用，应该让模型看到什么？**

注意，它不回答“调用哪个模型”。模型选择属于下一章的模型路由。

## 3.11 Prompt Runtime 的分层组装

Alice 方法论给出一个很好的分层模型：

```text
层 1：人格定义
  稳定，很少变化。
  定义 Agent 是谁、价值观、基本行为规范。

层 2：能力边界
  中等频率变化。
  定义工具说明、工具使用原则、安全边界。

层 3：上下文注入
  每次对话重新构建。
  包括项目记忆、用户画像、当前激活的 Skill。

层 4：动态追加
  每轮迭代更新。
  包括当前日期、权限拒绝摘要、渠道前缀等。
```

这个分层的核心价值是：不同层可以独立维护。

稳定层应该放在前面。它们可以充分利用 prompt cache，降低成本和延迟。动态层应该放在后面，避免每次变化都破坏前缀缓存。

典型反例是把当前时间放在 system prompt 开头：

```text
当前时间：2026-07-07 10:30
你是一个编码 Agent...
```

更好的做法是：

```text
你是一个编码 Agent...
长期稳定规则...

[Dynamic Context]
Current time: 2026-07-07 10:30
```

learn-claude-code 的 s10 用教学版说明了 section 化：

```python
PROMPT_SECTIONS = {
    "identity": "You are a coding agent. Act, don't explain.",
    "tools": "Available tools: bash, read_file, write_file.",
    "workspace": f"Working directory: {WORKDIR}",
    "memory": "Relevant memories are injected below when available.",
}
```

组装时按真实状态选择：

```python
def assemble_system_prompt(context):
    sections = []
    sections.append(PROMPT_SECTIONS["identity"])
    sections.append(PROMPT_SECTIONS["tools"])
    sections.append(PROMPT_SECTIONS["workspace"])

    if context.get("memories"):
        sections.append(f"Relevant memories:\n{context['memories']}")

    return "\n\n".join(sections)
```

重点不是代码，而是原则：

- section 是独立维护单元。
- 是否加载 section 由真实状态决定，而不是关键词猜测。
- 每个 section 可以单独测试。
- 每个 section 可以单独统计 token。
- 每个 section 可以有独立缓存策略。

## 3.12 上下文注入：不是知道越多越好

Agent 可以看到很多东西：项目文档、用户偏好、记忆、工具说明、MCP server instructions、当前文件树、git 状态、最近错误日志。

但 prompt 不是仓库垃圾桶。信息注入要遵循三个原则。

**第一，只注入当前任务有用的信息。**  
当前任务是修一个 Python 测试，就没有必要注入全部写作 Skill。

**第二，优先注入摘要和索引，按需展开全文。**  
Skill 列表可以常驻，但 Skill 正文应该激活后再加载。记忆索引可以常驻，但记忆全文应该按相关性召回。

**第三，动态信息放在靠后位置。**  
当前时间、权限拒绝、临时路径、最近工具错误都很易变，放前面会破坏缓存。

这也是 Skill 和 Memory 的共同设计逻辑：先让模型知道“有什么”，再让它在需要时加载“具体内容”。

## 3.13 Prompt 覆盖与优先级

成熟 Agent 通常允许用户和项目提供自己的规则。问题是：规则冲突时谁优先？

可以采用类似配置层级的优先级：

```text
内置默认规则
  < 全局用户规则
  < 项目规则
  < 会话规则
  < 显式传入的 system prompt
```

但这不意味着高优先级规则可以突破安全底线。安全规则应该放在更底层的 guard、权限系统、沙箱里，而不是只靠 prompt。

Alice 的 `[PROTECTED] / [MUTABLE]` 分区很值得借鉴：

```text
[PROTECTED]
核心身份、安全底线、不可变约束。
[/PROTECTED]

[MUTABLE]
表达风格、默认工作方式、用户可调整偏好。
[/MUTABLE]
```

这个分区让自进化或个性化有了明确边界：哪些可以改，哪些不能改。

## 3.14 Prompt 也需要测试

很多团队会给代码写测试，却不给 prompt 写测试。结果是 prompt 越改越玄学：今天加一句修了 A，明天 B 又坏了。

Agent prompt 至少应该有四类测试集：

| 测试类型 | 检查什么 | 示例 |
| --- | --- | --- |
| 行为测试 | 是否按预期流程行动 | 修改前是否读取文件 |
| 工具测试 | 是否选择正确工具 | 本地问题不联网，最新信息才搜索 |
| 边界测试 | 是否避免危险行为 | 不执行破坏性 git 命令 |
| 输出测试 | 是否符合格式和粒度 | 最终回复是否包含验证结果 |

最小测试方法可以很简单：保存一组固定任务，每次改 prompt 后跑一遍，观察行为差异。

例如：

```text
Case: 用户要求“修复这个测试失败”
期望：
- 读取失败日志或运行测试。
- 定位相关代码。
- 做最小修改。
- 再次运行测试。
- 最终说明验证结果。

不期望：
- 直接重写模块。
- 未验证就声称修复。
- 修改无关文件。
```

如果条件允许，可以进一步做自动化评测：让另一个模型或规则脚本检查 transcript 中是否出现了必要步骤。但学习阶段先养成“prompt 变更必须有回归案例”的习惯就很重要。

Anthropic 官方提示工程文档强调，在优化 prompt 前应该先有成功标准和经验测试方法。把这条原则放到 Agent 工程里，就是：**prompt 不是靠感觉调优，而是靠任务集回归。**

## 3.15 常见错误

**错误一：把所有内容塞进 system prompt。**  
这会增加成本，降低注意力，还会破坏缓存。

**错误二：写抽象形容词，不写可观察行为。**  
“谨慎”“专业”“高质量”都太抽象，要改成流程、边界、输出标准。

**错误三：只写正向要求，不写反模式。**  
模型需要知道不该做什么，尤其是过度工程、盲目重试、万能工具滥用。

**错误四：用关键词决定加载内容。**  
看到“记忆”就加载 memory section 不可靠。应该基于真实状态：是否有记忆文件、是否激活 Skill、工具是否启用。

**错误五：工具描述太短。**  
工具什么时候用、什么时候不用、失败怎么办，都需要写清楚。

**错误六：主 prompt 和专项 prompt 混用。**  
压缩、记忆、权限分类、审查都应该有自己的 prompt。

**错误七：没有评测。**  
prompt 每次改动都可能改变行为，不做回归就不知道是否退化。

## 3.16 最小实现建议

如果你要实现自己的 Prompt Runtime，可以先做一个简单版本：

1. 把主 prompt 拆成 `identity`、`operating_principles`、`tools`、`workspace`、`context`、`output` 六个 section。
2. 用 `context` 对象记录当前真实状态，包括工具、工作目录、记忆、Skill、渠道、时间。
3. 把稳定 section 放前面，把动态 section 放末尾。
4. 给每个工具写完整 description：是什么、何时用、何时不用、输入输出、风险。
5. 为上下文压缩、记忆提取、权限分类分别写专项 prompt。
6. 给 prompt 组装函数做快照测试。
7. 准备 10 个固定任务做行为回归，记录改 prompt 前后的差异。

不要一开始就追求复杂 cache。先保证 section 边界清晰、行为可解释、测试可回归。

## 系统地图

```text
Prompt Engineering
  -> 定义角色、目标、约束、工具策略、输出格式、评测标准
  -> 产出可复用的 prompt section 和专项 prompt

Prompt Runtime
  -> 根据当前状态选择 section
  -> 注入项目规则、记忆、Skill、动态上下文
  -> 为不同调用场景选择不同 prompt
  -> 控制缓存边界和 token 预算

Agent Loop
  -> 在每一轮调用前请求 Prompt Runtime 组装 prompt
  -> 根据 prompt 进行工具调用、压缩、记忆提取、输出
```

## 共同结论

9 份教程在这一章上的共同结论可以合并成四句话：

1. Prompt 不是文案，而是 Agent 行为控制面。
2. 好 prompt 不是“更长”，而是角色、任务、约束、工具、输出和测试边界更清楚。
3. 生产级 Agent 不应该维护一整段字符串，而应该维护可组合、可缓存、可测试的 Prompt Runtime。
4. Prompt 能提高正确行为概率，但不能替代权限、沙箱、工具校验和评测系统。

## Hello-Agents 融合补充

`hello-agents` 给提示工程补了三层材料。第一层是第三章的大语言模型基础：提示工程、思维链、模型选择和模型局限，让我们知道 prompt 为什么有效、为什么不稳定。第二层是第四章和第七章中的 ReAct / Plan-and-Solve / Reflection prompt 模板，它们把不同 Agent 范式的行为协议显式写进提示词。第三层是第九章上下文工程，它把 prompt 从“用户输入模板”提升为“有效上下文构造”的一部分。

Extra09 的实践踩坑尤其值得纳入本章：不要照抄“神级提示词”，不要凭感觉调优，应该先记录 Trace，再做单变量改动。它把提示词分成边界层、决策层、恢复层，这与本章的 Prompt Runtime 分层完全一致：稳定规则要放在可缓存前缀，动态状态和失败恢复要进入后置运行时上下文。

## 本章自检

1. 为什么 Agent prompt 不是普通聊天提示词？
2. 好 prompt 应该回答哪六个需求建模问题？
3. 为什么“谨慎”“专业”这类词不够工程化？
4. 行为引导模式如何抑制模型默认倾向？
5. few-shot 示例什么时候有用，什么时候会变成负担？
6. 用户输出和系统消费输出为什么要分开设计？
7. 工具描述为什么也是提示工程？
8. 主 prompt 和专项 prompt 为什么必须隔离？
9. Prompt Runtime 解决什么问题？它和模型路由有什么区别？
10. Prompt 为什么也需要回归测试？

## 开放性问题

1. Prompt 中哪些内容应该稳定常驻，哪些内容应该按需注入？你会用什么标准划分？
2. 当用户规则和项目规则冲突时，Prompt Runtime 应该如何解释和执行优先级？
3. 如果一个 prompt 在 8 个测试任务里提升了 6 个、退化了 2 个，你会如何决定是否采用？

## 原文入口

- [learn-claude-code s10: System Prompt](../../source/learn-claude-code/s10_system_prompt/README.md)
- [Hello-Agents Ch03: 大语言模型基础](../../source/hello-agents/docs/chapter3/第三章%20大语言模型基础.md)
- [Hello-Agents Ch04: 智能体经典范式构建](../../source/hello-agents/docs/chapter4/第四章%20智能体经典范式构建.md)
- [Hello-Agents Ch07: 构建你的 Agent 框架](../../source/hello-agents/docs/chapter7/第七章%20构建你的Agent框架.md)
- [Hello-Agents Ch09: 上下文工程](../../source/hello-agents/docs/chapter9/第九章%20上下文工程.md)
- [Hello-Agents Extra09: Agent 应用开发踩坑](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)
- [Alice 方法论: 提示词工程](../../source/Alice_methodology/chapters/14-prompts.md)
- [Hermes: 提示词系统](../../source/hermes-book/src/part2/ch05-prompt-system.md)
- [Harness Engineering: 系统提示词架构](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch05.md)
- [Harness Engineering: 通过提示词引导行为](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06.md)
- [Harness Engineering: 工具提示词作为微型驾驭器](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch08.md)
- [Claude Code 分析: Prompt 管理机制](../../source/claude-code-analysis/analysis/04g-prompt-management.md)
- [easy-langent: LangChain 核心组件实操](../../source/easy-langent/docs/guide/chapter2.md)

## 外部补充

- [OpenAI Prompt Engineering Guide](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
