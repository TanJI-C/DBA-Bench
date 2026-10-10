"""Instance-5 (tidb_oltp_online_topology_change) event capability bindings.

The maintenance itself is agent work under a published, public work order;
these capabilities only deliver the external changes of the change window
(reserved store arrival with its placement-policy drift, trade peak,
connection-pool bias, bounded migration-link slowdown) and never retire
anything on the agent's behalf. Cleanup reverts only injector-owned
reversible state (I/O ceilings); topology facts, published policies and work
orders are run facts.
"""

from __future__ import annotations

import threading

from src.persistent_scenarios.backend.contracts import (
    AppliedEvidence,
    CapabilityDeclaration,
    EventActivationResult,
    EventAlertPayload,
    EventAttemptEvidence,
    OwnershipMode,
    PreventionEvidence,
    ResourceOwnership,
)
from src.persistent_scenarios.backend.tidb.capabilities.hotspot.capabilities import released_config_version
from src.persistent_scenarios.runtime.ledger import JSONValue

ACTIVATION_BUDGET_SECONDS = 30.0
IMPACT_POLL_SECONDS = 0.5


def _port(context):
    environment = context.environment
    for name in ("control_connection", "workload", "pd_stores", "start_tikv", "backend_connection_counts"):
        if not hasattr(environment, name):
            raise RuntimeError(
                f"TiDB persistent environment does not provide the required port method: "
                f"method={name!r}, environment={type(environment).__name__}"
            )
    return environment


def _wait_for(predicate, *, clock, stop, budget_seconds: float):
    deadline = clock.monotonic() + budget_seconds
    while True:
        value = predicate()
        if value is not None:
            return value
        if clock.monotonic() >= deadline:
            return None
        clock.wait_until(clock.monotonic() + IMPACT_POLL_SECONDS, stop)


class MaintenanceWorkOrderCapability:
    """Publishes the public maintenance work order through the control table.

    The work order freezes the change identities (reserved store, retire
    target, drain backend) and the public delivery deadlines. The driver's
    maintenance poller plans the ledger jobs from these rows; delivery is
    observed from trusted facts only.
    """

    capability_id = "maintenance_work_order"
    _PARAMS = frozenset({
        "order_id", "reserve_tikv", "retire_tikv", "drain_backend", "deliverable_ids", "deadlines",
    })

    INSERT_SQL = (
        "INSERT INTO ops.maintenance_orders (order_id, deliverable_id, kind, target, deadline_seconds, "
        "published_at_ms, status) VALUES (%s, %s, %s, %s, %s, %s, 'published')"
    )

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"table:ops.maintenance_orders:{event.entity}",
                resource_kind="control_table",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=30,
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        order_id = str(payload["order_id"])
        reserve_tikv = str(payload["reserve_tikv"])
        retire_tikv = str(payload["retire_tikv"])
        drain_backend = str(payload["drain_backend"])
        deliverable_ids = {str(key): str(value) for key, value in payload["deliverable_ids"].items()}
        deadlines = {str(key): int(value) for key, value in payload["deadlines"].items()}
        required_kinds = {"store_scaleout", "placement_satisfied", "tidb_drain", "store_retired"}
        missing = sorted(required_kinds - set(deadlines) - set(deliverable_ids))
        if missing:
            raise ValueError(
                f"maintenance work order lacks delivery deadlines or deliverable ids: "
                f"order_id={order_id!r}, missing={missing!r}"
            )
        rows = (
            ("store_scaleout", reserve_tikv, deadlines["store_scaleout"], deliverable_ids["store_scaleout"]),
            ("placement_satisfied", "ops.maintenance_tracking", deadlines["placement_satisfied"],
             deliverable_ids["placement_satisfied"]),
            ("tidb_drain", drain_backend, deadlines["tidb_drain"], deliverable_ids["tidb_drain"]),
            ("store_retired", retire_tikv, deadlines["store_retired"], deliverable_ids["store_retired"]),
        )
        port = _port(context)
        published_at_ms = int(context.clock.monotonic() * 1000)
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                for kind, target, deadline_seconds, deliverable_id in rows:
                    cursor.execute(
                        self.INSERT_SQL,
                        (order_id, deliverable_id, kind, target, deadline_seconds, published_at_ms),
                    )
            connection.commit()
        finally:
            connection.close()
        driver = port.workload()
        adopted = _wait_for(
            lambda: self._adopted_count(driver, deliverable_ids),
            clock=context.clock, stop=threading.Event(), budget_seconds=30,
        )
        if adopted is None:
            raise RuntimeError(
                f"maintenance work order was not adopted by the driver: order_id={order_id!r}, "
                f"rows={rows!r}"
            )
        return EventActivationResult(
            handle=_WorkOrderHandle(event_id=context.event.event_id, order_id=order_id),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={"order_id": order_id, "deliverables": len(rows)},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"order_id": order_id, "adopted_deliverables": adopted, "published_at_ms": published_at_ms},
            ),
            prevented=None,
        )

    def _adopted_count(self, driver, deliverable_ids) -> int | None:
        """Adoption = every deliverable planned by the driver's poller.

        The driver decides a terminal and removes the job from its planned
        set in the same step (decide-then-remove), so a deliverable that is
        already decided-and-removed is adopted too: requiring the id to still
        sit in the planned set would reject the fast legitimate decision
        path. Only an id in neither set means the poller never picked the
        work order up.
        """
        expected = set(deliverable_ids.values())
        adopted = driver.planned_deliverable_ids() | driver.decided_deliverable_ids()
        if expected.issubset(adopted):
            return len(expected)
        return None

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="在线拓扑变更维护窗口",
            symptoms=[
                "维护工单已发布：预留新存储节点扩容并纳入服务、修复放置策略偏差、"
                "摘除旧连接并退役指定旧存储节点",
                "交易服务在变更窗口内不得中断，交付期限以工单为准",
            ],
            severity="critical",
            category="maintenance",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}


