#!/usr/bin/env python3
"""Scan a folder of source materials and print a starter outline + meta.

输出格式（YAML-ish + Markdown），方便上游 Claude 直接吃：
  - 头部 meta：主题猜测、读者建议、推荐输出文件名
  - 主体大纲：按一级子目录分组，每个文件一行（含编号前缀剥离后的清洗标题 + 字节数 + 首段预览）

设计原则：不做语义判断，只做"机械可靠"的扫描和清洗，把判断留给 LLM。
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

# 收录的源文件扩展（按优先级）
EXTS = {".md", ".txt", ".html", ".htm", ".rst"}

# 噪音文件名（直接跳过）
SKIP_NAMES = re.compile(r"^(?:README|CHANGELOG|LICENSE|\.DS_Store|TODO|index)\b", re.IGNORECASE)


def natural_key(s: str) -> list:
    """让 01- / 1- / 10- 之类正确排序。"""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def strip_prefix(name: str) -> str:
    """剥离编号前缀: '01--xxx', '01-xxx', '1. xxx', '【01】xxx' 等。"""
    stem = Path(name).stem
    # 去掉常见编号前缀
    cleaned = re.sub(r"^[\s\[【\(（]*\d+[\s.\-_、）)\]】]+", "", stem)
    # 折叠多余的破折号和下划线
    cleaned = re.sub(r"[\-_]{2,}", " ", cleaned).strip(" -_·.")
    return cleaned or stem


def preview(path: Path, limit: int = 160) -> str:
    """读首段文本作为预览，剥简单 HTML / markdown 标记。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    # 去 HTML 标签
    text = re.sub(r"<[^>]+>", " ", text)
    # 去 markdown 标题、引用、列表符号
    text = re.sub(r"^[#>*\-\d.\s]+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def collect(root: Path) -> tuple[dict[str, list[Path]], list[Path]]:
    """返回 (按一级子目录分组的文件, 根目录下的散文件)。"""
    grouped: dict[str, list[Path]] = {}
    loose: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in EXTS:
            continue
        if SKIP_NAMES.match(p.name):
            continue
        # 跳过隐藏目录
        rel = p.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if any(seg in {"node_modules", "venv", ".venv", "dist", "__pycache__"} for seg in rel.parts):
            continue
        if len(rel.parts) == 1:
            loose.append(p)
        else:
            grouped.setdefault(rel.parts[0], []).append(p)
    # 自然排序
    for k in grouped:
        grouped[k].sort(key=lambda p: natural_key(p.name))
    loose.sort(key=lambda p: natural_key(p.name))
    return grouped, loose


def render(root: Path, grouped: dict[str, list[Path]], loose: list[Path]) -> str:
    topic = strip_prefix(root.name) or root.name
    total = sum(len(v) for v in grouped.values()) + len(loose)
    chapter_count = len(grouped) + (1 if loose else 0)

    out: list[str] = []
    out.append("---")
    out.append(f"topic_guess: {topic}")
    out.append(f"source_root: {root}")
    out.append(f"total_files: {total}")
    out.append(f"chapter_count: {chapter_count}")
    out.append(f"suggested_output: {topic}_Learning_Notes.md")
    out.append(f"suggested_outline: {topic}_Learning_Notes_Outline.md")
    out.append("---")
    out.append("")
    out.append(f"# {topic} 学习笔记 · 自动扫描大纲（起点版）")
    out.append("")
    out.append("> 这是脚本机械扫描的起点大纲。上游 Claude 会基于此重写章节 / 小节名，")
    out.append("> 并把每节挂回对应的源文件（HTML 注释方式）。请勿直接用此文件当作终稿大纲。")
    out.append("")

    def render_group(title: str, files: list[Path]) -> None:
        out.append(f"## {strip_prefix(title)}")
        out.append(f"<!-- group_dir: {title} -->")
        out.append("")
        for f in files:
            rel = f.relative_to(root)
            size_kb = f.stat().st_size / 1024
            out.append(f"- **{strip_prefix(f.name)}**  `[{rel}]`  ({size_kb:.1f} KB)")
            prev = preview(f)
            if prev:
                out.append(f"  - 预览：{prev}")
        out.append("")

    # 先输出分组，再输出散文件
    for chapter, files in sorted(grouped.items(), key=lambda kv: natural_key(kv[0])):
        render_group(chapter, files)
    if loose:
        render_group("（根目录散文件）", loose)

    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description="扫描材料目录，输出起点大纲（供 LLM 改写）")
    p.add_argument("dir", help="材料根目录")
    p.add_argument("--json", action="store_true", help="改为输出 JSON，方便程序化处理")
    args = p.parse_args()

    root = Path(args.dir).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"错误：{root} 不是目录")

    grouped, loose = collect(root)
    if not grouped and not loose:
        sys.exit(f"错误：{root} 下没有发现可识别的源文件（扩展名：{sorted(EXTS)}）")

    if args.json:
        data = {
            "topic_guess": strip_prefix(root.name) or root.name,
            "source_root": str(root),
            "total_files": sum(len(v) for v in grouped.values()) + len(loose),
            "chapters": [
                {
                    "title": strip_prefix(name),
                    "dir": name,
                    "files": [
                        {
                            "path": str(f.relative_to(root)),
                            "title": strip_prefix(f.name),
                            "size_bytes": f.stat().st_size,
                            "preview": preview(f),
                        }
                        for f in files
                    ],
                }
                for name, files in sorted(grouped.items(), key=lambda kv: natural_key(kv[0]))
            ],
            "loose_files": [
                {"path": str(f.relative_to(root)), "title": strip_prefix(f.name),
                 "size_bytes": f.stat().st_size, "preview": preview(f)}
                for f in loose
            ],
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render(root, grouped, loose))


if __name__ == "__main__":
    main()
