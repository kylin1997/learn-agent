# 第 9 章：权限、安全、沙箱与隐私治理

> Agent 安全的目标不是让模型“表现得谨慎”，而是让一次不可靠的推理即使面对恶意输入，也只能在被授权、可隔离、可审计、可撤销的边界内行动。

## 9.1 学习目标与边界

学完本章，你应该能够：

1. 从资产、主体、信任域和数据流出发建立 Agent 威胁模型。
2. 设计由 Policy、权限规则、风险判断、用户审批和执行约束组成的决策管线。
3. 区分 Prompt 约束、应用层权限和系统层沙箱的安全强度。
4. 处理间接 Prompt Injection、命令注入、路径逃逸和多阶段攻击。
5. 治理 Skill、插件、依赖和外部工具形成的供应链风险。
6. 追踪数据进入模型、日志、记忆、外部服务和同步系统的完整路径。
7. 用对抗测试和不可绕过的不变式验收安全系统。

本章讨论的是 Agent Harness 的治理面，不展开某个产品的配置命令，也不把加密、容器或审批中的任何一种机制描述成万能方案。MCP 等互操作协议的协议机制放在第 11 章；本章只讨论它们跨越信任边界时必须接受的统一治理。

## 9.2 为什么 Agent 改变了安全问题

普通对话系统主要产生文本；Agent 会把文本变成动作。一次模型输出可能继续触发文件读写、命令执行、网络访问、消息发送、数据库修改和下一轮模型调用。风险因此不只取决于“模型说了什么”，还取决于：

```text
风险 = 能力 × 权限 × 可达资产 × 自主时长 × 不可逆性
```

这不是精确的数学公式，而是一种建模提醒：同一个误判，在只读临时目录里可能只是噪声，在持有生产凭证且无人值守的 Agent 中则可能成为事故。

安全工程首先要保护四类资产：

| 资产 | 例子 | 主要后果 |
| --- | --- | --- |
| 机密性资产 | API Key、聊天记录、客户数据、长期记忆 | 泄露、越权使用、隐私侵害 |
| 完整性资产 | 源码、配置、数据库、审计记录 | 篡改、后门、错误决策 |
| 可用性资产 | 计算配额、外部服务、任务队列 | 资源耗尽、拒绝服务、任务阻塞 |
| 权威性资产 | 发信身份、发布权限、支付与部署凭证 | 冒名、错误承诺、真实世界损失 |

由此得到第一条原则：**安全边界必须围绕真实资产和真实副作用建立，不能围绕模型的语气建立。**

## 9.3 信任边界：谁能影响谁

### 9.3.1 主体、信任域与入口

一个典型 Agent 至少包含以下主体：用户、模型、Harness、内置工具、Skill/插件、外部服务、操作系统以及数据存储。它们不属于同一信任域。

```text
用户意图域
  -> Harness 控制域
      -> 模型推理域（概率性、不完全可信）
      -> 扩展域（Skill、插件、外部服务）
      -> 执行域（文件、进程、网络、凭证）
      -> 数据域（会话、记忆、日志、遥测）
```

信任边界不是“内网/外网”的同义词。项目仓库中的 README、网页正文、Issue 评论、工具返回值、模型生成的命令，甚至已安装 Skill 的正文，都可能携带攻击性指令。来源在本机，不代表内容可信；由模型生成，也不代表动作已获授权。

### 9.3.2 指令、数据与能力必须分离

安全设计要区分三种东西：

- **指令**：谁有权定义目标和约束。
- **数据**：为完成目标而读取的材料，只能作为证据。
- **能力**：系统实际允许执行的动作集合。

Prompt 可以帮助模型识别这三者，却不能强制它们分离。真正的分离发生在 Harness 中：外部内容带来源标签；模型输出必须转成结构化调用；每次调用重新授权；执行器只能获得本次动作需要的能力。

### 9.3.3 建立最小威胁模型

可以用下面六问快速建立威胁模型：

