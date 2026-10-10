import json

import pytest

from src.trace_serialization import strict_json_dumps, strict_json_loads, validate_trace_document
from src.scenarios.runtime.env_gateway import EnvGateway


def test_strict_json_rejects_non_finite_numbers():
    with pytest.raises(ValueError, match="Non-finite JSON number"):
        strict_json_dumps({"latency": float("inf")})


def test_strict_json_rejects_non_standard_constants_on_read():
    with pytest.raises(ValueError, match="Non-standard JSON constant"):
        strict_json_loads('{"value": NaN}', context="attempt/trace.json")


def test_trace_schema_validation_requires_identity_metadata():
    value = json.loads(strict_json_dumps({"$schema": "run_trace_v3", "metadata": {}}))
    with pytest.raises(ValueError, match="metadata is incomplete"):
        validate_trace_document(value, schema="run_trace_v3", context="trace.json")


def test_gateway_records_joinable_turn_action_and_result_ids():
    history = []
    timeline = []
    gateway = EnvGateway(
        type("Env", (), {"execute_action": lambda self, api, args: {"status": "success"}})(),
        history,
        timeline,
    )
    result = gateway.execute("query_metrics", {"metric_type": "cpu"})

    assert history[0]["action_id"] == timeline[0]["actions"][0]["action_id"]
    assert history[0]["result_id"] == timeline[0]["results"][0]["result_id"]
    assert timeline[0]["turn_id"] == "turn-000001"
    assert result["status"] == "success"
