# 个性化面试题候选审核

## 默认呈现规则

先使用一张汇总表列出全部候选：`ID | 来源 | 拟定标题 | 结论 | 难度 | 一句话证据 | 待确认项`。

默认只为 `NEW_QUESTION`、`SCENARIO_CANDIDATE` 和 `NEEDS_REVIEW` 展开下方完整结构。`ALREADY_COVERED` 与 `DO_NOT_CREATE` 只在用户要求复核时展开，避免审核报告被低优先级条目淹没。

## 分析上下文

- 运行模式：{{策划模式/缺口模式}}
- 知识源：{{去标识化名称}}
- 纳入文件：{{相对路径列表}}
- 排除内容：{{exclusions}}
- 已有题目集合：{{未提供/相对路径与范围}}
- 扫描知识单元：{{count}}
- 个人画像摘要：{{去标识化摘要/未提供，使用通用模式}}
- 目标岗位/JD：{{摘要/未提供}}
- 分析时间：{{timestamp}}

## 结果摘要

- 推荐普通题：{{count}}
- 推荐场景题：{{count}}
- 已覆盖：{{仅缺口模式填写，否则写不适用}}
- 不建议生成：{{count}}
- 需要人工核实：{{count}}

## 候选 {{stable_id}}

### 来源

- 文件：{{relative_source_file}}
- 标题路径：{{heading_path}}
- 知识单元：{{knowledge_unit}}
- 来源摘要：{{source_summary}}

### 个性化依据

- 目标岗位关联：{{high/medium/low + reason}}
- 与真实经历的关系：{{验证强项/补强弱项/通用/未提供画像}}
- 学习或求职价值：{{reason}}
- 不得推断的内容：{{unsupported_personal_claims_or_none}}

### 覆盖分析

- 适用状态：{{缺口模式填写/策划模式不适用}}
- 覆盖程度：{{充分/部分/很浅/未覆盖/不适用}}
- 检索置信度：{{高/中/低/不适用}}
- 相关题目：{{相对路径或稳定标识/无/不适用}}
- 已覆盖维度：{{dimensions/不适用}}
- 缺失维度：{{dimensions/不适用}}
- 判断证据：{{evidence/不适用}}

### 候选决策

- 结论：{{NEW_QUESTION/SCENARIO_CANDIDATE/ALREADY_COVERED/DO_NOT_CREATE/NEEDS_REVIEW}}
- 推荐理由：{{reason}}
- 核心考察目标：{{assessment_goal}}
- 可区分的能力：{{discriminator}}
- 重复风险：{{high/medium/low/unknown}}
- 推荐难度：{{初级/中级/高级}}
- 难度依据：{{difficulty_reason}}
- 拟定标题：{{proposed_title}}
- 场景题潜力：{{high/medium/low + reason}}

### 用户确认

- 是否生成：{{待确认/是/否}}
- 最终题型：{{普通题/交给场景题设计/不生成}}
- 最终难度：{{待确认}}
- 考察重点调整：{{待确认}}
- 补充要求：{{待确认}}

## 人工核实项

- {{来源事实、覆盖证据、画像冲突或难度歧义}}
