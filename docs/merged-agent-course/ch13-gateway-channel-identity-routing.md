# 第 13 章：Gateway、多渠道、身份与路由

> 本章目标：理解 Gateway 不是“给 Agent 接几个聊天平台”的薄转发层，而是常驻 Agent 的入口控制面。读完本章，你应该能够设计统一消息信封、Channel Adapter、身份解析、session key、租户与 Agent 路由，解释它们之间不能合并的职责，并用边缘鉴权、最小信任和隔离测试防止串线与越权。

## 13.1 学习目标与边界

本章回答一条外部消息进入系统时的五个问题：

1. 这是什么平台事件，是否真实、完整且未被重复接收？
2. 平台声称的发送者是谁，系统把他解析成哪个规范身份？
3. 这次交互属于哪个租户、账号、会话和线程？
4. 应由哪个 Agent、工作区、模型策略和权限域处理？
5. 回复如何转换成目标渠道支持的表达形式？

本章只讨论入口、身份、会话边界与路由。后台任务、Cron、heartbeat、投递重试和运行时恢复属于[第 14 章](ch14-background-cron-delivery-resilience.md)。长期目标闭环与停止治理属于[第 15 章](ch15-loop-engineering.md)。这个边界很重要：Gateway 决定“请求去哪里”，后台运行时决定“任务如何可靠跑完”，Loop Engineering 决定“为什么继续以及何时停止”。

## 13.2 核心机制：从平台事件到可信请求

CLI、Web、Telegram、Slack、飞书和邮件的事件结构不同：发送者字段、群聊模型、线程、附件、引用、编辑和回执语义都不一样。如果核心 Agent 直接依赖平台 SDK，平台差异会渗入 Prompt、会话和工具层，新增一个渠道就会复制一套业务逻辑。

Gateway 的第一项工作是把平台事件规范化为稳定的消息信封：

```text
Platform Event
  -> Edge Authentication
  -> Channel Adapter
  -> Canonical Envelope
  -> Identity Resolver
  -> Tenant / Agent Router
  -> Session Resolver
  -> Agent Runtime
```

这里的顺序不是装饰。未经验证的事件不能先参与身份关联或路由；否则攻击者可以伪造发送者、租户或 session key，把不可信输入送入高权限 Agent。

## 13.3 统一消息信封：保留语义，不保留平台耦合

一个可迁移的入站信封至少包含：

```python
@dataclass(frozen=True)
class InboundEnvelope:
    event_id: str
    channel: str
    account_id: str
    conversation_id: str
    conversation_type: str       # dm | group | channel
    sender_principal: str        # 平台内已验证主体
    thread_id: str | None
    text: str
    attachments: tuple[Attachment, ...]
    mentions: tuple[str, ...]
    reply_to: str | None
    occurred_at: datetime
    received_at: datetime
    trust: TrustContext
    raw_ref: str                 # 原事件的受控引用，而非任意透传
```

关键设计点有四个：

- `event_id` 用于入口去重，不应由消息文本拼接而成。
- `account_id` 表示接收消息的 bot 或应用账号，同一渠道多账号时不能省略。
- `conversation_id` 与 `sender_principal` 分离，因为“谁发的”和“在哪说的”不是同一维度。
- `trust` 记录签名、连接、配对或 allowlist 的验证结果，不能让 Adapter 只返回一个模糊的 `authenticated=True`。

统一不等于丢失。平台独有能力可以进入受版本控制的 `capabilities` 或受限扩展字段，但核心路由不能依赖任意 `raw_event` 深层字段。否则“统一信封”只是多套平台结构外面包了一层字典。

出站同样需要规范化：

```text
OutboundMessage = content + target + reply/thread intent + media + interaction intent
```

Adapter 再根据渠道能力渲染：支持卡片的渠道生成卡片，只支持文本的渠道降级为文本。Agent 表达“需要确认”，而不是直接生成某个平台按钮 JSON。

## 13.4 Channel Adapter：把差异留在边缘

Channel Adapter 的职责包括：

- 验证 webhook 签名、连接身份、时间窗与重放条件。
- 解析事件并生成规范信封。
- 规范化文本、引用、附件、mention、线程与编辑事件。
- 把统一回复渲染为平台格式。
- 暴露渠道能力与限制，例如长度、附件大小、按钮和流式输出。
- 把平台错误翻译成运行时可判断的错误类别。

它不负责：

- 选择业务 Agent。
- 决定跨平台是否共享长期身份和上下文。
- 读取 Agent 记忆来猜测发送者。
- 在 Adapter 内直接运行 Agent Loop。
- 把平台管理员身份自动提升为 Agent 工具权限。

最后一点尤其容易出错。渠道角色只说明平台内的关系，不自动等价于操作系统、数据库或部署权限。