1. **保护什么**：密钥、文件、身份、资金还是服务可用性？
2. **谁能输入**：用户、网页作者、仓库贡献者、插件发布者、远端 Agent？
3. **输入能走多远**：只能影响回答，还是能触达 Shell、网络和生产 API？
4. **哪里发生提权**：文本何时变成工具参数，临时授权何时变成持久规则？
5. **失败如何扩散**：一个子进程、一个插件或一个任务能否影响其他会话？
6. **如何发现和恢复**：是否有证据、停止开关、快照、补偿动作和密钥轮换？

没有威胁模型的“安全功能清单”容易堆出很多按钮，却漏掉真正的攻击路径。

对 Coding Agent 和 Computer Use Agent，还可以用一条更尖锐的检查：系统是否同时具备**访问私有数据、接收不可信内容、向外部通信或执行副作用**三项能力。三者闭合时，间接 Prompt Injection 就拥有从进入、取数到外传或破坏的完整路径。长期记忆不是必需的第四项，但会把一次攻击放大为跨会话潜伏。工程上的重点不是幻想识别所有恶意文本，而是切断能力链：敏感数据不可见、网络默认受限、每个副作用重新授权、记忆写入独立审查。

## 9.4 Prompt 不是硬安全边界

Prompt 很重要，但它属于行为引导：可以声明外部内容不可信、提醒模型不要泄露密钥、要求危险动作前确认。它不能保证模型始终遵守，也不能阻止被攻陷的工具或插件绕过模型直接产生副作用。

可以按强度把控制分成四层：

| 层 | 作用 | 是否确定性强制 |
| --- | --- | --- |
| Prompt/Skill | 引导模型判断、规划和解释 | 否 |
| Policy/权限引擎 | 根据主体、动作、资源和上下文裁决 | 是，前提是所有调用都经过它 |
| 工具实现 | 参数校验、幂等、限额、乐观锁 | 是，限于工具自身 |
| 沙箱/操作系统 | 限制文件、网络、进程、系统调用和凭证 | 是，限于正确配置的边界 |

Prompt 的正确位置是纵深防御中的一层，而不是最底层。应坚持一个测试：**即使模型完全不配合，硬边界是否仍然成立？**

## 9.5 从 Policy 到执行的权限管线

### 9.5.1 Policy 是机器可执行的治理契约

Policy 不只是 allow/deny 列表。它应回答：哪个主体，在什么会话和项目中，能对哪个资源执行什么动作，在什么条件下，需要什么义务。

可以抽象为：

```text
decision = Policy(
  subject, action, resource, context,
  tool_claims, data_classification, user_intent
)

decision ∈ {allow, deny, ask, allow_with_obligations}
```

`obligations` 可包含：必须使用沙箱、只允许特定路径、结果必须脱敏、执行前生成 diff、执行后验证、记录审计、在截止时间后撤销授权等。这样，Policy 不只决定“能不能”，还决定“怎样做才可以”。

### 9.5.2 一条稳健的决策链

```text
工具提案
  -> 身份与会话绑定
  -> Schema/类型/大小校验
  -> 参数规范化与语义解析
  -> 生成不可变 CanonicalCall / Action
  -> 不可覆盖的静态 deny
  -> 组织/用户/项目 Policy 合并
  -> 当前权限模式
  -> 风险与数据分类
  -> approval 或自动裁决
  -> 生成最小执行能力
  -> 沙箱内执行
  -> 输出清洗、审计与状态更新
```

顺序很重要。未经规范化的路径不能参与规则匹配；宽泛 allow 不能遮蔽更强的 deny；审批不能发生在用户看不到真实参数的时候；执行后产生的新数据还要再次经过隐私和输出治理。

规范化不能只生成一份“供检查参考”的副本。系统必须把校验后的工具名、规范化参数、真实资源标识、效果集合和数据流固化为不可变 `CanonicalCall / Action`，权限匹配、审批摘要、能力签发、审计和最终执行都引用同一个对象。原始 `raw_call` 在规范化后只能作为受限取证材料保存，**绝不能再次进入执行器**，否则会形成“检查 A、执行 B”的解析差异漏洞。

### 9.5.3 规则层级与合并

常见来源包括内置安全底线、组织 Policy、用户全局规则、项目规则、会话授权和单次确认。更高的业务优先级不应自动拥有更高的安全优先级。建议使用以下合并原则：

