# 第 18 章：生产工程、可观测性与产品迭代

> 一个 Agent 在演示中成功一次，只能证明路径存在；它在真实流量、外部故障、版本变化和隐私约束下仍能持续交付，才算进入生产。本章讨论如何把 Agent 建成可运行、可解释、可恢复、可演进的产品系统。

## 18.1 学习目标与边界

学完本章，你应该能够：

1. 用显式状态机管理一次任务从接收到终止的完整生命周期。
2. 设计与 Agent Loop 同构的 trace、log、metric，而不是只记录最终回答。
3. 为可用性、延迟、恢复和投递定义 SLI、SLO 与错误预算。
4. 把应用、Prompt、模型路由、工具契约、权限策略和数据模式纳入统一版本管理。
5. 拆解 token、成本和延迟，定位真正的资源消耗与用户等待。
6. 对不同故障采用有界重试、降级、恢复、补偿或人工接管。
7. 在不默认收集原始内容的前提下获得足够的诊断证据。
8. 把用户反馈、生产信号、版本发布和回滚连接成产品改进闭环。
9. 在受控分析域中监测高影响决策的分群差异、解释失败和申诉推翻，而不把敏感属性扩散到普通遥测。

本章不重复第 17 章的离线测试、任务集、评分器、对照实验和基准设计。第 17 章负责实验设计与因果性的质量判断：在控制变量、代表性样本和统计不确定性下回答“变化是否真的改善能力”。第 18 章负责发布执行与运行可靠性：回答“这个已决定发布的版本如何灰度、观测、满足 SLO、恢复和回滚”。两章的分工是：

| 问题 | 第 17 章 | 第 18 章 |
| --- | --- | --- |
| 新版本能力是否因变更而更好 | 评测集、对照实验与因果判断 | 执行灰度并观察运行结果，不单凭生产相关性判因果 |
| 某个输出是否正确 | 评分器、规则、人工标注与质量置信区间 | 记录结果、证据和用户反馈，触发回查 |
| 系统是否可靠 | 故障注入可作为测试 | 生命周期、SLO、告警、恢复 |
| 是否具备发布资格 | 离线质量与安全门槛 | 按既定策略执行发布、灰度、SLO 操作和回滚 |

离线评测是发布前证据，生产观测是发布后证据。二者共享版本号和轨迹标识，但不能互相替代。

## 18.2 核心原理：从一次调用转向一次可管理的运行

普通请求通常是“收到、处理、返回”。Agent 运行则可能跨越多轮模型调用、工具调用、权限确认、后台任务和子 Agent，还可能在进程重启后继续。因此，生产系统的基本单位不应只是 HTTP request，而应是 **run**：一次具有目标、预算、状态、版本和终止原因的可恢复执行。

### 18.2.1 运行状态机

```text
ACCEPTED -> QUEUED -> RUNNING -> VERIFYING -> COMPLETED
               ^          |           |             |
               |          |           |             v
               |          +-----------+------> DELIVERY_PENDING
               |                                  |
WAITING_USER --+                                  v
RETRY_WAIT -----+---------------------------> DELIVERING -> SUCCEEDED
RECOVERING -----+                                  |
     |                                             v
     +----> RUNNING / VERIFYING / DELIVERY_PENDING / FAILED

RUNNING / VERIFYING / DELIVERING -> RETRY_WAIT
RUNNING / VERIFYING / DELIVERING -> FAILED
任何非终态 -> WAITING_USER（需要人工决定时）或 CANCELLED
```

`COMPLETED` 表示业务产物已经持久化，但尚未承诺用户已收到；只有 outbox 对应的业务交付成功后才能进入 `SUCCEEDED`。如果产品契约允许“产物可查询即完成”，也要把该契约明确写入状态定义，不能在实现中临时改变。

挂起状态必须保存返回目标和截止条件：

- `WAITING_USER` 在授权或澄清到达后回到 `QUEUED`，由调度器重新取得执行权；拒绝、撤销或超时进入 `CANCELLED` 或带原因的 `FAILED`。
- `RETRY_WAIT` 保存 `retry_target_state`、`not_before` 和尝试预算；到期后回到 `QUEUED`，而不是从任意位置直接跳回模型循环。
- `RECOVERING` 根据 checkpoint 和未决副作用回到 `RUNNING`、`VERIFYING` 或 `DELIVERY_PENDING`；证据不足或状态损坏则进入 `FAILED`，高风险不确定状态转 `WAITING_USER`。
- `DELIVERING` 失败可以进入 `RETRY_WAIT`，但只重试 outbox 消息，不得重跑已经 `COMPLETED` 的业务步骤。

状态转换必须由确定性运行时负责，不能让模型仅用自然语言宣称“任务完成”。每次转换至少记录：

- `run_id`、`session_id`、`task_id`；
- 转换前后状态与时间；
- 触发者：用户、调度器、执行器、验证器或运维操作；
- 原因码和可公开的原因摘要；
- 当前 checkpoint 与配置版本；
- 剩余时间、token、费用和工具调用预算。

