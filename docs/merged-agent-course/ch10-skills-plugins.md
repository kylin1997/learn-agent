# 第 10 章：Skills 与插件系统

> Tool 让 Agent 获得一个动作，Skill 让 Agent 学会一类工作的做法，插件则把一组可安装、可治理、可演进的能力组织成产品扩展单元。

## 10.1 学习目标与边界

学完本章，你应该能够：

1. 解释 Skill 在 Prompt、Tool 和固定 Workflow 之间的位置。
2. 设计元数据、正文、脚本与参考资料的渐进披露机制。
3. 区分 Skill 的发现、就绪、激活、加载、使用和改进阶段。
4. 用 manifest 把插件的组件、依赖、权限、版本和来源声明为可验证契约。
5. 设计能力包的安装、解析、启用、升级、禁用、诊断和回滚流程。
6. 为 Skill 与插件建立来源可信、依赖锁定和冲突处理机制。
7. 给自改进划定不可修改的安全边界，并用评测和审批控制发布。

本章只讨论 Skills 与插件。Tool 作为它们依赖的原子执行能力会被用于说明边界，但不重复工具运行时；MCP 及其工具发现、连接和授权机制统一放在第 11 章，不在本章展开。插件可以声明外部协议组件，但声明和治理属于插件，协议行为仍属于互操作层。

## 10.2 为什么需要 Skill 这一中间层

Agent 的能力常被粗略地分成 Prompt 和 Tool：前者告诉模型怎么思考，后者让系统执行动作。但实际任务中还有大量“可复用的情境化做法”：代码审查要按风险排序，写研究报告要先建立证据矩阵，处理 PDF 要先判断文本层是否存在。

把这些做法全部放进系统 Prompt，会带来三个问题：

- 每轮都占上下文，即使当前任务无关。
- 不同领域的流程互相干扰，降低指令显著性。
- 用户或团队难以独立版本化、分享和迭代某一类做法。

把它们做成 Tool 也不合适。Tool 应有稳定的结构化输入输出并完成一个可执行动作；“做好代码审查”本身包含判断、循环、多个工具调用和停顿点，不是一个原子函数。

Skill 因此位于两者之间：

```text
System Prompt: Agent 的恒定身份、全局规则和安全不变式
Skill:         特定任务下按需加载的流程知识、领域约束和资源入口
Tool:          受权限控制的原子动作
Workflow:      由代码固定的状态转移和控制流
```

Skill 提高的是“在这个情境中如何组合已有能力”的质量。它不天然增加执行权限，也不应取代必须确定执行的 Workflow。

## 10.3 Skill、Workflow 与插件的边界

| 维度 | Skill | Workflow | 插件 |
| --- | --- | --- | --- |
| 核心对象 | 模型可读的流程与知识 | 代码定义的状态机/执行图 | 可安装的能力包 |
| 控制方式 | 模型在约束内判断 | 程序决定转移 | manifest + 生命周期管理 |
| 适合任务 | 开放、需专业判断 | 路径固定、需确定性 | 多组件、需分发治理 |
| 典型内容 | `SKILL.md`、references、scripts、assets | 节点、状态、分支、检查点 | Skills、命令、Hook、工具、配置、UI 等 |
| 失败重点 | 误激活、指令歧义、上下文膨胀 | 状态错误、恢复和幂等 | 来源、依赖、权限、升级、兼容性 |

一个插件可以包含多个 Skill；一个 Skill 可以指导模型调用工具或进入 Workflow；三者可以组合，但不应把边界抹平。判断原则是：

- 需要“告诉模型怎样做”时，用 Skill。
- 需要“无论模型怎样想都必须按此顺序执行”时，用 Workflow。
- 需要把多个组件作为一个可安装、可升级、可禁用的单元交付时，用插件。

## 10.4 Skill 的最小形态与完整结构

最小 Skill 只需要一个带元数据的 `SKILL.md`：

```markdown
---
name: code-review
description: Review code changes for correctness, regressions, and missing tests.
metadata:
  version: "1.2.0"
---

# Code Review

1. Read the change and its callers.
2. Identify behavioral risks before style issues.
3. Verify findings with code evidence.
4. Report findings by severity with file and line references.
```

