# 第 11 章：MCP、A2A、ANP 与 Agent 互操作

> 互操作协议不是把所有参与者变成同一种 Agent，而是让彼此不了解内部实现的系统，仍能发现能力、建立会话、交换任务与结果，并在失败和不信任存在时保持边界。

## 11.1 学习目标与边界

学完本章，你应该能够：

1. 区分 MCP、A2A、ANP 各自试图标准化的互操作边界。
2. 解释三种协议中的角色、描述对象、发现方式和调用生命周期。
3. 区分协议版本/能力协商、业务任务协商与开放网络服务协商。
4. 分别设计身份认证、权限授权、用户同意和跨主体互信。
5. 处理连接、重试、重复投递、长任务、描述漂移和发现污染。
6. 从版本、扩展、审计、撤销、责任和生态准入角度治理协议。
7. 设计一个能组合三类协议、又不混淆责任边界的互操作层。

本章不是产品配置手册，不讲如何点击安装某个 Server，也不把教学框架的包装类当作协议规范。协议仍在快速演进，字段和绑定以具体版本的官方规范为准；本章重点是可迁移的角色、状态、信任和治理方法。

本章的规范基线固定为 MCP `2025-11-25` 与 A2A `1.0.0`。ANP 官方文档按 `1.1` 发布线组织，但部分页面使用滚动 URL，且元协议仍是草案；本章记录的 ANP 页面访问日期为 **2026-07-17**。读者复现时应核对页面版本和变更记录，不能假设滚动链接长期保持本文语义。

## 11.2 互操作究竟在标准化什么

“Agent 通信”常把三类问题混在一起：

1. **能力接入**：一个 Agent 如何使用外部工具、资源和模板？
2. **任务协作**：两个独立 Agent 如何交换消息、跟踪长任务和交付工件？
3. **开放网络**：一个未知 Agent 如何在互联网中声明身份、被发现并协商可用接口？

MCP、A2A、ANP 分别把重点放在这三层：

| 协议 | 首要问题 | 主要互操作边界 | 核心对象 |
| --- | --- | --- | --- |
| MCP | 模型应用如何接入外部上下文与能力 | Host/Client 与能力 Server | Tool、Resource、Prompt、Capability |
| A2A | 独立 Agent 系统如何协作完成任务 | A2A Client 与远端 Agent Server | Agent Card、Message、Task、Artifact |
| ANP | 开放网络中的 Agent 如何有身份地发现、连接和协商 | 跨域 Agent 与发现/消息/应用协议 | DID、Agent Description、Discovery、Message/Application Protocol |

这不是互斥选型。一个远端 A2A Agent 内部可以通过 MCP 使用数据库；一个开放网络可以用 ANP 发现对方身份与服务，再选择 A2A 或某个领域协议执行任务。关键是不要让一种协议承担它没有定义的责任。

## 11.3 先建立统一分析框架

分析任意互操作协议时，按下面九问展开：

1. **角色**：谁发起、谁托管、谁执行、谁拥有资源？
2. **描述**：能力、接口、数据格式和安全要求如何表达？
3. **发现**：参与者如何得到对端地址与描述？
4. **协商**：协商协议版本、传输、内容类型、任务还是价格？
5. **调用**：请求、响应、流式、异步和取消如何工作？
6. **状态**：谁是状态权威，如何恢复和去重？
7. **安全**：如何认证、授权、取得用户同意并保护数据？
8. **信任**：如何判断声明、结果和对方行为值得依赖？
9. **治理**：版本、扩展、注册表、审计、撤销和责任由谁管理？

只比较“都用 JSON”或“都能调用工具”没有意义。真正决定系统设计的是状态归属和信任边界。

## 11.4 MCP：连接模型应用与外部能力

### 11.4.1 MCP 解决的问题

没有标准协议时，每个模型应用都要为文件系统、数据库、代码平台和企业服务分别编写适配器，还要自行处理工具 schema、连接、认证和错误。MCP 把这些能力放在独立 Server 后，通过统一协议暴露给 Host。

MCP 不等于模型的 Function Calling。Function Calling 描述模型如何产出结构化调用；MCP 描述 Host 如何与外部能力提供者建立会话、发现原语并交换协议消息。Host 仍需把 MCP 工具转换成模型可见的工具，并把模型输出送回 MCP Client。

### 11.4.2 协议角色

```text
User
  -> MCP Host
       |- Model / Agent Loop
       |- MCP Client A <-> Server A
       |- MCP Client B <-> Server B
       `- Consent / Policy / Context Aggregation
```

- **Host**：面向用户的应用与控制者，创建 Client、选择可见能力、执行安全 Policy、处理用户授权并聚合上下文。
- **Client**：Host 内与一个 Server 保持一对一有状态会话的协议端点，负责初始化、能力协商和消息路由。
- **Server**：提供聚焦的 Tools、Resources、Prompts 等能力，可以是本地进程或远端服务。

一个 Host 管理多个 Client，Client 与 Server 一一对应，这有助于隔离不同 Server 的状态和信任边界。Server 提供能力，不因此拥有用户对其他 Server 或本机资产的权限。

#### 从内部工具到可复用 MCP Server

MCP 的一个实际迁移路径，是把原本绑定在单个 Agent 进程里的工具变成可被多个 Host 复用的能力：

```text
Agent 内部函数
  -> 稳定 Tool Contract：名称、输入 Schema、输出、错误和副作用
  -> MCP Server 封装：暴露能力并管理资源生命周期
  -> Host 的 MCP Client：发现、命名、Policy 与上下文适配
  -> 桌面应用、IDE、CLI 或 Agent Runtime 等多个 Client 复用
