# Agent 学习方案

本方案基于 `source/` 下 9 份教程整理，目标是覆盖所有内容，同时把重复章节合并成一条可执行的学习路线。

## 总体策略

学习路线分为 10 个阶段。每个阶段包含三件事：

- 读：阅读对应教程章节。
- 做：实现一个最小可运行机制。
- 对照：比较不同教程对同一主题的设计取舍。

多语言重复内容以中文和主线版本为准；旧版轨道作为对应关系参考，不重复安排。

## 阶段 1：Agent 基础心智与系统地图

读：

- `source/learn-claude-code/README-zh.md`
- `source/Alice_methodology/chapters/00-preface.md`
- `source/Alice_methodology/chapters/01-philosophy.md`
- `source/Alice_methodology/chapters/02-architecture.md`
- `source/hermes-book/src/part1/ch01-design-bets.md`
- `source/hermes-book/src/part1/ch02-repo-map.md`
- `source/easy-langent/docs/guide/chapter1.md`
- `source/hello-agents/README.md`
- `source/hello-agents/docs/chapter1/第一章 初识智能体.md`
- `source/hello-agents/docs/chapter2/第二章 智能体发展史.md`
- `source/hello-claw/docs/cn/build/chapter1/index.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch01.md`

目标：

- 建立 Agent = Model + Harness 的心智模型。
- 理解 Agent Loop、工具、上下文、权限、记忆、渠道、运行时之间的关系。
- 形成一张本项目自己的 Agent 能力地图。

产出：

- 一页系统地图笔记。
- 一张术语表：Agent Loop、Harness、Tool、Skill、MCP、Memory、Gateway、Permission。

## 阶段 2：Agent Loop 与工具调用

读：

- `source/learn-claude-code/s01_agent_loop/README.md`
- `source/learn-claude-code/s02_tool_use/README.md`
- `source/learn-claude-code/s03_permission/README.md`
- `source/learn-claude-code/s04_hooks/README.md`
- `source/claw0/sessions/zh/s01_agent_loop.md`
- `source/claw0/sessions/zh/s02_tool_use.md`
- `source/Alice_methodology/chapters/03-agent-loop.md`
- `source/Alice_methodology/chapters/04-tool-system.md`
- `source/hermes-book/src/part2/ch03-request-journey.md`
- `source/hermes-book/src/part2/ch04-aiagent-core.md`
- `source/hermes-book/src/part3/ch06-tool-system.md`
- `source/hermes-book/src/part3/ch07-tool-profiles.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch02.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch03.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch04.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part1/ch04b.md`
- `source/claude-code-analysis/analysis/01-architecture-overview.md`
- `source/claude-code-analysis/analysis/04b-tool-call-implementation.md`
- `source/hello-agents/docs/chapter4/第四章 智能体经典范式构建.md`
- `source/hello-agents/docs/chapter7/第七章 构建你的Agent框架.md`
- `source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md`

目标：

- 理解一个最小 Agent Loop 的不变结构。
- 理解 tool schema、handler map、tool_result、流式执行、并发安全、hook 扩展点。
- 理解权限判断为什么应进入工具执行链路。

产出：

- 一个最小 Python Agent：支持循环、工具分发、权限检查、hook。

## 阶段 3：Prompt、模型路由与输出控制

读：

- `source/easy-langent/docs/guide/chapter2.md`
- `source/Alice_methodology/chapters/11-llm-routing.md`
- `source/Alice_methodology/chapters/14-prompts.md`
- `source/hermes-book/src/part2/ch05-prompt-system.md`
- `source/hermes-book/src/part6/ch17-config-profiles.md`
- `source/hermes-book/src/part6/ch18-model-abstraction.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch05.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch06b.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch07.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part2/ch08.md`
- `source/claude-code-analysis/analysis/04g-prompt-management.md`
- `source/hello-agents/docs/chapter3/第三章 大语言模型基础.md`
- `source/hello-agents/docs/chapter7/第七章 构建你的Agent框架.md`
- `source/hello-agents/docs/chapter9/第九章 上下文工程.md`
- `source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md`

目标：

- 掌握系统提示词运行时组装。
- 掌握提示词模板、少样本、输出解析、结构化输出。
- 设计多模型 provider、fallback、日志与配置分层。

产出：

- 一个 prompt assembler。
- 一个 provider router。
- 一个 Pydantic/JSON 输出解析示例。

## 阶段 4：会话与上下文管理 + 长期记忆系统

读：

