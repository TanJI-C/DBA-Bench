"""Instance-5 event capabilities and business verifiers.

Exposed for the integration assembly: ``CAPABILITIES`` and ``VERIFIERS``
(``(verifier_id, callable)`` pairs; call convention
``verifier(port, connection, ledger_view, params)``).
"""

from .capabilities import (
    ConnectionPoolBiasCapability,
    MaintenanceWorkOrderCapability,
    MigrationLinkDelayCapability,
    ReserveStoreArrivalCapability,
    TradePeakCapability,
)
from .verifiers import VERIFIERS

CAPABILITIES: tuple = (
    MaintenanceWorkOrderCapability(),
    ReserveStoreArrivalCapability(),
    TradePeakCapability(),
    ConnectionPoolBiasCapability(),
    MigrationLinkDelayCapability(),
)

__all__ = ["CAPABILITIES", "VERIFIERS"]
