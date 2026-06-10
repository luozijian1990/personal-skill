---
name: aliyun-asr
description: 用阿里云"录音文件识别闲时版"批量把音频/视频 URL 转成文字。当用户说"音频转文字""录音识别""ASR""语音转写""闲时版""批量识别录音""把这些 mp3/m4a/wav 转成文本""阿里云语音""speech to text""会议录音转写"等场景使用。异步两步式：submit 提交 URL → 24h 内 poll 取回 .txt + .json。即使用户没说"阿里云",只要语境是【一批音频 URL → 想要文字稿】就触发。
---

# 阿里云 ASR 闲时版批量识别

## 这个 skill 做什么

把一批公网可访问的音频/视频 URL 提交给阿里云"录音文件识别闲时版"，24 小时内回来取结果，每个文件产出 `<name>.txt`（句子拼接）+ `<name>.json`（完整 Result，含时间戳）。

适合：会议录音、访谈、客服语音、批量音频归档。**不适合**实时识别（用普通版）、单条紧急转写（闲时版 SLA 是 24h）。

## 第一步：检查环境

按顺序确认下面三件事，缺哪步补哪步。**不要跳过**。

### 1. CLI 装了吗

```bash
which aliyun-asr
```

- 有路径输出（通常 `~/.local/bin/aliyun-asr`）→ 继续下一步
- 没有 → 让用户跑：

  ```bash
  cd ~/git/aliyun-asr  # 项目源码位置
  uv tool install .
  ```

  如果项目源码不在 `~/git/aliyun-asr`，问用户在哪。

### 2. 凭证配了吗

凭证读取顺序：**环境变量 > `~/.config/aliyun-asr/credentials`**。

```bash
test -f ~/.config/aliyun-asr/credentials && echo "配置文件存在" || echo "缺配置文件"
```

如果两个来源都没有，引导用户建配置文件（**推荐**，因为 skill 全局调用时不依赖项目 direnv）：

```bash
mkdir -p ~/.config/aliyun-asr
cat > ~/.config/aliyun-asr/credentials <<'EOF'
ALIYUN_AK_ID=LTAI5t...
ALIYUN_AK_SECRET=...
NLS_APP_KEY=...
EOF
chmod 600 ~/.config/aliyun-asr/credentials
```

三个值在哪拿：

- `ALIYUN_AK_ID` / `ALIYUN_AK_SECRET`：阿里云控制台 → AccessKey 管理（**建议 RAM 子账号** + `AliyunNLSFullAccess`）
- `NLS_APP_KEY`：**智能语音交互控制台**（https://nls-portal.console.aliyun.com/）→ 全部项目 → 项目的 Appkey。**不是阿里云 AccessKey**，新人常踩这个坑。

### 3. 工作目录

`aliyun-asr` 把状态账本 `tasks.jsonl` 和结果默认写在**当前目录**。建议先让用户 `mkdir` 一个项目目录再 `cd` 进去，比如 `~/asr-runs/2026-06-meeting/`。同一批任务必须在同一个目录里跑 submit 和 poll，否则 poll 找不到 `tasks.jsonl`。

## 典型工作流

### Step 1：准备 CSV

跟用户确认音频 URL 在哪。常见来源：

- OSS / S3 / 七牛 等公网对象存储
- 私有 bucket 需要带签名的 URL
- 本地文件**不能直接用**，得先传到能公网访问的地方

让用户准备 `jobs.csv`（**必须带 header**）：

```csv
url,output_name
https://your-bucket.oss-cn-shanghai.aliyuncs.com/2026-05-25-会议.mp3,meeting_0525
https://your-bucket.oss-cn-shanghai.aliyuncs.com/li-interview.m4a,interview_li
```

**关键约定**（违反会报错或踩坑，必须告诉用户）：