Agent Skills 官方格式把 `name` 和 `description` 定义为顶层必需字段，把扩展信息放在可选的 `metadata` 映射中；`version` 不是标准顶层字段。示例中的 `metadata.version` 是宿主或发布系统使用的扩展键，官方规范不赋予它跨宿主一致的版本解析语义。需要强版本约束时，插件 manifest、锁文件或组织 Catalog 才是权威来源。

完整结构可以是：

```text
code-review/
  SKILL.md                 # 触发摘要、边界、主流程
  references/              # 仅在需要时读取的规范与领域资料
  scripts/                 # 需要确定性的校验、转换和批处理
  assets/                  # 输出模板、示例文件、静态素材
  agents/                  # 可选的展示或委托元数据
  tests/                   # 激活、流程和脚本回归案例
```

目录多不等于质量高。只有当资源能被清楚引用、按需加载并接受版本治理时，才值得从正文拆出。

## 10.5 渐进披露：把能力库变成可检索上下文

### 10.5.1 三层加载

Skill 系统的关键不是“能读 Markdown”，而是不会把所有 Markdown 一次塞进上下文。典型的三级披露是：

```text
第 1 层：Catalog Metadata
  name + description + catalog_version + readiness + source
  启动时或检索时可见

第 2 层：SKILL.md Instructions
  触发后加载主流程、约束和资源导航

第 3 层：Resources
  references / scripts / assets
  只有具体步骤需要时才读取或执行
```

第一层解决“可能该用什么”，第二层解决“这类任务怎样做”，第三层解决“当前步骤需要哪些细节或确定性执行”。渐进披露降低 token 成本，也减少无关指令竞争。这里的 `catalog_version` 是宿主 Catalog 为解析、锁定和审计维护的版本元数据，可以来自受信插件 manifest、锁文件、内容摘要或经验证的 `metadata.version`；它不是 Agent Skills 标准要求在启动上下文中暴露的字段，也不能仅凭任意 Skill 自报值建立信任。

### 10.5.2 披露不是简单截断

成熟系统需要预算策略：为 Catalog、激活 Skill 正文和运行结果分别设预算；超限时优先保留名称、触发条件、禁止事项和资源索引，再按相关性加载正文。盲目截断文件尾部可能恰好删除安全边界或验收步骤。

应让 Skill 本身可导航：主文件保持短而完整，清楚写明何时读取哪个 reference。避免多层链式引用，让模型为了一个规则连续追五个文件；也避免在多个 reference 中复制同一规范，造成版本漂移。

### 10.5.3 脚本与参考资料分工

- **references** 提供模型需要理解和判断的知识。
- **scripts** 固化对格式、顺序或数值要求严格的步骤。
- **assets** 是输出要使用的材料，不应默认注入上下文。

如果模型每次都要重新生成同一段易错转换代码，应把它变成测试过的脚本；如果任务需要结合上下文作开放判断，则保留在指令或参考资料中。核心不是“代码越多越专业”，而是把确定性放在正确层。

## 10.6 Skill 激活是一条路由管线

### 10.6.1 发现不等于激活

Skill 生命周期至少包含：

```text
discover -> parse -> validate -> resolve -> ready
    -> retrieve -> rank -> activate -> load -> use -> evaluate
```

- **discover**：在允许的目录、内置清单或插件中找到候选。
- **validate**：校验 frontmatter、名称、大小、结构与来源。
- **resolve**：检查依赖、工具、运行时和版本约束。
- **ready**：确认当前环境可以使用，但尚未加入任务上下文。
- **retrieve/rank**：根据当前任务检索并排序候选。
- **activate/load**：选定 Skill，加载正文和必要资源。
- **use/evaluate**：执行指导并记录是否产生价值。

扫描到了 `SKILL.md` 只能证明文件存在。依赖缺失、来源不可信、版本冲突或权限不足时，它都不应进入 ready 状态。

### 10.6.2 激活信号

激活可以组合以下信号：

