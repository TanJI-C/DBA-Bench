from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth, measure_latency_profile
from src.database.tidb import tidb_plan_metrics
from src.database.sql import execute_result_rows, require_success_payload

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.tidb.common import validate_sql_identifier


class TidbQueryPerfNoncoveringIndexTailLatencyInjector(BaseFaultInjector):
    """Create a real degraded access path for the checkout order-history API."""

    def __init__(self) -> None:
        self._routers_initialized = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._capture_auto_analyze_state(context.env)
        self._disable_auto_analyze(context.env)
        with context.env.metrics_hidden():
            self._create_schema(context.env)
            self._load_rows(context.env)
            self._verify_fault_state(context.env)
        self._initialize_workload_connection_routers(context)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._disable_auto_analyze(context.env)
        self._verify_fault_state(context.env)
        self._initialize_workload_connection_routers(context)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config)
        env = context.env
        self._assert_auto_analyze_disabled(env)
        self._verify_fault_state(env)

        fault_plan = self._explain_analyze(env)
        fault_plan_metrics = tidb_plan_metrics(fault_plan, self.table)
        fault_p95_ms, fault_samples_ms = self._measure_p95_ms(env)
        if fault_p95_ms <= self.p95_slo_ms:
            raise RuntimeError(
                "QP05 fault did not breach the declared target SLO: "
                f"table={self.db}.{self.table}, fault_p95_ms={fault_p95_ms}, "
                f"p95_slo_ms={self.p95_slo_ms}, scan_volume={fault_plan_metrics['scan_volume']}"
            )

        target_payload = require_success_payload(
            env.execute_sql(self.query),
            "capture QP05 target result truth",
        )
        table_truth = execute_result_rows(
            env.execute_sql,
            self.table_crc_sql,
            "capture QP05 table truth",
        )
        page_context_truth = execute_result_rows(
            env.execute_sql,
            self.page_context_truth_sql,
            "capture QP05 page context truth",
        )
        route_registry_truth = execute_result_rows(
            env.execute_sql,
            self.route_registry_truth_sql,
            "capture QP05 route registry truth",
        )
        index_catalog = execute_result_rows(
            env.execute_sql,
            self.index_catalog_sql,
            "capture QP05 index catalog",
        )
        service_health = require_success_payload(
            env.manage_cluster("service", "list"),
            "capture QP05 service health",
        )
        topsql = require_success_payload(
            env.observe_metric("topsql"),
            "capture QP05 TopSQL",
        )
        query_latency = require_success_payload(
            env.query_metrics("query_latency"),
            "capture QP05 query latency",
        )
        tikv_log = require_success_payload(
            env.read_log("tikv/tikv-0", lines=200),
            "capture QP05 TiKV log evidence",
        )
        tidb_log = require_success_payload(
            env.read_log("tidb/tidb-0", lines=200),
            "capture QP05 TiDB log evidence",
        )
        stats = require_success_payload(
            env.execute_sql(self.stats_sql),
            "capture QP05 statistics metadata",
        )
        table_size = require_success_payload(
            env.execute_sql(self.table_size_sql),
            "capture QP05 table size metadata",
        )
        ddl_jobs = require_success_payload(
            env.execute_sql(self.ddl_jobs_sql),
            "capture QP05 DDL jobs",
        )

        return {
            "qp05_fault_plan": fault_plan,
            "qp05_fault_plan_metrics": fault_plan_metrics,
            "qp05_fault_p95_ms": fault_p95_ms,
            "qp05_fault_latency_samples_ms": fault_samples_ms,
            "qp05_baseline_target_result_truth": capture_query_result_truth(
                target_payload,
                ordered=True,
            ),
            "qp05_baseline_table_truth": table_truth,
            "qp05_baseline_page_context_truth": page_context_truth,
            "qp05_baseline_route_registry_truth": route_registry_truth,
            "qp05_baseline_index_catalog": index_catalog,
            "qp05_service_health": service_health,
            "qp05_topsql": topsql,
            "qp05_query_latency": query_latency,
            "qp05_tikv_log": tikv_log,
            "qp05_tidb_log": tidb_log,
            "qp05_stats_meta": stats,
            "qp05_baseline_table_size": table_size,
            "qp05_baseline_ddl_jobs": ddl_jobs,
            "qp05_auto_analyze_state": {
                "ratio": self.original_auto_analyze_ratio,
                "start_time": self.original_auto_analyze_start_time,
                "end_time": self.original_auto_analyze_end_time,
            },
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._assert_auto_analyze_disabled(context.env)
        self._verify_fault_state(context.env)
        if self._routers_initialized:
            context.env.reset_connection_routers()
            self._routers_initialized = False

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        env = context.env
        if self._routers_initialized:
            env.reset_connection_routers()
            self._routers_initialized = False
        for table in (
            self.audit_table,
            self.route_registry_table,
            self.page_context_table,
            self.table,
            self.numbers_table,
            self.digits_table,
        ):
            require_success_payload(
                env.execute_bootstrap_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"drop QP05 table {self.db}.{table}",
            )
        self._restore_auto_analyze_state(env)

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "database")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.audit_table = validate_sql_identifier(str(config["audit_table"]), "audit table")
        self.page_context_table = validate_sql_identifier(
            str(config["page_context_table"]), "page context table"
        )
        self.route_registry_table = validate_sql_identifier(
            str(config["route_registry_table"]), "route registry table"
        )
        self.numbers_table = validate_sql_identifier(f"{self.table}_numbers", "numbers table")
        self.digits_table = validate_sql_identifier(f"{self.table}_digits", "digits table")
        self.row_count = int(config["row_count"])
        self.query = str(config["query"])
        self.workload_query = str(config["workload_query"])
        self.table_crc_sql = str(config["table_crc_sql"])
        self.page_context_truth_sql = str(config["page_context_truth_sql"])
        self.route_registry_sql = str(config["route_registry_sql"])
        self.route_registry_truth_sql = str(config["route_registry_truth_sql"])
        self.index_catalog_sql = str(config["index_catalog_sql"])
        self.stats_sql = str(config["stats_sql"])
        self.table_size_sql = str(config["table_size_sql"])
        self.ddl_jobs_sql = str(config["ddl_jobs_sql"])
        self.fault_index_names = tuple(str(item) for item in config["fault_index_names"])
        self.replaceable_fault_index_names = tuple(
            str(item) for item in config["replaceable_fault_index_names"]
        )
        self.route_registry_rows = tuple(tuple(row) for row in config["route_registry_rows"])
        self.route_registry_row_count = int(config["route_registry_row_count"])
        self.target_workload_fingerprint = str(config["target_workload_fingerprint"])
        self.fault_scan_floor = int(config["fault_scan_floor"])
        self.p95_slo_ms = float(config["p95_slo_ms"])
        self.latency_sample_count = int(config["latency_sample_count"])

    def _execute(self, env, sql: str, context: str) -> dict:
        return require_success_payload(
            env.execute_bootstrap_sql(sql),
            f"{context}: sql={sql!r}",
        )

    def _capture_auto_analyze_state(self, env) -> None:
        rows = execute_result_rows(
            env.execute_sql,
            "SELECT @@GLOBAL.tidb_auto_analyze_ratio, "
            "@@GLOBAL.tidb_auto_analyze_start_time, "
            "@@GLOBAL.tidb_auto_analyze_end_time",
            "capture QP05 auto-analyze state",
        )
        if len(rows) != 1 or len(rows[0]) != 3:
            raise RuntimeError(
                "QP05 auto-analyze state query must return one three-column row: "
                f"rows={rows!r}"
            )
        self.original_auto_analyze_ratio = str(rows[0][0])
        self.original_auto_analyze_start_time = str(rows[0][1])
        self.original_auto_analyze_end_time = str(rows[0][2])

    def _disable_auto_analyze(self, env) -> None:
        require_success_payload(
            env.execute_sql("SET GLOBAL tidb_auto_analyze_ratio=0.000010"),
            "disable QP05 auto-analyze",
        )
        rows = execute_result_rows(
            env.execute_sql,
            "SELECT DATE_FORMAT(DATE_SUB(UTC_TIMESTAMP(), INTERVAL 30 MINUTE), '%H:%i +0000'), "
            "DATE_FORMAT(DATE_SUB(UTC_TIMESTAMP(), INTERVAL 29 MINUTE), '%H:%i +0000')",
            "choose QP05 closed auto-analyze window",
        )
        if len(rows) != 1 or len(rows[0]) != 2:
            raise RuntimeError(
                "QP05 closed auto-analyze window query must return one two-column row: "
                f"rows={rows!r}"
            )
        self.disabled_auto_analyze_start_time = str(rows[0][0])
        self.disabled_auto_analyze_end_time = str(rows[0][1])
        require_success_payload(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_start_time="
                f"'{self.disabled_auto_analyze_start_time}'"
            ),
            "close QP05 auto-analyze start time",
        )
        require_success_payload(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_end_time="
                f"'{self.disabled_auto_analyze_end_time}'"
            ),
            "close QP05 auto-analyze end time",
        )
        self._assert_auto_analyze_disabled(env)

    def _assert_auto_analyze_disabled(self, env) -> None:
        rows = execute_result_rows(
            env.execute_sql,
            "SELECT @@GLOBAL.tidb_auto_analyze_ratio, "
            "@@GLOBAL.tidb_auto_analyze_start_time, "
            "@@GLOBAL.tidb_auto_analyze_end_time",
            "verify QP05 auto-analyze is disabled",
        )
        observed = [str(value) for value in rows[0]]
        expected = [
            "0.000010",
            self.disabled_auto_analyze_start_time,
            self.disabled_auto_analyze_end_time,
        ]
        if float(observed[0]) != 0.000010 or observed[1:] != expected[1:]:
            raise RuntimeError(
                "QP05 requires auto-analyze to stay outside its active window: "
                f"expected={expected!r}, observed={observed!r}"
            )

    def _restore_auto_analyze_state(self, env) -> None:
        require_success_payload(
            env.execute_sql(
                f"SET GLOBAL tidb_auto_analyze_ratio={self.original_auto_analyze_ratio}"
            ),
            "restore QP05 auto-analyze ratio",
        )
        require_success_payload(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_start_time="
                f"'{self.original_auto_analyze_start_time}'"
            ),
            "restore QP05 auto-analyze start time",
        )
        require_success_payload(
            env.execute_sql(
                "SET GLOBAL tidb_auto_analyze_end_time="
                f"'{self.original_auto_analyze_end_time}'"
            ),
            "restore QP05 auto-analyze end time",
        )

    def _initialize_workload_connection_routers(self, context: FaultLifecycleContext) -> None:
        routers = {
            profile.connection_pool: {"initial_target": "tidb/tidb-0"}
            for profile in context.case.background_workload.profiles
            if profile.connection_pool is not None
        }
        context.env.initialize_connection_routers(routers)
        self._routers_initialized = True

    def _create_schema(self, env) -> None:
        self._execute(env, f"CREATE DATABASE IF NOT EXISTS {self.db}", "create QP05 database")
        for table in (
            self.audit_table,
            self.route_registry_table,
            self.page_context_table,
            self.table,
            self.numbers_table,
            self.digits_table,
        ):
            self._execute(
                env,
                f"DROP TABLE IF EXISTS {self.db}.{table}",
                f"clear QP05 table {self.db}.{table}",
            )
        self._execute(
            env,
            f"""
            CREATE TABLE {self.db}.{self.page_context_table} (
                route_key VARCHAR(64) PRIMARY KEY,
                tenant_id INT NOT NULL,
                order_state VARCHAR(12) NOT NULL,
                window_start DATETIME NOT NULL,
                window_end DATETIME NOT NULL,
                KEY qp05_page_scope (tenant_id, order_state, window_start, window_end)
            )
            """,
            "create QP05 page context table",
        )
        self._execute(
            env,
            f"""
            INSERT INTO {self.db}.{self.page_context_table}
                (route_key, tenant_id, order_state, window_start, window_end)
            VALUES
                ('checkout-history-page', 42, 'READY', '2025-01-01', '2025-07-01'),
                ('checkout-history-export', 42, 'READY', '2024-07-01', '2025-01-01'),
                ('checkout-history-replay', 177, 'READY', '2025-01-01', '2025-07-01'),
                ('checkout-history-ops', 42, 'SHIPPED', '2025-01-01', '2025-07-01'),
                ('merchant-settlement-page', 205, 'READY', '2025-01-01', '2025-04-01'),
                ('customer-support-page', 318, 'READY', '2024-10-01', '2025-01-01'),
                ('warehouse-replay-page', 177, 'SHIPPED', '2024-07-01', '2025-01-01'),
                ('fraud-review-page', 260, 'READY', '2025-04-01', '2025-07-01'),
                ('checkout-history-page-mobile', 42, 'READY', '2025-01-01', '2025-07-01'),
                ('checkout-history-legacy', 42, 'READY', '2024-10-01', '2025-01-01'),
                ('warehouse-replay-export', 177, 'SHIPPED', '2024-07-01', '2025-01-01'),
                ('merchant-settlement-export', 205, 'READY', '2024-10-01', '2025-01-01')
            """,
            "load QP05 page context routes",
        )
        self._execute(
            env,
            f"""
            CREATE TABLE {self.db}.{self.route_registry_table} (
                fingerprint VARCHAR(64) NOT NULL,
                route_key VARCHAR(64) NOT NULL,
                route_version INT NOT NULL,
                is_current TINYINT NOT NULL,
                surface VARCHAR(32) NOT NULL,
                projection_class VARCHAR(32) NOT NULL,
                slo_ms INT NOT NULL,
                PRIMARY KEY (fingerprint, route_version),
                KEY qp05_route_current (fingerprint, is_current, route_key)
            )
            """,
            "create QP05 route registry",
        )
        route_values = ",\n".join(
            "(" + ", ".join(
                str(value) if isinstance(value, int) else f"'{value}'"
                for value in row
            ) + ")"
            for row in self.route_registry_rows
        )
        self._execute(
            env,
            f"""
            INSERT INTO {self.db}.{self.route_registry_table}
                (fingerprint, route_key, route_version, is_current, surface, projection_class, slo_ms)
            VALUES
                {route_values}
            """,
            "load QP05 route registry versions",
        )
        self._execute(
            env,
            f"""
            CREATE TABLE {self.db}.{self.table} (
                event_id BIGINT PRIMARY KEY,
                tenant_id INT NOT NULL,
                event_time DATETIME NOT NULL,
                order_state VARCHAR(12) NOT NULL,
                order_total DECIMAL(10, 2) NOT NULL,
                currency CHAR(3) NOT NULL,
                fulfillment_zone TINYINT NOT NULL,
                merchant_id INT NOT NULL,
                customer_ref CHAR(10) NOT NULL,
                last_modified DATETIME NOT NULL,
                event_note VARCHAR(64) NOT NULL,
                KEY {self.fault_index_names[0]} (event_time, tenant_id, order_state, event_id),
                KEY {self.fault_index_names[1]} (order_state, event_time, tenant_id, event_id),
                KEY {self.fault_index_names[2]} (
                    event_time, tenant_id, order_state, event_id,
                    order_total, currency, fulfillment_zone, event_note
                ),
                KEY {self.fault_index_names[3]} (
                    event_time, tenant_id, order_state, event_id,
                    order_total, currency, fulfillment_zone, merchant_id, event_note
                ),
                KEY {self.fault_index_names[4]} (
                    order_state, event_time, tenant_id, event_id,
                    order_total, currency, fulfillment_zone, merchant_id, event_note
                ),
                KEY {self.fault_index_names[5]} (
                    event_time, tenant_id, order_state, event_id,
                    order_total, currency, fulfillment_zone, merchant_id, customer_ref,
                    last_modified, event_note
                ),
                KEY {self.fault_index_names[6]} (
                    order_state, event_time, tenant_id, event_id,
                    order_total, currency, fulfillment_zone, merchant_id, customer_ref,
                    last_modified, event_note
                ),
                KEY {self.fault_index_names[7]} (
                    event_time, fulfillment_zone, tenant_id, order_state, event_id,
                    order_total, currency, merchant_id, customer_ref, last_modified, event_note
                ),
                KEY qp05_history_tenant_window (
                    tenant_id, event_time, order_state, event_id,
                    order_total, currency, fulfillment_zone
                ),
                KEY qp05_history_state_window (
                    order_state, event_time, tenant_id, event_id,
                    order_total, currency, fulfillment_zone
                ),
                KEY qp05_merchant_recent (merchant_id, last_modified),
                KEY qp05_customer_time (customer_ref, event_time),
                KEY qp05_zone_state_modified (fulfillment_zone, order_state, last_modified),
                KEY qp05_currency_state_modified (currency, order_state, last_modified),
                KEY qp05_note_time (event_note, event_time)
            )
            """,
            "create QP05 order-event table",
        )
        self._execute(
            env,
            f"""
            CREATE TABLE {self.db}.{self.audit_table} (
                audit_id BIGINT PRIMARY KEY,
                event_id BIGINT NOT NULL,
                operation VARCHAR(16) NOT NULL,
                created_at DATETIME NOT NULL,
                KEY qp05_audit_event (event_id)
            )
            """,
            "create QP05 audit table",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.digits_table} (n TINYINT PRIMARY KEY)",
            "create QP05 digit generator",
        )
        self._execute(
            env,
            f"INSERT INTO {self.db}.{self.digits_table} VALUES "
            + ",".join(f"({value})" for value in range(10)),
            "load QP05 digit generator",
        )
        self._execute(
            env,
            f"CREATE TABLE {self.db}.{self.numbers_table} (n INT PRIMARY KEY)",
            "create QP05 number generator",
        )

    def _load_rows(self, env) -> None:
        expression = (
            "d0.n + d1.n * 10 + d2.n * 100 + d3.n * 1000 "
            "+ d4.n * 10000 + d5.n * 100000 + 1"
        )
        self._execute(
            env,
            f"""
            INSERT INTO {self.db}.{self.numbers_table} (n)
            SELECT {expression}
            FROM {self.db}.{self.digits_table} d0
            CROSS JOIN {self.db}.{self.digits_table} d1
            CROSS JOIN {self.db}.{self.digits_table} d2
            CROSS JOIN {self.db}.{self.digits_table} d3
            CROSS JOIN {self.db}.{self.digits_table} d4
            CROSS JOIN {self.db}.{self.digits_table} d5
            WHERE {expression} <= {self.row_count}
            """,
            "load QP05 number generator",
        )
        batch_size = 10_000
        for batch_start in range(1, self.row_count + 1, batch_size):
            batch_end = min(batch_start + batch_size, self.row_count + 1)
            self._execute(
                env,
                f"""
                INSERT INTO {self.db}.{self.table} (
                    event_id, tenant_id, event_time, order_state, order_total,
                    currency, fulfillment_zone, merchant_id, customer_ref,
                    last_modified, event_note
                )
                SELECT
                    n,
                    CASE WHEN MOD(n, 10) = 0 THEN 42 ELSE 100 + MOD(n, 400) END,
                    DATE_ADD('2024-07-01', INTERVAL MOD(n, 365) DAY),
                    CASE
                        WHEN MOD(n, 10) = 0 THEN CASE
                            WHEN MOD(n, 365) BETWEEN 184 AND 273
                            THEN CASE WHEN MOD(n DIV 10, 8) = 0 THEN 'READY' ELSE 'SHIPPED' END
                            ELSE CASE WHEN MOD(n DIV 10, 20) = 0 THEN 'READY' ELSE 'SHIPPED' END
                        END
                        ELSE CASE
                            WHEN MOD(n, 365) BETWEEN 184 AND 273
                                THEN CASE WHEN MOD(n DIV 8, 2) = 0 THEN 'READY' ELSE 'SHIPPED' END
                            WHEN MOD(n, 20) = 1 THEN 'READY'
                            ELSE 'SHIPPED'
                        END
                    END,
                    CAST(25 + MOD(n * 17, 97500) / 100 AS DECIMAL(10, 2)),
                    CASE MOD(n, 3) WHEN 0 THEN 'USD' WHEN 1 THEN 'EUR' ELSE 'JPY' END,
                    MOD(n, 8),
                    1000 + MOD(n, 2500),
                    LPAD(CAST(MOD(n, 100000) AS CHAR), 10, '0'),
                    DATE_ADD('2024-07-01', INTERVAL MOD(n, 365) DAY),
                    CONCAT('order-event-', MOD(n, 1000))
                FROM {self.db}.{self.numbers_table}
                WHERE n >= {batch_start} AND n < {batch_end}
                """,
                f"load QP05 business rows [{batch_start}, {batch_end})",
            )
        self._load_audit_rows(env)
        self._execute(
            env,
            f"ANALYZE TABLE {self.db}.{self.table} WITH 0.1 SAMPLERATE",
            "analyze QP05 order-event table",
        )

    def _load_audit_rows(self, env) -> None:
        self._execute(
            env,
            f"""
            INSERT INTO {self.db}.{self.audit_table}
                (audit_id, event_id, operation, created_at)
            SELECT (candidate.event_id * 2) + operation.op_no,
                   candidate.event_id,
                   CASE operation.op_no
                       WHEN 0 THEN 'checkout_view'
                       ELSE 'status_sync'
                   END,
                   candidate.event_time
            FROM (
                SELECT DISTINCT ranked.event_id, ranked.event_time
                FROM (
                    SELECT e.event_id, e.event_time,
                           ROW_NUMBER() OVER (
                               PARTITION BY c.route_key
                               ORDER BY e.event_time, e.event_id
                           ) AS route_rank
                    FROM {self.db}.{self.table} AS e
                    JOIN {self.db}.{self.page_context_table} AS c
                      ON e.tenant_id = c.tenant_id
                     AND e.order_state = c.order_state
                     AND e.event_time >= c.window_start
                     AND e.event_time < c.window_end
                ) AS ranked
                WHERE ranked.route_rank <= 120
            ) AS candidate
            JOIN (
                SELECT 0 AS op_no
                UNION ALL
                SELECT 1 AS op_no
            ) AS operation
            """,
            "load QP05 order-event audit eligibility",
        )

    def _verify_fault_state(self, env) -> None:
        rows = execute_result_rows(
            env.execute_sql,
            f"SELECT COUNT(*) FROM {self.db}.{self.table}",
            "verify QP05 row count",
        )
        if rows != [[self.row_count]]:
            raise RuntimeError(
                "QP05 fault row count mismatch: "
                f"table={self.db}.{self.table}, expected={self.row_count}, observed={rows!r}"
            )
        page_context_rows = execute_result_rows(
            env.execute_sql,
            f"SELECT COUNT(*) FROM {self.db}.{self.page_context_table}",
            "verify QP05 page context routes",
        )
        if page_context_rows != [[12]]:
            raise RuntimeError(
                "QP05 page context route count mismatch: "
                f"table={self.db}.{self.page_context_table}, expected=12, observed={page_context_rows!r}"
            )
        route_registry_rows = execute_result_rows(
            env.execute_sql,
            f"SELECT COUNT(*) FROM {self.db}.{self.route_registry_table}",
            "verify QP05 route registry rows",
        )
        if route_registry_rows != [[self.route_registry_row_count]]:
            raise RuntimeError(
                "QP05 route registry row count mismatch: "
                f"table={self.db}.{self.route_registry_table}, expected={self.route_registry_row_count}, "
                f"observed={route_registry_rows!r}"
            )
        catalog = execute_result_rows(
            env.execute_sql,
            self.index_catalog_sql,
            "verify QP05 fault index catalog",
        )
        for index_name in self.fault_index_names:
            columns = [
                (int(row[3]), str(row[4]))
                for row in catalog
                if len(row) > 4 and str(row[2]) == index_name
            ]
            if not columns:
                raise RuntimeError(
                    f"QP05 fault index is missing: table={self.db}.{self.table}, index={index_name!r}"
                )
        plan = self._explain_analyze(env)
        metrics = tidb_plan_metrics(plan, self.table)
        if not metrics["has_index_reader"] and not metrics["has_index_lookup"]:
            raise RuntimeError(
                "QP05 fault did not produce an index access path: "
                f"table={self.db}.{self.table}, metrics={metrics!r}"
            )
        if int(metrics["scan_volume"]) < self.fault_scan_floor:
            raise RuntimeError(
                "QP05 fault scan amplification is below the contract: "
                f"table={self.db}.{self.table}, scan_volume={metrics['scan_volume']}, "
                f"fault_scan_floor={self.fault_scan_floor}, plan={plan!r}"
            )

    def _explain_analyze(self, env) -> list:
        return execute_result_rows(
            env.execute_sql,
            f"EXPLAIN ANALYZE {self.query}",
            "QP05 EXPLAIN ANALYZE",
        )

    def _measure_p95_ms(self, env) -> tuple[float, tuple[float, ...]]:
        profile = measure_latency_profile(
            env.execute_sql,
            self.query,
            warmup_samples=0,
            measured_samples=self.latency_sample_count,
            context="QP05 latency probe",
        )
        return round(float(profile["p95_ms"]), 3), tuple(
            round(float(sample), 3) for sample in profile["samples_ms"]
        )
