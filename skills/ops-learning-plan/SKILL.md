---
name: ops-learning-plan
description: Create a personalized, practical study plan for one operations, SRE, cloud-native, observability, data-system, or infrastructure topic using the existing knowledge in the ops-roadmap repository. Use when a user wants to learn, review, refresh, or systematically study a concrete topic with a daily or weekly schedule, practice tasks, and measurable outcomes. This is a knowledge-learning planner, not a career, job-market, or JD roadmap tool.
---

# ops-learning-plan

把 `ops-roadmap` 知识库中的教材裁剪成可执行的个人课程表。输出应回答：学什么、先学什么、需要多久、如何练习，以及学完能做什么。

## 适用范围

适用于明确的单一技术主题，例如 Prometheus、Kubernetes 网络、eBPF、MySQL、Kafka、Linux 性能或 Nginx；也适用于复习某个主题的薄弱部分。用户至少需要提供主题，基础、目标、每天/每周时间、周期和深度均为可选。

不用于职业规划、招聘 JD 分析、岗位匹配、薪资或市场分析、roadmap.sh 求职路线、长期进度数据库、考试系统或 Web 应用。

## Source of Truth

默认使用本地或远程 `ops-roadmap` 仓库，优先读取 `topics/` 下的 Markdown。Markdown 是教材源文件；`*-roadmap.html` 只用于提供可点击导航，不作为主要知识分析来源。

如果仓库不在当前工作区：

1. 先检查当前目录、常见相邻目录以及仓库的 `origin` 是否指向 `luozijian1990/ops-roadmap`。
2. 能访问本地仓库时直接读取，不要为了规划课程重新搜索大量互联网教程。
3. 只有主题不在仓库、用户明确要求额外资料，或仓库内容不足以支撑目标时，才说明缺口并询问是否补充外部资料。绝不能假装仓库已有该主题。

## 工作流

### 1. 解析请求

提取主题、当前基础、学习目标、时间预算、完成周期和期望深度。只把主题当作强制输入；缺失信息使用合理默认值，不连续追问。默认是“系统入门 + 基本生产实践”、系统学习模式、约 4 周、每周 5～7 小时。用户已明确掌握的内容不得重复排入主计划。

把模式理解为：

- 快速补课：数天到两周，优先理解和能用，大幅裁剪深入内容。
- 系统学习：两到八周，覆盖原理、使用和基础生产实践，是默认模式。
- 深入学习：一个月到更长，加入底层原理、架构、排障和深入实践。

### 2. 匹配 Topic

在 `topics/<category>/<topic>/` 中按目录名、README 标题、Markdown H1/H2/H3 和常见别名匹配。支持中文/英文、缩写和常用称呼，例如 `k8s` ↔ `Kubernetes`、`K8s 网络` ↔ `kubernetes-networking`、`PromQL` ↔ Prometheus 查询主题。

匹配后记录实际路径，并优先链接对应的 roadmap HTML；需要精确定位时链接 Markdown。链接使用仓库内相对路径或 GitHub 地址，不能复制大段教材正文。

若有多个候选，选择最贴合用户目标的 Topic，并在输出中说明选择；只有无法可靠判断主题时才提问。

### 3. 读取并建模内容

把 Markdown 结构理解为：课程 → Chapter（H2）→ Section（H3）→ Knowledge Point（H4）。保留章节顺序、代码示例、表格、Mermaid 和有意义的换行；不要把生成 HTML 当成教材重新解析。

基于主题内容和常识识别可能的前置知识。前置只解决理解障碍，不得机械扩大范围：用户已掌握的前置标记为“已具备”，必要但缺失的前置给出约 30 min、1 h、2 h、半天或 1 天等粗粒度补课建议，非必要背景放入可选项。

### 4. 按目标裁剪

对每个候选章节/知识点结合用户目标、基础、深度和时间预算分类：

- **必须学习**：达成目标不可缺的概念、工具、配置、排障路径。
- **建议学习**：能提高迁移性、生产质量或后续深入，但可延后。
- **本次跳过**：与目标无关、重复已知内容，或在当前周期内收益过低的深入实现。

裁剪要有理由。比如“运维排障”优先工具、Hook 选择、观测路径和 Runbook，减少复杂底层开发；“复习 PromQL”不应重新安排完整 Prometheus 入门。

### 5. 安排时间

先算可用总时长，再按依赖关系分配到 Week/Day；不要生成 47 分钟、83 分钟等伪精确时长，只使用 `30 min`、`1 h`、`2 h`、`半天`、`1 天` 或合理区间。若用户只有周末时间，按周末 session 安排，不强行生成 Day 1～Day 7。

每个周期应混合学习、实践、复习和验证。默认每天约 1 小时可参考 `35 min 学习 + 20 min 实验 + 5 min 总结`，但按主题风险和任务复杂度调整，不机械套用比例。时间不足时先保留必须学习和核心实践。

### 6. 设计实践与验收

实践必须服务于目标，并尽量形成可观察结果。例如部署 Prometheus、接入 exporter、写 PromQL/Alert Rule、模拟 Target Down；或用 bpftrace 追踪 execve、选择 tracepoint/kprobe/uprobe、完成一次网络丢包排障。每周至少安排一个动手任务，系统计划应有一组最终实践清单。

完成标准必须是能力描述，而不是“看完文章”或“完成所有章节”。使用可核验的复选项，例如能解释数据模型、独立配置 Target、编写查询、定位故障、说明 Hook 选择并复现结果。若环境依赖（权限、内核、集群、云资源）影响实践，标注替代方案或前置条件。

## 输出格式

除非用户指定其他格式，使用以下结构，内容可按主题增删：

```markdown
# <主题> 学习计划

## 学习目标
<一句能力导向的目标>

## 学习周期
<周期、每天/每周投入、预计总投入；注明默认假设>

## 前置知识
- 已具备：...
- 需要补：...（时间）

## 本次课程范围
### 必须学习
- ...（可附对应 Markdown 或 roadmap HTML 链接）
### 建议学习
- ...
### 本次跳过
- ...（简短理由）

# Week 1 · <主题>
<按用户可用节奏列出 Day 或周末 session，每项包含学习内容和粗粒度时间>

实践：
- ...

本周完成标准：
- [ ] ...

## 实践清单
- [ ] ...

## 完成标准
- [ ] ...

## 对应 Ops Roadmap
- [主题或章节](相对路径或 GitHub 链接)
```

保持输出是导航和课程表，不重写教材。对于未知主题，明确写出“当前 `ops-roadmap` 尚未覆盖该主题”，然后提供有限的下一步选择，而不是虚构 Topic 或大段外部教程。

## 触发示例

- “帮我学 Prometheus，每天 1 小时”
- “我会 Kubernetes 基础，但 K8s 网络弱，集中补两周”
- “两周学一下 eBPF，主要用于运维排障”
- “我只有周末时间，想系统学习 MySQL”
- “PromQL 不熟，帮我复习一周”

## 与其他 Skill 的边界

- `learning-notes-builder`：把已收集的材料整理成教材。
- `learning-roadmap`：把结构化教材生成可交互 Roadmap。
- `ops-learning-plan`：从现有教材中选择、排序、排程、设计实践并定义结果；不修改 `ops-roadmap` 内容。