```

迁移的价值不只是少写几份适配代码，而是把工具实现、协议接入和 Agent 策略拆开。不同语言、框架或部署位置的 Host 可以共享同一能力；工具升级也不必同步改写每个 Agent 的内部注册代码。

但“套一层 MCP”不会自动得到可靠服务。内部函数变成 Server 后，原来隐含在进程内的状态、身份和生命周期都必须显式设计：并发调用是否互相影响，模块级变量是否变成多用户共享状态，怎样区分租户，谁负责超时、限流、审计、版本兼容和资源清理。若工具只服务于同一进程、没有跨语言或多 Client 需求，保留普通函数调用通常更简单；只有复用边界和独立生命周期真实存在时，协议化才值得它带来的故障面。

#### 同一能力在交互式 Host 与自主 Agent 中风险不同

桌面聊天应用通常由用户发起一轮请求，并能在高影响工具调用前展示参数、等待确认。自主 Agent 则可能在一个 Run 中连续选择工具，把一次错误结果作为下一步输入，并在无人注视时扩大副作用。两者连接同一个 MCP Server，不代表风险相同：

| 使用方式 | 主要控制机会 | 主要风险 |
| --- | --- | --- |
| 交互式 Desktop/IDE | 用户逐次查看、修改或拒绝调用 | 同意疲劳、参数展示不完整、用户误判 |
| 自主 Agent Runtime | Policy、预算、沙箱和停止条件自动约束整条链 | 错误级联、重复副作用、间接注入和长时间无人监督 |

因此，MCP Server 不能假设“Client 会弹确认框”，Host 也不能把 Server 的工具描述当作安全承诺。Server 要在服务端实施身份、资源级授权、输入校验、幂等和限额；Host 则负责按当前用户意图限制模型可见工具、检查每次参数、控制预算并在高风险节点重新取得同意。交互方式改变时，应重新做威胁建模，而不是原样复制桌面测试环境的权限配置。

### 11.4.3 发现分为“找到 Server”和“列出能力”

MCP 核心会话内可以列出 Server 提供的 Tools、Resources 和 Prompts，但“全世界有哪些 MCP Server”不是核心协议替你解决的问题。Server 地址通常来自用户配置、项目配置、插件、组织托管目录或产品连接器。

连接后的典型过程是：

```text
取得 Server 配置
  -> 建立 transport
  -> initialize：交换协议版本与 capabilities
  -> initialized
  -> list tools/resources/prompts（仅请求双方支持的原语）
  -> 规范化名称并加入 Host 的能力目录
