# prototype-parity-review

审查 React + Mock 是否忠实实现了已经人工批准的 HTML Prototype，并输出 `PASS`、`PASS_WITH_NOTES` 或 `FAIL` 的原型一致性门禁报告。

HTML 是视觉与交互契约，React 是工程化实现。本 Skill 关注工程化过程中是否改变了已确认的产品设计，不追求逐像素相同的截图，也不替代代码审查、真实后端 E2E 或最终人工验收。

- 触发与审查流程：见 [`SKILL.md`](SKILL.md)（Agent 通过它驱动整个审查工作流）
- 审查清单：见 [`references/review-checklist.md`](references/review-checklist.md)
- 报告模板：见 [`templates/report.md`](templates/report.md)

## 这个 skill 包含什么

| 路径 | 角色 |
|---|---|
| `SKILL.md` | Agent 入口：固定比较契约、建立覆盖矩阵、采集证据、判定严重度、输出门禁报告 |
| `references/review-checklist.md` | 视觉与交互一致性检查清单（布局、层级、字体、间距、Dialog/Drawer、状态等） |
| `templates/report.md` | 门禁报告模板，默认写入 `docs/reviews/YYYY-MM-DD-<topic>-prototype-parity.md` |
| `evals/` | 评估夹具：`parity-pass`（一致通过）、`runtime-failure`（运行失败）等场景 |
| `agents/openai.yaml` | 面向特定 Agent 的配置示例 |

## 所处流程

```text
HTML Prototype
→ 人工原型评审
→ React + Mock
→ 原型一致性审查   ← 本 Skill
→ 架构草案
```

`FAIL` 时停止，不进入架构草案。输出 `FAIL` 报告后，未经用户确认修复范围不得自行修改产品代码。

## 使用

完成 React + Mock 实现后，可以直接提出：

- "用这个 skill 检查 React 项目是否忠实实现了批准的 HTML 原型。"
- "原型一致性审查，通过后才进入架构草案。"

前置条件：已批准的 HTML Prototype（路径或 URL）与批准记录、React + Mock 项目与启动方式、关键业务 Flow 与代表性 viewport。缺少可比较的 HTML、React 实现、人工批准证据或关键 Flow 范围时，正式 Gate 为 `FAIL`，不会自动放行。

## 许可证

随仓库根目录 [`LICENSE`](../../LICENSE)（MIT, Copyright (c) 2026 luozijian1990）。
