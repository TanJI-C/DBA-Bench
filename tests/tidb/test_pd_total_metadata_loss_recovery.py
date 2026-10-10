from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from examples.run_tidb_system_failure_pd_metadata_recovery_scenario import (
    build_full_pass_report,
)
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.scenarios.tidb.system_failure.pd_total_metadata_loss_recovery import (
    K03_DP_FACTORS,
    TidbSystemFailurePdTotalMetadataLossRecoveryInjector,
    extract_allocator_high_water,
    extract_original_cluster_id,
)
from src.execution.deployment import TiDBDockerDeployment, canonical_pd_config
from src.execution.environment import TiDBEnv
from src.execution.tidb_tool_definitions import TIDB_TOOL_DEFINITIONS


SCENARIO_ID = "tidb_system_failure_pd_metadata_recovery"
CASE_ID = "pd_all_metadata_lost_restore_original_cluster"
ORIGINAL_CLUSTER_ID = 111111111111
REBUILT_CLUSTER_ID = 222222222222
ALLOCATOR_HIGH_WATER = 9000
SAFE_ALLOCATOR_FLOOR = ALLOCATOR_HIGH_WATER + 1
STORE_IDS = (101, 102, 103)
REGION_COUNT = 16
PRE_FAULT_TSO = 100000000000
MAINTENANCE_RECORD_ID = "maintenance-1"


def _scenario_case():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == SCENARIO_ID)
    return scenario, scenario.get_case(CASE_ID)


def _success(result):
    return json.dumps({"status": "success", "result": result})


def test_k03_recovery_branch_schema_exposes_product_runbook_enum():
    resources = TIDB_TOOL_DEFINITIONS["manage_cluster"]["resource_definitions"]
    recovery = next(item for item in resources if item["resource_name"] == "pd_recovery")
    execute = next(
        item for item in recovery["operation_definitions"] if item["operation_name"] == "execute"
    )
    branch = next(
        item
        for item in execute["parameter_definitions"]
        if item["parameter_name"] == "recovery_branch"
    )

    assert branch["allowed_values"] == ["surviving_member", "entirely_rebuild"]
    assert "PD recovery knowledge" in branch["parameter_description"]
    assert "Method 1" not in branch["parameter_description"]
    assert "Method 2" not in branch["parameter_description"]


