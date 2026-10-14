from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.project_paths import REPOSITORY_ROOT
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase


PROJECT_ROOT = REPOSITORY_ROOT
CORPUS = PROJECT_ROOT / "knowledge" / "tidb" / "mappings" / "tidb81_chunks.jsonl"
SERVING_CORPUS = PROJECT_ROOT / "knowledge" / "tidb_unified" / "mappings" / "tidb81_serving_chunks.jsonl"


@pytest.fixture(scope="module")
def indexed_corpus(tmp_path_factory):
    assert CORPUS.is_file(), f"Materialized TiDB corpus is missing: {CORPUS}"
    persist_dir = tmp_path_factory.mktemp("tidb81-retrieval") / "sqlite"
    kb = TiDBKnowledgeBase(
        persist_dir=persist_dir,
        backend="sqlite",
        knowledge_base_mode="hierarchical",
        source_file=CORPUS,
    )
    stats = kb.build()
    assert stats["status"] == "success"
    return kb


@pytest.mark.parametrize(
    ("kb_type", "query"),
    (
        ("architecture", "raft leader transfer region scheduling tso mvcc"),
        ("configuration", "tidb_server_memory_limit tidb_mem_oom_action"),
        ("observability", "pending-peer-region-count slow query Top SQL"),
        ("diagnosis", "TiCDC checkpoint lag changefeed stopped"),
        ("operation", "interrupted rolling restart evict-leader scheduler"),
        ("performance", "index merge selection explain analyze memory spill"),
        ("recovery", "BR PITR log backup checkpoint majority replica loss"),
        ("data_pipeline", "TiCDC downstream DDL time zone DM shard DDL lock"),
        ("reference", "information_schema.cluster_config tidb_trx error code"),
        ("release", "introduced deprecated changed in TiDB 8.1"),
    ),
)
def test_representative_query_retrieves_the_requested_category(
    indexed_corpus,
    kb_type,
    query,
):
    result = indexed_corpus.query(
        query,
        source_scope="all",
        kb_type=kb_type,
        top_k=10,
        max_chars_per_result=600,
    )
    assert result["count"] > 0, (kb_type, query)
    assert {item["kb_type"] for item in result["results"]} == {kb_type}
    assert all(item["version"] == "8.1" for item in result["results"])
    assert all(
        item["pinned_source_url"].startswith(
            "https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/"
        )
        for item in result["results"]
    )


def test_materialized_corpus_has_no_benchmark_specific_leakage():
    forbidden = ("aiopsbench", "scenario_id", "case_id", "evaluator keyword")
    for line_number, line in enumerate(CORPUS.read_text(encoding="utf-8").splitlines(), 1):
        record = json.loads(line)
        serialized = json.dumps(record, ensure_ascii=False).casefold()
        assert all(token not in serialized for token in forbidden), (
            line_number,
            record["chunk_id"],
        )
        assert record["version"] == "8.1"
        assert record["content"].strip()


def test_unified_serving_corpus_has_no_provenance_or_scenario_leakage():
    assert SERVING_CORPUS.is_file(), f"Unified serving corpus is missing: {SERVING_CORPUS}"
    forbidden = (
        "aiopsbench", "scenario_id", "case_id", "source_kind", "source_origin",
        "knowledge/tidb/curated", "docs/scenarios", "benchmark case",
    )
    required = {
        "chunk_id", "title", "kb_type", "component", "source_scope", "version", "content",
    }
    for line_number, line in enumerate(SERVING_CORPUS.read_text(encoding="utf-8").splitlines(), 1):
        record = json.loads(line)
        assert required <= set(record), (line_number, sorted(set(record)))
        serialized = json.dumps(record, ensure_ascii=False).casefold()
        assert all(token not in serialized for token in forbidden), (
            line_number,
            record["chunk_id"],
        )
        assert record["version"] == "8.1"
        assert not record["source_id"]
        assert not record["source_file"]
        assert not record["source_url"]
        assert not record["pinned_source_url"]


def test_unified_serving_corpus_contains_ticdc_gc_safepoint_knowledge():
    expected_titles = {
        "TiCDC progress state after a capture restart",
        "TiCDC service GC safepoint ownership and cleanup",
        "TiCDC progress and TiKV MVCC recovery scope",
        "Joint TiCDC and GC recovery verification",
    }
    records = [
        json.loads(line)
        for line in SERVING_CORPUS.read_text(encoding="utf-8").splitlines()
    ]
    selected = {record["title"]: record for record in records if record["title"] in expected_titles}
    assert set(selected) == expected_titles
    for record in selected.values():
        assert record["version"] == "8.1"
        assert record["component"] in {"ticdc", "tikv"}
        assert record["source_scope"] == "self_managed"
        assert record["content"].strip()
        assert not record["source_id"]
        assert not record["source_file"]
        assert not record["source_url"]
        assert not record["pinned_source_url"]
