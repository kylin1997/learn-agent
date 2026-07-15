# 第 9 章：Skills、MCP、插件与自进化

> 本章目标：理解 Agent 的能力扩展体系。读完本章，你应该能区分 Skill、Tool、MCP、Plugin、自进化分别解决什么问题，并能设计一套可发现、可加载、可授权、可更新、可回退的能力系统。

## 9.1 能力扩展的四个层次

Agent 不可能把所有能力都写死在核心循环里。它需要持续扩展：

- 新工具：连接外部 API 或本地能力。
- 新流程：把某类任务的做法沉淀下来。
- 新接口：接入标准协议和外部服务。
- 新产品能力：安装插件、配置渠道、增加 UI。
- 新行为习惯：从使用反馈中改进技能或偏好。

这些扩展看起来都叫“能力”，但层次不同：

| 层次 | 解决什么 | 例子 |
| --- | --- | --- |
| Tool | 执行一个动作 | 搜索、读文件、发 HTTP 请求 |
| Skill | 教模型如何完成一类任务 | 写技术博客、做代码审查、生成报告 |
| MCP | 用标准协议接外部工具 | GitHub、数据库、浏览器、企业系统 |
| Plugin | 打包一组技能、工具、配置和 UI | 一个完整的开发辅助扩展 |
| Self-evolution | 根据反馈改进规则或技能 | 自动优化 Skill、更新偏好 |

如果混淆这些层次，系统会变乱：把流程写成工具描述，把 API 接入写进 prompt，把插件当成单个 Skill，把自进化当成随便改系统提示词。

## 9.2 Skill 填补的是工具和 Prompt 之间的空白

Alice 的 Skill 章节说得很清楚：Skill 位于工具和 prompt 之间。

工具回答“能做什么动作”。  
Prompt 回答“Agent 总体怎么行动”。  
Skill 回答“遇到某类任务时，具体按什么流程做”。

例如“写技术博客”不适合做成单个工具，因为它不是一个原子动作；也不适合塞进 system prompt，因为不是每次都需要。它适合做成 Skill：

```text
当用户要求写技术博客时：
1. 先确认读者和主题。
2. 搜索或读取相关资料。
3. 生成大纲。
4. 等用户确认。
5. 分节写作。
6. 做一致性和事实检查。
```

Skill 的价值是把经验流程变成可加载的操作指南。

## 9.3 Skill 文件结构

一个常见 Skill 结构：

```text
my-skill/
  SKILL.md
  references/
  scripts/
  templates/
```

`SKILL.md` 通常包含 frontmatter：

```markdown
---
name: technical-writer
description: Write clear technical articles from source material
---

# Technical Writer

Use this skill when the user asks to write or revise a technical article.

Workflow:
1. Identify audience and thesis.
2. Gather sources.
3. Produce outline.
4. Draft section by section.
5. Review for accuracy and structure.
```

高质量 Skill 的特点：

- 触发条件清楚。
- 步骤具体。
- 输入输出明确。
- 需要工具时说清工具。
- 需要等待用户确认时明确停下。
- 引用资料放在 `references/`，脚本放在 `scripts/`。

低质量 Skill 只会写“帮用户写好文章”，这几乎没有执行价值。

## 9.4 两级加载：索引常驻，正文按需

Skill 和 Memory 一样，都要避免全文常驻。

更好的加载方式：

```text
启动时:
  扫描 Skill metadata，建立清单。

对话中:
  根据用户任务选择可能相关 Skill。

激活时:
  读取 SKILL.md 正文。

需要时:
  再读取 references、templates、scripts。
```

`learn-claude-code` s07 用教学版说明了这一点：不是所有 Skill 都塞进 system prompt，而是先 list，再 load。

这样做有三个好处：

- 节省 token。
- 避免无关流程干扰当前任务。
- 让 Skill 可以独立维护和更新。

## 9.5 Skill 激活不是关键词匹配那么简单

最简单的 Skill 触发是关键词，例如用户说“写博客”就加载 writing Skill。但生产系统要更稳：

- 用户显式点名 Skill，优先加载。
- 当前任务语义匹配 Skill description。
- 项目规则指定某类任务使用某 Skill。
- 文件路径匹配 Skill frontmatter `paths`。
- 子 Agent 或插件声明需要某 Skill。

也要支持“不加载”：

- Skill 与当前任务不相关。
- Skill 依赖缺失。
- Skill 来源不可信。
- Skill 超出上下文预算。
- Skill 需要的权限未授权。

Skill 激活本质上是一次路由决策。

## 9.6 Skill 与工具的区别

很多初学者会问：Skill 能不能直接调用工具？工具能不能写很长说明变成 Skill？

可以，但不建议混淆。

| 维度 | Tool | Skill |
| --- | --- | --- |
| 本质 | 可执行动作 | 操作流程和知识 |
| 输入 | 结构化参数 | 自然语言任务上下文 |
| 输出 | 工具结果 | 指导模型行动 |
| 权限 | 必须运行时检查 | 加载也要检查来源，执行仍靠工具权限 |
| 生命周期 | 注册、调用、返回 | 发现、加载、使用、改进 |

