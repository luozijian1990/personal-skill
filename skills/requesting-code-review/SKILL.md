---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch superpowers:code-reviewer subagent to catch issues before they cascade.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

**Plan-driven completion** — when the work being reviewed is the implementation of a written plan (paired `<date>-<topic>-design.md` and `-tasks.md` in `docs/plans/`), use **Plan Scorecard Mode** below. It produces a durable `-review.md` artifact instead of inline verbal feedback.

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code-reviewer subagent:**

Use Task tool with superpowers:code-reviewer type, fill template at `code-reviewer.md`

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch superpowers:code-reviewer subagent]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from docs/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: requesting-code-review/code-reviewer.md

---

## Plan Scorecard Mode

Use when the work under review is the completion of a written plan (the kind produced by `writing-plans` and executed via `executing-plans` / `subagent-driven-development`). Instead of inline verbal feedback on a git diff, this mode produces a structured **scorecard file** paired with the design and tasks — a three-file lineage that makes the review a durable artifact and feeds the next iteration.

### Detect this mode

Trigger when ALL of these hold:
- A `docs/plans/<date>-<topic>-design.md` exists alongside `<date>-<topic>-tasks.md`
- Most/all tasks in tasks.md are checked `[x]`
- User asks to "review the plan", "审核这份计划", "给 tasks.md 打分", "做一份 review.md", or similar

### Why a separate mode

- Plan-driven work has explicit ground truth (Decisions, Non-Goals, per-task `约束:`) that can be audited deterministically — not just "vibes review"
- The scorecard file is a paired artifact, not throwaway chat
- Drives a feedback loop: review → tasks.md `## N. Review fixes` → re-review → `status: resolved`

### Workflow

**1. Locate the triplet:**
```bash
PLAN_PREFIX="<date>-<topic>"   # e.g. 2026-05-05-ai-dashboard-spec-generator
PLANS_DIR="docs/plans"
test -f "$PLANS_DIR/$PLAN_PREFIX-design.md"
test -f "$PLANS_DIR/$PLAN_PREFIX-tasks.md"
```

**2. Dispatch a `general-purpose` subagent** with the template at `plan-scorecard-reviewer.md`, filling:
- `{PLAN_PREFIX}` — date+topic prefix
- `{PLANS_DIR}` — usually `docs/plans`
- `{PROJECT_ROOT}` — absolute path to project
- `{CONVENTIONS_FILE}` — usually `CLAUDE.md` (or whatever the project uses); empty string if none

Use `general-purpose` (not `superpowers:code-reviewer`) — the agent needs broad Read/Write across the repo and must extract criteria from design/tasks dynamically.

**3. Subagent writes** to `$PLANS_DIR/$PLAN_PREFIX-review.md`. Do NOT have it modify any existing file.

**4. Report back to user:** total score, Critical/Major/Minor counts, status recommendation. Do not paste the report body — the user will read the file.

### Rubric (9 dimensions, weights sum to 100)

| # | Dimension | Weight | What to check |
|---|-----------|--------|---------------|
| 1 | 约束遵守度 | 20 | Every "约束:" line in tasks.md — does the code respect it? |
| 2 | Non-Goals 边界 | 15 | design.md Non-Goals — any quiet violations? |
| 3 | Decisions 一致性 | 15 | Each Decision in design.md — does the implementation match? |
| 4 | 任务勾选真实性 | 10 | Spot-check `[x]` tasks against actual code/tests |
| 5 | 设计-实现同步 | 8 | Does design.md still describe abandoned approaches? |
| 6 | 项目约定 | 10 | `CLAUDE.md` (or equivalent) rules respected? |
| 7 | 测试覆盖关键 case | 10 | Reverse cases named in "约束:" — are they tested? |
| 8 | 代码质量基线 | 7 | Naming, complexity, obvious duplication |
| 9 | 可验证性 | 5 | Are validation steps in tasks.md clear and reproducible? |

Per-dimension score: 1-10. Contribution: `weight × score / 10`. Total: out of 100.

### Issue Tiers and Cycle

Issues are sorted into three tiers, each with a distinct remediation path:

| Tier | Examples | Remediation |
|------|----------|-------------|
| **Critical** | Violates a Non-Goal, exposes secrets, broken in production | Stop and fix before further work; review `status: issues-found` |
| **Major** | Violates a Decision, missed `约束:`, missing key test | Append `## N. Review fixes` to **tasks.md** (do NOT touch existing `[x]` tasks); re-review when done |
| **Minor** | Naming, comments, small dup, mock drift | Fix directly in code; append a `## Fix Log` entry to **review.md** |

**Never modify an already-checked `[x]` task.** Append-only preserves the time-line: original tasks reflect "what we believed was done"; review-driven fixes are a separate, traceable round.

If issues are large enough to warrant a redirect (architecture-level), recommend a v2 plan triplet (`<new-date>-<topic>-{design,tasks,review}.md`) rather than stretching the existing tasks.md.

### Status Field

Review file frontmatter carries `status:`:

- `draft` — review in progress
- `issues-found` — Critical or Major issues exist; remediation pending
- `resolved` — all issues addressed (Major fixes shipped via tasks.md, Minor fixes logged in Fix Log)

Cycle: `draft → issues-found → (fixes via tasks.md or code) → resolved`. A review stuck in `issues-found` for too long is a tech-debt signal worth surfacing.

### Critical Rules for Plan Scorecard Mode

**DO:**
- Cite specific `file:line` for every deduction
- Name the violated source (`task §11.2 约束`, `Decision 7`, `Non-Goal #3`, `CLAUDE.md: handler 不直读 repository`)
- Be honest — give high scores when the implementation deserves them
- Leave a tier empty (write "无" / "None") when no issues qualify

**DON'T:**
- Score on vibes — every deduction needs evidence
- Deduct for "future-proofing" the plan didn't require
- Modify any existing `[x]` task — append-only
- Run tests/builds in the agent — keep it static and deterministic; the user runs validation commands

See template at: requesting-code-review/plan-scorecard-reviewer.md
