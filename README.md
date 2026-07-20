# Learn Agent

这个工程用于系统学习 AI Agent。项目把 `source/` 下 9 个教程工程中的可迁移知识合并为一套 20 章教材，并通过持续演进的综合 Agent 完成实践。

## 从这里开始

1. 阅读[《Agent 学习指南》](docs/agent-learning-guide.md)，了解五阶段路线、每章学习动作和实践产物。
2. 从[《融合版 Agent 教材目录》](docs/merged-agent-course/course-catalog.md)进入主教材，并查看各章 Review 状态。
3. 需要核查来源、合并规则或排除项时，查看[《来源覆盖说明》](docs/source-coverage.md)。

## 目录说明

- `docs/merged-agent-course/`：融合教材正文、配图和暂存旧稿。
- `source/`：9 个原始教程工程，只在需要代码原型或论证上下文时回源。
- `docs/`：学习指南、来源覆盖说明及后续学习笔记。
- `experiments/` 或 `src/`：本项目自己的实验与综合 Agent 实现。
- [AGENTS.md](AGENTS.md)：Codex 在本工程中的协作和文档同步规约。

## 学习原则

- 主读融合教材，不按来源目录机械通读。
- 需要实现细节或证据时再回到 `source/`。
- 每个阶段都给同一个综合 Agent 增加可测试的能力。
- 使用自检、开放性问题、失败案例和实验结果判断是否真正掌握。
