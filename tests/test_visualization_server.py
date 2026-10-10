from __future__ import annotations

import json
import threading
from functools import partial
from urllib.request import ProxyHandler, Request, build_opener

from src.visualization.server import ThreadedHTTPServer, VisualizationHandler


def test_raw_trace_page_and_api(tmp_path):
    traces = tmp_path / "traces"
    traces.mkdir()
    filename = "run_FakeScenario_LLMAgent_2026-07-11_10_00_00.json"
    raw = json.dumps({
        "$schema": "run_trace_v3",
        "metadata": {"scenario_name": "FakeScenario", "agent_type": "LLMAgent", "timestamp_end": 10},
        "evaluation": {"DiagnosisPass": True, "OutcomePass": True, "SafePass": True},
        "diagnostic_structure": {"type": "linear"},
    })
    (traces / filename).write_text(raw, encoding="utf-8")
    artifacts = tmp_path / "artifacts" / "pilot"
    artifacts.mkdir(parents=True)
    (artifacts / "manifest.yaml").write_text("experiment_id: pilot\n", encoding="utf-8")
    run = {
        "run_id": "run-1", "scenario_id": "scenario", "case_id": "default",
        "agent_id": "agent", "status": "succeeded", "started_at": "2026-07-11T10:00:00Z",
    }
    (artifacts / "runs.jsonl").write_text(json.dumps(run) + "\n", encoding="utf-8")
    (artifacts / "stdout.log").write_text("original stdout", encoding="utf-8")
    result_root = tmp_path / "results" / "postgresql" / "pg-five-models"
    result_root.mkdir(parents=True)
    (result_root / "result-set.yaml").write_text(
        """result_set_id: pg-five-models
state: open
system: postgresql
repetitions: 1
expected_runs: 5
categories:
  - {id: query_perf, title: Query Performance}
  - {id: system_failure, title: System Failure}
  - {id: health_check, title: Health Check}
  - {id: business_change, title: Business Change}
  - {id: resource_governance, title: Resource Governance}
models:
  - {id: agent-a, name: test-model-a}
""",
        encoding="utf-8",
    )
    catalog = result_root / "catalog"
    catalog.mkdir()
    (catalog / "query_perf.json").write_text(json.dumps({
        "category_id": "query_perf",
        "cases": [{
            "alias": 1,
            "scenario_id": "scenario",
            "scenario_name": "Scenario",
            "case_id": "default",
            "case_name": "Default",
            "difficulty": "easy",
            "diagnostic_depth": 2,
            "environmental_complexity": 0.25,
        }],
    }), encoding="utf-8")
    run_dir = result_root / "work" / "categories" / "query_perf" / "models" / "agent-a" / "runs"
    run_dir.mkdir(parents=True)
    (run_dir / "001__r001.json").write_text(json.dumps({
        "schema_version": "aiopsbench_result_run_v1",
        "result_set_id": "pg-five-models",
        "category_id": "query_perf",
        "run_key": "scenario/default/agent-a/r001",
        "scenario_id": "scenario",
        "case_id": "default",
        "model": {"agent_id": "agent-a", "model_name": "test-model-a"},
        "repetition": 1,
        "seed": 7,
        "execution": {"status": "succeeded", "duration_seconds": 10},
        "interaction": {"iterations": 2, "tool_calls": 3},
        "tokens": {"input": 10, "cache_input": 4, "output": 2},
        "evaluation": {"valid_for_aggregate": True, "DiagnosisPass": True, "OutcomePass": True, "SafePass": True},
        "timing": {"container_start_seconds": 1, "preparation_seconds": 2, "agent_interaction_seconds": 3, "evaluation_seconds": 1, "cleanup_seconds": 3},
        "fault_snapshot": {"used": False, "name": None},
        "provenance": {"experiment_id": "pilot", "run_id": "run-1", "attempt": 1, "trace_path": "artifacts/experiments/pilot/trace.json"},
    }), encoding="utf-8")
    handler = partial(
        VisualizationHandler,
        traces_dir=str(traces),
        reports_dir=str(tmp_path / "reports"),
        artifacts_dir=str(tmp_path / "artifacts"),
        results_dir=str(tmp_path / "results"),
    )
    server = ThreadedHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    opener = build_opener(ProxyHandler({}))
    try:
        page = opener.open(base + "/raw-traces").read().decode()
        listing = json.loads(opener.open(base + "/api/traces?q=fake&agent=LLMAgent").read())
        returned_raw = opener.open(base + f"/api/traces/{filename}/raw").read().decode()
        experiment_list = json.loads(opener.open(base + "/api/experiments").read())
        run_list = json.loads(opener.open(base + "/api/experiments/pilot/runs?q=run-1").read())
        stdout = opener.open(base + "/artifacts/experiments/pilot/stdout.log").read().decode()
        health = json.loads(opener.open(base + "/api/health").read())
        result_sets = json.loads(opener.open(base + "/api/result-sets").read())
        result_set = json.loads(opener.open(base + "/api/result-sets/pg-five-models").read())
        category = json.loads(
            opener.open(base + "/api/result-sets/pg-five-models/categories/query_perf").read()
        )
        results_page = opener.open(base + "/results").read().decode()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert "原始 Trace 日志" in page
    assert listing["total"] == 1
    assert listing["items"][0]["safe_pass"] is True
    assert returned_raw == raw
    assert experiment_list[0]["experiment_id"] == "pilot"
    assert run_list["items"][0]["run_id"] == "run-1"
    assert stdout == "original stdout"
    assert health == {"status": "ok"}
    assert result_sets[0]["result_set_id"] == "pg-five-models"
    assert result_set["state"] == "open"
    assert category["runs"][0]["run_key"] == "scenario/default/agent-a/r001"
    assert "实验结果" in results_page


def test_task_review_state_is_persisted_in_report_metadata(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "review.html"
    report.write_text(
        """<script type=\"application/json\" data-task-meta>{
  \"title\": \"Review\",
  \"path\": \"/reports/review.html\"
}</script>""",
        encoding="utf-8",
    )
    handler = partial(
        VisualizationHandler,
        traces_dir=str(tmp_path / "traces"),
        reports_dir=str(reports),
        artifacts_dir=str(tmp_path / "artifacts"),
    )
    server = ThreadedHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    opener = build_opener(ProxyHandler({}))
    review_state = {
        "pg_query_perf_missing_index::product_category_prefix_simple": {
            "status": "通过",
            "definition": True,
            "dp": True,
            "outcome": True,
            "sp": True,
            "note": "reviewed",
        }
    }
    request = Request(
        f"http://127.0.0.1:{server.server_port}/api/tasks/update",
        data=json.dumps({
            "path": "/reports/review.html",
            "review_state": review_state,
        }).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        opener.open(request).read()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    saved = report.read_text(encoding="utf-8")
    metadata = json.loads(saved.split("data-task-meta>", 1)[1].split("</script>", 1)[0])
    assert metadata["review_state"] == review_state
