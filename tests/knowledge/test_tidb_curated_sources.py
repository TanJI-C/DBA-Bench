"""Knowledge-asset contracts for the tracked TiDB curated corpus."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from scripts.merge_tidb_curated_knowledge import load_markdown_records
from src.project_paths import REPOSITORY_ROOT


def test_k09_raw_knowledge_source_is_generic_and_version_bound():
    root = REPOSITORY_ROOT / "knowledge" / "tidb" / "curated" / "tidb_dr_auto_sync"
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.md"))
    assert "K09" not in source_text
    assert "scenario_id" not in source_text
    assert "evaluator" not in source_text
    assert "Store ID" not in source_text
    assert "TiDB 8.1" in source_text


def test_k09_markdown_sources_enter_unified_merge_input():
    paths = {
        origin["path"]
        for _, origin in load_markdown_records()
        if origin["path"].startswith("knowledge/tidb/curated/tidb_dr_auto_sync/")
    }
    assert paths == {
        "knowledge/tidb/curated/tidb_dr_auto_sync/dr_auto_sync_state_machine_and_roles.md",
        "knowledge/tidb/curated/tidb_dr_auto_sync/endpoint_fencing_and_admission_evidence.md",
        "knowledge/tidb/curated/tidb_dr_auto_sync/online_unsafe_recovery_state_and_validation.md",
    }


def test_k01_knowledge_source_is_versioned_mechanism_only():
    source_root = REPOSITORY_ROOT / "knowledge" / "tidb" / "curated" / "tidb_system_failure_gc_mvcc_recovery"
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in sorted(source_root.glob("*.md")))

    assert "TiDB 8.1" in source_text
    assert "min_commit_ts > start_ts" in source_text
    assert "recover-mvcc" in source_text
    assert "bench_k01" not in source_text
    assert "k01_target_orders" not in source_text
    assert "region_id" not in source_text
    assert "Store ID" not in source_text
    assert "10001" not in source_text
    assert "9317" not in source_text

    serving_path = REPOSITORY_ROOT / "knowledge" / "tidb_unified" / "mappings" / "tidb81_serving_chunks.jsonl"
    records = [json.loads(line) for line in serving_path.read_text(encoding="utf-8").splitlines()]
    k01_records = [
        record for record in records
        if "recover-mvcc" in record["content"] or "min_commit_ts" in record["content"]
    ]
    assert k01_records
    assert all(not record["source_id"] and not record["source_file"] for record in k01_records)


def test_k01_unified_knowledge_materialization_has_stable_hashes():
    processed_path = REPOSITORY_ROOT / "knowledge/tidb_unified/mappings/tidb81_chunks.jsonl"
    serving_path = REPOSITORY_ROOT / "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
    manifest_path = REPOSITORY_ROOT / "knowledge/tidb_unified/manifests/tidb81_unified_manifest.json"
    records = [json.loads(line) for line in processed_path.read_text(encoding="utf-8").splitlines()]
    serving = [json.loads(line) for line in serving_path.read_text(encoding="utf-8").splitlines()]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(records) == len(serving) == manifest["layers"]["serving"]["record_count"]
    assert manifest["source_kinds"]["curated"] >= 3
    assert manifest["layers"]["processed"]["sha256"] == hashlib.sha256(processed_path.read_bytes()).hexdigest()
    assert manifest["layers"]["serving"]["sha256"] == hashlib.sha256(serving_path.read_bytes()).hexdigest()
    assert all(
        record["content_sha256"] == hashlib.sha256(record["content"].encode("utf-8")).hexdigest()
        for record in records + serving
    )


def test_k12_manifest_uses_unified_serving_contract_and_all_knowledge_hops():
    manifest_path = REPOSITORY_ROOT / "knowledge" / "tidb" / "curated" / "manifests" / (
        "tidb_system_failure_clustered_index_consistency.yaml"
    )
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    materialization = manifest["materialization"]
    assert materialization["formal_serving_corpus"] == (
        "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
    )
    assert materialization["formal_processed_corpus"] == (
        "knowledge/tidb_unified/mappings/tidb81_chunks.jsonl"
    )
    assert materialization["formal_provenance"] == (
        "knowledge/tidb_unified/provenance/tidb81_provenance.jsonl"
    )
    assert materialization["collection"] == "tidb81_unified_docs"
    assert materialization["no_private_agent_index"] is True
    assert materialization["no_fallback"] is True
    assert materialization["processed_record_count"] == 3571
    assert materialization["serving_record_count"] == 3571
    assert materialization["source_kind_counts"] == {"official": 3515, "curated": 56}
    assert {hop["hop_id"] for hop in manifest["hops"]} == {
        "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8",
    }
    for hop in manifest["hops"]:
        assert {
            "knowledge_question",
            "expected_concept",
            "version_scope",
            "required_environment_binding",
            "decision_changed",
            "counterfactual",
            "allowed_source_scope",
            "visible_evidence",
        } <= set(hop)
    assert not re.search(r"kb[_ ]?first", manifest_path.read_text(encoding="utf-8"), re.IGNORECASE)


def test_k12_raw_knowledge_has_no_run_fixture_or_evaluator_answer_leak():
    source_root = (
        REPOSITORY_ROOT
        / "knowledge"
        / "tidb"
        / "curated"
        / "tidb_system_failure_clustered_index_consistency"
    )
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(source_root.glob("*.md"))
    ).casefold()
    for forbidden in ("account 501", "account 502", "run_id", "tso", "evaluatorpass"):
        assert forbidden not in text
