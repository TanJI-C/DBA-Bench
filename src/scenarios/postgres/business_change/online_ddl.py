from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeCollationConversionForStoreReturnsCollationConversionEvaluatorCase,
    PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleEvaluatorCase,
    PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillEvaluatorCase,
    PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleEvaluatorCase,
    PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase,
    PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase,
)


from src.workloads.specs import WorkloadProfile

from src.execution.specs import PostgresCaseRuntime, CaseResourceSpec
from src.workloads.specs import BackgroundWorkloadSpec, EMPTY_BACKGROUND_WORKLOAD
from src.scenarios.base import DifficultyCalibration, PostgresScenario, FaultPlan, PostgresScenarioCase


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeOnlineDdlCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    target_column: str
    slow_queries: tuple[str, ...]
    simulated_rows: int
    writer_threads: int
    writer_interval: float
    blocker_hold_seconds: float
    audit_table: str
    queue_table: str

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlScenarioCase(PgBusinessChangeOnlineDdlCase):
    pass

def build_online_ddl_noise_profiles(
    table: str = "order_line",
    audit_table: str = "order_line_audit_shadow",
    queue_table: str = "order_note_backfill_queue",
) -> List[WorkloadProfile]:
    """Business-shaped noise for the online DDL change scenario.

    These profiles deliberately stay in the same order-entry domain as the
    target DDL. They make slow/top/workload activity show adjacent release and
    reporting work, so the agent must still verify the exact target table,
    column, table size, and lock risk before changing schema.
    """
    return [
        WorkloadProfile(
            name="order_entry_latency_probe",
            sql=(
                f"SELECT ol_w_id, ol_d_id, count(*) AS pending_lines, "
                f"sum(ol_amount) AS gross_amount "
                f"FROM {table} "
                "WHERE ol_delivery_d IS NULL "
                "GROUP BY ol_w_id, ol_d_id "
                "ORDER BY pending_lines DESC "
                "LIMIT 20"
            ),
            qps=0.7,
            tier="LIGHT",
            application_name="order-entry-api",
        ),
        WorkloadProfile(
            name="delivery_note_audit_rollup",
            sql=(
                f"SELECT ol_w_id, count(*) AS audited_lines, "
                "count(*) FILTER (WHERE ol_delivery_note IS NOT NULL) AS noted_lines "
                f"FROM {audit_table} "
                "GROUP BY ol_w_id "
                "ORDER BY audited_lines DESC "
                "LIMIT 10"
            ),
            qps=0.35,
            tier="MEDIUM",
            application_name="delivery-note-audit",
        ),
        WorkloadProfile(
            name="release_queue_backfill_probe",
            sql=(
                f"SELECT status, count(*) AS queued, max(updated_at) AS newest "
                f"FROM {queue_table} "
                "GROUP BY status "
                "ORDER BY queued DESC"
            ),
            qps=0.5,
            tier="LIGHT",
            application_name="release-backfill-preview",
        ),
        WorkloadProfile(
            name="order_line_sample_count_decoy",
            sql=(
                f"SELECT count(*) AS sampled_lines "
                f"FROM {table} "
                "WHERE ol_w_id BETWEEN 1 AND 4 "
                "AND ol_delivery_d IS NULL"
            ),
            qps=0.35,
            tier="LIGHT",
            application_name="release-cardinality-preview",
        ),
        WorkloadProfile(
            name="release_precheck_lock_probe",
            sql=(
                "SET LOCAL lock_timeout = '50ms'; "
                f"LOCK TABLE {audit_table} IN SHARE UPDATE EXCLUSIVE MODE;"
            ),
            qps=0.25,
            tier="LOCK_NOISE",
            application_name="release-precheck",
        ),
        WorkloadProfile(
            name="missing_delivery_note_cache_log_noise",
            sql="SELECT count(*) FROM delivery_note_release_cache_missing;",
            qps=0.25,
            tier="LOG_NOISE",
            application_name="release-cache-refresh",
        ),
    ]