- `source/learn-claude-code/s08_context_compact/README.md`
- `source/learn-claude-code/s09_memory/README.md`
- `source/learn-claude-code/s10_system_prompt/README.md`
- `source/claw0/sessions/zh/s03_sessions.md`
- `source/claw0/sessions/zh/s06_intelligence.md`
- `source/Alice_methodology/chapters/05-context-memory.md`
- `source/Alice_methodology/blog/blog-04-memory-system.md`
- `source/hermes-book/src/part4/ch10-session-db.md`
- `source/hermes-book/src/part4/ch11-memory-provider.md`
- `source/hermes-book/src/part4/ch12-context-compression.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch09.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch10.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch11.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part3/ch12.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part4/ch13.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part4/ch14.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part4/ch15.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch24.md`
- `source/claude-code-analysis/analysis/04-agent-memory.md`
- `source/claude-code-analysis/analysis/04f-context-management.md`
- `source/claude-code-analysis/analysis/04i-session-storage-resume.md`
- `source/hello-agents/docs/chapter8/第八章 记忆与检索.md`
- `source/hello-agents/docs/chapter9/第九章 上下文工程.md`
- `source/hello-agents/Extra-Chapter/Extra02-上下文工程补充知识.md`
- `source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md`

目标：

- 掌握 JSONL 会话、append-only 事件流、resume。
- 掌握自动压缩、微压缩、token 预算、工具结果落盘。
- 单独掌握长期记忆、用户画像、项目记忆、召回与去重。

产出：

- 一个文件型 session store。
- 一个 compact 策略。
- 一个 memory recall 原型。

## 阶段 5：LangChain 与 LangGraph 应用开发

读：

- `source/easy-langent/docs/guide/chapter3.md`
- `source/easy-langent/docs/guide/chapter4.md`
- `source/easy-langent/docs/guide/chapter5.md`
- `source/easy-langent/docs/guide/chapter6.md`
- `source/easy-langent/docs/guide/chapter7.md`
- `source/easy-langent/docs/guide/chapter8.md`
- `source/easy-langent/project/**/README.md`
- `source/hello-agents/docs/chapter5/第五章 基于低代码平台的智能体搭建.md`
- `source/hello-agents/docs/chapter6/第六章 框架开发实践.md`
- `source/hello-agents/docs/chapter13/第十三章 智能旅行助手.md`
- `source/hello-agents/docs/chapter14/第十四章 自动化深度研究智能体.md`
- `source/hello-agents/docs/chapter15/第十五章 构建赛博小镇.md`
- `source/hello-agents/Co-creation-projects/README.md`

目标：

- 掌握 LangChain 的模型、prompt、parser、memory、tool、chain、RAG。
- 掌握 LangGraph 的 state、node、edge、conditional edge、checkpoint、human-in-the-loop。
- 用课程项目理解应用层 Agent 如何落地。

必须覆盖的项目：

- Agentic RAG
- DataAgent
- MCPChat
- MedicalRag
- PersonalMemoryAssistant
- AI 招聘面试官
- 客服工单智能处理
- 狼人杀 AI 游戏
- 剧本杀智能体游戏
- 谁是卧底两个版本
- 智能体辩论赛
- 小说创作智能体
- 哈尔滨冰雪大世界舆情决策系统

产出：

- 一个 LangGraph 小应用。
- 一个 RAG 应用。
- 一个多角色游戏或业务流程 Agent。

## 阶段 6：安全、权限、沙箱与隐私治理

读：

- `source/Alice_methodology/chapters/07-permission.md`
- `source/Alice_methodology/chapters/12-security.md`
- `source/hello-claw/docs/cn/adopt/chapter10/index.md`
- `source/hello-claw/docs/cn/build/chapter7/index.md`
- `source/hello-claw/docs/cn/build/chapter9/index.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch16.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch17.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch17b.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch18.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch18b.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part5/ch19.md`
- `source/claude-code-analysis/analysis/02-security-analysis.md`
- `source/claude-code-analysis/analysis/02-user-data-and-usage.md`
- `source/claude-code-analysis/analysis/03-privacy-avoidance.md`
- `source/claude-code-analysis/analysis/04e-sandbox-implementation.md`
- `source/claude-code-analysis/analysis/06-extra-findings.md`
- `source/claude-code-analysis/analysis/06b-negative-keyword-analysis.md`
- `source/hello-agents/docs/chapter9/第九章 上下文工程.md`
- `source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md`

目标：

- 理解权限模式、规则系统、审批、权限冒泡。
- 理解沙箱、提示注入防御、Unicode 清洗、信任边界。
- 理解本地数据、云端调用、telemetry、密钥管理的治理方式。

产出：

