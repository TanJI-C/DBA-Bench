from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DOCS = sorted((PROJECT_ROOT / "docs/scenarios").glob("*.md"))
CURRENT_DOCS = tuple(
    path
    for path in SCENARIO_DOCS
    if "文档状态：历史设计记录" not in path.read_text(encoding="utf-8")
) + (PROJECT_ROOT / "docs/standards/knowledge/postgresql-document-classification.standard.md",)

REMOVED_PATH = re.compile(
    r"(?:src/(?:control|evaluation|orchestration)(?:/|`)"
    r"|tests/phase[0-9]+(?:_|\.)"
    r"|src/experiment(?:/|`))"
)
PATH_REFERENCE = re.compile(r"(?<![\w])((?:src|tests|examples|scripts)/[A-Za-z0-9_./*:-]+)")


def _normalize_path_reference(reference: str) -> str:
    reference = reference.rstrip("`.,;)]}")
    reference = re.sub(r"(?:::\w[\w.]*)+$", "", reference)
    return re.sub(r":\d+(?:-\d+)?$", "", reference)


def test_current_documentation_has_no_removed_package_paths():
    violations = []
    for path in CURRENT_DOCS:
        text = path.read_text(encoding="utf-8")
        if REMOVED_PATH.search(text):
            violations.append(path.relative_to(PROJECT_ROOT))
    assert violations == []


def test_current_documentation_references_existing_project_paths():
    missing = []
    for path in CURRENT_DOCS:
        text = path.read_text(encoding="utf-8")
        for raw_reference in PATH_REFERENCE.findall(text):
            reference = _normalize_path_reference(raw_reference)
            if "*" in reference:
                matches = list(PROJECT_ROOT.glob(reference))
                exists = bool(matches)
            else:
                exists = (PROJECT_ROOT / reference).exists()
            if not exists:
                missing.append(f"{path.relative_to(PROJECT_ROOT)}: {raw_reference}")
    assert missing == []