class _WorkOrderHandle:
    def __init__(self, *, event_id: str, order_id: str) -> None:
        self.event_id = event_id
        self.order_id = order_id


class ReserveStoreArrivalCapability:
    """The reserved store arrives, carrying the change plan's placement drift.

    The reserved store joins first with its real zone label. The change plan
    then attaches its runbook placement policy, which pins every replica of
    the tracked table to the reserve zone — a constraint that matches exactly
    the one new store, so the attach is accepted while the replica count can
    never be satisfied. SHOW PLACEMENT sticks in a non-scheduled state and
    the repair is the agent's to choose. (A zero-matching constraint form is
    rejected outright by TiDB/PD at attach with 8243 ErrRuleContent — a real
    mechanism fact used by the prevention path.)
    """

    capability_id = "reserve_store_arrival"
    _PARAMS = frozenset({"target", "policy_name", "followers", "constraints", "tracked_table"})

    def declaration(self, event) -> CapabilityDeclaration:
        target = str(event.payload["target"])
        policy_name = str(event.payload["policy_name"])
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    resource_key=f"store:{target}:lifecycle",
                    resource_kind="tikv_store_lifecycle",
                    mode=OwnershipMode.EXCLUSIVE,
                ),
                ResourceOwnership(
                    resource_key=f"placement:policy:{policy_name}",
                    resource_kind="pd_placement_policy",
                    mode=OwnershipMode.EXCLUSIVE,
                ),
            ),
            max_activation_seconds=120,
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        target = str(payload["target"])
        policy_name = str(payload["policy_name"])
        followers = int(payload["followers"])
        constraints = str(payload["constraints"])
        tracked_table = str(payload["tracked_table"])
        port = _port(context)
        store = port.start_tikv(target)
        placement_before = self._placement_state(port, tracked_table)
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE PLACEMENT POLICY IF NOT EXISTS {policy_name} "
                    f"FOLLOWERS={followers} CONSTRAINTS=\"{constraints}\""
                )
                cursor.execute(f"ALTER TABLE {tracked_table} PLACEMENT POLICY={policy_name}")
            connection.commit()
        finally:
            connection.close()
        placement = self._placement_state(port, tracked_table)
        return EventActivationResult(
            handle=_ReserveStoreHandle(event_id=context.event.event_id, target=target, port=port),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={
                    "target": target,
                    "policy_name": policy_name,
                    "followers": followers,
                    "constraints": constraints,
                },
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "target": target,
                    "store_id": store.get("store_id"),
                    "store_state": store.get("state"),
                    "placement_state_before_policy": placement_before,
                    "placement_state": placement,
                    "policy_name": policy_name,
                },
            ),
            prevented=None,
        )

    def _placement_state(self, port, tracked_table: str) -> str:
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW PLACEMENT FOR TABLE {tracked_table}")
                row = cursor.fetchone()
            connection.commit()
        finally:
            connection.close()
        if row is None:
            # Measured TiDB v8.1 semantics: a table without an explicit
            # placement policy has NO SHOW PLACEMENT row at all, so the fresh
            # tracked table reads as the default layout - a fact to record,
            # not an error.
            return "NO-EXPLICIT-PLACEMENT"
        return str(row[2])

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="预留存储节点已到达",
            symptoms=["预留存储节点已按变更窗口启动并注册为新的 TiKV Store"],
            severity="info",
            category="maintenance",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        handle = self._handle(handle)
        for store in handle.port.pd_stores():
            record = store["store"]
            if str(record.get("address")) == f"{handle.target.rsplit('/', 1)[-1]}:20160":
                return {
                    "capability_id": self.capability_id,
                    "event_id": handle.event_id,
                    "clean": True,
                    "store_state": str(record.get("state_name")),
                }
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "clean": True, "store_state": None}

    def _handle(self, handle) -> "_ReserveStoreHandle":
        if not isinstance(handle, _ReserveStoreHandle):
            raise ValueError(f"unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class _ReserveStoreHandle:
    def __init__(self, *, event_id: str, target: str, port) -> None:
        self.event_id = event_id
        self.target = target
        self.port = port


class TradePeakCapability:
    """Raises the externally planned trade rate during the change window."""

    capability_id = "trade_peak"
    _PARAMS = frozenset({"tier"})

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"traffic:trade:{event.entity}",
                resource_kind="workload_traffic",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=30,
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        tier = str(payload["tier"])
        driver = _port(context).workload()
        driver.apply_tier(tier)
        return EventActivationResult(
            handle=_TierHandle(event_id=context.event.event_id, tier=tier),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(), detail={"tier": tier},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"tier": driver.current_tier(), "expected": tier},
            ),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="交易峰值到达",
            symptoms=["计划内的交易高峰进入变更窗口，订单提交速率上升"],
            severity="info",
            category="trade_peak",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}


