"""Capability: replication link bandwidth degradation.

Link competition is a real external network condition, but the only sanctioned
repair path for an Agent is the public control table: this capability publishes
the degraded rate to ``frs_work_control.replication_link_rate_kbit`` (updated_by
='link_provisioning', an audited external provisioning change) and the runtime's
LinkPolicyGovernor applies it as a tc tbf qdisc on the primary's egress toward
the standby. Releasing restores the full link capacity. The applied/released
states carry qdisc evidence plus the dst-scoped filter set (the shaping is
replication-only by construction).

The degradation is partial — the published rate
covers the steady-state write rate, so replay keeps up while only the baseline
workload runs and falls behind only while an update surge pushes WAL
generation past the shaped rate. The alert therefore reports the freshness
symptom alone; attributing it to the link requires correlating the lag windows
with the surge windows (the surge alert is live in every lag window and is the
standing misattribution decoy).
"""

from __future__ import annotations

import time
from typing import Any, Callable, Mapping

from src.persistent_scenarios.backend.contracts import EventActivationContext, EventAlertPayload

from ..htap_shared_isolation.base import (
    CoreProtocolCapability,
    HtapCapabilityHandle,
    exclusive,
    injection_failed,
)

CONTROL_KEY = "replication_link_rate_kbit"
AWAIT_TBF_SECONDS = 30.0
_POLL_SECONDS = 1.0


class LinkBandwidthCapability(CoreProtocolCapability):
    capability_id = "frs_link_bandwidth_degraded"
    max_activation_seconds = 120

    def _resources(self, entity: str):
        return (exclusive(f"network:replication-link:{entity}", "network_qdisc"),)

    def _throttle_facts(self, context: EventActivationContext) -> dict[str, Any]:
        facts = context.environment.throttle_facts()
        return {"qdisc_show": facts["qdisc_show"], "filter_show": facts["filter_show"]}

    def _publish_rate(self, context: EventActivationContext, rate_kbit: int, updated_by: str) -> None:
        context.environment.primary_sql(
            f"UPDATE frs_work_control SET control_value = '{int(rate_kbit)}', updated_by = '{updated_by}', "
            f"updated_at = clock_timestamp() WHERE control_key = '{CONTROL_KEY}';"
        )

    def _start(self, context: EventActivationContext) -> HtapCapabilityHandle:
        handle = HtapCapabilityHandle(
            event_id=context.event.event_id,
            capability_id=self.capability_id,
            entity=context.event.entity,
            payload=context.event.payload,
        )
        rate_kbit = int(context.event.payload["throttle_rate_kbit"])
        handle.facts["throttle_rate_kbit"] = rate_kbit
        handle.runtime_state["session_facts_fn"] = (lambda ctx: (lambda: self._throttle_facts(ctx)))(context)
        handle.runtime_state["release_fn"] = context.environment.release_bandwidth_limit
        handle.runtime_state["policy_reset_fn"] = (
            lambda ctx=context: self._publish_rate(ctx, 0, "link_provisioning")
        )
        self._publish_rate(context, rate_kbit, "link_provisioning")
        return handle

    def _await_impact(self, context: EventActivationContext, handle: HtapCapabilityHandle) -> Mapping[str, Any]:
        # The governor consumes the published control row on its next poll; the
        # qdisc evidence must appear within the activation window or the
        # injection is a real failure.
        started = context.clock.monotonic()
        facts = self._throttle_facts(context)
        while "tbf" not in facts["qdisc_show"] and context.clock.monotonic() - started < AWAIT_TBF_SECONDS:
            time.sleep(_POLL_SECONDS)
            facts = self._throttle_facts(context)
        handle.facts.update(facts)
        if "tbf" not in facts["qdisc_show"]:
            handle.runtime_state["policy_reset_fn"]()
            handle.runtime_state["release_fn"]()
            raise injection_failed(handle, f"tbf qdisc absent after publishing the degraded rate: facts={facts!r}")
        handle.facts["outcome_kind"] = "applied"
        return dict(handle.facts)

    def _alert(self, handle: HtapCapabilityHandle) -> EventAlertPayload:
        # Symptom-only payload: the degraded link has no alert-worthy local
        # evidence of its own (the standby's CPU/IO profile stays healthy and
        # the shaping touches nothing but the replication stream), and the
        # freshness/replay symptom is shared with the update-surge windows the
        # alert text deliberately does not disambiguate. Root cause lives in
        # the governance row, reachable only through the correlation work.
        return EventAlertPayload(
            title=(
                "Report freshness on the analytics replica is degrading: replay is falling behind the "
                "primary and recently committed data may not be visible to report readers yet."
            ),
            symptoms=(
                "report freshness degrading",
                "replica replay falling behind the primary",
                "primary WAL retention increasing",
            ),
            severity="warning",
            category="replica_freshness",
        )

    def cleanup(self, handle: HtapCapabilityHandle) -> None:
        # Restore the governance policy and the physical qdisc. Both: the run
        # may already have stopped the governor thread, so the policy write
        # alone cannot release the link; a mid-run agent repair through the
        # control plane may already have released it, so the direct release is
        # applied-state guarded. A handle can legitimately be cleaned twice.
        if handle.runtime_state.get("released"):
            return
        handle.stop.set()
        handle.join_sessions()
        reset = handle.runtime_state.get("policy_reset_fn")
        if reset is not None:
            reset()
        release = handle.runtime_state.get("release_fn")
        if release is not None:
            handle.runtime_state["released"] = True
            release()

    def assert_clean(self, handle: HtapCapabilityHandle) -> Mapping[str, object]:
        facts = handle.runtime_state["session_facts_fn"]()
        if "tbf" in facts["qdisc_show"]:
            raise RuntimeError(f"Link bandwidth throttle survived cleanup: event_id={handle.event_id!r}, facts={facts!r}")
        return {"capability_id": self.capability_id, "event_id": handle.event_id, "status": "clean"}
