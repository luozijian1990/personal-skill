---
name: html-to-mui-react
description: 将 HTML 原型图 1:1 复刻为基于 Vite + React + MUI v5 的前端项目，使用 TypeScript、React Router v6、mock 数据、styled() API，并预先配好 dev/mock/prod 三套环境。当用户提供 HTML 原型目录（或 HTML 文件）并希望转成可运行的 React 项目、或提到"复刻原型""把 HTML 转成 React""用 MUI 重写这个原型""把这些原型生成前端工程"等意图时，使用此 skill。即使用户没有明说"用 MUI"或"用 Vite"，只要上下文是把静态 HTML 原型搭成正式 React 前端项目，都应触发。
---

# HTML → MUI React 项目复刻器

把一份 HTML 静态原型（通常是多个 HTML 文件，每个代表一个页面）转换成一个结构规范、可运行的 Vite + React + MUI v5 前端项目，并内置 mock 数据和多环境配置。

## 用法

用户会告诉你 HTML 原型所在的目录（例如 `/mnt/user-data/uploads/prototype/`），以及要生成的项目名。你需要：

1. 读取并理解所有 HTML 原型文件
2. 按照下文的"项目骨架"生成一个完整的 `frontend/` 目录
3. 按照下文的"HTML → React 映射规则"把每个 HTML 页面转成对应的 Page 组件
4. 为每个页面生成合理的中文 mock 数据
5. 最终产物可以直接 `npm install && npm run dev:mock` 跑起来

## 工作流

### 第 1 步：侦察 HTML 原型

执行下面的动作，不要跳过：

- `ls` 列出原型目录的所有文件
- 对每个 HTML 文件都 `view` 一遍，记录：
  - 页面名称和对应的 URL 路径（从文件名推断，比如 `login.html` → `/login`）
  - 页面里出现的数据（表格字段、表单字段、卡片内容等）——这些要变成 mock 数据
  - 页面里的交互元素（Modal / Dialog、Tabs、Toast、Drawer、Snackbar 等）——这些要替换成 MUI 组件
  - 页面是否有侧边栏 / 顶栏等公共布局——这些要抽成 Layout
- 如果原型之间有导航关系（比如侧边栏的菜单项跳转到其他页面），把完整的路由表整理出来

完成侦察后，在输出里简短列一下你识别到的"页面清单 + 路由表 + 公共布局"，让用户确认无误再生成代码。

### 第 2 步：生成项目骨架

在用户指定的目录下（默认 `frontend/`）创建以下结构。**不要省略任何一个文件**，即便内容很短：

```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── index.html
├── .env.development         # dev 环境：指向 dev 后端
├── .env.mock                # mock 环境：不调用真实接口
├── .env.production          # prod 环境：指向生产后端
├── public/
└── src/
    ├── main.tsx
    ├── App.tsx              # 路由集中在这里
    ├── vite-env.d.ts
    ├── theme/
    │   └── index.ts         # MUI 主题定制
    ├── layouts/
    │   └── MainLayout.tsx   # 侧边栏 + 顶栏（按原型里的公共布局来）
    ├── routes/
    │   └── index.tsx        # 路由配置（可选，也可以全部放 App.tsx）
    ├── pages/               # 每个 HTML 页面一个子目录
    │   └── XxxPage/
    │       ├── index.tsx
    │       └── styles.ts    # styled() 定义
    ├── components/          # 可复用的小组件（按需）
    ├── mock/                # 集中的 mock 数据，按页面/模块分文件
    │   ├── users.ts
    │   └── ...
    ├── api/                 # 接口封装层，根据 VITE_USE_MOCK 切换
    │   ├── request.ts       # axios 或 fetch 封装
    │   ├── users.ts
    │   └── ...
    └── utils/
```

### 第 3 步：HTML → React 映射规则

