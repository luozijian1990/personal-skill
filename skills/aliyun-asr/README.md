# aliyun-asr

阿里云"录音文件识别闲时版"批量转写 Agent Skill，自带可独立安装的 Python CLI。

- 触发与使用流程：见 [`SKILL.md`](SKILL.md)（Agent 通过它驱动整个 submit / poll 工作流）
- CLI 源码：见 [`scripts/`](scripts/)
- 上游文档参考：见 [`references/aliyun-doc.md`](references/aliyun-doc.md)

本 README **只讲安装与基础设置**，方便人类使用者快速把 CLI 跑起来；具体的 CSV 格式、状态码、踩坑速查等使用细节统一放在 `SKILL.md` 中，避免与之失同步。

## 这个 skill 包含什么

| 路径 | 角色 |
|---|---|
| `SKILL.md` | Agent 入口：触发条件 + 提交/回收的标准工作流 + 踩坑速查 |
| `scripts/aliyun_asr.py` | 单文件实现的 CLI，提供 `submit` / `poll` / `list` 三个子命令 |
| `scripts/pyproject.toml` | 标准 PEP 621 项目描述，导出 `aliyun-asr` console script |
| `scripts/requirements.txt` | 仅依赖 `aliyun-python-sdk-core==2.13.3` |
| `references/aliyun-doc.md` | 阿里云"录音文件识别"开发者文档入口与调用注意事项 |

## 安装 CLI

推荐使用 [`uv`](https://github.com/astral-sh/uv) 全局安装到 `~/.local/bin/`：

```bash
cd skills/aliyun-asr/scripts
uv tool install .
which aliyun-asr      # 应该输出 ~/.local/bin/aliyun-asr
```

> 若机器上已经维护着独立的 `aliyun-asr` 项目（例如 `~/git/aliyun-asr`），优先用那个版本即可，本目录下的源码可以视为快照。

不想用 `uv` 时也可以用 `pip`：

```bash
cd skills/aliyun-asr/scripts
python -m pip install --user .
```

## 配置阿里云凭证

凭证读取优先级：**环境变量 > `~/.config/aliyun-asr/credentials`**。推荐用配置文件，因为 Agent 全局调用时不再依赖项目内 direnv：

```bash
mkdir -p ~/.config/aliyun-asr
cat > ~/.config/aliyun-asr/credentials <<'EOF'
ALIYUN_AK_ID=LTAI5t...
ALIYUN_AK_SECRET=...
NLS_APP_KEY=...
EOF
chmod 600 ~/.config/aliyun-asr/credentials
```

三个值的来源：

- `ALIYUN_AK_ID` / `ALIYUN_AK_SECRET`：阿里云控制台 → AccessKey 管理（建议 RAM 子账号 + `AliyunNLSFullAccess`）
- `NLS_APP_KEY`：[智能语音交互控制台](https://nls-portal.console.aliyun.com/) → 项目的 Appkey，**不是阿里云 AccessKey**

## 验证安装

```bash
aliyun-asr --help
```

能看到 `submit / poll / list` 三个子命令即装好。提交、回收、CSV 格式等详细说明请直接看 `SKILL.md`。

## 适用边界

- 服务对接：阿里云"录音文件识别**闲时版**"（`speechfiletranscriberlite.cn-shanghai`），SLA 24 小时
- 不适合：实时识别、单条紧急转写（请使用普通版而非闲时版）
- 文件大小：音频 ≤ 512 MB、视频 ≤ 2 GB、时长 ≤ 12 h
- 支持格式：WAV / MP3 / MP4 / M4A / WMA / AAC / OGG / AMR / FLAC

## 许可证

随仓库根目录 [`LICENSE`](../../LICENSE)（MIT, Copyright (c) 2026 luozijian1990）。
本 skill 调用的阿里云 SDK (`aliyun-python-sdk-core`) 遵循其自身许可证，使用者自行遵守。
