from dataclasses import dataclass
from typing import Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureCpuLockSpinForAdvisoryLockRetryCpuStormEvaluatorCase,
    PgSystemFailureCpuLockSpinForCheckoutRetryLockBlockerSimpleEvaluatorCase,
    PgSystemFailureCpuLockSpinForWarehouseLockRetryCpuEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


IO_SATURATION_POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True)
class NeighborChainSpec:
    """Healthy background business chain sharing the fault-chain shape.

    Same-shape but causally unrelated neighbor sessions that fill the same
    observation window of the key tools (unfiltered pg_stat_activity, lock-wait
    tree). Each chain owns its business row / advisory key and is NOT part of
    the protected-scope OP/SP contract; a targeted repair must simply never
    need to touch it.
    """

    blocker_app: str
    waiter_prefix: str
    retry_prefix: str
    lock_target: int  # warehouse row id for row-lock chains, advisory key for advisory chains
    waiter_count: int
    spinner_count: int
    claim_row: int = 0  # settlement_lock_claims claim_id (advisory chains only)
    claim_name: str = ""  # settlement window name (advisory chains only)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCpuLockSpinCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    fault_variant: str
    table: str
    row_id: int
    decoy_row_id: int
    advisory_lock_key: int
    decoy_advisory_lock_key: int
    critical_blocker_app: str
    critical_waiter_prefix: str
    retry_worker_prefix: str
    decoy_blocker_app: str
    decoy_waiter_prefix: str
    decoy_retry_worker_prefix: str
    slow_queries: tuple[str, ...]
    waiter_count: int
    spinner_count: str
    retry_batch_size: int
    min_lock_waiters: int
    decoy_waiter_count: int
    decoy_spinner_count: int
    noise_profiles: tuple[object, ...]
    neighbor_chains: tuple[NeighborChainSpec, ...] = ()

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCpuLockSpinForWarehouseLockRetryCpuScenarioCase(PgSystemFailureCpuLockSpinCase):
    pass

