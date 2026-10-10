"""Tests for DBAIOps baseline agent."""

import json
import os
import sys
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.baselines.dbaiops.types import (
    ADFResult, AnomalyEquation, DiagnosticPath, EvolutionState,
    GraphEdge, GraphNode,
)
from src.agents.baselines.dbaiops.adf import AdaptiveDetectorFunction
from src.agents.baselines.dbaiops.anomaly_model import (
    AnomalyModel, compute_trend,
    TREND_STABLE, TREND_SHARP_RISE, TREND_SHARP_DECLINE,
)
from src.agents.baselines.dbaiops.graph import ExperienceGraph
from src.agents.baselines.dbaiops.retriever import (
    ExperienceRetriever,
    SQL_BACKED_METRIC_QUERIES,
)
from src.agents.agent import FINAL_TURN_SUBMIT_PROMPT, LLMAgent


GRAPH_PATH = os.path.join(
    project_root, "data", "knowledge_graph", "pg_experience_graph.json"
)

MOCK_REPORT = "Mock diagnosis report with root cause and recovery solution."


def make_inner_llm(monkeypatch, replies, report=MOCK_REPORT):
    """Build an inner LLMAgent whose LLM calls are fully mocked."""
    inner_llm = LLMAgent(url="mock", api_key="mock", model="mock-model", use_native_tools=True)
    reply_iter = iter(replies)
    monkeypatch.setattr(
        inner_llm,
        "_next_llm_actions",
        lambda max_empty_retries: next(reply_iter),
    )
    monkeypatch.setattr(
        inner_llm,
        "call_text",
        lambda prompt, system_prompt=None: report,
    )
    return inner_llm


class FakeGateway:
    """Gateway returning realistic result shapes without a database."""

    def __init__(self, cpu_series=(50.0, 51.0, 52.0, 53.0)):
        self.calls = []
        self.cpu_series = list(cpu_series)

    def execute(self, api, args, *, thinking="", source=""):
        self.calls.append((api, args))
        if api == "query_metrics":
            metric = args.get("metric_type", "unknown")
            return {
                "status": "success",
                "metric": metric,
                "kind": "series",
                "series": {
                    "db": {"timestamps": [1, 2, 3, 4], "value": list(self.cpu_series)}
                },
            }
        if api == "execute_sql":
            sql = str(args.get("sql_query", ""))
            if "pg_stat_activity" in sql:
                return {
                    "status": "success",
                    "columns": ["pid", "duration_ms"],
                    "result": [[101, 1200.0], [102, 3400.0]],
                }
            return {
                "status": "success",
                "columns": ["n_dead_tup", "dead_ratio"],
                "result": [[4200, 0.21], [880, 0.05]],
            }
        return {"status": "success", "message": "ok"}


class TestADF:
    """Test Adaptive Detector Function (paper Section 6.1)."""

    def test_normal_values(self):
        adf = AdaptiveDetectorFunction(theta=10.0, score_threshold=1.2)
        values = [10.0, 11.0, 10.5, 10.2, 10.8]
        result = adf.evaluate(values)
        assert not result.is_abnormal
        assert result.sigma < 1.0

    def test_abnormal_spike(self):
        adf = AdaptiveDetectorFunction(theta=10.0, score_threshold=0.5)
        values = [10.0, 11.0, 10.5, 55.0, 58.0, 61.0]
        result = adf.evaluate(values)
        assert result.sigma > 10.0
        assert result.deviation > 20.0

    def test_empty_values(self):
        adf = AdaptiveDetectorFunction()
        result = adf.evaluate([])
        assert not result.is_abnormal
        assert result.score == 0.0

    def test_single_value(self):
        adf = AdaptiveDetectorFunction()
        result = adf.evaluate([42.0])
        assert not result.is_abnormal

    def test_baseline_computation(self):
        adf = AdaptiveDetectorFunction()
        values = [10.0, 12.0, 11.0, 10.5, 50.0]
        result = adf.evaluate(values)
        # Baseline should be close to the earlier values, not the spike
        assert result.baseline < 15.0