- **一个 HTML 页面 → 一个 Page 组件**（放在 `src/pages/PageName/index.tsx`），路径和文件名对齐
- **HTML 里的 `<dialog>`、自定义 modal 弹窗 → `<Dialog>` / `<DialogTitle>` / `<DialogContent>` / `<DialogActions>`**
- **HTML 里的 tab 切换（通常用类名 active 实现）→ `<Tabs>` + `<Tab>`，用 `value` + `onChange` 控制**
- **HTML 里的 toast / alert / 通知 → `<Snackbar>` + `<Alert>`**
- **HTML 里的抽屉、侧边弹出 → `<Drawer>`**
- **HTML 里的表格 → `<Table>` + `<TableHead>` / `<TableBody>` / `<TableRow>` / `<TableCell>`，分页用 `<TablePagination>`**
- **HTML 里的表单 → `<TextField>` / `<Select>` / `<MenuItem>` / `<FormControl>` / `<Checkbox>` / `<Radio>`**
- **HTML 里的内联样式 / class 样式 → 一律用 `styled()` API 封装成组件**，不要用 `sx` prop，不要写 CSS 文件
- **HTML 里的图标 → `@mui/icons-material`**（比如 `<EditIcon />`、`<DeleteIcon />`）
- **HTML 里的图表（如果有）→ `recharts`**（柱图 `<BarChart>`、折线图 `<LineChart>`、饼图 `<PieChart>`）

### 第 4 步：设计约束（MUI 风格）

这些是硬约束，不能违背：

- **干净的白色背景**，不要渐变，不要花哨装饰
- **遵循 MUI 原生风格**，不要过度定制 theme，不要改默认圆角和阴影到完全不像 MUI
- **只用 MUI 组件库**，不引入 Antd、Semi、Arco 等其他 UI 库
- **图表只用 recharts**，不用 echarts、chart.js
- **不写注释、不写 console.log、不写 TODO**
- **所有文案使用中文**，包括 mock 数据、按钮文字、占位符、提示信息
- **字体一律走 `@fontsource/*` npm 包**，绝对不要在 `index.html` 里写 `<link href="https://fonts.googleapis.com/...">` 或 `<link href="https://fonts.gstatic.com/...">`。Google Fonts CDN 在国内访问极慢甚至超时，会让首屏阻塞数秒。如果原型 HTML 里有这种 `<link>`，**必须删掉**，改成在 `main.tsx` 里 `import '@fontsource/字体名/字重.css'`。任何外部字体 CDN（包括第三方镜像）都不允许引入。

### 第 5 步：Mock 数据和 API 层

`api/request.ts` 里根据 `import.meta.env.VITE_USE_MOCK` 判断走 mock 还是真实接口：

```ts
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (USE_MOCK) {
    const mockHandler = await import(`../mock/router`);
    return mockHandler.handle<T>(path, options);
  }
  const baseURL = import.meta.env.VITE_API_BASE_URL;
  const res = await fetch(`${baseURL}${path}`, options);
  return res.json();
}
```

Mock 数据的设计原则：

- **分模块组织**：每个页面/业务模块单独一个 `mock/xxx.ts` 文件
- **模拟真实数据**：不要用 `"测试数据 1"` `"测试数据 2"`，要写接近真实业务的中文（人名、公司名、部门、状态等）
- **数据量合理**：列表类数据准备 10-30 条，足够让分页、筛选能看出效果
- **保持字段一致性**：mock 的字段名要和真实接口对齐，后续接后端时不用改业务代码

### 第 6 步：环境配置

`.env.development`:
```
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://dev-api.example.com
```

`.env.mock`:
```
VITE_USE_MOCK=true
VITE_API_BASE_URL=
```

`.env.production`:
```
VITE_USE_MOCK=false
VITE_API_BASE_URL=https://api.example.com
```

`package.json` 里的 scripts：

```json
{
  "scripts": {
    "dev": "vite --mode development",
    "dev:mock": "vite --mode mock",
    "build": "tsc -b && vite build --mode development",
    "build:mock": "tsc -b && vite build --mode mock",
    "build:prod": "tsc -b && vite build --mode production",
    "preview": "vite preview"
  }
}
```

注意 `build` 默认走 development 配置（按用户原话"build 默认走的 dev 配置"），`build:prod` 走生产。

### 第 7 步：依赖版本

