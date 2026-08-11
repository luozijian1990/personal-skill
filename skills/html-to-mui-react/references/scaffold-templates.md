# 脚手架模板

生成“框架文件”（非业务页面）时复用这里的模板。先根据模式决定复用范围：

- `fidelity`：复用 package、Vite、TypeScript、Router、环境和 API 层；`theme`、Layout 与业务样式必须从原型反推。
- `mui-normalize`：可以直接使用下方 Theme 与 Layout 基线，再按页面功能调整。

替换 `{{PROJECT_NAME}}`、`{{ROUTES}}`、`{{MENU_ITEMS}}` 等占位符。不要在 `fidelity` 模式中把示例 Theme 当成视觉规范。

## package.json

```json
{
  "name": "{{PROJECT_NAME}}",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite --mode development",
    "dev:mock": "vite --mode mock",
    "build": "tsc -b && vite build --mode development",
    "build:mock": "tsc -b && vite build --mode mock",
    "build:prod": "tsc -b && vite build --mode production",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "@mui/material": "^5.16.0",
    "@mui/icons-material": "^5.16.0",
    "@emotion/react": "^11.13.0",
    "@emotion/styled": "^11.13.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

## vite.config.ts

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    host: true
  }
});
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

## tsconfig.node.json

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

## index.html

模板里**不要**写任何 Google Fonts / 字体 CDN 的 `<link>` 标签。`fidelity` 使用原型的语言标记；`mui-normalize` 在没有来源语言时可用 `zh-CN`。字体改成本地依赖时，只安装和导入原型实际使用的字体与字重，并同步写入 `package.json`。

```html
<!doctype html>
<html lang="{{HTML_LANG}}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{PROJECT_TITLE}}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## src/main.tsx

如果原型用到自定义字体，在第一行 `import` 之后按实际字重追加 `@fontsource/<字体名>/<字重>.css`，并把对应包加入依赖。没有使用就不要安装或导入。`CssBaseline` 只用于 `mui-normalize`，或经比对确认其 reset 与原型一致的 `fidelity` 项目；共享模板默认不启用它。图表库同样按需添加，不把 Recharts 等库放入基础依赖。

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import App from './App';
import { theme } from './theme';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <HashRouter>
        <App />
      </HashRouter>
    </ThemeProvider>
  </React.StrictMode>
);
```

`mui-normalize` 模式把共享模板中的 MUI import 和 `ThemeProvider` 内容替换为以下形式：

```tsx
import { CssBaseline, ThemeProvider } from '@mui/material';

<ThemeProvider theme={theme}>
  <CssBaseline />
  <HashRouter><App /></HashRouter>
