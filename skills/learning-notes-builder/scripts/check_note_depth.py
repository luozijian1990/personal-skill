#!/usr/bin/env python3
"""Flag learning-note H3 sections that are likely too thin to teach from."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


H3_RE = re.compile(r"^###\s+(.+?)\s*$")
H2_RE = re.compile(r"^##\s+")
H4_RE = re.compile(r"^####\s+")
SRC_RE = re.compile(r"^\s*<!--\s*src:")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)]\s+)")
SENTENCE_RE = re.compile(r"[。！？!?]+|[.]+(?=\s|$)")


@dataclass
class Section:
    title: str
    line: int
    body: list[str]


def parse_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None
    in_fence = False

    for line_no, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            if current is not None:
                current.body.append(line)
            continue

        if not in_fence:
            h3 = H3_RE.match(line)
            if h3 and not H4_RE.match(line):
                if current is not None:
                    sections.append(current)
                current = Section(h3.group(1), line_no, [])
                continue
            if H2_RE.match(line) and not line.startswith("###"):
                if current is not None:
                    sections.append(current)
                    current = None
                continue

        if current is not None:
            current.body.append(line)

    if current is not None:
        sections.append(current)
    return sections


def inspect(section: Section, min_lines: int, min_chars: int) -> list[str]:
    useful = [
        line
        for line in section.body
        if line.strip() and not SRC_RE.match(line)
    ]
    h4_groups: list[list[str]] = []
    current_h4: list[str] | None = None
    for line in section.body:
        if H4_RE.match(line):
            if current_h4 is not None:
                h4_groups.append(current_h4)
            current_h4 = []
        elif current_h4 is not None and line.strip() and not SRC_RE.match(line):
            current_h4.append(line)
    if current_h4 is not None:
        h4_groups.append(current_h4)

    def h4_is_substantive(lines: list[str]) -> bool:
        text = "".join(re.sub(r"\s+", "", line) for line in lines)
        artifacts = (
            sum(bool(FENCE_RE.match(line)) for line in lines) >= 2
            or sum(bool(TABLE_RE.match(line)) for line in lines) >= 2
            or sum(bool(LIST_RE.match(line)) for line in lines) >= 3
        )
        return len(lines) >= 3 or len(text) >= 50 or artifacts

    substantive_h4_count = sum(h4_is_substantive(group) for group in h4_groups)
    fence_count = sum(bool(FENCE_RE.match(line)) for line in useful)
    table_rows = sum(bool(TABLE_RE.match(line)) for line in useful)
    list_items = sum(bool(LIST_RE.match(line)) for line in useful)
    has_artifact = fence_count >= 2 or table_rows >= 2 or list_items >= 3

    prose_lines = [
        line.strip()
        for line in useful
        if not H4_RE.match(line)
        and not FENCE_RE.match(line)
        and not TABLE_RE.match(line)
        and not LIST_RE.match(line)
    ]
    prose = " ".join(prose_lines)
    content_lines = len(prose_lines)
    chars = len(re.sub(r"[`*_#>\[\](){}\s-]", "", prose))
    sentences = len(SENTENCE_RE.findall(prose))

    reasons: list[str] = []
    if not useful:
        reasons.append("无正文")
    elif substantive_h4_count < 2 and not has_artifact and sentences <= 1:
        reasons.append("只有一句或不足一句正文")
    if substantive_h4_count < 2 and not has_artifact and content_lines < min_lines and chars < min_chars:
        reasons.append(f"内容过薄 prose_lines={content_lines} prose_chars={chars}")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查学习笔记中疑似只有一句话或内容过薄的 H3。"
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--min-content-lines", type=int, default=4)
    parser.add_argument("--min-prose-chars", type=int, default=180)
    args = parser.parse_args()

    issue_count = 0
    section_count = 0
    for path in args.files:
        if not path.is_file():
            print(f"ERROR {path}: 文件不存在", file=sys.stderr)
            issue_count += 1
            continue
        sections = parse_sections(path.read_text(encoding="utf-8"))
        section_count += len(sections)
        for section in sections:
            reasons = inspect(
                section, args.min_content_lines, args.min_prose_chars
            )
            if reasons:
                issue_count += 1
                print(
                    f"THIN {path}:{section.line} {section.title} :: "
                    + "; ".join(reasons)
                )

    if issue_count:
        print(f"FAIL sections={section_count} thin={issue_count}")
        return 1
    print(f"PASS sections={section_count} thin=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