1. 用户显式点名，通常拥有最高业务优先级。
2. 用户任务与 `description` 的语义匹配。
3. 当前文件路径与 `paths` 过滤规则匹配。
4. 项目或组织 Policy 指定必须使用某 Skill。
5. 已激活 Skill 声明下一步需要另一个 Skill。
6. 任务状态满足前置条件，且依赖和权限就绪。

`description` 是路由接口，不是宣传文案。它应同时描述“何时使用”和“何时不要使用”，避免宽泛的“处理所有文档”抢占其他 Skill。

### 10.6.3 显式调用与模型调用

高副作用 Skill 可以设置为只能显式调用；普通 Skill 可以允许模型主动激活。无论哪种方式，激活只授予“读取操作指南”的能力，不自动授予指南中提到的工具权限。

模型可提出激活候选，但 Harness 应检查：来源是否允许、依赖是否满足、上下文预算是否足够、同名冲突是否已解析、当前任务是否允许此 Skill。最终激活记录要包含来源、版本和原因，便于调试误触发。

### 10.6.4 多 Skill 组合

同时激活多个 Skill 时会出现指令冲突、资源重复和预算竞争。系统应限制活跃数量，按任务角色确定主 Skill 与辅助 Skill，并在冲突时采用显式优先级或停止询问，而不是让模型猜测哪个规则更重要。

Skill 的依赖图还要检测循环：`research` 要求 `writer`，`writer` 又要求 `research`，如果没有阶段状态，会无限加载或反复委托。

## 10.7 写给模型的指令应怎样设计

高质量 Skill 通常具备以下特征：

- **单一职责**：围绕一个稳定任务族，不承诺包办所有工作。
- **触发边界清楚**：正例、反例和不适用条件明确。
- **输入输出可识别**：说明需要哪些材料，交付物如何验收。
- **关键顺序明确**：哪些步骤可调整，哪些必须先后执行。
- **停止点明确**：何时等待用户、何时因缺失信息而停止。
- **失败路径明确**：依赖缺失、格式异常和验证失败怎么处理。
- **自由度匹配风险**：高风险步骤低自由度，开放创作允许更多判断。
- **语言简洁**：只保留模型当前完成任务所需的内容。

“必须写得非常专业”“尽力提供高质量结果”几乎不可测试。更好的约束是“先列出带路径的证据，再提出结论；无法定位证据时标记为未验证”。

负面边界往往比泛化目标更有效，例如：不要在用户只询问审查方法时启动完整代码审查；不要自动发布；不要在来源不足时虚构引用。负面约束不是越多越好，应只保留真实发生且代价较高的失败模式。

## 10.8 插件：清单驱动的能力包

### 10.8.1 为什么不能只复制目录

插件比 Skill 大，因为它面对的是产品扩展生命周期。一个插件可能包含 Skills、工具、命令、Hook、默认配置、UI 资源和外部服务声明。若系统只扫描目录并执行其中内容，就无法可靠回答：它来自谁、需要什么、会获得哪些权限、升级后变了什么、冲突时选谁。

manifest 是插件与宿主之间的契约：

```yaml
id: com.example.code-quality
name: Code Quality Pack
version: 2.1.0
requires_host: ">=1.8 <3.0"
components:
  skills:
    - path: skills/code-review
    - path: skills/test-planner
  hooks:
    - event: after_tool_use
      entry: hooks/scan-output.js
permissions:
  filesystem:
    read: ["workspace/**"]
  network: []
dependencies:
  plugins:
    - id: com.example.shared-formatters
      version: "^1.4"
provenance:
  publisher: example-org
  source: https://example.invalid/code-quality
  digest: sha256:...
```

字段名可因实现不同而变化，但必须表达稳定身份、版本、宿主兼容性、组件、依赖、权限和来源。敏感配置只声明引用，不在 manifest 中存明文凭证。

### 10.8.2 能力包的组件边界

插件加载器不应把所有文件视为同一种内容：

| 组件 | 加载时机 | 核心治理 |
| --- | --- | --- |
| Skill | 发现时读元数据，激活时读正文 | 路由、预算、来源、冲突 |
| Hook | 对应生命周期事件 | 顺序、超时、失败隔离、不可绕过 deny |
| 命令/工具 | 注册或调用时 | schema、权限、沙箱、审计 |
| UI/资产 | 界面需要时 | 内容安全、资源隔离、兼容性 |
| 配置 | 解析阶段 | schema、作用域、秘密引用、迁移 |

