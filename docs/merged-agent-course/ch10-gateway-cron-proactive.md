# 第 10 章：Gateway、多渠道、Cron 与主动 Agent

> 本章目标：把 Agent 从单一 CLI 对话扩展为常驻服务。读完本章，你应该能设计统一消息格式、多渠道适配、路由绑定、Gateway、心跳、Cron、投递队列、重试和并发 lane。

## 10.1 从对话程序到常驻系统

前面的 Agent 主要是“用户发一句，Agent 回一轮”。但真实产品往往需要常驻运行：

- CLI、Web、Telegram、飞书、Slack、微信等多渠道接入。
- 不同用户、群聊、项目路由到不同 Agent。
- 后台任务慢慢跑。
- 定时任务主动触发。
- 消息失败后可靠投递。
- 多个 lane 并发但互不干扰。
- 系统重启后能恢复队列和状态。

这就是 Gateway 和主动 Agent 的主题。

可以把它看成架构升级：

```text
单轮 Agent Loop
  -> Session Agent
  -> Multi-channel Gateway
  -> Scheduled / Proactive Agent
  -> Reliable Agent Service
```

## 10.2 Channel：先统一消息格式

`claw0` 的通道章节从 `InboundMessage` 开始，这是正确入口。

不同平台消息长得完全不同：CLI 是一行输入，Telegram 有 chat id 和 message id，飞书有 tenant、open_id、群聊和 mention，WebSocket 有连接和事件。若每个平台都直接调用 Agent，核心逻辑会被平台细节污染。

所以要先标准化：

```text
InboundMessage:
  channel
  account_id
  conversation_id
  sender_id
  text
  attachments
  timestamp
  raw_event
```

标准化之后，Agent 看到的是统一消息，而不是平台 SDK。

## 10.3 Channel Adapter：平台差异留在边缘

Hermes Gateway 章节把平台适配器抽象得很清楚：每个平台适配器负责收、发、媒体、typing、重试、认证等能力。

适配器应该处理：

- 解析平台事件。
- 转换成统一 `InboundMessage`。
- 发送统一 `OutboundMessage`。
- 处理媒体和附件缓存。
- 做平台限流和错误适配。
- 维护 token、连接和重连。

核心 Agent 不应该知道“这是飞书消息还是 Telegram 消息”。它只处理标准输入输出。

```text
Telegram Adapter
Feishu Adapter
CLI Adapter
Web Adapter
  -> InboundMessage
  -> Gateway Router
  -> Agent
  -> OutboundMessage
  -> Platform Adapter
```

## 10.4 Gateway：一个入口，多个 Agent

Gateway 不只是渠道适配，它还要做路由。

典型路由维度：

- channel：来自哪个平台。
- account：哪个 bot 账号。
- conversation：哪个群聊或 DM。
- sender：哪个用户。
- explicit switch：用户是否强制切换 Agent。
- binding table：配置里是否绑定了特定 Agent。

`claw0` 的 BindingTable 是一个非常清晰的教学模型：

```text
(channel, user, conversation)
  -> resolve binding
  -> AgentConfig
  -> session key
  -> run_agent_turn
```

路由系统要解决两个问题：这条消息应该交给哪个 Agent？它应该接到哪个 session 上？

## 10.5 Session Key：多渠道系统的身份边界

Session key 决定“这条消息属于哪段上下文”。

错误设计会造成串线：

- 群聊 A 的上下文进入群聊 B。
- 用户在 Telegram 的私人偏好影响企业飞书群。
- 同一平台多个 bot 共用一个 session。
- 强制切换 Agent 后旧上下文污染新 Agent。

一个 session key 通常包含：

```text
agent_id
channel
account_id
conversation_id
dm_scope
sender_id 或 group_id
```

是否包含 sender_id，要看产品语义。群聊里是共享会话，还是每个用户单独会话？这是产品决策，不是技术细节。

## 10.6 Gateway 与 Prompt Runtime

多渠道会影响 prompt。

比如 CLI 可以输出长 Markdown，Slack/飞书可能需要短回复，群聊里需要 mention 门控，移动端不适合大段代码，某些平台支持附件而某些不支持。

所以 Gateway 应把渠道信息注入 Prompt Runtime：

```text
Dynamic Context:
  channel: feishu
  conversation_type: group
  mentioned: true
  output_constraints: concise, no huge code block
```

但渠道信息不应该污染长期人格。它是动态上下文，不是 Agent 身份。

## 10.7 Heartbeat：主动性的最低配

主动 Agent 不一定一开始就需要复杂计划器。最小主动性是 heartbeat。

