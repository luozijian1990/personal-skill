---
name: learning-roadmap
description: 把"学习笔记"类 markdown 转成 roadmap.sh 风格的可交互 HTML 学习路线图——米黄手账配色 + 黑墨边框 + 立体阴影、三态进度（待学 / 在学 / 已学）+ localStorage 持久化、右侧滑出详情面板（marked 渲染正文、highlight.js 高亮代码、mermaid 渲染流程图）、顶部搜索 + 进度条。当用户说"把这篇笔记做成 roadmap"、"生成学习路线图"、"做个学习路径"、"roadmap.sh 那种页面/网页"、"可视化我的笔记"、"把 markdown 笔记变成网页"、"做个学习进度跟踪"、"扫描所有学习笔记生成总览"、"learning roadmap"、"知识图谱页面"、"笔记导航图" 时使用。即使用户没明说 "roadmap"，只要语境是【已有结构化的 markdown 笔记（## 章节 / ### 小节）→ 想要可视化、可点击、能跟踪进度的网页】，都应该主动触发。支持单文件和批量两种模式，批量会生成 index.html 卡片汇总入口。
---

# learning-roadmap

把结构化的学习笔记 markdown（`##` 主章节 + `###` 小节）渲染成可交互的 HTML 学习路线图。

## 何时用

- 用户给出一个学习笔记 md，明说或暗示想要可视化、可点击、能勾选进度的版本
- 用户有一堆笔记目录，想要一个总览页面来管理学习状态
- 用户提到 roadmap.sh 这种风格

**不适用**：纯散文型笔记（没有清晰的章节分级）、API 文档、变更日志。

## 当解析失败时（脚本退出码 = 2）

脚本如果发现 markdown 结构跟期望不符，会在 stderr 输出诊断并以退出码 2 退出，**不会**生成任何 HTML。看到这种情况**不要重试**，根据诊断分两档处理：

### 档 1：诊断里有 "✅ 可以通过 --shift 修复"

说明笔记的标题层级整体偏了 N 级（最常见：笔记用 H1/H2/H3 而不是 H2/H3/H4）。处理步骤：

1. **不要自作主张直接 `--shift`**，把诊断输出原文给用户看
2. 询问类似：
   > 看起来这篇笔记的章节用 H{N}、小节用 H{N+1}，跟 roadmap 期望的 H2/H3 不一样。
   > 我可以用 `--shift {建议值}` 重跑修复。同意吗？
3. 用户同意后用建议的 shift 值重跑：
   ```bash
   python3 scripts/build_roadmap.py --shift 1 <file>
   ```

### 档 2：诊断里有 "💡 建议：用 /learning-notes-builder"

说明笔记 heading 太少或太散，**无法**用 shift 修复（典型场景：散文型记录、纯列表、heading 完全缺失）。处理：

1. **不要硬试 `--shift`**——多大值都修不好
2. 告诉用户：
   > 这篇笔记的结构不适合直接做 roadmap（heading 太少或太散）。
   > 建议用 `/learning-notes-builder` 把它当作"原材料"重新合成成结构化笔记，再回来转 roadmap。
3. 如果用户回答"这就是我所有的内容了" → 提示他们可以把这一篇拆成多个文件放到一个目录，再喂给 learning-notes-builder

## 怎么用

核心脚本：`scripts/build_roadmap.py`。一切都在它里面，包括 HTML 模板。不要把模板拆出去——保持单文件易于维护。

### 单文件转换

```bash
python3 scripts/build_roadmap.py <input.md> [output.html]
```

- 默认输出到 `<input所在目录>/<stem>-roadmap.html`
- 用户给的路径是相对路径时，记得 `cd` 到正确目录或传绝对路径

### 批量模式

```bash
python3 scripts/build_roadmap.py --batch <dir> [--out <index 输出目录>]
```

- 递归扫描 `<dir>` 下所有 `.md`，**结构自适应**：含 `##` 主章节且至少 3 个 `###` 小节才算"学习笔记"
- 自动跳过 README/CHANGELOG/LICENSE 等噪音文件、node_modules / .venv / dist 等目录、隐藏目录
- 每篇笔记的 roadmap 紧挨着源 md 生成（`<note>-roadmap.html`）
- 总览 `learning-roadmap-index.html` 默认放在扫描根目录
- `--min-sections N` 可调阈值

### 批量 + 本地服务

```bash
python3 scripts/build_roadmap.py --serve <dir> [--port 8000]
```

`--serve` 在批量生成后启动本地 HTTP 服务并打开浏览器。**这是看到 index 实时进度的唯一可靠方式**——浏览器在 `file://` 协议下对 localStorage 做了路径级隔离，index 读不到各 roadmap 的进度。

## 输出文件交付方式

执行完后，对用户说清楚：

- **单文件**：直接给出生成的 HTML 路径，并用 `open` 命令打开它
- **批量**：先点 index 路径让用户预览，然后提示"要在 index 看到实时进度，运行 `--serve` 模式"

## 关键实现要点（编辑脚本时要保留的不变量）

1. **代码块感知的标题解析**：`##` / `###` 的识别必须忽略 ` ``` ` 代码块内的 `#` 注释行——否则 shell/python 代码里的注释会被误识别为标题
2. **mermaid 渲染**：详情面板打开时，把 `<pre><code class="language-mermaid">` 替换成 `<div class="mermaid">` 再调用 `mermaid.run()`。marked 默认会把 mermaid 当普通代码块，不替换就只有纯文本
3. **mermaid 放大预览**：drawer 内的 Mermaid 图表要能点击打开独立放大弹层；放大层使用自己的 `diagram-backdrop` / `diagram-modal`，不要复用 drawer 的 backdrop；弹层默认按视口自动缩放，但必须保留可读下限（桌面约 75%、移动端约 55%），避免大图被压到节点文字不可读，必要时允许弹层内部滚动；提供 `+` / `-` 缩放按钮；点击后的 clone 需要测量 `foreignObject` 中 HTML label 的真实排版尺寸，必要时只在弹层里扩大对应节点的 label 容器和外层 shape，避免“框框里的字”被裁切；克隆 SVG 后要把 `width="100%"` 归一化为 viewBox 实际宽高，否则图表会在弹层容器中异常缩小；如果重写 id，必须同步重写 SVG 内部 `<style>` 的 `#id` 选择器，否则文字颜色和 Mermaid 样式会失效；Esc 优先关闭图表放大层，再关闭 drawer
4. **localStorage key**：`roadmap:<笔记一级标题>`。index 卡片就靠这个 key 读各笔记进度
5. **back link**：批量模式下，每个 roadmap 顶部要有一个返回 index 的链接，用 `os.path.relpath` 计算，跨目录也能用
6. **三态循环**：点卡片左侧小圆 → 待学 / 在学 / 已学 循环；点卡片本体 → 弹出详情面板

## 视觉风格（修改时尽量保留）

- 米黄底 `#fdf6e3` + 纸张色卡片 `#fffdf5` + 黑墨边框 `#1f2933`
- 立体阴影 `box-shadow: 3px 3px 0 var(--ink)`（手账 / sticky note 感）
- 主章节之间用虚线分隔，呼应 roadmap.sh 的"手绘连接线"
- 字体优先用系统中文（PingFang SC / Microsoft YaHei）

如果用户要换主题色，改 `:root` 里的 CSS 变量就够了，不要重写结构。
