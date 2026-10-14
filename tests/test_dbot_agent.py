"""Tests for the DB-GPT code-first D-Bot adapter (parallel multi-expert)."""

import json
import os
import sys
from unittest.mock import MagicMock

import numpy as np
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import src.agents.baselines.dbot.agent as dbot_agent_module
from src.agents.agent import LLMAgent
from src.agents.baselines.dbot.agent import DbotAgent, ExpertSolver
from src.agents.baselines.dbot.knowledge import DbotKnowledge
from src.agents.baselines.dbot.mcts import TreeSearchConfig
from src.agents.baselines.dbot.prompts import DBOT_FINAL_TURN_PROMPT
from src.agents.baselines.dbot.types import DbotReport, ExpertDiagnosis
from src.execution.environments.postgres import PGEnv


def db_gpt_tool_schemas():
    return PGEnv(deployment=object(), tool_profile="db_gpt").get_tool_schemas()


def history_tool_schemas(management_tool):
    return [
        {"function": {"name": "query_history"}},
        {"function": {"name": management_tool}},
    ]


class RecordingGateway:
    """Thread-safe-enough fake gateway: returns scripted results per api."""

    def __init__(self, results=None):
        self.calls = []
        self.results = results or {}

    def execute(self, api, args, *, thinking="", source=""):
        self.calls.append({"api": api, "args": args, "source": source})
        if api in self.results:
            return self.results[api]
        return {"status": "success", "api": api, "metric": args.get("metric_type", api),
                "value": {"sample": "evidence"}}


def make_agent(replies=None, **kwargs):
    """Build a DbotAgent whose top-level LLM returns scripted text replies."""
    agent = DbotAgent(
        model="fake",
        url="http://example.com/v1",
        api_key="test",
        config_path="missing.json",
        **kwargs,
    )
    scripted = list(replies or [])

    fake_llm = MagicMock()
    fake_llm.call_text.side_effect = lambda prompt, system_prompt=None: (
        scripted.pop(0) if scripted else (_ for _ in ()).throw(RuntimeError("no scripted reply"))
    )
    agent._llm = fake_llm
    agent._scripted = scripted
    return agent


def make_solver(expert_name="CpuExpert", alert="High CPU", replies=None,
                tool_schemas=None, knowledge=None, use_native_tools=False, gateway=None,
                max_turns=20, search_config=None, rng=None):
    scripted = list(replies or [])
    fake_llm = MagicMock()
    fake_llm.call_text.side_effect = lambda prompt, system_prompt=None: (
        scripted.pop(0) if scripted else (_ for _ in ()).throw(RuntimeError("no scripted reply"))
    )
    fake_llm.get_last_usage_event.return_value = {"input_tokens": 0, "output_tokens": 0}
    fake_llm.get_usage_events.return_value = []
    solver = ExpertSolver(
        expert_name=expert_name,
        alert=alert,
        tool_schemas=tool_schemas or db_gpt_tool_schemas(),
        knowledge=knowledge,
        use_native_tools=use_native_tools,
        search_config=search_config or TreeSearchConfig(),
        max_turns=max_turns,
        llm=fake_llm,
        gateway=gateway or RecordingGateway(),
        rng=rng or np.random.default_rng(0),
    )
    return solver


