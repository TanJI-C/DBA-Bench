import json
from pathlib import Path
from types import SimpleNamespace

from src.agents.agent import LLMAgent
from src.database.system import DatabaseSystem
from src.scenarios.runtime.orchestrator import Orchestrator
from src.visualization.exporter import export_run_trace


class FakeAgent:
    def export_diagnostic_trace(self):
        return {
            "agent_type": "FakeAgent",
            "mode": "fake",
            "prompts": {"system": "system prompt", "user": "user prompt"},
            "turns": [
                {
                    "turn_number": 1,
                    "timestamp": None,
                    "thinking": "check cpu",
                    "actions": [
                        {
                            "api": "query_metrics",
                            "args": {
                                "metric_type": "cpu",
                                "target": "postgresql",
                            },
                        }
                    ],
                    "results": [
                        {
                            "api": "query_metrics",
                            "status": "executed",
                            "data": None,
                        }
                    ],
                }
            ],
            "diagnostic_structure": {"type": "linear"},
            "conversation_history": [],
        }


class FakeScenario:
    system = DatabaseSystem.POSTGRESQL
    scenario_id = "fake_scenario"
    description = "fake scenario"


class FakeCase:
    case_id = "fake_case"
    title = "Fake case"


class FakeOrchestrator:
    def __init__(self):
        self.agent = FakeAgent()
        self.scenario = FakeScenario()
        self.case = FakeCase()
        self.case_run = SimpleNamespace(
            run_id="fixed-run-id",
            background_workload_planned={"profile_count": 0},
            background_workload_observed={},
        )
        self._last_eval_result = {
            "DiagnosisPass": True,
            "OutcomePass": True,
            "SafePass": True,
        }
        self.phase_timings = {
            "container_start_seconds": 1.0,
            "preparation_seconds": 2.0,
            "agent_interaction_seconds": 3.0,
            "evaluation_seconds": 4.0,
            "cleanup_seconds": 5.0,
            "total_seconds": 15.0,
        }
        self.fault_snapshot = {"used": False, "name": None}
        self.turn_history = [
            {
                "turn_number": 1,
                "timestamp_start": 123.0,
                "timestamp_agent_output": 123.1,
                "timestamp_end": 123.2,
                "raw_output": json.dumps(
                    {
                        "thinking": "check cpu",
                        "actions": [
                            {
                                "api": "query_metrics",
                                "args": {
                                    "metric_type": "cpu",
                                    "target": "postgresql",
                                },
                            }
                        ],
                    }
                ),
                "actions": [
                    {
                        "api": "query_metrics",
                        "args": {
                            "metric_type": "cpu",
                            "target": "postgresql",
                        },
                    }
                ],
                "results": [
                    {
                        "api": "query_metrics",
                        "status": "success",
                        "data": {
                            "metric": "cpu",
                            "value": 91,
                        },
                    }
                ],
                "should_break": False,
                "error": None,
            }
        ]


def test_exporter_enriches_turn_results_from_orchestrator_timeline(tmp_path):
    filepath = export_run_trace(FakeOrchestrator(), output_dir=str(tmp_path))

    with open(filepath, "r", encoding="utf-8") as f:
        trace = json.load(f)

    assert trace["orchestrator_timeline"][0]["results"][0]["data"]["value"] == 91
    assert trace["turns"][0]["results"][0]["status"] == "success"
    assert trace["turns"][0]["results"][0]["data"]["metric"] == "cpu"
    assert trace["metadata"]["timestamp_start"] == 123.0
    assert trace["metadata"]["run_id"] == "fixed-run-id"
    assert trace["metadata"]["scenario_id"] == "fake_scenario"
    assert trace["metadata"]["case_id"] == "fake_case"
    assert trace["$schema"] == "run_trace_v3"
    assert trace["evaluation"] == {
        "DiagnosisPass": True,
        "OutcomePass": True,
        "SafePass": True,
    }
    assert trace["phase_timings"]["agent_interaction_seconds"] == 3.0
    assert trace["fault_snapshot"] == {"used": False, "name": None}


