---
name: playwright-e2e-debug-report
description: 仅当用户明确要求使用 Playwright 或 playwright-cli 做真实浏览器 E2E、全量功能测试、冒烟测试、回归测试，或要求先生成 HITL test-task、自动化执行、问题分流、经批准后自修复并输出 Markdown 测试报告时使用。不要用于普通前端开发、普通调试或非 Playwright 测试。
---

# Playwright E2E 调试报告

## 用途

这个 skill 用来把已经完成的 `design.md` / `tasks.md` 转成需要人工确认的 Playwright E2E 测试任务，确认后再用 `playwright-cli` 跑真实浏览器测试，分流失败原因，按批准范围自修复产品 bug，重跑验证，并生成 Markdown 测试报告。

它是编排型流程，不替代底层 Playwright 操作 skill。

## 硬性门禁

- 未生成 `test-task.md` 并获得用户确认前，不执行 E2E。除非用户提供已经确认过的测试任务并要求直接执行。
- 未在测试任务中明确批准 `auto_fix: true`，不自修复产品代码。
- 未批准 `cleanup_test_data: true` 或用户未明确要求清理，不删除测试数据。
- 未批准 `allow_destructive_flows: true`，不执行破坏性流程。
- 报告里禁止写入密码、cookie、token、原始请求体。
- 缺少测试账号、登录方式或已授权 session 时，必须停止并询问用户；不得编造账号、绕过登录、弱化鉴权或直接改代码跳过认证。
- 遇到生产环境访问、依赖安装、付费外部调用、不安全删除、数据库迁移、未批准的提权命令时，先停下来确认。

## 工作流

1. **读取项目上下文**
   - 读取本地仓库约束，例如 `AGENTS.md`。
   - 读取相关且已完成的设计和任务文档，通常在 `docs/plans/` 下。
   - 明确前后端启动命令、访问 URL、认证方式、mock/真实后端模式、预期验证命令。

2. **生成 HITL 测试任务**
   - 写入 `docs/test-tasks/YYYY-MM-DD-{{topic_slug}}-test-tasks.md`。
   - 测试矩阵优先来自已完成的 design/tasks；页面和路由探索只用于补齐遗漏。
   - HITL 设置必须使用可机器判定的键值格式，例如 `auto_fix: false`，不要只放在 checkbox 文案里。
   - 使用 `references/test-task.template.md`。
   - 向用户给出简短确认摘要并等待确认。

3. **确认后执行**
   - 启动或复用需要的后端和前端 dev server。
   - 确认真实目标：URL、代理/API base、cookie/session 行为，以及是否为非 mock 模式。
   - 按需使用 `playwright-cli` 执行浏览器操作、页面快照、请求检查、控制台日志、截图或 trace。

4. **先分流失败，再决定动作**
   - 将失败分类为：环境问题、测试脚本/定位器问题、产品 bug、数据/初始化问题、权限/认证问题。
   - 如果是测试脚本问题，修正测试动作后继续。
   - 如果是产品 bug 且 `auto_fix: true`，做最小局部修复并重跑受影响场景。
   - 如果是产品 bug 且 `auto_fix: false`，只记录问题；如果不修复无法继续，停止并生成部分报告。
   - 如果失败不影响其他独立场景，继续执行剩余场景，并在报告中记录该失败。
   - 如果后续场景依赖已失败的前置状态，将这些场景标记为 `SKIPPED`，不要误报为 `FAIL`。

5. **验证**
   - 修复后重跑失败场景和受影响场景。
   - 完成前运行仓库需要的 build/test/lint/vet 等验证命令。
   - 只把新鲜命令输出作为最终证据。

6. **输出报告**
   - 写入 `docs/reports/YYYY-MM-DD-{{topic_slug}}-report.md`。
   - 使用 `references/report.template.md`。
   - 包含环境、HITL 设置、测试数据、结果矩阵、失败问题、修复记录、日志/产物、验证命令和遗留风险。

## 测试矩阵规则

- 优先覆盖用户真实工作流，不只检查孤立按钮。
- 如果 design/tasks 中存在相关能力，覆盖登录/鉴权、主导航、核心 CRUD、权限敏感视图、审计/日志、错误/阻断流程。
- 写清楚测试数据预期，以及保留还是清理。
- 测试任务中必须写清中止条件。
- 不发明超出 design/tasks 范围的大型场景。

## 自修复规则

当 `auto_fix: true` 时，只在完成根因分析后修复：

- 只修复证据明确、影响局部的应用 bug。
- 不为了满足错误测试而修改业务规则。
- 未经用户明确批准，不削弱鉴权、权限检查、校验、日志或审计行为。
- 每次修复后，重跑原失败场景和相关 build/test 命令。

当 `auto_fix: false` 时，收集足够复现证据，让用户决定后续处理。

## 报告规则

- 汇总 Playwright 请求和控制台证据，不粘贴大段日志。
- 对预期负向流程，例如故意触发的 409，标记为预期结果，不当作异常。
- `SKIPPED` 必须说明跳过原因，例如“依赖 T03 登录成功，但 T03 已失败”。
- 记录保留的测试资源名称和 ID。
- 记录验证命令及 PASS/FAIL；如果有沙箱或授权限制，要说明。
- 最终报告保持简洁，但要足够审计和复现。

## 参考模板

- 写 HITL 测试任务时使用 `references/test-task.template.md`。
- 写最终测试报告时使用 `references/report.template.md`。
