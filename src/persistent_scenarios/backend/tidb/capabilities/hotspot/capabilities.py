"""Instance-1 (tidb_oltp_hotspot_resilience) event capability bindings.

Capabilities follow the frozen core protocol exactly
(``src/persistent_scenarios/backend/contracts.py``): typed declaration with
per-entity resource ownership, activate returning attempt plus exactly one of
applied/prevented evidence, symptom-only alerts, and cleanup that reverts only
injector-owned state (published configuration and agent repairs are run facts
and are never reverted).
"""

from __future__ import annotations

import threading
import time

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
from src.persistent_scenarios.runtime.ledger import JSONValue
from src.persistent_scenarios.tidb.hotspot import schema
from src.persistent_scenarios.tidb.hotspot.business import settlement_touch
from src.persistent_scenarios.tidb.port import TiDBPersistentEnvironmentPort

ACTIVATION_BUDGET_SECONDS = 20.0
IMPACT_POLL_SECONDS = 0.5


def _port(context) -> TiDBPersistentEnvironmentPort:
    environment = context.environment
    for name in (
        "control_connection", "workload", "set_tikv_io_rate_limit", "tikv_io_rate_limit",
        "table_leader_distribution", "set_tikv_container_cpu_limit", "tikv_container_cpu_limit",
    ):
        if not hasattr(environment, name):
            raise RuntimeError(
                f"TiDB persistent environment does not provide the required port method: "
                f"method={name!r}, environment={type(environment).__name__}"
            )
    return environment


def released_config_version(payload_version: int, applied_version: int) -> int:
    """The version a planned client release lands at.

    The planned release version is a floor, not a static identity: agent
    publications of the same control row raise the applied version, and a
    release that tried to reuse an already-applied version would be rejected
    by the driver's strict-version validation. The release therefore lands
    above every applied publication, which keeps the release effective without
    rolling an agent publication back.
    """
    return payload_version if payload_version > applied_version else applied_version + 1


def _wait_for(predicate, *, clock, stop, budget_seconds: float):
    deadline = clock.monotonic() + budget_seconds
    while True:
        value = predicate()
        if value is not None:
            return value
        if clock.monotonic() >= deadline:
            return None
        clock.wait_until(clock.monotonic() + IMPACT_POLL_SECONDS, stop)


class PromoHotspotCapability:
    """Concentrates the externally planned traffic onto one promotion group.

    Pure workload-tier change driven through the driver control surface; the
    promotion surge itself is silent business input (trigger silent).
    """

    capability_id = "promo_hotspot"
    _PARAMS = frozenset({"tier"})

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"traffic:promo:{event.entity}",
                resource_kind="workload_traffic",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=int(ACTIVATION_BUDGET_SECONDS),
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        tier = str(payload["tier"])
        driver = _port(context).workload()
        attempted_at = context.clock.monotonic()
        driver.apply_tier(tier)
        applied_at = context.clock.monotonic()
        return EventActivationResult(
            handle=_TierHandle(event_id=context.event.event_id, tier=tier),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=attempted_at,
                detail={"tier": tier},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=applied_at,
                facts={"tier": driver.current_tier(), "expected": tier},
            ),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="订单提交延迟上升",
            symptoms=["热门商品相关订单的提交与支付时延显著上升，库存行等待增加"],
            severity="critical",
            category="trade_degradation",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}


class _TierHandle:
    def __init__(self, *, event_id: str, tier: str) -> None:
        self.event_id = event_id
        self.tier = tier


