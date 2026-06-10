#!/usr/bin/env python3
"""Convert structured learning-note markdown into roadmap.sh-style interactive HTML.

Usage:
  build_roadmap.py <file.md> [output.html]      # single file
  build_roadmap.py --batch <dir> [--out <dir>]  # scan dir, generate per-note roadmaps + index.html
  build_roadmap.py --serve <dir> [--port 8000]  # batch then start local server so index can read progress
"""
from __future__ import annotations
import argparse
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path


# ---------- markdown parsing ----------

def _clean_subitem(text: str, max_len: int = 42) -> str:
    text = text.strip().rstrip(":：。.")
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # 长句截到第一个标点/冒号
    head = re.split(r"[：:，,。.；;—\-]", text, maxsplit=1)[0].strip()
    if 6 <= len(head) <= max_len:
        return head
    return text[:max_len].rstrip()


def _fallback_subitems(content: str, limit: int = 6) -> list[str]:
    """没有 #### 时，从内容里挑顶层列表项作为关键词。"""
    items: list[str] = []
    in_code = False
    for raw in content.split("\n"):
        if raw.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^[-*+]\s+(.+)$", raw)  # 顶层（不含缩进）
        if not m:
            continue
        cleaned = _clean_subitem(m.group(1))
        if cleaned and cleaned not in items:
            items.append(cleaned)
            if len(items) >= limit:
                break
    return items


def heading_histogram(text: str) -> dict[int, int]:
    """统计 markdown 各级 heading 数量（H1-H6），跳过代码块内的 # 注释。"""
    counts = {i: 0 for i in range(1, 7)}
    in_code = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+\S", line)
        if m:
            counts[len(m.group(1))] += 1
    return counts


def diagnose(text: str, parts: list[dict]) -> tuple[str, str] | None:
    """解析结果异常时返回 (severity, message)；否则返回 None。

    severity:
      - 'recoverable'   : 可以通过 --shift N 修复
      - 'unrecoverable' : 结构上不适合做 roadmap，建议改用 learning-notes-builder
    """
    sec_count = sum(len(p["sections"]) for p in parts)
    if parts and sec_count > 0:
        return None

    hist = heading_histogram(text)
    total = sum(hist.values())

    lines = ["⚠️  解析失败——没有发现可用的小节。", "", "Heading 直方图："]
    if total == 0:
        lines.append("  （H1-H6 全部为 0）")
    else:
        for lvl in range(1, 7):
            if hist[lvl] > 0:
                lines.append(f"  H{lvl}: {hist[lvl]} 个")
    lines.append("")

    # 找数量最多的层级
    best_level, best_count = max(hist.items(), key=lambda kv: kv[1])

    # 判定档位：可挽救 vs 不可挽救
    if best_count < 3:
        lines.append("诊断：heading 太少或太散，没有清晰的章节结构。无法用 --shift 修复。")
        lines.append("")
        lines.append("💡 建议：用 /learning-notes-builder 把它（连同任何相关原材料）")
        lines.append("   重新合成一份结构化 markdown，再回来跑 roadmap。")
        return ("unrecoverable", "\n".join(lines))

    shift = 3 - best_level
    if shift == 0:
        lines.append("诊断：heading 层级看起来正常，但解析出 0 小节。结构可能比较特殊。")
        lines.append("")
        lines.append("💡 建议：用 /learning-notes-builder 重新合成一份结构化 markdown。")
        return ("unrecoverable", "\n".join(lines))

    lines.append(f"诊断：你的笔记把 H{best_level}（{best_count} 个）当作小节，")
    lines.append(f"      但 roadmap 期望小节在 H3 级。")
    lines.append("")
    lines.append("✅ 可以通过 --shift 修复。建议：")
    lines.append(f"  python3 build_roadmap.py --shift {shift} <file>")
    return ("recoverable", "\n".join(lines))


def parse(md_path: Path, shift: int = 0) -> dict:
    """解析 markdown。shift != 0 时把所有 heading 层级整体平移 shift 级。"""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    in_code = False
    title = md_path.stem
    parts: list[dict] = []
    current_part: dict | None = None
    current_section: dict | None = None
    pre_part_buffer: list[str] = []

    for raw in lines:
        line = raw.rstrip("\n")

        if line.lstrip().startswith("```"):
            in_code = not in_code
            if current_section is not None:
                current_section["content"].append(line)
            continue

        if in_code:
            if current_section is not None:
                current_section["content"].append(line)
            continue

        # 放宽到 H1-H6，平移后再判断有效范围
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m:
            level = len(m.group(1)) + shift
            heading = m.group(2).strip()
            if level < 1 or level > 4:
                # 平移后超出 [1,4]，当普通文本处理
                if current_section is not None:
                    current_section["content"].append(line)
                continue
            if level == 1:
                title = heading
                continue
            if level == 2:
                current_part = {"title": heading, "sections": []}
                parts.append(current_part)
                current_section = None
                continue
            if level == 3:
                if current_part is None:
                    current_part = {"title": "概述", "sections": []}
                    parts.append(current_part)
                current_section = {"title": heading, "content": [], "subs": []}
                current_part["sections"].append(current_section)
                continue
            if level == 4 and current_section is not None:
                cleaned = _clean_subitem(heading)
                if cleaned and cleaned not in current_section["subs"]:
                    current_section["subs"].append(cleaned)
                current_section["content"].append(line)
                continue

        if current_section is not None:
            current_section["content"].append(line)
        elif current_part is None:
            pre_part_buffer.append(line)

    for p in parts:
        for s in p["sections"]:
            s["content"] = "\n".join(s["content"]).strip()
            if not s["subs"]:
                s["subs"] = _fallback_subitems(s["content"])

    intro = "\n".join(pre_part_buffer).strip()
    return {"title": title, "intro": intro, "parts": parts}


