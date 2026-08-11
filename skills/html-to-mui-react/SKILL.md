---
name: html-to-mui-react
description: 将一个或多个 HTML Prototype 工程化为 Vite + React + MUI v5 前端项目，使用 TypeScript、React Router v6、Mock 数据和 dev/mock/prod 三套环境。默认使用 fidelity 保真模式，保留已批准原型的布局、颜色、字体、间距、密度、动画、响应式行为和交互；仅在用户明确表示原型只代表功能、视觉无需保留或要求统一 MUI 风格时使用 mui-normalize 模式。当用户提出“HTML 转 React”“复刻原型”“把静态页面做成 React + Mock”“用 MUI 重写原型”等请求时使用。
---

# HTML → React + MUI 工程化

把 HTML Prototype 转成可运行的 React + Mock 产品契约。MUI 是实现手段，不是默认视觉答案；已经批准的原型优先于组件库默认样式。

## 两种模式

| 模式 | 何时使用 | 视觉契约 |
|---|---|---|
| `fidelity`（默认） | 原型已经批准，或用户没有明确放弃原型视觉 | 最大程度保留原型；组件和样式方案必须服从原型 |
| `mui-normalize` | 用户明确说原型只代表功能，或要求统一成企业 MUI 风格 | 保留功能和流程，视觉统一为本 Skill 的 MUI 基线 |

不要因为项目使用 MUI，就把 `fidelity` 原型自动改造成默认 MUI Dashboard。

## 输入

- HTML 文件或原型目录；
- 输出目录，默认 `frontend/`；
- 已批准的页面、关键 Flow 和目标 viewport；
- 项目已有的 React、样式和组件约束（如存在）；
- 用户明确选择的模式（如已提供）。

缺少 HTML 输入时停止，不编造页面。原型尚未批准时可以工程化，但必须把输出标为“待原型评审”，不能声称它是批准后的产品契约。

## 工作流

### 1. 侦察原型

读取全部 HTML、关联脚本、样式和本地资源。能运行时在真实浏览器中查看，不只读源码。形成：

1. 页面清单与路由映射；
2. 公共布局、Navigation 和信息层级；
3. 数据字段、状态与 Mock API Shape；
4. Dialog、Drawer、Tab、筛选、分页、表单和任务流程；
5. Loading、Error、Empty、Success、Progress 等非默认状态；
6. 字体、颜色、间距、边框、圆角、阴影、密度、动画和响应式行为；
7. 外部字体、图片、图标和第三方资源依赖。

如果交互只藏在脚本中，必须跟踪事件和状态变化；不要只根据静态首屏推断功能。

### 2. 固定模式与转换契约

按以下规则推荐模式：

- 已批准原型、强调“1:1”“复刻”“保持设计”或未说明视觉可改变 → `fidelity`；
- 明确说“视觉不重要”“只保留功能”“统一 MUI” → `mui-normalize`；
- 语义冲突，例如同时要求“完全 1:1”和“全部改成标准 MUI” → 列出冲突并请求用户选择。

输出一份简短契约：模式、页面/路由、公共布局、关键 Flow、目标 viewport、允许变化和未确认项。

**🔴 CHECKPOINT · 🛑 STOP：让用户确认转换契约后再生成工程。** 用户已经在当前请求中明确确认模式、页面和关键 Flow 时，不重复询问。

### 3. 建立项目骨架

默认使用 Vite、React、TypeScript、React Router v6、MUI v5、Mock API 和 dev/mock/prod 三套环境。读取 [`references/scaffold-templates.md`](references/scaffold-templates.md)：

- 两种模式都可复用 package、Vite、TypeScript、Router、环境和 API 层骨架；
- `mui-normalize` 可直接采用其中的 MUI Theme 与 Layout 基线；
- `fidelity` 只复用工程结构，Theme、Layout 和业务页面必须由原型反推，不能套默认白色 Dashboard。

一个 HTML 页面对应一个 Page 组件。公共结构只有在多个页面确实共享时才提取为 Layout 或组件，不能为了“看起来工程化”过度抽象。

### 4. 实现 fidelity 模式

按可观察结果复刻，不要求 DOM 或组件树相同：

- 保留 Layout、颜色、字体、间距、边框、阴影、密度、层级、Navigation、动画和响应式行为；
- 保留原型文案与语言，不擅自翻译或重写；
- MUI 组件会改变外观时，通过 Theme、`styled()`、CSS Modules 或项目已有方案恢复原型；
- 原型的自定义控件无法由标准 MUI 组件等价表达时，使用语义化 React 组件和必要样式，不强行套 MUI；
- 图表优先保持原型的图形类型、配色、比例、Label 和交互；只有实现库未指定时才选择 `recharts`；
- Dialog、Drawer、Tab、表单、Toast 和任务状态必须保留打开、取消、提交、失败和完成行为；
- 字体改成本地依赖或系统字体，不复制 Google Fonts 等外部字体 CDN。

原型存在明显可访问性或安全问题时，不要静默“修好”并造成契约漂移。记录问题，给出最小修正建议，等待用户确认后再改变可观察行为。

### 5. 实现 mui-normalize 模式

保留原有标准化能力：

- 使用干净白底、MUI 原生层级和克制 Theme；
- Dialog、Tabs、Snackbar、Drawer、Table、Form 等优先映射到对应 MUI 组件；
- 业务样式使用 `styled()`，不使用 `@mui/styles`；
- 图表使用 `recharts`；
- 默认使用中文界面与贴近真实业务的中文 Mock 数据，除非用户指定其他语言；
- 不引入 Ant Design、Semi、Arco 等第二套组件库；
- 不写 `console.log`、遗留 TODO 或无效注释；
- 字体使用 `@fontsource/*`，不使用字体 CDN。

