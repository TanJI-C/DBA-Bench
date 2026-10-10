from scripts.collect_pg_full_reference_report import measurement_status, pass_summary, path_status


def _full_score_record(*, valid_for_aggregate: bool) -> dict:
    return {
        "status": "succeeded",
        "valid_for_aggregate": valid_for_aggregate,
        "diagnosis_pass": True,
        "outcome_pass": True,
        "safe_pass": True,
    }


def test_full_score_path_is_independent_from_aggregate_validity():
    record = _full_score_record(valid_for_aggregate=False)

    summary = pass_summary(record)

    assert summary["full_score"] is True
    assert summary["valid_for_aggregate"] is False
    assert path_status(record) == "full-score"
    assert measurement_status(record, {"complete": True}, {"complete": True}) == "measured"


def test_measurement_withholds_only_missing_runtime_or_cleanup_evidence():
    record = _full_score_record(valid_for_aggregate=True)

    assert measurement_status(record, {"complete": False}, {"complete": True}) == "pending-runtime"
    assert measurement_status(record, {"complete": True}, {"complete": False}) == "pending-cleanup"
