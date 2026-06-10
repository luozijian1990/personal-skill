# Go Agent Template

## Directory Structure

```
CLAUDE.md
AGENTS.md -> CLAUDE.md
agent/
├── cmd/
│   └── main.go
├── config/
│   └── config.go
├── config.yaml
├── internal/
│   ├── agent/
│   ├── tools/
│   ├── prompts/
│   ├── model/
│   └── handler/
│       └── health.go
├── pkg/
│   └── logger/
│       └── logger.go
├── logs/
│   └── .gitkeep
├── Makefile
├── .gitignore
├── README.md
├── go.mod
└── go.sum
```

## File Contents

### cmd/main.go

```go
package main

import (
	"flag"
	"fmt"
	"net/http"

	"go.uber.org/zap"

	"{module}/config"
	"{module}/internal/handler"
	"{module}/pkg/logger"
)

func main() {
	configPath := flag.String("config", "config.yaml", "path to config file")
	flag.Parse()

	cfg, err := config.Load(*configPath)
	if err != nil {
		panic(fmt.Sprintf("failed to load config: %v", err))
	}

	if err := logger.Init(logger.Config{
		Level:      cfg.Log.Level,
		File:       cfg.Log.File,
		MaxSize:    cfg.Log.MaxSize,
		MaxBackups: cfg.Log.MaxBackups,
		MaxAge:     cfg.Log.MaxAge,
		Compress:   cfg.Log.Compress,
	}); err != nil {
		panic(fmt.Sprintf("failed to init logger: %v", err))
	}
	defer logger.Sync()

	mux := http.NewServeMux()

	// Routes
	handler.RegisterHealthRoutes(mux)

	addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	logger.Info("server starting", zap.String("addr", addr))

	// Wrap with CORS
	corsHandler := handler.CORSMiddleware(mux)

	if err := http.ListenAndServe(addr, corsHandler); err != nil {
		logger.Error("server failed", zap.Error(err))
	}
}
```

### config/config.go

```go
package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Server ServerConfig `yaml:"server"`
	Log    LogConfig    `yaml:"log"`
}

type ServerConfig struct {
	Host string `yaml:"host"`
	Port int    `yaml:"port"`
}

type LogConfig struct {
	Level      string `yaml:"level"`
	File       string `yaml:"file"`
	MaxSize    int    `yaml:"max_size"`
	MaxBackups int    `yaml:"max_backups"`
	MaxAge     int    `yaml:"max_age"`
	Compress   bool   `yaml:"compress"`
}

func Load(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config file: %w", err)
	}

	cfg := &Config{
		Server: ServerConfig{
			Host: "0.0.0.0",
			Port: 8080,
		},
		Log: LogConfig{
			Level:      "info",
			File:       "logs/app.log",
			MaxSize:    10,
			MaxBackups: 30,
			MaxAge:     30,
			Compress:   true,
		},
	}

	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("parse config file: %w", err)
	}

	return cfg, nil
}
```

Replace `{module}` with the actual Go module path.

### config.yaml

```yaml
server:
  host: "0.0.0.0"
  port: 8080

log:
  level: "info"
  file: "logs/app.log"
  max_size: 10       # MB
  max_backups: 30
  max_age: 30        # days
  compress: true
```

### internal/handler/health.go

```go
package handler

import (
	"encoding/json"
	"net/http"
)

func RegisterHealthRoutes(mux *http.ServeMux) {
	mux.HandleFunc("GET /health", healthCheck)
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

// CORSMiddleware wraps an http.Handler with CORS headers.
func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}
```

### pkg/logger/logger.go

```go
package logger

import (
	"os"
	"path/filepath"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"gopkg.in/natefinch/lumberjack.v2"
)

var Log *zap.Logger

type Config struct {
	Level      string
	File       string
	MaxSize    int // MB
	MaxBackups int
	MaxAge     int // days
	Compress   bool
}

func Init(cfg Config) error {
	level := parseLevel(cfg.Level)

	// 确保日志目录存在
	if cfg.File != "" {
		dir := filepath.Dir(cfg.File)
		if err := os.MkdirAll(dir, 0755); err != nil {
			return err
		}
	}

	// 编码配置
	encoderConfig := zapcore.EncoderConfig{
		TimeKey:        "time",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		MessageKey:     "msg",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.LowercaseLevelEncoder,
		EncodeTime: func(t time.Time, enc zapcore.PrimitiveArrayEncoder) {
			enc.AppendString(t.Format("2006-01-02 15:04:05"))
		},
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}

	var cores []zapcore.Core

	// 控制台输出
	consoleEncoder := zapcore.NewConsoleEncoder(encoderConfig)
	consoleCore := zapcore.NewCore(consoleEncoder, zapcore.AddSync(os.Stdout), level)
	cores = append(cores, consoleCore)

	// 文件输出（使用 lumberjack 实现日志轮转）
	if cfg.File != "" {
		fileWriter := &lumberjack.Logger{
			Filename:   cfg.File,
			MaxSize:    cfg.MaxSize,
			MaxBackups: cfg.MaxBackups,
			MaxAge:     cfg.MaxAge,
			Compress:   cfg.Compress,
		}
		fileEncoder := zapcore.NewConsoleEncoder(encoderConfig)
		fileCore := zapcore.NewCore(fileEncoder, zapcore.AddSync(fileWriter), level)
		cores = append(cores, fileCore)
	}

	core := zapcore.NewTee(cores...)
	Log = zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))

	return nil
}

func parseLevel(level string) zapcore.Level {
	switch level {
	case "debug":
		return zapcore.DebugLevel
	case "info":
		return zapcore.InfoLevel
	case "warn":
		return zapcore.WarnLevel
	case "error":
		return zapcore.ErrorLevel
	default:
		return zapcore.InfoLevel
	}
}

func Info(msg string, fields ...zap.Field) {
	Log.Info(msg, fields...)
}

func Warn(msg string, fields ...zap.Field) {
	Log.Warn(msg, fields...)
}

func Error(msg string, fields ...zap.Field) {
	Log.Error(msg, fields...)
}

func Debug(msg string, fields ...zap.Field) {
	Log.Debug(msg, fields...)
}

func Sync() {
	if Log != nil {
		_ = Log.Sync()
	}
}
```

