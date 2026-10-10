"""Resolve TiDB documentation links without changing linked text."""

from __future__ import annotations

import posixpath
import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit


MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)([^)]*\))")


def documentation_url(source_file: str, target: str, website_base_url: str) -> str:
    parsed = urlsplit(target)
    if parsed.scheme or target.startswith(("#", "mailto:", "tel:")):
        return target
    if not parsed.path.casefold().endswith((".md", ".markdown")):
        return target
    parent = PurePosixPath(source_file).parent.as_posix()
    resolved = (
        posixpath.normpath(parsed.path.lstrip("/"))
        if parsed.path.startswith("/")
        else posixpath.normpath(posixpath.join(parent, parsed.path))
    )
    if resolved.startswith("../"):
        raise ValueError(
            f"Relative documentation link escapes source root: source_file={source_file!r}, "
            f"target={target!r}, resolved={resolved!r}"
        )
    page = resolved.rsplit(".", 1)[0]
    if page.endswith("/README"):
        page = page[:-len("/README")]
    url = f"{website_base_url.rstrip('/')}/{page.lstrip('/')}"
    return urlunsplit(("https", urlsplit(url).netloc, urlsplit(url).path, parsed.query, parsed.fragment))


def resolve_markdown_links(text: str, source_file: str, website_base_url: str) -> str:
    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        if prefix.startswith("!["):
            return match.group(0)
        return prefix + documentation_url(source_file, target, website_base_url) + suffix

    return MARKDOWN_LINK_RE.sub(replace, text)
