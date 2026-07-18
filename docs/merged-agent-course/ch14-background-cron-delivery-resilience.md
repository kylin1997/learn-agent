# 第 14 章：后台任务、Cron、投递与运行时韧性

> 本章目标：把“Agent 在后台跑”拆成可持久化、可调度、可隔离、可重试和可恢复的运行时协议。读完本章，你应该能够区分后台任务、Cron 与 heartbeat，设计任务状态机和投递状态机，解释至少一次投递为何要求幂等，并用退避、熔断、并发 lane、租约和恢复扫描构成运行时韧性。

## 14.1 学习目标与边界

Gateway 解决消息进入系统后的身份和路由，[第 13 章](ch13-gateway-channel-identity-routing.md)已经完成这一部分。本章从“工作已被接受”开始，回答：

- 长任务如何脱离前台请求生命周期？
- 周期性和事件性任务如何被可靠触发？
- 进程崩溃、网络失败和提供商故障后如何继续？
- Agent 生成结果后，怎样区分“渠道已接受”“已送达”和“用户已读”，并只承诺渠道真正可观测的层级？
- 多种工作如何并发而不让后台任务拖垮主对话？

本章不讨论如何围绕开放目标多轮收敛；那是[第 15 章](ch15-loop-engineering.md)的 Loop Engineering。Cron 可以触发一次任务，但“按时重复”本身不等于目标反馈闭环。

## 14.2 核心机制：三个分离的状态机

常驻 Agent 最容易犯的错误，是把“触发了”“执行完了”“发出去了”都记成一个 `done`。实际上至少存在三个状态机：

```text
Schedule: due -> claimed -> emitted | misfired
Execution: queued -> running -> succeeded | failed | cancelled
Delivery: pending -> sending -> provider_accepted | retry_wait | dead_letter
Optional receipt: published -> delivered -> read
```

它们之间通过稳定 ID 关联，而不是共享一个布尔值：

```text
job_id -> run_id -> attempt_id -> result_artifact -> delivery_id
```

调度成功只表示产生了执行请求；执行成功只表示得到了结果；`provider_accepted` 只表示渠道 API 接受或发布了消息。只有渠道提供独立回执时，系统才能继续观测 `delivered` 或 `read`。三者分离后，系统才能只重发消息而不重跑昂贵任务，或只重跑失败步骤而不重复已完成副作用。

## 14.3 最小实现：把后台任务生命周期从连接中解耦

前台请求适合短任务：连接存在、用户等待、结果立即返回。后台任务则需要自己的身份、状态和取消协议：

```python
@dataclass
class TaskRecord:
    task_id: str
    tenant_id: str
    session_key: str
    kind: str
    payload_ref: str
    idempotency_key: str
    state: str
    priority: int
    lane: str
    attempt: int
    max_attempts: int
    available_at: datetime
    lease_owner: str | None
    lease_until: datetime | None
    created_at: datetime
    updated_at: datetime
```

提交后台任务时应立即返回 `task_id`，而不是让调用方持有线程对象或进程内 Future 作为唯一句柄。用户随后可以查询状态、取消任务或订阅结果。

`learn-claude-code` 的教学实现用子进程和线程说明“立即返回、后台执行、之后读取结果”的基本模式。生产系统还需把任务记录、输出工件和取消意图外化；否则进程一重启，后台工作就从系统认知中消失。

## 14.4 Cron：时间只负责产生工作

Cron Job 是“何时产生哪类执行请求”的声明，不应直接承载完整执行状态：

| 字段 | 作用 |
| --- | --- |
| `job_id` | 稳定作业身份 |
| `schedule` / `timezone` | 时间规则与时区 |
| `task_template` | 到点生成的工作模板 |
| `target` | Agent、session 或投递目标 |
| `enabled` | 是否继续产生新 run |
| `misfire_policy` | 宕机错过后跳过、补一次或补齐 |
| `overlap_policy` | 前一 run 未完成时跳过、排队或并行 |
| `jitter` | 分散同时启动的压力 |
| `max_runs` / `expires_at` | 生命周期上限 |
| `last_fire_at` / `next_fire_at` | 可恢复调度游标 |

调度器的核心不是每秒扫描字符串，而是原子 claim：多个实例看到同一到期作业时，只能有一个成功创建该时间槽的 `run_id`。

```text
slot_key = hash(job_id, scheduled_at)
UNIQUE(job_id, scheduled_at)
```

这个唯一约束把重复调度转换成可检测冲突。模型不参与判断“这一分钟是否已经触发过”。