class _TierHandle:
    def __init__(self, *, event_id: str, tier: str) -> None:
        self.event_id = event_id
        self.tier = tier


class ConnectionPoolBiasCapability:
    """The client fleet publishes a backend bias concentrating new connections
    onto the backend slated for drain. Adoption goes through the trusted
    driver poller; a stale/unsafe publication is prevented, not adopted."""

    capability_id = "connection_pool_bias"
    _PARAMS = frozenset({
        "config_version", "connect_bias", "max_connection_lifetime_seconds",
        "request_timeout_ms", "max_retries", "retry_backoff_ms", "retry_jitter_ms", "lock_wait_timeout_seconds",
    })

    PUBLISH_SQL = (
        "UPDATE ops.client_config SET config_version = %s, request_timeout_ms = %s, max_retries = %s, "
        "retry_backoff_ms = %s, retry_jitter_ms = %s, max_connection_lifetime_seconds = %s, "
        "connect_bias = %s, lock_wait_timeout_seconds = %s WHERE id = 1"
    )

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key="table:ops.client_config",
                resource_kind="control_table",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=30,
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        port = _port(context)
        driver = port.workload()
        # The planned bias version is a floor: agent publications of the
        # shared client-config control row raise the applied version, and the
        # driver's strict-version validation rejects any stale republication.
        # The bias must land even after agent publications, so it publishes
        # above the applied version (the UPDATE only rewrites the connection
        # columns; other published fields survive).
        target_version = released_config_version(
            int(payload["config_version"]), driver.applied_config_version()
        )
        params = (
            target_version,
            int(payload["request_timeout_ms"]),
            int(payload["max_retries"]),
            int(payload["retry_backoff_ms"]),
            int(payload["retry_jitter_ms"]),
            int(payload["max_connection_lifetime_seconds"]),
            str(payload["connect_bias"]),
            int(payload["lock_wait_timeout_seconds"]),
        )
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.PUBLISH_SQL, params)
            connection.commit()
        finally:
            connection.close()
        attempted_at = context.clock.monotonic()
        budget = driver.config.control_poll_seconds * 4 + 2.0

        def adopted_version():
            version = driver.applied_config_version()
            return version if version == target_version else None

        adopted = _wait_for(
            adopted_version, clock=context.clock, stop=threading.Event(), budget_seconds=budget,
        )
        if adopted is not None:
            return EventActivationResult(
                handle=_BiasHandle(event_id=context.event.event_id, backend=str(payload["connect_bias"])),
                attempt=EventAttemptEvidence(
                    attempted_at_monotonic=attempted_at,
                    detail={"config_version": target_version, "connect_bias": str(payload["connect_bias"])},
                ),
                applied=AppliedEvidence(
                    observed_at_monotonic=context.clock.monotonic(),
                    facts={
                        "config_version": target_version,
                        "connect_bias": str(payload["connect_bias"]),
                        "connection_counts": {
                            str(key): int(value) for key, value in driver.backend_connection_counts().items()
                        },
                    },
                ),
                prevented=None,
            )
        rejections = tuple(
            rejection
            for rejection in driver.rejected_publications()
            if rejection["published_version"] == str(target_version)
        )
        if rejections:
            return EventActivationResult(
                handle=_BiasHandle(event_id=context.event.event_id, backend=str(payload["connect_bias"])),
                attempt=EventAttemptEvidence(
                    attempted_at_monotonic=attempted_at,
                    detail={"config_version": target_version},
                ),
                applied=None,
                prevented=PreventionEvidence(
                    attempted=EventAttemptEvidence(
                        attempted_at_monotonic=attempted_at,
                        detail={"config_version": target_version},
                    ),
                    mechanism="client_config_validation",
                    protection_state={"rejections": [dict(rejection) for rejection in rejections]},
                    observed_at_monotonic=context.clock.monotonic(),
                ),
            )
        raise RuntimeError(
            f"connection pool bias publication was neither adopted nor rejected: "
            f"event_id={context.event.event_id!r}, config_version={target_version!r}"
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="客户端连接池配置发布",
            symptoms=["客户端连接池按发布计划调整了后端选择偏好与连接生命周期"],
            severity="info",
            category="client_release",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}