`WAITING_USER` 与 `RUNNING` 必须分开。用户两分钟后批准写文件，不应被计算成工具执行两分钟；同理，排队、模型首 token、完整生成、工具执行和投递也应分别计时。

### 18.2.2 资源生命周期

Hermes 的进程生命周期材料说明，长期运行的第一道防线不是更聪明的恢复算法，而是资源能被有序取得和释放。一个 run 可能持有：模型流、MCP 连接、浏览器、终端进程、数据库事务、临时目录、worktree、子 Agent 和遥测缓冲区。

建议把资源所有权写进结构，而不是散落在退出回调中：

```python
class RunScope:
    async def __aenter__(self):
        self.checkpoint = await state_store.open_run(self.spec)
        self.resources = ResourceRegistry()
        return self

    async def __aexit__(self, error_type, error, traceback):
        await self.resources.stop_accepting_new_work()
        await self.resources.drain(deadline_seconds=20)
        await state_store.save_final_checkpoint(self.checkpoint, error)
        await telemetry.flush(deadline_seconds=3)
        await self.resources.close_all()
```

优雅关停不是“等到所有事情自然结束”，而是有优先级和总期限的清理序列：

1. 停止接收新任务并把实例标记为 not-ready。
2. 取消尚未开始的低优先级工作。
3. 给正在运行的可安全步骤一个 drain 窗口。
4. 持久化 run、任务队列和幂等键。
5. 终止子进程、浏览器、MCP 和临时环境。
6. 刷新必要日志；超过期限则落盘，不能无限阻塞退出。

进程崩溃后，启动扫描不能把残留的 `RUNNING` 直接当成失败或成功，而要转为 `RECOVERING`，读取最后 checkpoint，再判断重放、补偿、等待人工确认还是终止。

### 18.2.3 多实例租约、心跳与 fencing

多实例环境不能只靠“发现旧 `RUNNING` 就接管”。网络分区或长暂停可能让旧 worker 仍在执行，两个实例同时恢复同一 run。状态存储需要为活动 run 保存 `lease_owner`、`lease_expires_at`、`state_version` 和单调递增的 `fencing_token`：

1. worker 通过 compare-and-swap（CAS）比较 `state_version`，只有租约空闲或已过期时才能取得 lease。
2. 成功取得 lease 时递增 `fencing_token`；心跳只延长当前 owner、当前 token 的租约。
3. 每次 checkpoint、状态转换和受保护的内部写入都携带 token；存储拒绝来自旧 token 的写入。
4. lease 丢失的 worker 立即停止推进，不得仅凭本地“任务还在跑”继续提交。
5. 新 owner 进入 `RECOVERING`，先核对 checkpoint、幂等记录和外部状态，再决定续跑。

```sql
UPDATE runs
SET lease_owner = :worker,
    lease_expires_at = :expires,
    fencing_token = fencing_token + 1,
    state_version = state_version + 1
WHERE run_id = :run_id
  AND state_version = :expected_version
  AND (lease_expires_at < :now OR lease_owner = :worker);
```

lease 防止长期并行占有，CAS 防止并发状态覆盖，fencing token 防止旧 owner 在暂停恢复后提交陈旧写入。三者仍不能自动约束不支持 token 的第三方系统；外部副作用还必须使用 operation ID、幂等键、状态查询或人工接管。心跳间隔、租约时长和时钟容差要一起设计，并用暂停、网络分区和重复恢复测试验证。

## 18.3 可观测性必须映射 Agent 的因果链

Alice 的可观测性章节和 Harness 的生产遥测分析都强调：Agent 的执行非线性、耗时长、归因困难。可观测性的目的不是“多记日志”，而是回答四个问题：发生了什么、为什么发生、影响了谁、下一步怎么处置。

### 18.3.1 Trace：还原一次运行

Span 层级应直接映射运行结构：

```text
run
├── interaction
│   ├── context_build
│   ├── llm_request
│   ├── tool
│   │   ├── blocked_on_user
│   │   └── execution
│   ├── checkpoint
│   └── delivery
├── subagent
│   └── ...child spans
└── verification
```

根 span 携带 `run_id` 和版本清单，子 span 携带 `parent_span_id`。模型调用还应记录 `caller`，例如 `main`、`compact`、`memory`、`classifier`、`subagent`、`verifier`。这样“费用为什么上涨”才能归因到压缩、记忆或子 Agent，而不是只看到总 token。

每个 span 记录状态和时间，不默认记录 Prompt、工具参数或工具结果原文。对于流式模型，至少区分：

- 排队时长；
- time to first token；
- 完整生成时长；
- 重试前后的 API 时长；
- 用户等待与系统执行时长；
- 成功、取消、超时或错误原因。

### 18.3.2 Log：记录离散事实

日志适合表达状态转换、策略决策和异常。使用稳定事件名与结构化字段：

