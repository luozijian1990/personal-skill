# Kubernetes 故障排查完整决策树

> 来源：[learnk8s - Troubleshooting Deployments](https://learnk8s.io/troubleshooting-deployments)

## Mermaid 流程图

```mermaid
flowchart TD
    Start([开始]) --> GetPods["`**kubectl get pods**`"]
    GetPods --> AllRunning{所有 Pod<br/>都 RUNNING?}

    %% ============ Pod 层 - 非 Running 分支 ============
    AllRunning -->|NO| Pending{Pod 状态是<br/>Pending?}

    Pending -->|YES| HasNode{Pod 是否<br/>分配了节点?}
    HasNode -->|NO| Scheduler[调度器故障]
    HasNode -->|YES| ClusterRes{集群资源<br/>不足?}
    ClusterRes -->|YES| AddRes[增加集群资源]
    ClusterRes -->|NO| Quota{是否达到<br/>ResourceQuota 限制?}
    Quota -->|YES| RelaxQuota[放宽 ResourceQuota]
    Quota -->|NO| PVCPending{是否挂载了 Pending<br/>状态的 PVC?}
    PVCPending -->|YES| FixPVC[修复 PersistentVolumeClaim]
    PVCPending -->|NO| Unknown1[未知状态<br/>咨询 StackOverflow]

    Pending -->|NO| ImgPull{Pod 状态是<br/>ImagePullBackOff?}
    ImgPull -->|YES| ImgName{镜像名<br/>是否正确?}
    ImgName -->|NO| FixImgName[修复镜像名]
    ImgName -->|YES| ImgTag{镜像 Tag<br/>是否有效/存在?}
    ImgTag -->|NO| FixImgTag[修复 Tag]
    ImgTag -->|YES| PrivateReg{是否从私有仓库<br/>拉取镜像?}
    PrivateReg -->|YES| ConfigSecret[配置 imagePullSecret]
    PrivateReg -->|NO| Unknown2[未知状态]

    ImgPull -->|NO| RunErr{Pod 状态是<br/>RunContainerError?}
    RunErr -->|YES| VolumeMount[可能卷挂载有问题]

    RunErr -->|NO| CrashLoop{Pod 状态是<br/>CrashLoopBackOff?}
    CrashLoop -->|YES| CheckLogs{是否检查过日志<br/>并修复崩溃的应用?}
    CheckLogs -->|NO| FixApp1[修复崩溃的应用<br/>kubectl logs pod --previous]
    CheckLogs -->|YES| ForgotCMD{是否忘记了 Dockerfile<br/>中的 CMD 指令?}
    ForgotCMD -->|YES| FixDockerfile[修复 Dockerfile]
    ForgotCMD -->|NO| FixLiveness[修复活性探针 livenessProbe]

    CrashLoop -->|NO| Unknown3[未知状态]

    %% ============ Pod 层 - Running 但 NotReady 分支 ============
    AllRunning -->|YES| AllReady{所有 Pod<br/>都 READY?}
    AllReady -->|NO| Restart{Pod 是否频繁重启?}
    Restart -->|YES| FixLiveness
    Restart -->|NO| HasRunning{是否有处于<br/>Running 状态的容器?}
    HasRunning -->|NO| CRIErr[CRI 或 Kubelet 故障]
    HasRunning -->|YES| CanLog{能否看到<br/>应用日志?}
    CanLog -->|NO| KubeletErr[Kubelet 故障]
    CanLog -->|YES| ReadyProbe{就绪探针<br/>是否失败?}
    ReadyProbe -->|YES| FixReady[修复就绪探针]
    ReadyProbe -->|NO| TooFast{容器是否<br/>太快死掉?}
    TooFast -->|YES| FixApp2[修复应用程序]
    TooFast -->|NO| PortOK{容器暴露端口正确<br/>且监听 0.0.0.0?}
    PortOK -->|NO| FixPort[监听 0.0.0.0<br/>更新 containerPort]
    PortOK -->|YES| PodOK[Pod 运行正常]

    %% ============ Service 层 ============
    AllReady -->|YES| SvcCheck[排查 Service 层]
    SvcCheck --> DescribeSvc["`**kubectl describe service svc**`"]
    DescribeSvc --> HasEndpoints{能否看到<br/>端点列表?}
    HasEndpoints -->|NO| SelectorOK{标签选择器是否<br/>与 Pod 标签匹配?}
    SelectorOK -->|NO| FixSelector[修复 Service 选择器]
    SelectorOK -->|YES| PodHasIP{Pod 是否分配<br/>了 IP 地址?}
    PodHasIP -->|NO| CtrlMgrErr[控制器管理器故障]
    PodHasIP -->|YES| KubeletErr2[Kubelet 故障]
    HasEndpoints -->|YES| TargetPort{targetPort<br/>与 containerPort 匹配?}
    TargetPort -->|NO| FixTargetPort[修复 targetPort]
    TargetPort -->|YES| KubeProxyErr[Kube Proxy 故障]

    %% ============ Ingress 层 ============
    SvcCheck -->|Service OK| IngCheck[排查 Ingress 层]
    IngCheck --> DescribeIng["`**kubectl describe ingress ing**`"]
    DescribeIng --> HasBackends{能否看到<br/>后端列表?}
    HasBackends -->|NO| FixIngSvc[修复 Ingress 的<br/>service.name 和<br/>service.port.number]
    HasBackends -->|YES| SvcMatch{serviceName / servicePort<br/>与 Service 匹配?}
    SvcMatch -->|NO| FixIngSvc
    SvcMatch -->|YES| IngCtrlErr[Ingress 控制器故障]

    %% ============ 终点 ============
    IngCheck -->|Ingress OK| FromInternet{能否从公网访问?}
    FromInternet -->|YES| Done([应用正常])
    FromInternet -->|NO| Infra[基础设施问题]
```

## 关键命令速查

```bash
# Pod 层
kubectl get pods
kubectl get pods -o wide                       # 看 Node 和 IP
kubectl describe pod <pod>                     # 看 Events
kubectl logs <pod>                             # 当前日志
kubectl logs <pod> --previous                  # 上次崩溃的日志

# Service 层
kubectl get svc
kubectl describe service <svc>                 # 看 Endpoints
kubectl get endpoints <svc>

# Ingress 层
kubectl get ingress
kubectl describe ingress <ing>                 # 看 Backends
```
