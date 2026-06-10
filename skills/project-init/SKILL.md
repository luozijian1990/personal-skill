---
name: project-init
description: "Initialize standardized Python or Golang projects with proper directory structure, logging, config, and web framework setup. Use this skill whenever the user wants to create a new project, scaffold a project, init a project, start a new backend service, start a new agent project, or mentions creating a new Python/Go application — even if they don't explicitly say 'init'."
---

# 项目初始化

该技能用于初始化标准化的 Python 和 Golang 项目，涵盖目录结构、日志、配置、Web 框架、错误处理、CORS、健康检查、git 初始化、.gitignore 和 README 生成。

## 工作流程

1. 向用户确认两个问题（如果上下文中已经明确则跳过）：
   - **语言**：Python 还是 Golang？
   - **类型**：backend（后端服务）还是 agent（智能体）？

2. 根据用户选择，读取对应的模板文件，生成完整的项目脚手架。

3. 生成完毕后，输出创建内容的摘要。

## 初始化前检查

- 检查当前目录是否已有 git 仓库（`git rev-parse --git-dir`），如果没有则执行 `git init -b main`（旧版本 git 没有 `-b` 参数时，先 `git init` 再 `git symbolic-ref HEAD refs/heads/main`）。
- 根据类型在 `backend/` 或 `agent/` 目录下创建项目。
- 所有需要文件的目录至少包含一个占位文件或 `__init__.py`。
- 创建 `logs/` 目录，放入 `.gitkeep` 保持目录存在。

## 分支策略（脚手架生成后执行）

在所有项目文件、`.gitignore`、`README.md`、`CLAUDE.md` 等都写入完毕后，按下面顺序建立分支：

1. **确保在 `main` 分支上完成首次提交**：
   - `git add -A`
   - `git commit -m "chore: scaffold project via project-init"`（如果当前不在 `main`，先 `git checkout -b main` 或 `git branch -M main`）。
   - `main` 是正式发布分支，初始化之后默认不再直接在上面提交。
2. **创建并切换到 `test` 开发分支**：
   - `git checkout -b test`
   - 后续所有开发都在 `test` 上进行；`main` 仅用于发布正式环境。
3. 如果仓库在初始化前已经存在并且已有 `test` 分支，直接 `git checkout test` 而不是重新创建，避免覆盖既有工作。
4. 最终输出摘要时，明确告知用户：
   - 当前所在分支是 `test`；
   - `main` 已保留为正式发布分支，请勿直接在 `main` 上开发；
   - 发布到正式环境时，从 `test`（或后续派生的 feature 分支）合并回 `main`。

## 模板参考

根据用户选择，从本技能的 `references/` 目录读取对应的模板文件：

| 语言   | 类型    | 模板文件                            |
|--------|---------|-------------------------------------|
| Python | backend | `references/python_backend.md`      |
| Python | agent   | `references/python_agent.md`        |
| Go     | backend | `references/go_backend.md`          |
| Go     | agent   | `references/go_agent.md`            |

读取选定的模板文件，严格按照模板内容生成所有项目文件。

## 通用标准（所有模板共享）

### .gitignore
生成语言对应的 .gitignore 文件，始终包含 `logs/`。

### README.md
生成 README.md，包含以下章节：
- 项目名称与描述
- 启动/运行方式
- 配置说明（列出所有配置项及默认值）
- 目录结构概览

### 健康检查
所有 Web 项目暴露 `GET /health` 端点，返回 `{"status": "ok"}`。

### 端口配置
端口始终定义在配置文件/类中，并提供合理的默认值（Python 默认 8000，Go 默认 8080）。

### CORS
所有 Web 项目默认加载 CORS 中间件，开发环境下允许所有来源。

## CLAUDE.md 放置规则

- `CLAUDE.md` 和 `AGENTS.md` 必须创建在 **git 仓库根目录**，而不是 `backend/` 或 `agent/` 子目录下。只有放在仓库根目录，Claude Code 才会自动读取。
- 如果项目文件在子目录（如 `backend/`、`agent/`）下创建，`CLAUDE.md` 仍然要放在上一级的仓库根目录。

## CLAUDE.md 内容组合规则

生成 `CLAUDE.md` 时，**必须**按以下顺序拼接两段内容，中间用一行分隔符 `---` 隔开：

1. **通用行为准则（preamble）**：从 `references/claude_md_preamble.md` 读取，原样写入，**不要改动**。这是所有项目共享的 LLM 编码行为约束。
2. **项目特定内容**：从对应语言/类型的模板（如 `references/python_backend.md`）的 `### CLAUDE.md` 段落读取，替换占位符（`{project_name}`、`{module}` 等）后写入。

最终 `CLAUDE.md` 的结构应当是：

```
<preamble 全部内容>

---

<项目特定内容（# {project_name} 开头那段）>
```

## 注意事项

- 不要让用户手动创建文件，所有文件自动生成。
- 脚手架生成后，提醒用户安装依赖（`pip install -r requirements.txt` 或 `go mod tidy`）。
- 如果用户提供了项目名称，在 README 和模块名中使用该名称；否则使用目录名。
