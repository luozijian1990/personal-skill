# SSH Remote Ops

让具备本地 shell 能力的 Agent 直接通过 OpenSSH 操作远程服务器，不额外开发远程执行 API、常驻 Agent 服务或 Python 封装。

`SKILL.md` 负责告诉 Agent 如何确认目标、只读排查、控制变更和验证结果；主机侧仍以普通用户和 sudoers 最小权限作为硬边界。

## 设计理念

这个 Skill 采用三层安全模型：

1. **Skill 行为层**：默认只读，危险命令禁止执行，状态变更需要明确授权，并要求备份、校验和回退；
2. **操作系统用户层**：使用专用普通用户登录，不直接开放 root；
3. **sudoers 权限层**：只允许业务确实需要的固定命令，即使 Agent 生成了越权命令，操作系统也会拒绝。

SSH 已经提供成熟的认证、加密、跳板机和多主机连接能力。对于常规巡检、日志分析和受控运维，直接复用 SSH 的实现和维护成本最低。当需求扩展到集中审计、多团队租户隔离、短期凭证或大规模并发调度时，再考虑 SSH CA、堡垒机或 HTTP/mTLS 执行服务。

## 需要准备的密钥材料

| 材料 | 是否敏感 | 存放位置 | 用途 |
|---|---|---|---|
| SSH 私钥 | 是 | Agent 运行账号的 `~/.ssh/` 或系统密钥服务 | 证明客户端身份 |
| SSH 公钥 | 否 | 远程用户的 `~/.ssh/authorized_keys` | 允许对应私钥登录 |
| 服务器主机公钥指纹 | 否，但必须可信 | 运维资产记录或其他可信渠道 | 首次连接时确认服务器身份 |
| `known_hosts` 记录 | 否，但关系到完整性 | Agent 运行账号的 `~/.ssh/known_hosts` | 后续检测服务器身份变化 |

Skill 目录和 Git 仓库中不需要、也不应该保存任何真实私钥、密码或 Token。公钥虽然不是秘密，也建议通过主机初始化流程或配置管理系统部署，而不是与通用 Skill 绑定。

## 1. 生成专用 SSH 密钥

为 Agent 单独生成 Ed25519 密钥，不要复用个人日常登录密钥：

```bash
ssh-keygen \
  -t ed25519 \
  -a 100 \
  -C "agent-ops@<environment>" \
  -f ~/.ssh/agent_ops_ed25519
```

优先设置口令，并通过 `ssh-agent` 或系统密钥链向 Agent 运行环境提供密钥：

```bash
ssh-add ~/.ssh/agent_ops_ed25519
ssh-add -l
```

Agent 进程还需要继承对应的 `SSH_AUTH_SOCK` 环境；只在另一个终端运行 `ssh-add`，但没有把 agent socket 暴露给实际运行进程，仍然无法使用该密钥。

如果无人值守进程确实无法使用带口令密钥，可以生成一把无口令的专用密钥，但必须同时满足：

- 私钥只属于 Agent 运行账号，权限为 `0600`；
- 远程端只接受专用普通用户，不允许 root 登录；
- 使用来源 IP、跳板机或网络策略限制连接来源；
- 使用精确 sudoers 白名单限制提权能力；
- 制定轮换和吊销方式，怀疑泄露时立即移除对应公钥。