class TestAnomalyModel:
    """Test AnomalyModel (paper Section 5.1)."""

    def test_threshold_detection(self):
        eq = AnomalyEquation(metric_raw="cpu", threshold_1=80.0, frequency_m=1, frequency_n=1)
        model = AnomalyModel("test", "trigger_test", [eq])
        assert model.evaluate({"cpu": 90.0})
        assert not model.evaluate({"cpu": 70.0})

    def test_evaluate_raw_skips_frequency_control(self):
        eq = AnomalyEquation(metric_raw="cpu", threshold_1=80.0, frequency_m=3, frequency_n=5)
        model = AnomalyModel("test", "trigger_test", [eq])
        assert model.evaluate_raw({"cpu": 90.0})
        assert not model.evaluate({"cpu": 90.0})

    def test_frequency_control(self):
        eq = AnomalyEquation(metric_raw="cpu", threshold_1=80.0, frequency_m=3, frequency_n=5)
        model = AnomalyModel("test", "trigger_test", [eq])
        # First two evaluations: not enough history
        assert not model.evaluate({"cpu": 90.0})
        assert not model.evaluate({"cpu": 90.0})
        # Third: triggers (3/3 = True)
        assert model.evaluate({"cpu": 90.0})

    def test_trend_detection(self):
        eq = AnomalyEquation(
            metric_raw="disk_io", threshold_1=100.0,
            metric_composite="disk_io_trend", threshold_2=50.0,
            trend_condition=3,  # sharp_rise
            frequency_m=1, frequency_n=1,
        )
        model = AnomalyModel("test", "trigger_test", [eq])
        # Condition 2: trend matches AND raw > threshold_2
        assert model.evaluate({"disk_io": 60.0, "disk_io_trend": 3})
        assert not model.evaluate({"disk_io": 60.0, "disk_io_trend": 0})

    def test_compute_trend_stable(self):
        assert compute_trend([10, 10, 10, 10, 10]) == TREND_STABLE

    def test_compute_trend_sharp_rise(self):
        assert compute_trend([10, 12, 14, 30, 50, 70]) == TREND_SHARP_RISE

    def test_compute_trend_sharp_decline(self):
        assert compute_trend([70, 50, 30, 14, 12, 10]) == TREND_SHARP_DECLINE


class TestExperienceGraph:
    """Test ExperienceGraph (paper Section 4)."""

    def test_load_graph(self):
        graph = ExperienceGraph(GRAPH_PATH)
        assert len(graph.nodes) > 50
        assert len(graph.edges) > 50

    def test_trigger_vertices(self):
        graph = ExperienceGraph(GRAPH_PATH)
        triggers = graph.get_trigger_vertices()
        assert len(triggers) >= 10
        assert all(t.type == "trigger" for t in triggers)

    def test_get_neighbors(self):
        graph = ExperienceGraph(GRAPH_PATH)
        neighbors = graph.get_neighbors("trigger_index_problem")
        assert len(neighbors) > 0

    def test_containment_edges(self):
        graph = ExperienceGraph(GRAPH_PATH)
        exp_nodes = graph.get_neighbors("trigger_index_problem", "containment")
        assert any(n.type == "experience" for n in exp_nodes)

    def test_diagnosis_paths(self):
        graph = ExperienceGraph(GRAPH_PATH)
        paths = graph.get_diagnosis_paths("trigger_index_problem")
        assert len(paths) > 0
        # Paths should reach tool or metric nodes
        for path in paths:
            assert any(n.type in ("tool", "metric", "experience") for n in path.nodes)

    def test_overlapping_models(self):
        graph = ExperienceGraph(GRAPH_PATH)
        overlapping = graph.find_overlapping_models("trigger_index_problem")
        # Should find other triggers sharing tags/metrics
        assert len(overlapping) > 0

    def test_create_cross_edge(self):
        graph = ExperienceGraph(GRAPH_PATH)
        initial_edges = len(graph.edges)
        edge = graph.create_cross_edge("trigger_index_problem", "trigger_high_cpu", "relevance")
        assert edge is not None
        assert len(graph.edges) == initial_edges + 1
        # No duplicate
        edge2 = graph.create_cross_edge("trigger_index_problem", "trigger_high_cpu", "relevance")
        assert edge2 is None


