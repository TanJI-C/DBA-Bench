"""Final-horizon trusted sampling for the pg5 PostgreSQL assembly.

Executes the instance-registered verifiers plus the framework GUC and
ledger-window checks and returns typed facts; evaluation consumes them from
the run and never runs SQL itself.
"""

from __future__ import annotations

from typing import Mapping

from src.persistent_scenarios.model.enums import RequiredStateKind, SettingEffect, SettingScope
from src.persistent_scenarios.model.spec import GucEffectiveSpec, PersistentScenarioSpec
from src.persistent_scenarios.runtime.ledger import LedgerView
from src.persistent_scenarios.runtime.lifecycle import (
    EvidenceStatus,
    IntegrityFact,
    IntegrityStatus,
    RequiredStateEvidence,
)
from src.persistent_scenarios.runtime.ports import PersistentScenarioEnvironmentInvalidError

from .bindings import InstanceBinding
from .instance_adapter import InstanceWorkloadRuntime


SCORING_START_EPOCH_PARAM = "run_scoring_start_epoch"


def _resolve_verifier_params(params: Mapping[str, object], scoring_start_epoch: float | None) -> Mapping[str, object]:
    """Substitute the symbolic scoring-start epoch with the run's real value.

    Scenario YAMLs may declare ``run_scoring_start_epoch`` as a verifier param;
    it denotes the wall-clock epoch at which the business scoring window
    started. Without a known epoch the symbol passes through and the verifier
    fails loudly on it.
    """
    if scoring_start_epoch is None:
        return params
    resolved = {
        key: (scoring_start_epoch if value == SCORING_START_EPOCH_PARAM else value)
        for key, value in params.items()
    }
    return resolved