检查本地权限：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/agent_ops_ed25519
chmod 644 ~/.ssh/agent_ops_ed25519.pub
```

## 2. 创建远程受限用户

下面以 Linux 上的 `agent-ops` 用户为例。创建用户属于主机管理操作，应由管理员执行：

```bash
sudo useradd --create-home --shell /bin/bash agent-ops
sudo install -d -m 700 -o agent-ops -g agent-ops /home/agent-ops/.ssh
```

将 `~/.ssh/agent_ops_ed25519.pub` 的单行内容部署到：

```text
/home/agent-ops/.ssh/authorized_keys
```

然后设置权限：

```bash
sudo chown agent-ops:agent-ops /home/agent-ops/.ssh/authorized_keys
sudo chmod 600 /home/agent-ops/.ssh/authorized_keys
```

可以在公钥前添加 OpenSSH 限制，减少转发和交互式终端能力：

```text
restrict,from="<agent-source-ip-or-cidr>" ssh-ed25519 <public-key> agent-ops@<environment>
```

使用跳板机时，远程服务器看到的来源地址可能是跳板机地址，应按真实网络路径设置 `from=`。较旧 OpenSSH 不支持 `restrict` 时，可使用 `no-agent-forwarding,no-port-forwarding,no-X11-forwarding,no-pty` 等独立选项。

## 3. 配置 SSH alias

在 Agent 运行账号的 `~/.ssh/config` 中维护连接信息：

```sshconfig
Host ops-prod-web-01
    HostName <server-host-or-ip>
    User agent-ops
    Port <ssh-port>
    IdentityFile ~/.ssh/agent_ops_ed25519
    IdentitiesOnly yes
    BatchMode yes
    ConnectTimeout 10
    StrictHostKeyChecking yes
```

需要跳板机时增加：

```sshconfig
    ProxyJump <jump-host-alias>
```

连接参数放在 SSH config 中，可以避免 Skill 写死用户名、端口、私钥路径或网络拓扑。非敏感的 alias 与用途可以登记在 `references/hosts.md`。

## 4. 核对服务器主机密钥

首次连接前，从云平台控制台、主机管理员或其他可信渠道获取服务器 SSH 主机公钥指纹。由人工进行一次交互式连接，确认显示的指纹一致后才接受并写入 `known_hosts`：

```bash
ssh \
  -o BatchMode=no \
  -o StrictHostKeyChecking=ask \
  -- ops-prod-web-01 'exit'
```

完成首次登记后，Agent 使用 SSH config 中的 `BatchMode yes` 和 `StrictHostKeyChecking yes` 进行非交互连接。

`ssh-keyscan` 只能获取网络端返回的主机公钥，不能独立证明它是真实服务器，因此不能替代可信渠道核对。

如果以后出现 `REMOTE HOST IDENTIFICATION HAS CHANGED`，应停止连接并查明主机重装、IP/DNS 变化或中间人攻击等原因，不要直接删除旧记录绕过检查。

## 5. 配置最小 sudo 权限

普通巡检先使用 `agent-ops` 自身权限。确需读取受限日志、检查服务配置或执行受控 reload 时，再由管理员使用 `visudo` 添加精确白名单。

详细原则和最小示例见 [`references/sudoers.md`](references/sudoers.md)。不要配置：

```sudoers
agent-ops ALL=(ALL) NOPASSWD: ALL
```

也不要轻易允许 shell、解释器、编辑器、包管理器、任意文件写入工具，或带宽泛参数通配符的 Docker、Kubernetes 和 systemd 命令。这些权限通常等价于完整 root。

## 6. 验证

先检查 SSH 最终配置：

```bash
ssh -G -- ops-prod-web-01
```

再验证普通用户只读连接：

```bash
ssh -o BatchMode=yes -- ops-prod-web-01 \
  'id; hostname; date -Is; uptime'
```

最后检查 sudo 白名单：

```bash
ssh -o BatchMode=yes -- ops-prod-web-01 'sudo -n -l'
```

验收时确认：

- 登录用户不是 root；
- 未授权命令会被拒绝；
- `sudo -n` 不会等待密码输入；
- 主机密钥检查保持开启；
- Agent 只能访问已批准的目标主机和命令范围；
- 私钥未出现在 Skill 目录、Git 状态、日志或 Agent 回复中。

## 使用

完成部署后，可以直接提出：

- “检查 `ops-prod-web-01` 的磁盘和 inode 使用情况。”
- “查看生产 Nginx 状态和最近 200 行错误日志，只诊断，不修改。”
- “确认配置通过检查后 reload Nginx，并验证健康状态。”

Agent 的实际执行规则以 [`SKILL.md`](SKILL.md) 为准。
