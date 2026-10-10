"""Corpus-independent JSONL knowledge indexing with explicit backends."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from src.project_paths import REPOSITORY_ROOT, SHARED_REPOSITORY_ROOT, resolve_project_path, resolve_shared_project_path

from .embedding_model_runtime import default_embedding_model_url, request_embeddings


SUPPORTED_BACKENDS = frozenset({"sqlite", "chroma"})
DEFAULT_EMBED_MODEL = "Qwen/Qwen3-Embedding-4B"


class KnowledgeBaseDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class KnowledgeRecord:
    chunk_id: str
    source_id: str
    title: str
    kb_type: str
    component: str
    related_components: tuple[str, ...]
    source_scope: str
    topic_tags: tuple[str, ...]
    version: str
    source_file: str
    heading_path: str
    source_url: str
    pinned_source_url: str
    use_when: str
    retrieval_keywords: tuple[str, ...]
    follow_up: str
    content: str
    content_sha256: str

    @property
    def embedding_text(self) -> str:
        content = self.content[:2048]
        return "\n".join((
            self.title,
            self.use_when,
            "Keywords: " + ", ".join(self.retrieval_keywords),
            self.follow_up,
            content,
        ))


@dataclass(frozen=True)
class KnowledgeBuildStats:
    status: str
    source_file: str
    persist_dir: str
    collection_name: str
    knowledge_base_mode: str
    backend: str
    embedding_model: str | None
    document_count: int
    node_count: int
    manifest_path: str
    database_path: str | None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repository_relative(path: Path) -> str:
    """manifest 路径的存储形式：仓库内资源写相对 REPOSITORY_ROOT 的 POSIX 相对路径
    （随仓库分发的数据文件不携带构建机绝对路径）；仓库外语料没有相对形式，保留绝对路径。"""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def source_sha256(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if path.is_dir():
        digest = hashlib.sha256()
        files = sorted(item for item in path.rglob("*") if item.is_file())
        for item in files:
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(item.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()
    raise FileNotFoundError(f"Knowledge source path does not exist: source={path}")


class MarkdownKnowledgeBase:
    """Build and query one configured documentation corpus."""

    def __init__(
        self,
        *,
        persist_dir: os.PathLike[str] | str,
        collection_name: str,
        backend: str,
        knowledge_base_mode: str,
        default_source_file: os.PathLike[str] | str,
        valid_kb_types: Iterable[str],
        valid_components: Iterable[str],
        valid_scopes: Iterable[str],
        build_script: str,
        embed_model_name: str = DEFAULT_EMBED_MODEL,
        embed_device: str = "cpu",
        embed_batch_size: int = 1,
        embed_workers: int = 1,
        product_label: str = "documentation",
    ):
        if backend not in SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported knowledge backend: backend={backend!r}, "
                f"supported={sorted(SUPPORTED_BACKENDS)!r}"
            )
        if knowledge_base_mode not in {"general", "hierarchical"}:
            raise ValueError(
                f"Unsupported knowledge mode: mode={knowledge_base_mode!r}, "
                "supported=['general', 'hierarchical']"
            )
        self.persist_dir = resolve_shared_project_path(persist_dir)
        self.collection_name = collection_name
        self.backend = backend
        self.knowledge_base_mode = knowledge_base_mode
        self.default_source_file = resolve_shared_project_path(default_source_file)
        self.valid_kb_types = frozenset(valid_kb_types)
        self.valid_components = frozenset(valid_components)
        self.valid_scopes = frozenset(valid_scopes)
        self.build_script = build_script
        self.embed_model_name = embed_model_name
        self.embed_device = embed_device
        self.embed_batch_size = embed_batch_size
        if embed_workers < 1:
            raise ValueError(f"Embedding workers must be positive: embed_workers={embed_workers}")
        self.embed_workers = embed_workers
        self.product_label = product_label

    @property
    def manifest_path(self) -> Path:
        return self.persist_dir / "manifest.json"

    @property
    def sqlite_path(self) -> Path:
        return self.persist_dir / f"{self.collection_name}.sqlite3"

    def build(
        self,
        source_file: os.PathLike[str] | str | None = None,
        *,
        reset_collection: bool = True,
        show_progress: bool = True,
    ) -> dict[str, Any]:
        source_path = resolve_shared_project_path(source_file or self.default_source_file)
        records = self._load_records(source_path)
        if self.backend == "sqlite":
            stats = self._build_sqlite(source_path, records, reset_collection)
        else:
            stats = self._build_chroma(source_path, records, reset_collection, show_progress)
        manifest = {
            **asdict(stats),
            **self._source_metadata(source_path, records),
            "build_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return asdict(stats)

    def query(
        self,
        query: str,
        *,
        source_scope: str | None = None,
        top_k: int = 5,
        kb_type: str | None = None,
        component: str | None = None,
        max_chars_per_result: int = 1600,
    ) -> dict[str, Any]:
        query = str(query).strip()
        if not query:
            raise ValueError("Knowledge query is required: query=''")
        if source_scope is not None and source_scope not in self.valid_scopes:
            raise ValueError(
                f"Unknown knowledge source_scope: value={source_scope!r}, "
                f"allowed={sorted(self.valid_scopes)!r}"
            )
        if kb_type is not None and kb_type not in self.valid_kb_types:
            raise ValueError(
                f"Unknown knowledge kb_type: value={kb_type!r}, allowed={sorted(self.valid_kb_types)!r}"
            )
        if component is not None and component not in self.valid_components:
            raise ValueError(
                f"Unknown knowledge component: value={component!r}, "
                f"allowed={sorted(self.valid_components)!r}"
            )
        if not isinstance(top_k, int) or not 1 <= top_k <= 20:
            raise ValueError(f"Knowledge top_k must be an integer from 1 to 20: top_k={top_k!r}")
        if not isinstance(max_chars_per_result, int) or not 200 <= max_chars_per_result <= 8000:
            raise ValueError(
                "Knowledge max_chars_per_result must be an integer from 200 to 8000: "
                f"value={max_chars_per_result!r}"
            )
        manifest = self._validated_manifest()
        if self.backend == "sqlite":
            results = self._query_sqlite(
                query, source_scope, top_k, kb_type, component, max_chars_per_result
            )
        else:
            results = self._query_chroma(
                query, source_scope, top_k, kb_type, component, max_chars_per_result
            )
        return {
            "status": "success",
            "query": query,
            "source_scope": source_scope,
            "kb_type": kb_type,
            "component": component,
            "top_k": top_k,
            "count": len(results),
            "results": results,
            "index": {
                "backend": self.backend,
                "collection": self.collection_name,
                "persist_dir": str(self.persist_dir),
                "source_commit": manifest.get("source_commit"),
                "materialized_corpus_sha256": manifest["materialized_corpus_sha256"],
            },
        }

    def _load_records(self, source_path: Path) -> list[KnowledgeRecord]:
        if not source_path.is_file():
            raise FileNotFoundError(
                f"Knowledge JSONL source does not exist: product={self.product_label!r}, "
                f"source_file={source_path}"
            )
        required = {
            "chunk_id", "source_id", "title", "kb_type", "component", "related_components",
            "source_scope", "topic_tags", "version", "source_file", "source_heading_path",
            "source_url", "pinned_source_url", "use_when", "retrieval_keywords", "follow_up",
            "content", "content_sha256",
        }
        records = []
        for line_number, line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                raise ValueError(
                    f"Knowledge JSONL contains an empty line: source_file={source_path}, line={line_number}"
                )
            value = json.loads(line)
            if not isinstance(value, dict) or not required <= set(value):
                actual = sorted(value) if isinstance(value, dict) else type(value).__name__
                raise ValueError(
                    f"Knowledge JSONL record fields are incomplete: source_file={source_path}, "
                    f"line={line_number}, required={sorted(required)!r}, actual={actual!r}"
                )
            if value["kb_type"] not in self.valid_kb_types:
                raise ValueError(
                    f"Knowledge JSONL has unknown kb_type: source_file={source_path}, "
                    f"line={line_number}, value={value['kb_type']!r}"
                )
            if value["component"] not in self.valid_components:
                raise ValueError(
                    f"Knowledge JSONL has unknown component: source_file={source_path}, "
                    f"line={line_number}, value={value['component']!r}"
                )
            if value["source_scope"] not in self.valid_scopes:
                raise ValueError(
                    f"Knowledge JSONL has unknown source_scope: source_file={source_path}, "
                    f"line={line_number}, value={value['source_scope']!r}"
                )
            actual_hash = hashlib.sha256(value["content"].encode("utf-8")).hexdigest()
            if value["content_sha256"] != actual_hash:
                raise ValueError(
                    f"Knowledge JSONL content hash mismatch: source_file={source_path}, "
                    f"line={line_number}, chunk_id={value['chunk_id']!r}, "
                    f"expected={value['content_sha256']!r}, actual={actual_hash!r}"
                )
            records.append(KnowledgeRecord(
                chunk_id=value["chunk_id"],
                source_id=value["source_id"],
                title=value["title"],
                kb_type=value["kb_type"],
                component=value["component"],
                related_components=tuple(value["related_components"]),
                source_scope=value["source_scope"],
                topic_tags=tuple(value["topic_tags"]),
                version=value["version"],
                source_file=value["source_file"],
                heading_path=value["source_heading_path"],
                source_url=value["source_url"],
                pinned_source_url=value["pinned_source_url"],
                use_when=value["use_when"],
                retrieval_keywords=tuple(value["retrieval_keywords"]),
                follow_up=value["follow_up"],
                content=value["content"],
                content_sha256=value["content_sha256"],
            ))
        if not records:
            raise ValueError(f"Knowledge JSONL contains no records: source_file={source_path}")
        ids = [record.chunk_id for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Knowledge JSONL contains duplicate chunk IDs: source_file={source_path}")
        return records

    def _source_metadata(
        self,
        source_path: Path,
        records: Sequence[KnowledgeRecord],
    ) -> dict[str, Any]:
        processing_path = source_path.parent / "tidb81_processing_manifest.json"
        processing = json.loads(processing_path.read_text(encoding="utf-8")) if processing_path.is_file() else {}
        lock_path = SHARED_REPOSITORY_ROOT / "knowledge" / "tidb_src" / ".source-lock.json"
        source_lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else {}
        return {
            "source_corpus_id": source_lock.get("corpus_id"),
            "source_branch": source_lock.get("branch"),
            "source_commit": source_lock.get("commit") or processing.get("source_commit"),
            "materialized_corpus_sha256": source_sha256(source_path),
            "split_prompt_sha256": processing.get("split_prompt_sha256"),
            "enrich_prompt_sha256": processing.get("enrich_prompt_sha256"),
            "embedding_model": self.embed_model_name if self.backend == "chroma" else None,
            "backend": self.backend,
            "collection_name": self.collection_name,
            "document_count": len({record.source_file for record in records}),
            "node_count": len(records),
        }

    def _validated_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.is_file():
            raise FileNotFoundError(
                f"{self.product_label} knowledge index is not built: backend={self.backend!r}, "
                f"persist_dir={self.persist_dir}, manifest={self.manifest_path}. "
                f"Build it with: conda run -n aiops python {self.build_script} "
                f"--backend {self.backend} --knowledge-mode {self.knowledge_base_mode}"
            )
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if manifest.get("backend") != self.backend or manifest.get("collection_name") != self.collection_name:
            raise ValueError(
                f"Knowledge index manifest configuration mismatch: manifest={self.manifest_path}, "
                f"expected_backend={self.backend!r}, actual_backend={manifest.get('backend')!r}, "
                f"expected_collection={self.collection_name!r}, "
                f"actual_collection={manifest.get('collection_name')!r}"
            )
        source_path = resolve_project_path(manifest["source_file"])
        if not source_path.exists():
            raise FileNotFoundError(
                f"Knowledge index source file is missing: manifest={self.manifest_path}, "
                f"source_file={source_path}"
            )
        current_hash = source_sha256(source_path)
        if current_hash != manifest["materialized_corpus_sha256"]:
            raise ValueError(
                f"Stale knowledge index corpus hash: manifest={self.manifest_path}, "
                f"source_file={source_path}, indexed={manifest['materialized_corpus_sha256']!r}, "
                f"current={current_hash!r}"
            )
        lock_path = SHARED_REPOSITORY_ROOT / "knowledge" / "tidb_src" / ".source-lock.json"
        if manifest.get("source_commit") and lock_path.is_file():
            current_commit = json.loads(lock_path.read_text(encoding="utf-8"))["commit"]
            if current_commit != manifest["source_commit"]:
                raise ValueError(
                    f"Stale knowledge index source commit: manifest={self.manifest_path}, "
                    f"indexed={manifest['source_commit']!r}, current={current_commit!r}"
                )
        return manifest

    def _build_sqlite(
        self,
        source_path: Path,
        records: Sequence[KnowledgeRecord],
        reset_collection: bool,
    ) -> KnowledgeBuildStats:
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        if reset_collection and self.sqlite_path.exists():
            self.sqlite_path.unlink()
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, title TEXT NOT NULL,
                    kb_type TEXT NOT NULL, component TEXT NOT NULL,
                    related_components TEXT NOT NULL, source_scope TEXT NOT NULL,
                    topic_tags TEXT NOT NULL, version TEXT NOT NULL, source_file TEXT NOT NULL,
                    heading_path TEXT NOT NULL, source_url TEXT NOT NULL,
                    pinned_source_url TEXT NOT NULL, use_when TEXT NOT NULL,
                    retrieval_keywords TEXT NOT NULL, follow_up TEXT NOT NULL,
                    content TEXT NOT NULL, content_sha256 TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED, title, use_when, retrieval_keywords, content
                );
            """)
            if reset_collection:
                conn.execute("DELETE FROM chunks")
                conn.execute("DELETE FROM chunks_fts")
            for record in records:
                conn.execute(
                    "INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        record.chunk_id, record.source_id, record.title, record.kb_type,
                        record.component, json.dumps(record.related_components),
                        record.source_scope, json.dumps(record.topic_tags), record.version,
                        record.source_file, record.heading_path, record.source_url,
                        record.pinned_source_url, record.use_when,
                        json.dumps(record.retrieval_keywords), record.follow_up,
                        record.content, record.content_sha256,
                    ),
                )
                conn.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (record.chunk_id,))
                conn.execute(
                    "INSERT INTO chunks_fts VALUES (?,?,?,?,?)",
                    (
                        record.chunk_id, record.title, record.use_when,
                        " ".join(record.retrieval_keywords), record.content,
                    ),
                )
        return KnowledgeBuildStats(
            status="success",
            source_file=_repository_relative(source_path),
            persist_dir=_repository_relative(self.persist_dir),
            collection_name=self.collection_name,
            knowledge_base_mode=self.knowledge_base_mode,
            backend="sqlite",
            embedding_model=None,
            document_count=len({record.source_file for record in records}),
            node_count=len(records),
            manifest_path=_repository_relative(self.manifest_path),
            database_path=_repository_relative(self.sqlite_path),
        )

    def _query_sqlite(
        self,
        query: str,
        source_scope: str | None,
        top_k: int,
        kb_type: str | None,
        component: str | None,
        max_chars: int,
    ) -> list[dict[str, Any]]:
        if not self.sqlite_path.is_file():
            raise FileNotFoundError(
                f"SQLite knowledge database is missing: database={self.sqlite_path}, "
                f"manifest={self.manifest_path}"
            )
        terms = re.findall(r"[A-Za-z0-9_.$-]+", query)
        if not terms:
            raise ValueError(f"Knowledge query has no indexable terms: query={query!r}")
        match_query = " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)
        where = ["chunks_fts MATCH ?"]
        params: list[Any] = [match_query]
        if source_scope and source_scope != "all":
            where.append("c.source_scope IN (?, 'shared', 'all')")
            params.append(source_scope)
        if kb_type:
            where.append("c.kb_type = ?")
            params.append(kb_type)
        if component:
            where.append("(c.component = ? OR c.related_components LIKE ?)")
            params.extend((component, f'%"{component}"%'))
        params.append(top_k)
        sql = f"""
            SELECT c.*, bm25(chunks_fts) AS distance
            FROM chunks_fts JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
            WHERE {' AND '.join(where)}
            ORDER BY distance ASC, c.chunk_id ASC
            LIMIT ?
        """
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        return [
            self._row_result(dict(row), rank, max_chars, float(row["distance"]))
            for rank, row in enumerate(rows, 1)
        ]

    def _build_chroma(
        self,
        source_path: Path,
        records: Sequence[KnowledgeRecord],
        reset_collection: bool,
        show_progress: bool,
    ) -> KnowledgeBuildStats:
        chromadb = self._chroma_dependencies()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(self.persist_dir))
        if reset_collection:
            existing = {item.name for item in client.list_collections()}
            if self.collection_name in existing:
                client.delete_collection(self.collection_name)
            collection = client.create_collection(self.collection_name)
        else:
            collection = client.get_or_create_collection(self.collection_name)
        embedding_service_urls = self._embedding_service_urls()
        upsert_batch_size = 256 if self.embed_workers > 1 else 32
        embedding_records = sorted(records, key=lambda record: len(record.embedding_text))
        for start in range(0, len(embedding_records), upsert_batch_size):
            batch = embedding_records[start:start + upsert_batch_size]
            texts = [record.embedding_text for record in batch]
            requests = [
                (
                    texts[request_start:request_start + self.embed_batch_size],
                    embedding_service_urls[index % len(embedding_service_urls)],
                )
                for index, request_start in enumerate(
                    range(0, len(texts), self.embed_batch_size)
                )
            ]
            with ThreadPoolExecutor(max_workers=len(embedding_service_urls)) as executor:
                vectors = executor.map(
                    lambda job: request_embeddings(
                        job[0],
                        self.embed_model_name,
                        self.embed_device,
                        prompt_name="text",
                        base_url=job[1],
                    ),
                    requests,
                )
                embeddings = [vector for batch_vectors in vectors for vector in batch_vectors]
            collection.upsert(
                ids=[record.chunk_id for record in batch],
                embeddings=embeddings,
                documents=[record.content for record in batch],
                metadatas=[self._chroma_metadata(record) for record in batch],
            )
        return KnowledgeBuildStats(
            status="success",
            source_file=_repository_relative(source_path),
            persist_dir=_repository_relative(self.persist_dir),
            collection_name=self.collection_name,
            knowledge_base_mode=self.knowledge_base_mode,
            backend="chroma",
            embedding_model=self.embed_model_name,
            document_count=len({record.source_file for record in records}),
            node_count=len(records),
            manifest_path=_repository_relative(self.manifest_path),
            database_path=None,
        )

    def _query_chroma(
        self,
        query: str,
        source_scope: str | None,
        top_k: int,
        kb_type: str | None,
        component: str | None,
        max_chars: int,
    ) -> list[dict[str, Any]]:
        chromadb = self._chroma_dependencies()
        client = chromadb.PersistentClient(path=str(self.persist_dir))
        try:
            collection = client.get_collection(self.collection_name)
        except Exception as exc:
            raise FileNotFoundError(
                f"Chroma knowledge collection is missing: persist_dir={self.persist_dir}, "
                f"collection={self.collection_name!r}, error={exc}"
            ) from exc
        clauses = []
        if source_scope and source_scope != "all":
            clauses.append({"source_scope": {"$in": [source_scope, "shared", "all"]}})
        if kb_type:
            clauses.append({"kb_type": kb_type})
        if component:
            clauses.append({f"has_component_{component}": True})
        where = None if not clauses else clauses[0] if len(clauses) == 1 else {"$and": clauses}
        embedding = request_embeddings(
            [query],
            self.embed_model_name,
            self.embed_device,
            prompt_name="query",
            base_url=self._embedding_service_urls()[0],
        )[0]
        query_args = {
            "query_embeddings": [embedding],
            "n_results": top_k,
            "include": ["metadatas", "distances", "documents"],
        }
        if where is not None:
            query_args["where"] = where
        result = collection.query(**query_args)
        return [
            self._row_result(
                {**metadata, "content": document},
                rank,
                max_chars,
                float(distance),
            )
            for rank, (metadata, distance, document) in enumerate(
                zip(
                    result["metadatas"][0],
                    result["distances"][0],
                    result["documents"][0],
                ),
                1,
            )
        ]

    def _chroma_dependencies(self):
        try:
            import chromadb
        except ImportError as exc:
            raise KnowledgeBaseDependencyError(
                "Chroma knowledge dependencies are missing. Install with: "
                "conda run -n aiops pip install -e '.[knowledge]'. "
                f"Original import error: {exc}"
            ) from exc
        return chromadb

    @staticmethod
    def _embedding_service_urls() -> tuple[str, ...]:
        configured_urls = os.environ.get("AIOPS_EMBEDDING_MODEL_URLS", "")
        embedding_service_urls = tuple(
            url.strip() for url in configured_urls.split(",") if url.strip()
        )
        if embedding_service_urls:
            return embedding_service_urls
        single_url = os.environ.get("AIOPS_EMBEDDING_MODEL_URL", "").strip()
        return (single_url or default_embedding_model_url(),)

    @staticmethod
    def _chroma_metadata(record: KnowledgeRecord) -> dict[str, Any]:
        metadata = {
            "chunk_id": record.chunk_id,
            "source_id": record.source_id,
            "title": record.title,
            "kb_type": record.kb_type,
            "component": record.component,
            "components": "|" + "|".join((record.component, *record.related_components)) + "|",
            "source_scope": record.source_scope,
            "version": record.version,
            "source_file": record.source_file,
            "heading_path": record.heading_path,
            "source_url": record.source_url,
            "pinned_source_url": record.pinned_source_url,
        }
        for component in (record.component, *record.related_components):
            metadata[f"has_component_{component}"] = True
        return metadata

    @staticmethod
    def _row_result(
        row: dict[str, Any],
        rank: int,
        max_chars: int,
        distance: float,
    ) -> dict[str, Any]:
        content = row["content"]
        truncated = content if len(content) <= max_chars else content[:max_chars].rstrip() + "…"
        score = 1.0 / (1.0 + abs(distance))
        return {
            "rank": rank,
            "score": round(score, 6),
            "source_id": row["source_id"],
            "title": row["title"],
            "version": row["version"],
            "kb_type": row["kb_type"],
            "component": row["component"],
            "source_scope": row["source_scope"],
            "source_file": row["source_file"],
            "heading_path": row["heading_path"],
            "source_url": row["source_url"],
            "pinned_source_url": row["pinned_source_url"],
            "content": truncated,
        }