class SettlementLongTxCapability:
    """A settlement client runs its bounded batch of hot-row settlement legs.

    Each leg is a real business attempt: it takes the inventory row's write
    lock (``SELECT ... FOR UPDATE``) and holds it for the batch hold window
    before committing, then — unless the settlement client is paused — moves
    on to the next queued leg after a short gap. The queue is the coupling
    surface: its later legs sit on the promotion wave-2 hot rows, so an
    unresolved batch still holds a wave-2 row while the second wave runs.
    Killing the current session does not stop the batch (the client
    reconnects and continues its queue); the documented
    ``ops.client_config.settlement_paused`` publication stops it after the
    current leg. Cleanup releases only this client's sessions (rollback +
    KILL fallback) and never touches agent sessions.
    """

    capability_id = "settlement_long_tx"
    _PARAMS = frozenset({"queue", "hold_seconds", "leg_gap_seconds"})
    TRX_SQL = "SELECT SESSION_ID FROM INFORMATION_SCHEMA.TIDB_TRX"
    CONNECTION_ID_SQL = "SELECT CONNECTION_ID()"
    PAUSE_READ_SQL = "SELECT settlement_paused FROM ops.client_config WHERE id = 1"

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"session:settlement-tx:{event.entity}",
                resource_kind="database_session",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=int(ACTIVATION_BUDGET_SECONDS),
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        legs = tuple(str(sku) for sku in payload["queue"])
        hold_seconds = float(payload["hold_seconds"])
        leg_gap_seconds = float(payload["leg_gap_seconds"])
        if not legs:
            raise ValueError(
                f"settlement batch queue must not be empty: event_id={context.event.event_id!r}"
            )
        unknown_skus = sorted(set(legs) - set(schema.SEED_PRICE_CENTS))
        if unknown_skus:
            raise ValueError(
                f"settlement batch queue references SKUs without seeded inventory rows: "
                f"event_id={context.event.event_id!r}, unknown_skus={unknown_skus!r}"
            )
        if hold_seconds <= 0:
            raise ValueError(f"hold_seconds must be positive: value={hold_seconds}")
        if leg_gap_seconds < 0:
            raise ValueError(f"leg_gap_seconds must be non-negative: value={leg_gap_seconds}")
        port = _port(context)
        handle = _LongTxHandle(event_id=context.event.event_id, port=port)
        handle.thread = threading.Thread(
            target=self._run,
            args=(handle, legs, hold_seconds, leg_gap_seconds, context.clock),
            daemon=True,
            name=f"tidb5-settlement-tx-{handle.event_id}",
        )
        handle.thread.start()
        attempted_at = context.clock.monotonic()
        # A preventive pause publication (a legitimate agent action before this
        # event's arrival) stops the batch before its first leg: that is the
        # prevented path of this capability, reported as prevented evidence —
        # never an arrival failure.
        deadline = context.clock.monotonic() + ACTIVATION_BUDGET_SECONDS
        while True:
            if handle.connection_id is not None:
                break
            if handle.prevented_reason is not None:
                return EventActivationResult(
                    handle=handle,
                    attempt=EventAttemptEvidence(
                        attempted_at_monotonic=attempted_at,
                        detail={"queue": list(legs), "hold_seconds": hold_seconds},
                    ),
                    applied=None,
                    prevented=PreventionEvidence(
                        attempted=EventAttemptEvidence(
                            attempted_at_monotonic=attempted_at,
                            detail={"queue": list(legs), "hold_seconds": hold_seconds},
                        ),
                        mechanism="settlement_batch_paused",
                        protection_state={"paused_at_leg": handle.paused_at_leg},
                        observed_at_monotonic=context.clock.monotonic(),
                    ),
                )
            if context.clock.monotonic() >= deadline:
                raise RuntimeError(
                    f"settlement batch did not start within its activation budget: "
                    f"event_id={handle.event_id!r}, queue={legs!r}"
                )
            context.clock.wait_until(context.clock.monotonic() + IMPACT_POLL_SECONDS, handle.stop)
        observed = _wait_for(
            lambda: self._open_transaction_facts(port, handle),
            clock=context.clock, stop=handle.stop,
            budget_seconds=ACTIVATION_BUDGET_SECONDS,
        )
        if observed is None:
            raise RuntimeError(
                f"held settlement leg is not observable in INFORMATION_SCHEMA.TIDB_TRX: "
                f"event_id={handle.event_id!r}, connection_id={handle.connection_id!r}"
            )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=attempted_at,
                detail={"queue": list(legs), "hold_seconds": hold_seconds, "connection_id": handle.connection_id},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "open_transactions": observed,
                    "connection_id": handle.connection_id,
                    "holding_sku": handle.holding_sku,
                    "batch_legs": len(legs),
                },
            ),
            prevented=None,
        )

    def _run(self, handle, legs: tuple[str, ...], hold_seconds: float, leg_gap_seconds: float, clock) -> None:
        for index, sku in enumerate(legs):
            if handle.stop.is_set():
                return
            if self._settlement_paused(handle.port):
                handle.paused_at_leg = index
                if index == 0:
                    handle.prevented_reason = "settlement_batch_paused_before_first_leg"
                return
            connection = handle.port.control_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(self.CONNECTION_ID_SQL)
                    handle.connection_id = int(cursor.fetchone()[0])
                connection.commit()
                handle.connection_ids = handle.connection_ids + (handle.connection_id,)
                handle.holding_sku = sku
                handle.leg_index = index
                settlement_touch(connection, sku)
                clock.wait_until(clock.monotonic() + hold_seconds, handle.stop)
                if handle.stop.is_set():
                    connection.rollback()
                else:
                    connection.commit()
            except Exception as exc:  # noqa: BLE001 - the batch client reconnects and continues its queue
                handle.leg_failures = handle.leg_failures + (
                    {"leg_index": index, "sku": sku, "error": repr(exc)},
                )
            finally:
                try:
                    connection.close()
                except Exception:
                    pass
            if handle.stop.is_set():
                return
            if leg_gap_seconds > 0:
                clock.wait_until(clock.monotonic() + leg_gap_seconds, handle.stop)
        handle.batch_exhausted = True

    def _settlement_paused(self, port) -> bool:
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.PAUSE_READ_SQL)
                row = cursor.fetchone()
            connection.commit()
        finally:
            connection.close()
        if row is None:
            raise RuntimeError("ops.client_config has no policy row for id=1")
        return bool(int(row[0]))

    def _open_transaction_facts(self, port, handle) -> list[int] | None:
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.TRX_SQL)
                rows = cursor.fetchall()
            connection.commit()
        finally:
            connection.close()
        conn_ids = [int(row[0]) for row in rows]
        return conn_ids if handle.connection_id in conn_ids else None

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="交易下单/支付成功率下降",
            symptoms=[
                "部分订单事务在库存行上长时间等待，端到端时延上升",
                "存在长时间未提交的事务持有热点行锁（事务年龄异常增长）",
            ],
            severity="critical",
            category="trade_degradation",
        )

    def cleanup(self, handle) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        if handle.thread is not None:
            handle.thread.join(timeout=60)
        for connection_id in handle.connection_ids:
            port = handle.port
            connection = port.control_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"KILL {int(connection_id)}")
                connection.commit()
            except Exception as exc:  # the session may already be gone: verify below
                handle.kill_errors = handle.kill_errors + (repr(exc),)
            finally:
                connection.close()
        if handle.thread is not None and handle.thread.is_alive():
            raise RuntimeError(
                f"settlement batch session did not stop: event_id={handle.event_id!r}, "
                f"connection_ids={handle.connection_ids!r}, kill_errors={handle.kill_errors!r}"
            )

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        handle = self._handle(handle)
        port = handle.port
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.TRX_SQL)
                rows = cursor.fetchall()
            connection.commit()
        finally:
            connection.close()
        conn_ids = [int(row[0]) for row in rows]
        clean = all(connection_id not in conn_ids for connection_id in handle.connection_ids)
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": clean,
            "remaining_open_transactions": len(conn_ids),
            "batch_legs_started": len(handle.connection_ids),
            "paused_at_leg": handle.paused_at_leg,
            "batch_exhausted": handle.batch_exhausted,
        }

    def _handle(self, handle) -> "_LongTxHandle":
        if not isinstance(handle, _LongTxHandle):
            raise ValueError(f"unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class _LongTxHandle:
    def __init__(self, *, event_id: str, port) -> None:
        self.event_id = event_id
        self.port = port
        self.thread: threading.Thread | None = None
        self.stop = threading.Event()
        self.connection_id: int | None = None
        self.connection_ids: tuple[int, ...] = ()
        self.holding_sku: str | None = None
        self.leg_index: int | None = None
        self.paused_at_leg: int | None = None
        self.batch_exhausted = False
        self.prevented_reason: str | None = None
        self.leg_failures: tuple[dict[str, JSONValue], ...] = ()
        self.kill_errors: tuple[str, ...] = ()


class TikvSlowThrottleCapability:
    """Applies a reversible I/O ceiling to the TiKV store carrying the hot table.

    The activation proves the store actually hosts the table's region leaders
    before slowing it down, captures the baseline limit, and restores it at
    cleanup. The Raft majority stays intact: the store is slowed, never stopped.
    """

    capability_id = "tikv_slow_throttle"
    _PARAMS = frozenset({"target", "max_bytes_per_sec", "table"})

    def declaration(self, event) -> CapabilityDeclaration:
        target = str(event.payload["target"])
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"store:{target}:io",
                resource_kind="tikv_io_rate_limit",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=int(ACTIVATION_BUDGET_SECONDS),
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        target = str(payload["target"])
        max_bytes = int(payload["max_bytes_per_sec"])
        table = str(payload["table"])
        if max_bytes <= 0:
            raise ValueError(f"max_bytes_per_sec must be positive: value={max_bytes}")
        port = _port(context)
        distribution = port.table_leader_distribution(table)
        if int(distribution.get(target, 0)) <= 0:
            raise RuntimeError(
                f"throttle target does not carry any leader region of the hot table: "
                f"target={target!r}, table={table!r}, leader_distribution={distribution!r}"
            )
        baseline = port.tikv_io_rate_limit(target)
        baseline_limit = int(baseline["max-bytes-per-sec"])
        handle = _ThrottleHandle(event_id=context.event.event_id, target=target, baseline_limit=baseline_limit, port=port)
        observed = port.set_tikv_io_rate_limit(target, max_bytes)
        if int(observed["max-bytes-per-sec"]) != max_bytes:
            raise RuntimeError(
                f"TiKV I/O limit did not take effect: target={target!r}, "
                f"requested={max_bytes}, observed={observed!r}"
            )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={"target": target, "max_bytes_per_sec": max_bytes, "baseline": baseline_limit},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "target": target,
                    "baseline_max_bytes_per_sec": baseline_limit,
                    "throttled_to_max_bytes_per_sec": max_bytes,
                    "leader_distribution": {str(key): int(value) for key, value in distribution.items()},
                },
            ),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="部分写入请求提交延迟上升",
            symptoms=[
                "涉及部分数据范围的写入提交时延持续上升",
                "存储节点磁盘 I/O 利用率异常，慢日志增多",
            ],
            severity="critical",
            category="storage_degradation",
        )

    def cleanup(self, handle) -> None:
        handle = self._handle(handle)
        if handle.restored:
            return
        observed = handle.port.set_tikv_io_rate_limit(handle.target, handle.baseline_limit)
        if int(observed["max-bytes-per-sec"]) != handle.baseline_limit:
            raise RuntimeError(
                f"TiKV I/O baseline restore failed: target={handle.target!r}, "
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

    def _handle(self, handle) -> "_ThrottleHandle":
        if not isinstance(handle, _ThrottleHandle):
            raise ValueError(f"unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class _ThrottleHandle:
    def __init__(self, *, event_id: str, target: str, baseline_limit: int, port) -> None:
        self.event_id = event_id
        self.target = target
        self.baseline_limit = baseline_limit
        self.port = port
        self.restored = False


class TikvThrottleReleaseCapability:
    """External release of a store I/O ceiling (timeline step, not a repair)."""

    capability_id = "tikv_throttle_release"
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
            max_activation_seconds=int(ACTIVATION_BUDGET_SECONDS),
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        target = str(payload["target"])
        max_bytes = int(payload["max_bytes_per_sec"])
        port = _port(context)
        before = port.tikv_io_rate_limit(target)
        observed = port.set_tikv_io_rate_limit(target, max_bytes)
        if int(observed["max-bytes-per-sec"]) != max_bytes:
            raise RuntimeError(
                f"TiKV I/O release did not take effect: target={target!r}, "
                f"requested={max_bytes}, observed={observed!r}"
            )
        already = int(before["max-bytes-per-sec"]) == max_bytes
        return EventActivationResult(
            handle=_ReleaseHandle(event_id=context.event.event_id, target=target),
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={"target": target, "max_bytes_per_sec": max_bytes},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "target": target,
                    "released_to_max_bytes_per_sec": max_bytes,
                    "already_at_baseline": already,
                    "before": {str(key): value for key, value in before.items()},
                },
            ),
            prevented=None,
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="存储限速解除",
            symptoms=["存储节点 I/O 限速已按变更窗口解除"],
            severity="info",
            category="storage_recovery",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}