该模式可以改变视觉，但不能丢失页面、数据字段、交互、权限表现或状态反馈。

### 6. Mock、API 与环境

- 每个业务模块使用独立 Mock 文件；列表准备足够验证筛选和分页的数据，避免“测试数据 1”式占位；
- API 层通过 `VITE_USE_MOCK` 切换 Mock 与真实请求，业务组件不直接判断环境；
- `.env.development` 指向开发后端，`.env.mock` 只走 Mock，`.env.production` 指向生产后端占位；
- Mock 字段、状态机和错误形状与页面契约一致，后续接后端时不需要重写 UI 业务逻辑；
- 不把 Mock 成功路径描述成真实鉴权、后端可靠性或生产能力。

### 7. 验证

生成完成后执行当前环境允许的最新验证：

1. 检查页面和路由数量与原型映射一致；
2. 运行 TypeScript/build；依赖未安装时不擅自联网安装，记录待用户执行的命令；
3. 能启动时使用真实浏览器检查目标 viewport、关键 Flow、控制台错误和页面溢出；
4. `fidelity` 模式逐项核对视觉语言与交互状态；
5. 标明 `VERIFIED`、`NOT_VERIFIED` 和失败证据，不用“应该可以”代替结果。

为关键页面和 Flow 记录可追溯证据，至少包含：

| 模式 | 原型基准 | 契约项 | 等价数据/状态 | viewport | 预期 | 实际观察 | 证据 | 结论 |
|---|---|---|---|---|---|---|---|---|
| `fidelity` / `mui-normalize` | 文件、URL 或修订 | 视觉项、字段或 Flow | Mock fixture / 前置状态 | 例如 1440×900 | 原型可观察结果 | React 可观察结果 | 截图、操作记录、DOM、控制台或命令结果 | `VERIFIED` / `NOT_VERIFIED` / 已批准偏差 |

`fidelity` 需要在等价数据和 viewport 下留下视觉及关键 Flow 证据，不能只用 DOM 或 build 证明视觉保真；`mui-normalize` 不比较原视觉，但要为每个字段、筛选条件、分页动作、权限表现和 Loading/Error/Empty/Success 等状态逐项举证。

如果构建或浏览器验证失败，先判断是环境、依赖、实现还是原型资源问题；只修复证据明确且在授权范围内的问题。仍失败时交付部分结果和复现命令，不宣告完成。

### 8. 交付

最终报告包含：

- 使用的模式与原型基准；
- 页面、路由、公共布局和 Mock 模块；
- 已保留的关键视觉/交互契约；
- 构建和浏览器验证结果；
- 关键 viewport、Flow 与偏差证据表；
- 未验证项、已知偏差和用户批准的变化；
- 本地启动命令；
- 下一步：`fidelity` 模式交给 `prototype-parity-review` 做独立 Gate，确认通过后再进入架构设计。

如果环境中没有 `prototype-parity-review`，按本节证据表完成同范围检查并标记 `NOT_INDEPENDENT`，交给用户人工确认；不得把该回退描述成独立 Gate 已通过。

## 失败处理

| 触发条件 | 处理 | 仍无法解决 |
|---|---|---|
| HTML、脚本或本地资源缺失 | 列出缺失文件并停止对应页面转换 | 将页面标为 `NOT_VERIFIED`，不编造替代设计 |
| 模式要求互相冲突 | 展示 `fidelity` 与 `mui-normalize` 的影响并请求选择 | 停在转换契约检查点，不生成代码 |
| 外部字体/CDN 不可用 | 改用对应 `@fontsource` 或原型定义的系统字体栈 | 记录字体偏差及其影响 |
| 原型交互无法复现 | 回查事件脚本、状态和前置数据 | 标记缺失 Flow，不把静态页面当完成 |
| 依赖不可安装或 build 失败 | 保留命令与首个有效错误，判断环境还是代码问题 | 输出部分交付，状态为 `NOT_VERIFIED` |
| React 与原型出现明显偏差 | 修复最小实现并重跑受影响页面/Flow | 交给 `prototype-parity-review` 判定 `FAIL`，停止进入架构阶段 |

## 反例黑名单

- 不把所有原型统一改成默认 MUI Dashboard。
- 不因为用了 MUI 就覆盖原型字体、密度、圆角、阴影和 Navigation。
- 不只复刻静态首屏而遗漏 Dialog、Error、Empty、Loading 和任务状态。
- 不擅自增加、删除或重排未经批准的功能和高风险操作。
- 不复制 Google Fonts、Adobe Fonts 或第三方字体镜像 CDN。
- 不把源码存在、构建未跑或浏览器未测描述为验证通过。
- 不在 `mui-normalize` 模式里丢失功能，也不在 `fidelity` 模式里用“企业化”作为改版理由。

## 固定工程约定

- 默认使用 `HashRouter`，避免静态托管刷新 404；用户已有部署契约时服从项目约定。
- MUI v5 的 `styled` 从 `@mui/material/styles` 导入。
- Vite 客户端环境变量使用 `VITE_` 前缀，并在 `vite-env.d.ts` 声明类型。
- 不使用 `@mui/styles`。
- 依赖版本和框架文件以 [`references/scaffold-templates.md`](references/scaffold-templates.md) 为基线；已有项目优先服从其锁定版本和代码规范。
