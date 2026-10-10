from types import SimpleNamespace

import pytest

from src.execution.history.metrics import MetricQuery
from src.execution.tidb_history import build_slow_query_records, build_topsql_records, parse_docker_log_records, reject_tidb_public_historical_sql
from src.execution.tidb_metrics import (
    CASE_ONLY_METRICS,
    LivePrometheusMetricProvider,
    PdMetricSampler,
    SQL_BACKED_METRICS,
    TIDB_METRIC_CATALOG,
)
from tests.tidb.test_tidb_environment import FakeDeployment


BASE_MS = 1_700_000_000_000


def _prometheus_request(query, _start, _end, _step):
    value = "0.1" if "container_cpu_usage_seconds_total" in query else "1"
    values = [[BASE_MS / 1000, value], [(BASE_MS + 2_000) / 1000, value]]
    if " by (container_label_com_docker_compose_service)" in query:
        return [
            {"metric": {"container_label_com_docker_compose_service": service}, "values": values}
            for service in ("pd-0", "tikv-0", "tidb-0")
        ]
    if "by (instance" in query:
        return [{"metric": {"instance": "tidb-0:10080"}, "values": values}]
    return [{"metric": {}, "values": values}]


def test_prometheus_adapter_captures_catalog_metrics_and_variants():
    deployment = FakeDeployment()
    provider = LivePrometheusMetricProvider(
        deployment=deployment,
        run_id="adapter",
        request_range=_prometheus_request,
    )
    prometheus_metrics = tuple(sorted(
        TIDB_METRIC_CATALOG.metric_names
        - SQL_BACKED_METRICS
        - CASE_ONLY_METRICS
    ))
    frames = provider.capture(prometheus_metrics, BASE_MS, BASE_MS + 2_000, 2)
    assert {frame.metric for frame in frames} == set(prometheus_metrics)
    assert all(frame.timestamps_ms for frame in frames)


def test_case_only_sql_and_job_metrics_require_their_case_scoped_adapters():
    provider = LivePrometheusMetricProvider(
        deployment=FakeDeployment(),
        run_id="case-only-adapter",
        request_range=_prometheus_request,
    )
    with pytest.raises(RuntimeError, match="Case sampler"):
        provider.query(MetricQuery(
            metric="plan_cardinality",
            start_epoch_ms=BASE_MS,
            end_epoch_ms=BASE_MS + 2_000,
            step_seconds=2,
        ))
    with pytest.raises(RuntimeError, match="Case WorkloadRunner"):
        provider.query(MetricQuery(
            metric="workload_profile",
            start_epoch_ms=BASE_MS,
            end_epoch_ms=BASE_MS + 2_000,
            step_seconds=2,
        ))


def test_prometheus_adapter_rejects_missing_disk_io_service():
    def missing_write(query, start, end, step):
        if "container_fs_writes_bytes_total" in query:
            return []
        return _prometheus_request(query, start, end, step)

    provider = LivePrometheusMetricProvider(
        deployment=FakeDeployment(),
        run_id="disk-io-missing",
        request_range=missing_write,
    )
    with pytest.raises(RuntimeError, match="disk_io query is missing database services"):
        provider.query(MetricQuery(metric="disk_io", start_epoch_ms=BASE_MS, end_epoch_ms=BASE_MS + 2_000))


