from __future__ import annotations

from pathlib import Path

import pytest

from scripts.inventory_tidb_documentation import build_inventory
from src.knowledge.document_processing.source_manifest import write_source_manifest


def snapshot(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir()
    (root / "README.md").write_text("# Repository\n", encoding="utf-8")
    (root / "TOC.md").write_text(
        "# TOC\n\n- [Operations](/operation.md)\n- [Cloud](tidb-cloud/cloud.md)\n",
        encoding="utf-8",
    )
    (root / "operation.md").write_text(
        "---\ntitle: Operations\nsummary: Run TiDB.\n---\n\n# Operations\n",
        encoding="utf-8",
    )
    (root / "tidb-cloud").mkdir()
    (root / "tidb-cloud" / "cloud.md").write_text("# Cloud\n", encoding="utf-8")
    (root / ".github").mkdir()
    (root / ".github" / "pull_request_template.md").write_text("# PR\n", encoding="utf-8")
    write_source_manifest(root, "fixture")
    return root


def test_inventory_accounts_for_every_markdown_and_explains_exclusions(tmp_path):
    root = snapshot(tmp_path)
    records = build_inventory(root)

    assert len(records) == len(list(root.rglob("*.md")))
    assert all(record["processing_status"] in {"included", "excluded"} for record in records)
    assert all(
        record["exclusion_reason"]
        for record in records
        if record["processing_status"] == "excluded"
    )
    by_file = {record["source_file"]: record for record in records}
    assert by_file["operation.md"]["toc_membership"] == ["TOC.md"]
    assert by_file["operation.md"]["document_scope"] == "self_managed"
    assert by_file["tidb-cloud/cloud.md"]["document_scope"] == "cloud"
    assert by_file[".github/pull_request_template.md"]["exclusion_reason"] == "repository_maintenance_document"


def test_inventory_rejects_unresolved_local_toc_link(tmp_path):
    root = snapshot(tmp_path)
    (root / "TOC.md").write_text("# TOC\n\n- [Missing](missing.md)\n", encoding="utf-8")
    write_source_manifest(root, "fixture")

    with pytest.raises(FileNotFoundError, match="TOC link does not resolve"):
        build_inventory(root)
