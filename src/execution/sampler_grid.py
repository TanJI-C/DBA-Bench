"""Shared fixed-grid sampling tolerance policy.

The PostgreSQL resource sampler and the TiDB metric-capture grid alignment
enforce one contract: an isolated timing anomaly (a late sample or a short run
of missed grid slots) is tolerated and skipped with padding, and only
sustained sampling degradation fails the run. Each anomaly event raises the
strike count; a stretch of in-grid samples at least
SAMPLER_LAG_TOLERANCE_INTERVALS slots long decays it back toward zero. The
run is abandoned only after SAMPLER_LAG_STRIKES_LIMIT net strikes.
"""

SAMPLER_LAG_TOLERANCE_INTERVALS = 3
SAMPLER_LAG_STRIKES_LIMIT = 10


class SamplerGridStrikes:
    """Strike/decay counter for the fixed-grid sampling contract."""

    def __init__(self, *, strikes_limit: int = SAMPLER_LAG_STRIKES_LIMIT) -> None:
        self._strikes_limit = strikes_limit
        self._strikes = 0

    @property
    def strikes(self) -> int:
        return self._strikes

    def strike(self, *, detail: str = "") -> None:
        self._strikes += 1
        if self._strikes >= self._strikes_limit:
            message = (
                "Sampler repeatedly violated the fixed grid tolerance: "
                f"strikes={self._strikes}, strikes_limit={self._strikes_limit}"
            )
            if detail:
                message = f"{message}, {detail}"
            raise RuntimeError(message)

    def decay(self) -> None:
        self._strikes = max(0, self._strikes - 1)
