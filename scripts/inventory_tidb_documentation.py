#!/usr/bin/env python3
"""Inventory every Markdown file in a pinned TiDB source snapshot."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT, resolve_project_path  # noqa: E402
from src.knowledge.document_processing.schemas import DOCUMENT_SCOPES  # noqa: E402
from src.knowledge.document_processing.source_manifest import (  # noqa: E402
    SOURCE_MANIFEST_FILENAME,
    load_json,
    verify_source_manifest,
    write_json,
)


PROJECT_ROOT = REPOSITORY_ROOT


LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
ROOT_EXCLUSIONS = {
    "README.md": "repository_maintenance_document",
    "CONTRIBUTING.md": "repository_maintenance_document",
    "CODE_OF_CONDUCT.md": "repository_maintenance_document",
    "SECURITY.md": "repository_maintenance_document",
    "LICENSE.md": "license_document",
    "_docHome.md": "site_navigation_document",
    "_index.md": "site_navigation_document",
    "keywords.md": "site_generated_dynamic_document",
    "resources/markdownlint-rules.md": "repository_maintenance_document",
    "tidb-cloud/_index.md": "site_navigation_document",
}


def frontmatter(path: Path) -> tuple[str | None, str | None]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            payload = yaml.safe_load("\n".join(lines[1:index])) or {}
            if not isinstance(payload, dict):
                raise ValueError(f"Front matter must be an object: source_file={path}")
            title = payload.get("title")
            summary = payload.get("summary")
            return (
                str(title).strip() if title is not None else None,
                str(summary).strip() if summary is not None else None,
            )
    raise ValueError(f"Unterminated front matter: source_file={path}")


def toc_files(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.rglob("*.md") if "toc" in path.stem.casefold())


def toc_membership(source_dir: Path) -> dict[str, list[str]]:
    membership: dict[str, list[str]] = {}
    for toc in toc_files(source_dir):
        toc_relative = toc.relative_to(source_dir).as_posix()
        for target in LINK_RE.findall(toc.read_text(encoding="utf-8")):
            parsed = urlsplit(unquote(target))
            if parsed.scheme or target.startswith(("#", "mailto:")):
                continue
            path = parsed.path
            if not path.casefold().endswith((".md", ".markdown")):
                continue
            resolved = (
                posixpath.normpath(path.lstrip("/"))
                if path.startswith("/")
                else posixpath.normpath(
                    posixpath.join(PurePosixPath(toc_relative).parent.as_posix(), path)
                )
            )
            resolved_path = source_dir / resolved
            if not resolved_path.is_file():
                raise FileNotFoundError(
                    f"TiDB TOC link does not resolve: toc={toc_relative!r}, target={target!r}, "
                    f"resolved={resolved!r}"
                )
            membership.setdefault(resolved, []).append(toc_relative)
    return {path: sorted(set(tocs)) for path, tocs in membership.items()}


def classify_scope(source_file: str) -> str:
    lowered = source_file.casefold()
    if source_file.startswith(".github/"):
        return "repository_internal"
    if any(token in lowered for token in ("tidb-cloud", "cloud/", "-cloud", "cloud-")):
        return "cloud"
    if any(token in lowered for token in ("kubernetes", "operator/", "tidb-operator")):
        return "kubernetes"
    if any(token in lowered for token in ("developer-guide", "dev-guide", "contribute", "development")):
        return "developer"
    if any(token in lowered for token in ("glossary", "overview", "faq", "release-notes")):
        return "shared"
    return "self_managed"


def exclusion(source_file: str) -> str | None:
    if source_file.startswith(".github/"):
        return "repository_maintenance_document"
    if source_file in ROOT_EXCLUSIONS:
        return ROOT_EXCLUSIONS[source_file]
    name = PurePosixPath(source_file).name.casefold()
    if "toc" in PurePosixPath(source_file).stem.casefold():
        return "navigation_document"
    if name in {"license.md", "readme.md"} and "/" not in source_file:
        return "repository_maintenance_document"
    return None


def build_inventory(source_dir: Path) -> list[dict]:
    manifest = verify_source_manifest(source_dir)
    source_records = {
        record["path"]: record
        for record in manifest["files"]
        if record["kind"] == "markdown"
    }
    membership = toc_membership(source_dir)
    records: list[dict] = []
    for source_file, source_record in sorted(source_records.items()):
        title, summary = frontmatter(source_dir / source_file)
        reason = exclusion(source_file)
        scope = "repository_internal" if reason == "repository_maintenance_document" else classify_scope(source_file)
        if scope not in DOCUMENT_SCOPES:
            raise ValueError(f"Unknown document scope: source_file={source_file!r}, scope={scope!r}")
        records.append({
            "source_file": source_file,
            "source_sha256": source_record["sha256"],
            "frontmatter_title": title,
            "frontmatter_summary": summary,
            "toc_membership": membership.get(source_file, []),
            "document_scope": scope,
            "processing_status": "excluded" if reason else "included",
            "exclusion_reason": reason,
        })
    if len(records) != len(source_records):
        raise RuntimeError(
            f"Inventory completeness failure: markdown_count={len(source_records)}, inventory_count={len(records)}"
        )
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("knowledge/tidb_src"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("knowledge/tidb/mappings/tidb81_document_inventory.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = resolve_project_path(args.source_dir)
    load_json(source_dir / SOURCE_MANIFEST_FILENAME)
    records = build_inventory(source_dir)
    output_path = resolve_project_path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, records)
    included = sum(record["processing_status"] == "included" for record in records)
    excluded = len(records) - included
    print(json.dumps({
        "status": "success",
        "total_markdown": len(records),
        "included": included,
        "excluded": excluded,
        "output": str(output_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
