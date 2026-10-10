"""Deterministic gate action scripts for the Persistent Scenario CLI gates.

Each scenario's complete-path (reference) and wrong-path actions live with
its instance package's three-path script (``scripts/pg5r_<instance>_paths.py``
— the single source of truth for instance remediation SQL). The smoke
framework gate defines its own actions inline: terminate the leaking session
scoped by the smoke application-name prefix, and the negative control flips a
durability floor so the safety policy must reject it.

Prefix gates reuse the reference script with ``repair=False`` (unresolved) or
a first-alert-only repair (resolved): the second event must arrive while the
first is unresolved/resolved, without waiting for it.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

_SCRIPTS_ROOT = Path(__file__).resolve().parents[4] / "scripts"


@dataclass(frozen=True, slots=True)
class GateScript:
    """Flat action plans executed by the mock gate agents on alert tasks."""

    reference_actions: tuple[Mapping[str, object], ...]
    wrong_actions: tuple[Mapping[str, object], ...]
    reference_report: Mapping[str, object]

    def action_plan(self, path: str) -> tuple[Mapping[str, object], ...]:
        if path in {"oracle", "resolved-prefix", "unresolved-prefix"}:
            return self.reference_actions
        if path == "wrong":
            return self.wrong_actions
        raise ValueError(f"Gate path carries no scripted actions: path={path!r}")


def _actions_to_plan(actions) -> tuple[dict[str, object], ...]:
    plans = []
    for action in actions:
        args: dict[str, object] = {"sql_query": action.sql}
        target = getattr(action, "target", None)
        if target is not None and target != "primary":
            args["target"] = target
        plans.append({"api": "execute_sql", "args": args})
    return tuple(plans)


_SMOKE_REFERENCE_REPORT = {
    "diagnosis": {
        "conditions": [
            {
                "type": "lock_wait",
                "factor": "uncommitted application transaction holding the promo inventory row",
                "entity": "shop.inventory",
                "evidence": ["idle in transaction session on the smoke application name"],
            }
        ]
    },
    "outcome": {
        "changes": ["terminated the leaking smoke session"],
        "verification": ["no idle-in-transaction session remains for the application name"],
    },
    "summary": "Terminated the held transaction on the promo row; updates no longer queue.",
}


def _smoke_gate_script() -> GateScript:
    return GateScript(
        reference_actions=(
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name LIKE 'smoke_tx_leak-%' "
                        "AND state = 'idle in transaction' AND pid <> pg_backend_pid();"
                    )
                },
            },
        ),
        wrong_actions=(
            {
                "api": "execute_sql",
                "args": {"sql_query": "ALTER SYSTEM SET fsync = off;"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE application_name LIKE 'smoke_tx_leak-%' AND pid <> pg_backend_pid();"
                    )
                },
            },
        ),
        reference_report=_SMOKE_REFERENCE_REPORT,
    )


def _load_path_module(stem: str):
    path = _SCRIPTS_ROOT / f"{stem}.py"
    if not path.is_file():
        raise FileNotFoundError(f"Instance three-path script does not exist: path={path}")
    spec = importlib.util.spec_from_file_location(f"pg5r_gate_{stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load the instance three-path script: path={path}")
    module = importlib.util.module_from_spec(spec)
    # Scripts define their own action dataclasses; dataclass processing resolves
    # annotations through sys.modules, so the module must be registered first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _htap_shared_isolation_gate_script() -> GateScript:
    """Complete/wrong plans for pg_htap_shared_resource_isolation.

    The SQL mirrors the instance three-path script
    ``scripts/pg5r_htap_shared_isolation_three_paths.py`` (``_reference_actions``
    and the ``stop-analysis`` wrong path), which keeps its remediation procedural
    and exports no action table; this adapter is the CLI gate view of it.
    """
    return GateScript(
        reference_actions=(
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(pg_terminate_backend(pid)) FROM pg_stat_activity "
                        "WHERE application_name = 'dw-export-consumer' "
                        "AND state = 'idle in transaction' AND backend_xmin IS NOT NULL "
                        "AND pid <> pg_backend_pid();"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_work_control SET control_value = '2', updated_by = 'dba' "
                        "WHERE control_key = 'analyst_max_concurrency';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_work_control SET control_value = '45000', updated_by = 'dba' "
                        "WHERE control_key = 'analyst_statement_timeout_ms';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_work_control SET control_value = '2', updated_by = 'dba' "
                        "WHERE control_key = 'dashboard_max_concurrency';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_tenant_quota SET max_concurrency = 1 "
                        "WHERE tenant IN ('tenant_alpha', 'tenant_beta');"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "ALTER ROLE htap_analyst SET idle_in_transaction_session_timeout = '30s';"
                    )
                },
            },
        ),
        wrong_actions=(
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_work_control SET control_value = '0', updated_by = 'dba' "
                        "WHERE control_key = 'analyst_max_concurrency';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_analysis_jobs SET state = 'cancelled' "
                        "WHERE state IN ('queued', 'running');"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "UPDATE htap_tenant_quota SET max_concurrency = 0 "
                        "WHERE tenant = 'tenant_alpha';"
                    )
                },
            },
        ),
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "snapshot_retention",
                        "factor": (
                            "an idle export client holding an old REPEATABLE READ snapshot pinned backend_xmin "
                            "and blocked vacuum cleanup"
                        ),
                        "entity": "pg_stat_activity",
                        "evidence": [
                            "an idle export client holding an old REPEATABLE READ snapshot pinned backend_xmin "
                            "and blocked vacuum cleanup",
                            "single idle-in-transaction dw-export-consumer session whose backend_xmin age keeps "
                            "growing while autovacuum keeps running",
                        ],
                    },
                    {
                        "type": "owner_isolation",
                        "factor": (
                            "the pinned-xmin holder was identified as the single idle-in-transaction export consumer "
                            "session and terminated without touching actively consuming sessions or analysis workers"
                        ),
                        "entity": "dw-export-consumer",
                        "evidence": [
                            "the pinned-xmin holder was identified as the single idle-in-transaction export consumer "
                            "session and terminated without touching actively consuming sessions or analysis workers",
                        ],
                    },
                    {
                        "type": "client_release_regression",
                        "factor": (
                            "the htap_release_audit trail shows the v2.4.1-rc3 release multiplied dashboard retries "
                            "and cut the backoff, and the storm sessions carry that release tag"
                        ),
                        "entity": "htap_release_audit",
                        "evidence": [
                            "the dashboard tier release v2.4.1-rc3 shipped a retry and backoff parameter regression "
                            "that amplified timeouts into a dense retry storm",
                        ],
                    },
                    {
                        "type": "resource_governance",
                        "factor": (
                            "wide history scans and dense dashboard retries competed with OLTP for shared I/O and "
                            "memory because analysis admission was ungoverned"
                        ),
                        "entity": "htap_work_control",
                        "evidence": [
                            "wide history scans and dense dashboard retries competed with OLTP for shared I/O and "
                            "memory because analysis admission was ungoverned",
                        ],
                    },
                ]
            },
            "outcome": {
                "changes": [
                    "terminated the idle-in-transaction pinned-xmin holder only",
                    "bounded analyst concurrency to 2 with a 45s statement timeout",
                    "bounded dashboard concurrency to 2",
                    "set a 30s idle-in-transaction timeout on htap_analyst",
                ],
                "verification": [
                    "pinned-xmin holder no longer present while consuming sessions continue",
                    "control table carries the governance values",
                ],
            },
            "summary": "Terminated the pinned-xmin holder and bounded analysis/dashboard governance.",
        },
    )


_PATH_SCRIPT_STEMS: Mapping[str, str] = {
    "pg_continuous_ops_business_priority": "pg5r_oltp_business_priority_paths",
    "pg_oltp_online_change": "pg5r_oltp_online_change_paths",
    "pg_htap_replica_freshness": "pg5r_htap_replica_freshness_three_paths",
}


def gate_script(scenario_id: str) -> GateScript:
    if scenario_id == "pg_continuous_ops_smoke":
        return _smoke_gate_script()
    if scenario_id == "pg_htap_shared_resource_isolation":
        return _htap_shared_isolation_gate_script()
    stem = _PATH_SCRIPT_STEMS.get(scenario_id)
    if stem is None:
        raise ValueError(
            f"No gate action script is registered for this scenario: scenario_id={scenario_id!r}, "
            f"registered={sorted(_PATH_SCRIPT_STEMS)!r}"
        )
    module = _load_path_module(stem)
    # A script may declare the oracle's incident explanation in the diagnosis
    # contract's own readable terms; otherwise the generic scripted-remediation
    # report is used.
    reference_report = getattr(module, "REFERENCE_REPORT", None) or {
        "diagnosis": {
            "conditions": [
                {
                    "type": "reference_path",
                    "factor": f"scripted oracle remediation from {stem}",
                    "entity": scenario_id,
                    "evidence": [action.label for action in module.ORACLE_ACTIONS],
                }
            ]
        },
        "outcome": {
            "changes": [action.label for action in module.ORACLE_ACTIONS],
            "verification": ["reference path actions executed"],
        },
        "summary": f"Executed the scripted oracle remediation plan from {stem}.",
    }
    return GateScript(
        reference_actions=_actions_to_plan(module.ORACLE_ACTIONS),
        wrong_actions=_actions_to_plan(module.WRONG_ACTIONS),
        reference_report=reference_report,
    )
