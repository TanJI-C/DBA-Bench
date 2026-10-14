#!/usr/bin/env python3
"""Deterministically materialize reviewed TiDB processing records."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT, resolve_project_path  # noqa: E402
from src.knowledge.document_processing.markdown_parser import parse_markdown_document  # noqa: E402
from src.knowledge.document_processing.schemas import KNOWLEDGE_CATEGORIES  # noqa: E402
from src.knowledge.document_processing.source_manifest import (  # noqa: E402
    SOURCE_LOCK_FILENAME,
    SOURCE_MANIFEST_FILENAME,
    load_json,
    sha256_bytes,
    verify_source_manifest,
    write_json,
)
from src.knowledge.document_processing.tidb_cleaner import clean_markdown_text  # noqa: E402


PROJECT_ROOT = REPOSITORY_ROOT


def load_json_list(path: Path) -> list:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected JSON list: path={path}, type={type(payload).__name__}")
    return payload


def slug(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    return normalized or "section"


def source_urls(source_file: str, heading_path: str, source_lock: dict) -> tuple[str, str]:
    page = source_file.rsplit(".", 1)[0]
    anchor = slug(heading_path.split(" > ")[-1])
    official = f"{source_lock['website_base_url'].rstrip('/')}/{page}#{anchor}"
    pinned = f"{source_lock['github_blob_base_url'].rstrip('/')}/{source_file}"
    return official, pinned


def merge_ranges(units: list[dict]) -> list[dict[str, int]]:
    ranges: list[dict[str, int]] = []
    for unit in units:
        start, end = int(unit["start_line"]), int(unit["end_line"])
        if ranges and start == ranges[-1]["end"] + 1:
            ranges[-1]["end"] = end
        else:
            ranges.append({"start": start, "end": end})
    return ranges


def extract_lines(path: Path, start: int, end: int) -> str:
    lines = path.read_bytes().decode("utf-8-sig").splitlines(keepends=True)
    if start < 1 or end < start or end > len(lines):
        raise ValueError(
            f"Invalid source line range: path={path}, start={start}, end={end}, line_count={len(lines)}"
        )
    return "".join(lines[start - 1:end])


def review_id(source_file: str, chunk_key: str, unit_ids: list[str]) -> str:
    digest = sha256_bytes(
        f"{source_file}\n{chunk_key}\n{'|'.join(unit_ids)}".encode("utf-8")
    )[:16]
    return f"review_{digest}"


def load_review_resolutions(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    payload = load_json(path)
    resolutions = payload.get("resolutions")
    if not isinstance(resolutions, list):
        raise ValueError(f"Review resolutions must contain a list: path={path}")
    result = {}
    for item in resolutions:
        if not isinstance(item, dict) or set(item) != {"review_id", "status", "reviewer", "reason"}:
            raise ValueError(f"Invalid strict review resolution: path={path}, item={item!r}")
        if item["status"] not in {"approved", "rejected"}:
            raise ValueError(f"Unknown review resolution status: path={path}, item={item!r}")
        if item["review_id"] in result:
            raise ValueError(f"Duplicate review resolution: review_id={item['review_id']!r}, path={path}")
        result[item["review_id"]] = item
    return result


def inventory_input_sha256(record: dict) -> str:
    return sha256_bytes(
        json.dumps(record, ensure_ascii=False, sort_keys=True).encode("utf-8")
    )


def collect_chunks(
    source_dir: Path,
    inventory: list[dict],
    processing_run: Path,
    source_lock: dict,
) -> tuple[list[dict], list[dict]]:
    included = [record for record in inventory if record["processing_status"] == "included"]
    states = {
        payload["source_file"]: payload
        for payload in (
            load_json(path) for path in sorted((processing_run / "states").glob("*.json"))
        )
    }
    expected_files = {record["source_file"] for record in included}
    if set(states) != expected_files:
        raise ValueError(
            f"Processing state coverage mismatch: run={processing_run}, "
            f"missing={sorted(expected_files - set(states))!r}, extra={sorted(set(states) - expected_files)!r}"
        )
    failed = [source_file for source_file, state in states.items() if state.get("state") != "completed"]
    if failed:
        raise ValueError(
            f"Cannot materialize partial TiDB corpus: run={processing_run}, "
            f"non_completed_count={len(failed)}, source_files={failed[:20]!r}"
        )
    records_by_file = {record["source_file"]: record for record in included}
    chunks: list[dict] = []
    review_queue: list[dict] = []
    for source_file in sorted(expected_files):
        inventory_record = records_by_file[source_file]
        state = states[source_file]
        document = parse_markdown_document(source_dir / source_file, source_dir)
        if document.source_sha256 != inventory_record["source_sha256"] or state["source_sha256"] != document.source_sha256:
            raise ValueError(
                f"Source hash mismatch during materialization: source_file={source_file!r}, "
                f"inventory={inventory_record['source_sha256']!r}, processing={state['source_sha256']!r}, "
                f"actual={document.source_sha256!r}"
            )
        if state.get("inventory_input_sha256") != inventory_input_sha256(inventory_record):
            raise ValueError(
                f"Inventory input hash mismatch during materialization: source_file={source_file!r}, "
                f"processing={state.get('inventory_input_sha256')!r}, "
                f"actual={inventory_input_sha256(inventory_record)!r}"
            )
        observed_units: list[str] = []
        for group in state["groups"]:
            units_by_id = {unit["unit_id"]: unit for unit in group["units"]}
            expected_group_units = [unit["unit_id"] for unit in group["units"]]
            group_observed: list[str] = []
            for chunk in group["chunks"]:
                unit_ids = chunk["unit_ids"]
                selected_units = [units_by_id[unit_id] for unit_id in unit_ids]
                group_observed.extend(unit_ids)
                official_parts = []
                for unit in selected_units:
                    raw = extract_lines(
                        source_dir / source_file,
                        int(unit["start_line"]),
                        int(unit["end_line"]),
                    )
                    cleaned, _ = clean_markdown_text(
                        raw,
                        source_file,
                        unit["heading_path"],
                        source_lock["website_base_url"],
                    )
                    if cleaned != unit["text"]:
                        raise ValueError(
                            f"Processing/materialization cleaned content mismatch: source_file={source_file!r}, "
                            f"unit_id={unit['unit_id']!r}, range={(unit['start_line'], unit['end_line'])}"
                        )
                    official_parts.append(cleaned)
                official_content = "".join(official_parts).strip() + "\n"
                if not official_content.strip():
                    raise ValueError(
                        f"Materialized chunk has empty official content: source_file={source_file!r}, "
                        f"chunk_key={chunk['chunk_key']!r}"
                    )
                rid = review_id(source_file, chunk["chunk_key"], unit_ids)
                if chunk["needs_human_review"]:
                    review_queue.append({
                        "review_id": rid,
                        "source_file": source_file,
                        "chunk_key": chunk["chunk_key"],
                        "title": chunk["title"],
                        "primary_category": chunk["primary_category"],
                        "primary_component": chunk["primary_component"],
                        "related_components": chunk["related_components"],
                        "deployment_scope": chunk["deployment_scope"],
                        "heading_paths": chunk["heading_paths"],
                        "source_line_ranges": merge_ranges(selected_units),
                        "classification_reason": chunk["classification_reason"],
                        "content_sha256": sha256_bytes(official_content.encode("utf-8")),
                        "oversized_indivisible": any(
                            unit["indivisible"] and int(unit["token_count"]) > 4000
                            for unit in selected_units
                        ),
                        "status": "unresolved",
                    })
                chunks.append({
                    "source_file": source_file,
                    "source_sha256": document.source_sha256,
                    "source_title": document.title,
                    "source_scope": inventory_record["document_scope"],
                    "toc_membership": inventory_record["toc_membership"],
                    "chunk_key": chunk["chunk_key"],
                    "review_id": rid if chunk["needs_human_review"] else None,
                    "unit_ids": unit_ids,
                    "heading_paths": chunk["heading_paths"],
                    "source_line_ranges": merge_ranges(selected_units),
                    "title": chunk["title"],
                    "kb_type": chunk["primary_category"],
                    "component": chunk["primary_component"],
                    "related_components": chunk["related_components"],
                    "source_scope_retrieval": chunk["deployment_scope"],
                    "topic_tags": chunk["topic_tags"],
                    "classification_reason": chunk["classification_reason"],
                    "needs_human_review": chunk["needs_human_review"],
                    "official_content": official_content,
                    "content_sha256": sha256_bytes(official_content.encode("utf-8")),
                    "enrichment": chunk["enrichment"],
                    "processing_model": state["model"],
                    "split_prompt_sha256": state["split_prompt_sha256"],
                    "enrich_prompt_sha256": state["enrich_prompt_sha256"],
                })
            if group_observed != expected_group_units:
                raise ValueError(
                    f"Materialization group unit coverage mismatch: source_file={source_file!r}, "
                    f"group_number={group['group_number']}, expected={expected_group_units!r}, "
                    f"actual={group_observed!r}"
                )
            observed_units.extend(group_observed)
        all_state_units = [
            unit["unit_id"] for group in state["groups"] for unit in group["units"]
        ]
        if observed_units != all_state_units:
            raise ValueError(
                f"Materialization document unit coverage mismatch: source_file={source_file!r}"
            )
    return chunks, review_queue


def stable_chunk_ids(chunks: list[dict], source_commit: str) -> None:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for chunk in chunks:
        by_category[chunk["kb_type"]].append(chunk)
    observed: set[str] = set()
    for category in sorted(by_category):
        ordered = sorted(
            by_category[category],
            key=lambda item: (item["source_file"], item["source_line_ranges"][0]["start"], item["chunk_key"]),
        )
        for index, chunk in enumerate(ordered, start=1):
            identity = "\n".join((
                source_commit,
                chunk["source_file"],
                " | ".join(chunk["heading_paths"]),
                chunk["content_sha256"],
            ))
            digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10]
            chunk_id = f"tidb81_{category}_{index:04d}_{digest}"
            if chunk_id in observed:
                raise ValueError(f"Duplicate deterministic chunk id: chunk_id={chunk_id!r}")
            observed.add(chunk_id)
            chunk["chunk_id"] = chunk_id


def markdown_record(chunk: dict, source_lock: dict, resolution: dict | None) -> str:
    heading_path = chunk["heading_paths"][0]
    official_url, pinned_url = source_urls(chunk["source_file"], heading_path, source_lock)
    line_ranges = ", ".join(
        f"{item['start']}-{item['end']}" for item in chunk["source_line_ranges"]
    )
    related = ", ".join(f"`{item}`" for item in chunk["related_components"]) or "none"
    tags = ", ".join(f"`{item}`" for item in chunk["topic_tags"]) or "none"
    review_status = "reviewed" if resolution else "ai_classified"
    enrichment = chunk["enrichment"]
    return f"""# {chunk['title']}