```

因此，安装市场的搜索结果和 `tools/list` 的返回值属于两个不同信任阶段。前者帮助找到候选 Server，后者描述已连接 Server 的当前能力；都不能自动获得执行授权。

### 11.4.4 协商与调用

MCP 的协商重点是协议版本和 capabilities：双方只使用共同支持的功能。它不是 Agent 之间对“谁负责这项任务”进行业务协商。

典型原语包括：

- `tools/list` / `tools/call`：发现并调用可执行能力。
- `resources/list` / `resources/read`：发现并读取上下文资源。
- `prompts/list` / `prompts/get`：获取可复用提示模板。
- 通知、日志以及规范定义的双向能力：支持会话内动态变化和 Server 到 Client 的请求。

Host 要为动态工具建立稳定命名空间，例如 `mcp__server__tool`，处理同名、描述长度、schema 变化和工具池缓存失效。工具列表变化后，模型看到的能力目录也必须一致更新。

### 11.4.5 MCP 的认证、授权与同意

MCP Authorization 是可选能力，不是建立 MCP 会话的普遍前提；未保护的 Server 或本地 stdio 场景可以不采用这套 HTTP 授权流。实现一旦选择保护远程 HTTP 资源，就应按该版本授权规范工作：Authorization Server 与用户交互并**签发 access token**（若 token 采用 JWT 形态，则还会对其签名），MCP Client 作为 OAuth Client 代表资源所有者取得 token，MCP Server 则是 Resource Server，负责验证 token、受众和 scope。Authorization Server 可以与 MCP Server 同部署，也可以是独立服务。

必须区分三件事：

```text
Authorization Server：认证/取得同意并签发面向 MCP Server 的 token
MCP Server / Resource Server：验证 token，并按 scope/资源执行服务端授权
MCP Host Policy：另行裁决模型在当前任务中能看到和调用哪些能力
用户调用级同意：允许这次具体调用造成哪些读取或副作用
```

OAuth token 证明 Client 持有访问远端服务的权限，不证明模型这次调用符合用户意图。Server 声明工具为 read-only，也只是可用于 Policy 的声明；Host 仍要按实际参数和本地风险重新判断。令牌不得透传给非目标 Server，Server 之间也不应共享 Host 的上下文。

### 11.4.6 MCP 的互信边界

MCP 建立的是协议兼容，不是自动信任。Host 需要验证 Server 来源和传输身份；Server 需要验证 Client 凭证；双方仍要怀疑对方发送的描述和内容。

不可信 Server 可以：夸大工具安全性、返回 Prompt Injection、制造超大结果、频繁改变 schema、诱导 Host 泄露其他 Server 的数据。反过来，恶意 Client 也可能滥用工具、重放请求或耗尽资源。互信只能由 TLS/OAuth、来源治理、最小权限、配额、审计和行为监测共同建立。

## 11.5 A2A：让独立 Agent 交换任务与工件

### 11.5.1 A2A 解决的问题

当一个 Agent 把研究、预订或审查任务委托给另一个独立 Agent 时，它不应了解对方内部的模型、记忆和工具。它需要知道对方擅长什么、接受什么输入、怎样认证、任务进度如何查询、最终工件如何取得。

A2A 标准化的是独立 Agent 系统之间的协作接口。它保留远端 Agent 的不透明性：委托方看到公开能力与任务状态，而不是远端内部推理链。

### 11.5.2 协议角色与核心对象

- **User**：目标和授权的最终来源，可以是人或上层服务。
- **A2A Client/Client Agent**：代表用户发起请求的应用或 Agent。
- **A2A Server/Remote Agent**：暴露 A2A 接口、执行任务并返回状态和结果的远端 Agent 系统。

核心对象是：

| 对象 | 作用 |
| --- | --- |
| Agent Card | 描述 Agent 身份、接口、能力、Skills、输入输出模式和认证要求 |
| Message | 一次对话交换，由 role 和一种或多种 Part 组成 |
| Part | 文本、文件或结构化数据的内容容器 |
| Task | 有 ID、有状态、可长期运行的工作单元 |
| Artifact | Task 产生的可交付结果，可分片或增量更新 |
| Context | 关联多个 Task/Message 的逻辑上下文 |

这里的 Skill 是 Agent Card 中对远端能力的描述，不等同于第 10 章的本地 `SKILL.md` 文件。相同名词在不同协议层可能有不同数据模型。

### 11.5.3 A2A 不要求固定网络拓扑

早期教学材料常把 A2A 概括为“网状 P2P，消除中心协调器”。更准确的理解是：A2A 定义 Client 与远端 Agent Server 的标准交互，不强制整个系统必须去中心化，也不保证没有网关、协调器或注册表。

企业系统完全可以使用中心路由、服务网格或多租户 Gateway；多个 Agent 也可以直接互调。拓扑属于部署和编排选择，协议互操作不应与某种拓扑绑定。

### 11.5.4 发现与 Agent Card

A2A Client 可以通过 well-known URI、受治理目录或直接配置取得 Agent Card。Card 声明：

- 服务端点和支持的协议绑定。
- Agent 能力与 Skills。
- 默认或 Skill 级输入输出媒体类型。
- 流式、推送等能力。
- 安全方案和要求。
- 版本、提供方与可选签名。

公开 Card 应最小披露，不放内部地址或秘密。需要向已认证客户暴露额外能力时，可以使用受访问控制的扩展 Card。Card 可以使用 JWS 签名，但验证签名之前，Client 必须先通过可信渠道把发布者身份绑定到验证密钥，例如组织信任库中的固定密钥、经验证域名控制下的 JWKS、受信 PKI 链或预先钉住的 `kid`。如果 `jku` 和 Card 一起来自同一条未验证链路，攻击者可以同时替换 Card 和公钥。

因此，JWS 本身只证明 Card 由对应私钥签名且签名后内容未被篡改；只有可信的“发布者 -> 公钥”绑定成立后，才能进一步归因到预期发布者。即使归因成功，签名仍不证明能力声明真实、服务安全或结果正确，并且还要检查密钥有效期、轮换和撤销状态。

### 11.5.5 协商、调用与任务生命周期

A2A 的协商首先发生在 Card 层：Client 选择双方支持的协议绑定、输入输出模式、安全方案和扩展。具体业务协商则通过 Message/Task 往返进行，例如远端 Agent 请求补充信息、拒绝时间约束或提出替代方案。

```text
discover Agent Card
  -> verify + choose interface/security/content modes
  -> send Message
      -> immediate Message，或
      -> Task(id, state=submitted/working/...)
  -> poll / stream / receive push updates
  -> exchange more Messages when input is needed
  -> receive Artifacts
  -> completed / failed / canceled / rejected