def test_exporter_accepts_metric_history_return_to_normal_audit(tmp_path):
    orchestrator = FakeOrchestrator()
    orchestrator.case_run.metric_history = {
        "schema_version": 2,
        "return_to_normal_sample_count": 3,
    }

    filepath = export_run_trace(orchestrator, output_dir=str(tmp_path))
    trace = json.loads(Path(filepath).read_text(encoding="utf-8"))

    assert trace["metadata"]["metric_history"] == {
        "return_to_normal_sample_count": 3,
        "schema_version": 2,
    }


def test_exporter_preserves_metric_history_handoff_audit(tmp_path):
    orchestrator = FakeOrchestrator()
    orchestrator.case_run.metric_history = {
        "agent_handoff": {
            "diagnostic_workload": "stopped_after_target_capture",
            "fault_policy": "latent",
            "history": "frozen_before_agent",
        }
    }

    filepath = export_run_trace(orchestrator, output_dir=str(tmp_path))

    with open(filepath, encoding="utf-8") as f:
        trace = json.load(f)

    assert trace["metadata"]["metric_history"]["agent_handoff"]["fault_policy"] == "latent"


def test_exporter_preserves_multi_capture_and_target_activity_audit(tmp_path):
    orchestrator = FakeOrchestrator()
    orchestrator.case_run.metric_history = {
        "normal_capture_count": 2,
        "normal_capture_origins": [
            {"capture_id": "normal-0", "start_ms": 1000, "end_ms": 3000},
            {"capture_id": "normal-1", "start_ms": 4000, "end_ms": 6000},
        ],
        "normal_capture_ranges": [
            {"capture_id": "normal-0", "start_ms": 1000, "end_ms": 3000},
            {"capture_id": "normal-1", "start_ms": 4000, "end_ms": 6000},
        ],
        "normal_source_capture_ids": ["normal-0", "normal-1"],
        "target_lightning_activity": {
            "lightning_progress": {"active_sample_count": 3},
        },
    }

    filepath = export_run_trace(orchestrator, output_dir=str(tmp_path))
    trace = json.loads(Path(filepath).read_text(encoding="utf-8"))

    assert trace["metadata"]["metric_history"] == orchestrator.case_run.metric_history


def test_exporter_preserves_batched_agent_turns_and_terminal_submit(tmp_path):
    orchestrator = FakeOrchestrator()
    orchestrator.agent.export_diagnostic_trace = lambda: {
        "agent_type": "FakeAgent",
        "mode": "fake",
        "prompts": {"system": "", "user": ""},
        "turns": [
            {
                "turn_number": 1,
                "timestamp": None,
                "thinking": "batch",
                "actions": [
                    {"api": "query_metrics", "args": {"metric_type": "cpu", "target": "postgresql"}},
                    {"api": "execute_sql", "args": {"sql_query": "SELECT 1"}},
                ],
                "results": [],
            },
            {
                "turn_number": 2,
                "timestamp": None,
                "thinking": "done",
                "actions": [{"api": "submit", "args": {"report": {}}}],
                "results": [],
            },
        ],
        "diagnostic_structure": {"type": "linear"},
        "conversation_history": [],
        "llm_usage": [],
    }
    orchestrator.turn_history = [
        {
            "turn_number": 1,
            "timestamp_start": 1.0,
            "raw_output": "",
            "actions": [{"api": "query_metrics", "args": {"metric_type": "cpu", "target": "postgresql"}}],
            "results": [{"api": "query_metrics", "status": "success", "data": {"value": 90}}],
        },
        {
            "turn_number": 2,
            "timestamp_start": 2.0,
            "raw_output": "",
            "actions": [{"api": "execute_sql", "args": {"sql_query": "SELECT 1"}}],
            "results": [{"api": "execute_sql", "status": "success", "data": {"result": [[1]]}}],
        },
    ]

    filepath = export_run_trace(orchestrator, output_dir=str(tmp_path))
    trace = json.loads(Path(filepath).read_text(encoding="utf-8"))

    assert [[action["api"] for action in turn["actions"]] for turn in trace["turns"]] == [
        ["query_metrics", "execute_sql"],
        ["submit"],
    ]
    assert [result["status"] for result in trace["turns"][0]["results"]] == ["success", "success"]
    assert trace["turns"][-1]["results"] == [{"api": "submit", "status": "submitted", "data": None}]


