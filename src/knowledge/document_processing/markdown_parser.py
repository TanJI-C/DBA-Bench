"""Deterministic line-oriented Markdown section parser.

The parser deliberately does not repair malformed Markdown. An unterminated fence,
front matter block, or HTML comment is a source-processing failure.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .schemas import (
    MarkdownCodeBlock,
    MarkdownConstruct,
    MarkdownDocument,
    MarkdownSection,
)
from .source_manifest import sha256_bytes


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]{0,4}(`{3,}|~{3,})([^\r\n]*)$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SHORTCODE_RE = re.compile(r"\{\{[%<].*?[>%]\}\}")
CONTAINER_RE = re.compile(r"</?[A-Z][A-Za-z0-9]*(?:\s[^>]*)?/?>|<div(?:\s[^>]*)?>|</div>")
LIST_RE = re.compile(r"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+")
ADMONITION_RE = re.compile(
    r"^[ \t]*(?:>[ \t]*)?(?:\*\*)?(?:Note|Warning|Caution|Important|Tip)(?:\*\*)?[ \t]*[:.]?",
    re.IGNORECASE,
)


def _frontmatter(lines: list[str], source_file: str) -> tuple[dict[str, object], int]:
    if not lines or lines[0].strip() != "---":
        return {}, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw = "".join(lines[1:index])
            payload = yaml.safe_load(raw) or {}
            if not isinstance(payload, dict):
                raise ValueError(
                    f"YAML front matter must be an object: source_file={source_file!r}, "
                    f"type={type(payload).__name__}"
                )
            return payload, index + 1
    raise ValueError(f"Unterminated YAML front matter: source_file={source_file!r}")


def _scan_fences(lines: list[str], source_file: str) -> tuple[set[int], tuple[MarkdownCodeBlock, ...]]:
    fenced_lines: set[int] = set()
    blocks: list[MarkdownCodeBlock] = []
    opening: tuple[int, str, str] | None = None
    for index, line in enumerate(lines):
        match = FENCE_RE.match(line.rstrip("\r\n"))
        if opening is None:
            if match:
                marker = match.group(1)
                opening = (index, marker[0], marker)
                fenced_lines.add(index)
            continue
        fenced_lines.add(index)
        start, marker_char, marker = opening
        if (
            match
            and match.group(1)[0] == marker_char
            and len(match.group(1)) >= len(marker)
            and not match.group(2).strip()
        ):
            info = lines[start].strip()[len(marker):].strip()
            blocks.append(MarkdownCodeBlock(
                start_line=start + 1,
                end_line=index + 1,
                language=info.split()[0] if info else "",
                text="".join(lines[start:index + 1]),
            ))
            opening = None
    if opening is not None:
        raise ValueError(
            f"Unterminated fenced code block: source_file={source_file!r}, "
            f"start_line={opening[0] + 1}, marker={opening[2]!r}"
        )
    return fenced_lines, tuple(blocks)


def _contiguous_constructs(
    lines: list[str], start: int, end: int, predicate, kind: str,
) -> tuple[MarkdownConstruct, ...]:
    constructs: list[MarkdownConstruct] = []
    index = start
    while index < end:
        if not predicate(lines[index]):
            index += 1
            continue
        construct_start = index
        index += 1
        while index < end and (predicate(lines[index]) or not lines[index].strip()):
            index += 1
        constructs.append(MarkdownConstruct(
            kind=kind,
            start_line=construct_start + 1,
            end_line=index,
            text="".join(lines[construct_start:index]),
        ))
    return tuple(constructs)


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _section(
    lines: list[str], start: int, end: int, heading_path: tuple[str, ...], level: int,
    code_blocks: tuple[MarkdownCodeBlock, ...],
) -> MarkdownSection:
    text = "".join(lines[start:end])
    start_line, end_line = start + 1, end
    section_blocks = tuple(
        block for block in code_blocks
        if start_line <= block.start_line and block.end_line <= end_line
    )
    links = tuple(match.group(1) for match in LINK_RE.finditer(text))
    images = tuple(match.group(1) for match in IMAGE_RE.finditer(text))
    return MarkdownSection(
        heading_path=heading_path,
        level=level,
        start_line=start_line,
        end_line=end_line,
        text=text,
        content_sha256=sha256_bytes(text.encode("utf-8")),
        code_blocks=section_blocks,
        tables=_contiguous_constructs(lines, start, end, _is_table_line, "table"),
        lists=_contiguous_constructs(lines, start, end, lambda line: bool(LIST_RE.match(line)), "list"),
        admonitions=_contiguous_constructs(lines, start, end, lambda line: bool(ADMONITION_RE.match(line)), "admonition"),
        links=links,
        images=images,
        shortcodes=tuple(match.group(0) for match in SHORTCODE_RE.finditer(text)),
        containers=tuple(match.group(0) for match in CONTAINER_RE.finditer(text)),
    )


def parse_markdown_text(
    text: str,
    source_file: str,
    source_sha256: str | None = None,
) -> MarkdownDocument:
    source_bytes = text.encode("utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines(keepends=True)
    frontmatter, body_start = _frontmatter(lines, source_file)
    fenced_lines, code_blocks = _scan_fences(lines, source_file)
    headings: list[tuple[int, int, str, tuple[str, ...]]] = []
    stack: list[tuple[int, str]] = []
    for index in range(body_start, len(lines)):
        if index in fenced_lines:
            continue
        match = HEADING_RE.match(lines[index].rstrip("\r\n"))
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        headings.append((index, level, title, tuple(item[1] for item in stack)))
    if not headings:
        raise ValueError(f"Markdown document has no headings: source_file={source_file!r}")
    paths = [heading[3] for heading in headings]
    duplicates = sorted({path for path in paths if paths.count(path) > 1})
    if duplicates:
        raise ValueError(
            f"Duplicate heading paths are ambiguous: source_file={source_file!r}, "
            f"heading_paths={[' > '.join(path) for path in duplicates]!r}"
        )
    sections = tuple(
        _section(
            lines,
            body_start if index == 0 else heading[0],
            headings[index + 1][0] if index + 1 < len(headings) else len(lines),
            heading[3],
            heading[1],
            code_blocks,
        )
        for index, heading in enumerate(headings)
    )
    title = str(frontmatter.get("title") or headings[0][2]).strip()
    summary_value = frontmatter.get("summary")
    summary = str(summary_value).strip() if summary_value is not None else None
    return MarkdownDocument(
        source_file=source_file,
        title=title,
        summary=summary,
        frontmatter=frontmatter,
        sections=sections,
        source_sha256=source_sha256 or sha256_bytes(source_bytes),
    )


def parse_markdown_document(path: Path, source_root: Path | None = None) -> MarkdownDocument:
    source_file = path.relative_to(source_root).as_posix() if source_root else path.as_posix()
    try:
        source_bytes = path.read_bytes()
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Markdown is not UTF-8: source_file={source_file!r}, error={exc}") from exc
    return parse_markdown_text(
        text,
        source_file,
        source_sha256=sha256_bytes(source_bytes),
    )
