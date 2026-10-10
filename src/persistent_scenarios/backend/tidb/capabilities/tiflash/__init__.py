"""Instance-native Event capabilities for tidb_htap_tiflash_isolation.

Each capability expresses external intent as real effects on the public control plane
or the node topology, and returns structured arrival facts. Prevention is never
synthesized: a capability that cannot complete its effect raises, and only a genuinely
blocked attempt returns prevented evidence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.persistent_scenarios.backend.contracts import (
    CapabilityDeclaration,
    EventActivationContext,
    EventActivationResult,
    EventAlertPayload,
    OwnershipMode,
    ResourceOwnership,
)
from src.persistent_scenarios.runtime.lifecycle import (
    AppliedEvidence,
    EventAttemptEvidence,
)

from .runtime import HtapIsolationRuntime
from .schema import ENGINE_PREFERENCES

CAPABILITY_BASELINE_ANALYSIS = "tidb5_htap_baseline_analysis"
CAPABILITY_ENGINE_ROUTE_RELEASE = "tidb5_htap_engine_route_release"
CAPABILITY_PEAK_AND_ANALYSIS = "tidb5_htap_peak_and_analysis"
CAPABILITY_TIFLASH_DEGRADATION = "tidb5_htap_tiflash_degradation"
CAPABILITY_TIFLASH_RECOVERY = "tidb5_htap_tiflash_recovery"
CAPABILITY_TENANT_ONBOARDING = "tidb5_htap_tenant_onboarding"

CAPABILITIES = (
    CAPABILITY_BASELINE_ANALYSIS,
    CAPABILITY_ENGINE_ROUTE_RELEASE,
    CAPABILITY_PEAK_AND_ANALYSIS,
    CAPABILITY_TIFLASH_DEGRADATION,
    CAPABILITY_TIFLASH_RECOVERY,
    CAPABILITY_TENANT_ONBOARDING,
)

ANALYSIS_DEADLINE_OFFSET = 900
PEAK_ANALYSIS_DEADLINE_OFFSET = 900
DEFAULT_PEAK_CPU_LIMIT = 0.5
MAX_ACTIVATION_SECONDS = 120


def _preference_from_payload(payload) -> str:
    preference = str(payload.get("engine_preference", ""))
    if preference not in ENGINE_PREFERENCES:
        raise ValueError(
            f"engine preference payload must be one of {ENGINE_PREFERENCES!r}: payload={dict(payload)!r}"
        )
    return preference


@dataclass(frozen=True, slots=True)
class _BaselineHandle:
    event_id: str
    analysis_job_id: str


class BaselineAnalysisCapability:
    """Baseline: the first required region analysis is committed by the
    capability timeline itself at scoring start (t=0), while the shared dataset is
    still the provisioned baseline (history rows loaded, no sabotage published yet).

    The commit point owns `region_analysis_early` end to end: the job identity is the
    deliverable identity and the deadline is the calibrated analysis
    deadline offset from submission, so the delivery window ends at t=900 - exactly
    when the wrong route release lands. There is no submission path outside this
    capability: the real-model run exercises the engine timeline only.
    """

    capability_id = CAPABILITY_BASELINE_ANALYSIS

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("queue:analysis:baseline", "queue_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        job_id = runtime.submit_required_analysis("region_analysis_early", at + ANALYSIS_DEADLINE_OFFSET)
        handle = _BaselineHandle(event_id=context.event.event_id, analysis_job_id=job_id)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={"analysis_job_id": job_id}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"analysis_job_submitted": True}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _BaselineHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="A required region analysis delivery entered the queue at baseline",
            symptoms=(
                "the baseline analysis snapshot was declared while the dataset was still at its provisioned state",
                "the delivery carries a business deadline independent of the trading side",
            ),
            severity="notice",
            category="htap_analysis",
        )

    def cleanup(self, handle: _BaselineHandle) -> None:
        return None

    def assert_clean(self, handle: _BaselineHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _ReleaseHandle:
    event_id: str
    release: dict


class EngineRouteReleaseCapability:
    """t=15: a scheduler release publishes a wrong engine preference.

    The preference lands in the audited `htap.analytics_config`; every new claim
    connection applies it as a SESSION setting. On v8.1.0 `tidb_isolation_read_engines`
    is SESSION-only (SET GLOBAL raises 1228), so a config-table release is the real
    publication surface - and a fix that only touches existing sessions cannot cover
    the tenants that onboard later.
    """

    capability_id = CAPABILITY_ENGINE_ROUTE_RELEASE

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("config:analytics_config", "control_table_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        preference = _preference_from_payload(context.event.payload)
        release = runtime.release_engine_preference(at, preference)
        handle = _ReleaseHandle(event_id=context.event.event_id, release=release)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail=release),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts={"release": release}
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _ReleaseHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="The analytics connection template was re-published by the scheduler",
            symptoms=(
                "analytics jobs are running their large scans away from the column-store replica",
                "trading latency grows while heavy analytics occupy the row-store engines",
            ),
            severity="warning",
            category="htap_routing",
        )

    def cleanup(self, handle: _ReleaseHandle) -> None:
        return None

    def assert_clean(self, handle: _ReleaseHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _PeakHandle:
    event_id: str
    multiplier: int
    analysis_job_id: str | None
    tenant_analysis_job_id: str | None


class PeakAndAnalysisCapability:
    """t=28: a trading peak overlaps a large-range analysis delivery.

    Occurrence 2 (the recovery-overlap window) re-arms the trading peak without
    submitting another pool analysis, and instead commits the new tenant's heavy
    analysis - the deliverable whose routing errors recur while the tenant placement
    attachment is missing.
    """

    capability_id = CAPABILITY_PEAK_AND_ANALYSIS

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership("rhythm:trade_rate", "workload_rhythm", OwnershipMode.EXCLUSIVE),
                ResourceOwnership("queue:analysis:peak", "queue_row", OwnershipMode.EXCLUSIVE),
                ResourceOwnership("queue:tenant_analysis:peak", "queue_row", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        multiplier = int(context.event.payload.get("trade_multiplier", 2))
        if multiplier < 1:
            raise ValueError(f"trade multiplier must be positive: multiplier={multiplier}")
        runtime.set_trade_multiplier(multiplier)
        submit_analysis = bool(context.event.payload.get("submit_analysis", True))
        tenant_analysis = bool(context.event.payload.get("tenant_analysis", False))
        analysis_job_id = (
            runtime.submit_required_analysis("region_analysis_peak", at + PEAK_ANALYSIS_DEADLINE_OFFSET)
            if submit_analysis
            else None
        )
        tenant_analysis_job_id = (
            runtime.submit_tenant_analysis("tenant_region_heavy_analysis", at + PEAK_ANALYSIS_DEADLINE_OFFSET)
            if tenant_analysis
            else None
        )
        handle = _PeakHandle(
            event_id=context.event.event_id,
            multiplier=multiplier,
            analysis_job_id=analysis_job_id,
            tenant_analysis_job_id=tenant_analysis_job_id,
        )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at,
                detail={
                    "multiplier": multiplier,
                    "analysis_job_id": analysis_job_id,
                    "tenant_analysis_job_id": tenant_analysis_job_id,
                },
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={
                    "trade_multiplier": multiplier,
                    "analysis_job_submitted": analysis_job_id is not None,
                    "tenant_analysis_job_submitted": tenant_analysis_job_id is not None,
                },
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _PeakHandle) -> EventAlertPayload:
        symptoms = ["order volume doubled for the peak window"]
        if handle.analysis_job_id is not None:
            symptoms.append("a required large-range analysis is queued with a business deadline")
        if handle.tenant_analysis_job_id is not None:
            symptoms.append("the new tenant's first heavy analysis entered its own delivery queue")
        return EventAlertPayload(
            title="Trading peak and a large analysis delivery are running together",
            symptoms=tuple(symptoms),
            severity="warning",
            category="htap_peak",
        )

    def cleanup(self, handle: _PeakHandle) -> None:
        return None

    def assert_clean(self, handle: _PeakHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _DegradeHandle:
    event_id: str
    throttle: dict


class TiflashDegradationCapability:
    """t=40: one TiFlash node is throttled reversibly.

    The throttle opens the node's maintenance window. The tenant onboarding
    pipeline defers replica attachments for tables created inside this window and
    does not flush them when the window closes - that residue is the repair surface.
    The throttle itself is a node-level CPU limit, not an engine shutdown: analysis
    must slow down and survive, and permanently disabling analysis cannot pass.
    """

    capability_id = CAPABILITY_TIFLASH_DEGRADATION

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    resource_key=f"node:tiflash:{event.entity}", resource_kind="container_cpu", mode=OwnershipMode.EXCLUSIVE
                ),
            ),
            max_activation_seconds=MAX_ACTIVATION_SECONDS,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        cpus = float(context.event.payload.get("cpu_limit", DEFAULT_PEAK_CPU_LIMIT))
        if cpus <= 0:
            raise ValueError(f"throttled cpu limit must be positive: cpus={cpus}")
        throttle = runtime.apply_tiflash_cpu_limit(cpus)
        maintenance = runtime.set_node_maintenance(True)
        handle = _DegradeHandle(event_id=context.event.event_id, throttle=throttle)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail={**throttle, **maintenance}),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"throttle": throttle, "node_maintenance": maintenance},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _DegradeHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="The column-store node has slowed down",
            symptoms=(
                "analysis queries on the column-store replica take visibly longer",
                "the node is still serving: analysis must continue, not be switched off",
            ),
            severity="warning",
            category="htap_node_health",
        )

    def cleanup(self, handle: _DegradeHandle) -> None:
        return None

    def assert_clean(self, handle: _DegradeHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _RecoveryHandle:
    event_id: str
    throttle: dict
    restart: dict


class TiflashRecoveryCapability:
    """t=70: the throttled TiFlash node is restored.

    The recovery is a node rejoin - the CPU limit is restored AND the container
    restarts, so its replicas rebuild with a real catch-up lag (observable through
    information_schema.tiflash_replica). The node maintenance window closes here, but
    placement attachments deferred during it are NOT flushed: tables onboarded inside
    the window keep their missing replica until the operator re-attaches it.
    """

    capability_id = CAPABILITY_TIFLASH_RECOVERY

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(
                    resource_key=f"node:tiflash:{event.entity}", resource_kind="container_cpu", mode=OwnershipMode.EXCLUSIVE
                ),
            ),
            max_activation_seconds=MAX_ACTIVATION_SECONDS,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        throttle = runtime.apply_tiflash_cpu_limit(None)
        restart = runtime.restart_tiflash_node()
        maintenance = runtime.set_node_maintenance(False)
        handle = _RecoveryHandle(event_id=context.event.event_id, throttle=throttle, restart=restart)
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(
                attempted_at_monotonic=at, detail={**throttle, **restart, **maintenance}
            ),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(),
                facts={"throttle": throttle, "node_restarted": restart, "node_maintenance": maintenance},
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _RecoveryHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="The column-store node is back to its normal speed",
            symptoms=(
                "the column-store node latency profile recovered",
                "queued analysis work still needs to drain",
            ),
            severity="notice",
            category="htap_node_health",
        )

    def cleanup(self, handle: _RecoveryHandle) -> None:
        return None

    def assert_clean(self, handle: _RecoveryHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


@dataclass(frozen=True, slots=True)
class _TenantHandle:
    event_id: str
    started: dict


class TenantOnboardingCapability:
    """t=58: a new tenant onboards and repeats the same class of analysis.

    The tenant's table is created (CREATE TABLE LIKE - no inherited TiFlash
    replica) and loaded with a real slice of the shared orders, the tenant's
    column-store template is published, and the tenant service starts. Tables created
    inside the node's maintenance window have their replica attachment deferred by the
    onboarding pipeline - the deferral is audited and is not flushed by the later
    recovery event, so only an explicit placement re-attach repairs it.
    """

    capability_id = CAPABILITY_TENANT_ONBOARDING

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._runtime_provider = runtime_provider

    def declaration(self, event) -> CapabilityDeclaration:
        return CapabilityDeclaration(
            capability_id=self.capability_id,
            resources=(
                ResourceOwnership(f"queue:analysis:{event.entity}", "queue_row", OwnershipMode.EXCLUSIVE),
                ResourceOwnership("table:tenant_orders", "table", OwnershipMode.EXCLUSIVE),
            ),
            max_activation_seconds=60,
        )

    def activate(self, context: EventActivationContext) -> EventActivationResult:
        runtime = self._runtime_provider()
        at = context.clock.monotonic()
        template = runtime.release_tenant_template(at)
        tables = runtime.create_tenant_tables(at)
        started = runtime.start_tenant_workers()
        job_id = runtime.submit_required_analysis("region_analysis_final", at + ANALYSIS_DEADLINE_OFFSET)
        handle = _TenantHandle(
            event_id=context.event.event_id,
            started={**template, **tables, **started, "analysis_job_id": job_id},
        )
        return EventActivationResult(
            handle=handle,
            attempt=EventAttemptEvidence(attempted_at_monotonic=at, detail=started),
            applied=AppliedEvidence(
                observed_at_monotonic=context.clock.monotonic(), facts=handle.started
            ),
            prevented=None,
        )

    def alert(self, context: EventActivationContext, handle: _TenantHandle) -> EventAlertPayload:
        return EventAlertPayload(
            title="A new analytics tenant is live and running its first reports",
            symptoms=(
                "new analytics connections joined the pool with the current template",
                "their large scans behave like the previously noisy workload",
            ),
            severity="notice",
            category="htap_tenant",
        )

    def cleanup(self, handle: _TenantHandle) -> None:
        return None

    def assert_clean(self, handle: _TenantHandle) -> dict[str, object]:
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}


class HtapCapabilityRegistry:
    """Registration entry wired by integration; the driver supplies the runtime."""

    def __init__(self, runtime_provider: Callable[[], HtapIsolationRuntime]) -> None:
        self._capabilities = {
            CAPABILITY_BASELINE_ANALYSIS: BaselineAnalysisCapability(runtime_provider),
            CAPABILITY_ENGINE_ROUTE_RELEASE: EngineRouteReleaseCapability(runtime_provider),
            CAPABILITY_PEAK_AND_ANALYSIS: PeakAndAnalysisCapability(runtime_provider),
            CAPABILITY_TIFLASH_DEGRADATION: TiflashDegradationCapability(runtime_provider),
            CAPABILITY_TIFLASH_RECOVERY: TiflashRecoveryCapability(runtime_provider),
            CAPABILITY_TENANT_ONBOARDING: TenantOnboardingCapability(runtime_provider),
        }

    def capability(self, capability_id: str):
        instance = self._capabilities.get(capability_id)
        if instance is None:
            raise KeyError(
                f"unknown htap isolation capability: capability_id={capability_id!r}, "
                f"known={sorted(self._capabilities)!r}"
            )
        return instance
