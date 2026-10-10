from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance import (
    TidbResourceGovernanceConnectionBalancingEvaluatorCase,
    TidbResourceGovernanceConnectionBalancingAlternateTargetEvaluatorCase,
)

from src.scenarios.workloads import WorkloadProfile

from ...base import (
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    FaultPlan,
    TiDBScenario,
    TiDBScenarioCase,
)

from ..runtime import TIDB_V8_1_0, tidb_runtime

from collections.abc import Mapping

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import json_object, require_sql_success, validate_sql_identifier


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceConnectionBalancingCase(TiDBScenarioCase):
    db: str
    table: str
    cache_table: str
    row_count: int
    initial_target: str
    router_names: tuple[str, ...]
    managed_router_names: tuple[str, ...]
    protected_router_names: tuple[str, ...]
    protected_router_target: str
    protected_router_policy: str
    tidb_targets: tuple[str, ...]
    accepted_policies: tuple[str, ...]
    max_connection_skew: int
    minimum_initial_connections: int
    minimum_final_connections: int
    routing_convergence_attempts: int
    routing_poll_interval_seconds: float
    minimum_workload_calls: int
    maximum_workload_failure_ratio: float
    expected_business_truth: tuple[int, int, int, int]
    business_query: str

@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernanceConnectionBalancingForMultiTidbConnectionBalanceAndDrainScenarioCase(
    TidbResourceGovernanceConnectionBalancingCase
):
    pass

def _build_background_workload() -> BackgroundWorkloadSpec:
    return BackgroundWorkloadSpec(
        profiles=(
            WorkloadProfile(
                name="rg08_checkout_order_lookup",
                sql=(
                    "SELECT order_id, customer_id, status, amount "
                    "FROM test.rg08_orders WHERE order_id = 1733"
                ),
                qps=2.5,
                tier="OLTP_CORE",
                application_name="checkout-api",
                connection_pool="checkout-router",
            ),
            WorkloadProfile(
                name="rg08_customer_dashboard_rollup",
                sql=(
                    "SELECT customer_id, status, COUNT(*) AS order_count, SUM(amount) AS gross_amount "
                    "FROM test.rg08_orders WHERE created_at >= '2026-07-01 00:00:00' "
                    "GROUP BY customer_id, status ORDER BY gross_amount DESC LIMIT 32"
                ),
                qps=0.65,
                tier="REPORTING",
                application_name="order-dashboard",
                connection_pool="reporting-router",
            ),
            WorkloadProfile(
                name="rg08_inventory_reconciliation",
                sql=(
                    "SELECT warehouse_id, COUNT(*) AS order_count, SUM(amount) AS gross_amount "
                    "FROM test.rg08_orders GROUP BY warehouse_id ORDER BY warehouse_id"
                ),
                qps=0.55,
                tier="BATCH_READ",
                application_name="inventory-reconciliation",
                connection_pool="reporting-router",
            ),
            WorkloadProfile(
                name="rg08_finance_export_preview",
                sql=(
                    "SELECT status, COUNT(*) AS order_count, SUM(amount) AS gross_amount "
                    "FROM test.rg08_orders GROUP BY status ORDER BY gross_amount DESC"
                ),
                qps=0.35,
                tier="REPORTING",
                application_name="finance-export-preview",
                connection_pool="reporting-router",
            ),
            WorkloadProfile(
                name="rg08_checkout_write_probe",
                sql="UPDATE test.rg08_orders SET amount = amount WHERE order_id = 1733",
                qps=0.75,
                tier="OLTP_CORE",
                application_name="checkout-write-path",
                connection_pool="checkout-router",
            ),
            WorkloadProfile(
                name="rg08_cache_refresh_probe",
                sql=(
                    "SELECT cache_id, cache_status FROM test.rg08_order_cache "
                    "WHERE cache_id BETWEEN 1 AND 32"
                ),
                qps=0.7,
                tier="CACHE_REFRESH",
                application_name="order-cache-refresh",
                connection_pool="reporting-router",
            ),
            WorkloadProfile(
                name="rg08_long_order_transaction",
                sql=(
                    "SELECT SLEEP(8), COUNT(*) FROM test.rg08_orders "
                    "WHERE status IN ('PAID', 'SHIPPED')"
                ),
                qps=0.05,
                tier="LONG_TRANSACTION",
                application_name="order-settlement-worker",
                connection_pool="settlement-router",
            ),
            WorkloadProfile(
                name="rg08_settlement_status_probe",
                sql=(
                    "SELECT order_id, status, amount FROM test.rg08_orders "
                    "WHERE order_id IN (1733, 2048, 3072)"
                ),
                qps=0.25,
                tier="OLTP_CORE",
                application_name="order-settlement-status",
                connection_pool="settlement-router",
            ),
            WorkloadProfile(
                name="rg08_instance_identity_probe",
                sql="SELECT @@hostname, @@port, NOW()",
                qps=1.0,
                tier="OBSERVABILITY",
                application_name="connection-pool-health-probe",
                connection_pool="identity-probe-router",
            ),
        ),
        worker_count=12,
        seed=20260802,
        start_phase=BackgroundWorkloadStartPhase.AFTER_FAULTS,
        warmup_seconds=12,
    )

