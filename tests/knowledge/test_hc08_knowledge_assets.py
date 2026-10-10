from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from src.project_paths import REPOSITORY_ROOT
from src.knowledge.tidb_knowledge_base import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_HIERARCHICAL_SQLITE_DIR,
    DEFAULT_HIERARCHICAL_SOURCE_FILE,
)


ROOT = REPOSITORY_ROOT
SOURCE_DIR = ROOT / "knowledge/tidb/curated/tidb_health_check_placement_policy"
SOURCE_FILE = SOURCE_DIR / "tidb81_hc08_chunks.jsonl"
SOURCE_MANIFEST = SOURCE_DIR / ".source-manifest.json"
SCENARIO_MANIFEST = ROOT / "knowledge/tidb/curated/manifests/tidb_health_check_placement_policy.yaml"
UNIFIED_MANIFEST = ROOT / "knowledge/tidb_unified/manifests/tidb81_unified_manifest.json"
PROCESSED_SOURCE = ROOT / "knowledge/tidb_unified/mappings/tidb81_chunks.jsonl"
SERVING_SOURCE = ROOT / "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
PROVENANCE_SOURCE = ROOT / "knowledge/tidb_unified/provenance/tidb81_provenance.jsonl"
SQLITE_MANIFEST = ROOT / "data/knowledge_bases/tidb81_unified_docs/manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_hc08_source_manifest_matches_tracked_corpus():
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    files = {item["path"]: item["sha256"] for item in manifest["files"]}

    assert files["tidb81_hc08_chunks.jsonl"] == sha256(SOURCE_FILE)
    assert files["placement_policy_inheritance.md"] == sha256(
        SOURCE_DIR / "placement_policy_inheritance.md"
    )
    assert files["placement_policy_constraints_and_progress.md"] == sha256(
        SOURCE_DIR / "placement_policy_constraints_and_progress.md"
    )
    assert files["placement_policy_review_safety.md"] == sha256(
        SOURCE_DIR / "placement_policy_review_safety.md"
    )
    assert f"source_sha256: {files['tidb81_hc08_chunks.jsonl']}" in SCENARIO_MANIFEST.read_text(
        encoding="utf-8"
    )


def test_hc08_raw_records_are_in_the_unified_processed_and_serving_layers():
    assert UNIFIED_MANIFEST.is_file(), f"Unified manifest is missing: {UNIFIED_MANIFEST}"
    assert PROCESSED_SOURCE.is_file(), f"Processed corpus is missing: {PROCESSED_SOURCE}"
    assert SERVING_SOURCE.is_file(), f"Serving corpus is missing: {SERVING_SOURCE}"
    assert PROVENANCE_SOURCE.is_file(), f"Provenance sidecar is missing: {PROVENANCE_SOURCE}"

    raw_records = [json.loads(line) for line in SOURCE_FILE.read_text(encoding="utf-8").splitlines()]
    processed_records = [json.loads(line) for line in PROCESSED_SOURCE.read_text(encoding="utf-8").splitlines()]
    serving_records = [json.loads(line) for line in SERVING_SOURCE.read_text(encoding="utf-8").splitlines()]
    provenance_records = [json.loads(line) for line in PROVENANCE_SOURCE.read_text(encoding="utf-8").splitlines()]

    raw_origin_ids = {record["source_id"] for record in raw_records}
    processed_hc08 = [
        record
        for record in processed_records
        if record.get("source_origin_id") in raw_origin_ids
    ]
    assert len(processed_hc08) == len(raw_records)
    assert {record["chunk_id"] for record in processed_hc08} <= {
        record["chunk_id"] for record in serving_records
    }
    assert {record["chunk_id"] for record in processed_hc08} <= {
        record["chunk_id"] for record in provenance_records
    }
    assert {record["title"] for record in raw_records} <= {
        record["title"] for record in serving_records
    }
    for record in processed_hc08:
        assert record["source_kind"] == "curated"
        assert record["source_origin_path"].endswith("tidb_health_check_placement_policy/tidb81_hc08_chunks.jsonl")
    for record in serving_records:
        assert not record["source_id"]
        assert not record["source_file"]
        assert not record["source_url"]
        assert not record["pinned_source_url"]

    unified_manifest = json.loads(UNIFIED_MANIFEST.read_text(encoding="utf-8"))
    assert unified_manifest["source_kinds"]["curated"] >= len(raw_records)
    assert unified_manifest["layers"]["processed"]["sha256"] == sha256(PROCESSED_SOURCE)
    assert unified_manifest["layers"]["serving"]["sha256"] == sha256(SERVING_SOURCE)
    assert unified_manifest["provenance_sha256"] == sha256(PROVENANCE_SOURCE)


@pytest.mark.skipif(not SQLITE_MANIFEST.exists(),
                    reason="the generated sqlite index under data/knowledge_bases is built on demand and is not distributed")
def test_hc08_uses_the_shared_hierarchical_index_contract():
    assert DEFAULT_HIERARCHICAL_SOURCE_FILE == Path(
        "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
    )
    assert DEFAULT_HIERARCHICAL_SQLITE_DIR == Path("data/knowledge_bases/tidb81_unified_docs")
    assert DEFAULT_COLLECTION_NAME == "tidb81_unified_docs"

    index_manifest = json.loads(SQLITE_MANIFEST.read_text(encoding="utf-8"))
    assert index_manifest["knowledge_base_mode"] == "hierarchical"
    assert index_manifest["collection_name"] == DEFAULT_COLLECTION_NAME
    assert index_manifest["source_file"] == SERVING_SOURCE.relative_to(ROOT).as_posix()
    assert index_manifest["materialized_corpus_sha256"] == sha256(SERVING_SOURCE)
    scenario_manifest = SCENARIO_MANIFEST.read_text(encoding="utf-8")
    assert not re.search(r"kb[_ ]?first", scenario_manifest, re.IGNORECASE)
    assert "raw_source_file:" in scenario_manifest
    assert "serving_source_file: knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl" in scenario_manifest