_PGBUSINESSCHANGEONLINEDDLSCENARIO_CASE = PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlScenarioCase(
    case_id='order_line_delivery_note_ddl',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "large order line table under writes",
                    "entity": "order_line_delivery_note_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed large order line table under writes"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "add column needs access exclusive lock",
                    "entity": "order_line_delivery_note_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed add column needs access exclusive lock"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "audit and backfill queue are not target",
                    "entity": "order_line_delivery_note_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed audit and backfill queue are not target"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "short lock timeout with retry",
                    "entity": "order_line_delivery_note_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed short lock timeout with retry"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "verify delivery note column",
                    "entity": "order_line_delivery_note_ddl",
                    "evidence": [
                        "scripted diagnostic actions observed verify delivery note column"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "added the delivery note column"
            ],
            "verification": [
                "lock_timeout and retry strategy verified"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Online schema change on a large hot PostgreSQL order_line table.',
    alert='发布窗口告警：订单写入链路正在上线配送备注能力，应用映射字段为 ol_delivery_note。当前 order-entry 读写延迟 SLO 接近阈值，连接数、事务吞吐和发布预检任务同时升高。请确认应变更的在线业务对象，在不中断下单流量的前提下完成结构变更，并复查变更已生效。',
    alert_en="Release window alert: the order write path is rolling out a delivery note capability, and the application maps it to the column ol_delivery_note. The order-entry read/write latency SLO is close to its threshold, and connections, transaction throughput and release pre-check tasks are rising at the same time. Identify the online business object that should be changed, complete the structural change without interrupting order traffic, and re-check that the change has taken effect.",
    initial_state={'status': 'change_pending',
 'table': 'order_line',
 'workload': 'high_write_concurrency',
 'target_column': 'missing'},
    expected_target={'status': 'changed_safely',
 'table': 'order_line',
 'target_column': 'ol_delivery_note',
 'required_strategy': 'safe_online_ddl'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_online_ddl_noise_profiles()),
        worker_count=2,
        seed=0,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='order_line',
    target_column='ol_delivery_note',
    slow_queries=('ALTER TABLE order_line ADD COLUMN ol_delivery_note text;',),
    simulated_rows=100000000,
    writer_threads=3,
    writer_interval=0.05,
    blocker_hold_seconds=12.0,
    audit_table='order_line_audit_shadow',
    queue_table='order_note_backfill_queue',
    difficulty=DifficultyCalibration(
        diagnostic_depth=3,
        environmental_complexity=0.416667,
        reference_run_ids=(
            "reference-48__pg_business_change_online_ddl__"
            "order_line_delivery_note_ddl__mock__r001",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleScenarioCase(
    PgBusinessChangeOnlineDdlCase
):
    pass


_PGBUSINESSCHANGEONLINEDDLSCENARIO_SIMPLE_CASE = (
    PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleScenarioCase(
        case_id="order_line_gift_note_ddl_simple",
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "hot order line table under writes",
                        "entity": "order_line_gift_note_ddl_simple",
                        "evidence": [
                            "scripted diagnostic actions observed hot order line table under writes"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "add column needs access exclusive lock",
                        "entity": "order_line_gift_note_ddl_simple",
                        "evidence": [
                            "scripted diagnostic actions observed add column needs access exclusive lock"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "audit activity is not the target",
                        "entity": "order_line_gift_note_ddl_simple",
                        "evidence": [
                            "scripted diagnostic actions observed audit activity is not the target"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "short lock timeout with retry",
                        "entity": "order_line_gift_note_ddl_simple",
                        "evidence": [
                            "scripted diagnostic actions observed short lock timeout with retry"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "verify gift note column",
                        "entity": "order_line_gift_note_ddl_simple",
                        "evidence": [
                            "scripted diagnostic actions observed verify gift note column"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "added the gift note column"
                ],
                "verification": [
                    "lock_timeout and retry strategy verified"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-initialized:latest",
        workload_tag="initialized",
        title="Simplified online nullable-column release on a moderately large hot order table.",
        alert=(
            "发布窗口告警：订单链路正在上线礼赠备注能力，当前写入仍在持续，"
            "发布预检观察到短暂锁竞争。请确认实际在线对象和缺失结构，"
            "使用快速失败并可重试的方式完成变更，随后核验业务结构。"
        ),
        alert_en="Release window alert: the order path is rolling out a gift note capability, writes are still ongoing, and the release pre-check observed brief lock contention. Identify the actual online object and the missing structure, complete the change in a fail-fast and retryable way, and then verify the business structure.",
        initial_state={
            "status": "change_pending",
            "workload": "steady_write_concurrency",
            "target_column": "missing",
        },
        expected_target={
            "status": "changed_safely",
            "required_strategy": "bounded_lock_wait_with_retry",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(
                build_online_ddl_noise_profiles(
                    table="order_line",
                    audit_table="order_line_gift_audit_shadow",
                    queue_table="gift_note_release_queue",
                )[:2]
            ),
            worker_count=1,
            seed=0x4101,
            warmup_seconds=2,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="order_line",
        target_column="ol_gift_note",
        slow_queries=("ALTER TABLE order_line ADD COLUMN ol_gift_note text;",),
        simulated_rows=5000000,
        writer_threads=1,
        writer_interval=0.15,
        blocker_hold_seconds=4.0,
        audit_table="order_line_gift_audit_shadow",
        queue_table="gift_note_release_queue",
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.25,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_online_ddl_"
                "order_line_gift_note_ddl_simple_MockLLMAgent.json",
            ),
        ),
    )
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgBusinessChangeOnlineDdlInjector(BaseFaultInjector):
    """
    Simulate a hot TPC-C order_line table awaiting an online DDL change.
    The injector creates a compact local table, exposes a large reltuples
    estimate, and keeps lightweight writer threads active for observability.
    """
    def __init__(self):
        self.env = None
        self.table = "order_line"
        self.target_column = "ol_delivery_note"
        self.audit_table = "order_line_audit_shadow"
        self.queue_table = "order_note_backfill_queue"
        self.blocker_application_name = "checkout-order-ledger-hold"
        self._stop_event = None
        self._threads = []
        self._blocker_thread = None

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] Preparing hot table {self.table}...")
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                ol_id bigserial PRIMARY KEY,
                ol_w_id integer NOT NULL DEFAULT 1,
                ol_d_id integer NOT NULL DEFAULT 1,
                ol_o_id integer NOT NULL DEFAULT 1,
                ol_number integer NOT NULL DEFAULT 1,
                ol_i_id integer NOT NULL DEFAULT 1,
                ol_quantity integer NOT NULL DEFAULT 5,
                ol_amount numeric(12,2) NOT NULL DEFAULT 0,
                ol_delivery_d timestamp NULL
            );
        """)
        env.execute_sql(f"ALTER TABLE {self.table} DROP COLUMN IF EXISTS {self.target_column};")
        env.execute_sql(f"""
            INSERT INTO {self.table} (ol_w_id, ol_d_id, ol_o_id, ol_number, ol_i_id, ol_quantity, ol_amount)
            SELECT 1, (g % 10) + 1, g, (g % 15) + 1, (g % 100000) + 1, 5, 10.00
            FROM generate_series(1, 20000) AS g
            WHERE (SELECT count(*) FROM {self.table}) < 20000;
        """)
        env.execute_sql(f"ANALYZE {self.table};")
        env.execute_sql(
            f"UPDATE pg_class SET reltuples = {self.simulated_rows} "
            f"WHERE oid = '{self.table}'::regclass;"
        )
        self._ensure_noise_objects(env)
        self._start_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.target_column = _validate_sql_identifier(config['target_column'], "target_column")
        self.audit_table = _validate_sql_identifier(config['audit_table'], "audit_table")
        self.queue_table = _validate_sql_identifier(config['queue_table'], "queue_table")
        self.simulated_rows = int(config['simulated_rows'])
        self.writer_threads = int(config['writer_threads'])
        self.writer_interval = float(config['writer_interval'])
        self.blocker_hold_seconds = float(config['blocker_hold_seconds'])

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"(SELECT count(*) FROM {self.table}), "
                "NOT EXISTS (SELECT 1 FROM information_schema.columns "
                f"WHERE table_schema = 'public' AND table_name = '{self.table}' "
                f"AND column_name = '{self.target_column}');"
            ),
            "verify online-DDL fault image",
        )
        table_name, row_count, target_missing = payload["result"][0]
        if table_name != self.table or int(row_count) < 20000 or target_missing is not True:
            raise RuntimeError(
                f"Online-DDL fault image does not match the Case: table={table_name}, "
                f"row_count={row_count}, target_missing={target_missing}"
            )

    def _start_runtime(self) -> None:
        import threading
        import time

        self._stop_event = threading.Event()
        self._threads = []
        self._blocker_thread = threading.Thread(
            target=self._ddl_blocker_loop,
            args=(self.blocker_hold_seconds,),
            daemon=True,
        )
        self._blocker_thread.start()
        for idx in range(self.writer_threads):
            thread = threading.Thread(
                target=self._writer_loop,
                args=(idx, self.writer_interval),
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)

        time.sleep(1)
        print(
            f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] Hot write workload active; "
            f"simulated reltuples={self.simulated_rows}."
        )

    def _writer_loop(self, worker_id: int, interval: float):
        import random
        import time
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=3,
                application_name=f"checkout-order-writer-{worker_id}",
            )
            conn.autocommit = True
            while self._stop_event is not None and not self._stop_event.is_set():
                oid = random.randint(1, 100000000)
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO {self.table} "
                        "(ol_w_id, ol_d_id, ol_o_id, ol_number, ol_i_id, ol_quantity, ol_amount) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (1, worker_id + 1, oid, 1, random.randint(1, 100000), 5, 10.00),
                    )
                time.sleep(interval)
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] Writer {worker_id} stopped: {exc}")
        finally:
            if conn is not None:
                conn.close()

    def _ddl_blocker_loop(self, hold_seconds: float):
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                connect_timeout=3,
                application_name=self.blocker_application_name,
            )
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {self.table} "
                    "(ol_w_id, ol_d_id, ol_o_id, ol_number, ol_i_id, ol_quantity, ol_amount) "
                    "VALUES (99, 99, 99, 99, 99, 5, 10.00)"
                )
                if self._stop_event is not None:
                    self._stop_event.wait(timeout=hold_seconds)
            conn.commit()
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] DDL blocker stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                conn.close()

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {
            "qps": env.query_metrics("qps"),
            "active_connections": env.query_metrics("active_connections"),
            "table_estimate": env.execute_sql(
                f"SELECT reltuples::bigint FROM pg_class WHERE oid = '{self.table}'::regclass;"
            ),
        }

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background writer and blocker threads for teardown."""
        print("[FaultInjector:PgBusinessChangeOnlineDdlInjector] quiesce...")
        if self._stop_event is not None:
            self._stop_event.set()
            if self._blocker_thread is not None:
                self._blocker_thread.join(timeout=3)
                self._blocker_thread = None
            for thread in self._threads:
                thread.join(timeout=2)
            self._threads = []
            self._stop_event = None

    def recover(self, context: FaultLifecycleContext):
        if self._stop_event is not None:
            print("[FaultInjector:PgBusinessChangeOnlineDdlInjector] Stopping writer workload...")
            self._stop_event.set()
            if self._blocker_thread is not None:
                self._blocker_thread.join(timeout=3)
                self._blocker_thread = None
            for thread in self._threads:
                thread.join(timeout=2)
            self._threads = []
            self._stop_event = None

        if self.env is not None:
            print(f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] Cleaning target column {self.target_column}...")
            self.env.execute_sql(f"ALTER TABLE IF EXISTS {self.table} DROP COLUMN IF EXISTS {self.target_column};")
            self.env.execute_sql(f"ANALYZE {self.table};")

    def _ensure_noise_objects(self, env):
        """Create same-domain non-root-cause objects used by workload noise."""
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.audit_table} (
                audit_id bigserial PRIMARY KEY,
                ol_w_id integer NOT NULL DEFAULT 1,
                ol_d_id integer NOT NULL DEFAULT 1,
                ol_o_id integer NOT NULL DEFAULT 1,
                ol_amount numeric(12,2) NOT NULL DEFAULT 0,
                ol_delivery_d timestamp NULL,
                ol_delivery_note text NULL,
                captured_at timestamp NOT NULL DEFAULT now()
            );
        """)
        env.execute_sql(f"""
            INSERT INTO {self.audit_table} (ol_w_id, ol_d_id, ol_o_id, ol_amount, ol_delivery_d, ol_delivery_note)
            SELECT 1, (g % 10) + 1, g, 10.00,
                   CASE WHEN g % 3 = 0 THEN now() ELSE NULL END,
                   CASE WHEN g % 7 = 0 THEN 'precheck-note' ELSE NULL END
            FROM generate_series(1, 8000) AS g
            WHERE (SELECT count(*) FROM {self.audit_table}) < 8000;
        """)
        env.execute_sql(f"ANALYZE {self.audit_table};")
        env.execute_sql(
            f"UPDATE pg_class SET reltuples = {max(1000000, self.simulated_rows // 5)} "
            f"WHERE oid = '{self.audit_table}'::regclass;"
        )
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.queue_table} (
                queue_id bigserial PRIMARY KEY,
                order_id integer NOT NULL,
                status text NOT NULL DEFAULT 'pending',
                updated_at timestamp NOT NULL DEFAULT now()
            );
        """)
        env.execute_sql(f"""
            INSERT INTO {self.queue_table} (order_id, status, updated_at)
            SELECT g,
                   CASE WHEN g % 5 = 0 THEN 'retry' WHEN g % 2 = 0 THEN 'ready' ELSE 'pending' END,
                   now() - (g % 3600) * interval '1 second'
            FROM generate_series(1, 3000) AS g
            WHERE (SELECT count(*) FROM {self.queue_table}) < 3000;
        """)
        env.execute_sql(f"ANALYZE {self.queue_table};")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._start_runtime()
        print(f"[FaultInjector:PgBusinessChangeOnlineDdlInjector] Writer workload re-activated.")
class PgBusinessChangeOnlineDdlScenario(PostgresScenario):
    scenario_id = 'pg_business_change_online_ddl'
    description = 'Online schema change on a large hot PostgreSQL order_line table.'
    cases = (
        _PGBUSINESSCHANGEONLINEDDLSCENARIO_CASE,
        _PGBUSINESSCHANGEONLINEDDLSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgBusinessChangeOnlineDdlCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeOnlineDdlInjector,
                config={
                    'table': case.table,
                    'target_column': case.target_column,
                    'simulated_rows': case.simulated_rows,
                    'writer_threads': case.writer_threads,
                    'writer_interval': case.writer_interval,
                    'blocker_hold_seconds': case.blocker_hold_seconds,
                    'audit_table': case.audit_table,
                    'queue_table': case.queue_table,
                },
            ),
        )