```json
{
  "event": "tool.completed",
  "timestamp": "2026-07-17T12:00:00Z",
  "run_id": "run_01...",
  "trace_id": "tr_01...",
  "tool": "read_file",
  "permission": "allow",
  "duration_ms": 43,
  "output_bytes": 8120,
  "result": "success",
  "app_version": "0.4.1",
  "prompt_version": "research-agent@7",
  "policy_version": "project-readonly@3"
}
```

错误日志要有稳定的 `error_code` 和 `retryability`，不要依赖不断变化的错误消息做统计。高基数字段如用户 ID、路径、完整工具名和 Prompt 哈希不应成为 metric label；必要时留在受控日志或 trace 中。

### 18.3.3 Metric：观察群体趋势

Metric 用于聚合和告警，而不是复原单次任务。最小集合可以分成四组：

| 维度 | 指标示例 |
| --- | --- |
| 流量 | 接收 run 数、并发 run、队列深度、按入口分类的请求率 |
| 可靠性 | 成功终止率、恢复率、投递成功率、工具错误率、重复副作用拦截数 |
| 延迟 | 接受到首个可见响应、TTFT、工具执行、用户等待、端到端完成时长 |
| 资源 | input/output/cache token、费用、上下文占用、重试开销、子 Agent 数 |
| 决策治理 | 按批准的低基数分片统计误拒、误放、人工升级、申诉、推翻和解释失败率 |

指标必须有分母。例如只看“失败 100 次”没有意义；要同时知道总调用量和版本分布。分位数通常比平均值更能暴露长尾，至少观察 p50、p95 和 p99。

决策治理指标需要更严格的数据边界。受保护属性不能成为公开、高基数标签，也不应进入每条普通业务日志；可以在受控分析域中用最小必要字段做周期聚合，并设置小样本抑制、访问审计和保留期。线上差异是调查和回滚信号，不会自动说明成因，更不能让系统自行修改阈值来“修平”仪表盘。

### 18.3.4 三信号如何配合

```text
Metric 告诉你：v0.4.1 的投递失败率升高
  -> Trace 告诉你：失败集中在 delivery span，前序执行已成功
  -> Log 告诉你：平台返回 rate_limited，第三次退避后超出投递期限
  -> 状态存储告诉你：结果仍可重新投递，不应重跑有副作用的任务
```

三者共享 `run_id`、`trace_id`、版本和原因码，才能从趋势下钻到事实。

## 18.4 SLI、SLO 与错误预算

“尽量稳定”无法指导取舍。Google SRE 将常见 SLI 表达为 `good events / eligible events`，并要求明确测量方式和窗口。Agent 的 SLO 要覆盖用户可感知的接收、响应、恢复和投递链，而不只是模型 API uptime。

### 18.4.1 先定义 eligible events

每个 SLI 都要单独定义分母。`eligible run` 不是“所有看起来方便统计的 run”，而是满足该 SLI 适用契约的运行。例如交互响应 SLI 可以只包含交互入口、通过输入校验且确实要求即时响应的 run；投递 SLI 只包含产生了可投递 Artifact 的 run。

可以排除并单独报告：明确标记的测试或影子流量、在进入系统前即被 schema 拒绝的无效输入、用户在任何执行发生前主动取消的请求，以及契约预先声明的维护事件。不能排除：系统超时、内部限流、恢复失败、错误授权判断、依赖故障或运行后用户因系统过慢而取消。这些正是服务可靠性的一部分。

每份 SLI 规范至少写清：

- 用户与入口、eligible 条件、good 条件和失败条件；
- 测量点是客户端、边缘、服务端还是 outbox；
- 统计窗口是滚动 28 天、自然月还是其他固定窗口；
- 全量还是采样、采样概率、分层方式和权重恢复方法；
- 延迟阈值、分位数、低流量处理和数据迟到规则；
- 按版本、任务类型和风险等级的切片，但不把高基数字段做标签。

生产 SLO 优先全量计数。流量过大必须采样时，使用稳定的 `run_id` 确定性采样并按任务类型、版本和错误类别分层；分母、分子使用同一采样规则并报告置信区间。所有高风险副作用、终态丢失和安全事件不采样。

### 18.4.2 建议的 SLI

| SLI | 定义 |
| --- | --- |
| 接收可靠性 | 持久化入队成功的 eligible intake events / eligible intake events |
| 恢复点新鲜度 | 在 checkpoint 期限内完成持久化的 eligible long-run intervals / eligible long-run intervals |
| 终止完整性 | 在终止期限内进入明确终态的 eligible runs / eligible runs |
| 结果投递率 | 在投递期限内由 outbox 确认送达的 eligible artifacts / eligible artifacts |
| 交互响应延迟 | 在阈值内产生首个有意义响应的 eligible interactive runs / eligible interactive runs |
| 恢复时延 | 在阈值内从 lease 过期恢复到可推进状态的 eligible recovery events / eligible recovery events |

“回答正确率”通常属于第 17 章的质量评测，不宜直接伪装成高频在线 SLO。生产中可以使用用户纠正率、任务撤销率或验证失败率作为代理信号，但必须承认它们不是语义正确性的完整测量。

