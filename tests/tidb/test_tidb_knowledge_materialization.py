from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialize_tidb_hierarchical_knowledge import (
    collect_chunks,
    publish_corpus,
)
from src.knowledge.document_processing.source_manifest import (
    sha256_bytes,
    write_source_manifest,
)


SOURCE_LOCK = {
    "corpus_id": "tidb-official-docs-8.1-en",
    "commit": "d9124e84872b8f9915123444ab4402f9a36c33c9",
    "website_base_url": "https://docs.pingcap.com/tidb/stable",
    "github_blob_base_url": "https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9",
}


def fixture(tmp_path: Path, *, state: str = "completed", needs_review: bool = False):
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    source_text = "# Memory Control\n\nSet `tidb_mem_quota_query` for one query.\n"
    source_file = "configure-memory-usage.md"
    (source_dir / source_file).write_text(source_text, encoding="utf-8")
    write_source_manifest(source_dir, SOURCE_LOCK["corpus_id"])
    source_hash = sha256_bytes(source_text.encode("utf-8"))
    inventory = [{
        "source_file": source_file,
        "source_sha256": source_hash,
        "frontmatter_title": None,
        "frontmatter_summary": None,
        "toc_membership": ["TOC.md"],
        "document_scope": "self_managed",
        "processing_status": "included",
        "exclusion_reason": None,
    }]
    processing_run = tmp_path / "run"
    (processing_run / "states").mkdir(parents=True)
    processing_manifest = {
        "run_id": "fixture",
        "source_commit": SOURCE_LOCK["commit"],
        "model": "fixture-model",
        "split_prompt_sha256": "1" * 64,
        "enrich_prompt_sha256": "2" * 64,
        "completed_count": 1 if state == "completed" else 0,
        "failed_count": 0 if state == "completed" else 1,
    }
    state_payload = {
        "source_file": source_file,
        "source_sha256": source_hash,
        "inventory_input_sha256": sha256_bytes(
            json.dumps(inventory[0], sort_keys=True).encode("utf-8")
        ),
        "state": state,
        "model": "fixture-model",
        "split_prompt_sha256": "1" * 64,
        "enrich_prompt_sha256": "2" * 64,
        "groups": [{
            "group_number": 1,
            "units": [{
                "unit_id": "u00001",
                "heading_path": "Memory Control",
                "start_line": 1,
                "end_line": 3,
                "text": source_text,
                "token_count": 20,
                "indivisible": False,
            }],
            "chunks": [{
                "unit_ids": ["u00001"],
                "heading_paths": ["Memory Control"],
                "title": "Configure Query Memory Quota",
                "primary_category": "configuration",
                "primary_component": "tidb",
                "related_components": [],
                "deployment_scope": "self_managed",
                "topic_tags": ["memory", "system_variable"],
                "classification_reason": "Defines query memory quota behavior.",
                "needs_human_review": needs_review,
                "chunk_key": "g0001c0001",
                "enrichment": {
                    "use_when": "Use when configuring TiDB query memory quota.",
                    "retrieval_keywords": ["tidb_mem_quota_query"],
                    "follow_up": "Check the active session value.",
                    "classification_note": "Defines a TiDB memory system variable.",
                },
            }],
        }],
    }
    if state != "completed":
        state_payload["error"] = {"type": "FixtureError", "message": "failed"}
    (processing_run / "states" / "state.json").write_text(
        json.dumps(state_payload), encoding="utf-8",
    )
    return source_dir, inventory, processing_run, processing_manifest


def materialize(tmp_path: Path, output_name: str = "tidb") -> Path:
    source_dir, inventory, processing_run, manifest = fixture(tmp_path)
    chunks, review_queue = collect_chunks(
        source_dir, inventory, processing_run, SOURCE_LOCK,
    )
    output = tmp_path / output_name
    publish_corpus(
        output,
        source_dir,
        inventory,
        manifest,
        chunks,
        review_queue,
        {},
        SOURCE_LOCK,
        processing_run / "review_queue.json",
    )
    return output


def test_materialization_writes_markdown_json_mappings_and_jsonl(tmp_path):
    output = materialize(tmp_path)

    jsonl_path = output / "mappings" / "tidb81_chunks.jsonl"
    records = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    record = records[0]
    assert record["chunk_id"].startswith("tidb81_configuration_0001_")
    assert record["source_line_ranges"] == [{"start": 1, "end": 3}]
    assert record["content_sha256"] == sha256_bytes(record["content"].encode("utf-8"))
    markdown_path = next((output / "configuration").glob("*.md"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "## Official Source Content" in markdown
    assert "tidb_mem_quota_query" in markdown
    assert "Processing Model" not in markdown
    assert "Processing Prompt" not in markdown
    assert "fixture-model" not in markdown
    assert (output / "ATTRIBUTION.md").is_file()


def test_materialization_chunk_ids_are_deterministic(tmp_path):
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    first_record = json.loads((first / "mappings" / "tidb81_chunks.jsonl").read_text().strip())
    second_record = json.loads((second / "mappings" / "tidb81_chunks.jsonl").read_text().strip())
    assert first_record["chunk_id"] == second_record["chunk_id"]


def test_materialization_refuses_partial_processing_without_replacing_output(tmp_path):
    source_dir, inventory, processing_run, _ = fixture(tmp_path, state="failed")
    output = tmp_path / "tidb"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(ValueError, match="partial TiDB corpus"):
        collect_chunks(source_dir, inventory, processing_run, SOURCE_LOCK)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_materialization_requires_explicit_review_resolution(tmp_path):
    source_dir, inventory, processing_run, manifest = fixture(tmp_path, needs_review=True)
    chunks, review_queue = collect_chunks(
        source_dir, inventory, processing_run, SOURCE_LOCK,
    )
    output = tmp_path / "tidb"
    pending = processing_run / "review_queue.json"

    with pytest.raises(ValueError, match="review is incomplete"):
        publish_corpus(
            output,
            source_dir,
            inventory,
            manifest,
            chunks,
            review_queue,
            {},
            SOURCE_LOCK,
            pending,
        )
    assert not output.exists()
    queue = json.loads(pending.read_text(encoding="utf-8"))
    assert queue["unresolved_count"] == 1
