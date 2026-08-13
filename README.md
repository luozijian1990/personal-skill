# personal-skill

一份经过筛选、改造和组合的通用 Agent Skills 合集，主要来自维护者（[@luozijian1990](https://github.com/luozijian1990)）的个人 Agent 环境实践。仓库定位于直接使用者与 Skill 设计参考者，**不暗示全部内容均为原创**，第三方内容的来源与许可证在 `[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)` 中单独记录。

## 快速开始

### 使用 `npx skills` 安装

无需克隆仓库或全局安装 CLI。先查看仓库中可安装的 Skill：

```bash
npx skills@latest add luozijian1990/personal-skill --list
```

全局安装全部 Skill 到 Claude Code：

```bash
npx skills@latest add luozijian1990/personal-skill \
  --skill '*' \
  --agent claude-code \
  --global
```

也可以只安装指定 Skill：

```bash
npx skills@latest add luozijian1990/personal-skill \
  --skill stack-selector \
  --agent claude-code \
  --global
```

如需安装到其他受支持的 Agent，调整 `--agent` 参数；省略 `--global` 时默认安装到当前项目。

### 作为 Claude Code Plugin 安装

在 Claude Code 会话中添加本仓库提供的 Marketplace，然后安装插件：

```text
/plugin marketplace add luozijian1990/personal-skill
/plugin install personal-skill@personal-skill
/reload-plugins
```

Plugin 模式会一次加载本仓库的全部 Skill，并使用 `personal-skill` 命名空间。例如：

```text
/personal-skill:stack-selector
```

### 作为 Codex Plugin 使用

仓库根目录提供 `.codex-plugin/plugin.json`，并通过 `skills/` 暴露全部 Skill，可作为 `personal-skill` Codex Plugin 接入 Codex Marketplace。

本仓库只维护可分发的 Plugin 源码，不会自动修改使用者的个人 Marketplace 配置。安装到 Marketplace 后，请新建 Codex 对话，使新加载的 Skill 生效。

### 手动使用

```bash
git clone https://github.com/luozijian1990/personal-skill.git
```

- 全部 Skill 位于 `skills/` 目录，按 `skills/<name>/SKILL.md` 的通用结构组织；
- 可按所使用的 Agent（Claude Code、Codex、其他遵循 Agent Skill 规范的工具等）自己的加载方式接入；
- 推荐的轻量开发工作流见 `[docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)`。



## 兼容性与验证声明

- 本目录采用通用 Agent Skill 结构（`SKILL.md` + 关联资源），不绑定特定 Agent 平台；
- 多数 Skill 主要在维护者的个人环境中实践、改造和验证，**不同 Agent、不同模型、不同版本的实际行为可能存在差异**；
- 不为每个 Skill 单独维护“已验证 / 部分验证 / 未验证”状态，避免容易过期的状态徽章误导使用者；
- 使用者应在自己的环境中先进行小规模验证，再用于关键场景。



## Skill 清单

下面的分类按用途组织，每个 Skill 一句话简介。详细使用说明请打开本地目录下的 `SKILL.md`。

### 轻量开发工作流（来自 mattpocock/skills）


| Skill                                                          | 简介                                  |
| -------------------------------------------------------------- | ----------------------------------- |
| `[setup-matt-pocock-skills](skills/setup-matt-pocock-skills/)` | 首次使用时配置 issue tracker、领域文档和标签约定     |
| `[grill-with-docs](skills/grill-with-docs/)`                   | 在已有代码库中逐问澄清需求，并沉淀领域词汇与 ADR          |
| `[grill-me](skills/grill-me/)`                                 | 没有代码库或不需要留档时，进行无状态需求审查              |
| `[grilling](skills/grilling/)`                                 | 提供逐题追问的基础审查原语                       |
| `[domain-modeling](skills/domain-modeling/)`                   | 统一领域术语，维护 `CONTEXT.md` 和必要的 ADR     |
| `[codebase-design](skills/codebase-design/)`                   | 设计深模块、接口和可测试 seam                   |
| `[to-spec](skills/to-spec/)`                                   | 把已讨论内容综合成规格并发布到 issue tracker       |
| `[to-tickets](skills/to-tickets/)`                             | 把规格拆成带阻塞关系的纵向 tracer-bullet tickets |
| `[tdd](skills/tdd/)`                                           | 对每个 ticket 采用红—绿—重构循环实现             |
| `[code-review](skills/code-review/)`                           | 从 Standards 和 Spec 两个轴审查变更          |
| `[handoff](skills/handoff/)`                                   | 将当前上下文压缩成跨会话 handoff 文档             |
| `[diagnosing-bugs](skills/diagnosing-bugs/)`                   | 为难复现 bug 建反馈回路，并用回归测试锁定根因           |




### 内容、设计与可视化


| Skill                                                            | 简介                                           |
| ---------------------------------------------------------------- | -------------------------------------------- |
| `[baoyu-infographic](skills/baoyu-infographic/)`                 | 21×21 布局/风格组合的信息图生成器，从内容反推合适的可视化方案           |
| `[baoyu-markdown-to-html](skills/baoyu-markdown-to-html/)`       | 把 Markdown 转成内嵌样式的 HTML，适配公众号及外链引用           |
| `[draw-io-diagram-generator](skills/draw-io-diagram-generator/)` | 生成可直接打开的 draw.io 流程图 / 架构图 / 时序图等            |
| `[frontend-design](skills/frontend-design/)`                     | 生成有设计感的前端组件、页面、海报；避免 AI 默认审美                 |
| `[frontend-slides](skills/frontend-slides/)`                     | 从零或从 PPT 生成富动画的 HTML 幻灯片                     |
| `[learning-notes-builder](skills/learning-notes-builder/)`       | 把整理好的材料目录合成结构化中文学习笔记 markdown                |
| `[learning-roadmap](skills/learning-roadmap/)`                   | 把学习笔记 markdown 转成 roadmap.sh 风格的可交互 HTML 路线图 |




### Roadmap 与面试题设计


| Skill                                                              | 简介                                                       |
| ------------------------------------------------------------------ | -------------------------------------------------------- |
| `[question-gap-analyzer](skills/question-gap-analyzer/)`           | 分析 Roadmap 或 Markdown 知识材料，结合个人画像、JD 和可选已有题目，筛选普通题与场景题候选 |
| `[scenario-question-designer](skills/scenario-question-designer/)` | 把 Roadmap 知识点、题目候选或故障素材设计成经人工确认的个性化场景面试题                 |




### 项目开发与浏览器测试


| Skill                                                                | 简介                                                |
| -------------------------------------------------------------------- | ------------------------------------------------- |
| `[html-to-mui-react](skills/html-to-mui-react/)`                     | 把 HTML 原型 1:1 复刻为 Vite + React + MUI v5 项目，含三套环境  |
| `[playwright-cli](skills/playwright-cli/)`                           | 用 `playwright-cli` 在终端驱动真实浏览器：导航、截图、表单、调试         |
| `[playwright-e2e-debug-report](skills/playwright-e2e-debug-report/)` | Playwright 真实浏览器 E2E 全量测试 + 经批准的自修复 + Markdown 报告 |
| `[project-init](skills/project-init/)`                               | 按规范化结构初始化 Python / Golang 后端项目脚手架                 |
| `[prototype-parity-review](skills/prototype-parity-review/)`         | 审查 React + Mock 是否忠实实现已批准的 HTML 原型，输出 PASS / PASS_WITH_NOTES / FAIL 门禁报告 |
| `[stack-selector](skills/stack-selector/)`                           | 从 React mock 和运行约束反推运维类 Python / Go 项目的后端组件与技术栈   |




### 运维与平台工具


| Skill                                              | 简介                                   |
| -------------------------------------------------- | ------------------------------------ |
| `[aliyun-asr](skills/aliyun-asr/)`                 | 用阿里云“录音文件识别闲时版”批量把音频/视频 URL 转成文字     |
| `[grafana-dashboards](skills/grafana-dashboards/)` | 生成与管理生产级 Grafana 监控大盘                |
| `[k8s-troubleshoot](skills/k8s-troubleshoot/)`     | Pod/Service/Ingress/公网四层排查 K8s 部署故障  |
| `[ops-readiness-review](skills/ops-readiness-review/)` | 按风险裁剪审查运维工具的生产就绪度：危险操作、鉴权、审计、Secret、恢复等，输出 PASS / PASS_WITH_RISKS / FAIL 报告 |
| `[ssh-remote-ops](skills/ssh-remote-ops/)`         | 通过 SSH 对远程服务器进行只读优先、授权明确、可回退的运维排查与操作 |




### Skill 工具链


| Skill                                  | 简介                                                          |
| -------------------------------------- | ----------------------------------------------------------- |
| `[darwin-skill](skills/darwin-skill/)` | 自动化的 Skill 优化器：按 8 维 rubric 评分、用 git 做 hill-climbing、生成结果卡片 |




### 学习


| Skill                    | 简介                             |
| ------------------------ | ------------------------------ |
| `[teach](skills/teach/)` | 在工作区内持续维护 mission、参考资料、课程和学习记录 |




## 使用说明

- 每个 Skill 目录是自包含的，所有引用使用相对路径，便于按需取用或组合；
- Skill 名称即 `name:` 字段；触发方式由 `description:` 字段控制，详见各 `SKILL.md`；
- 若 Skill 依赖外部命令（如 `playwright-cli`、`bun`、`npx`、`curl` 等），请按各 Skill 内说明先行安装；
- 仓库不重复列出每个 Skill 的依赖矩阵，避免与各 Skill 内部文档失同步。



## 贡献

欢迎新增 Skill、改进现有 Skill 或修复问题。提交前请先阅读 `[CONTRIBUTING.md](CONTRIBUTING.md)`，重点关注**来源与许可证**、**单 Skill 自包含**、**验证说明**三条最低门槛。

## 许可证

- 根目录 `[LICENSE](LICENSE)`（MIT，Copyright (c) 2026 luozijian1990）**仅覆盖**本仓库的原创内容和本仓库有权对外许可的本地改动；
- 第三方 Skill 继续遵循其上游许可证。完整的逐项来源、上游路径、许可证标识、本地改动摘要以及无 LICENSE 上游的披露，统一记录在 `[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)`；
- 上游许可证原文位于 `[THIRD_PARTY_LICENSES/](THIRD_PARTY_LICENSES/)`；
- `skills/frontend-design/LICENSE.txt` 按 Anthropic 上游要求随该 Skill 目录保留。



## 致谢

本合集中改编、组合的部分内容来自以下上游项目（具体许可证与本地改动见 `THIRD_PARTY_NOTICES.md`）：

- [mattpocock/skills](https://github.com/mattpocock/skills) — Matt Pocock
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — GitHub
- [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) — Microsoft
- [wshobson/agents](https://github.com/wshobson/agents) — Seth Hobson
- [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) — Zara Zhang
- [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) — JimLiu
- [alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) — alchaincyf