class TestRoleAssignment:
    def test_parse_selected_experts(self):
        agent = make_agent(max_hired_experts=3)
        selected = agent._select_experts("High CPU and slow query", "1. CpuExpert\n2. QueryExpert")
        assert selected == ["CpuExpert", "QueryExpert"]
        assert set(agent.diagnoses) == {"CpuExpert", "QueryExpert"}

    def test_role_assignment_trims_by_reply_order(self):
        agent = make_agent(max_hired_experts=1)
        selected = agent._select_experts("High CPU and slow query", "QueryExpert CpuExpert")
        assert selected == ["QueryExpert"]

    def test_empty_role_assignment_raises(self):
        agent = make_agent(max_hired_experts=2)
        with pytest.raises(RuntimeError):
            agent._select_experts("WAL disk space is exhausted", "")

    def test_unknown_local_knowledge_expert_is_rejected(self, tmp_path):
        path = tmp_path / "General.jsonl"
        path.write_text(
            '{"expert_name":"GeneralExpert","desc":"generic","metrics":"cpu","steps":"check"}\n',
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            make_agent(knowledge_paths=[str(path)])

    def test_knowledge_paths_drive_agent_knowledge(self, tmp_path):
        path = tmp_path / "CpuExpert.jsonl"
        path.write_text(
            '{"cause_name":"high_cpu","desc":"CPU query bottleneck","metrics":"cpu topsql","steps":"optimize SQL"}\n',
            encoding="utf-8",
        )
        agent = make_agent(knowledge_paths=[str(path)])
        assert agent.knowledge is not None
        assert agent.expert_names == ["CpuExpert"]

    def test_rejects_old_paper_mode(self):
        with pytest.raises(ValueError):
            make_agent(mode="dbot_tree")


class TestExpertSolverSteps:
    def test_history_tool_name_does_not_identify_database_system(self):
        pg_agent = make_agent()
        pg_agent.set_tools(history_tool_schemas("manage_instance"))
        assert pg_agent._is_tidb is False

        tidb_agent = make_agent()
        tidb_agent.set_tools(history_tool_schemas("manage_cluster"))
        assert tidb_agent._is_tidb is True

        pg_solver = make_solver(tool_schemas=history_tool_schemas("manage_instance"))
        tidb_solver = make_solver(tool_schemas=history_tool_schemas("manage_cluster"))
        assert pg_solver._is_tidb is False
        assert tidb_solver._is_tidb is True

    def test_chain_depth_limit_resets_for_each_simulation(self):
        solver = make_solver(
            max_turns=10,
            search_config=TreeSearchConfig(
                simulation_count=2,
                single_chain_max_step=1,
            ),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                "Reflection: first chain reached its depth limit.",
                "candidate_0",
                'Thought: Check CPU again\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                "Reflection: second chain reached its depth limit.",
                "candidate_1",
                "CPU saturation is the root cause.",
                "Optimize the CPU-heavy SQL.",
            ],
        )

        diagnosis = solver.run()

        assert solver.turn_count == 2
        assert diagnosis.search["simulation_index"] == 2
        assert len(diagnosis.search["candidates"]) == 2
        assert len(diagnosis.steps) == 2

    def test_early_finish_preserves_budget_for_second_simulation(self):
        solver = make_solver(
            max_turns=4,
            search_config=TreeSearchConfig(simulation_count=2),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: First candidate\nAction: finish\nAction Input: {"diagnose":"CPU candidate one","solution":["optimize SQL"],"knowledge":"CPU evidence"}',
                "Reflection: first candidate is useful.",
                "candidate_0",
                'Thought: Check CPU again\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: Second candidate\nAction: finish\nAction Input: {"diagnose":"CPU candidate two","solution":["reduce load"],"knowledge":"TopSQL evidence"}',
                "Reflection: second candidate is stronger.",
                "candidate_1",
                "CPU saturation is the root cause.",
                "Optimize the CPU-heavy SQL.",
            ],
        )

        diagnosis = solver.run()

        assert solver.turn_count == 4
        assert diagnosis.search["simulation_index"] == 2
        assert len(diagnosis.search["candidates"]) == 2
        assert all(
            DBOT_FINAL_TURN_PROMPT not in call.args[0]
            for call in solver.llm.call_text.call_args_list
        )

    def test_max_turns_adds_final_finish_prompt(self):
        solver = make_solver(
            max_turns=1,
            search_config=TreeSearchConfig(
                simulation_count=1,
                single_chain_max_step=1,
            ),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: Final diagnosis\nAction: finish\nAction Input: {"diagnose":"CPU saturation","solution":["optimize SQL"],"knowledge":"CPU evidence"}',
                "Reflection: CPU evidence is sufficient.",
                "candidate_0",
                "CPU saturation is the root cause.",
                "Optimize the CPU-heavy SQL.",
            ],
        )

        diagnosis = solver.run()

        prompts = [call.args[0] for call in solver.llm.call_text.call_args_list]
        assert DBOT_FINAL_TURN_PROMPT in prompts[1]
        assert solver.turn_count == 1
        assert diagnosis.search["max_turns"] == 1
        assert diagnosis.search["simulation_index"] == 1
        assert diagnosis.search["candidates"][0]["finish"]["diagnose"] == "CPU saturation"

    def test_final_turn_rejects_non_finish_tool(self):
        solver = make_solver(
            max_turns=1,
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: Check CPU again\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
            ],
        )

        with pytest.raises(
            RuntimeError,
            match="D-Bot expert final turn must call only finish",
        ):
            solver.run()

    def test_native_final_turn_rejects_finish_plus_another_tool(self, monkeypatch):
        solver = make_solver(use_native_tools=True, max_turns=1)
        solver._start_simulation_if_needed()
        llm = LLMAgent(
            url="mock",
            api_key="mock",
            model="mock-model",
            use_native_tools=True,
        )
        request_messages = []

        def fake_call(messages):
            request_messages.append(messages)
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_finish",
                                "type": "function",
                                "function": {
                                    "name": "finish",
                                    "arguments": json.dumps({
                                        "diagnose": "CPU saturation",
                                        "solution": ["optimize SQL"],
                                        "knowledge": "CPU evidence",
                                    }),
                                },
                            },
                            {
                                "id": "call_metric",
                                "type": "function",
                                "function": {
                                    "name": "query_metrics",
                                    "arguments": json.dumps({"metric_type": "cpu"}),
                                },
                            },
                        ],
                    }
                }]
            }

        monkeypatch.setattr(llm, "_call_llm", fake_call)
        monkeypatch.setattr(llm, "get_last_usage_event", lambda: {"input_tokens": 0, "output_tokens": 0})
        solver.llm = llm

        with pytest.raises(
            RuntimeError,
            match="additional_tool_calls=1",
        ):
            solver._next_db_gpt_action(final_turn=True)

        assert DBOT_FINAL_TURN_PROMPT in request_messages[0][1]["content"]

    def test_build_steps_use_db_gpt_tool_names(self):
        solver = make_solver()
        step = solver._build_initial_step("CpuExpert")
        assert step.tool_name == "whether_is_abnormal_metric"
        assert step.aiops_action == {"api": "whether_is_abnormal_metric", "args": {"metric_name": "cpu"}}

        knowledge = solver._build_knowledge_step("QueryExpert", {"metric": "slow_queries"}, "check knowledge")
        assert knowledge.tool_name == "match_diagnose_knowledge"
        assert knowledge.aiops_action["api"] == "match_diagnose_knowledge"
        assert knowledge.tool_input["metric_prefix"] == "cpu"

    def test_knowledge_observation_includes_expert_knowledge(self, tmp_path):
        path = tmp_path / "CpuExpert.jsonl"
        path.write_text(
            '{"cause_name":"high_cpu","desc":"CPU query bottleneck","metrics":"cpu topsql","steps":"optimize SQL"}\n',
            encoding="utf-8",
        )
        kb = DbotKnowledge([str(path)], top_k=5)
        solver = make_solver(knowledge=kb)
        step = solver._build_knowledge_step("CpuExpert", {"metric": "cpu"}, "check knowledge")
        solver._finalize_step_observation(step, {
            "results": [
                {"status": "success", "metric": "cpu", "kind": "series", "series": {"postgres": {"timestamps": ["2026-07-28 10:00:00"], "percent": [95]}}},
                {"status": "success", "metric": "topsql", "kind": "records", "records": [{"query": "select * from t"}]},
                {"status": "success", "metric": "slow_queries", "kind": "records", "records": [{"query": "select * from t"}]},
            ]
        })
        assert step.tool_name == "match_diagnose_knowledge"
        assert step.tool_input["matched_knowledge"][0]["source"].endswith("CpuExpert.jsonl:1")
        assert "CPU query bottleneck" in step.tool_input["matched_knowledge"][0]["content"]

    def test_match_diagnose_knowledge_aggregates_metrics_workload_slow_queries(self):
        solver = make_solver()
        step = solver._build_knowledge_step("CpuExpert", {"metric_name": "CpuExpert"}, "check evidence")
        solver._finalize_step_observation(step, {
            "results": [
                {"status": "success", "metric": "cpu", "kind": "series", "series": {"postgres": {"timestamps": ["2026-07-28 10:00:00"], "percent": [95]}}},
                {"status": "success", "metric": "topsql", "kind": "records", "records": [{"query": "select * from t"}]},
                {"status": "success", "metric": "slow_queries", "kind": "records", "records": [{"query": "select * from t"}]},
            ]
        })
        assert "The abnormal metrics are" in step.db_gpt_observation
        assert "The workload queries are" in step.db_gpt_observation
        assert "The slow queries" in step.db_gpt_observation
        assert [item["metric"] for item in step.top_metrics] == ["cpu", "topsql", "slow_queries"]

    def test_metric_prefix_matches_db_gpt_source_logic(self):
        solver = make_solver()
        assert solver._build_knowledge_step("MemoryExpert", {}, "memory").tool_input["system_metrics"] == [
            "memory", "cache_hit_ratio", "active_connections",
        ]
        assert solver._build_knowledge_step("IoExpert", {}, "io").tool_input["system_metrics"] == [
            "disk_io", "disk_usage", "cache_hit_ratio",
        ]
        assert solver._build_knowledge_step("DiskExpert", {}, "disk").tool_input["system_metrics"] == [
            "cpu", "active_connections", "qps",
        ]

    def test_index_advisor_collects_workload_not_index_usage(self):
        solver = make_solver()
        step = solver._build_index_advisor_step("IndexExpert", {"start_time": "s", "end_time": "e"}, "advise indexes")
        assert step.tool_name == "optimize_index_selection"
        assert step.aiops_action == {"api": "optimize_index_selection", "args": {"start_time": "s", "end_time": "e"}}

    def test_builds_direct_environment_tool_step(self):
        solver = make_solver()
        step = solver._build_tool_step(
            "CpuExpert", "read_log", {"log_type": "pg_log", "lines": 20}, "check logs directly",
        )
        assert step.tool_name == "read_log"
        assert step.aiops_actions == [{"api": "read_log", "args": {"log_type": "pg_log", "lines": 20}}]
        solver._finalize_step_observation(step, {"status": "success", "content": "log line"})
        assert "Environment tool read_log returned" in step.db_gpt_observation

    def test_prepare_requires_evidence(self):
        solver = make_solver(expert_name="QueryExpert")
        with pytest.raises(RuntimeError):
            solver._prepare_expert_diagnosis()