```

短请求可以直接返回 Message；长任务返回 Task，并通过轮询、流式或推送传递进度。Client 应保存 Task ID、Context ID 和消息 ID，在断线后恢复，而不是重新创建一项不可区分的新任务。

### 11.5.6 A2A 的认证、授权与互信

A2A 复用 Web 安全实践。认证要求在 Agent Card 中声明，凭证通常通过传输层头部携带，不混入自然语言 Message。生产连接使用 TLS，并验证 Server 身份；可采用 API Key、OAuth、OpenID Connect、mTLS 等规范支持的方案。

认证之后，远端 Agent 仍要基于用户、租户、Skill、资源和任务动作执行授权。Client 也要判断：用户是否允许把这些数据委托给该 Agent，该 Agent 是否可以再委托，返回 Artifact 能否进入后续高权限步骤。

互信至少有四层：

1. 传输端点确实属于预期服务方。
2. Agent Card 的验证密钥已通过可信渠道绑定到该服务方，且 Card 未被篡改。
3. 当前身份被允许调用某项 Skill。
4. 远端结果在业务上足够可靠，能用于下一步决策。

前三层可以大量依赖密码学、可信密钥分发和 Policy；第四层需要证据、质量评测、声誉、交叉验证和责任契约。拿任意 JWS 自带公钥验证成功，不足以完成第二层。

## 11.6 ANP：面向开放 Agent 网络的协议组合

### 11.6.1 ANP 解决的问题

当对端不在预配置的企业目录中，问题从“怎样调用已知 Agent”扩展为：谁是这个 Agent、如何解析它的服务端点、如何发布可被机器理解的描述、怎样在跨域网络中发现和连接、如何选择后续应用协议。

ANP 把目标放在 Agentic Web：复用 HTTP、DNS、TLS 等互联网基础设施，用 DID、描述、发现、消息和应用协议构成开放协议组合。它比单一 RPC 更接近网络基础设施愿景。

### 11.6.2 协议层次与角色

可以将 ANP 理解为三层：

```text
现有互联网基础设施
  HTTP / DNS / TLS / Web PKI / Search / CDN

身份与通信基础设施
  Agent DID / DID Document / service endpoint / signed request / messaging

描述、发现与应用协议
  Agent Description / Agent Discovery / meta-protocol / domain protocols
```

参与角色不止两个 Agent，还可能包括 DID 解析入口、描述发布者、搜索/发现服务、消息服务和领域服务。它们各有独立信任边界，不能把“发现服务返回的结果”当成“对端已认证”。

### 11.6.3 身份与发现

ANP 使用 Agent DID 表示协议主体。DID Document 提供稳定身份入口、验证密钥关系和服务端点线索；公开 Agent Description 描述名称、能力和接口；域可通过 `.well-known/agent-descriptions` 发布可发现描述集合，搜索服务也可以索引这些公开描述。

典型链路是：

```text
任务需求
  -> 搜索/抓取 Agent Description
  -> 得到候选 Agent DID 与能力描述
  -> 解析 DID Document
  -> 验证身份材料与服务端点
  -> 获取/验证具体接口描述
  -> 选择协议并建立通信
