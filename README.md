# personal-skill

一份经过筛选、改造和组合的通用 Agent Skills 合集，主要来自维护者（[@luozijian1990](https://github.com/luozijian1990)）的个人 Agent 环境实践。仓库定位于直接使用者与 Skill 设计参考者，**不暗示全部内容均为原创**，第三方内容的来源与许可证在 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 中单独记录。

## 快速开始

```bash
git clone https://github.com/luozijian1990/personal-skill.git
```

- 全部 Skill 位于 `skills/` 目录，按 `skills/<name>/SKILL.md` 的通用结构组织；
- 请按你所使用的 Agent（Claude Code、Codex、其他遵循 Agent Skill 规范的工具等）自己的加载方式接入；
- 本仓库**不提供**具体平台的加载路径或配置命令，原因是这些命令容易随版本变化而失效，且会让维护者承担超出仓库范围的兼容性承诺。

## 兼容性与验证声明

- 本目录采用通用 Agent Skill 结构（`SKILL.md` + 关联资源），不绑定特定 Agent 平台；
- 多数 Skill 主要在维护者的个人环境中实践、改造和验证，**不同 Agent、不同模型、不同版本的实际行为可能存在差异**；
- 不为每个 Skill 单独维护“已验证 / 部分验证 / 未验证”状态，避免容易过期的状态徽章误导使用者；
- 使用者应在自己的环境中先进行小规模验证，再用于关键场景。

## Skill 清单

下面的分类按用途组织，每个 Skill 一句话简介。详细使用说明请打开本地目录下的 `SKILL.md`。

### 开发工作流与工程方法

| Skill | 简介 |
|---|---|
| [`brainstorming`](skills/brainstorming/) | 在动手前把想法压成可实施设计；提供 Design / Grill / Refinement 三种模式与 SDD 模板 |
| [`dispatching-parallel-agents`](skills/dispatching-parallel-agents/) | 识别可并行的独立任务，按结构化方式派发给多个 subagent |
| [`executing-plans`](skills/executing-plans/) | 按 plan 文件逐任务实施，分批校验，并在每个 task 完成时立即更新状态 |
| [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | 实现完成后引导合入、PR 或清理的结构化收尾流程 |
| [`receiving-code-review`](skills/receiving-code-review/) | 接到评审反馈时要求验证而非表演性认同，避免盲目改动 |
| [`requesting-code-review`](skills/requesting-code-review/) | 完成任务前以一致模板请求评审，附带评分机制 |
| [`stack-selector`](skills/stack-selector/) | vibe coding 流程中，从 React mock 反推后端能力，按「项目形态 × 语言 × 维度」敲定技术栈 |
| [`subagent-driven-development`](skills/subagent-driven-development/) | 在当前会话里按 plan 的独立任务并行驱动 subagent |
| [`systematic-debugging`](skills/systematic-debugging/) | 遇到 bug / 测试失败时按系统化流程定位根因，先复现再修 |
| [`test-driven-development`](skills/test-driven-development/) | 实现任何 feature/bugfix 前先写测试，让代码服从可验证目标 |
| [`using-git-worktrees`](skills/using-git-worktrees/) | 启动需要隔离的特性工作时，安全地建立 git worktree |
| [`using-superpowers`](skills/using-superpowers/) | 介绍如何发现并恰当地调用各项 superpowers skill |
| [`verification-before-completion`](skills/verification-before-completion/) | 宣称“完成”前先跑验证命令，证据先于断言 |
| [`writing-plans`](skills/writing-plans/) | 把规格 / 需求拆成可逐步执行的多任务实施计划 |
| [`writing-skills`](skills/writing-skills/) | 新建或编辑 Skill，并按规范在部署前完成自检 |

### 内容、设计与可视化

| Skill | 简介 |
|---|---|
| [`baoyu-infographic`](skills/baoyu-infographic/) | 21×21 布局/风格组合的信息图生成器，从内容反推合适的可视化方案 |
| [`baoyu-markdown-to-html`](skills/baoyu-markdown-to-html/) | 把 Markdown 转成内嵌样式的 HTML，适配公众号及外链引用 |
| [`draw-io-diagram-generator`](skills/draw-io-diagram-generator/) | 生成可直接打开的 draw.io 流程图 / 架构图 / 时序图等 |
| [`frontend-design`](skills/frontend-design/) | 生成有设计感的前端组件、页面、海报；避免 AI 默认审美 |
| [`frontend-slides`](skills/frontend-slides/) | 从零或从 PPT 生成富动画的 HTML 幻灯片 |
| [`learning-notes-builder`](skills/learning-notes-builder/) | 把整理好的材料目录合成结构化中文学习笔记 markdown |
| [`learning-roadmap`](skills/learning-roadmap/) | 把学习笔记 markdown 转成 roadmap.sh 风格的可交互 HTML 路线图 |

### 项目开发与浏览器测试

| Skill | 简介 |
|---|---|
| [`html-to-mui-react`](skills/html-to-mui-react/) | 把 HTML 原型 1:1 复刻为 Vite + React + MUI v5 项目，含三套环境 |
| [`playwright-cli`](skills/playwright-cli/) | 用 `playwright-cli` 在终端驱动真实浏览器：导航、截图、表单、调试 |
| [`playwright-e2e-debug-report`](skills/playwright-e2e-debug-report/) | Playwright 真实浏览器 E2E 全量测试 + 经批准的自修复 + Markdown 报告 |
| [`project-init`](skills/project-init/) | 按规范化结构初始化 Python / Golang 后端项目脚手架 |

### 运维与平台工具

| Skill | 简介 |
|---|---|
| [`aliyun-asr`](skills/aliyun-asr/) | 用阿里云“录音文件识别闲时版”批量把音频/视频 URL 转成文字 |
| [`grafana-dashboards`](skills/grafana-dashboards/) | 生成与管理生产级 Grafana 监控大盘 |
| [`k8s-troubleshoot`](skills/k8s-troubleshoot/) | Pod/Service/Ingress/公网四层排查 K8s 部署故障 |

### Skill 工具链

| Skill | 简介 |
|---|---|
| [`darwin-skill`](skills/darwin-skill/) | 自动化的 Skill 优化器：按 8 维 rubric 评分、用 git 做 hill-climbing、生成结果卡片 |

## 使用说明

- 每个 Skill 目录是自包含的，所有引用使用相对路径，便于按需取用或组合；
- Skill 名称即 `name:` 字段；触发方式由 `description:` 字段控制，详见各 `SKILL.md`；
- 若 Skill 依赖外部命令（如 `playwright-cli`、`bun`、`npx`、`curl` 等），请按各 Skill 内说明先行安装；
- 仓库不重复列出每个 Skill 的依赖矩阵，避免与各 Skill 内部文档失同步。

## 贡献

欢迎新增 Skill、改进现有 Skill 或修复问题。提交前请先阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)，重点关注**来源与许可证**、**单 Skill 自包含**、**验证说明**三条最低门槛。

## 许可证

- 根目录 [`LICENSE`](LICENSE)（MIT，Copyright (c) 2026 luozijian1990）**仅覆盖**本仓库的原创内容和本仓库有权对外许可的本地改动；
- 第三方 Skill 继续遵循其上游许可证。完整的逐项来源、上游路径、许可证标识、本地改动摘要以及无 LICENSE 上游的披露，统一记录在 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)；
- 上游许可证原文位于 [`THIRD_PARTY_LICENSES/`](THIRD_PARTY_LICENSES/)；
- `skills/frontend-design/LICENSE.txt` 按 Anthropic 上游要求随该 Skill 目录保留。

## 致谢

本合集中改编、组合的部分内容来自以下上游项目（具体许可证与本地改动见 `THIRD_PARTY_NOTICES.md`）：

- [obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent
- [mattpocock/skills](https://github.com/mattpocock/skills) — Matt Pocock
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — GitHub
- [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) — Microsoft
- [wshobson/agents](https://github.com/wshobson/agents) — Seth Hobson
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) — Zara Zhang
- [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) — JimLiu
- [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) — alchaincyf