## 13.5 身份解析：平台主体、规范身份和授权主体

“用户是谁”至少有三层含义：

| 层次 | 示例 | 用途 |
| --- | --- | --- |
| 平台主体 | `telegram:123`、`slack:U456` | 验证事件来源 |
| 规范身份 | `person:alice`、`service:ci` | 跨渠道关联与偏好 |
| 授权主体 | `tenant:t1/member:m9/role:operator` | 权限和审计 |

身份解析可以表示为：

```text
(channel, account_id, verified_platform_principal)
  -> Identity Link Lookup
  -> canonical_identity
  -> tenant_membership + roles
```

`identityLinks` 一类机制只应该关联已经通过所有权证明或管理员确认的平台身份。显示名、头像、邮箱文本或模型推断都不能作为强关联依据。错误合并会把两个人的记忆、权限和私聊上下文混在一起；错误拆分通常只造成体验割裂，风险明显更低。因此系统无法确认时应默认不合并。

身份关联也不等于会话合并。系统可以知道 Telegram 和 Slack 上是同一个人，却仍因工作/私人租户不同而使用不同 session。规范身份回答“是不是同一个主体”，session key 回答“这次应接续哪段工作现场”。

## 13.6 Session Key：上下文隔离协议

Session key 不是缓存 key，而是上下文、顺序和并发隔离协议。一个稳妥的构造通常包含：

```text
session_key = hash(
  tenant_id,
  agent_id,
  channel,
  account_id,
  scope,
  conversation_id,
  thread_id?,
  canonical_identity?
)
```

不同产品会选择不同 `scope`：

| scope | 语义 | 主要风险 |
| --- | --- | --- |
| shared/main | 多个入口共享主会话 | 多用户串线，通常只适合单用户 |
| per-peer | 每个规范身份一段私聊 | 跨渠道意外合并 |
| per-channel-peer | 每个平台每人一段私聊 | 隔离稳妥，但体验不连续 |
| per-account-channel-peer | bot 账号×平台×用户隔离 | 多账号场景最安全，key 更长 |
| per-conversation | 群或频道共享现场 | 群成员可看到共同上下文 |
| per-thread | 每个线程独立现场 | 线程关闭、迁移与过期需要治理 |

群聊不能简单把 `sender_id` 塞进 key。共享群会话与“群内每人私有会话”是两种产品语义。前者需要 mention 门控、群成员变化和敏感记忆隔离；后者则可能让 Agent 的回复缺少群聊共同上下文。

Session key 必须在可信字段上由服务端生成。禁止外部请求自由指定完整 key；确需接受 hook 提供的 key 时，应限制前缀、租户和可访问 Agent，并记录调用主体。

## 13.7 路由：先租户，再 Agent，最后会话

路由建议分为三个明确阶段：

```text
1. Tenant Resolution
   verified endpoint/account -> tenant_id

2. Agent Binding
   tenant + channel + account + conversation + principal -> agent_id

3. Session Resolution
   tenant + agent + scope + conversation/principal/thread -> session_key
```

顺序错误会产生隐蔽越权。例如先按用户声明的 `agent_id` 读取 Agent 配置，再检查租户，可能在拒绝请求前已经泄露模型、工具或工作区元数据。

绑定表可以采用“最具体匹配优先”：

```python
def resolve_agent(ctx: RouteContext, bindings: list[Binding]) -> str:
    candidates = [b for b in bindings if b.matches(ctx)]
    candidates.sort(key=lambda b: b.specificity, reverse=True)
    if not candidates:
        return tenant_default_agent(ctx.tenant_id)
    if len(candidates) > 1 and candidates[0].specificity == candidates[1].specificity:
        raise AmbiguousRoute(candidates[:2])
    return candidates[0].agent_id
```

生产系统不能依赖“配置顺序刚好正确”。规则应有显式优先级、冲突检测和可解释结果。每次路由至少留下 `tenant_id`、`agent_id`、`session_key_hash`、命中规则和决策版本，便于追查串线。

## 13.8 多租户与多 Agent：隔离不仅在 Prompt 里

多租户隔离需要贯穿：

- 身份目录和绑定表。
- session、记忆、附件与检索索引。
- Agent 工作区、工具凭证和模型预算。
- 日志、指标、缓存和审计导出。
- 限流、并发配额和错误返回。

`tenant_id` 只出现在 system prompt 并不构成隔离。所有存储查询都必须带租户分区，服务端授权必须在读取资源前完成。高风险或互不信任的操作者不应仅靠同一 Gateway 内的逻辑标签隔离；应拆分进程、凭证、主机或网络边界。

多 Agent 路由也不能只看“哪个 Agent 更懂”。Agent 身后绑定了不同工作区、工具、数据权限和成本策略。路由本质上是能力与信任域选择，语义匹配只是其中一个信号。