1. 不可覆盖的 deny 最先裁决。
2. 其余规则按明确的作用域和优先级求值。
3. 多条规则冲突时选择更窄作用域或更保守结果。
4. 临时授权带资源、参数、次数和过期时间，不升级为无限授权。
5. 每个结果保存命中规则、输入摘要和决策原因。

规则引擎还要检测遮蔽：例如 `allow Bash(*)` 会让后续 `deny Bash(git push --force *)` 失效。能写入配置不等于配置有效，危险的宽泛规则应被拒绝或降级为每次询问。

### 9.5.4 路径和命令不是普通字符串

对 `../` 做文本搜索远远不够。路径授权至少要处理规范化、符号链接、挂载点、大小写差异、UNC 路径和检查后替换（TOCTOU）。执行器应尽可能使用已打开的文件句柄或目录能力，避免“检查的是 A，执行时变成 B”。

Shell 命令还包含管道、重定向、子命令、解释器和环境变量展开。一个允许的前缀可能携带任意代码，因此应优先提供结构化专用工具；确需 Shell 时，先解析命令段，再逐段应用规则和沙箱，而不是把整条字符串当成一个动作。

## 9.6 Approval：责任移交，而不是免检通行证

审批适合处理“系统无法独自承担的风险判断”，不适合替代基本安全。一个好的审批请求应让用户知道：

- 将执行什么动作以及完整目标资源。
- 为什么需要它，与当前目标有什么关系。
- 会读取、修改或外发哪些数据。
- 动作是否可逆，影响范围多大。
- 授权只限本次、此会话，还是某个窄规则。

审批决策应绑定规范化后的动作摘要。参数变化、工具变化、目标域变化或数据敏感级别上升后必须重新审批，不能复用旧同意。

以下做法会制造“同意疲劳”：每个低风险读取都询问、把十个不同动作合成一句“允许继续”、默认选中永久授权、用抽象工具名隐藏真实副作用。审批越频繁不一定越安全；当用户无法有效区分风险时，它只是把责任推给用户。

审批之后仍要执行不可覆盖 deny、沙箱、数据最小化和审计。用户可以同意删除项目构建产物，但不应通过一次弹窗让进程获得整个主目录的写权限。审批表达的是用户意图和责任移交，不能替代系统调用、文件、网络、进程或凭证的硬隔离；如果某动作按 Policy 必须在沙箱中执行，用户同意也不能把它降级为宿主执行。

## 9.7 风险分类器的正确位置

LLM 分类器能理解“清理缓存”和“删除用户数据”的语义差别，适合处理规则未覆盖的灰区。但它仍是概率组件，只能做辅助裁决。

一些 SDK 把这类检查称为 `Agent Guardrail`，并允许检查失败时触发异常或 tripwire。需要区分两层：**运行时强制中断**可以是确定性的，但“是否应该触发”如果由另一个模型判断，结论仍是概率性信号。Grounding Agent、Critic Agent 或风险 Agent 都可能误放行、误拒绝，也可能与被检查 Agent 共享相同盲点。

因此，Agent Guardrail 适合发现语义风险、证据不足、内容偏题和需要人工复核的灰区，不适合替代 Schema 校验、ACL、不可覆盖 deny、参数规范化、配额和沙箱。高风险动作即使通过 Agent Guardrail，也必须继续经过硬边界；Guardrail 超时、解析失败或多个检查器结论冲突时，应按策略转为 `ask` 或 `deny`，不能把“检查器没有返回失败”解释为安全证明。

推荐管线：

```text
确定性安全白名单 -> 直接允许
确定性危险规则   -> 拒绝或询问
语义不明确       -> 快速分类器
高影响且不确定   -> 强分类器 + 人工审批
超时/解析失败    -> fail closed
```

分类器输入应包含规范化后的工具、参数、当前目标、可达资源和最近拒绝，而不是只看一条命令。输出要使用严格枚举和理由码；解析失败、模型不可用或结果矛盾时，降级为 `ask` 或 `deny`。

