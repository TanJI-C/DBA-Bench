"""TiDB 8.1 unified knowledge base configuration."""

from __future__ import annotations

import os
import hashlib
import json
import re
from pathlib import Path

from src.project_paths import SHARED_REPOSITORY_ROOT, resolve_shared_project_path

from .document_processing.schemas import COMPONENTS, KNOWLEDGE_CATEGORIES, RETRIEVAL_SCOPES
from .document_processing.markdown_parser import parse_markdown_document
from .document_processing.tidb_cleaner import clean_markdown_sections
from .markdown_knowledge_base import (
    DEFAULT_EMBED_MODEL,
    KnowledgeRecord,
    MarkdownKnowledgeBase,
)


DEFAULT_COLLECTION_NAME = "tidb81_unified_docs"
DEFAULT_GENERAL_SOURCE_FILE = Path("knowledge/tidb_src")
DEFAULT_HIERARCHICAL_SOURCE_FILE = Path(
    "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
)
DEFAULT_GENERAL_SQLITE_DIR = Path("data/knowledge_bases/tidb81_docs")
DEFAULT_GENERAL_CHROMA_DIR = Path("data/knowledge_bases/tidb81_chroma")
DEFAULT_HIERARCHICAL_SQLITE_DIR = Path("data/knowledge_bases/tidb81_unified_docs")
DEFAULT_HIERARCHICAL_CHROMA_DIR = Path("data/knowledge_bases/tidb81_unified_chroma")


def normalize_knowledge_mode(mode: str) -> str:
    normalized = str(mode).strip().casefold()
    if normalized not in {"general", "hierarchical"}:
        raise ValueError(
            f"Unsupported TiDB knowledge mode: mode={mode!r}, "
            "supported=['general', 'hierarchical']"
        )
    return normalized


def default_source_file(mode: str) -> Path:
    normalized = normalize_knowledge_mode(mode)
    environment_name = (
        "AIOPS_TIDB_HIERARCHICAL_KB_SOURCE"
        if normalized == "hierarchical"
        else "AIOPS_TIDB_GENERAL_KB_SOURCE"
    )
    default = (
        DEFAULT_HIERARCHICAL_SOURCE_FILE
        if normalized == "hierarchical"
        else DEFAULT_GENERAL_SOURCE_FILE
    )
    return resolve_shared_project_path(os.environ.get(environment_name, default))


def default_persist_dir(backend: str, mode: str) -> Path:
    normalized = normalize_knowledge_mode(mode)
    if backend not in {"sqlite", "chroma"}:
        raise ValueError(f"Unsupported TiDB knowledge backend: backend={backend!r}")
    key = f"AIOPS_TIDB_{normalized.upper()}_KB_{backend.upper()}_DIR"
    defaults = {
        ("general", "sqlite"): DEFAULT_GENERAL_SQLITE_DIR,
        ("general", "chroma"): DEFAULT_GENERAL_CHROMA_DIR,
        ("hierarchical", "sqlite"): DEFAULT_HIERARCHICAL_SQLITE_DIR,
        ("hierarchical", "chroma"): DEFAULT_HIERARCHICAL_CHROMA_DIR,
    }
    return resolve_shared_project_path(os.environ.get(key, defaults[(normalized, backend)]))