## 13.9 Gateway 是边缘信任边界

Gateway 靠近公网、聊天平台和用户设备，必须把不可信输入转成带证据的内部请求。入口控制至少包括：

- webhook 签名、时间戳和 nonce/事件去重。
- 长连接或 API 客户端的双向认证与密钥轮换。
- DM pairing、allowlist、群聊 mention 或命令门控。
- 请求体、文本、附件数量与大小限制。
- URL、MIME、文件名与媒体处理的安全检查。
- 每主体、每租户、每账号的速率和并发限制。
- 日志脱敏，禁止记录原始 token、cookie 和私密附件。
- 明确的信任降级：验证失败直接拒绝，不交给模型判断。

Prompt injection 是内容层攻击，伪造身份和跨租户路由是控制面攻击。二者不能只靠同一条系统提示防御。

## 13.10 最小实现

最小 Gateway 不需要支持十个平台，但需要从第一天保持边界完整：

```python
def handle(raw_event: bytes, endpoint: Endpoint) -> Receipt:
    trust = endpoint.adapter.authenticate(raw_event, endpoint.credentials)
    envelope = endpoint.adapter.normalize(raw_event, trust)
    dedupe.claim(envelope.channel, envelope.account_id, envelope.event_id)

    tenant = tenant_resolver.resolve(endpoint, envelope)
    principal = identity_resolver.resolve(tenant, envelope.sender_principal)
    agent = binding_table.resolve(tenant, envelope, principal)
    session = session_resolver.resolve(tenant, agent, envelope, principal)

    policy.authorize_ingress(tenant, principal, agent, envelope)
    audit.record_route(envelope, tenant, principal, agent, session)
    return runtime.submit(agent, session, envelope)
```

建议按以下顺序实现：

1. 一个真实渠道加一个本地测试渠道。
2. 不可变统一信封与 Adapter contract tests。
3. 服务端 tenant、Agent 和 session 解析。
4. 入口去重、allowlist 与明确拒绝路径。
5. 路由解释日志和跨租户隔离测试。
6. 渠道能力协商与出站降级。

Cron 和后台 worker 此时都不是 Gateway 最小实现的一部分。

## 13.11 生产约束

生产 Gateway 还需要面对：

- **事件演化**：平台会增加事件类型和字段，Adapter 要版本化并容忍未知字段。
- **顺序不保证**：编辑、删除和消息事件可能乱序到达，不能把接收顺序当业务顺序。
- **重复接收**：平台重试 webhook 是正常现象，入口去重必须持久且有合理保留期。
- **能力差异**：长度、富文本、附件和线程能力要协商，不能静默截断关键内容。
- **隐私驻留**：原始事件、附件和身份链接的存储位置与保留期必须受策略控制。
- **配置变更**：绑定规则和身份链接要有版本、审计、预演和回滚。
- **可用性边界**：Gateway 可以快速确认“已接收”，但不能把“已接收”冒充“Agent 已完成”。

## 13.12 常见失败模式

| 失败 | 表现 | 根因 | 修复方向 |
| --- | --- | --- | --- |
| Adapter 直连 Agent | 渠道逻辑散落在 Prompt 与工具中 | 没有规范信封 | 建立稳定边界与 contract tests |
| 信任客户端 session key | 可读取或污染他人上下文 | 把标识符当授权 | 服务端生成并限制 hook 前缀 |
| 按显示名合并身份 | 两个用户记忆混合 | 弱证据关联 | 仅用已验证主体建立链接 |
| 身份合并即会话合并 | 工作和私人上下文串线 | 混淆 identity 与 scope | 独立设计 session policy |
| 默认规则吞掉具体规则 | 消息进入错误 Agent | 路由优先级隐式 | 最具体匹配、冲突即失败 |
| 只在 Prompt 中写 tenant | 数据仍可跨租户读取 | 缺少存储与凭证隔离 | 每层强制 tenant partition |
| 平台管理员自动高权限 | 群管理员触发主机工具 | 混淆渠道角色与授权角色 | 单独映射和审批 |
| 原样保存 raw event | 日志泄露 token 和私密内容 | 可观测性无数据治理 | 受控引用、脱敏与保留期 |

## 13.13 测试与验收

### Adapter 契约测试

- 同一语义的不同平台事件生成等价规范字段。
- 未知事件安全忽略或隔离，不触发 Agent。
- 签名错误、过期时间戳和重放事件被拒绝。
- 富内容降级不丢失确认、引用和附件风险提示。

### 身份与会话测试

- 同一平台两个用户绝不共享私聊 session。
- 同一用户跨平台是否合并严格服从 `dmScope` 与已验证 identity link。
- 同一平台两个 bot 账号按 `account_id` 隔离。
- 群、线程、私聊和重置后的 key 符合产品语义。