唯一约束只能防止重复，不能单独保证任务一定入队。调度器在 claim 成功后、enqueue 之前崩溃，会留下一个永远停在 `claimed` 的时间槽。生产实现应选择一种原子交接协议：

```text
BEGIN
  insert schedule_slot(job_id, scheduled_at, claimed)
  insert run(run_id, slot_key, queued)
  insert outbox(run_id, enqueue_requested)
COMMIT
```

独立 relay 再把 outbox 发布到执行队列，并在成功后更新状态。如果调度存储和队列无法共享事务，则 claim 必须带租约；恢复扫描要回收过期 claim，检查对应 run 或队列消息是否存在，再安全补发。`UNIQUE(job_id, scheduled_at)` 与 outbox/租约分别解决“不要重复”和“不要丢失”，两者不能互相替代。

### Misfire 与重叠策略

系统宕机两小时后恢复，一个每五分钟运行的任务已经错过 24 次。常见策略是：

- `skip`：跳过历史，只计算下一个时间点。
- `fire_once`：立即补一次，合并错过窗口。
- `catch_up`：补齐每个时间槽，必须配合速率与总量上限。

前一次仍在运行时也要显式选择：`forbid`、`queue_one`、`replace` 或 `allow`。默认无限并行会把一次慢依赖变成任务洪峰。

## 14.5 Heartbeat：状态巡检，不是低精度 Cron

Heartbeat 表达“周期醒来检查是否值得行动”：

```text
wake -> inspect checklist/state -> act or stay silent -> record pulse
```

Cron 表达已知时间规则，heartbeat 表达基于当前状态的轻量巡检。二者的区别在意图：

| 机制 | 触发语义 | 无事时 | 典型用途 |
| --- | --- | --- | --- |
| Cron | 到点即产生工作 | 仍有一次 run | 日报、固定提醒、周期同步 |
| Heartbeat | 到点检查是否有事 | 静默并记录健康 | 收件箱巡检、状态异常提醒 |
| Event | 外部状态变化 | 无事件不运行 | webhook、队列消息、告警 |

Heartbeat 必须有静默契约、活跃时间窗、最小间隔和通知抑制。否则“主动性”会退化成重复打扰。健康信号应记录最后成功巡检时间，但不能用一个 `HEARTBEAT_OK` 文本掩盖检查项根本没有执行。

## 14.6 队列、租约与确认

一个可靠 worker 循环通常是：

```text
poll available task
  -> atomically claim lease
  -> execute with timeout/cancellation
  -> persist result
  -> ack success
  -> or classify failure and reschedule/dead-letter
```

租约而不是永久 `running` 标记，使崩溃任务可以恢复。worker 定期续租；进程消失后，`lease_until` 过期，reaper 才能把任务重新置为可领取。租约时间必须长于正常心跳抖动，又短于业务可接受的恢复时间。

队列的核心不只是 FIFO，还包括：

- 持久化 enqueue 与原子 claim。
- 可见性超时或租约。
- 优先级与租户公平性。
- 有界积压与 backpressure。
- 取消、超时和死信。
- 每次尝试的独立记录。
- payload 与大工件分离存储。

## 14.7 投递语义与幂等

分布式系统无法仅凭“发送 API 返回前连接断了”判断对方是否收到。常见语义是：

| 语义 | 保证 | 代价 |
| --- | --- | --- |
| 至多一次 | 不重复，但可能丢 | 失败不重试 |
| 至少一次 | 尽量不丢，但可能重复 | 消费端必须幂等或去重 |
| 恰好一次效果 | 业务结果看起来只发生一次 | 需要幂等键、事务与状态回读 |

网络层“严格恰好一次”通常不可得。工程目标应是至少一次传输加恰好一次业务效果。

幂等键要绑定业务意图，而不是绑定某次随机 attempt：

```text
execution key = tenant + task type + logical input/version
delivery key  = result_id + destination + rendering_version
```

写操作可以使用唯一约束、upsert、事务 inbox/outbox、条件更新或接收方幂等 API。若渠道不支持幂等键，发送方至少保存平台 message id，并在不确定失败后先查询状态；无法查询时应接受“可能重复”并让内容可识别，而不是假装保证恰好一次。

### Transactional Outbox

业务状态与“待发送事件”若分别写入，进程可能在两次写入之间崩溃。Transactional Outbox 在同一数据库事务中写业务结果和 outbox 记录，再由独立投递器发送：

```text
BEGIN
  save task result
  insert outbox(delivery_id, payload_ref, pending)
COMMIT

delivery worker -> send -> mark provider_accepted
```