class TestExpertSolverSearch:
    def test_parse_react_action_and_finish(self):
        solver = make_solver()
        solver.tree = None
        action = solver._parse_react_action(
            'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu_usage"}'
        )
        assert action.tool_name == "whether_is_abnormal_metric"
        assert action.tool_input == {"metric_name": "cpu_usage"}

        finish = solver._parse_react_action(
            'Thought: Done\nAction: finish\n'
            'Action Input: {"diagnose":"cpu","solution":["tune sql"],"knowledge":"cpu docs"}'
        )
        assert finish.tool_name == "finish"
        assert finish.tool_input == {"diagnose": "cpu", "solution": ["tune sql"], "knowledge": "cpu docs"}

    def test_submit_is_rejected_inside_expert_search(self):
        solver = make_solver()
        with pytest.raises(ValueError):
            solver._parse_react_action('Thought: Done\nAction: submit\nAction Input: {}')

    def test_schema_driven_solver_rejects_unavailable_tools(self):
        env = PGEnv(deployment=object(), tool_profile="no_knowledge")
        solver = make_solver(tool_schemas=env.get_tool_schemas())
        with pytest.raises(ValueError):
            solver._parse_react_action(
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu_usage"}'
            )

    def test_schema_driven_solver_accepts_pg_env_tools(self):
        env = PGEnv(deployment=object(), tool_profile="no_knowledge")
        solver = make_solver(tool_schemas=env.get_tool_schemas())
        parsed = solver._parse_react_action(
            'Thought: Check CPU\nAction: query_metrics\nAction Input: {"metric_type":"cpu","target":null}'
        )
        assert parsed.tool_name == "query_metrics"
        assert parsed.tool_input == {"metric_type": "cpu", "target": None}

    def test_vote_backpropagates_value_to_terminal_and_ancestors(self):
        np.random.seed(0)
        solver = make_solver()
        parsed = solver._parse_react_action(
            'Thought: Done\nAction: finish\n'
            'Action Input: {"diagnose":"cpu","solution":["tune sql"],"knowledge":"cpu docs"}'
        )
        candidate = solver._finish_candidate(parsed)
        solver._complete_vote_round("candidate_0")
        terminal = solver.tree.get_node(candidate.terminal_node_id)
        assert terminal.is_terminal
        assert terminal.values
        assert solver.tree.root.values
        assert solver.selected_candidate == candidate
        assert candidate.finish["diagnose"] == "cpu"

    def test_uct_decision_uses_db_gpt_random_multinomial(self):
        solver = make_solver(rng=np.random.default_rng(2))
        solver._start_simulation_if_needed()
        solver.tree.add_child(solver.tree.root, "Thought", "old branch")
        assert solver._make_decision_by_value(solver.tree.root) == -1

    def test_vote_candidates_are_random_subset_with_local_numbering(self):
        np.random.seed(1)
        solver = make_solver()
        for idx in range(3):
            parsed = solver._parse_react_action(
                'Thought: candidate {idx}\nAction: finish\n'
                'Action Input: {{"diagnose":"candidate {idx}","solution":["s"],"knowledge":"k"}}'.format(idx=idx)
            )
            solver._finish_candidate(parsed)
        ctx = solver._vote_prompt_context()
        assert "candidate 0" in ctx["candidates"]
        assert "candidate 2" in ctx["candidates"]
        assert "candidate 1" not in ctx["candidates"]
        assert "<candidate_0>" in ctx["candidates"]
        assert "<candidate_1>" in ctx["candidates"]