插件提供组件，不应接管宿主安全内核。一个 Hook 返回 allow，也不能覆盖不可变 deny；一个 Skill 声明 `allowed_tools` 只能收窄工具集，不能扩大用户权限。

## 10.9 插件生命周期

### 10.9.1 五个核心阶段

```text
1. Discover: 发现候选包与来源元数据
2. Inspect:  解析 manifest，展示组件、依赖、权限和风险
3. Resolve:  求解版本与依赖，验证完整性和兼容性
4. Activate: 原子注册组件，建立隔离和审计身份
5. Operate:  诊断、升级、禁用、卸载、回滚和撤销凭证
```

安装只意味着内容进入受控存储；启用才意味着组件可以参与运行。将两者分开，用户才能在执行任何代码前审查能力和权限。

### 10.9.2 原子激活与失败隔离

插件含多个组件时，不能加载两个成功、第三个失败后留下半激活状态。激活过程应构建临时注册表，通过全部校验后一次提交；失败则回滚，不污染当前运行时。

插件故障应有类型化状态，例如 manifest 无效、依赖缺失、宿主不兼容、签名失败、权限被拒、组件冲突、迁移失败、运行时崩溃。把所有错误压成“插件加载失败”会让诊断和自动恢复都失去依据。

### 10.9.3 禁用、卸载与残留状态

禁用停止组件运行但保留包和配置；卸载移除包，却不能盲目删除用户数据。系统需要声明哪些状态由插件拥有、哪些属于用户产物，以及卸载后凭证、缓存、后台任务和数据迁移如何处理。

安全事件中还要支持快速隔离：立即阻止插件 Hook 和工具、撤销临时凭证、停止后台进程，同时保留足够证据用于审计。

## 10.10 版本、依赖与冲突治理

### 10.10.1 身份与版本必须稳定

显示名称可以变化，插件 ID 和 Skill 规范名必须稳定。同名不同来源不能静默覆盖。每次运行记录解析后的确切版本，避免“昨天能复现，今天自动指向最新版”。

语义化版本只能表达发布者对兼容性的承诺，不能替代测试。宿主 API、manifest schema、Skill 格式和插件间依赖都要独立声明兼容范围。

### 10.10.2 依赖求解

依赖系统至少处理：

- 直接与传递依赖。
- 版本范围交集和互斥冲突。
- 可选依赖与能力降级。
- 循环依赖。
- 平台、架构和运行时约束。
- 锁文件、哈希和可复现安装。

解析失败时，不要“尽量挑一个最新版”后继续。应给出冲突链，让用户或管理员明确选择升级、降级、隔离或放弃安装。

### 10.10.3 Skill 覆盖与来源优先级

常见来源包括组织托管、内置、用户全局、项目和插件。优先级应显式，并同时考虑信任：项目内同名 Skill 可以定制工作方式，但不应冒充组织强制 Skill；符号链接和真实路径去重要防止同一 Skill 被重复加载。

更稳健的做法是保留命名空间和来源标记，只在用户明确配置别名时提供短名。这样冲突可见，也更容易审计某次激活究竟用了哪份指令。

## 10.11 来源可信与供应链边界

来源治理要区分四个问题：

1. **身份**：发布者是谁？
2. **完整性**：下载内容是否被篡改？
3. **声誉**：发布者和包过去是否可靠？
4. **行为**：当前版本实际声明和执行了什么？

签名和哈希主要解决前两个问题，不能证明代码无恶意。市场审核和下载量也不能替代本地最小权限。建议建立信任分级：内置或组织托管、已验证发布者、用户指定来源、未知来源；信任等级影响自动更新、可申请权限和默认是否启用。

安装与更新时比较：新增组件、新增依赖、权限扩大、网络目标变化、Hook 事件变化、安装脚本变化和敏感配置变化。任何权限扩张都应被视为新的授权请求，而不是普通补丁更新。

## 10.12 自改进：从经验提案到受控发布