class PostgresStateFactProvider:
    """Final-horizon sampling executing the instance-registered verifiers."""

    def __init__(self, bindings: Mapping[str, InstanceBinding]):
        self._bindings = bindings
        self._workload_runtime: InstanceWorkloadRuntime | None = None

    def _binding(self, spec: PersistentScenarioSpec) -> InstanceBinding:
        return self._bindings[spec.environment.workload]

    def _runtime(self) -> InstanceWorkloadRuntime:
        if self._workload_runtime is None:
            raise ValueError(
                "PostgreSQL state-fact sampling requires the workload runtime: "
                "no instance run was assembled in this backend process"
            )
        return self._workload_runtime

    def capture_integrity_facts(
        self,
        environment,
        spec: PersistentScenarioSpec,
        *,
        scoring_start_epoch: float | None = None,
    ) -> tuple[IntegrityFact, ...]:
        binding = self._binding(spec)
        facts: list[IntegrityFact] = []
        for check in spec.integrity_checks:
            verifier = binding.verifiers.get(check.verifier_id)
            params = _resolve_verifier_params(check.params, scoring_start_epoch)
            if verifier is None:
                raise ValueError(
                    "Integrity check references an unregistered verifier: "
                    f"check_id={check.check_id!r}, verifier_id={check.verifier_id!r}, "
                    f"registered={sorted(binding.verifiers)!r}"
                )
            if binding.style == "warehouse":
                result = self._call_warehouse_verifier(
                    binding, environment, verifier=verifier, params=params, verifier_id=check.verifier_id
                )
                status = IntegrityStatus.PASSED if result["passed"] is True else IntegrityStatus.FAILED
            elif binding.style == "htap":
                try:
                    result = verifier(environment.open_workload_connection, params)
                except Exception as exc:
                    raise PersistentScenarioEnvironmentInvalidError(
                        "Integrity verifier sampling failed: "
                        f"check_id={check.check_id!r}, verifier_id={check.verifier_id!r}, error={exc!r}"
                    ) from exc
                status = IntegrityStatus.PASSED if result["passed"] is True else IntegrityStatus.FAILED
            else:
                runtime = self._runtime()
                snapshot = binding.terminal_snapshot(environment)
                evidence_kwargs = {"ops": runtime.driver.ledger.ops(), "snapshot": snapshot}
                if check.verifier_id in binding.connection_verifiers:
                    evidence_kwargs["connection"] = environment.open_workload_connection(
                        "persistent_scenario-integrity-verifier"
                    )
                try:
                    result = verifier(params, **evidence_kwargs)
                except Exception as exc:
                    raise PersistentScenarioEnvironmentInvalidError(
                        "Integrity verifier sampling failed: "
                        f"check_id={check.check_id!r}, verifier_id={check.verifier_id!r}, error={exc!r}"
                    ) from exc
                status = IntegrityStatus.PASSED if result["passed"] is True else IntegrityStatus.FAILED
            facts.append(IntegrityFact(
                check_id=check.check_id,
                kind="result_truth",
                status=status,
                details=dict(result),
            ))
        return tuple(facts)

    def capture_required_state_evidence(
        self,
        environment,
        spec: PersistentScenarioSpec,
        *,
        scoring_start_epoch: float | None = None,
    ) -> tuple[RequiredStateEvidence, ...]:
        binding = self._binding(spec)
        evidence: list[RequiredStateEvidence] = []
        for check in spec.required_state:
            captured_at = self._clock()
            if isinstance(check, GucEffectiveSpec):
                facts: Mapping[str, object] = self._guc_effective_facts(environment, check)
            elif check.kind is RequiredStateKind.CONTINUITY:
                view = self._service_ledger_view(binding, check.service_id)
                # The workload plans business input only up to the input stop, so
                # the observation window anchors there: past it no traffic can
                # exist by design and a scoring_end anchor would make the
                # denominator structurally zero.
                window_end = min(
                    self._workload_runtime.scoring_end_monotonic,
                    self._workload_runtime.input_stop_monotonic,
                )
                window_transactions = [
                    record
                    for record in view.logical_transactions()
                    if record.service_id == check.service_id
                    and record.planned_at_monotonic >= window_end - check.window_seconds
                ]
                facts = {
                    "completed": sum(1 for record in window_transactions if record.good),
                    "denominator": len(window_transactions),
                }
            elif check.kind is RequiredStateKind.DELIVERABLE_PRESENT:
                jobs = [
                    job
                    for ledger_view in self._ledger_views()
                    for job in ledger_view.jobs()
                    if job.job_id == check.deliverable_id
                ]
                delivered = bool(jobs) and jobs[0].terminal.value == "completed"
                verifier_id = binding.deliverable_verifiers[check.deliverable_id]
                try:
                    result = self._call_verifier(
                        binding, environment, verifier_id,
                        _resolve_verifier_params(check.params, scoring_start_epoch),
                        verifier_pass_field="passed",
                    )
                except Exception as exc:
                    evidence.append(RequiredStateEvidence(
                        check_id=check.check_id,
                        status=EvidenceStatus.COLLECTOR_FAILURE,
                        facts={"reason": repr(exc)},
                        captured_at_monotonic=captured_at,
                    ))
                    continue
                facts = {"present": delivered, "correct": result["passed"] is True}
            elif check.kind is RequiredStateKind.VERIFIER:
                try:
                    facts = dict(self._call_verifier(
                        binding, environment, check.verifier_id,
                        _resolve_verifier_params(check.params, scoring_start_epoch),
                        verifier_pass_field=binding.verifier_pass_fields.get(check.verifier_id, "passed"),
                    ))
                except Exception as exc:
                    evidence.append(RequiredStateEvidence(
                        check_id=check.check_id,
                        status=EvidenceStatus.COLLECTOR_FAILURE,
                        facts={"reason": repr(exc)},
                        captured_at_monotonic=captured_at,
                    ))
                    continue
            else:
                raise ValueError(
                    f"Unknown required-state check kind: check_id={check.check_id!r}, kind={check.kind!r}"
                )
            evidence.append(RequiredStateEvidence(
                check_id=check.check_id,
                status=EvidenceStatus.CAPTURED,
                facts=facts,
                captured_at_monotonic=captured_at,
            ))
        return tuple(evidence)

    def _clock(self):
        runtime = self._runtime()
        try:
            return runtime.scoring_end_monotonic
        except (AttributeError, ValueError):
            from src.persistent_scenarios.runtime.clock import RealClock

            return RealClock().monotonic()

    def _ledger_views(self) -> list[LedgerView]:
        runtime = self._runtime()
        if isinstance(runtime, InstanceWorkloadRuntime):
            return [LedgerView(runtime.trusted_ledger)]
        return [LedgerView(ledger) for ledger in runtime.ledgers().values()]

    def _service_ledger_view(self, binding, service_id: str) -> LedgerView:
        runtime = self._runtime()
        if isinstance(runtime, InstanceWorkloadRuntime):
            return LedgerView(runtime.trusted_ledger)
        if binding.style == "htap":
            # One trusted ledger backs every service; continuity windows are
            # filtered by the record's service_id after the view is opened.
            return LedgerView(runtime.ledgers()["trusted"])
        ledgers = runtime.ledgers()
        if service_id not in ledgers:
            raise ValueError(
                f"service ledger not found for continuity sampling: service_id={service_id!r}, "
                f"known={sorted(ledgers)!r}"
            )
        return LedgerView(ledgers[service_id])

    def _call_verifier(self, binding, environment, verifier_id: str, params: Mapping, *, verifier_pass_field: str):
        verifier = binding.verifiers.get(verifier_id)
        if verifier is None:
            raise ValueError(
                "Verifier is not registered for this binding: "
                f"verifier_id={verifier_id!r}, registered={sorted(binding.verifiers)!r}"
            )
        if binding.style == "warehouse":
            result = self._call_warehouse_verifier(
                binding, environment, verifier=verifier, params=params, verifier_id=verifier_id
            )
        elif binding.style == "htap":
            result = verifier(environment.open_workload_connection, params)
        else:
            runtime = self._runtime()
            snapshot = binding.terminal_snapshot(environment)
            evidence_kwargs = {"ops": runtime.driver.ledger.ops(), "snapshot": snapshot}
            if verifier_id in binding.connection_verifiers:
                evidence_kwargs["connection"] = environment.open_workload_connection(
                    "persistent_scenario-state-verifier"
                )
            result = verifier(params, **evidence_kwargs)
        if verifier_pass_field != "passed":
            result = {"passed": result.get(verifier_pass_field), **result}
        return result

    def _call_warehouse_verifier(self, binding, environment, *, verifier, params: Mapping, verifier_id: str):
        runtime = self._runtime()
        ledger_view = None
        service_id = binding.verifier_ledgers.get(verifier_id)
        if service_id is not None:
            ledger_view = LedgerView(runtime.ledgers()[service_id])
        connection = environment.open_workload_connection("persistent_scenario-warehouse-verifier")
        try:
            return verifier(connection, ledger_view, params)
        finally:
            connection.close()

    @staticmethod
    def _guc_effective_facts(environment, check: GucEffectiveSpec) -> dict[str, object]:
        if check.scope is SettingScope.ROLE:
            open_role_connection = getattr(environment, "open_role_connection", None)
            if open_role_connection is not None:
                return PostgresStateFactProvider._role_login_guc_facts(
                    open_role_connection, check
                )
        connection = environment.open_workload_connection("persistent_scenario-guc-effective")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name, setting FROM pg_settings WHERE name = %(name)s;",
                    {"name": check.guc_name},
                )
                row = cursor.fetchone()
                if row is None:
                    raise PersistentScenarioEnvironmentInvalidError(
                        f"Required GUC does not exist: check_id={check.check_id!r}, guc_name={check.guc_name!r}"
                    )
                if check.scope is SettingScope.SERVER:
                    fresh_connection = True
                    scope_name = None
                    # A pending restart only matters when the setting is
                    # declared to take effect after one; the other effect
                    # classes must be live on the sampled connection now.
                    pending_restart = None
                    if check.effective_on is SettingEffect.AFTER_RESTART:
                        cursor.execute(
                            "SELECT COALESCE((SELECT setting FROM pg_settings WHERE name = 'pending_restart'), 'f');"
                        )
                        pending_restart = str(cursor.fetchone()[0]).lower() in {"on", "t", "true"}
                else:
                    # pg_db_role_setting stores role/database-scoped GUCs in the
                    # setconfig array as "name=value" rows; role scope pins
                    # setdatabase=0, database scope pins setrole=0.
                    cursor.execute(
                        "SELECT split_part(config, '=', 2) FROM ("
                        "  SELECT unnest(setconfig) AS config, setrole, setdatabase "
                        "  FROM pg_db_role_setting"
                        ") s "
                        "WHERE split_part(s.config, '=', 1) = %(name)s "
                        "AND ("
                        "  (%(scope)s = 'role' AND s.setdatabase = 0 "
                        "   AND s.setrole = (SELECT oid FROM pg_roles WHERE rolname = %(scope_name)s))"
                        "  OR"
                        "  (%(scope)s = 'database' AND s.setrole = 0 "
                        "   AND s.setdatabase = (SELECT oid FROM pg_database WHERE datname = %(scope_name)s))"
                        ");",
                        {"scope": check.scope.value, "scope_name": check.scope_name, "name": check.guc_name},
                    )
                    scope_row = cursor.fetchone()
                    scope_name = check.scope_name
                    # Role/database-scope verification through a fresh session in
                    # that scope requires the scope's own credentials; until the
                    # deployment supplies them the effective check stays false.
                    fresh_connection = False
                    server_value = str(row[1])
                    connection.rollback()
                    return {
                        "value": scope_row[0] if scope_row is not None else server_value,
                        "fresh_connection": fresh_connection,
                        "scope": check.scope.value,
                        "scope_name": scope_name,
                        "pending_restart": False,
                    }
            connection.rollback()
        finally:
            connection.close()
        facts = {
            "value": str(row[1]),
            "fresh_connection": fresh_connection,
            "scope": check.scope.value,
            "scope_name": scope_name,
        }
        if check.effective_on is SettingEffect.AFTER_RESTART:
            facts["pending_restart"] = pending_restart
        return facts

    @staticmethod
    def _role_login_guc_facts(open_role_connection, check: GucEffectiveSpec) -> dict[str, object]:
        """Effective value sampled through a fresh login as the scoped role.

        Role settings only take effect for sessions started inside the role,
        so the environments that carry role credentials verify through a real
        fresh login instead of the pg_db_role_setting catalog view. Role
        settings never pend a restart.
        """

        connection = open_role_connection(check.scope_name, "persistent_scenario-guc-effective")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_setting(%(name)s);", {"name": check.guc_name})
                row = cursor.fetchone()
            connection.rollback()
        finally:
            connection.close()
        facts = {
            "value": str(row[0]),
            "fresh_connection": True,
            "scope": check.scope.value,
            "scope_name": check.scope_name,
        }
        if check.effective_on is SettingEffect.AFTER_RESTART:
            facts["pending_restart"] = False
        return facts


