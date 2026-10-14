import json
import random
import re
import time
from collections.abc import Callable, Iterable
from typing import List

from src.workloads.specs import WorkloadProfile
from src.workloads.tpcds import LIGHT_IDS, MEDIUM_IDS

_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def _validate_sql_identifier(value: str, name: str) -> str:
    # 这些名称会被拼进 DROP/CREATE INDEX 等 DDL，必须先收窄到普通 identifier。
    if not _SQL_IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid SQL identifier for {name}: {value!r}")
    return value


def _require_sql_success(result, context: str):
    payload = json.loads(result) if isinstance(result, str) else result
    if isinstance(payload, dict) and payload.get("status") == "error":
        raise RuntimeError(f"{context} failed: {result}")
    return result


def _json_response(result, context: str) -> dict:
    payload = json.loads(result) if isinstance(result, str) else result
    if not isinstance(payload, dict):
        raise TypeError(f"{context} expected a JSON object, got {type(payload).__name__}")
    return payload


def _json_object(result, context: str) -> dict:
    payload = _json_response(result, context)
    if payload.get("status") == "error":
        raise RuntimeError(f"{context} failed: {result}")
    return payload


def _run_cleanup_steps(
    context: str,
    steps: Iterable[tuple[str, Callable[[], object]]],
) -> None:
    failures = []
    for operation, step in steps:
        try:
            step()
        except Exception as exc:
            failures.append((operation, exc))
    if failures:
        details = "; ".join(
            f"{operation}: {type(exc).__name__}: {exc}"
            for operation, exc in failures
        )
        raise RuntimeError(f"{context} failed: {details}") from failures[0][1]


def _join_thread(thread, timeout: float, context: str) -> None:
    thread.join(timeout=timeout)
    if thread.is_alive():
        raise RuntimeError(f"{context} did not stop within {timeout} seconds")


def _cancel_open_connection(connection) -> None:
    if not connection.closed:
        connection.cancel()