### 路由与租户测试

- 用表驱动测试覆盖默认、具体、冲突和无匹配规则。
- 对每个存储接口执行跨租户负向测试。
- 随机生成 channel/account/conversation/principal 组合，检查 key 无碰撞和规则确定性。
- 变更绑定表前运行影子路由，比较新旧决策但不真正执行。

验收不是“两个渠道都能聊天”，而是任何输入都能解释其认证、身份、租户、Agent 和 session 决策，且负向隔离测试持续通过。

## 13.14 系统地图

```text
External Platform / Web / CLI
  -> Edge Auth + Replay Defense
  -> Channel Adapter
  -> Canonical Inbound Envelope
  -> Tenant Resolver
  -> Identity Resolver
  -> Binding Table / Agent Router
  -> Session Policy + Session Key
  -> Ingress Authorization
  -> Agent Harness
  -> Canonical Outbound Message
  -> Capability-aware Channel Rendering

Cross-cutting:
  Dedupe | Rate Limit | Audit | Privacy | Config Version | Isolation
```

## 13.15 共同结论

1. Gateway 是入口控制面，不只是消息转发器。
2. Adapter 统一平台语义，Identity Resolver 统一主体，Session Resolver 隔离工作现场，Router 选择能力与信任域；四者不能混成一个函数。
3. 规范身份可以跨平台关联，但 session 是否合并必须由独立策略决定。
4. Session key 同时决定上下文、顺序与并发边界，必须由服务端基于可信字段生成。
5. 多租户隔离要落到存储、凭证、工作区和审计，不能只写在 Prompt 中。
6. Gateway 应在边缘拒绝伪造身份、重放和超限输入，不能把控制面安全交给模型判断。

## 13.16 本章自检

1. Channel Adapter、Identity Resolver、Agent Router 和 Session Resolver 分别负责什么？
2. 为什么 `identityLinks` 不应自动导致跨平台共享会话？
3. `account_id` 在同一平台多 bot 场景中为什么不可省略？
4. 群聊按 conversation 建 key 与按 sender 建 key 各自表达什么产品语义？
5. 为什么 session key 是上下文、数据与并发隔离边界，却不能替代独立授权？
6. 如何证明一条消息没有被路由到错误租户或错误 Agent？
7. 为什么 Gateway 已接收不等于任务已完成？

## 13.17 开放性问题

1. 跨平台规范身份应由用户自证、管理员关联还是风险模型建议？撤销链接后历史记忆如何处理？
2. 一个用户同时属于个人租户与企业租户时，哪些偏好可以共享，哪些必须物理隔离？
3. 群聊 Agent 应维护共享 session、每人 session，还是两层 session？如何避免敏感信息在层间泄漏？
4. 当语义路由模型与显式绑定规则冲突时，谁拥有最终决定权，如何向用户解释？
5. 路由配置热更新期间，已经排队但尚未执行的消息应使用旧版本还是新版本？
6. 端到端加密渠道中，Gateway 无法读取正文时，身份、路由和审核应如何设计？
7. 对互不信任的客户，逻辑多租户何时足够，何时必须拆分 Gateway、主机和凭证？
8. 渠道能力降级导致交互确认丢失时，系统应该拒绝发送、转为文本确认还是切换渠道？

## 13.18 原文入口

### 本地教程与实现

- [claw0：会话](../../source/claw0/sessions/zh/s03_sessions.md)
- [claw0：通道](../../source/claw0/sessions/zh/s04_channels.md)
- [claw0：网关与路由](../../source/claw0/sessions/zh/s05_gateway_routing.md)
- [claw0：通道最小实现](../../source/claw0/sessions/zh/s04_channels.py)
- [claw0：网关路由最小实现](../../source/claw0/sessions/zh/s05_gateway_routing.py)
- [Hermes：一次请求的旅程](../../source/hermes-book/src/part2/ch03-request-journey.md)
- [Hermes：Gateway](../../source/hermes-book/src/part5/ch14-gateway.md)
- [hello-claw：架构总览中的消息循环与统一网关](../../source/hello-claw/docs/cn/build/chapter1/index.md)
- [hello-claw：统一网关](../../source/hello-claw/docs/cn/build/chapter6/index.md)
- [hello-claw：安全沙箱与入口信任边界](../../source/hello-claw/docs/cn/build/chapter7/index.md)
- [hello-claw：配置中的 dmScope、identityLinks 与 bindings](../../source/hello-claw/docs/cn/appendix/appendix-g.md)

### 延伸标准

- [CloudEvents 规范](https://cloudevents.io/)
- [OWASP Webhook Security Guidelines](https://owasp.org/www-community/attacks/Webhook_Security_Guidelines)