```

DID Document 适合低频、低敏感的身份和服务入口，不应充当实时负载、在线状态、成员表或高频密钥日志。动态数据放入受控服务端点，避免身份文档快速膨胀和泄露。

### 11.6.4 协商与调用

ANP 的 Agent Description 与元协议思路允许一方先获取对端能力，再协商共同理解的接口；之后调用具体应用协议。当前规范集合中，不同部分成熟度不同，元协议仍可能处于草案阶段，因此生产系统不能把“未来可语义协商”当作已经稳定的互操作保证。

调用可以使用 ANP 消息协议或领域应用协议。重要的是分开：

- **发现**回答“可能找谁”。
- **身份验证**回答“当前消息是否由某 DID 控制者发出”。
- **协商**回答“双方准备用什么接口和语义”。
- **应用协议**回答“这项业务怎样请求、确认、完成和争议处理”。

开放网络中的“价格、服务等级、支付、法律条款”不应被一个通用自然语言协商结果替代，需要对应领域的可验证协议和凭证。

### 11.6.5 DID 不等于信任，签名不等于授权

DID 和签名可以证明消息与某个密钥控制关系一致、内容未被篡改，但不能证明：

- 这个 Agent 描述的能力真实。
- 它不会滥用收到的数据。
- 它有权代表某个人或组织作出业务承诺。
- 它过去可靠，或当前没有被攻陷。
- 调用者被允许访问特定资源。

ANP 的开放性要求额外治理：名称与 DID 绑定、密钥轮换和撤销、组织凭证、声誉和证书、Sybil 防护、内容来源、最小披露、速率限制以及领域授权。身份是授权与审计的输入，不是最终决策。

## 11.7 横向比较：发现、协商、调用

| 阶段 | MCP | A2A | ANP |
| --- | --- | --- | --- |
| 初始关系 | Host 通常已知 Server 配置 | Client 取得 Agent Card | 可从开放描述/搜索开始 |
| 发现对象 | 已连接 Server 的 Tools/Resources/Prompts | 远端 Agent 的接口、能力、Skills、安全要求 | Agent 身份、描述、服务端点和协议入口 |
| 协商重点 | 协议版本与 capabilities | 绑定、内容模式、安全方案、扩展和任务交互 | 身份解析、接口/协议选择与开放网络协商 |
| 调用单位 | Tool/Resource/Prompt 协议方法 | Message、Task、Artifact | Message 或领域应用协议对象 |
| 长任务 | Server/工具自行建模，核心不是任务协作协议 | Task 生命周期是核心 | 由消息或具体应用协议定义 |
| 全局发现 | 核心协议不负责 | 可用 well-known、目录或直配 | 是核心愿景之一 |
| 内部透明度 | Server 内部不透明 | 远端 Agent 内部不透明 | 跨域主体内部不透明 |

三者的共同点是“描述先于调用”，但描述的层次不同。MCP 描述能力原语，A2A 描述协作 Agent，ANP 描述开放网络主体和可继续发现的协议入口。

## 11.8 横向比较：认证、授权与互信

| 问题 | MCP | A2A | ANP |
| --- | --- | --- | --- |
| 对端身份 | 本地进程来源或远端 TLS/OAuth 端点 | TLS、Card 安全声明、可选 Card 签名 | DID/DID Document、签名、TLS 与服务端点 |
| 凭证位置 | transport/HTTP 授权层 | 通常在 HTTP/gRPC 安全层，不放 Message | 签名请求、消息安全层或应用协议 |
| 授权主体 | Server 授权 Client；Host 再授权模型调用 | Remote Agent 按 Client/User/Tenant/Skill 授权 | 每个服务/应用协议按 DID、凭证和 Policy 授权 |
| 用户同意 | Host 负责具体能力调用同意 | Client 负责委托与数据披露同意 | 调用 Agent 负责跨域发现、披露和承诺同意 |
| 内容可信 | Tool 结果仍不可信 | Message/Artifact 仍需验证 | 描述、搜索结果和消息都需验证 |
| 行为信誉 | 协议外治理 | 协议外治理 | 开放网络中更关键，仍不能只靠 DID |

任何协议都不能把 Authentication、Authorization、Consent 和 Trust 合并成一个“已连接”状态：

```text
Authentication: 你是谁/控制哪个凭证？
Authorization:   你可以对哪个资源做什么？
Consent:         用户是否同意这次具体委托和数据流？
Trust:           我应在多大程度上依赖你的声明与结果？
```

## 11.9 失败语义：协议工程的真正分水岭

### 11.9.1 MCP 失败

- Server 启动失败、断线、协议版本不兼容。
- 能力列表或 schema 在会话中变化。
- 两个 Server 工具同名，或描述过长污染上下文。
- OAuth 过期、刷新失败、错误受众或认证雪崩。
- 工具超时后实际已成功，重试造成重复副作用。
- Server 返回超大、恶意或格式错误的结果。
- Host 缓存旧工具池，模型调用不存在的能力。

MCP Client 要有连接状态机、超时、错误分类、重连和能力目录失效机制。对有副作用的调用，不能看到超时就盲目重试，应使用幂等键或先查询结果状态。

### 11.9.2 A2A 失败

- Agent Card 过期、接口迁移、签名或安全要求变化。
- Message 已送达但响应丢失，重发导致重复 Task。
- 长任务停在 `working`，远端状态丢失或租约过期。
- SSE 中断、推送重复、乱序、伪造或目标 webhook 不可达。
- Task 等待输入，但 Client 没有恢复对应会话。
- Artifact 分片不完整、媒体类型不支持或内容不可验证。
- Agent 递归委托形成环，责任和预算失控。
- 远端拒绝/取消与本地状态不同步。

Client 应持久化任务标识、用消息 ID 去重、定义取消和超时、验证推送来源并支持轮询兜底。Task 状态是业务事实，不能只依赖一条流式连接的内存状态。

### 11.9.3 ANP 失败

- 发现索引被污染，恶意 Agent 使用相似名称或虚假能力。
- DID 解析失败、密钥轮换、撤销信息滞后或服务端点被接管。
- Agent Description 与实际接口漂移，语义相似但业务含义不同。
- Sybil 节点刷高声誉或对发现服务发起拒绝服务。
- 签名有效但消息重放、上下文错配或授权范围不足。
- 跨域网络分区、搜索偏见和区域治理导致不可达。
- 协商得到的临时接口缺乏稳定版本和测试向量。
- 多跳调用中数据来源和责任链丢失。

开放发现系统必须把候选、已验证身份、已授权主体和已建立业务信任分成不同状态。缓存 DID 与描述时要保存版本、有效期和撤销策略。

## 11.10 重试、幂等、取消与补偿

跨进程和跨网络系统无法可靠区分“请求未执行”和“执行成功但响应丢失”。下面的调用信封是**本课程建议的本地 Adapter/Harness 契约**，不是 MCP、A2A、ANP 共同定义的线协议字段，也不能假设对端会原样接受：

```text
request_id      全局追踪
idempotency_key 业务去重
principal       调用主体
deadline        最晚完成时间
budget          成本/轮数/数据上限
trace_context   跨系统审计关联
data_labels     隐私与用途限制
```

Adapter 必须把本地信封映射到具体能力：若某个 MCP Tool schema 或服务文档声明幂等键，就传递相应字段；否则本地 `idempotency_key` 只能用于去重本机重试，不能保证 Server 不重复执行。A2A `1.0.0` 中 Get 类操作天然幂等、Cancel Task 幂等，Send Message 仅 **MAY** 幂等，Server 可使用 `messageId` 去重；Client 不能把它提升为无条件保证。ANP 则要按实际消息 Profile 或应用协议判断。

查询操作可以安全重试的前提是语义真的只读；创建、发送、支付和发布只有在具体工具/服务支持幂等键或可查询状态时才能自动重试；无法映射时要保持 `uncertain` 并转人工处置或补偿。取消是一项请求，不是时间倒流：远端可能已产生部分 Artifact 或外部副作用，协议适配器必须返回实际终止程度。

重试还要有指数退避、抖动、次数上限和熔断，避免一个失效 Server 或 Agent 被所有会话同时重连。认证失败通常不应按普通网络错误重试，否则会形成认证雪崩或账户锁定。

## 11.11 描述、Schema 与语义漂移

协议保证字段可以解析，不保证双方对业务含义理解一致。`search` 可能表示全文检索、联网搜索或数据库模糊匹配；`cancel` 可能表示停止计算，也可能只停止推送。

治理语义漂移需要：

- 稳定标识和显式版本，不用显示名称充当协议 ID。
- 机器可验证 schema、枚举、错误码和媒体类型。
- 示例与测试向量，但示例不代替规范。
- 能力摘要的内容哈希与缓存失效。
- 向后兼容规则和弃用窗口。
- 关键业务使用领域协议，不依赖自由文本约定。
- 对未知字段、状态和扩展采用明确策略。

兼容性不等于“忽略所有不认识的东西”。安全关键字段未知时应拒绝；非关键扩展可以保留并透传。协议需要说明哪些字段能安全忽略。

## 11.12 组合架构：让三种协议各司其职

设想一个跨组织差旅 Agent：

```text
用户差旅 Agent
  |
  | ANP：发现酒店 Agent 的 DID、描述与服务入口
  v
