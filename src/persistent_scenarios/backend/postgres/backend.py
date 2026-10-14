"""PostgreSQL Persistent Scenario backend composition root.

The backend owns the per-workload assembly of the pg5 instances: each
``InstanceBinding`` maps an ``environment.workload`` routing key to the
instance package's capability registry, verifier registry, driver parameters
and scenario identities. Registry construction is an explicit import map —
no automatic discovery. Workloads whose instance packages have not landed
fail assembly with an explicit error; there is no fallback.

One backend process serves one run: the workload provider registers the run's
instance resources (connection sources, evidence ledger, driver) with the
backend, which the capability adapters and the final state-fact sampling
consume.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping

from src.persistent_scenarios.backend.postgres.action_classifier import PostgresActionClassifier
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import TcpConnectionSource
from src.persistent_scenarios.backend.postgres.bindings import (
    InstanceBinding,
    _default_workload_bindings,
)
from src.persistent_scenarios.backend.postgres.environment import PostgresEnvironmentProvider
from src.persistent_scenarios.backend.postgres.event_provider import PostgresEventProvider
from src.persistent_scenarios.backend.postgres.instance_adapter import (
    InstanceCapabilityAdapter,
    InstanceRunResources,
    InstanceWorkloadRuntime,
    adapt_capability_registry,
    evidence_ledger_path,
)
from src.persistent_scenarios.backend.postgres.registry import PostgresEventCapabilityRegistry
from src.persistent_scenarios.backend.postgres.safety import PostgresSafetyProvider
from src.persistent_scenarios.backend.postgres.state_facts import PostgresStateFactProvider
from src.persistent_scenarios.backend.postgres.telemetry import PostgresTelemetryProvider
from src.database.system import DatabaseSystem
from src.persistent_scenarios.runtime.ledger import TrustedLedger
from src.persistent_scenarios.model.spec import PersistentScenarioSpec



def _deliverable_deadlines(spec: PersistentScenarioSpec | None) -> dict[str, float]:
    if spec is None:
        return {}
    return {
        deliverable.deliverable_id: deliverable.deadline_seconds
        for service in spec.services
        for deliverable in getattr(service, "deliverables", ())
    }


def _job_control_tables(spec: PersistentScenarioSpec | None) -> tuple[str, ...]:
    if spec is None:
        return ()
    tables: list[str] = []
    for event in spec.events:
        table = event.payload.get("control_table")
        if isinstance(table, str) and table.strip() and table not in tables:
            tables.append(table)
    return tuple(tables)


class PostgresWorkloadProvider:
    def __init__(
        self,
        bindings: Mapping[str, InstanceBinding],
        register_run_resources: Callable[[str, InstanceRunResources], None],
        register_workload_runtime: Callable[[object], None],
        evidence_root: Path,
    ):
        self._bindings = bindings
        self._register_run_resources = register_run_resources
        self._register_workload_runtime = register_workload_runtime
        self._evidence_root = Path(evidence_root)

    def create_runtime(self, environment, spec: PersistentScenarioSpec, run_id: str, clock, *, persistent_scenario_started: float):
        binding = self._bindings[spec.environment.workload]
        if binding.style == "warehouse":
            runtime = self._create_warehouse_runtime(environment, spec, run_id, clock, persistent_scenario_started)
            self._register_workload_runtime(runtime)
            return runtime
        if binding.style == "htap":
            runtime = self._create_htap_runtime(binding, environment, spec, run_id, clock, persistent_scenario_started)
            self._register_workload_runtime(runtime)
            return runtime
        runtime = self._create_oltp_runtime(binding, environment, spec, run_id, clock, persistent_scenario_started)
        self._register_workload_runtime(runtime)
        return runtime

    def _create_htap_runtime(self, binding, environment, spec, run_id, clock, persistent_scenario_started):
        return binding.driver_factory(
            environment=environment,
            spec=spec,
            run_id=run_id,
            clock=clock,
            persistent_scenario_started=persistent_scenario_started,
            evidence_root=self._evidence_root,
        )

    def _create_warehouse_runtime(self, environment, spec, run_id, clock, scoring_origin):
        binding = self._bindings[spec.environment.workload]
        ledgers = binding.ledgers_factory(self._evidence_root, run_id)
        driver = binding.driver_factory(
            environment=environment,
            ledgers=ledgers,
            spec=spec,
            run_id=run_id,
            clock=clock,
            scoring_origin=scoring_origin,
        )
        return driver

    def _create_oltp_runtime(self, binding, environment, spec, run_id, clock, persistent_scenario_started):
        source = TcpConnectionSource(
            host=environment.host,
            port=environment.port,
            user=environment.user,
            password=environment.password,
            dbname=environment.dbname,
        )
        admin_source = TcpConnectionSource(
            host=environment.host,
            port=environment.port,
            user=environment.user,
            password=environment.password,
            dbname=environment.dbname,
        )
        evidence = binding.evidence_factory(self._evidence_root, run_id)
        driver = binding.driver_factory(
            source=source,
            clock=clock,
            evidence=evidence,
            spec=spec,
            run_id=run_id,
            scoring_origin=persistent_scenario_started,
        )
        trusted_ledger = TrustedLedger(
            "commerce",
            evidence_ledger_path(self._evidence_root, run_id, "ledger-commerce"),
        )
        runtime = InstanceWorkloadRuntime(
            driver,
            trusted_ledger,
            evidence,
            transaction_service_id=binding.transaction_service_id,
            horizon_seconds=spec.horizon_seconds,
            input_stop_seconds=spec.input_stop_seconds,
            job_service_ids=binding.job_service_ids,
            job_ids=binding.job_ids,
            job_deadline_seconds=_deliverable_deadlines(spec),
        )
        self._register_run_resources(
            run_id,
            InstanceRunResources(source=source, admin_source=admin_source, evidence=evidence, driver=driver),
        )
        return runtime


class PostgresPersistentScenarioBackend:
    system = DatabaseSystem.POSTGRESQL

    def __init__(
        self,
        spec: PersistentScenarioSpec | None = None,
        *,
        evidence_root: Path | None = None,
        workload_bindings: Mapping[str, InstanceBinding] | None = None,
    ):
        bindings = dict(_default_workload_bindings() if workload_bindings is None else workload_bindings)
        self._spec = spec
        self._bindings = bindings
        self._evidence_root = Path(evidence_root) if evidence_root is not None else Path("logs")
        resolved = None
        if spec is not None:
            self._validate_spec_shape(spec)
            resolved = bindings[spec.environment.workload]
        resources_by_run_id: dict[str, InstanceRunResources] = {}

        def register_run_resources(run_id: str, resources: InstanceRunResources) -> None:
            resources_by_run_id[run_id] = resources

        # The warehouse capability set resolves the run driver lazily: the
        # runtime only exists after the workload provider assembles it.
        driver_slot: dict[str, object] = {}

        def warehouse_runtime_provider():
            runtime = driver_slot.get("runtime")
            if runtime is None:
                raise ValueError(
                    "Warehouse reporting capability activation requires the workload runtime: "
                    "no runtime was assembled in this backend process"
                )
            return runtime

        def register_workload_runtime(runtime) -> None:
            driver_slot["runtime"] = runtime
            self.state_facts._workload_runtime = runtime

        # Instance packages may reuse capability IDs (both OLTP instances ship
        # `promo_tier`), so only the resolved binding contributes capabilities.
        if resolved is None:
            raise ValueError(
                "PostgreSQL Persistent Scenario backend assembly requires a spec: "
                "the capability registry is built from the resolved instance binding"
            )
        if resolved.style == "warehouse":
            warehouse_registry = resolved.capability_registry_factory(warehouse_runtime_provider)
            capabilities = [
                warehouse_registry.capability(capability_id)
                for capability_id in resolved.capability_ids
            ]
        elif resolved.style == "htap":
            capabilities = [
                resolved.capability_registry[capability_id]
                for capability_id in resolved.capability_ids
            ]
        else:
            capabilities = [
                InstanceCapabilityAdapter(capability, resources_by_run_id)
                for capability in adapt_capability_registry(resolved.capability_registry)
            ]
        self.capabilities = PostgresEventCapabilityRegistry(capabilities)
        self.events = PostgresEventProvider(self.capabilities)
        self.environment = PostgresEnvironmentProvider(
            runtime_options=resolved.postgres_runtime_options if resolved is not None else "",
            binding=resolved,
        )
        self.state_facts = PostgresStateFactProvider({resolved.workload_key: resolved} if resolved is not None else {})
        self.workload = PostgresWorkloadProvider(
            bindings,
            register_run_resources,
            register_workload_runtime,
            self._evidence_root,
        )
        self.telemetry = PostgresTelemetryProvider()
        self.safety = PostgresSafetyProvider()
        self.action_classifier = PostgresActionClassifier(job_control_tables=_job_control_tables(spec))

    def _validate_spec_shape(self, spec: PersistentScenarioSpec) -> None:
        if spec.system.value != self.system.value:
            raise ValueError(
                "PostgreSQL Persistent Scenario backend received an incompatible system: "
                f"scenario_id={spec.scenario_id!r}, system={spec.system.value!r}"
            )
        workload = spec.environment.workload
        binding = self._bindings.get(workload)
        if binding is None:
            raise ValueError(
                "No PostgreSQL instance binding is registered for this workload key: "
                f"workload={workload!r}, scenario_id={spec.scenario_id!r}, "
                f"registered={sorted(self._bindings)!r}"
            )
        if spec.scenario_id not in binding.scenario_ids:
            raise ValueError(
                "Scenario identity is not owned by the resolved instance binding: "
                f"scenario_id={spec.scenario_id!r}, workload={workload!r}, "
                f"owned={sorted(binding.scenario_ids)!r}"
            )
        if binding.style != "htap" and len(spec.environment.nodes) > 1:
            raise ValueError(
                "Multi-node PostgreSQL topology assembly is htap-only: "
                f"scenario_id={spec.scenario_id!r}, node_ids={[node.node_id for node in spec.environment.nodes]!r}"
            )

    def validate_spec(self, spec: PersistentScenarioSpec) -> None:
        self._validate_spec_shape(spec)
        for event in spec.events:
            self.events.capability(event.capability_id).declaration(event)

    def provider_bundle(self):
        from src.persistent_scenarios.backend.provider_bundle import PersistentScenarioProviderBundle

        return PersistentScenarioProviderBundle(
            system=self.system,
            environment=self.environment,
            events=self.capabilities,
            workload=self.workload,
            telemetry=self.telemetry,
            safety=self.safety,
        )
