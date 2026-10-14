import re
from pathlib import Path

import pytest

from src.database.system import DatabaseSystem
from src.persistent_scenarios.model.loader import load_persistent_scenario
from src.scenarios import SCENARIO_REGISTRY
from src.scenarios.case_tags import CASE_TAGS, citation_tag
from src.scenarios.registry import ScenarioCategory

CATEGORY_ABBRS = {
    ScenarioCategory.BASIC: "ba",
    ScenarioCategory.QUERY_PERF: "qp",
    ScenarioCategory.SYSTEM_FAILURE: "sf",
    ScenarioCategory.HEALTH_CHECK: "hc",
    ScenarioCategory.BUSINESS_CHANGE: "bc",
    ScenarioCategory.RESOURCE_GOVERNANCE: "rg",
}
SYSTEM_PREFIXES = {"postgresql": "pg", "tidb": "tb"}
BOUNDED_TAG_PATTERN = re.compile(r"(pg|tb)-(ba|qp|sf|hc|bc|rg)-\d{2}")
PERSISTENT_TAG_PATTERN = re.compile(r"(PG|TB)-PS-\d{2}")

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "docs" / "catalogs" / "case-tags.catalog.md"


def registered_cases():
    return [
        (registration, case)
        for registration in SCENARIO_REGISTRY
        for case in registration.scenario.cases
    ]


def persistent_spec_paths():
    return sorted(
        path
        for path in (REPO_ROOT / "src" / "persistent_scenarios").glob("*/*.yaml")
        if not path.name.endswith(".driver.yaml")
    )


def test_registry_case_identity_is_globally_unique():
    keys = [(registration.scenario_id, case.case_id) for registration, case in registered_cases()]
    assert len(keys) == len(set(keys))


def test_case_tags_cover_the_registry_exactly():
    keys = {(registration.scenario_id, case.case_id) for registration, case in registered_cases()}
    assert set(CASE_TAGS) == keys


def test_case_tag_prefix_matches_system_and_category():
    for registration, case in registered_cases():
        tag = CASE_TAGS[(registration.scenario_id, case.case_id)]
        expected_prefix = (
            f"{SYSTEM_PREFIXES[registration.system.value]}-{CATEGORY_ABBRS[registration.category]}"
        )
        assert tag.startswith(f"{expected_prefix}-"), (
            registration.scenario_id,
            case.case_id,
            tag,
            expected_prefix,
        )


def test_case_tag_sequences_are_contiguous_per_group():
    groups: dict[str, list[int]] = {}
    for registration, case in registered_cases():
        prefix, seq = CASE_TAGS[(registration.scenario_id, case.case_id)].rsplit("-", 1)
        groups.setdefault(prefix, []).append(int(seq))
    for prefix, seqs in groups.items():
        assert seqs == list(range(1, len(seqs) + 1)), prefix


def test_case_tags_use_the_bounded_format():
    for tag in CASE_TAGS.values():
        assert BOUNDED_TAG_PATTERN.fullmatch(tag), tag


def test_citation_tag_resolver():
    registration, case = registered_cases()[0]
    key = (registration.scenario_id, case.case_id)
    assert citation_tag(*key) == CASE_TAGS[key]
    with pytest.raises(KeyError, match="citation tag"):
        citation_tag("no_such_scenario", "no_such_case")


def test_persistent_citation_tags_are_unique_and_valid():
    seen: dict[str, Path] = {}
    untagged: list[str] = []
    for path in persistent_spec_paths():
        spec = load_persistent_scenario(path)
        if spec.citation_tag is None:
            untagged.append(spec.scenario_id)
            continue
        assert PERSISTENT_TAG_PATTERN.fullmatch(spec.citation_tag), (path, spec.citation_tag)
        expected_prefix = "PG" if spec.system is DatabaseSystem.POSTGRESQL else "TB"
        assert spec.citation_tag.startswith(f"{expected_prefix}-"), (path, spec.citation_tag)
        assert spec.citation_tag not in seen, (spec.citation_tag, seen.get(spec.citation_tag), path)
        seen[spec.citation_tag] = path
    assert untagged == ["pg_continuous_ops_smoke"]


def test_case_tags_catalog_is_in_sync():
    text = CATALOG_PATH.read_text()
    for key in sorted(CASE_TAGS):
        assert f"`{CASE_TAGS[key]}`" in text, key
    doc_tags = set(re.findall(r"`((?:pg|tb)-(?:ba|qp|sf|hc|bc|rg|cf|ma)-\d{2})`", text))
    doc_tags |= set(re.findall(r"`((?:PG|TB)-PS-\d{2})`", text))
    known = set(CASE_TAGS.values()) | {
        spec.citation_tag
        for spec in (load_persistent_scenario(path) for path in persistent_spec_paths())
        if spec.citation_tag is not None
    }
    assert doc_tags == known