Tool 是手，Skill 是手册。手册可以教你用手，但不能替代手。

## 9.7 MCP：外接工具的标准协议

MCP 解决的是另一个问题：不同工具服务如何以标准方式接入 Agent。

一个 MCP 连接大致包含：

```text
Agent
  -> MCP Client
      -> connect server
      -> discover tools
      -> normalize tool names
      -> assemble tool pool
      -> call tool
      -> handle result / error / reconnect
```

MCP 的价值是把外部能力标准化：

- 工具发现。
- 工具 schema。
- 调用协议。
- 认证和连接生命周期。
- 多 transport。
- 服务器反向通知。

`learn-claude-code` s19、Alice MCP 章节、Claude Code 分析的 MCP 实现都强调同一点：MCP 工具进入工具池后，也必须经过权限、安全和 prompt 描述管理。

## 9.8 MCP 的风险：工具池是动态的

MCP 带来灵活性，也带来风险：

- 服务器可能连接失败或断线。
- 工具列表可能变化。
- 工具描述质量参差不齐。
- 工具名称可能冲突。
- 工具结果可能很大。
- 工具返回内容是不可信输入。
- OAuth 和 token 生命周期需要治理。

因此 MCP 工具应该命名规范化，例如：

```text
mcp__server__tool
```

并且必须进入统一权限管线：

```text
MCP Tool
  -> name normalization
  -> tool description budget
  -> permission check
  -> sandbox / network policy
  -> result budget
  -> untrusted output labeling
```

不要因为工具来自 MCP，就默认它安全。

## 9.9 Plugin：把能力打包成产品单元

Plugin 通常比 Skill 大。它可以包含：

- 一个或多个 Skill。
- MCP server 配置。
- Hooks。
- 命令。
- UI。
- 默认配置。
- 权限声明。

如果 Skill 是一份操作指南，Plugin 更像一个可安装能力包。

hello-claw 的技能开发与插件说明强调了发布、安装、启用、禁用、诊断、配置凭证等完整生命周期。这些内容提醒我们：能力扩展不是“把文件复制进去”就结束了，还要管理信任、依赖、版本和权限。

## 9.10 能力加载优先级

能力系统需要优先级。常见层次：

```text
内置 bundled skills
  < 用户全局 skills
  < 项目 skills
  < 插件提供 skills
  < 会话临时激活
```

但优先级不等于可以覆盖安全底线。项目 Skill 可以调整工作方式，但不能绕过工具权限。插件 Skill 可以提供流程，但不能偷偷读取敏感文件。

对同名 Skill 要处理：

- 去重。
- 来源标记。
- 版本冲突。
- 用户可见。
- 禁用机制。

## 9.11 Skill 自我改进

自进化最安全的切入点不是让 Agent 直接改核心代码，而是改可回退的 Skill 或用户偏好。

Alice 的自进化章节提出 L0-L2 三层：

```text
L0:
  人格、偏好、可变规则反思。

L1:
  Skill、prompt、流程改进。

L2:
  代码级改动，需要沙箱、审查、回退。
```

Skill 自动改进应该有门禁：

- 只改 `[MUTABLE]` 或 Skill 正文中的可变部分。
- 不能改安全底线。
- 生成 diff，而不是直接覆盖。
- 保留撤销栈。
- 重要改动需要用户确认。
- 改完要跑回归案例。

这是一条很重要的边界：**自进化不是自由修改自己，而是受控更新可回退配置。**

## 9.12 能力系统的最小实现

第一版可以这样做：

1. 支持 `skills/*/SKILL.md`。
2. 解析 `name`、`description`、`paths`。
3. 启动时构建 Skill catalog。
4. 当前任务按 description 选择候选 Skill。
5. 激活后读取 `SKILL.md` 正文。
6. references、scripts 按需读取，不自动全量加载。
7. MCP 工具统一命名并进入工具池。
8. MCP 工具调用走和内置工具一样的权限管线。
9. 插件安装后显示来源、权限、依赖和启用状态。
10. Skill 改进只生成建议或 diff，用户确认后写入。

## Hello-Agents 融合补充

`hello-agents` 第 10 章把 MCP 放进更大的通信协议图谱：MCP、A2A、ANP 分别面向不同层次的问题。MCP 解决 Agent 与外部工具、资源、服务之间的标准连接；A2A 更关注 Agent 与 Agent 之间的交互；ANP 则更偏开放网络中的 Agent 发现、身份和互操作。对本课程来说，MCP 是最先应该落地的能力，因为它直接影响工具生态和权限管线。

第 10 章还强调 MCP 不只是“调用工具”，而包含客户端、传输、工具发现、参数协议和结果返回。学习时可以把它拆成五个问题：

