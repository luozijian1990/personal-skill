import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

function App() {
  const [tab, setTab] = useState('open');
  const [drawer, setDrawer] = useState(false);

  return <>
    <header><strong>运维控制台</strong><nav>事件 &nbsp; 服务 &nbsp; 审计</nav></header>
    <main>
      <h1>事件中心</h1>
      <button onClick={() => setTab(tab === 'open' ? 'resolved' : 'open')}>{tab === 'open' ? '处理中' : '已解决'}</button>
      <button onClick={() => setDrawer(true)}>查看详情</button>
      {drawer && <aside>INC-1042</aside>}
    </main>
  </>;
}

createRoot(document.getElementById('root')).render(<App />);