这保证成功结果不会因为崩溃而永远漏发，但发送仍可能重复，所以接收侧幂等依然必要。

渠道返回 2xx 或 message id 通常只证明服务端接受或发布消息，不证明用户设备已收到，更不证明用户已读。投递状态必须按渠道能力建模：没有送达回执的渠道应停在 `provider_accepted`，不能为了统一报表虚构 `delivered`。SLA 也要写明观测终点，例如“99.9% 的消息在 30 秒内被 Provider 接受”，而不是含糊地写“送达用户”。

## 14.8 失败分类：先判断，再重试

所有错误都重试会放大故障。建议至少区分：

| 类别 | 示例 | 默认动作 |
| --- | --- | --- |
| transient | 超时、连接重置、短期限流 | 有界重试与退避 |
| throttled | 429、配额窗口 | 尊重 `Retry-After`、降并发 |
| auth | token 过期、签名错误 | 停止该配置，等待修复 |
| invalid | 参数、格式、目标不存在 | 不重试，进入人工修复 |
| permission | 工具或资源被拒绝 | 不绕过，升级审批 |
| capacity | 本地队列、磁盘、线程耗尽 | backpressure、降载 |
| provider outage | 上游大面积不可用 | 熔断、降级或备用提供商 |
| unknown | 未分类异常 | 少量保守重试后死信 |

错误对象应携带 `retryable`、`retry_after`、`provider`、`operation` 和安全的诊断信息，使恢复策略由结构化信号驱动。

## 14.9 退避、抖动与重试预算

指数退避的一个常见形式是：

```text
delay = min(cap, base * 2^attempt)
sleep = random(0, delay)  # full jitter
```

抖动避免大量任务同时恢复形成惊群。重试还必须受三个预算约束：

- 单任务最大尝试次数与总时长。
- 单依赖或单租户的重试速率。
- 系统总重试流量占比。

如果一次故障导致新请求 100 次、每次又自动重试 5 次，真正压力是 600 次。重试预算应把恢复流量限制为正常流量的一部分，并为用户主 lane 保留容量。

## 14.10 熔断、隔离与降级

熔断器避免对明显故障的依赖持续施压：

```text
CLOSED --failure threshold--> OPEN
OPEN --cooldown--> HALF_OPEN
HALF_OPEN --probe success--> CLOSED
HALF_OPEN --probe failure--> OPEN
```

熔断按“依赖+操作+凭证/区域”选择粒度。全局一个熔断器会让单租户错误拖垮所有请求，粒度过细又无法抑制系统性故障。

与熔断配套的还有：

- bulkhead：不同提供商、租户和工作类型使用独立容量池。
- timeout：每个外部调用都有截止时间。
- fallback：切模型或渠道前检查语义和权限是否等价。
- graceful degradation：保留查询与取消，暂停新后台工作。
- load shedding：队列过载时明确拒绝低优先级任务。

降级不能悄悄改变安全属性。高权限模型不可用时，不能自动切到一个缺少相同工具约束的执行环境。

## 14.11 并发 Lane：有序局部并行

把所有工作放进一个全局队列，会让长任务阻塞用户消息；把所有任务无限并发，又会产生竞态和资源耗尽。命名 lane 提供中间结构：

```text
main/session:<key>  max=1   同一会话严格串行
cron:<job_id>       max=1   默认防止作业重叠
heartbeat:<agent>   max=1   低优先级，可让步
background:<tenant> max=N   受租户配额约束
delivery:<channel>  max=M   服从平台限流
global              max=K   总体资源上限
```

同一 session lane 串行可防止上下文更新乱序；不同 session 可以并行；global lane 再限制总并发。lane 不是线程名字，而是顺序、公平性和资源预算的声明。

生产实现还要处理：

- 每租户加权公平，防止大客户饿死小客户。
- 优先级反转和长任务占槽。
- 队列长度、等待时间和取消传播。
- generation/epoch，阻止旧生命周期完成回调重新泵送新队列。
- 同一资源的并发写入冲突，必要时使用资源锁或乐观版本。

## 14.12 故障恢复与生命周期

服务启动时不能直接开始接新任务，应该先恢复：

```text
STARTING
  -> validate storage and credentials
  -> load schedules and recompute next fire
  -> reclaim expired schedule claims and relay pending schedule outbox
  -> reclaim expired leases
  -> scan pending outbox/deliveries
  -> restore circuit and rate-limit state where needed
  -> READY
```