酒店 Agent / A2A Server
  |
  | A2A：创建行程任务、补充偏好、跟踪状态、交付订单 Artifact
  v
酒店内部执行 Agent
  |
  | MCP：访问库存、地图、客户数据库和支付前置工具
  v
内部系统
```

信任不能沿链条自动传递。用户授权 A2A 委托，不等于酒店 Agent 可读取用户所有记忆；酒店 Agent 的 MCP token 不应交给用户 Agent；ANP 发现结果只产生候选，不自动批准交易。

组合层需要保存委托链和数据标签：原始用户是谁、哪个 Agent 在代表谁、每一跳披露了什么、哪个系统产生了最终证据。否则协议越丰富，责任越模糊。

## 11.13 最小实现：统一互操作控制器

不要一开始实现三个完整协议栈。先用官方 SDK 或成熟库负责协议编解码，在 Harness 中实现统一的描述缓存、Policy、调用信封、状态存储和审计。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Peer:
    protocol: str          # mcp | a2a | anp
    stable_id: str
    endpoint: str
    description_digest: str
    trust_state: str       # candidate | authenticated | authorized

@dataclass(frozen=True)
class Envelope:
    """本地控制信封；Adapter 按对端能力选择可映射字段。"""
    request_id: str
    idempotency_key: str
    principal: str
    deadline_ms: int
    data_labels: tuple[str, ...]

class InteropController:
    def __init__(self, policy, state, adapters, audit):
        self.policy = policy
        self.state = state
        self.adapters = adapters
        self.audit = audit

    async def discover(self, protocol, query):
        candidates = await self.adapters[protocol].discover(query)
        return [verify_candidate(c) for c in candidates]

    async def invoke(self, peer, operation, payload, envelope):
        assert peer.trust_state in {"authenticated", "authorized"}
        decision = self.policy.authorize(
            principal=envelope.principal,
            peer=peer,
            operation=operation,
            payload=payload,
            data_labels=envelope.data_labels,
        )
        if not decision.allowed:
            raise PermissionError(decision.reason)

        self.state.begin(envelope, peer, operation)
        try:
            adapter = self.adapters[peer.protocol]
            wire_request = adapter.map_local_envelope(
                peer, operation, payload, envelope
            )
            result = await adapter.invoke(peer, operation, wire_request)
            checked = validate_and_label_result(peer, operation, result)
            self.state.complete(envelope.request_id, checked.status)
            return checked
        except TransientError as error:
            self.state.mark_uncertain(envelope.request_id, error)
            raise  # retry policy must inspect idempotency and remote state
        finally:
            self.audit.record(envelope.request_id)
```

三个 Adapter 的最小职责不同：

```text
MCPAdapter:
  connect -> initialize -> list primitives -> call/read/get

A2AAdapter:
  fetch/verify card -> choose binding -> send message
  -> persist task -> poll/stream/push -> artifact

ANPAdapter:
  discover description -> resolve DID -> verify proof
  -> choose negotiated/application protocol -> delegate to adapter
```

ANP Adapter 最终可能把调用交给 A2A 或领域协议 Adapter；这不是重复，而是“发现和身份层”与“任务执行层”的组合。

## 11.14 生产约束

1. **协议版本固定**：保存双方协商版本、绑定和扩展，升级先做兼容测试。
2. **描述可验证**：缓存 Card/Description/Tool Schema 的摘要、来源、有效期和签名状态。
3. **凭证隔离**：每个 Server、Agent、租户和受众使用独立凭证，不跨协议透传。
4. **统一 Policy**：协议 Adapter 不自行决定业务授权，所有副作用进入同一治理面。
5. **状态持久化**：Task、会话、请求 ID、推送配置和重试状态可在重启后恢复。
6. **幂等优先**：按具体 Tool/操作能力映射本地去重信息；无法映射时不宣称远端幂等，未知结果先查状态。
7. **有界输入输出**：限制描述、schema、消息、Artifact、流和递归委托大小。
8. **来源标签**：跨协议返回均标记为不可信外部内容，保留数据谱系。
9. **可取消与可补偿**：展示远端真实状态，不把本地取消误写成全局撤销。
10. **租户隔离**：描述缓存可以共享，授权、上下文、任务和凭证不能串租户。
11. **可观测**：统一 trace 关联发现、认证、授权、调用、重试和最终副作用。
12. **配额与熔断**：按对端、身份、操作和租户限制速率、成本与并发。
13. **撤销传播**：密钥、Card、DID、插件或 Server 被撤销后，缓存和活跃会话及时失效。
14. **成熟度标记**：草案功能、教学模拟和生产规范不得使用同一“已支持”标签。

