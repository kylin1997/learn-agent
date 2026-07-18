# 融合版 Agent 教材

本目录保存基于 `source/` 下 9 份教程融合重写的 Agent 教材。主教材按可迁移的知识主题组织，不按来源工程逐章摘抄；产品安装、配置、命令手册和低成熟度案例不进入正文。

## 新版章节目录

20 章正文已经生成。第 1 章和第 6 章经过用户 Review，其余章节作为完整初稿等待逐章 Review；“已生成”只表示结构、来源和机械检查完成，不表示内容已经最终确认。

### 第一篇：基础心智

1. [Agent、智能体历史与 Harness](ch01-agent-and-harness.md)（已 Review）
2. [大语言模型基础与模型行为](ch02-llm-foundations-model-behavior.md)（待 Review）
3. [Agent Loop、经典范式与工具运行时](ch03-agent-loop-paradigms-tools.md)（待 Review）

### 第二篇：运行时与知识

4. [Prompt Engineering 与 Prompt Runtime](ch04-prompt-engineering-runtime.md)（待 Review）
5. [模型运行时、路由与调用可靠性](ch05-model-runtime-routing-reliability.md)（待 Review）
6. [会话、状态与上下文工程](ch06-session-state-context-engineering.md)（已 Review）
7. [长期记忆系统](ch07-long-term-memory.md)（待 Review）
8. [RAG 与外部知识系统](ch08-rag-knowledge-systems.md)（待 Review）

### 第三篇：框架与应用编排

9. [Agent 框架与应用编排](ch09-agent-frameworks-orchestration.md)（待 Review）

### 第四篇：治理与扩展

10. [权限、安全、沙箱与隐私治理](ch10-security-permission-sandbox-privacy.md)（待 Review）
11. [Skills 与插件系统](ch11-skills-plugins.md)（待 Review）
12. [MCP、A2A、ANP 与 Agent 互操作](ch12-agent-interoperability.md)（待 Review）

### 第五篇：常驻运行与多 Agent

13. [Gateway、多渠道、身份与路由](ch13-gateway-channel-identity-routing.md)（待 Review）
14. [后台任务、Cron、投递与运行时韧性](ch14-background-cron-delivery-resilience.md)（待 Review）
15. [Loop Engineering：从单次循环到可持续执行系统](ch15-loop-engineering.md)（待 Review）
16. [多 Agent、任务系统与团队协作](ch16-multi-agent-task-team.md)（待 Review）

### 第六篇：评测、进化与生产

17. [Agent 测试、评测与基准体系](ch17-agent-testing-evaluation-benchmarks.md)（待 Review）
18. [Agent 自进化与后训练](ch18-agent-self-evolution-post-training.md)（待 Review）
19. [生产工程、可观测性与产品迭代](ch19-production-observability-product-iteration.md)（待 Review）
20. [代表案例与综合 Agent 项目](ch20-cases-capstone-agent.md)（待 Review）

## 旧版文件

目录中的旧版第 2-14 章文件暂时保留，用于回溯重构前的内容和链接。它们不再是主教材入口；新增引用和后续修改应以本页列出的新版文件为准。待 20 章逐章 Review 完成后，再统一决定是否迁入 `legacy/`。

## 内容筛选规则

1. 可迁移的原理和架构进入主教材并完整讲解。
2. 能解释关键机制的代表实现进入正文或案例框。
3. 成熟案例用于验证原理，不按项目功能清单逐项收录。
4. 产品安装、配置、命令操作、硬件部署和低代码点击教程不进入主教材。
5. 重复、过时或低成熟度内容在覆盖审计中记录，不把“出现过”误写成“已深入覆盖”。

## 统一章节结构

每章根据主题取舍，但尽量包含：学习目标与边界、核心问题、原理、运行机制、最小实现、生产约束、失败模式、测试与验收、代表案例、系统地图、共同结论、自检、开放性问题和原文入口。

来源内容直接融合进正文，不再使用“某某教程补充”式附加段落。外部资料优先使用论文、标准和官方工程文档，并与本地来源分组列出。

## 覆盖检查

- [9 个来源工程覆盖审计](source-coverage-audit.md)