def test_exporter_uses_experiment_identity_and_filename(tmp_path, monkeypatch):
    monkeypatch.setenv("AIOPS_EXPERIMENT_ID", "experiment-1")
    monkeypatch.setenv("AIOPS_RUN_ID", "run-1")
    monkeypatch.setenv("AIOPS_AGENT_ID", "agent-1")
    monkeypatch.setenv("AIOPS_REPETITION", "3")
    monkeypatch.setenv("AIOPS_SEED", "33")
    monkeypatch.setenv("AIOPS_TRACE_FILENAME", "run_run-1__a001.json")

    filepath = export_run_trace(FakeOrchestrator(), output_dir=str(tmp_path))
    trace = json.loads((tmp_path / "run_run-1__a001.json").read_text(encoding="utf-8"))

    assert filepath == str(tmp_path / "run_run-1__a001.json")
    assert trace["metadata"]["experiment_id"] == "experiment-1"
    assert trace["metadata"]["run_id"] == "fixed-run-id"
    assert trace["metadata"]["scenario_id"] == "fake_scenario"
    assert trace["metadata"]["case_id"] == "fake_case"
    assert trace["metadata"]["agent_id"] == "agent-1"
    assert trace["metadata"]["repetition"] == 3
    assert trace["metadata"]["seed"] == 33


def test_exporter_records_model_provenance(tmp_path):
    orchestrator = FakeOrchestrator()
    original_export = orchestrator.agent.export_diagnostic_trace
    orchestrator.agent.export_diagnostic_trace = lambda: {
        **original_export(),
        "model": "test-model-c",
        "provider": "openai",
        "reasoning_effort": "xhigh",
    }

    filepath = export_run_trace(orchestrator, output_dir=str(tmp_path))
    trace = json.loads(Path(filepath).read_text(encoding="utf-8"))

    assert trace["metadata"]["model"] == "test-model-c"
    assert trace["metadata"]["provider"] == "openai"
    assert trace["metadata"]["reasoning_effort"] == "xhigh"


def test_orchestrator_uses_experiment_run_id_for_case_run(monkeypatch):
    monkeypatch.setenv("AIOPS_RUN_ID", "experiment-run-1")

    evaluator = type("Evaluator", (), {"__init__": lambda self, env: None})

    orchestrator = Orchestrator(
        env=object(),
        scenario=SimpleNamespace(scenario_id="scenario"),
        case=SimpleNamespace(case_id="case", case_no=0, evaluator=evaluator),
        agent=object(),
    )

    assert orchestrator.case_run.run_id == "experiment-run-1"


def test_llm_agent_prompt_mode_parses_actions_list_without_api_call():
    agent = object.__new__(LLMAgent)
    agent.enable_log = False
    agent.logger = None
    agent.action_history = []

    raw_output = json.dumps(
        {
            "thinking": "batch checks",
            "actions": [
                {
                    "api": "query_metrics",
                    "args": {"metric_type": "cpu", "target": "postgresql"},
                },
                {
                    "api": "execute_sql",
                    "args": {"sql_query": "SELECT 1"},
                },
            ],
        }
    )

    actions = agent.parse_actions(raw_output)

    assert [action["api"] for action in actions] == ["query_metrics", "execute_sql"]
    assert len(agent.action_history) == 2


def test_llm_agent_native_tool_calls_executes_all_calls():
    agent = object.__new__(LLMAgent)
    agent.enable_log = False
    agent.logger = None
    agent.action_history = []
    agent.model = "mock-model"
    agent._conversation_history = []
    agent._usage_events = []
    agent._diagnostic_usage_event_count = 0
    agent._diagnostic_turn_usage = []
    response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "query_metrics",
                            "arguments": '{"metric_type": "topsql"}',
                        },
                    },
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {
                            "name": "execute_sql",
                            "arguments": '{"sql_query": "EXPLAIN ANALYZE SELECT pg_sleep(60)"}',
                        },
                    },
                ],
            }
        }]
    }
    agent._call_llm = lambda messages: response

    _, actions = agent._next_llm_actions(max_empty_retries=0)

    assert [action["api"] for action in actions] == ["query_metrics", "execute_sql"]
    assert len(agent._conversation_history[0]["tool_calls"]) == 2
