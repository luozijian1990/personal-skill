---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Based on the design.md from brainstorming, generate a structured tasks.md that breaks the design into atomic, executable tasks. Each task is a pseudocode-level description with explicit constraints — no inline implementation code, no inline test code.

Assume the executor (AI or human) is a skilled developer but knows nothing about this specific codebase. The tasks.md gives them the full picture: what to do, in what order, with what constraints.

**Announce at start:** "I'm using the writing-plans skill to create tasks.md."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Input:** `docs/plans/YYYY-MM-DD-<topic>-design.md` (from brainstorming)

**Save plans to:** `docs/plans/YYYY-MM-DD-<topic>-tasks.md`

## Task Granularity

**Each task is one atomic operation:**
- One method, one configuration, or one file
- Described with pseudocode arrow chains: `动作A → 动作B → 动作C`
- Explicit constraints written in the task description (not in comments or code)

**TDD steps are NOT written in tasks.md.** The executing-plans + TDD skill will expand each task into Red-Green-Refactor during execution. Tasks.md is for overview and constraint transfer, not for complete implementation.

## Plan Document Header

**Every tasks.md MUST start with this header:**

```markdown
# Tasks: [Feature Name]

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
>
> **Design:** @docs/plans/YYYY-MM-DD-<topic>-design.md

**Goal:** [One sentence describing what this builds]

---
```

## Task Structure (按 @references/tasks.template.md)

````markdown
## 1. {{模块/分组名称}}

- [ ] 1.1 {{具体操作描述，如"在 XxxEnum.java 中新增 CASE_X(Handler.class) 枚举值"}}

## 2. {{模块/分组名称}}

- [ ] 2.1 {{创建文件/类，如"创建 XxxHandler.java，继承 BaseHandler"}}
- [ ] 2.2 {{方法级 task：校验 X 非空 → 转存 Y → 调 super.methodA(param)}}
- [ ] 2.3 {{方法级 task（完全重写，禁止调 super）：步骤A → 步骤B → 步骤C}}

## 3. {{模块/分组名称}}

- [ ] 3.1 {{注入依赖}}
- [ ] 3.2 {{辅助方法：查 table.field，条件 → 返回 true}}
- [ ] 3.3 {{重写方法：条件A → handler 委托；条件B → super}}

## N. 验证

- [ ] N.1 执行编译/构建确认无错误
- [ ] N.2 {{其他验证}}
````

### Key Rules for Task Descriptions

- **Pseudocode arrow chains**: `fetchToken → cacheToken → param.setToken(accessToken)`
- **Explicit constraints**: Write them directly in the task description:
  - `"禁止调 super"` — complete rewrite, not enhancement
  - `"校验 X 非空"` — precondition check required
  - `"不设置 Y"` — intentionally left empty, not an omission
  - `"异常继续"` — catch and continue, don't throw
  - `"从 X 获取，不从 Y 获取"` — data source constraint
- **Group by module/file**, not flat numbering
- **Dependency order** within each group
- **Last group is always verification** (compile, test, smoke test)

## Decision→Task Mapping Check

**After generating tasks.md, you MUST perform this self-check:**

For each Decision in design.md:
1. Is there at least one task that implements this Decision?
2. Are the Decision's constraints (e.g., "禁止调 super", "不从 Y 获取") explicitly written in the corresponding task description?
3. If a Decision has a risk/trap noted in the rationale, is it reflected as a constraint in the task?

**If any Decision is missing a corresponding task, or any constraint is not transferred, fix before saving.**

Report the mapping check result to the user:
```
Decision→Task 映射检查：
  Decision 1 (xxx) → Task 2.1 ✓
  Decision 2 (xxx) → Task 2.3, 3.1 ✓
  Decision 3 (xxx) → Task 3.4 ✓ (约束"禁止调 super"已写入)
  ...
```

## 语言与状态要求

- **所有 tasks.md 文档必须用中文撰写**（标题、描述、步骤说明均用中文，代码和命令保持原文）
- 每完成一个 task，将 `[ ]` 改为 `[x]`
- AI 执行时应逐个完成，完成一个标记一个，不要批量完成后统一标记

## Remember
- Exact file paths always
- Pseudocode descriptions, not complete code
- Constraints explicit in task description, not hidden in comments
- Group by module, not flat numbering
- Reference design.md for rationale
- Last group is always verification

## Execution Handoff

After saving the plan, offer execution choice:

**"Tasks complete and saved to `docs/plans/<filename>-tasks.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**
- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses superpowers:executing-plans