```text
定期醒来
  -> 检查是否满足前置条件
  -> 检查用户是否活跃
  -> 执行一条轻量任务
  -> 必要时发消息
  -> 无事则静默
```

`claw0` 的 heartbeat lane 很重要：用户主 lane 优先，heartbeat 不能抢占用户交互。

主动性必须克制。一个好 Agent 不应该因为能主动说话，就不停打扰用户。

## 10.8 Cron：按时间表生产工作

Cron 是更明确的主动任务。

一个 Cron Job 至少需要：

| 字段 | 含义 |
| --- | --- |
| id | 作业 ID |
| schedule | 五段式 cron 或 interval |
| prompt/task | 到点执行什么 |
| target | 投递到哪个 channel/session |
| enabled | 是否启用 |
| durable | 是否持久化 |
| max_runs / expires_at | 上限和过期 |
| last_run / next_run | 调度状态 |

调度器要处理 cron 表达式解析、防重入、错过时间后的快进、jitter 防惊群、作业上限、作业校验，以及 durable 和 session-only 的区别。

Cron 不是“定时调用模型”那么简单，它是长期运行系统的一部分。

## 10.9 Delivery Queue：发送消息也要可靠

Agent 生成了回复，不代表用户一定收到。

平台发送可能失败：网络断开、token 过期、平台限流、消息格式不支持、附件上传失败、目标会话不存在。

所以需要 Delivery Queue：

```text
OutboundMessage
  -> enqueue
  -> delivery runner
  -> send
  -> ack success
  -> fail with retry / dead letter
```

队列要支持原子写入、ack / fail 生命周期、指数退避、最大重试次数、dead letter、统计和可观测性。

## 10.10 Resilience：配置轮换与故障分类

`claw0` 的 resilience 章节把失败分层讲得很好。常见故障包括 rate limit、auth failure、network timeout、provider outage、tool failure、permission denied、prompt too long。

不同故障应该走不同恢复路径：

| 故障 | 恢复 |
| --- | --- |
| rate limit | cooldown + profile rotation |
| auth failure | 停用配置，提示修复 |
| network timeout | 有界重试 |
| provider outage | fallback model/provider |
| permission denied | 不重试，反馈用户 |
| prompt too long | compact |

恢复策略不能盲目重试。先分类，再恢复。

## 10.11 并发 Lane：不要让后台任务抢主对话

常驻 Agent 会有多类工作：用户主对话、Cron、Heartbeat、后台长任务、投递队列、记忆整理、子 Agent 研究任务。

如果全部放一个队列，用户体验会很差。一个长任务可能阻塞用户即时消息。

LaneQueue 的思路是按工作类型分 lane：

```text
main lane:
  用户交互，优先级最高。

cron lane:
  定时任务，有并发限制。

heartbeat lane:
  非阻塞，用户活跃时让步。

research lane:
  可并行，但限制数量。
```

每个 lane 有自己的并发上限、队列、generation、重启恢复策略。

## 10.12 主动 Agent 的产品边界

主动性是很有吸引力的能力，但也容易变成打扰。

主动 Agent 应遵守：

- 用户可关闭。
- 有明确触发条件。
- 无事不打扰。
- 群聊里更谨慎。
- 重要行动前确认。
- 定时任务可查看、暂停、删除。
- 主动消息可追溯来源。

一个好的主动 Agent 像可靠同事，不像通知噪音。

## Hello-Agents 融合补充

`hello-agents` 第 5 章里的 n8n 很适合放到本章理解。n8n 的价值不在于它比代码更“智能”，而在于它天然站在事件流和工作流视角：触发器、节点、条件分支、外部服务、定时任务、重试和通知。学习 Gateway / Cron 时，可以把 n8n 看成一个低代码版的主动 Agent 编排器。

第 13 章的智能旅行助手展示了另一种入口：Web 应用。这里的 Agent 不只是命令行对话，而是嵌入一个前端产品，前端负责收集目的地、预算、日期、偏好等结构化输入，后端 Agent 再调用工具和角色模块生成方案。这个案例说明，多渠道并不总是“接 Telegram、Slack、微信”，也包括 Web 表单、移动端、游戏客户端和内部系统。

第 15 章的赛博小镇补充了后台任务和主动行为的例子。NPC 不可能只在用户点击时才思考，它需要后台批量对话、记忆更新、关系变化和游戏状态同步。这类系统更接近常驻 Agent：它要管理生命周期、并发、节流、持久化和可观察状态。否则，Agent 越主动，越容易变成不可控的后台噪音。