## 11.15 典型失败模式

| 失败模式 | 根因 | 修正方向 |
| --- | --- | --- |
| 把 MCP 当成 Agent 任务协议 | 只看到都能发送 JSON | 长任务协作用 A2A/领域任务模型 |
| 把 A2A 等同于网状 P2P | 将部署拓扑写进协议定义 | 分离 Client/Server 互操作与拓扑选择 |
| 把 ANP 发现结果直接调用 | 发现、身份、授权和信任混淆 | 建立候选到授权主体的状态机 |
| 有 OAuth token 就跳过审批 | 远端授权替代用户意图 | Host/Client 再做调用级 Policy |
| Agent Card 签名后全信任结果 | 完整性等同业务可靠性 | 证据验证、声誉、限额和责任契约 |
| 超时后自动重试发送/支付 | 不确定结果下重复副作用 | 幂等键、状态查询和补偿 |
| 工具/能力描述无限进入 Prompt | 动态发现缺乏预算 | 目录检索、截断策略和按需暴露 |
| 把凭证放进 Message/Prompt | 控制面与内容面混合 | 使用传输安全层和秘密存储 |
| 流断开就认为远端任务失败 | 传输状态等同业务状态 | 持久 Task ID，重连后查询权威状态 |
| 忽略草案与稳定规范差异 | 生态愿景当作兼容承诺 | 版本固定、能力探测和成熟度标记 |

## 11.16 测试与验收

### 11.16.1 协议契约测试

1. 不同版本、未知 capability、未知扩展和降级协商。
2. 描述 schema、签名、内容摘要、缓存过期和撤销。
3. 多种绑定返回语义一致，错误码可映射。
4. 大小限制、媒体类型、编码和恶意嵌套数据。
5. 官方测试向量、参考实现和跨语言实现互测。

### 11.16.2 安全与信任测试

1. 错误受众 token、过期凭证、scope 不足和令牌透传。
2. TLS 身份错误、Card/Description 篡改和 DID 密钥轮换。
3. 工具描述、Message、Artifact 中的 Prompt Injection。
4. 跨租户任务、缓存、推送和凭证隔离。
5. 用户未同意的数据外发和远端再委托。
6. 发现污染、相似名称、Sybil 和声誉操纵。

### 11.16.3 故障与恢复测试

1. 请求发送前、发送中、远端执行后、响应前四个断点故障。
2. 重复 Message、重复推送、乱序流、部分 Artifact 和重放请求。
3. Client/Host/Server 分别重启后的状态恢复。
4. OAuth 刷新失败、认证服务故障和并发重认证。
5. Task 卡住、取消竞态、超时后完成和补偿失败。
6. Server 能力热更新、Agent Card 迁移和 DID 端点变更。
7. 网络分区、熔断、恢复探测和流量回升。

### 11.16.4 验收问题

系统应能回答：

- 这个能力或 Agent 是怎样被发现的？
- 我验证了哪个身份，使用了哪个协议版本？
- 谁授权了这次调用，披露了哪些数据？
- 请求失败时，远端是否可能已经产生副作用？
- 结果来自哪一跳，经过哪些转换，能否追溯？
- 如何取消、撤销凭证、隔离对端并恢复任务？

## 11.17 协议与生态治理

互操作规模扩大后，技术兼容只是最低要求，还需要：

- **规范治理**：版本发布、变更提案、弃用周期和安全公告。
- **扩展治理**：命名空间、注册、冲突规则和稳定性等级。
- **实现治理**：一致性测试、认证计划、参考测试向量和漏洞响应。
- **目录治理**：发布者验证、内容审核、撤销、申诉和反刷量。
- **数据治理**：用途限制、保留期、跨域传输和删除责任。
- **责任治理**：委托链、服务等级、错误归属、赔付和争议证据。
- **运行治理**：配额、滥用检测、黑名单、区域策略和紧急停用。

开放标准不意味着无治理。相反，参与者越陌生，越需要可移植的身份、证据、撤销和责任机制。中心目录便于审核但可能形成单点和偏见；完全去中心化提高开放性，却把发现污染和 Sybil 成本推给每个调用者。现实系统通常采用分层目录与本地 Policy 结合。

## 11.18 系统地图

```text
                         User / Organization Policy
                                    |
                            Interop Controller
           discovery cache / identity / consent / state / audit
                +-------------------+-------------------+
                |                   |                   |
             MCP Adapter         A2A Adapter         ANP Adapter
                |                   |                   |
       Host -- Client          Client Agent       Discovery / DID
                |                   |                   |
          MCP Server          Remote Agent       Agent Description
      tools/resources/prompts  message/task/artifact      |
                |                   |              negotiated or
          internal systems      Agent internals     application protocol

Trust states:
candidate -> endpoint verified -> authenticated -> authorized -> monitored

Cross-cutting:
version/capability negotiation | idempotency | deadlines | data labels
rate limits | provenance | revocation | tracing | cancellation/compensation
```