class TestPromptSlimming:
    """Prompts carry compact evidence; full observations stay in steps and the trace."""

    def _walk(self, node):
        yield node
        for child in node.children:
            yield from self._walk(child)

    def test_tree_observation_stores_compact_text_not_raw_result(self):
        gateway = RecordingGateway(results={
            "read_log": {"status": "success", "content": "log line", "padding": "P" * 3000},
        })
        solver = make_solver(
            tool_schemas=PGEnv(deployment=object(), tool_profile="no_knowledge").get_tool_schemas(),
            gateway=gateway,
            search_config=TreeSearchConfig(simulation_count=1),
            replies=[
                'Thought: Read logs\nAction: read_log\nAction Input: {"log_type":"pg_log","lines":10}',
                'Thought: Done\nAction: finish\nAction Input: {"diagnose":"d","solution":["s"],"knowledge":"k"}',
                "Reflection: logs were enough.",
                "candidate_0",
                "root cause",
                "solution",
            ],
        )

        diagnosis = solver.run()

        observations = [node.observation for node in self._walk(solver.tree.root) if node.observation]
        assert observations == [diagnosis.steps[0].db_gpt_observation]
        assert "P" * 1300 not in observations[0]
        assert '"raw"' not in observations[0]
        assert "P" * 3000 in json.dumps(diagnosis.steps[0].observation)

    def test_abnormal_metric_observation_is_bounded(self):
        solver = make_solver()
        step = solver._build_initial_step("CpuExpert")
        solver._finalize_step_observation(step, {"status": "success", "metric": "cpu", "padding": "P" * 3000})
        assert "P" * 1300 not in step.db_gpt_observation
        assert step.db_gpt_observation.startswith("The metric cpu was checked for abnormality.")

    def test_environment_tool_steps_are_cited_once(self):
        solver = make_solver()
        step = solver._build_tool_step("CpuExpert", "read_log", {"log_type": "pg_log", "lines": 20}, "check logs")
        solver._finalize_step_observation(step, {"status": "success", "content": "log line"})
        solver.diagnosis.steps.append(step)

        diagnosis = solver._prepare_expert_diagnosis()

        assert [item["type"] for item in diagnosis.knowledge] == ["read_log"]

    def test_native_text_fallback_records_conversation_pair(self, monkeypatch):
        solver = make_solver(use_native_tools=True)
        solver._start_simulation_if_needed()
        llm = LLMAgent(url="mock", api_key="mock", model="mock-model", use_native_tools=True)

        def fake_call(messages):
            return {"choices": [{"message": {
                "role": "assistant",
                "content": 'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
            }}]}

        monkeypatch.setattr(llm, "_call_llm", fake_call)
        monkeypatch.setattr(llm, "get_last_usage_event", lambda: {"input_tokens": 12, "output_tokens": 3})
        solver.llm = llm

        parsed = solver._next_db_gpt_action()

        assert parsed.tool_name == "whether_is_abnormal_metric"
        assert parsed.total_input_tokens == 12
        assert [message["role"] for message in solver.conversation] == ["user", "assistant"]
        assert solver.conversation[0]["task"] == "mcts_action:CpuExpert"

    def test_former_candidates_use_summaries_not_full_trajectories(self):
        gateway = RecordingGateway(results={
            "whether_is_abnormal_metric": {"status": "success", "metric": "cpu", "padding": "P" * 3000},
        })
        solver = make_solver(
            gateway=gateway,
            search_config=TreeSearchConfig(simulation_count=2),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: First\nAction: finish\nAction Input: {"diagnose":"CPU saturation","solution":["optimize SQL"],"knowledge":"cpu evidence"}',
                "Reflection: first candidate is solid.",
                "candidate_0",
                'Thought: Check again\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: Second\nAction: finish\nAction Input: {"diagnose":"CPU again","solution":["reduce load"],"knowledge":"topsql"}',
                "Reflection: second candidate is weaker.",
                "candidate_1",
                "root cause",
                "solution",
            ],
        )

        solver.run()

        prompts = [call.args[0] for call in solver.llm.call_text.call_args_list]
        second_simulation_prompt = prompts[4]
        assert "<candidate_0>" in second_simulation_prompt
        assert "Actions: whether_is_abnormal_metric(" in second_simulation_prompt
        assert "Diagnose: CPU saturation" in second_simulation_prompt
        assert 'Solution: ["optimize SQL"]' in second_simulation_prompt
        assert second_simulation_prompt.count("Reflection: first candidate is solid.") == 1
        assert all("P" * 1300 not in prompt for prompt in prompts)

        vote_prompt = prompts[7]
        assert "Diagnose: CPU again" in vote_prompt
        assert "Reflection: second candidate is weaker." in vote_prompt

    def test_step_limited_candidate_summary_marks_missing_finish(self):
        solver = make_solver(
            search_config=TreeSearchConfig(simulation_count=1, single_chain_max_step=1),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                "Reflection: depth limit.",
                "candidate_0",
                "root cause",
                "solution",
            ],
        )

        solver.run()

        summary = solver._candidate_summary(solver.candidates[0])
        assert summary.startswith("Actions: whether_is_abnormal_metric(")
        assert "without calling finish" in summary
        assert "Diagnose:" not in summary

    def test_expert_diagnosis_prompts_use_selected_trajectory_only(self):
        solver = make_solver(
            search_config=TreeSearchConfig(simulation_count=1),
            replies=[
                'Thought: Check CPU\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
                'Thought: Done\nAction: finish\nAction Input: {"diagnose":"d","solution":["s"],"knowledge":"k"}',
                "Reflection: enough.",
                "candidate_0",
                "root cause",
                "solution",
            ],
        )

        diagnosis = solver.run()

        prompts = [call.args[0] for call in solver.llm.call_text.call_args_list]
        root_cause_prompt, solution_prompt = prompts[4], prompts[5]
        assert diagnosis.selected_trajectory in root_cause_prompt
        assert diagnosis.selected_trajectory in solution_prompt
        assert "root cause" in solution_prompt
        assert "AiOpsBench Actions" not in root_cause_prompt
        assert "AiOpsBench Actions" not in solution_prompt

    def test_report_context_drops_diagnosis_process(self):
        agent = make_agent()
        report = DbotReport(
            diagnosis_process="X" * 9000,
            roundtable_reviews=[{"expert": "CpuExpert", "review": "ok"}],
        )

        context = json.loads(agent._report_context(report))

        assert set(context) == {"roundtable_reviews", "citations", "top_metrics"}

    def test_roundtable_context_caps_selected_trajectory(self):
        agent = make_agent(max_hired_experts=1)
        agent.selected_experts = ["CpuExpert"]
        agent.diagnoses["CpuExpert"] = ExpertDiagnosis(expert_name="CpuExpert", selected_trajectory="T" * 5000)

        context = json.loads(agent._all_diagnoses_context())

        assert len(context["selected_trajectory"]) == 1500

    def test_citation_marking_submits_via_mark_citations_tool(self):
        agent = make_agent()
        agent.use_native_tools = False

        def fake_call_text(prompt, system_prompt=None):
            assert "Citations:" in prompt
            assert "Respond in this exact format" in prompt
            return (
                'Thought: Mark citations.\nAction: mark_citations\n'
                'Action Input: {"root_cause":"root [1]","solutions":"solution [1]"}'
            )

        agent._llm.call_text.side_effect = fake_call_text
        root_cause, solutions = agent._mark_citations("root", "solution", "[1] src. desc")
        assert root_cause == "root [1]"
        assert solutions == "solution [1]"

    def test_citation_marking_rejects_other_tools(self):
        agent = make_agent()
        agent.use_native_tools = False
        agent._llm.call_text.side_effect = lambda prompt, system_prompt=None: (
            'Thought: Done\nAction: finish\n'
            'Action Input: {"diagnose":"d","solution":["s"],"knowledge":"k"}'
        )
        with pytest.raises(ValueError, match="mark_citations"):
            agent._mark_citations("root", "solution", "[1] src. desc")

    def test_citation_marking_rejects_missing_fields(self):
        agent = make_agent()
        agent.use_native_tools = False
        agent._llm.call_text.side_effect = lambda prompt, system_prompt=None: (
            'Thought: Mark citations.\nAction: mark_citations\n'
            'Action Input: {"root_cause":"root [1]","solutions":"  "}'
        )
        with pytest.raises(ValueError, match="missing or empty"):
            agent._mark_citations("root", "solution", "[1] src. desc")

    def test_citation_marking_native_tool_call(self, monkeypatch):
        agent = make_agent()
        agent.use_native_tools = True
        llm = LLMAgent(url="mock", api_key="mock", model="mock-model", use_native_tools=True)

        def fake_call(messages):
            return {"choices": [{"message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": "call_mark",
                    "type": "function",
                    "function": {
                        "name": "mark_citations",
                        "arguments": json.dumps({
                            "root_cause": "root [1]",
                            "solutions": "solution [1]",
                        }),
                    },
                }],
            }}]}

        monkeypatch.setattr(llm, "_call_llm", fake_call)
        agent._llm = llm

        root_cause, solutions = agent._mark_citations("root", "solution", "[1] src. desc")

        assert root_cause == "root [1]"
        assert solutions == "solution [1]"
        assert any(
            message.get("task") == "report_citation_mark" and message["role"] == "user"
            for message in agent._conversation
        )

    def test_citation_marking_native_rejects_parallel_tool_calls(self, monkeypatch):
        agent = make_agent()
        agent.use_native_tools = True
        llm = LLMAgent(url="mock", api_key="mock", model="mock-model", use_native_tools=True)

        def fake_call(messages):
            tool_call = {
                "id": "call_mark",
                "type": "function",
                "function": {
                    "name": "mark_citations",
                    "arguments": json.dumps({"root_cause": "root [1]", "solutions": "solution [1]"}),
                },
            }
            return {"choices": [{"message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [tool_call, dict(tool_call, id="call_mark_2")],
            }}]}

        monkeypatch.setattr(llm, "_call_llm", fake_call)
        agent._llm = llm

        with pytest.raises(RuntimeError, match="exactly once"):
            agent._mark_citations("root", "solution", "[1] src. desc")


