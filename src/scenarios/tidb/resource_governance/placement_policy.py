import json

from collections.abc import Mapping

from src.database.query_results import capture_query_result_truth

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext

from src.scenarios.tidb.common import json_object, require_sql_success, validate_sql_identifier

from dataclasses import dataclass, replace

from src.scenarios.evaluation.tidb.resource_governance.placement_policy import (
    TidbResourceGovernancePlacementPolicyEvaluatorCase,
    TidbResourceGovernancePlacementPolicyNeighborIsolationEvaluatorCase,
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


@dataclass(frozen=True, slots=True, kw_only=True)
class TidbResourceGovernancePlacementPolicyForComplianceTableZoneMigrationScenarioCase(TiDBScenarioCase):
    db: str
    table: str
    protected_tables: tuple[str, ...]
    neighbor_tables: tuple[str, ...]
    service_registry_table: str
    service_registry_rows: tuple[tuple[str, str, str, int], ...]
    workload_catalog_table: str
    workload_catalog_rows: tuple[tuple[str, str, str, int, int], ...]
    relation_directory_table: str
    relation_directory_rows: tuple[tuple[str, int, str, str, int], ...]
    route_lease_table: str
    route_lease_rows: tuple[tuple[str, int, str, str, int], ...]
    route_allocation_table: str
    route_allocation_rows: tuple[tuple[str, int, int, int, str, str, int], ...]
    traffic_assignment_table: str
    traffic_assignment_rows: tuple[tuple[str, str, str, int, str, str, int, int], ...]
    route_segment_table: str
    route_segment_rows: tuple[tuple[str, str, str, int, int, int, str, int], ...]
    request_binding_table: str
    request_binding_rows: tuple[tuple[str, str, str, str, int, int, int, int], ...]
    request_context_table: str
    request_context_rows: tuple[tuple[str, str, int, int, str, int], ...]
    compliance_request_table: str
    compliance_request_rows: tuple[
        tuple[str, str, str, int, str, str, str, int, str, str, int], ...
    ]
    legacy_policy: str
    target_policy: str
    semantic_policy: str
    audit_policy: str
    etl_policy: str
    neighbor_policies: tuple[str, ...]
    neighbor_row_counts: tuple[int, ...]
    row_count: int
    business_query: str
    required_replica_zones: tuple[str, ...]
    leader_zone: str
    min_available_bytes: int


def _relation_workload_profiles(table: str, prefix: str) -> tuple[WorkloadProfile, ...]:
    return (
        WorkloadProfile(
            name=f"{prefix}_status_rollup",
            sql=(
                "SELECT status, COUNT(*) AS orders, SUM(amount) AS gross_amount "
                f"FROM {table} WHERE tenant_id BETWEEN 10 AND 60 "
                "GROUP BY status ORDER BY status"
            ),
            qps=0.35,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name=f"{prefix}_tenant_dashboard",
            sql=(
                "SELECT tenant_id, COUNT(*) AS orders, SUM(amount) AS gross_amount "
                f"FROM {table} WHERE tenant_id BETWEEN 20 AND 45 "
                "GROUP BY tenant_id ORDER BY gross_amount DESC, tenant_id LIMIT 20"
            ),
            qps=0.22,
            tier="MEDIUM",
        ),
        WorkloadProfile(
            name=f"{prefix}_detail_lookup",
            sql=(
                "SELECT id, tenant_id, status, amount "
                f"FROM {table} WHERE id = 4207"
            ),
            qps=0.48,
            tier="LIGHT",
        ),
        WorkloadProfile(
            name=f"{prefix}_time_window",
            sql=(
                "SELECT COUNT(*), SUM(amount) "
                f"FROM {table} WHERE event_ts >= FROM_UNIXTIME(1700004000) "
                "AND event_ts < FROM_UNIXTIME(1700040000)"
            ),
            qps=0.28,
            tier="LIGHT",
        ),
    )


_CASE = TidbResourceGovernancePlacementPolicyForComplianceTableZoneMigrationScenarioCase(
    case_id="compliance_table_zone_migration",
    reference_report={
        "diagnosis": {
            "conditions": []
        },
        "outcome": {
            "changes": [
                "attach an equivalent policy whose definition satisfies the approved compliance request"
            ],
            "verification": [
                "the target placement is SCHEDULED, every target Region satisfies the policy, and business truth is unchanged"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=TidbResourceGovernancePlacementPolicyEvaluatorCase,
    title="Reconcile a regulated checkout placement without disturbing related tables.",
    alert=(
        "[P1] An approved regulated-checkout placement requirement is not satisfied by the live relation. "
        "The catalog contains several same-shape relations, historical routing epochs, and policy "
        "definitions with different semantics. Correlate the current request context, committed route, "
        "and relation directory, then map the approval's survival and leader-locality requirements to "
        "a policy that the current healthy stores can satisfy. Change only the committed target relation, "
        "wait for asynchronous PD scheduling to finish, and verify the physical peers and business truth. "
        "Preserve every related relation, policy definition, control-plane row, and store topology. "
        "Do not stop a node or alter cluster-wide replication settings."
    ),
    initial_state={
        "status": "running",
        "table_policy": "legacy policy violates the current approval",
        "placement_status": "stable but noncompliant",
    },
    expected_target={
        "status": "scheduled",
        "approval": "satisfied by an equivalent table-scoped policy",
        "business_result": "unchanged",
    },
    background_workload=BackgroundWorkloadSpec(
        profiles=(
            *_relation_workload_profiles("rg04_relation_02", "relation_02"),
            *_relation_workload_profiles("rg04_relation_01", "relation_01"),
            *_relation_workload_profiles("rg04_relation_03", "relation_03"),
            WorkloadProfile(
                name="audit_event_retention_scan",
                sql=(
                    "SELECT status, COUNT(*) FROM rg04_audit_events "
                    "WHERE event_ts >= FROM_UNIXTIME(1700000000) "
                    "GROUP BY status ORDER BY status"
                ),
                qps=0.31,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="audit_event_tenant_probe",
                sql=(
                    "SELECT tenant_id, COUNT(*) FROM rg04_audit_events "
                    "WHERE tenant_id BETWEEN 5 AND 35 GROUP BY tenant_id LIMIT 16"
                ),
                qps=0.19,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="etl_batch_ready_count",
                sql=(
                    "SELECT status, COUNT(*) FROM rg04_etl_stage "
                    "GROUP BY status ORDER BY status"
                ),
                qps=0.27,
                tier="LIGHT",
            ),
            WorkloadProfile(
                name="etl_reconciliation_join",
                sql=(
                    "SELECT COUNT(*) FROM rg04_etl_stage e "
                    "JOIN rg04_audit_events a ON a.id = e.id "
                    "WHERE e.tenant_id BETWEEN 10 AND 50"
                ),
                qps=0.16,
                tier="MEDIUM",
            ),
        ),
        worker_count=4,
        seed=0x5A04,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=8,
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=7,
        environmental_complexity=0.828715,
        reference_run_ids=(
            "reference-271__tidb_resource_governance_placement_policy__compliance_table_zone_migration__"
            "tidb_resource_governance_placement_policy__"
            "compliance_table_zone_migration__mock_reference__r001",
        ),
    ),
    runtime=tidb_runtime(
        release=TIDB_V8_1_0,
        pd_count=3,
        tikv_count=4,
        tidb_count=2,
        sql_timeout_seconds=120,
        tikv_store_zones=("az-a", "az-a", "az-b", "az-c"),
        pd_location_labels=("zone",),
        bootstrap_cache_enabled=False,
    ),
    db="test",
    table="rg04_relation_02",
    protected_tables=("rg04_audit_events", "rg04_etl_stage"),
    neighbor_tables=("rg04_relation_01", "rg04_relation_03"),
    workload_catalog_table="rg04_workload_catalog",
    workload_catalog_rows=(
        ("svc-r08", "role-08", "route-01", 7, 0),
        ("svc-r17-checkout", "role-17", "route-01", 7, 1),
        ("svc-r17-checkout", "role-17", "route-02", 7, 1),
        ("svc-r23", "role-23", "route-03", 7, 1),
        ("svc-r08", "role-08", "route-02", 6, 0),
        ("svc-r17-checkout", "role-17", "route-01", 6, 0),
        ("svc-r23", "role-23", "route-03", 6, 0),
    ),
    relation_directory_table="rg04_relation_directory",
    relation_directory_rows=(
        ("route-01", 7, "rg04_relation_01", "class-17", 1),
        ("route-02", 7, "rg04_relation_02", "class-17", 1),
        ("route-03", 7, "rg04_relation_03", "class-03", 1),
        ("route-01", 6, "rg04_relation_02", "class-02", 0),
        ("route-02", 6, "rg04_relation_01", "class-01", 0),
        ("route-03", 6, "rg04_relation_03", "class-03", 0),
    ),
    route_lease_table="rg04_route_leases",
    route_lease_rows=(
        ("route-01", 7, "serving", "primary", 1),
        ("route-02", 7, "serving", "primary", 1),
        ("route-03", 7, "serving", "control", 1),
        ("route-01", 6, "expired", "primary", 0),
        ("route-02", 6, "expired", "primary", 0),
        ("route-03", 6, "expired", "control", 0),
    ),
    route_allocation_table="rg04_route_allocations",
    route_allocation_rows=(
        ("route-01", 7, 46, 7, "active", "primary", 1),
        ("route-02", 7, 42, 7, "active", "primary", 1),
        ("route-03", 7, 42, 7, "active", "control", 1),
        ("route-01", 6, 30, 6, "expired", "primary", 0),
        ("route-02", 6, 30, 6, "expired", "primary", 0),
        ("route-03", 6, 30, 6, "expired", "control", 0),
    ),
    traffic_assignment_table="rg04_traffic_assignments",
    traffic_assignment_rows=(
        ("svc-r08", "role-08", "route-01", 7, "settlement", "expired", 0, 0),
        ("svc-r17-checkout", "role-17", "route-01", 7, "regulated-checkout", "assigned", 100, 1),
        ("svc-r17-checkout", "role-17", "route-02", 7, "regulated-checkout", "assigned", 100, 1),
        ("svc-r23", "role-23", "route-03", 7, "reconciliation", "control", 100, 1),
        ("svc-r08", "role-08", "route-02", 6, "settlement", "expired", 0, 0),
        ("svc-r17-checkout", "role-17", "route-01", 6, "regulated-checkout", "expired", 0, 0),
        ("svc-r17-checkout", "role-17", "route-02", 6, "regulated-checkout", "expired", 0, 0),
        ("svc-r23", "role-23", "route-03", 6, "reconciliation", "expired", 0, 0),
    ),
    route_segment_table="rg04_route_segments",
    route_segment_rows=(
        ("route-01", "role-08", "segment-08", 7, 0, 79, "expired", 0),
        ("route-01", "role-17", "segment-17-checkout", 7, 10, 60, "assigned", 1),
        ("route-02", "role-17", "segment-17-checkout", 7, 10, 60, "assigned", 1),
        ("route-03", "role-23", "segment-23", 7, 10, 50, "assigned", 1),
        ("route-01", "role-17", "segment-17-checkout-old", 6, 0, 9, "expired", 0),
        ("route-02", "role-17", "segment-17-checkout-old", 6, 10, 60, "expired", 0),
        ("route-03", "role-23", "segment-23-old", 6, 10, 50, "expired", 0),
    ),
    request_binding_table="rg04_request_route_bindings",
    request_binding_rows=(
        ("checkout_status_rollup", "role-17", "route-01", "segment-17-checkout", 7, 45, 100, 1),
        ("checkout_status_rollup", "role-17", "route-02", "segment-17-checkout", 7, 42, 100, 1),
        ("checkout_tenant_dashboard", "role-17", "route-01", "segment-17-checkout", 7, 45, 100, 1),
        ("checkout_tenant_dashboard", "role-17", "route-02", "segment-17-checkout", 7, 42, 100, 1),
        ("checkout_detail_lookup", "role-17", "route-01", "segment-17-checkout", 7, 45, 100, 1),
        ("checkout_detail_lookup", "role-17", "route-02", "segment-17-checkout", 7, 42, 100, 1),
        ("checkout_time_window", "role-17", "route-01", "segment-17-checkout", 7, 45, 100, 1),
        ("checkout_time_window", "role-17", "route-02", "segment-17-checkout", 7, 42, 100, 1),
        ("settlement_status_rollup", "role-08", "route-01", "segment-08", 7, 44, 50, 0),
        ("reconciliation_status_rollup", "role-23", "route-03", "segment-23", 7, 42, 50, 1),
        ("checkout_status_rollup", "role-17", "route-01", "segment-17-checkout-old", 6, 30, 90, 0),
        ("checkout_status_rollup", "role-17", "route-02", "segment-17-checkout-old", 6, 30, 90, 0),
    ),
    request_context_table="rg04_request_contexts",
    request_context_rows=(
        ("checkout_status_rollup", "role-17", 7, 42, "current", 1),
        ("checkout_tenant_dashboard", "role-17", 7, 42, "current", 1),
        ("checkout_detail_lookup", "role-17", 7, 42, "current", 1),
        ("checkout_time_window", "role-17", 7, 42, "current", 1),
        ("settlement_status_rollup", "role-08", 7, 41, "expired", 0),
        ("reconciliation_status_rollup", "role-23", 7, 42, "current", 1),
        ("checkout_status_rollup", "role-17", 6, 30, "expired", 0),
    ),
    compliance_request_table="rg04_compliance_requests",
    compliance_request_rows=(
        (
            "approval-17-current",
            "role-17",
            "checkout_status_rollup",
            7,
            "regulated-eu",
            "three-distinct-zones",
            "zone/az-c",
            3,
            "table",
            "approved",
            1,
        ),
        (
            "approval-17-expired",
            "role-17",
            "checkout_status_rollup",
            6,
            "regulated-eu",
            "single-zone",
            "zone/az-a",
            3,
            "table",
            "expired",
            0,
        ),
        (
            "approval-23-current",
            "role-23",
            "reconciliation_status_rollup",
            7,
            "internal-control",
            "two-distinct-zones",
            "zone/az-b",
            3,
            "table",
            "approved",
            1,
        ),
    ),
    service_registry_table="rg04_service_registry",
    service_registry_rows=(
        ("role-08", "settlement", "standard", 1),
        ("role-17", "regulated-checkout", "regulated", 1),
        ("role-23", "reconciliation", "control", 1),
    ),
    legacy_policy="rg04_layout_a",
    target_policy="rg04_layout_b",
    semantic_policy="rg04_layout_majority_primary",
    audit_policy="rg04_layout_e",
    etl_policy="rg04_layout_f",
    neighbor_policies=("rg04_layout_c", "rg04_layout_d"),
    neighbor_row_counts=(12000, 12000),
    row_count=12000,
    business_query=(
        "SELECT status, COUNT(*) AS orders, SUM(amount) AS gross_amount "
        "FROM rg04_relation_02 WHERE tenant_id BETWEEN 10 AND 60 "
        "GROUP BY status ORDER BY status"
    ),
    required_replica_zones=("az-a", "az-b", "az-c"),
    leader_zone="az-c",
    min_available_bytes=512 * 1024 * 1024,
)

_NEIGHBOR_ISOLATION_CASE = replace(
    _CASE,
    case_id="compliance_table_neighbor_isolation",
    case_no=1,
    evaluator=TidbResourceGovernancePlacementPolicyNeighborIsolationEvaluatorCase,
    title="Move the regulated ledger relation while preserving the original checkout relation as a neighbor.",
    alert=(
        "[P1] A regulated ledger relation is not satisfying its approved placement requirement. The "
        "catalog contains same-shape relations with different service routes, policies, and historical "
        "epochs. Identify the committed relation and its approval from current routing and policy "
        "evidence, choose a policy the healthy stores can satisfy, and preserve the checkout neighbor, "
        "quorum, capacity headroom, and business results. Do not stop a node or alter cluster-wide "
        "replication settings."
    ),
    initial_state={
        "status": "running",
        "target_relation": "regulated ledger relation requires current-route correlation",
        "neighbor_relation": "checkout relation must remain unchanged",
        "leader_zone": "az-a",
        "replicas": 3,
    },
    expected_target={
        "status": "scheduled",
        "leader_zone": "az-c",
        "follower_zones": ("az-a", "az-b"),
        "replicas": 3,
        "target_relation": "rg04_relation_01",
        "neighbor_preserved": "rg04_relation_02",
        "business_result": "unchanged",
    },
    table="rg04_relation_01",
    neighbor_tables=("rg04_relation_02", "rg04_relation_03"),
    business_query=(
        "SELECT status, COUNT(*) AS orders, SUM(amount) AS gross_amount "
        "FROM rg04_relation_01 WHERE tenant_id BETWEEN 10 AND 60 "
        "GROUP BY status ORDER BY status"
    ),
    difficulty=DifficultyCalibration(
        diagnostic_depth=11,
        environmental_complexity=0.8,
        reference_run_ids=(
            "reference-277__tidb_resource_governance_placement_policy__"
            "compliance_table_neighbor_isolation__mock__r001",
        ),
    ),
)


class TidbResourceGovernancePlacementPolicyInjector(BaseFaultInjector):
    """Create a misplaced compliance table and real placement-policy evidence."""

    def install(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._preexisting_policy_names = frozenset(
            policy.casefold()
            for policy in self._list_policy_names(
                context.env,
                "capture pre-existing RG04 placement policies",
            )
        )
        fixed_policies = {policy.casefold() for policy in self._fixed_policies()}
        policy_collisions = sorted(
            policy
            for policy in self._preexisting_policy_names
            if policy.casefold() in fixed_policies
        )
        if policy_collisions:
            raise RuntimeError(
                "RG04 placement policy names are already in use before setup: "
                f"policies={policy_collisions!r}"
            )
        self._remove_previous_objects(context.env)
        self._create_policies(context.env)
        self._create_tables(context.env)
        self._load_tables(context.env)
        self._load_service_registry(context.env)
        self._load_workload_catalog(context.env)
        self._load_relation_directory(context.env)
        self._load_route_leases(context.env)
        self._load_route_allocations(context.env)
        self._load_traffic_assignments(context.env)
        self._load_route_segments(context.env)
        self._load_request_bindings(context.env)
        self._load_request_contexts(context.env)
        self._load_compliance_requests(context.env)
        for table, count in (
            (self.table, self.row_count),
            (self.neighbor_tables[0], self.neighbor_row_counts[0]),
            (self.neighbor_tables[1], self.neighbor_row_counts[1]),
        ):
            require_sql_success(
                context.env.execute_sql(
                    f"SPLIT TABLE {self.db}.{table} BETWEEN (0) AND ({count + 1}) REGIONS 4"
                ),
                f"split TiDB RG04 ledger table: table={self.db}.{table}",
            )
        self._verify_persistent_state(context.env)

    def activate(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state(context.env)

    def prepare_observability(self, context: FaultLifecycleContext) -> Mapping[str, object]:
        self._configure(context.config, context.env)
        self._verify_persistent_state(context.env)
        business_payload = json_object(
            context.env.execute_sql(self.business_query),
            f"capture RG04 business result: sql={self.business_query!r}",
        )
        return {
            "rg04_business_result_truth": capture_query_result_truth(
                business_payload,
                ordered=True,
            ),
            "rg04_initial_placement": json_object(
                context.env.execute_sql("SHOW PLACEMENT"),
                "capture RG04 initial placement",
            ),
            "rg04_store_labels": json_object(
                context.env.execute_sql(
                    "SELECT STORE_ID, STORE_STATE_NAME, LABEL, CAPACITY, AVAILABLE "
                    "FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS ORDER BY STORE_ID"
                ),
                "capture RG04 TiKV labels",
            ),
            "rg04_compliance_requests": json_object(
                context.env.execute_sql(
                    "SELECT request_id, service_role_code, request_shape, routing_epoch, "
                    "jurisdiction, survival_objective, leader_locality_code, required_voters, "
                    "policy_scope, request_state, active "
                    f"FROM {self.compliance_request_table} "
                    "ORDER BY request_id"
                ),
                "capture RG04 compliance requests",
            ),
            "rg04_policy_catalog": json_object(
                context.env.execute_sql(
                    "SELECT POLICY_NAME, PRIMARY_REGION, REGIONS, CONSTRAINTS, "
                    "LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, "
                    "SCHEDULE, FOLLOWERS, LEARNERS "
                    "FROM INFORMATION_SCHEMA.PLACEMENT_POLICIES ORDER BY POLICY_NAME"
                ),
                "capture RG04 policy catalog",
            ),
            "rg04_policy_attachments": json_object(
                context.env.execute_sql(
                    "SELECT TABLE_NAME, TIDB_PLACEMENT_POLICY_NAME "
                    "FROM INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_SCHEMA='{self.db}' ORDER BY TABLE_NAME"
                ),
                "capture RG04 policy attachments",
            ),
        }

    def quiesce(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        self._verify_persistent_state(context.env)

    def recover(self, context: FaultLifecycleContext) -> None:
        self._configure(context.config, context.env)
        for table in self.all_tables:
            require_sql_success(
                context.env.execute_sql(f"ALTER TABLE {self.db}.{table} PLACEMENT POLICY=default"),
                f"detach RG04 placement policy: table={self.db}.{table}",
            )
        for table in self.all_tables:
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE {self.db}.{table}"),
                f"drop RG04 table: table={self.db}.{table}",
            )
        for registry_table in (
            self.service_registry_table,
            self.workload_catalog_table,
            self.relation_directory_table,
            self.route_lease_table,
            self.route_allocation_table,
            self.traffic_assignment_table,
            self.route_segment_table,
            self.request_binding_table,
            self.request_context_table,
            self.compliance_request_table,
        ):
            require_sql_success(
                context.env.execute_sql(f"DROP TABLE {self.db}.{registry_table}"),
                f"drop RG04 registry table: table={self.db}.{registry_table}",
            )
        fixed_policies = {policy.casefold() for policy in self._fixed_policies()}
        for policy in self._list_policy_names(
            context.env,
            "list RG04 placement policies during recovery",
        ):
            if (
                policy.casefold() == "default"
                or policy.casefold() in fixed_policies
                or policy.casefold() in self._preexisting_policy_names
            ):
                continue
            require_sql_success(
                context.env.execute_sql(f"DROP PLACEMENT POLICY {policy}"),
                f"drop Agent-created RG04 placement policy: policy={policy}",
            )
        for policy in self._fixed_policies():
            require_sql_success(
                context.env.execute_sql(f"DROP PLACEMENT POLICY {policy}"),
                f"drop RG04 placement policy: policy={policy}",
            )

    def _fixed_policies(self) -> tuple[str, ...]:
        return (
            self.legacy_policy,
            self.target_policy,
            self.semantic_policy,
            self.audit_policy,
            self.etl_policy,
            *self.neighbor_policies,
        )

    @staticmethod
    def _list_policy_names(env: object, context: str) -> frozenset[str]:
        rows = json_object(
            env.execute_sql(
                "SELECT POLICY_NAME FROM INFORMATION_SCHEMA.PLACEMENT_POLICIES "
                "ORDER BY POLICY_NAME"
            ),
            context,
        )["result"]
        return frozenset(
            validate_sql_identifier(str(row[0]).strip("`"), "placement_policy")
            for row in rows
        )

    def _configure(self, config: Mapping[str, object], env: object) -> None:
        self.env = env
        self.db = validate_sql_identifier(str(config["db"]), "db")
        self.table = validate_sql_identifier(str(config["table"]), "table")
        self.noise_tables = tuple(
            validate_sql_identifier(str(table), "noise_table")
            for table in config["noise_tables"]
        )
        self.neighbor_tables = tuple(
            validate_sql_identifier(str(table), "neighbor_table")
            for table in config["neighbor_tables"]
        )
        self.legacy_policy = validate_sql_identifier(str(config["legacy_policy"]), "legacy_policy")
        self.target_policy = validate_sql_identifier(str(config["target_policy"]), "target_policy")
        self.semantic_policy = validate_sql_identifier(str(config["semantic_policy"]), "semantic_policy")
        self.audit_policy = validate_sql_identifier(str(config["audit_policy"]), "audit_policy")
        self.etl_policy = validate_sql_identifier(str(config["etl_policy"]), "etl_policy")
        self.neighbor_policies = tuple(
            validate_sql_identifier(str(policy), "neighbor_policy")
            for policy in config["neighbor_policies"]
        )
        self.neighbor_row_counts = tuple(int(count) for count in config["neighbor_row_counts"])
        self.service_registry_table = validate_sql_identifier(
            str(config["service_registry_table"]), "service_registry_table"
        )
        self.service_registry_rows = tuple(
            (str(role_code), str(purpose), str(service_class), int(active))
            for role_code, purpose, service_class, active in config["service_registry_rows"]
        )
        self.workload_catalog_table = validate_sql_identifier(
            str(config["workload_catalog_table"]), "workload_catalog_table"
        )
        self.workload_catalog_rows = tuple(
            (str(service_key), str(service_role), str(route_id), int(epoch), int(active))
            for service_key, service_role, route_id, epoch, active in config["workload_catalog_rows"]
        )
        self.relation_directory_table = validate_sql_identifier(
            str(config["relation_directory_table"]), "relation_directory_table"
        )
        self.relation_directory_rows = tuple(
            (str(route_id), int(epoch), str(relation), str(role), int(active))
            for route_id, epoch, relation, role, active in config["relation_directory_rows"]
        )
        self.route_lease_table = validate_sql_identifier(
            str(config["route_lease_table"]), "route_lease_table"
        )
        self.route_lease_rows = tuple(
            (str(route_id), int(epoch), str(lease_state), str(traffic_class), int(active))
            for route_id, epoch, lease_state, traffic_class, active in config["route_lease_rows"]
        )
        self.route_allocation_table = validate_sql_identifier(
            str(config["route_allocation_table"]), "route_allocation_table"
        )
        self.route_allocation_rows = tuple(
            (str(route_id), int(epoch), int(allocation_epoch), int(effective_epoch), str(allocation_state), str(traffic_class), int(active))
            for route_id, epoch, allocation_epoch, effective_epoch, allocation_state, traffic_class, active
            in config["route_allocation_rows"]
        )
        self.traffic_assignment_table = validate_sql_identifier(
            str(config["traffic_assignment_table"]), "traffic_assignment_table"
        )
        self.traffic_assignment_rows = tuple(
            (str(service_key), str(role_code), str(route_id), int(epoch), str(scope), str(state), int(share), int(active))
            for service_key, role_code, route_id, epoch, scope, state, share, active
            in config["traffic_assignment_rows"]
        )
        self.route_segment_table = validate_sql_identifier(
            str(config["route_segment_table"]), "route_segment_table"
        )
        self.route_segment_rows = tuple(
            (str(route_id), str(role_code), str(segment_id), int(epoch), int(start), int(end), str(state), int(active))
            for route_id, role_code, segment_id, epoch, start, end, state, active
            in config["route_segment_rows"]
        )
        self.request_binding_table = validate_sql_identifier(
            str(config["request_binding_table"]), "request_binding_table"
        )
        self.request_binding_rows = tuple(
            (
                str(shape),
                str(role_code),
                str(route_id),
                str(segment_id),
                int(epoch),
                int(binding_epoch),
                int(rank),
                int(active),
            )
            for shape, role_code, route_id, segment_id, epoch, binding_epoch, rank, active
            in config["request_binding_rows"]
        )
        self.request_context_table = validate_sql_identifier(
            str(config["request_context_table"]), "request_context_table"
        )
        self.request_context_rows = tuple(
            (
                str(shape),
                str(role_code),
                int(routing_epoch),
                int(context_epoch),
                str(context_state),
                int(active),
            )
            for shape, role_code, routing_epoch, context_epoch, context_state, active
            in config["request_context_rows"]
        )
        self.compliance_request_table = validate_sql_identifier(
            str(config["compliance_request_table"]), "compliance_request_table"
        )
        self.compliance_request_rows = tuple(
            (
                str(request_id),
                str(role_code),
                str(request_shape),
                int(routing_epoch),
                str(jurisdiction),
                str(survival_objective),
                str(leader_locality_code),
                int(required_voters),
                str(policy_scope),
                str(request_state),
                int(active),
            )
            for (
                request_id,
                role_code,
                request_shape,
                routing_epoch,
                jurisdiction,
                survival_objective,
                leader_locality_code,
                required_voters,
                policy_scope,
                request_state,
                active,
            ) in config["compliance_request_rows"]
        )
        self.all_tables = (self.table, *self.noise_tables, *self.neighbor_tables)
        self.row_count = int(config["row_count"])
        self.business_query = str(config["business_query"])

    def _remove_previous_objects(self, env: object) -> None:
        for table in self.all_tables:
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{table}"),
                f"clear RG04 table: table={self.db}.{table}",
            )
        for registry_table in (
            self.service_registry_table,
            self.workload_catalog_table,
            self.relation_directory_table,
            self.route_lease_table,
            self.route_allocation_table,
            self.traffic_assignment_table,
            self.route_segment_table,
            self.request_binding_table,
            self.request_context_table,
            self.compliance_request_table,
        ):
            require_sql_success(
                env.execute_sql(f"DROP TABLE IF EXISTS {self.db}.{registry_table}"),
                f"clear RG04 registry table: table={self.db}.{registry_table}",
            )
        for policy in (
            self.legacy_policy,
            self.target_policy,
            self.semantic_policy,
            self.audit_policy,
            self.etl_policy,
            *self.neighbor_policies,
        ):
            require_sql_success(
                env.execute_sql(f"DROP PLACEMENT POLICY IF EXISTS {policy}"),
                f"clear RG04 placement policy: policy={policy}",
            )

    def _create_policies(self, env: object) -> None:
        policies = (
            (
                self.legacy_policy,
                "LEADER_CONSTRAINTS='[+zone=az-a]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-a\": 1, \"+zone=az-b\": 1}'",
            ),
            (
                self.target_policy,
                "LEADER_CONSTRAINTS='[+zone=az-c]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-a\": 1, \"+zone=az-b\": 1}'",
            ),
            (
                self.semantic_policy,
                "PRIMARY_REGION='az-c' REGIONS='az-a,az-b,az-c' "
                "SCHEDULE='MAJORITY_IN_PRIMARY'",
            ),
            (
                self.audit_policy,
                "LEADER_CONSTRAINTS='[+zone=az-a]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-b\": 1, \"+zone=az-c\": 1}'",
            ),
            (
                self.etl_policy,
                "LEADER_CONSTRAINTS='[+zone=az-b]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-a\": 1, \"+zone=az-c\": 1}'",
            ),
            (
                self.neighbor_policies[0],
                "LEADER_CONSTRAINTS='[+zone=az-a]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-a\": 1, \"+zone=az-b\": 1}'",
            ),
            (
                self.neighbor_policies[1],
                "LEADER_CONSTRAINTS='[+zone=az-b]' "
                "FOLLOWER_CONSTRAINTS='{\"+zone=az-c\": 2}'",
            ),
        )
        for policy, constraints in policies:
            require_sql_success(
                env.execute_sql(f"CREATE PLACEMENT POLICY {policy} FOLLOWERS=2 {constraints}"),
                f"create RG04 placement policy: policy={policy}",
            )

    def _create_tables(self, env: object) -> None:
        table_definition = (
            "id BIGINT PRIMARY KEY, "
            "tenant_id INT NOT NULL, "
            "status VARCHAR(16) NOT NULL, "
            "event_ts DATETIME NOT NULL, "
            "amount DECIMAL(12,2) NOT NULL, "
            "payload VARCHAR(512) NOT NULL, "
            "KEY idx_tenant_status (tenant_id, status)"
        )
        definitions = (
            (self.table, self.legacy_policy),
            (self.noise_tables[0], self.audit_policy),
            (self.noise_tables[1], self.etl_policy),
            (self.neighbor_tables[0], self.neighbor_policies[0]),
            (self.neighbor_tables[1], self.neighbor_policies[1]),
        )
        for table, policy in definitions:
            require_sql_success(
                env.execute_sql(
                    f"CREATE TABLE {self.db}.{table} ({table_definition}) "
                    f"PLACEMENT POLICY={policy}"
                ),
                f"create RG04 table: table={self.db}.{table}",
            )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.service_registry_table} ("
                "service_role_code VARCHAR(32) PRIMARY KEY, "
                "business_purpose VARCHAR(64) NOT NULL, "
                "service_class VARCHAR(32) NOT NULL, "
                "active TINYINT NOT NULL"
                ")"
            ),
            f"create RG04 service registry: table={self.db}.{self.service_registry_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.workload_catalog_table} ("
                "service_key VARCHAR(64) NOT NULL, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "route_id VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (service_key, route_id, routing_epoch), "
                "KEY idx_route_epoch (route_id, routing_epoch)"
                ")"
            ),
            f"create RG04 workload catalog: table={self.db}.{self.workload_catalog_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.relation_directory_table} ("
                "route_id VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "relation_name VARCHAR(64) NOT NULL, "
                "relation_class VARCHAR(32) NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (route_id, routing_epoch), "
                "KEY idx_relation_name (relation_name)"
                ")"
            ),
            f"create RG04 relation directory: table={self.db}.{self.relation_directory_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.route_lease_table} ("
                "route_id VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "lease_state VARCHAR(16) NOT NULL, "
                "traffic_class VARCHAR(32) NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (route_id, routing_epoch), "
                "KEY idx_active_state (active, lease_state)"
                ")"
            ),
            f"create RG04 route leases: table={self.db}.{self.route_lease_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.route_allocation_table} ("
                "route_id VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "allocation_epoch BIGINT NOT NULL, "
                "effective_routing_epoch BIGINT NOT NULL, "
                "allocation_state VARCHAR(16) NOT NULL, "
                "traffic_class VARCHAR(32) NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (route_id, routing_epoch, allocation_epoch), "
                "KEY idx_active_state (active, allocation_state)"
                ")"
            ),
            f"create RG04 route allocations: table={self.db}.{self.route_allocation_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.traffic_assignment_table} ("
                "service_key VARCHAR(64) NOT NULL, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "route_id VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "traffic_scope VARCHAR(64) NOT NULL, "
                "claim_state VARCHAR(16) NOT NULL, "
                "traffic_share INT NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (service_key, route_id, routing_epoch), "
                "KEY idx_route_epoch (route_id, routing_epoch)"
                ")"
            ),
            f"create RG04 traffic assignment registry: table={self.db}.{self.traffic_assignment_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.route_segment_table} ("
                "route_id VARCHAR(32) NOT NULL, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "segment_id VARCHAR(64) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "tenant_start INT NOT NULL, "
                "tenant_end INT NOT NULL, "
                "segment_state VARCHAR(16) NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (route_id, routing_epoch, segment_id), "
                "KEY idx_role_epoch_range (service_role_code, routing_epoch, tenant_start, tenant_end)"
                ")"
            ),
            f"create RG04 route segment registry: table={self.db}.{self.route_segment_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.request_binding_table} ("
                "request_shape VARCHAR(64) NOT NULL, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "route_id VARCHAR(32) NOT NULL, "
                "segment_id VARCHAR(64) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "binding_epoch BIGINT NOT NULL, "
                "binding_rank INT NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (request_shape, service_role_code, route_id, routing_epoch), "
                "KEY idx_active_rank (service_role_code, routing_epoch, active, binding_rank)"
                ")"
            ),
            f"create RG04 request route binding registry: table={self.db}.{self.request_binding_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.request_context_table} ("
                "request_shape VARCHAR(64) NOT NULL, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "context_epoch BIGINT NOT NULL, "
                "context_state VARCHAR(16) NOT NULL, "
                "active TINYINT NOT NULL, "
                "PRIMARY KEY (request_shape, service_role_code, routing_epoch), "
                "KEY idx_active_context (service_role_code, routing_epoch, active, context_epoch)"
                ")"
            ),
            f"create RG04 request context registry: table={self.db}.{self.request_context_table}",
        )
        require_sql_success(
            env.execute_sql(
                f"CREATE TABLE {self.db}.{self.compliance_request_table} ("
                "request_id VARCHAR(64) PRIMARY KEY, "
                "service_role_code VARCHAR(32) NOT NULL, "
                "request_shape VARCHAR(64) NOT NULL, "
                "routing_epoch BIGINT NOT NULL, "
                "jurisdiction VARCHAR(32) NOT NULL, "
                "survival_objective VARCHAR(64) NOT NULL, "
                "leader_locality_code VARCHAR(32) NOT NULL, "
                "required_voters INT NOT NULL, "
                "policy_scope VARCHAR(16) NOT NULL, "
                "request_state VARCHAR(16) NOT NULL, "
                "active TINYINT NOT NULL, "
                "KEY idx_active_request (service_role_code, request_shape, routing_epoch, active)"
                ")"
            ),
            f"create RG04 compliance request registry: table={self.db}.{self.compliance_request_table}",
        )

    def _load_tables(self, env: object) -> None:
        for table, count, prefix in (
            (self.table, self.row_count, "relation-02"),
            (self.noise_tables[0], 2400, "audit-event"),
            (self.noise_tables[1], 1800, "etl-stage"),
            (self.neighbor_tables[0], self.neighbor_row_counts[0], "relation-01"),
            (self.neighbor_tables[1], self.neighbor_row_counts[1], "relation-03"),
        ):
            for start in range(1, count + 1, 600):
                end = min(start + 600, count + 1)
                values = ",".join(
                    (
                        f"({row_id}, {row_id % 80}, "
                        f"'{self._status(prefix, row_id)}', "
                        f"FROM_UNIXTIME({1700000000 + row_id}), "
                        f"{row_id % 1000}.{row_id % 100:02d}, "
                        f"RPAD('{prefix}', 256, 'x'))"
                    )
                    for row_id in range(start, end)
                )
                require_sql_success(
                    env.execute_sql(
                        f"INSERT INTO {self.db}.{table} "
                        "(id, tenant_id, status, event_ts, amount, payload) "
                        f"VALUES {values}"
                    ),
                    f"load RG04 table batch: table={self.db}.{table}, start={start}, end={end - 1}",
                )
    def _load_service_registry(self, env: object) -> None:
        values = ",".join(
            f"('{role_code}', '{purpose}', '{service_class}', {active})"
            for role_code, purpose, service_class, active in self.service_registry_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.service_registry_table} "
                "(service_role_code, business_purpose, service_class, active) VALUES "
                f"{values}"
            ),
            f"load RG04 service registry: table={self.db}.{self.service_registry_table}",
        )

    def _load_workload_catalog(self, env: object) -> None:
        values = ",".join(
            f"('{service_key}', '{role_code}', '{route_id}', {epoch}, {active})"
            for service_key, role_code, route_id, epoch, active in self.workload_catalog_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.workload_catalog_table} "
                "(service_key, service_role_code, route_id, routing_epoch, active) VALUES "
                f"{values}"
            ),
            f"load RG04 workload catalog: table={self.db}.{self.workload_catalog_table}",
        )

    def _load_relation_directory(self, env: object) -> None:
        values = ",".join(
            f"('{route_id}', {epoch}, '{relation}', '{relation_class}', {active})"
            for route_id, epoch, relation, relation_class, active in self.relation_directory_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.relation_directory_table} "
                "(route_id, routing_epoch, relation_name, relation_class, active) VALUES "
                f"{values}"
            ),
            f"load RG04 relation directory: table={self.db}.{self.relation_directory_table}",
        )

    def _load_route_leases(self, env: object) -> None:
        values = ",".join(
            f"('{route_id}', {epoch}, '{lease_state}', '{traffic_class}', {active})"
            for route_id, epoch, lease_state, traffic_class, active in self.route_lease_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.route_lease_table} "
                "(route_id, routing_epoch, lease_state, traffic_class, active) VALUES "
                f"{values}"
            ),
            f"load RG04 route leases: table={self.db}.{self.route_lease_table}",
        )

    def _load_route_allocations(self, env: object) -> None:
        values = ",".join(
            f"('{route_id}', {epoch}, {allocation_epoch}, {effective_epoch}, '{allocation_state}', '{traffic_class}', {active})"
            for route_id, epoch, allocation_epoch, effective_epoch, allocation_state, traffic_class, active
            in self.route_allocation_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.route_allocation_table} "
                "(route_id, routing_epoch, allocation_epoch, effective_routing_epoch, allocation_state, traffic_class, active) VALUES "
                f"{values}"
            ),
            f"load RG04 route allocations: table={self.db}.{self.route_allocation_table}",
        )

    def _load_traffic_assignments(self, env: object) -> None:
        values = ",".join(
            f"('{service_key}', '{role_code}', '{route_id}', {epoch}, '{scope}', '{state}', {share}, {active})"
            for service_key, role_code, route_id, epoch, scope, state, share, active
            in self.traffic_assignment_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.traffic_assignment_table} "
                "(service_key, service_role_code, route_id, routing_epoch, traffic_scope, claim_state, traffic_share, active) VALUES "
                f"{values}"
            ),
            f"load RG04 traffic assignment registry: table={self.db}.{self.traffic_assignment_table}",
        )

    def _load_route_segments(self, env: object) -> None:
        values = ",".join(
            f"('{route_id}', '{role_code}', '{segment_id}', {epoch}, {start}, {end}, '{state}', {active})"
            for route_id, role_code, segment_id, epoch, start, end, state, active
            in self.route_segment_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.route_segment_table} "
                "(route_id, service_role_code, segment_id, routing_epoch, tenant_start, tenant_end, segment_state, active) VALUES "
                f"{values}"
            ),
            f"load RG04 route segment registry: table={self.db}.{self.route_segment_table}",
        )

    def _load_request_bindings(self, env: object) -> None:
        values = ",".join(
            f"('{shape}', '{role_code}', '{route_id}', '{segment_id}', {epoch}, {binding_epoch}, {rank}, {active})"
            for shape, role_code, route_id, segment_id, epoch, binding_epoch, rank, active
            in self.request_binding_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.request_binding_table} "
                "(request_shape, service_role_code, route_id, segment_id, routing_epoch, binding_epoch, binding_rank, active) VALUES "
                f"{values}"
            ),
            f"load RG04 request route bindings: table={self.db}.{self.request_binding_table}",
        )

    def _load_request_contexts(self, env: object) -> None:
        values = ",".join(
            f"('{shape}', '{role_code}', {routing_epoch}, {context_epoch}, '{context_state}', {active})"
            for shape, role_code, routing_epoch, context_epoch, context_state, active
            in self.request_context_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.request_context_table} "
                "(request_shape, service_role_code, routing_epoch, context_epoch, context_state, active) VALUES "
                f"{values}"
            ),
            f"load RG04 request contexts: table={self.db}.{self.request_context_table}",
        )

    def _load_compliance_requests(self, env: object) -> None:
        values = ",".join(
            (
                f"('{request_id}', '{role_code}', '{request_shape}', {routing_epoch}, "
                f"'{jurisdiction}', '{survival_objective}', '{leader_locality_code}', "
                f"{required_voters}, '{policy_scope}', '{request_state}', {active})"
            )
            for (
                request_id,
                role_code,
                request_shape,
                routing_epoch,
                jurisdiction,
                survival_objective,
                leader_locality_code,
                required_voters,
                policy_scope,
                request_state,
                active,
            ) in self.compliance_request_rows
        )
        require_sql_success(
            env.execute_sql(
                f"INSERT INTO {self.db}.{self.compliance_request_table} "
                "(request_id, service_role_code, request_shape, routing_epoch, jurisdiction, "
                "survival_objective, leader_locality_code, required_voters, policy_scope, "
                "request_state, active) VALUES "
                f"{values}"
            ),
            f"load RG04 compliance requests: table={self.db}.{self.compliance_request_table}",
        )

    @staticmethod
    def _status(prefix: str, row_id: int) -> str:
        if prefix == "relation-02" or prefix.startswith("relation-"):
            return ("paid", "pending", "cancelled")[row_id % 3]
        if prefix == "audit-event":
            return ("recorded", "review", "archived")[row_id % 3]
        return ("queued", "running", "complete")[row_id % 3]

    def _verify_persistent_state(self, env: object) -> None:
        expected_counts = {
            self.table: self.row_count,
            self.noise_tables[0]: 2400,
            self.noise_tables[1]: 1800,
            self.neighbor_tables[0]: self.neighbor_row_counts[0],
            self.neighbor_tables[1]: self.neighbor_row_counts[1],
        }
        for table, expected in expected_counts.items():
            payload = json_object(
                env.execute_sql(f"SELECT COUNT(*) FROM {self.db}.{table}"),
                f"verify RG04 row count: table={self.db}.{table}",
            )
            actual = payload["result"]
            if actual != [[expected]]:
                raise RuntimeError(
                    f"RG04 table row count mismatch: table={self.db}.{table}, "
                    f"expected={expected}, actual={actual!r}"
                )
        registry_counts = (
            (self.service_registry_table, len(self.service_registry_rows)),
            (self.workload_catalog_table, len(self.workload_catalog_rows)),
            (self.relation_directory_table, len(self.relation_directory_rows)),
            (self.route_lease_table, len(self.route_lease_rows)),
            (self.route_allocation_table, len(self.route_allocation_rows)),
            (self.traffic_assignment_table, len(self.traffic_assignment_rows)),
            (self.route_segment_table, len(self.route_segment_rows)),
            (self.request_binding_table, len(self.request_binding_rows)),
            (self.request_context_table, len(self.request_context_rows)),
            (self.compliance_request_table, len(self.compliance_request_rows)),
        )
        for registry_table, expected in registry_counts:
            registry_payload = json_object(
                env.execute_sql(f"SELECT COUNT(*) FROM {self.db}.{registry_table}"),
                f"verify RG04 registry row count: table={self.db}.{registry_table}",
            )
            if registry_payload["result"] != [[expected]]:
                raise RuntimeError(
                    f"RG04 registry row count mismatch: table={self.db}.{registry_table}, "
                    f"expected={expected}, actual={registry_payload['result']!r}"
                )
        labels = json_object(
            env.execute_sql(
                "SELECT LABEL FROM INFORMATION_SCHEMA.TIKV_STORE_STATUS "
                "WHERE STORE_STATE_NAME='Up' ORDER BY STORE_ID"
            ),
            "verify RG04 TiKV store labels",
        )["result"]
        observed_zones = {
            str(self._store_labels(row[0])["zone"])
            for row in labels
        }
        if observed_zones != {"az-a", "az-b", "az-c"}:
            raise RuntimeError(
                f"RG04 TiKV zone labels are incomplete: expected={{'az-a', 'az-b', 'az-c'}}, "
                f"actual={sorted(observed_zones)!r}"
            )

    @staticmethod
    def _store_labels(raw: object) -> dict[str, str]:
        return {
            str(label["key"]): str(label["value"])
            for label in json.loads(str(raw))
        }


