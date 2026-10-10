#!/usr/bin/env python3
"""Run reproducible retrieval and Agent-facing projection smoke tests."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT  # noqa: E402
from src.execution.environment import TiDBEnv
from src.knowledge.embedding_model_runtime import ensure_embedding_model
from src.knowledge.tidb_knowledge_base import TiDBKnowledgeBase


PROJECT_ROOT = REPOSITORY_ROOT


MODEL = "Qwen/Qwen3-Embedding-4B"
SERVING_SOURCE = PROJECT_ROOT / "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
CHROMA_DIR = PROJECT_ROOT / "data/knowledge_bases/tidb81_unified_chroma"
COLLECTION = "tidb81_unified_docs"
EMBEDDING_URL = os.environ.get("AIOPS_EMBEDDING_MODEL_URL", "http://127.0.0.1:8765")

STANDARD_QUERIES = [
    {
        "name": "memory_limit_oom_action",
        "query": "tidb_server_memory_limit tidb_mem_oom_action",
        "markers": ["tidb_server_memory_limit", "tidb_mem_oom_action"],
    },
    {
        "name": "online_unsafe_recovery_finished",
        "query": "Online Unsafe Recovery failed stores Finished affected table IDs",
        "markers": ["Online Unsafe Recovery", "failed Store", "Finished"],
    },
    {
        "name": "pd_recover_identity_allocator",
        "query": "pd-recover original cluster ID alloc-id TSO NTP",
        "markers": ["pd-recover", "alloc-id", "TSO"],
    },
    {
        "name": "ticdc_checkpoint_resolved_ddl_retry",
        "query": "TiCDC checkpoint resolved DDL retry timezone sink",
        "markers": ["checkpoint", "resolved", "DDL"],
    },
    {
        "name": "clustered_pk_odku_consistency",
        "query": "clustered primary key ODKU 8141 assertion secondary index",
        "markers": ["clustered", "8141", "secondary index"],
    },
    {
        "name": "placement_inheritance_constraints",
        "query": "placement policy inheritance FOLLOWERS PRIMARY_REGION REGIONS",
        "markers": ["FOLLOWERS", "PRIMARY_REGION", "REGIONS"],
    },
    {
        "name": "lightning_checkpoint_restore_identity",
        "query": "Lightning checkpoint restore source schema target identity",
        "markers": ["Lightning", "checkpoint", "schema"],
    },
    {
        "name": "timestamp_ddl_session_semantics",
        "query": "timestamp DDL session time zone default display value",
        "markers": ["timestamp", "time zone", "DDL"],
    },
]


class FakeDeployment:
    run_id = "unified-kb-smoke"
    primary_tidb_endpoint = ("127.0.0.1", 4000)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def gpu_memory() -> list[dict[str, int | str]]:
    output = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.used,memory.free",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = []
    for line in output.splitlines():
        index, name, used, free = [part.strip() for part in line.split(",", 3)]
        result.append({"index": int(index), "name": name, "memory_used_mib": int(used), "memory_free_mib": int(free)})
    return result


def query_once(kb: TiDBKnowledgeBase, item: dict[str, object]) -> tuple[float, dict[str, object]]:
    started = time.perf_counter()
    result = kb.query(
        str(item["query"]),
        source_scope="all",
        top_k=5,
        max_chars_per_result=1600,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    combined = "\n".join(row["content"] for row in result["results"])
    markers = [str(marker) for marker in item["markers"]]
    return elapsed_ms, {
        "name": item["name"],
        "query": item["query"],
        "latency_ms": round(elapsed_ms, 3),
        "count": result["count"],
        "kb_types": sorted({row["kb_type"] for row in result["results"]}),
        "components": sorted({row["component"] for row in result["results"]}),
        "marker_hits": {marker: marker.casefold() in combined.casefold() for marker in markers},
        "recall_hit": any(marker.casefold() in combined.casefold() for marker in markers),
        "marker_complete": all(marker.casefold() in combined.casefold() for marker in markers),
    }


def main() -> int:
    if not SERVING_SOURCE.is_file():
        raise FileNotFoundError(f"Serving corpus is missing: path={SERVING_SOURCE}")
    probe = ensure_embedding_model(MODEL, "cuda", base_url=EMBEDDING_URL)

    before_gpu = gpu_memory()
    kb = TiDBKnowledgeBase(
        persist_dir=CHROMA_DIR,
        collection_name=COLLECTION,
        backend="chroma",
        knowledge_base_mode="hierarchical",
        source_file=SERVING_SOURCE,
        embed_model_name=MODEL,
        embed_device=os.environ.get("AIOPS_SMOKE_EMBED_DEVICE", "cuda"),
        embed_batch_size=1,
        embed_workers=1,
    )
    cold_latency, cold_result = query_once(kb, STANDARD_QUERIES[0])
    warm_samples: list[dict[str, object]] = []
    warm_latencies: list[float] = []
    for _ in range(3):
        for item in STANDARD_QUERIES:
            elapsed_ms, result = query_once(kb, item)
            warm_latencies.append(elapsed_ms)
            warm_samples.append(result)

    env = TiDBEnv(deployment=FakeDeployment())
    env._tidb_knowledge_bases["hierarchical"] = kb
    projected = json.loads(env._search_tidb_knowledge(
        query="tidb_server_memory_limit tidb_mem_oom_action",
        source_scope="all",
        top_k=3,
        max_chars_per_result=600,
        knowledge_base_mode="hierarchical",
    ))
    allowed = {"rank", "score", "title", "version", "kb_type", "component", "source_scope", "content"}
    forbidden = {"source_id", "source_file", "source_url", "pinned_source_url", "index", "persist_dir", "source_commit", "materialized_corpus_sha256"}
    projected_fields = sorted(set(projected["results"][0]))
    leaked_fields = sorted(
        forbidden.intersection(projected["results"][0])
        | {key for key in projected if key in forbidden}
    )
    unexpected_fields = sorted(set(projected["results"][0]) - allowed)
    after_gpu = gpu_memory()
    output = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL,
        "embedding_service": {
            "endpoint": EMBEDDING_URL,
            "status": probe.status,
            "detail": probe.detail,
            "base_url": probe.base_url,
            "model": probe.model,
        },
        "backend": "chroma",
        "collection": COLLECTION,
        "source_file": str(SERVING_SOURCE),
        "embedding_device": os.environ.get("AIOPS_SMOKE_EMBED_DEVICE", "cuda"),
        "gpu_before": before_gpu,
        "gpu_after": after_gpu,
        "cold_query": {"latency_ms": round(cold_latency, 3), **cold_result},
        "warm_query": {
            "sample_count": len(warm_latencies),
            "min_ms": round(min(warm_latencies), 3),
            "p50_ms": round(percentile(warm_latencies, 0.50), 3),
            "p95_ms": round(percentile(warm_latencies, 0.95), 3),
            "max_ms": round(max(warm_latencies), 3),
            "mean_ms": round(statistics.mean(warm_latencies), 3),
            "recall_hits": sum(bool(item["recall_hit"]) for item in warm_samples),
            "recall_total": len(warm_samples),
            "marker_complete_hits": sum(bool(item["marker_complete"]) for item in warm_samples),
            "samples": warm_samples,
        },
        "agent_projection": {
            "status": projected["status"],
            "fields": projected_fields,
            "unexpected_fields": unexpected_fields,
            "leaked_fields": leaked_fields,
            "source_fields_exposed": bool(leaked_fields),
        },
    }
    output_path = PROJECT_ROOT / "logs" / "tidb_unified_kb_smoke.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output["agent_projection"]["source_fields_exposed"]:
        raise RuntimeError(f"Agent-facing source fields leaked: fields={leaked_fields}")
    if output["warm_query"]["recall_hits"] != output["warm_query"]["recall_total"]:
        raise RuntimeError(
            f"Standard retrieval recall smoke failed: hits={output['warm_query']['recall_hits']}, total={output['warm_query']['recall_total']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
