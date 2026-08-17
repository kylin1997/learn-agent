# Learn Agent

这个工程用于系统学习 AI Agent。项目把 `source/` 下 12 个教程工程中的可迁移知识合并为一套 20 章教材，并通过持续演进的综合 Agent 完成实践。

## 从这里开始

1. 阅读[《Agent 学习指南》](docs/agent-learning-guide.md)，了解五阶段路线、每章学习动作和实践产物。
2. 从[《融合版 Agent 教材目录》](docs/merged-agent-course/course-catalog.md)进入主教材，并查看各章 Review 状态。
3. 需要核查来源、合并规则或排除项时，查看[《来源覆盖说明》](docs/source-coverage.md)。

## 目录说明

- `docs/merged-agent-course/`：融合教材的 20 章正文、配图和课程目录。
- `source/`：12 个原始教程工程，只在需要代码原型或论证上下文时回源。
- `docs/`：学习指南、来源覆盖说明及后续学习笔记。
- `experiments/` 或 `src/`：本项目自己的实验与综合 Agent 实现。
- [AGENTS.md](AGENTS.md)：Codex 在本工程中的协作和文档同步规约。

## 含 Agent 演示代码的工程

以下 `source/` 子目录包含 `xxx.py` 形式的 Agent 演示代码，结构与 `learn-claude-code` 类似：

- [ ] `source/learn-claude-code/`：20 个 `sXX_name/code.py`（Agent 循环、工具使用、权限、Hook、子 Agent 等）
- [ ] `source/hello-agents/code/`：14 个 `chapterN/*.py`（从 FirstAgentTest 到 MCP、A2A、评估等）
- [ ] `source/claw0/sessions/`：10 个 `sXX_name.py` × 3 语言（en/zh/ja），覆盖 Agent 循环到并发
- [ ] `source/ai-agent-book/`：10 个 `chapterN/sub-project/*.py`（上下文、搜索、编码、浏览器等）
- [ ] `source/ai-agents-in-action-2nd-edition-cn/code/`：12 个 `chapter_NN/*.py`（从首个 Agent 到认知架构）
- [ ] `source/easy-langent/project/`：多个子项目含 `*.py`（MCPChat、DebateGame、MedicalRag 等）

## 学习原则

- 主读融合教材，不按来源目录机械通读。
- 需要实现细节或证据时再回到 `source/`。
- 每个阶段都给同一个综合 Agent 增加可测试的能力。
- 使用自检、开放性问题、失败案例和实验结果判断是否真正掌握。