- 一份本项目 Agent 安全清单。
- 一个权限分类器原型。
- 一个 sandbox 策略草案。

## 阶段 7：Skills、MCP、插件与自进化

读：

- `source/learn-claude-code/s07_skill_loading/README.md`
- `source/learn-claude-code/s19_mcp_plugin/README.md`
- `source/learn-claude-code/skills/**`
- `source/Alice_methodology/chapters/08-mcp.md`
- `source/Alice_methodology/chapters/09-skills.md`
- `source/Alice_methodology/chapters/10-self-evolution.md`
- `source/hermes-book/src/part3/ch08-skill-system.md`
- `source/hermes-book/src/part3/ch09-delegation.md`
- `source/hello-claw/docs/cn/build/skill-practice/index.md`
- `source/hello-claw/docs/cn/appendix/appendix-d.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch22.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch22b.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch23.md`
- `source/claude-code-analysis/analysis/04c-skills-implementation.md`
- `source/claude-code-analysis/analysis/04d-mcp-implementation.md`
- `source/claude-code-analysis/analysis/11-hidden-features-and-easter-eggs.md`
- `source/hello-agents/docs/chapter10/第十章 智能体通信协议.md`
- `source/hello-agents/Extra-Chapter/Extra05-AgentSkills解读.md`
- `source/hello-agents/Extra-Chapter/Extra08-如何写出好的Skill.md`
- `source/hello-agents/Extra-Chapter/Extra10-Agent自进化.md`
- `source/hello-agents/Extra-Chapter/Extra11-WebAgent科普与实战.md`

目标：

- 区分 Tool、Skill、MCP、Plugin 的职责边界。
- 掌握 `SKILL.md` frontmatter、按需加载、技能目录、技能安装发布。
- 掌握 MCP transport、工具命名、连接生命周期、OAuth、权限。
- 理解自进化的边界、撤销栈、用户许可。

产出：

- 一个标准 Skill。
- 一个 MCP 工具接入示例。
- 一个可撤销自进化流程设计。

## 阶段 8：Gateway、渠道、常驻运行、主动性与 Loop Engineering

读：

- `source/claw0/sessions/zh/s04_channels.md`
- `source/claw0/sessions/zh/s05_gateway_routing.md`
- `source/claw0/sessions/zh/s07_heartbeat_cron.md`
- `source/claw0/sessions/zh/s08_delivery.md`
- `source/claw0/sessions/zh/s09_resilience.md`
- `source/claw0/sessions/zh/s10_concurrency.md`
- `source/hello-claw/docs/cn/adopt/intro/index.md`
- `source/hello-claw/docs/cn/adopt/chapter1/index.md` 到 `chapter11/index.md`
- `source/hello-claw/docs/cn/build/chapter5/index.md`
- `source/hello-claw/docs/cn/build/chapter6/index.md`
- `source/hello-claw/docs/cn/build/chapter8/index.md`
- `source/hello-claw/docs/cn/build/chapter10/index.md`
- `source/hermes-book/src/part5/ch13-cli-tui.md`
- `source/hermes-book/src/part5/ch14-gateway.md`
- `source/hermes-book/src/part5/ch15-cron.md`
- `source/hermes-book/src/part5/ch16-terminal-backends.md`
- `source/hermes-book/src/part6/ch19-concurrency.md`
- `source/hermes-book/src/part6/ch20-lifecycle.md`
- `source/hermes-book/src/part6/ch21-runtime-defense.md`
- `source/hello-agents/docs/chapter5/第五章 基于低代码平台的智能体搭建.md`
- `source/hello-agents/docs/chapter13/第十三章 智能旅行助手.md`
- `source/hello-agents/docs/chapter15/第十五章 构建赛博小镇.md`

融合补充：

- `docs/merged-agent-course/ch11-loop-engineering.md`

目标：

- 掌握多渠道输入统一、gateway、绑定路由、session 隔离。
- 掌握心跳、Cron、主动任务、后台投递、退避重试。
- 掌握常驻进程、生命周期、并发 lane、远程访问。
- 理解 Loop Engineering 不是 Agent Loop 的扩展，而是围绕一次或多次执行组织目标、反馈、状态和停止决策的外层控制系统。
- 掌握 verifier、checkpoint、no-progress detection、approval gate 和恢复策略。

产出：

- 一个统一 InboundMessage。
- 一个 gateway routing 原型。
- 一个 cron/heartbeat + delivery queue 原型。
- 一份可执行的 Loop Specification 和一个带 verifier、state、stop condition 的最小可信 Loop。

## 阶段 9：多 Agent、任务系统与并行隔离