### 18.4.3 SLO 示例

以下数字只是设计样例，必须根据场景、风险和成本校准：

```yaml
slo:
  window: "rolling_28d"
  intake_durable:
    eligible: "valid non-test intake events"
    good: "durably queued within 1s"
    target: ">= 99.9%"
    sampling: "100%"
  first_visible_response:
    eligible: "interactive runs not paused by user before first response"
    good: "meaningful status or content within 3s"
    target: ">= 95%"
    sampling: "deterministic 20%, stratified by version and task class"
  completed_delivery:
    eligible: "artifacts whose channel contract requires push delivery"
    good: "outbox receipt confirmed within 60s"
    target: ">= 99.5%"
    sampling: "100%"
  recovery:
    eligible: "expired leases with a valid checkpoint"
    good: "new fenced owner reaches a resumable state within 5m"
    target: ">= 99%"
    sampling: "100%"
```

对比例型 SLO，错误预算是窗口内允许的 bad eligible events。告警与发布策略还要定义 burn rate、观察窗口和最低样本量，避免低流量下一个事件造成没有上下文的剧烈波动。当天样本不足时展示原始计数，不伪造稳定百分比。

**重复副作用不是可消费的错误预算。** 对受保护操作，`duplicate_side_effect = 0` 是硬安全不变量：一旦发生立即停止相关写路径、保全证据并进入事故处理，不能因为“月度预算还够”继续运行。错误预算适用于可接受的服务不可靠性，不适用于权限越界、数据泄漏、重复付款等禁止事件。

当错误预算消耗过快，团队应暂停扩大流量或高风险功能，优先修复可靠性。错误预算不是给失败找借口，而是把“继续发功能还是先修系统”的争论变成可观察的决策。

## 18.5 配置、契约与版本必须共同可追溯

Agent 行为不只由代码决定。相同代码配上不同 Prompt、模型、工具 schema、Skill、权限规则或检索索引，可能产生完全不同的路径。因此每次 run 都应绑定不可变的 `RuntimeManifest`：

```yaml
runtime_manifest:
  app: "0.4.1+git.a1b2c3d"
  dependency_lock: "sha256:..."
  runtime_environment:
    os_image: "sha256:..."
    python: "3.13.5"
  resolved_model:
    route: "balanced@4"
    provider: "provider-a"
    model: "model-x-2026-06-01"
    endpoint_region: "ap-southeast"
    parameters_hash: "sha256:..."
  prompts:
    system_hash: "sha256:..."
    planner_hash: "sha256:..."
  skills:
    catalog_hash: "sha256:..."
    loaded: ["repo-research@2:sha256:..."]
  tool_schemas_hash: "sha256:..."
  permission_policy: "project-readonly@3"
  corpus_snapshot:
    repository_commit: "a1b2c3d"
    rag_index: "project-docs@2026-07-17:sha256:..."
  memory_schema: 2
  trace_schema: 3
  feature_flags:
    parallel_search: "treatment"
```

### 18.5.1 配置加载原则

Hermes 的配置与 Profile 设计提供了可迁移的顺序：默认值、环境与 SecretRef、用户配置、项目配置、运行时覆盖。生产实现还应满足：

- 合并规则明确，最终值可解释；
- 未知键和类型错误在启动或发布阶段失败；
- secret 与普通配置分离，日志中只出现引用和状态；
- profile 隔离目录、会话、记忆和缓存，防止实例串扰；
- 迁移可重复、可回滚，并记录 schema version；
- 只有经过声明的安全键可以热重载。

不要让一次 run 中途悄悄换 Prompt 或权限策略。热更新应对新 run 生效；长任务若必须迁移，先 checkpoint，再显式记录旧、新 manifest 和迁移结果。

### 18.5.2 发布演进

生产演进可以从低复杂度开始：

```text
本地单进程
  -> 独立状态库与结构化日志
  -> API + worker + durable queue
  -> 多实例 + 分布式 trace + 统一配置
  -> 多租户隔离 + 灰度 + 自动回滚门槛
```

每一步都只在现有瓶颈出现时增加。单进程尚未建立 run 状态机时，提前引入复杂编排平台只会把不可见状态分散到更多机器。

发布流程至少包含：配置静态校验、数据库迁移检查、离线质量门槛、影子或小流量灰度、SLO 观察窗口、扩大流量、可执行回滚。Prompt 和工具契约也要走同一流程，不能作为“文案修改”绕过版本控制。

## 18.6 成本与延迟是一张因果账本

成本优化不能只看每次模型报价，延迟优化也不能只换快模型。一次 run 的资源账本必须覆盖系统实际承担或转嫁的资源：