还要记录拒绝。若用户已拒绝某动作，Agent 不应换一种措辞反复尝试等价操作。拒绝记录要参与后续规划和权限裁决，但不应泄露进不可信的外部上下文。

## 9.8 沙箱：把授权变成最小可执行能力

### 9.8.1 应用权限与系统沙箱分工

权限引擎理解语义：“这次写入是否符合用户意图？”沙箱限制可能性：“即使获准执行，这个进程最多能碰到什么？”

```text
Policy: 允许格式化当前项目的 src/ 目录
Sandbox:
  read  = workspace
  write = workspace/src + temp
  net   = deny
  env   = 仅格式化器必要变量
  proc  = 仅指定二进制，带超时和资源上限
```

二者缺一不可。只做权限判断，命令内部仍可能越界；只做沙箱，Agent 仍可能在边界内删除所有允许写入的数据。

### 9.8.2 沙箱的控制面

生产沙箱至少要覆盖：

- 文件系统可读/可写目录与只读挂载。
- 网络默认策略、域名/IP/端口和 DNS 约束。
- 进程、子进程、系统调用、CPU、内存、磁盘和时间限额。
- 环境变量、凭证注入和敏感文件可见性。
- IPC、设备、剪贴板、浏览器会话和宿主服务访问。
- 执行结束后的临时资源清理与结果提取。

凭证应按调用临时注入，绑定受众和最小 scope，不能把宿主完整环境复制进沙箱。网络 allowlist 也要防 DNS 重绑定、重定向和代理绕过。

### 9.8.3 沙箱失败时怎么办

系统必须可证明沙箱真的启用。依赖缺失、策略编译失败或平台不支持时，不能悄悄退化为宿主执行。默认行为应是拒绝；只有 Policy 预先允许，而且动作同时满足**低风险、无外发、数据源与数据汇均不含敏感数据、效果可逆、也不依赖硬隔离不变式**时，才能进入受限的无沙箱执行器。降级必须被显式记录和提示，但再次审批本身不能让不满足这些条件的动作通过。

例如，本地读取公开的项目元数据可能允许按策略降级；读取凭证、联网、向第三方发送内容、运行任意解释器、不可逆写入或任何声明 `sandbox_required` 的动作都必须 fail closed。这里的判断基于规范化后的完整效果集合和数据流，不能只看工具显示名称。

沙箱也不是绝对隔离。内核漏洞、错误挂载、过宽 IPC 和宿主侧后处理都可能形成逃逸路径。多阶段攻击尤其值得注意：攻击者先在沙箱可写区植入配置或仓库钩子，之后由宿主上的可信程序触发。执行后清理、宿主工具隔离和跨边界文件格式验证同样属于沙箱设计。

## 9.9 Prompt Injection：把内容攻击阻断在动作边界

### 9.9.1 直接与间接注入

直接注入来自用户输入；间接注入藏在网页、邮件、代码注释、文档、图片 OCR、工具描述或工具返回值中。后者更危险，因为用户常以为自己只是“让 Agent 总结资料”。

攻击链通常是：

```text
不可信内容
  -> 被放入模型上下文
  -> 冒充高优先级指令
  -> 诱导模型选择高权限工具
  -> 读取秘密或产生外部副作用
```

只清洗“忽略之前指令”这样的关键词无法解决问题。攻击可以改写语言、编码或结构，模型也可能主动推断出同样的恶意动作。

### 9.9.2 纵深防御

1. **来源标注**：结构化区分系统指令、用户委托和外部证据。
2. **边界清洗**：Unicode 规范化、移除不可见控制字符、递归处理嵌套结果。
3. **上下文最小化**：只取完成任务需要的片段，限制描述和结果大小。
4. **能力隔离**：读取不可信内容的阶段不同时持有高危写入和外发能力。
5. **动作再授权**：任何副作用都根据用户原始意图重新判断，不接受内容中的“授权”。
6. **数据流控制**：秘密不能流入未授权输出、日志或第三方工具。
7. **结果验证**：检查最终 diff、收件人、目标域和实际副作用。

