"""Instance binding records for the pg5 PostgreSQL assembly.

One ``InstanceBinding`` maps an ``environment.workload`` routing key to the
instance package's capability registry, verifier registry, driver parameters
and scenario identities. The default map is an explicit import list — no
automatic discovery — and instance packages without a landed implementation
are absent from it (assembly reports them as pending instead of guessing).

Binding styles:

- ``oltp`` — instance capabilities speak the module-local dialect and are
  wrapped by ``InstanceCapabilityAdapter``; the driver keeps its own
  ``BusinessLedger`` which the workload runtime translates into one core
  ``TrustedLedger``; verifiers take ``(params, ops=, snapshot=[, connection=])``
  and report ``passed``.
- ``warehouse`` — capabilities speak the core protocol directly; the driver is
  the core-shaped ``WarehouseReportingRuntime`` built over four per-service
  core ledgers; verifiers take ``(connection, LedgerView, params)`` and report
  their pass under a per-verifier fact key.
- ``htap`` — capabilities speak the core protocol directly; the driver is the
  instance's own ``PersistentWorkloadRuntime`` wrapped by
  ``HtapWorkloadRuntimeAdapter`` so only the core-shaped trusted ledger
  reaches the engine; verifiers take ``(open_connection, params)`` where
  ``open_connection(application_name, target)`` opens a verified connection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping

import yaml

from src.persistent_scenarios.backend.postgres.instance_adapter import (
    HtapWorkloadRuntimeAdapter,
    evidence_ledger_path,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    VERIFIERS_BY_ID as FRS_VERIFIERS,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    PRODUCTION_CALENDAR as FRS_PRODUCTION_CALENDAR,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    HtapReplicaFreshnessWorkloadProvider,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import (
    VERIFIERS_BY_ID as HTAP_VERIFIERS,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import (
    PRODUCTION_CALENDAR as HTAP_PRODUCTION_CALENDAR,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import (
    HtapSharedIsolationWorkloadProvider,
)
from src.persistent_scenarios.backend.postgres.capabilities.htap_replica_freshness import (
    CAPABILITIES_BY_ID as FRS_CAPABILITIES_BY_ID,
)
from src.persistent_scenarios.backend.postgres.capabilities.htap_shared_isolation import (
    CAPABILITIES_BY_ID as HTAP_CAPABILITIES_BY_ID,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import load_order_book_snapshot
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import EvidenceLedgerFile
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.runtime import DriverConfig, OltpWorkloadDriver
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import generate_inventory_rows
from src.persistent_scenarios.backend.postgres.workloads.warehouse_reporting.runtime import (
    SERVICE_IDS,
    WarehouseReportingRuntime,
)
from src.persistent_scenarios.backend.postgres.workloads.warehouse_reporting.verifiers import (
    VERIFIERS as WAREHOUSE_VERIFIERS,
)
from src.persistent_scenarios.runtime.ledger import TrustedLedger

from src.persistent_scenarios.backend.postgres.capabilities.business_priority import (
    CAPABILITY_REGISTRY as BUSINESS_PRIORITY_CAPABILITIES,
)
from src.persistent_scenarios.backend.postgres.capabilities.online_change import (
    CAPABILITY_REGISTRY as ONLINE_CHANGE_CAPABILITIES,
)
from src.persistent_scenarios.backend.postgres.capabilities.smoke import (
    CAPABILITY_REGISTRY as SMOKE_CAPABILITIES,
)
from src.persistent_scenarios.backend.postgres.capabilities.warehouse_reporting import (
    CAPABILITY_IDS as WAREHOUSE_CAPABILITY_IDS,
    WarehouseCapabilityRegistry,
)
from src.persistent_scenarios.backend.postgres.workloads.business_priority import config as business_priority_config
from src.persistent_scenarios.backend.postgres.workloads.online_change import config as online_change_config
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import VERIFIERS as OLTP_VERIFIERS
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.traffic import TrafficPlan, TrafficTier

_PROJECT_DEFINITIONS_ROOT = Path("src/persistent_scenarios/postgres")
_OLAP_DRIVER_YAML = _PROJECT_DEFINITIONS_ROOT / "pg_warehouse_batch_reporting.driver.yaml"


class InstanceBinding:
    """Assembly record for one instance package.

    ``scenario_ids`` ties the binding to the scenario identities it owns so a
    spec cannot run against another instance's mechanisms.
    ``style`` selects the capability/driver/verifier dialect ("oltp" or
    "warehouse"); ``connection_verifiers`` names the verifiers whose signature
    accepts a live connection; ``deliverable_verifiers`` maps a deliverable
    job to the instance verifier that owns its delivery truth.
    """

    def __init__(
        self,
        *,
        workload_key: str,
        scenario_ids: frozenset[str],
        capability_registry=None,
        verifiers: Mapping[str, Callable[..., Mapping[str, object]]],
        driver_factory: Callable[..., object],
        transaction_service_id: str = "trade",
        job_service_ids: Mapping[str, str] = (),
        job_ids: tuple[str, ...] = (),
        connection_verifiers: frozenset[str] = frozenset(),
        deliverable_verifiers: Mapping[str, str] = (),
        evidence_factory: Callable[[Path, str], EvidenceLedgerFile] | None = None,
        terminal_snapshot: Callable[..., object] | None = None,
        style: str = "oltp",
        postgres_runtime_options: str = "",
        verifier_ledgers: Mapping[str, str | None] = (),
        verifier_pass_fields: Mapping[str, str] = (),
        capability_registry_factory: Callable | None = None,
        capability_ids: tuple[str, ...] = (),
        ledgers_factory: Callable[[Path, str], Mapping[str, TrustedLedger]] | None = None,
        role_credentials: Mapping[str, str] = (),
    ):
        self.workload_key = workload_key
        self.scenario_ids = scenario_ids
        self.capability_registry = capability_registry
        self.verifiers = dict(verifiers)
        self.driver_factory = driver_factory
        self.transaction_service_id = transaction_service_id
        self.job_service_ids = dict(job_service_ids)
        self.job_ids = tuple(job_ids)
        self.connection_verifiers = frozenset(connection_verifiers)
        self.deliverable_verifiers = dict(deliverable_verifiers)
        self.evidence_factory = evidence_factory
        self.terminal_snapshot = terminal_snapshot
        self.style = style
        self.postgres_runtime_options = postgres_runtime_options
        self.verifier_ledgers = dict(verifier_ledgers)
        self.verifier_pass_fields = dict(verifier_pass_fields)
        self.capability_registry_factory = capability_registry_factory
        self.capability_ids = tuple(capability_ids)
        self.ledgers_factory = ledgers_factory
        self.role_credentials = dict(role_credentials)


def _oltp_driver_factory(plan, driver_config, *, new_version_column: str | None = None):
    def factory(*, source, clock, evidence, spec, run_id, scoring_origin):
        return OltpWorkloadDriver(
            source=source,
            clock=clock,
            evidence=evidence,
            plan=plan,
            config=driver_config,
            run_id=run_id,
            scoring_origin=scoring_origin,
            horizon_seconds=spec.horizon_seconds,
            input_stop_seconds=spec.input_stop_seconds,
            warmup_seconds=spec.warmup_seconds,
            new_version_column=new_version_column,
        )

    return factory


def _oltp_evidence_factory(evidence_root: Path, run_id: str) -> EvidenceLedgerFile:
    return EvidenceLedgerFile(evidence_ledger_path(evidence_root, run_id, "instance"), run_id)


def _role_passwords(role_credentials: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Dataset-image role table (role -> {user, password}) in binding form (role -> password)."""
    return {role: entry["password"] for role, entry in role_credentials.items()}


