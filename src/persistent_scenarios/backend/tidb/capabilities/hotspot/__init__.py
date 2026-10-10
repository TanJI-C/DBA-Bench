"""Instance-1 event capabilities and business verifiers.

Exposed for the integration assembly: ``CAPABILITIES`` (one object per
capability_id, satisfying the core ``PersistentScenarioEventCapability``
protocol) and ``VERIFIERS`` (``(verifier_id, callable)`` pairs, call
convention ``verifier(port, connection, ledger_view, params)``).
"""

from .capabilities import (
    LegacyClientReleaseCapability,
    PromoHotspotCapability,
    SettlementLongTxCapability,
    TikvCatchUpBurstCapability,
    TikvSlowThrottleCapability,
    TikvThrottleReleaseCapability,
)
from .verifiers import VERIFIERS

CAPABILITIES: tuple = (
    PromoHotspotCapability(),
    SettlementLongTxCapability(),
    TikvSlowThrottleCapability(),
    TikvThrottleReleaseCapability(),
    TikvCatchUpBurstCapability(),
    LegacyClientReleaseCapability(),
)

__all__ = ["CAPABILITIES", "VERIFIERS"]
