"""Pure static PersistentScenario model enums."""

from __future__ import annotations

from enum import Enum


class DatabaseSystem(str, Enum):
    POSTGRESQL = "postgresql"
    TIDB = "tidb"


class CalibrationStatus(str, Enum):
    DEVELOPMENT_PROVISIONAL = "development_provisional"
    VALIDATED = "validated"


class EventTrigger(str, Enum):
    """How an Event becomes visible. ALERT publishes a mailbox work item;
    SILENT arrives engine-side only (agent discovers it through tools)."""

    ALERT = "alert"
    SILENT = "silent"


class LoadClass(str, Enum):
    """Discriminator for service objective shapes."""

    OLTP = "oltp"
    OLAP = "olap"
    HTAP = "htap"


class OlapMode(str, Enum):
    DELIVERABLE_CHECKLIST = "deliverable_checklist"
    TASK_CLASS_BUDGET = "task_class_budget"


class HtapMode(str, Enum):
    SHARED = "shared"
    REPLICA = "replica"


class RequiredStateKind(str, Enum):
    CONTINUITY = "continuity"
    DELIVERABLE_PRESENT = "deliverable_present"
    GUC_EFFECTIVE = "guc_effective"
    VERIFIER = "verifier"


class SettingScope(str, Enum):
    """Where a required setting lives.

    The vocabulary is parameterized by ``spec.system``: postgresql uses the
    GUC contexts ``server|database|role``; tidb uses the system-variable and
    component-configuration scopes ``global|session|instance|component``.
    """

    SERVER = "server"
    DATABASE = "database"
    ROLE = "role"
    GLOBAL = "global"
    SESSION = "session"
    INSTANCE = "instance"
    COMPONENT = "component"


class SettingEffect(str, Enum):
    """Which connections must observe the required value at final sampling.

    ``new_connections``: sessions opened after the change (long-lived
      pre-change sessions are not required to see it) - PG ALTER
      SYSTEM/DATABASE/ROLE defaults, TiDB ``SET GLOBAL``.
    ``all``: every connection at sampling time must see it - TiDB INSTANCE
      scope, or scenarios that require rolling existing sessions.
    ``after_restart``: no connection can show the value until the owning
      component restarts (PG postmaster GUCs observed as ``pending_restart``,
      TiDB component configuration files); final sampling happens after that
      restart. System-specific observation detail belongs to the backend
      sampling side, not to this contract.
    """

    NEW_CONNECTIONS = "new_connections"
    ALL_CONNECTIONS = "all"
    AFTER_RESTART = "after_restart"


SETTING_SCOPES_BY_SYSTEM: dict[DatabaseSystem, frozenset[SettingScope]] = {
    DatabaseSystem.POSTGRESQL: frozenset({SettingScope.SERVER, SettingScope.DATABASE, SettingScope.ROLE}),
    DatabaseSystem.TIDB: frozenset({
        SettingScope.GLOBAL,
        SettingScope.SESSION,
        SettingScope.INSTANCE,
        SettingScope.COMPONENT,
    }),
}

SETTING_SCOPES_WITH_NAME: frozenset[SettingScope] = frozenset({
    SettingScope.DATABASE,
    SettingScope.ROLE,
    SettingScope.COMPONENT,
})