### CLAUDE.md

**注意**：生成 `CLAUDE.md` 时，必须先写入 `references/claude_md_preamble.md` 的完整内容，再写一行 `---` 分隔符，最后追加下面这段项目特定内容（详见 SKILL.md 的「CLAUDE.md 内容组合规则」）。

Generate with the actual project name and module replacing `{project_name}` and `{module}`:

```markdown
# {project_name}

## 项目说明

Go Agent 服务，使用标准库 net/http 构建轻量 HTTP 接口。

## 技术栈

| 类型 | 选型 |
|------|------|
| Web 框架 | net/http（标准库，轻量） |
| 日志 | zapcore + lumberjack（`pkg/logger/`），控制台与文件均为 Console 格式，支持轮转 |
| 配置 | config.yaml + yaml.v3 解析，支持 `-config` flag 指定文件路径 |
| 模块名 | `{module}` |

## 目录结构

```
cmd/main.go          # 入口：加载配置、初始化 logger、注册路由、启动服务
config/config.go     # 配置结构体与 Load() 函数
internal/
├── agent/           # Agent 核心逻辑
├── tools/           # 工具定义
├── prompts/         # Prompt 模板
├── model/           # 数据模型
└── handler/         # HTTP handler + CORS 中间件
pkg/logger/          # 全局 logger 封装
```

## 开发约定

- **新增配置项**：在 `config/config.go` 的对应 struct 中添加，同步更新 `config.yaml`
- **使用日志**：`logger.Info("msg", zap.String("key", val))`，使用 `zap.Field` 结构化字段
- **新增接口**：在 `internal/handler/` 下添加，在 `cmd/main.go` 的 `mux` 中注册
- **Agent 工具**：在 `internal/tools/` 下定义，在 `internal/agent/` 中组装
- **Prompt 模板**：统一放 `internal/prompts/`，不要硬编码在业务逻辑里
- **错误处理**：使用 `fmt.Errorf("context: %w", err)` 包装错误向上传递
- **健康检查**：`GET /health` 已内置，不要修改

## 启动方式

```bash
go mod tidy
make run
# 或指定配置文件
go run cmd/main.go -config /path/to/config.yaml
```

默认端口 8080，可在 `config.yaml` 中修改。
```

### AGENTS.md

Create as a symlink: `ln -s CLAUDE.md AGENTS.md`

### Makefile

```makefile
.PHONY: run build test clean

APP_NAME := agent
BUILD_DIR := ./bin

run:
	go run cmd/main.go

build:
	go build -o $(BUILD_DIR)/$(APP_NAME) cmd/main.go

test:
	go test ./...

clean:
	rm -rf $(BUILD_DIR)
```

### .gitignore

```
# Binaries
bin/
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test
*.test
*.out

# Dependency
vendor/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store

# Logs
logs/

# Config overrides
*.local.yaml
```

### README.md

Use the following template:

```markdown
# {project_name}

## Description

TODO: Add project description.

## Quick Start

1. Install dependencies:

```bash
go mod tidy
```

2. Run the server:

```bash
make run
```

Or with a custom config:

```bash
go run cmd/main.go -config /path/to/config.yaml
```

The server will start at `http://localhost:8080`.

## Configuration

Configuration is managed via `config.yaml`:

```yaml
server:
  host: "0.0.0.0"    # Server host
  port: 8080          # Server port

log:
  level: "info"       # Log level (debug/info/warn/error)
  file: "logs/app.log"
  max_size: 10        # Max size in MB before rotation
  max_backups: 30     # Max number of old log files
  max_age: 30         # Max days to retain old log files
  compress: true      # Compress rotated files
```

## Directory Structure

```
agent/
├── cmd/main.go          # Application entry point
├── config/              # Configuration loading
├── config.yaml          # Configuration file
├── internal/
│   ├── agent/           # Agent core logic
│   ├── tools/           # Tool definitions
│   ├── prompts/         # Prompt templates
│   ├── model/           # Data models
│   └── handler/         # HTTP handlers + CORS
├── pkg/                 # Reusable packages
│   └── logger/          # Logging (zap + lumberjack)
├── logs/                # Log files (auto-generated)
└── Makefile             # Build commands
```
```

### go.mod

Initialize with `go mod init {module}`, then run `go mod tidy`.

Required dependencies:
- `go.uber.org/zap`
- `gopkg.in/natefinch/lumberjack.v2`
- `gopkg.in/yaml.v3`
```