def section_count(data: dict) -> int:
    return sum(len(p["sections"]) for p in data["parts"])


def qualifies(data: dict, min_sections: int = 3) -> bool:
    """A markdown is a 'learning note' if it has at least N H3 sections under H2 parts."""
    return len(data["parts"]) >= 1 and section_count(data) >= min_sections


# ---------- single-note HTML ----------

ROADMAP_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>__TITLE__ · Roadmap</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({startOnLoad:false, theme:'base', themeVariables:{
    background:'#fffdf5', primaryColor:'#fff9d6', primaryBorderColor:'#1f2933',
    primaryTextColor:'#1f2933', lineColor:'#1f2933', fontFamily:'inherit'}});
  window.__mermaid = mermaid;
</script>
<style>
  :root{
    --bg:#fdf6e3; --ink:#1f2933; --muted:#6b6657;
    --paper:#fffdf5; --line:#1f2933;
    --todo:#cbd5e1; --doing:#facc15; --done:#22c55e;
    --accent:#fbbf24;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);
    font-family:'Inter','PingFang SC','Microsoft YaHei',sans-serif;}
  header{padding:32px 40px 16px;border-bottom:2px dashed var(--ink);
    position:sticky;top:0;background:var(--bg);z-index:5;}
  h1{margin:0 0 8px;font-size:28px;letter-spacing:1px}
  .meta{display:flex;gap:24px;align-items:center;flex-wrap:wrap;font-size:13px;color:var(--muted)}
  .progress{flex:1;min-width:220px;height:10px;background:#e7dfc7;
    border:1px solid var(--ink);border-radius:6px;overflow:hidden}
  .progress > span{display:block;height:100%;background:var(--done);width:0;transition:width .3s}
  .legend{display:flex;gap:14px;align-items:center}
  .dot{width:12px;height:12px;border-radius:50%;border:1px solid var(--ink);display:inline-block;vertical-align:middle;margin-right:4px}
  .dot.todo{background:var(--todo)} .dot.doing{background:var(--doing)} .dot.done{background:var(--done)}
  button.reset, a.back{background:var(--paper);border:1px solid var(--ink);
    border-radius:6px;padding:6px 12px;cursor:pointer;font:inherit;text-decoration:none;color:var(--ink)}
  button.reset:hover, a.back:hover{background:var(--accent)}
  main{padding:32px 40px 80px;max-width:1280px;margin:0 auto}
  .part{margin-bottom:48px;position:relative}
  .part-head{display:flex;align-items:center;gap:14px;margin-bottom:18px}
  .part-num{width:42px;height:42px;border-radius:50%;background:var(--ink);
    color:var(--bg);display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:18px;flex-shrink:0}
  .part-title{font-size:20px;font-weight:600;margin:0}
  .part-bar{flex:1;height:0;border-top:2px dashed var(--ink);opacity:.4}
  .sections{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
    gap:14px;padding-left:56px}
  .card{background:var(--paper);border:1.5px solid var(--ink);
    border-radius:10px;padding:12px 14px;cursor:pointer;
    box-shadow:3px 3px 0 var(--ink);transition:transform .12s,box-shadow .12s;
    position:relative;display:flex;align-items:center;gap:10px;min-height:64px}
  .card:hover{transform:translate(-1px,-1px);box-shadow:4px 4px 0 var(--ink)}
  .card[data-status="doing"]{background:#fff9d6}
  .card[data-status="done"]{background:#d9f7d9}
  .card .status{width:18px;height:18px;border-radius:50%;border:1.5px solid var(--ink);
    flex-shrink:0;background:var(--todo);cursor:pointer}
  .card[data-status="doing"] .status{background:var(--doing)}
  .card[data-status="done"] .status{background:var(--done)}
  .card .ttl{font-size:13.5px;line-height:1.35;font-weight:500}
  .card .badge{margin-left:auto;font-size:11px;color:var(--muted);
    background:rgba(31,41,51,.05);border:1px solid rgba(31,41,51,.15);
    padding:1px 7px;border-radius:10px;flex-shrink:0}
  /* drawer 顶部胶囊条（1-2 排自动折行，每个胶囊不同色） */
  .tags-bar{display:flex;flex-wrap:wrap;gap:7px 8px;padding:14px 24px 14px;
    border-bottom:1px dashed var(--ink);background:#fffdf5;align-items:center}
  .tags-bar .pill{font-size:12px;color:var(--ink);
    border:1px solid var(--ink);padding:3px 10px;border-radius:14px;
    white-space:nowrap;box-shadow:1.5px 1.5px 0 var(--ink);font-weight:500}
  .tags-bar .pill.more{background:transparent;border-style:dashed;color:var(--muted);
    box-shadow:none;cursor:help}
  .tags-bar.empty{display:none}
  .search input{padding:6px 10px;border:1px solid var(--ink);border-radius:6px;font:inherit;background:var(--paper)}
  .drawer{position:fixed;top:0;right:0;width:min(640px,92vw);height:100vh;
    background:var(--paper);border-left:2px solid var(--ink);
    transform:translateX(100%);transition:transform .25s;z-index:20;
    display:flex;flex-direction:column}
  .drawer.open{transform:translateX(0)}
  .drawer header{position:sticky;top:0;display:flex;align-items:center;
    gap:12px;padding:16px 20px;border-bottom:1px solid var(--ink);background:var(--paper)}
  .drawer h2{margin:0;font-size:17px;flex:1}
  .drawer .body{padding:18px 24px;overflow:auto;flex:1;line-height:1.7;font-size:14.5px}
  .drawer .body pre{background:#1a1d23;color:#eee;padding:12px;border-radius:6px;overflow:auto}
  .drawer .body code{font-family:'JetBrains Mono','Menlo',monospace;font-size:13px}
  .drawer .body :not(pre) > code{background:#f1ead0;padding:2px 5px;border-radius:3px}
  .drawer .body .mermaid{background:var(--paper);border:1.5px solid var(--ink);
    border-radius:8px;padding:14px;margin:10px 0;box-shadow:3px 3px 0 var(--ink);
    overflow:auto;text-align:center;cursor:zoom-in}
  .drawer .body .mermaid svg{max-width:100%;height:auto}
  .drawer .body h1,.drawer .body h2,.drawer .body h3,.drawer .body h4{margin:1.2em 0 .4em}
  .drawer .body table{border-collapse:collapse;margin:8px 0}
  .drawer .body th,.drawer .body td{border:1px solid #c8c0a4;padding:5px 9px}
  .drawer .toggle-group{display:flex;gap:6px}
  .drawer .toggle-group button{padding:4px 10px;border:1px solid var(--ink);
    background:transparent;border-radius:5px;font:inherit;cursor:pointer;font-size:12px}
  .drawer .toggle-group button.active{background:var(--ink);color:var(--bg)}
  .drawer .close{background:transparent;border:none;font-size:22px;cursor:pointer;line-height:1;padding:0 4px}
  .backdrop{position:fixed;inset:0;background:rgba(31,41,51,.35);z-index:15;display:none}
  .backdrop.open{display:block}
  .diagram-backdrop{position:fixed;inset:0;background:rgba(31,41,51,.55);z-index:35;display:none}
  .diagram-backdrop.open{display:block}
  .diagram-modal{position:fixed;inset:clamp(10px,3vmin,28px);background:var(--paper);
    border:2px solid var(--ink);border-radius:10px;box-shadow:6px 6px 0 var(--ink);
    z-index:40;display:none;flex-direction:column;overflow:hidden}
  .diagram-modal.open{display:flex}
  .diagram-modal header{position:static;display:flex;align-items:center;gap:12px;
    padding:12px 16px;border-bottom:1px solid var(--ink);background:var(--paper)}
  .diagram-modal header strong{font-size:15px;flex:1}
  .diagram-controls{display:flex;align-items:center;gap:6px}
  .diagram-controls button{width:30px;height:30px;border:1px solid var(--ink);
    border-radius:6px;background:var(--paper);font:inherit;line-height:1;cursor:pointer}
  .diagram-controls button:hover{background:var(--accent)}
  .diagram-zoom{min-width:44px;text-align:center;font-size:12px;color:var(--muted)}
  .diagram-close{background:transparent;border:none;font-size:24px;cursor:pointer;line-height:1;padding:0 4px}
  .diagram-body{overflow:auto;flex:1;background:#fffdf5;color:var(--ink)}
  .diagram-canvas{min-width:100%;min-height:100%;display:flex;align-items:center;justify-content:center}
  .diagram-inner{transform-origin:center center}
  .diagram-inner .mermaid{display:block;margin:0;padding:0;background:transparent;
    border:0;box-shadow:none;text-align:center;cursor:default;color:var(--ink)}
  .diagram-inner .mermaid svg{display:block;max-width:none !important;height:auto !important}
  .hidden{display:none !important}
  @media (max-width:640px){
    main{padding:18px}
    .sections{padding-left:0;grid-template-columns:1fr}
    header{padding:18px 20px 12px}
  }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="meta">
    __BACK_LINK__
    <div class="legend">
      <span><span class="dot todo"></span>待学</span>
      <span><span class="dot doing"></span>在学</span>
      <span><span class="dot done"></span>已学</span>
    </div>
    <div class="progress" title="学习进度"><span id="bar"></span></div>
    <span id="progress-text">0 / 0</span>
    <span class="search"><input id="search" type="search" placeholder="搜索小节…"></span>
    <button class="reset" id="reset">重置进度</button>
  </div>
</header>
<main id="roadmap"></main>

<div class="backdrop" id="backdrop"></div>
<aside class="drawer" id="drawer">
  <header>
    <h2 id="d-title"></h2>
    <div class="toggle-group" data-role="status">
      <button data-status="todo">待学</button>
      <button data-status="doing">在学</button>
      <button data-status="done">已学</button>
    </div>
    <button class="close" id="d-close">×</button>
  </header>
  <div class="tags-bar empty" id="d-tags"></div>
  <div class="body" id="d-body"></div>
</aside>
<div class="diagram-backdrop" id="diagram-backdrop"></div>
<section class="diagram-modal" id="diagram-modal" role="dialog" aria-modal="true" aria-label="放大图表">
  <header>
    <strong>Mermaid 图表</strong>
    <div class="diagram-controls" aria-label="图表缩放">
      <button id="diagram-zoom-out" title="缩小">-</button>
      <span class="diagram-zoom" id="diagram-zoom">100%</span>
      <button id="diagram-zoom-in" title="放大">+</button>
    </div>
    <button class="diagram-close" id="diagram-close" title="关闭">×</button>
  </header>
  <div class="diagram-body" id="diagram-body">
    <div class="diagram-canvas" id="diagram-canvas">
      <div class="diagram-inner" id="diagram-inner"></div>
    </div>
  </div>
</section>

<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  const data = JSON.parse(document.getElementById('data').textContent);
  const STORAGE_KEY = 'roadmap:' + data.title;
  const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');

  const root = document.getElementById('roadmap');
  let totalCount = 0;

  data.parts.forEach((part, pi) => {
    const partEl = document.createElement('section');
    partEl.className = 'part';
    partEl.innerHTML = `
      <div class="part-head">
        <div class="part-num">${pi+1}</div>
        <h2 class="part-title">${escapeHtml(part.title)}</h2>
        <div class="part-bar"></div>
      </div>
      <div class="sections"></div>
    `;
    const grid = partEl.querySelector('.sections');
    part.sections.forEach((sec, si) => {
      totalCount++;
      const id = `${pi}-${si}`;
      const status = state[id] || 'todo';
      const card = document.createElement('div');
      card.className = 'card';
      card.dataset.id = id;
      card.dataset.status = status;
      card.dataset.title = sec.title.toLowerCase();
      const subCount = (sec.subs || []).length;
      card.innerHTML = `
        <div class="status" title="点击切换状态"></div>
        <div class="ttl">${escapeHtml(sec.title)}</div>
        ${subCount ? `<span class="badge" title="${subCount} 个知识点">${subCount}</span>` : ''}
      `;
      card.addEventListener('click', e => {
        if (e.target.classList.contains('status')) {
          cycleStatus(id);
        } else {
          openDrawer(pi, si);
        }
      });
      grid.appendChild(card);
    });
    root.appendChild(partEl);
  });

  const drawer = document.getElementById('drawer');
  const backdrop = document.getElementById('backdrop');
  const dTitle = document.getElementById('d-title');
  const dBody = document.getElementById('d-body');
  const diagramBackdrop = document.getElementById('diagram-backdrop');
  const diagramModal = document.getElementById('diagram-modal');
  const diagramBody = document.getElementById('diagram-body');
  const diagramCanvas = document.getElementById('diagram-canvas');
  const diagramInner = document.getElementById('diagram-inner');
  const diagramZoom = document.getElementById('diagram-zoom');
  const diagramZoomOut = document.getElementById('diagram-zoom-out');
  const diagramZoomIn = document.getElementById('diagram-zoom-in');
  let diagramScale = 1;
  let diagramBaseWidth = 1;
  let diagramBaseHeight = 1;
  let currentId = null;

  const dTags = document.getElementById('d-tags');
  function pillColor(i){
    // 黄金角分布，柔和粉彩，深色 ink 字看得清
    const h = (i * 47) % 360;
    return `hsl(${h}, 72%, 86%)`;
  }
  function renderTags(subs){
    const MAX = 12;
    if (!subs || !subs.length) { dTags.className = 'tags-bar empty'; dTags.innerHTML = ''; return; }
    dTags.className = 'tags-bar';
    const visible = subs.slice(0, MAX);
    const rest = subs.slice(MAX);
    dTags.innerHTML = visible.map((s, i) =>
      `<span class="pill" style="background:${pillColor(i)}">${escapeHtml(s)}</span>`
    ).join('') + (rest.length
      ? `<span class="pill more" title="${escapeHtml(rest.join(' · '))}">+${rest.length}</span>`
      : '');
  }
  function openDrawer(pi, si){
    const sec = data.parts[pi].sections[si];
    currentId = `${pi}-${si}`;
    // 若小节标题已含 "N.N " 或 "N.N.N " 编号，去掉避免与自动编号重复
    const cleanTitle = sec.title.replace(/^\d+(\.\d+)*\s+/, '');
    dTitle.textContent = `${pi+1}.${si+1}  ${cleanTitle}`;
    renderTags(sec.subs);
    dBody.innerHTML = marked.parse(sec.content || '*（此小节没有正文）*');
    dBody.querySelectorAll('pre > code.language-mermaid').forEach((code, idx) => {
      const div = document.createElement('div');
      div.className = 'mermaid';
      div.id = 'mmd-' + Date.now() + '-' + idx;
      div.title = '点击放大图表';
      div.textContent = code.textContent;
      code.parentElement.replaceWith(div);
    });
    dBody.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
    if (window.__mermaid) {
      window.__mermaid.run({nodes: dBody.querySelectorAll('.mermaid')}).catch(()=>{});
    }
    dBody.scrollTop = 0;
    drawer.classList.add('open');
    backdrop.classList.add('open');
    syncStatusButtons();
  }
  function closeDrawer(){
    drawer.classList.remove('open');
    backdrop.classList.remove('open');
    currentId = null;
  }
  document.getElementById('d-close').onclick = closeDrawer;
  backdrop.onclick = closeDrawer;
  document.getElementById('diagram-close').onclick = closeDiagram;
  diagramBackdrop.onclick = closeDiagram;
  diagramZoomOut.onclick = () => setDiagramScale(diagramScale / 1.2);
  diagramZoomIn.onclick = () => setDiagramScale(diagramScale * 1.2);
  dBody.addEventListener('click', e => {
    const diagram = e.target.closest('.mermaid');
    if (diagram) openDiagram(diagram);
  });
  window.addEventListener('resize', () => {
    if (diagramModal.classList.contains('open')) fitDiagramToViewport();
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (diagramModal.classList.contains('open')) closeDiagram();
    else closeDrawer();
  });

  function openDiagram(diagram){
    diagramInner.innerHTML = '';
    resetDiagramViewport();
    const clone = diagram.cloneNode(true);
    clone.removeAttribute('id');
    clone.removeAttribute('title');
    rewriteSvgIds(clone, 'zoom-' + Date.now() + '-');
    normalizeDiagramSvg(clone);
    diagramInner.appendChild(clone);
    diagramModal.classList.add('open');
    diagramBackdrop.classList.add('open');
    requestAnimationFrame(() => {
      relaxDiagramNodeLabels(clone);
      normalizeDiagramSvg(clone);
      const size = measureDiagram(clone);
      diagramBaseWidth = size.width;
      diagramBaseHeight = size.height;
      fitDiagramToViewport();
    });
  }
  function closeDiagram(){
    diagramModal.classList.remove('open');
    diagramBackdrop.classList.remove('open');
    diagramInner.innerHTML = '';
  }
  function resetDiagramViewport(){
    diagramScale = 1;
    diagramCanvas.style.width = '';
    diagramCanvas.style.height = '';
    diagramInner.style.transform = 'scale(1)';
    diagramZoom.textContent = '100%';
  }
  function fitDiagramToViewport(){
    const bodyBox = diagramBody.getBoundingClientRect();
    const roomW = Math.max(1, bodyBox.width - 32);
    const roomH = Math.max(1, bodyBox.height - 32);
    const fit = Math.min(roomW / diagramBaseWidth, roomH / diagramBaseHeight);
    const readableMin = window.innerWidth < 700 ? 0.55 : 0.75;
    setDiagramScale(clamp(fit, readableMin, 1.5));
  }
  function setDiagramScale(scale){
    diagramScale = clamp(scale, 0.1, 3);
    const pad = 32;
    diagramCanvas.style.width = Math.ceil(diagramBaseWidth * diagramScale + pad) + 'px';
    diagramCanvas.style.height = Math.ceil(diagramBaseHeight * diagramScale + pad) + 'px';
    diagramInner.style.transform = `scale(${diagramScale})`;
    diagramZoom.textContent = Math.round(diagramScale * 100) + '%';
    requestAnimationFrame(() => {
      diagramBody.scrollLeft = Math.max(0, (diagramCanvas.scrollWidth - diagramBody.clientWidth) / 2);
      diagramBody.scrollTop = Math.max(0, (diagramCanvas.scrollHeight - diagramBody.clientHeight) / 2);
    });
  }
  function measureDiagram(root){
    const svg = root.querySelector('svg');
    if (svg) {
      const viewBox = svg.viewBox && svg.viewBox.baseVal;
      if (viewBox && viewBox.width && viewBox.height) {
        return {width: viewBox.width, height: viewBox.height};
      }
      const rect = svg.getBoundingClientRect();
      if (rect.width && rect.height) return {width: rect.width, height: rect.height};
    }
    const rect = root.getBoundingClientRect();
    return {width: Math.max(1, rect.width), height: Math.max(1, rect.height)};
  }
  function normalizeDiagramSvg(root){
    const svg = root.querySelector('svg');
    if (!svg) return;
    const viewBox = svg.viewBox && svg.viewBox.baseVal;
    if (viewBox && viewBox.width && viewBox.height) {
      svg.setAttribute('width', viewBox.width);
      svg.setAttribute('height', viewBox.height);
      svg.style.maxWidth = 'none';
    }
  }
  function relaxDiagramNodeLabels(root){
    const svg = root.querySelector('svg');
    if (!svg) return;
    let changed = false;
    svg.querySelectorAll('g.node').forEach(node => {
      const shape = node.querySelector('rect,polygon,circle,ellipse,path');
      const foreignObject = node.querySelector('foreignObject');
      const htmlLabel = foreignObject && foreignObject.querySelector('div,span');
      if (!shape || !foreignObject || !htmlLabel) return;

      const foBox = foreignObject.getBBox();
      const foRect = foreignObject.getBoundingClientRect();
      const labelRect = htmlLabel.getBoundingClientRect();
      if (!foBox.width || !foBox.height || !foRect.width || !foRect.height) return;

      const scaleX = foRect.width / foBox.width;
      const scaleY = foRect.height / foBox.height;
      const labelWidth = labelRect.width / scaleX;
      const labelHeight = labelRect.height / scaleY;
      const nextFoWidth = Math.ceil(Math.max(foBox.width, labelWidth + 10));
      const nextFoHeight = Math.ceil(Math.max(foBox.height, labelHeight + 8));
      const dx = nextFoWidth - foBox.width;
      const dy = nextFoHeight - foBox.height;
      if (dx <= 1 && dy <= 1) return;

      centerForeignObject(foreignObject, dx, dy);
      foreignObject.setAttribute('width', nextFoWidth);
      foreignObject.setAttribute('height', nextFoHeight);
      expandNodeShape(shape, nextFoWidth + 24, nextFoHeight + 18);
      changed = true;
    });
    if (changed) refreshSvgViewBox(svg);
  }
  function centerForeignObject(foreignObject, dx, dy){
    const labelGroup = foreignObject.closest('g.label');
    if (labelGroup && labelGroup !== foreignObject.ownerSVGElement) {
      const shifted = shiftTranslate(labelGroup, -dx / 2, -dy / 2);
      if (shifted) return;
    }
    const x = parseFloat(foreignObject.getAttribute('x') || foreignObject.getBBox().x || 0);
    const y = parseFloat(foreignObject.getAttribute('y') || foreignObject.getBBox().y || 0);
    foreignObject.setAttribute('x', x - dx / 2);
    foreignObject.setAttribute('y', y - dy / 2);
  }
  function shiftTranslate(el, dx, dy){
    const transform = el.getAttribute('transform') || '';
    const match = transform.match(/translate\(\s*([-0-9.]+)(?:[ ,]+([-0-9.]+))?\s*\)/);
    if (!match) return false;
    const x = parseFloat(match[1]);
    const y = parseFloat(match[2] || '0');
    if (!Number.isFinite(x) || !Number.isFinite(y)) return false;
    el.setAttribute('transform', transform.replace(match[0], `translate(${x + dx}, ${y + dy})`));
    return true;
  }
  function expandNodeShape(shape, minWidth, minHeight){
    const box = shape.getBBox();
    const targetWidth = Math.max(box.width, minWidth);
    const targetHeight = Math.max(box.height, minHeight);
    if (targetWidth <= box.width + 1 && targetHeight <= box.height + 1) return;
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    const tag = shape.tagName.toLowerCase();
    if (tag === 'rect') {
      shape.setAttribute('x', cx - targetWidth / 2);
      shape.setAttribute('y', cy - targetHeight / 2);
      shape.setAttribute('width', targetWidth);
      shape.setAttribute('height', targetHeight);
    } else if (tag === 'ellipse') {
      shape.setAttribute('rx', targetWidth / 2);
      shape.setAttribute('ry', targetHeight / 2);
    } else if (tag === 'circle') {
      shape.setAttribute('r', Math.max(targetWidth, targetHeight) / 2);
    } else if (tag === 'polygon') {
      expandPolygon(shape, box, targetWidth, targetHeight);
    }
  }
  function expandPolygon(shape, box, targetWidth, targetHeight){
    const sx = box.width ? targetWidth / box.width : 1;
    const sy = box.height ? targetHeight / box.height : 1;
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    const points = (shape.getAttribute('points') || '').trim().split(/\s+/).map(pair => {
      const [x, y] = pair.split(',').map(Number);
      if (!Number.isFinite(x) || !Number.isFinite(y)) return pair;
      return `${cx + (x - cx) * sx},${cy + (y - cy) * sy}`;
    });
    shape.setAttribute('points', points.join(' '));
  }
  function refreshSvgViewBox(svg){
    try {
      const box = svg.getBBox();
      const pad = 8;
      svg.setAttribute('viewBox', `${box.x - pad} ${box.y - pad} ${box.width + pad * 2} ${box.height + pad * 2}`);
    } catch (_) {}
  }
  function clamp(value, min, max){
    return Math.max(min, Math.min(max, value));
  }
  function rewriteSvgIds(root, prefix){
    const idMap = new Map();
    root.querySelectorAll('[id]').forEach(el => {
      const oldId = el.id;
      const newId = prefix + oldId;
      idMap.set(oldId, newId);
      el.id = newId;
    });
    if (!idMap.size) return;
    const replacements = [...idMap.entries()].sort((a, b) => b[0].length - a[0].length);
    root.querySelectorAll('*').forEach(el => {
      for (const attr of [...el.attributes]) {
        let value = attr.value;
        replacements.forEach(([oldId, newId]) => {
          value = value.replaceAll(`#${oldId}`, `#${newId}`);
        });
        if (value !== attr.value) el.setAttribute(attr.name, value);
      }
    });
    root.querySelectorAll('style').forEach(style => {
      let css = style.textContent || '';
      replacements.forEach(([oldId, newId]) => {
        css = css.replaceAll(`#${oldId}`, `#${newId}`);
      });
      style.textContent = css;
    });
  }

  drawer.querySelectorAll('.toggle-group button').forEach(btn => {
    btn.onclick = () => {
      if (!currentId) return;
      setStatus(currentId, btn.dataset.status);
      syncStatusButtons();
    };
  });
  function syncStatusButtons(){
    const cur = state[currentId] || 'todo';
    drawer.querySelectorAll('.toggle-group button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.status === cur);
    });
  }

  function cycleStatus(id){
    const order = ['todo','doing','done'];
    const cur = state[id] || 'todo';
    const next = order[(order.indexOf(cur)+1) % order.length];
    setStatus(id, next);
  }
  function setStatus(id, status){
    if (status === 'todo') delete state[id]; else state[id] = status;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    const card = document.querySelector(`.card[data-id="${id}"]`);
    if (card) card.dataset.status = status;
    if (currentId === id) syncStatusButtons();
    updateProgress();
  }

  function updateProgress(){
    const done = Object.values(state).filter(v => v === 'done').length;
    document.getElementById('bar').style.width = (done / totalCount * 100) + '%';
    document.getElementById('progress-text').textContent = `${done} / ${totalCount}`;
  }
  updateProgress();

  document.getElementById('search').addEventListener('input', e => {
    const q = e.target.value.trim().toLowerCase();
    document.querySelectorAll('.card').forEach(c => {
      c.classList.toggle('hidden', q && !c.dataset.title.includes(q));
    });
    document.querySelectorAll('.part').forEach(p => {
      const anyVisible = [...p.querySelectorAll('.card')].some(c => !c.classList.contains('hidden'));
      p.classList.toggle('hidden', !anyVisible);
    });
  });

  document.getElementById('reset').onclick = () => {
    if (!confirm('重置所有进度？')) return;
    for (const k of Object.keys(state)) delete state[k];
    localStorage.removeItem(STORAGE_KEY);
    document.querySelectorAll('.card').forEach(c => c.dataset.status = 'todo');
    updateProgress();
  };

  function escapeHtml(s){
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
})();
</script>
</body>
</html>
"""


def render_single(data: dict, *, back_href: str | None = None) -> str:
    back_link = (
        f'<a class="back" href="{back_href}">← 返回总览</a>' if back_href else ""
    )
    return (
        ROADMAP_HTML
        .replace("__TITLE__", data["title"])
        .replace("__BACK_LINK__", back_link)
        .replace("__DATA__", json.dumps(data, ensure_ascii=False))
    )


# ---------- index page ----------

INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>__INDEX_TITLE__</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root{
    --bg:#fdf6e3; --ink:#1f2933; --muted:#6b6657;
    --paper:#fffdf5; --done:#22c55e; --accent:#fbbf24;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);
    font-family:'Inter','PingFang SC','Microsoft YaHei',sans-serif;}
  header{padding:36px 48px 20px;border-bottom:2px dashed var(--ink)}
  h1{margin:0 0 6px;font-size:30px}
  .sub{color:var(--muted);font-size:13px}
  .tip{margin-top:10px;font-size:12px;color:var(--muted)}
  .tip code{background:#f1ead0;padding:2px 5px;border-radius:3px;font-family:'JetBrains Mono','Menlo',monospace}
  .controls{margin:18px 0 6px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .controls input{padding:7px 12px;border:1px solid var(--ink);border-radius:6px;font:inherit;background:var(--paper);min-width:260px}
  main{padding:24px 48px 80px;max-width:1280px;margin:0 auto}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
  .card{background:var(--paper);border:1.5px solid var(--ink);border-radius:12px;
    padding:18px 18px 16px;box-shadow:4px 4px 0 var(--ink);text-decoration:none;color:inherit;
    display:flex;flex-direction:column;gap:10px;transition:transform .12s,box-shadow .12s}
  .card:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink);background:#fff9d6}
  .card .ttl{font-size:17px;font-weight:600;line-height:1.3}
  .card .stats{font-size:12.5px;color:var(--muted);display:flex;gap:14px;flex-wrap:wrap}
  .pbar{height:8px;background:#e7dfc7;border:1px solid var(--ink);border-radius:5px;overflow:hidden}
  .pbar > span{display:block;height:100%;background:var(--done);width:0;transition:width .3s}
  .ptext{font-size:11.5px;color:var(--muted);display:flex;justify-content:space-between}
  .hidden{display:none !important}
  @media (max-width:640px){header,main{padding-left:18px;padding-right:18px}}
</style>
</head>
<body>
<header>
  <h1>__INDEX_TITLE__</h1>
  <div class="sub">共 __NOTE_COUNT__ 篇笔记 · __TOTAL_SECTIONS__ 个小节</div>
  <div class="controls">
    <input id="q" type="search" placeholder="搜索笔记…">
    <span class="sub" id="visible-count"></span>
  </div>
  <div class="tip">提示：要在本页看到各笔记的实时学习进度，请用 <code>python3 -m http.server</code> 在此目录启动本地服务后访问（file:// 协议下浏览器对 localStorage 做了隔离）。</div>
</header>
<main>
  <div class="grid" id="grid"></div>
</main>
<script id="data" type="application/json">__INDEX_DATA__</script>
<script>
(function(){
  const notes = JSON.parse(document.getElementById('data').textContent);
  const grid = document.getElementById('grid');

  notes.forEach(n => {
    const state = JSON.parse(localStorage.getItem('roadmap:' + n.title) || '{}');
    const done = Object.values(state).filter(v => v === 'done').length;
    const pct = n.sections ? Math.round(done / n.sections * 100) : 0;
    const a = document.createElement('a');
    a.className = 'card';
    a.href = n.href;
    a.dataset.title = (n.title + ' ' + n.href).toLowerCase();
    a.innerHTML = `
      <div class="ttl">${escapeHtml(n.title)}</div>
      <div class="stats">
        <span>${n.parts} 部分</span>
        <span>${n.sections} 小节</span>
        <span title="源文件">${escapeHtml(n.source)}</span>
      </div>
      <div class="pbar"><span style="width:${pct}%"></span></div>
      <div class="ptext"><span>${done} / ${n.sections} 已学</span><span>${pct}%</span></div>
    `;
    grid.appendChild(a);
  });

  document.getElementById('visible-count').textContent = notes.length + ' 篇';
  document.getElementById('q').addEventListener('input', e => {
    const q = e.target.value.trim().toLowerCase();
    let visible = 0;
    grid.querySelectorAll('.card').forEach(c => {
      const show = !q || c.dataset.title.includes(q);
      c.classList.toggle('hidden', !show);
      if (show) visible++;
    });
    document.getElementById('visible-count').textContent = visible + ' 篇';
  });

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
})();
</script>
</body>
</html>
"""


def render_index(notes: list[dict], title: str) -> str:
    total_sections = sum(n["sections"] for n in notes)
    return (
        INDEX_HTML
        .replace("__INDEX_TITLE__", title)
        .replace("__NOTE_COUNT__", str(len(notes)))
        .replace("__TOTAL_SECTIONS__", str(total_sections))
        .replace("__INDEX_DATA__", json.dumps(notes, ensure_ascii=False))
    )


# ---------- batch ----------

SKIP_PATTERNS = re.compile(
    r"(?:^|/)(?:README|CHANGELOG|LICENSE|CONTRIBUTING|TODO|HISTORY|NOTES)\.md$",
    re.IGNORECASE,
)


def discover(root: Path, min_sections: int = 3, shift: int = 0) -> list[tuple[Path, dict]]:
    """Walk root, parse every .md, keep ones that look like learning notes."""
    found: list[tuple[Path, dict]] = []
    for md in sorted(root.rglob("*.md")):
        # skip generated/aux files, hidden dirs
        if any(part.startswith(".") for part in md.relative_to(root).parts):
            continue
        if SKIP_PATTERNS.search(str(md)):
            continue
        # skip files inside node_modules / venv / etc.
        if any(seg in {"node_modules", "venv", ".venv", "dist", "build", "__pycache__"}
               for seg in md.parts):
            continue
        try:
            data = parse(md, shift=shift)
        except Exception as e:
            print(f"  ! skip {md.relative_to(root)}: {e}", file=sys.stderr)
            continue
        if qualifies(data, min_sections):
            found.append((md, data))
    return found


def build_single(md_path: Path, out_path: Path, back_href: str | None = None, shift: int = 0) -> dict:
    data = parse(md_path, shift=shift)
    out_path.write_text(render_single(data, back_href=back_href), encoding="utf-8")
    return data


def build_batch(root: Path, out_dir: Path | None, min_sections: int, shift: int = 0) -> Path:
    out_dir = out_dir or root
    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / "learning-roadmap-index.html"
    notes_meta: list[dict] = []

    found = discover(root, min_sections, shift=shift)
    if not found:
        raise SystemExit(f"在 {root} 下没有发现符合条件的学习笔记（≥{min_sections} 个 ### 小节）")

    print(f"扫描 {root}：发现 {len(found)} 篇符合条件的笔记")
    for md, data in found:
        rel = md.relative_to(root)
        # roadmap goes right next to the source md
        roadmap_path = md.parent / f"{md.stem}-roadmap.html"
        # back link from roadmap → index, using relative path
        try:
            back_rel = os.path.relpath(index_path, roadmap_path.parent)
        except ValueError:
            back_rel = None
        roadmap_path.write_text(
            render_single(data, back_href=back_rel), encoding="utf-8"
        )
        href = os.path.relpath(roadmap_path, out_dir)
        sec = section_count(data)
        notes_meta.append({
            "title": data["title"],
            "source": str(rel),
            "href": href,
            "parts": len(data["parts"]),
            "sections": sec,
        })
        print(f"  ✓ {rel}  →  {roadmap_path.relative_to(root)}  ({len(data['parts'])}/{sec})")

    notes_meta.sort(key=lambda n: (-n["sections"], n["title"]))
    index_path.write_text(
        render_index(notes_meta, title=f"学习笔记 · Roadmap 总览（{root.name}）"),
        encoding="utf-8",
    )
    print(f"\n✓ 总览已生成：{index_path}")
    return index_path


def serve(root: Path, port: int = 8000, open_index: Path | None = None) -> None:
    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        if open_index is not None:
            try:
                rel = open_index.resolve().relative_to(root.resolve())
                url += str(rel)
            except ValueError:
                pass
        print(f"\n→ 本地服务已启动：{url}")
        print("  （Ctrl+C 停止）")
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


# ---------- CLI ----------

def main() -> None:
    p = argparse.ArgumentParser(
        description="把学习笔记 markdown 转成 roadmap.sh 风格的可交互 HTML"
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument("--batch", metavar="DIR", help="批量扫描目录，生成各 roadmap + index.html")
    g.add_argument("--serve", metavar="DIR", help="批量生成并启动本地服务（让 index 能读取实时进度）")
    p.add_argument("input", nargs="?", help="单文件模式：markdown 文件路径")
    p.add_argument("output", nargs="?", help="单文件模式：输出 html 路径（默认 <stem>-roadmap.html）")
    p.add_argument("--out", metavar="DIR", help="批量模式：index.html 输出目录（默认 = 扫描目录）")
    p.add_argument("--min-sections", type=int, default=3,
                   help="批量模式下判定为学习笔记的最小 ### 小节数（默认 3）")
    p.add_argument("--port", type=int, default=8000, help="--serve 端口（默认 8000）")
    p.add_argument("--shift", type=int, default=0, metavar="N",
                   help="把笔记里的 heading 层级整体平移 N 级再解析（默认 0）。"
                        "例：笔记用 H1/H2/H3 而非 H2/H3/H4 时用 --shift 1")
    args = p.parse_args()

    if args.batch or args.serve:
        root = Path(args.batch or args.serve).expanduser().resolve()
        if not root.is_dir():
            p.error(f"{root} 不是目录")
        out_dir = Path(args.out).expanduser().resolve() if args.out else root
        index_path = build_batch(root, out_dir, args.min_sections, shift=args.shift)
        if args.serve:
            serve(root, args.port, open_index=index_path)
        return

    if not args.input:
        p.error("需要指定输入文件，或使用 --batch / --serve")
    src = Path(args.input).expanduser().resolve()
    if not src.is_file():
        p.error(f"{src} 不存在")
    dst = Path(args.output).expanduser().resolve() if args.output \
        else src.with_name(f"{src.stem}-roadmap.html")

    # 先 parse 检查结构；异常时给诊断、退出码 2，不生成文件
    text = src.read_text(encoding="utf-8")
    data = parse(src, shift=args.shift)
    diag = diagnose(text, data["parts"])
    if diag is not None:
        severity, msg = diag
        print(msg, file=sys.stderr)
        # 退出码区分：0=成功，1=用法错（由 argparse 触发），2=输入结构问题
        sys.exit(2)

    dst.write_text(render_single(data, back_href=None), encoding="utf-8")
    shift_note = f" [shift={args.shift}]" if args.shift else ""
    print(f"✓ {src.name} → {dst.name}  ({len(data['parts'])} parts, {section_count(data)} sections){shift_note}")


if __name__ == "__main__":
    main()