Skill 是适合改进的层，因为它文本化、局部、可评测、可版本化。但“适合”不等于可以让 Agent 直接改完并立即生效。

### 10.12.1 可变与受保护区域

至少区分：

```text
PROTECTED:
  安全边界、权限上限、来源 Policy、发布审批规则

MUTABLE:
  示例、流程说明、常见失败修正、资源导航、用户偏好
```

这个分区必须由代码和文件权限强制，不能只在 Skill 中写“不要修改受保护内容”。插件核心代码、自更新器和权限声明的修改应采用更高等级流程。

### 10.12.2 改进闭环

```text
记录失败/反馈
  -> 提取与 Skill 相关的最小证据
  -> 生成候选 diff 与改进假设
  -> 静态检查和安全扫描
  -> 在固定评测集与历史回放上比较
  -> 人工或 Policy 审批
  -> 发布新版本/灰度
  -> 监测退化
  -> 保留一键回滚
```

改进必须回答“哪个失败会被修复，如何知道没有破坏其他任务”。只根据一次成功对话把偶然策略写入长期 Skill，容易过拟合；只优化完成率，也可能增加成本、权限申请和隐私暴露。

### 10.12.3 自改进的权限上限

Skill 可以建议使用更窄、更可靠的流程，不能通过改写自己获得新工具权限。插件可以提出更新，不能自行签署、审批和发布同一个更新。生成、评测、批准和部署最好由不同角色或至少不同阶段完成。

自改进发现缺少能力时，可以生成需求或安装建议；自动搜索到一个包不等于可以自动安装并启用。能力来源的信任决策始终在改进循环之外。

## 10.13 最小实现：Catalog、激活器与插件注册表

下面的伪代码保留最重要的边界：元数据常驻、正文按需、权限只收窄、插件原子激活。

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SkillMeta:
    qualified_name: str
    description: str
    catalog_version: str        # 宿主解析后的版本，不是标准顶层 frontmatter
    source: str
    root: Path
    required_tools: tuple[str, ...]
    explicit_only: bool = False

class SkillCatalog:
    def __init__(self):
        self.items: dict[str, SkillMeta] = {}

    def discover(self, roots, trust_policy):
        for root in roots:
            for skill_file in find_skill_files(root):
                meta = parse_frontmatter_only(skill_file)
                validate_meta(meta, skill_file)
                item = qualify_with_source(meta, skill_file)
                if trust_policy.can_index(item):
                    self.items[item.qualified_name] = item

    def candidates(self, task, context):
        ready = [s for s in self.items.values() if dependencies_ready(s)]
        return rank_by_relevance(task, context.paths, ready)

def activate(skill, task, session):
    if skill.explicit_only and task.explicit_skill != skill.qualified_name:
        raise PermissionError("explicit invocation required")
    session.policy.assert_source_allowed(skill.source)

    # Skill can only reduce the session's tool set.
    effective_tools = session.allowed_tools.intersection(skill.required_tools)
    instructions = load_with_budget(skill.root / "SKILL.md")
    return ActiveSkill(skill, instructions, effective_tools)

def activate_plugin(package, runtime):
    manifest = verify_and_parse_manifest(package)
    resolve_locked_dependencies(manifest)
    runtime.policy.approve_manifest_delta(manifest)

    staged = runtime.registry.stage()
    for component in manifest.components:
        staged.register(validate_component(component, manifest))
    staged.healthcheck()
    staged.commit()  # all components become visible together