- `output_name` 写**基名不带后缀**，脚本自动加 `.txt` / `.json`
- `output_name` 不能含 `/` `\` 或 `.` `..`
- 默认按 `url` 去重，重复 URL 跳过；想强制重提加 `--allow-dup`
- 同一个 `output_name` 配两个不同 URL → 直接报错退出（防止文件互相覆盖）

支持格式：WAV / MP3 / MP4 / M4A / WMA / AAC / OGG / AMR / FLAC。音频 ≤ 512MB，视频 ≤ 2GB，时长 ≤ 12h。

### Step 2：提交

```bash
aliyun-asr submit --csv jobs.csv
```

正常输出：

```
准备提交 3 条, 已存在跳过 0 条
  [OK ] a1b2c3d4-...  -> meeting_0525.txt
  ...
完成: 成功 3, 失败 0, 状态文件: tasks.jsonl
```

提交完成后**明确告诉用户**：

> 闲时版 SLA 是 24 小时内出结果，可以关电脑了。明天（或几小时后）回来跑 `aliyun-asr poll` 取结果。

### Step 3：回收结果

```bash
# 扫所有未完成
aliyun-asr poll

# 精准点：只查特定日期之后提交的
aliyun-asr poll --since 2026-05-25

# 自定义输出目录（默认 ./outputs/）
aliyun-asr poll --outdir results/2026-05-25

# 批量 > 50 条时建议加 sleep（同 TaskId 限 1 QPS）
aliyun-asr poll --sleep 0.2
```

成功的会在 `outputs/`（或 `--outdir`）下生成 `<name>.txt` + `<name>.json`。已完成的不会重查，幂等可反复跑。

### Step 4：看进度

```bash
aliyun-asr list                  # 全部
aliyun-asr list --status pending # 未完成
aliyun-asr list --status done    # 已成功
aliyun-asr list --status failed  # 失败的
```

`✓` 成功 / `…` 排队或识别中 / `✗` 失败。

## 状态码速查

| Code | 含义 |
|------|------|
| 21050000 | 成功（结果已就绪） |
| 21050001 | 识别中 |
| 21050002 | 排队中 |
| 其它 | 失败，详情看 `status_text` |

## 踩坑速查

1. **`缺少 ALIYUN_AK_ID / ALIYUN_AK_SECRET`** → 凭证没配，回到上面"第一步 / 2"。
2. **`InvalidAccessKeyId`** → AK 错了，或子账号没授权 `AliyunNLSFullAccess`。
3. **`AppKey is invalid`** → `NLS_APP_KEY` 填错了（**写的是阿里云 AK，不是 NLS 控制台的 Appkey**）。让用户去 https://nls-portal.console.aliyun.com/ 拿正确的。
4. **任务一直 `21050002` 排队** → 闲时版就是这样，24h 内出结果都算正常，不要慌着重提。
5. **同 URL 想换文件名** → 默认按 URL 去重会跳过。要重提：删掉 `tasks.jsonl` 里对应那行，或加 `--allow-dup`。
6. **Excel 导出的 CSV** → 没问题，脚本用 `utf-8-sig` 读，能吃掉 BOM。
7. **批量上百条 poll** → 给 `poll` 加 `--sleep 0.2`，避免同 TaskId 1 QPS 限流。
8. **跨目录跑 poll 找不到任务** → `tasks.jsonl` 在 submit 时的工作目录里，poll 必须在同一目录跑（或用 `--tasks /path/to/tasks.jsonl`）。

## 不要做的事

- 不要建议用户把 URL 写一长串塞进命令行参数 —— 这个 CLI 只吃 CSV
- 不要在用户没确认 URL 公网可访问之前提交 —— 阿里云拉不到文件会直接 fail
- 不要为了"看看"建议用户反复 `submit` 同一个 URL —— 默认幂等，加 `--allow-dup` 会真的多扣一次配额
- 不要建议从普通版接口（`SubmitTask` 在 `nlsmeta.cn-shanghai`）拿 —— 这个工具只对接**闲时版**（`speechfiletranscriberlite.cn-shanghai`）
