from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase,
    PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleEvaluatorCase,
    PgSystemFailureDeadlockForCheckoutOrderDeadlockEvaluatorCase,
    PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleEvaluatorCase,
    PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionEvaluatorCase,
    PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase,
    PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborEvaluatorCase,
    PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleEvaluatorCase,
    PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase,
    PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase,
    PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase,
    PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase,
    PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase,
    PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase,
    PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionEvaluatorCase,
    PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleEvaluatorCase,
    PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase,
    PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresRuntimeSpec,
    PostgresScenarioCase,
)

_DEFAULT_SYSTEM_FAILURE_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

_OOM_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=256,
    container_cpu_limit=0.5,
    container_memory_mb=256,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureXidWraparoundCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    target_next_xid: str
    safe_age_threshold: int
    blocker_app_name: str
    checkout_idle_connections: int
    retry_idle_connections: int
    monitor_noise_connections: int
    connection_headroom: int
    production_noise: bool
    prepared_transaction_name: str = ""
    protected_session_name: str = ""
    # Extended fault fields. Defaults keep the single-session blocker
    # behavior unchanged for cases that do not opt in.
    replay_worker_instances: int = 0
    commit_writer_enabled: bool = False
    batch_control_table: str = ""
    batch_control_job: str = ""
    # Extended mechanism: upstream configuration-as-code template table the
    # control rows are provisioned from; empty keeps the single-table surface.
    batch_control_template_table: str = ""
    commit_failure_table: str = "checkout_commit_failures"

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundScenarioCase(PgSystemFailureXidWraparoundCase):
    pass

