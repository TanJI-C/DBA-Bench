import pytest

from src.benchmark.result_identity import (
    analysis_run_filename,
    persistent_result_tag,
    result_run_filename,
    result_run_key,
    validate_case_tag,
)


def case():
    return {
        "scenario_id": "pg_query_perf_missing_index",
        "case_id": "product_category_substring",
        "citation_tag": "pg-qp-01",
    }


def test_frozen_tag_defines_result_and_analysis_identity():
    tag = validate_case_tag(case())
    assert result_run_key(tag, "agent", 2) == "pg-qp-01/agent/r002"
    assert result_run_filename(tag, 2) == "pg-qp-01__r002.json"
    assert analysis_run_filename(tag, "agent", 2) == "pg-qp-01__agent__r002.json"


@pytest.mark.parametrize("change", [{"citation_tag": "pg-qp-02"}, {"alias": 1}])
def test_wrong_tag_and_numeric_alias_are_rejected(change):
    with pytest.raises(ValueError, match="frozen citation tag"):
        validate_case_tag(case() | change)


def test_persistent_result_tag_uses_formal_spec_and_rejects_smoke():
    assert persistent_result_tag("pg_continuous_ops_business_priority") == "PG-PS-01"
    with pytest.raises(ValueError, match="no formal result citation tag"):
        persistent_result_tag("pg_continuous_ops_smoke")
