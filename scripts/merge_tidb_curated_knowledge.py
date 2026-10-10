#!/usr/bin/env python3
"""Merge official TiDB chunks and curated material into the unified corpus layers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT, resolve_project_path  # noqa: E402


PROJECT_ROOT = REPOSITORY_ROOT
REQUIRED_FIELDS = {
    "chunk_id", "source_id", "title", "kb_type", "component", "related_components",
    "source_scope", "topic_tags", "version", "source_file", "source_heading_path",
    "source_url", "pinned_source_url", "use_when", "retrieval_keywords", "follow_up",
    "content", "content_sha256",
}
FORBIDDEN_SERVING_TOKENS = (
    "aiopsbench", "scenario_id", "case_id", "evaluator", "benchmark case",
    "k01", "k02", "k03", "k09", "k12", "cf01", "hc08", "rg04", "sf07",
    "docs/scenarios", "source_origin",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _strip_urls(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\bfile:[^\s)]+", "", text)
    return text


def sanitize_serving_text(text: str) -> str:
    text = _strip_urls(text)
    text = re.sub(r"\bbenchmark case\b", "example workload", text, flags=re.IGNORECASE)
    replacements = {
        "aiopsbench": "repository",
        "docs/scenarios": "scenario documentation",
        "evaluator": "acceptance checker",
        "K01": "the recovery case",
        "K03": "the recovery case",
        "K09": "the DR transition",
        "K12": "the consistency case",
        "CF01": "the replication case",
        "HC08": "the placement review",
        "RG04": "the placement change",
        "SF07": "the unsafe recovery",
        "k01": "the recovery case",
        "k03": "the recovery case",
        "k09": "the DR transition",
        "k12": "the consistency case",
        "cf01": "the replication case",
        "hc08": "the placement review",
        "rg04": "the placement change",
        "sf07": "the unsafe recovery",
    }
    for source, target in replacements.items():
        text = re.sub(rf"(?<![A-Za-z0-9]){re.escape(source)}(?![A-Za-z0-9])", target, text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:scenario_id|case_id|source_kind|source_origin_[A-Za-z_]+)\b\s*[:=]\s*[^\n]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _base_record(record: dict[str, Any], *, content: str, digest: str, title: str | None = None) -> dict[str, Any]:
    result = {
        "chunk_id": f"tidb81_{digest[:20]}",
        "source_id": f"tidb81-knowledge:{digest[:20]}",
        "title": title or record["title"],
        "kb_type": record["kb_type"],
        "component": record["component"],
        "related_components": list(record.get("related_components", [])),
        "source_scope": record["source_scope"],
        "topic_tags": [sanitize_serving_text(str(item)) for item in record.get("topic_tags", [])],
        "version": "8.1",
        "source_file": f"curated/{digest[:20]}.md",
        "source_heading_path": sanitize_serving_text(record.get("source_heading_path", record["title"])),
        "source_url": "",
        "pinned_source_url": "",
        "use_when": sanitize_serving_text(record.get("use_when", "")),
        "retrieval_keywords": [sanitize_serving_text(str(item)) for item in record.get("retrieval_keywords", [])],
        "follow_up": sanitize_serving_text(record.get("follow_up", "")),
        "content": content,
        "content_sha256": sha256_text(content),
    }
    return result


def load_existing_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((PROJECT_ROOT / "knowledge" / "tidb" / "curated").glob("*/*chunks.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            missing = REQUIRED_FIELDS - set(value)
            if missing:
                raise ValueError(f"Curated record is incomplete: path={path}, line={line_number}, missing={sorted(missing)}")
            origin = {"path": path.relative_to(PROJECT_ROOT).as_posix(), "line": line_number, "record": value}
            records.append((value, origin))
    return records


def markdown_record(source_dir: Path, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    stem = path.stem
    content = path.read_text(encoding="utf-8").strip()
    mappings = {
        "k01_gc_phases_and_scope": ("GC phases, legal neighbors, and scope", "diagnosis", "tikv", ["mvcc", "gc", "locks"]),
        "k01_lock_codec_and_recovery": ("TiKV lock codec and bounded MVCC recovery", "recovery", "tikv", ["mvcc", "lock", "recovery"]),
        "k01_observability_contract": ("Agent-visible MVCC recovery evidence", "observability", "tikv", ["mvcc", "gc", "observability"]),
        "sf07_observability_and_safety_contract": ("Unsafe recovery evidence and safety boundary", "diagnosis", "pd", ["unsafe-recovery", "stores", "safety"]),
        "sf07_online_unsafe_recovery": ("Online Unsafe Recovery product boundary and state", "recovery", "pd", ["unsafe-recovery", "pd", "stores"]),
        "sf07_scope_and_rpo_contract": ("Unsafe recovery affected scope and RPO", "recovery", "pd", ["unsafe-recovery", "rpo", "regions"]),
        "dr_auto_sync_state_machine_and_roles": ("DR Auto-Sync state machine and placement roles", "architecture", "pd", ["dr-auto-sync", "placement-rules", "voter", "learner"]),
        "endpoint_fencing_and_admission_evidence": ("Endpoint fencing and business admission evidence", "operation", "tidb", ["failover", "fencing", "rpo", "canary"]),
        "online_unsafe_recovery_state_and_validation": ("Online Unsafe Recovery state and validation boundary", "recovery", "pd", ["unsafe-recovery", "failed-stores", "tombstone", "admin-check"]),
        "k08_checkpoint_identity_and_retry": ("PITR checkpoint identity and retry semantics", "recovery", "br", ["pitr", "checkpoint", "restore"]),
        "k08_pitr_chain_and_log_reachability": ("PITR chain, global checkpoint, and log reachability", "diagnosis", "br", ["pitr", "log-backup", "continuity"]),
        "k08_safe_recovery_and_acceptance": ("Safe recovery after a failed PITR checkpoint", "recovery", "br", ["pitr", "checkpoint", "safety"]),
        "lightning_checkpoint_identity_and_resume": ("Lightning checkpoint identity and resume semantics", "diagnosis", "lightning", ["lightning", "checkpoint", "identity", "resume"]),
        "lightning_physical_import_capacity_and_protection": ("Lightning physical import capacity and protection boundaries", "operation", "lightning", ["lightning", "physical-import", "capacity", "protection"]),
        "lightning_checkpoint_admission_and_terminal_acceptance": ("Lightning checkpoint admission and terminal acceptance", "recovery", "lightning", ["lightning", "checkpoint", "admission", "acceptance"]),
        "tidb81_ticdc_progress_and_restart": ("TiCDC progress state after a capture restart", "diagnosis", "ticdc", ["ticdc", "resolved-ts", "checkpoint-ts", "restart"]),
        "tidb81_ticdc_service_safepoint_ownership": ("TiCDC service GC safepoint ownership and cleanup", "recovery", "ticdc", ["ticdc", "service-gc-safepoint", "gc-ttl", "pd"]),
        "tidb81_ticdc_mvcc_recovery_scope": ("TiCDC progress and TiKV MVCC recovery scope", "recovery", "tikv", ["ticdc", "mvcc", "region", "peer-scope"]),
        "tidb81_ticdc_gc_recovery_verification": ("Joint TiCDC and GC recovery verification", "recovery", "ticdc", ["ticdc", "gc", "verification", "safety"]),
    }
    title, kb_type, component, tags = mappings[stem]
    record = {
        "title": title,
        "kb_type": kb_type,
        "component": component,
        "related_components": ["tidb", "tikv", "pd"],
        "source_scope": "self_managed",
        "topic_tags": tags,
        "version": "8.1",
        "source_file": path.relative_to(PROJECT_ROOT).as_posix(),
        "source_heading_path": title,
        "use_when": f"Use this knowledge when diagnosing or recovering TiDB 8.1 {title.casefold()}.",
        "retrieval_keywords": tags + [title],
        "follow_up": "Bind the documented invariant to current SQL, PD, Store, Region, and log evidence before acting.",
        "content": content,
    }
    return record, {"path": path.relative_to(PROJECT_ROOT).as_posix(), "line": None, "record": record}


def load_markdown_records() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    root = PROJECT_ROOT / "knowledge" / "tidb" / "curated"
    result = []
    for source_dir_name in (
        "tidb_system_failure_gc_mvcc_recovery",
        "tidb_system_failure_pending_offline",
        "tidb_business_change_pitr_checkpoint_recovery",
        "tidb_business_change_lightning_checkpoint",
        "tidb_dr_auto_sync",
        "tidb_composite_fault_ticdc_gc_safepoint",
    ):
        source_dir = root / source_dir_name
        for path in sorted(source_dir.glob("*.md")):
            result.append(markdown_record(source_dir, path))
    return result


def official_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"Official corpus has an empty line: path={path}, line={line_number}")
        value = json.loads(line)
        missing = REQUIRED_FIELDS - set(value)
        if missing:
            raise ValueError(f"Official record is incomplete: path={path}, line={line_number}, missing={sorted(missing)}")
        if value["content_sha256"] != sha256_text(value["content"]):
            raise ValueError(f"Official record hash mismatch: path={path}, line={line_number}, chunk_id={value['chunk_id']!r}")
        records.append(value)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    path.write_text(payload, encoding="utf-8")
    return sha256_text(payload)


def run(official_path: Path, output_root: Path) -> dict[str, Any]:
    official = official_records(official_path)
    extension_pairs = load_existing_records() + load_markdown_records()
    unified: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for record in official:
        item = dict(record)
        item["content_sha256"] = sha256_text(item["content"])
        item.update({
            "source_kind": "official",
            "source_origin_id": item["source_id"],
            "source_origin_path": item["source_file"],
            "source_origin_url": item["source_url"],
            "source_origin_pinned_url": item["pinned_source_url"],
        })
        unified.append(item)
        provenance.append({"chunk_id": item["chunk_id"], "source_kind": "official", "source_origin_id": item["source_id"], "source_origin_path": item["source_file"], "source_origin_url": item["source_url"]})
        seen_ids.add(item["chunk_id"])

    for original, origin in extension_pairs:
        content = sanitize_serving_text(original["content"])
        digest = sha256_text("\n".join((original["title"], original.get("source_id", ""), content)))
        item = _base_record(original, content=content, digest=digest)
        if item["chunk_id"] in seen_ids:
            raise ValueError(f"Unified chunk ID collision: chunk_id={item['chunk_id']}")
        item.update({
            "source_kind": "curated",
            "source_origin_id": original.get("source_id", f"markdown:{origin['path']}"),
            "source_origin_path": origin["path"],
            "source_origin_url": original.get("source_url", ""),
            "source_origin_pinned_url": original.get("pinned_source_url", ""),
        })
        unified.append(item)
        provenance.append({"chunk_id": item["chunk_id"], "source_kind": "curated", "source_origin_id": item["source_origin_id"], "source_origin_path": item["source_origin_path"], "source_origin_url": item["source_origin_url"]})
        seen_ids.add(item["chunk_id"])

    serving: list[dict[str, Any]] = []
    for item in unified:
        serving_item = {key: item[key] for key in REQUIRED_FIELDS}
        serving_item["source_id"] = ""
        serving_item["source_file"] = ""
        serving_item["source_url"] = ""
        serving_item["pinned_source_url"] = ""
        serving_item["title"] = sanitize_serving_text(serving_item["title"])
        serving_item["source_heading_path"] = sanitize_serving_text(serving_item["source_heading_path"])
        serving_item["use_when"] = sanitize_serving_text(serving_item["use_when"])
        serving_item["retrieval_keywords"] = [sanitize_serving_text(str(value)) for value in serving_item["retrieval_keywords"]]
        serving_item["follow_up"] = sanitize_serving_text(serving_item["follow_up"])
        serving_item["content"] = sanitize_serving_text(serving_item["content"])
        serving_item["content_sha256"] = sha256_text(serving_item["content"])
        semantic_fields = {
            key: value
            for key, value in serving_item.items()
            if key != "content_sha256"
        }
        serialized = json.dumps(semantic_fields, ensure_ascii=False).casefold()
        leaked = [
            token
            for token in FORBIDDEN_SERVING_TOKENS
            if re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", serialized)
        ]
        if leaked:
            raise ValueError(f"Serving corpus leakage: chunk_id={item['chunk_id']}, tokens={leaked}")
        serving.append(serving_item)

    second_path = output_root / "mappings" / "tidb81_chunks.jsonl"
    serving_path = output_root / "mappings" / "tidb81_serving_chunks.jsonl"
    provenance_path = output_root / "provenance" / "tidb81_provenance.jsonl"
    manifest_path = output_root / "manifests" / "tidb81_unified_manifest.json"
    second_hash = write_jsonl(second_path, unified)
    serving_hash = write_jsonl(serving_path, serving)
    provenance_hash = write_jsonl(provenance_path, provenance)
    summary = {
        "schema_version": 1,
        "corpus_id": "tidb81-unified-kb",
        "target_version": "8.1",
        "layers": {
            "processed": {
                "path": str(second_path.relative_to(PROJECT_ROOT)),
                "record_count": len(unified),
                "sha256": second_hash,
                "provenance_path": str(provenance_path.relative_to(PROJECT_ROOT)),
            },
            "serving": {
                "path": str(serving_path.relative_to(PROJECT_ROOT)),
                "record_count": len(serving),
                "sha256": serving_hash,
                "agent_projection": [
                    "rank", "score", "title", "version", "kb_type",
                    "component", "source_scope", "content",
                ],
            },
        },
        "source_kinds": {"official": len(official), "curated": len(extension_pairs)},
        "official_source": {
            "path": str(official_path.relative_to(PROJECT_ROOT)),
            "sha256": sha256_text(official_path.read_text(encoding="utf-8")),
        },
        "provenance_sha256": provenance_hash,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "official_count": len(official),
        "curated_count": len(extension_pairs),
        "unified_count": len(unified),
        "serving_count": len(serving),
        "official_source_sha256": sha256_text(official_path.read_text(encoding="utf-8")),
        "unified_sha256": second_hash,
        "serving_sha256": serving_hash,
        "provenance_sha256": provenance_hash,
        "second_layer": str(second_path),
        "serving_layer": str(serving_path),
        "provenance": str(provenance_path),
        "manifest": str(manifest_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-source", type=Path, default=Path("knowledge/tidb/mappings/tidb81_chunks.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("knowledge/tidb_unified"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(
        run(resolve_project_path(args.official_source), resolve_project_path(args.output_root)),
        ensure_ascii=False,
        indent=2,
    ))
