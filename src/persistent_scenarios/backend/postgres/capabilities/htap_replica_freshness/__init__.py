"""Native capability registry for pg_htap_replica_freshness."""

from .link_bandwidth import LinkBandwidthCapability
from .primary_update_surge import PrimaryUpdateSurgeCapability
from .standby_long_snapshot import StandbyLongSnapshotCapability

REPLICA_FRESHNESS_CAPABILITY_TYPES = (
    StandbyLongSnapshotCapability,
    PrimaryUpdateSurgeCapability,
    LinkBandwidthCapability,
)

CAPABILITIES_BY_ID = {capability.capability_id: capability() for capability in REPLICA_FRESHNESS_CAPABILITY_TYPES}

__all__ = [
    "StandbyLongSnapshotCapability",
    "PrimaryUpdateSurgeCapability",
    "LinkBandwidthCapability",
    "REPLICA_FRESHNESS_CAPABILITY_TYPES",
    "CAPABILITIES_BY_ID",
]
