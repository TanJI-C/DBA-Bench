"""Strict schemas shared by TiDB document processing and materialization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


KNOWLEDGE_CATEGORIES = frozenset({
    "architecture", "configuration", "observability", "diagnosis", "operation",
    "performance", "recovery", "data_pipeline", "reference", "release",
})
COMPONENTS = frozenset({
    "tidb", "tikv", "pd", "tiflash", "ticdc", "tiproxy", "br", "lightning",
    "dumpling", "dm", "tiup", "dashboard", "operator", "cloud", "sql",
    "ecosystem", "shared",
})
DOCUMENT_SCOPES = frozenset({
    "self_managed", "cloud", "kubernetes", "developer", "shared", "repository_internal",
})
RETRIEVAL_SCOPES = frozenset({
    "self_managed", "cloud", "kubernetes", "developer", "shared", "all",
})


@dataclass(frozen=True)
class MarkdownCodeBlock:
    start_line: int
    end_line: int
    language: str
    text: str


@dataclass(frozen=True)
class MarkdownConstruct:
    kind: str
    start_line: int
    end_line: int
    text: str


@dataclass(frozen=True)
class MarkdownSection:
    heading_path: tuple[str, ...]
    level: int
    start_line: int
    end_line: int
    text: str
    content_sha256: str
    code_blocks: tuple[MarkdownCodeBlock, ...]
    tables: tuple[MarkdownConstruct, ...]
    lists: tuple[MarkdownConstruct, ...]
    admonitions: tuple[MarkdownConstruct, ...]
    links: tuple[str, ...]
    images: tuple[str, ...]
    shortcodes: tuple[str, ...]
    containers: tuple[str, ...]

    @property
    def heading_path_text(self) -> str:
        return " > ".join(self.heading_path)


@dataclass(frozen=True)
class MarkdownDocument:
    source_file: str
    title: str
    summary: str | None
    frontmatter: dict[str, object]
    sections: tuple[MarkdownSection, ...]
    source_sha256: str


@dataclass(frozen=True)
class SplitChunk:
    unit_ids: tuple[str, ...]
    heading_paths: tuple[str, ...]
    title: str
    primary_category: str
    primary_component: str
    related_components: tuple[str, ...]
    deployment_scope: str
    topic_tags: tuple[str, ...]
    classification_reason: str
    needs_human_review: bool


@dataclass(frozen=True)
class SplitPlan:
    source_file: str
    chunks: tuple[SplitChunk, ...]


@dataclass(frozen=True)
class RetrievalEnrichment:
    use_when: str
    retrieval_keywords: tuple[str, ...]
    follow_up: str
    classification_note: str


@dataclass(frozen=True)
class ProcessingUnit:
    unit_id: str
    heading_path: str
    start_line: int
    end_line: int
    text: str
    token_count: int
    indivisible: bool


def dataclass_dict(value: Any) -> dict[str, Any]:
    return asdict(value)