class _BiasHandle:
    def __init__(self, *, event_id: str, backend: str) -> None:
        self.event_id = event_id
        self.backend = backend


class MigrationLinkDelayCapability:
    """Slows the migration link by capping the reserved store's ingest I/O.

    Bounded and reversible: the baseline is captured at activation and the
    ceiling is restored at cleanup. The bound leaves the maintenance
    completable, per the change contract.
    """

    capability_id = "migration_link_delay"
    _PARAMS = frozenset({"target", "max_bytes_per_sec"})

    def declaration(self, event) -> CapabilityDeclaration:
        target = str(event.payload["target"])
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"store:{target}:io",
                resource_kind="tikv_io_rate_limit",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=30,
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        target = str(payload["target"])
        max_bytes = int(payload["max_bytes_per_sec"])
        if max_bytes <= 0:
            raise ValueError(f"max_bytes_per_sec must be positive: value={max_bytes}")
        port = _port(context)
        baseline = port.tikv_io_rate_limit(target)
        baseline_limit = int(baseline["max-bytes-per-sec"])
        observed = port.set_tikv_io_rate_limit(target, max_bytes)
        if int(observed["max-bytes-per-sec"]) != max_bytes:
            raise RuntimeError(
                f"migration link delay did not take effect: target={target!r}, "
                f"requested={max_bytes}, observed={observed!r}"
            )
        return EventActivationResult(
            handle=_DelayHandle(
                event_id=context.event.event_id, target=target, baseline_limit=baseline_limit, port=port,
            ),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={"target": target, "max_bytes_per_sec": max_bytes},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "target": target,
                    "baseline_max_bytes_per_sec": baseline_limit,
                    "delayed_to_max_bytes_per_sec": max_bytes,
                },
            ),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="变更链路带宽受限",
            symptoms=["变更窗口内迁移链路带宽受限，副本迁移速率下降"],
            severity="info",
            category="maintenance",
        )

    def cleanup(self, handle) -> None:
        handle = self._handle(handle)
        if handle.restored:
            return
        observed = handle.port.set_tikv_io_rate_limit(handle.target, handle.baseline_limit)
        if int(observed["max-bytes-per-sec"]) != handle.baseline_limit:
            raise RuntimeError(
                f"migration link baseline restore failed: target={handle.target!r}, "
                f"baseline={handle.baseline_limit}, observed={observed!r}"
            )
        handle.restored = True

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        handle = self._handle(handle)
        observed = handle.port.tikv_io_rate_limit(handle.target)
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": int(observed["max-bytes-per-sec"]) == handle.baseline_limit,
            "baseline_max_bytes_per_sec": handle.baseline_limit,
            "observed": {str(key): value for key, value in observed.items()},
        }

    def _handle(self, handle) -> "_DelayHandle":
        if not isinstance(handle, _DelayHandle):
            raise ValueError(f"unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class _DelayHandle:
    def __init__(self, *, event_id: str, target: str, baseline_limit: int, port) -> None:
        self.event_id = event_id
        self.target = target
        self.baseline_limit = baseline_limit
        self.port = port
        self.restored = False
