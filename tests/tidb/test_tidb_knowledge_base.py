from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from src.knowledge.markdown_knowledge_base import KnowledgeBuildStats
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase, default_source_file


def write_corpus(path: Path) -> Path:
    path.parent.mkdir(parents=True)
    records = [
        {
            "chunk_id": "tidb81_configuration_0001_aaaaaaaaaa",
            "source_id": "tidb-docs-8.1:configure-memory-usage.md#query-memory",
            "title": "Configure Query Memory Quota",
            "kb_type": "configuration",
            "component": "tidb",
            "related_components": [],
            "source_scope": "self_managed",
            "topic_tags": ["memory", "oom"],
            "version": "8.1",
            "source_file": "configure-memory-usage.md",
            "source_heading_path": "TiDB Memory Control > Query memory",
            "source_line_ranges": [{"start": 20, "end": 47}],
            "source_url": "https://docs.pingcap.com/tidb/stable/configure-memory-usage#query-memory",
            "pinned_source_url": "https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md",
            "use_when": "Use when a TiDB query reaches its memory quota.",
            "retrieval_keywords": ["tidb_mem_quota_query", "tidb_mem_oom_action"],
            "follow_up": "Check the configured OOM action.",
            "content": "tidb_mem_quota_query limits query memory and tidb_mem_oom_action controls the OOM action.\n",
            "content_sha256": "",
        },
        {
            "chunk_id": "tidb81_diagnosis_0001_bbbbbbbbbb",
            "source_id": "tidb-docs-8.1:ticdc/troubleshoot.md#checkpoint-lag",
            "title": "Troubleshoot TiCDC Checkpoint Lag",
            "kb_type": "diagnosis",
            "component": "ticdc",
            "related_components": ["tikv"],
            "source_scope": "shared",
            "topic_tags": ["cdc", "checkpoint"],
            "version": "8.1",
            "source_file": "ticdc/troubleshoot.md",
            "source_heading_path": "Troubleshoot TiCDC > Checkpoint lag",
            "source_line_ranges": [{"start": 10, "end": 30}],
            "source_url": "https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot#checkpoint-lag",
            "pinned_source_url": "https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/troubleshoot.md",
            "use_when": "Use when a TiCDC changefeed checkpoint does not advance.",
            "retrieval_keywords": ["checkpoint-ts", "changefeed stopped"],
            "follow_up": "Check TiCDC and TiKV health.",
            "content": "Inspect checkpoint-ts when a TiCDC changefeed is stopped or lagging.\n",
            "content_sha256": "",
        },
    ]
    for record in records:
        record["content_sha256"] = hashlib.sha256(record["content"].encode()).hexdigest()
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    return path


def sqlite_kb(tmp_path: Path):
    source = write_corpus(tmp_path / "mappings" / "tidb81_chunks.jsonl")
    kb = TiDBKnowledgeBase(
        persist_dir=tmp_path / "index",
        backend="sqlite",
        knowledge_base_mode="hierarchical",
        source_file=source,
    )
    return source, kb


def test_sqlite_build_exact_identifier_retrieval_and_filters(tmp_path):
    _, kb = sqlite_kb(tmp_path)
    stats = kb.build()
    result = kb.query(
        "tidb_mem_quota_query tidb_mem_oom_action",
        source_scope="self_managed",
        kb_type="configuration",
        component="tidb",
        top_k=5,
    )
    assert stats["backend"] == "sqlite"
    assert stats["document_count"] == 2
    assert stats["node_count"] == 2
    assert result["count"] == 1
    assert result["results"][0]["source_id"].endswith("#query-memory")
    assert result["results"][0]["pinned_source_url"].startswith(
        "https://github.com/pingcap/docs/blob/d9124e"
    )
    assert result["index"]["backend"] == "sqlite"


def test_shared_scope_record_is_visible_to_specific_scope_and_component_filter(tmp_path):
    _, kb = sqlite_kb(tmp_path)
    kb.build()
    result = kb.query(
        "checkpoint-ts changefeed",
        source_scope="self_managed",
        kb_type="diagnosis",
        component="tikv",
    )
    assert result["count"] == 1
    assert result["results"][0]["component"] == "ticdc"


