"""PostgreSQL documentation knowledge base for agent-side retrieval.

The default backend is a local Chroma vector store using
Qwen/Qwen3-Embedding-4B. SQLite FTS5 is retained as a dependency-light fallback
for exact PostgreSQL identifiers and for environments where the vector index or
embedding model is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import queue
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.project_paths import resolve_shared_project_path


DEFAULT_BACKEND = "chroma"
DEFAULT_COLLECTION_NAME = "pg16_docs"
DEFAULT_GENERAL_DOCS_DIR = Path("knowledge/pg_src/pg16-docs-md")
DEFAULT_HIERARCHICAL_DOCS_DIR = Path("knowledge/pg")
DEFAULT_DOCS_DIR = DEFAULT_GENERAL_DOCS_DIR
DEFAULT_EMBED_MODEL = "Qwen/Qwen3-Embedding-4B"
DEFAULT_EMBED_DEVICE = "cpu"
DEFAULT_EMBED_BATCH_SIZE = 1
DEFAULT_EMBED_PARALLEL = False
DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"
DEFAULT_CHROMA_PERSIST_DIR = Path("data/knowledge_bases/pg16_chroma")
DEFAULT_SQLITE_PERSIST_DIR = Path("data/knowledge_bases/pg16_docs")
DEFAULT_HIERARCHICAL_CHROMA_PERSIST_DIR = Path("data/knowledge_bases/pg16_hierarchical_chroma")
DEFAULT_HIERARCHICAL_SQLITE_PERSIST_DIR = Path("data/knowledge_bases/pg16_hierarchical_docs")
DEFAULT_PERSIST_DIR = DEFAULT_CHROMA_PERSIST_DIR
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 160
SUPPORTED_BACKENDS = {"sqlite", "chroma"}
KNOWLEDGE_TYPES = {"configuration", "guide", "solution", "fact"}
KNOWLEDGE_BASE_MODES = {"general", "hierarchical"}


def _manual_embed_worker(
    device: str,
    items: Sequence[Tuple[int, str]],
    model_name: str,
    batch_size: int,
    result_queue: mp.Queue,
) -> None:
    try:
        from llama_index.embeddings.huggingface.utils import (
            get_query_instruct_for_model_name,
            get_text_instruct_for_model_name,
        )
        from sentence_transformers import SentenceTransformer

        indices = [item[0] for item in items]
        texts = [item[1] for item in items]
        model = SentenceTransformer(
            model_name,
            device=device,
            prompts={
                "query": get_query_instruct_for_model_name(model_name),
                "text": get_text_instruct_for_model_name(model_name),
            },
        )
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            prompt_name="text",
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        result_queue.put({
            "status": "success",
            "device": device,
            "indices": indices,
            "embeddings": embeddings,
        })
    except Exception as exc:
        result_queue.put({
            "status": "error",
            "device": device,
            "error_type": type(exc).__name__,
            "error": str(exc),
        })


def normalize_knowledge_base_mode(mode: Optional[str] = None) -> str:
    normalized = str(mode or os.environ.get("AIOPS_PG_KB_MODE", "general")).strip().lower()
    aliases = {
        "": "general",
        "default": "general",
        "plain": "general",
        "flat": "general",
        "generic": "general",
        "typed": "hierarchical",
        "split": "hierarchical",
        "layered": "hierarchical",
        "dbagent": "hierarchical",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in KNOWLEDGE_BASE_MODES:
        raise ValueError(
            f"Unsupported PG knowledge base mode: {mode}. "
            f"Supported modes: {', '.join(sorted(KNOWLEDGE_BASE_MODES))}"
        )
    return normalized


def default_docs_dir(knowledge_base_mode: Optional[str] = None) -> Path:
    mode = normalize_knowledge_base_mode(knowledge_base_mode)
    mode_env = (
        "AIOPS_PG_HIERARCHICAL_KB_DOCS_DIR"
        if mode == "hierarchical"
        else "AIOPS_PG_GENERAL_KB_DOCS_DIR"
    )
    default_dir = (
        DEFAULT_HIERARCHICAL_DOCS_DIR
        if mode == "hierarchical"
        else DEFAULT_GENERAL_DOCS_DIR
    )
    configured = os.environ.get(mode_env) or os.environ.get("AIOPS_PG_KB_DOCS_DIR")
    return resolve_shared_project_path(configured or default_dir)


def default_persist_dir(backend: Optional[str] = None, knowledge_base_mode: Optional[str] = None) -> Path:
    normalized_backend = (backend or default_backend()).strip().lower()
    mode = normalize_knowledge_base_mode(knowledge_base_mode)
    if mode == "hierarchical":
        default_dir = (
            DEFAULT_HIERARCHICAL_SQLITE_PERSIST_DIR
            if normalized_backend in ("sqlite", "fts", "sqlite_fts")
            else DEFAULT_HIERARCHICAL_CHROMA_PERSIST_DIR
        )
        mode_env = "AIOPS_PG_HIERARCHICAL_KB_DIR"
    else:
        default_dir = (
            DEFAULT_SQLITE_PERSIST_DIR
            if normalized_backend in ("sqlite", "fts", "sqlite_fts")
            else DEFAULT_CHROMA_PERSIST_DIR
        )
        mode_env = "AIOPS_PG_GENERAL_KB_DIR"
    return resolve_shared_project_path(os.environ.get(mode_env) or os.environ.get("AIOPS_PG_KB_DIR", default_dir))


def default_sqlite_persist_dir(knowledge_base_mode: Optional[str] = None) -> Path:
    mode = normalize_knowledge_base_mode(knowledge_base_mode)
    mode_env = (
        "AIOPS_PG_HIERARCHICAL_KB_SQLITE_DIR"
        if mode == "hierarchical"
        else "AIOPS_PG_GENERAL_KB_SQLITE_DIR"
    )
    default_dir = (
        DEFAULT_HIERARCHICAL_SQLITE_PERSIST_DIR
        if mode == "hierarchical"
        else DEFAULT_SQLITE_PERSIST_DIR
    )
    return resolve_shared_project_path(
        os.environ.get(mode_env) or os.environ.get("AIOPS_PG_KB_SQLITE_DIR", default_dir)
    )


def default_collection_name() -> str:
    return os.environ.get("AIOPS_PG_KB_COLLECTION", DEFAULT_COLLECTION_NAME)


def default_embed_model() -> str:
    return os.environ.get("AIOPS_PG_KB_EMBED_MODEL", DEFAULT_EMBED_MODEL)


def default_embed_device() -> str:
    return os.environ.get("AIOPS_PG_KB_EMBED_DEVICE", DEFAULT_EMBED_DEVICE)


def default_embed_batch_size() -> int:
    raw = os.environ.get("AIOPS_PG_KB_EMBED_BATCH_SIZE", DEFAULT_EMBED_BATCH_SIZE)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = DEFAULT_EMBED_BATCH_SIZE
    return max(1, min(value, 128))


def default_embed_parallel_process() -> bool:
    raw = os.environ.get("AIOPS_PG_KB_EMBED_PARALLEL", str(DEFAULT_EMBED_PARALLEL))
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def default_embed_target_devices() -> Optional[List[str]]:
    raw = os.environ.get("AIOPS_PG_KB_EMBED_TARGET_DEVICES", "").strip()
    if not raw:
        return None
    return [device.strip() for device in raw.split(",") if device.strip()]


def default_hf_endpoint() -> str:
    return os.environ.get("AIOPS_HF_ENDPOINT", DEFAULT_HF_ENDPOINT)


def default_backend() -> str:
    return os.environ.get("AIOPS_PG_KB_BACKEND", DEFAULT_BACKEND)


@dataclass
class KnowledgeBuildStats:
    status: str
    source_dir: str
    persist_dir: str
    collection_name: str
    knowledge_base_mode: str
    backend: str
    embedding_model: Optional[str]
    embedding_batch_size: Optional[int]
    embedding_parallel_process: Optional[bool]
    embedding_target_devices: Optional[List[str]]
    document_count: int
    node_count: int
    chunk_size: int
    chunk_overlap: int
    manifest_path: str
    database_path: Optional[str] = None


@dataclass
class KnowledgeChunk:
    chunk_id: str
    source: str
    file_path: str
    title: str
    part: str
    kb_type: str
    headings: List[str]
    heading_path: str
    chunk_index: int
    content: str


class KnowledgeBaseDependencyError(RuntimeError):
    pass


def _dependency_error(exc: BaseException) -> KnowledgeBaseDependencyError:
    return KnowledgeBaseDependencyError(
        "PG knowledge base optional Chroma dependencies are not installed. "
        "Use the default SQLite backend, or install them in the aiops "
        "environment with: conda run -n aiops pip install -e '.[knowledge]'. "
        f"Original import error: {exc}"
    )


def _load_ingest_dependencies():
    try:
        import chromadb
        from llama_index.core import Document
        from llama_index.core.ingestion import IngestionPipeline
        from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.vector_stores.chroma import ChromaVectorStore
    except ImportError as exc:  # pragma: no cover - exercised via caller output
        raise _dependency_error(exc) from exc
    return {
        "chromadb": chromadb,
        "Document": Document,
        "IngestionPipeline": IngestionPipeline,
        "MarkdownNodeParser": MarkdownNodeParser,
        "SentenceSplitter": SentenceSplitter,
        "HuggingFaceEmbedding": HuggingFaceEmbedding,
        "ChromaVectorStore": ChromaVectorStore,
    }


def _load_query_dependencies():
    try:
        import chromadb
        from llama_index.core import VectorStoreIndex
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.vector_stores.chroma import ChromaVectorStore
    except ImportError as exc:  # pragma: no cover - exercised via caller output
        raise _dependency_error(exc) from exc
    return {
        "chromadb": chromadb,
        "VectorStoreIndex": VectorStoreIndex,
        "HuggingFaceEmbedding": HuggingFaceEmbedding,
        "ChromaVectorStore": ChromaVectorStore,
    }


class PGKnowledgeBase:
    """Build and query the local PostgreSQL documentation index."""

    def __init__(
        self,
        persist_dir: os.PathLike[str] | str | None = None,
        collection_name: Optional[str] = None,
        embed_model_name: Optional[str] = None,
        embed_batch_size: Optional[int] = None,
        embed_parallel_process: Optional[bool] = None,
        embed_target_devices: Optional[Sequence[str]] = None,
        backend: Optional[str] = None,
        knowledge_base_mode: Optional[str] = None,
    ):
        self.collection_name = collection_name or default_collection_name()
        self.knowledge_base_mode = normalize_knowledge_base_mode(knowledge_base_mode)
        self.embed_model_name = embed_model_name or default_embed_model()
        self.embed_batch_size = embed_batch_size or default_embed_batch_size()
        self.embed_parallel_process = (
            default_embed_parallel_process()
            if embed_parallel_process is None
            else bool(embed_parallel_process)
        )
        self.embed_target_devices = (
            list(embed_target_devices)
            if embed_target_devices is not None
            else default_embed_target_devices()
        )
        self.backend = self._normalize_backend(backend or default_backend())
        self.persist_dir = resolve_shared_project_path(
            persist_dir or default_persist_dir(self.backend, self.knowledge_base_mode)
        )

    @property
    def manifest_path(self) -> Path:
        return self.persist_dir / "manifest.json"

    @property
    def sqlite_path(self) -> Path:
        return self.persist_dir / f"{self.collection_name}.sqlite3"

    def build(
        self,
        source_dir: os.PathLike[str] | str | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        reset_collection: bool = True,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        if self.backend == "chroma":
            return self._build_chroma(
                source_dir=source_dir,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                reset_collection=reset_collection,
                show_progress=show_progress,
            )
        return self._build_sqlite(
            source_dir=source_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            reset_collection=reset_collection,
        )

    def query(
        self,
        query: str,
        top_k: int = 5,
        max_chars_per_result: int = 1600,
        kb_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = (query or "").strip()
        if not query:
            return {"status": "error", "error": "query is required"}
        normalized_kb_type = self._normalize_kb_type(kb_type)
        if kb_type is not None and str(kb_type).strip() and normalized_kb_type is None:
            return {
                "status": "error",
                "error": (
                    "kb_type must be one of: "
                    + ", ".join(sorted(KNOWLEDGE_TYPES))
                ),
            }
        top_k = self._coerce_int(top_k, default=5, minimum=1, maximum=20)
        max_chars_per_result = self._coerce_int(
            max_chars_per_result,
            default=1600,
            minimum=200,
            maximum=8000,
        )

        if self.backend == "chroma":
            missing_index = self._missing_index_error()
            if missing_index:
                fallback = self._query_sqlite_fallback(
                    query,
                    top_k,
                    max_chars_per_result,
                    normalized_kb_type,
                    reason=missing_index.get("error", "Chroma index is unavailable."),
                )
                return fallback or missing_index
            result = self._query_chroma(
                query,
                top_k,
                max_chars_per_result,
                normalized_kb_type,
            )
            if result.get("status") == "error":
                fallback = self._query_sqlite_fallback(
                    query,
                    top_k,
                    max_chars_per_result,
                    normalized_kb_type,
                    reason=result.get("error", "Chroma query failed."),
                )
                return fallback or result
            return result

        missing_index = self._missing_index_error()
        if missing_index:
            return missing_index
        return self._query_sqlite(
            query,
            top_k,
            max_chars_per_result,
            normalized_kb_type,
        )

    def _build_sqlite(
        self,
        source_dir: os.PathLike[str] | str | None,
        chunk_size: int,
        chunk_overlap: int,
        reset_collection: bool,
    ) -> Dict[str, Any]:
        source_path = resolve_shared_project_path(
            source_dir or default_docs_dir(self.knowledge_base_mode)
        )
        markdown_files = self._list_markdown_files(source_path)
        if not markdown_files:
            return {
                "status": "error",
                "error": f"No Markdown files found under {source_path}",
                "source_dir": str(source_path),
            }

        chunk_size = self._coerce_int(chunk_size, DEFAULT_CHUNK_SIZE, 300, 10000)
        chunk_overlap = self._coerce_int(
            chunk_overlap,
            DEFAULT_CHUNK_OVERLAP,
            0,
            max(chunk_size - 1, 0),
        )

        self.persist_dir.mkdir(parents=True, exist_ok=True)
        if reset_collection and self.sqlite_path.exists():
            self.sqlite_path.unlink()

        chunks: List[KnowledgeChunk] = []
        for file_path in markdown_files:
            metadata = self._metadata_for_file(file_path, source_path)
            text = file_path.read_text(encoding="utf-8")
            chunks.extend(self._chunk_document(text, metadata, chunk_size, chunk_overlap))

        if not chunks:
            return {
                "status": "error",
                "error": f"No chunks generated from Markdown files under {source_path}",
                "source_dir": str(source_path),
            }

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                self._create_sqlite_schema(conn)
                if not reset_collection:
                    self._delete_sqlite_sources(conn, [chunk.source for chunk in chunks])
                self._insert_sqlite_chunks(conn, chunks)
                self._write_sqlite_meta(
                    conn,
                    source_path=source_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    markdown_files=markdown_files,
                    chunks=chunks,
                )
        except sqlite3.Error as exc:
            return self._error(f"Failed to build SQLite PG knowledge base: {exc}")

        stats = KnowledgeBuildStats(
            status="success",
            source_dir=str(source_path),
            persist_dir=str(self.persist_dir),
            collection_name=self.collection_name,
            knowledge_base_mode=self.knowledge_base_mode,
            backend="sqlite",
            embedding_model=None,
            embedding_batch_size=None,
            embedding_parallel_process=None,
            embedding_target_devices=None,
            document_count=len(markdown_files),
            node_count=len(chunks),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            manifest_path=str(self.manifest_path),
            database_path=str(self.sqlite_path),
        )
        self._write_manifest(stats, markdown_files)
        return asdict(stats)

    def _query_sqlite(
        self,
        query: str,
        top_k: int,
        max_chars_per_result: int,
        kb_type: Optional[str],
    ) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = self._query_sqlite_fts(conn, query, top_k, kb_type)
                if not rows:
                    rows = self._query_sqlite_like(conn, query, top_k, kb_type)
        except sqlite3.Error as exc:
            return self._error(f"Failed to query SQLite PG knowledge base: {exc}")

        return {
            "status": "success",
            "query": query,
            "kb_type": kb_type,
            "top_k": top_k,
            "count": len(rows),
            "results": [
                self._sqlite_row_to_result(row, rank, max_chars_per_result)
                for rank, row in enumerate(rows, start=1)
            ],
            "index": {
                "backend": "sqlite",
                "persist_dir": str(self.persist_dir),
                "database_path": str(self.sqlite_path),
                "collection_name": self.collection_name,
            },
        }

    def _build_chroma(
        self,
        source_dir: os.PathLike[str] | str | None,
        chunk_size: int,
        chunk_overlap: int,
        reset_collection: bool,
        show_progress: bool,
    ) -> Dict[str, Any]:
        source_path = resolve_shared_project_path(
            source_dir or default_docs_dir(self.knowledge_base_mode)
        )
        markdown_files = self._list_markdown_files(source_path)
        if not markdown_files:
            return {
                "status": "error",
                "error": f"No Markdown files found under {source_path}",
                "source_dir": str(source_path),
            }

        chunk_size = self._coerce_int(chunk_size, DEFAULT_CHUNK_SIZE, 300, 10000)
        chunk_overlap = self._coerce_int(
            chunk_overlap,
            DEFAULT_CHUNK_OVERLAP,
            0,
            max(chunk_size - 1, 0),
        )

        self._ensure_hf_endpoint()
        deps = _load_ingest_dependencies()
        chromadb = deps["chromadb"]
        Document = deps["Document"]
        IngestionPipeline = deps["IngestionPipeline"]
        MarkdownNodeParser = deps["MarkdownNodeParser"]
        SentenceSplitter = deps["SentenceSplitter"]
        HuggingFaceEmbedding = deps["HuggingFaceEmbedding"]
        ChromaVectorStore = deps["ChromaVectorStore"]

        self.persist_dir.mkdir(parents=True, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        if reset_collection:
            self._delete_collection_if_exists(chroma_client)
        collection = chroma_client.get_or_create_collection(self.collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)

        documents = [
            Document(
                text=file_path.read_text(encoding="utf-8"),
                id_=str(file_path.relative_to(source_path)),
                metadata=self._chroma_metadata_for_file(file_path, source_path),
            )
            for file_path in markdown_files
        ]

        if self.embed_parallel_process:
            split_pipeline = IngestionPipeline(
                transformations=[
                    MarkdownNodeParser(),
                    SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
                ],
            )
            nodes = split_pipeline.run(documents=documents, show_progress=show_progress)
            self._embed_nodes_manually(nodes)
            vector_store.add(nodes)
        else:
            embed_model = HuggingFaceEmbedding(
                model_name=self.embed_model_name,
                device=default_embed_device(),
                embed_batch_size=self.embed_batch_size,
            )
            pipeline = IngestionPipeline(
                transformations=[
                    MarkdownNodeParser(),
                    SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
                    embed_model,
                ],
                vector_store=vector_store,
            )
            nodes = pipeline.run(documents=documents, show_progress=show_progress)

        stats = KnowledgeBuildStats(
            status="success",
            source_dir=str(source_path),
            persist_dir=str(self.persist_dir),
            collection_name=self.collection_name,
            knowledge_base_mode=self.knowledge_base_mode,
            backend="chroma",
            embedding_model=self.embed_model_name,
            embedding_batch_size=self.embed_batch_size,
            embedding_parallel_process=self.embed_parallel_process,
            embedding_target_devices=self.embed_target_devices,
            document_count=len(documents),
            node_count=len(nodes),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            manifest_path=str(self.manifest_path),
            database_path=None,
        )
        self._write_manifest(stats, markdown_files)
        return asdict(stats)

    def _embed_nodes_manually(self, nodes: Sequence[Any]) -> None:
        from llama_index.core.schema import MetadataMode

        devices = self.embed_target_devices or [default_embed_device()]
        items = [
            (index, node.get_content(metadata_mode=MetadataMode.EMBED))
            for index, node in enumerate(nodes)
        ]
        shards = [items[index::len(devices)] for index in range(len(devices))]
        ctx = mp.get_context("spawn")
        result_queue = ctx.Queue()
        processes = [
            ctx.Process(
                target=_manual_embed_worker,
                args=(device, shard, self.embed_model_name, self.embed_batch_size, result_queue),
            )
            for device, shard in zip(devices, shards)
            if shard
        ]
        for process in processes:
            process.start()

        results: List[Dict[str, Any]] = []
        while len(results) < len(processes):
            try:
                results.append(result_queue.get(timeout=30))
            except queue.Empty:
                failed = [
                    process
                    for process in processes
                    if not process.is_alive() and process.exitcode not in (0, None)
                ]
                if failed:
                    raise RuntimeError(
                        "Manual multi-GPU embedding worker exited unexpectedly: "
                        + ", ".join(str(process.exitcode) for process in failed)
                    )

        for process in processes:
            process.join()
        errors = [result for result in results if result.get("status") != "success"]
        if errors:
            raise RuntimeError(
                "Manual multi-GPU embedding failed: "
                + json.dumps(errors, ensure_ascii=False)
            )

        for result in results:
            for index, embedding in zip(result["indices"], result["embeddings"]):
                nodes[index].embedding = embedding.tolist()

    def _query_chroma(
        self,
        query: str,
        top_k: int,
        max_chars_per_result: int,
        kb_type: Optional[str],
    ) -> Dict[str, Any]:
        try:
            self._ensure_hf_endpoint()
            deps = _load_query_dependencies()
            chromadb = deps["chromadb"]
            VectorStoreIndex = deps["VectorStoreIndex"]
            HuggingFaceEmbedding = deps["HuggingFaceEmbedding"]
            ChromaVectorStore = deps["ChromaVectorStore"]

            chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
            collection = chroma_client.get_collection(self.collection_name)
            vector_store = ChromaVectorStore(chroma_collection=collection)
            embed_model = HuggingFaceEmbedding(
                model_name=self.embed_model_name,
                device=default_embed_device(),
                embed_batch_size=self.embed_batch_size,
            )
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model,
            )
            retrieve_k = min(top_k * 8, 160) if kb_type else top_k
            retriever = index.as_retriever(similarity_top_k=retrieve_k)
            nodes = retriever.retrieve(query)
        except KnowledgeBaseDependencyError as exc:
            return self._error(str(exc))
        except Exception as exc:
            return self._error(f"Failed to query Chroma PG knowledge base: {exc}")

        results = []
        rank = 0
        for node_with_score in nodes:
            node = node_with_score.node
            metadata = dict(getattr(node, "metadata", {}) or {})
            if kb_type and metadata.get("kb_type") != kb_type:
                continue
            rank += 1
            content = node.get_content(metadata_mode="none")
            score = getattr(node_with_score, "score", None)
            if score is not None:
                score = float(score)
            results.append({
                "rank": rank,
                "score": score,
                "source": metadata.get("relative_path") or metadata.get("file_path"),
                "title": metadata.get("title"),
                "part": metadata.get("part"),
                "kb_type": metadata.get("kb_type"),
                "heading_path": metadata.get("heading_path") or metadata.get("header_path"),
                "chunk_id": getattr(node, "node_id", None),
                "content": self._truncate(content, max_chars_per_result),
            })
            if len(results) >= top_k:
                break

        return {
            "status": "success",
            "query": query,
            "kb_type": kb_type,
            "top_k": top_k,
            "count": len(results),
            "results": results,
            "index": {
                "backend": "chroma",
                "persist_dir": str(self.persist_dir),
                "collection_name": self.collection_name,
                "embedding_model": self.embed_model_name,
            },
        }

    def _query_sqlite_fallback(
        self,
        query: str,
        top_k: int,
        max_chars_per_result: int,
        kb_type: Optional[str],
        reason: str,
    ) -> Optional[Dict[str, Any]]:
        fallback = PGKnowledgeBase(
            persist_dir=default_sqlite_persist_dir(self.knowledge_base_mode),
            collection_name=self.collection_name,
            embed_model_name=self.embed_model_name,
            backend="sqlite",
            knowledge_base_mode=self.knowledge_base_mode,
        )
        if fallback._missing_index_error():
            return None
        result = fallback._query_sqlite(query, top_k, max_chars_per_result, kb_type)
        if result.get("status") == "success":
            result["fallback_for"] = "chroma"
            result["fallback_reason"] = reason
            result.setdefault("index", {})["fallback_for"] = "chroma"
        return result

    def _query_sqlite_fts(
        self,
        conn: sqlite3.Connection,
        query: str,
        top_k: int,
        kb_type: Optional[str],
    ) -> List[sqlite3.Row]:
        terms = self._query_terms(query)
        if not terms:
            return []
        fts_query = " OR ".join(self._quote_fts_term(term) for term in terms)
        kb_type_clause = "AND c.kb_type = ?" if kb_type else ""
        params: List[Any] = [fts_query]
        if kb_type:
            params.append(kb_type)
        params.append(top_k)
        try:
            return conn.execute(
                f"""
                SELECT
                    c.chunk_id,
                    c.source,
                    c.file_path,
                    c.title,
                    c.part,
                    c.kb_type,
                    c.headings,
                    c.heading_path,
                    c.chunk_index,
                    c.content,
                    bm25(chunks_fts) AS distance
                FROM chunks_fts
                JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
                WHERE chunks_fts MATCH ?
                {kb_type_clause}
                ORDER BY distance
                LIMIT ?
                """,
                tuple(params),
            ).fetchall()
        except sqlite3.Error:
            return []

    def _query_sqlite_like(
        self,
        conn: sqlite3.Connection,
        query: str,
        top_k: int,
        kb_type: Optional[str],
    ) -> List[sqlite3.Row]:
        terms = self._query_terms(query)
        if not terms:
            return []
        kb_type_clause = "WHERE kb_type = ?" if kb_type else ""
        params: Tuple[Any, ...] = (kb_type,) if kb_type else ()
        rows = conn.execute(
            f"""
            SELECT
                chunk_id,
                source,
                file_path,
                title,
                part,
                kb_type,
                headings,
                heading_path,
                chunk_index,
                content,
                0.0 AS distance
            FROM chunks
            {kb_type_clause}
            """,
            params,
        ).fetchall()
        scored = []
        for row in rows:
            haystack = " ".join([
                row["title"] or "",
                row["heading_path"] or "",
                row["content"] or "",
            ]).lower()
            score = sum(1 for term in terms if term.lower() in haystack)
            if score:
                scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in scored[:top_k]]

    def _sqlite_row_to_result(
        self,
        row: sqlite3.Row,
        rank: int,
        max_chars_per_result: int,
    ) -> Dict[str, Any]:
        distance = float(row["distance"] or 0.0)
        score = -distance if distance < 0 else 1.0 / (1.0 + distance)
        headings = self._json_loads(row["headings"], default=[])
        return {
            "rank": rank,
            "score": score,
            "source": row["source"],
            "title": row["title"],
            "part": row["part"],
            "kb_type": row["kb_type"],
            "headings": headings,
            "heading_path": row["heading_path"],
            "chunk_id": row["chunk_id"],
            "chunk_index": row["chunk_index"],
            "content": self._truncate(row["content"], max_chars_per_result),
        }

    def _create_sqlite_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                file_path TEXT NOT NULL,
                title TEXT,
                part TEXT,
                kb_type TEXT,
                headings TEXT,
                heading_path TEXT,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                chunk_id UNINDEXED,
                content,
                title,
                headings,
                source UNINDEXED,
                part UNINDEXED,
                kb_type UNINDEXED
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

    def _delete_sqlite_sources(self, conn: sqlite3.Connection, sources: Sequence[str]) -> None:
        unique_sources = sorted(set(sources))
        for source in unique_sources:
            chunk_ids = [
                row[0]
                for row in conn.execute(
                    "SELECT chunk_id FROM chunks WHERE source = ?",
                    (source,),
                ).fetchall()
            ]
            if not chunk_ids:
                continue
            conn.execute("DELETE FROM chunks WHERE source = ?", (source,))
            for chunk_id in chunk_ids:
                conn.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (chunk_id,))

    def _insert_sqlite_chunks(self, conn: sqlite3.Connection, chunks: Sequence[KnowledgeChunk]) -> None:
        conn.executemany(
            """
            INSERT OR REPLACE INTO chunks (
                chunk_id, source, file_path, title, part, kb_type, headings,
                heading_path, chunk_index, content
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    chunk.chunk_id,
                    chunk.source,
                    chunk.file_path,
                    chunk.title,
                    chunk.part,
                    chunk.kb_type,
                    json.dumps(chunk.headings, ensure_ascii=False),
                    chunk.heading_path,
                    chunk.chunk_index,
                    chunk.content,
                )
                for chunk in chunks
            ],
        )
        conn.executemany(
            """
            INSERT INTO chunks_fts (
                chunk_id, content, title, headings, source, part, kb_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    chunk.chunk_id,
                    chunk.content,
                    chunk.title,
                    " ".join(chunk.headings),
                    chunk.source,
                    chunk.part,
                    chunk.kb_type,
                )
                for chunk in chunks
            ],
        )

    def _write_sqlite_meta(
        self,
        conn: sqlite3.Connection,
        source_path: Path,
        chunk_size: int,
        chunk_overlap: int,
        markdown_files: Sequence[Path],
        chunks: Sequence[KnowledgeChunk],
    ) -> None:
        payload = {
            "backend": "sqlite",
            "source_dir": str(source_path),
            "collection_name": self.collection_name,
            "knowledge_base_mode": self.knowledge_base_mode,
            "document_count": len(markdown_files),
            "node_count": len(chunks),
            "kb_type_counts": dict(Counter(chunk.kb_type for chunk in chunks)),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        conn.executemany(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
            [(key, json.dumps(value, ensure_ascii=False)) for key, value in payload.items()],
        )

    def _missing_index_error(self) -> Optional[Dict[str, Any]]:
        reason = "PG knowledge base index is not built yet."
        if self.backend == "sqlite":
            if self.sqlite_path.exists() and self.manifest_path.exists():
                return None
        else:
            chroma_error = self._chroma_index_error()
            if chroma_error is None:
                return None
            reason = chroma_error

        command = (
            "conda run -n aiops python scripts/build_pg_knowledge_base.py "
            f"--backend {self.backend} "
            f"--knowledge-mode {self.knowledge_base_mode} "
            f"--source-dir {default_docs_dir(self.knowledge_base_mode)} "
            f"--persist-dir {self.persist_dir}"
        )
        return self._error(
            reason,
            build_command=command,
            backend=self.backend,
            persist_dir=str(self.persist_dir),
        )

    def _chroma_index_error(self) -> Optional[str]:
        if not self.persist_dir.exists() or not self.manifest_path.exists():
            return "PG Chroma knowledge base index is not built yet."
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "PG Chroma knowledge base manifest is missing or invalid."
        manifest_backend = manifest.get("backend")
        if manifest_backend and manifest_backend != "chroma":
            return f"PG knowledge base manifest backend is {manifest_backend}, expected chroma."
        manifest_model = manifest.get("embedding_model")
        if manifest_model and manifest_model != self.embed_model_name:
            return (
                "PG Chroma knowledge base was built with embedding model "
                f"{manifest_model}, expected {self.embed_model_name}."
            )
        return None

    def _error(self, error: str, **extra: Any) -> Dict[str, Any]:
        body = {"status": "error", "error": error}
        body.update(extra)
        return body

    def _delete_collection_if_exists(self, chroma_client: Any) -> None:
        try:
            chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass

    @staticmethod
    def _ensure_hf_endpoint() -> None:
        os.environ.setdefault("HF_ENDPOINT", default_hf_endpoint())

    def _write_manifest(self, stats: KnowledgeBuildStats, markdown_files: Sequence[Path]) -> None:
        payload = asdict(stats)
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        payload["file_count"] = len(markdown_files)
        payload["source_files"] = [str(path) for path in markdown_files]
        self.manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _normalize_backend(backend: str) -> str:
        normalized = (backend or DEFAULT_BACKEND).strip().lower()
        aliases = {
            "fts": "sqlite",
            "sqlite_fts": "sqlite",
            "vector": "chroma",
        }
        normalized = aliases.get(normalized, normalized)
        if normalized not in SUPPORTED_BACKENDS:
            raise ValueError(
                f"Unsupported PG knowledge backend: {backend}. "
                f"Supported backends: {', '.join(sorted(SUPPORTED_BACKENDS))}"
            )
        return normalized

    @staticmethod
    def _normalize_kb_type(kb_type: Optional[str]) -> Optional[str]:
        if kb_type is None:
            return None
        normalized = str(kb_type).strip().lower()
        if not normalized:
            return None
        if normalized in KNOWLEDGE_TYPES:
            return normalized
        return None

    @staticmethod
    def _coerce_int(value: Any, default: int, minimum: int, maximum: int) -> int:
        try:
            coerced = int(value)
        except (TypeError, ValueError):
            coerced = default
        return max(minimum, min(coerced, maximum))

    @staticmethod
    def _list_markdown_files(source_dir: Path) -> List[Path]:
        if not source_dir.exists():
            return []
        markdown_files = sorted(path for path in source_dir.rglob("*.md") if path.is_file())
        if source_dir.name == "pg":
            return [
                path
                for path in markdown_files
                if path.relative_to(source_dir).parts
                and path.relative_to(source_dir).parts[0] in KNOWLEDGE_TYPES
            ]
        return markdown_files

    @staticmethod
    def _metadata_for_file(file_path: Path, source_dir: Path) -> Dict[str, Any]:
        relative_path = file_path.relative_to(source_dir)
        parts = relative_path.parts
        title, headings = PGKnowledgeBase._extract_title_and_headings(file_path)
        kb_type = parts[0] if parts and parts[0] in KNOWLEDGE_TYPES else ""
        return {
            "file_path": str(file_path),
            "relative_path": str(relative_path),
            "part": parts[0] if parts else "",
            "kb_type": kb_type,
            "title": title or file_path.stem.replace("_", " "),
            "headings": headings[:20],
        }

    @staticmethod
    def _chroma_metadata_for_file(file_path: Path, source_dir: Path) -> Dict[str, Any]:
        metadata = PGKnowledgeBase._metadata_for_file(file_path, source_dir)
        headings = metadata.get("headings") or []
        if isinstance(headings, list):
            metadata["headings"] = " > ".join(str(item) for item in headings)
        return metadata

    @staticmethod
    def _extract_title_and_headings(file_path: Path) -> Tuple[str, List[str]]:
        headings: List[str] = []
        title = ""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped.startswith("#"):
                        continue
                    heading = PGKnowledgeBase._clean_heading(stripped.lstrip("#").strip())
                    if not heading:
                        continue
                    headings.append(heading)
                    if not title and stripped.startswith("# "):
                        title = heading
                    if len(headings) >= 20 and title:
                        break
        except OSError:
            return "", []
        return title, headings

    @staticmethod
    def _chunk_document(
        text: str,
        metadata: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[KnowledgeChunk]:
        relative_path = metadata.get("relative_path", "")
        sections = PGKnowledgeBase._split_markdown_sections(
            text,
            default_heading=metadata.get("title") or relative_path,
        )
        chunks: List[KnowledgeChunk] = []
        chunk_index = 0
        for heading_path, section_text in sections:
            blocks = PGKnowledgeBase._split_blocks(section_text)
            for content in PGKnowledgeBase._blocks_to_chunk_texts(blocks, chunk_size, chunk_overlap):
                normalized = content.strip()
                if not normalized:
                    continue
                chunk_index += 1
                chunk_id = PGKnowledgeBase._make_chunk_id(relative_path, chunk_index, normalized)
                chunks.append(KnowledgeChunk(
                    chunk_id=chunk_id,
                    source=relative_path,
                    file_path=metadata.get("file_path", ""),
                    title=metadata.get("title", ""),
                    part=metadata.get("part", ""),
                    kb_type=metadata.get("kb_type", ""),
                    headings=heading_path,
                    heading_path=" > ".join(heading_path),
                    chunk_index=chunk_index,
                    content=normalized,
                ))
        return chunks

    @staticmethod
    def _split_markdown_sections(text: str, default_heading: str) -> List[Tuple[List[str], str]]:
        sections: List[Tuple[List[str], str]] = []
        heading_stack: List[str] = [default_heading] if default_heading else []
        current_heading = heading_stack.copy()
        current_lines: List[str] = []
        in_code = False

        def flush() -> None:
            if current_lines:
                sections.append((current_heading.copy(), "\n".join(current_lines).strip()))

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code = not in_code
            match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if match and not in_code:
                flush()
                level = len(match.group(1))
                heading = PGKnowledgeBase._clean_heading(match.group(2))
                heading_stack = heading_stack[: max(level - 1, 0)]
                heading_stack.append(heading)
                current_heading = heading_stack.copy()
                current_lines = [line]
                continue
            current_lines.append(line)
        flush()

        return [(headings, body) for headings, body in sections if body]

    @staticmethod
    def _split_blocks(text: str) -> List[str]:
        blocks: List[str] = []
        current: List[str] = []
        in_code = False
        for line in text.splitlines():
            stripped = line.strip()
            fence = stripped.startswith("```") or stripped.startswith("~~~")
            if fence:
                in_code = not in_code
            if not stripped and not in_code:
                if current:
                    blocks.append("\n".join(current).strip())
                    current = []
                continue
            current.append(line)
        if current:
            blocks.append("\n".join(current).strip())
        return [block for block in blocks if block]

    @staticmethod
    def _blocks_to_chunk_texts(
        blocks: Sequence[str],
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        chunks: List[str] = []
        current: List[str] = []

        for block in blocks:
            if len(block) > chunk_size:
                if current:
                    chunks.append(PGKnowledgeBase._join_blocks(current))
                    current = PGKnowledgeBase._overlap_tail(current, chunk_overlap)
                chunks.extend(PGKnowledgeBase._split_long_text(block, chunk_size, chunk_overlap))
                continue

            candidate = current + [block]
            if current and len(PGKnowledgeBase._join_blocks(candidate)) > chunk_size:
                chunks.append(PGKnowledgeBase._join_blocks(current))
                current = PGKnowledgeBase._overlap_tail(current, chunk_overlap)
                candidate = current + [block]
                if current and len(PGKnowledgeBase._join_blocks(candidate)) > chunk_size:
                    current = []
            current.append(block)

        if current:
            chunks.append(PGKnowledgeBase._join_blocks(current))
        return chunks

    @staticmethod
    def _join_blocks(blocks: Sequence[str]) -> str:
        return "\n\n".join(block.strip() for block in blocks if block.strip()).strip()

    @staticmethod
    def _overlap_tail(blocks: Sequence[str], max_chars: int) -> List[str]:
        if max_chars <= 0:
            return []
        tail: List[str] = []
        total = 0
        for block in reversed(blocks):
            block_len = len(block) + (2 if tail else 0)
            if tail and total + block_len > max_chars:
                break
            if not tail and block_len > max_chars:
                return []
            tail.append(block)
            total += block_len
        return list(reversed(tail))

    @staticmethod
    def _split_long_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        if "\n" in text:
            return PGKnowledgeBase._split_long_lines(text, chunk_size, chunk_overlap)

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                split_at = text.rfind(" ", start, end)
                if split_at > start + chunk_size // 2:
                    end = split_at
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = max(end - chunk_overlap, start + 1)
        return chunks

    @staticmethod
    def _split_long_lines(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        chunks: List[str] = []
        current: List[str] = []

        for line in text.splitlines():
            if len(line) > chunk_size:
                if current:
                    chunks.append("\n".join(current).strip())
                    current = PGKnowledgeBase._line_overlap_tail(current, chunk_overlap)
                chunks.extend(PGKnowledgeBase._split_long_text(line, chunk_size, chunk_overlap))
                continue

            candidate = "\n".join(current + [line]).strip()
            if current and len(candidate) > chunk_size:
                chunks.append("\n".join(current).strip())
                current = PGKnowledgeBase._line_overlap_tail(current, chunk_overlap)
                candidate = "\n".join(current + [line]).strip()
                if current and len(candidate) > chunk_size:
                    current = []
            current.append(line)

        if current:
            chunks.append("\n".join(current).strip())
        return [chunk for chunk in chunks if chunk]

    @staticmethod
    def _line_overlap_tail(lines: Sequence[str], max_chars: int) -> List[str]:
        if max_chars <= 0:
            return []
        tail: List[str] = []
        total = 0
        for line in reversed(lines):
            line_len = len(line) + (1 if tail else 0)
            if tail and total + line_len > max_chars:
                break
            if not tail and line_len > max_chars:
                return []
            tail.append(line)
            total += line_len
        return list(reversed(tail))

    @staticmethod
    def _make_chunk_id(relative_path: str, chunk_index: int, content: str) -> str:
        digest = hashlib.sha1(f"{relative_path}\n{chunk_index}\n{content}".encode("utf-8")).hexdigest()
        return f"{relative_path}:{chunk_index}:{digest[:12]}"

    @staticmethod
    def _query_terms(query: str) -> List[str]:
        raw_terms = re.findall(r"[A-Za-z0-9_]+", query.lower())
        terms: List[str] = []
        seen = set()
        for term in raw_terms:
            candidates = [term]
            if "_" in term:
                candidates.extend(part for part in term.split("_") if part)
            for candidate in candidates:
                if len(candidate) <= 1 or candidate in seen:
                    continue
                seen.add(candidate)
                terms.append(candidate)
        return terms[:32]

    @staticmethod
    def _quote_fts_term(term: str) -> str:
        escaped = term.replace('"', '""')
        return f'"{escaped}"'

    @staticmethod
    def _clean_heading(heading: str) -> str:
        heading = re.sub(r"\s+", " ", heading).strip()
        return heading.rstrip("#").strip()

    @staticmethod
    def _json_loads(raw: str, default: Any) -> Any:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return default

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3].rstrip() + "..."
