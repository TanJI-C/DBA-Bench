"""Agent tool surface for one persistent TiDB topology.

This is the sessions support layer: core ``PersistentScenarioAgentControl``
calls ``get_tool_schemas()`` / ``execute_action(api, args)`` on the
environment, and the optional agent-SQL bounding hook
``set_agent_sql_timeouts`` / ``reset_agent_sql_timeouts``. Trusted surfaces
(capabilities, verifiers, workload drivers) use the explicit
``execute_sql_trusted`` / ``*_connection_factory`` methods and are never
exposed to the agent.

TiDB semantics honored here:

- the agent SQL surface opens a fresh connection per ``execute_sql`` call, so
  session state (TEMPORARY tables, session variables) does NOT persist across
  calls; GLOBAL variable changes take effect for new sessions only and are the
  agent-visible way to change cluster defaults;
- agent statements are bounded with ``MAX_EXECUTION_TIME`` (SELECTs) and
  ``innodb_lock_wait_timeout`` (lock waits); there is no ``pending_restart``
  concept on TiDB;
- slow-query details are NOT pre-aggregated: the agent queries
  ``information_schema.cluster_statements_summary`` and
  ``cluster_processlist`` through ``execute_sql``;
- ``manage_instance`` restarts/stops/starts one compose service and returns
  after compose finishes, not after cluster re-readiness.
"""

from __future__ import annotations

from collections.abc import Callable
import http.client
import json
import re
import threading
import time
from typing import Any, Mapping

import pymysql
import pymysql.err

from src.execution.tidb_metrics import LivePrometheusMetricProvider, TIDB_METRIC_CATALOG
from src.execution.tidb_persistent_deployment import TiDBPersistentDeploymentError
from src.execution.history.metrics import MetricQuery, format_utc_timestamp

from .changefeed import CdcChangefeedAdmin
from .classifier import TiDBActionClassifier

_LOG_TYPE_ROLES = ("pd", "tikv", "tidb", "tiflash", "ticdc", "downstream", "prometheus", "cadvisor")
_LOG_MAX_LINES = 400
_LOG_MAX_CONTENT_CHARS = 24000
_SQL_ROW_LIMIT = 5000
_SQL_MAX_CELL_CHARS = 2000

_TIMEOUT_SPEC_RE = re.compile(r"^(\d+)(ms|s)?$")


def _parse_timeout_seconds(spec: str, parameter: str) -> float:
    match = _TIMEOUT_SPEC_RE.match(spec.strip())
    if not match:
        raise ValueError(f"Agent SQL timeout must look like '<n>s' or '<n>ms': {parameter}={spec!r}")
    value = int(match.group(1))
    return value / 1000.0 if match.group(2) == "ms" else float(value)


# The live provider raises these RuntimeErrors for metrics the catalog advertises
# but that need a Case-side provider (WorkloadRunner / SQL+PD sampler) which the
# persistent assembly never attaches. Matched by message so newly added
# sampler-backed metrics keep the same agent-visible contract.
_METRIC_PROVIDER_MISSING_MARKERS = (
    "requires the Case WorkloadRunner",  # workload_profile
    "requires a Case sampler",           # statistics_state, plan_cardinality, pd_region_* / pd_leader_*
)

# Fault episodes make "Prometheus is reachable but the target's series is gone"
# routine (a throttled/removed store stops exporting), so the provider's
# data-missing RuntimeErrors are agent-visible environment facts too.
_METRIC_DATA_MISSING_MARKERS = (
    "Prometheus query must return one series",  # single-target selector found no series
    "query is missing database services",       # cpu/memory/disk_io aggregate lost a store's series
)


def _is_metric_provider_missing(exc: RuntimeError) -> bool:
    return any(marker in str(exc) for marker in _METRIC_PROVIDER_MISSING_MARKERS)


def _is_metric_data_missing(exc: RuntimeError) -> bool:
    return any(marker in str(exc) for marker in _METRIC_DATA_MISSING_MARKERS)