```

第一版可以只支持本地 Skill、固定来源层级和只含 Skills 的插件，但仍应从一开始保留来源、版本、启用状态和原子注册，避免以后无法追溯。

## 10.14 生产约束

1. Catalog 只常驻最小元数据，并有明确 token 预算。
2. Skill 正文、脚本和参考资料分别校验大小、编码和路径边界。
3. 激活结果绑定 Skill 的确切来源、版本和内容摘要。
4. Skill 只能收窄工具范围，工具执行仍走统一权限管线。
5. 插件 manifest 使用版本化 schema，未知关键字段应拒绝而非忽略。
6. 安装、启用、更新、禁用和卸载是不同状态转换。
7. 依赖使用锁定版本和内容摘要，可重建确切运行环境。
8. Hook 和后台组件有超时、熔断、资源限额和独立审计身份。
9. 更新进行权限差异比较，支持灰度、健康检查和自动回滚。
10. 删除插件前处理凭证、任务、缓存和用户数据的所有权。
11. 多租户环境隔离 Catalog、配置、凭证和插件状态。
12. 远程 Skill 搜索结果只进入候选列表，不自动取得信任。

## 10.15 典型失败模式

| 失败模式 | 根因 | 修正方向 |
| --- | --- | --- |
| 所有 Skill 全文常驻 | 没有渐进披露 | Catalog 元数据常驻，正文与资源按需加载 |
| 只靠关键词激活 | 触发模型过于简单 | 语义、路径、显式调用、就绪和负例联合判断 |
| `description` 写成宣传语 | 路由边界缺失 | 同时写适用和不适用条件 |
| 激活 Skill 后自动开放工具 | 把流程知识当授权 | 工具集合取交集，执行重新授权 |
| 项目 Skill 静默覆盖组织 Skill | 优先级等同信任 | 命名空间、来源可见和不可覆盖 Policy |
| 插件安装即运行所有组件 | 安装与启用混淆 | 先审查 manifest，再原子激活 |
| 自动更新只比较版本号 | 看不到权限和依赖变化 | manifest/锁文件/权限差异审查 |
| 依赖冲突时挑最新版继续 | 追求可用掩盖不确定性 | 显式失败并展示冲突链 |
| Agent 改 Skill 后立即生效 | 缺少独立评测与发布 | diff、回放、审批、版本和回滚 |
| 插件禁用后后台任务仍运行 | 生命周期不完整 | 统一撤销组件、进程和凭证 |

## 10.16 测试与验收

### 10.16.1 Skill 测试

1. **解析测试**：frontmatter 缺失、未知字段、非法名称、超大文件和编码异常。
2. **激活正例**：典型用户任务能检索到正确 Skill。
3. **激活负例**：相似但不适用的任务不会误触发。
4. **优先级测试**：显式调用、路径、组织 Policy 和来源冲突结果稳定。
5. **预算测试**：大量 Skill 下 Catalog 和正文不超过预算，关键边界不被截断。
6. **资源测试**：reference 按需读取，脚本只在声明步骤执行，路径不逃逸。
7. **权限测试**：Skill 不能扩大工具和数据访问范围。
8. **效果回归**：固定任务集比较完成质量、成本、轮数和人工干预。

### 10.16.2 插件测试

1. manifest schema、签名/摘要和宿主兼容性。
2. 直接/传递/可选/循环依赖与版本冲突。
3. 多组件激活中途失败后的完整回滚。
4. Hook 超时、崩溃和重复执行的隔离。
5. 升级新增权限时重新审批，拒绝后保持旧版本可用。
6. 禁用和卸载后无残留进程、工具、任务或有效凭证。
7. 回滚恢复确切组件、配置和依赖版本。
8. 未知来源、篡改包和发布者密钥撤销场景。

验收标准不是“能加载示例 Skill”，而是：系统能准确解释某能力从哪里来、为什么被激活、当前能使用什么、失败后如何恢复。

## 10.17 系统地图

```text
                         Capability Sources
        Built-in / Managed / User / Project / Plugin / Remote Index
                                  |
                    Discover -> Validate -> Trust
                                  |
                         Skill / Plugin Catalog
                                  |
Task -> Retrieve -> Rank -> Readiness -> Activate -> Load Instructions
                                  |                    |
                                  |               references/scripts/assets
                                  v
                         Effective Tool Subset
                                  |
                    Permission Pipeline -> Execute
                                  |
                        Evaluate Outcome / Feedback
                                  |
                 Candidate Diff -> Tests -> Approval -> Version

Plugin Plane:
Package -> Manifest -> Integrity -> Dependency Resolve -> Permission Diff
        -> Stage Components -> Healthcheck -> Atomic Enable
        -> Diagnose / Upgrade / Disable / Uninstall / Rollback
