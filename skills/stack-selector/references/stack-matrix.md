# 选型矩阵：形态 × 语言 × 维度

这是 stack-selector 的知识库。每个维度给出 Python / Golang 的候选、**推荐默认**，以及何时该换备选。
用法：先定项目形态和语言，再到对应章节按维度查，不用整篇背。

> 库的活跃度会变。给一线选型时，归档/停更的库不要当默认推荐（本文件已剔除已知归档项，
> 例如 Go 的 `gorilla/websocket` 已归档，新项目默认用 `coder/websocket`）。

## 目录

- [A. backend 形态](#a-backend-形态)
  - [A1. 核心维度](#a1-核心维度必填)
  - [A2. 按需维度](#a2-按需维度看-mock-信号)
- [B. 采集 / 执行型 agent 形态](#b-采集--执行型-agent-形态)
- [C. CLI 形态](#c-cli-形态)
- [D. 工程化横切（贯穿三种形态）](#d-工程化横切贯穿三种形态)
- [E. 数据库选择速查](#e-数据库选择速查)

---

## A. backend 形态

### A1. 核心维度（必填）

| 维度 | Python | Golang | 推荐默认 & 切换条件 |
|---|---|---|---|
| **Web 框架** | FastAPI | `net/http`(Go 1.22+ 的 ServeMux 已支持 method+路径路由) / chi / Gin | Python 默认 **FastAPI**（自带校验+OpenAPI）。Go：富路由+中间件栈的完整服务用 **Gin**；只要轻量路由+中间件用 **chi**（与 stdlib 完全兼容）；端点极少时直接 **net/http**。 |
| **ORM / 数据访问** | SQLAlchemy(+Alembic 迁移) / SQLModel | GORM / sqlx / sqlc | Python 默认 **SQLAlchemy + Alembic**；想和 pydantic 打通用 **SQLModel**。Go：要 ORM 体验用 **GORM**；想写原生 SQL 但要省去扫描样板用 **sqlx**；想由 SQL 反向生成类型安全代码用 **sqlc**（团队 SQL 熟练时最稳）。 |
| **数据库** | PostgreSQL / MySQL / SQLite | 同左 | 默认 **PostgreSQL**（功能全、JSON 支持好）。单机/嵌入式/工具类用 **SQLite**。已有 MySQL 生态就 MySQL。详见 [E 节](#e-数据库选择速查)。 |
| **配置管理** | pydantic-settings / dynaconf | viper / koanf | Python 默认 **pydantic-settings**（和 FastAPI 同源，类型校验白送）。Go 默认 **viper**（多来源+热加载）；想更轻、模块化用 **koanf**。 |
| **日志** | loguru / structlog | slog(标准库) / zap / zerolog | Python 默认 **loguru**（开箱即用）；要结构化+严肃生产用 **structlog**。Go 默认 **slog**（Go 1.21+ 标准库，无需第三方）；追求极致性能用 **zap** 或 **zerolog**。 |
| **认证** | PyJWT / python-jose（+ OAuth2） | golang-jwt | 默认 **JWT**（Python: PyJWT；Go: golang-jwt）。对接外部身份提供方用 **OAuth2/OIDC**。 |
| **授权（RBAC）** | casbin (pycasbin) | casbin | 有角色/权限模型时用 **casbin**（两种语言同一套模型，运维平台多角色场景常用）。无角色区分则不需要。 |

### A2. 按需维度（看 mock 信号才填，否则显式排除）

| 维度 | Python | Golang | 推荐默认 & 切换条件 |
|---|---|---|---|
| **缓存** | cachetools / aiocache（进程内）；redis-py（Redis） | 内置 `map`+`sync.RWMutex` / ristretto（进程内）；go-redis（Redis） | **先进程内缓存**，多实例需共享/需持久化才上 **Redis**。无热点读信号则不引入。 |
| **实时通信** | 轮询（无需库）/ sse-starlette（SSE）/ FastAPI 内置 WebSocket | 轮询 / 标准库 SSE / **coder/websocket**（WS） | **默认轮询**；服务端单向推用 **SSE**；双向高频才上 **WS**。Go 的 WS 新项目用 **coder/websocket**（context 原生、并发写安全）；维护老代码才用已归档的 gorilla/websocket。 |
| **异步任务 / 后台 worker** | Celery / arq / Dramatiq | goroutine+channel / asynq | 简单后台任务：Python 用 **arq**（基于 Redis，轻）或 **Dramatiq**；重型分布式任务用 **Celery**。Go 优先 **goroutine+channel**，需要持久化任务队列用 **asynq**（基于 Redis）。 |
| **定时调度** | APScheduler | robfig/cron | 巡检/周期检查的命根子。Python **APScheduler**，Go **robfig/cron**。 |
| **消息队列** | aiokafka(Kafka) / pika(RabbitMQ) / nats-py(NATS) | sarama 或 kafka-go(Kafka) / amqp091-go(RabbitMQ) / nats.go(NATS) | **运维内部工具极少需要**。真有跨服务事件/削峰才上。轻量首选 **NATS**；已有 Kafka 生态用 Kafka。无强证据则显式排除。 |
| **可观测性** | prometheus-client + opentelemetry-python | client_golang + opentelemetry-go | 做指标暴露/对接 Prometheus 时引入。指标用 **Prometheus client**，链路追踪用 **OpenTelemetry**。 |
| **时序数据库** | （客户端：对应库） | （客户端：对应库） | 指标趋势类数据用 **VictoriaMetrics**（省资源、兼容 Prometheus 协议）/ **Prometheus** / **InfluxDB**。**别把时序塞关系库。** |
| **远程执行 / SSH** | paramiko / asyncssh | golang.org/x/crypto/ssh | 远程主机操作时引入。Python 异步场景用 **asyncssh**，否则 **paramiko**；Go 用标准扩展库 **x/crypto/ssh**。 |
| **gRPC** | grpcio + grpcio-tools | google.golang.org/grpc | 运维平台多服务内部通信时引入。对外 HTTP API 不需要。 |
| **K8s 客户端** | kubernetes（官方 client） | client-go | 对接 K8s 资源时引入。Go 的 **client-go** 是一等公民，对接深度操作优先 Go。 |
| **数据校验** | pydantic（FastAPI 白送，无需额外引入） | go-playground/validator | Python 用 FastAPI 时校验已内置。Go 需显式引入 **validator**。 |
| **HTTP 客户端** | httpx（异步友好）/ requests | net/http / go-resty | 调外部 API 时。Python 异步选 **httpx**。Go 标准库够用，想要链式/重试糖用 **go-resty**。 |
| **重试 / 退避 / 熔断** | tenacity | cenkalti/backoff + sony/gobreaker | 调用易抖动的外部依赖时引入，提升可靠性。 |
| **文件存储** | （本地 / boto3 等对象存储 SDK） | （本地 / 对应对象存储 SDK） | 小量文件本地落盘即可；规模化用对象存储（MinIO/S3 兼容）。 |

---

## B. 采集 / 执行型 agent 形态

agent 常驻主机，采集指标或执行指令，**多数时候不碰数据库，也不需要 Web 框架**。
backend 那张表基本不适用，按下面这套独立维度走。

| 维度 | 要敲定什么 | Python | Golang |
|---|---|---|---|
| **系统/进程指标采集** | CPU/内存/磁盘/网络/进程 | psutil | gopsutil |
| **上报方式** | push 还是 pull——**直接决定要不要 HTTP 服务面** | push: 调 server API / 推 Pushgateway/Kafka；pull: 用框架暴露 `/metrics` | 同左；pull 模式暴露 `/metrics` 用 **net/http** 即可，**别上 Gin** |
| **断网缓冲** | 网断了数据丢不丢——本地落盘 spool | SQLite / 本地文件 | bbolt / badger（嵌入式 KV）/ SQLite |
| **指令通道**（执行型） | 怎么收指令 | 轮询 server / 长连接 / 订阅 MQ | 同左 |
| **执行安全**（执行型） | 超时控制、并发上限、命令白名单——**agent 能在主机跑命令，这块不卡死会出事** | `asyncio` 超时 + 信号量 + 白名单校验 | `context` 超时 + 带缓冲 channel 限并发 + 白名单 |
| **资源自限** | agent 不能吃满宿主机——CPU/内存上限 | cgroup / 自身限流 | 同左，Go 内存占用天然更低 |
| **生命周期** | 优雅退出 + 信号处理 + 配置热加载（不重启换配置） | signal 处理 + watchdog 监听配置 | `os/signal` + `context` 取消 + fsnotify 监听配置 |
| **分发** | 怎么装到大量主机上 | PyInstaller 打包 / 容器化（带运行时，较重） | **单二进制 + systemd**（Go 在这点上完胜，是 agent 选 Go 的主因） |

> **选型提示**：采集/执行 agent 若要分发到大量主机、对资源敏感，**强烈倾向 Go**（单文件、无运行时依赖、内存低）。
> Python 写 agent 不是不行，但分发和资源占用是硬伤。

---

## C. CLI 形态

> 注意：React mock **反推不出 CLI**（前端 mock 对应的几乎必然是 backend）。
> CLI 形态通常是用户脱离 mock、明确说「做一个命令行工具」时才走这条线。

| 维度 | Python | Golang | 推荐默认 & 切换条件 |
|---|---|---|---|
| **CLI 框架** | Typer（基于类型注解，最省事）/ Click | Cobra（事实标准，kubectl/docker 都用它） | Python 默认 **Typer**，Go 默认 **Cobra**。 |
| **配置** | 同 backend（pydantic-settings / dynaconf） | viper（和 Cobra 同作者，天然搭配） | Go 的 Cobra+viper 是黄金组合。 |
| **输出格式** | rich（彩色/表格）/ tabulate；JSON 输出用标准库 | text/tabwriter（标准库表格）/ lipgloss | 给人看用表格，给机器用/管道用 **JSON**（务必支持 `--json`/`-o json`）。 |
| **交互** | rich（进度条/spinner）/ questionary（交互提问） | bubbletea（TUI）/ promptui（交互提问） | 长任务给进度条，危险操作给确认提示。 |
| **分发** | PyInstaller / pipx | 单二进制 | Go 单二进制分发体验最好。 |

---

## D. 工程化横切（贯穿三种形态）

这些不算「选型」，但确认单里最好带一句，省得 SDD 之后再补。

| 维度 | Python | Golang |
|---|---|---|
| **测试** | pytest | 标准库 testing + testify |
| **DB 迁移** | Alembic | golang-migrate |
| **API 文档** | FastAPI 自带 OpenAPI/Swagger（白送） | swaggo（Gin 等用注解生成 Swagger） |
| **依赖/构建** | uv / poetry | go mod（标准） |
| **代码质量** | ruff（lint+format 一把梭） | golangci-lint |

---

## E. 数据库选择速查

| 场景 | 选 | 理由 |
|---|---|---|
| 默认、功能全、要 JSON/复杂查询 | **PostgreSQL** | 运维平台默认首选 |
| 单机工具、嵌入式、零运维 | **SQLite** | 一个文件，无需独立部署 |
| 已有 MySQL 生态/团队熟 | **MySQL** | 不折腾，跟团队走 |
| 指标趋势、时间序列数据 | **时序库**（VictoriaMetrics/Prometheus/InfluxDB） | 关系库存时序早晚查询爆炸 |
| agent 本地断网缓冲 | **SQLite / bbolt / badger** | 嵌入式，无需独立 DB 进程 |

**一句话**：业务关系数据 → PostgreSQL；工具单机 → SQLite；指标时序 → 时序库；agent 本地 → 嵌入式 KV。
不要用一种库扛所有场景。