_CASE = TidbResourceGovernanceConnectionBalancingForMultiTidbConnectionBalanceAndDrainScenarioCase(
    case_id="multi_tidb_connection_balance_and_drain",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "changed the checkout, reporting and settlement business pools to distributing policies",
                "marked tidb/tidb-0 draining while preserving the identity probe affinity"
            ],
            "verification": [
                "verified all managed pools balanced new connections and had zero routed connections on tidb/tidb-0",
                "verified the protected identity probe remained on tidb/tidb-2, all endpoints served, and business rows were unchanged"
            ]
        },
        "summary": "The affected business pools were rebalanced and the old TiDB SQL instance was drained without changing the protected identity probe."
    },
    case_no=0,
    evaluator=TidbResourceGovernanceConnectionBalancingEvaluatorCase,
    title="Rebalance affected TiDB connection pools and gracefully drain the affected SQL instance.",
    alert=(
        "[P1] [TiDB/Connection Service] checkout and order-dashboard latency is unstable. "
        "The release window requires reviewing application connection placement without interrupting "
        "in-flight orders. "
        "Inspect time-windowed connection, CPU, QPS, query-latency, workload and cluster evidence; "
        "separate affected application traffic from stable background traffic; then complete a reversible "
        "load-balancer transition and verify business results, endpoint availability and session drain."
    ),
    initial_state={
        "status": "degraded",
        "topology": "three TiDB SQL instances behind multiple application connection routers",
        "initial_policy": "multiple_pool_affinities",
        "required_operation": "identify affected pools, rebalance new connections, then drain the affected backend",
    },
    expected_target={
        "status": "recovered",
        "accepted_policies": ("round_robin", "least_connections"),
        "draining_target": "tidb/tidb-0",
        "protected_router_policy": "single_instance",
        "protected_router_target": "tidb/tidb-2",
        "drained_active_connections": 0,
        "business_data_preserved": True,
        "all_tidb_endpoints_serving": True,
    },
    background_workload=_build_background_workload(),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=3,
        tidb_count=3,
        sql_timeout_seconds=120,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.848739,
        reference_run_ids=(
            "reference-273__tidb_resource_governance_connection_balancing__multi_tidb_connection_balance_and_drain__mock__r001",
        ),
    ),
    db="test",
    table="rg08_orders",
    cache_table="rg08_order_cache",
    row_count=4096,
    initial_target="tidb/tidb-0",
    router_names=(
        "checkout-router",
        "reporting-router",
        "settlement-router",
        "identity-probe-router",
    ),
    managed_router_names=("checkout-router", "reporting-router", "settlement-router"),
    protected_router_names=("identity-probe-router",),
    protected_router_target="tidb/tidb-2",
    protected_router_policy="single_instance",
    tidb_targets=("tidb/tidb-0", "tidb/tidb-1", "tidb/tidb-2"),
    accepted_policies=("round_robin", "least_connections"),
    max_connection_skew=2,
    minimum_initial_connections=2,
    minimum_final_connections=2,
    routing_convergence_attempts=90,
    routing_poll_interval_seconds=1.0,
    minimum_workload_calls=12,
    maximum_workload_failure_ratio=0.20,
    expected_business_truth=(4096, 8390656, 1, 4096),
    business_query=(
        "SELECT COUNT(*), CAST(COALESCE(SUM(order_id), 0) AS SIGNED), "
        "MIN(order_id), MAX(order_id) "
        "FROM test.rg08_orders"
    ),
)