```

## 10.18 共同结论

1. Skill 封装的是按需加载的流程知识，不是新的执行权限。
2. 渐进披露的本质是把大型能力库变成可检索、可预算的上下文系统。
3. 发现、就绪、激活、加载和使用是不同状态，不能用一个“已安装”概括。
4. 插件是 manifest 驱动的能力包，价值在于统一分发和生命周期治理。
5. 版本号、依赖、来源和权限必须共同决定一个能力是否可运行。
6. 安装与启用分离、原子激活和可回滚，是插件进入生产的基本条件。
7. 自改进应产出候选变更和证据，不能同时拥有修改、批准与发布权。

## 10.19 本章自检

1. 为什么“写技术文章”更适合 Skill，而“保存文件”更适合 Tool？
2. 三级渐进披露分别解决什么问题？
3. Skill 被发现后，还需要经过哪些步骤才能激活？
4. `description` 为什么既要写正向触发，也要写不适用条件？
5. Skill 的工具白名单为什么只能收窄而不能扩大权限？
6. manifest 相比目录扫描提供了哪些可验证契约？
7. 为什么插件安装和启用必须是两个状态？
8. 签名能证明什么，不能证明什么？
9. Skill 自改进为什么需要固定评测集和历史回放？

## 10.20 开放性问题

1. 当多个 Skill 都与任务高度相关时，应由模型组合、规则编排，还是要求用户选择？
2. 如何测量 Skill 的真实增益，并排除模型随机性和任务难度变化？
3. `description` 的标准化会提高互操作，却可能限制表达能力；最小公共字段应包含什么？
4. 项目可以覆盖用户 Skill 到什么程度，组织托管 Skill 又应保留哪些不可覆盖部分？
5. 当 Skill 依赖一个未安装插件时，系统应自动建议、自动下载，还是只报告缺失？
6. 插件的传递依赖申请了高于顶层插件的权限时，授权界面应如何表达？
7. 远程 Skill 市场如何抵抗刷量、接管废弃包和相似名称投毒？
8. 插件升级改变输出语义但不改变 API，应该算补丁版本还是破坏性版本？
9. 自改进 Skill 如何避免只适应一个用户而损害团队共同流程？
10. 能否把一段长期稳定的 Skill 自动编译成确定性 Workflow？转换的判据是什么？
11. 谁拥有 Agent 生成的新 Skill，其来源、许可和责任应如何记录？

## 10.21 原文入口

### 本地融合来源

- [learn-claude-code：Skill Loading](../../source/learn-claude-code/s07_skill_loading/README.md)
- [learn-claude-code：Skill 示例](../../source/learn-claude-code/skills/agent-builder/SKILL.md)
- [Alice 方法论：Skill 系统](../../source/Alice_methodology/chapters/09-skills.md)
- [Alice 方法论：自我进化](../../source/Alice_methodology/chapters/10-self-evolution.md)
- [Harness Engineering：技能系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch22.md)
- [Harness Engineering：插件系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch22b.md)
- [Claude Code 分析：Skills 实现](../../source/claude-code-analysis/analysis/04c-skills-implementation.md)
- [Hermes：Skill System](../../source/hermes-book/src/part3/ch08-skill-system.md)
- [claw0：Intelligence 与 Skill 发现](../../source/claw0/sessions/zh/s06_intelligence.md)
- [claw0：示例 Skill](../../source/claw0/workspace/skills/example-skill/SKILL.md)
- [easy-langent：Skills 与动态工具暴露](../../source/easy-langent/docs/tmp/chapter9.md)
- [hello-agents：Agent Skills 解读](../../source/hello-agents/Extra-Chapter/Extra05-AgentSkills解读.md)
- [hello-agents：如何写出好的 Skill](../../source/hello-agents/Extra-Chapter/Extra08-如何写出好的Skill.md)
- [hello-agents：Agent 自进化](../../source/hello-agents/Extra-Chapter/Extra10-Agent自进化.md)
- [hello-claw：技能开发与插件生命周期](../../source/hello-claw/docs/cn/appendix/appendix-d.md)
- [深入理解 AI Agent：第 2 章 Agent Skills 与渐进式披露](../../source/ai-agent-book/book/chapter2.md)

### 官方规范入口

- [Agent Skills 官方格式规范](https://agentskills.io/specification)
