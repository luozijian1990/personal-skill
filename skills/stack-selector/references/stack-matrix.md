# 选型矩阵：组件 × 语言 × 运行约束

这是 stack-selector 的稳定默认技术库。先确认系统组件、语言和运行约束，再读取对应章节。每个维度最多
保留一个推荐方案和一个备选方案；没有明确收益时使用推荐方案。

当前矩阵只覆盖运维类 Python / Go 项目，不是通用语言选型大全。

## 目录

- [A. Backend](#a-backend)
- [B. Worker / Scheduler](#b-worker--scheduler)
- [C. Agent](#c-agent)
- [D. CLI](#d-cli)
- [E. Kubernetes Controller / Operator](#e-kubernetes-controller--operator)
- [F. 数据与存储](#f-数据与存储)
- [G. 通信方式](#g-通信方式)
- [H. 安全与运行基线](#h-安全与运行基线)
- [I. 工程化](#i-工程化)

---

## A. Backend

默认是模块化单体 Backend。表中的数据访问、认证和授权都需要结合项目确认，不因为看到 CRUD 或登录页
就自动采用 ORM、JWT 或 RBAC。

| 维度 | Python | Go | 推荐默认与备选条件 |
|---|---|---|---|
| Web 框架 | **FastAPI** | **Gin** | Python 默认 FastAPI；Go 默认 Gin，端点少且团队偏标准库风格时备选 chi |
| 数据访问 | **SQLAlchemy + Alembic** | **sqlc** | Python 可只用 SQLAlchemy Core/显式 SQL；Go 默认 sqlc，团队更需要 ORM 体验时备选 GORM |
| 配置 | **pydantic-settings** | **viper** | 默认从环境变量或挂载配置读取；Secret 不写入配置文件和仓库 |
| 结构化日志 | **structlog** | **slog** | 默认输出 JSON 或稳定键值字段并携带 request/task ID；仅在现有日志栈有要求时替换 |
| 认证 | **复用现有 SSO / OIDC / 网关身份** | 同左 | 内部系统默认复用已有身份设施；没有可复用设施时备选服务端 Session，不因登录页默认 JWT |
| 授权 | 应用内角色与数据范围检查 | 同左 | 固定少量角色先写清规则；策略复杂且动态时备选 casbin |
| 数据校验 | FastAPI / Pydantic 内置 | go-playground/validator | 只在 API 边界校验输入，不重复堆校验框架 |
| HTTP 客户端 | **httpx** | **net/http** | 外部调用需要统一超时；Go 需要链式调用和统一重试时备选 go-resty |

---

## B. Worker / Scheduler

任务进度和定时配置只说明存在任务执行能力，不自动意味着独立 Worker 或任务队列。先选择最轻的可靠性层级：

```text
短任务同步执行 -> 进程内后台任务 -> 独立 Worker + 持久化队列
```

| 维度 | Python | Go | 推荐默认与升级条件 |
|---|---|---|---|
| 进程内后台任务 | **asyncio + 有界并发** | **goroutine + 有界 channel** | 默认把任务状态持久化到关系库；避免无上限创建任务 |
| 独立 Worker | **Celery** | **asynq** | 仅在需要重启恢复、自动重试、多实例消费或独立扩缩容时使用；会引入 Redis 等队列依赖 |
| Scheduler | **APScheduler** | **robfig/cron** | 单实例可与 Backend 同进程；多实例必须处理选主、重复触发和补偿 |
| 任务状态 | 关系库任务表 | 同左 | 记录状态、时间、错误和操作者；队列不是业务状态的唯一来源 |
| 取消与恢复 | 取消令牌 + 检查点 | `context` + 检查点 | 只有可安全中断的任务才标记为可取消；恢复语义必须在 SDD 中明确 |

---

## C. Agent

只有需要目标主机本地采集/执行、中心端不可达，或大规模分发确有收益时才增加 Agent。多数 Agent 不需要
Web 框架和中心数据库。

| 维度 | Python | Go | 推荐默认与备选条件 |
|---|---|---|---|
| 系统指标采集 | **psutil** | **gopsutil** | 只采集需求明确的指标，避免无边界采集 |
| 上报方式 | 调 Backend API | 调 Backend API | 默认 push；已有 Prometheus pull 体系时备选暴露 `/metrics` |
| 断网缓冲 | **SQLite** | **bbolt** | 只有允许断网续传时启用，并设置容量和保留上限 |
| 指令通道 | 轮询 Backend | 轮询 Backend | 默认轮询；低延迟且连接稳定性要求明确时再考虑长连接 |
| 执行控制 | `asyncio` 超时 + Semaphore | `context` 超时 + 有界 channel | 命令白名单、参数校验、并发上限和审计不可省略 |
| 生命周期 | signal + 取消上下文 | `os/signal` + `context` | 支持健康状态、优雅退出和有上限的资源使用 |
| 分发 | 容器或 PyInstaller | **单二进制 + systemd** | 大量主机、资源敏感时默认 Go；团队固定 Python 时才采用 Python 备选 |

---

## D. CLI

CLI 可以与 Backend 或 Agent 同时存在，用于自动化、批处理和管理员操作。

| 维度 | Python | Go | 推荐默认与备选条件 |
|---|---|---|---|
| CLI 框架 | **Typer** | **Cobra** | 小型 Python CLI 也可直接 argparse；不要为了单个命令引入复杂框架 |
| 配置 | pydantic-settings | viper | 与 Backend / Agent 复用配置约定，但不要把服务端 Secret 下发到 CLI |
| 输出 | rich + `--json` | `text/tabwriter` + `--json` | 人读用表格，自动化调用提供稳定 JSON |
| 危险操作 | 显式确认 | 显式确认 | 非交互自动化通过专门参数确认，并保留操作审计 |
| 分发 | pipx | 单二进制 | 需要跨大量机器分发时倾向 Go |

---

## E. Kubernetes Controller / Operator

普通 Pod、Deployment、Node 查询和操作只需 Backend / Worker 调用 Kubernetes API。只有持续监听资源事件、
协调期望状态或管理 CRD 时才引入 Controller / Operator。

| 维度 | 推荐 | 备选与条件 |
|---|---|---|
| 实现方式 | **Go + controller-runtime / client-go** | 团队只能使用 Python 且协调逻辑简单时备选 Kopf |
| 状态协调 | 幂等 Reconcile + 状态条件 | 不用定时全量扫描替代事件协调，除非目标系统不提供 watch |
| 权限 | 最小 RBAC + 独立 ServiceAccount | 不复用集群管理员凭证 |
| 可用性 | 单活或 leader election | 多副本时启用 leader election，并明确重试和退避 |

---

## F. 数据与存储

| 维度 | 推荐 | 备选与升级条件 |
|---|---|---|
| 关系数据 | **复用已有 PostgreSQL / MySQL** | 单机 Docker、小数据量且接受文件级备份时备选 SQLite |
| 时序数据 | **先评估关系数据库** | 数据量、保留周期或时间范围查询超过关系库能力时备选 VictoriaMetrics |
| 缓存 | **单实例不设缓存或使用进程内缓存** | 多实例需要共享、明确热点或缓存一致性收益时备选 Redis |
| 文件 | **小量文件使用持久化本地卷** | 多实例、容量增长或生命周期管理要求明确时备选现有对象存储 |
| 任务状态 | **关系库任务表** | 不用内存和消息队列代替可审计的业务状态 |
| 迁移与备份 | 版本化迁移 + 定期备份恢复演练 | SQLite 使用一致性文件备份；服务数据库复用现有备份体系 |
| 保留策略 | 为任务结果、审计和日志设置期限 | 合规或调查需要更长周期时单独确认归档位置和成本 |

趋势图只是时序数据的信号。小数据量、短保留时间和简单查询可以先用关系数据库，不默认时序数据库。

---

## G. 通信方式

| 场景 | 推荐 | 备选与升级条件 |
|---|---|---|
| React 调 Backend | **HTTP JSON API** | 已有明确契约和多语言内部调用需求时备选 gRPC，但不用于浏览器直连 |
| 任务进度与低频状态 | **轮询** | 需要服务端单向及时推送时备选 SSE |
| 双向高频通信 | **先确认轮询 / SSE 不足** | 确有双向高频交互时使用 `coder/websocket` |
| Backend 到 Worker | **进程内调用或任务表** | 需要持久化消费、自动重试和多实例时备选任务队列 |
| Backend 到 Agent | **Agent 轮询命令并上报结果** | 延迟要求明确且网络稳定时备选长连接 |
| 跨服务事件 | **直接调用或关系库事务** | 明确存在异步解耦、积压或削峰时备选现有消息系统 |

Go WebSocket 新项目默认推荐 `coder/websocket`，因为 API 更轻、对 `context` 的支持更自然。不要再以
`gorilla/websocket`「已归档」作为推荐理由；维护旧项目时根据现有依赖和迁移收益决定是否更换。

---

## H. 安全与运行基线

这些维度必须在确认单中说明处理方式，但不要求每项引入第三方组件。

| 维度 | 默认处理 | 何时升级 |
|---|---|---|
| 配置与 Secret | 环境变量、只读挂载或现有 Secret 系统；仓库和日志不出现明文 | Kubernetes 使用 Secret 或现有外部 Secret 系统 |
| 健康检查与退出 | 提供存活/就绪检查；收到信号后停止接单并限时等待任务结束 | 有负载均衡或编排平台时接入 readiness 和摘流流程 |
| 日志与错误 | 结构化日志，带 request/task ID，错误记录上下文但隐藏 Secret | 已有集中日志平台时接入；不为小工具单独建设平台 |
| 超时、重试、并发 | 所有外部调用有超时；只对可重试错误退避；设置全局和目标级并发上限 | 出现依赖雪崩风险时再评估熔断 |
| 幂等与重复提交 | 写操作使用幂等键、唯一约束或状态机保护 | 跨系统操作需要明确去重窗口和补偿 |
| 数据迁移与备份 | 版本化迁移；写明备份周期、恢复步骤和责任人 | 数据重要性提高时做自动恢复演练 |
| 操作审计 | 记录谁在何时对什么目标执行什么操作及结果 | 高风险操作增加审批和不可篡改归档 |
| 长任务取消与恢复 | 状态持久化；仅在安全点响应取消；默认失败后人工重试 | 需要重启恢复或自动重试时拆 Worker / 引入持久化队列 |
| 远程命令白名单 | 允许的动作模板 + 参数校验，禁止任意 shell 拼接 | 特殊命令走单独审批和更严格权限 |
| 凭证保存 | 引用 Secret，不回传前端、不写任务日志；使用最小权限和轮换 | 多租户或高风险环境接入专用凭证系统 |
| 结果与日志保留 | 设置默认期限、容量上限和清理任务 | 合规或调查要求出现时归档到现有存储 |

OpenTelemetry、Redis、MQ 和独立日志平台均为按需组件，不属于默认运行基线。

---

## I. 工程化

| 维度 | Python | Go |
|---|---|---|
| 测试 | **pytest** | **testing + testify** |
| 数据库迁移 | **Alembic** | **golang-migrate** |
| API 文档 | FastAPI OpenAPI | swaggo |
| 依赖与构建 | **uv** | **go mod** |
| 代码质量 | **ruff** | **golangci-lint** |

工程化选择应复用仓库已有工具；表中默认值只用于新项目或仓库没有既定约定时。