</ThemeProvider>
```

按需依赖使用以下版本基线，不需要时不要加入 `package.json`：

```json
{
  "recharts": "^2.12.0",
  "@fontsource/dm-sans": "^5.0.0",
  "@fontsource/dm-mono": "^5.0.0"
}
```

## src/App.tsx

集中的路由表。根据原型的页面清单填充 `<Route>`。

```tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
// 按原型里的页面继续 import...

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        {/* 按原型里的页面继续添加 */}
      </Route>
    </Routes>
  );
}
```

## src/vite-env.d.ts

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_MOCK: string;
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## src/theme/index.ts

以下是 `mui-normalize` 的干净白底 MUI 基线。`fidelity` 模式必须按原型重建 palette、typography、shape、shadow 和 component overrides，不直接复制本段。

```ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2'
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff'
    }
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'PingFang SC',
      'Hiragino Sans GB',
      'Microsoft YaHei',
      'sans-serif'
    ].join(',')
  },
  shape: {
    borderRadius: 6
  }
});
```

## src/api/request.ts

根据 `VITE_USE_MOCK` 切换数据源。

```ts
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  params?: Record<string, string | number>;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  if (USE_MOCK) {
    const { handleMock } = await import('../mock/router');
    return handleMock<T>(path, options);
  }

  const { method = 'GET', body, params } = options;
  const query = params
    ? '?' + new URLSearchParams(params as Record<string, string>).toString()
    : '';

  const res = await fetch(`${BASE_URL}${path}${query}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}
```

## src/mock/router.ts

Mock 请求分发器。根据 path 匹配到对应的 mock handler。

```ts
import type { RequestOptions } from '../api/request';

type MockHandler = (options: RequestOptions) => unknown;

const routes: Record<string, MockHandler> = {
  // 例如：
  // 'GET /users': () => ({ list: userList, total: userList.length }),
  // 根据实际页面需要的接口填充
};

export async function handleMock<T>(path: string, options: RequestOptions): Promise<T> {
  const method = options.method || 'GET';
  const key = `${method} ${path}`;
  const handler = routes[key];
  await new Promise((resolve) => setTimeout(resolve, 200));
  if (!handler) {
    throw new Error(`Mock handler not found: ${key}`);
  }
  return handler(options) as T;
}
```

## src/layouts/MainLayout.tsx

带侧边栏 + 顶栏的主布局，用 `<Outlet />` 渲染子路由。菜单项根据原型里出现的导航入口来填。

```tsx
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Avatar
} from '@mui/material';
import { styled } from '@mui/material/styles';
import DashboardIcon from '@mui/icons-material/Dashboard';

const DRAWER_WIDTH = 220;

const LayoutRoot = styled(Box)({
  display: 'flex',
  minHeight: '100vh'
});

const Main = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: DRAWER_WIDTH,
  backgroundColor: theme.palette.background.default
}));

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  width: `calc(100% - ${DRAWER_WIDTH}px)`,
  marginLeft: DRAWER_WIDTH,
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.primary,
  boxShadow: 'none',
  borderBottom: `1px solid ${theme.palette.divider}`
}));

const menuItems = [
  { label: '仪表盘', path: '/dashboard', icon: <DashboardIcon /> }
  // 根据原型填充更多菜单项
];

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <LayoutRoot>
      <StyledAppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            后台管理系统
          </Typography>
          <Avatar>U</Avatar>
        </Toolbar>
      </StyledAppBar>
      <Drawer
        variant="persistent"
        open
        sx={{
          width: DRAWER_WIDTH,
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' }
        }}
      >
        <Toolbar>
          <Typography variant="h6">Logo</Typography>
        </Toolbar>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.path}
              selected={location.pathname.startsWith(item.path)}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Main>
        <Toolbar />
        <Outlet />
      </Main>
    </LayoutRoot>
  );
}
```

## src/pages/XxxPage/index.tsx（示例：列表页样板）

业务页面不要直接套这个，只是示意 styled() 的用法。具体页面要根据 HTML 原型内容写。

```tsx
import { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, Table, TableHead, TableBody, TableRow, TableCell } from '@mui/material';
import { styled } from '@mui/material/styles';
import { request } from '@/api/request';

const PageRoot = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2)
}));

const HeaderBar = styled(Box)({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 16
});

const TablePaper = styled(Paper)({
  padding: 16
});

interface UserItem {
  id: string;
  name: string;
  role: string;
}

export default function UsersPage() {
  const [list, setList] = useState<UserItem[]>([]);

  useEffect(() => {
    request<{ list: UserItem[] }>('/users').then((res) => setList(res.list));
  }, []);

  return (
    <PageRoot>
      <HeaderBar>
        <Typography variant="h5">用户管理</Typography>
        <Button variant="contained">新建用户</Button>
      </HeaderBar>
      <TablePaper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>姓名</TableCell>
              <TableCell>角色</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {list.map((u) => (
              <TableRow key={u.id}>
                <TableCell>{u.name}</TableCell>
                <TableCell>{u.role}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TablePaper>
    </PageRoot>
  );
}
```

## 环境变量文件

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
