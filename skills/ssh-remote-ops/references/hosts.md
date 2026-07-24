# SSH 主机清单模板

仅记录非敏感连接信息。优先把实际连接细节维护在用户自己的 `~/.ssh/config` 中，本文件只记录别名和用途。

| SSH alias | 环境 | 用途 | 负责人 | 备注 |
|---|---|---|---|---|
| `example-web-staging` | 预发 | Web 服务 | 示例负责人 | 通过公司跳板机连接 |

## SSH config 示例

下面只展示结构，不要提交真实内网地址、用户名或私钥路径：

```sshconfig
Host example-web-staging
    HostName <host>
    User <user>
    Port <port>
    IdentityFile <local-private-key-path>
    IdentitiesOnly yes
    ProxyJump <jump-host-alias>
```

约束：

- 不记录密码、私钥内容、Token 或一次性验证码；
- 不把生产主机真实信息提交到公开仓库；
- 主机下线、改名或转交负责人后及时更新；
- 同名 alias 不得指向不同环境，避免误操作。