优雅关闭则反向进行：停止领取新工作、停止产生新 Cron run、等待有界时间、持久化检查点、释放或让租约过期，最后关闭连接。强行把所有 `running` 标成 `queued` 会让仍在执行的旧 worker 与新 worker 重复写入。

恢复扫描必须可重复执行。reaper、outbox relay 和 schedule catch-up 自身也要幂等，并通过批量、游标和速率限制避免启动风暴。

## 14.13 可观测性与运行控制

至少记录以下指标：

- 各 lane 队列深度、最老任务年龄、等待与执行时间。
- Cron 触发延迟、misfire、重叠抑制和 run 成功率。
- heartbeat 最后成功时间、静默率和通知率。
- 每类错误、重试次数、退避时间和重试耗尽率。
- 熔断器状态、半开探测和降级次数。
- 投递延迟、重复、死信、Provider 接受率，以及渠道实际支持时的送达率和已读率。
- 租约过期、恢复任务数和不确定结果数。

每条链路使用 `job_id/run_id/task_id/attempt_id/delivery_id` 关联日志和 trace。控制面应允许暂停作业、取消任务、重放死信、限制租户、打开或关闭降级，但每个操作都需要审计。

## 14.14 生产约束

1. **时间不可靠**：执行时间点和日志统一存 UTC，但周期规则必须保留原始 IANA 时区，并持续按该时区求值。当地时间“每天 09:00”不能永久换算成固定 UTC，否则夏令时切换后会偏移。
2. **队列会积压**：必须有容量上限、过载策略和磁盘水位保护。
3. **取消是协作式的**：向工具和子进程传播取消信号，超时后再强制终止。
4. **结果可能不确定**：外部写调用超时后先回读，不要立即重做。
5. **凭证会轮换**：认证失败与服务故障分开，旧凭证任务不得无限重试。
6. **模型调用昂贵**：heartbeat 先运行确定性检查，只在有候选事件时调用模型。
7. **死信是工作队列**：需要负责人、原因、重放条件和保留期，不是错误坟场。

## 14.15 常见失败模式

| 失败 | 后果 | 修复 |
| --- | --- | --- |
| 进程内线程即任务系统 | 重启后任务失踪 | 持久任务记录、租约与恢复扫描 |
| Cron 回调直接做业务 | 无法独立重试和审计 | Cron 只生成带唯一槽位的 run |
| 一个 `done` 覆盖全链路 | 无法区分执行与投递 | 三个状态机和关联 ID |
| 所有异常立即重试 | 故障放大、费用失控 | 分类、退避、预算和熔断 |
| 固定退避无 jitter | 恢复时惊群 | full jitter 或 decorrelated jitter |
| 重试没有幂等键 | 重复下单、重复消息 | 业务幂等、唯一约束、outbox |
| 单一全局队列 | 主对话被后台任务阻塞 | session/lane 隔离与全局上限 |
| 无限 lane 并发 | 提供商限流、内存耗尽 | 分层配额和 backpressure |
| 重启即重排所有 running | 新旧 worker 双写 | 租约过期、epoch 与 fencing token |
| heartbeat 必须发消息 | 通知噪音 | 静默契约与抑制窗口 |

## 14.16 测试与验收

### 确定性单元测试

- 用 fake clock 覆盖时区、夏令时、misfire、jitter 和过期。
- 验证退避上限、`Retry-After`、重试预算和错误分类。
- 表驱动测试任务、投递与熔断状态转换。
- 幂等键在同一业务意图重试时稳定，在输入版本变化时改变。

### 并发与故障注入

- 多调度器同时 claim 同一时间槽，只创建一个 run。
- worker 在外部写成功后、保存结果前崩溃，恢复后不重复业务效果。
- 投递成功但 ack 丢失，重试后接收端只出现一次业务效果。
- 租约续期、过期回收和旧 generation 回调不会双重泵送。
- 提供商持续失败时熔断，恢复后只允许少量半开探测。
- 队列满时低优先级任务被明确拒绝，主 lane 仍可用。

### 恢复演练

在任务运行、Cron claim、结果提交和投递各阶段随机杀死进程，再启动恢复。验收标准不是“没有异常日志”，而是：没有任务无声丢失，没有不可解释重复副作用，没有跨 lane 串线，所有不确定结果都进入可见状态。

## 系统地图

