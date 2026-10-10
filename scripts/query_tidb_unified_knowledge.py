#!/usr/bin/env python3
"""Query the TiDB 8.1 unified serving knowledge base.

The default target is the final Chroma serving index built from
``knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl``.  Chroma
queries use the shared local embedding service; the first request starts the
service in the background when it is absent and rejects a different model.
SQLite is available only when selected explicitly with ``--backend sqlite``.

Examples::

    conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
        --query "Online Unsafe Recovery failed stores Finished"

    conda run -n aiops python scripts/query_tidb_unified_knowledge.py \
        --query "alloc-id recovery high-water" \
        --top-k 10 --kb-type recovery --component pd --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import SHARED_REPOSITORY_ROOT  # noqa: E402
from src.knowledge.document_processing.schemas import (  # noqa: E402
    COMPONENTS,
    KNOWLEDGE_CATEGORIES,
    RETRIEVAL_SCOPES,
)
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase  # noqa: E402


PROJECT_ROOT = SHARED_REPOSITORY_ROOT


COLLECTION_NAME = "tidb81_unified_docs"
SERVING_SOURCE = PROJECT_ROOT / "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
CHROMA_DIR = PROJECT_ROOT / "data/knowledge_bases/tidb81_unified_chroma"
SQLITE_DIR = PROJECT_ROOT / "data/knowledge_bases/tidb81_unified_docs"
DEFAULT_EMBEDDING_URL = os.environ.get(
    "AIOPS_EMBEDDING_MODEL_URL", "http://127.0.0.1:8765"
).rstrip("/")
DEFAULT_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-4B"
AGENT_RESULT_FIELDS = (
    "rank",
    "score",
    "title",
    "version",
    "kb_type",
    "component",
    "source_scope",
    "content",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        required=True,
        help="Natural-language question or TiDB identifier to search for.",
    )
    parser.add_argument(
        "--backend",
        choices=("chroma", "sqlite"),
        default="chroma",
        help="Serving index backend. Defaults to the GPU-backed Chroma index.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (1-20; default: 5).",
    )
    parser.add_argument(
        "--source-scope",
        choices=sorted(RETRIEVAL_SCOPES),
        default="all",
        help="Documentation scope filter (default: all).",
    )
    parser.add_argument(
        "--kb-type",
        choices=sorted(KNOWLEDGE_CATEGORIES),
        help="Optional knowledge category filter.",
    )
    parser.add_argument(
        "--component",
        choices=sorted(COMPONENTS),
        help="Optional TiDB component filter.",
    )
    parser.add_argument(
        "--max-chars-per-result",
        type=int,
        default=1600,
        help="Maximum content characters per result (200-8000; default: 1600).",
    )
    parser.add_argument(
        "--embedding-url",
        default=DEFAULT_EMBEDDING_URL,
        help=(
            "Embedding service base URL for Chroma (default: "
            f"{DEFAULT_EMBEDDING_URL})."
        ),
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help=(
            "Embedding model name expected from the service (default: "
            f"{DEFAULT_EMBEDDING_MODEL})."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit source-neutral JSON instead of the human-readable view.",
    )
    return parser.parse_args()


def configured_knowledge_base(args: argparse.Namespace) -> TiDBKnowledgeBase:
    if not SERVING_SOURCE.is_file():
        raise FileNotFoundError(
            f"Unified TiDB serving corpus is missing: source_file={SERVING_SOURCE}"
        )

    if args.backend == "chroma":
        embedding_url = args.embedding_url.rstrip("/")
        if not embedding_url:
            raise ValueError("Embedding service URL must not be empty: --embedding-url")
        os.environ["AIOPS_EMBEDDING_MODEL_URL"] = embedding_url
        # The final serving setup has one Agent-facing endpoint. Do not let a
        # caller's old multi-endpoint environment redirect this query.
        os.environ.pop("AIOPS_EMBEDDING_MODEL_URLS", None)

    return TiDBKnowledgeBase(
        persist_dir=CHROMA_DIR if args.backend == "chroma" else SQLITE_DIR,
        collection_name=COLLECTION_NAME,
        backend=args.backend,
        knowledge_base_mode="hierarchical",
        source_file=SERVING_SOURCE,
        embed_model_name=args.embedding_model,
        embed_device="cuda",
    )


def agent_result(row: dict[str, Any]) -> dict[str, Any]:
    """Return only fields exposed by the Agent-facing knowledge tool."""

    return {field: row[field] for field in AGENT_RESULT_FIELDS}


def run_query(args: argparse.Namespace) -> dict[str, Any]:
    knowledge_base = configured_knowledge_base(args)
    started = time.perf_counter()
    result = knowledge_base.query(
        args.query,
        source_scope=args.source_scope,
        top_k=args.top_k,
        kb_type=args.kb_type,
        component=args.component,
        max_chars_per_result=args.max_chars_per_result,
    )
    latency_ms = (time.perf_counter() - started) * 1000
    if result["status"] != "success":
        raise RuntimeError(f"TiDB knowledge query returned a non-success status: result={result!r}")
    return {
        "status": "success",
        "query": result["query"],
        "latency_ms": round(latency_ms, 3),
        "count": result["count"],
        "results": [agent_result(row) for row in result["results"]],
    }


def print_human(payload: dict[str, Any]) -> None:
    print(f"Query: {payload['query']}")
    print(f"Latency: {payload['latency_ms']:.3f} ms")
    print(f"Results: {payload['count']}")
    for row in payload["results"]:
        print(
            f"\n[{row['rank']}] {row['title']} "
            f"(score={row['score']:.6f}, version={row['version']}, "
            f"kb_type={row['kb_type']}, component={row['component']}, "
            f"source_scope={row['source_scope']})"
        )
        print(row["content"])


def main() -> int:
    args = parse_args()
    try:
        payload = run_query(args)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