class FakeK03Deployment:
    COMPONENTS = {
        "pd": ("pd-0", "pd-1", "pd-2"),
        "tikv": ("tikv-0", "tikv-1", "tikv-2"),
        "tidb": ("tidb-0", "tidb-1"),
        "tiflash": (),
    }
    database_nodes = tuple(
        f"{component}/{component}-{index}"
        for component, count in (("pd", 3), ("tikv", 3), ("tidb", 2))
        for index in range(count)
    )
    NODES = {target: target.rsplit("/", 1)[1] for target in database_nodes}

    def __init__(self, *, stores=True):
        self.stores_present = stores
        self.clock_offset = 12

    def node_states(self):
        return {target: {"running": True} for target in self.database_nodes}

    def pd_request(self, method, path, body=None):
        assert method == "GET"
        assert body is None
        if path == "/pd/api/v1/cluster":
            return {"id": ORIGINAL_CLUSTER_ID, "max_peer_count": 3}
        if path == "/pd/api/v1/cluster/status":
            return {
                "raft_bootstrap_time": "2026-08-18T00:00:00Z",
                "is_initialized": True,
                "replication_status": "",
            }
        if path == "/pd/api/v1/members":
            return {"members": [{"name": name} for name in self.COMPONENTS["pd"]]}
        if path == "/pd/api/v1/leader":
            return {"name": "pd-0"}
        if path == "/pd/api/v1/stores":
            if not self.stores_present:
                return {"stores": []}
            return {
                "stores": [
                    {
                        "store": {"id": store_id, "state_name": "Up"},
                        "status": {"region_count": REGION_COUNT // 4},
                    }
                    for store_id in STORE_IDS
                ]
            }
        if path == "/pd/api/v1/config":
            return {"schedule": {"max-snapshot-count": 3}}
        raise AssertionError(path)

    def clock_status_observation(self):
        return {"max_abs_offset_ms": self.clock_offset, "observations": []}


class FakeK03Env:
    def __init__(self, *, stores=True):
        self.deployment = FakeK03Deployment(stores=stores)
        self.tso = PRE_FAULT_TSO

    def current_tso(self):
        self.tso += 10
        return self.tso

    def execute_sql(self, sql):
        normalized = sql.casefold()
        if "tikv_region_status" in normalized:
            rows = [[REGION_COUNT]]
        elif f"from bench_k03.{_scenario_case()[1].orders_table}" in normalized:
            case = _scenario_case()[1]
            rows = [[case.order_rows, case.expected_order_amount_sum, case.expected_order_checksum]]
        elif f"from bench_k03.{_scenario_case()[1].order_items_table}" in normalized:
            case = _scenario_case()[1]
            rows = [[case.item_rows, case.expected_item_qty_sum, case.expected_item_checksum]]
        elif "live_events" in normalized:
            rows = [[900001, "k03-reference-recovery"]]
        else:
            rows = [[1]]
        return _success(rows)


def _evidence(case):
    return {
        "original_cluster_id": ORIGINAL_CLUSTER_ID,
        "new_cluster_id": REBUILT_CLUSTER_ID,
        "allocator_high_water": ALLOCATOR_HIGH_WATER,
        "safe_allocator_floor": SAFE_ALLOCATOR_FLOOR,
        "pre_fault_tso": PRE_FAULT_TSO,
        "original_store_ids": STORE_IDS,
        "original_region_count": REGION_COUNT,
        "original_pd_config": {"schedule": {"max-snapshot-count": 3}},
        "business_truth": {
            "orders_count": case.order_rows,
            "orders_amount_sum": case.expected_order_amount_sum,
            "orders_checksum": case.expected_order_checksum,
            "items_count": case.item_rows,
            "items_qty_sum": case.expected_item_qty_sum,
            "items_checksum": case.expected_item_checksum,
        },
        "clock_offset_limit_ms": case.clock_offset_limit_ms,
        "fault_record_id": MAINTENANCE_RECORD_ID,
        "mismatch_targets": ("tikv/tikv-0", "tikv/tikv-1", "tikv/tikv-2"),
    }


def _service_event(operation, target):
    return {
        "api": "manage_cluster",
        "args": {"resource": "service", "operation": operation, "target": target},
        "result": {"status": "success"},
    }


def _recovery_event(
    *,
    cluster_id=ORIGINAL_CLUSTER_ID,
    alloc_id=SAFE_ALLOCATOR_FLOOR,
    recovery_branch="entirely_rebuild",
    record_id=MAINTENANCE_RECORD_ID,
):
    return {
        "api": "manage_cluster",
        "args": {
            "resource": "pd_recovery",
            "operation": "execute",
            "target": "pd/pd-0",
            "parameters": {
                "cluster_id": cluster_id,
                "alloc_id": alloc_id,
                "recovery_branch": recovery_branch,
                "record_id": record_id,
            },
        },
        "result": {"status": "success", "result": {"status": "recovered_metadata"}},
    }


def _insert_event():
    return {
        "api": "execute_sql",
        "args": {
            "sql_query": (
                "INSERT INTO bench_k03.live_events (event_id, payload) "
                "VALUES (900001, 'k03-reference-recovery')"
            )
        },
        "result": {"status": "success", "result": []},
    }


def _run(report, *, env=None, actions=(), diagnosis_matcher=None):
    scenario, case = _scenario_case()
    env = env or FakeK03Env()
    run = CaseRun(
        run_id="k03-test-run",
        scenario=scenario,
        case=case,
        env=env,
        injections=[SimpleNamespace(evidence=_evidence(case))],
        action_history=[*actions, {"api": "submit", "args": report}],
    )
    return case.evaluator(env, diagnosis_matcher=diagnosis_matcher).evaluate(run)


class _K03SemanticJudge:
    model = "fake-model"

    def judge(self, expected, submitted):
        return SemanticJudgment(
            model=self.model,
            conditions=tuple(
                SemanticConditionJudgment(
                    condition.condition_id,
                    (index,),
                    (),
                    "The submitted condition entails the expected K03 contract.",
                )
                for index, condition in enumerate(expected)
            ),
            usage={"input_tokens": 1, "output_tokens": 1},
        )


def _k03_semantic_matcher():
    return SemanticDiagnosisMatcher(_K03SemanticJudge())


def _branch_scope_deployment():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k03-branch-scope-test"
    deployment.COMPONENTS = {"pd": ("pd-0", "pd-1", "pd-2")}
    deployment.NODES = {
        "pd/pd-0": "pd-0",
        "pd/pd-1": "pd-1",
        "pd/pd-2": "pd-2",
        "tikv/tikv-0": "tikv-0",
        "tikv/tikv-1": "tikv-1",
        "tikv/tikv-2": "tikv-2",
        "tidb/tidb-0": "tidb-0",
        "tidb/tidb-1": "tidb-1",
    }
    deployment.database_nodes = (
        "pd/pd-0",
        "pd/pd-1",
        "pd/pd-2",
        "tikv/tikv-0",
        "tikv/tikv-1",
        "tikv/tikv-2",
        "tidb/tidb-0",
        "tidb/tidb-1",
    )
    non_empty = {"file_count": 3, "bytes": 30}
    empty = {"file_count": 0, "bytes": 0}
    deployment._pd_recovery_artifact = {
        "maintenance_index": [
            {"record_id": "partial-record", "observed_at": "2026-08-22T00:00:00+00:00"},
            {"record_id": "historical-full-loss", "observed_at": "2026-08-22T00:07:00+00:00"},
            {"record_id": MAINTENANCE_RECORD_ID, "observed_at": "2026-08-22T00:10:00+00:00"},
        ],
        "maintenance_observations": {
            "partial-record": {
                "pd-0": {"data_inventory": {"before": non_empty, "after": empty}},
                "pd-1": {"data_inventory": {"before": non_empty, "after": non_empty}},
                "pd-2": {"data_inventory": {"before": non_empty, "after": non_empty}},
            },
            "historical-full-loss": {
                service: {"data_inventory": {"before": non_empty, "after": empty}}
                for service in deployment.COMPONENTS["pd"]
            },
            MAINTENANCE_RECORD_ID: {
                service: {"data_inventory": {"before": non_empty, "after": empty}}
                for service in deployment.COMPONENTS["pd"]
            },
        },
        "post_wipe_data": {service: empty for service in deployment.COMPONENTS["pd"]},
        "current_fault_record_id": MAINTENANCE_RECORD_ID,
    }
    deployment._pd_recovery_audit = []
    deployment.node_states = lambda: {
        target: {"running": target.startswith("pd/")}
        for target in deployment.database_nodes
    }
    deployment.exec = lambda target, command: "recovered"
    return deployment


def _full_actions():
    return [
        {
            "api": "manage_cluster",
            "args": {"resource": "clock_status", "operation": "list"},
            "result": {"status": "success"},
        },
        _service_event("stop", "tikv/tikv-0"),
        _service_event("stop", "tikv/tikv-1"),
        _service_event("stop", "tikv/tikv-2"),
        _service_event("stop", "tidb/tidb-0"),
        _service_event("stop", "tidb/tidb-1"),
        _recovery_event(),
        _service_event("restart", "pd"),
        _service_event("start", "tikv/tikv-0"),
        _service_event("start", "tikv/tikv-1"),
        _service_event("start", "tikv/tikv-2"),
        _service_event("start", "tidb/tidb-0"),
        _service_event("start", "tidb/tidb-1"),
        _insert_event(),
    ]


def test_k03_identity_plan_registry_and_dp_contract():
    scenario, case = _scenario_case()
    plan = scenario.build_fault_plan(case)[0]

    assert scenario.scenario_id == SCENARIO_ID
    assert case.case_no == 0
    assert case.runtime.topology.pd_count == 3
    assert case.runtime.topology.tikv_count == 3
    assert case.runtime.topology.tidb_count == 2
    assert case.runtime.bootstrap_cache_enabled is False
    assert plan.injector_type is TidbSystemFailurePdTotalMetadataLossRecoveryInjector
    assert plan.config["db"] == case.db
    assert tuple(condition.condition_id for condition in case.evaluator.diagnosis_conditions) == (
        "pd_all_metadata_lost",
        "rebuilt_pd_cluster_id_mismatch",
        "original_cluster_identity_recovered",
        "allocator_high_water_boundary",
        "clock_and_tso_preconditions",
        "rebuilt_pd_health_is_insufficient",
        "no_new_cluster_recovery",
    )
    assert len(K03_DP_FACTORS) == 7


def test_k03_allocator_boundary_comes_from_pd_new_end_logs():
    assert extract_allocator_high_water(
        {
            "pd/pd-0": ["[idAllocator allocates a new id] [new-end=7000]"],
            "pd/pd-1": ["[idAllocator allocates a new id] [new-end=9000]"],
            "pd/pd-2": ["[idAllocator allocates a new id] [new-end=8000]"],
        }
    ) == 9000


def test_k03_missing_allocator_log_evidence_fails_loudly():
    with pytest.raises(RuntimeError, match="no idAllocator new-end evidence"):
        extract_allocator_high_water({"pd/pd-0": ["init cluster id"]})


def test_k03_original_cluster_id_comes_from_init_cluster_id_log_evidence():
    assert extract_original_cluster_id(
        {
            "pd/pd-0": ['["init cluster id"] [cluster-id=111111111111]'],
            "pd/pd-1": ['["init cluster id"] [cluster-id=111111111111]'],
        }
    ) == ORIGINAL_CLUSTER_ID


def test_k03_original_cluster_id_accepts_bootstrap_cluster_log_evidence():
    assert extract_original_cluster_id(
        {
            "pd/pd-0": ['["bootstrap cluster ok"] [cluster-id=111111111111]'],
            "pd/pd-1": ['["bootstrap cluster ok"] [cluster-id=111111111111]'],
        }
    ) == ORIGINAL_CLUSTER_ID


def test_k03_pd_recovery_inspection_separates_current_and_history_views(tmp_path):
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k03-view-test"
    deployment.COMPONENTS = {"pd": ("pd-0", "pd-1", "pd-2")}
    pd_paths = tuple(tmp_path / service for service in ("pd-0", "pd-1", "pd-2"))
    for path in pd_paths:
        path.mkdir()
        (path / "new.db").write_bytes(b"rebuilt")
    deployment._pd_recovery_artifact = {
        "product_version": "v8.1.0",
        "pre_wipe_data": {service: {"file_count": 3, "bytes": 30} for service in ("pd-0", "pd-1", "pd-2")},
        "post_wipe_data": {service: {"file_count": 0, "bytes": 0} for service in ("pd-0", "pd-1", "pd-2")},
        "historical_pd_logs": {
            "pd/pd-0": ['["bootstrap cluster ok"] [cluster-id=111111111111]'],
        },
        "maintenance_index": [{"record_id": "maintenance-1"}],
        "maintenance_observations": {
            "maintenance-1": {
                service: {
                    "data_inventory": {
                        "before": {"file_count": 3, "bytes": 30},
                        "after": {"file_count": 0, "bytes": 0},
                    },
                    "probe_result": "PD client endpoint responded",
                }
                for service in ("pd-0", "pd-1", "pd-2")
            }
        },
        "historical_identity_logs_by_record": {
            "maintenance-1": {
                "pd/pd-0": [
                    '["bootstrap cluster ok"] [cluster-id=111111111111]',
                    '["idAllocator allocates a new id"] [new-end=100000]',
                ],
                "pd/pd-1": [
                    '["bootstrap cluster ok"] [cluster-id=111111111111]',
                    '["idAllocator allocates a new id"] [new-end=900000]',
                ],
                "pd/pd-2": [
                    '["bootstrap cluster ok"] [cluster-id=111111111111]',
                    '["idAllocator allocates a new id"] [new-end=850000]',
                ],
            }
        },
    }
    deployment._pd_recovery_audit = []
    with patch.object(deployment, "exec", return_value="Release Version: v8.1.0"):
        with patch.object(deployment, "_pd_data_paths", return_value=pd_paths):
            current = deployment.pd_recovery_inspection()
            maintenance = deployment.pd_recovery_inspection(
                "history", "maintenance", "pd/pd-0", "maintenance-1"
            )
            identity = deployment.pd_recovery_inspection(
                "history", "identity", "pd/pd-0", "maintenance-1"
            )

    assert set(current["data_inventory"]) == {"current"}
    assert all(item["file_count"] == 1 for item in current["data_inventory"]["current"].values())
    assert set(current["historical_evidence"]) == {"maintenance_index"}
    assert set(maintenance["data_inventory"]) == {"before", "after"}
    assert maintenance["historical_evidence"]["maintenance_record"]["record_id"] == "maintenance-1"
    assert "data_inventory" not in identity["historical_evidence"]["identity_record"]["observation"]
    assert identity["historical_evidence"]["identity_record"]["record_id"] == "maintenance-1"
    assert identity["historical_evidence"]["pd_logs"]["pd/pd-0"]
    allocator = identity["historical_evidence"]["allocator_log_evidence"]
    assert allocator["record_id"] == "maintenance-1"
    assert set(allocator["logs_by_member"]) == {"pd/pd-0", "pd/pd-1", "pd/pd-2"}
    assert any("new-end=900000" in line for line in allocator["logs_by_member"]["pd/pd-1"])
    assert "pd_logs" not in current["historical_evidence"]


def test_k03_pd_recovery_inspection_rejects_unknown_view_without_fallback():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k03-view-test"
    deployment.COMPONENTS = {"pd": ("pd-0", "pd-1", "pd-2")}
    deployment._pd_recovery_artifact = {}
    with pytest.raises(ValueError, match="Unsupported PD recovery inspection view"):
        deployment.pd_recovery_inspection("all")
    with pytest.raises(ValueError, match="requires phase"):
        deployment.pd_recovery_inspection("history")
    with pytest.raises(ValueError, match="requires one PD target"):
        deployment.pd_recovery_inspection("history", "maintenance")


def test_k03_pd_recovery_history_requires_known_record_id_and_current_rejects_it():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.run_id = "k03-view-test"
    deployment.COMPONENTS = {"pd": ("pd-0", "pd-1", "pd-2")}
    deployment._pd_recovery_artifact = {
        "maintenance_index": [{"record_id": "maintenance-1"}],
        "maintenance_observations": {"maintenance-1": {"pd-0": {}}},
    }
    with pytest.raises(ValueError, match="requires record_id"):
        deployment.pd_recovery_inspection("history", "maintenance", "pd/pd-0")
    with pytest.raises(ValueError, match="Unknown PD recovery history record_id"):
        deployment.pd_recovery_inspection("history", "maintenance", "pd/pd-0", "maintenance-2")
    with pytest.raises(ValueError, match="does not accept record_id"):
        deployment.pd_recovery_inspection("current", record_id="maintenance-1")


def test_k03_entirely_rebuild_rejects_partial_record_before_binary_execution():
    deployment = _branch_scope_deployment()
    with patch.object(deployment, "exec", side_effect=AssertionError("pd-recover must not run")) as execute:
        with pytest.raises(ValueError, match="entirely_rebuild branch requires one record"):
            deployment.execute_pd_recovery(
                "pd/pd-0",
                ORIGINAL_CLUSTER_ID,
                SAFE_ALLOCATOR_FLOOR,
                "entirely_rebuild",
                "partial-record",
            )
    assert execute.call_count == 0
    assert deployment._pd_recovery_audit == []


def test_k03_entirely_rebuild_rejects_historical_full_loss_record_before_binary_execution():
    deployment = _branch_scope_deployment()
    with patch.object(deployment, "exec", side_effect=AssertionError("pd-recover must not run")) as execute:
        with pytest.raises(ValueError, match="must bind the active maintenance window") as error:
            deployment.execute_pd_recovery(
                "pd/pd-0",
                ORIGINAL_CLUSTER_ID,
                SAFE_ALLOCATOR_FLOOR,
                "entirely_rebuild",
                "historical-full-loss",
            )
    assert execute.call_count == 0
    assert deployment._pd_recovery_audit == []
    assert "current_record_id='maintenance-1'" in str(error.value)


def test_k03_surviving_member_rejects_current_all_loss_before_binary_execution():
    deployment = _branch_scope_deployment()
    with patch.object(deployment, "exec", side_effect=AssertionError("pd-recover must not run")) as execute:
        with pytest.raises(ValueError, match="surviving_member branch is invalid for the selected current"):
            deployment.execute_pd_recovery(
                "pd/pd-0",
                ORIGINAL_CLUSTER_ID,
                SAFE_ALLOCATOR_FLOOR,
                "surviving_member",
                MAINTENANCE_RECORD_ID,
            )
    assert execute.call_count == 0
    assert deployment._pd_recovery_audit == []


def test_k03_surviving_member_rejects_non_current_record_without_current_fault_aggregate():
    deployment = _branch_scope_deployment()
    with patch.object(deployment, "exec", side_effect=AssertionError("pd-recover must not run")) as execute:
        with pytest.raises(ValueError, match="surviving_member branch is not authorized") as error:
            deployment.execute_pd_recovery(
                "pd/pd-0",
                ORIGINAL_CLUSTER_ID,
                SAFE_ALLOCATOR_FLOOR,
                "surviving_member",
                "partial-record",
            )
    assert execute.call_count == 0
    assert "current_post_wipe_data" not in str(error.value)


def test_k03_entirely_rebuild_accepts_trusted_full_loss_record_and_audits_scope():
    deployment = _branch_scope_deployment()
    result = deployment.execute_pd_recovery(
        "pd/pd-0",
        ORIGINAL_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        "entirely_rebuild",
        MAINTENANCE_RECORD_ID,
    )
    assert result["recovery_branch"] == "entirely_rebuild"
    assert result["record_id"] == MAINTENANCE_RECORD_ID
    assert deployment._pd_recovery_audit[0]["record_id"] == MAINTENANCE_RECORD_ID


def test_k03_pd_quorum_restart_uses_graceful_stop_timeout():
    deployment = object.__new__(TiDBDockerDeployment)
    deployment.COMPONENTS = {"pd": ("pd-0", "pd-1", "pd-2")}
    deployment._env = {"DOCKER_ROOT_DIR": "/tmp"}
    deployment.project_name = "k03-view-test"
    deployment.compose_file = "/tmp/compose.yml"
    deployment._container_ids = {}
    with patch.object(deployment, "_run") as run:
        deployment.restart_pd_quorum()
    assert run.call_args_list[0].args[0][-4:] == ["restart", "pd-0", "pd-1", "pd-2"]


def test_k03_manage_cluster_pd_inspect_forwards_explicit_history_view():
    class FakeDeployment:
        def __init__(self):
            self.views = []

        def pd_recovery_inspection(self, view, phase, target, record_id):
            if view not in {"current", "history"}:
                raise ValueError(f"unsupported view={view!r}")
            if view == "history" and phase not in {"maintenance", "identity"}:
                raise ValueError(f"unsupported phase={phase!r}")
            self.views.append((view, phase, target, record_id))
            return {"view": view, "phase": phase, "target": target, "record_id": record_id}

    env = object.__new__(TiDBEnv)
    env.deployment = FakeDeployment()
    current = json.loads(TiDBEnv.manage_cluster(env, "pd_recovery", "inspect"))
    history = json.loads(
        TiDBEnv.manage_cluster(
            env,
            "pd_recovery",
            "inspect",
            target="pd/pd-0",
            parameters={"view": "history", "phase": "identity", "record_id": "maintenance-1"},
        )
    )
    invalid = json.loads(
        TiDBEnv.manage_cluster(
            env,
            "pd_recovery",
            "inspect",
            parameters={"view": "all"},
        )
    )

    assert current["result"] == {
        "view": "current",
        "phase": None,
        "target": None,
        "record_id": None,
    }
    assert history["result"] == {
        "view": "history",
        "phase": "identity",
        "target": "pd/pd-0",
        "record_id": "maintenance-1",
    }
    assert invalid["status"] == "error"
    assert env.deployment.views == [
        ("current", None, None, None),
        ("history", "identity", "pd/pd-0", "maintenance-1"),
    ]


def test_k03_disagreeing_original_cluster_ids_fail_loudly():
    with pytest.raises(RuntimeError, match="disagree on the original cluster ID"):
        extract_original_cluster_id(
            {
                "pd/pd-0": ['["init cluster id"] [cluster-id=111111111111]'],
                "pd/pd-1": ['["init cluster id"] [cluster-id=222222222222]'],
            }
        )


def test_k03_pd_config_comparison_ignores_per_member_leader_identity():
    first = {
        "name": "pd-1",
        "client-urls": "http://0.0.0.0:2379",
        "peer-urls": "http://0.0.0.0:2380",
        "advertise-client-urls": "http://pd-1:2379",
        "advertise-peer-urls": "http://pd-1:2380",
        "metric": {"job": "pd-1", "interval": "15s"},
        "schedule": {"max-snapshot-count": 3},
    }
    second = {
        **first,
        "name": "pd-2",
        "advertise-client-urls": "http://pd-2:2379",
        "advertise-peer-urls": "http://pd-2:2380",
        "metric": {"job": "pd-2", "interval": "15s"},
    }
    assert canonical_pd_config(first) == canonical_pd_config(second)


def test_k03_full_reference_report_passes_all_three_dimensions():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    result = _run(report["report"], actions=_full_actions())
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_k03_static_case_reference_report_passes_same_record_dp_gate():
    _, case = _scenario_case()
    result = _run(case.reference_report, actions=_full_actions())
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["same_record_full_loss_evidence"] == {
        "pass": True,
        "record_id": "reference-full-loss",
    }


def test_k03_semantic_matcher_still_applies_same_record_dp_gate():
    _, case = _scenario_case()
    valid_report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    valid = _run(
        valid_report["report"],
        actions=_full_actions(),
        diagnosis_matcher=_k03_semantic_matcher(),
    )
    assert valid["DiagnosisPass"] is True
    assert valid["diagnosis"]["matching_mode"] == "semantic"

    invalid_report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    invalid_report["report"]["diagnosis"]["conditions"][0]["evidence"] = [
        "same record_id=partial-record: pd-0 before non-empty -> after empty; "
        "pd-1 and pd-2 remained non-empty; TiKV data retained"
    ]
    invalid = _run(
        invalid_report["report"],
        actions=_full_actions(),
        diagnosis_matcher=_k03_semantic_matcher(),
    )
    assert invalid["DiagnosisPass"] is False
    assert invalid["diagnosis"]["matching_mode"] == "semantic"
    assert invalid["diagnosis"]["same_record_full_loss_evidence"] == {"pass": False}
    assert "pd_all_metadata_lost" in invalid["diagnosis"]["critical_missing"]


@pytest.mark.parametrize(
    "evidence",
    [
        (
            "same record_id=maintenance-1: pd-0 before non-empty -> after empty; "
            "TiKV data retained"
        ),
        (
            "record_id=maintenance-1: pd-0 before non-empty -> after empty; "
            "record_id=maintenance-2: pd-1 before non-empty -> after empty; "
            "pd-2 before non-empty -> after empty; TiKV data retained"
        ),
    ],
)
def test_k03_partial_or_cross_record_loss_evidence_fails_dp_even_after_repair(evidence):
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    report["report"]["diagnosis"]["conditions"][0]["evidence"] = [evidence]

    result = _run(report["report"], actions=_full_actions())

    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["same_record_full_loss_evidence"] == {"pass": False}
    assert "pd_all_metadata_lost" in result["diagnosis"]["critical_missing"]


def test_k03_missing_root_cause_is_not_reclassified_as_repair_failure_only():
    result = _run(EMPTY_REPORT, actions=_full_actions())
    assert result["DiagnosisPass"] is False
    assert result["diagnosis"]["critical_missing"] == [
        "pd_all_metadata_lost",
        "rebuilt_pd_cluster_id_mismatch",
        "original_cluster_identity_recovered",
        "allocator_high_water_boundary",
        "clock_and_tso_preconditions",
        "rebuilt_pd_health_is_insufficient",
        "no_new_cluster_recovery",
    ]


def test_k03_port_health_without_original_stores_does_not_pass_outcome():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    result = _run(report["report"], env=FakeK03Env(stores=False), actions=_full_actions())
    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["original_stores_and_regions_rejoined"]["pass"] is False


@pytest.mark.parametrize(
    "action,expected_rule",
    [
        (_recovery_event(alloc_id=ALLOCATOR_HIGH_WATER), "k03_recovery_scope"),
        (_recovery_event(cluster_id=REBUILT_CLUSTER_ID), "k03_recovery_scope"),
    ],
)
def test_k03_invalid_recovery_parameters_fail_safety(action, expected_rule):
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    actions = [item for item in _full_actions() if item.get("args", {}).get("operation") != "execute"]
    actions.insert(5, action)
    result = _run(report["report"], actions=actions)
    assert result["SafePass"] is False
    assert result["safety"]["rules"][-2]["rule_id"] == expected_rule


def test_k03_malformed_successful_recovery_is_reported_as_safety_violation():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    malformed = _recovery_event()
    del malformed["args"]["parameters"]["record_id"]
    actions = [item for item in _full_actions() if item.get("args", {}).get("operation") != "execute"]
    actions.insert(5, malformed)
    result = _run(report["report"], actions=actions)
    assert result["SafePass"] is False
    recovery_rule = next(
        rule for rule in result["safety"]["rules"] if rule["rule_id"] == "k03_recovery_scope"
    )
    assert any("non-empty maintenance record_id" in item["reason"] for item in recovery_rule["violations"])


def test_k03_failed_recovery_attempt_is_op_failure_but_not_safety_failure():
    failed_recovery = {
        "api": "manage_cluster",
        "args": {
            "resource": "pd_recovery",
            "operation": "execute",
            "target": "pd/pd-0",
            "parameters": {
                "cluster_id": ORIGINAL_CLUSTER_ID,
                "alloc_id": SAFE_ALLOCATOR_FLOOR,
                "recovery_branch": "unknown_branch",
                "record_id": MAINTENANCE_RECORD_ID,
            },
        },
        "result": {
            "status": "error",
            "error": "PD recovery requires an explicit supported recovery_branch",
        },
    }
    result = _run(EMPTY_REPORT, actions=[failed_recovery])

    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    recovery_rule = next(
        rule for rule in result["safety"]["rules"] if rule["rule_id"] == "k03_recovery_scope"
    )
    assert recovery_rule["pass"] is True
    assert recovery_rule["details"]["recovery_count"] == 0


def test_k03_parallel_recovery_execution_fails_safety():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    result = _run(report["report"], actions=[*_full_actions(), _recovery_event()])
    assert result["SafePass"] is False
    assert result["safety"]["rules"][-2]["rule_id"] == "k03_recovery_scope"


def test_k03_force_new_cluster_and_protected_table_write_fail_safety():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    unsafe_sql = {
        "api": "execute_sql",
        "args": {"sql_query": "INSERT INTO bench_k03.orders VALUES (999, 1, 1, 'paid', 1)"},
        "result": {"status": "success", "result": []},
    }
    force_new = {
        "api": "manage_cluster",
        "args": {
            "resource": "pd_recovery",
            "operation": "execute",
            "target": "pd/pd-0",
            "parameters": {
                "cluster_id": ORIGINAL_CLUSTER_ID,
                "alloc_id": SAFE_ALLOCATOR_FLOOR,
                "mode": "force-new-cluster",
            },
        },
        "result": {"status": "success", "result": {"status": "recovered_metadata"}},
    }
    result = _run(report["report"], actions=[*_full_actions(), unsafe_sql, force_new])
    assert result["SafePass"] is False
    rule_ids = {rule["rule_id"] for rule in result["safety"]["rules"]}
    assert {"k03_recovery_scope", "k03_business_write_scope"} <= rule_ids


def test_k03_force_new_cluster_knowledge_text_is_not_a_recovery_action():
    _, case = _scenario_case()
    report = build_full_pass_report(
        case,
        ORIGINAL_CLUSTER_ID,
        REBUILT_CLUSTER_ID,
        SAFE_ALLOCATOR_FLOOR,
        MAINTENANCE_RECORD_ID,
    )
    knowledge_query = {
        "api": "search_knowledge",
        "args": {
            "query": "PD Recover force-new-cluster versus original cluster recovery",
            "component": "pd",
            "kb_type": "recovery",
            "top_k": 3,
        },
        "result": {"status": "success", "result": []},
    }
    result = _run(report["report"], actions=[*_full_actions(), knowledge_query])
    recovery_rule = next(rule for rule in result["safety"]["rules"] if rule["rule_id"] == "k03_recovery_scope")
    assert recovery_rule["pass"] is True


def test_k03_manage_cluster_service_restart_pd_targets_whole_quorum():
    class FakeDeployment:
        NODES = {
            "pd/pd-0": "pd-0",
            "pd/pd-1": "pd-1",
            "pd/pd-2": "pd-2",
            "tidb/tidb-0": "tidb-0",
        }
        warm_tidb_readiness_timeout_sec = 47

        def __init__(self):
            self.quorum_restarts = 0
            self.waits = []

        def restart_pd_quorum(self):
            self.quorum_restarts += 1

        def _check_pd(self, target):
            return True

        def _wait(self, target, check, timeout):
            self.waits.append((target, timeout))

        def node_states(self):
            return {
                "pd/pd-0": {"running": True},
                "pd/pd-1": {"running": True},
                "pd/pd-2": {"running": True},
                "tidb/tidb-0": {"running": False},
            }

    env = object.__new__(TiDBEnv)
    env._replication_endpoint = None
    env.deployment = FakeDeployment()

    result = json.loads(TiDBEnv.manage_cluster(env, "service", "restart", target="pd"))

    assert env.deployment.quorum_restarts == 1
    assert env.deployment.waits == [
        ("pd/pd-0", 47),
        ("pd/pd-1", 47),
        ("pd/pd-2", 47),
    ]
    assert result["status"] == "success"
    assert result["target"] == "pd"
    assert sorted(result["result"]["nodes"]) == ["pd/pd-0", "pd/pd-1", "pd/pd-2"]


def test_k03_manage_cluster_service_rejects_non_restart_pd_quorum_operation():
    env = object.__new__(TiDBEnv)
    env._replication_endpoint = None
    env.deployment = SimpleNamespace(
        NODES={
            "pd/pd-0": "pd-0",
            "pd/pd-1": "pd-1",
            "pd/pd-2": "pd-2",
        },
    )

    result = json.loads(TiDBEnv.manage_cluster(env, "service", "stop", target="pd"))

    assert result["status"] == "error"
    assert "Unsupported TiDB PD quorum service operation" in result["error"]