用这些版本（都是经过验证的稳定组合）：

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "@mui/material": "^5.16.0",
    "@mui/icons-material": "^5.16.0",
    "@emotion/react": "^11.13.0",
    "@emotion/styled": "^11.13.0",
    "recharts": "^2.12.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

**字体依赖（按需追加，不要走 CDN）**：如果原型 HTML 里用到了非系统字体，把对应的 `@fontsource/<字体名>` 加到 `dependencies` 里，并在 `src/main.tsx` 顶部 `import` 用到的字重 CSS。常见映射：

| 原型里的字体 | npm 包 | main.tsx 导入示例 |
| --- | --- | --- |
| DM Sans | `@fontsource/dm-sans` | `import '@fontsource/dm-sans/400.css'` |
| DM Mono | `@fontsource/dm-mono` | `import '@fontsource/dm-mono/400.css'` |
| Inter | `@fontsource/inter` | `import '@fontsource/inter/400.css'` |
| Roboto | `@fontsource/roboto` | `import '@fontsource/roboto/400.css'` |
| 思源黑体 | `@fontsource/noto-sans-sc` | `import '@fontsource/noto-sans-sc/400.css'` |

**只 import 实际用到的字重**（一般 300/400/500/600 够用），多余字重会增加 bundle 体积。`theme.ts` 的 `typography.fontFamily` 写法保持不变：`"'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif"`，fontsource 注册的字体名和 Google Fonts 完全一致。

### 第 8 步：生成后的自检

生成完所有文件后，在结尾简短报告：

- 生成了几个页面 Page 组件
- 路由表长什么样（路径 → 组件）
- mock 数据分几个模块
- 下一步执行命令：`cd frontend && npm install && npm run dev:mock`

不要跑 `npm install`（用户要下载到本地跑），不要自己验证运行结果——只要代码结构和语法正确即可。

## 参考模板

完整的脚手架模板代码（`main.tsx`、`App.tsx`、`theme/index.ts`、`api/request.ts`、`MainLayout.tsx` 的范例）保存在 `references/scaffold-templates.md` 里。当你需要生成这些"框架文件"时，读这个参考文件，复用里面的模板，只改动页面相关的部分。

业务页面（Page 组件）不要套模板，要根据 HTML 原型的实际内容来写。

## 常见坑提醒

- **路由用 `HashRouter`**：默认使用 `HashRouter`（URL 带 `#`），不用 `BrowserRouter`。原因是常见部署场景（静态托管、对象存储、没法配 `index.html` fallback 的环境）下 history 模式刷新会 404，hash 模式无需后端配合
- **React Router v6 的 API 变了**：用 `<Routes>` + `<Route element={<Page />} />`，不是 v5 的 `<Switch>` + `<Route component={} />`
- **MUI v5 的 styled 导入**：从 `@mui/material/styles` 导入，不是 `@mui/styles`
- **Vite 的环境变量**：必须以 `VITE_` 开头才会暴露给客户端，通过 `import.meta.env.VITE_XXX` 访问，不是 `process.env`
- **TypeScript 的 env 类型**：要在 `src/vite-env.d.ts` 里声明 `ImportMetaEnv`，否则 `import.meta.env.VITE_USE_MOCK` 会报类型错误
- **不要用 HTML `<form>`**：用标准事件处理（`onClick`、`onChange`），避免刷新页面的默认行为
- **不要引入 `@mui/styles`**：那是 v4 残留，v5 里用 `@mui/material/styles` 下的 `styled()`
- **绝不引用 Google Fonts CDN**：原型 HTML 里如果出现 `<link rel="preconnect" href="https://fonts.googleapis.com">` 或 `<link href="https://fonts.googleapis.com/css2?...">` / `https://fonts.gstatic.com/...`，**必须删除**，不要原样搬到生成的 `index.html`。在国内访问 Google Fonts CDN 经常超时或秒级延迟，会让首屏白屏几秒。正确做法：在 `package.json` 里加 `@fontsource/<字体名>` 依赖，在 `src/main.tsx` 顶部 `import '@fontsource/<字体名>/<字重>.css'`，字体随 bundle 本地分发。任何字体 CDN（Google、Adobe、第三方镜像）都不引入。