模型可以作为检测器提示可疑内容，但真正阻断发生在权限、能力和数据流边界。应把“模型已识别这是一条注入”视为有益信号，而不是安全证明。

## 9.10 供应链：能力扩展也是代码执行入口

Agent 的供应链不只包括 Python/npm 依赖，还包括 Skill、插件、MCP Server、模型、Prompt 模板、容器镜像、自动更新渠道和远端 Agent 描述。它们可能同时携带代码、指令、配置和凭证需求。

安装前至少验证：

- 来源身份、仓库和发布渠道是否可信。
- 包内容、manifest、签名或哈希是否一致。
- 版本是否固定，传递依赖和安装脚本是什么。
- 声明了哪些工具、Hook、网络访问、文件访问和凭证。
- 更新是否扩大权限或改变数据去向。

运行时要把扩展视为独立主体：授予单独的权限、资源配额和审计身份；不要继承宿主全部凭证。更新前重算权限差异，重大变更重新确认。支持禁用、隔离、回滚和撤销凭证，维护组件清单与来源证据。

最危险的组合是“自动发现 + 自动安装 + 自动启用 + 自动更新 + 高权限执行”。每一步单看都提高便利性，串联后却形成无人审查的远程代码路径。

## 9.11 隐私治理：追踪数据生命周期

### 9.11.1 数据不只进入模型

一次任务的数据可能流向：模型 API、会话 transcript、长期记忆、向量库、工具参数、外部服务、遥测、错误转储、团队同步、远程控制和备份。隐私治理不能只写“是否训练模型”，而要为每条流回答：

```text
收集什么 -> 为什么需要 -> 发给谁 -> 保存多久
谁能访问 -> 如何删除 -> 是否跨境/跨租户 -> 失败时是否泄漏
```

### 9.11.2 数据分类与最小化

可以把数据分为公开、内部、机密、受监管四级，并将分类结果带入权限管线。最小化包括：

- 只发送任务所需字段，不上传整个仓库或整段会话。
- 在进入模型、日志和遥测前分别脱敏，不能只在 UI 隐藏。
- 默认不把 `.env`、SSH Key、凭证目录和生产数据加入上下文。
- 记忆写入前判断必要性、敏感度、保留期和可删除性。
- 外发结果使用 Outbox 或预览，检查收件人和附件。

Secret scanner 是最后一道检测，不是读取秘密的许可证。扫描器也会漏报；最可靠的做法仍是让秘密尽量不进入通用上下文。

### 9.11.3 加密与密钥治理

静态数据和传输数据应加密，敏感字段可独立加密并带版本标记，便于轮换算法和迁移。密钥不应与密文放在相同保护域；解锁前禁止初始化流程用空值覆盖加密数据。

向量数据库还有特殊问题：加密文本不等于隐藏 embedding 中的语义泄漏。需要把索引本身纳入访问控制、租户隔离、删除和备份治理，而不是只加密原文。

### 9.11.4 用户权利与组织治理

用户应能查看、纠正和删除记忆，关闭非必要遥测，知道哪些连接器会收到数据。团队环境还需要租户隔离、角色授权、保留策略、法律依据、审计访问和事件响应。隐私设置必须约束真实数据路径，而不是只改变界面文案。

## 9.12 最小实现：一个可审计的安全内核

下面的伪代码刻意把模型放在裁决之外。模型提出动作，安全内核决定动作能否成为现实：

