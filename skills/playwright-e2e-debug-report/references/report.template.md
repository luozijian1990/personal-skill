# Test Report: {{title}}

<!--
报告原则：
1. 先给结论，再给证据。
2. 失败问题要能复现：场景、现象、根因、是否修复、重测结果。
3. 日志和 Playwright 证据只摘要，不粘贴大段输出。
4. 不写入密码、cookie、token、原始请求体。
5. 测试数据默认记录并保留，除非用户批准清理。
-->

## 摘要

- 结果：PASS / PARTIAL / FAIL
- 日期：{{YYYY-MM-DD}}
- 分支：{{branch}}
- 执行者：Codex + playwright-cli
- 测试任务：{{test_task_path}}

## 环境

- 后端：`{{backend_command}}`
- 前端：`{{frontend_command}}`
- 前端 URL：`{{frontend_url}}`
- API base/proxy：`{{api_base_or_proxy}}`
- 认证方式：{{auth_mode}}
- mock/真实后端模式：{{mock_or_real_mode}}

## HITL 设置

- `auto_fix: true/false`
- `cleanup_test_data: true/false`
- `allow_destructive_flows: true/false`

## 测试结果

| ID | 场景 | 结果 | 证据 | 说明 |
|---|---|---|---|---|
| T01 | {{场景}} | PASS / FAIL / SKIPPED | {{请求/控制台/日志/截图证据摘要}} | {{说明}} |

## 测试数据

- 创建：
  - `{{resource_name}}` / `{{id}}`
- 清理：
  - kept / deleted / not approved

## 发现的问题

### Issue 1: {{标题}}

- 严重级别：blocker / major / minor
- 现象：{{发生了什么}}
- 根因：{{为什么发生}}
- 修复：{{修改了什么；或说明 auto_fix=false 因此未修复}}
- 重测：PASS / FAIL / not run

## 日志与产物

- Playwright requests：{{摘要或路径}}
- Console：{{摘要或路径}}
- 后端日志：{{摘要或路径}}
- 截图/trace：{{路径，如有}}

## 最终验证

- `{{command}}`：PASS / FAIL

## 遗留风险

- {{风险或未覆盖范围}}

## 最终状态

PASS / PARTIAL / FAIL