class TestExperienceRetriever:
    """Test ExperienceRetriever (paper Section 6.1)."""

    def test_initialize(self):
        graph = ExperienceGraph(GRAPH_PATH)
        adf = AdaptiveDetectorFunction()
        retriever = ExperienceRetriever(graph, adf)
        state = retriever.initialize("trigger_index_problem")
        assert state.trigger_id == "trigger_index_problem"
        assert len(state.expanded_paths) > 0

    def test_take_pending_actions(self):
        graph = ExperienceGraph(GRAPH_PATH)
        adf = AdaptiveDetectorFunction()
        retriever = ExperienceRetriever(graph, adf)
        retriever.initialize("trigger_index_problem")
        claimed = retriever.take_pending_actions()
        assert claimed
        for node, action in claimed:
            assert node.type in ("metric", "tool")
            assert "api" in action and "args" in action
        # All claimed nodes are marked queried; a second pass claims nothing new
        second_pass = retriever.take_pending_actions()
        assert second_pass == []

    def test_excluded_metric_types_are_skipped(self):
        graph = ExperienceGraph(GRAPH_PATH)
        retriever = ExperienceRetriever(
            graph, AdaptiveDetectorFunction(), exclude_metric_types={"cache_hit_ratio"}
        )
        retriever.initialize("trigger_index_problem")
        claimed = retriever.take_pending_actions()
        assert all(
            node.attributes.get("metric_type", node.name) != "cache_hit_ratio"
            for node, _ in claimed
        )

    @pytest.mark.parametrize("metric", sorted(SQL_BACKED_METRIC_QUERIES))
    def test_sql_backed_metric_nodes_use_execute_sql(self, metric):
        graph = ExperienceGraph(GRAPH_PATH)
        retriever = ExperienceRetriever(graph, AdaptiveDetectorFunction())
        node = GraphNode(
            id=f"metric_{metric}",
            type="metric",
            name=metric,
            content=f"{metric} observation",
            attributes={"api": "query_metrics", "metric_type": metric},
        )

        action = retriever._metric_node_to_action(node)

        assert action == {
            "api": "execute_sql",
            "args": {"sql_query": SQL_BACKED_METRIC_QUERIES[metric]["sql"]},
        }

    @pytest.mark.parametrize("metric", ["active_connections", "disk_usage"])
    def test_environment_metric_nodes_keep_query_metrics(self, metric):
        graph = ExperienceGraph(GRAPH_PATH)
        retriever = ExperienceRetriever(graph, AdaptiveDetectorFunction())
        node = GraphNode(
            id=f"metric_{metric}",
            type="metric",
            name=metric,
            content=f"{metric} observation",
            attributes={"api": "query_metrics", "metric_type": metric},
        )

        action = retriever._metric_node_to_action(node)

        assert action == {
            "api": "query_metrics",
            "args": {"metric_type": metric},
        }

    def test_snapshot_resample_requeries_sql_backed_nodes_only(self):
        graph = ExperienceGraph(GRAPH_PATH)
        retriever = ExperienceRetriever(graph, AdaptiveDetectorFunction())
        retriever.initialize("trigger_index_problem")
        claimed = retriever.take_pending_actions()
        queried_metrics = {
            node.attributes.get("metric_type", node.name)
            for node, _ in claimed
            if node.type == "metric"
        }
        resamples = retriever.take_snapshot_resample_actions()
        resampled_types = {
            node.attributes.get("metric_type", node.name)
            for node, _ in resamples
        }
        assert resampled_types == queried_metrics & set(SQL_BACKED_METRIC_QUERIES)
        assert all(action["api"] == "execute_sql" for _, action in resamples)

    def test_evolution_terminates_on_normal(self):
        graph = ExperienceGraph(GRAPH_PATH)
        adf = AdaptiveDetectorFunction(score_threshold=0.9)
        retriever = ExperienceRetriever(graph, adf)
        retriever.initialize("trigger_index_problem")
        retriever.state.accumulated_metrics["cpu"] = [10.0, 11.0, 10.5, 10.2]
        state = retriever.evolve()
        assert not state.should_continue
        assert state.adf_results
        assert state.adf_results[0].metric == "cpu"

    def test_evolve_skips_sequences_below_min_samples(self):
        graph = ExperienceGraph(GRAPH_PATH)
        retriever = ExperienceRetriever(graph, AdaptiveDetectorFunction())
        retriever.initialize("trigger_index_problem")
        retriever.state.accumulated_metrics["cpu"] = [10.0, 11.0]
        state = retriever.evolve()
        assert state.adf_results == []
        # Not enough evidence yet: evolution continues
        assert state.should_continue

    def test_experience_evidence(self):
        graph = ExperienceGraph(GRAPH_PATH)
        adf = AdaptiveDetectorFunction()
        retriever = ExperienceRetriever(graph, adf)
        retriever.initialize("trigger_dead_tuple")
        evidence = retriever.get_experience_evidence()
        assert len(evidence) > 0
        assert any("vacuum" in e.lower() or "dead" in e.lower() for e in evidence)


