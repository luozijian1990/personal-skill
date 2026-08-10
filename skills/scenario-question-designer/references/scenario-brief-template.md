# 场景题确认稿

## 默认呈现规则

默认先列汇总表：`ID | 场景主题 | 事实状态 | 核心判断 | 难度 | 风险/待核实 | 待确认项`。

每个候选的精简确认稿只展开事实分类、场景六要素、关键数据、核心假设、处置判断和用户确认。只有用户要求详细确认稿，或质量审查发现问题时，才展开完整的推理链、难度调节和逐项质量理由。

## 分析上下文

- 输入范围：{{candidate_ids_or_sources}}
- 已有题目集合：{{未提供/相对路径与范围}}
- 个人画像摘要：{{去标识化摘要/未提供，使用通用模式}}
- 目标岗位/JD：{{摘要/未提供}}
- 生成时间：{{timestamp}}

## 场景 {{stable_id}}

### 输入与来源

- 原始输入摘要：{{raw_input_summary}}
- 来源：{{relative_path_and_heading_or_user_input}}
- 用户提供事实：{{user_facts}}
- 来源支持事实：{{source_facts}}
- 模拟构造值：{{constructed_values}}
- 待核实：{{facts_to_verify}}

### 个性化定位

- 核心技术领域：{{primary_domain}}
- 关联知识点：{{knowledge_points}}
- 适合岗位：{{roles_or_generic}}
- 与个人目标的关系：{{strength_validation/weakness_training/general}}
- 核心考察目标：{{assessment_goal}}
- 不得推断的个人经历：{{unsupported_claims_or_none}}

### 场景六要素

- 环境：{{environment}}
- 异常现象：{{symptoms}}
- 已知条件：{{known_conditions}}
- 排除条件：{{excluded_conditions_or_none}}
- 业务约束：{{business_constraints}}
- 要求做出的处理判断：{{required_decision}}

### 数据设计

| 数据项 | 值、单位、基线与窗口 | 来源状态 | 对判断的作用 |
|---|---|---|---|
| {{metric}} | {{value_context}} | {{用户事实/来源事实/模拟构造值/待核实}} | {{decision_effect}} |

- 数据完整性：{{missing_baseline_unit_window_or_none}}
- 题干呈现：{{which_values_appear_in_prompt}}
- 模拟边界：{{why_values_are_not_universal_thresholds}}

### 预期能力与推理

- 关键假设：{{hypotheses}}
- 信息优先级：{{information_priorities}}
- 分析顺序：{{reasoning_sequence}}
- 止损与恢复：{{containment_and_recovery}}
- 恢复验证：{{verification}}
- 风险与方案权衡：{{tradeoffs}}
- 防复发方向：{{prevention}}
- 能力区分点：{{discriminators}}

### 质量审查

- 是否避免泛泛“怎么排查”：{{yes_no_reason}}
- 条件是否因果一致：{{yes_no_reason}}
- 是否保留必要不确定性和多条合理路径：{{yes_no_reason}}
- 每个关键数据是否有来源状态和判断作用：{{yes_no_reason}}
- 是否存在装饰性数值或伪造阈值：{{yes_no_reason}}
- 与本轮/已有题目的区别：{{distinct_scope_or_limit}}
- 是否完成隐私检查：{{yes_no_reason}}

### 难度与拟定题目

- 难度：{{初级/中级/高级}}
- 难度依据：{{difficulty_reason}}
- 降低难度：{{how_to_make_easier}}
- 提高难度：{{how_to_make_harder}}
- 拟定标题：{{proposed_title}}
- 题干草案：{{question_prompt}}
- 主要追问方向：{{followup_axes}}

### 用户确认

- 是否生成：{{待确认/是/否}}
- 最终事实与构造条件：{{待确认}}
- 最终适合对象：{{待确认}}
- 最终难度：{{待确认}}
- 约束、数据和追问调整：{{待确认}}