```python
from dataclasses import dataclass
from enum import Enum

class Effect(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    EXTERNAL = "external_side_effect"

@dataclass(frozen=True)
class CanonicalCall:
    tool: str
    args_canonical: bytes       # 确定性编码，执行器不再解析 raw_call
    args_digest: str

@dataclass(frozen=True)
class DataEndpoint:
    kind: str                   # file | memory | model | network | log ...
    locator: str
    classification: str        # public | internal | secret | regulated
    external: bool = False

@dataclass(frozen=True)
class Action:
    subject: str
    call: CanonicalCall
    effects: frozenset[Effect]  # 一个动作可以同时 READ + NETWORK + EXTERNAL
    resources: tuple[str, ...]
    data_sources: tuple[DataEndpoint, ...]
    data_sinks: tuple[DataEndpoint, ...]
    risk: str
    reversible: bool

@dataclass(frozen=True)
class Decision:
    result: str                 # allow | deny | ask
    reason: str
    obligations: tuple[str, ...]
    expires_at: float | None = None

def authorize(raw_call, session, policy) -> tuple[Action, Decision]:
    parsed = validate_schema(raw_call)
    action = normalize_freeze_and_classify(parsed, session)

    if violates_non_overridable_deny(action):
        return action, Decision("deny", "hard_deny", ())

    decision = policy.evaluate(action, session.user_intent)
    if decision.result == "allow" and action.effects != frozenset({Effect.READ}):
        decision = bind_obligations(
            decision,
            required=("sandbox", "audit", "post_verify"),
        )
    return action, decision

def can_degrade_without_sandbox(action, policy) -> bool:
    endpoints = action.data_sources + action.data_sinks
    return (
        policy.allows_unsandboxed_degrade(action)
        and action.risk == "low"
        and Effect.EXTERNAL not in action.effects
        and not any(endpoint.external for endpoint in action.data_sinks)
        and not any(
            endpoint.classification in {"secret", "regulated"}
            for endpoint in endpoints
        )
        and action.reversible
        and not policy.requires_hard_isolation(action)
    )

def select_executor(action, decision, sandbox, policy):
    if sandbox.available:
        return sandbox.bind(action)
    if "sandbox" in decision.obligations:
        raise RuntimeError("required sandbox unavailable")
    if not can_degrade_without_sandbox(action, policy):
        raise RuntimeError("unsafe unsandboxed degradation")
    return restricted_local_executor(action)

def execute(raw_call, session, policy):
    action, decision = authorize(raw_call, session, policy)
    if decision.result == "ask":
        decision = request_scoped_approval(action, decision)
    if decision.result != "allow":
        audit(action, decision, outcome="blocked")
        raise PermissionError(decision.reason)

    capability = mint_ephemeral_capability(action, decision)
    executor = select_executor(action, decision, session.sandbox, policy)
    result = executor.run(action.call, capability)  # 永远不执行 raw_call
    checked = redact_and_verify(result, action)
    audit(action, decision, outcome=checked.outcome)
    return checked.visible_result
```

显式的数据源和数据汇让 Policy 能识别复合副作用。例如“读取本地客户表后调用外部 API”不是一个简单的 `NETWORK` 动作，而是同时包含 `READ + NETWORK + EXTERNAL`，数据从机密文件源流向外部网络汇。只检查单一 `effect` 会漏掉这种跨边界组合。

第一版不需要复杂的 AI 分类器。先实现结构化工具、四态决策、静态 deny、作用域审批、文件与网络沙箱、审计、脱敏和紧急停止，通常比添加更多 Prompt 更有价值。

## 9.13 生产约束

1. **默认最小能力**：新工具、新扩展、新数据源默认不可达。
2. **完整中介**：不存在绕过权限内核的备用执行路径。
3. **租户隔离**：会话、记忆、缓存、凭证和审计都绑定租户与主体。
4. **短期凭证**：使用受众绑定、最小 scope、短有效期的临时凭证。
5. **幂等与补偿**：外部副作用使用幂等键；不可回滚动作提高审批级别。
6. **有界执行**：限制轮数、时间、成本、并发、输出和重试。
7. **可停止**：取消信号能穿透模型、工具、子进程和远端任务。
8. **审计防篡改**：日志记录决策与结果，但不记录完整秘密。
9. **策略版本化**：每次执行能追溯到具体 Policy 和扩展版本。
10. **变更再评估**：工具 schema、插件权限和模型行为变化后重跑安全验收。

安全相关不确定性应 fail closed；可恢复的网络或服务故障可以有界重试和降级。两者不能混为“出错就继续”。

## 9.14 典型失败模式