_ALTERNATE_TARGET_CASE = replace(
    _CASE,
    case_id="multi_tidb_alternate_target_drain",
    case_no=1,
    evaluator=TidbResourceGovernanceConnectionBalancingAlternateTargetEvaluatorCase,
    title="Rebalance the affected pools and drain the alternate TiDB backend.",
    alert=(
        "[P1] Connection placement is unstable during a release window. Compare the three SQL backends, "
        "identify the backend carrying the affected application pools, and move those pools before draining "
        "that backend. Preserve settlement continuity and in-flight work while keeping the settlement pool "
        "within the application-pool rebalance scope; only the identity probe affinity is protected. Preserve "
        "endpoint continuity and order truth."
    ),
    initial_state={
        "status": "degraded",
        "topology": "three TiDB SQL instances behind multiple application connection routers",
        "initial_policy": "multiple_pool_affinities",
        "required_operation": "identify the alternate affected backend, rebalance new connections, then drain it",
    },
    expected_target={
        **_CASE.expected_target,
        "draining_target": "tidb/tidb-1",
    },
    initial_target="tidb/tidb-1",
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.2,
        reference_run_ids=(
            "tidb-reference-14__tidb_resource_governance_connection_balancing__"
            "multi_tidb_alternate_target_drain__mock__r001",
        ),
    ),
)

class TidbResourceGovernanceConnectionBalancingScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_connection_balancing"
    description = "Multiple TiDB SQL instances require application connection rebalance and graceful session drain."
    cases = (_CASE, _ALTERNATE_TARGET_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernanceConnectionBalancingCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernanceConnectionBalancingInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "cache_table": case.cache_table,
                    "row_count": case.row_count,
                    "initial_target": case.initial_target,
                    "minimum_initial_connections": case.minimum_initial_connections,
                    "managed_router_names": case.managed_router_names,
                    "protected_router_names": case.protected_router_names,
                    "protected_router_target": case.protected_router_target,
                    "protected_router_policy": case.protected_router_policy,
                    "routers": {
                        "checkout-router": {"initial_target": case.initial_target},
                        "reporting-router": {"initial_target": case.initial_target},
                        "settlement-router": {
                            "initial_target": (
                                case.tidb_targets[0]
                                if case.initial_target == case.tidb_targets[1]
                                else case.tidb_targets[1]
                            )
                        },
                        "identity-probe-router": {
                            "initial_target": case.protected_router_target
                        },
                    },
                },
            ),
        )


__all__ = (
    "TidbResourceGovernanceConnectionBalancingCase",
    "TidbResourceGovernanceConnectionBalancingForMultiTidbConnectionBalanceAndDrainScenarioCase",
    "TidbResourceGovernanceConnectionBalancingScenario",
)