def _oltp_terminal_snapshot_factory(initial_inventory: Mapping[str, int]):
    def terminal_snapshot(environment):
        connection = environment.open_workload_connection("persistent_scenario-terminal-snapshot")
        try:
            return load_order_book_snapshot(connection, initial_inventory=initial_inventory)
        finally:
            connection.close()

    return terminal_snapshot


def _initial_inventory(promo_initial_qty: int) -> dict[str, int]:
    return {str(row["sku"]): int(row["qty_available"]) for row in generate_inventory_rows(promo_initial_qty)}


# The smoke trade stream must saturate the small pool once a promo hot row is
# locked: at 0.5 qps the locked-SKU collision rate stayed below the pool's
# lock-wait service rate, so the zero path never exceeded the business budget
# (measured: 2 rejected of 28, fraction 0.93). At 3 qps the collision rate (~0.6/s,
# each collision pinning a worker for the full lock-timeout + retry) exceeds
# the pool's service rate, queued orders blow their deadlines, and the
# unremediated path fails `trade_good_fraction` while the repaired paths
# recover immediately after the oracle terminates the leak backend.
_SMOKE_TRADE_TIERS = TrafficPlan(tiers=(TrafficTier("normal", 0.0, 3.0, 6.0, 10000),))
_SMOKE_DRIVER_CONFIG = DriverConfig(pool_size=3, control_poll_seconds=5.0, seed=20260918)


