# Python Backend Template

## Directory Structure

```
CLAUDE.md
AGENTS.md -> CLAUDE.md
backend/
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── health.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
└── logs/
    └── .gitkeep
```

## File Contents

### main.py

```python
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import health
from app.utils.logger import logger, setup_logger

# 初始化 logger
setup_logger({
    "log": {
        "level": settings.LOG_LEVEL,
        "file": settings.LOG_FILE,
        "max_size_mb": settings.LOG_MAX_SIZE_MB,
        "backup_count": settings.LOG_BACKUP_COUNT,
    }
})

app = FastAPI(title=settings.APP_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Register routers
app.include_router(health.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
```

### app/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "backend"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_SIZE_MB: int = 10
    LOG_BACKUP_COUNT: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
```

### app/__init__.py

```python
```

### app/routers/__init__.py

```python
```

### app/routers/health.py

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

### app/models/__init__.py

```python
```

### app/schemas/__init__.py

```python
```

### app/services/__init__.py

```python
```

### app/utils/logger.py

```python
"""
最简洁的全局 logger - Go 语言风格
"""

import os
import sys
from loguru import logger as _logger


def init_logger(config: dict = None):
    """初始化全局 logger"""
    # 移除默认处理器
    _logger.remove()

    if config is None:
        config = {}

    log_config = config.get('log', {})
    level = log_config.get('level', 'INFO').upper()

    # 控制台配置
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    _logger.add(
        sys.stderr,
        format=console_format,
        level=level,
        colorize=True
    )

    # 文件配置
    log_file = log_config.get('file')
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        )

        _logger.add(
            log_file,
            format=file_format,
            level=level,
            rotation=log_config.get('max_size_mb', 10) * 1024 * 1024,
            retention=log_config.get('backup_count', 5),
            encoding="utf-8"
        )

    _logger.info("Logger initialized")
    return _logger


# 默认初始化
logger = init_logger()


def setup_logger(config: dict = None):
    """重新配置 logger"""
    global logger
    logger = init_logger(config)
    return logger


__all__ = ['logger', 'setup_logger']
```

### app/utils/__init__.py

```python
```

### CLAUDE.md

**注意**：生成 `CLAUDE.md` 时，必须先写入 `references/claude_md_preamble.md` 的完整内容，再写一行 `---` 分隔符，最后追加下面这段项目特定内容（详见 SKILL.md 的「CLAUDE.md 内容组合规则」）。

Generate with the actual project name replacing `{project_name}`:

```markdown
# {project_name}

## 项目说明

Python 后端服务，基于 FastAPI 构建。

## 技术栈

| 类型 | 选型 |
|------|------|
| Web 框架 | FastAPI |
| 日志 | loguru（`app/utils/logger.py`），支持控制台彩色输出 + 文件轮转 |
| 配置 | pydantic_settings BaseSettings，key 大写，支持同名环境变量覆盖 |
| 依赖管理 | requirements.txt |

## 目录结构

```
app/
├── config.py      # 配置类 Settings，所有配置项在此定义
├── routers/       # 路由，每个模块一个文件
├── models/        # ORM 数据库模型
├── schemas/       # Pydantic 请求/响应模型
├── services/      # 业务逻辑层
└── utils/
    └── logger.py  # 全局 logger，import 直接使用
```

## 开发约定

- **新增配置项**：在 `app/config.py` 的 `Settings` 类中添加，命名全大写
- **使用日志**：`from app.utils.logger import logger`，禁止直接使用 `print` 或标准库 logging
- **新增接口**：在 `app/routers/` 下新建文件，在 `main.py` 中 `include_router`
- **错误处理**：业务异常统一抛出，由 `main.py` 的 `global_exception_handler` 捕获
- **健康检查**：`GET /health` 已内置，不要修改

## 启动方式

```bash
pip install -r requirements.txt
python main.py
```

默认端口 8000，可通过环境变量 `PORT` 覆盖。
```

### AGENTS.md

Create as a symlink: `ln -s CLAUDE.md AGENTS.md`

### requirements.txt

```
fastapi
uvicorn[standard]
pydantic-settings
loguru
```

### .gitignore

```
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv/
venv/
env/
*.egg-info/
dist/
build/
logs/
*.log
.idea/
.vscode/
*.swp
*.swo
.DS_Store
```

### README.md

Use the following template, replacing `{project_name}` with the actual project name:

```markdown
# {project_name}

## Description

TODO: Add project description.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
python main.py
```

The server will start at `http://localhost:8000`.

## Configuration

All configuration is managed via environment variables or `.env` file:

| Key       | Default   | Description       |
|-----------|-----------|-------------------|
| APP_NAME         | backend      | Application name           |
| HOST             | 0.0.0.0      | Server host                |
| PORT             | 8000         | Server port                |
| DEBUG            | False        | Debug mode                 |
| LOG_LEVEL        | INFO         | Logging level              |
| LOG_FILE         | logs/app.log | Log file path              |
| LOG_MAX_SIZE_MB  | 10           | Max log file size (MB)     |
| LOG_BACKUP_COUNT | 5            | Number of log files to keep|

## Directory Structure

```
backend/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── app/
│   ├── config.py        # Configuration (BaseSettings)
│   ├── routers/         # API route handlers
│   ├── models/          # Database / ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
└── logs/                # Log files (auto-generated)
```
```