class TidbResourceGovernanceConnectionBalancingInjector(BaseFaultInjector):
    """Create a skewed application connection pool and a drainable TiDB backend."""

    def __init__(self) -> None:
        self._router_initialized = False

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._create_business_tables(context.env)
        self._load_business_rows(context.env)
        self._verify_business_state(context.env)
        context.env.initialize_connection_routers(self.routers)
        self._router_initialized = True

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config)
        self._verify_business_state(context.env)
        context.env.initialize_connection_routers(self.routers)
        self._router_initialized = True

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        statuses = context.env.connection_router_statuses()
        for router_name in self.managed_router_names:
            status = statuses[router_name]
            active = status["active_connections"]
            initial_target = self.routers[router_name]["initial_target"]
            if active[initial_target] < self.minimum_initial_connections:
                raise RuntimeError(
                    "RG08 initial connection skew was not observable after workload warmup: "
                    f"router={router_name!r}, target={initial_target!r}, "
                    f"active_connections={active!r}, "
                    f"minimum_initial_connections={self.minimum_initial_connections}"
                )
        for router_name in self.protected_router_names:
            status = statuses[router_name]
            active = status["active_connections"]
            if (
                status["policy"] != self.protected_router_policy
                or status["initial_target"] != self.protected_router_target
                or int(active[self.protected_router_target]) <= 0
            ):
                raise RuntimeError(
                    "RG08 protected identity router was not observable in its expected affinity: "
                    f"router={router_name!r}, status={status!r}, "
                    f"expected_policy={self.protected_router_policy!r}, "
                    f"expected_target={self.protected_router_target!r}"
                )
        return {
            "rg08_initial_routers": statuses,
            "rg08_initial_business_truth": self.business_truth(context.env),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        if self._router_initialized:
            context.env.reset_connection_routers()
            self._router_initialized = False

    def recover(self, context: FaultLifecycleContext) -> None:
        if self._router_initialized:
            context.env.reset_connection_routers()
            self._router_initialized = False
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.cache_table}"),
            "drop RG08 cache table",
        )
        require_sql_success(
            context.env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.table}"),
            "drop RG08 business table",
        )

    def _configure(self, config: Mapping[str, object]) -> None:
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.cache_table = validate_sql_identifier(str(config["cache_table"]), "cache_table")
        self.row_count = int(config["row_count"])
        self.initial_target = str(config["initial_target"])
        self.managed_router_names = tuple(str(name) for name in config["managed_router_names"])
        self.protected_router_names = tuple(
            str(name) for name in config["protected_router_names"]
        )
        self.protected_router_target = str(config["protected_router_target"])
        self.protected_router_policy = str(config["protected_router_policy"])
        self.routers = {
            str(name): {"initial_target": str(router_config["initial_target"])}
            for name, router_config in dict(config["routers"]).items()
        }
        self.minimum_initial_connections = int(config["minimum_initial_connections"])
        self.business_truth_sql = (
            f"SELECT COUNT(*), CAST(COALESCE(SUM(order_id), 0) AS SIGNED), "
            f"MIN(order_id), MAX(order_id) "
            f"FROM {self.db}.{self.table}"
        )
        if self.row_count <= 0:
            raise ValueError(f"RG08 row_count must be positive: row_count={self.row_count}")
        if self.minimum_initial_connections <= 0:
            raise ValueError(
                "RG08 minimum_initial_connections must be positive: "
                f"minimum_initial_connections={self.minimum_initial_connections}"
            )

    def _create_business_tables(self, env) -> None:
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.cache_table}"),
            "clear RG08 cache table",
        )
        require_sql_success(
            env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{self.table}"),
            "clear RG08 business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.table} ("
                "order_id INT PRIMARY KEY, customer_id INT NOT NULL, warehouse_id INT NOT NULL, "
                "status VARCHAR(16) NOT NULL, amount DECIMAL(12, 2) NOT NULL, "
                "created_at DATETIME NOT NULL, payload VARCHAR(64) NOT NULL)"
            ),
            "create RG08 business table",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.cache_table} ("
                "cache_id INT PRIMARY KEY, cache_status VARCHAR(16) NOT NULL, "
                "payload VARCHAR(64) NOT NULL)"
            ),
            "create RG08 cache table",
        )
        cache_values = ",".join(
            f"({index}, 'warm', 'cache-entry-{index}')" for index in range(1, 129)
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.cache_table} VALUES {cache_values}"
            ),
            "load RG08 cache table",
        )

    def _load_business_rows(self, env) -> None:
        chunk_size = 512
        for start in range(1, self.row_count + 1, chunk_size):
            stop = min(start + chunk_size, self.row_count + 1)
            values = ",".join(
                (
                    f"({order_id}, {(order_id * 17) % 1000 + 1}, {(order_id % 16) + 1}, "
                    f"'{('PAID', 'PENDING', 'SHIPPED', 'CANCELLED', 'REFUNDED')[order_id % 5]}', "
                    f"{(order_id * 37) % 100000 / 100:.2f}, "
                    f"'2026-07-{(order_id % 28) + 1:02d} 12:{order_id % 60:02d}:00', "
                    f"'order-payload-{order_id % 97}')"
                )
                for order_id in range(start, stop)
            )
            require_sql_success(
                env.execute_sql(f"INSERT INTO {self.db}.{self.table} VALUES {values}"),
                f"load RG08 business rows start={start} stop={stop - 1}",
            )

    def _verify_business_state(self, env) -> None:
        payload = json_object(
            env.execute_sql(self.business_truth_sql),
            "verify RG08 business state",
        )
        expected = [[self.row_count, self.row_count * (self.row_count + 1) // 2, 1, self.row_count]]
        if payload["result"] != expected:
            raise RuntimeError(
                "RG08 business table has unexpected contents: "
                f"table={self.db}.{self.table}, expected={expected!r}, actual={payload['result']!r}"
            )

    def business_truth(self, env) -> dict[str, object]:
        payload = json_object(
            env.execute_sql(self.business_truth_sql),
            "capture RG08 business truth",
        )
        return {"sql": self.business_truth_sql, "result": payload["result"]}