| 失败模式 | 根因 | 修正方向 |
| --- | --- | --- |
| Prompt 写了“不要泄密”便认为安全 | 把软约束当硬边界 | 在工具与数据出口强制授权和流控 |
| 审批后授予整个 Shell | 授权粒度过粗 | 绑定动作、参数、资源、次数和期限 |
| 沙箱不可用时经审批便宿主执行 | 把同意误当成硬隔离 | 仅低风险、无外发、无敏感且可逆动作可按 Policy 降级 |
| 路径规则只做字符串前缀 | 可被 `..`、符号链接和 TOCTOU 绕过 | 规范化并在执行时绑定真实对象 |
| MCP/插件来自“知名市场”就全信任 | 把分发渠道当代码证明 | 安装审计、签名/哈希、最小权限、运行隔离 |
| 工具结果直接拼进 system prompt | 不可信数据发生指令提权 | 来源标签、内容隔离、动作再授权 |
| 遥测脱敏但错误转储保留原文 | 只治理主路径 | 枚举所有数据出口并统一分类策略 |
| 用户拒绝后 Agent 换命令重试 | 没有语义拒绝记录 | 记录等价动作并反馈给规划器 |
| 自动更新不比较新增权限 | 版本升级隐式提权 | manifest diff、重新审批、可回滚发布 |

## 9.15 测试与验收

### 9.15.1 安全不变式

至少验证以下不变式：

- 任意模型输出都不能绕过权限入口直接执行。
- 明确 deny 在任何模式、Hook、Skill 和审批后仍然有效。
- 未批准的路径、网络域和凭证在进程内不可见。
- 外部内容不能自行扩大工具权限或改变数据分类。
- 沙箱未启用时，高风险动作不会落到宿主执行。
- 审计足以重建“谁在何时因何规则对何资源做了什么”。

### 9.15.2 测试矩阵

1. **规则测试**：精确、前缀、通配符、冲突、遮蔽和过期授权。
2. **路径测试**：`..`、符号链接、挂载点、UNC、大小写和 TOCTOU。
3. **命令测试**：管道、重定向、子 shell、解释器、编码和多命令组合。
4. **注入测试**：网页、工具描述、JSON 嵌套字段、Unicode 隐形字符和多轮诱导。
5. **沙箱测试**：文件、网络、进程、环境变量、资源耗尽和依赖缺失。
6. **隐私测试**：模型请求、日志、遥测、错误转储、记忆、备份和外发内容。
7. **供应链测试**：篡改包、依赖替换、权限升级更新、撤销和回滚。
8. **审批测试**：参数变更、重放、过期、批量动作和同意疲劳场景。
9. **故障测试**：超时、断连、部分成功、取消、重启和重复投递。

验收不能只看“恶意请求被拒绝”，还要检查正常任务是否能以窄权限完成。过度阻断会促使用户开启绕过模式，同样会削弱系统安全。

## 9.16 系统地图

```text
                         Governance Plane
 Asset Inventory -> Data Classification -> Policy -> Audit / Incident Response
                                            |
 User Goal -> Planner -> Tool Proposal -> Authorization Pipeline
                                            |
             +------------------------------+--------------------+
             | deny                         | ask                | allow
             v                              v                    v
       Replan / Stop                 Scoped Approval     Capability Minting
                                                                  |
 Untrusted Content -> Label / Sanitize / Minimize -> Sandboxed Executor
                                                                  |
      File / Network / Process / Credentials / External Side Effects
                                                                  |
                       Verify -> Redact -> Record -> Return

 Supply Chain: Skill / Plugin / MCP Server / Dependency / Model / Update Channel
   -> provenance -> manifest diff -> trust tier -> least privilege -> rollback
```

## 9.17 共同结论

1. Agent 安全的核心对象是从不可信输入到真实副作用的整条链路。
2. Prompt 能改善行为，但不是权限、数据流或执行隔离的硬边界。
3. Policy 负责语义裁决，approval 负责有限责任移交，sandbox 负责限制实际可能性。
4. 身份验证、权限授权、能力隔离和结果审计是不同机制，不能互相替代。
5. Prompt Injection 无法只靠内容过滤根治，必须在动作和数据出口重新授权。
6. Skill、插件和协议服务扩大能力的同时也扩大供应链与隐私边界。
7. 可停止、可验证、可追溯、可撤销，与“能完成任务”同属生产正确性。

