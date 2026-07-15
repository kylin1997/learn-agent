# 第 13 章：工程化、测试、可观测性与产品化

> 本章目标：把 Agent 从“能跑”推进到“能维护”。读完本章，你应该能设计测试分层、日志指标追踪、错误恢复、生命周期管理、配置体系、成本控制和产品评估机制。

## 13.1 Agent 工程化为什么更难

Agent 系统比普通后端更难测、更难观测、更难复现。原因是：

- 模型输出不完全确定。
- 上下文每轮变化。
- 工具调用有副作用。
- 外部平台和 MCP 会失败。
- 权限与沙箱影响执行路径。
- 多 Agent 和后台任务引入并发。
- 成本和延迟随 token 波动。

所以 Agent 工程化不是最后上线前再补，而是从第一天就要进入架构。

## 13.2 测试分层

Hermes 测试章节把复杂 Agent 的测试分成多层，很值得借鉴：

| 层级 | 测什么 |
| --- | --- |
| 单元测试 | prompt assembler、权限规则、token 估算、工具 schema |
| 集成测试 | Agent Loop、工具调用、上下文压缩、记忆召回 |
| 平台测试 | Gateway、渠道适配、投递队列、Cron |
| 端到端测试 | 用户任务从输入到完成的完整路径 |
| 稳定性测试 | 中断、超时、重试、恢复、并发 |
| 安全测试 | 权限绕过、prompt injection、敏感文件保护 |

不要只测最终文本。Agent 的正确性包含过程：

- 是否读取了必要文件。
- 是否调用了正确工具。
- 是否遵守权限。
- 是否运行验证。
- 是否正确压缩上下文。
- 是否避免重复失败路径。

## 13.3 测试隔离

Agent 测试必须隔离环境：

- 独立 home 目录。
- 独立 memory 目录。
- 独立 config。
- 独立 transcript。
- 禁止真实密钥。
- 网络和文件系统可控。
- 每个测试有超时。

否则测试会互相污染，尤其是 memory、session、cache 和配置。

一个好习惯是：测试目录本身就是架构地图。每个子系统都有对应测试目录。

## 13.4 Prompt 与行为回归

Prompt 变更也要测试。

可以维护一组固定任务：

```text
Case: 修改一个函数
期望:
  先读文件 -> 最小修改 -> 运行相关测试 -> 汇报验证

Case: 询问最新信息
期望:
  使用搜索 -> 引用来源 -> 标注日期

Case: 请求危险操作
期望:
  询问确认或拒绝
```

回归检查不一定全自动。学习阶段可以人工 review transcript。生产阶段可以用规则和验证模型辅助判定。

## 13.5 可观测性：Trace、Metric、Log

Alice 可观测性章节用 OTel 三信号说明 Agent 观测：

```text
Trace:
  一次用户请求经过哪些模型调用、工具调用、子 Agent、压缩、记忆召回。

Metric:
  token、延迟、成本、错误率、重试次数、压缩频率、工具成功率。

Log:
  结构化事件、权限决策、错误原因、投递状态。
```

Agent trace 应该能回答：

- 这次回答用了哪个模型？
- 注入了哪些 memory？
- 调用了哪些工具？
- 哪个工具失败了？
- 有没有触发 compact？
- token 花在哪里？
- 最终回复为什么这样生成？

没有可观测性，Agent 出错时只能猜。

## 13.6 隐私保护默认

可观测性和隐私有冲突。trace 越详细，越可能记录敏感信息。

默认策略：

- 日志记录结构化元数据，少记录原文。
- 对 prompt、tool result、memory 做脱敏。
- secret 不进 telemetry。
- 用户可关闭或导出。
- 本地开发优先本地日志。

可观测性要服务调试，不应该变成隐私黑洞。

## 13.7 错误恢复

`learn-claude-code` s11 把错误恢复归纳成几条路径：

- 输出被截断：继续生成。
- 上下文超限：压缩后重试。
- 临时故障：指数退避。
- provider 故障：fallback。
- 流式中断：保留部分结果并恢复。

关键原则：

```text
先分类，再恢复。
恢复有上限。
同一路径失败多次后换策略。
不要盲目重复同一操作。
```

错误恢复既是稳定性问题，也是用户体验问题。用户不应该因为一次网络抖动就丢掉整轮任务。

## 13.8 生命周期管理

常驻 Agent 有很多资源：

- 浏览器实例。
- 终端进程。
- MCP 连接。
- Gateway 平台连接。
- 后台任务。
- worktree。
- 临时文件。
- 数据库连接。

Hermes 生命周期章节强调：稳定性的第一层是资源能被正确关闭。

需要处理：

- SIGTERM / SIGHUP。
- 优雅关停。
- drain queue。
- close agent。
- 清理孤儿进程。
- worktree 年龄清理。
- 超时体系。
- doctor 诊断。

没有生命周期管理，Agent 跑久了就会资源泄漏。

## 13.9 配置体系

产品化 Agent 需要配置：

- 模型和 provider。
- 权限模式。
- 工具开关。
- MCP server。
- Skill。
- Gateway 渠道。
- Cron。
- 日志和 telemetry。
- 用户和项目规则。

配置要支持：

- 分层覆盖。
- include。
- 环境变量替换。
- SecretRef。
- 严格验证。
- 部分热重载。
- 配置诊断。

配置越灵活，越需要验证和可解释性。

## 13.10 成本与性能

Agent 成本主要来自：

- system prompt。
- 历史上下文。
- 工具结果。
- 记忆召回。
- 子 Agent。
- 压缩调用。
- 重试和 fallback。

性能优化不是简单“换快模型”，而是：

