# Tasks: {{title}}

<!--
任务拆解原则：
1. 每个 task 是一个原子操作（一个方法、一个配置、一个文件）
2. 粒度：拿到就能直接编码，不需要再猜意图
3. 描述用伪码级箭头链：动作A → 动作B → 动作C
4. 按模块/文件分组，组内按依赖顺序排列
5. 最后一组是整体验收（编译/构建、单元/服务层/API 测试、AC 覆盖）

task 描述中的关键约束要显式写出：
- "禁止调 super" — 完全重写
- "校验 X 非空" — 前置校验
- "不设置 Y" — 刻意留空
- "异常继续" — catch 后 continue
这些约束如果不写，实现者大概率会按常规路径走，产生 bug。
-->

## 1. {{模块/分组名称，如"策略注册"}}

- [ ] 1.1 {{具体操作描述，如"在 XxxEnum.java 中新增 CASE_X(Handler.class) 枚举值"}}

## 2. {{模块/分组名称，如"新增 Handler"}}

- [ ] 2.1 {{创建文件/类，如"创建 XxxHandler.java，继承 BaseHandler"}}
- [ ] 2.2 {{方法级 task，如"重写 methodA()：校验 X 非空 → 转存 Y → 调 super.methodA(param)"}}
- [ ] 2.3 {{方法级 task，如"重写 methodB()（完全重写，禁止调 super）：步骤A → 步骤B → 步骤C"}}
- [ ] 2.4 {{更多方法...}}

## 3. {{模块/分组名称，如"现有类改造"}}

- [ ] 3.1 {{如"注入 @Autowired XxxHandler handler"}}
- [ ] 3.2 {{如"新增 isXxx() 辅助方法：查 table.field，条件 → 返回 true"}}
- [ ] 3.3 {{如"重写 methodA()：条件A → handler 委托；条件B → super"}}
- [ ] 3.4 {{更多方法...}}

## 4. 整体验收

- [ ] 4.1 执行 `mvn compile` / `npm run build` 确认编译无错误
- [ ] 4.2 {{执行单元测试/服务层测试/API 测试，覆盖 AC1、AC2}}
- [ ] 4.3 {{执行失败场景自动化测试，覆盖 AC3}}
- [ ] 4.4 {{执行回归边界自动化测试，覆盖 AC4}}

<!--
整体验收要求：
- 每条 Acceptance Criteria 都必须映射到至少一个验收 task，task 描述中直接写"覆盖 ACx"
- 默认验收方式是单元测试、服务层测试、API 测试、隔离集成测试或构建检查
- 外部系统用 mock/spy/fixture 验证调用参数和事务边界，不默认真实调用 Helm、Kubernetes、Git push、生产数据库、付费 API
- 不默认加入 Playwright/E2E；只有用户明确要求或 design 指出浏览器行为是主要风险时才写入，并优先交给 playwright-e2e-debug-report 流程
- 如果某个 AC 当前无法自动化验证，必须写成 Open Question 或 Rollout/manual verification note，不能静默省略

task 数量参考：
- 小需求（改 1-2 个文件）：5-10 个 task
- 中需求（改 3-5 个文件）：10-20 个 task
- 大需求（改 5+ 个文件）：20-40 个 task，考虑拆成多个 tasks.md

每完成一个 task，将 [ ] 改为 [x]。
AI 执行时应逐个完成，完成一个标记一个，不要批量完成后统一标记。
-->
