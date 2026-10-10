from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


WORKLOAD_STATEMENT_TIMEOUT = "30s"
WORKLOAD_LOCK_TIMEOUT = "1s"


@dataclass(frozen=True, slots=True)
class SessionSetupBehavior:
    """Derive client-side session setup traffic from connection-cached configuration."""

    config_query: str
    statement: str
    statement_count: Callable[[tuple[object, ...], int], int]

    def __post_init__(self):
        if not self.config_query.strip() or not self.statement.strip():
            raise ValueError(
                "Session setup behavior requires a config query and statement: "
                f"config_query={self.config_query!r}, statement={self.statement!r}"
            )


@dataclass(frozen=True, slots=True)
class WorkloadProfile:
    """A single SQL fingerprint continuously executed by the runner."""

    name: str
    sql: str
    qps: float = 0.5
    tier: str = "LIGHT"
    commit: bool = False
    application_name: Optional[str] = None
    connection_pool: Optional[str] = None
    target: Optional[str] = None
    connection_setup_statements: tuple[str, ...] = ()
    connection_refresh_seconds: Optional[float] = None
    session_setup: Optional[SessionSetupBehavior] = None
    transactional: bool = True
    activity_period_seconds: Optional[float] = None
    activity_active_seconds: Optional[float] = None

    def __post_init__(self):
        if self.connection_pool is not None and self.target is not None:
            raise ValueError(
                "WorkloadProfile route must use either connection_pool or target: "
                f"profile={self.name!r}, connection_pool={self.connection_pool!r}, target={self.target!r}"
            )
        if any(not statement.strip() for statement in self.connection_setup_statements):
            raise ValueError(
                "WorkloadProfile connection setup statements must be non-empty: "
                f"profile={self.name!r}, statements={self.connection_setup_statements!r}"
            )
        if self.connection_refresh_seconds is not None and self.connection_refresh_seconds <= 0:
            raise ValueError(
                "WorkloadProfile connection refresh interval must be positive: "
                f"profile={self.name!r}, seconds={self.connection_refresh_seconds!r}"
            )
        if (self.activity_period_seconds is None) != (self.activity_active_seconds is None):
            raise ValueError(
                "WorkloadProfile activity period requires both period and active seconds: "
                f"profile={self.name!r}, period={self.activity_period_seconds!r}, "
                f"active={self.activity_active_seconds!r}"
            )
        if self.activity_period_seconds is not None:
            if self.activity_period_seconds <= 0 or self.activity_active_seconds <= 0:
                raise ValueError(
                    "WorkloadProfile activity period and active seconds must be positive: "
                    f"profile={self.name!r}, period={self.activity_period_seconds!r}, "
                    f"active={self.activity_active_seconds!r}"
                )
            if self.activity_active_seconds > self.activity_period_seconds:
                raise ValueError(
                    "WorkloadProfile active seconds cannot exceed its period: "
                    f"profile={self.name!r}, period={self.activity_period_seconds!r}, "
                    f"active={self.activity_active_seconds!r}"
                )


class BackgroundWorkloadStartPhase(Enum):
    BEFORE_FAULTS = "before_faults"
    AFTER_FAULTS = "after_faults"
    AFTER_OBSERVABILITY = "after_observability"


@dataclass(frozen=True, slots=True, kw_only=True)
class BackgroundWorkloadSpec:
    profiles: tuple[WorkloadProfile, ...]
    worker_count: int
    seed: int
    start_phase: BackgroundWorkloadStartPhase = BackgroundWorkloadStartPhase.AFTER_FAULTS
    warmup_seconds: float = 0


EMPTY_BACKGROUND_WORKLOAD = BackgroundWorkloadSpec(
    profiles=(),
    worker_count=0,
    seed=0,
)
