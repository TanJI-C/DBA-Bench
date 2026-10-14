import argparse
from datetime import datetime, timezone
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeOnlineDdlPauseResumeScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator


CASE_ID = "paused_unique_index_backfill"
ROUTE_TABLE = "route_registry"
ROUTE_BINDING_TABLE = "route_bindings"
CHANGE_REQUEST_TABLE = "schema_change_requests"
ROUTE_LEASE_TABLE = "route_lease_fences"
ROUTE_OWNER_TABLE = "route_owner_heartbeats"
ROUTE_COMMIT_TABLE = "route_cutover_commits"
ROUTE_TRAFFIC_TABLE = "route_traffic_assignments"
ROUTE_RUNTIME_TABLE = "route_runtime_observations"
AS_OF_TIMESTAMP = datetime(2026, 8, 2, 23, 59, 59, tzinfo=timezone.utc)


def _rows(response: dict, operation: str) -> list:
    if response.get("status") != "success":
        raise RuntimeError(f"BC09 mock operation failed: operation={operation!r}, response={response!r}")
    rows = response.get("result")
    if not isinstance(rows, list):
        raise TypeError(f"BC09 mock operation returned non-row result: operation={operation!r}, response={response!r}")
    return rows


class BC09MockLLMAgent(MockLLMAgent):
    """Deterministic mock that still discovers and resumes the live DDL job."""

    def __init__(
        self,
        *,
        case,
        business_relations,
        business_contract_table,
        reference_report,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._case = case
        self._business_relations = tuple(business_relations)
        self._business_contract_table = business_contract_table
        self._reference_report = reference_report

    def solve(self):
        case = self._case
        schema_list = ", ".join(
            f"'{schema}'"
            for schema in dict.fromkeys(database for database, _ in self._business_relations)
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SELECT INSTANCE, DIGEST, DIGEST_TEXT, EXEC_COUNT, AVG_LATENCY, SUM_LATENCY FROM information_schema.cluster_statements_summary ORDER BY SUM_LATENCY DESC LIMIT 50"},
            thinking="Inspect the live workload before touching the paused schema change.",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "active_connections"},
            thinking="Confirm that business reads and catalog probes are producing real noise.",
        )
        routes = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT route_id, service_name, route_role, route_state, route_key, binding_id, "
                    "route_version, current_route "
                    f"FROM {case.database}.{case.route_table} WHERE service_name = '{case.service_name}' "
                    "ORDER BY route_version DESC, route_id"
                )
            },
            thinking="Resolve the current logical primary route before looking up a physical binding.",
        )
        route_rows = [
            row
            for row in _rows(routes, "resolve business route")
            if len(row) >= 8
            and str(row[1]) == case.service_name
            and str(row[2]).casefold() == "primary"
            and str(row[3]).casefold() == "active"
            and int(row[7]) == 1
        ]
        if not route_rows:
            raise RuntimeError(f"BC09 mock found no active primary route candidates: rows={route_rows!r}")
        bindings = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT binding_id, route_id, route_key, binding_generation, binding_state, "
                    "relation_schema, relation_table, lease_state, current_binding, effective_from, effective_until "
                    f"FROM {case.database}.{case.route_binding_table} "
                    "ORDER BY route_key, binding_generation DESC, binding_id"
                )
            },
            thinking="Resolve the serving physical relation from the versioned route binding and lease state.",
        )
        all_binding_rows = _rows(bindings, "resolve route binding")
        leases = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT binding_id, fence_epoch, fence_state, current_lease, owner_instance, "
                    "owner_incarnation, observed_at, valid_until "
                    f"FROM {case.database}.{case.route_lease_table} ORDER BY binding_id, fence_epoch DESC"
                )
            },
            thinking="Check the authoritative lease fence because route_bindings lease_state may be stale.",
        )
        all_lease_rows = _rows(leases, "resolve route lease fence")
        owners = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT owner_instance, service_name, owner_state, last_heartbeat, lease_expires_at, "
                    "incarnation, current_owner "
                    f"FROM {case.database}.{case.route_owner_table} ORDER BY owner_instance"
                )
            },
            thinking="Verify that the selected fence owner is live at the observation time, not merely present in lease history.",
        )
        all_owner_rows = _rows(owners, "resolve route owner heartbeat")
        commits = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT commit_id, route_id, route_key, binding_id, route_version, commit_state, "
                    "current_commit, effective_from, effective_until "
                    f"FROM {case.database}.{case.route_commit_table} ORDER BY route_key, route_version, commit_id"
                )
            },
            thinking="Verify that a time-valid owner lease was actually committed by the route cutover control plane.",
        )
        all_commit_rows = _rows(commits, "resolve route cutover commit")
        traffic = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT assignment_id, route_id, binding_id, service_name, traffic_class, assignment_state, "
                    "read_weight, write_weight, current_assignment, effective_from, effective_until "
                    f"FROM {case.database}.{case.route_traffic_table} ORDER BY service_name, traffic_class, assignment_id"
                )
            },
            thinking="Confirm that the committed binding actually carries live business traffic instead of a shadow or zero-weight cohort.",
        )
        all_traffic_rows = _rows(traffic, "resolve route traffic assignment")
        runtime = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT route_id, binding_id, service_name, route_key, MAX(observed_state), MAX(request_origin), "
                    "SUM(read_requests), SUM(write_requests), MAX(last_request_at), MIN(observed_at), "
                    "MAX(observation_until), MAX(current_observation), relation_schema, relation_table "
                    f"FROM {case.database}.{case.route_runtime_table} "
                    "GROUP BY route_id, binding_id, service_name, route_key, relation_schema, relation_table "
                    "ORDER BY route_id, binding_id"
                )
            },
            thinking="Confirm the control-plane assignment against real request observations in the fixed business window.",
        )
        all_runtime_rows = _rows(runtime, "resolve route runtime observation")
        now = AS_OF_TIMESTAMP
        serving_candidates = []
        for route_row in route_rows:
            route_id, route_key, binding_id, route_version = (
                str(route_row[0]),
                str(route_row[4]),
                str(route_row[5]),
                int(route_row[6]),
            )
            serving_rows = [
                row
                for row in all_binding_rows
                if len(row) >= 11
                and str(row[0]) == binding_id
                and str(row[1]) == route_id
                and str(row[2]) == route_key
                and int(row[3]) == route_version
                and str(row[4]).casefold() == "serving"
                and str(row[7]).casefold() == "valid"
                and int(row[8]) == 1
                and datetime.strptime(str(row[9]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[10]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            ]
            if len(serving_rows) == 1:
                serving_candidates.append((route_row, serving_rows[0]))
            elif len(serving_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate serving bindings for route: "
                    f"route={route_row!r}, rows={serving_rows!r}"
                )
        fenced_candidates = []
        for route_row, binding_row in serving_candidates:
            binding_id = str(binding_row[0])
            lease_rows = [
                row
                for row in all_lease_rows
                if len(row) >= 8
                and str(row[0]) == binding_id
                and str(row[2]).casefold() == "held"
                and int(row[3]) == 1
                and str(row[4])
                and int(row[5]) > 0
                and datetime.strptime(str(row[6]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[7]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            ]
            if len(lease_rows) == 1:
                fenced_candidates.append((route_row, binding_row, lease_rows[0]))
            elif len(lease_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate active lease fences: "
                    f"binding_id={binding_id!r}, rows={lease_rows!r}"
                )
        live_candidates = []
        for route_row, binding_row, lease_row in fenced_candidates:
            owner_instance = str(lease_row[4])
            owner_rows = [
                row
                for row in all_owner_rows
                if len(row) >= 7
                and str(row[0]) == owner_instance
                and str(row[1]) == case.service_name
                and str(row[2]).casefold() == "healthy"
                and int(row[6]) == 1
                and int(row[5]) > 0
                and datetime.strptime(str(row[3]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[4]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                and int(lease_row[5]) == int(row[5])
            ]
            if len(owner_rows) == 1:
                live_candidates.append((route_row, binding_row, lease_row, owner_rows[0]))
            elif len(owner_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate live owner heartbeats: "
                    f"owner_instance={owner_instance!r}, rows={owner_rows!r}"
                )
        committed_candidates = []
        for route_row, binding_row, lease_row, owner_row in live_candidates:
            route_id = str(route_row[0])
            route_key = str(route_row[4])
            binding_id = str(route_row[5])
            route_version = int(route_row[6])
            commit_rows = [
                row
                for row in all_commit_rows
                if len(row) >= 9
                and str(row[1]) == route_id
                and str(row[2]) == route_key
                and str(row[3]) == binding_id
                and int(row[4]) == route_version
                and str(row[5]).casefold() == "committed"
                and int(row[6]) == 1
                and datetime.strptime(str(row[7]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[8]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            ]
            if len(commit_rows) == 1:
                committed_candidates.append((route_row, binding_row, lease_row, owner_row, commit_rows[0]))
            elif len(commit_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate committed route cutovers: "
                    f"binding_id={binding_id!r}, rows={commit_rows!r}"
                )
        if not committed_candidates:
            raise RuntimeError(
                f"BC09 mock expected at least one committed live-owner route candidate: "
                f"routes={route_rows!r}, bindings={all_binding_rows!r}, leases={all_lease_rows!r}, "
                f"owners={all_owner_rows!r}, commits={all_commit_rows!r}"
            )
        traffic_candidates = []
        for route_row, binding_row, lease_row, owner_row, commit_row in committed_candidates:
            route_id = str(route_row[0])
            binding_id = str(route_row[5])
            traffic_rows = [
                row
                for row in all_traffic_rows
                if len(row) >= 11
                and str(row[1]) == route_id
                and str(row[2]) == binding_id
                and str(row[3]) == case.service_name
                and str(row[5]).casefold() == "serving"
                and int(row[6]) > 0
                and int(row[7]) > 0
                and int(row[8]) == 1
                and datetime.strptime(str(row[9]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[10]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            ]
            if len(traffic_rows) == 1:
                traffic_candidates.append((route_row, binding_row, lease_row, owner_row, commit_row, traffic_rows[0]))
            elif len(traffic_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate serving traffic assignments: "
                    f"binding_id={binding_id!r}, rows={traffic_rows!r}"
                )
        runtime_candidates = []
        for route_row, binding_row, lease_row, owner_row, commit_row, traffic_row in traffic_candidates:
            route_id = str(route_row[0])
            binding_id = str(route_row[5])
            runtime_rows = [
                row
                for row in all_runtime_rows
                if len(row) >= 14
                and str(row[0]) == route_id
                and str(row[1]) == binding_id
                and str(row[2]) == case.service_name
                and str(row[3]) == str(route_row[4])
                and str(row[4]).casefold() == "active"
                and str(row[5]).casefold() == "production"
                and int(row[6]) > 0
                and int(row[7]) > 0
                and datetime.strptime(str(row[8]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and datetime.strptime(str(row[9]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) <= now
                and now < datetime.strptime(str(row[10]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                and int(row[11]) == 1
                and str(row[12]) == str(binding_row[5])
                and str(row[13]) == str(binding_row[6])
            ]
            if len(runtime_rows) == 1:
                runtime_candidates.append(
                    (route_row, binding_row, lease_row, owner_row, commit_row, traffic_row, runtime_rows[0])
                )
            elif len(runtime_rows) > 1:
                raise RuntimeError(
                    f"BC09 mock found duplicate active runtime observations: "
                    f"binding_id={binding_id!r}, rows={runtime_rows!r}"
                )
        contracts = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT contract_id, service_name, route_key, query_name, contract_state, "
                    "expected_row_count, expected_amount_sum, expected_min_event_id, expected_max_event_id, "
                    "expected_payload_count, expected_payload_digest, current_contract, effective_from, effective_until "
                    f"FROM {case.database}.{self._business_contract_table} "
                    "ORDER BY service_name, route_key, contract_id"
                )
            },
            thinking="Read the unfiltered service-level customer query contracts before interpreting candidate table results.",
        )
        contract_rows = [
            row
            for row in _rows(contracts, "read business query contracts")
            if len(row) >= 14
            and str(row[1]) == case.service_name
            and str(row[2]) == case.route_key
            and str(row[3]) == "customer_reconciliation_v7"
            and str(row[4]).casefold() == "active"
            and int(row[11]) == 1
        ]
        if len(contract_rows) != 1:
            raise RuntimeError(f"BC09 mock expected one active customer query contract: rows={contract_rows!r}")
        expected_result = tuple(int(value) for value in contract_rows[0][5:11])
        business_probe = self.execute(
            "execute_sql",
            {
                "sql_query": " UNION ALL ".join(
                    (
                        f"SELECT '{database}.{table}', primary_batch, COUNT(*), SUM(amount), MIN(event_id), "
                        f"MAX(event_id), COUNT(DISTINCT payload), "
                        f"BIT_XOR(CRC32(CONCAT_WS('#', event_id, payload))) FROM {database}.{table} "
                        "WHERE event_id BETWEEN 8990 AND 9010 AND tenant_id IN (1, 33, 37, 65, 69) "
                        "AND event_type = 'refund' "
                        "GROUP BY primary_batch"
                    )
                    for database, table in self._business_relations
                )
            },
            thinking="Run the real customer reconciliation query across every candidate relation and compare its result digest to the active service contract.",
        )
        business_rows = _rows(business_probe, "reconcile business route results")
        runtime_candidates = [
            candidate
            for candidate in runtime_candidates
            if sum(
                1
                for row in business_rows
                if len(row) >= 8
                and str(row[0]) == f"{candidate[1][5]}.{candidate[1][6]}"
                and tuple(int(value) for value in row[2:8]) == expected_result
            ) == 1
        ]
        if len(runtime_candidates) != 1:
            raise RuntimeError(
                f"BC09 mock expected one live runtime route candidate: "
                f"traffic={traffic_candidates!r}, runtime={all_runtime_rows!r}"
            )
        route_row, binding_row, lease_row, owner_row, commit_row, traffic_row, runtime_row = runtime_candidates[0]
        route_id, route_key, binding_id, route_version = (
            str(route_row[0]),
            str(route_row[4]),
            str(route_row[5]),
            int(route_row[6]),
        )
        binding_rows = [binding_row]
        database, table = str(binding_rows[0][5]), str(binding_rows[0][6])
        requests = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT change_id, route_id, binding_id, request_state, change_kind, index_name, "
                    "column_name, expected_unique, approved_route_version, current_request "
                    f"FROM {case.database}.{case.change_request_table} "
                    "ORDER BY approved_route_version DESC, change_id"
                )
            },
            thinking="Match the currently approved schema-change request to the same route binding and version.",
        )
        request_rows = [
            row
            for row in _rows(requests, "resolve schema change request")
            if len(row) >= 10
            and str(row[1]) == route_id
            and str(row[2]) == binding_id
            and str(row[3]).casefold() == "paused"
            and str(row[4]).casefold() == "add_unique_index"
            and str(row[6]).casefold() == "payload"
            and int(row[7]) == 1
            and int(row[8]) == route_version
            and int(row[9]) == 1
        ]
        if len(request_rows) != 1:
            raise RuntimeError(f"BC09 mock expected one current schema-change request: rows={request_rows!r}")
        index_name = str(request_rows[0][5])
        jobs = self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "ADMIN SHOW DDL JOBS"
                )
            },
            thinking="Match the resolved physical relation to the unfiltered paused DDL history, not the newest job.",
        )
        job_rows = [
            row
            for row in _rows(jobs, "find paused DDL job history")
            if len(row) >= 12
            and str(row[1]) == database
            and str(row[2]) == table
            and str(row[3]).casefold().startswith("add index")
            and str(row[11]).casefold() == "paused"
        ]
        if len(job_rows) != 1:
            raise RuntimeError(f"BC09 mock expected exactly one paused add-index job: rows={job_rows!r}")
        job_id = int(job_rows[0][0])
        job_queries = self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN SHOW DDL JOB QUERIES {job_id}"},
            thinking="Confirm that the selected job query matches the approved unique payload request.",
        )
        query_rows = _rows(job_queries, "verify DDL job query")
        if len(query_rows) != 1 or index_name.casefold() not in str(query_rows[0][0]).casefold():
            raise RuntimeError(f"BC09 mock selected an unexpected DDL query: rows={query_rows!r}, index={index_name!r}")
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME, KEY_NAME, NON_UNIQUE, IS_VISIBLE, SEQ_IN_INDEX, COLUMN_NAME "
                    "FROM information_schema.tidb_indexes "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME, KEY_NAME, SEQ_IN_INDEX"
                )
            },
            thinking="Compare identical catalog shapes while retaining schema and table ownership.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH FROM information_schema.tables "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) "
                    "ORDER BY TABLE_ROWS DESC, TABLE_SCHEMA, TABLE_NAME"
                )
            },
            thinking="Check candidate cardinalities without treating the largest relation as the primary route.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT "
                    "FROM information_schema.columns "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION"
                )
            },
            thinking="Confirm that the route-resolved relation has the same production-shaped schema as its decoys.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
                    "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))), 0) "
                    f"FROM {database}.{table}"
                )
            },
            thinking="Capture the route-resolved business truth before resuming the same job.",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN RESUME DDL JOBS {job_id}"},
            thinking="Resume only the paused job belonging to the active primary route.",
        )
        # The billing case intentionally uses a large real backfill so the paused state is stable.
        # Give TiDB time to finish that same job before issuing bounded status probes.
        time.sleep(60)
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            status = self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT JOB_ID, JOB_TYPE, STATE FROM information_schema.ddl_jobs "
                        f"WHERE JOB_ID = {job_id}"
                    )
                },
                thinking="Poll the same job until TiDB reports the backfill synced.",
            )
            state_rows = _rows(status, "poll DDL job")
            if len(state_rows) == 1 and str(state_rows[0][2]).casefold() == "synced":
                break
            if len(state_rows) == 1 and str(state_rows[0][2]).casefold() in {
                "cancelled", "canceled", "rollback done", "error",
            }:
                raise RuntimeError(f"BC09 mock DDL job entered a failed terminal state: rows={state_rows!r}")
            time.sleep(1)
        else:
            raise TimeoutError(f"BC09 mock timed out waiting for DDL job sync: job_id={job_id}")
        self.execute(
            "query_metrics",
            {"metric_type": "qps"},
            thinking="Check that the cluster is still serving the online read workload after the change.",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "active_connections"},
            thinking="Confirm the workload continued while the index became public.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME, KEY_NAME, NON_UNIQUE, IS_VISIBLE, SEQ_IN_INDEX, COLUMN_NAME "
                    "FROM information_schema.tidb_indexes "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME, KEY_NAME, SEQ_IN_INDEX"
                )
            },
            thinking="Verify the new public index on the route-resolved relation against all same-named decoys.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH FROM information_schema.tables "
                    f"WHERE TABLE_SCHEMA IN ({schema_list}) "
                    "ORDER BY TABLE_ROWS DESC, TABLE_SCHEMA, TABLE_NAME"
                )
            },
            thinking="Cross-check candidate cardinalities after completion without losing route identity.",
        )
        self.execute(
            "execute_sql",
            {"sql_query": f"ADMIN CHECK TABLE {database}.{table}"},
            thinking="Run TiDB's physical and logical consistency check on the routed business table.",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SELECT COUNT(DISTINCT JOB_ID) FROM information_schema.ddl_jobs "
                    f"WHERE DB_NAME = '{database}' AND TABLE_NAME = '{table}' "
                    "AND LOWER(JOB_TYPE) LIKE 'add index%'"
                )
            },
            thinking="Ensure the routed relation produced one job rather than a duplicate backfill.",
        )
        self.execute(
            "read_log",
            {"target": "tidb/tidb-0", "lines": 80},
            thinking="Check the TiDB DDL log for completion evidence without relying on it alone.",
        )
        return {"report": self._reference_report}


def main() -> None:
    scenario = TidbBusinessChangeOnlineDdlPauseResumeScenario()
    parser = argparse.ArgumentParser(
        description="Run TiDB BC09: resume a paused online unique-index backfill."
    )
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--port", type=int, default=27100)
    parser.add_argument("--container-name", default="tidb-bc09")
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
    )
    if args.mode == "mock":
        agent = BC09MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA agent.",
            use_native_tools=False,
            case=case,
            business_contract_table=case.business_contract_table,
            reference_report=case.reference_report,
            business_relations=(
                (case.database, case.table),
                *((decoy.database, decoy.table) for decoy in case.decoy_tables),
            ),
        )
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(
            model=args.model,
            config_path=args.config_path,
            use_native_tools=True,
        )
    result = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns).run()
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
