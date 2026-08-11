# ops-readiness-review

审查运维工具和平台在生产运行与操作安全方面是否就绪，覆盖危险操作、鉴权授权、审计、Secret、远程执行、Kubernetes、异步任务、API 可靠性、可观测性、数据生命周期、部署和失败恢复，并输出 `PASS`、`PASS_WITH_RISKS` 或 `FAIL` 报告。

本 Skill 关注运行正确性：软件在真实环境中操作基础设施、处理失败和长期运行时是否安全、可恢复、可观察。不替代 `code-review`（代码质量与 Spec 符合度）、安全测试、E2E 或人工验收。

- 触发与审查流程：见 [`SKILL.md`](SKILL.md)（Agent 通过它驱动整个审查工作流）
- 就绪清单：见 [`references/readiness-checklist.md`](references/readiness-checklist.md)
- 报告模板：见 [`templates/report.md`](templates/report.md)

## 这个 skill 包含什么

| 路径 | 角色 |
|---|---|
| `SKILL.md` | Agent 入口：建立系统风险画像、证据索引、按风险裁剪的检查、严重度评定、输出报告 |
| `references/readiness-checklist.md` | 12 个领域的就绪检查清单（危险操作、鉴权、审计、Secret、远程执行、K8s、异步任务、API 可靠性、可观测性、数据生命周期、部署、失败恢复） |
| `templates/report.md` | 报告模板，默认写入 `docs/reviews/YYYY-MM-DD-<topic>-ops-readiness.md` |
| `evals/` | 评估夹具与测试输出样例（如 `async-worker` 场景） |
| `agents/openai.yaml` | 面向特定 Agent 的配置示例 |

## 核心原则

- **风险校准**：只读 Dashboard 与 Kubernetes 管理、SSH 批量执行需要不同审查深度，允许 `NOT_APPLICABLE`；
- **证据优先**：区分 `DOCUMENTED` / `STATIC` / `TESTED` / `RUNTIME_VERIFIED`，不把计划文档当成实现证据；
- **不按清单堆基础设施**：不因有异步任务就自动要求 MQ，不因部署到 Kubernetes 就自动要求 Operator 或 Service Mesh；
- **高风险能力提高门槛**：删除、重启、扩缩容、回滚、远程执行和批量操作要同时看授权、确认、审计、幂等、爆炸半径和恢复；
- **默认审查，不替用户接受风险**：风险接受必须有责任人和依据。

## 使用

在运维工具完成开发、进入最终验收时，可以直接提出：

- "对这个运维平台做一次 ops-readiness-review。"
- "K8s 管理工具快上线了，评估一下生产就绪度。"

需要执行生产变更、真实远程命令、破坏性测试或数据库迁移时，会先展示目标、命令、爆炸半径、回退方式和证据用途，等待明确批准后才会执行。

## 许可证

随仓库根目录 [`LICENSE`](../../LICENSE)（MIT, Copyright (c) 2026 luozijian1990）。
