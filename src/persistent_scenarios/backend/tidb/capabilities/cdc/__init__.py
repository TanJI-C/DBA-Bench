"""TiDB CDC freshness instance capabilities and verifiers.

``CAPABILITIES`` and ``VERIFIERS`` are the registration surfaces consumed by
integration (explicit per-workload import mapping; no auto discovery).
"""

from .capabilities import (
    CdcDownstreamBatchCapability,
    CdcOrderPeakCapability,
    CdcSchemaReleaseCapability,
)
from .verifiers import VERIFIERS

CAPABILITIES: tuple = (
    CdcDownstreamBatchCapability(),
    CdcSchemaReleaseCapability(),
    CdcOrderPeakCapability(),
)

__all__ = ["CAPABILITIES", "VERIFIERS"]
