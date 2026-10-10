"""Native capability registry for pg_htap_shared_resource_isolation.

Capabilities are registered by capability_id; the same capability may run for
several occurrences with distinct event_ids.
"""

from .dashboard_retry_storm import DashboardRetryStormCapability
from .hotspot_churn import HotspotChurnCapability
from .stuck_export_snapshot import StuckExportSnapshotCapability
from .wide_history_scan import WideHistoryScanCapability

SHARED_ISOLATION_CAPABILITY_TYPES = (
    WideHistoryScanCapability,
    StuckExportSnapshotCapability,
    HotspotChurnCapability,
    DashboardRetryStormCapability,
)

CAPABILITIES_BY_ID = {capability.capability_id: capability() for capability in SHARED_ISOLATION_CAPABILITY_TYPES}

__all__ = [
    "WideHistoryScanCapability",
    "StuckExportSnapshotCapability",
    "HotspotChurnCapability",
    "DashboardRetryStormCapability",
    "SHARED_ISOLATION_CAPABILITY_TYPES",
    "CAPABILITIES_BY_ID",
]
