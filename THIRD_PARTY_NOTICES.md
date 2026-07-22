# Third-Party Notices

本仓库收录、改编了若干第三方 Agent Skills。本文件统一记录来源、上游许可证、本地改动摘要，以及无法收录的内容。详细的逐项审计在 README 中不再重复。

## 许可证边界

- 根目录的 `LICENSE`（MIT）**仅覆盖**本仓库的原创内容和本仓库有权对外许可的本地改动。
- 本表中列出的第三方 Skill **继续遵循各自上游许可证**，根 MIT 不替代、不扩大其覆盖范围。
- 上游许可证原文位于 `THIRD_PARTY_LICENSES/`，文件命名为 `<上游所有者>-<上游仓库>-LICENSE.txt`。
- `skills/frontend-design/LICENSE.txt` 按 Anthropic 上游要求随该 Skill 目录一并保留。
- 本仓库未对任何第三方版权声明进行改写或剔除。

## 审计字段说明

| 字段 | 含义 |
|---|---|
| Skill | 本仓库 `skills/<name>` 目录名 |
| 上游仓库 | GitHub 上游 `owner/repo` |
| 上游路径 | 上游仓库内对应内容的目录或文件 |
| 上游版本 | 审计时所参考的分支（commit 未固定，以仓库当前 HEAD 为准） |
| 许可证 | 上游声明的许可证标识 |
| 收录方式 | 原样收录 / 改编 / 混合改编 |
| 主要本地改动 | 与上游对比可确认的关键差异（保守描述，不虚构） |
| 上游 LICENSE | `THIRD_PARTY_LICENSES/` 中保留的文件名 |

审计日期：2026-07-22。

## 第三方 Skill 审计表

### 1. mattpocock/skills（MIT）

