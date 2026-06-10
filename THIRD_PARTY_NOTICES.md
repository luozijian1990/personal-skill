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

审计日期：2026-06-10。

## 第三方 Skill 审计表

### 1. obra/superpowers（MIT，Copyright (c) 2025 Jesse Vincent）

下列 Skill 来源同一上游仓库，统一引用 `THIRD_PARTY_LICENSES/obra-superpowers-LICENSE.txt`。

| Skill | 上游路径（main 分支） | 收录方式 | 主要本地改动 |
|---|---|---|---|
| `dispatching-parallel-agents` | `skills/dispatching-parallel-agents/` | 原样收录 | 未做内容改动 |
| `executing-plans` | `skills/executing-plans/` | 改编 | 在 Step 2 增加“立即更新 plan 文件中该 task 状态字段”的中文执行约定；其余流程保持上游一致 |
| `finishing-a-development-branch` | `skills/finishing-a-development-branch/` | 原样收录 | 未做内容改动 |
| `receiving-code-review` | `skills/receiving-code-review/` | 原样收录 | 未做内容改动 |
| `subagent-driven-development` | `skills/subagent-driven-development/` | 原样收录 | 未做内容改动 |
| `systematic-debugging` | `skills/systematic-debugging/` | 原样收录 | 未做内容改动 |
| `test-driven-development` | `skills/test-driven-development/` | 原样收录 | 未做内容改动 |
| `using-git-worktrees` | `skills/using-git-worktrees/` | 原样收录 | 未做内容改动 |
| `using-superpowers` | `skills/using-superpowers/` | 原样收录 | 未做内容改动 |
| `verification-before-completion` | `skills/verification-before-completion/` | 原样收录 | 未做内容改动 |
| `writing-skills` | `skills/writing-skills/` | 原样收录 | 未做内容改动 |

### 2. obra/superpowers + mattpocock/skills 混合改编

| Skill | 上游 A | 上游 B | 许可证 | 收录方式 | 主要本地改动 |
|---|---|---|---|---|---|
| `brainstorming` | `obra/superpowers`：`skills/brainstorming/` | `mattpocock/skills`：`skills/productivity/grill-me/` | 两者均 MIT | 混合改编 | 在 obra `brainstorming` 基础上整合 mattpocock `grill-me` 的“Grill Mode”交互模式；引入 SDD 风格的 `proposal.md` / `design.md` 模板与 Mode Selection 决策；保留 HARD-GATE 实施前审批的约束 |

上游 LICENSE：
- `THIRD_PARTY_LICENSES/obra-superpowers-LICENSE.txt`
- `THIRD_PARTY_LICENSES/mattpocock-skills-LICENSE.txt`

### 3. obra/superpowers 独立改编

| Skill | 上游路径 | 许可证 | 收录方式 | 主要本地改动 |
|---|---|---|---|---|
| `requesting-code-review` | `skills/requesting-code-review/` | MIT | 改编 | 增加评分机制与 review 模板的本地化调整（与上游对比可确认的差异，详细 diff 以仓库实际内容为准） |
| `writing-plans` | `skills/writing-plans/` | MIT | 改编 | 增加 tasks 模板、Decision→Task 映射校验等本地化补充 |

上游 LICENSE：`THIRD_PARTY_LICENSES/obra-superpowers-LICENSE.txt`。

### 4. 其他第三方 Skill（上游许可证明确）

| Skill | 上游仓库 | 上游路径 | 上游分支 | 许可证 | 收录方式 | 主要本地改动 | 上游 LICENSE |
|---|---|---|---|---|---|---|---|
| `draw-io-diagram-generator` | `github/awesome-copilot` | `skills/draw-io-diagram-generator/` | main | MIT, Copyright GitHub, Inc. | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/github-awesome-copilot-LICENSE.txt` |
| `frontend-design` | `anthropics/skills` | `skills/frontend-design/` | main | Apache-2.0, Copyright Anthropic, PBC | 原样收录（含上游 LICENSE.txt） | 未做内容改动 | `skills/frontend-design/LICENSE.txt`（按上游要求随该 Skill 目录保留） |
| `frontend-slides` | `zarazhangrui/frontend-slides` | 仓库根目录（`SKILL.md` 位于根） | main | MIT, Copyright (c) 2025 Zara Zhang | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/zarazhangrui-frontend-slides-LICENSE.txt` |
| `grafana-dashboards` | `wshobson/agents` | `plugins/observability-monitoring/skills/grafana-dashboards/` | main | MIT, Copyright (c) 2024 Seth Hobson | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/wshobson-agents-LICENSE.txt` |
| `playwright-cli` | `microsoft/playwright-cli` | `skills/playwright-cli/` | main | Apache-2.0, Copyright (c) Microsoft Corporation | 原样收录 | 未做内容改动 | `THIRD_PARTY_LICENSES/microsoft-playwright-cli-LICENSE.txt` |

### 5. 上游无 LICENSE 文件但本仓库选择收录

仓库所有者在**知悉法律默认"All Rights Reserved"风险**的前提下选择收录下列 Skill。本节如实披露真实状态，**不构成对再分发授权的确认**，使用者需自行评估法律风险。本仓库未对任何文件追加不实的许可证声明，也未在 `THIRD_PARTY_LICENSES/` 下创建虚构的 LICENSE 文件。

| Skill | 上游仓库 | 上游路径 | 上游分支 | 上游 LICENSE 文件 | 上游 README 许可证声明 | 收录决定 |
|---|---|---|---|---|---|---|
| `baoyu-infographic` | `JimLiu/baoyu-skills` | `baoyu-infographic/` | main / master 均存在 README，根目录无 LICENSE 文件 | `LICENSE` / `LICENSE.md` / `LICENSE.txt` / `License` / `COPYING` 均 HTTP 404 | 审计日未确认 | 仓库所有者选择收录，风险自担 |
| `baoyu-markdown-to-html` | `JimLiu/baoyu-skills` | `baoyu-markdown-to-html/` | 同上 | 同上 | 同上 | 同上 |
| `darwin-skill` | `alchaincyf/darwin-skill` | 仓库根目录 | master 存在 README，根目录无 LICENSE 文件 | `LICENSE` / `LICENSE.md` / `LICENSE.txt` / `License` / `COPYING` 均 HTTP 404 | `README.md` 出现 `License: MIT` 徽章（指向不存在的 `LICENSE` 文件），按本仓库审计规则**不以徽章替代许可证正文** | 仓库所有者选择收录，风险自担 |

后续追加授权时的处理：
- 若上游补充了正式 LICENSE 文件，将其复制到 `THIRD_PARTY_LICENSES/JimLiu-baoyu-skills-LICENSE.txt` 或 `THIRD_PARTY_LICENSES/alchaincyf-darwin-skill-LICENSE.txt`，并在第 4 节追加条目。
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
