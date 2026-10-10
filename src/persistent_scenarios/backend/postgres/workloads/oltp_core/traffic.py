"""Traffic tiers and the externally owned arrival plan.

`place_order_qps` drives the paired trade arrival: each checkout arrival also
schedules exactly one payment callback (lagged), so payment volume always
mirrors checkout volume. Rejected or timed-out checkouts still own their
payment operation identity and count in the denominator as business losses.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrafficTier:
    name: str
    start_seconds: float
    place_order_qps: float
    stock_read_qps: float
    op_deadline_ms: int

    def __post_init__(self) -> None:
        for name in ("place_order_qps", "stock_read_qps"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"Traffic tier QPS must be positive: tier={self.name!r}, {name}={value!r}")
        if self.op_deadline_ms <= 0:
            raise ValueError(f"Traffic tier deadline must be positive: tier={self.name!r}, op_deadline_ms={self.op_deadline_ms!r}")


@dataclass(frozen=True, slots=True)
class TrafficPlan:
    """Tiers sorted by start; the first tier must start at second zero."""

    tiers: tuple[TrafficTier, ...]

    def __post_init__(self) -> None:
        if not self.tiers:
            raise ValueError("TrafficPlan requires at least one tier")
        starts = [tier.start_seconds for tier in self.tiers]
        if starts != sorted(starts):
            raise ValueError(f"TrafficPlan tiers must be ordered by start: starts={starts!r}")
        if starts[0] != 0:
            raise ValueError(f"TrafficPlan first tier must start at second zero: starts={starts!r}")
        names = [tier.name for tier in self.tiers]
        if len(names) != len(set(names)):
            raise ValueError(f"TrafficPlan tier names must be unique: names={names!r}")

    def tier_at(self, seconds: float) -> TrafficTier:
        selected = self.tiers[0]
        for tier in self.tiers:
            if tier.start_seconds <= seconds:
                selected = tier
            else:
                break
        return selected

    def tier_by_name(self, name: str) -> TrafficTier:
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise ValueError(f"Unknown traffic tier: name={name!r}, known={sorted(tier.name for tier in self.tiers)!r}")

    def as_mapping(self) -> dict[str, float]:
        return {tier.name: tier.start_seconds for tier in self.tiers}
