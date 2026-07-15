# 融合版 Agent 教材

本目录用于保存基于 `source/` 下 9 份教程融合重写后的教材。目标是：主要阅读本目录即可系统学习完整内容；需要查看原始上下文、代码或细节时，再通过每章末尾的来源链接回到原文。

## 章节目录

1. [Agent 到底是什么](ch01-agent-and-harness.md)
2. [Agent Loop 与工具调用](ch02-agent-loop-and-tools.md)
3. [Prompt Runtime 与提示工程](ch03-prompt-runtime.md)
4. [模型路由、Provider 抽象与调用可靠性](ch04-model-routing.md)
5. [会话与上下文管理](ch05-session-and-context.md)
6. [长期记忆系统](ch06-memory-system.md)
7. [LangChain 与 LangGraph 应用开发](ch07-langchain-langgraph.md)
8. [权限、安全、沙箱与隐私治理](ch08-security-permission-sandbox.md)
9. [Skills、MCP、插件与自进化](ch09-skills-mcp-plugins.md)
10. [Gateway、多渠道、Cron 与主动 Agent](ch10-gateway-cron-proactive.md)
11. [Loop Engineering：从单次循环到可持续执行系统](ch11-loop-engineering.md)
12. [多 Agent、任务系统与团队协作](ch12-multi-agent-task-system.md)
13. [工程化、测试、可观测性与产品化](ch13-engineering-observability-product.md)
14. [综合项目：构建自己的 Agent](ch14-capstone-agent.md)

## 覆盖检查

- [9 个来源工程覆盖审计](source-coverage-audit.md)

## 写作约定

- 每章以主题为单位融合 9 份教程，不按原仓库顺序照搬。
- 每章保留原文入口，方便回源。
- 原文中重复讲的主题合并为一套工程判断。
- 原文没有但学习上必要的主题，可以作为外部补充独立成章。
- `Loop Engineering` 是独立章节，放在 `Gateway、多渠道、Cron 与主动 Agent` 之后。
