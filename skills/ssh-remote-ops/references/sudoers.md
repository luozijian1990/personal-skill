# 受限运维账号的 sudoers 指南

仅在需要设计或审查远程账号的 sudo 权限时使用。sudoers 修改属于高风险系统变更，应由具备主机管理权限的人通过 `visudo` 完成。

## 设计原则

- 默认无 sudo 权限，只增加已确认的必要命令；
- 使用命令的绝对路径，可通过目标机上的 `command -v <name>` 核实；
- 尽量精确到服务、参数和文件，不用宽泛的 `*`；
- 读操作与写操作分开授权；
- 不授权 shell、编辑器、解释器、调试器、包管理器或可加载任意插件的程序；
- 不授权可以改写任意文件、改变属主权限或启动任意命令的工具；
- 不使用 `NOPASSWD: ALL`；
- 修改后运行 `visudo -c`，并保留另一个管理员会话用于恢复。

## 审查现有权限

以目标账号执行：

```bash
sudo -n -l
```

重点检查：

- 是否存在 `ALL` 或能匹配任意参数的通配规则；
- 是否能通过 `sh`、`bash`、`env`、`find -exec`、`awk`、`perl`、`python`、`vim`、`less` 等程序逃逸；
- 是否允许覆盖服务配置、systemd unit、cron、SSH 配置或动态链接库路径；
- 容器、Kubernetes 或配置管理工具是否等价于主机 root 权限；
- 命令路径是否与目标机实际安装路径一致。

## 最小示例

下面的规则只用于说明“固定命令和固定参数”的形式，需按目标机路径、服务名和实际需求重新审查：

```sudoers
Cmnd_Alias AGENT_READONLY = \
    /usr/bin/systemctl status nginx.service --no-pager, \
    /usr/bin/journalctl -u nginx.service -n 200 --no-pager, \
    /usr/sbin/nginx -t

agent-ops ALL=(root) NOPASSWD: AGENT_READONLY
```

不要为了减少规则数量而把服务名、文件路径或剩余参数替换成通配符。若确实需要可变参数，优先编写一个由管理员维护、输入校验严格的固定包装程序，再只授权该程序。
