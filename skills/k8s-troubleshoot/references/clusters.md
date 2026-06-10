# 集群 Kubeconfig 映射表

排查前先查这里，根据用户提到的集群名找到对应的 kubeconfig 路径或 context。

| 集群名 | kubeconfig 路径 | context 名 | 备注 |
|---|---|---|---|
| （示例）A集群 | ~/.kube/config-a | a-cluster-admin | 生产环境 |
| （示例）B集群 | ~/.kube/config-b | b-cluster-dev | 测试环境 |

> 更新方式：直接编辑此文件，新增集群时按上面的格式填一行。