## 11.19 共同结论

1. MCP 主要标准化模型应用与能力 Server，A2A 主要标准化独立 Agent 的任务协作，ANP 主要探索开放 Agent 网络的身份、发现与协议连接。
2. 三种协议可以分层组合，不应互相冒充对方的状态模型和信任机制。
3. 发现只产生候选，认证只证明身份关系，授权和用户同意仍需单独裁决。
4. 协议兼容不等于内容可信、能力真实或行为可靠。
5. A2A 定义 Client/Server 互操作，不强制中心化或去中心化拓扑。
6. DID、签名、TLS 和 OAuth 都是互信基础设施的一部分，没有一种能独自完成信任治理。
7. 长任务的正确性取决于持久状态、幂等、重连、取消和补偿，而不只是请求格式。
8. 生产互操作需要版本、扩展、目录、撤销、数据谱系和责任链共同治理。

## 11.20 本章自检

1. MCP 与模型 Function Calling 分别标准化什么？
2. MCP Host、Client、Server 的安全责任有何不同？
3. 为什么 MCP 的 `tools/list` 不能解决全球 Server 发现？
4. A2A 的 Message、Task 和 Artifact 分别表达什么？
5. 为什么 A2A 不应被定义成必然的网状 P2P 协议？
6. Agent Card 的签名能证明什么，不能证明什么？
7. ANP 中 DID Document、Agent Description 和 Discovery 各自负责什么？
8. 为什么 DID 验证成功后仍需授权和信誉判断？
9. 超时后直接重试一个发送操作为什么危险？
10. 如何在组合 MCP、A2A、ANP 时保留用户委托和数据来源链？

## 11.21 开放性问题

1. A2A Agent Card 和 ANP Agent Description 是否可能共享一个最小能力描述核心，同时保留各自语义？
2. 开放目录如何证明 Agent 的能力不是虚假声明，而又不要求公开内部实现？
3. 当远端 Agent 再委托第三方时，原用户的同意和数据用途限制如何跨跳传播？
4. 长任务跨多个 Agent 时，哪个节点应成为最终状态权威？
5. 如何为自然语言协商生成可执行、可审计、可争议处理的正式契约？
6. DID 密钥被盗但撤销尚未传播时，依赖方怎样控制风险窗口？
7. Agent Card 或工具 schema 高频变化时，缓存一致性和 Prompt 稳定性如何兼顾？
8. 一个协议扩展被少数大平台事实垄断后，开放标准如何保持可竞争性？
9. 跨协议追踪会提升可审计性，也可能暴露用户关系图；怎样做到最小可追溯？
10. 声誉系统怎样抵抗 Sybil、串谋和新 Agent 冷启动偏见？
11. 哪些任务绝不应该开放给未知网络 Agent，即使它通过了身份和能力验证？
12. 当两个协议都能完成同一交互时，应依据成熟度、信任、状态模型还是成本选型？

## 11.22 原文入口

### 本地融合来源

- [hello-agents：智能体通信协议](../../source/hello-agents/docs/chapter10/第十章%20智能体通信协议.md)
- [hello-agents：第 10 章示例报告](../../source/hello-agents/code/chapter10/report.md)
- [learn-claude-code：MCP Tools](../../source/learn-claude-code/s19_mcp_plugin/README.md)
- [Alice 方法论：MCP 协议](../../source/Alice_methodology/chapters/08-mcp.md)
- [Claude Code 分析：MCP 实现](../../source/claude-code-analysis/analysis/04d-mcp-implementation.md)
- [Harness Engineering：多 Agent 中的 MCP 就绪检查](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20.md)
- [easy-langent：MCPChat](../../source/easy-langent/project/MCPChat/README.md)
- [Hermes：Gateway 协议适配层](../../source/hermes-book/src/part5/ch14-gateway.md)
- [claw0：Gateway 与 JSON-RPC 路由](../../source/claw0/sessions/zh/s05_gateway_routing.md)
- [hello-claw：轻量 Agent 的 MCP 取舍](../../source/hello-claw/docs/cn/build/chapter8/index.md)
- [AI Agents in Action 第 3 章：MCP 工具迁移与不同 Client 风险](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/3.AI智能体的MCP操作.md)
- [深入理解 AI Agent：第 4 章 MCP 与协作工具](../../source/ai-agent-book/book/chapter4.md)

### 官方规范与项目入口

- [MCP `2025-11-25` 官方架构](https://modelcontextprotocol.io/specification/2025-11-25/architecture)
- [MCP 官方授权规范](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [A2A `1.0.0` 官方规范](https://a2a-protocol.org/v1.0.0/specification/)
- [ANP `1.1` 官方入门指南（滚动 URL，访问于 2026-07-17）](https://agent-network-protocol.com/docs/anp-getting-started-guide)
- [ANP `1.1` 身份与发现规范（滚动 URL，访问于 2026-07-17）](https://agent-network-protocol.com/specs/message/identity-discovery)
- [ANP 官方规范仓库](https://github.com/agent-network-protocol/AgentNetworkProtocol)
