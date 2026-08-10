# 已有题目样例

## K8S-001：Kubernetes Scheduler 的主要作用是什么？

Scheduler 负责监听未绑定节点的 Pod，根据过滤和打分结果选择节点，并将绑定结果写回集群。

## K8S-002：requests 和 limits 有什么区别？

requests 参与调度并表示最低资源需求，limits 约束容器最多可使用的资源。
