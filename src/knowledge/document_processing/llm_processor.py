"""Strict two-stage LLM processing for TiDB documentation."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Sequence

from .markdown_parser import FENCE_RE
from .schemas import (
    COMPONENTS,
    KNOWLEDGE_CATEGORIES,
    RETRIEVAL_SCOPES,
    MarkdownDocument,
    MarkdownSection,
    ProcessingUnit,
    RetrievalEnrichment,
    SplitChunk,
    SplitPlan,
)
from .source_manifest import sha256_bytes
from .tidb_cleaner import CleanedSection, clean_markdown_text


PROCESSING_SCHEMA_VERSION = "tidb-document-processing-v5"
TARGET_CHUNK_TOKENS = 2500
HARD_CHUNK_TOKENS = 4000
MAX_GROUP_TOKENS = 3800
LEAKAGE_RE = re.compile(
    r"(?:aiopsbench|scenario[_ -]?id|case[_ -]?id|hidden root cause|"
    r"evaluator keyword|src/control/evaluators|diagnosispass|outcomepass|safepass)",
    re.I,
)


def estimate_tokens(text: str) -> int:
    lexical = len(re.findall(r"[A-Za-z0-9_]+|[^\w\s]", text))
    return max(1, lexical, math.ceil(len(text.encode("utf-8")) / 3.0))


def _atomic_ranges(section: MarkdownSection) -> dict[int, tuple[int, bool]]:
    intervals: list[tuple[int, int]] = [
        (block.start_line, block.end_line) for block in section.code_blocks
    ]
    for table in section.tables:
        candidate = (table.start_line, table.end_line)
        if any(start <= candidate[0] <= end or candidate[0] <= start <= candidate[1] for start, end in intervals):
            continue
        intervals.append(candidate)
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if current[0] <= previous[1]:
            raise ValueError(
                f"Overlapping indivisible Markdown constructs: heading_path={section.heading_path_text!r}, "
                f"previous={previous}, current={current}"
            )
    return {start: (end, True) for start, end in intervals}


def _section_blocks(section: MarkdownSection) -> list[tuple[int, int, str, bool]]:
    lines = section.text.splitlines(keepends=True)
    atomic = _atomic_ranges(section)
    blocks: list[tuple[int, int, str, bool]] = []
    local = 0
    while local < len(lines):
        absolute = section.start_line + local
        if absolute in atomic:
            end_line, indivisible = atomic[absolute]
            end_local = end_line - section.start_line + 1
            blocks.append((absolute, end_line, "".join(lines[local:end_local]), indivisible))
            local = end_local
            continue
        start_local = local
        local += 1
        while local < len(lines):
            absolute_next = section.start_line + local
            if absolute_next in atomic:
                break
            if not lines[local - 1].strip() and lines[local].strip():
                break
            local += 1
        blocks.append((
            section.start_line + start_local,
            section.start_line + local - 1,
            "".join(lines[start_local:local]),
            False,
        ))
    return blocks


def _split_large_text_block(
    start_line: int,
    text: str,
    target_tokens: int,
) -> list[tuple[int, int, str, bool]]:
    lines = text.splitlines(keepends=True)
    pieces: list[tuple[int, int, str, bool]] = []
    piece_start = 0
    current: list[str] = []
    for index, line in enumerate(lines):
        candidate = "".join([*current, line])
        if current and estimate_tokens(candidate) > target_tokens:
            pieces.append((
                start_line + piece_start,
                start_line + index - 1,
                "".join(current),
                False,
            ))
            piece_start = index
            current = [line]
        else:
            current.append(line)
    if current:
        pieces.append((
            start_line + piece_start,
            start_line + len(lines) - 1,
            "".join(current),
            False,
        ))
    return pieces


def build_processing_units(
    document: MarkdownDocument,
    cleaned_sections: Sequence[CleanedSection],
    website_base_url: str,
    target_tokens: int = TARGET_CHUNK_TOKENS,
) -> tuple[ProcessingUnit, ...]:
    if len(document.sections) != len(cleaned_sections):
        raise ValueError(
            f"Parsed/cleaned section count mismatch: source_file={document.source_file!r}, "
            f"parsed={len(document.sections)}, cleaned={len(cleaned_sections)}"
        )
    units: list[ProcessingUnit] = []
    next_id = 1
    for section, cleaned in zip(document.sections, cleaned_sections):
        if (section.start_line, section.end_line) != cleaned.source_line_range:
            raise ValueError(
                f"Cleaned section range mismatch: source_file={document.source_file!r}, "
                f"heading_path={section.heading_path_text!r}, parsed={(section.start_line, section.end_line)}, "
                f"cleaned={cleaned.source_line_range}"
            )
        raw_blocks = _section_blocks(section)
        blocks: list[tuple[int, int, str, bool]] = []
        for start, end, text, indivisible in raw_blocks:
            if indivisible or estimate_tokens(text) <= target_tokens:
                blocks.append((start, end, text, indivisible))
            else:
                blocks.extend(_split_large_text_block(start, text, target_tokens))
        current: list[tuple[int, int, str, bool]] = []
        for block in blocks:
            candidate_text = "".join(item[2] for item in [*current, block])
            if current and estimate_tokens(candidate_text) > target_tokens:
                raw_text = "".join(item[2] for item in current)
                text, _ = clean_markdown_text(
                    raw_text,
                    document.source_file,
                    section.heading_path_text,
                    website_base_url,
                )
                units.append(ProcessingUnit(
                    unit_id=f"u{next_id:05d}",
                    heading_path=section.heading_path_text,
                    start_line=current[0][0],
                    end_line=current[-1][1],
                    text=text,
                    token_count=estimate_tokens(text),
                    indivisible=any(item[3] for item in current),
                ))
                next_id += 1
                current = []
            current.append(block)
            if block[3] and estimate_tokens(block[2]) > target_tokens:
                text, _ = clean_markdown_text(
                    block[2],
                    document.source_file,
                    section.heading_path_text,
                    website_base_url,
                )
                units.append(ProcessingUnit(
                    unit_id=f"u{next_id:05d}",
                    heading_path=section.heading_path_text,
                    start_line=block[0],
                    end_line=block[1],
                    text=text,
                    token_count=estimate_tokens(text),
                    indivisible=True,
                ))
                next_id += 1
                current = []
        if current:
            raw_text = "".join(item[2] for item in current)
            text, _ = clean_markdown_text(
                raw_text,
                document.source_file,
                section.heading_path_text,
                website_base_url,
            )
            units.append(ProcessingUnit(
                unit_id=f"u{next_id:05d}",
                heading_path=section.heading_path_text,
                start_line=current[0][0],
                end_line=current[-1][1],
                text=text,
                token_count=estimate_tokens(text),
                indivisible=any(item[3] for item in current),
            ))
            next_id += 1
    if not units:
        raise ValueError(f"Document produced no processing units: source_file={document.source_file!r}")
    previous_end = document.sections[0].start_line - 1
    for unit in units:
        if unit.start_line != previous_end + 1:
            raise ValueError(
                f"Processing unit coverage gap/overlap: source_file={document.source_file!r}, "
                f"unit_id={unit.unit_id!r}, expected_start={previous_end + 1}, actual_start={unit.start_line}"
            )
        previous_end = unit.end_line
    if previous_end != document.sections[-1].end_line:
        raise ValueError(
            f"Processing units do not reach document end: source_file={document.source_file!r}, "
            f"last_unit_end={previous_end}, document_end={document.sections[-1].end_line}"
        )
    return tuple(units)


def group_processing_units(
    units: Sequence[ProcessingUnit],
    max_group_tokens: int = MAX_GROUP_TOKENS,
) -> tuple[tuple[ProcessingUnit, ...], ...]:
    groups: list[tuple[ProcessingUnit, ...]] = []
    current: list[ProcessingUnit] = []
    current_tokens = 0
    for unit in units:
        if current and current_tokens + unit.token_count > max_group_tokens:
            groups.append(tuple(current))
            current = []
            current_tokens = 0
        current.append(unit)
        current_tokens += unit.token_count
        if unit.token_count > max_group_tokens:
            groups.append(tuple(current))
            current = []
            current_tokens = 0
    if current:
        groups.append(tuple(current))
    return tuple(groups)


def _object(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: context={context}, type={type(value).__name__}")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValueError(
            f"Strict JSON fields mismatch: context={context}, expected={sorted(expected)}, actual={sorted(actual)}"
        )


def _string(value: object, context: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"Expected non-empty string: context={context}, value={value!r}")
    return value.strip()


def _string_list(value: object, context: str, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"Expected string list: context={context}, value={value!r}")
    result = tuple(_string(item, f"{context}[{index}]") for index, item in enumerate(value))
    return result


def validate_split_plan(
    payload: object,
    source_file: str,
    units: Sequence[ProcessingUnit],
) -> SplitPlan:
    root = _object(payload, "split_plan")
    _exact_keys(root, {"source_file", "chunks"}, "split_plan")
    if root["source_file"] != source_file:
        raise ValueError(
            f"Split plan invented source path: expected={source_file!r}, actual={root['source_file']!r}"
        )
    if not isinstance(root["chunks"], list) or not root["chunks"]:
        raise ValueError(f"Split plan chunks must be a non-empty list: source_file={source_file!r}")
    units_by_id = {unit.unit_id: unit for unit in units}
    expected_ids = [unit.unit_id for unit in units]
    observed_ids: list[str] = []
    chunks: list[SplitChunk] = []
    expected_chunk_fields = {
        "unit_ids", "heading_paths", "title", "primary_category", "primary_component",
        "related_components", "deployment_scope", "topic_tags", "classification_reason",
        "needs_human_review",
    }
    for index, item in enumerate(root["chunks"]):
        value = _object(item, f"chunks[{index}]")
        _exact_keys(value, expected_chunk_fields, f"chunks[{index}]")
        unit_ids = _string_list(value["unit_ids"], f"chunks[{index}].unit_ids")
        unknown_units = [unit_id for unit_id in unit_ids if unit_id not in units_by_id]
        if unknown_units:
            raise ValueError(
                f"Split plan invented unit ids: source_file={source_file!r}, chunk={index}, "
                f"unknown_units={unknown_units!r}"
            )
        chunk_units = [units_by_id[unit_id] for unit_id in unit_ids]
        unit_positions = [expected_ids.index(unit_id) for unit_id in unit_ids]
        if unit_positions != list(range(unit_positions[0], unit_positions[0] + len(unit_positions))):
            raise ValueError(
                f"Split chunk units must be contiguous and source ordered: source_file={source_file!r}, "
                f"chunk={index}, unit_ids={unit_ids!r}"
            )
        heading_paths = _string_list(value["heading_paths"], f"chunks[{index}].heading_paths")
        expected_paths = tuple(dict.fromkeys(unit.heading_path for unit in chunk_units))
        if heading_paths != expected_paths:
            raise ValueError(
                f"Split chunk heading paths do not match units: source_file={source_file!r}, "
                f"chunk={index}, expected={expected_paths!r}, actual={heading_paths!r}"
            )
        category = _string(value["primary_category"], f"chunks[{index}].primary_category")
        component = _string(value["primary_component"], f"chunks[{index}].primary_component")
        related = _string_list(
            value["related_components"], f"chunks[{index}].related_components", allow_empty=True,
        )
        scope = _string(value["deployment_scope"], f"chunks[{index}].deployment_scope")
        if category not in KNOWLEDGE_CATEGORIES:
            raise ValueError(f"Unknown TiDB knowledge category: source_file={source_file!r}, value={category!r}")
        if component not in COMPONENTS or any(item not in COMPONENTS for item in related):
            raise ValueError(
                f"Unknown TiDB component: source_file={source_file!r}, primary={component!r}, related={related!r}"
            )
        if component in related:
            raise ValueError(
                f"Primary component duplicated in related_components: source_file={source_file!r}, "
                f"component={component!r}"
            )
        if scope not in RETRIEVAL_SCOPES:
            raise ValueError(f"Unknown TiDB deployment scope: source_file={source_file!r}, value={scope!r}")
        if not isinstance(value["needs_human_review"], bool):
            raise ValueError(
                f"needs_human_review must be boolean: source_file={source_file!r}, chunk={index}, "
                f"value={value['needs_human_review']!r}"
            )
        chunk_text = "".join(unit.text for unit in chunk_units)
        chunk_tokens = estimate_tokens(chunk_text)
        oversized_atomic = len(chunk_units) == 1 and chunk_units[0].indivisible
        if chunk_tokens > HARD_CHUNK_TOKENS and not oversized_atomic:
            raise ValueError(
                f"Split chunk exceeds hard token limit: source_file={source_file!r}, chunk={index}, "
                f"tokens={chunk_tokens}, hard_limit={HARD_CHUNK_TOKENS}, unit_ids={unit_ids!r}"
            )
        mandatory_review = oversized_atomic and chunk_tokens > HARD_CHUNK_TOKENS
        if mandatory_review and not value["needs_human_review"]:
            raise ValueError(
                f"Split chunk requires human review: source_file={source_file!r}, chunk={index}, "
                f"tokens={chunk_tokens}, unit_ids={unit_ids!r}"
            )
        chunks.append(SplitChunk(
            unit_ids=unit_ids,
            heading_paths=heading_paths,
            title=_string(value["title"], f"chunks[{index}].title"),
            primary_category=category,
            primary_component=component,
            related_components=related,
            deployment_scope=scope,
            topic_tags=_string_list(value["topic_tags"], f"chunks[{index}].topic_tags", allow_empty=True),
            classification_reason=_string(
                value["classification_reason"], f"chunks[{index}].classification_reason",
            ),
            needs_human_review=value["needs_human_review"],
        ))
        observed_ids.extend(unit_ids)
    if observed_ids != expected_ids:
        missing = [unit_id for unit_id in expected_ids if unit_id not in observed_ids]
        duplicates = sorted({unit_id for unit_id in observed_ids if observed_ids.count(unit_id) > 1})
        raise ValueError(
            f"Split plan unit coverage failure: source_file={source_file!r}, "
            f"missing={missing!r}, duplicates={duplicates!r}, expected_order={expected_ids!r}, "
            f"actual_order={observed_ids!r}"
        )
    return SplitPlan(source_file=source_file, chunks=tuple(chunks))


def validate_enrichments(
    payload: object,
    source_file: str,
    chunk_keys: Sequence[str],
) -> dict[str, RetrievalEnrichment]:
    root = _object(payload, "enrichment")
    _exact_keys(root, {"source_file", "enrichments"}, "enrichment")
    if root["source_file"] != source_file:
        raise ValueError(
            f"Enrichment invented source path: expected={source_file!r}, actual={root['source_file']!r}"
        )
    if not isinstance(root["enrichments"], list):
        raise ValueError(f"Enrichments must be a list: source_file={source_file!r}")
    expected_fields = {
        "chunk_key", "use_when", "retrieval_keywords", "follow_up", "classification_note",
    }
    result: dict[str, RetrievalEnrichment] = {}
    observed: list[str] = []
    for index, item in enumerate(root["enrichments"]):
        value = _object(item, f"enrichments[{index}]")
        _exact_keys(value, expected_fields, f"enrichments[{index}]")
        chunk_key = _string(value["chunk_key"], f"enrichments[{index}].chunk_key")
        observed.append(chunk_key)
        combined = " ".join(
            str(value[field]) for field in ("use_when", "retrieval_keywords", "follow_up", "classification_note")
        )
        if LEAKAGE_RE.search(combined):
            raise ValueError(
                f"Benchmark leakage detected in retrieval metadata: source_file={source_file!r}, "
                f"chunk_key={chunk_key!r}"
            )
        result[chunk_key] = RetrievalEnrichment(
            use_when=_string(value["use_when"], f"enrichments[{index}].use_when"),
            retrieval_keywords=_string_list(
                value["retrieval_keywords"], f"enrichments[{index}].retrieval_keywords",
            ),
            follow_up=_string(value["follow_up"], f"enrichments[{index}].follow_up", allow_empty=True),
            classification_note=_string(
                value["classification_note"], f"enrichments[{index}].classification_note",
            ),
        )
    if observed != list(chunk_keys):
        raise ValueError(
            f"Enrichment coverage/order failure: source_file={source_file!r}, "
            f"expected={list(chunk_keys)!r}, actual={observed!r}"
        )
    return result


class DocumentProcessingClient:
    """Small non-interactive provider client dedicated to strict JSON document jobs."""

    def __init__(self, config_path: Path, model: str):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if model not in config:
            raise KeyError(
                f"Document-processing model is absent from LLM config: model={model!r}, "
                f"config_path={config_path}, configured_models={sorted(config)!r}"
            )
        model_config = _object(config[model], f"llm_config[{model!r}]")
        self.model = model
        self.api_key = _string(model_config.get("api_key"), f"llm_config[{model!r}].api_key")
        self.provider = str(model_config.get("provider") or ("anthropic" if "claude" in model.casefold() else "openai")).casefold()
        if self.provider not in {"openai", "anthropic"}:
            raise ValueError(f"Unsupported document-processing provider: model={model!r}, provider={self.provider!r}")
        url = _string(model_config.get("url"), f"llm_config[{model!r}].url").rstrip("/")
        for suffix in ("/chat/completions", "/v1/messages"):
            if url.endswith(suffix):
                url = url[:-len(suffix)]
        if self.provider == "anthropic" and url.endswith("/v1"):
            url = url[:-3]
        self.url = url.rstrip("/")

    def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        user_text = json.dumps(user_payload, ensure_ascii=False, separators=(",", ":"))
        if self.provider == "anthropic":
            import anthropic

            response = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.url,
                timeout=600,
                max_retries=2,
            ).messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_text}],
                temperature=0,
                max_tokens=16384,
            )
            raw = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        else:
            from openai import OpenAI

            response = OpenAI(
                api_key=self.api_key,
                base_url=self.url,
                timeout=600,
                max_retries=2,
            ).chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=16384,
            )
            raw = response.choices[0].message.content or ""
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Document-processing model returned malformed JSON: model={self.model!r}, "
                f"provider={self.provider!r}, raw_response={raw!r}"
            ) from exc
        return raw, {"payload": payload, "usage": usage}


def split_request_payload(
    document: MarkdownDocument,
    document_scope: str,
    toc_membership: Sequence[str],
    units: Sequence[ProcessingUnit],
) -> dict[str, Any]:
    return {
        "source_file": document.source_file,
        "source_version": "8.1",
        "document_title": document.title,
        "document_summary": document.summary,
        "document_scope": document_scope,
        "toc_membership": list(toc_membership),
        "allowed_categories": sorted(KNOWLEDGE_CATEGORIES),
        "allowed_components": sorted(COMPONENTS),
        "allowed_scopes": sorted(RETRIEVAL_SCOPES),
        "complete_heading_outline": [section.heading_path_text for section in document.sections],
        "source_units": [asdict(unit) for unit in units],
    }


def enrichment_request_payload(
    source_file: str,
    split_plan: SplitPlan,
    units: Sequence[ProcessingUnit],
    group_number: int,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    units_by_id = {unit.unit_id: unit for unit in units}
    chunks = []
    keys = []
    for index, chunk in enumerate(split_plan.chunks, start=1):
        key = f"g{group_number:04d}c{index:04d}"
        keys.append(key)
        chunks.append({
            "chunk_key": key,
            "title": chunk.title,
            "primary_category": chunk.primary_category,
            "primary_component": chunk.primary_component,
            "related_components": list(chunk.related_components),
            "deployment_scope": chunk.deployment_scope,
            "topic_tags": list(chunk.topic_tags),
            "heading_paths": list(chunk.heading_paths),
            "official_content": "".join(units_by_id[unit_id].text for unit_id in chunk.unit_ids),
        })
    return {"source_file": source_file, "chunks": chunks}, tuple(keys)


def processing_fingerprint(
    source_sha256: str,
    inventory_sha256: str,
    split_prompt_sha256: str,
    enrich_prompt_sha256: str,
    model: str,
) -> str:
    payload = "\n".join((
        PROCESSING_SCHEMA_VERSION,
        source_sha256,
        inventory_sha256,
        split_prompt_sha256,
        enrich_prompt_sha256,
        model,
    ))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prompt_sha256(prompt: str) -> str:
    return sha256_bytes(prompt.encode("utf-8"))
