from __future__ import annotations

import pytest
import hashlib

from src.knowledge.document_processing.markdown_parser import parse_markdown_text
from src.knowledge.document_processing.llm_processor import (
    build_processing_units,
    processing_fingerprint,
    validate_enrichments,
    validate_split_plan,
)
from src.knowledge.document_processing.tidb_cleaner import clean_markdown_sections


SOURCE = """---
title: Memory Control
summary: Configure memory safely.
aliases: [/old-memory]
---

<!-- markdownlint-disable MD024 -->

# Memory Control

<CustomContent platform="tidb">

> **Warning:**
>
> Keep the limit below host memory.

- First item
  - Nested item

| Variable | Default |
| --- | --- |
| `tidb_mem_oom_action` | `CANCEL` |

{{< copyable "sql" >}}

```sql
SELECT '# not a heading' AS exact_text;

SELECT * FROM t;
```

See [the variable reference](/system-variables.md#tidb_mem_oom_action).

</CustomContent>

## Query quota

Set `tidb_mem_quota_query` for one statement.

### Example

Use a session value.

## Instance quota

Set `tidb_server_memory_limit` for the server.
"""


def test_parser_extracts_frontmatter_sections_and_constructs():
    document = parse_markdown_text(SOURCE, "configure-memory-usage.md")

    assert document.title == "Memory Control"
    assert document.summary == "Configure memory safely."
    assert document.frontmatter["aliases"] == ["/old-memory"]
    assert [section.heading_path_text for section in document.sections] == [
        "Memory Control",
        "Memory Control > Query quota",
        "Memory Control > Query quota > Example",
        "Memory Control > Instance quota",
    ]
    first = document.sections[0]
    assert len(first.code_blocks) == 1
    assert first.code_blocks[0].language == "sql"
    assert len(first.tables) == 1
    assert first.lists
    assert first.admonitions
    assert first.links == ("/system-variables.md#tidb_mem_oom_action",)


def test_cleaner_preserves_code_tables_warnings_and_resolves_links():
    document = parse_markdown_text(SOURCE, "configure-memory-usage.md")
    cleaned = clean_markdown_sections(
        document.sections,
        document.source_file,
        "https://docs.pingcap.com/tidb/stable",
    )

    first = cleaned[0].content
    assert document.sections[0].code_blocks[0].text in first
    assert "| `tidb_mem_oom_action` | `CANCEL` |" in first
    assert "> **Warning:**" in first
    assert "{{< copyable" not in first
    assert "<CustomContent" not in first
    assert "https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action" in first


def test_parser_ignores_headings_inside_fences_and_distinguishes_repeated_names_by_parent():
    document = parse_markdown_text(
        "# Root\n\n## A\n\n### Example\n\n```text\n## not heading\n```\n\n## B\n\n### Example\n",
        "repeated.md",
    )
    assert [section.heading_path_text for section in document.sections] == [
        "Root", "Root > A", "Root > A > Example", "Root > B", "Root > B > Example",
    ]


def test_parser_rejects_missing_headings_without_full_source_fallback():
    with pytest.raises(ValueError, match="has no headings"):
        parse_markdown_text("Official text without a heading.\n", "missing-heading.md")


def test_cleaner_rejects_unknown_site_component():
    document = parse_markdown_text("# Title\n\n<UnknownPanel value=\"x\" />\n", "unknown.md")
    with pytest.raises(ValueError, match="Unsupported TiDB HTML/MDX container"):
        clean_markdown_sections(
            document.sections,
            document.source_file,
            "https://docs.pingcap.com/tidb/stable",
        )


def test_parser_rejects_unterminated_fence():
    with pytest.raises(ValueError, match="Unterminated fenced code block"):
        parse_markdown_text("# Title\n\n```sql\nSELECT 1;\n", "broken.md")