## 9.18 本章自检

1. 为什么“模型已经答应不执行危险命令”不能构成安全证明？
2. Policy 的 `allow_with_obligations` 比简单 allow 多解决了什么问题？
3. approval 为什么必须绑定规范化后的动作与参数？
4. 应用层权限和系统层沙箱分别能阻止哪些攻击？
5. 为什么读取网页的阶段不应默认同时持有外发和密钥读取能力？
6. 如何判断一次插件更新是否构成权限升级？
7. 数据已从日志中脱敏，为什么仍不能断言隐私治理完成？
8. 哪些安全测试可以证明 fail closed，而不只是观察到一次拒绝？

## 9.19 开放性问题

1. 当用户明确要求永久关闭确认时，哪些风险可以由用户承担，哪些安全底线仍不应允许覆盖？
2. 如何给语义上等价但参数不同的危险动作建立稳定的拒绝指纹？
3. 在浏览器 Agent 中，登录态 Cookie 应由沙箱、工具代理还是独立凭证服务持有？
4. 当一个任务需要同时读取机密数据和调用外部模型时，怎样证明最小披露已经实现？
5. Agent 的长期记忆是否应支持“用途限制”，使同一事实只能用于特定类型任务？
6. 对不可逆的资金、发布和通知动作，什么样的双人审批或职责分离才足够？
7. 如何对 LLM 风险分类器做漂移监测，并避免模型升级悄悄改变安全基线？
8. 签名能证明插件来自谁，却不能证明插件没有恶意；来源可信和内容可信应如何组合评分？
9. 当沙箱允许写项目文件时，怎样防止植入配置后由宿主工具在未来触发的多阶段攻击？
10. 企业应保存多少审计上下文，才能兼顾事故调查、商业秘密和个人隐私？

## 9.20 原文入口

### 本地融合来源

- [learn-claude-code：Permission](../../source/learn-claude-code/s03_permission/README.md)
- [learn-claude-code：Hooks](../../source/learn-claude-code/s04_hooks/README.md)
- [Alice 方法论：权限系统](../../source/Alice_methodology/chapters/07-permission.md)
- [Alice 方法论：安全体系](../../source/Alice_methodology/chapters/12-security.md)
- [Harness Engineering：权限系统](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch16.md)
- [Harness Engineering：YOLO 分类器](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch17.md)
- [Harness Engineering：提示注入防御](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch17b.md)
- [Claude Code 分析：安全分析](../../source/claude-code-analysis/analysis/02-security-analysis.md)
- [Claude Code 分析：Sandbox 实现](../../source/claude-code-analysis/analysis/04e-sandbox-implementation.md)
- [Claude Code 分析：用户数据与使用](../../source/claude-code-analysis/analysis/02-user-data-and-usage.md)
- [Claude Code 分析：隐私规避](../../source/claude-code-analysis/analysis/03-privacy-avoidance.md)
- [Hermes：工具配置与执行审批](../../source/hermes-book/src/part3/ch07-tool-profiles.md)
- [claw0：工具使用与执行链](../../source/claw0/sessions/zh/s02_tool_use.md)
- [easy-langent：Agent 工作流与人工审批](../../source/easy-langent/docs/guide/chapter7.md)
- [hello-agents：上下文工程](../../source/hello-agents/docs/chapter9/第九章%20上下文工程.md)
- [hello-agents：Agent 应用开发实践](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)
- [hello-claw：安全实践](../../source/hello-claw/docs/cn/university/security/index.md)
- [AI Agents in Action 第 4 章：Agent Flow Guardrails](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/4.架构与构建多智能体系统.md)
- [AI Agents in Action 第 7 章：Grounding 与 Critic Guardrails](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/7.通过评估与反馈构建稳健的智能体.md)
- [深入理解 AI Agent：第 5 章 Coding Agent 的执行安全](../../source/ai-agent-book/book/chapter5.md)

### 协议与标准入口

- [MCP 官方架构：Host 负责安全策略与用户授权](https://modelcontextprotocol.io/specification/2025-11-25/architecture)
- [MCP 官方授权规范](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