class TidbResourceGovernancePlacementPolicyScenario(TiDBScenario):
    scenario_id = "tidb_resource_governance_placement_policy"
    description = "Migrate a TiDB compliance table to a regulated zone while preserving replica safety."
    cases = (_CASE, _NEIGHBOR_ISOLATION_CASE)

    def build_fault_plan(
        self,
        case: TidbResourceGovernancePlacementPolicyForComplianceTableZoneMigrationScenarioCase,
    ) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=TidbResourceGovernancePlacementPolicyInjector,
                config={
                    "db": case.db,
                    "table": case.table,
                    "noise_tables": case.protected_tables,
                    "neighbor_tables": case.neighbor_tables,
                    "service_registry_table": case.service_registry_table,
                    "service_registry_rows": case.service_registry_rows,
                    "workload_catalog_table": case.workload_catalog_table,
                    "workload_catalog_rows": case.workload_catalog_rows,
                    "relation_directory_table": case.relation_directory_table,
                    "relation_directory_rows": case.relation_directory_rows,
                    "route_lease_table": case.route_lease_table,
                    "route_lease_rows": case.route_lease_rows,
                    "route_allocation_table": case.route_allocation_table,
                    "route_allocation_rows": case.route_allocation_rows,
                    "traffic_assignment_table": case.traffic_assignment_table,
                    "traffic_assignment_rows": case.traffic_assignment_rows,
                    "route_segment_table": case.route_segment_table,
                    "route_segment_rows": case.route_segment_rows,
                    "request_binding_table": case.request_binding_table,
                    "request_binding_rows": case.request_binding_rows,
                    "request_context_table": case.request_context_table,
                    "request_context_rows": case.request_context_rows,
                    "compliance_request_table": case.compliance_request_table,
                    "compliance_request_rows": case.compliance_request_rows,
                    "legacy_policy": case.legacy_policy,
                    "target_policy": case.target_policy,
                    "semantic_policy": case.semantic_policy,
                    "audit_policy": case.audit_policy,
                    "etl_policy": case.etl_policy,
                    "neighbor_policies": case.neighbor_policies,
                    "neighbor_row_counts": case.neighbor_row_counts,
                    "row_count": case.row_count,
                    "business_query": case.business_query,
                },
            ),
        )
