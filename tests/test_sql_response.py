import json

import pytest

from src.database.sql import (
    execute_json_payload,
    execute_result_rows,
    parse_json_object,
    require_one_result_row,
    require_success_payload,
)


def test_shared_sql_response_parser_handles_payload_and_rows():
    raw = json.dumps({"status": "success", "result": [[1]]})

    assert parse_json_object(raw, "test") == {"status": "success", "result": [[1]]}
    assert require_success_payload(raw, "test")["result"] == [[1]]
    assert execute_json_payload(lambda sql: raw, "SELECT 1", "test")["result"] == [[1]]
    assert execute_result_rows(lambda sql: raw, "SELECT 1", "test") == [[1]]
    assert require_one_result_row([[1, 2]], "test") == [1, 2]
    assert require_one_result_row([(3, 4)], "test") == [3, 4]


def test_shared_sql_response_parser_fails_on_error_or_non_object():
    with pytest.raises(RuntimeError, match="failed"):
        require_success_payload({"status": "error", "error": "boom"}, "test")
    with pytest.raises(RuntimeError, match="failed"):
        require_success_payload({"result": []}, "test")
    with pytest.raises(TypeError, match="JSON object"):
        parse_json_object("[]", "test")
    with pytest.raises(TypeError, match="result rows"):
        execute_result_rows(lambda sql: json.dumps({"status": "success", "result": {}}), "SELECT 1", "test")
    with pytest.raises(ValueError, match="expected one result row"):
        require_one_result_row([], "test")
    with pytest.raises(ValueError, match="expected one result row"):
        require_one_result_row([1], "test")
