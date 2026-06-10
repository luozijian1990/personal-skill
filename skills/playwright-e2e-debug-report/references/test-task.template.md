# Test Tasks: {{title}}

<!--
Playwright E2E 测试任务拆解原则：
1. 先读已完成的 design/tasks，再推导测试矩阵；页面探索只能补漏，不能扩大需求范围。
2. 每个测试场景必须是用户可感知的完整流程，避免只测孤立按钮。
3. 所有高风险动作必须显式写出并等待用户确认：自修复、清理数据、破坏性流程、生产环境、依赖安装。
4. 测试数据默认保留，除非用户明确批准清理。
5. 如果发现产品 bug，是否修复只看 `auto_fix` 设置；没有批准就只记录。
-->

> 来源：
> - Design: {{design_path}}
> - Tasks: {{tasks_path}}
> - 目标分支: {{branch}}

## 目标

{{用一句话说明本次 Playwright E2E 要验证什么功能范围。}}

## HITL 设置

```yaml
auto_fix: false
cleanup_test_data: false
allow_destructive_flows: false
```

<!--
确认项说明：
- auto_fix: 是否允许发现产品 bug 后由 Codex 做最小局部修复并重跑。
- cleanup_test_data: 是否允许删除本次创建的测试数据。
- allow_destructive_flows: 是否允许执行删除、禁用、批量修改等破坏性流程。
-->

## 用户确认

- [ ] 用户已确认以上 HITL 设置
- [ ] 用户已确认执行本测试任务

## 范围

### 本次覆盖

- {{workflow_or_page_1}}
- {{workflow_or_page_2}}

### 本次不覆盖

- {{workflow_or_page_not_tested}}
- 不访问生产环境，除非用户明确批准。
- 不记录密码、cookie、token、原始请求体。

## 环境

- 后端启动命令：`{{backend_command}}`
- 前端启动命令：`{{frontend_command}}`
- 前端 URL：`{{frontend_url}}`
- API base/proxy：`{{api_base_or_proxy}}`
- 认证方式：{{auth_mode}}
- 测试账号来源：{{config_docs_or_user_provided}}
- 认证前置状态：{{account_available/existing_session/needs_user_input}}
- mock/真实后端模式：{{mock_or_real_mode}}

## 测试数据计划

- 创建：
  - {{resource_type_and_name_pattern}}
- 默认保留：是
- 清理：仅在用户明确批准后执行
- 记录要求：报告中记录保留资源的名称和 ID

## 测试矩阵

| ID | 模块 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|---|
| T01 | {{模块/页面}} | {{场景，如“登录后进入用户管理列表”}} | {{步骤A → 步骤B → 步骤C}} | {{可观察的预期结果}} |

<!--
矩阵设计参考：
- 登录/鉴权：正常登录、未登录访问、权限不足。
- 主流程：核心导航、列表、详情、新增、编辑、删除/禁用（仅批准后）。
- 数据校验：必填、重复、非法输入、服务端错误提示。
- 日志/审计：如果 design/tasks 明确要求日志或审计，要验证是否可观察。
- 阻断场景：预期 403/404/409 等负向流程要标记为预期结果。
-->

## 中止条件

- 检测到生产环境。
- 需要安装依赖。
- 需要执行未批准的提权命令。
- 需要执行未批准的破坏性动作。
- 缺少测试账号、登录方式或可用 session。
- 继续测试必须先做未批准的产品代码修复。
- 阻断级产品 bug 导致剩余场景无法继续。

## 执行状态

等待用户确认后执行。
