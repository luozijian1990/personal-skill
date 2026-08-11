import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

function App() {
  const [tab, setTab] = useState('open');
  const [drawer, setDrawer] = useState(false);
  const [message, setMessage] = useState(false);

  return <>
    <header><strong>运维控制台</strong><nav>事件 &nbsp; 服务 &nbsp; 审计</nav></header>
    <main>
      <h1>事件中心</h1>
      <div className="tabs"><button className={tab === 'open' ? 'active' : ''} onClick={() => setTab('open')}>处理中</button><button className={tab === 'resolved' ? 'active' : ''} onClick={() => setTab('resolved')}>已解决</button></div>
      {tab === 'open' ? <article className="incident"><span>INC-1042 · API 延迟</span><button onClick={() => setDrawer(true)}>查看详情</button></article> : <section className="panel">暂无已解决事件</section>}
      {message && <section className="panel">事件已指派</section>}
    </main>
    {drawer && <div className="backdrop"><aside><h2>INC-1042</h2><p>API 延迟高于基线。</p><button className="primary" onClick={() => { setDrawer(false); setMessage(true); }}>指派给我</button><button onClick={() => setDrawer(false)}>关闭</button></aside></div>}
  </>;
}

createRoot(document.getElementById('root')).render(<App />);
