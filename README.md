# Learn Agent

这个工程用于系统学习 AI Agent。`source/` 目录下包含 9 份教程材料，既有 LangChain/LangGraph 应用实战，也有 Claude Code、OpenClaw、Hermes、Alice 等 Agent 产品和工程实现分析。

## 学习入口

- [学习方案](docs/agent-learning-plan.md)：按 Agent 能力栈合并后的主线学习路线。
- [融合版 Agent 教材](docs/merged-agent-course/README.md)：融合 9 份教程并补充外部资料，新版 20 章正文已经生成，当前按章 Review。
- [教程覆盖地图](docs/source-coverage-map.md)：9 份教程各自侧重点、去重合并方式和最终覆盖关系。
- [Codex 协作规约](AGENTS.md)：后续再次打开项目时，Codex 应遵循的项目约定。

## 9 份教程

1. `source/easy-langent`：LangChain、LangGraph 与应用项目实战。项目地址：[datawhalechina/easy-langent](https://github.com/datawhalechina/easy-langent)
2. `source/hermes-book`：Hermes Agent 源码与 self-improving personal agent 工程设计。项目地址：[ZhangHanDong/hermes-book](https://github.com/ZhangHanDong/hermes-book)
3. `source/Alice_methodology`：桌面 AI Agent 的工程方法论、记忆、权限、多 Agent、人格化设计。项目地址：[itshen/Alice_methodology](https://github.com/itshen/Alice_methodology)
4. `source/hello-claw`：OpenClaw 使用、运维、Skill 场景实战与构建教程。项目地址：[datawhalechina/hello-claw](https://github.com/datawhalechina/hello-claw)
5. `source/claw0`：从零构建 AI Agent Gateway 的 10 节 Python 教程。项目地址：[shareAI-lab/claw0](https://github.com/shareAI-lab/claw0)
6. `source/harness-engineering-from-cc-to-ai-coding`：Claude Code 源码到 AI Coding 最佳实践。项目地址：[ZhangHanDong/harness-engineering-from-cc-to-ai-coding](https://github.com/ZhangHanDong/harness-engineering-from-cc-to-ai-coding)
7. `source/claude-code-analysis`：Claude Code 源码静态分析、架构、安全、组件、竞品对比。项目地址：[liuup/claude-code-analysis](https://github.com/liuup/claude-code-analysis)
8. `source/learn-claude-code`：从零构建 Claude Code 式 Agent Harness 的 20 节渐进教程。项目地址：[shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)
9. `source/hello-agents`：Datawhale《从零开始构建智能体》，覆盖 Agent 基础、ReAct/Plan/Reflection、低代码平台、框架实践、记忆检索、上下文工程、通信协议、Agentic RL、评估与综合项目。项目地址：[datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents)

## 学习原则

- 不按目录机械顺序学习，而是按 Agent 能力栈推进。
- 重复主题合并学习，差异内容用于横向对照。
- 每个阶段都要有读书笔记、源码走读和最小实现。
- 最终目标是做出一个综合 Agent：工具调用、权限、上下文、记忆、Skill、MCP、Gateway、Cron、Loop Controller、外部状态、独立验证、停止控制、多 Agent 和可观测性都具备。
