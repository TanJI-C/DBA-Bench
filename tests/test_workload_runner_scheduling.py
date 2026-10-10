import threading
import time

from src.scenarios.workloads import WorkloadProfile
from src.scenarios.runtime.workload_runner import WorkloadRunner


class RecordingRunner(WorkloadRunner):
    def _execute_one(self, profile):
        with self._lock:
            self._stats[profile.name]["attempts"] += 1
            self._stats[profile.name]["successes"] += 1
            self._stats[profile.name]["latencies_ms"].append(0.0)


def run_counts(worker_count):
    runner = RecordingRunner(
        env=None,
        profiles=[
            WorkloadProfile(name="fast", sql="SELECT 1", qps=20),
            WorkloadProfile(name="slow", sql="SELECT 1", qps=10),
        ],
        worker_count=worker_count,
        seed=7,
    )
    runner.start()
    time.sleep(0.6)
    runner.stop()
    return {name: values["attempts"] for name, values in runner.get_observed()["profiles"].items()}


def test_worker_count_does_not_multiply_qps_and_profile_ratio_is_preserved():
    one_worker = run_counts(1)
    three_workers = run_counts(3)
    assert abs(one_worker["fast"] - three_workers["fast"]) <= 1
    assert abs(one_worker["slow"] - three_workers["slow"]) <= 1
    assert 1.7 <= one_worker["fast"] / one_worker["slow"] <= 2.3


def test_stop_does_not_drain_queue_or_cancel_connections():
    class PendingQueue:
        def get_nowait(self):
            raise AssertionError("stop must not walk the pending workload queue")

    class ActiveConnection:
        closed = False

        def cancel(self):
            raise AssertionError("stop must not issue an unbounded connection cancel")

    runner = RecordingRunner(
        env=None,
        profiles=[WorkloadProfile(name="probe", sql="SELECT 1", qps=1)],
        worker_count=1,
    )
    runner._queue = PendingQueue()
    runner._worker_connections = {object(): ActiveConnection()}

    runner.stop(join_timeout=0)


def test_observation_activity_keeps_low_frequency_profiles_outside_recent_ring():
    runner = WorkloadRunner(
        env=None,
        profiles=[
            WorkloadProfile(name="target", sql="SELECT 1", qps=4),
            WorkloadProfile(name="decoy", sql="SELECT 1", qps=0.1),
        ],
        worker_count=1,
    )
    with runner._lock:
        runner._stats["target"].update(
            attempts=120,
            successes=120,
            failures=0,
            last_ok=True,
        )
        runner._stats["target"]["successful_latencies_ms"].extend([10.0] * 120)
        runner._stats["decoy"].update(
            attempts=1,
            successes=1,
            failures=0,
            last_ok=True,
        )
        runner._stats["decoy"]["successful_latencies_ms"].append(200.0)

    activity = runner.get_observation_activity(limit=100)
    assert {item["fingerprint"] for item in activity["value"]} == {"target", "decoy"}
    assert activity["total_runs"] == 121
    assert activity["window_seconds"] >= 0.0


def test_observation_window_discards_work_queued_before_window():
    runner = WorkloadRunner(
        env=None,
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=4)],
        worker_count=1,
    )
    runner._threads = [object()]
    runner._queue.put(runner.profiles[0])
    runner._queue.put(runner.profiles[0])
    with runner._lock:
        runner._stats["target"]["attempts"] = 2
        runner._stats["target"]["successes"] = 2

    runner.begin_observation_window()

    assert runner._queue.empty()
    assert runner.get_observation_activity()["total_runs"] == 0


def test_observation_priming_uses_real_profile_execution_path():
    runner = RecordingRunner(
        env=None,
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=1)],
        worker_count=1,
    )
    runner._threads = [object()]
    runner.prime_observation_profiles(("target",))

    assert runner.get_observation_activity()["total_runs"] == 1


def test_profile_attempt_warmup_requires_population_not_success_ratio():
    runner = WorkloadRunner(
        env=None,
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=4)],
        worker_count=1,
    )
    with runner._lock:
        runner._stats["target"].update(attempts=10, successes=8, failures=2)

    snapshot = runner.wait_for_profile_attempts(
        "target",
        minimum_attempts=10,
        timeout_seconds=0.1,
    )

    assert snapshot["ready"] is True
    assert snapshot["attempts"] == 10
    assert snapshot["successes"] == 8


def test_activity_p95_uses_nearest_rank_percentile():
    runner = WorkloadRunner(
        env=None,
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=4)],
        worker_count=1,
    )
    with runner._lock:
        runner._recent.extend(
            {
                "profile": "target",
                "tier": "MEDIUM",
                "exec_ms": float(value),
                "ok": True,
                "error": None,
                "session_setup_statements": 0,
            }
            for value in range(1, 21)
        )
        runner._stats["target"].update(
            attempts=20,
            successes=20,
            failures=0,
            last_ok=True,
        )
        runner._stats["target"]["successful_latencies_ms"].extend(
            float(value) for value in range(1, 21)
        )

    assert runner.get_activity()["value"][0]["p95_ms"] == 19.0
    assert runner.get_observation_activity()["value"][0]["p95_ms"] == 19.0
    assert runner.get_observation_activity()["value"][0]["p99_ms"] == 20.0


def test_activity_can_limit_to_a_recent_window(monkeypatch):
    runner = WorkloadRunner(
        env=None,
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=4)],
        worker_count=1,
    )
    now = 100.0
    monkeypatch.setattr("src.scenarios.runtime.workload_runner.time.time", lambda: now)
    with runner._lock:
        runner._recent.extend(
            {
                "timestamp": timestamp,
                "profile": "target",
                "tier": "MEDIUM",
                "exec_ms": latency,
                "ok": True,
                "error": None,
                "session_setup_statements": 0,
            }
            for timestamp, latency in ((70.0, 10.0), (95.0, 30.0))
        )
        runner.started_at = 0.0

    activity = runner.get_activity(window_seconds=10)

    assert activity["value"][0]["calls"] == 1
    assert activity["value"][0]["p99_ms"] == 30.0


def test_observation_activity_discards_completion_from_prior_window():
    class FakeEnvironment:
        def open_workload_connection(self, application_name, connection_pool):
            return object()

        def configure_workload_session(self, connection, profile):
            return None

        def execute_workload_profile(self, connection, profile):
            return {"session_setup_statements": 0}

    runner = WorkloadRunner(
        env=FakeEnvironment(),
        profiles=[WorkloadProfile(name="target", sql="SELECT 1", qps=1)],
        worker_count=1,
    )
    profile = runner.profiles[0]
    thread = threading.current_thread()
    thread._runner_observation_epoch = 0
    with runner._lock:
        runner._observation_epoch = 1

    runner._execute_one(profile)

    values = runner._stats[profile.name]
    assert values["successes"] == 0
    assert values["failures"] == 0
    assert values["successful_latencies_ms"] == []