```text
总成本 = 模型 token 与缓存
       + 工具/API 调用
       + 搜索、RAG 与数据许可
       + CPU/GPU/浏览器/沙箱计算
       + 数据库、对象与向量存储
       + 网络出口与消息投递
       + trace/log/metric 采集、传输和保留
       + 人工审批、复核、支持与事故处置

端到端延迟 = 从 eligible 起点到用户承诺完成点的关键路径 wall-clock
累计工作时长 = 所有模型、工具、子 Agent、验证和恢复 span 时长之和
```

并行步骤的端到端延迟取关键路径，不能把所有 span 相加；相加得到的累计工作时长用于解释资源消耗和并行度。端到端延迟还应分开报告系统可控时长、排队、用户暂停和投递等待。建议同时记录 `total_api_duration` 与 `total_api_duration_without_retries`，否则供应商抖动造成的重试会被误认为正常推理变慢。还要单列 cache read/create token、工具结果字节数和上下文压缩前后大小。

优化顺序应从消除浪费开始：

1. 阻止无进展循环和重复工具调用。
2. 大结果落盘，按需回读，避免每轮重复进入上下文。
3. 稳定 Prompt 前缀以提高缓存命中。
4. 对分类、抽取、压缩等窄任务使用合适的小模型。
5. 并行真正独立且只读的工具，写操作保持串行。
6. 把非关键记忆整理、分析和遥测导出移出交互关键路径。
7. 超过预算时降级结果深度、请求用户选择或停止，而不是静默超支。

成本标签应使用 `caller`、任务类型、模型路线和版本，不要使用用户文本。产品层关注的是“每个成功交付的成本”和“为一次失败花了多少”，而不只是 token 总量。

## 18.7 错误恢复：先分类，再恢复

`learn-claude-code` 的错误恢复和 Hermes 的运行时防御共同给出一个原则：恢复策略必须与错误类别匹配，并且有界。

| 类别 | 例子 | 默认动作 |
| --- | --- | --- |
| 暂时性外部错误 | 429、过载、短暂断网 | 带抖动退避，受 deadline 限制 |
| Provider 故障 | 连续过载、区域不可用 | 切换兼容 fallback，并记录行为差异风险 |
| 上下文错误 | 超窗、输出截断 | 压缩或 continuation，限制连续次数 |
| 工具输入错误 | schema 不合法、参数缺失 | 返回结构化错误给循环，只允许修正后重试 |
| 权限或策略拒绝 | 敏感写入、越权路径 | 不重试；等待用户或终止 |
| 副作用不确定 | 请求超时但外部可能已写入 | 先用幂等键或查询确认，禁止盲重放 |
| 数据损坏 | checkpoint 不完整、schema 不兼容 | 隔离 run，保留证据，人工修复或安全终止 |

重试要同时受尝试次数、累计时间、费用和 no-progress 检测约束。恢复路径本身也可能失败，因此要记录 `recovery_attempt` 和最终 `stop_reason`。

### 18.7.1 幂等、checkpoint 与补偿

有副作用的工具调用在执行前生成 `operation_id`，外部系统支持时把它作为幂等键；不支持时，保存“准备执行”记录和外部对象标识。checkpoint 至少包含：已完成步骤、待办、工具调用结果引用、预算、manifest 和未决副作用。

补偿不是把时间倒流，而是执行一个语义上的修复动作。例如创建了错误草稿，可以删除草稿；真实付款则可能只能发起退款。无法可靠补偿的操作必须提高审批等级。

## 18.8 隐私保护默认的观测体系

观测数据会同时包含用户内容、工具参数、文件路径、密钥、记忆和内部推理线索。默认策略应是“元数据足够、内容最少”：

- 默认不记录 Prompt、工具输入输出和 memory 原文；
- 字符串字段使用允许列表，未知字段拒绝进入外部遥测；
- MCP 服务器名、路径等高风险标识优先分桶或删除；确需跨事件关联时，使用受控 token 映射，或按租户与用途隔离密钥的 HMAC，并支持轮换；
- secret 在事件产生前脱敏，不能依赖下游清洗；
- 详细诊断由用户显式开启，限定 run、期限和访问者；
- 本地落盘同样设置权限、保留期、容量上限和删除机制；
- trace 导出失败可短期落盘重传，但不得因此保存本不该收集的内容；
- 支持用户查看、导出和删除与其相关的观测记录。

普通哈希不是匿名化：低熵用户名、路径、工具名可以被字典反推，相同哈希还会造成跨数据集关联。HMAC、tokenization 和分桶只能降低暴露面，不能把敏感数据自动变成非敏感数据；映射表、密钥、伪名化字段及其备份仍按原数据等级治理，应用访问控制、用途限制、保留期和删除规则。不同租户、环境和分析目的使用不同的 HMAC 域，避免跨域拼接用户轨迹。

实时告警通道与长期分析通道可以分层：前者只接收策展后的核心事件，后者接收经过治理的更多元数据。两个通道都应有远程熔断开关，以便发现泄漏风险时先停止导出。

## 18.9 从反馈到版本的产品闭环

Alice 的快速发布与共建材料展示了一个关键事实：产品迭代速度取决于完整反馈链路，而不只是写代码速度。Agent 可以辅助整理反馈，但不能替代产品责任人判断问题、风险和优先级。