1. 如何发现 server 提供了哪些工具？
2. 如何把工具 schema 转成模型可理解的说明？
3. 如何把模型输出转成合法工具参数？
4. 如何把工具结果标记为可信或不可信上下文？
5. 如何让远端工具也经过本地权限审计？

Extra05 和 Extra08 对 Skills 的补充很关键。Skills 与 MCP 的差异在于：Skill 主要提供“如何做”的流程知识，MCP 主要提供“能调用什么”的外部能力。好的 Skill 不应该一开始把所有细节塞进上下文，而应该通过 progressive disclosure 分层加载：先读 `SKILL.md`，必要时再读 references、scripts、assets。Extra08 还把好 Skill 的写法拆成 frontmatter、简洁约束、脚本、参考资料、资产和可委托 agent 元数据，这正好补足本章的工程实践。

Extra10 的自进化内容提醒我们：能力系统可以自我改进，但必须先有评估、回滚、治理和供应链安全。一个会自动安装、自动改写、自动执行的能力系统，如果没有边界，本质上就是一个高风险执行环境。正确顺序应该是：

```text
记录使用问题
  -> 生成改进建议
  -> 用评测集验证
  -> 展示 diff 和风险
  -> 用户确认
  -> 可回滚发布
```

Extra11 的 WebAgent 则说明 MCP 不只适合文件、数据库、搜索，也可以成为浏览器操作、网页感知和任务执行的连接层。WebAgent 和传统 RPA 的差别在于：它不只是执行固定脚本，还要理解页面状态、推理下一步动作，并把不确定性暴露给权限系统。

## 系统地图

```text
Skill Catalog
  -> discover
  -> select
  -> load
  -> execute guidance
  -> improve

MCP
  -> connect
  -> discover tools
  -> normalize
  -> permission
  -> call

Plugin
  -> package skills/tools/hooks/config
  -> install
  -> trust
  -> enable / disable
```

## 共同结论

1. Skill 是可加载流程，不是工具本身。
2. MCP 是标准化外接工具协议，但不自动可信。
3. Plugin 是能力打包与分发单位，需要信任和权限治理。
4. 自进化要从可回退的 Skill 和可变配置开始，不应直接修改核心安全边界。

## 本章自检

1. Skill、Tool、MCP、Plugin 的边界分别是什么？
2. 为什么 Skill 要两级加载？
3. MCP 工具为什么也要经过统一权限系统？
4. 插件生命周期为什么包含信任、依赖和诊断？
5. 自进化为什么要有 `[PROTECTED] / [MUTABLE]` 边界？

## 开放性问题

1. 一个“数据库分析助手”应该做成 Skill、MCP server、Plugin，还是三者组合？你如何划分？
2. 如果某个 Skill 频繁被用户修改，你如何判断它应该升级为产品功能，还是继续作为项目级 Skill？
3. 自进化系统提出了一个更高效但更危险的流程，应该由谁来评估和批准？

## 原文入口

- [learn-claude-code s07: Skill Loading](../../source/learn-claude-code/s07_skill_loading/README.md)
- [learn-claude-code s19: MCP Tools](../../source/learn-claude-code/s19_mcp_plugin/README.md)
- [learn-claude-code skills 示例](../../source/learn-claude-code/skills/agent-builder/SKILL.md)
- [Alice 方法论: MCP](../../source/Alice_methodology/chapters/08-mcp.md)
- [Alice 方法论: Skills](../../source/Alice_methodology/chapters/09-skills.md)
- [Alice 方法论: 自我进化](../../source/Alice_methodology/chapters/10-self-evolution.md)
- [Hermes: Skill System](../../source/hermes-book/src/part3/ch08-skill-system.md)
- [Hermes: Delegation](../../source/hermes-book/src/part3/ch09-delegation.md)
- [Harness Engineering Ch22: 技能系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch22.md)
- [Claude Code 分析: Skills 实现](../../source/claude-code-analysis/analysis/04c-skills-implementation.md)
- [Claude Code 分析: MCP 实现](../../source/claude-code-analysis/analysis/04d-mcp-implementation.md)
- [hello-claw 附录 D: 技能开发与发布](../../source/hello-claw/docs/cn/appendix/appendix-d.md)
- [hello-agents Ch10: 智能体通信协议](../../source/hello-agents/docs/chapter10/第十章%20智能体通信协议.md)
- [hello-agents Extra05: AgentSkills 解读](../../source/hello-agents/Extra-Chapter/Extra05-AgentSkills解读.md)
- [hello-agents Extra08: 如何写出好的 Skill](../../source/hello-agents/Extra-Chapter/Extra08-如何写出好的Skill.md)
- [hello-agents Extra10: Agent 自进化](../../source/hello-agents/Extra-Chapter/Extra10-Agent自进化.md)
- [hello-agents Extra11: WebAgent 科普与实战](../../source/hello-agents/Extra-Chapter/Extra11-WebAgent科普与实战.md)