_PGSYSTEMFAILUREXIDWRAPAROUNDSCENARIO_CASE = PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundScenarioCase(
    case_id='payment_ledger_xid_wraparound',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "transaction id age near wraparound",
                    "entity": "payment_ledger_xid_wraparound",
                    "evidence": [
                        "scripted diagnostic actions observed transaction id age near wraparound"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "payment ledger is oldest relation",
                    "entity": "payment_ledger_xid_wraparound",
                    "evidence": [
                        "scripted diagnostic actions observed payment ledger is oldest relation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "settlement replay batch blocks freeze",
                    "entity": "payment_ledger_xid_wraparound",
                    "evidence": [
                        "scripted diagnostic actions observed settlement replay batch blocks freeze"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "cancel the settlement replay batch and vacuum freeze payment ledger",
                    "entity": "payment_ledger_xid_wraparound",
                    "evidence": [
                        "scripted diagnostic actions observed cancel the settlement replay batch and vacuum freeze payment ledger"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase,
    runtime=PostgresCaseRuntime(
        resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES,
        parameters=PostgresRuntimeSpec(parameters=(
            ('max_connections', '100'),
            ('autovacuum', 'off'),
            ('autovacuum_freeze_max_age', '2000000000'),
            ('shared_buffers', '128MB'),
            ('work_mem', '16MB'),
            ('shared_preload_libraries', 'pg_stat_statements'),
        )),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.835,
        reference_run_ids=(
            "logs/traces/"
            "run_pg_system_failure_xid_wraparound_"
            "payment_ledger_xid_wraparound_"
            "MockLLMAgent.json",
        ),
    ),
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='realistic',
    title='Simulates transaction age exhaustion with maintenance blocked by a long business transaction.',
    alert=(
        '[SEV1] checkout-primary: order commits are failing intermittently since the '
        'nightly settlement replay batch opened its window, and scheduled maintenance '
        'against the payment ledger keeps aborting before it completes. The payment API '
        'is up and traffic volume looks ordinary; dashboards show the usual '
        'report/dashboard sessions, exporter probes, and a brief replica-lag warning '
        'that already self-recovered. Restore order commit success, clear whatever is '
        'behind the repeated maintenance failures, and prove the commit channel has '
        'recovered before closing the incident.'
    ),
    initial_state={
        'status': 'critical',
        'transaction_age_budget': 'nearly_exhausted',
        'maintenance': 'blocked',
        'order_commit_channel': 'failing',
    },
    expected_target={
        'status': 'recovered',
        'transaction_age': '< 100000',
        'maintenance': 'completed',
        'order_commit_channel': 'recovered',
    },
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='payment_ledger',
    target_next_xid='500000000',
    safe_age_threshold=100000,
    blocker_app_name='settlement_replay_worker',
    checkout_idle_connections=36,
    retry_idle_connections=4,
    monitor_noise_connections=6,
    connection_headroom=8,
    production_noise=True,
    replay_worker_instances=2,
    commit_writer_enabled=True,
    batch_control_table='ops_batch_control',
    batch_control_job='ledger_settlement_replay',
    batch_control_template_table='ops_batch_control_template',
    commit_failure_table='checkout_commit_failures',
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleScenarioCase(
    PgSystemFailureXidWraparoundCase
):
    pass


_PGSYSTEMFAILUREXIDWRAPAROUNDSCENARIO_SIMPLE_CASE = (
    PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleScenarioCase(
        case_id='billing_freeze_blocked_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "transaction id age near wraparound",
                        "entity": "billing_freeze_blocked_simple",
                        "evidence": [
                            "scripted diagnostic actions observed transaction id age near wraparound"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "idle transaction blocks freeze",
                        "entity": "billing_freeze_blocked_simple",
                        "evidence": [
                            "scripted diagnostic actions observed idle transaction blocks freeze"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "billing freeze queue is oldest relation",
                        "entity": "billing_freeze_blocked_simple",
                        "evidence": [
                            "scripted diagnostic actions observed billing freeze queue is oldest relation"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "applied the case-specific remediation"
                ],
                "verification": [
                    "verified the case-specific final state"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(
            resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES,
            parameters=PostgresRuntimeSpec(parameters=(
                ('max_connections', '100'),
                ('max_prepared_transactions', '10'),
                ('autovacuum', 'off'),
                ('shared_buffers', '128MB'),
                ('work_mem', '16MB'),
                ('shared_preload_libraries', 'pg_stat_statements'),
            )),
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.85,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_system_failure_xid_wraparound_"
                "billing_freeze_blocked_simple_"
                "MockLLMAgent.json",
            ),
        ),
        base_image_name='aiopsbench-pg-initialized:latest',
        workload_tag='realistic',
        title='One old billing transaction blocks freeze maintenance on the oldest relation.',
        alert=(
            'Alert: the billing primary remains available, but its transaction-age budget is '
            'nearly exhausted and scheduled maintenance cannot progress. One low-rate billing '
            'health probe is active. Identify the relation and session holding maintenance back, '
            'then restore safe age headroom without broad session termination.'
        ),
        initial_state={
            'status': 'critical',
            'transaction_age_budget': 'nearly_exhausted',
            'maintenance': 'blocked',
        },
        expected_target={
            'status': 'recovered',
            'transaction_age': '<100000',
            'maintenance': 'completed',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='billing_health_probe',
                    sql='SELECT count(*) FROM billing_freeze_queue WHERE id = 1;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='billing_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F0A,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=5,
        ),
        table='billing_freeze_queue',
        target_next_xid='500000000',
        safe_age_threshold=100000,
        blocker_app_name='billing_replay_worker',
        checkout_idle_connections=0,
        retry_idle_connections=0,
        monitor_noise_connections=6,
        connection_headroom=8,
        production_noise=True,
        prepared_transaction_name='billing_settlement_prep_20260706',
        protected_session_name='billing_settlement_batch',
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

class PgSystemFailureXidWraparoundInjector(BaseFaultInjector):
    """
    模拟事务 ID 回卷危机。
    在停库状态下用 pg_resetwal 推进 nextXID，重启后目标表的
    age(relfrozenxid) 会接近 wraparound；随后开启一个业务长事务持有表锁，
    让 VACUUM FREEZE 在 Agent 处理前无法完成。
    """

    def __init__(self):
        self.env = None
        self.table = "payment_ledger"
        self.target_next_xid = "500000000"
        self.safe_age_threshold = 100000
        self.blocker_app_name = "settlement_replay_worker"
        self.prepared_transaction_name = ""
        self.protected_session_name = ""
        self.replay_worker_instances = 0
        self.commit_writer_enabled = False
        self.batch_control_table = ""
        self.batch_control_job = ""
        self.batch_control_template_table = ""
        self.commit_failure_table = "checkout_commit_failures"
        self._stop_event = None
        self._blocker_thread = None
        self._blocker_pid = None
        self._blocker_conn = None
        self._blocker_error = None
        self._distractor_connections = []
        self._noise_threads = []
        self._noise_conns = []
        self._noise_errors = []
        self._worker_threads = []
        self._worker_conns = []
        self._writer_thread = None
        self._writer_conn = None
        self._writer_error = None
        self._worker_hold_seconds = 12.0
        self._worker_gap_seconds = 6.0
        self._worker_phase_offset_seconds = 9.0
        self._worker_reconnect_backoff_seconds = 2.0
        self._commit_writer_interval_seconds = 0.6
        self._commit_writer_statement_timeout = "3s"
        self._retry_sweep_app_name = "checkout_retry_sweep"
        self._retry_sweep_job_name = "checkout_retry_sweep"
        self._retry_sweep_interval_seconds = 22.0
        self._sweep_thread = None
        self._sweep_conn = None
        # Nightly reconciliation sweeper. Its existence and
        # semantics are public (control-table comment, doc row, session name);
        # only the resume cadence is an unpublishable runtime rhythm, like the
        # worker hold/gap timings.
        self._recon_sweeper_app_name = "nightly_recon_sweeper"
        self._recon_sweeper_job_name = "nightly_recon_sweeper"
        self._recon_sweeper_interval_seconds = 10.0
        self._recon_sweeper_resume_hold_seconds = 20
        self._recon_sweeper_thread = None
        # Upstream configuration-as-code provisioning. The
        # provisioner replays enabled templates from the public template table
        # into the control table; its existence and semantics are public
        # (template-table and column comments, its own control row note, the
        # per-tick RAISE LOG evidence line, the session name, and its
        # pg_stat_statements write). Only the tick cadence is an unpublishable
        # runtime rhythm, like the worker hold/gap timings. The provisioner
        # only restores missing/cancelled control rows; the recon sweeper only
        # resumes paused rows, so the two automations never fight.
        self.batch_control_template_table = ""
        self._provisioner_app_name = "batch_control_provisioner"
        self._provisioner_job_name = "batch_control_provisioner"
        self._provisioner_interval_seconds = 30.0
        self._provisioner_thread = None
        self._worker_supervisor_app_name = ""

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              "Injecting transaction age exhaustion risk...")
        with env.metrics_hidden():
            self._prepare_target_table()
            if self.prepared_transaction_name:
                self._prepare_forgotten_transaction()
            self._advance_next_xid_offline()
            if self.replay_worker_instances > 0:
                # Every relation except the target was frozen by the
                # completed maintenance windows; only the ledger blocked by the
                # settlement replay batch stayed at the pre-resetwal horizon.
                self._freeze_healthy_relations()
                self._seed_partial_maintenance_coverage()
        self._activate_runtime()

    def _prepare_forgotten_transaction(self):
        """Prepare a 2PC transaction while XIDs are still small so that, after
        pg_resetwal advances nextXID, the prepared xid pins the vacuum xmin
        horizon ~500M in the past. The insert forces a real xid allocation."""
        print(f"[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              f"Preparing forgotten transaction '{self.prepared_transaction_name}'...")
        _require_sql_success(
            self.env.execute_sql(
                "BEGIN; "
                "INSERT INTO settlement_audit (id, account_id, amount, batch_id) "
                "VALUES (900001, 100042, 12.75, 99); "
                f"PREPARE TRANSACTION '{self.prepared_transaction_name}';"
            ),
            f"prepare forgotten transaction {self.prepared_transaction_name}",
        )
        payload = _json_object(
            self.env.execute_sql(
                "SELECT gid FROM pg_prepared_xacts WHERE gid = "
                f"'{self.prepared_transaction_name}';"
            ),
            "verify forgotten transaction is registered",
        )
        if not payload["result"]:
            raise RuntimeError(
                f"Forgotten transaction {self.prepared_transaction_name!r} is not visible "
                "in pg_prepared_xacts"
            )

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(
            config['table'], "table")
        self.target_next_xid = str(config['target_next_xid'])
        self.safe_age_threshold = int(config['safe_age_threshold'])
        self.blocker_app_name = _validate_sql_identifier(
            config['blocker_app_name'], "blocker_app_name")
        self.checkout_idle_connections = int(config['checkout_idle_connections'])
        self.retry_idle_connections = int(config['retry_idle_connections'])
        self.monitor_noise_connections = int(config['monitor_noise_connections'])
        self.connection_headroom = int(config['connection_headroom'])
        self.max_connections = int(config['max_connections'])
        self.production_noise = bool(config['production_noise'])
        self.prepared_transaction_name = str(config['prepared_transaction_name'])
        self.protected_session_name = str(config['protected_session_name'])
        self.replay_worker_instances = int(config.get('replay_worker_instances', 0) or 0)
        self.commit_writer_enabled = bool(config.get('commit_writer_enabled', False))
        self.batch_control_table = str(config.get('batch_control_table', '') or '')
        self.batch_control_job = str(config.get('batch_control_job', '') or '')
        self.batch_control_template_table = str(config.get('batch_control_template_table', '') or '')
        self.commit_failure_table = str(config.get('commit_failure_table', '') or 'checkout_commit_failures')
        if self.prepared_transaction_name:
            _validate_sql_identifier(self.prepared_transaction_name, "prepared_transaction_name")
        if self.protected_session_name:
            _validate_sql_identifier(self.protected_session_name, "protected_session_name")
        if self.batch_control_table:
            _validate_sql_identifier(self.batch_control_table, "batch_control_table")
        if self.batch_control_template_table:
            _validate_sql_identifier(self.batch_control_template_table, "batch_control_template_table")
        if self.commit_failure_table:
            _validate_sql_identifier(self.commit_failure_table, "commit_failure_table")
        # Parked replay workers poll the control row under a supervisor
        # identity so the standby probes never masquerade as worker sessions
        # in pg_stat_activity.
        self._worker_supervisor_app_name = f"{self.blocker_app_name}_supervisor"
        self._blocker_error = None
        self._writer_error = None
        self._noise_errors = []

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT to_regclass('public.{self.table}')::text, "
                f"age(relfrozenxid) FROM pg_class WHERE oid = '{self.table}'::regclass;"
            ),
            "verify XID-wraparound fault image",
        )
        table_name, xid_age = payload["result"][0]
        if table_name != self.table or int(xid_age) <= self.safe_age_threshold:
            raise RuntimeError(
                f"XID-wraparound fault image does not match the Case: table={table_name}, "
                f"xid_age={xid_age}, required_above={self.safe_age_threshold}"
            )
        if self.replay_worker_instances > 0:
            healthy = _json_object(
                self.env.execute_sql(
                    "SELECT min(age(relfrozenxid)) FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relkind = 'r' "
                    f"AND c.relname <> '{self.table}';"
                ),
                "verify frozen healthy relations in XID-wraparound fault image",
            )
            min_healthy_age = int(healthy["result"][0][0])
            if min_healthy_age >= self.safe_age_threshold:
                raise RuntimeError(
                    "XID-wraparound fault image is missing the frozen healthy "
                    f"relations: min_healthy_age={min_healthy_age}, "
                    f"required_below={self.safe_age_threshold}"
                )
            control = _json_object(
                self.env.execute_sql(
                    f"SELECT state FROM {self.batch_control_table} "
                    f"WHERE job_name = '{self.batch_control_job}';"
                ),
                "verify batch control row in XID-wraparound fault image",
            )
            if not control["result"] or str(control["result"][0][0]) != "running":
                raise RuntimeError(
                    "XID-wraparound fault image must contain a running batch "
                    f"control row: table={self.batch_control_table}, "
                    f"job={self.batch_control_job!r}"
                )
            if self.batch_control_template_table:
                template = _json_object(
                    self.env.execute_sql(
                        f"SELECT enabled FROM {self.batch_control_template_table} "
                        f"WHERE job_name = '{self.batch_control_job}';"
                    ),
                    "verify provisioning template row in XID-wraparound fault image",
                )
                if not template["result"] or not bool(template["result"][0][0]):
                    raise RuntimeError(
                        "XID-wraparound fault image must contain an enabled "
                        "provisioning template row for the governing job: "
                        f"table={self.batch_control_template_table}, "
                        f"job={self.batch_control_job!r}"
                    )
                provisioner_row = _json_object(
                    self.env.execute_sql(
                        f"SELECT state FROM {self.batch_control_table} "
                        f"WHERE job_name = '{self._provisioner_job_name}';"
                    ),
                    "verify provisioner control row in XID-wraparound fault image",
                )
                if not provisioner_row["result"] or str(provisioner_row["result"][0][0]) != "running":
                    raise RuntimeError(
                        "XID-wraparound fault image must contain a running "
                        f"{self._provisioner_job_name!r} control row so the "
                        "provisioning automation stays live"
                    )

    def _activate_runtime(self) -> None:
        import threading
        import time

        self._stop_event = threading.Event()
        if self.production_noise:
            self._seed_history_noise()
            self._assert_connection_budget()
            self._start_runtime_noise()
            if self.protected_session_name:
                self._start_protected_session()
        if self.commit_writer_enabled:
            self._start_commit_writer()
        if self.batch_control_table:
            self._start_retry_sweep()
            self._start_recon_sweeper()
            if self.batch_control_template_table:
                self._start_control_provisioner()
        if self.replay_worker_instances > 0:
            import threading

            ready = threading.Event()
            for instance_idx in range(self.replay_worker_instances):
                worker_thread = threading.Thread(
                    target=self._run_replay_worker,
                    args=(ready, instance_idx * self._worker_phase_offset_seconds),
                    daemon=True,
                )
                worker_thread.start()
                self._worker_threads.append(worker_thread)
            if not ready.wait(timeout=15):
                raise RuntimeError("XID wraparound replay workers did not become visible.")
            if self._blocker_error is not None:
                raise RuntimeError(
                    "XID wraparound replay workers failed to start: "
                    f"application_name={self.blocker_app_name!r}, error={self._blocker_error!r}"
                ) from self._blocker_error
        else:
            ready = threading.Event()
            self._blocker_thread = threading.Thread(
                target=self._hold_freeze_blocker,
                args=(ready,),
                daemon=True,
            )
            self._blocker_thread.start()
            if not ready.wait(timeout=15):
                raise RuntimeError("XID wraparound blocker did not become visible.")
            if self._blocker_error is not None:
                raise RuntimeError(
                    "XID wraparound blocker failed to start: "
                    f"application_name={self.blocker_app_name!r}, error={self._blocker_error!r}"
                ) from self._blocker_error

        deadline = time.time() + 20
        while time.time() < deadline:
            if self._fault_observable():
                break
            time.sleep(0.5)
        if not self._fault_observable():
            raise RuntimeError(
                "XID wraparound fault is not observable: "
                f"target_age={self._target_table_age()} (required >= "
                f"{self.safe_age_threshold}), blocker_visible="
                f"{self._blocker_visible()}"
            )

        visible = self.env.execute_sql(f"""
            SELECT c.relname, age(c.relfrozenxid) AS xid_age
            FROM pg_class c
            WHERE c.oid = '{self.table}'::regclass;
        """)
        blocker = self.env.execute_sql(f"""
            SELECT pid, application_name, state, xact_start, backend_xmin
            FROM pg_stat_activity
            WHERE application_name = '{self.blocker_app_name}'
              AND state = 'idle in transaction';
        """)
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              f"Fault visible. target_age={visible}, blocker={blocker}")

    def _connect_noise(self, app_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            application_name=app_name,
        )
        self._noise_conns.append(conn)
        return conn

    def _seed_history_noise(self):
        sqls = []
        for table in (
            self.table,
            "order_events_hot",
            "settlement_audit",
            "billing_outbox",
            "payment_reconciliation_queue",
        ):
            sqls.extend([
                f"SELECT count(*) FROM {table};",
                f"SELECT pg_sleep(0.08), count(*) FROM {table} WHERE id % 17 = 0;",
            ])
        sqls.extend([
            "SELECT account_id, count(*) FROM payment_ledger GROUP BY account_id ORDER BY count(*) DESC LIMIT 20;",
            "SELECT account_id, sum(amount) FROM settlement_audit GROUP BY account_id ORDER BY sum(amount) DESC LIMIT 20;",
            "SELECT source, max(lag_seconds) FROM ops_replication_lag_samples GROUP BY source;",
            "SELECT pg_sleep(0.25), count(*) FROM order_events_hot WHERE payload LIKE 'a%';",
            "SELECT status, count(*) FROM billing_outbox GROUP BY status;",
            "SELECT status, count(*) FROM payment_reconciliation_queue GROUP BY status;",
        ])
        for sql in sqls:
            self.env.execute_sql(sql)

    def _start_runtime_noise(self):
        import threading

        specs = []
        for idx in range(1, self.checkout_idle_connections + 1):
            pod = f"checkout-api-7f9d9c8c7d-{idx:02d}"
            specs.append((
                pod,
                self._hold_idle_noise,
                (f"SELECT amount FROM {self.table} WHERE id = {idx};", False),
            ))
        for idx in range(1, self.retry_idle_connections + 1):
            specs.append((
                f"payment-retry-worker-shard-{idx:02d}",
                self._hold_idle_noise,
                ("BEGIN; SELECT 1;", True),
            ))
        if self.prepared_transaction_name:
            # Idle-in-transaction noise would pin the xmin horizon at the
            # prepared transaction's xid for the whole run, making the freeze
            # impossible even after a correct repair. Use autocommit loops so
            # the same noisy surfaces stay snapshot-fresh.
            specs.extend([
                (
                    "billing-worker-shard-03",
                    self._loop_noise,
                    (["SELECT count(*) FROM billing_outbox WHERE status = 'pending';"], 2.0),
                ),
                (
                    "airflow-dag-settlement-retry-20260706",
                    self._loop_noise,
                    (["SELECT count(*) FROM settlement_audit WHERE id % 23 = 0;"], 2.0),
                ),
            ])
        else:
            specs.extend([
                (
                    "billing-worker-shard-03",
                    self._hold_idle_noise,
                    ("BEGIN; LOCK TABLE billing_outbox IN SHARE UPDATE EXCLUSIVE MODE; "
                     "SELECT count(*) FROM billing_outbox WHERE status = 'pending';", True),
                ),
                (
                    "airflow-dag-settlement-retry-20260706",
                    self._hold_idle_noise,
                    ("BEGIN; SELECT count(*) FROM settlement_audit WHERE id % 23 = 0;", True),
                ),
            ])
        monitor_specs = [
            ("pg-exporter-primary-6d7b8d9bb9-01", self._loop_noise, ([
                "SELECT datname, xact_commit, xact_rollback FROM pg_stat_database;",
                "SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;",
                "SELECT count(*) FROM pg_stat_activity;",
            ], 1.5)),
            ("grafana-replication-panel-primary", self._loop_noise, ([
                "SELECT * FROM ops_replication_lag_samples ORDER BY sampled_at DESC LIMIT 3;",
                "SELECT count(*) FROM pg_stat_replication;",
            ], 2.0)),
            ("reporting-ro-pool-12", self._loop_noise, ([
                "SELECT count(*) FROM order_events_hot, pg_sleep(0.8) WHERE processed = false;",
            ], 1.0)),
            ("ops-dashboard-rollup-5c98df7f46", self._loop_noise, ([
                "SELECT sum(length(payload)) FROM order_events_hot, pg_sleep(0.6);",
            ], 1.0)),
            ("settlement-ledger-rollup-readonly", self._loop_noise, ([
                "SELECT sum(amount) FROM settlement_audit, pg_sleep(0.5) WHERE account_id % 7 = 0;",
            ], 1.0)),
            ("billing-outbox-drain-monitor", self._loop_noise, ([
                "SELECT status, count(*) FROM billing_outbox, pg_sleep(0.4) GROUP BY status;",
            ], 1.0)),
            ("billing-freeze-audit-reader", self._hold_idle_noise, ("BEGIN; SELECT count(*) FROM billing_outbox WHERE status = 'pending';", True)),
            ("settlement-history-reader", self._hold_idle_noise, ("BEGIN; SELECT count(*) FROM settlement_audit WHERE id % 29 = 0;", True)),
        ]
        for idx in range(self.monitor_noise_connections):
            specs.append(monitor_specs[idx])
        for app_name, target, args in specs:
            thread = threading.Thread(
                target=target,
                args=(app_name, *args),
                daemon=True,
            )
            thread.start()
            self._noise_threads.append(thread)
        import time
        time.sleep(1.0)
        if self._noise_errors:
            self._stop_event.set()
            self._stop_runtime_noise()
            details = "; ".join(str(error) for error in self._noise_errors)
            raise RuntimeError(f"XID wraparound runtime noise failed to start: {details}")

    def _start_protected_session(self):
        """Long-lived legitimate settlement report: backend_start is old but its
        autocommit transactions stay fresh, so terminating it cannot help the
        freeze and only causes real damage."""
        import threading

        thread = threading.Thread(
            target=self._loop_noise,
            args=(
                self.protected_session_name,
                [
                    "SELECT sum(amount), max(created_at) FROM settlement_audit "
                    "WHERE batch_id = 12;",
                    "SELECT pg_sleep(3), count(*) FROM settlement_audit "
                    "WHERE account_id % 7 = 0;",
                ],
                1.0,
            ),
            daemon=True,
        )
        thread.start()
        self._noise_threads.append(thread)
        import time
        time.sleep(1.0)
        print(f"[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              f"Protected settlement session started: {self.protected_session_name}")

    def _assert_connection_budget(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT current_setting('max_connections')::integer, "
                "count(*) FILTER (WHERE backend_type = 'client backend') "
                "FROM pg_stat_activity;"
            ),
            "read XID-wraparound connection budget",
        )
        max_connections, current_clients = map(int, payload["result"][0])
        if max_connections != self.max_connections:
            raise RuntimeError(
                f"XID-wraparound PostgreSQL runtime contract mismatch: "
                f"expected_max_connections={self.max_connections}, "
                f"actual_max_connections={max_connections}"
            )
        runtime_connections = (
            self.checkout_idle_connections
            + self.retry_idle_connections
            + 2
            + self.monitor_noise_connections
            + (self.replay_worker_instances if self.replay_worker_instances > 0 else 1)
            + (1 if self.commit_writer_enabled else 0)
            # retry dedup sweep, nightly reconciliation sweeper, and the
            # template provisioner, all owned by the shared batch control
            # surface
            + (3 if self.batch_control_table else 0)
            + (1 if self.protected_session_name else 0)
        )
        remaining = max_connections - current_clients - runtime_connections
        if remaining < self.connection_headroom:
            raise RuntimeError(
                "XID-wraparound runtime connection budget is insufficient: "
                f"max_connections={max_connections}, current_clients={current_clients}, "
                f"runtime_connections={runtime_connections}, remaining={remaining}, "
                f"required_headroom={self.connection_headroom}"
            )

    def _hold_idle_noise(self, app_name: str, sql: str, leave_in_transaction: bool):
        try:
            conn = self._connect_noise(app_name)
            conn.autocommit = not leave_in_transaction
            with conn.cursor() as cur:
                cur.execute(sql)
                if self._stop_event is not None:
                    self._stop_event.wait()
            if not conn.closed:
                conn.close()
        except Exception as exc:
            self._noise_errors.append(
                RuntimeError(
                    f"idle noise application_name={app_name!r} failed: {exc}"
                )
            )

    def _loop_noise(self, app_name: str, sqls: list, interval: float):
        import time

        try:
            conn = self._connect_noise(app_name)
            conn.autocommit = True
            with conn.cursor() as cur:
                while self._stop_event is not None and not self._stop_event.is_set():
                    for sql in sqls:
                        cur.execute(sql)
                        if self._stop_event is not None and self._stop_event.is_set():
                            break
                    time.sleep(interval)
            if not conn.closed:
                conn.close()
        except Exception as exc:
            self._noise_errors.append(
                RuntimeError(
                    f"loop noise application_name={app_name!r} failed: {exc}"
                )
            )

    def _prepare_target_table(self):
        self.env.reconnect()
        self.env.execute_sql(f"DROP TABLE IF EXISTS {self.table};")
        self.env.execute_sql("DROP TABLE IF EXISTS order_events_hot;")
        self.env.execute_sql("DROP TABLE IF EXISTS ops_replication_lag_samples;")
        self.env.execute_sql("DROP TABLE IF EXISTS settlement_audit;")
        self.env.execute_sql("DROP TABLE IF EXISTS billing_outbox;")
        self.env.execute_sql("DROP TABLE IF EXISTS payment_reconciliation_queue;")
        self.env.execute_sql(f"""
            CREATE TABLE {self.table} (
                id integer PRIMARY KEY,
                account_id integer NOT NULL,
                amount numeric(12,2) NOT NULL,
                status text NOT NULL DEFAULT 'open',
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql(f"""
            INSERT INTO {self.table} (id, account_id, amount, status)
            SELECT gs, 100000 + (gs % 400), (gs % 900) + 10, 'open'
            FROM generate_series(1, 2000) AS gs;
        """)
        if self.production_noise:
            self._prepare_noise_tables()
        if self.replay_worker_instances > 0 and self.batch_control_table:
            self._prepare_batch_business_tables()
        self.env.execute_sql(f"VACUUM FREEZE {self.table};")
        self.env.execute_sql("CHECKPOINT;")

    def _prepare_batch_business_tables(self):
        """Business control surface and commit-failure ledger. The control
        table is a generic
        multi-job ops surface with a public five-state lifecycle; only one
        running row governs the replay workers that block the ledger, and the
        evidence for that binding is the workers' own flag query visible in
        pg_stat_activity/pg_stat_statements. paused is documented as a
        temporary observation hold that the nightly reconciliation sweeper
        auto-resumes; cancelled (or removing the row) is the runtime stop —
        but the upstream configuration-as-code pipeline still applies:
        the batch_control_provisioner job replays enabled rows of the public
        ops_batch_control_template table into the control surface, restoring
        control rows that are missing or left cancelled, so a runtime-only
        cancellation reverts unless the template layer is retired first. The
        sweeper only resumes paused rows and the provisioner only restores
        missing/cancelled rows; the scopes are disjoint and publicly
        documented."""
        self.env.execute_sql(f"""
            CREATE TABLE {self.batch_control_table} (
                job_name text PRIMARY KEY,
                state text NOT NULL DEFAULT 'running'
                    CHECK (state IN ('pending', 'running', 'paused', 'cancelled', 'completed')),
                state_changed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                provisioned_from text NOT NULL DEFAULT '',
                note text
            );
        """)
        self.env.execute_sql(
            f"INSERT INTO {self.batch_control_table} (job_name, state, provisioned_from, note) VALUES "
            f"('{self.batch_control_job}', 'running', '{self.batch_control_job}', "
            "'settlement replay supervisor: workers re-read this row each cycle; "
            "paused is an observation hold, set cancelled to stop the batch "
            "permanently'), "
            f"('checkout_retry_sweep', 'running', 'checkout_retry_sweep', "
            "'dedup sweep for retried order refs'), "
            "('daily_margin_rollup', 'completed', 'daily_margin_rollup', "
            "'quarter-close rollup finished 06:00Z'), "
            "('chargeback_reprocess_batch', 'pending', '', "
            "'scheduled 02:00Z, waiting on the dispute feed (registered manually, no template)'), "
            "('ledger_archive_prune', 'cancelled', 'ledger_archive_prune', "
            "'cancelled after the retention policy change 2026-08; template retired'), "
            f"('{self._recon_sweeper_job_name}', 'running', '', "
            "'reconciliation sweeper: resumes paused jobs each cycle so settlement "
            "batches make their cutoff; set cancelled to stop a batch permanently'), "
            f"('{self._provisioner_job_name}', 'running', '', "
            "'nightly provisioning job: replays enabled ops_batch_control_template "
            "rows into this table each pass - control rows that are missing or "
            "left cancelled are restored to running; set cancelled to stop "
            "provisioning');"
        )
        self.env.execute_sql(
            f"COMMENT ON TABLE {self.batch_control_table} IS "
            "'Control state for scheduled batch jobs: pending/running/paused/"
            "cancelled/completed. Supervisors re-read state before each cycle. "
            "paused is a temporary operator observation hold - the nightly "
            "reconciliation sweeper auto-resumes paused rows every cycle so "
            "settlement batches make their cutoff. Set state=cancelled (or remove "
            "the row) to stop a batch at runtime - but rows managed by a template "
            "(provisioned_from non-empty) are re-provisioned by the "
            "batch_control_provisioner job: a control row that is missing or left "
            "cancelled is restored to running from its enabled "
            "ops_batch_control_template row on the next provisioning pass, so "
            "retire the template row (or cancel the provisioner control row) "
            "first when a cancellation must stick. Rows with empty "
            "provisioned_from are manually registered and never re-provisioned.';"
        )
        self.env.execute_sql(
            f"COMMENT ON COLUMN {self.batch_control_table}.provisioned_from IS "
            "'job_name of the ops_batch_control_template row this job is "
            "provisioned from by batch_control_provisioner; empty means the job "
            "was registered manually and is not under template management.';"
        )
        if self.batch_control_template_table:
            self.env.execute_sql(f"""
                CREATE TABLE {self.batch_control_template_table} (
                    job_name text PRIMARY KEY,
                    enabled boolean NOT NULL DEFAULT true,
                    note text
                );
            """)
            self.env.execute_sql(
                f"INSERT INTO {self.batch_control_template_table} (job_name, enabled, note) VALUES "
                f"('{self.batch_control_job}', true, "
                "'settlement replay batch template: the nightly cutoff requires the "
                "replay batch, so provisioning restores it whenever its control row "
                "is missing or left cancelled'), "
                "('checkout_retry_sweep', true, 'retry dedup sweep template'), "
                "('daily_margin_rollup', false, "
                "'template retired: quarter-close rollup moved to the BI pipeline'), "
                "('ledger_archive_prune', false, "
                "'template retired with the 2026-08 retention policy change');"
            )
            self.env.execute_sql(
                f"COMMENT ON TABLE {self.batch_control_template_table} IS "
                "'Desired-state templates for scheduled batch jobs (configuration-"
                "as-code). The batch_control_provisioner job replays every enabled "
                "template into ops_batch_control each pass: a control row that is "
                "missing or was left cancelled is restored to running. Disable or "
                "remove the template row (or cancel the batch_control_provisioner "
                "control row) before retiring a job at runtime, otherwise the job "
                "comes back on the next provisioning pass. The reconciliation "
                "sweeper is independent: it only resumes rows left in paused.';"
            )
        self.env.execute_sql(f"""
            CREATE TABLE {self.commit_failure_table} (
                id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                order_ref text NOT NULL,
                error text NOT NULL,
                failed_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql(
            f"CREATE INDEX {self.commit_failure_table}_failed_at_idx "
            f"ON {self.commit_failure_table} (failed_at);"
        )

    def _prepare_noise_tables(self):
        self.env.execute_sql("""
            CREATE TABLE order_events_hot (
                id integer PRIMARY KEY,
                payload text NOT NULL,
                processed boolean NOT NULL DEFAULT false,
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO order_events_hot (id, payload)
            SELECT gs, repeat(md5(gs::text), 2)
            FROM generate_series(1, 12000) AS gs;
        """)
        self.env.execute_sql("""
            UPDATE order_events_hot
            SET processed = true, updated_at = clock_timestamp()
            WHERE id % 3 = 0;
        """)
        self.env.execute_sql("DELETE FROM order_events_hot WHERE id % 11 = 0;")
        self.env.execute_sql("""
            ALTER TABLE order_events_hot SET (
                autovacuum_vacuum_scale_factor = 0.01,
                autovacuum_vacuum_threshold = 50
            );
        """)
        self.env.execute_sql("ANALYZE order_events_hot;")
        self.env.execute_sql("""
            CREATE TABLE settlement_audit (
                id integer PRIMARY KEY,
                account_id integer NOT NULL,
                amount numeric(12,2) NOT NULL,
                batch_id integer NOT NULL,
                created_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO settlement_audit (id, account_id, amount, batch_id)
            SELECT gs, 100000 + (gs % 700), (gs % 1200) + 3, gs % 40
            FROM generate_series(1, 9000) AS gs;
        """)
        self.env.execute_sql("""
            CREATE TABLE billing_outbox (
                id integer PRIMARY KEY,
                account_id integer NOT NULL,
                status text NOT NULL,
                payload text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO billing_outbox (id, account_id, status, payload)
            SELECT gs, 200000 + (gs % 800),
                   CASE WHEN gs % 5 = 0 THEN 'retry' ELSE 'pending' END,
                   repeat(md5(gs::text), 2)
            FROM generate_series(1, 7000) AS gs;
        """)
        self.env.execute_sql("""
            CREATE TABLE payment_reconciliation_queue (
                id integer PRIMARY KEY,
                account_id integer NOT NULL,
                status text NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO payment_reconciliation_queue (id, account_id, status)
            SELECT gs, 300000 + (gs % 500),
                   CASE WHEN gs % 13 = 0 THEN 'blocked' ELSE 'ready' END
            FROM generate_series(1, 5000) AS gs;
        """)
        self.env.execute_sql("DELETE FROM settlement_audit WHERE id % 19 = 0;")
        self.env.execute_sql("DELETE FROM billing_outbox WHERE id % 29 = 0;")
        self.env.execute_sql("DELETE FROM payment_reconciliation_queue WHERE id % 31 = 0;")
        self.env.execute_sql("ANALYZE settlement_audit;")
        self.env.execute_sql("ANALYZE billing_outbox;")
        self.env.execute_sql("ANALYZE payment_reconciliation_queue;")
        self.env.execute_sql("""
            CREATE TABLE ops_replication_lag_samples (
                sampled_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                source text NOT NULL,
                lag_seconds integer NOT NULL,
                note text NOT NULL
            );
        """)
        self.env.execute_sql("""
            INSERT INTO ops_replication_lag_samples (source, lag_seconds, note)
            VALUES
                ('replica-b', 41, 'apply lag during settlement batch'),
                ('replica-b', 8, 'lag recovered before database maintenance completed'),
                ('monitor', 0, 'primary still reports old transaction age budget risk');
        """)
        # Census breadth: a frozen FX snapshot table plus two
        # read-only business tables that will carry overdue-but-safe freeze
        # ages after _seed_partial_maintenance_coverage rewinds their
        # relfrozenxid below.
        self.env.execute_sql("""
            CREATE TABLE fx_rate_snapshots (
                id integer PRIMARY KEY,
                currency_pair text NOT NULL,
                rate numeric(12,6) NOT NULL,
                sampled_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO fx_rate_snapshots (id, currency_pair, rate)
            SELECT gs, 'USD/CNY', 7.10 + (gs % 7) * 0.01
            FROM generate_series(1, 3000) AS gs;
        """)
        self.env.execute_sql("""
            CREATE TABLE ledger_audit_trail (
                id integer PRIMARY KEY,
                ledger_id integer NOT NULL,
                action text NOT NULL,
                recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO ledger_audit_trail (id, ledger_id, action)
            SELECT gs, 100000 + (gs % 400),
                   CASE WHEN gs % 9 = 0 THEN 'amend' ELSE 'append' END
            FROM generate_series(1, 4000) AS gs;
        """)
        self.env.execute_sql("""
            CREATE TABLE payment_disputes (
                id integer PRIMARY KEY,
                order_ref text NOT NULL,
                reason text NOT NULL,
                opened_at timestamptz NOT NULL DEFAULT clock_timestamp()
            );
        """)
        self.env.execute_sql("""
            INSERT INTO payment_disputes (id, order_ref, reason)
            SELECT gs, 'ORD-' || gs,
                   CASE WHEN gs % 4 = 0 THEN 'chargeback' ELSE 'inquiry' END
            FROM generate_series(1, 2500) AS gs;
        """)

    def _advance_next_xid_offline(self):
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              f"Advancing nextXID to {self.target_next_xid} with pg_resetwal...")
        self._stop_postgres()
        pgdata = self.env.deployment.pgdata
        self._docker_exec([
            "bash", "-c",
            "PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1) "
            f"&& su - postgres -c \"$PG_BIN/pg_resetwal -f -x {self.target_next_xid} {pgdata}\""
        ], timeout=60)
        self._ensure_pg_xact_segment()
        self._start_postgres()

    def _ensure_pg_xact_segment(self):
        pgdata = self.env.deployment.pgdata
        xid = int(self.target_next_xid)
        # PostgreSQL pg_xact segment size is 32 SLRU pages * 8192 bytes.
        # Each byte stores four transaction states, so one segment covers
        # 1,048,576 transaction IDs.
        script = (
            "set -e; "
            f"seg=$(printf '%04X' $(({xid} / 1048576))); "
            f"path='{pgdata}/pg_xact/'$seg; "
            "if [ ! -f \"$path\" ]; then "
            "dd if=/dev/zero of=\"$path\" bs=256k count=1 status=none; "
            "chown postgres:postgres \"$path\"; "
            "chmod 600 \"$path\"; "
            "fi"
        )
        self._docker_exec(["bash", "-c", script], timeout=30)

    def _hold_freeze_blocker(self, ready):
        import psycopg2

        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                application_name=self.blocker_app_name,
            )
            conn.autocommit = False
            self._blocker_conn = conn
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
                cur.execute(f"LOCK TABLE {self.table} IN SHARE UPDATE EXCLUSIVE MODE;")
                cur.execute(f"SELECT count(*) FROM {self.table} WHERE account_id = 100042;")
                cur.execute("SELECT pg_backend_pid();")
                self._blocker_pid = int(cur.fetchone()[0])
                ready.set()
                if self._stop_event is not None:
                    self._stop_event.wait()
            try:
                conn.rollback()
            finally:
                conn.close()
        except Exception as exc:
            self._blocker_error = exc
            print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
                  f"Blocker stopped: {exc}")
            ready.set()

    def _freeze_healthy_relations(self):
        """Freeze every public user relation except the blocked target so the
        fault presents exactly one wraparound-critical relation with healthy
        protected neighbors. pg_catalog
        relations keep their initdb-era relfrozenxid on purpose: vacuuming
        system catalogs on a pg_resetwal-punched cluster demonstrably rewrites
        unrelated pg_class rows, and their ancient ages are the realistic
        cluster-horizon signature of a wraparound incident anyway."""
        payload = _json_object(
            self.env.execute_sql(
                "SELECT quote_ident(n.nspname) || '.' || quote_ident(c.relname) "
                "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE c.relkind IN ('r', 'p', 'm') "
                "AND n.nspname = 'public' "
                f"AND c.relname <> '{self.table}';"
            ),
            "list healthy relations to freeze",
        )
        for (relation,) in payload["result"]:
            self.env.execute_sql(f"VACUUM (FREEZE) {relation};")
        self.env.execute_sql("CHECKPOINT;")
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              f"Froze {len(payload['result'])} healthy public relations; "
              f"'{self.table}' stays at the wraparound horizon "
              f"(target_age_after_freeze={self._target_table_age()}).")

    def _seed_partial_maintenance_coverage(self):
        """A real cluster mixes freshly
        frozen relations with tables that are overdue for regular freeze
        maintenance but nowhere near the wraparound horizon. Rewinding
        relfrozenxid on two read-only business tables shapes that partially
        maintained census; only the blocked ledger stays wraparound-critical.
        The catalog rewind is injector-internal fault-image shaping of the
        same class as pg_resetwal; the resulting census rows are exactly what
        the Agent sees."""
        for table, relfrozenxid in (
            ("ledger_audit_trail", 499936000),
            ("payment_disputes", 499761000),
        ):
            self.env.execute_sql(
                f"UPDATE pg_class SET relfrozenxid = '{relfrozenxid}'::xid "
                f"WHERE oid = 'public.{table}'::regclass;"
            )
        self.env.execute_sql("CHECKPOINT;")
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              "Seeded partial maintenance coverage: ledger_audit_trail and "
              "payment_disputes carry overdue-but-safe freeze ages.")

    def _control_state(self, conn):
        """Autocommit read of the batch control row's public lifecycle state;
        a missing row means the batch was removed from the runtime surface
        (the provisioner may re-insert it from its template)."""
        if not self.batch_control_table:
            return "running"
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT state FROM {self.batch_control_table} "
                f"WHERE job_name = '{self.batch_control_job}';"
            )
            row = cur.fetchone()
        return None if row is None else str(row[0])

    def _park_while_stopped(self, conn):
        """Desired-state convergence: drain into standby for
        every non-running control state (paused observation hold, cancelled or
        removed row pending re-provisioning, pending/completed windows), then
        re-arm only when the row reads 'running' again — either because the
        recon sweeper resumed a paused hold or because the
        batch_control_provisioner restored a cancelled/missing row from its
        enabled template. The standby polls under the supervisor identity so
        parked workers never masquerade as live worker sessions."""
        try:
            conn.close()
        except Exception:
            pass
        while self._stop_event is not None and not self._stop_event.is_set():
            self._stop_event.wait(self._worker_reconnect_backoff_seconds)
            if self._stop_event is None or self._stop_event.is_set():
                return
            probe = None
            try:
                probe = self._connect_noise(self._worker_supervisor_app_name)
                state = self._control_state(probe)
            except Exception:
                return
            finally:
                if probe is not None and not probe.closed:
                    try:
                        probe.close()
                    except Exception:
                        pass
            if state == "running":
                return

    def _run_replay_worker(self, ready, phase_delay_seconds):
        """One settlement replay batch worker (desired-state
        model). Workers hold SHARE on the target table in staggered shifts so
        maintenance cannot progress while the batch runs; a terminated worker
        is re-spawned by its supervisor unless the batch was stopped through
        the business control table. 'running' is the only state that runs a
        hold cycle; every other state (paused observation hold, cancelled or
        removed row, pending/completed windows) drains the worker into the
        supervisor standby park. The control row is managed by
        the upstream batch_control_provisioner, which restores cancelled or
        missing rows from their enabled ops_batch_control_template row, so a
        runtime-only cancellation reverts and the parked workers re-arm; only
        retiring the template layer (or stopping the provisioner) together
        with the runtime stop keeps the batch down for good."""
        import time

        conn = None
        try:
            conn = self._connect_noise(self.blocker_app_name)
        except Exception as exc:
            self._blocker_error = exc
            ready.set()
            return
        self._worker_conns.append(conn)
        announced = False
        if phase_delay_seconds and self._stop_event is not None:
            self._stop_event.wait(phase_delay_seconds)

        def _park_and_reconnect():
            """Drain into the supervisor standby, then return a live
            connection for the next state check (or None while shutting
            down)."""
            self._park_while_stopped(conn)
            if self._stop_event is None or self._stop_event.is_set():
                return None
            try:
                fresh = self._connect_noise(self.blocker_app_name)
            except Exception:
                return None
            self._worker_conns.append(fresh)
            return fresh

        try:
            while self._stop_event is not None and not self._stop_event.is_set():
                try:
                    state = self._control_state(conn)
                    if state != "running":
                        conn = _park_and_reconnect()
                        if conn is None:
                            break
                        continue
                    conn.autocommit = False
                    with conn.cursor() as cur:
                        cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
                        cur.execute(f"LOCK TABLE {self.table} IN SHARE MODE;")
                        cur.execute(f"SELECT count(*) FROM {self.table} WHERE account_id = 100042;")
                        if not announced:
                            cur.execute("SELECT pg_backend_pid();")
                            self._blocker_pid = int(cur.fetchone()[0])
                            announced = True
                            ready.set()
                    if self._stop_event is not None:
                        self._stop_event.wait(self._worker_hold_seconds)
                    conn.rollback()
                    state = self._control_state(conn)
                    if state != "running":
                        conn = _park_and_reconnect()
                        if conn is None:
                            break
                        continue
                    if self._stop_event is not None:
                        self._stop_event.wait(self._worker_gap_seconds)
                except Exception:
                    if self._stop_event is None or self._stop_event.is_set():
                        break
                    # The session was terminated out-of-band (operations incident);
                    # the batch supervisor reconnects the worker after a short
                    # backoff, so killing sessions cannot stop the replay.
                    try:
                        conn.close()
                    except Exception:
                        pass
                    if self._stop_event is not None:
                        self._stop_event.wait(self._worker_reconnect_backoff_seconds)
                    if self._stop_event is None or self._stop_event.is_set():
                        break
                    try:
                        conn = self._connect_noise(self.blocker_app_name)
                        self._worker_conns.append(conn)
                    except Exception:
                        break
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _start_retry_sweep(self):
        """Benign retry dedup sweep: a real, running neighbor
        job on the shared control surface. It appends duplicate-order-ref
        failure rows to the same commit-failure stream, so failure absence
        can never double as recovery evidence."""
        import threading

        self._sweep_thread = threading.Thread(
            target=self._run_retry_sweep,
            daemon=True,
        )
        self._sweep_thread.start()

    def _run_retry_sweep(self):
        import time

        import psycopg2

        while self._stop_event is not None and not self._stop_event.is_set():
            conn = None
            try:
                conn = self._connect_noise(self._retry_sweep_app_name)
                self._sweep_conn = conn
                conn.autocommit = True
                while self._stop_event is not None and not self._stop_event.is_set():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"SELECT state FROM {self.batch_control_table} "
                            f"WHERE job_name = '{self._retry_sweep_job_name}';"
                        )
                        row = cur.fetchone()
                        if row is None or str(row[0]) != "running":
                            return
                        cur.execute(
                            f"INSERT INTO {self.commit_failure_table} "
                            "(order_ref, error) VALUES (%s, %s);",
                            (
                                f"ORD-RETRY-{int(time.time() * 1000)}",
                                "duplicate order_ref from retry sweep, skipped",
                            ),
                        )
                    self._stop_event.wait(self._retry_sweep_interval_seconds)
                return
            except Exception:
                if self._stop_event is None or self._stop_event.is_set():
                    return
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self._stop_event.wait(self._worker_reconnect_backoff_seconds)

    def _start_recon_sweeper(self):
        """Nightly reconciliation sweeper:
        batch automation that auto-resumes paused control rows each cycle so
        settlement batches make their cutoff. Its existence and semantics are
        public — the control-table comment, its own doc row, the app_name
        session in pg_stat_activity/pg_stat_statements, and the observable
        resume effect. paused is therefore only a temporary observation hold;
        cancelled (or removing the row) is the permanent stop. Stopping the
        sweeper itself first and then pausing the batch is an accepted
        equivalent repair."""
        import threading

        self._recon_sweeper_thread = threading.Thread(
            target=self._run_recon_sweeper,
            daemon=True,
        )
        self._recon_sweeper_thread.start()

    def _run_recon_sweeper(self):
        import time

        while self._stop_event is not None and not self._stop_event.is_set():
            conn = None
            try:
                conn = self._connect_noise(self._recon_sweeper_app_name)
                conn.autocommit = True
                while self._stop_event is not None and not self._stop_event.is_set():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"SELECT state FROM {self.batch_control_table} "
                            f"WHERE job_name = '{self._recon_sweeper_job_name}';"
                        )
                        row = cur.fetchone()
                        if row is None or str(row[0]) != "running":
                            return
                        cur.execute(
                            f"UPDATE {self.batch_control_table} "
                            "SET state = 'running', state_changed_at = clock_timestamp() "
                            "WHERE state = 'paused' "
                            f"AND state_changed_at < clock_timestamp() "
                            f"- interval '{self._recon_sweeper_resume_hold_seconds} seconds' "
                            "RETURNING job_name;"
                        )
                        resumed = [str(item[0]) for item in cur.fetchall()]
                    if resumed:
                        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
                              f"nightly recon sweeper auto-resumed paused rows: {resumed}")
                    self._stop_event.wait(self._recon_sweeper_interval_seconds)
                return
            except Exception:
                if self._stop_event is None or self._stop_event.is_set():
                    return
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self._stop_event.wait(self._worker_reconnect_backoff_seconds)

    def _start_control_provisioner(self):
        """Nightly configuration-as-code provisioner:
        deterministic desired-state automation that
        replays enabled ops_batch_control_template rows into the control
        table. A control row that is missing or left cancelled is restored to
        running from its template, so a runtime-only cancellation reverts and
        the batch comes back. Everything about the mechanism is public — the
        template-table and column comments, the provisioner's own control row
        note, the per-tick RAISE LOG evidence line, the app_name session, and
        its pg_stat_statements write; only the 30s tick cadence is an
        unpublishable runtime rhythm. Retiring the template row (or cancelling
        this job's own control row) stops the restore behavior; the
        provisioner exits permanently when its own control row leaves running
        or the template table is dropped. It only restores missing/cancelled
        rows — the recon sweeper's paused-only resume scope is untouched."""
        import threading

        self._provisioner_thread = threading.Thread(
            target=self._run_control_provisioner,
            daemon=True,
        )
        self._provisioner_thread.start()

    def _run_control_provisioner(self):
        import time

        import psycopg2

        while self._stop_event is not None and not self._stop_event.is_set():
            conn = None
            try:
                conn = self._connect_noise(self._provisioner_app_name)
                conn.autocommit = True
                while self._stop_event is not None and not self._stop_event.is_set():
                    with conn.cursor() as cur:
                        # Own control row gates the automation: cancelled or
                        # removed row permanently stops provisioning.
                        cur.execute(
                            f"SELECT state FROM {self.batch_control_table} "
                            f"WHERE job_name = '{self._provisioner_job_name}';"
                        )
                        row = cur.fetchone()
                        if row is None or str(row[0]) != "running":
                            return
                        # A dropped template table removes the provisioning
                        # source: the provisioner stops permanently instead of
                        # erroring in a loop.
                        cur.execute(
                            f"SELECT to_regclass('public."
                            f"{self.batch_control_template_table}')::text;"
                        )
                        if cur.fetchone()[0] is None:
                            return
                        # Restore pass: enabled templates whose control row is
                        # missing or left cancelled come back as running.
                        cur.execute(
                            f"INSERT INTO {self.batch_control_table} "
                            "(job_name, state, state_changed_at, provisioned_from, note) "
                            f"SELECT t.job_name, 'running', clock_timestamp(), t.job_name, t.note "
                            f"FROM {self.batch_control_template_table} t "
                            "WHERE t.enabled AND NOT EXISTS ( "
                            f"SELECT 1 FROM {self.batch_control_table} c "
                            "WHERE c.job_name = t.job_name AND c.state <> 'cancelled') "
                            "ON CONFLICT (job_name) DO UPDATE SET "
                            "state = 'running', state_changed_at = clock_timestamp(), "
                            "provisioned_from = EXCLUDED.provisioned_from, "
                            "note = EXCLUDED.note "
                            "RETURNING job_name;"
                        )
                        restored = [str(item[0]) for item in cur.fetchall()]
                    restored_list = ", ".join(restored) if restored else "none"
                    with conn.cursor() as cur:
                        # One RAISE LOG evidence line per tick (single line,
                        # deterministic content derived from this pass).
                        cur.execute(
                            "DO $$ BEGIN RAISE LOG 'batch_control_provisioner tick: "
                            f"scanned enabled templates in {self.batch_control_template_table}; "
                            "restored control rows: " + restored_list + "'; END $$;"
                        )
                    if restored:
                        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
                              f"batch_control_provisioner restored control rows: {restored}")
                    self._stop_event.wait(self._provisioner_interval_seconds)
                return
            except Exception:
                if self._stop_event is None or self._stop_event.is_set():
                    return
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self._stop_event.wait(self._worker_reconnect_backoff_seconds)

    def _start_commit_writer(self):
        import threading

        self._writer_thread = threading.Thread(
            target=self._run_commit_writer,
            daemon=True,
        )
        self._writer_thread.start()
        import time

        time.sleep(1.0)
        if self._writer_error is not None:
            raise RuntimeError(
                "XID wraparound commit writer failed to start: "
                f"error={self._writer_error!r}"
            ) from self._writer_error
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] "
              "Checkout commit writer started against the payment ledger.")

    def _run_commit_writer(self):
        """Checkout order-commit traffic. Inserts into the target table, which
        the replay workers hold under SHARE, so commits fail during the
        incident and recover once the batch is paused. Failures land in the
        business failure table as agent-visible truth. Like a real payment
        service the writer survives out-of-band session termination: any
        connection-level failure breaks out to the supervisor reconnect
        instead of being swallowed as a statement-level commit failure."""
        import time

        import psycopg2

        try:
            conn = self._connect_noise("checkout_order_commit_writer")
        except Exception as exc:
            self._writer_error = exc
            return
        self._writer_conn = conn
        sequence = 0

        def _record_failure(cur, order_ref):
            cur.execute(
                f"INSERT INTO {self.commit_failure_table} "
                "(order_ref, error) VALUES (%s, %s);",
                (order_ref, "commit canceled after 3000 ms"),
            )

        def _is_statement_timeout(exc) -> bool:
            # psycopg2 maps QueryCanceled (SQLSTATE 57014, statement timeout /
            # cancel) onto OperationalError, so the statement-level failure is
            # identified by pgcode; every other OperationalError (server closed
            # the connection, admin shutdown, ...) is a connection-level event.
            return getattr(exc, "pgcode", None) == "57014"

        while self._stop_event is not None and not self._stop_event.is_set():
            try:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(
                        f"SET statement_timeout = '{self._commit_writer_statement_timeout}';"
                    )
                    while self._stop_event is not None and not self._stop_event.is_set():
                        sequence += 1
                        order_ref = (
                            f"ORD-{int(time.time() * 1000)}-{sequence:06d}"
                        )
                        try:
                            cur.execute(
                                f"INSERT INTO {self.table} (id, account_id, amount, status) "
                                "VALUES (%s, %s, %s, 'captured');",
                                (10000 + sequence, 100000 + (sequence % 400), "18.40"),
                            )
                        except Exception as exc:
                            if not _is_statement_timeout(exc):
                                # Connection killed out-of-band (operations
                                # incident): the payment service reconnects
                                # through the supervisor path below.
                                raise
                            try:
                                conn.rollback()
                            except Exception:
                                pass
                            try:
                                _record_failure(cur, order_ref)
                            except Exception as failure_exc:
                                if not _is_statement_timeout(failure_exc):
                                    raise
                            finally:
                                try:
                                    conn.rollback()
                                except Exception:
                                    pass
                        self._stop_event.wait(self._commit_writer_interval_seconds)
                        if conn.closed:
                            raise psycopg2.InterfaceError("connection closed")
                break
            except Exception:
                if self._stop_event is None or self._stop_event.is_set():
                    break
                try:
                    conn.close()
                except Exception:
                    pass
                self._stop_event.wait(self._worker_reconnect_backoff_seconds)
                if self._stop_event is None or self._stop_event.is_set():
                    break
                try:
                    conn = self._connect_noise("checkout_order_commit_writer")
                    self._writer_conn = conn
                except Exception:
                    break
        try:
            conn.close()
        except Exception:
            pass

    def _fault_observable(self) -> bool:
        age = self._target_table_age()
        blocker = self._blocker_visible()
        return age >= self.safe_age_threshold and blocker

    def _target_table_age(self) -> int:
        result = self.env.execute_sql(f"""
            SELECT age(relfrozenxid)
            FROM pg_class
            WHERE oid = '{self.table}'::regclass;
        """)
        try:
            obj = json.loads(result)
            rows = obj.get("result") or []
            return int(rows[0][0]) if rows else 0
        except Exception:
            return 0

    def _blocker_visible(self) -> bool:
        result = self.env.execute_sql(f"""
            SELECT count(*)
            FROM pg_stat_activity
            WHERE application_name = '{self.blocker_app_name}'
              AND state = 'idle in transaction';
        """)
        try:
            obj = json.loads(result)
            rows = obj.get("result") or []
            return bool(rows and int(rows[0][0]) > 0)
        except Exception:
            return False

    def _stop_postgres(self):
        result = self.env.manage_instance("stop")
        try:
            obj = json.loads(result)
            if obj.get("status") == "success":
                return
        except Exception:
            pass

    def _start_postgres(self):
        result = self.env.manage_instance("start")
        try:
            obj = json.loads(result)
            if obj.get("status") != "success":
                raise RuntimeError(result)
        except json.JSONDecodeError as exc:
            raise RuntimeError(result) from exc
        self.env.reconnect()

    def _docker_exec(self, args: list, timeout: int = 30):
        import subprocess

        container = self.env.deployment.container_name
        cmd = ["docker", "exec", container] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"docker exec failed: {' '.join(cmd)}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            )
        return result.stdout

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        return {}

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background blocker thread and connection for teardown."""
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] quiesce...")

        if self._stop_event is not None:
            self._stop_event.set()
        self._stop_runtime_noise()
        self._stop_replay_runtime(context.env)

        if self._blocker_pid:
            _require_sql_success(
                context.env.execute_sql(
                    f"SELECT pg_terminate_backend({int(self._blocker_pid)});"
                ),
                f"terminate XID-wraparound blocker {self._blocker_pid}",
            )

        if self._blocker_conn is not None:
            self._blocker_conn.close()
            self._blocker_conn = None

        if self._blocker_thread is not None:
            _join_thread(
                self._blocker_thread,
                5,
                "XID-wraparound blocker thread",
            )
            self._blocker_thread = None
        self._stop_event = None
        self._blocker_pid = None

    def _stop_runtime_noise(self):
        for thread in self._noise_threads:
            thread.join(timeout=10)
        for conn in self._noise_conns:
            if not conn.closed:
                conn.close()
        for thread in self._noise_threads:
            thread.join(timeout=1)
        self._noise_threads = []
        self._noise_conns = []

    def _stop_replay_runtime(self, env=None):
        """Stop the replay workers and the commit writer started for this
        scenario's runtime, then release their sessions and connections."""
        env = env or self.env
        for app_name in (
            self.blocker_app_name,
            self._worker_supervisor_app_name,
            "checkout_order_commit_writer",
            self._retry_sweep_app_name,
            self._recon_sweeper_app_name,
            self._provisioner_app_name,
        ):
            if env is not None:
                try:
                    env.execute_sql(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        f"WHERE application_name = '{app_name}';"
                    )
                except Exception:
                    pass
        for thread in self._worker_threads:
            thread.join(timeout=10)
        if self._writer_thread is not None:
            self._writer_thread.join(timeout=10)
        if self._recon_sweeper_thread is not None:
            self._recon_sweeper_thread.join(timeout=10)
            self._recon_sweeper_thread = None
        if self._provisioner_thread is not None:
            self._provisioner_thread.join(timeout=10)
            self._provisioner_thread = None
        for conn in self._worker_conns:
            if not conn.closed:
                try:
                    conn.close()
                except Exception:
                    pass
        if self._writer_conn is not None and not self._writer_conn.closed:
            try:
                self._writer_conn.close()
            except Exception:
                pass
        self._worker_threads = []
        self._worker_conns = []
        self._writer_thread = None
        self._writer_conn = None
        self._blocker_pid = None

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] Recovering...")
        if self._stop_event is not None:
            self._stop_event.set()
        self._stop_runtime_noise()
        self._stop_replay_runtime(env)

        if self._blocker_pid:
            termination_sql = f"SELECT pg_terminate_backend({int(self._blocker_pid)});"
        else:
            termination_sql = f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name = '{self.blocker_app_name}';
            """
        _require_sql_success(
            env.execute_sql(termination_sql),
            f"terminate XID-wraparound blocker {self.blocker_app_name}",
        )

        if self._blocker_conn is not None:
            self._blocker_conn.close()
            self._blocker_conn = None

        if self._blocker_thread is not None:
            self._blocker_thread.join(timeout=5)
            self._blocker_thread = None
        self._stop_event = None
        self._blocker_pid = None

        if self.prepared_transaction_name:
            payload = _json_object(
                env.execute_sql(
                    "SELECT gid FROM pg_prepared_xacts WHERE gid = "
                    f"'{self.prepared_transaction_name}';"
                ),
                "check forgotten transaction before recovery freeze",
            )
            if payload["result"]:
                _require_sql_success(
                    env.execute_sql(
                        f"ROLLBACK PREPARED '{self.prepared_transaction_name}';"
                    ),
                    f"roll back forgotten transaction {self.prepared_transaction_name}",
                )

        _require_sql_success(
            env.execute_sql(f"VACUUM FREEZE {self.table};"),
            f"freeze recovered XID-wraparound table {self.table}",
        )
        print("[FaultInjector:PgSystemFailureXidWraparoundInjector] Recovery complete.")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._activate_runtime()


class PgSystemFailureXidWraparoundScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_xid_wraparound'
    description = 'Simulates transaction age exhaustion with maintenance blocked by a long business transaction.'
    cases = (
        _PGSYSTEMFAILUREXIDWRAPAROUNDSCENARIO_CASE,
        _PGSYSTEMFAILUREXIDWRAPAROUNDSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureXidWraparoundCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureXidWraparoundInjector,
                config={
                    'table': case.table,
                    'target_next_xid': case.target_next_xid,
                    'safe_age_threshold': case.safe_age_threshold,
                    'blocker_app_name': case.blocker_app_name,
                    'checkout_idle_connections': case.checkout_idle_connections,
                    'retry_idle_connections': case.retry_idle_connections,
                    'monitor_noise_connections': case.monitor_noise_connections,
                    'connection_headroom': case.connection_headroom,
                    'max_connections': int(case.runtime.parameters.parameter('max_connections')),
                    'production_noise': case.production_noise,
                    'prepared_transaction_name': case.prepared_transaction_name,
                    'protected_session_name': case.protected_session_name,
                    'replay_worker_instances': case.replay_worker_instances,
                    'commit_writer_enabled': case.commit_writer_enabled,
                    'batch_control_table': case.batch_control_table,
                    'batch_control_job': case.batch_control_job,
                    'batch_control_template_table': case.batch_control_template_table,
                    'commit_failure_table': case.commit_failure_table,
                },
            ),
        )