def test_file_parser_hashes_raw_crlf_bytes(tmp_path):
    from src.knowledge.document_processing.markdown_parser import parse_markdown_document

    raw = b"# Title\r\n\r\nOfficial content.\r\n"
    path = tmp_path / "crlf.md"
    path.write_bytes(raw)
    document = parse_markdown_document(path, tmp_path)
    assert document.source_sha256 == hashlib.sha256(raw).hexdigest()
    assert "\r\n" in document.sections[0].text


def processing_units():
    document = parse_markdown_text(SOURCE, "configure-memory-usage.md")
    cleaned = clean_markdown_sections(
        document.sections,
        document.source_file,
        "https://docs.pingcap.com/tidb/stable",
    )
    return document, build_processing_units(
        document,
        cleaned,
        "https://docs.pingcap.com/tidb/stable",
    )


def valid_split_payload(document, units):
    return {
        "source_file": document.source_file,
        "chunks": [{
            "unit_ids": [unit.unit_id for unit in units],
            "heading_paths": list(dict.fromkeys(unit.heading_path for unit in units)),
            "title": "Configure TiDB memory controls",
            "primary_category": "configuration",
            "primary_component": "tidb",
            "related_components": [],
            "deployment_scope": "self_managed",
            "topic_tags": ["memory", "oom"],
            "classification_reason": "The source defines TiDB query and instance memory controls.",
            "needs_human_review": False,
        }],
    }


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda payload: payload.update({"extra": True}), "Strict JSON fields mismatch"),
        (lambda payload: payload["chunks"][0].update(primary_category="other"), "Unknown TiDB knowledge category"),
        (lambda payload: payload["chunks"][0].update(primary_component="unknown"), "Unknown TiDB component"),
        (lambda payload: payload["chunks"][0].update(heading_paths=["Missing"]), "heading paths do not match"),
        (lambda payload: payload["chunks"][0].update(unit_ids=payload["chunks"][0]["unit_ids"][:-1]), "heading paths do not match"),
    ),
)
def test_split_schema_rejects_invalid_output(mutation, message):
    document, units = processing_units()
    payload = valid_split_payload(document, units)
    mutation(payload)
    with pytest.raises(ValueError, match=message):
        validate_split_plan(payload, document.source_file, units)


def test_split_and_enrichment_schema_accept_complete_strict_output():
    document, units = processing_units()
    plan = validate_split_plan(valid_split_payload(document, units), document.source_file, units)
    assert len(plan.chunks) == 1

    enrichments = validate_enrichments({
        "source_file": document.source_file,
        "enrichments": [{
            "chunk_key": "g0001c0001",
            "use_when": "Use when configuring TiDB query or instance memory limits.",
            "retrieval_keywords": ["tidb_mem_quota_query", "tidb_server_memory_limit"],
            "follow_up": "Check the configured OOM action and memory metrics.",
            "classification_note": "The source defines TiDB memory configuration behavior.",
        }],
    }, document.source_file, ["g0001c0001"])
    assert enrichments["g0001c0001"].retrieval_keywords[0] == "tidb_mem_quota_query"


def test_enrichment_schema_rejects_benchmark_leakage_and_extra_fields():
    document, _ = processing_units()
    payload = {
        "source_file": document.source_file,
        "enrichments": [{
            "chunk_key": "g0001c0001",
            "use_when": "Use for AiOpsBench scenario_id hidden root cause.",
            "retrieval_keywords": ["memory"],
            "follow_up": "Check memory.",
            "classification_note": "Memory configuration.",
        }],
    }
    with pytest.raises(ValueError, match="Benchmark leakage"):
        validate_enrichments(payload, document.source_file, ["g0001c0001"])


def test_processing_fingerprint_changes_with_inventory_input():
    first = processing_fingerprint("a" * 64, "b" * 64, "c" * 64, "d" * 64, "test-model-b")
    second = processing_fingerprint("a" * 64, "e" * 64, "c" * 64, "d" * 64, "test-model-b")
    assert first != second
