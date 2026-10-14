"""Schedule shared background workload profiles for an orchestration run."""
import heapq
import logging
import queue
import threading
import time
from collections import deque
from typing import Callable, List, Optional, Sequence

from src.database.query_results import nearest_rank_percentile
from src.execution.history.metrics import MetricFrame
from src.workloads.specs import WORKLOAD_LOCK_TIMEOUT, WORKLOAD_STATEMENT_TIMEOUT, WorkloadProfile
from src.workloads.tpcds import default_mix

logger = logging.getLogger(__name__)


class WorkloadRunner:
    """Schedule each profile at its declared QPS on a fixed worker pool."""

    RECENT_BUFFER_SIZE = 5000
    STATEMENT_TIMEOUT = WORKLOAD_STATEMENT_TIMEOUT  # HEAVY 档单条可跑 9s+，超时必须留足余量，否则 workload 大面积 fail 掩盖故障注入效果；临时文件爆盘由 cooldown 兜底。
    LOCK_TIMEOUT = WORKLOAD_LOCK_TIMEOUT
    APPLICATION_NAME = "aiopsbench_workload_runner"
    DEFAULT_WORKERS = 6  # 512MB/1CPU 容器下 6 worker 是平衡点：4 worker 吞吐不足（150s 仅 16 exec），8 worker 偶发 OOM。

    def __init__(
        self,
        env,
        profiles: Optional[List[WorkloadProfile]] = None,
        worker_count: Optional[int] = None,
        seed: int = 0,
        before_profile_hook: Optional[Callable[[], None]] = None,
    ):
        self.env = env
        self.profiles: List[WorkloadProfile] = list(profiles) if profiles is not None else list(default_mix())
        if any(profile.qps <= 0 for profile in self.profiles):
            invalid = [(profile.name, profile.qps) for profile in self.profiles if profile.qps <= 0]
            raise ValueError(f"Workload profile QPS must be positive: {invalid}")
        self._stop = threading.Event()
        self._threads: List[threading.Thread] = []
        self.worker_count = int(worker_count) if worker_count is not None else self.DEFAULT_WORKERS
        if self.worker_count <= 0:
            raise ValueError(f"WorkloadRunner worker_count must be positive, got {self.worker_count}")
        self.seed = seed
        self._before_profile_hook = before_profile_hook
        self._lock = threading.Lock()
        self._window_condition = threading.Condition(self._lock)
        self._active_executions = 0
        self._observation_transition = False
        self._recent: deque = deque(maxlen=self.RECENT_BUFFER_SIZE)
        self._metric_events: deque = deque(maxlen=20000)
        self._queue: queue.Queue = queue.Queue()
        self._worker_connections = {}
        self._observation_epoch = 0
        self._stats = {
            profile.name: {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "session_setup_statements": 0,
                "result_rows": 0,
                "latencies_ms": [],
                "successful_latencies_ms": [],
                "last_ok": None,
            }
            for profile in self.profiles
        }
        self.started_at = None
        self.stopped_at = None

    def set_before_profile_hook(self, hook: Callable[[], None]) -> None:
        if self._threads:
            raise RuntimeError("WorkloadRunner hooks must be configured before start")
        if self._before_profile_hook is not None:
            raise RuntimeError("WorkloadRunner before-profile hook is already configured")
        self._before_profile_hook = hook

    def start(self):
        if self._threads:
            raise RuntimeError("WorkloadRunner is already running")
        self._stop.clear()
        self.started_at = time.time()
        for i in range(self.worker_count):
            t = threading.Thread(target=self._worker_loop, name=f"workload-runner-{i}", daemon=True)
            t.start()
            self._threads.append(t)
        scheduler = threading.Thread(target=self._scheduler_loop, name="workload-scheduler", daemon=True)
        scheduler.start()
        self._threads.append(scheduler)
        logger.info("workload runner started: %d workers, %d profiles", self.worker_count, len(self.profiles))

    def stop(self, join_timeout: float = 35.0):
        self._stop.set()
        deadline = time.monotonic() + join_timeout
        for t in self._threads:
            t.join(timeout=max(0.0, deadline - time.monotonic()))
        alive = [t for t in self._threads if t.is_alive()]
        if alive:
            # 协作式停止超时后，卡在 SQL socket 读上的 worker 只能靠断开其
            # workload 连接解除阻塞；这是停机升级路径的一部分，不是兜底分支。
            logger.warning(
                "workload runner cooperative stop timed out, closing worker connections: %s",
                [t.name for t in alive],
            )
            for t in alive:
                for conn in getattr(t, "_runner_connections", {}).values():
                    try:
                        conn.close()
                    except Exception as exc:
                        logger.warning(
                            "workload runner connection close failed during stop: thread=%s error=%s",
                            t.name, exc,
                        )
            grace_deadline = time.monotonic() + 10.0
            for t in alive:
                t.join(timeout=max(0.0, grace_deadline - time.monotonic()))
        stopped_at = time.time()
        still_alive = [t.name for t in self._threads if t.is_alive()]
        if still_alive:
            raise RuntimeError(f"WorkloadRunner threads did not stop: {still_alive}")
        self.stopped_at = stopped_at
        self._threads = []

    def begin_observation_window(self, before_reset: Optional[Callable[[], None]] = None) -> None:
        if not self._threads:
            raise RuntimeError("WorkloadRunner observation window requires a running runner")
        with self._window_condition:
            if self._observation_transition:
                raise RuntimeError("WorkloadRunner observation window transition is already active")
            self._observation_transition = True
            deadline = time.monotonic() + 30.0
            while self._active_executions:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._observation_transition = False
                    self._window_condition.notify_all()
                    raise RuntimeError(
                        "WorkloadRunner observation window could not quiesce active executions: "
                        f"active_executions={self._active_executions}"
                    )
                self._window_condition.wait(remaining)
            try:
                while True:
                    try:
                        self._queue.get_nowait()
                    except queue.Empty:
                        break
                    else:
                        self._queue.task_done()
                self._close_idle_connections()
                if before_reset is not None:
                    before_reset()
                self._observation_epoch += 1
                self._recent.clear()
                for values in self._stats.values():
                    values["attempts"] = 0
                    values["successes"] = 0
                    values["failures"] = 0
                    values["session_setup_statements"] = 0
                    values["result_rows"] = 0
                    values["latencies_ms"].clear()
                    values["successful_latencies_ms"].clear()
                    values["last_ok"] = None
                self.started_at = time.time()
                self.stopped_at = None
            except BaseException:
                self._observation_transition = False
                self._window_condition.notify_all()
                raise
            self._observation_transition = False
            self._window_condition.notify_all()

    def wait_for_successful_observation(self, timeout_seconds: float) -> dict:
        if not self._threads:
            raise RuntimeError("WorkloadRunner observation wait requires a running runner")
        if timeout_seconds <= 0:
            raise ValueError(
                f"WorkloadRunner observation wait timeout must be positive: timeout_seconds={timeout_seconds}"
            )
        deadline = time.monotonic() + timeout_seconds
        profile_names = tuple(self._stats)
        while True:
            with self._lock:
                attempts = {name: self._stats[name]["attempts"] for name in profile_names}
                successes = {name: self._stats[name]["successes"] for name in profile_names}
            ready = all(successes[name] > 0 for name in profile_names)
            snapshot = {
                "ready": ready,
                "attempts": attempts,
                "successes": successes,
                "timeout_seconds": timeout_seconds,
            }
            if ready:
                return snapshot
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return snapshot
            self._stop.wait(min(0.05, remaining))

    def wait_for_profile_attempts(
        self,
        profile_name: str,
        *,
        minimum_attempts: int,
        timeout_seconds: float,
    ) -> dict:
        """Wait for a minimum sample population without asserting its health."""
        if profile_name not in self._stats:
            raise ValueError(f"unknown workload profile: profile_name={profile_name!r}")
        if minimum_attempts <= 0:
            raise ValueError(f"minimum_attempts must be positive: minimum_attempts={minimum_attempts!r}")
        if timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive: timeout_seconds={timeout_seconds!r}")
        deadline = time.monotonic() + timeout_seconds
        while True:
            with self._lock:
                attempts = int(self._stats[profile_name]["attempts"])
                successes = int(self._stats[profile_name]["successes"])
            snapshot = {
                "ready": attempts >= minimum_attempts,
                "profile_name": profile_name,
                "minimum_attempts": minimum_attempts,
                "attempts": attempts,
                "successes": successes,
                "timeout_seconds": timeout_seconds,
            }
            if snapshot["ready"]:
                return snapshot
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return snapshot
            self._stop.wait(min(0.05, remaining))

    def prime_observation_profiles(self, profile_names: Sequence[str]) -> None:
        """Execute named profiles once after a reset using the real workload path."""
        if not self._threads:
            raise RuntimeError("WorkloadRunner observation priming requires a running runner")
        profiles = {profile.name: profile for profile in self.profiles}
        missing = [name for name in profile_names if name not in profiles]
        if missing:
            raise RuntimeError(f"WorkloadRunner cannot prime unknown profiles: profiles={missing!r}")
        for name in profile_names:
            self._execute_one(profiles[name])

    def _close_idle_connections(self) -> None:
        connections = tuple(self._worker_connections.items())
        self._worker_connections.clear()
        for (thread, key), connection in connections:
            thread_connections = getattr(thread, "_runner_connections", {})
            thread_connections.pop(key, None)
            connection_started_at = getattr(thread, "_runner_connection_started_at", {})
            connection_started_at.pop(key, None)
            if not getattr(connection, "closed", False) and getattr(connection, "open", True):
                self.env.close_workload_connection(connection)

    def _enter_execution(self) -> None:
        with self._window_condition:
            while self._observation_transition:
                self._window_condition.wait()
            self._active_executions += 1

    def _leave_execution(self) -> None:
        with self._window_condition:
            self._active_executions -= 1
            if self._active_executions < 0:
                raise RuntimeError(
                    "WorkloadRunner active execution count became negative: "
                    f"active_executions={self._active_executions}"
                )
            if self._active_executions == 0:
                self._window_condition.notify_all()

    @staticmethod
    def _connection_key(profile: WorkloadProfile) -> tuple[str, Optional[str]]:
        if profile.connection_pool is not None:
            return ("pool", profile.connection_pool)
        return ("target", profile.target)

    def _ensure_connection(self, profile: WorkloadProfile) -> bool:
        """Keep one connection per worker and workload route."""
        t = threading.current_thread()
        connections = getattr(t, "_runner_connections", {})
        connection_started_at = getattr(t, "_runner_connection_started_at", {})
        key = self._connection_key(profile)
        conn = connections.get(key)
        if conn is not None and self.env.should_recycle_workload_connection(conn):
            self._close_connection(profile, conn)
            connections.pop(key)
            connection_started_at.pop(key)
            with self._lock:
                self._worker_connections.pop((t, key), None)
            conn = None
        if conn is not None:
            refresh_seconds = profile.connection_refresh_seconds
            if (
                refresh_seconds is not None
                and time.monotonic() - connection_started_at[key] >= refresh_seconds
            ):
                self._close_connection(profile, conn)
                connections.pop(key, None)
                connection_started_at.pop(key, None)
                with self._lock:
                    self._worker_connections.pop((t, key), None)
                conn = None
        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
            except Exception:
                self._close_connection(profile, conn)
                connections.pop(key, None)
                connection_started_at.pop(key, None)
                with self._lock:
                    self._worker_connections.pop((t, key), None)
        try:
            application_name = profile.application_name or self.APPLICATION_NAME
            if profile.connection_pool is not None:
                conn = self.env.open_workload_connection(
                    application_name,
                    profile.connection_pool,
                )
            elif profile.target is None:
                conn = self.env.open_workload_connection(application_name)
            else:
                conn = self.env.open_workload_connection(
                    application_name,
                    target=profile.target,
                )
            if profile.connection_setup_statements or profile.session_setup is not None:
                self.env.initialize_workload_session(conn, profile)
        except Exception as exc:
            logger.warning(
                "workload runner connect failed: route=%s application=%s error=%s",
                key,
                application_name,
                exc,
            )
            return False
        connections[key] = conn
        connection_started_at[key] = time.monotonic()
        t._runner_connections = connections
        t._runner_connection_started_at = connection_started_at
        with self._lock:
            self._worker_connections[(t, key)] = conn
        return True

    def _close_connection(self, profile: WorkloadProfile, connection) -> None:
        self.env.close_workload_connection(connection)

    def _scheduler_loop(self):
        now = time.monotonic()
        schedule = [(now, index, profile) for index, profile in enumerate(self.profiles)]
        heapq.heapify(schedule)
        while not self._stop.is_set():
            next_run_at, index, profile = heapq.heappop(schedule)
            if self._stop.wait(max(0.0, next_run_at - time.monotonic())):
                break
            period = profile.activity_period_seconds
            active = profile.activity_active_seconds
            if period is None or active is None or (time.monotonic() - now) % period < active:
                self._queue.put(profile)
            heapq.heappush(schedule, (next_run_at + 1.0 / profile.qps, index, profile))

    def _worker_loop(self):
        try:
            while not self._stop.is_set():
                try:
                    profile = self._queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                try:
                    with self._lock:
                        observation_epoch = self._observation_epoch
                    threading.current_thread()._runner_observation_epoch = observation_epoch
                    self._execute_one(profile)
                finally:
                    self._queue.task_done()
        finally:
            thread = threading.current_thread()
            for conn in getattr(thread, "_runner_connections", {}).values():
                if not getattr(conn, "closed", False) and getattr(conn, "open", True):
                    self.env.close_workload_connection(conn)
            with self._lock:
                for key in tuple(self._worker_connections):
                    if key[0] is thread:
                        self._worker_connections.pop(key, None)
            thread._runner_connections = {}
            thread._runner_connection_started_at = {}

    def _execute_one(self, profile: WorkloadProfile):
        self._enter_execution()
        try:
            with self._lock:
                thread = threading.current_thread()
                observation_epoch = getattr(thread, "_runner_observation_epoch", self._observation_epoch)
                if observation_epoch != self._observation_epoch:
                    return
                self._stats[profile.name]["attempts"] += 1
            if self._before_profile_hook is not None:
                self._before_profile_hook()
            if not self._ensure_connection(profile):
                with self._lock:
                    if observation_epoch != self._observation_epoch:
                        return
                    event = {
                        "timestamp": time.time(),
                        "profile": profile.name,
                        "tier": profile.tier,
                        "exec_ms": 0.0,
                        "ok": False,
                        "error": "connection_failed",
                        "session_setup_statements": 0,
                        "result_rows": 0,
                    }
                    self._metric_events.append(event)
                    self._recent.append(event)
                    self._stats[profile.name]["failures"] += 1
                    self._stats[profile.name]["last_ok"] = False
                return
            conn = getattr(thread, "_runner_connections", {}).get(self._connection_key(profile))
            if conn is None:
                raise RuntimeError(
                    f"WorkloadRunner connection disappeared after successful acquisition: "
                    f"profile={profile.name!r}, connection_pool={profile.connection_pool!r}, "
                    f"target={profile.target!r}"
                )
            start = time.monotonic()
            ok = False
            err = None
            session_setup_statements = 0
            result_rows = 0
            try:
                self.env.configure_workload_session(conn, profile)
                execution = self.env.execute_workload_profile(conn, profile)
                session_setup_statements = int(execution["session_setup_statements"])
                result_rows = int(execution["result_rows"])
                ok = True
            except Exception as exc:
                err = str(exc)[:200]
                try:
                    conn.rollback()
                except Exception:
                    pass
            elapsed_ms = round((time.monotonic() - start) * 1000.0, 2)
            record_event = getattr(self.env, "record_operation_event", None)
            if callable(record_event):
                record_event(
                    event_type="workload_execution",
                    entity_type="workload_profile",
                    entity=profile.name,
                    action="execute",
                    status="completed" if ok else "failed",
                    correlation_id=f"workload-{observation_epoch}-{profile.name}",
                    details={
                        "duration_ms": elapsed_ms,
                        "result_rows": result_rows,
                        "tier": profile.tier,
                        "error": err,
                    },
                )
            with self._lock:
                if observation_epoch != self._observation_epoch:
                    return
                self._recent.append({
                    "timestamp": time.time(),
                    "profile": profile.name,
                    "tier": profile.tier,
                    "exec_ms": elapsed_ms,
                    "ok": ok,
                    "error": err,
                    "session_setup_statements": session_setup_statements,
                    "result_rows": result_rows,
                })
                self._metric_events.append(self._recent[-1])
                if ok:
                    self._stats[profile.name]["successes"] += 1
                    self._stats[profile.name]["session_setup_statements"] += session_setup_statements
                    self._stats[profile.name]["result_rows"] += result_rows
                    self._stats[profile.name]["successful_latencies_ms"].append(elapsed_ms)
                else:
                    self._stats[profile.name]["failures"] += 1
                self._stats[profile.name]["last_ok"] = ok
                self._stats[profile.name]["latencies_ms"].append(elapsed_ms)
                if "missing_idx" in profile.name or "q75" in profile.name:
                    logger.info("fault_fp exec: %s ok=%s elapsed=%.0fms err=%s", profile.name, ok, elapsed_ms, err)
                # 第一条成功执行时打印一次，确认 runner 跑通。
                if len(self._recent) == 1:
                    logger.info("workload runner first exec: %s in %.0fms ok=%s", profile.name, elapsed_ms, ok)
        finally:
            self._leave_execution()

    def get_activity(self, limit: int = 20, window_seconds: Optional[float] = None) -> dict:
        """Aggregate recent execs by profile. Returns sorted list by mean_ms desc.

        内存聚合，500 条记录的 sort+group ≈ 0.1ms。
        """
        with self._lock:
            recent = list(self._recent)
            started_at = self.started_at
        if window_seconds is not None:
            if window_seconds <= 0:
                raise ValueError(f"Workload activity window_seconds must be positive: {window_seconds!r}")
            cutoff = time.time() - float(window_seconds)
            recent = [item for item in recent if float(item["timestamp"]) >= cutoff]
        window_seconds = max(0.0, time.time() - started_at) if started_at is not None else 0.0
        return self._aggregate_activity(recent, window_seconds, limit)

    def get_activity_between(self, start_ts: float, end_ts: float, limit: int = 20) -> dict:
        """Aggregate execs whose timestamps fall inside [start_ts, end_ts]."""
        if end_ts <= start_ts:
            raise ValueError(
                f"Workload activity window must be non-empty: start_ts={start_ts!r}, end_ts={end_ts!r}"
            )
        with self._lock:
            recent = list(self._recent)
        recent = [
            item
            for item in recent
            if start_ts <= float(item["timestamp"]) <= end_ts
        ]
        return self._aggregate_activity(recent, round(end_ts - start_ts, 3), limit)

    def _aggregate_activity(self, recent: list, window_seconds: float, limit: int) -> dict:
        by_profile: dict = {}
        for r in recent:
            by_profile.setdefault(r["profile"], []).append(r)
        result = []
        for name, runs in by_profile.items():
            times = sorted(r["exec_ms"] for r in runs if r["ok"])
            n_ok = len(times)
            mean_ms = round(sum(times) / n_ok, 2) if n_ok else 0.0
            p95_ms = round(
                nearest_rank_percentile(times, 0.95) if times else 0.0,
                2,
            )
            p99_ms = round(
                nearest_rank_percentile(times, 0.99) if times else 0.0,
                2,
            )
            session_setup_statements = sum(
                int(run["session_setup_statements"])
                for run in runs
            )
            result.append({
                "fingerprint": name,
                "tier": runs[0]["tier"],
                "calls": len(runs),
                "ok_calls": n_ok,
                "fail_calls": len(runs) - n_ok,
                "mean_ms": mean_ms,
                "p95_ms": p95_ms,
                "p99_ms": p99_ms,
                "last_ok": runs[-1]["ok"],
                "session_setup_statements": session_setup_statements,
                "last_session_setup_statements": int(runs[-1]["session_setup_statements"]),
            })
        result.sort(key=lambda x: x["mean_ms"], reverse=True)
        return {
            "status": "success",
            "metric": "workload_activity",
            "total_runs": len(recent),
            "active_profiles": len(by_profile),
            "worker_count": self.worker_count,
            "window_seconds": round(window_seconds, 3),
            "value": result[:limit],
        }

    def get_observation_activity(self, limit: int = 20) -> dict:
        """Aggregate every execution in the current observation window."""
        with self._lock:
            started_at = self.started_at
            stats = {
                name: {
                    "attempts": values["attempts"],
                    "successes": values["successes"],
                    "failures": values["failures"],
                    "successful_latencies_ms": tuple(values["successful_latencies_ms"]),
                    "last_ok": values["last_ok"],
                }
                for name, values in self._stats.items()
            }
        window_seconds = max(0.0, time.time() - started_at) if started_at is not None else 0.0
        result = []
        for profile in self.profiles:
            values = stats[profile.name]
            if values["attempts"] == 0:
                continue
            times = sorted(values["successful_latencies_ms"])
            n_ok = len(times)
            mean_ms = round(sum(times) / n_ok, 2) if n_ok else 0.0
            p95_ms = round(
                nearest_rank_percentile(times, 0.95) if times else 0.0,
                2,
            )
            p99_ms = round(
                nearest_rank_percentile(times, 0.99) if times else 0.0,
                2,
            )
            result.append({
                "fingerprint": profile.name,
                "tier": profile.tier,
                "application_name": profile.application_name or self.APPLICATION_NAME,
                "calls": values["attempts"],
                "ok_calls": values["successes"],
                "fail_calls": values["failures"],
                "mean_ms": mean_ms,
                "p95_ms": p95_ms,
                "p99_ms": p99_ms,
                "last_ok": values["last_ok"],
            })
        result.sort(key=lambda item: item["mean_ms"], reverse=True)
        return {
            "status": "success",
            "metric": "workload_activity",
            "total_runs": sum(item["calls"] for item in result),
            "active_profiles": len(result),
            "worker_count": self.worker_count,
            "window_seconds": round(window_seconds, 3),
            "value": result[:limit],
        }

    def get_live_activity_counts(self) -> dict:
        """Return cumulative observation-window activity counters without latency ranking."""
        with self._lock:
            return {
                name: {
                    "calls": int(values["attempts"]),
                    "ok_calls": int(values["successes"]),
                    "fail_calls": int(values["failures"]),
                }
                for name, values in self._stats.items()
            }

    def capture_profile_metric(
        self,
        *,
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        profile_names: tuple[str, ...],
    ) -> MetricFrame:
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                "Workload profile metric capture window must be positive: "
                f"start_epoch_ms={start_epoch_ms}, end_epoch_ms={end_epoch_ms}"
            )
        if step_seconds <= 0:
            raise ValueError(f"Workload profile metric step must be positive: step_seconds={step_seconds}")
        known_profiles = {profile.name for profile in self.profiles}
        unknown = sorted(set(profile_names) - known_profiles)
        if unknown:
            raise ValueError(
                "Workload profile metric requested unknown profiles: "
                f"unknown={unknown!r}, known={sorted(known_profiles)!r}"
            )
        if not profile_names:
            raise ValueError("Workload profile metric requires at least one profile")
        with self._lock:
            events = tuple(
                event
                for event in self._metric_events
                if start_epoch_ms <= int(float(event["timestamp"]) * 1000) <= end_epoch_ms
                and event["profile"] in profile_names
            )
        timestamps = tuple(range(start_epoch_ms, end_epoch_ms + 1, step_seconds * 1000))
        series = {}
        timestamps_by_profile = {}
        for profile_name in profile_names:
            fields = {
                "ok_per_second": [],
                "error_per_second": [],
                "p95_ms": [],
            }
            for bucket_start in timestamps:
                bucket_end = min(bucket_start + step_seconds * 1000, end_epoch_ms)
                bucket_events = tuple(
                    event
                    for event in events
                    if event["profile"] == profile_name
                    and bucket_start <= int(float(event["timestamp"]) * 1000) < bucket_end
                )
                ok_latencies = sorted(
                    float(event["exec_ms"])
                    for event in bucket_events
                    if event["ok"]
                )
                fields["ok_per_second"].append(sum(1 for event in bucket_events if event["ok"]) / step_seconds)
                fields["error_per_second"].append(sum(1 for event in bucket_events if not event["ok"]) / step_seconds)
                fields["p95_ms"].append(
                    nearest_rank_percentile(ok_latencies, 0.95) if ok_latencies else 0.0
                )
            series[profile_name] = {
                field: tuple(values)
                for field, values in fields.items()
            }
            timestamps_by_profile[profile_name] = timestamps
        return MetricFrame(
            metric="workload_profile",
            query_target=None,
            step_seconds=step_seconds,
            series=series,
            timestamps_ms=timestamps_by_profile,
        )

    def get_observed(self) -> dict:
        ended_at = self.stopped_at or time.time()
        duration = ended_at - self.started_at if self.started_at else 0.0
        profiles = {}
        with self._lock:
            stats = {name: dict(values) for name, values in self._stats.items()}
        for name, values in stats.items():
            latencies = values.pop("latencies_ms")
            values.pop("successful_latencies_ms")
            values.pop("last_ok")
            ordered_latencies = sorted(latencies)
            p95_index = min(len(ordered_latencies) - 1, max(0, int(len(ordered_latencies) * 0.95))) if ordered_latencies else 0
            p99_index = min(len(ordered_latencies) - 1, max(0, int(len(ordered_latencies) * 0.99))) if ordered_latencies else 0
            profiles[name] = {
                **values,
                "actual_qps": values["attempts"] / duration if duration else 0.0,
                "success_qps": values["successes"] / duration if duration else 0.0,
                "mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
                "p95_latency_ms": ordered_latencies[p95_index] if ordered_latencies else 0.0,
                "p99_latency_ms": ordered_latencies[p99_index] if ordered_latencies else 0.0,
            }
        return {
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "duration_seconds": duration,
            "profiles": profiles,
        }
