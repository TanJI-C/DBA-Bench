"""ExperienceRetriever - Paper Section 6.1.

Two-stage graph evolution: Proximity-based Graph Inference + Statistical-based Graph Clipping.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from src.agents.baselines.dbaiops.adf import AdaptiveDetectorFunction
from src.agents.baselines.dbaiops.graph import ExperienceGraph
from src.agents.baselines.dbaiops.types import (
    ADFResult,
    EvolutionState,
    GraphNode,
)


# SQL-backed metric nodes are served through execute_sql (the agent tool surface does not
# pre-aggregate these into query_metrics). `value_column` names the column whose sum is the
# metric sample; when it is None the row count is the sample (count-defined triggers).
SQL_BACKED_METRIC_QUERIES = {
    "slow_queries": {
        "sql": (
            "SELECT pid, usename, datname, state, wait_event_type, wait_event, query, "
            "extract(epoch FROM clock_timestamp() - query_start) * 1000 AS duration_ms "
            "FROM pg_stat_activity "
            "WHERE state = 'active' AND pid <> pg_backend_pid() "
            "ORDER BY query_start NULLS LAST LIMIT 20;"
        ),
        "value_column": None,
    },
    "topsql": {
        "sql": (
            "SELECT queryid, query, calls, total_exec_time, mean_exec_time "
            "FROM pg_stat_statements "
            "WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database()) "
            "ORDER BY total_exec_time DESC LIMIT 10;"
        ),
        "value_column": None,
    },
    "dead_tuples": {
        "sql": (
            "SELECT schemaname, relname AS table_name, n_live_tup, n_dead_tup, "
            "round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 4) "
            "AS dead_ratio FROM pg_stat_user_tables "
            "ORDER BY n_dead_tup DESC LIMIT 20;"
        ),
        "value_column": "n_dead_tup",
    },
}

# ADF on a 2-sample sequence flags every difference as abnormal (D > σ whenever two
# samples differ), so evaluation starts once a metric has at least 3 samples.
ADF_MIN_SAMPLES = 3


class ExperienceRetriever:
    """Paper Section 6.1: Two-Stage Graph Evolution.

    Stage 1 - Proximity-based Graph Inference:
      Traverse from trigger, collect metrics, discover overlapping models,
      create cross-edges to expand the graph.

    Stage 2 - Statistical-based Graph Clipping (ADF):
      Evaluate collected metric sequences with ADF. If abnormal → continue expanding.
      If all normal → terminate and return diagnosis evidence.
    """

    def __init__(self, graph: ExperienceGraph, adf: AdaptiveDetectorFunction,
                 max_depth: int = 4, top_k: int = 5,
                 exclude_metric_types: Optional[Set[str]] = None):
        self.graph = graph
        self.adf = adf
        self.max_depth = max_depth
        self.top_k = top_k
        self.exclude_metric_types = set(exclude_metric_types or ())
        self.state: Optional[EvolutionState] = None

    def initialize(self, trigger_id: str) -> EvolutionState:
        """Start evolution from a trigger vertex."""
        self.state = EvolutionState(trigger_id=trigger_id)
        # Stage 1: initial proximity discovery
        paths = self.graph.get_diagnosis_paths(trigger_id, self.max_depth)
        self.state.expanded_paths = paths[:self.top_k]
        # Discover overlapping models and create cross-edges
        self._proximity_discovery(trigger_id)
        return self.state

    def take_pending_actions(self) -> List[Tuple[GraphNode, Dict[str, Any]]]:
        """Claim every unqueried metric/tool node on the expanded paths.

        Paper Stage 1: after the graph evolves, all metrics on the evolved paths are
        collected. Excluded metric types (e.g. not on the current tool surface) are
        marked queried and skipped permanently.
        """
        claimed: List[Tuple[GraphNode, Dict[str, Any]]] = []
        if self.state is None:
            return claimed
        for path in self.state.expanded_paths:
            for node in path.nodes:
                if node.id in self.state.queried_nodes:
                    continue
                self.state.queried_nodes.append(node.id)
                if node.type == "metric":
                    if node.attributes.get("metric_type", node.name) in self.exclude_metric_types:
                        continue
                    action = self._metric_node_to_action(node)
                elif node.type == "tool":
                    action = self._tool_node_to_action(node)
                else:
                    continue
                claimed.append((node, action))
        return claimed

    def take_snapshot_resample_actions(self) -> List[Tuple[GraphNode, Dict[str, Any]]]:
        """Re-query already-queried SQL-backed metric nodes.

        Paper Stage 2: the ADF needs a value sequence per metric observed over time.
        query_metrics series metrics carry their full history; SQL-backed snapshot
        metrics only gain a sample per evolution iteration, so they are re-queried
        on every iteration to grow their sequence.
        """
        resamples: List[Tuple[GraphNode, Dict[str, Any]]] = []
        if self.state is None:
            return resamples
        seen: Set[str] = set()
        for path in self.state.expanded_paths:
            for node in path.nodes:
                if node.type != "metric" or node.id in seen:
                    continue
                if node.id not in self.state.queried_nodes:
                    continue
                metric_type = node.attributes.get("metric_type", node.name)
                if metric_type not in SQL_BACKED_METRIC_QUERIES:
                    continue
                seen.add(node.id)
                resamples.append((node, self._metric_node_to_action(node)))
        return resamples

    def evolve(self) -> EvolutionState:
        """Run one iteration of the two-stage evolution loop (ADF clipping + expansion)."""
        if self.state is None:
            raise RuntimeError("Call initialize() first")
        state = self.state
        state.depth += 1

        # Stage 2: Statistical-based Graph Clipping (ADF)
        any_abnormal = False
        any_evaluated = False
        current_results: List[ADFResult] = []
        for metric_name, values in state.accumulated_metrics.items():
            if len(values) < ADF_MIN_SAMPLES:
                continue
            any_evaluated = True
            result = self.adf.evaluate(list(values))
            result = ADFResult(
                metric=metric_name,
                sigma=result.sigma,
                cv=result.cv,
                baseline=result.baseline,
                deviation=result.deviation,
                f_state=result.f_state,
                w1=result.w1,
                w2=result.w2,
                score=result.score,
                is_abnormal=result.is_abnormal,
            )
            current_results.append(result)
            if result.is_abnormal:
                any_abnormal = True

        state.adf_results = current_results

        if not any_evaluated:
            state.should_continue = True
        elif any_abnormal and state.depth < self.max_depth:
            self._expand_from_abnormal_metrics()
            state.should_continue = True
        else:
            state.should_continue = False

        # Snapshot this iteration for history
        state.adf_history.append({
            "depth": state.depth,
            "should_continue": state.should_continue,
            "expanded_paths_count": len(state.expanded_paths),
            "adf_results": [
                {"metric": r.metric, "score": r.score,
                 "is_abnormal": r.is_abnormal, "sigma": r.sigma,
                 "deviation": r.deviation}
                for r in current_results
            ],
        })

        return state

    def should_terminate(self) -> bool:
        """ADF determination: all metrics normal → terminate."""
        if self.state is None:
            return True
        return not self.state.should_continue

    def get_experience_evidence(self) -> List[str]:
        """Collect experience vertex content from explored paths for LLM prompt."""
        if self.state is None:
            return []
        evidence = []
        seen: Set[str] = set()
        for path in self.state.expanded_paths:
            for node in path.nodes:
                if node.type == "experience" and node.id not in seen:
                    seen.add(node.id)
                    evidence.append(f"[{node.name}] {node.content}")
        return evidence

    def get_current_path_for_node(self, node_id: str) -> Optional[List[str]]:
        """Return the node-name chain of the path containing node_id."""
        if self.state is None:
            return None
        for path in self.state.expanded_paths:
            for node in path.nodes:
                if node.id == node_id:
                    return [f"{n.name} ({n.type})" for n in path.nodes]
        return None

    # --- Private methods ---

    def _proximity_discovery(self, trigger_id: str):
        """Stage 1: find overlapping models and create cross-edges."""
        overlapping = self.graph.find_overlapping_models(trigger_id)
        for other_trigger_id in overlapping:
            edge = self.graph.create_cross_edge(
                trigger_id, other_trigger_id, "relevance"
            )
            if edge and self.state:
                self.state.cross_edges_created.append(edge)
            # Also expand paths from overlapping triggers
            extra_paths = self.graph.get_diagnosis_paths(
                other_trigger_id, self.max_depth - 1
            )
            if self.state:
                for p in extra_paths[:2]:
                    if len(self.state.expanded_paths) < self.top_k * 2:
                        self.state.expanded_paths.append(p)

    def _expand_from_abnormal_metrics(self):
        """Expand graph from nodes associated with abnormal metrics."""
        if self.state is None:
            return
        abnormal_metrics = {r.metric for r in self.state.adf_results if r.is_abnormal}
        for path in list(self.state.expanded_paths):
            for node in path.nodes:
                if node.type == "metric" and node.name in abnormal_metrics:
                    # Find connected triggers via this metric
                    incoming = self.graph.get_incoming_neighbors(node.id)
                    for parent in incoming:
                        if parent.type == "trigger" and parent.id != self.state.trigger_id:
                            self._proximity_discovery(parent.id)

    def _metric_node_to_action(self, node: GraphNode) -> Dict[str, Any]:
        """Map a Metric Vertex to an AiOpsBench API call."""
        attrs = node.attributes
        api = attrs.get("api", "query_metrics")
        if api == "query_metrics":
            metric_type = attrs.get("metric_type", node.name)
            target = attrs.get("target")
            if metric_type in SQL_BACKED_METRIC_QUERIES:
                return {
                    "api": "execute_sql",
                    "args": {"sql_query": SQL_BACKED_METRIC_QUERIES[metric_type]["sql"]},
                }
            args = {"metric_type": metric_type}
            if target:
                args["target"] = target
            return {"api": api, "args": args}
        return {"api": "query_metrics", "args": {"metric_type": node.name}}

    def _tool_node_to_action(self, node: GraphNode) -> Dict[str, Any]:
        """Map a Tool Vertex to an AiOpsBench API call."""
        attrs = node.attributes
        api = attrs.get("api", "execute_sql")
        args = attrs.get("args", {})
        if api == "execute_sql" and "sql_query" not in args:
            sql = attrs.get("sql_template", f"SELECT 1 -- {node.name}")
            args = {"sql_query": sql}
        elif api == "read_log":
            args.setdefault("log_type", attrs.get("log_type", "pg_log"))
            args.setdefault("lines", 50)
        return {"api": api, "args": args}