下列精选 Skill 来源于 [mattpocock/skills](https://github.com/mattpocock/skills)，统一引用 `THIRD_PARTY_LICENSES/mattpocock-skills-LICENSE.txt`。本地保留了个人使用的 13 个 Skill，并将 `diagnosing-bugs` 中不存在的架构改进入口改为本仓库同时收录的 `codebase-design`；开发工作流说明见 `docs/DEVELOPMENT_WORKFLOW.md`。

| Skill | 上游路径（以仓库当前结构为准） | 收录方式 |
|---|---|---|
| `code-review` | `skills/engineering/code-review/` | 精选收录 |
| `codebase-design` | `skills/engineering/codebase-design/` | 精选收录 |
| `diagnosing-bugs` | `skills/engineering/diagnosing-bugs/` | 改编 |
| `domain-modeling` | `skills/engineering/domain-modeling/` | 精选收录 |
| `grill-me` | `skills/productivity/grill-me/` | 精选收录 |
| `grill-with-docs` | `skills/productivity/grill-with-docs/` | 精选收录 |
| `grilling` | `skills/productivity/grilling/` | 精选收录 |
| `handoff` | `skills/productivity/handoff/` | 精选收录 |
| `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills/` | 精选收录 |
| `tdd` | `skills/engineering/tdd/` | 精选收录 |
| `teach` | `skills/learning/teach/` | 精选收录 |
| `to-spec` | `skills/engineering/to-spec/` | 精选收录 |
| `to-tickets` | `skills/engineering/to-tickets/` | 精选收录 |

### 2. 其他第三方 Skill（上游许可证明确）

| Skill | 上游仓库 | 上游路径 | 上游分支 | 许可证 | 收录方式 | 主要本地改动 | 上游 LICENSE |
|---|---|---|---|---|---|---|---|
| `draw-io-diagram-generator` | `github/awesome-copilot` | `skills/draw-io-diagram-generator/` | main | MIT, Copyright GitHub, Inc. | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/github-awesome-copilot-LICENSE.txt` |
| `frontend-design` | `anthropics/skills` | `skills/frontend-design/` | main | Apache-2.0, Copyright Anthropic, PBC | 原样收录（含上游 LICENSE.txt） | 未做内容改动 | `skills/frontend-design/LICENSE.txt`（按上游要求随该 Skill 目录保留） |
| `frontend-slides` | `zarazhangrui/frontend-slides` | 仓库根目录（`SKILL.md` 位于根） | main | MIT, Copyright (c) 2025 Zara Zhang | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/zarazhangrui-frontend-slides-LICENSE.txt` |
| `grafana-dashboards` | `wshobson/agents` | `plugins/observability-monitoring/skills/grafana-dashboards/` | main | MIT, Copyright (c) 2024 Seth Hobson | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/wshobson-agents-LICENSE.txt` |
| `playwright-cli` | `microsoft/playwright-cli` | `skills/playwright-cli/` | main | Apache-2.0, Copyright (c) Microsoft Corporation | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/microsoft-playwright-cli-LICENSE.txt` |

### 3. 上游无 LICENSE 文件但本仓库选择收录

仓库所有者在**知悉法律默认"All Rights Reserved"风险**的前提下选择收录下列 Skill。本节如实披露真实状态，**不构成对再分发授权的确认**，使用者需自行评估法律风险。本仓库未对任何文件追加不实的许可证声明，也未在 `THIRD_PARTY_LICENSES/` 下创建虚构的 LICENSE 文件。

| Skill | 上游仓库 | 上游路径 | 上游分支 | 上游 LICENSE 文件 | 上游 README 许可证声明 | 收录决定 |
|---|---|---|---|---|---|---|
| `baoyu-infographic` | `JimLiu/baoyu-skills` | `baoyu-infographic/` | main / master 均存在 README，根目录无 LICENSE 文件 | `LICENSE` / `LICENSE.md` / `LICENSE.txt` / `License` / `COPYING` 均 HTTP 404 | 审计日未确认 | 仓库所有者选择收录，风险自担 |
| `baoyu-markdown-to-html` | `JimLiu/baoyu-skills` | `baoyu-markdown-to-html/` | 同上 | 同上 | 同上 | 同上 |
| `darwin-skill` | `alchaincyf/darwin-skill` | 仓库根目录 | master 存在 README，根目录无 LICENSE 文件 | `LICENSE` / `LICENSE.md` / `LICENSE.txt` / `License` / `COPYING` 均 HTTP 404 | `README.md` 出现 `License: MIT` 徽章（指向不存在的 `LICENSE` 文件），按本仓库审计规则**不以徽章替代许可证正文** | 仓库所有者选择收录，风险自担 |

后续追加授权时的处理：
- 若上游补充了正式 LICENSE 文件，将其复制到 `THIRD_PARTY_LICENSES/JimLiu-baoyu-skills-LICENSE.txt` 或 `THIRD_PARTY_LICENSES/alchaincyf-darwin-skill-LICENSE.txt`，并在本节后追加条目。
- 若上游作者通过 issue、邮件或社交平台明确授权再分发，将证据归档到本仓库的 `docs/permissions/` 下，并在本表"上游 README 许可证声明"列改为"作者书面授权（见 docs/permissions/...）"。
- 在上述任何一种情况落地之前，本表保持现状。

## NOTICE 文件核实

按 Apache-2.0 第 4(d) 条款的要求，上游若存在 `NOTICE` 文件，须随分发一并保留。

| 上游 | 是否存在 NOTICE | 处理 |
|---|---|---|
| `github/awesome-copilot`（main，仓库根） | 不存在 | 无需创建 `THIRD_PARTY_LICENSES/github-awesome-copilot-NOTICE.txt` |
| `microsoft/playwright-cli`（main，仓库根） | 不存在 | 无需创建 `THIRD_PARTY_LICENSES/microsoft-playwright-cli-NOTICE.txt` |
| `anthropics/skills`（main，`skills/frontend-design/`） | 不存在 | 无需在 Skill 目录额外补 NOTICE |

核实方式：直接拉取上游仓库根目录的 `NOTICE` / `NOTICE.txt` / `NOTICE.md`，均返回 HTTP 404。

## 原创 Skill

下列 Skill 为本仓库原创项目，遵循根 `LICENSE`（MIT）。仅作清单声明，不另列上游来源。

- `aliyun-asr`
- `html-to-mui-react`
- `k8s-troubleshoot`
- `learning-notes-builder`
- `learning-roadmap`
- `playwright-e2e-debug-report`
- `project-init`
- `stack-selector`

第三方依赖（如阿里云 SDK、Playwright、React、MUI、marked、highlight.js、mermaid 等）不在本表的“上游来源”范围内，仍受其各自项目许可证约束，使用者自行遵守。

## 维护说明

- 新增第三方 Skill 时，先核实上游 LICENSE 是否允许再分发，并在本文件登记上游路径、许可证、收录方式与改动摘要。
- 上游许可证正文必须**逐字**保留在 `THIRD_PARTY_LICENSES/` 或 Skill 目录内，禁止改写版权声明或省略条款。
- 当上游版本演进与本仓库收录版本产生明显差异时，可在“主要本地改动”列追加说明，不必反向同步全部上游变更。