## Knowledge Metadata

- Knowledge Type: `{chunk['kb_type']}`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `{source_lock['commit']}`
- Source File: `knowledge/tidb_src/{chunk['source_file']}`
- Source Title: `{chunk['source_title']}`
- Source Heading Path: `{' | '.join(chunk['heading_paths'])}`
- Source Line Ranges: `{line_ranges}`
- Source Scope: `{chunk['source_scope_retrieval']}`
- Primary Component: `{chunk['component']}`
- Related Components: {related}
- Topic Tags: {tags}
- Documentation Version: `8.1`
- Chunk ID: `{chunk['chunk_id']}`
- Source ID: `tidb-docs-8.1:{chunk['source_file']}#{slug(heading_path.split(' > ')[-1])}`
- Review Status: `{review_status}`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `{chunk['content_sha256']}`

## Source Links

- Official Documentation: {official_url}
- Pinned GitHub Source: {pinned_url}

## Retrieval Guidance

- Use When: {enrichment['use_when']}
- Retrieval Keywords: {', '.join(enrichment['retrieval_keywords'])}
- Follow-up Guidance: {enrichment['follow_up']}
- Classification Note: {enrichment['classification_note']}

## Official Source Content

{chunk['official_content']}"""


def publish_corpus(
    output_dir: Path,
    source_dir: Path,
    inventory: list[dict],
    processing_manifest: dict,
    chunks: list[dict],
    review_queue: list[dict],
    resolutions: dict[str, dict],
    source_lock: dict,
    pending_review_path: Path,
) -> None:
    stable_chunk_ids(chunks, source_lock["commit"])
    unresolved = [item for item in review_queue if item["review_id"] not in resolutions]
    rejected = [item for item in review_queue if resolutions.get(item["review_id"], {}).get("status") == "rejected"]
    if unresolved or rejected:
        write_json(pending_review_path, {
            "source_commit": source_lock["commit"],
            "unresolved_count": len(unresolved),
            "rejected_count": len(rejected),
            "records": review_queue,
        })
        raise ValueError(
            f"TiDB corpus review is incomplete: unresolved={len(unresolved)}, rejected={len(rejected)}, "
            f"review_queue={pending_review_path}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tidb-materialize-", dir=output_dir.parent) as temp_name:
        build_dir = Path(temp_name) / output_dir.name
        mappings = build_dir / "mappings"
        mappings.mkdir(parents=True)
        for category in sorted(KNOWLEDGE_CATEGORIES):
            (build_dir / category).mkdir()
        source_to_chunks: dict[str, list[str]] = defaultdict(list)
        jsonl_records = []
        classification_records = []
        chunk_manifest = []
        for chunk in sorted(chunks, key=lambda item: item["chunk_id"]):
            resolution = resolutions.get(chunk["review_id"]) if chunk["review_id"] else None
            filename = f"{chunk['chunk_id']}.md"
            relative_path = f"{chunk['kb_type']}/{filename}"
            (build_dir / relative_path).write_text(
                markdown_record(chunk, source_lock, resolution),
                encoding="utf-8",
            )
            source_to_chunks[chunk["source_file"]].append(chunk["chunk_id"])
            heading_path = chunk["heading_paths"][0]
            official_url, pinned_url = source_urls(chunk["source_file"], heading_path, source_lock)
            source_id = f"tidb-docs-8.1:{chunk['source_file']}#{slug(heading_path.split(' > ')[-1])}"
            jsonl_records.append({
                "chunk_id": chunk["chunk_id"],
                "source_id": source_id,
                "title": chunk["title"],
                "kb_type": chunk["kb_type"],
                "component": chunk["component"],
                "related_components": chunk["related_components"],
                "source_scope": chunk["source_scope_retrieval"],
                "topic_tags": chunk["topic_tags"],
                "version": "8.1",
                "source_file": chunk["source_file"],
                "source_heading_path": " | ".join(chunk["heading_paths"]),
                "source_line_ranges": chunk["source_line_ranges"],
                "source_url": official_url,
                "pinned_source_url": pinned_url,
                "use_when": chunk["enrichment"]["use_when"],
                "retrieval_keywords": chunk["enrichment"]["retrieval_keywords"],
                "follow_up": chunk["enrichment"]["follow_up"],
                "content": chunk["official_content"],
                "content_sha256": chunk["content_sha256"],
            })
            classification_records.append({
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "source_line_ranges": chunk["source_line_ranges"],
                "kb_type": chunk["kb_type"],
                "component": chunk["component"],
                "related_components": chunk["related_components"],
                "source_scope": chunk["source_scope_retrieval"],
                "topic_tags": chunk["topic_tags"],
                "classification_reason": chunk["classification_reason"],
            })
            chunk_manifest.append({
                "chunk_id": chunk["chunk_id"],
                "path": relative_path,
                "content_sha256": chunk["content_sha256"],
                "source_file": chunk["source_file"],
            })
        (mappings / "tidb81_chunks.jsonl").write_text(
            "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in jsonl_records),
            encoding="utf-8",
        )
        write_json(mappings / "tidb81_document_inventory.json", inventory)
        write_json(mappings / "tidb81_section_classification.json", classification_records)
        write_json(mappings / "tidb81_source_to_chunks.json", dict(sorted(source_to_chunks.items())))
        write_json(mappings / "tidb81_chunk_manifest.json", chunk_manifest)
        write_json(
            mappings / "tidb81_exclusion_manifest.json",
            [record for record in inventory if record["processing_status"] == "excluded"],
        )
        reviewed_queue = []
        for item in review_queue:
            reviewed_queue.append({**item, **resolutions[item["review_id"]]})
        write_json(mappings / "tidb81_review_queue.json", reviewed_queue)
        write_json(mappings / "tidb81_processing_manifest.json", processing_manifest)
        review_summary = (
            "# TiDB 8.1 Knowledge Review Summary\n\n"
            f"- Source commit: `{source_lock['commit']}`\n"
            f"- Materialized chunks: {len(chunks)}\n"
            f"- Reviewed chunks: {len(review_queue)}\n"
            f"- Oversized indivisible source constructs: "
            f"{sum(item['oversized_indivisible'] for item in review_queue)}\n"
            "- Unresolved reviews: 0\n"
            "- Duplicate chunk IDs: 0\n"
            "- Uncovered processing units: 0\n"
        )
        (mappings / "tidb81_review_summary.md").write_text(review_summary, encoding="utf-8")
        (build_dir / "README.md").write_text(
            "# TiDB 8.1 Official Documentation Knowledge Corpus\n\n"
            "This directory is generated from the pinned English TiDB official documentation snapshot in "
            "`knowledge/tidb_src/`. JSONL under `mappings/` is the authoritative RAG input.\n",
            encoding="utf-8",
        )
        (build_dir / "ATTRIBUTION.md").write_text(
            "# Attribution\n\n"
            "This corpus contains material derived from the TiDB official English documentation at "
            "https://github.com/pingcap/docs, pinned to commit "
            f"`{source_lock['commit']}` and licensed under CC BY-SA 3.0. "
            "The immutable upstream license is preserved at `knowledge/tidb_src/LICENSE`.\n",
            encoding="utf-8",
        )
        if output_dir.exists():
            backup = output_dir.with_name(output_dir.name + ".previous")
            if backup.exists():
                shutil.rmtree(backup)
            os.replace(output_dir, backup)
            os.replace(build_dir, output_dir)
            shutil.rmtree(backup)
        else:
            os.replace(build_dir, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("knowledge/tidb_src"))
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("knowledge/tidb/mappings/tidb81_document_inventory.json"),
    )
    parser.add_argument("--processing-run", type=Path, required=True)
    parser.add_argument("--review-resolutions", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("knowledge/tidb"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = resolve_project_path(args.source_dir)
    verify_source_manifest(source_dir)
    source_lock = load_json(source_dir / SOURCE_LOCK_FILENAME)
    load_json(source_dir / SOURCE_MANIFEST_FILENAME)
    inventory_path = resolve_project_path(args.inventory)
    inventory = load_json_list(inventory_path)
    processing_run = resolve_project_path(args.processing_run)
    processing_manifest = load_json(processing_run / "manifest.json")
    if processing_manifest["source_commit"] != source_lock["commit"]:
        raise ValueError(
            f"Processing/source commit mismatch: processing={processing_manifest['source_commit']!r}, "
            f"source={source_lock['commit']!r}"
        )
    inventory_hash = sha256_bytes(
        json.dumps(inventory, ensure_ascii=False, sort_keys=True).encode("utf-8")
    )
    if processing_manifest.get("inventory_sha256") != inventory_hash:
        raise ValueError(
            f"Processing/inventory hash mismatch: processing={processing_manifest.get('inventory_sha256')!r}, "
            f"actual={inventory_hash!r}, inventory={inventory_path}"
        )
    chunks, review_queue = collect_chunks(
        source_dir, inventory, processing_run, source_lock,
    )
    resolutions = load_review_resolutions(
        resolve_project_path(args.review_resolutions) if args.review_resolutions else None
    )
    publish_corpus(
        resolve_project_path(args.output_dir),
        source_dir,
        inventory,
        processing_manifest,
        chunks,
        review_queue,
        resolutions,
        source_lock,
        processing_run / "review_queue.json",
    )
    print(json.dumps({
        "status": "success",
        "output_dir": str(resolve_project_path(args.output_dir)),
        "chunk_count": len(chunks),
        "reviewed_count": len(review_queue),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