_PGSYSTEMFAILURECPULOCKSPINSCENARIO_CASE = PgSystemFailureCpuLockSpinForWarehouseLockRetryCpuScenarioCase(
    case_id='warehouse_lock_retry_cpu',
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "high cpu",
                    "entity": "orders-ledger-writer-17",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed high cpu"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "compute intensive sql excluded",
                    "entity": "orders-ledger-writer-17",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed compute intensive sql excluded"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "lock wait retry storm",
                    "entity": "orders-ledger-writer-17",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed lock wait retry storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "critical row lock blocker",
                    "entity": "orders-ledger-writer-17",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed critical row lock blocker"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only critical blocker",
                    "entity": "orders-ledger-writer-17",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed terminate only critical blocker"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only orders-ledger-writer-17"
            ],
            "verification": [
                "critical blocker and lock waiters are absent; CPU was rechecked"
            ]
        },
        "summary": "CPU pressure came from the critical lock retry chain, not compute-heavy SQL."
    },
    case_no=0,
    evaluator=PgSystemFailureCpuLockSpinForWarehouseLockRetryCpuEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='complex-v5',
    fault_variant='row_lock_spin',
    title='High CPU alert caused by lock-wait spin clients rather than compute-heavy queries.',
    alert='[FIRING: CRITICAL] alertname=PostgresCpuSaturationPrimary service=orders-api severity=critical. Primary PostgreSQL CPU has remained above 90% for 5 minutes. New-order transaction p95 latency is above its SLO, and application retries are increasing. Initial triage indicates database-side CPU pressure; storage I/O and memory saturation are not currently indicated. Investigate high-CPU SQL activity, recent query regressions, and workload changes affecting order-processing latency.',
    initial_state={'status': 'degraded',
 'alert': 'cpu_high',
 'table': 'warehouse',
 'visible_symptom': 'cpu_over_90_and_transaction_latency'},
    expected_target={'status': 'recovered',
 'table': 'warehouse',
 'lock_waiters': 0,
 'root_cause': 'lock_contention_spin_wait'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='warehouse',
    row_id=11,
    decoy_row_id=19,
    advisory_lock_key=0,
    decoy_advisory_lock_key=0,
    critical_blocker_app='orders-ledger-writer-17',
    critical_waiter_prefix='orders-api-worker-',
    retry_worker_prefix='orders-api-retry-',
    decoy_blocker_app='orders-ledger-batch-09',
    decoy_waiter_prefix='orders-ledger-batch-worker-',
    decoy_retry_worker_prefix='orders-ledger-batch-retry-',
    slow_queries=('UPDATE warehouse SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = 11;',),
    waiter_count=16,
    spinner_count='auto',
    retry_batch_size=3,
    min_lock_waiters=20,
    decoy_waiter_count=8,
    decoy_spinner_count=4,
    noise_profiles=(WorkloadProfile(name='orders_latency_probe',
                 sql='SELECT pg_sleep(3.2), count(*) AS pending_orders FROM warehouse WHERE w_id '
                     'IN (11, 19, 13, 23)',
                 qps=0.18,
                 tier='SLOW_NOISE',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='orders_cpu_rollup',
                 sql='SELECT sum((g % 97) * (g % 89)) AS settlement_score FROM generate_series(1, '
                     '950000) AS g',
                 qps=0.16,
                 tier='CPU_NOISE',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='orders_ledger_balance_refresh',
                 sql='SELECT (w_id % 6) AS bucket, count(*) AS n, coalesce(sum(w_ytd), 0) AS ytd '
                     'FROM warehouse GROUP BY bucket ORDER BY ytd DESC',
                 qps=0.35,
                 tier='LIGHT',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='orders_maintenance_touch_worker',
                 sql='UPDATE warehouse SET w_ytd = w_ytd + 0.01, w_updated_at = clock_timestamp() '
                     'WHERE w_id = 23',
                 qps=0.4,
                 tier='LIGHT',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='missing_orders_cache_log_noise',
                 sql='SELECT count(*) FROM orders_cache_rollup_missing;',
                 qps=0.12,
                 tier='LOG_NOISE',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='orders_secondary_latency_probe',
                 sql='SELECT pg_sleep(1.8), max(w_updated_at) FROM warehouse WHERE w_id BETWEEN 9 '
                     'AND 21',
                 qps=0.14,
                 tier='SLOW_NOISE',
                 commit=False,
                 application_name=None),
 WorkloadProfile(name='orders_retry_hotrow_probe_w11',
                 sql='UPDATE warehouse SET w_ytd = w_ytd + 0.02, w_updated_at = clock_timestamp() '
                     'WHERE w_id = 11',
                 qps=0.22,
                 tier='LOCK_NOISE',
                 commit=False,
                 application_name='orders-api-batch-retry-11'),
 WorkloadProfile(name='orders_retry_hotrow_probe_w19',
                 sql='UPDATE warehouse SET w_ytd = w_ytd + 0.02, w_updated_at = clock_timestamp() '
                     'WHERE w_id = 19',
                 qps=0.22,
                 tier='LOCK_NOISE',
                 commit=False,
                 application_name='orders-api-batch-retry-19'),
 WorkloadProfile(name='orders_inventory_reconciliation_touch',
                 sql='UPDATE warehouse SET w_ytd = w_ytd + 0.01, w_updated_at = clock_timestamp() '
                     'WHERE w_id = 13',
                 qps=0.26,
                 tier='LIGHT',
                 commit=False,
                 application_name='orders-ledger-writer-13'),
 WorkloadProfile(name='orders_settlement_reconciliation_touch',
                 sql='UPDATE warehouse SET w_ytd = w_ytd + 0.01, w_updated_at = clock_timestamp() '
                     'WHERE w_id = 23',
                 qps=0.26,
                 tier='LIGHT',
                 commit=False,
                 application_name='orders-ledger-writer-23')),
    # This Case omits the healthy background chains
    # (returns-credit-batch-06, pricing-recalc-batch-11) so the scenario keeps
    # an easy/hard contrast across its Cases; the
    # checkout and advisory Cases keep theirs. `neighbor_chains`
    # falls back to the empty default (pure injection-side noise, evaluator
    # contract untouched).
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.445,
        reference_run_ids=(
            "reference-260__pg_system_failure_cpu_lock_spin__"
            "warehouse_lock_retry_cpu__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCpuLockSpinForCheckoutRetryLockBlockerSimpleScenarioCase(PgSystemFailureCpuLockSpinCase):
    pass

_PGSYSTEMFAILURECPULOCKSPINSCENARIO_CHECKOUT_RETRY_CASE = PgSystemFailureCpuLockSpinForCheckoutRetryLockBlockerSimpleScenarioCase(
    case_id='checkout_retry_lock_blocker_simple',
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "high cpu",
                    "entity": "checkout-ledger-writer-03",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed high cpu"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "compute intensive sql excluded",
                    "entity": "checkout-ledger-writer-03",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed compute intensive sql excluded"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "lock wait retry storm",
                    "entity": "checkout-ledger-writer-03",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed lock wait retry storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "critical row lock blocker",
                    "entity": "checkout-ledger-writer-03",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed critical row lock blocker"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only critical blocker",
                    "entity": "checkout-ledger-writer-03",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed terminate only critical blocker"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only checkout-ledger-writer-03"
            ],
            "verification": [
                "critical blocker and lock waiters are absent; CPU was rechecked"
            ]
        },
        "summary": "CPU pressure came from the critical lock retry chain, not compute-heavy SQL."
    },
    case_no=1,
    evaluator=PgSystemFailureCpuLockSpinForCheckoutRetryLockBlockerSimpleEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='simple-retry-lock',
    fault_variant='row_lock_spin',
    title='High CPU alert caused by checkout retry loops waiting on one locked warehouse row.',
    alert='[FIRING: CRITICAL] alertname=PostgresCpuSaturationPrimary service=checkout-api severity=critical. Primary PostgreSQL CPU has stayed above 90% while checkout write latency and retry counts rose. Initial dashboards show CPU pressure, with no clear storage or memory saturation. Diagnose the cause of the CPU and write-latency spike, and restore checkout writes safely.',
    initial_state={'status': 'degraded',
 'alert': 'cpu_high',
 'table': 'warehouse',
 'visible_symptom': 'cpu_high_with_checkout_retry_latency'},
    expected_target={'status': 'recovered',
 'table': 'warehouse',
 'lock_waiters': 0,
 'root_cause': 'checkout_retry_spin_from_row_lock'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='warehouse',
    row_id=7,
    decoy_row_id=29,
    advisory_lock_key=0,
    decoy_advisory_lock_key=0,
    critical_blocker_app='checkout-ledger-writer-03',
    critical_waiter_prefix='checkout-api-lockwait-',
    retry_worker_prefix='checkout-api-retry-loop-',
    decoy_blocker_app='inventory-recount-batch-02',
    decoy_waiter_prefix='inventory-recount-batch-worker-',
    decoy_retry_worker_prefix='inventory-recount-batch-retry-',
    slow_queries=('UPDATE warehouse SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = 7;',),
    waiter_count=6,
    spinner_count=8,
    retry_batch_size=2,
    min_lock_waiters=6,
    decoy_waiter_count=3,
    decoy_spinner_count=2,
    noise_profiles=(WorkloadProfile(name='checkout_cpu_rollup',
                 sql='SELECT sum((g % 43) * (g % 37)) FROM generate_series(1, 250000) AS g',
                 qps=0.10,
                 tier='CPU_NOISE',
                 commit=False,
                 application_name='checkout-batch-rollup'),
 WorkloadProfile(name='checkout_warehouse_read_probe',
                 sql='SELECT count(*), coalesce(sum(w_ytd), 0) FROM warehouse WHERE w_id BETWEEN 1 AND 16',
                 qps=0.25,
                 tier='LIGHT',
                 commit=False,
                 application_name='checkout-read-probe')),
    # Healthy background chains: payment settlement and fraud review are
    # independent consumers of the same warehouse dimension table outside the
    # checkout-api alert scope; each runs its own row-scoped batch window.
    neighbor_chains=(
        NeighborChainSpec(
            blocker_app='payment-settlement-batch-08',
            waiter_prefix='payment-settlement-worker-',
            retry_prefix='payment-settlement-retry-',
            lock_target=21,
            waiter_count=5,
            spinner_count=2,
        ),
        NeighborChainSpec(
            blocker_app='fraud-review-batch-03',
            waiter_prefix='fraud-review-worker-',
            retry_prefix='fraud-review-retry-',
            lock_target=15,
            waiter_count=4,
            spinner_count=2,
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.578,
        reference_run_ids=(
            "reference-261__pg_system_failure_cpu_lock_spin__"
            "checkout_retry_lock_blocker_simple__mock__r001",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureCpuLockSpinForAdvisoryLockRetryCpuStormScenarioCase(PgSystemFailureCpuLockSpinCase):
    pass

_PGSYSTEMFAILURECPULOCKSPINSCENARIO_ADVISORY_LOCK_CASE = PgSystemFailureCpuLockSpinForAdvisoryLockRetryCpuStormScenarioCase(
    case_id='advisory_lock_retry_cpu_storm',
    runtime=PostgresCaseRuntime(resources=IO_SATURATION_POSTGRES_RESOURCES),
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "high cpu",
                    "entity": "settlement-advisory-holder-01",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed high cpu"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "advisory lock retry storm",
                    "entity": "settlement-advisory-holder-01",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed advisory lock retry storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "leaked settlement advisory lock",
                    "entity": "settlement-advisory-holder-01",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed leaked settlement advisory lock"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "critical advisory lock key",
                    "entity": "settlement-advisory-holder-01",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed critical advisory lock key"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only settlement advisory holder",
                    "entity": "settlement-advisory-holder-01",
                    "evidence": [
                        "pg_stat_activity and pg_locks confirmed terminate only settlement advisory holder"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "terminated only settlement-advisory-holder-01"
            ],
            "verification": [
                "critical blocker and lock waiters are absent; CPU was rechecked"
            ]
        },
        "summary": "CPU pressure came from the critical lock retry chain, not compute-heavy SQL."
    },
    case_no=2,
    evaluator=PgSystemFailureCpuLockSpinForAdvisoryLockRetryCpuStormEvaluatorCase,
    base_image_name='aiopsbench-pg-default:latest',
    workload_tag='advisory-lock-retry',
    fault_variant='advisory_lock_spin',
    title='High CPU alert caused by workers retrying a leaked PostgreSQL advisory lock.',
    alert='[FIRING: CRITICAL] alertname=PostgresCpuSaturationPrimary service=settlement-api severity=critical. Primary PostgreSQL CPU has stayed above 90% while settlement close jobs keep retrying without progress and checkout confirmation latency rose. Initial dashboards do not show storage or memory saturation. Diagnose the cause of the CPU saturation and the stalled settlement progress, then restore settlement jobs without restarting PostgreSQL.',
    initial_state={'status': 'degraded',
 'alert': 'cpu_high',
 'table': 'settlement_lock_claims',
 'visible_symptom': 'cpu_high_with_settlement_retry_latency'},
    expected_target={'status': 'recovered',
 'table': 'settlement_lock_claims',
 'lock_waiters': 0,
 'root_cause': 'leaked_advisory_lock_retry_spin'},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table='settlement_lock_claims',
    row_id=1,
    decoy_row_id=2,
    advisory_lock_key=7701701,
    decoy_advisory_lock_key=7701702,
    critical_blocker_app='settlement-close-coordinator-01',
    critical_waiter_prefix='settlement-close-worker-',
    retry_worker_prefix='settlement-close-retry-',
    decoy_blocker_app='settlement-history-archiver-02',
    decoy_waiter_prefix='settlement-archiver-worker-',
    decoy_retry_worker_prefix='settlement-archiver-retry-',
    slow_queries=('SELECT pg_advisory_lock(7701701);',),
    waiter_count=5,
    spinner_count=6,
    retry_batch_size=2,
    min_lock_waiters=5,
    decoy_waiter_count=2,
    decoy_spinner_count=1,
    noise_profiles=(WorkloadProfile(name='settlement_cpu_rollup',
                 sql='SELECT sum((g % 31) * (g % 29)) FROM generate_series(1, 220000) AS g',
                 qps=0.10,
                 tier='CPU_NOISE',
                 commit=False,
                 application_name='settlement-batch-rollup'),),
    # Healthy background chains: the settlement service runs several
    # advisory-key-scoped internal windows at once (close, history archive,
    # fee batch, reconciliation); each window owns its advisory key and its
    # settlement_lock_claims claim row. Normal windows, not part of the
    # incident and not in the protected-scope contract.
    neighbor_chains=(
        NeighborChainSpec(
            blocker_app='settlement-fee-batch-04',
            waiter_prefix='settlement-fee-worker-',
            retry_prefix='settlement-fee-retry-',
            lock_target=7701703,
            waiter_count=4,
            spinner_count=2,
            claim_row=3,
            claim_name='settlement_fee_window',
        ),
        NeighborChainSpec(
            blocker_app='settlement-recon-batch-06',
            waiter_prefix='settlement-recon-worker-',
            retry_prefix='settlement-recon-retry-',
            lock_target=7701705,
            waiter_count=4,
            spinner_count=2,
            claim_row=4,
            claim_name='settlement_recon_window',
        ),
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.577,
        reference_run_ids=(
            "reference-262__pg_system_failure_cpu_lock_spin__"
            "advisory_lock_retry_cpu_storm__mock__r001",
        ),
    ),
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

def _pg_cpu_lock_spin_worker(
    dsn: dict,
    table: str,
    row_id: int,
    stop_event,
    worker_id: int,
    retry_batch_size: int,
    application_prefix: str = "order_api_retry_worker_",
):
    import time
    import psycopg2

    # Keep the CPU pressure tied to the lock pathology itself. Each worker
    # repeatedly starts a tiny transaction, waits briefly for the hot row lock,
    # rolls back on timeout, and retries immediately.
    retry_batch_size = max(1, int(retry_batch_size))

    conn = None
    try:
        conn = psycopg2.connect(**dsn)
        conn.autocommit = False
        with conn.cursor() as cur:
            app_name = f"{application_prefix}{worker_id}"
            cur.execute("SET application_name = %s;", (app_name,))
            cur.execute("SET log_min_messages = 'fatal';")
            cur.execute("SET log_min_error_statement = 'panic';")
        conn.commit()
        while not stop_event.is_set():
            for _ in range(retry_batch_size):
                if stop_event.is_set():
                    break
                try:
                    with conn.cursor() as cur:
                        cur.execute("SET LOCAL lock_timeout = '2ms';")
                        cur.execute(
                            f"UPDATE {table} SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = %s;",
                            (row_id,),
                        )
                    conn.rollback()
                    return
                except Exception:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
            time.sleep(0.001)
    except Exception as exc:
        print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Spinner {worker_id} stopped: {exc}")
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _pg_advisory_lock_spin_worker(
    dsn: dict,
    lock_key: int,
    stop_event,
    worker_id: int,
    retry_batch_size: int,
    application_prefix: str,
    bookkeeping_table: str = "settlement_lock_claims",
    bookkeeping_row: int = 1,
):
    import time
    import psycopg2

    retry_batch_size = max(1, int(retry_batch_size))
    conn = None
    try:
        conn = psycopg2.connect(**dsn)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SET application_name = %s;", (f"{application_prefix}{worker_id:02d}",))
            cur.execute("SET log_min_messages = 'fatal';")
            cur.execute("SET log_min_error_statement = 'panic';")
        conn.commit()
        while not stop_event.is_set():
            for _ in range(retry_batch_size):
                if stop_event.is_set():
                    break
                try:
                    # 每次重试尝试是一个独立事务：抢锁失败后写入重试簿记并做速率
                    # 检查，最后整体回滚——CPU 压力来自数据库内部的重试负载，
                    # 与告警表象一致。
                    with conn.cursor() as cur:
                        cur.execute("SELECT pg_try_advisory_lock(%s);", (lock_key,))
                        acquired = bool(cur.fetchone()[0])
                        if acquired:
                            conn.rollback()
                            cur.execute("SELECT pg_advisory_unlock(%s);", (lock_key,))
                            return
                        cur.execute(
                            f"UPDATE {bookkeeping_table} "
                            "SET retry_count = retry_count + 1, "
                            "last_attempt_at = clock_timestamp() WHERE claim_id = %s;",
                            (bookkeeping_row,),
                        )
                        cur.execute(
                            f"SELECT count(*) FROM {bookkeeping_table} "
                            "WHERE last_attempt_at > clock_timestamp() - interval '2 seconds';"
                        )
                        cur.fetchone()
                    conn.rollback()
                except Exception:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
            time.sleep(0.001)
    except Exception as exc:
        print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Advisory spinner {worker_id} stopped: {exc}")
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


class PgSystemFailureCpuLockSpinInjector(BaseFaultInjector):
    """
    Simulate a high-CPU alert where the real bottleneck is lock
    contention on a compact TPC-C warehouse table.
    """
    def __init__(self):
        self.env = None
        self.fault_variant = "row_lock_spin"
        self.table = "warehouse"
        self.row_id = 11
        self.decoy_row_id = 19
        self.advisory_lock_key = 0
        self.decoy_advisory_lock_key = 0
        self.critical_blocker_app = "orders-ledger-writer-17"
        self.critical_waiter_prefix = "orders-api-worker-"
        self.retry_worker_prefix = "orders-api-retry-"
        self.decoy_blocker_app = "orders-ledger-maint-09"
        self.decoy_waiter_prefix = "orders-maint-worker-"
        self.decoy_retry_worker_prefix = "orders-maint-retry-"
        self.noise_profiles = []
        self.neighbor_chains = ()
        self._stop_event = None
        self._spin_stop_event = None
        self._decoy_stop_event = None
        self._blocker_thread = None
        self._decoy_blocker_thread = None
        self._neighbor_blocker_threads = []
        self._waiter_threads = []
        self._decoy_waiter_threads = []
        self._neighbor_waiter_threads = []
        self._spin_processes = []
        self._connections = []
        self._noise_runner = None

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._start_runtime()

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install_persistent_state()
        self._start_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        import os

        self.env = env
        self.fault_variant = str(config['fault_variant'])
        self.table = _validate_sql_identifier(config['table'], "table")
        self.row_id = int(config['row_id'])
        self.decoy_row_id = int(config['decoy_row_id'])
        self.advisory_lock_key = int(config['advisory_lock_key'])
        self.decoy_advisory_lock_key = int(config['decoy_advisory_lock_key'])
        self.critical_blocker_app = config['critical_blocker_app']
        self.critical_waiter_prefix = config['critical_waiter_prefix']
        self.retry_worker_prefix = config['retry_worker_prefix']
        self.decoy_blocker_app = config['decoy_blocker_app']
        self.decoy_waiter_prefix = config['decoy_waiter_prefix']
        self.decoy_retry_worker_prefix = config['decoy_retry_worker_prefix']
        self.noise_profiles = list(config['noise_profiles'])
        self.neighbor_chains = tuple(config.get('neighbor_chains') or ())
        self.waiter_count = int(config['waiter_count'])
        configured_spinner_count = config['spinner_count']
        if configured_spinner_count == "auto":
            cpu_count = os.cpu_count()
            if cpu_count is None:
                raise RuntimeError("Cannot resolve CPU count for automatic lock-spin worker count")
            self.spinner_count = max(4, min(cpu_count + 1, 10))
        else:
            self.spinner_count = int(configured_spinner_count)
        self.retry_batch_size = int(config['retry_batch_size'])
        self.decoy_waiter_count = int(config['decoy_waiter_count'])
        self.decoy_spinner_count = int(config['decoy_spinner_count'])
        self.min_lock_waiters = int(config['min_lock_waiters'])

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Preparing TPC-C table {self.table}...")
        if self.fault_variant == "advisory_lock_spin":
            chain_rows = "".join(
                f",\n                        ({chain.claim_row}, '{chain.claim_name}', 0)"
                for chain in self.neighbor_chains
                if chain.claim_row
            )
            _require_sql_success(
                self.env.execute_sql(
                    f"""
                    CREATE TABLE {self.table} (
                        claim_id integer PRIMARY KEY,
                        lock_name text NOT NULL,
                        last_attempt_at timestamptz NOT NULL DEFAULT now(),
                        retry_count integer NOT NULL DEFAULT 0
                    );
                    INSERT INTO {self.table} (claim_id, lock_name, retry_count)
                    VALUES
                        ({self.row_id}, 'settlement_close_window', 0),
                        ({self.decoy_row_id}, 'settlement_history_archive_window', 0){chain_rows};
                    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
                    ANALYZE {self.table};
                    """
                ),
                "install advisory CPU lock-spin persistent state",
            )
            return
        _require_sql_success(
            self.env.execute_sql(
                f"""
                CREATE TABLE {self.table} (
                    w_id integer PRIMARY KEY,
                    w_name text NOT NULL DEFAULT 'W1',
                    w_ytd numeric(12,2) NOT NULL DEFAULT 0,
                    w_updated_at timestamp NOT NULL DEFAULT now()
                );
                INSERT INTO {self.table} (w_id, w_name, w_ytd)
                SELECT g, 'W' || g::text, 0
                FROM generate_series(1, 32) AS g;
                CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
                ANALYZE {self.table};
                """
            ),
            "install CPU lock-spin persistent state",
        )

    def _verify_persistent_state(self) -> None:
        key_column = "claim_id" if self.fault_variant == "advisory_lock_spin" else "w_id"
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT count(*) FROM {self.table} "
                f"WHERE {key_column} IN ({self.row_id}, {self.decoy_row_id});"
            ),
            "verify CPU lock-spin fault image rows",
        )
        if int(payload["result"][0][0]) != 2:
            raise RuntimeError(
                f"CPU lock-spin fault image is missing hotspot rows: table={self.table}, "
                f"row_ids=({self.row_id}, {self.decoy_row_id}), count={payload['result'][0][0]}"
            )

    def _start_runtime(self) -> None:
        import multiprocessing
        import threading
        import time

        self._terminate_leftover_sessions()

        self._stop_event = threading.Event()
        self._decoy_stop_event = threading.Event()
        self._spin_stop_event = multiprocessing.Event()
        self._waiter_threads = []
        self._decoy_waiter_threads = []
        self._neighbor_blocker_threads = []
        self._neighbor_waiter_threads = []
        self._spin_processes = []
        self._connections = []

        if self.fault_variant == "advisory_lock_spin":
            dsn = {
                "host": self.env.host,
                "port": self.env.port,
                "user": self.env.user,
                "password": self.env.password,
                "dbname": self.env.dbname,
                "connect_timeout": 3,
            }
            self._start_advisory_runtime(dsn)
            return

        self._blocker_thread = threading.Thread(target=self._hold_row_lock, daemon=True)
        self._blocker_thread.start()
        time.sleep(1.0)

        for idx in range(self.waiter_count):
            thread = threading.Thread(target=self._blocking_waiter, args=(idx,), daemon=True)
            thread.start()
            self._waiter_threads.append(thread)

        self._decoy_blocker_thread = threading.Thread(target=self._hold_decoy_lock, daemon=True)
        self._decoy_blocker_thread.start()
        time.sleep(0.4)
        for idx in range(self.decoy_waiter_count):
            thread = threading.Thread(target=self._blocking_decoy_waiter, args=(idx,), daemon=True)
            thread.start()
            self._decoy_waiter_threads.append(thread)
        self._wait_for_lock_waiters(self.min_lock_waiters)

        dsn = {
            "host": self.env.host,
            "port": self.env.port,
            "user": self.env.user,
            "password": self.env.password,
            "dbname": self.env.dbname,
            "connect_timeout": 3,
        }
        for idx in range(self.spinner_count):
            proc = multiprocessing.Process(
                target=_pg_cpu_lock_spin_worker,
                args=(
                    dsn,
                    self.table,
                    self.row_id,
                    self._spin_stop_event,
                    idx,
                    self.retry_batch_size,
                    self.retry_worker_prefix,
                ),
                daemon=True,
            )
            proc.start()
            self._spin_processes.append(proc)
        for idx in range(self.decoy_spinner_count):
            proc = multiprocessing.Process(
                target=_pg_cpu_lock_spin_worker,
                args=(
                    dsn,
                    self.table,
                    self.decoy_row_id,
                    self._spin_stop_event,
                    idx,
                    max(1, self.retry_batch_size - 1),
                    self.decoy_retry_worker_prefix,
                ),
                daemon=True,
            )
            proc.start()
            self._spin_processes.append(proc)

        self._start_row_neighbor_chains(dsn)
        self._start_noise_runner()
        time.sleep(2.0)
        print(
            f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Lock blocker, "
            f"{self.waiter_count} waiters, {self.decoy_waiter_count} decoy waiters, "
            f"{self.spinner_count} critical spin clients, {self.decoy_spinner_count} decoy spin clients, "
            f"{len(self.neighbor_chains)} healthy neighbor chains, "
            f">={self.min_lock_waiters} visible lock waiters, "
            "and workload noise are active."
        )

    def _start_advisory_runtime(self, dsn: dict) -> None:
        import multiprocessing
        import threading
        import time

        self._blocker_thread = threading.Thread(
            target=self._hold_advisory_lock,
            args=(self.advisory_lock_key, self.critical_blocker_app, self._stop_event),
            daemon=True,
        )
        self._blocker_thread.start()
        time.sleep(0.8)

        for idx in range(self.waiter_count):
            thread = threading.Thread(
                target=self._blocking_advisory_waiter,
                args=(idx, self.advisory_lock_key, self.critical_waiter_prefix),
                daemon=True,
            )
            thread.start()
            self._waiter_threads.append(thread)

        self._decoy_blocker_thread = threading.Thread(
            target=self._hold_advisory_lock,
            args=(self.decoy_advisory_lock_key, self.decoy_blocker_app, self._decoy_stop_event),
            daemon=True,
        )
        self._decoy_blocker_thread.start()
        time.sleep(0.4)
        for idx in range(self.decoy_waiter_count):
            thread = threading.Thread(
                target=self._blocking_advisory_waiter,
                args=(idx, self.decoy_advisory_lock_key, self.decoy_waiter_prefix),
                daemon=True,
            )
            thread.start()
            self._decoy_waiter_threads.append(thread)
        self._start_advisory_neighbor_holder_threads()
        self._wait_for_lock_waiters(self.min_lock_waiters)

        for idx in range(self.spinner_count):
            proc = multiprocessing.Process(
                target=_pg_advisory_lock_spin_worker,
                args=(
                    dsn,
                    self.advisory_lock_key,
                    self._spin_stop_event,
                    idx,
                    self.retry_batch_size,
                    self.retry_worker_prefix,
                    self.table,
                    self.row_id,
                ),
                daemon=True,
            )
            proc.start()
            self._spin_processes.append(proc)
        for idx in range(self.decoy_spinner_count):
            proc = multiprocessing.Process(
                target=_pg_advisory_lock_spin_worker,
                args=(
                    dsn,
                    self.decoy_advisory_lock_key,
                    self._spin_stop_event,
                    idx,
                    max(1, self.retry_batch_size - 1),
                    self.decoy_retry_worker_prefix,
                    self.table,
                    self.decoy_row_id,
                ),
                daemon=True,
            )
            proc.start()
            self._spin_processes.append(proc)

        self._start_advisory_neighbor_spinners(dsn)
        self._start_noise_runner()
        time.sleep(2.0)
        print(
            f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Advisory lock holder, "
            f"{self.waiter_count} waiters, {self.decoy_waiter_count} decoy waiters, "
            f"{self.spinner_count} critical spin clients, {self.decoy_spinner_count} decoy spin clients, "
            f"{len(self.neighbor_chains)} healthy neighbor chains, "
            "and workload noise are active."
        )

    def _start_row_neighbor_chains(self, dsn: dict) -> None:
        import multiprocessing
        import threading
        import time

        for chain in self.neighbor_chains:
            blocker_thread = threading.Thread(
                target=self._hold_row_lock_on,
                args=(chain.blocker_app, chain.lock_target, self._decoy_stop_event),
                daemon=True,
            )
            blocker_thread.start()
            self._neighbor_blocker_threads.append(blocker_thread)
            time.sleep(0.4)
            for idx in range(chain.waiter_count):
                thread = threading.Thread(
                    target=self._blocking_waiter_on,
                    args=(chain.waiter_prefix, chain.lock_target, idx),
                    daemon=True,
                )
                thread.start()
                self._neighbor_waiter_threads.append(thread)
            for idx in range(chain.spinner_count):
                proc = multiprocessing.Process(
                    target=_pg_cpu_lock_spin_worker,
                    args=(
                        dsn,
                        self.table,
                        chain.lock_target,
                        self._spin_stop_event,
                        idx,
                        max(1, self.retry_batch_size - 1),
                        chain.retry_prefix,
                    ),
                    daemon=True,
                )
                proc.start()
                self._spin_processes.append(proc)

    def _start_advisory_neighbor_holder_threads(self) -> None:
        import threading
        import time

        for chain in self.neighbor_chains:
            blocker_thread = threading.Thread(
                target=self._hold_advisory_lock,
                args=(chain.lock_target, chain.blocker_app, self._decoy_stop_event),
                daemon=True,
            )
            blocker_thread.start()
            self._neighbor_blocker_threads.append(blocker_thread)
            time.sleep(0.4)
            for idx in range(chain.waiter_count):
                thread = threading.Thread(
                    target=self._blocking_advisory_waiter,
                    args=(idx, chain.lock_target, chain.waiter_prefix),
                    daemon=True,
                )
                thread.start()
                self._neighbor_waiter_threads.append(thread)

    def _start_advisory_neighbor_spinners(self, dsn: dict) -> None:
        import multiprocessing

        for chain in self.neighbor_chains:
            for idx in range(chain.spinner_count):
                proc = multiprocessing.Process(
                    target=_pg_advisory_lock_spin_worker,
                    args=(
                        dsn,
                        chain.lock_target,
                        self._spin_stop_event,
                        idx,
                        max(1, self.retry_batch_size - 1),
                        chain.retry_prefix,
                        self.table,
                        chain.claim_row or self.decoy_row_id,
                    ),
                    daemon=True,
                )
                proc.start()
                self._spin_processes.append(proc)

    def _connect(self, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=self.env.host,
            port=self.env.port,
            user=self.env.user,
            password=self.env.password,
            dbname=self.env.dbname,
            connect_timeout=3,
            application_name=application_name,
        )
        conn.autocommit = False
        self._connections.append(conn)
        return conn

    def _hold_row_lock(self):
        self._hold_row_lock_on(self.critical_blocker_app, self.row_id, self._stop_event)

    def _hold_row_lock_on(self, application_name: str, row_id: int, stop_event):
        conn = None
        try:
            conn = self._connect(application_name)
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.table} SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = %s;",
                    (row_id,),
                )
                if stop_event is not None:
                    stop_event.wait()
            conn.rollback()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Blocker stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _hold_advisory_lock(self, lock_key: int, application_name: str, stop_event):
        # 会话级泄漏形态：autocommit 会话取得 advisory lock 后空闲等待客户端，
        # 不处于任何事务——生产连接池泄漏 advisory lock 的典型状态。
        conn = None
        try:
            conn = self._connect(application_name)
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_lock(%s);", (lock_key,))
            if stop_event is not None:
                stop_event.wait()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Advisory holder stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _blocking_advisory_waiter(self, worker_id: int, lock_key: int, prefix: str):
        conn = None
        try:
            conn = self._connect(f"{prefix}{worker_id:02d}")
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_lock(%s);", (lock_key,))
                cur.execute("SELECT pg_advisory_unlock(%s);", (lock_key,))
            conn.commit()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Advisory waiter {worker_id} stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _blocking_waiter(self, worker_id: int):
        self._blocking_waiter_on(self.critical_waiter_prefix, self.row_id, worker_id)

    def _blocking_waiter_on(self, waiter_prefix: str, row_id: int, worker_id: int):
        conn = None
        try:
            conn = self._connect(f"{waiter_prefix}{worker_id:02d}")
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {self.table} SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = %s;", (row_id,))
            conn.commit()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Waiter {worker_id} stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _hold_decoy_lock(self):
        conn = None
        try:
            conn = self._connect(self.decoy_blocker_app)
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.table} SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = %s;",
                    (self.decoy_row_id,),
                )
                if self._decoy_stop_event is not None:
                    self._decoy_stop_event.wait()
            conn.rollback()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Decoy blocker stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _blocking_decoy_waiter(self, worker_id: int):
        conn = None
        try:
            conn = self._connect(f"{self.decoy_waiter_prefix}{worker_id:02d}")
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {self.table} SET w_ytd = w_ytd + 1, w_updated_at = now() WHERE w_id = %s;",
                    (self.decoy_row_id,),
                )
            conn.commit()
        except Exception as exc:
            print(f"[FaultInjector:PgSystemFailureCpuLockSpinInjector] Decoy waiter {worker_id} stopped: {exc}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    def _start_noise_runner(self):
        if not self.noise_profiles:
            return
        runner = self.create_workload_runner(self.env, self.noise_profiles, 2)
        runner.start()
        self._noise_runner = runner

    def _wait_for_lock_waiters(self, min_waiters: int, timeout_seconds: float = 10.0):
        import time

        critical_prefix = self.critical_waiter_prefix.replace("'", "''")
        decoy_prefix = self.decoy_waiter_prefix.replace("'", "''")
        deadline = time.time() + timeout_seconds
        last_count = 0
        while time.time() < deadline:
            payload = _json_object(self.env.execute_sql(f"""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE wait_event_type = 'Lock'
                  AND (
                      application_name LIKE '{critical_prefix}%'
                      OR application_name LIKE '{decoy_prefix}%'
                  );
            """), "read CPU lock-spin waiter count")
            last_count = int(payload["result"][0][0])
            if last_count >= min_waiters:
                return
            time.sleep(0.2)
        raise RuntimeError(
            f"Expected at least {min_waiters} stable lock-waiting sessions, observed {last_count}."
        )

    def _terminate_leftover_sessions(self):
        critical_blocker = self.critical_blocker_app.replace("'", "''")
        critical_waiter = self.critical_waiter_prefix.replace("'", "''")
        retry_worker = self.retry_worker_prefix.replace("'", "''")
        decoy_blocker = self.decoy_blocker_app.replace("'", "''")
        decoy_waiter = self.decoy_waiter_prefix.replace("'", "''")
        decoy_retry = self.decoy_retry_worker_prefix.replace("'", "''")
        neighbor_clauses = "".join(
            f"\n                    OR application_name = '{chain.blocker_app.replace(chr(39), chr(39) * 2)}'"
            f"\n                    OR application_name LIKE '{chain.waiter_prefix.replace(chr(39), chr(39) * 2)}%'"
            f"\n                    OR application_name LIKE '{chain.retry_prefix.replace(chr(39), chr(39) * 2)}%'"
            for chain in self.neighbor_chains
        )
        _require_sql_success(
            self.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE (
                    application_name LIKE 'order_api_%'
                    OR application_name LIKE 'aiopsbench_cpu_lock_%'
                    OR application_name LIKE 'checkout-api-%'
                    OR application_name LIKE 'payment-retry-%'
                    OR application_name LIKE 'inventory-sync-%'
                    OR application_name LIKE 'inventory-recount-%'
                    OR application_name LIKE 'orders-ledger-%'
                    OR application_name LIKE 'orders-api-%'
                    OR application_name LIKE 'settlement-close-%'
                    OR application_name LIKE 'settlement-archiver-%'
                    OR application_name = 'settlement-batch-rollup'
                    OR application_name = 'checkout-batch-rollup'
                    OR application_name LIKE 'checkout-read-probe%'
                    OR application_name = '{critical_blocker}'
                    OR application_name LIKE '{critical_waiter}%'
                    OR application_name LIKE '{retry_worker}%'
                    OR application_name = '{decoy_blocker}'
                    OR application_name LIKE '{decoy_waiter}%'
                    OR application_name LIKE '{decoy_retry}%'
                    {neighbor_clauses}
                    OR application_name = 'aiopsbench_workload_runner'
                )
                  AND pid <> pg_backend_pid();
            """),
            "terminate CPU lock-spin sessions",
        )

    def prepare_observability(self, context: FaultLifecycleContext):
        env = context.env
        if self.fault_variant == "advisory_lock_spin":
            seed_result = env.execute_sql(
                f"SET statement_timeout = '1500ms'; "
                f"SELECT pg_try_advisory_lock({self.advisory_lock_key});"
            )
            if not env.reconnect():
                raise RuntimeError(
                    f"Advisory CPU lock-spin observability could not reconnect: "
                    f"scenario={context.scenario_id}, case={context.case_id}"
                )
            return {
                "visible_business_seed": seed_result,
                "active_connections": env.query_metrics("active_connections"),
                "slow_queries": env.query_metrics("slow_queries", threshold_ms=1000),
                "cpu": env.query_metrics("cpu"),
            }
        seed_result = env.execute_sql(
            f"SET statement_timeout = '1500ms'; "
            f"SET lock_timeout = '1200ms'; "
            f"UPDATE {self.table} SET w_ytd = w_ytd + 1, w_updated_at = now() "
            f"WHERE w_id = {self.row_id};"
        )
        seed_payload = _json_response(seed_result, "seed visible CPU lock-spin business update")
        if seed_payload.get("status") == "error" and "lock timeout" not in str(seed_result).lower():
            raise RuntimeError(
                "Visible CPU lock-spin business update failed for an unexpected reason: "
                f"scenario={context.scenario_id}, case={context.case_id}, result={seed_result}"
            )
        if not env.reconnect():
            raise RuntimeError(
                f"CPU lock-spin observability could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        return {
            "visible_business_seed": seed_result,
            "active_connections": env.query_metrics("active_connections"),
            "slow_queries": env.query_metrics("slow_queries", threshold_ms=1000),
            "cpu": env.query_metrics("cpu"),
        }

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

    @staticmethod
    def _stop_process(process, index: int) -> None:
        process.join(timeout=2)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
        if process.is_alive():
            raise RuntimeError(f"CPU lock-spin process {index} did not stop")

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        self.env = context.env
        print("[FaultInjector:PgSystemFailureCpuLockSpinInjector] Recovering CPU lock-spin fault...")
        if self._noise_runner is not None:
            self._noise_runner.stop()
            self._noise_runner = None

        if self._spin_stop_event is not None:
            self._spin_stop_event.set()

        if self._stop_event is not None:
            self._stop_event.set()
        if self._decoy_stop_event is not None:
            self._decoy_stop_event.set()

        self._terminate_leftover_sessions()
        threads = [
            self._blocker_thread,
            self._decoy_blocker_thread,
            *self._waiter_threads,
            *self._decoy_waiter_threads,
            *self._neighbor_blocker_threads,
            *self._neighbor_waiter_threads,
        ]
        steps = [
            (
                f"stop spin process {index}",
                lambda process=process, index=index: self._stop_process(process, index),
            )
            for index, process in enumerate(self._spin_processes)
        ]
        steps.extend(
            (
                f"join lock thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    3,
                    f"CPU lock-spin thread {index}",
                ),
            )
            for index, thread in enumerate(threads)
            if thread is not None
        )
        steps.extend(
            (f"close connection {index}", conn.close)
            for index, conn in enumerate(self._connections)
            if not conn.closed
        )
        _run_cleanup_steps(
            f"CPU lock-spin cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._spin_processes = []
        self._spin_stop_event = None
        self._blocker_thread = None
        self._decoy_blocker_thread = None
        self._waiter_threads = []
        self._decoy_waiter_threads = []
        self._neighbor_blocker_threads = []
        self._neighbor_waiter_threads = []
        self._connections = []
        self._stop_event = None
        self._decoy_stop_event = None

    def recover(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

        _require_sql_success(
            context.env.execute_sql(f"ANALYZE {self.table};"),
            f"analyze recovered CPU lock-spin table {self.table}",
        )
        print("[FaultInjector:PgSystemFailureCpuLockSpinInjector] Recovery complete.")


class PgSystemFailureCpuLockSpinScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_cpu_lock_spin'
    description = 'High CPU alert caused by lock-wait spin clients rather than compute-heavy queries.'
    cases = (
        _PGSYSTEMFAILURECPULOCKSPINSCENARIO_CASE,
        _PGSYSTEMFAILURECPULOCKSPINSCENARIO_CHECKOUT_RETRY_CASE,
        _PGSYSTEMFAILURECPULOCKSPINSCENARIO_ADVISORY_LOCK_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureCpuLockSpinCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureCpuLockSpinInjector,
                config={
                    'table': case.table,
                    'fault_variant': case.fault_variant,
                    'row_id': case.row_id,
                    'advisory_lock_key': case.advisory_lock_key,
                    'decoy_advisory_lock_key': case.decoy_advisory_lock_key,
                    'waiter_count': case.waiter_count,
                    'spinner_count': case.spinner_count,
                    'retry_batch_size': case.retry_batch_size,
                    'min_lock_waiters': case.min_lock_waiters,
                    'critical_blocker_app': case.critical_blocker_app,
                    'critical_waiter_prefix': case.critical_waiter_prefix,
                    'retry_worker_prefix': case.retry_worker_prefix,
                    'decoy_blocker_app': case.decoy_blocker_app,
                    'decoy_waiter_prefix': case.decoy_waiter_prefix,
                    'decoy_retry_worker_prefix': case.decoy_retry_worker_prefix,
                    'decoy_row_id': case.decoy_row_id,
                    'decoy_waiter_count': case.decoy_waiter_count,
                    'decoy_spinner_count': case.decoy_spinner_count,
                    'neighbor_chains': case.neighbor_chains,
                    'noise_profiles': case.noise_profiles,
                },
            ),
        )