def _warehouse_ledgers_factory(evidence_root: Path, run_id: str) -> dict[str, TrustedLedger]:
    return {
        service_id: TrustedLedger(
            service_id,
            evidence_ledger_path(evidence_root, run_id, f"ledger-{service_id}"),
        )
        for service_id in SERVICE_IDS
    }


def _warehouse_driver_factory(*, environment, ledgers, spec, run_id, clock, scoring_origin):
    return WarehouseReportingRuntime(
        env=environment,
        clock=clock,
        run_id=run_id,
        ledgers=ledgers,
        input_end_monotonic=scoring_origin + spec.input_stop_seconds,
    )


def _load_driver_runtime_options() -> str:
    """The measured PG runtime options every warehouse run must deploy with."""

    document = yaml.safe_load(_OLAP_DRIVER_YAML.read_text(encoding="utf-8"))
    options = document.get("runtime_options") or {}
    rendered = " ".join(f"-c {name}={value}" for name, value in options.items())
    return rendered


def _htap_driver_factory(provider_factory):
    """Bind one htap instance provider to the adapter's runtime signature.

    ``provider_factory`` receives the run evidence directory (so the instance
    runtime's external JSONL ledgers land beside the other run evidence) and
    the assembled environment (whose ``time_scale`` selects the compressed
    business calendar).
    """

    def factory(*, environment, spec, run_id, clock, persistent_scenario_started, evidence_root):
        ledger_dir = Path(evidence_root) / "persistent-scenario-evidence" / run_id
        provider = provider_factory(ledger_dir, environment)
        runtime = provider.create_runtime(
            environment, spec, run_id, clock,
            persistent_scenario_started=persistent_scenario_started,
        )
        return HtapWorkloadRuntimeAdapter(
            runtime, horizon_seconds=spec.horizon_seconds, input_stop_seconds=spec.input_stop_seconds
        )

    return factory


def _htap_shared_isolation_provider_factory(ledger_dir: Path, environment):
    return HtapSharedIsolationWorkloadProvider(
        calendar=HTAP_PRODUCTION_CALENDAR,
        ledger_dir=ledger_dir,
    )


def _htap_replica_freshness_provider_factory(ledger_dir: Path, environment):
    return HtapReplicaFreshnessWorkloadProvider(
        calendar=FRS_PRODUCTION_CALENDAR.compressed(environment.time_scale),
        ledger_dir=ledger_dir,
    )