读：

- `source/learn-claude-code/s05_todo_write/README.md`
- `source/learn-claude-code/s06_subagent/README.md`
- `source/learn-claude-code/s12_task_system/README.md`
- `source/learn-claude-code/s13_background_tasks/README.md`
- `source/learn-claude-code/s14_cron_scheduler/README.md`
- `source/learn-claude-code/s15_agent_teams/README.md`
- `source/learn-claude-code/s16_team_protocols/README.md`
- `source/learn-claude-code/s17_autonomous_agents/README.md`
- `source/learn-claude-code/s18_worktree_isolation/README.md`
- `source/Alice_methodology/chapters/06-multi-agent.md`
- `source/Alice_methodology/blog/blog-05-multi-agent.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20b.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part6/ch20c.md`
- `source/claude-code-analysis/analysis/04h-multi-agent.md`
- `source/hello-claw/docs/cn/university/multi-claw-hiclaw/index.md`
- `source/hello-claw/docs/cn/university/knowledge-base/index.md`
- `source/hello-claw/docs/cn/university/one-person-company/index.md`
- `source/hello-claw/docs/cn/university/group-debate/index.md`
- `source/hello-agents/docs/chapter6/第六章 框架开发实践.md`
- `source/hello-agents/docs/chapter13/第十三章 智能旅行助手.md`
- `source/hello-agents/docs/chapter14/第十四章 自动化深度研究智能体.md`
- `source/hello-agents/docs/chapter15/第十五章 构建赛博小镇.md`
- `source/hello-agents/docs/chapter16/第十六章 毕业设计.md`

目标：

- 掌握 TodoWrite、任务图、后台任务、团队协议。
- 掌握 subagent、coordinator、swarm、自主认领。
- 掌握 worktree 隔离、权限冒泡、mailbox、shutdown/summary。

产出：

- 一个任务系统。
- 一个 Lead/Worker 多 Agent 协作原型。
- 一个 worktree 隔离执行实验。

## 阶段 10：工程化、测试、可观测性与产品化

读：

- `source/Alice_methodology/chapters/13-observability.md`
- `source/Alice_methodology/chapters/15-engineering-patterns.md`
- `source/Alice_methodology/chapters/16-alive-agent.md`
- `source/Alice_methodology/blog/*.md`
- `source/hermes-book/src/part6/ch22-testing.md`
- `source/hermes-book/src/part7/ch23-philosophy.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch25.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch26.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch27.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch28.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch29.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/part7/ch30.md`
- `source/harness-engineering-from-cc-to-ai-coding/book/src/appendix/*.md`
- `source/claude-code-analysis/analysis/components/*.md`
- `source/claude-code-analysis/analysis/05-differentiators-and-comparison.md`
- `source/claude-code-analysis/analysis/07-code-evidence-index.md`
- `source/claude-code-analysis/analysis/08-competitive-comparison.md`
- `source/claude-code-analysis/analysis/09-final-summary.md`
- `source/claude-code-analysis/analysis/10-src-file-tree.md`
- `source/hello-claw/docs/cn/appendix/*.md`
- `source/hello-claw/docs/cn/university/*.md`
- `source/hello-agents/docs/chapter11/第十一章 Agentic-RL.md`
- `source/hello-agents/docs/chapter12/第十二章 智能体性能评估.md`
- `source/hello-agents/Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md`
- `source/hello-agents/Co-creation-projects/README.md`

目标：

- 掌握测试、日志、trace、metrics、Feature Flag、版本演进。
- 理解 UI/TUI 控制面、组件分层、用户反馈闭环。
- 学会把教程知识转成可长期维护的 Agent 产品。

产出：

- 一份测试计划。
- 一份可观测性方案。
- 一个综合 Agent 的技术设计文档。

## 最终综合项目

最终项目建议做一个“学习型个人编码/研究助理”，包含：

- Agent Loop
- 工具调用与权限控制
- Hooks
- Prompt runtime
- 会话持久化
- 上下文压缩
- 长期记忆系统
- Skill 系统
- MCP 外接工具
- RAG
- Gateway 与多渠道接入
- Cron 与主动任务
- Delivery queue
- 多 Agent 团队
- Worktree 隔离
- 安全与沙箱
- 日志、指标、追踪
- Web 或 TUI 控制面

验收标准：

- 每个机制都有最小实现。
- 每个机制都能在 9 份教程中找到对应来源。
- 每个阶段都有读书笔记和代码实验。
- 所有 `easy-langent/project` 与 `hello-claw/university` 案例都至少完成一次走读或复现。