```text
Gateway / API / Event / Clock
  -> Task or Schedule Request
  -> Durable Task Store
  -> Scheduler (slot claim, misfire, overlap, jitter)
  -> Lane Queue + Global / Tenant Limits
  -> Worker Lease
  -> Agent Harness / Deterministic Job
  -> Result Store
  -> Transactional Outbox
  -> Delivery Queue
  -> Channel / API
  -> Ack or Retry / Dead Letter

Runtime controls:
  Idempotency | Timeout | Backoff | Circuit Breaker | Bulkhead
  Cancellation | Recovery Scan | Metrics | Audit | Backpressure
```

## 共同结论

1. 调度、执行和投递是三个状态机，不能用一个完成标记代替。
2. Cron 负责按时间产生工作，heartbeat 负责周期巡检；二者都不天然构成目标反馈 Loop。
3. 至少一次投递是常见现实，恰好一次业务效果依赖幂等、唯一约束和事务边界。
4. 重试必须建立在错误分类、退避、抖动和总预算上，持续故障要熔断与降级。
5. Lane 同时表达顺序、公平和资源边界；同 session 串行、跨 session 并行、全局再限流。
6. 韧性不是“永不失败”，而是失败可见、状态可恢复、副作用不失控、系统能有界降级。

## 本章自检

1. 为什么 Cron 触发成功、Agent 执行成功和消息投递成功必须分开记录？
2. Heartbeat 与 Cron 的触发语义有什么区别？
3. 租约如何帮助恢复崩溃中的任务？为什么还需要 fencing token 或 generation？
4. 为什么至少一次投递要求业务幂等？
5. Transactional Outbox 解决什么窗口，不能解决什么问题？
6. 哪些错误应该重试，哪些错误重试只会扩大故障？
7. Session lane 与 global lane 分别保护什么？
8. 如何通过故障注入证明系统可恢复？

## 开放性问题

1. 当一次外部写调用超时且无法回读时，系统应该自动重试、请求人工确认还是标记为不确定？
2. Cron 错过 100 个时间槽时，如何根据业务语义选择跳过、合并或补齐，而不是只看技术配置？
3. 高优先级主对话与已经运行很久的后台任务争抢资源时，是否应该抢占？如何保存可恢复检查点？
4. 多租户共享模型配额时，公平、付费等级和紧急任务应如何共同决定 lane 权重？
5. 渠道不支持幂等发送和状态查询时，怎样定义诚实的投递 SLA？
6. 熔断器状态应只存在内存、跨实例共享，还是按区域分层？不同方案如何影响恢复风暴？
7. Heartbeat 的“值得打扰”能否被可靠评测？误报和漏报的成本如何进入策略？
8. 死信重放时，原任务代码、Prompt 或权限策略已经升级，应按旧版本还是新版本执行？
9. 当重试成本高于任务价值时，系统如何自动计算并停止恢复？

## 原文入口

### 本地教程与实现

- [claw0：心跳与 Cron](../../source/claw0/sessions/zh/s07_heartbeat_cron.md)
- [claw0：消息投递](../../source/claw0/sessions/zh/s08_delivery.md)
- [claw0：弹性](../../source/claw0/sessions/zh/s09_resilience.md)
- [claw0：并发](../../source/claw0/sessions/zh/s10_concurrency.md)
- [claw0：投递队列最小实现](../../source/claw0/sessions/zh/s08_delivery.py)
- [claw0：命名 lane 最小实现](../../source/claw0/sessions/zh/s10_concurrency.py)
- [learn-claude-code：错误恢复](../../source/learn-claude-code/s11_error_recovery/README.md)
- [learn-claude-code：后台任务](../../source/learn-claude-code/s13_background_tasks/README.md)
- [learn-claude-code：Cron Scheduler](../../source/learn-claude-code/s14_cron_scheduler/README.md)
- [Hermes：Cron](../../source/hermes-book/src/part5/ch15-cron.md)
- [Hermes：并发](../../source/hermes-book/src/part6/ch19-concurrency.md)
- [Hermes：生命周期](../../source/hermes-book/src/part6/ch20-lifecycle.md)
- [Hermes：运行时防御](../../source/hermes-book/src/part6/ch21-runtime-defense.md)
- [Hermes：测试](../../source/hermes-book/src/part6/ch22-testing.md)
- [hello-claw：架构总览中的泳道、heartbeat 与分层容错](../../source/hello-claw/docs/cn/build/chapter1/index.md)
- [hello-claw：消息循环](../../source/hello-claw/docs/cn/build/chapter5/index.md)

### 延伸资料

- [Amazon Builders' Library：Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Microsoft：Circuit Breaker pattern](https://learn.microsoft.com/azure/architecture/patterns/circuit-breaker)
- [Cloud Design Patterns：Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