class TestDbotFlow:
    """End-to-end: a single expert solves via gateway, then report is built."""

    def _single_expert_replies(self):
        return [
            "During inspection, the database had high CPU with slow SQL.",  # anomaly description
            "Analysis Report of High CPU With Slow SQL",                     # title
            "CpuExpert",                                                     # role assignment
            # roundtable + report (after expert finishes)
            "The cross review is evidence-backed.",
            "Refined root cause from ChiefDBA.",
            "Refined solution from ChiefDBA.",
            'Thought: Mark citations.\nAction: mark_citations\nAction Input: '
            '{"root_cause":"Refined root cause from ChiefDBA. [1]",'
            '"solutions":"Refined solution from ChiefDBA. [1]"}',
            "['CPU CONTENTION']",                                            # labels
            '{"actions": [], "rationale": "No safe remediation is supported."}',  # remediation plan
        ]

    def _expert_replies(self):
        return [
            'Thought: Check CPU first\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu_usage"}',
            'Thought: Report candidate\nAction: finish\nAction Input: {"diagnose":"CPU contention from slow SQL","solution":["optimize CPU-heavy SQL"],"knowledge":"cpu knowledge"}',
            "Reflection: first candidate has CPU evidence.",
            "candidate_0",
            'Thought: Check again\nAction: whether_is_abnormal_metric\nAction Input: {"metric_name":"cpu"}',
            'Thought: Report second\nAction: finish\nAction Input: {"diagnose":"CPU contention from TopSQL","solution":["reduce expensive SQL"],"knowledge":"topsql knowledge"}',
            "Reflection: second candidate uses TopSQL evidence.",
            "candidate_1",
            "CpuExpert root cause from selected trajectory.",
            "CpuExpert solution from selected trajectory.",
        ]

    def test_full_flow_submits_report(self, monkeypatch):
        np.random.seed(0)
        agent = make_agent(replies=self._single_expert_replies(), max_hired_experts=1)
        agent.use_native_tools = False
        agent.set_tools(db_gpt_tool_schemas())
        agent.set_user_prompt("High CPU with slow SQL")
        agent.init_env_gateway(RecordingGateway())

        # Each ExpertSolver gets its own scripted LLM instead of a real one.
        expert_replies = self._expert_replies()

        def fake_new_llm():
            scripted = list(expert_replies)
            fake = MagicMock()
            fake.call_text.side_effect = lambda prompt, system_prompt=None: scripted.pop(0)
            fake.get_last_usage_event.return_value = {"input_tokens": 0, "output_tokens": 0}
            fake.get_usage_events.return_value = []
            return fake

        monkeypatch.setattr(agent, "_new_llm", fake_new_llm)

        submission = agent.solve()

        report = submission["report"]
        assert report["summary"] == "Analysis Report of High CPU With Slow SQL"
        assert report["diagnosis"]["conditions"][0]["factor"] == "Refined root cause from ChiefDBA. [1]"
        assert report["outcome"]["changes"] == ["Refined solution from ChiefDBA. [1]"]
        assert report["outcome"]["verification"] == ["The cross review is evidence-backed."]
        diagnosis = agent.diagnoses["CpuExpert"]
        assert diagnosis.root_cause == "CpuExpert root cause from selected trajectory."
        assert diagnosis.solutions == "CpuExpert solution from selected trajectory."
        assert diagnosis.search["selected_candidate"]
        remediation_tasks = [
            message["task"] for message in agent._conversation
            if message.get("role") == "user" and str(message.get("task", "")).startswith("remediation")
        ]
        assert remediation_tasks == ["remediation_plan"]

    def test_full_flow_executes_remediation_and_verifies(self, monkeypatch):
        np.random.seed(0)
        gateway = RecordingGateway(results={
            "execute_sql": {"status": "success", "message": "SQL executed."},
        })
        agent = make_agent(
            replies=self._single_expert_replies()[:-1] + [
                '{"actions": [{"api": "execute_sql", "args": {"sql_query": '
                '"CREATE INDEX idx_orders_customer_id ON orders(customer_id)"}}], '
                '"rationale": "The missing index is actionable."}',
                '{"queries": ["SELECT * FROM pg_indexes WHERE indexname = \'idx_orders_customer_id\'"]}',
            ],
            max_hired_experts=1,
        )
        agent.use_native_tools = False
        agent.set_tools(db_gpt_tool_schemas())
        agent.set_user_prompt("High CPU with slow SQL")
        agent.init_env_gateway(gateway)

        monkeypatch.setattr(agent, "_new_llm", self._fake_expert_llm_factory(self._expert_replies()))

        submission = agent.solve()

        report = submission["report"]
        assert report["outcome"]["changes"] == [
            "execute_sql: CREATE INDEX idx_orders_customer_id ON orders(customer_id) -> "
            '{"status": "success", "message": "SQL executed."}'
        ]
        assert report["outcome"]["verification"] == [
            "execute_sql: SELECT * FROM pg_indexes WHERE indexname = 'idx_orders_customer_id' -> "
            '{"status": "success", "message": "SQL executed."}'
        ]
        remediation_calls = [call for call in gateway.calls if call["source"] == "dbot:remediation"]
        assert [call["api"] for call in remediation_calls] == ["execute_sql", "execute_sql"]
        remediation_turns = agent._export_turns()[-2:]
        assert remediation_turns[0]["actions"] == [{
            "api": "execute_sql",
            "args": {"sql_query": "CREATE INDEX idx_orders_customer_id ON orders(customer_id)"},
        }]
        assert remediation_turns[1]["actions"] == [{
            "api": "execute_sql",
            "args": {"sql_query": "SELECT * FROM pg_indexes WHERE indexname = 'idx_orders_customer_id'"},
        }]

    def test_remediation_plan_invalid_json_raises(self):
        agent = make_agent()
        agent.set_tools(db_gpt_tool_schemas())
        agent._llm.call_text.side_effect = lambda prompt, system_prompt=None: "not a json object"

        with pytest.raises(RuntimeError, match="remediation_plan"):
            agent._run_remediation(DbotReport(root_cause="cpu", solutions="add index"))

    def test_remediation_plan_rejects_unavailable_api(self):
        agent = make_agent()
        agent._tools_schema = db_gpt_tool_schemas()
        agent._llm.call_text.side_effect = lambda prompt, system_prompt=None: (
            '{"actions": [{"api": "query_metrics", "args": {"metric_type": "cpu"}}], "rationale": "r"}'
        )

        with pytest.raises(RuntimeError, match="not an available remediation tool"):
            agent._run_remediation(DbotReport(root_cause="cpu", solutions="add index"))

    @staticmethod
    def _fake_expert_llm_factory(replies):
        scripted = list(replies)

        def factory():
            fake = MagicMock()
            fake.call_text.side_effect = lambda prompt, system_prompt=None: scripted.pop(0)
            fake.get_last_usage_event.return_value = {"input_tokens": 0, "output_tokens": 0}
            fake.get_usage_events.return_value = []
            return fake

        return factory

    def test_roundtable_prompt_includes_previous_reviews(self):
        agent = make_agent(
            replies=[
                "During inspection, CPU and query latency were abnormal.",
                "Analysis Report of CPU and Query Latency",
                "CpuExpert QueryExpert",
                "cpu review",
                "query review",
            ],
            max_hired_experts=2,
        )
        agent.set_user_prompt("High CPU and slow query")
        agent._initialize_reporter()
        agent._assign_roles()
        agent.diagnoses["CpuExpert"].root_cause = "cpu root"
        agent.diagnoses["CpuExpert"].solutions = "cpu solution"
        agent.diagnoses["QueryExpert"].root_cause = "query root"
        agent.diagnoses["QueryExpert"].solutions = "query solution"

        seen_prompts = []
        scripted = ["cpu review", "query review"]

        def fake_call(prompt, task):
            seen_prompts.append((task, prompt))
            return scripted.pop(0)

        agent._call_text_llm = fake_call
        agent._run_roundtable()

        assert seen_prompts[0][0] == "roundtable:CpuExpert"
        assert "[]" in seen_prompts[0][1]
        assert seen_prompts[1][0] == "roundtable:QueryExpert"
        assert "cpu review" in seen_prompts[1][1]

    def test_parallel_experts_each_receive_full_max_turns(self, monkeypatch):
        agent = make_agent(max_hired_experts=2)
        agent.selected_experts = ["CpuExpert", "QueryExpert"]
        agent.max_turns = 3
        agent.init_env_gateway(RecordingGateway())
        created = []

        class CapturingSolver:
            def __init__(self, **kwargs):
                self.expert_name = kwargs["expert_name"]
                self.conversation = []
                created.append((self.expert_name, kwargs["max_turns"]))

            def run(self):
                return ExpertDiagnosis(expert_name=self.expert_name)

        monkeypatch.setattr(dbot_agent_module, "ExpertSolver", CapturingSolver)
        monkeypatch.setattr(agent, "_new_llm", lambda: object())

        agent._run_experts_parallel()

        assert created == [("CpuExpert", 3), ("QueryExpert", 3)]
        assert set(agent.diagnoses) == {"CpuExpert", "QueryExpert"}

    def test_pg_env_db_gpt_profile_exposes_semantic_and_remediation_tools(self):
        env = PGEnv(deployment=object(), tool_profile="db_gpt")
        names = [schema["function"]["name"] for schema in env.get_tool_schemas()]
        assert names == [
            "whether_is_abnormal_metric",
            "match_diagnose_knowledge",
            "optimize_index_selection",
            "query_metrics",
            "execute_sql",
            "manage_instance",
            "read_log",
            "help",
            "submit",
            "exit",
        ]

    def test_provider_retry_retries_524_and_raises_after_limit(self):
        from src.agents.baselines.dbot.agent import call_with_provider_retry

        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            raise RuntimeError(
                "D-Bot report_citation_mark LLM call failed: Error code: 524 - "
                "{'retryable': True, 'retry_after': 0}"
            )

        with pytest.raises(RuntimeError, match="Error code: 524"):
            call_with_provider_retry(flaky, "report_citation_mark")
        assert calls["n"] == 3

    def test_provider_retry_retries_bare_overload_message(self, monkeypatch):
        monkeypatch.setattr("src.agents.baselines.dbot.agent.time.sleep", lambda s: None)
        from src.agents.baselines.dbot.agent import call_with_provider_retry

        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            raise RuntimeError(
                "LLM call_text 调用失败: Our servers are currently overloaded. "
                "Please try again later."
            )

        with pytest.raises(RuntimeError, match="overloaded"):
            call_with_provider_retry(flaky, "report_anomaly_description")
        assert calls["n"] == 3

    def test_provider_retry_retries_connection_error(self, monkeypatch):
        monkeypatch.setattr("src.agents.baselines.dbot.agent.time.sleep", lambda s: None)
        from src.agents.baselines.dbot.agent import call_with_provider_retry

        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            raise RuntimeError("LLM call_text 调用失败: Connection error.")

        with pytest.raises(RuntimeError, match="Connection error"):
            call_with_provider_retry(flaky, "report_anomaly_description")
        assert calls["n"] == 3

    def test_provider_retry_retries_generic_processing_error(self, monkeypatch):
        monkeypatch.setattr("src.agents.baselines.dbot.agent.time.sleep", lambda s: None)
        from src.agents.baselines.dbot.agent import call_with_provider_retry

        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            raise RuntimeError(
                "D-Bot native tool LLM call failed for expert=ConfigurationExpert: "
                "An error occurred while processing your request. You can retry "
                "your request, or contact us through our help center"
            )

        with pytest.raises(RuntimeError, match="An error occurred while processing"):
            call_with_provider_retry(flaky, "mcts_native_action:ConfigurationExpert")
        assert calls["n"] == 3

    def test_native_tool_action_retries_bare_overload(self, monkeypatch):
        monkeypatch.setattr("src.agents.baselines.dbot.agent.time.sleep", lambda s: None)
        solver = make_solver(expert_name="ConfigurationExpert", use_native_tools=True)
        responses = [
            {"error": "Our servers are currently overloaded. Please try again later."},
            {"error": "Our servers are currently overloaded. Please try again later."},
        ]
        solver.llm._call_llm.side_effect = lambda *_: (
            responses.pop(0) if responses else {
                "thinking": "check cpu",
                "has_tool_calls": True,
                "tool_calls": [{"api": "query_metrics", "args": {"metric_type": "cpu", "target": "primary"}}],
            }
        )
        solver.llm._parse_llm_response_message.side_effect = lambda response: (
            response, {"role": "assistant", "content": "ok"},
        )

        action = solver._next_native_tool_action("diagnose")

        assert action.tool_name == "query_metrics"
        assert solver.llm._call_llm.call_count == 3

    def test_mark_citations_reparses_raw_tool_args(self):
        agent = make_agent(use_native_tools=True)
        raw_args = '{"root_cause": "RC line1' + chr(10) + chr(10) + 'RC line2", "solutions": "S1"}'
        agent._llm._call_llm.return_value = {"role": "assistant", "content": "mark"}
        agent._llm._parse_llm_response_message.return_value = (
            {
                "thinking": "mark",
                "has_tool_calls": True,
                "tool_calls": [{"api": "mark_citations", "args": {"raw": raw_args}}],
            },
            {"role": "assistant", "content": "mark"},
        )

        root_cause, solutions = agent._mark_citations("rc", "sol", "citations")

        assert root_cause == "RC line1\n\nRC line2"
        assert solutions == "S1"

    def test_provider_retry_passes_through_non_retryable_errors(self):
        from src.agents.baselines.dbot.agent import call_with_provider_retry

        calls = {"n": 0}

        def fatal():
            calls["n"] += 1
            raise RuntimeError("Error code: 401 - invalid api key")

        with pytest.raises(RuntimeError, match="401"):
            call_with_provider_retry(fatal, "task")
        assert calls["n"] == 1

    def test_db_gpt_tool_profile_includes_remediation_tools(self):
        assert {
            "query_metrics", "execute_sql", "manage_instance", "read_log",
        } <= set(PGEnv.TOOL_PROFILES["db_gpt"])

    def test_other_baselines_do_not_require_tool_profile(self):
        from src.agents.baselines.andromeda.agent import AndromedaAgent
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        from src.agents.baselines.panda.agent import PandaAgent
        from src.agents.baselines.v_expel.agent import VExpeLAgent

        for agent_class in (LLMAgent, DbaiopsAgent, AndromedaAgent, PandaAgent, VExpeLAgent):
            assert getattr(agent_class, "required_tool_profile", None) is None


class TestDbotKnowledge:
    def test_load_jsonl(self, tmp_path):
        path = tmp_path / "CpuExpert.jsonl"
        path.write_text(
            '{"cause_name":"high_cpu","desc":"CPU is high","metrics":"cpu_usage"}\n',
            encoding="utf-8",
        )
        kb = DbotKnowledge([str(path)], top_k=1)
        results = kb.retrieve("CPU high", expert_name="CpuExpert")
        assert len(results) == 1
        assert results[0].expert_name == "CpuExpert"

    def test_missing_path_raises(self):
        with pytest.raises(FileNotFoundError):
            DbotKnowledge(["/path/does/not/exist"])