def test_repository_manifest_survives_checkout_relocation(tmp_path, monkeypatch):
    from src import project_paths
    from src.knowledge import markdown_knowledge_base

    root = tmp_path / "checkout"
    monkeypatch.setattr(project_paths, "SHARED_REPOSITORY_ROOT", root)
    monkeypatch.setattr(markdown_knowledge_base, "SHARED_REPOSITORY_ROOT", root)
    source, kb = sqlite_kb(root)
    stats = kb.build()
    assert stats["source_file"] == source.relative_to(root).as_posix()
    assert stats["persist_dir"] == "index"
    assert stats["manifest_path"] == "index/manifest.json"
    assert stats["database_path"] == f"index/{kb.collection_name}.sqlite3"

    relocated = tmp_path / "relocated"
    root.rename(relocated)
    monkeypatch.setattr(project_paths, "SHARED_REPOSITORY_ROOT", relocated)
    monkeypatch.setattr(markdown_knowledge_base, "SHARED_REPOSITORY_ROOT", relocated)
    moved_kb = TiDBKnowledgeBase(
        persist_dir=relocated / "index", backend="sqlite", knowledge_base_mode="hierarchical"
    )
    result = moved_kb.query("tidb_mem_quota_query", source_scope="self_managed")
    assert result["count"] == 1
    assert result["results"][0]["source_id"].endswith("#query-memory")


def test_external_corpus_manifest_preserves_absolute_path(tmp_path):
    source, kb = sqlite_kb(tmp_path)
    assert kb.build()["source_file"] == str(source)
    assert kb._validated_manifest()["source_file"] == str(source)


def test_query_rejects_stale_materialized_corpus(tmp_path):
    source, kb = sqlite_kb(tmp_path)
    kb.build()
    source.write_text(source.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Stale knowledge index corpus hash"):
        kb.query("tidb_mem_quota_query", source_scope="all")


def test_backend_selection_is_explicit():
    with pytest.raises(ValueError, match="Unsupported .*knowledge backend"):
        TiDBKnowledgeBase(backend="automatic", knowledge_base_mode="hierarchical")


def test_general_and_hierarchical_sources_are_distinct():
    assert default_source_file("general").name == "tidb_src"
    assert default_source_file("hierarchical").name == "tidb81_serving_chunks.jsonl"
    assert default_source_file("hierarchical").relative_to(
        default_source_file("hierarchical").parents[3]
    ).as_posix() == "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"


def test_hierarchical_defaults_use_the_shared_unified_index():
    kb = TiDBKnowledgeBase(backend="sqlite", knowledge_base_mode="hierarchical")

    assert kb.default_source_file.name == "tidb81_serving_chunks.jsonl"
    assert kb.default_source_file.parts[-4:] == (
        "knowledge", "tidb_unified", "mappings", "tidb81_serving_chunks.jsonl",
    )
    assert kb.persist_dir.parts[-2:] == ("knowledge_bases", "tidb81_unified_docs")
    assert "k01_extended" not in str(kb.persist_dir)


def test_linked_worktree_resolves_assets_from_git_common_directory():
    worktree_root = Path(__file__).resolve().parents[2]
    common_dir = Path(subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=worktree_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip())
    if not common_dir.is_absolute():
        common_dir = worktree_root / common_dir
    expected_root = common_dir.resolve().parent
    assert default_source_file("hierarchical").is_relative_to(expected_root)


def test_chroma_query_failure_does_not_fall_back_to_sqlite(tmp_path, monkeypatch):
    source = write_corpus(tmp_path / "mappings" / "tidb81_chunks.jsonl")
    kb = TiDBKnowledgeBase(
        persist_dir=tmp_path / "chroma",
        backend="chroma",
        knowledge_base_mode="hierarchical",
        source_file=source,
    )
    monkeypatch.setattr(kb, "_validated_manifest", lambda: {
        "materialized_corpus_sha256": "x",
        "source_commit": "d9124e84872b8f9915123444ab4402f9a36c33c9",
    })

    def fail(*args, **kwargs):
        raise RuntimeError("chroma query failed")

    monkeypatch.setattr(kb, "_query_chroma", fail)
    with pytest.raises(RuntimeError, match="chroma query failed"):
        kb.query("checkpoint lag", source_scope="all")


def test_chroma_build_writes_manifest_with_backend_and_embedding_model(tmp_path, monkeypatch):
    source = write_corpus(tmp_path / "mappings" / "tidb81_chunks.jsonl")
    kb = TiDBKnowledgeBase(
        persist_dir=tmp_path / "chroma",
        backend="chroma",
        knowledge_base_mode="hierarchical",
        source_file=source,
    )

    def fake_build(source_path, records, reset_collection, show_progress):
        return KnowledgeBuildStats(
            status="success",
            source_file=str(source_path),
            persist_dir=str(kb.persist_dir),
            collection_name=kb.collection_name,
            knowledge_base_mode=kb.knowledge_base_mode,
            backend="chroma",
            embedding_model=kb.embed_model_name,
            document_count=2,
            node_count=2,
            manifest_path=str(kb.manifest_path),
            database_path=None,
        )

    monkeypatch.setattr(kb, "_build_chroma", fake_build)
    kb.build()
    manifest = json.loads(kb.manifest_path.read_text())
    assert manifest["backend"] == "chroma"
    assert manifest["embedding_model"] == "Qwen/Qwen3-Embedding-4B"
    assert manifest["node_count"] == 2