Extra11 的 WebAgent 也能映射到本章：浏览器既是一个渠道，也是一个执行环境。WebAgent 接收页面状态、执行点击输入、返回观察结果，本质上也是一种 channel adapter。不同之处在于它面对的是动态网页和视觉状态，所以更需要超时、截图、动作审计和失败恢复。

## 10.13 最小实现建议

第一版可以这样做：

1. 定义统一 `InboundMessage` 和 `OutboundMessage`。
2. 实现 CLI channel，再加一个 WebSocket 或 Telegram channel。
3. 用 BindingTable 路由到 AgentConfig。
4. 设计 session key，避免群聊和私聊串线。
5. 增加 DeliveryQueue，发送失败可重试。
6. 增加一个 heartbeat lane，但默认静默。
7. 增加 cron job 存储和简单调度器。
8. 为 main、cron、heartbeat 分 lane。
9. 把 channel 信息注入 Prompt Runtime。
10. 给所有后台任务加日志、状态和关闭机制。

## 系统地图

```text
Platform Event
  -> Channel Adapter
  -> InboundMessage
  -> Gateway Router
  -> Session Key
  -> Agent Loop
  -> OutboundMessage
  -> Delivery Queue
  -> Platform Adapter

Cron / Heartbeat
  -> Lane Queue
  -> Agent Task
  -> Delivery Queue
```

## 共同结论

1. 多渠道系统必须先统一消息格式。
2. Gateway 的核心是路由和 session key，不只是平台适配。
3. 主动 Agent 需要 lane、前置条件和静默策略。
4. Cron 和投递队列都要持久化、可重试、可观测。
5. 常驻系统的难点不是模型调用，而是生命周期、并发和可靠性。

## 本章自检

1. Channel Adapter 和 Gateway Router 的职责有什么区别？
2. Session key 设计错了会导致什么问题？
3. Heartbeat 和 Cron 的边界是什么？
4. Delivery Queue 为什么需要 ack / fail 生命周期？
5. LaneQueue 为什么比单一任务队列更适合主动 Agent？

## 开放性问题

1. 群聊里的 Agent 应该默认共享上下文，还是按用户隔离上下文？你会如何设计配置项？
2. 当 Cron 任务连续失败三次时，系统应该自动停用、继续重试、还是询问用户？依据是什么？
3. 主动 Agent 的“有用提醒”和“打扰用户”之间的边界如何被产品化，而不是只靠 prompt？

## 原文入口

- [claw0 s04: 通道](../../source/claw0/sessions/zh/s04_channels.md)
- [claw0 s05: 网关与路由](../../source/claw0/sessions/zh/s05_gateway_routing.md)
- [claw0 s07: 心跳与 Cron](../../source/claw0/sessions/zh/s07_heartbeat_cron.md)
- [claw0 s08: 消息投递](../../source/claw0/sessions/zh/s08_delivery.md)
- [claw0 s09: 弹性](../../source/claw0/sessions/zh/s09_resilience.md)
- [claw0 s10: 并发](../../source/claw0/sessions/zh/s10_concurrency.md)
- [learn-claude-code s13: Background Tasks](../../source/learn-claude-code/s13_background_tasks/README.md)
- [learn-claude-code s14: Cron Scheduler](../../source/learn-claude-code/s14_cron_scheduler/README.md)
- [Hermes: CLI/TUI](../../source/hermes-book/src/part5/ch13-cli-tui.md)
- [Hermes: Gateway](../../source/hermes-book/src/part5/ch14-gateway.md)
- [Hermes: Cron](../../source/hermes-book/src/part5/ch15-cron.md)
- [Hermes: Concurrency](../../source/hermes-book/src/part6/ch19-concurrency.md)
- [Hermes: Lifecycle](../../source/hermes-book/src/part6/ch20-lifecycle.md)
- [hello-claw 配置文件详解](../../source/hello-claw/docs/cn/appendix/appendix-g.md)
- [hello-agents Ch05: 基于低代码平台的智能体搭建](../../source/hello-agents/docs/chapter5/第五章%20基于低代码平台的智能体搭建.md)
- [hello-agents Ch13: 智能旅行助手](../../source/hello-agents/docs/chapter13/第十三章%20智能旅行助手.md)
- [hello-agents Ch15: 构建赛博小镇](../../source/hello-agents/docs/chapter15/第十五章%20构建赛博小镇.md)
- [hello-agents Extra11: WebAgent 科普与实战](../../source/hello-agents/Extra-Chapter/Extra11-WebAgent科普与实战.md)