- Prompt cache 友好。
- 动态内容后置。
- 大结果落盘。
- 低成本模型做分类和摘要。
- 强模型只处理高价值任务。
- 并行独立工具调用。
- 背景任务不阻塞主对话。

这也连接第 4 章的模型路由和第 5 章的上下文预算。

## 13.11 产品评估

hello-claw 的应用场景点评给了一个很实用的思路：不要只说“这个 Agent 很强”，要按场景评分。

评估维度可以包括：

- 完成率。
- 准确性。
- 可控性。
- 响应速度。
- 成本。
- 安全风险。
- 用户打扰度。
- 可解释性。
- 维护成本。

不同场景权重不同。早间简报重视及时和简洁；代码审查重视准确和证据；客服重视一致性和安全；内容创作重视风格和可修改性。

## Hello-Agents 融合补充

`hello-agents` 第 12 章专门讨论智能体性能评估，补足了本章的评测体系。它提到的 BFCL 更偏函数调用能力评测，GAIA 更偏综合任务能力评测。两者提醒我们：Agent 评估不能只看最终回答像不像，而要分开看工具调用、信息检索、推理规划、执行可靠性和结果呈现。

可以把评估拆成四层：

```text
模型层：
  指令遵循、结构化输出、幻觉率、成本和延迟。

工具层：
  参数正确率、调用成功率、错误恢复、权限命中。

任务层：
  完成率、证据质量、步骤完整性、可复现性。

产品层：
  用户满意度、打扰度、可控性、维护成本。
```

Hello-Agents 的第 11 章 Agentic-RL 进一步说明，训练和优化应该建立在评估之上。SFT、LoRA、GRPO、奖励函数这些方法不是学习初期必须立刻动手的内容，但它们给出一个重要原则：如果没有可度量的任务、可复现的轨迹和可靠的奖励信号，所谓“让 Agent 更聪明”很容易变成调 prompt 的玄学。

Extra09 的踩坑经验强调 trace-first：先把模型输入、工具选择、上下文变化、错误恢复和最终输出记录下来，再谈优化。否则你看到的只是“这次结果不好”，却不知道是 prompt 问题、工具问题、上下文污染、模型选择问题，还是产品需求本身不清楚。

第 16 章毕业设计则从交付物角度补充工程规范：README、requirements、Notebook、项目说明、评测报告都应该成为项目的一部分。一个 Agent 项目是否成熟，不只看能不能跑，还要看别人能不能理解、复现、评估和继续改进。

## 13.12 最小工程化清单

第一版至少要有：

1. 结构化日志。
2. 每次模型调用记录 model、token、耗时、错误。
3. 每次工具调用记录工具名、权限结果、耗时、输出大小。
4. transcript 可导出。
5. 权限和安全测试。
6. prompt 行为回归案例。
7. 上下文压缩测试。
8. Gateway / Cron / queue 状态页或命令。
9. 配置校验。
10. 故障恢复策略和重试上限。

## 系统地图

```text
Agent Runtime
  -> Tests
  -> Trace / Metrics / Logs
  -> Error Recovery
  -> Lifecycle
  -> Config
  -> Product Evaluation
```

## 共同结论

1. Agent 工程化要测试过程，不只是测试最终文本。
2. 可观测性要覆盖模型、工具、记忆、压缩、子 Agent 和投递。
3. 错误恢复必须分类、有界、可降级。
4. 生命周期管理决定 Agent 能不能长期运行。
5. 产品化评估要按场景权衡，而不是泛泛比较“强不强”。

## 本章自检

1. Agent 测试为什么比普通软件测试更难？
2. Trace、Metric、Log 分别回答什么问题？
3. Prompt 行为回归应该测哪些行为？
4. 生命周期管理为什么是稳定性的第一层？
5. 产品评估为什么要按场景加权？

## 开放性问题

1. 对一个编码 Agent 来说，“正确完成任务”和“过程安全可控”哪个更重要？在什么情况下会改变排序？
2. 如果可观测性日志能帮助调试但可能包含敏感上下文，你会如何设计默认策略？
3. 什么时候应该为了降低成本使用弱模型，什么时候必须使用强模型？

## 原文入口

- [learn-claude-code s11: Error Recovery](../../source/learn-claude-code/s11_error_recovery/README.md)
- [learn-claude-code s20: Comprehensive Agent](../../source/learn-claude-code/s20_comprehensive/README.md)
- [Alice 方法论: 可观测性](../../source/Alice_methodology/chapters/13-observability.md)
- [Alice 方法论: 工程范式](../../source/Alice_methodology/chapters/15-engineering-patterns.md)
- [Hermes: Concurrency](../../source/hermes-book/src/part6/ch19-concurrency.md)
- [Hermes: Lifecycle](../../source/hermes-book/src/part6/ch20-lifecycle.md)
- [Hermes: Runtime Defense](../../source/hermes-book/src/part6/ch21-runtime-defense.md)
- [Hermes: Testing](../../source/hermes-book/src/part6/ch22-testing.md)
- [Harness Engineering Part7: 工程化章节](../../source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch25.md)
- [hello-claw 场景点评](../../source/hello-claw/docs/cn/adopt/lobster-review.md)
- [hello-agents Ch11: Agentic-RL](../../source/hello-agents/docs/chapter11/第十一章%20Agentic-RL.md)
- [hello-agents Ch12: 智能体性能评估](../../source/hello-agents/docs/chapter12/第十二章%20智能体性能评估.md)
- [hello-agents Ch16: 毕业设计](../../source/hello-agents/docs/chapter16/第十六章%20毕业设计.md)
- [hello-agents Extra09: Agent 应用开发实践踩坑与经验分享](../../source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md)