class _ReleaseHandle:
    def __init__(self, *, event_id: str, target: str) -> None:
        self.event_id = event_id
        self.target = target


class LegacyClientReleaseCapability:
    """Publishes the legacy client's aggressive retry policy via the control table.

    The driver-side poller is the trusted client protection: a stale version
    or unsafe policy is rejected and the activation reports prevented evidence
    instead of adoption.
    """

    capability_id = "legacy_client_release"
    _PARAMS = frozenset({
        "config_version", "request_timeout_ms", "max_retries", "retry_backoff_ms", "retry_jitter_ms",
    })

    PUBLISH_SQL = (
        "UPDATE ops.client_config SET config_version = %s, request_timeout_ms = %s, max_retries = %s, "
        "retry_backoff_ms = %s, retry_jitter_ms = %s WHERE id = 1"
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
        # The planned release version is a floor: agent publications of the
        # same control row (documented application-config levers) raise the
        # applied version, and the driver's strict-version validation rejects
        # any stale republication. Landing above the applied version keeps the
        # release effective without rolling agent publications back — the
        # UPDATE below only touches the retry columns, so a published
        # order_id_prefix or settlement pause survives the release.
        target_version = released_config_version(
            int(payload["config_version"]), driver.applied_config_version()
        )
        connection = port.control_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.PUBLISH_SQL,
                    (
                        target_version,
                        int(payload["request_timeout_ms"]),
                        int(payload["max_retries"]),
                        int(payload["retry_backoff_ms"]),
                        int(payload["retry_jitter_ms"]),
                    ),
                )
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
                handle=_ReleaseHandle(event_id=context.event.event_id, target="ops.client_config"),
                attempt=EventAttemptEvidence(
                    attempted_at_monotonic=attempted_at,
                    detail={"config_version": target_version},
                ),
                applied=AppliedEvidence(
                    observed_at_monotonic=context.clock.monotonic(),
                    facts={
                        "config_version": target_version,
                        "adopted_by_driver": True,
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
                handle=_ReleaseHandle(event_id=context.event.event_id, target="ops.client_config"),
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
            f"client config publication was neither adopted nor rejected by the driver: "
            f"event_id={context.event.event_id!r}, config_version={payload['config_version']!r}"
        )

    def alert(self, context, handle) -> EventAlertPayload:
        return EventAlertPayload(
            title="客户端版本发布完成",
            symptoms=["旧版结算客户端按发布计划启用新重试策略：短超时、高重试次数、无退避"],
            severity="info",
            category="client_release",
        )

    def cleanup(self, handle) -> None:
        return None

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        return {"capability_id": self.capability_id, "clean": True}




class TikvCatchUpBurstCapability:
    """Post-release catch-up state transition on the previously throttled store.

    Once the store I/O ceiling is lifted, the store spends a bounded window
    catching up its accumulated backlog; its serving headroom is physically
    reduced during that window (a real container CPU ceiling on the same
    node). The hot-region leaders that the throttle activation proved on this
    store keep suffering while they stay concentrated here, and they sail
    through the same burst once they are rebalanced off — the burst is the
    re-verification window that turns an incomplete "release only" fix back
    into real wave-2 degradation. The ceiling auto-restores after the bounded
    window; cleanup is idempotent.
    """

    capability_id = "tikv_catch_up_burst"
    _PARAMS = frozenset({"target", "cpu_limit", "burst_seconds"})

    def declaration(self, event) -> CapabilityDeclaration:
        target = str(event.payload["target"])
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(ResourceOwnership(
                resource_key=f"container:{target}:cpu",
                resource_kind="tikv_container_cpu_limit",
                mode=OwnershipMode.EXCLUSIVE,
            ),),
            max_activation_seconds=int(ACTIVATION_BUDGET_SECONDS),
        )

    def activate(self, context) -> EventActivationResult:
        payload = context.event.payload
        target = str(payload["target"])
        cpu_limit = float(payload["cpu_limit"])
        burst_seconds = float(payload["burst_seconds"])
        if cpu_limit <= 0:
            raise ValueError(f"catch-up burst cpu_limit must be positive: value={cpu_limit}")
        if burst_seconds <= 0:
            raise ValueError(f"catch-up burst window must be positive: value={burst_seconds}")
        port = _port(context)
        baseline = port.tikv_container_cpu_limit(target)
        baseline_cpus = float(baseline["cpus"])
        if cpu_limit >= baseline_cpus:
            raise ValueError(
                f"catch-up burst cpu_limit must sit below the observed baseline to reduce headroom: "
                f"target={target!r}, cpu_limit={cpu_limit}, baseline_cpus={baseline_cpus}"
            )
        observed = port.set_tikv_container_cpu_limit(target, cpu_limit)
        if abs(float(observed["cpus"]) - cpu_limit) > 1e-9:
            raise RuntimeError(
                f"catch-up burst CPU ceiling did not take effect: target={target!r}, "
                f"requested={cpu_limit}, observed={observed!r}"
            )
        handle = _BurstHandle(event_id=context.event.event_id, target=target, baseline_cpus=baseline_cpus, port=port)
        handle.thread = threading.Thread(
            target=self._restore_after, args=(handle, burst_seconds, context.clock), daemon=True,
            name=f"tidb5-catch-up-burst-{handle.event_id}",
        )
        handle.thread.start()
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=context.clock.monotonic(),
                detail={"target": target, "cpu_limit": cpu_limit, "burst_seconds": burst_seconds},
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "target": target,
                    "baseline_cpus": baseline_cpus,
                    "burst_cpu_limit": cpu_limit,
                    "burst_seconds": burst_seconds,
                    "hot_leaders_on_target": int(port.table_leader_distribution("shop.orders").get(target, 0)),
                },
            ),
            prevented=None,
        )

    def _restore_after(self, handle, burst_seconds: float, clock) -> None:
        clock.wait_until(clock.monotonic() + burst_seconds, handle.stop)
        with handle.restore_lock:
            if handle.restored or handle.stop.is_set():
                return
            self._restore(handle)

    def _restore(self, handle) -> None:
        observed = handle.port.set_tikv_container_cpu_limit(handle.target, handle.baseline_cpus)
        if abs(float(observed["cpus"]) - handle.baseline_cpus) > 1e-9:
            raise RuntimeError(
                f"catch-up burst baseline restore failed: target={handle.target!r}, "
                f"baseline_cpus={handle.baseline_cpus}, observed={observed!r}"
            )
        handle.restored = True

    def alert(self, context, handle) -> EventAlertPayload:
        # The burst arrives as a silent state transition; the engine only
        # calls this for trigger=alert, and the payload stays symptom-only
        # should the trigger ever change.
        return EventAlertPayload(
            title="存储节点恢复窗口内处理能力波动",
            symptoms=["存储节点在解除限速后的恢复窗口内出现短暂的处理能力回退，相关范围访问延迟再次上升"],
            severity="warning",
            category="storage_recovery",
        )

    def cleanup(self, handle) -> None:
        handle = self._handle(handle)
        handle.stop.set()
        if handle.thread is not None:
            handle.thread.join(timeout=30)
        with handle.restore_lock:
            if not handle.restored:
                self._restore(handle)

    def assert_clean(self, handle) -> dict[str, JSONValue]:
        handle = self._handle(handle)
        observed = handle.port.tikv_container_cpu_limit(handle.target)
        return {
            "capability_id": self.capability_id,
            "event_id": handle.event_id,
            "clean": abs(float(observed["cpus"]) - handle.baseline_cpus) <= 1e-9,
            "baseline_cpus": handle.baseline_cpus,
            "observed": {str(key): value for key, value in observed.items()},
        }

    def _handle(self, handle) -> "_BurstHandle":
        if not isinstance(handle, _BurstHandle):
            raise ValueError(f"unexpected handle for {self.capability_id}: handle={handle!r}")
        return handle


class _BurstHandle:
    def __init__(self, *, event_id: str, target: str, baseline_cpus: float, port) -> None:
        self.event_id = event_id
        self.target = target
        self.baseline_cpus = baseline_cpus
        self.port = port
        self.thread: threading.Thread | None = None
        self.stop = threading.Event()
        self.restore_lock = threading.Lock()
        self.restored = False