class TiDBKnowledgeBase(MarkdownKnowledgeBase):
    def __init__(
        self,
        *,
        persist_dir: str | os.PathLike[str] | None = None,
        collection_name: str | None = None,
        embed_model_name: str | None = None,
        embed_device: str | None = None,
        embed_batch_size: int | None = None,
        embed_workers: int | None = None,
        backend: str | None = None,
        knowledge_base_mode: str = "hierarchical",
        source_file: str | os.PathLike[str] | None = None,
    ):
        mode = normalize_knowledge_mode(knowledge_base_mode)
        selected_backend = (
            backend or os.environ.get("AIOPS_TIDB_KB_BACKEND", "chroma")
        ).casefold()
        super().__init__(
            persist_dir=persist_dir or default_persist_dir(selected_backend, mode),
            collection_name=collection_name
            or os.environ.get("AIOPS_TIDB_KB_COLLECTION", DEFAULT_COLLECTION_NAME),
            backend=selected_backend,
            knowledge_base_mode=mode,
            default_source_file=source_file or default_source_file(mode),
            valid_kb_types=KNOWLEDGE_CATEGORIES,
            valid_components=COMPONENTS,
            valid_scopes=RETRIEVAL_SCOPES,
            build_script="scripts/build_tidb_knowledge_base.py",
            embed_model_name=embed_model_name
            or os.environ.get("AIOPS_TIDB_KB_EMBED_MODEL", DEFAULT_EMBED_MODEL),
            embed_device=embed_device
            or os.environ.get("AIOPS_TIDB_KB_EMBED_DEVICE", "cuda"),
            embed_batch_size=embed_batch_size
            or int(os.environ.get("AIOPS_TIDB_KB_EMBED_BATCH_SIZE", "1")),
            embed_workers=embed_workers
            or int(os.environ.get("AIOPS_TIDB_KB_EMBED_WORKERS", "1")),
            product_label="TiDB 8.1 unified knowledge base",
        )

    def _load_records(self, source_path: Path) -> list[KnowledgeRecord]:
        if not source_path.is_dir():
            return super()._load_records(source_path)
        inventory_path = SHARED_REPOSITORY_ROOT / "knowledge" / "tidb" / "mappings" / "tidb81_document_inventory.json"
        if not inventory_path.is_file():
            raise FileNotFoundError(
                f"TiDB document inventory is required for general knowledge indexing: "
                f"inventory={inventory_path}, source_dir={source_path}"
            )
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        included = [record for record in inventory if record["processing_status"] == "included"]
        lock = json.loads((source_path / ".source-lock.json").read_text(encoding="utf-8"))
        records = []
        for inventory_record in included:
            document = parse_markdown_document(
                source_path / inventory_record["source_file"],
                source_path,
            )
            if document.source_sha256 != inventory_record["source_sha256"]:
                raise ValueError(
                    f"TiDB general source hash mismatch: source_file={document.source_file!r}, "
                    f"inventory={inventory_record['source_sha256']!r}, actual={document.source_sha256!r}"
                )
            cleaned = clean_markdown_sections(
                document.sections,
                document.source_file,
                lock["website_base_url"],
            )
            page = document.source_file.rsplit(".", 1)[0]
            for section, cleaned_section in zip(document.sections, cleaned):
                content = cleaned_section.content
                content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                anchor = re.sub(
                    r"[^a-z0-9]+",
                    "-",
                    section.heading_path[-1].casefold(),
                ).strip("-") or "section"
                identity = hashlib.sha256(
                    f"{lock['commit']}\n{document.source_file}\n{section.heading_path_text}\n{content_hash}".encode()
                ).hexdigest()[:12]
                records.append(KnowledgeRecord(
                    chunk_id=f"tidb81_general_{identity}",
                    source_id=f"tidb-docs-8.1:{document.source_file}#{anchor}",
                    title=section.heading_path[-1],
                    kb_type="reference",
                    component="shared",
                    related_components=(),
                    source_scope=inventory_record["document_scope"],
                    topic_tags=(),
                    version="8.1",
                    source_file=document.source_file,
                    heading_path=section.heading_path_text,
                    source_url=f"{lock['website_base_url'].rstrip('/')}/{page}#{anchor}",
                    pinned_source_url=f"{lock['github_blob_base_url'].rstrip('/')}/{document.source_file}",
                    use_when=section.heading_path_text,
                    retrieval_keywords=section.heading_path,
                    follow_up="",
                    content=content,
                    content_sha256=content_hash,
                ))
        if not records:
            raise ValueError(f"TiDB general source produced no section records: source_dir={source_path}")
        return records
