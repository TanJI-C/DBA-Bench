from dataclasses import dataclass

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureLockContentionForCustomerProfileLockQueueSimpleEvaluatorCase,
    PgSystemFailureLockContentionForCustomerRowLockQueueEvaluatorCase,
)
from src.workloads.specs import WorkloadProfile

from src.workloads.specs import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    EMPTY_BACKGROUND_WORKLOAD,
)
from src.scenarios.base import DifficultyCalibration, FaultPlan, PostgresScenario, PostgresScenarioCase
from src.execution.specs import CaseResourceSpec, PostgresCaseRuntime


# runtime fat image 以 shared_buffers=1GB / work_mem=64MB 运行；case 噪声含
# 16 个 TPC-DS 聚合会话 + ~60 连接，256MB cgroup 下后端会被 OOM 杀死并引发
# postmaster crash recovery（实测）。512MB 与同镜像类 system_failure 场景
# （cpu_lock_spin 等）一致。
LOCK_CONTENTION_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=0.5,
    container_memory_mb=512,
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.agent_language import agent_text

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

class PgSystemFailureLockContentionInjector(BaseFaultInjector):
    """
    模拟"锁争用与并发阻塞"故障。

    归类为 system_failure（长事务持锁），不在 query_perf 范围。
    开启一个长事务执行 UPDATE 但不 COMMIT，导致后续对该行/表的写操作被阻塞。
    """
    HOLDER_APP = "checkout_api_tx_17"
    WAITER_APP_PREFIX = "checkout_api_wait_"
    REVIEW_APP = "checkout_fraud_review_77"
    # 作业层复合根因：review 会话是 fraud_review 作业的当前执行者。作业的控制面是
    # 公开业务表 ops_fraud_review_queue（含 CHECK 枚举状态列与注释）；worker 在持锁周期内
    # 周期性检查 pending 任务，作业被暂停/取消后在持锁周期末退出；仅终止 worker 会话时，
    # 监督循环在确定性固定延迟后重启新 review 事务（新 pid、同 application_name）→ 队列复发。
    REVIEW_JOB_TABLE = "ops_fraud_review_queue"
    REVIEW_JOB_PENDING_SQL = (
        f"SELECT count(*) FROM {REVIEW_JOB_TABLE} WHERE status = 'pending';"
    )
    REVIEW_RESTART_DELAY_SECONDS = 2.0
    REVIEW_CONTROL_POLL_SECONDS = 1.0
    NOISE_APP = "nightly_reporting_snapshot"
    IDLE_NOISE_PREFIX = "checkout_api_pool_"
    SHORT_TX_NOISE_PREFIX = "profile_read_api_"
    DECOY_TX_APPS = ("profile_read_tx_legacy", "order_callback_audit_tx")
    DECOY_WAITER_APPS = ("nightly_reporting_wait_01", "profile_read_wait_01")
    BACKGROUND_QUERY_APPS = (
        "dashboard_profile_rollup",
        "dashboard_orders_heatmap",
        "dashboard_customer_ltv",
        "dashboard_sla_tile",
        "dashboard_refund_audit",
        "dashboard_inventory_overlay",
        "etl_customer_segment_scan",
        "etl_loyalty_rollup",
        "etl_coupon_attribution",
        "etl_sales_export",
        "etl_return_rate_refresh",
        "etl_order_funnel",
        "prometheus_pg_activity_scrape",
        "prometheus_pg_stat_statements",
        "prometheus_wait_event_sample",
        "prometheus_index_bloat_probe",
    )

    def __init__(self):
        self._stop_event = None
        self._recovering = False
        self.thread = None
        self.noise_thread = None
        self.lock_conn = None
        self.noise_conn = None
        self.review_conn = None
        self.waiter_conns = []
        self.idle_noise_conns = []
        self.short_tx_noise_conns = []
        self.decoy_conns = []
        self.decoy_waiter_conns = []
        self.noise_threads = []
        self.waiter_threads = []
        self.decoy_waiter_threads = []
        self.background_threads = []
        self.review_thread = None
        self._supervisor_thread = None

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._start_runtime()

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install_persistent_state()
        self.activate(context)

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config["table"], "table")
        self.update_sql = config["update_sql"]
        self.holder_followup_sql = config["holder_followup_sql"]
        self.noise_sql = config["noise_sql"]
        self.decoy_sqls = config["decoy_sqls"]
        self.decoy_wait_sqls = config["decoy_wait_sqls"]
        self.background_sql = config["background_sql"]
        self.ensure_row_sql = config["ensure_row_sql"]
        self.waiter_count = int(config["waiter_count"])
        self.idle_noise_count = int(config["idle_noise_count"])
        self.short_tx_noise_count = int(config["short_tx_noise_count"])
        self.background_query_apps = tuple(config["background_query_apps"])
        # 复合根因开关：review 事务先取得目标行的 FOR SHARE 授权锁并长期保持打开，
        # holder 的 UPDATE 排在其后，waiter 再排在 holder 之后，形成多级锁队列。
        # 置空则保持单 holder 机制（customer_profile_lock_queue_simple 不受影响）。
        self.review_lock_sql = str(config.get("review_lock_sql") or "")
        self.review_app = str(config.get("review_app") or self.REVIEW_APP)
        # 作业层控制面：幂等 DDL（建表 + 注释 + 种子 pending 任务），仅复合机制启用。
        self.review_job_ddl = tuple(config.get("review_job_ddl") or ())

    def _install_persistent_state(self) -> None:
        _require_sql_success(
            self.env.execute_sql(self.ensure_row_sql),
            "install lock-contention target row",
        )
        for statement in self.review_job_ddl:
            _require_sql_success(
                self.env.execute_sql(_agent_language_review_job_statement(statement)),
                "install fraud-review job control plane",
            )

    def _verify_persistent_state(self) -> None:
        # 幂等补建控制面：fault snapshot 不含作业层表时也能激活。
        for statement in self.review_job_ddl:
            _require_sql_success(
                self.env.execute_sql(_agent_language_review_job_statement(statement)),
                "ensure fraud-review job control plane",
            )
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT count(*) FROM {self.table} WHERE c_customer_sk = 1;"
            ),
            "verify lock-contention target row",
        )
        if int(payload["result"][0][0]) != 1:
            raise RuntimeError(
                f"Lock-contention fault image target row mismatch: table={self.table}, "
                f"c_customer_sk=1, count={payload['result'][0][0]}"
            )
        if self.review_job_ddl:
            payload = _json_object(
                self.env.execute_sql(self.REVIEW_JOB_PENDING_SQL),
                "verify fraud-review job pending task",
            )
            if int(payload["result"][0][0]) != 1:
                raise RuntimeError(
                    "Lock-contention fraud-review job control plane mismatch: "
                    f"expected exactly 1 pending task, count={payload['result'][0][0]}"
                )

    def _start_runtime(self) -> None:
        print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Injecting lock contention on {self.table}...")

        import threading
        import psycopg2
        import time

        self._stop_event = threading.Event()
        self._holder_ready = threading.Event()
        self._noise_ready = threading.Event()
        self._profile_decoy_ready = threading.Event()
        self._review_ready = threading.Event()
        self._review_error = None
        self.lock_conn = None
        self.noise_conn = None
        self.review_conn = None
        self.idle_noise_conns = []
        self.short_tx_noise_conns = []
        self.decoy_conns = []
        self.decoy_waiter_conns = []
        self.waiter_conns = []
        self.waiter_threads = []
        self.noise_threads = []
        self.decoy_waiter_threads = []
        self.background_threads = []
        self.review_thread = None
        self._supervisor_thread = None
        self._holder_error = None

        def connect_event_session(application_name):
            return psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                application_name=application_name,
                options="-c idle_in_transaction_session_timeout=0",
            )

        def review_work_pending() -> bool:
            """读公开控制面：是否仍有 pending 复核任务（作业是否仍要执行）。

            控制面不可读（如被 DROP）时按"无任务"处理；评估层的 OP/SP 会独立对
            DROP 控制表判负，injector 不在这里放大错误。
            """
            control_conn = None
            try:
                control_conn = connect_event_session(f"{self.review_app}_control")
                with control_conn.cursor() as cur:
                    cur.execute(self.REVIEW_JOB_PENDING_SQL)
                    return int(cur.fetchall()[0][0]) > 0
            except Exception:
                return False
            finally:
                if control_conn is not None:
                    try:
                        control_conn.close()
                    except Exception:
                        pass

        def review_worker():
            # fraud_review 作业 worker（复合根因的队列根）：领取 pending 复核任务，
            # 对争议行持 FOR SHARE 保持复核快照。持锁周期内每秒检查作业控制面：
            # 作业被暂停/取消（pending=0）时在持锁周期末回滚退出；会话被定向终止时
            # 连接报错退出，是否复发由监督循环依据控制面决定。
            conn = None
            try:
                if not review_work_pending():
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Review worker not started: no pending review task")
                    return
                conn = connect_event_session(self.review_app)
                conn.autocommit = False
                self.review_conn = conn
                with conn.cursor() as cur:
                    # 每次出现都写一行 PG 日志（Agent 可通过 read_log 观察）。
                    cur.execute(
                        "DO $$ BEGIN RAISE LOG 'fraud_review worker running, pid=%', "
                        "pg_backend_pid(); END $$;"
                    )
                    cur.execute(self.review_lock_sql)
                    self._review_ready.set()
                    while not self._stop_event.is_set():
                        cur.execute(self.REVIEW_JOB_PENDING_SQL)
                        if int(cur.fetchall()[0][0]) == 0:
                            print(
                                "[FaultInjector:PgSystemFailureLockContentionInjector] "
                                "Review worker exit: review job paused/cancelled"
                            )
                            return
                        self._stop_event.wait(self.REVIEW_CONTROL_POLL_SECONDS)
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    self._review_error = e
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Review session stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    try:
                        conn.close()
                    except Exception:
                        pass
                self.review_conn = None

        def review_supervisor():
            # 作业监督循环（业务语义：调度器维持 fraud_review 作业运行）：当前 worker
            # 退出且控制面仍有 pending 任务时，在确定性固定延迟后重启新 worker
            # （新 pid、同 application_name，pg_stat_activity 可见复发）；作业已暂停/
            # 取消则不再拉起（修复作业层后由监督自然停止）。禁止随机窗口。
            while not self._stop_event.is_set():
                worker = self.review_thread
                if worker is not None and worker.is_alive():
                    if self._stop_event.wait(0.2):
                        return
                    continue
                if self._stop_event.wait(self.REVIEW_RESTART_DELAY_SECONDS):
                    return
                if self._stop_event.is_set() or getattr(self, "_recovering", False):
                    return
                if self.review_thread is not None and self.review_thread.is_alive():
                    continue
                if not review_work_pending():
                    continue
                print(
                    "[FaultInjector:PgSystemFailureLockContentionInjector] Review "
                    "supervisor: relaunching fraud_review worker (job still pending)"
                )
                new_worker = threading.Thread(target=review_worker, daemon=True)
                self.review_thread = new_worker
                new_worker.start()

        def hold_lock():
            conn = None
            try:
                conn = connect_event_session(self.HOLDER_APP)
                conn.autocommit = False
                self.lock_conn = conn
                with conn.cursor() as cur:
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Executing: {self.update_sql}")
                    cur.execute(self.update_sql)
                    if not self.review_lock_sql:
                        cur.execute(self.holder_followup_sql)
                        # 单 holder 机制：UPDATE 已授权，这里就是持锁者。
                        self._holder_ready.set()
                    # 复合机制：UPDATE 排在 review 事务之后等锁；_holder_ready 由
                    # 主线程确认该会话真正进入 Lock 等待后置位，保证队列顺序
                    # review -> holder -> waiters。
                    self._stop_event.wait()
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    self._holder_error = e
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Error holding lock: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self.lock_conn = None

        def hold_noise_lock():
            conn = None
            try:
                conn = connect_event_session(self.NOISE_APP)
                conn.autocommit = False
                self.noise_conn = conn
                with conn.cursor() as cur:
                    cur.execute(self.noise_sql)
                    self._noise_ready.set()
                    self._stop_event.wait()
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Noise session stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                self.noise_conn = None

        def hold_decoy_tx(app_name, sql):
            conn = None
            try:
                conn = connect_event_session(app_name)
                conn.autocommit = False
                self.decoy_conns.append(conn)
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if app_name == "profile_read_tx_legacy":
                        self._profile_decoy_ready.set()
                    self._stop_event.wait()
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Decoy session stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if conn in self.decoy_conns:
                    self.decoy_conns.remove(conn)

        def hold_idle_noise(app_name):
            conn = None
            try:
                conn = connect_event_session(app_name)
                conn.autocommit = True
                self.idle_noise_conns.append(conn)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    self._stop_event.wait()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Idle noise stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if conn in self.idle_noise_conns:
                    self.idle_noise_conns.remove(conn)

        def hold_short_tx_noise(app_name):
            conn = None
            try:
                conn = connect_event_session(app_name)
                conn.autocommit = False
                self.short_tx_noise_conns.append(conn)
                with conn.cursor() as cur:
                    while not self._stop_event.is_set():
                        cur.execute(f"SELECT c_customer_sk FROM {self.table} WHERE c_customer_sk = 4;")
                        conn.commit()
                        self._stop_event.wait(0.8)
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Short tx noise stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if conn in self.short_tx_noise_conns:
                    self.short_tx_noise_conns.remove(conn)

        def run_background_query(app_name):
            conn = None
            try:
                conn = connect_event_session(app_name)
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SET work_mem = '1MB';")
                    while not self._stop_event.is_set():
                        cur.execute(self.background_sql)
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Background query stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        def wait_on_lock(app_name):
            conn = None
            try:
                if not self._holder_ready.wait(timeout=10):
                    return
                conn = connect_event_session(app_name)
                conn.autocommit = False
                self.waiter_conns.append(conn)
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '0';")
                    # 这里会阻塞在 holder 持有的行锁上，供 pg_locks/pg_stat_activity 观察。
                    cur.execute(self.update_sql)
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Waiter stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if conn in self.waiter_conns:
                    self.waiter_conns.remove(conn)

        def wait_on_decoy_lock(app_name, sql, ready_event):
            conn = None
            try:
                if not ready_event.wait(timeout=10):
                    return
                conn = connect_event_session(app_name)
                conn.autocommit = False
                self.decoy_waiter_conns.append(conn)
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = '0';")
                    cur.execute(sql)
                conn.rollback()
            except Exception as e:
                if not getattr(self, "_recovering", False):
                    print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Decoy waiter stopped: {e}")
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if conn in self.decoy_waiter_conns:
                    self.decoy_waiter_conns.remove(conn)

        review_enabled = bool(self.review_lock_sql)
        if review_enabled:
            self.review_thread = threading.Thread(target=review_worker, daemon=True)
            self.review_thread.start()
            if not self._review_ready.wait(timeout=10):
                raise RuntimeError(
                    f"Lock-contention review transaction did not acquire the shared lock: "
                    f"error={self._review_error!r}"
                ) from self._review_error
            self._supervisor_thread = threading.Thread(target=review_supervisor, daemon=True)
            self._supervisor_thread.start()
        self.thread = threading.Thread(target=hold_lock, daemon=True)
        self.thread.start()
        self.noise_thread = threading.Thread(target=hold_noise_lock, daemon=True)
        self.noise_thread.start()
        for app_name, sql in zip(self.DECOY_TX_APPS, self.decoy_sqls):
            thread = threading.Thread(target=hold_decoy_tx, args=(app_name, sql), daemon=True)
            self.noise_threads.append(thread)
            thread.start()
        for idx in range(self.idle_noise_count):
            thread = threading.Thread(
                target=hold_idle_noise,
                args=(f"{self.IDLE_NOISE_PREFIX}{idx + 1:02d}",),
                daemon=True,
            )
            self.noise_threads.append(thread)
            thread.start()
        for idx in range(self.short_tx_noise_count):
            thread = threading.Thread(
                target=hold_short_tx_noise,
                args=(f"{self.SHORT_TX_NOISE_PREFIX}{idx + 1:02d}",),
                daemon=True,
            )
            self.noise_threads.append(thread)
            thread.start()
        for app_name in self.background_query_apps:
            thread = threading.Thread(target=run_background_query, args=(app_name,), daemon=True)
            self.background_threads.append(thread)
            thread.start()
        for app_name, sql, ready_event in zip(
            self.DECOY_WAITER_APPS,
            self.decoy_wait_sqls,
            (self._noise_ready, self._profile_decoy_ready),
        ):
            thread = threading.Thread(target=wait_on_decoy_lock, args=(app_name, sql, ready_event), daemon=True)
            self.decoy_waiter_threads.append(thread)
            thread.start()
        if review_enabled:
            # 复合机制：确认 holder 的 UPDATE 真正进入 Lock 等待（排在 review 之后），
            # 再放行 waiter 线程，保证队列顺序 review -> holder -> waiters。
            self._wait_for_holder_queued()
            self._holder_ready.set()
        elif not self._holder_ready.wait(timeout=10):
            raise RuntimeError(
                f"Lock-contention holder did not acquire the target lock: "
                f"error={self._holder_error!r}"
            ) from self._holder_error

        for idx in range(self.waiter_count):
            app_name = f"{self.WAITER_APP_PREFIX}{idx + 1:02d}"
            thread = threading.Thread(target=wait_on_lock, args=(app_name,), daemon=True)
            self.waiter_threads.append(thread)
            thread.start()
        time.sleep(1.0)
        self._wait_for_waiting_locks(min_waiters=min(5, self.waiter_count))

    def _stop_runtime(self, context: FaultLifecycleContext) -> None:
        print(f"[FaultInjector:PgSystemFailureLockContentionInjector] Recovering lock contention...")
        self._recovering = True
        if self._stop_event is not None:
            self._stop_event.set()
        review_clause = (
            f"OR application_name = '{self.review_app}' " if self.review_lock_sql else ""
        )
        _require_sql_success(
            context.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE (
                    application_name = '{self.HOLDER_APP}'
                    OR application_name LIKE '{self.WAITER_APP_PREFIX}%'
                    OR application_name = '{self.NOISE_APP}'
                    OR application_name LIKE '{self.IDLE_NOISE_PREFIX}%'
                    OR application_name LIKE '{self.SHORT_TX_NOISE_PREFIX}%'
                    OR application_name IN ({", ".join(repr(app) for app in self.DECOY_WAITER_APPS)})
                    OR application_name IN ({", ".join(repr(app) for app in self.DECOY_TX_APPS + self.background_query_apps)})
                    {review_clause}
                )
                  AND pid <> pg_backend_pid();
            """),
            "terminate lock-contention sessions",
        )
        connections = [
            *self.waiter_conns,
            self.lock_conn,
            self.noise_conn,
            self.review_conn,
            *self.idle_noise_conns,
            *self.short_tx_noise_conns,
            *self.decoy_conns,
            *self.decoy_waiter_conns,
        ]
        threads = [
            self.thread,
            self.noise_thread,
            self.review_thread,
            self._supervisor_thread,
            *self.noise_threads,
            *self.waiter_threads,
            *self.decoy_waiter_threads,
            *self.background_threads,
        ]
        steps = [
            (f"close connection {index}", conn.close)
            for index, conn in enumerate(connections)
            if conn is not None
        ]
        if self.review_job_ddl:
            # 反向能力清理：作业控制面属本次故障注入的 persistent state。
            steps.append(
                (
                    f"drop {self.REVIEW_JOB_TABLE}",
                    lambda: _require_sql_success(
                        context.env.execute_sql(
                            f"DROP TABLE IF EXISTS {self.REVIEW_JOB_TABLE};"
                        ),
                        "drop fraud-review job control plane",
                    ),
                )
            )
        steps.extend(
            (
                f"join thread {index}",
                lambda thread=thread, index=index: _join_thread(
                    thread,
                    5,
                    f"lock-contention thread {index}",
                ),
            )
            for index, thread in enumerate(threads)
            if thread is not None
        )
        _run_cleanup_steps(
            f"Lock-contention cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self.waiter_conns = []
        self.lock_conn = None
        self.noise_conn = None
        self.review_conn = None
        self.idle_noise_conns = []
        self.short_tx_noise_conns = []
        self.decoy_conns = []
        self.decoy_waiter_conns = []
        self.thread = None
        self.noise_thread = None
        self.review_thread = None
        self._supervisor_thread = None
        self.noise_threads = []
        self.waiter_threads = []
        self.decoy_waiter_threads = []
        self.background_threads = []
        self._stop_event = None
        self._recovering = False

    def recover(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

    def prepare_observability(self, context: FaultLifecycleContext):
        import time

        config = context.config
        env = context.env
        with env.metrics_hidden():
            active_connections = env.query_metrics("active_connections")
            observed_lock_apps = [
                "'checkout_api_tx_17'",
                "'nightly_reporting_snapshot'",
                "'nightly_reporting_wait_01'",
                "'profile_read_tx_legacy'",
                "'profile_read_wait_01'",
            ]
            if self.review_lock_sql:
                observed_lock_apps.append(f"'{self.review_app}'")
            waiting_locks = env.execute_sql(
                "SELECT DISTINCT ON (a.pid) a.pid, a.application_name, a.state, a.wait_event_type, "
                "a.wait_event, l.locktype, l.mode, l.granted "
                "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
                f"WHERE a.application_name IN ({', '.join(observed_lock_apps)}) "
                "OR a.application_name LIKE 'checkout_api_wait_%' "
                "ORDER BY a.pid, l.granted;"
            )
            noise_context = env.execute_sql(
                "SELECT application_name, state, wait_event_type, left(query, 90), count(*) "
                "FROM pg_stat_activity WHERE application_name = 'nightly_reporting_snapshot' "
                "OR application_name IN ('profile_read_tx_legacy', 'order_callback_audit_tx', "
                "'nightly_reporting_wait_01', 'profile_read_wait_01') "
                "OR application_name LIKE 'dashboard_%' "
                "OR application_name LIKE 'etl_%' "
                "OR application_name LIKE 'prometheus_%' "
                "OR application_name LIKE 'checkout_api_pool_%' "
                "OR application_name LIKE 'profile_read_api_%' "
                "GROUP BY application_name, state, wait_event_type, left(query, 90) "
                "ORDER BY count(*) DESC, application_name;"
            )
            self._assert_lock_topology(active_connections, waiting_locks, noise_context)

            required_slow_queries = min(12, len(self.background_query_apps))
            deadline = time.monotonic() + 8
            slow_queries = env.query_metrics("slow_queries", threshold_ms=1000, limit=20)
            while self._background_slow_query_count(slow_queries) < required_slow_queries:
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "Lock-contention slow-query noise did not become observable: "
                        f"required={required_slow_queries}, "
                        f"observed={self._background_slow_query_count(slow_queries)}, "
                        f"slow_queries={slow_queries}"
                    )
                time.sleep(0.5)
                slow_queries = env.query_metrics("slow_queries", threshold_ms=1000, limit=20)

        seed_result = env.execute_sql(
            "SET statement_timeout = '1500ms'; " + self.update_sql.rstrip(";") + ";"
        )
        seed_payload = _json_response(seed_result, "seed lock-contention business update")
        if seed_payload.get("status") != "error" or "statement timeout" not in str(seed_result).lower():
            raise RuntimeError(
                "Lock-contention business update was not blocked until statement timeout: "
                f"result={seed_result}"
            )
        if not env.reconnect():
            raise RuntimeError(
                f"Lock-contention observability could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        return {
            "active_connections": active_connections,
            "slow_queries": slow_queries,
            "waiting_locks": waiting_locks,
            "noise_context": noise_context,
            "business_update_seed": seed_result,
        }

    def _assert_lock_topology(self, active_connections, waiting_locks, noise_context) -> None:
        lock_text = str(waiting_locks).lower()
        noise_text = str(noise_context).lower()
        decoy_wait_count = len(
            getattr(self, "decoy_wait_sqls", self.DECOY_WAITER_APPS)
        )
        expected_lock_apps = (
            self.HOLDER_APP,
            self.WAITER_APP_PREFIX,
            *self.DECOY_WAITER_APPS[:decoy_wait_count],
        )
        if self.review_lock_sql:
            expected_lock_apps = (*expected_lock_apps, self.review_app)
        for expected in expected_lock_apps:
            if expected.lower() not in lock_text:
                raise RuntimeError(
                    f"Lock-contention session is missing from lock topology: "
                    f"application_name={expected!r}, active_connections={active_connections}, "
                    f"waiting_locks={waiting_locks}"
                )
        expected_noise_apps = [self.NOISE_APP]
        if getattr(self, "idle_noise_count", 1):
            expected_noise_apps.append(self.IDLE_NOISE_PREFIX)
        if getattr(self, "short_tx_noise_count", 1):
            expected_noise_apps.append(self.SHORT_TX_NOISE_PREFIX)
        decoy_tx_count = len(
            getattr(self, "decoy_sqls", self.DECOY_TX_APPS[:1])
        )
        expected_noise_apps.extend(self.DECOY_TX_APPS[:decoy_tx_count])
        expected_noise_apps.extend(
            self.DECOY_WAITER_APPS[:decoy_wait_count]
        )
        background_query_apps = getattr(
            self,
            "background_query_apps",
            self.BACKGROUND_QUERY_APPS,
        )
        if background_query_apps:
            expected_noise_apps.append(background_query_apps[0])
        for expected in expected_noise_apps:
            if expected.lower() not in noise_text:
                raise RuntimeError(
                    f"Lock-contention noise floor is incomplete: "
                    f"application_name={expected!r}, active_connections={active_connections}, "
                    f"noise_context={noise_context}"
                )

    def _background_slow_query_count(self, slow_queries) -> int:
        payload = _json_object(slow_queries, "read lock-contention slow queries")
        return sum(
            1
            for row in payload.get("records", [])
            if "store_sales ss" in json.dumps(row, ensure_ascii=False).lower()
            and "date_dim d" in json.dumps(row, ensure_ascii=False).lower()
        )

    def quiesce(self, context: FaultLifecycleContext):
        self._stop_runtime(context)

    def _wait_for_holder_queued(self, timeout_seconds: float = 15.0):
        import time

        deadline = time.monotonic() + timeout_seconds
        sql = (
            "SELECT state, wait_event_type FROM pg_stat_activity "
            f"WHERE application_name = '{self.HOLDER_APP}';"
        )
        rows = []
        while time.monotonic() < deadline:
            rows = self._result_rows(self.env.execute_sql(sql))
            if rows and rows[0] and rows[0][0] == "active" and rows[0][1] == "Lock":
                return
            time.sleep(0.5)
        raise RuntimeError(
            f"Lock-contention holder did not queue behind the review transaction: "
            f"observed={rows!r}, holder_error={self._holder_error!r}"
        )

    def _wait_for_waiting_locks(self, min_waiters: int, timeout_seconds: float = 8.0):
        import time

        deadline = time.monotonic() + timeout_seconds
        sql = f"""
            SELECT count(*)
            FROM pg_locks l
            JOIN pg_stat_activity a ON a.pid = l.pid
            WHERE NOT l.granted
              AND a.application_name LIKE '{self.WAITER_APP_PREFIX}%';
        """
        while time.monotonic() < deadline:
            raw = self.env.execute_sql(sql)
            rows = self._result_rows(raw)
            if rows and rows[0] and int(rows[0][0]) >= min_waiters:
                return
            time.sleep(0.5)
        raise RuntimeError(
            f"Lock-contention waiters did not become observable: "
            f"expected_at_least={min_waiters}, timeout_seconds={timeout_seconds}"
        )

    def _result_rows(self, raw_result):
        rows = _json_object(raw_result, "read lock-contention result")["result"]
        if not isinstance(rows, list):
            raise TypeError(
                f"Lock-contention result must be a list, got {type(rows).__name__}"
            )
        return rows


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureLockContentionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    slow_queries: tuple[str, ...]
    update_sql: str
    ensure_row_sql: str
    waiter_count: int
    holder_followup_sql: str
    noise_sql: str
    decoy_sqls: tuple[str, ...]
    decoy_wait_sqls: tuple[str, ...]
    background_sql: str
    idle_noise_count: int
    short_tx_noise_count: int
    background_query_apps: tuple[str, ...]
    # 复合根因开关：非空时 review 事务先持目标行 FOR SHARE，holder 排队其后。
    review_lock_sql: str = ""
    # 作业层控制面：幂等 DDL，建公开业务控制表 + 注释 + 种子 pending 任务。
    # 仅复合机制 case 启用；空元组 = 无作业层（simple case 行为不变）。
    review_job_ddl: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureLockContentionForCustomerRowLockQueueScenarioCase(
    PgSystemFailureLockContentionCase
):
    pass


# 作业层控制面 DDL：fraud_review 作业的任务队列表。表/列 COMMENT 公开完整业务
# 契约（worker 领取 pending 任务并保持争议行共享锁；仅终止 worker 会被作业重新拉起，
# 取消/暂停必须走本表状态列）；status 由完整 CHECK 枚举列出全部合法值，Agent 可通过
# catalog（\d / information_schema / pg_constraint）看到。
FRAUD_REVIEW_JOB_DDL = (
    f"""
    CREATE TABLE IF NOT EXISTS {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE} (
        review_id   integer PRIMARY KEY,
        customer_sk integer NOT NULL,
        reason      text    NOT NULL,
        status      text    NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'paused', 'cancelled', 'completed')),
        created_at  timestamptz NOT NULL DEFAULT now(),
        updated_at  timestamptz NOT NULL DEFAULT now()
    );
    """,
    f"COMMENT ON TABLE {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE} IS "
    "'风控复核作业队列: fraud_review worker 按本表领取待复核任务(status=pending)并保持争议客户行的共享锁; "
    "仅终止 worker 会话会被作业重新拉起, 取消或暂停复核必须通过本表状态列。';",
    f"COMMENT ON COLUMN {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE}.status IS "
    "'任务状态(CHECK 完整枚举): pending=待执行(worker 会领取); paused=已暂停(不执行); "
    "cancelled=已取消(不执行); completed=已完成。';",
    f"""
    INSERT INTO {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE}
        (review_id, customer_sk, reason, status)
    SELECT 7701, 1, 'checkout dispute #77 manual risk review', 'pending'
    WHERE NOT EXISTS (
        SELECT 1 FROM {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE} WHERE review_id = 7701
    );
    """,
)

# The table and column comments are read by the agent through the catalog; the
# English run installs them in English. Keyed by the Chinese statement above.
_FRAUD_REVIEW_JOB_COMMENTS_EN = {
    FRAUD_REVIEW_JOB_DDL[1]: (
        f"COMMENT ON TABLE {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE} IS "
        "'Fraud review job queue: the fraud_review worker claims pending review tasks (status=pending) from this table "
        "and holds a shared lock on the disputed customer row; terminating only the worker session gets it restarted "
        "by the job, cancelling or pausing the review must go through the status column of this table.';"
    ),
    FRAUD_REVIEW_JOB_DDL[2]: (
        f"COMMENT ON COLUMN {PgSystemFailureLockContentionInjector.REVIEW_JOB_TABLE}.status IS "
        "'Task status (complete CHECK enumeration): pending=to be executed (the worker will claim it); "
        "paused=paused (not executed); cancelled=cancelled (not executed); completed=completed.';"
    ),
}


def _agent_language_review_job_statement(statement: str) -> str:
    return agent_text(zh=statement, en=_FRAUD_REVIEW_JOB_COMMENTS_EN.get(statement, statement))


_CASE = PgSystemFailureLockContentionForCustomerRowLockQueueScenarioCase(
    case_id="customer_row_lock_queue",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "customer row lock queue",
                    "entity": "customer_row_lock_queue",
                    "evidence": [
                        "scripted diagnostic actions observed customer row lock queue"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "review transaction holds customer row lock",
                    "entity": "customer_row_lock_queue",
                    "evidence": [
                        "scripted diagnostic actions observed review transaction holds customer row lock; "
                        "the checkout update queues behind it and sustains the waiter queue"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "decoy customer locks excluded",
                    "entity": "customer_row_lock_queue",
                    "evidence": [
                        "scripted diagnostic actions observed decoy customer locks excluded"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only blocking transaction",
                    "entity": "customer_row_lock_queue",
                    "evidence": [
                        "scripted diagnostic actions observed terminate only blocking transaction"
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
    evaluator=PgSystemFailureLockContentionForCustomerRowLockQueueEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=LOCK_CONTENTION_RESOURCES),
    base_image_name="aiopsbench-pg-tpcds:latest",
    workload_tag="tpcds",
    dataset_scale=1,
    title="Simulates lock contention by holding an uncommitted UPDATE transaction on a table.",
    alert=(
        "Alert: checkout customer-profile writes are breaching the 30s SLA. The database is busy "
        "with normal connection-pool traffic, profile reads, order callbacks, dashboard/reporting "
        "jobs, and exporter queries. Several API sessions are active but not making progress. "
        "Identify the primary blocker, separate it from background noise, and restore write "
        "throughput without restarting PostgreSQL.\n\nAffected statement:\nUPDATE customer SET "
        "c_salutation = 'Dr.' WHERE c_customer_sk = 1;\n\nBusiness impact: profile updates "
        "and order confirmation callbacks are queueing behind the same hot customer row.\n\n"
        "Authorization: you may execute and commit the business writes needed to complete this "
        "remediation within the affected scope, including pausing or cancelling queued "
        "application jobs through their own control tables. Keep the healthy neighbouring "
        "business flows running, do not modify data outside the incident, and do not restart "
        "PostgreSQL."
    ),
    initial_state={"status": "degraded", "lock": "waiting"},
    expected_target={"status": "recovered", "lock": "cleared"},
    background_workload=EMPTY_BACKGROUND_WORKLOAD,
    table="customer",
    slow_queries=("UPDATE customer SET c_salutation = 'Dr.' WHERE c_customer_sk = 1;",),
    update_sql="UPDATE customer SET c_salutation = 'Mr.' WHERE c_customer_sk = 1;",
    ensure_row_sql=(
        "INSERT INTO customer (c_customer_sk, c_customer_id, c_salutation) SELECT 1, "
        "'AIOPSLOCK000001', 'Mr.' WHERE NOT EXISTS (SELECT 1 FROM customer WHERE "
        "c_customer_sk = 1);INSERT INTO customer (c_customer_sk, c_customer_id, "
        "c_salutation) SELECT 2, 'AIOPSLOCK000002', 'Ms.' WHERE NOT EXISTS (SELECT 1 FROM "
        "customer WHERE c_customer_sk = 2);INSERT INTO customer (c_customer_sk, c_customer_id, "
        "c_salutation) SELECT 3, 'AIOPSLOCK000003', 'Mx.' WHERE NOT EXISTS (SELECT 1 FROM "
        "customer WHERE c_customer_sk = 3);INSERT INTO customer (c_customer_sk, c_customer_id, "
        "c_salutation) SELECT 4, 'AIOPSLOCK000004', 'Ms.' WHERE NOT EXISTS (SELECT 1 FROM "
        "customer WHERE c_customer_sk = 4);"
    ),
    waiter_count=12,
    holder_followup_sql="SELECT now();",
    noise_sql="SELECT c_customer_sk FROM customer WHERE c_customer_sk = 2 FOR UPDATE;",
    decoy_sqls=(
        "SELECT c_customer_sk FROM customer WHERE c_customer_sk = 3 FOR SHARE;",
        "SELECT count(*) FROM customer WHERE c_customer_sk BETWEEN 1 AND 1000;",
    ),
    decoy_wait_sqls=(
        "UPDATE customer SET c_salutation = 'Ms.' WHERE c_customer_sk = 2;",
        "UPDATE customer SET c_salutation = 'Mx.' WHERE c_customer_sk = 3;",
    ),
    background_sql=(
        "SELECT d.d_year, count(*), sum(ss.ss_net_paid) FROM store_sales ss "
        "JOIN date_dim d ON d.d_date_sk = ss.ss_sold_date_sk "
        "WHERE d.d_year BETWEEN 1998 AND 2002 AND ss.ss_quantity > 0 GROUP BY d.d_year;"
    ),
    idle_noise_count=24,
    short_tx_noise_count=6,
    background_query_apps=PgSystemFailureLockContentionInjector.BACKGROUND_QUERY_APPS,
    review_lock_sql=(
        "SELECT c_customer_sk, c_salutation FROM customer WHERE c_customer_sk = 1 FOR SHARE;"
    ),
    review_job_ddl=FRAUD_REVIEW_JOB_DDL,
    # 校准（未过滤实测）：锁等待链 join 68/132、activity 14/60、
    # lockwait_tree 13/2、topsql 0/10、控制面 1/0 → m=96 n=223，rho_s=0.3009，
    # C_s=0.6991（≥0.5）→ hard。D_s=6。
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.6991,
        reference_run_ids=(
            "reference-265__pg_system_failure_lock_contention__customer_row_lock_queue__mock__r001/attempts/005/trace.json",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureLockContentionForCustomerProfileLockQueueSimpleScenarioCase(
    PgSystemFailureLockContentionCase
):
    pass


_SIMPLE_CASE = PgSystemFailureLockContentionForCustomerProfileLockQueueSimpleScenarioCase(
    case_id="customer_profile_lock_queue_simple",
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "customer profile row lock queue",
                    "entity": "customer_profile_lock_queue_simple",
                    "evidence": [
                        "scripted diagnostic actions observed customer profile row lock queue"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "uncommitted customer profile transaction holds the row lock",
                    "entity": "customer_profile_lock_queue_simple",
                    "evidence": [
                        "scripted diagnostic actions observed uncommitted customer profile transaction holds the row lock"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "reporting row lock is unrelated to the profile write queue",
                    "entity": "customer_profile_lock_queue_simple",
                    "evidence": [
                        "scripted diagnostic actions observed reporting row lock is unrelated to the profile write queue"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "terminate only the primary customer profile blocker",
                    "entity": "customer_profile_lock_queue_simple",
                    "evidence": [
                        "scripted diagnostic actions observed terminate only the primary customer profile blocker"
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
    evaluator=PgSystemFailureLockContentionForCustomerProfileLockQueueSimpleEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=LOCK_CONTENTION_RESOURCES),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.5,
        reference_run_ids=(
            "logs/traces/"
            "run_pg_system_failure_lock_contention_"
            "customer_profile_lock_queue_simple_"
            "MockLLMAgent.json",
        ),
    ),
    base_image_name="aiopsbench-pg-tpcds:latest",
    workload_tag="tpcds",
    dataset_scale=1,
    title="A small customer-profile write queue blocked by one uncommitted transaction.",
    alert=(
        "Alert: customer-profile updates for one account are timing out, while the "
        "database remains available and unrelated reads continue to succeed. A small "
        "reporting task is also active on customer data. Identify the transaction "
        "responsible for the affected write queue, separate unrelated activity, and "
        "restore profile writes without restarting PostgreSQL.\n\n"
        "Affected statement:\n"
        "UPDATE customer SET c_salutation = 'Dr.' WHERE c_customer_sk = 1;"
    ),
    initial_state={
        "status": "degraded",
        "lock": "waiting",
        "affected_scope": "one_customer_profile",
    },
    expected_target={
        "status": "recovered",
        "lock": "cleared",
        "unrelated_reporting_transaction": "preserved",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="customer_calendar_health_probe",
                sql="SELECT count(*) FROM date_dim WHERE d_year = 2001;",
                qps=0.1,
                tier="LIGHT",
                application_name="customer_health_probe",
            ),
        ),
        worker_count=1,
        seed=0x2F01,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
    ),
    table="customer",
    slow_queries=(
        "UPDATE customer SET c_salutation = 'Dr.' WHERE c_customer_sk = 1;",
    ),
    update_sql="UPDATE customer SET c_salutation = 'Mr.' WHERE c_customer_sk = 1;",
    ensure_row_sql=(
        "INSERT INTO customer (c_customer_sk, c_customer_id, c_salutation) "
        "SELECT 1, 'AIOPSLOCK000001', 'Mr.' "
        "WHERE NOT EXISTS (SELECT 1 FROM customer WHERE c_customer_sk = 1);"
        "INSERT INTO customer (c_customer_sk, c_customer_id, c_salutation) "
        "SELECT 2, 'AIOPSLOCK000002', 'Ms.' "
        "WHERE NOT EXISTS (SELECT 1 FROM customer WHERE c_customer_sk = 2);"
        "INSERT INTO customer (c_customer_sk, c_customer_id, c_salutation) "
        "SELECT 4, 'AIOPSLOCK000004', 'Ms.' "
        "WHERE NOT EXISTS (SELECT 1 FROM customer WHERE c_customer_sk = 4);"
    ),
    waiter_count=3,
    holder_followup_sql="SELECT now();",
    noise_sql="SELECT c_customer_sk FROM customer WHERE c_customer_sk = 2 FOR UPDATE;",
    decoy_sqls=(),
    decoy_wait_sqls=(
        "UPDATE customer SET c_salutation = 'Ms.' WHERE c_customer_sk = 2;",
    ),
    background_sql="SELECT count(*) FROM date_dim WHERE d_year = 2001;",
    idle_noise_count=2,
    short_tx_noise_count=1,
    background_query_apps=(),
)


class PgSystemFailureLockContentionScenario(PostgresScenario):
    scenario_id = "pg_system_failure_lock_contention"
    description = "Simulates lock contention by holding an uncommitted UPDATE transaction on a table."
    cases = (_CASE, _SIMPLE_CASE)

    def build_fault_plan(
        self,
        case: PgSystemFailureLockContentionCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureLockContentionInjector,
                config={
                    "table": case.table,
                    "update_sql": case.update_sql,
                    "ensure_row_sql": case.ensure_row_sql,
                    "waiter_count": case.waiter_count,
                    "holder_followup_sql": case.holder_followup_sql,
                    "noise_sql": case.noise_sql,
                    "decoy_sqls": case.decoy_sqls,
                    "decoy_wait_sqls": case.decoy_wait_sqls,
                    "background_sql": case.background_sql,
                    "idle_noise_count": case.idle_noise_count,
                    "short_tx_noise_count": case.short_tx_noise_count,
                    "background_query_apps": case.background_query_apps,
                    "review_lock_sql": case.review_lock_sql,
                    "review_app": PgSystemFailureLockContentionInjector.REVIEW_APP,
                    "review_job_ddl": case.review_job_ddl,
                },
            ),
        )
