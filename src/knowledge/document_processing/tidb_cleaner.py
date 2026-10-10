"""Registered deterministic cleaning rules for TiDB Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .link_resolver import resolve_markdown_links
from .schemas import MarkdownSection


PRESENTATION_SHORTCODE_PATTERNS = (
    re.compile(r'^\s*\{\{<\s*copyable(?:\s+"[^"]*")?\s*>\}\}\s*$', re.MULTILINE),
    re.compile(r'^\s*\{\{%\s*copyable(?:\s+"[^"]*")?\s*%\}\}\s*$', re.MULTILINE),
    re.compile(r'^\s*\{\{\{<\s*copyable(?:\s+"[^"]*")?\s*>\}\}\s*$', re.MULTILINE),
)
KNOWN_INLINE_SHORTCODES = (
    re.compile(r"\{\{<\s*tag\s+([^>]+)>\}\}"),
    re.compile(r"\{\{%\s*tag\s+([^%]+)%\}\}"),
)
ANY_SHORTCODE_RE = re.compile(r"\{\{[%<].*?[>%]\}\}")
LOCALIZATION_COMMENT_RE = re.compile(r"<!--\s*(?:TRANSLATION|LOCALIZATION)[\s\S]*?-->", re.IGNORECASE)
MARKDOWNLINT_COMMENT_RE = re.compile(r"^\s*<!--\s*markdownlint-[\s\S]*?-->\s*$", re.IGNORECASE | re.MULTILINE)
FULL_LINE_TAG_RE = re.compile(r"^\s*</?([A-Z][A-Za-z0-9]*)(?:\s[^>]*)?/?>\s*$")
SPAN_RE = re.compile(r"</?span(?:\s[^>]*)?>", re.IGNORECASE)
STRUCTURAL_TAGS = frozenset({
    "CustomContent", "SimpleTab", "SimpleTabs", "Tabs", "Tab", "DevToolGroup",
    "DevToolCard", "DevLangAccordion", "LearningPath", "LearningPathContainer",
    "DocHomeContainer", "DocHomeCardContainer", "DocHomeSection", "IntroHero",
})
PRESENTATION_SELF_CLOSING_TAGS = frozenset({"MDSvgIcon", "EmailSubscriptionWrapper", "IntroHeroVideo"})
ADMONITION_TAGS = frozenset({"Note", "Warning", "Important", "Caution"})
FENCE_LINE_RE = re.compile(r"^[ \t]{0,4}(`{3,}|~{3,})([^\r\n]*)$")


@dataclass(frozen=True)
class CleanedSection:
    heading_path: tuple[str, ...]
    source_line_range: tuple[int, int]
    content: str
    applied_rules: tuple[str, ...]


def _remove_registered_shortcodes(text: str, source_file: str, heading_path: str) -> tuple[str, list[str]]:
    rules: list[str] = []
    for pattern in PRESENTATION_SHORTCODE_PATTERNS:
        replaced = pattern.sub("", text)
        if replaced != text:
            rules.append("remove_presentation_copyable_shortcode")
            text = replaced
    for pattern in KNOWN_INLINE_SHORTCODES:
        replaced = pattern.sub(lambda match: match.group(1).strip().strip('"\''), text)
        if replaced != text:
            rules.append("preserve_inline_shortcode_text")
            text = replaced
    unknown = ANY_SHORTCODE_RE.findall(text)
    if unknown:
        raise ValueError(
            f"Unsupported TiDB shortcode: source_file={source_file!r}, "
            f"heading_path={heading_path!r}, constructs={unknown!r}"
        )
    return text, rules


def _transform_tag_line(line: str, source_file: str, heading_path: str) -> tuple[str, str | None]:
    match = FULL_LINE_TAG_RE.match(line.rstrip("\r\n"))
    if not match:
        return line, None
    tag = match.group(1)
    stripped = line.strip()
    closing = stripped.startswith("</")
    self_closing = stripped.endswith("/>")
    if tag in ADMONITION_TAGS:
        if closing:
            return "", "convert_admonition_container"
        return f"> **{tag}:**\n>\n", "convert_admonition_container"
    if tag in PRESENTATION_SELF_CLOSING_TAGS and self_closing:
        return "", "remove_presentation_component"
    if tag in STRUCTURAL_TAGS:
        if closing:
            return "", "unwrap_navigation_container"
        flattened = {
            key: double_quoted or single_quoted
            for key, double_quoted, single_quoted in re.findall(
                r"([A-Za-z][A-Za-z0-9]*)=(?:\"([^\"]*)\"|'([^']*)')",
                stripped,
            )
        }
        label = flattened.get("label") or flattened.get("title")
        href = flattened.get("href") or flattened.get("docLink")
        content = flattened.get("content")
        pieces = []
        if label:
            pieces.append(f"[{label}]({href})" if href else label)
        if content:
            pieces.append(content)
        return ("\n".join(pieces) + "\n" if pieces else ""), "unwrap_navigation_container"
    raise ValueError(
        f"Unsupported TiDB HTML/MDX container: source_file={source_file!r}, "
        f"heading_path={heading_path!r}, construct={stripped!r}"
    )


def _clean_outside_fences(text: str, transform) -> tuple[str, list[str]]:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    rules: list[str] = []
    marker: tuple[str, int] | None = None
    for line in lines:
        fence = FENCE_LINE_RE.match(line)
        if marker is not None:
            output.append(line)
            if (
                fence
                and fence.group(1)[0] == marker[0]
                and len(fence.group(1)) >= marker[1]
                and not fence.group(2).strip()
            ):
                marker = None
            continue
        if fence:
            marker = (fence.group(1)[0], len(fence.group(1)))
            output.append(line)
            continue
        replacement, rule = transform(line)
        output.append(replacement)
        if rule:
            rules.append(rule)
    return "".join(output), rules


def _normalize_blank_lines_outside_fences(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    marker: tuple[str, int] | None = None
    blank_count = 0
    for line in lines:
        fence = FENCE_LINE_RE.match(line)
        if marker is not None:
            output.append(line)
            if (
                fence
                and fence.group(1)[0] == marker[0]
                and len(fence.group(1)) >= marker[1]
                and not fence.group(2).strip()
            ):
                marker = None
            continue
        if fence:
            marker = (fence.group(1)[0], len(fence.group(1)))
            blank_count = 0
            output.append(line)
            continue
        if not line.strip():
            blank_count += 1
            if blank_count <= 1:
                output.append(line)
            continue
        blank_count = 0
        output.append(line)
    return "".join(output).strip("\n") + "\n"


def clean_section(
    section: MarkdownSection,
    source_file: str,
    website_base_url: str,
) -> CleanedSection:
    heading_path = section.heading_path_text
    normalized, rules = clean_markdown_text(
        section.text,
        source_file,
        heading_path,
        website_base_url,
    )
    return CleanedSection(
        heading_path=section.heading_path,
        source_line_range=(section.start_line, section.end_line),
        content=normalized,
        applied_rules=rules,
    )


def clean_markdown_text(
    source_text: str,
    source_file: str,
    heading_path: str,
    website_base_url: str,
) -> tuple[str, tuple[str, ...]]:
    def clean_shortcodes(value: str) -> tuple[str, str | None]:
        replacement, applied = _remove_registered_shortcodes(value, source_file, heading_path)
        return replacement, "remove_registered_shortcode" if applied else None

    text, rules = _clean_outside_fences(source_text, clean_shortcodes)
    localized = LOCALIZATION_COMMENT_RE.sub("", text)
    if localized != text:
        rules.append("remove_localization_comment")
        text = localized
    lint_cleaned = MARKDOWNLINT_COMMENT_RE.sub("", text)
    if lint_cleaned != text:
        rules.append("remove_markdownlint_comment")
        text = lint_cleaned
    text, tag_rules = _clean_outside_fences(
        text,
        lambda value: _transform_tag_line(value, source_file, heading_path),
    )
    rules.extend(tag_rules)
    span_cleaned = SPAN_RE.sub("", text)
    if span_cleaned != text:
        rules.append("unwrap_inline_span")
        text = span_cleaned
    def clean_links(value: str) -> tuple[str, str | None]:
        replacement = resolve_markdown_links(value, source_file, website_base_url)
        return replacement, "resolve_relative_documentation_links" if replacement != value else None

    resolved, link_rules = _clean_outside_fences(text, clean_links)
    rules.extend(link_rules)
    if resolved != text:
        text = resolved
    normalized = _normalize_blank_lines_outside_fences(text)
    if normalized != text:
        rules.append("normalize_blank_lines")
    return normalized, tuple(dict.fromkeys(rules))


def clean_markdown_sections(
    sections: tuple[MarkdownSection, ...],
    source_file: str,
    website_base_url: str,
) -> tuple[CleanedSection, ...]:
    return tuple(clean_section(section, source_file, website_base_url) for section in sections)
