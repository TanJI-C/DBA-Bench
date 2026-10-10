#!/usr/bin/env python3
"""Build an explicit SQLite or Chroma TiDB 8.1 knowledge index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT  # noqa: E402
from src.knowledge.markdown_knowledge_base import KnowledgeBaseDependencyError  # noqa: E402
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase  # noqa: E402


PROJECT_ROOT = REPOSITORY_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["sqlite", "chroma"], required=True)
    parser.add_argument(
        "--knowledge-mode",
        choices=["general", "hierarchical"],
        required=True,
    )
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--persist-dir", type=Path)
    parser.add_argument("--collection", default="tidb81_unified_docs")
    parser.add_argument("--embedding-model", default="Qwen/Qwen3-Embedding-4B")
    parser.add_argument("--embedding-device", default="cpu")
    parser.add_argument("--embedding-batch-size", type=int, default=1)
    parser.add_argument("--embedding-workers", type=int, default=1)
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--no-progress", action="store_true")
    parser.add_argument(
        "--verify-query",
        default="tidb_server_memory_limit tidb_mem_oom_action",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    kb = TiDBKnowledgeBase(
        persist_dir=args.persist_dir,
        collection_name=args.collection,
        embed_model_name=args.embedding_model,
        embed_device=args.embedding_device,
        embed_batch_size=args.embedding_batch_size,
        embed_workers=args.embedding_workers,
        backend=args.backend,
        knowledge_base_mode=args.knowledge_mode,
        source_file=args.source_file,
    )
    try:
        stats = kb.build(
            source_file=args.source_file,
            reset_collection=not args.append,
            show_progress=not args.no_progress,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        if args.verify_query:
            result = kb.query(
                args.verify_query,
                source_scope="all",
                top_k=3,
                max_chars_per_result=600,
            )
            print(json.dumps({"verify_query": result}, ensure_ascii=False, indent=2))
    except KnowledgeBaseDependencyError as exc:
        print(json.dumps(
            {"status": "error", "error": str(exc)},
            ensure_ascii=False,
            indent=2,
        ))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