class PersistentTiDBEnvironment:
    system = "tidb"

    def __init__(
        self,
        *,
        deployment,
        user: str = "root",
        password: str = "",
        database: str = "test",
    ):
        self.deployment = deployment
        self.user = user
        self.password = password
        self.database = database
        self.agent_statement_timeout = "60s"
        self.agent_lock_wait_timeout = "10s"
        self.action_classifier = TiDBActionClassifier()
        self._metrics = LivePrometheusMetricProvider(deployment=deployment, run_id=deployment.run_id)

    # -- connections -------------------------------------------------------------

    def connect(self, *, database: str | None = None, autocommit: bool = False) -> pymysql.connections.Connection:
        """One fresh pymysql connection (agent surface and trusted helpers alike)."""
        return pymysql.connect(
            host="127.0.0.1",
            port=self.deployment.ports.tidb_sql[self.deployment.topology.role_services("tidb")[0]],
            user=self.user,
            password=self.password,
            database=database or self.database,
            autocommit=autocommit,
            charset="utf8mb4",
            connect_timeout=10,
            read_timeout=120,
            write_timeout=120,
        )

    def connect_downstream(self, service: str | None = None, *, database: str | None = None, autocommit: bool = False):
        """Fresh connection to the CDC downstream MySQL node."""
        host, port = self.deployment.downstream_sql_endpoint(service)
        return pymysql.connect(
            host=host, port=port, user="root", password="",
            database=database, autocommit=autocommit,
            charset="utf8mb4", connect_timeout=10, read_timeout=120, write_timeout=120,
        )

    def workload_connection_factory(self, *, database: str | None = None) -> Callable[[], object]:
        """Connection factory for TiDBOltpTransactionPool / TiDBJobQueueRunner."""
        return lambda: self.connect(database=database)

    # -- trusted CDC surface -------------------------------------------------------

    def changefeed_cli_runner(self, capture_target: str | None = None) -> Callable[[list[str]], str]:
        """Runner for ``CdcChangefeedCheckpointSampler`` / ``CdcChangefeedAdmin``.

        This is the only path capabilities need for TiCDC cli access; they never
        import or call the deployment directly.
        """
        service = self._cdc_service(capture_target)
        return lambda args: self.deployment.exec_command(service, args)

    def changefeed_admin(self, capture_target: str | None = None) -> CdcChangefeedAdmin:
        """Changefeed lifecycle operations (create/pause/resume/remove/query)."""
        return CdcChangefeedAdmin(
            cli_runner=self.changefeed_cli_runner(capture_target),
            pd_address=f"http://{self.deployment.topology.role_services('pd')[0]}:2379",
        )

    def gc_safepoint_list(self) -> dict:
        """PD service GC safe points (``/pd/api/v1/gc/safepoint``).

        Returns the raw PD payload: ``service_gc_safe_points`` (each with
        service_id / safe_point / expired_at — TiCDC pins its own entry while a
        changefeed exists), ``min_service_gc_safe_point`` and ``gc_safe_point``.
        """
        return self.deployment.pd_request("GET", "/pd/api/v1/gc/safepoint")

    def _cdc_service(self, capture_target: str | None) -> str:
        services = self.deployment.topology.role_services("ticdc")
        if not services:
            raise ValueError(
                f"Topology has no ticdc service: run_id={self.deployment.run_id!r}"
            )
        if capture_target is None:
            return services[0]
        if capture_target not in services:
            raise ValueError(
                f"capture_target is not a ticdc service: capture_target={capture_target!r}, known={services!r}"
            )
        return capture_target

    def connect_service(self, service: str, *, database: str | None = None, autocommit: bool = False):
        """Fresh connection pinned to one specific TiDB SQL service."""
        if service not in self.deployment.ports.tidb_sql:
            raise ValueError(
                f"Not a TiDB SQL service: service={service!r}, known={sorted(self.deployment.ports.tidb_sql)!r}"
            )
        return pymysql.connect(
            host="127.0.0.1",
            port=self.deployment.ports.tidb_sql[service],
            user=self.user, password=self.password,
            database=database or self.database,
            autocommit=autocommit, charset="utf8mb4",
            connect_timeout=10, read_timeout=120, write_timeout=120,
        )

    # -- trusted SQL surface -------------------------------------------------------

    def execute_sql_trusted(self, sql: str, *, service: str | None = None) -> tuple[tuple[str, ...], list[tuple]]:
        """Trusted execution (capabilities, verifiers, state facts). Raises on error.

        Commits before closing: the trusted surface is a full client session,
        so DML takes effect; DDL in TiDB commits implicitly either way.
        """
        connection = self.connect_service(service) if service is not None else self.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description is None:
                    columns, rows = (), []
                else:
                    columns = tuple(item[0] for item in cursor.description)
                    rows = list(cursor.fetchall())
            connection.commit()
            return columns, rows
        finally:
            connection.close()

    # -- agent SQL bounding hook (sessions.py contract) ------------------------------

    def set_agent_sql_timeouts(self, statement_timeout: str, lock_timeout: str) -> None:
        # Validated here so misformatted specs fail at the setter, not mid-query.
        _parse_timeout_seconds(statement_timeout, "statement_timeout")
        _parse_timeout_seconds(lock_timeout, "lock_timeout")
        self.agent_statement_timeout = statement_timeout
        self.agent_lock_wait_timeout = lock_timeout

    def reset_agent_sql_timeouts(self) -> None:
        self.agent_statement_timeout = "60s"
        self.agent_lock_wait_timeout = "10s"

    def _execute_agent_sql(self, sql_query: str) -> dict[str, Any]:
        statement_ms = int(_parse_timeout_seconds(self.agent_statement_timeout, "statement_timeout") * 1000)
        lock_seconds = int(_parse_timeout_seconds(self.agent_lock_wait_timeout, "lock_timeout"))
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET SESSION MAX_EXECUTION_TIME = {statement_ms}")
                cursor.execute(f"SET SESSION innodb_lock_wait_timeout = {lock_seconds}")
                cursor.execute(sql_query)
                if cursor.description is None:
                    connection.commit()
                    return {
                        "status": "success",
                        "statement": "affected",
                        "row_count": cursor.rowcount,
                        "message": "statement executed; no result set (session state does not persist across calls)",
                    }
                columns = [item[0] for item in cursor.description]
                rows = cursor.fetchall()
                if len(rows) > _SQL_ROW_LIMIT:
                    raise RuntimeError(
                        f"execute_sql result exceeds the row limit: rows={len(rows)}, limit={_SQL_ROW_LIMIT}"
                    )
                serialized = [
                    [self._cell(value) for value in row]
                    for row in rows
                ]
                return {"status": "success", "columns": columns, "rows": serialized, "row_count": len(serialized)}
        finally:
            connection.close()

    @staticmethod
    def _cell(value: object) -> object:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")[:_SQL_MAX_CELL_CHARS]
        if isinstance(value, str):
            return value[:_SQL_MAX_CELL_CHARS]
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        return str(value)

    # -- metrics ----------------------------------------------------------------

    def _query_metrics(self, metric_type: str, target: str | None, start_timestamp: str | None, end_timestamp: str | None) -> dict[str, Any]:
        definition = TIDB_METRIC_CATALOG.definition(metric_type)
        query = MetricQuery(metric=definition.name, target=target)
        if (start_timestamp is None) != (end_timestamp is None):
            raise ValueError(
                "query_metrics.start_timestamp and query_metrics.end_timestamp must be provided together: "
                f"start={start_timestamp!r}, end={end_timestamp!r}"
            )
        frame = self._metrics.query(query)
        series = []
        for series_target, fields in frame.series.items():
            timestamps = frame.timestamps_ms[series_target]
            series.append({
                "target": series_target,
                "fields": {field: list(values) for field, values in fields.items()},
                "timestamps": [format_utc_timestamp(int(ms)) for ms in timestamps],
            })
        return {
            "status": "success",
            "metric": frame.metric,
            "target": frame.query_target,
            "step_seconds": frame.step_seconds,
            "series": series,
        }

    # -- logs / instance management ------------------------------------------------

    def _read_log(self, log_type: str, target: str | None, lines: int) -> dict[str, Any]:
        if log_type not in _LOG_TYPE_ROLES:
            raise ValueError(
                f"Unknown read_log log_type: log_type={log_type!r}, expected={_LOG_TYPE_ROLES!r}"
            )
        services = self.deployment.topology.role_services(log_type)
        if log_type == "prometheus" or log_type == "cadvisor":
            services = (log_type,)
        if not services:
            raise ValueError(
                f"Topology has no service for log_type: run_id={self.deployment.run_id!r}, log_type={log_type!r}"
            )
        service = target if target is not None else services[0]
        if service not in services and service not in ("prometheus", "cadvisor"):
            raise ValueError(
                f"read_log target is not a known service of the role: log_type={log_type!r}, "
                f"target={service!r}, known={services!r}"
            )
        if lines <= 0 or lines > _LOG_MAX_LINES:
            raise ValueError(f"read_log lines must be in (0, {_LOG_MAX_LINES}]: lines={lines}")
        content = self.deployment.service_logs(service, tail=lines)
        if len(content) > _LOG_MAX_CONTENT_CHARS:
            content = content[-_LOG_MAX_CONTENT_CHARS:]
        return {"status": "success", "log_type": log_type, "service": service, "content": content}

    def _manage_instance(self, action: str, target: str | None, value: object) -> dict[str, Any]:
        if value is not None:
            raise ValueError(f"manage_instance does not accept a value: action={action!r}, value={value!r}")
        if action == "retire":
            return self._retire_tikv_store(target)
        if action not in ("restart", "stop", "start"):
            raise ValueError(
                f"Unsupported manage_instance action: action={action!r}, "
                f"allowed=['restart', 'start', 'stop', 'retire']"
            )
        if target is None or not str(target).strip():
            raise ValueError(f"manage_instance requires a service target: action={action!r}, target={target!r}")
        service = str(target)
        self.deployment.topology.service(service)  # raises on unknown service
        if value is not None:
            raise ValueError(f"manage_instance does not accept a value: action={action!r}, value={value!r}")
        self.deployment.manage_service(action, service)
        return {
            "status": "success",
            "service": service,
            "action": action,
            "state": self.deployment.service_state(service),
            "message": "compose action returned; cluster readiness must be observed via SQL/metrics",
        }

    def _retire_tikv_store(self, target: str | None) -> dict[str, Any]:
        """Decommission one TiKV store through PD: store delete puts the store
        Offline, PD migrates the remaining regions off it, and a fully drained
        store ends Tombstone (or drops out of the PD store list entirely).

        The measured last-mile stall of this topology (a region PD schedules no
        operator for keeps the drain pinned) is handled inside the operation:
        the drain watch applies transfer-leader once, then remove-peer, before
        giving up — the same authorized sequence the deterministic reference
        path applies. The call returns immediately; the drain continues in the
        background and the final sampling observes the terminal store state.
        """
        if target is None or not str(target).strip():
            raise ValueError(f"manage_instance('retire') requires a tikv service target: target={target!r}")
        service = str(target)
        self.deployment.topology.service(service)  # raises on unknown service
        store_id = None
        for store in self.deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ()):
            record = store.get("store", {})
            if record.get("address") == f"{service}:20160":
                store_id = int(record["id"])
                break
        if store_id is None:
            raise ValueError(f"PD has no store registered for the service: target={service!r}")
        self.deployment.pd_request("DELETE", f"/pd/api/v1/store/{store_id}")
        state = self._pd_store_state(store_id)
        if state != "Offline":
            raise RuntimeError(
                f"PD store delete did not leave the store Offline: target={service!r}, "
                f"store_id={store_id!r}, state={state!r}"
            )
        threading.Thread(
            target=self._watch_tikv_store_drain,
            name=f"tikv-store-drain-{service}",
            daemon=True,
            kwargs={"service": service, "store_id": store_id},
        ).start()
        return {
            "status": "success",
            "service": service,
            "action": "retire",
            "store_id": store_id,
            "state": state,
            "message": (
                "store deleted in PD (Offline); its regions are migrating off and the "
                "store ends Tombstone once empty — observe via information_schema.tikv_store_status"
            ),
        }

    def _pd_store_state(self, store_id: int) -> str | None:
        for store in self.deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ()):
            record = store.get("store", {})
            if int(record.get("id", -1)) == store_id:
                return str(record.get("state_name"))
        return None

    def _pd_store_region_count(self, store_id: int) -> int:
        for store in self.deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ()):
            record = store.get("store", {})
            if int(record.get("id", -1)) == store_id:
                return int(record.get("region_count", 0))
        return 0

    _DRAIN_POLL_SECONDS = 10.0
    _DRAIN_STALLED_POLLS_BEFORE_TRANSFER = 6
    _DRAIN_MAX_SECONDS = 2700.0

    def _watch_tikv_store_drain(self, service: str, store_id: int) -> None:
        """Background drain watch for a retired store. After a sustained
        region-count stall it applies transfer-leader for the stuck region
        once, then remove-peer — keeping quorum and never touching the store
        itself. Exits when the store turns Tombstone or leaves the PD list."""
        stalled_polls = 0
        last_region_count: int | None = None
        transfer_applied = False
        deadline = time.monotonic() + self._DRAIN_MAX_SECONDS
        while time.monotonic() < deadline:
            time.sleep(self._DRAIN_POLL_SECONDS)
            # PD API hiccups are a domain fact of a draining cluster (leader
            # elections, container churn): a failed poll is not a stalled drain.
            try:
                state = self._pd_store_state(store_id)
                if state in (None, "Tombstone"):
                    return
                region_count = self._pd_store_region_count(store_id)
                stalled_polls = stalled_polls + 1 if region_count == last_region_count else 0
                last_region_count = region_count
                if stalled_polls < self._DRAIN_STALLED_POLLS_BEFORE_TRANSFER or region_count == 0:
                    continue
                regions = self.deployment.pd_request("GET", f"/pd/api/v1/regions/store/{store_id}").get("regions", ())
                if not regions:
                    continue
                stuck_region = int(regions[0]["id"])
                if not transfer_applied:
                    target_store = min(
                        (
                            int(store.get("store", {}).get("id", -1))
                            for store in self.deployment.pd_request("GET", "/pd/api/v1/stores").get("stores", ())
                            if store.get("store", {}).get("state_name") == "Up"
                            and int(store.get("store", {}).get("id", -1)) != store_id
                        ),
                        default=-1,
                    )
                    if target_store == -1:
                        continue
                    self._pd_ctl("operator", "add", "transfer-leader", str(stuck_region), f"store {target_store}")
                    transfer_applied = True
                else:
                    self._pd_ctl("operator", "add", "remove-peer", str(stuck_region), str(store_id))
                stalled_polls = 0
            except Exception:
                continue

    def _pd_ctl(self, *args: str) -> str:
        """Run a bounded raw pd-ctl command in the first PD container."""
        output = self.deployment.exec_command(
            self.deployment.topology.role_services("pd")[0],
            ["/pd-ctl", "-u", "http://127.0.0.1:2379", *args],
        ).strip()
        if not output:
            raise RuntimeError(f"PD control command returned an empty response: args={args!r}")
        if "Usage:" in output or output.casefold().startswith("failed"):
            raise RuntimeError(f"PD control command was rejected: args={args!r}, output={output!r}")
        return output

    # -- core tool surface ------------------------------------------------------

    _TOOL_SCHEMAS: tuple[dict[str, Any], ...] = (
        {
            "type": "function",
            "function": {
                "name": "execute_sql",
                "description": (
                    "Execute SQL on the TiDB cluster. Every call uses a fresh session: "
                    "session variables and TEMPORARY tables do not persist. Query "
                    "information_schema.cluster_statements_summary, cluster_processlist, "
                    "cluster_info, tiflash_replica and user tables for details."
                ),
                "parameters": {
                    "type": "object",
                    "required": ["sql_query"],
                    "properties": {
                        "sql_query": {"type": "string", "description": "SQL text to execute"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_metrics",
                "description": (
                    "Query pre-aggregated time-series metrics (cpu, memory, disk_io, disk_usage, "
                    "network_io, qps, query_latency, connections, ...) from the monitoring stack. "
                    "SQL-backed details are not served here; use execute_sql."
                ),
                "parameters": {
                    "type": "object",
                    "required": ["metric_type"],
                    "properties": {
                        "metric_type": {"type": "string", "description": "Metric name"},
                        "target": {"type": "string", "description": "Optional deployment node target"},
                        "start_timestamp": {"type": "string", "description": "Optional YYYY-MM-DD HH:mm:ss UTC start"},
                        "end_timestamp": {"type": "string", "description": "Optional YYYY-MM-DD HH:mm:ss UTC end"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "manage_instance",
                "description": (
                    "Lifecycle control for one cluster service (target = service name such as "
                    "'tidb-0', 'tikv-1', 'pd-0'). Actions: restart, start, stop for any service; "
                    "retire decommissions one TiKV store through PD (store delete; PD migrates "
                    "the remaining regions off it and the store ends Tombstone). Returns after "
                    "compose finishes; observe re-readiness via SQL or metrics."
                ),
                "parameters": {
                    "type": "object",
                    "required": ["action", "target"],
                    "properties": {
                        "action": {"type": "string", "description": "restart | start | stop | retire"},
                        "target": {"type": "string", "description": "Service name"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "manage_changefeed",
                "description": (
                    "TiCDC changefeed lifecycle on the upstream cluster. Actions: "
                    "create (requires sink_uri, optional start_ts TSO), pause, resume, "
                    "remove, query. Returns the feed observation: state, checkpoint_tso, "
                    "error. capture_target selects the ticdc capture (e.g. 'ticdc-0')."
                ),
                "parameters": {
                    "type": "object",
                    "required": ["action", "changefeed_id"],
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "create | pause | resume | remove | query",
                        },
                        "changefeed_id": {"type": "string", "description": "Changefeed ID"},
                        "sink_uri": {
                            "type": "string",
                            "description": "create only: e.g. mysql://user:password@host:3306/",
                        },
                        "start_ts": {
                            "type": "integer",
                            "description": "create only: TSO to start replicating from (default current TSO)",
                        },
                        "capture_target": {
                            "type": "string",
                            "description": "ticdc service name (default first capture)",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_log",
                "description": (
                    "Read recent log lines of one service. log_type: tidb|tikv|pd|tiflash|ticdc|"
                    "downstream|prometheus|cadvisor. target selects the service index (e.g. 'tikv-1')."
                ),
                "parameters": {
                    "type": "object",
                    "required": ["log_type"],
                    "properties": {
                        "log_type": {"type": "string", "description": "Log role"},
                        "target": {"type": "string", "description": "Optional service name"},
                        "lines": {"type": "integer", "description": "Tail length (default 200, max 400)"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "help",
                "description": "Return help for one tool or the tool list.",
                "parameters": {
                    "type": "object",
                    "properties": {"tool_name": {"type": "string", "description": "Optional tool name"}},
                },
            },
        },
    )

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        return [json.loads(json.dumps(schema)) for schema in self._TOOL_SCHEMAS]

    def execute_action(self, api: str, args: Mapping[str, Any]) -> str:
        handler = {
            "execute_sql": self._tool_execute_sql,
            "query_metrics": self._tool_query_metrics,
            "manage_instance": self._tool_manage_instance,
            "manage_changefeed": self._tool_manage_changefeed,
            "read_log": self._tool_read_log,
            "help": self._tool_help,
        }.get(api)
        if handler is None:
            return json.dumps(
                {"status": "error", "error": f"Unknown API: {api}"},
                ensure_ascii=False,
            )
        try:
            payload = handler(args)
        except (ValueError, TypeError) as exc:
            return json.dumps(
                {"status": "error", "error": f"Invalid arguments for {api}: {exc}"},
                ensure_ascii=False,
            )
        except pymysql.err.MySQLError as exc:
            return json.dumps(
                {"status": "error", "error": f"MySQL error {exc.args[0] if exc.args else 'unknown'}: {exc}"},
                ensure_ascii=False,
            )
        return json.dumps(payload, ensure_ascii=False, default=str)

    def _tool_execute_sql(self, args: Mapping[str, Any]) -> dict[str, Any]:
        sql_query = args.get("sql_query")
        if not isinstance(sql_query, str) or not sql_query.strip():
            raise ValueError(f"execute_sql requires non-empty sql_query: args={dict(args)!r}")
        return self._execute_agent_sql(sql_query)

    def _tool_query_metrics(self, args: Mapping[str, Any]) -> dict[str, Any]:
        metric_type = args.get("metric_type")
        if not isinstance(metric_type, str) or not metric_type.strip():
            raise ValueError(f"query_metrics requires non-empty metric_type: args={dict(args)!r}")
        target = args.get("target")
        if target is not None and not isinstance(target, str):
            raise ValueError(f"query_metrics target must be a string: target={target!r}")
        try:
            return self._query_metrics(
                metric_type,
                target,
                args.get("start_timestamp"),
                args.get("end_timestamp"),
            )
        except RuntimeError as exc:
            if _is_metric_provider_missing(exc):
                # Same agent-visible error contract as cdc cli failures: the metric
                # is advertised by the catalog but this environment attaches no
                # Case provider for it, so the agent must adapt instead of dying.
                return {
                    "status": "error",
                    "metric": metric_type,
                    "error": f"metric has no provider in this environment: {exc}",
                }
            if _is_metric_data_missing(exc):
                # The exc text names the target query (single-target series=0) or
                # the exact missing services (aggregate), so the agent can re-target.
                return {
                    "status": "error",
                    "metric": metric_type,
                    "error": f"prometheus has no series for this metric: {exc}",
                }
            raise  # internal provider defect: fail loudly instead of a misleading agent payload
        except (OSError, http.client.HTTPException) as exc:
            # urlopen raises URLError (an OSError subclass) for refused/timed-out
            # connections and raw http.client.HTTPException (e.g. InvalidURL for a
            # missing Prometheus port) when the monitoring stack is unreachable;
            # that is an environment fact the agent can adapt to, not a session failure.
            return {
                "status": "error",
                "metric": metric_type,
                "error": f"prometheus unreachable: {exc}",
            }

    def _tool_manage_instance(self, args: Mapping[str, Any]) -> dict[str, Any]:
        action = args.get("action")
        if not isinstance(action, str) or not action.strip():
            raise ValueError(f"manage_instance requires a non-empty action: args={dict(args)!r}")
        return self._manage_instance(action, args.get("target"), args.get("value"))

    _MANAGE_CHANGEFEED_ACTIONS = ("create", "pause", "resume", "remove", "query")

    def _tool_manage_changefeed(self, args: Mapping[str, Any]) -> dict[str, Any]:
        action = args.get("action")
        if action not in self._MANAGE_CHANGEFEED_ACTIONS:
            raise ValueError(
                f"manage_changefeed requires action in {list(self._MANAGE_CHANGEFEED_ACTIONS)}: "
                f"action={action!r}"
            )
        changefeed_id = args.get("changefeed_id")
        if not isinstance(changefeed_id, str) or not changefeed_id.strip():
            raise ValueError(f"manage_changefeed requires a non-empty changefeed_id: args={dict(args)!r}")
        capture_target = args.get("capture_target")
        if capture_target is not None and not isinstance(capture_target, str):
            raise ValueError(f"manage_changefeed capture_target must be a string: capture_target={capture_target!r}")
        admin = self.changefeed_admin(capture_target)
        try:
            if action == "create":
                sink_uri = args.get("sink_uri")
                if not isinstance(sink_uri, str) or not sink_uri.strip():
                    raise ValueError(f"manage_changefeed create requires a non-empty sink_uri: args={dict(args)!r}")
                start_ts = args.get("start_ts")
                if start_ts is not None and (isinstance(start_ts, bool) or not isinstance(start_ts, int)):
                    raise ValueError(f"manage_changefeed start_ts must be an integer TSO: start_ts={start_ts!r}")
                return admin.create(changefeed_id, sink_uri, start_ts)
            if action == "pause":
                return admin.pause(changefeed_id)
            if action == "resume":
                return admin.resume(changefeed_id)
            if action == "remove":
                return admin.remove(changefeed_id)
            return admin.query(changefeed_id)
        except TiDBPersistentDeploymentError as exc:
            # Operational cli failure (unknown feed, unreachable sink, ...): the
            # same agent-visible error contract as MySQL errors for execute_sql.
            return {"status": "error", "action": action, "changefeed_id": changefeed_id,
                    "error": f"cdc cli failed: {exc}"}

    def _tool_read_log(self, args: Mapping[str, Any]) -> dict[str, Any]:
        log_type = args.get("log_type")
        if not isinstance(log_type, str) or not log_type.strip():
            raise ValueError(f"read_log requires a non-empty log_type: args={dict(args)!r}")
        lines = args.get("lines", 200)
        if isinstance(lines, bool) or not isinstance(lines, int):
            raise ValueError(f"read_log lines must be an integer: lines={lines!r}")
        target = args.get("target")
        if target is not None and not isinstance(target, str):
            raise ValueError(f"read_log target must be a string: target={target!r}")
        return self._read_log(log_type, target, lines)

    def _tool_help(self, args: Mapping[str, Any]) -> dict[str, Any]:
        tool_name = args.get("tool_name")
        if tool_name is None:
            return {
                "status": "success",
                "tools": [
                    {"name": schema["function"]["name"], "description": schema["function"]["description"]}
                    for schema in self._TOOL_SCHEMAS
                ],
            }
        for schema in self._TOOL_SCHEMAS:
            if schema["function"]["name"] == tool_name:
                return {"status": "success", "tool": tool_name, "definition": schema["function"]}
        return {"status": "error", "tool": tool_name, "error": f"Unknown tool: {tool_name}"}

    # -- lifecycle ----------------------------------------------------------------

    def deploy(self) -> None:
        self.deployment.deploy()

    def teardown(self) -> None:
        self.deployment.teardown()