```text
用户反馈 / 支持工单 / 生产信号
  -> 绑定 run_id、版本和场景
  -> 聚类：缺陷、需求、误解、性能、风险
  -> 读取轨迹与代码，形成可证伪假设
  -> 修复或实验
  -> 第 17 章离线评测门槛
  -> 小流量灰度
  -> 观察 SLO、成本、延迟与反馈
  -> 扩大、修改或回滚
  -> 通知反馈者并沉淀决策记录
```

不要根据单次差评自动修改 Prompt。先判断是能力缺口、交互预期、工具故障、数据问题、权限阻塞还是需求本身不成立。生产指标也不能替代用户研究：没有点击“差评”可能只是用户已经离开。

每个版本需要一份可关联的 change record：假设、受影响场景、离线证据、灰度范围、监控指标、回滚条件、责任人和最终结论。这样失败实验也能成为资产。

### 18.9.1 Annotation Registry：生产侧只负责可靠采集与交接

生产系统要把反馈绑定到可复现对象，而不是把自由文本直接送进 Prompt 优化器。一个最小 Annotation 记录包含：

```yaml
annotation_id: ann-204
run_id: run-881
target: artifact:report-v3
label: unsupported_claim
evidence_refs: [trace:span-19, claim:c-7]
reporter_role: user
consent_scope: quality_evaluation
privacy_state: pending_review
adjudication_state: unreviewed
created_at: 2026-07-21T10:00:00Z
```

Registry 维护 `captured -> quarantined -> reviewed -> adjudicated -> exported | rejected | deleted` 状态，并记录每次用途变化。生产侧负责身份、关联、权限、保留期和删除，不负责宣布标注是真值。

```text
Production / 第 18 章
  采集事件与 Annotation，绑定 run 和版本，隔离敏感内容
                |
                v
Evaluation / 第 17 章
  脱敏复核、仲裁、补齐可复现 case，晋升回归资产
                |
                v
Evolution / 第 19 章
  归因、生成最小候选、独立验证、审批与发布
                |
                v
Production / 第 18 章
  Shadow、Canary、SLO 观察、晋升或回滚
```

同一条 Annotation 可以被拒绝、修订或因授权撤回而删除。导出到评测或改进系统时只传递允许用途所需的最小字段和受控内容引用；不能因为它已经进入内部 Registry 就扩大数据使用范围。

## 18.10 最小生产骨架

```text
agent-service/
├── runtime/
│   ├── controller.py       # 状态转换、预算、停止条件
│   ├── lifecycle.py        # drain、close、recover
│   └── manifest.py         # 不可变运行版本清单
├── state/
│   ├── runs.py             # run/checkpoint 持久化
│   ├── leases.py           # heartbeat、CAS、fencing token
│   └── idempotency.py      # 副作用幂等记录
├── telemetry/
│   ├── tracing.py          # span 与上下文传播
│   ├── events.py           # 结构化事件 schema
│   ├── metrics.py          # 低基数指标
│   └── privacy.py          # 允许列表、脱敏、保留策略
├── recovery/
│   ├── classify.py         # 错误分类
│   └── policies.py         # retry/fallback/compensate/escalate
├── delivery/
│   └── outbox.py           # 完成与投递解耦
├── config/
│   ├── schema.py
│   └── migrations/
└── tests/
    ├── lifecycle/
    ├── recovery/
    ├── telemetry/
    └── rollout/
```

最小实现不需要先搭建庞大平台。SQLite 或 PostgreSQL 保存 run 和 outbox，JSON 结构化日志写本地，OTel span 输出到开发后端，几个核心 metric 暴露给监控系统，就足以验证设计。

## 18.11 生产约束与常见失败

### 约束

- 模型和外部工具都可能变慢、限流或改变行为。
- 运行可能跨进程、跨版本，状态必须外置。
- 高风险副作用不能靠“重试应该没事”处理。
- 遥测本身有成本、延迟和故障，不能阻塞主路径。
- 多实例会带来并发、重复消费和时钟偏差。
- 用户删除数据后，日志、备份和分析副本也要遵守策略。

### 失败模式

1. **只记录最终回答**：无法判断错在模型、上下文、工具还是投递。
2. **把等待审批算进工具耗时**：错误优化工具，忽略交互阻塞。
3. **日志字段随意生长**：指标基数爆炸，并泄漏路径或用户文本。
4. **代码有版本，Prompt 没版本**：生产回归无法复现。
5. **所有错误都指数退避**：权限拒绝和副作用不确定也被重复执行。
6. **完成即投递**：渠道失败导致已完成任务被整体重跑。
7. **灰度只看错误率**：成本、长尾延迟或用户撤销率已经恶化。
8. **详细日志永久开启**：调试便利变成持续隐私风险。
9. **遥测同步发送**：观测系统故障拖垮用户请求。
10. **反馈自动变需求**：局部声音推动系统向错误方向优化。
11. **租约过期即安全接管**：没有 CAS 与 fencing，旧 worker 恢复后覆盖新状态。
12. **清洗 SLO 分母**：把内部超时、依赖故障或运行后取消排除出 eligible events，得到虚假可靠性。
13. **把禁止事件放进错误预算**：重复副作用或越权写入被当成“可接受的 0.1%”。
14. **普通哈希冒充匿名化**：低熵字段可反推，同值还可跨租户关联。
15. **只记录模型路线**：实际 provider、模型参数、Prompt/Skill、索引和依赖环境无法复现。

