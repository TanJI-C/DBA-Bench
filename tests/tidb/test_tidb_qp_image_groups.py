import shutil

from src.scenarios.tidb import (
    TidbQueryPerfCaseWhenInCartesianSemiJoinScenario,
    TidbQueryPerfIndexMergeSelectionFailureScenario,
    TidbQueryPerfIndexOrderCorrelationScenario,
    TidbQueryPerfLikeEscapeRangeScenario,
    TidbQueryPerfNoncoveringIndexTailLatencyScenario,
    TidbQueryPerfOptimisticWriteConflictScenario,
    TidbQueryPerfStatisticsDriftScenario,
)
from src.scenarios.tidb.runtime import tidb_runtime, TIDB_V8_1_0
from src.execution.deployment import TiDBDockerDeployment


QP_SCENARIO_TYPES = (
    TidbQueryPerfIndexOrderCorrelationScenario,
    TidbQueryPerfOptimisticWriteConflictScenario,
    TidbQueryPerfIndexMergeSelectionFailureScenario,
    TidbQueryPerfStatisticsDriftScenario,
    TidbQueryPerfNoncoveringIndexTailLatencyScenario,
    TidbQueryPerfCaseWhenInCartesianSemiJoinScenario,
    TidbQueryPerfLikeEscapeRangeScenario,
)


def test_all_tidb_qp_cases_declare_unique_image_group_keys():
    scenarios = [scenario_type() for scenario_type in QP_SCENARIO_TYPES]
    keys = [scenario.cases[0].runtime.image_group_key for scenario in scenarios]

    assert all(keys)
    assert len(keys) == len(set(keys))
    assert all("storage" not in key for key in keys)


def test_runtime_image_group_key_configures_deployment(tmp_path, monkeypatch):
    monkeypatch.setenv("AIOPS_TIDB_IMAGE_GROUP_DIR", str(tmp_path / "groups"))
    runtime = tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=1,
        tikv_count=1,
        tidb_count=1,
        image_group_key="qp-runtime-contract",
    )
    deployment = TiDBDockerDeployment(run_id="runtime-contract", port_base=4820)
    deployment.configure_runtime(runtime)

    try:
        assert deployment.image_group_key == "qp-runtime-contract"
        assert deployment.image_group_snapshot_name().startswith(
            "aiopsbench-tidb-group-qp-runtime-contract-"
        )
        assert deployment.bootstrap_cache_path is None
        assert deployment.persistent_storage_enabled is False
    finally:
        shutil.rmtree(deployment.runtime_dir)