def test_tidb_log_and_record_adapters_keep_contract_fields():
    records = parse_docker_log_records(
        "2023-11-14T22:13:20.000000000Z [INFO] tidb: target onset\n"
        "2023-11-14T22:13:22.000000000Z WARN pd: scheduler settled\n",
        "tidb/tidb-0",
        BASE_MS,
        BASE_MS + 4_000,
    )
    assert [record.timestamp_ms for record in records] == [BASE_MS, BASE_MS + 2_000]
    assert records[0].payload["component"] == "tidb"
    compose_records = parse_docker_log_records(
        "pd-0-1  | 2023-11-14T22:13:20.000000000Z [INFO] pd: scheduler started\n"
        "pd-0-1  | # stack continuation\n",
        "pd/pd-0",
        BASE_MS,
        BASE_MS + 1_000,
    )
    assert compose_records[0].payload["component"] == "pd"
    assert compose_records[0].payload["message"].endswith("\n# stack continuation")
    with pytest.raises(ValueError, match="explicit timezone"):
        parse_docker_log_records("2023-11-14T22:13:20 tidb: no timezone", "tidb/tidb-0", BASE_MS, BASE_MS + 1_000)
    with pytest.raises(ValueError, match="continuation line"):
        parse_docker_log_records("# orphan continuation", "tidb/tidb-0", BASE_MS, BASE_MS + 1_000)

    topsql = build_topsql_records([{
        "INSTANCE": "tidb-0",
        "DIGEST": "digest-1",
        "PLAN_DIGEST": "plan-1",
        "DIGEST_TEXT": "select * from target",
        "EXEC_COUNT": 3,
        "AVG_LATENCY": 12.5,
        "SUM_LATENCY": 37.5,
        "SUMMARY_BEGIN_TIME": BASE_MS,
        "SUMMARY_END_TIME": BASE_MS + 2_000,
    }], "cluster", BASE_MS, BASE_MS + 4_000)
    assert topsql[0].payload["plan_digest"] == "plan-1"

    slow = build_slow_query_records([{
        "TIME": BASE_MS + 1_000,
        "INSTANCE": "tidb-0",
        "DIGEST": "digest-1",
        "QUERY": "select * from target",
        "QUERY_TIME": 101.0,
        "PROCESS_TIME": 88.0,
        "WAIT_TIME": 13.0,
        "BACKOFF_TIME": 2.0,
        "TOTAL_KEYS": 12,
        "PROCESS_KEYS": 9,
        "MEM_MAX": 1024,
        "DISK_MAX": 0,
    }], "cluster", BASE_MS, BASE_MS + 4_000)
    assert slow[0].payload["query_time_ms"] == 101.0


def test_tidb_sql_guard_rejects_physical_history_and_allows_current_state():
    reject_tidb_public_historical_sql("SELECT * FROM benchops.current_state")
    with pytest.raises(ValueError, match="physical historical telemetry"):
        reject_tidb_public_historical_sql("SELECT * FROM INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY")
    with pytest.raises(ValueError, match="physical historical telemetry"):
        reject_tidb_public_historical_sql("WITH rows AS (SELECT * FROM information_schema.statements_summary) SELECT * FROM rows")


def test_tidb_sql_guard_allows_resource_group_repair_and_rejects_other_commands():
    reject_tidb_public_historical_sql(
        "ALTER RESOURCE GROUP mf_rg01_checkout RU_PER_SEC = 700 BURSTABLE=FALSE"
    )
    with pytest.raises(ValueError, match="uninspectable SQL commands"):
        reject_tidb_public_historical_sql("LOCK TABLES benchops_mf_rg01.orders READ")


def test_tidb_sql_guard_rejects_unqualified_and_dynamic_history_access():
    for query in (
        "USE information_schema; SELECT * FROM cluster_slow_query",
        "SELECT * FROM cluster_slow_query",
        "PREPARE history_stmt FROM 'SELECT * FROM information_schema.cluster_slow_query'",
    ):
        with pytest.raises(ValueError, match="(?i)histor"):
            reject_tidb_public_historical_sql(query)


def test_prometheus_capture_rejects_shifted_timestamps():
    def shifted_request(_query, start, _end, _step):
        values = [[(start + 1_000) / 1000, "1"], [(start + 3_000) / 1000, "1"]]
        return [{"metric": {}, "values": values}]

    provider = LivePrometheusMetricProvider(
        deployment=FakeDeployment(),
        run_id="shifted-capture",
        request_range=shifted_request,
    )
    with pytest.raises(RuntimeError, match="shifted"):
        provider.capture(("qps",), BASE_MS, BASE_MS + 2_000, 2)


def test_pd_metric_sampler_starts_with_a_synchronous_sample(monkeypatch):
    sampler = PdMetricSampler(
        deployment=SimpleNamespace(),
        run_id="pd-initial-sample",
        sample_interval_sec=1,
    )
    timestamps = []

    def read_snapshot(timestamp_ms):
        timestamps.append(timestamp_ms)
        return SimpleNamespace(timestamp_ms=timestamp_ms)

    monkeypatch.setattr(sampler, "_read_snapshot", read_snapshot)
    sampler.start()
    sampler.stop()

    assert timestamps
    assert sampler._snapshots[0].timestamp_ms == timestamps[0]
