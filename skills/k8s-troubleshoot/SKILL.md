---
name: k8s-troubleshoot
description: Kubernetes 部署故障排查专家。当用户遇到 Pod 无法启动、Service 不通、Ingress 无法访问、kubectl 报错等 K8s 部署问题时使用。覆盖 Pod/Service/Ingress/公网四层排查，包括 Pending、ImagePullBackOff、CrashLoopBackOff、Endpoints 为空、Backends 不通等常见场景。即使用户只是贴了一段 kubectl 输出或描述"访问不了"，也应该触发此 skill。
---

# Kubernetes 部署故障排查

## 前置：确认目标集群

读 `references/clusters.md`，根据用户提到的集群名找到对应的 kubeconfig 路径或 context。

```
IF 用户提到了集群名:
  → 查 references/clusters.md 找到对应的 --kubeconfig 路径或 --context 名
  → 后续所有 kubectl 命令带上该参数
ELIF 用户未指定集群:
  → 使用默认 context（~/.kube/config 的 current-context）
IF 在 clusters.md 中找不到该集群:
  → 询问用户："这个集群的 kubeconfig 路径或 context 名是什么？"并提示可以更新 references/clusters.md
```

---

## 核心原则

排查必须**严格分层、自底向上**，逐层确认，禁止跳层：

1. **Pod 层** — Pod 能不能跑起来、跑得稳不稳
2. **Service 层** — 流量能不能从 Service 到达 Pod
3. **Ingress 层** — 流量能不能从集群外到达 Service
4. **公网层** — 集群暴露方式 / 基础设施

每一层的通用套路：**看状态 → `describe` 找原因 → 确认本层 OK 后再往上查**。

跳层排查是最常见的误区——比如 Pod 都没起来就去查 Ingress，会浪费大量时间。

---

## Layer 1：Pod 层

入口命令：`kubectl get pods`

### 决策树：Pod 不是 RUNNING

先跑 `kubectl describe pod <pod>` 拿到 Events，然后按以下 if-then 走：

```
IF status == Pending:
  IF Pod 未分配节点 (`kubectl get pods -o wide` 无 Node):
    → 调度器故障
  ELIF describe 显示 Insufficient cpu/memory:
    → 增加集群资源 / 调整 requests
  ELIF `kubectl describe quota` 显示达到限制:
    → 放宽 ResourceQuota
  ELIF `kubectl get pvc` 有 Pending 的 PVC:
    → 修复 PVC / StorageClass
  ELSE:
    → 未知，贴 Events 进一步分析

ELIF status == ImagePullBackOff:
  IF 镜像名拼写错误:
    → 修复镜像名
  ELIF 镜像 Tag 不存在（含 latest 被删）:
    → 修复 Tag
  ELIF 从私有仓库拉取:
    → 配置 imagePullSecrets
  ELSE:
    → 检查网络连通性 / registry 是否可达

ELIF status == RunContainerError:
  → 大概率是卷挂载问题（ConfigMap/Secret/PVC 不存在或路径冲突）
    用 describe 看 Events 确认

ELIF status == CrashLoopBackOff:
  IF 没看过崩溃日志:
    → `kubectl logs <pod> --previous`（必须加 --previous）
  ELIF 日志显示进程立即退出、无报错:
    → 检查 Dockerfile 是否缺少 CMD/ENTRYPOINT
  ELIF 应用启动到一半被 kill:
    → livenessProbe 太激进，加大 initialDelaySeconds
  ELSE:
    → 根据日志修复应用本身的 bug
```

### 决策树：Pod 是 RUNNING 但 NOT READY

```
IF Pod 在 Running 与 CrashLoopBackOff 之间循环:
  → 修 livenessProbe（探针判定应用挂了但其实没挂）

ELIF 没有 Running 的容器:
  → CRI 或 Kubelet 故障，排查节点

ELIF `kubectl logs` 无输出:
  → Kubelet 故障，排查节点

ELIF describe 显示 readinessProbe 失败:
  → 修 readinessProbe

ELIF 容器启动后很快退出:
  → 应用启动失败，查日志修应用

ELIF 端口不对 或 应用监听 127.0.0.1:
  → 改为监听 0.0.0.0，确认 containerPort 正确
```

---

## Layer 2：Service 层

确认 Pod 层 OK 后再来这里。入口命令：`kubectl describe service <svc>`

```
IF Endpoints 列表为空:
  IF selector 与 Pod label 不匹配 (`kubectl get pods --show-labels` 对比):
    → 修复 Service 的 selector，必须匹配 Pod 标签
  ELIF Pod 没有 IP 地址:
    → 控制器管理器（kube-controller-manager）或 Kubelet 故障
  ELSE:
    → Pod 可能还没 Ready，回 Layer 1 确认

ELIF Endpoints 有值但流量不通:
  IF targetPort ≠ Pod 的 containerPort:
    → 修复 Service targetPort，使其等于 containerPort
  ELSE:
    → Kube Proxy 故障（节点上 iptables/ipvs 规则异常）
```

---

## Layer 3：Ingress 层

确认 Service 层 OK 后再来这里。入口命令：`kubectl describe ingress <ing>`

```
IF Backends 列表为空:
  → serviceName/servicePort 没对上 Service
    修复 Ingress 的 service.name 和 service.port.number

ELIF Backends 有值但流量不通:
  IF serviceName 或 servicePort 与实际 Service 不一致:
    → 修复 Ingress 资源中的 service 配置
  ELSE:
    → Ingress 控制器故障（nginx-ingress/traefik/istio/云厂商 ALB）
      查控制器 Pod 日志和文档
```

---

## Layer 4：公网层

集群内全通但从公网访问不到，问题在集群外：

- LoadBalancer / NodePort 配置
- 云厂商安全组 / 防火墙
- DNS 解析
- TLS 证书

---

## 高频陷阱 Checklist

排查时主动检查这些常见坑，能省大量时间：

1. **应用监听 `127.0.0.1`** 而不是 `0.0.0.0` — 容器外永远打不进来
2. **`targetPort` ≠ `containerPort`** — Service 配错端口
3. **selector 标签拼错** — Endpoints 永远空
4. **`kubectl logs` 不加 `--previous`** — CrashLoopBackOff 时看不到崩溃前的日志
5. **忘了 Dockerfile 的 `CMD`** — 容器启动就退出
6. **私有仓库没配 `imagePullSecrets`** — 一直 ImagePullBackOff
7. **livenessProbe 太激进** — `initialDelaySeconds` 太短导致无限重启
8. **PVC Pending** 拖累 Pod Pending — 容易忽略存储层
9. **跳过 `kubectl describe`** — 90% 的答案都在 Events 里

## 排查输出格式

给用户的排查建议应该包含：

1. **当前判断**：处于哪一层、什么状态
2. **下一步命令**：给出具体的 kubectl 命令，用户可以直接复制执行
3. **可能原因**：基于当前信息列出最可能的原因（按概率排序）
4. **相关陷阱提醒**：如果当前状态匹配上面 checklist 中的某条，主动提醒

## 参考资料

如需查看完整的 Mermaid 决策流程图，读 `references/flowchart-detail.md`。