## 18.12 测试与验收

本章验收关注生产机制，而不是重复任务质量评分。

### 生命周期与恢复

- 在模型流、工具执行、等待审批、验证和投递阶段分别终止进程，重启后状态正确。
- `WAITING_USER`、`RETRY_WAIT`、`RECOVERING` 能按保存的返回目标进入合法状态，拒绝、超时和不可恢复错误进入明确终态。
- 优雅关停在总 deadline 内完成，关键 checkpoint 已持久化，资源无孤儿。
- 同一副作用消息被重复投递时，只产生一次外部写入。
- stale `RUNNING` 能转入 `RECOVERING`，不会被误报为成功。
- 两个 worker 竞争过期 lease 时只有一个 CAS 成功；旧 fencing token 的 checkpoint 和内部写入全部被拒绝。
- 暂停旧 worker、让新 worker 接管、再恢复旧 worker的故障注入不会产生双推进。

### 观测与隐私

- 任意失败 run 可由 `run_id` 找到 trace、版本、错误码和最后 checkpoint。
- trace 中用户等待与实际执行分离，父子 Agent 链路完整。
- metric label 通过基数检查，不包含用户文本、路径或随机 ID。
- 默认日志不包含 Prompt、secret、文件内容和工具结果原文。
- 普通哈希字段不能通过隐私检查；HMAC 必须按租户与用途域隔离并验证轮换和删除流程。
- 详细诊断到期自动关闭，遥测关闭或导出失败不影响主任务。

### SLO、成本与发布

- 仪表盘能展示 SLI 的 good、eligible、bad 原始计数、窗口、采样规则、置信区间和版本分布。
- eligible 规则测试证明系统超时、依赖故障和运行后取消不会被错误排除；高风险事件保持全量。
- 告警基于错误预算消耗或持续趋势，而非单次波动。
- 每个 run 能拆分模型、工具、检索、计算、存储、网络、遥测和人工成本；关键路径延迟与累计工作时长分别报告。
- RuntimeManifest 能解析到实际 provider/model/参数、Prompt/Skill 哈希、工具 schema、语料/索引快照和依赖环境。
- 新 Prompt、策略、Skill、索引或工具 schema 可灰度并一键回滚到旧 manifest。
- 投递故障只重试 outbox，不重新执行已完成的副作用步骤。
- duplicate side effect、越权写入和数据泄漏触发硬不变量事故流程，不被错误预算吸收。

### 产品闭环

- 用户反馈可在授权范围内关联 run 和版本。
- 每个改进项有假设、证据、灰度指标和回滚条件。
- 版本扩大或回滚有决策记录，反馈者能看到处理状态。

## 18.13 系统地图

```text
Inputs
  User / Channel / Cron
        |
        v
Run Control Plane
  State Machine -> Lease / Heartbeat / CAS / Fencing
        |                |
        v                v
  Budget -> Checkpoint -> Stop / Recover
        |                         |
        v                         v
Agent Runtime ----------------> Outbox / Delivery
  Model / Tool / Memory / Subagent / Verifier
        |
        v
Observability Plane
  Trace + Structured Log + Low-cardinality Metric
        |
        +-> SLI / SLO / Error Budget / Alert
        +-> Cost and Latency Attribution
        +-> Privacy Filter / Sampling / Retention
        |
        v
Product Loop
  Feedback -> Hypothesis -> Offline Gate -> Canary
           -> Observe -> Promote / Rollback -> Decision Record

Every node is bound to RuntimeManifest and run_id.
```

## 18.14 共同结论

1. 生产 Agent 的基本单位是可恢复的 run，而不是一次模型请求。
2. trace、log、metric 必须与 Agent Loop 同构，并共享运行与版本标识。
3. SLO 要覆盖接收、响应、恢复和投递，并对 good/eligible、窗口和采样做可审计定义；禁止事件不是错误预算。
4. 多实例恢复需要 lease、heartbeat、CAS 和 fencing token，外部副作用仍需幂等或对账。
5. 代码、实际 provider/model/参数、Prompt、Skill、工具契约、索引语料和依赖环境必须共同版本化。
6. 总成本要覆盖模型之外的工具、检索、计算、存储、网络、遥测和人工；关键路径延迟与累计工作时长分开。
7. 错误恢复必须先分类、后处置，并用幂等、checkpoint 和补偿保护副作用。
8. 可观测性默认收集元数据；哈希不等于匿名化，伪名化数据继续按敏感数据治理。
9. 产品反馈只有经过第 17 章的实验与质量判断，再由本章执行灰度、SLO 操作和回滚，才构成真正闭环。
10. Annotation Registry 负责可靠采集、关联和治理，不负责自动修改 Agent；回归资产和改进候选分别由第 17、19 章产生。
11. 高影响决策的公平性、解释失败和申诉推翻要进入受控生产监测，但线上差异只能触发调查、降级或回滚，不能自动替代规范性裁决。

