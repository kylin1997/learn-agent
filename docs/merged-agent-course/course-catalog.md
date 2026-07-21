# 融合版 Agent 教材目录

本目录保存基于 `source/` 下 10 份教程融合重写的 Agent 教材。教材按可迁移的知识主题组织，不按来源工程逐章摘抄。

- 学习方法与阶段安排见[《Agent 学习指南》](../agent-learning-guide.md)。
- 来源合并关系和覆盖结论见[《来源覆盖说明》](../source-coverage.md)。

## 阅读约定

- 本页列出的 20 章是主教材入口。
- “已 Review”表示用户已经确认章节的结构、深度和表达；“待 Review”表示正文已经生成，但仍可能继续调整。
- 章末“原文入口”用于查看实现原型、论证上下文或进一步资料，不要求顺序通读。
- 目录中的旧版第 2-14 章文件只用于回溯重构前内容，不属于主学习路径。

## 第一篇：基础心智

1. [Agent、智能体历史与 Harness](ch01-agent-and-harness.md)（已 Review）
2. [大语言模型基础与模型行为](ch02-llm-foundations-model-behavior.md)（待 Review）
3. [Agent Loop、经典范式与工具运行时](ch03-agent-loop-paradigms-tools.md)（待 Review）

## 第二篇：运行时与知识

4. [Prompt Engineering 与 Prompt Runtime](ch04-prompt-engineering-runtime.md)（待 Review）
5. [模型运行时、路由与调用可靠性](ch05-model-runtime-routing-reliability.md)（待 Review）
6. [会话、状态与上下文工程](ch06-session-state-context-engineering.md)（已 Review）
7. [长期记忆系统](ch07-long-term-memory.md)（待 Review）
8. [RAG 与外部知识系统](ch08-rag-knowledge-systems.md)（待 Review）

## 第三篇：框架与应用编排

9. [Agent 框架与应用编排](ch09-agent-frameworks-orchestration.md)（待 Review）

## 第四篇：治理与扩展

10. [权限、安全、沙箱与隐私治理](ch10-security-permission-sandbox-privacy.md)（待 Review）
11. [Skills 与插件系统](ch11-skills-plugins.md)（待 Review）
12. [MCP、A2A、ANP 与 Agent 互操作](ch12-agent-interoperability.md)（待 Review）

## 第五篇：常驻运行与多 Agent

13. [Gateway、多渠道、身份与路由](ch13-gateway-channel-identity-routing.md)（待 Review）
14. [后台任务、Cron、投递与运行时韧性](ch14-background-cron-delivery-resilience.md)（待 Review）
15. [Loop Engineering：从单次循环到可持续执行系统](ch15-loop-engineering.md)（待 Review）
16. [多 Agent、任务系统与团队协作](ch16-multi-agent-task-team.md)（待 Review）

## 第六篇：评测、进化与生产

17. [Agent 测试、评测与基准体系](ch17-agent-testing-evaluation-benchmarks.md)（待 Review）
18. [Agent 自进化与后训练](ch18-agent-self-evolution-post-training.md)（待 Review）
19. [生产工程、可观测性与产品迭代](ch19-production-observability-product-iteration.md)（待 Review）
20. [代表案例与综合 Agent 项目](ch20-cases-capstone-agent.md)（待 Review）

## 内容边界

教材正文收录可迁移的原理、架构、工程方法和代表实现，不按产品功能清单展开。详细筛选标准、排除项和审计结论统一维护在[《来源覆盖说明》](../source-coverage.md)中。

## 章节结构

每章根据主题取舍，通常包括：

- 学习目标与边界
- 核心问题、原理和运行机制
- 最小实现与代表案例
- 生产约束和常见失败模式
- 测试与验收
- 系统地图与共同结论
- 本章自检与开放性问题
- 本地来源与外部资料入口

## 旧稿处理

旧版第 2-14 章暂时留在本目录，方便逐章重构时回溯内容。新增引用和后续修改只使用本页列出的新版文件。待新版 20 章全部 Review 后，再统一决定是否迁入 `legacy/`。