class PgQueryPerfFaultFingerprintProbe:
    """Mixin: 在 inject() 末尾启动后台线程，循环跑 TPC-DS 重型 fingerprint，
    让 pg_stat_statements 持续更新，agent 通过 topsql / pg_stat_statements 找到故障 SQL。

    7 个真 query_perf 场景（missing_index / stale_statistics /
    parameter_sniffing / heavy_offset_pagination / implicit_type_conversion /
    sort_spill / suboptimal_join）的 Injector 都 mix in 这个基类，inject() 末尾
    调一次 _start_fault_fingerprint_probe()，recover() 末尾调一次
    _terminate_fault_fingerprint_probe()。SQL 含 $1 时自动走 PREPARE + EXECUTE 路径。
    """
    _fp_app_name: str = "aiopsbench_fault_fp"
    _fp_interval_seconds: float = 3.0
    _fp_default_bind_year: int = 2000

    def _query_observability_evidence(self, env):
        return {
            "topsql": env.query_metrics("topsql"),
            "slow_queries": env.query_metrics("slow_queries"),
        }

    def _env_supports_background_probe(self) -> bool:
        # 单元测试里 env 常是 MagicMock；只有真实 PGEnv 具备这些连接字段时才启动后台线程。
        return (
            isinstance(getattr(self.env, "host", None), str)
            and isinstance(getattr(self.env, "port", None), int)
            and isinstance(getattr(self.env, "user", None), str)
            and isinstance(getattr(self.env, "password", None), str)
            and isinstance(getattr(self.env, "dbname", None), str)
        )

    def _start_fault_fingerprint_probe(
        self,
        sql: str,
        app_name: str = None,
        interval_seconds: float = None,
        bind_year: int = None,
        db_user: str = None,
        db_password: str = None,
        idle_sleep: bool = False,
    ):
        """启动后台线程循环跑 fault fingerprint SQL。

        sql：完整的 TPC-DS 重型 SQL（可能含 $1 参数占位符）。
        app_name：connection application_name，用于清理时精确定位。
        interval_seconds：每次 execute 后的 sleep 间隔，qps ≈ 1/interval。
        bind_year：$1 占位符的 bind 值（仅在 sql 含 $1 时生效）。
        idle_sleep：True 时用 Python 侧 sleep，probe 连接在间歇期回到 idle，
        pg_stat_activity 的 last query 保留故障 SQL 字面量；默认 pg_sleep 保持
        连接 active，供 slow_queries running 分支观测。

        用 psycopg2 + autocommit + 独立 connection，不阻塞主流程。
        """
        import threading

        if not self._env_supports_background_probe():
            return
        if not sql:
            return
        # 先清理同 app_name 的旧连接，避免重复启动累积。
        self._terminate_fault_fingerprint_probe(app_name)

        app_name = app_name or self._fp_app_name
        interval = float(interval_seconds or self._fp_interval_seconds)
        bind_year = int(bind_year or self._fp_default_bind_year)
        has_placeholder = "$1" in sql

        self._fp_state = {
            "thread": None,
            "conn": None,
            "stopping": False,
            "app_name": app_name,
            "sql": sql,
            "has_placeholder": has_placeholder,
            "interval": interval,
            "bind_year": bind_year,
            "idle_sleep": bool(idle_sleep),
            "db_user": db_user or self.env.user,
            "db_password": db_password or self.env.password,
        }
        t = threading.Thread(
            target=self._run_fault_fingerprint_probe,
            daemon=True,
            name=f"fault-fp-{app_name}",
        )
        self._fp_state["thread"] = t
        t.start()

    def _run_fault_fingerprint_probe(self):
        import psycopg2

        state = getattr(self, "_fp_state", None)
        if state is None:
            return
        sql = state["sql"]
        app_name = state["app_name"]
        has_placeholder = state["has_placeholder"]
        interval = state["interval"]
        bind_year = state["bind_year"]
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=state["db_user"],
                password=state["db_password"],
                dbname=self.env.dbname,
                connect_timeout=5,
                application_name=app_name,
            )
            conn.autocommit = True
            state["conn"] = conn
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '0';")
                # 第一次 execute 跑一次让 PG 解析 + 写入 pg_stat_statements；
                # 后续按 interval 秒循环。prepared statement 必须每条 connection 独立建。
                prep_name = f"aiops_fp_{app_name}"[:63]
                if has_placeholder:
                    cur.execute(f"PREPARE {prep_name} AS {sql.rstrip(';')}")
                    execute_sql = f"EXECUTE {prep_name}({bind_year})"
                else:
                    execute_sql = sql.rstrip(";")
                # 先跑一次预热（让 pg_stat_statements 有这条 fingerprint）
                if has_placeholder:
                    cur.execute(execute_sql)
                else:
                    cur.execute(execute_sql)
            while not state["stopping"]:
                with conn.cursor() as cur:
                    cur.execute(execute_sql)
                if interval > 0:
                    # 默认用 pg_sleep 代替 Python time.sleep，sleep 期间 connection
                    # 仍处于 active 状态，慢_queries 工具的 running 分支能看到这条 probe。
                    # idle_sleep=True 时改为 Python 侧 sleep：连接回到 idle，pg_stat_activity
                    # 的 last query 保留故障 SQL 字面量，为 Agent 提供可恢复的原文证据路径。
                    if state["idle_sleep"]:
                        time.sleep(interval)
                    else:
                        with conn.cursor() as cur:
                            cur.execute(f"SELECT pg_sleep({interval})")
        except Exception as exc:
            if state.get("stopping"):
                return
            text = str(exc)
            if "server closed the connection unexpectedly" in text or "terminating connection" in text:
                return
            cls_name = self.__class__.__name__
            print(f"[FaultInjector:{cls_name}] fault fingerprint probe stopped: {exc}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            if state is not None:
                state["conn"] = None

    def _terminate_fault_fingerprint_probe(self, app_name: str = None):
        state = getattr(self, "_fp_state", None)
        if state is None:
            # 即便没启动过，也按 app_name 清残留连接（teardown 兜底）。
            target_app = app_name or getattr(self, "_fp_app_name", "aiopsbench_fault_fp")
            self._terminate_fp_by_app_name(target_app)
            return
        state["stopping"] = True
        if self.env is not None:
            self._terminate_fp_by_app_name(state["app_name"])
        conn = state.get("conn")
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            state["conn"] = None
        thread = state.get("thread")
        if thread is not None and thread.is_alive():
            thread.join(timeout=5)
        self._fp_state = None

    def _terminate_fp_by_app_name(self, app_name: str):
        if not self._env_supports_background_probe():
            return
        try:
            self.env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name = '{app_name}'
                  AND pid <> pg_backend_pid();
            """)
        except Exception:
            # 兜底：terminate 失败也不抛出，避免阻塞 recover 流程。
            pass

def build_query_perf_noise_profiles(
    exclude_fingerprint_ids: set[int],
    light_n: int = 2,
    medium_n: int = 1,
    seed: int = 0x5170,
) -> tuple[WorkloadProfile, ...]:
    from src.workloads.tpcds import get_tpcdsx_query

    exclude = {int(value) for value in exclude_fingerprint_ids}
    light_pool = [query_id for query_id in LIGHT_IDS if query_id not in exclude]
    medium_pool = [query_id for query_id in MEDIUM_IDS if query_id not in exclude]
    if not light_pool or not medium_pool:
        raise ValueError(f"No query-performance noise available after excluding {exclude}")

    rng = random.Random(seed)
    profiles = []
    for query_id in rng.sample(light_pool, min(light_n, len(light_pool))):
        profiles.append(WorkloadProfile(
            name=f"tpcds_q{query_id}",
            sql=get_tpcdsx_query(f"q{query_id}"),
            qps=round(rng.uniform(0.3, 0.5), 3),
            tier="LIGHT",
        ))
    for query_id in rng.sample(medium_pool, min(medium_n, len(medium_pool))):
        profiles.append(WorkloadProfile(
            name=f"tpcds_q{query_id}",
            sql=get_tpcdsx_query(f"q{query_id}"),
            qps=round(rng.uniform(0.15, 0.25), 3),
            tier="MEDIUM",
        ))
    return tuple(profiles)

def build_checkpoint_log_noise_profiles() -> List[WorkloadProfile]:
    # checkpoint 场景专用，高频业务日志噪声把 PostgreSQL 自带
    # "increase max_wal_size" hint 挤出默认 read_log(pg_log, lines=200) 窗口。
    return [
        WorkloadProfile(
            name="checkpoint_log_noise_statement_timeout_dashboard_refresh",
            sql="SET LOCAL statement_timeout = '20ms'; SELECT pg_sleep(0.2);",
            qps=2.0,
            tier="LOG_NOISE",
        ),
        WorkloadProfile(
            name="checkpoint_log_noise_missing_billing_rollup",
            sql="SELECT count(*) FROM billing_rollup_cache_missing;",
            qps=1.2,
            tier="LOG_NOISE",
        ),
        WorkloadProfile(
            name="checkpoint_log_noise_invalid_order_batch",
            sql="SELECT ('order_batch_' || clock_timestamp())::integer;",
            qps=1.2,
            tier="LOG_NOISE",
        ),
        WorkloadProfile(
            name="checkpoint_log_noise_lock_timeout",
            sql="SET LOCAL lock_timeout = '10ms'; LOCK TABLE checkout_order_archive IN ACCESS EXCLUSIVE MODE;",
            qps=0.8,
            tier="LOG_NOISE",
        ),
    ]

def build_checkpoint_temp_spill_profiles() -> List[WorkloadProfile]:
    # checkpoint 场景专用，真实制造 temp file / sort spill 干扰。
    # Agent 查 pg_stat_database/temp_blks 时会看到 work_mem 方向的可信候选根因。
    return [
        WorkloadProfile(
            name="checkpoint_temp_spill_order_report",
            sql=(
                "SET LOCAL work_mem = '64kB'; "
                "SELECT ss_customer_sk, ss_item_sk, sum(ss_net_paid) AS paid "
                "FROM store_sales "
                "GROUP BY ss_customer_sk, ss_item_sk "
                "ORDER BY paid DESC, ss_customer_sk, ss_item_sk "
                "LIMIT 20000"
            ),
            qps=0.25,
            tier="TEMP_SPILL",
        ),
        WorkloadProfile(
            name="checkpoint_temp_spill_customer_rollup",
            sql=(
                "SET LOCAL work_mem = '64kB'; "
                "SELECT c_customer_sk, c_last_name, count(*) AS n "
                "FROM customer JOIN store_sales ON ss_customer_sk = c_customer_sk "
                "GROUP BY c_customer_sk, c_last_name "
                "ORDER BY n DESC, c_last_name "
                "LIMIT 20000"
            ),
            qps=0.2,
            tier="TEMP_SPILL",
        ),
    ]

def build_io_saturation_noise_profiles(table: str = "reporting_order_fact") -> List[WorkloadProfile]:
    """Business-shaped noise for the shared slow-query / I/O-pressure scenario.

    The profiles create plausible report, temp-spill, CPU, and log distractions.
    They should not reveal the actual background refresh worker that saturates
    I/O; that root cause remains discoverable through pg_stat_activity.
    """
    return [
        WorkloadProfile(
            name="regional_sales_dashboard_refresh",
            sql=(
                "SELECT region_id, status, count(*) AS orders, "
                "coalesce(sum(amount), 0) AS gross_amount "
                f"FROM {table} "
                "WHERE order_ts > now() - interval '180 days' "
                "GROUP BY region_id, status "
                "ORDER BY gross_amount DESC, region_id "
                "LIMIT 32"
            ),
            qps=0.35,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name="report_temp_spill_rollup",
            sql=(
                "SET LOCAL work_mem = '64kB'; "
                "SELECT customer_id, substring(payload, 1, 12) AS payload_bucket, "
                "coalesce(sum(amount), 0) AS paid "
                f"FROM {table} "
                "GROUP BY customer_id, payload_bucket "
                "ORDER BY paid DESC, customer_id "
                "LIMIT 5000"
            ),
            qps=0.20,
            tier="TEMP_SPILL",
        ),
        WorkloadProfile(
            name="invoice_cpu_rollup",
            sql=(
                "SELECT sum((g % 97) * (g % 89)) AS invoice_score "
                "FROM generate_series(1, 700000) AS g"
            ),
            qps=0.14,
            tier="CPU_NOISE",
        ),
        WorkloadProfile(
            name="order_status_touch_worker",
            sql=(
                f"UPDATE {table} "
                "SET amount = amount "
                "WHERE id = 17"
            ),
            qps=0.30,
            tier="LIGHT",
            commit=False,
        ),
        WorkloadProfile(
            name="missing_report_cache_log_noise",
            sql="SELECT count(*) FROM report_cache_rollup_missing;",
            qps=0.12,
            tier="LOG_NOISE",
        ),
    ]