## 18.15 本章自检

1. 为什么 run 比 request 更适合作为生产 Agent 的生命周期单位？
2. `WAITING_USER` 为什么不能继续算作工具执行时间？
3. trace、log、metric 分别最适合回答什么问题？
4. 哪些在线信号是质量代理，而不是语义正确性的直接测量？
5. 为什么 Prompt、工具 schema 和权限策略都要进入版本清单？
6. 如何避免进程恢复时重复执行已经生效的外部写入？
7. 为什么遥测导出失败不应阻塞主任务？
8. 一条用户反馈进入开发前，还需要补齐哪些证据？
9. lease、CAS 和 fencing token 分别解决什么竞争问题？
10. 为什么重复副作用不能作为普通 SLO 的 bad event 消耗错误预算？

## 18.16 开放性问题

1. 长达数小时、需要多次人工审批的 Agent，SLO 应按整次任务还是按阶段定义？
2. 当 fallback 模型能提高可用性却可能改变行为质量时，应如何设置切换门槛？
3. 对无法提供幂等键的第三方工具，怎样证明一次超时操作到底有没有生效？
4. 详细 trace 对排障很有价值，但用户内容不能默认记录，如何设计一次性授权和最小披露？
5. 当错误预算充足但每个成功任务的成本持续上升，是否应该阻止发布？
6. Prompt 热更新应该立即作用于长任务，还是固定到 run 结束？迁移责任由谁承担？
7. 如何区分用户没有反馈是“满意”、 “没发现问题”还是“已经放弃”？
8. 多 Agent 并行时，父任务的 SLO 应如何吸收子任务的取消、部分成功和长尾？
9. 哪些观测字段应该成为跨框架标准，哪些应保留为产品内部实现？
10. 用户撤回数据授权后，已由该 Annotation 触发但尚未发布的改进候选应如何处置？

## 18.17 原文入口

### 本地来源

- [AI Agents in Action（第二版）：第 7 章，Trace、实验与 Annotation 反馈](../../source/ai-agents-in-action-2nd-edition-cn/cn-book/7.通过评估与反馈构建稳健的智能体.md)
- [深入理解 AI Agent：第 6 章 Agent 评估、成本与运行环境](../../source/ai-agent-book/book/chapter6.md)
- [30 Agents：第 4 章，部署、熔断与公平性审计](../../source/30-Agents-Every-AI-Engineer-Must-Build/chapter04/ch04_agent_deployment.ipynb)
- [30 Agents：第 12 章，公平性监测与解释失败](../../source/30-Agents-Every-AI-Engineer-Must-Build/chapter12/ch12_01_ethical_reasoning_agent.ipynb)

- [Alice 方法论：可观测性](../../source/Alice_methodology/chapters/13-observability.md)
- [Alice 方法论：十二个可迁移的工程范式](../../source/Alice_methodology/chapters/15-engineering-patterns.md)
- [Alice：一个月 140 个版本](../../source/Alice_methodology/blog/blog-07-rapid-release.md)
- [Alice：共建](../../source/Alice_methodology/blog/blog-06-co-building.md)
- [Hermes：配置与 Profiles](../../source/hermes-book/src/part6/ch17-config-profiles.md)
- [Hermes：模型抽象与成本追踪](../../source/hermes-book/src/part6/ch18-model-abstraction.md)
- [Hermes：进程与资源生命周期管理](../../source/hermes-book/src/part6/ch20-lifecycle.md)
- [Hermes：运行时防御与容错](../../source/hermes-book/src/part6/ch21-runtime-defense.md)
- [learn-claude-code s11：错误恢复](../../source/learn-claude-code/s11_error_recovery/README.md)
- [learn-claude-code s20：综合 Agent](../../source/learn-claude-code/s20_comprehensive/README.md)
- [Harness Engineering：驾驭工程原则](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch25.md)
- [Harness Engineering：可观测性工程](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch29.md)
- [Claude Code Analysis：用户数据与使用](../../source/claude-code-analysis/analysis/02-user-data-and-usage.md)
- [Claude Code Analysis：隐私规避](../../source/claude-code-analysis/analysis/03-privacy-avoidance.md)
- [Hello-Agents Extra09：Agent 应用开发实践踩坑与经验](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)

### 外部一手资料

- [Google SRE Book：Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE Workbook：Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE Book：Production Services Best Practices](https://sre.google/sre-book/service-best-practices/)
- [OpenTelemetry：Signals](https://opentelemetry.io/docs/concepts/signals/)