def _default_workload_bindings() -> dict[str, InstanceBinding]:
    bindings = {
        "business_priority": InstanceBinding(
            workload_key="business_priority",
            scenario_ids=frozenset({"pg_continuous_ops_business_priority"}),
            capability_registry=BUSINESS_PRIORITY_CAPABILITIES,
            verifiers=OLTP_VERIFIERS,
            driver_factory=_oltp_driver_factory(
                business_priority_config.TRADE_TIERS,
                business_priority_config.DRIVER_CONFIG,
            ),
            transaction_service_id="trade",
            job_service_ids={"orders-history-archive": "archive"},
            job_ids=("orders-history-archive",),
            deliverable_verifiers={"orders-history-archive": "archive_delivery"},
            connection_verifiers=frozenset({"archive_delivery_tradeoff"}),
            role_credentials=_role_passwords(business_priority_config.ROLE_CREDENTIALS),
            evidence_factory=_oltp_evidence_factory,
            terminal_snapshot=_oltp_terminal_snapshot_factory(
                _initial_inventory(business_priority_config.PROMO_INITIAL_QTY)
            ),
        ),
        "online_change": InstanceBinding(
            workload_key="online_change",
            scenario_ids=frozenset({"pg_oltp_online_change"}),
            capability_registry=ONLINE_CHANGE_CAPABILITIES,
            verifiers=OLTP_VERIFIERS,
            driver_factory=_oltp_driver_factory(
                online_change_config.TRADE_TIERS,
                online_change_config.DRIVER_CONFIG,
                new_version_column=online_change_config.NEW_VERSION_COLUMN,
            ),
            transaction_service_id="trade",
            job_service_ids={"backfill_promo_tier": "release"},
            job_ids=("backfill_promo_tier",),
            connection_verifiers=frozenset({"release_index_valid"}),
            deliverable_verifiers={"backfill_promo_tier": "backfill_completeness"},
            role_credentials=_role_passwords(online_change_config.ROLE_CREDENTIALS),
            evidence_factory=_oltp_evidence_factory,
            terminal_snapshot=_oltp_terminal_snapshot_factory(
                _initial_inventory(online_change_config.PROMO_INITIAL_QTY)
            ),
        ),
        "smoke": InstanceBinding(
            workload_key="smoke",
            scenario_ids=frozenset({"pg_continuous_ops_smoke"}),
            capability_registry=SMOKE_CAPABILITIES,
            verifiers=OLTP_VERIFIERS,
            driver_factory=_oltp_driver_factory(_SMOKE_TRADE_TIERS, _SMOKE_DRIVER_CONFIG),
            transaction_service_id="trade",
            evidence_factory=_oltp_evidence_factory,
            terminal_snapshot=_oltp_terminal_snapshot_factory(
                _initial_inventory(business_priority_config.PROMO_INITIAL_QTY)
            ),
        ),
        "tpcds": InstanceBinding(
            workload_key="tpcds",
            scenario_ids=frozenset({"pg_warehouse_batch_reporting"}),
            capability_registry_factory=lambda runtime_provider: WarehouseCapabilityRegistry(runtime_provider),
            capability_ids=WAREHOUSE_CAPABILITY_IDS,
            ledgers_factory=_warehouse_ledgers_factory,
            driver_factory=_warehouse_driver_factory,
            verifiers=WAREHOUSE_VERIFIERS,
            transaction_service_id="wh_report_service",
            style="warehouse",
            postgres_runtime_options=_load_driver_runtime_options(),
            verifier_ledgers={
                "wh_report_result_truth": "wh_report_service",
                "wh_fact_table_batch_invariant": None,
                "wh_backup_readable": "wh_backup_service",
                "wh_staging_tables_present": None,
                "wh_analytics_continuity": None,
            },
            verifier_pass_fields={"wh_analytics_continuity": "satisfied"},
            deliverable_verifiers={"routine_backup_read": "wh_backup_readable"},
        ),
        "htap_orders": InstanceBinding(
            workload_key="htap_orders",
            scenario_ids=frozenset({"pg_htap_shared_resource_isolation"}),
            capability_registry=HTAP_CAPABILITIES_BY_ID,
            capability_ids=tuple(HTAP_CAPABILITIES_BY_ID),
            verifiers=HTAP_VERIFIERS,
            driver_factory=_htap_driver_factory(_htap_shared_isolation_provider_factory),
            transaction_service_id="htap3_orders",
            style="htap",
        ),
        "frs_orders": InstanceBinding(
            workload_key="frs_orders",
            scenario_ids=frozenset({"pg_htap_replica_freshness"}),
            capability_registry=FRS_CAPABILITIES_BY_ID,
            capability_ids=tuple(FRS_CAPABILITIES_BY_ID),
            verifiers=FRS_VERIFIERS,
            driver_factory=_htap_driver_factory(_htap_replica_freshness_provider_factory),
            transaction_service_id="htap4_orders",
            style="htap",
            # LOGIN role passwords owned by the instance schema's CREATE ROLE
            # statements; role-scoped GUC verification logs in fresh as the role.
            role_credentials={"frs_oltp": "frs_oltp", "frs_report": "frs_report"},
        ),
    }
    return bindings