class TestDbaiopsAgent:
    """Integration tests for DbaiopsAgent (fully mocked LLM and gateway)."""

    def test_init(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(
            model="mock-model",
            graph_path=GRAPH_PATH,
        )
        assert agent.model == "mock-model"
        assert agent.use_native_tools is True

    def test_set_prompts(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.set_system_prompt("test system")
        agent.set_user_prompt("Slow query detected on table orders")
        assert agent._alert == "Slow query detected on table orders"

    def test_history_tool_name_does_not_identify_tidb(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        def schemas(management_tool):
            return [
                {"function": {"name": "query_history"}},
                {"function": {"name": management_tool}},
            ]

        pg_agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        pg_agent.set_tools(schemas("manage_instance"))
        assert pg_agent._is_tidb is False

        tidb_agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        tidb_agent.set_tools(schemas("manage_cluster"))
        assert tidb_agent._is_tidb is True

    def test_trigger_matching(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.set_user_prompt("Slow query detected, full table scan on orders table")
        agent._ensure_initialized()
        trigger = agent._match_trigger_by_keywords(agent._alert)
        assert trigger is not None
        assert "index" in trigger.id or "query" in trigger.name.lower()

    def test_reset(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.set_user_prompt("test alert")
        agent._turn = 5
        agent._observations.append({"test": True})
        agent._executed_changes.append("execute_sql(UPDATE x)")
        agent.reset()
        assert agent._turn == 0
        assert len(agent._observations) == 0
        assert agent._matched_trigger is None
        assert agent._executed_changes == []

    def test_anomaly_models_derive_composite_trend(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        model = agent._anomaly_models["trigger_index_problem"]
        eq = model.equations[0]
        assert eq.metric_raw == "slow_queries"
        # The graph carries no composite vertex; the trend is derived from METRIC_raw
        assert eq.metric_composite == "slow_queries#trend"
        assert eq.trend_condition is not None

    def test_extract_metrics_from_rows_and_series(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        retriever = agent._retriever
        retriever.initialize("trigger_dead_tuple")
        dead_node = GraphNode(
            id="metric_dead_tuples", type="metric", name="Dead Tuples", content="",
            attributes={"api": "query_metrics", "metric_type": "dead_tuples"},
        )
        cpu_node = GraphNode(
            id="metric_cpu", type="metric", name="CPU", content="",
            attributes={"api": "query_metrics", "metric_type": "cpu"},
        )

        agent._extract_metrics_from_result(
            {"status": "success", "columns": ["n_dead_tup", "dead_ratio"],
             "result": [[4200, 0.21], [880, 0.05]]},
            dead_node,
        )
        agent._extract_metrics_from_result(
            {"status": "success", "metric": "cpu", "kind": "series",
             "series": {"db": {"timestamps": [1, 2, 3], "value": [10.0, 20.0, 30.0]}}},
            cpu_node,
        )

        accumulated = retriever.state.accumulated_metrics
        assert accumulated["dead_tuples.row_count"] == [2.0]
        assert accumulated["dead_tuples.n_dead_tup"] == [5080.0]
        assert accumulated["cpu[db].value"] == [10.0, 20.0, 30.0]

    def test_anomaly_evaluation_uses_mn_frequency(self):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(
            graph_path=GRAPH_PATH, model="mock-model", frequency_m=2, frequency_n=3,
        )
        agent._ensure_initialized()
        retriever = agent._retriever
        retriever.initialize("trigger_high_cpu")
        agent._matched_trigger = retriever.graph.nodes["trigger_high_cpu"]

        for cpu_value in (95.0, 96.0, 97.0):
            retriever.state.accumulated_metrics["cpu[db].value"] = [cpu_value] * 4
            agent._record_trigger_anomaly_evaluation()

        evaluations = agent._anomaly_evaluations
        assert len(evaluations) == 3
        assert all(e["raw_anomaly"] for e in evaluations)
        # M/N control confirms from the second consecutive TRUE (m=2)
        assert [e["frequency_confirmed"] for e in evaluations] == [False, True, True]

    def test_run_llm_loop_text_reply_finalizes_with_report(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        agent.max_turns = 5
        agent.init_env_gateway(FakeGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[("Root cause found.", [])])

        submission = agent._run_llm_loop("Diagnose the alert.")

        assert submission["report"]["summary"] == MOCK_REPORT
        assert submission["report"]["diagnosis"]["conditions"][0]["factor"] == MOCK_REPORT
        assert agent._diagnosis_report == MOCK_REPORT
        last_step = agent._steps[-1]
        assert last_step.source == "llm_diagnosis"
        assert last_step.actions == [{"api": "submit", "args": {}}]

    def test_run_llm_loop_tracks_remediation_changes(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        agent.max_turns = 5
        agent.init_env_gateway(FakeGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Apply the fix.", [
                {"api": "execute_sql", "args": {"sql_query": "CREATE INDEX idx ON orders(id)"}},
                {"api": "execute_sql", "args": {"sql_query": "SELECT * FROM orders"}},
            ]),
            ("Verified.", [{"api": "submit", "args": {}}]),
        ])

        submission = agent._run_llm_loop("Diagnose the alert.")

        changes = submission["report"]["outcome"]["changes"]
        assert changes == ["execute_sql(CREATE INDEX idx ON orders(id))"]
        assert "Remediation actions were executed" in submission["report"]["outcome"]["verification"][0]

    def test_run_llm_loop_exit_raises(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        agent.max_turns = 5
        agent.init_env_gateway(FakeGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Giving up.", [{"api": "exit", "args": {}}]),
        ])

        with pytest.raises(RuntimeError, match="exited without submitting"):
            agent._run_llm_loop("Diagnose the alert.")

    def test_max_turns_adds_final_submit_prompt(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent._ensure_initialized()
        agent.max_turns = 1
        agent.init_env_gateway(FakeGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Inspect CPU.", [{"api": "query_metrics", "args": {"metric_type": "cpu"}}]),
            ("Submit final diagnosis.", [{"api": "submit", "args": {"diagnosis": "CPU saturation"}}]),
        ])

        submission = agent._run_llm_loop("Diagnose the alert.")

        assert submission["report"]["summary"] == MOCK_REPORT
        assert agent._turn == 3
        final_submit_steps = [
            step for step in agent._steps
            if step.messages
            and any(m.get("content") == FINAL_TURN_SUBMIT_PROMPT for m in step.messages)
        ]
        assert final_submit_steps
        # The last step is the RootCauseAnalyser report
        assert agent._steps[-1].source == "llm_diagnosis"

    def test_solve_full_graph_evolution_feeds_adf_and_report(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        gateway = FakeGateway()
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.max_turns = 30
        agent.set_user_prompt("Slow query detected, full table scan on orders table")
        agent.init_env_gateway(gateway)
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Evidence is sufficient.", [{"api": "submit", "args": {}}]),
        ])

        submission = agent.solve()

        assert submission["report"]["summary"] == MOCK_REPORT
        assert agent._diagnosis_prompt
        assert "ADF" in agent._diagnosis_prompt
        # SQL-backed snapshot metrics were re-sampled across evolution iterations
        accumulated = agent._retriever.state.accumulated_metrics
        assert len(accumulated["slow_queries.row_count"]) >= 2
        # ADF produced results for the collected sequences
        assert agent._retriever.state.adf_results
        # The matched trigger's detection equation was evaluated per iteration
        assert agent._anomaly_evaluations
        assert any(
            e["metric_values"].get("slow_queries") is not None
            for e in agent._anomaly_evaluations
        )
        # No remediation executed in this run
        assert submission["report"]["outcome"]["changes"] == [
            "No explicit remediation was reported"
        ]
        # Graph actions went through the gateway
        assert any(api == "execute_sql" for api, _ in gateway.calls)

    def test_solve_fallback_when_no_trigger_matches(self, monkeypatch):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent
        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.max_turns = 5
        agent.set_user_prompt("Completely unknown alien alert")
        agent.init_env_gateway(FakeGateway())
        agent._llm = make_inner_llm(monkeypatch, replies=[
            ("Investigating.", []),
        ])

        submission = agent.solve()

        assert submission["report"]["summary"] == MOCK_REPORT
        assert agent._matched_trigger is None
        assert [step.source for step in agent._steps] == ["llm_diagnosis"]

    @pytest.mark.parametrize(
        ("max_turns", "llm_replies", "expected_sources"),
        [
            (
                1,
                [
                    ("Submit graph evidence.", [
                        {"api": "submit", "args": {}}
                    ]),
                ],
                ["graph", "llm_diagnosis", "llm_diagnosis"],
            ),
            (
                2,
                [
                    ("Inspect once more.", [
                        {"api": "query_metrics", "args": {"metric_type": "cpu"}}
                    ]),
                    ("Submit combined evidence.", [
                        {"api": "submit", "args": {}}
                    ]),
                ],
                ["graph", "llm_remediation", "llm_diagnosis", "llm_diagnosis"],
            ),
        ],
        ids=["graph-exhausts-budget", "graph-and-llm-share-budget"],
    )
    def test_graph_turns_feed_into_final_submit_budget(
        self, monkeypatch, max_turns, llm_replies, expected_sources
    ):
        from src.agents.baselines.dbaiops.agent import DbaiopsAgent

        class OneActionRetriever:
            def __init__(self):
                self.state = EvolutionState()

            def initialize(self, trigger_id):
                self.state = EvolutionState(trigger_id=trigger_id)

            def should_terminate(self):
                return not self.state.should_continue

            def take_pending_actions(self):
                if self.state.queried_nodes:
                    return []
                self.state.queried_nodes.append("metric_cpu")
                node = GraphNode(
                    id="metric_cpu", type="metric", name="cpu", content="",
                    attributes={"metric_type": "cpu"},
                )
                return [(
                    node,
                    {"api": "query_metrics", "args": {"metric_type": "cpu"}},
                )]

            def take_snapshot_resample_actions(self):
                return []

            def evolve(self):
                self.state.should_continue = False

            def get_current_path_for_node(self, node_id):
                return [node_id]

            def get_experience_evidence(self):
                return ["CPU evidence"]

        agent = DbaiopsAgent(graph_path=GRAPH_PATH, model="mock-model")
        agent.max_turns = max_turns
        agent.set_user_prompt("CPU alert")
        gateway = FakeGateway()
        agent.init_env_gateway(gateway)
        agent._retriever = OneActionRetriever()
        trigger = GraphNode(
            id="trigger_cpu",
            type="trigger",
            name="CPU saturation",
            content="CPU saturation trigger",
            attributes={"metric_raw": "cpu", "threshold_1": 80},
        )
        monkeypatch.setattr(agent, "_ensure_initialized", lambda: None)
        monkeypatch.setattr(agent, "_match_trigger_by_keywords", lambda alert: trigger)

        agent._llm = make_inner_llm(monkeypatch, replies=llm_replies)

        submission = agent.solve()

        assert submission["report"]["summary"] == MOCK_REPORT
        assert [step.source for step in agent._steps] == expected_sources
        assert [step.turn_number for step in agent._steps] == list(
            range(1, len(expected_sources) + 1)
        )
        assert agent._steps[-1].actions[0]["api"] == "submit"
        assert any(
            step.messages
            and any(m.get("content") == FINAL_TURN_SUBMIT_PROMPT for m in step.messages)
            for step in agent._steps
        )
        assert len(gateway.calls) >= 1
