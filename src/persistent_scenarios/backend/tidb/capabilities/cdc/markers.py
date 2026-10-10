"""End-to-end business marker pairing for the CDC freshness scenario.

Business freshness is decided by pairing source-committed orders with the
rows the downstream read model actually serves, by (business key, version)
and marker digest. Changefeed state and checkpoint TSO are auxiliary evidence
only: state=normal with a frozen checkpoint can leave downstream rows missing
(verified on TiCDC v8.1.0), so only the paired rows prove freshness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .schema import DOWNSTREAM_DATABASE, UPSTREAM_DATABASE, ORDERS_TABLE


@dataclass(frozen=True, slots=True)
class UpstreamCommittedOrder:
    order_id: int
    version: int
    state: str
    amount: str
    marker: str


@dataclass(frozen=True, slots=True)
class PairingReport:
    checked: int
    missing: tuple[int, ...]
    version_mismatch: tuple[tuple[int, int, int], ...]  # (order_id, upstream_version, downstream_version)
    marker_mismatch: tuple[int, ...]

    @property
    def complete(self) -> bool:
        return not (self.missing or self.version_mismatch or self.marker_mismatch)

    def as_details(self) -> Mapping[str, object]:
        return {
            "checked": self.checked,
            "missing_order_ids": list(self.missing)[:500],
            "missing_count": len(self.missing),
            "version_mismatch": [list(item) for item in self.version_mismatch][:500],
            "version_mismatch_count": len(self.version_mismatch),
            "marker_mismatch_order_ids": list(self.marker_mismatch)[:500],
            "marker_mismatch_count": len(self.marker_mismatch),
        }


def fetch_upstream_committed(cursor, order_ids: Sequence[int]) -> dict[int, UpstreamCommittedOrder]:
    if not order_ids:
        return {}
    ids = ",".join(str(int(oid)) for oid in order_ids)
    cursor.execute(
        f"SELECT order_id, version, state, amount, marker FROM {UPSTREAM_DATABASE}.{ORDERS_TABLE} "
        f"WHERE order_id IN ({ids})"
    )
    return {
        int(row[0]): UpstreamCommittedOrder(order_id=int(row[0]), version=int(row[1]),
                                            state=str(row[2]), amount=str(row[3]), marker=str(row[4]))
        for row in cursor.fetchall()
    }


def fetch_downstream_versions(cursor, order_ids: Sequence[int]) -> dict[int, tuple[int, str, str]]:
    if not order_ids:
        return {}
    ids = ",".join(str(int(oid)) for oid in order_ids)
    cursor.execute(
        f"SELECT order_id, version, state, marker FROM {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} "
        f"WHERE order_id IN ({ids})"
    )
    return {int(row[0]): (int(row[1]), str(row[2]), str(row[3])) for row in cursor.fetchall()}


def pair_orders(cursor, upstream_orders: Mapping[int, UpstreamCommittedOrder]) -> PairingReport:
    """Pair source-committed orders against the downstream read model.

    A commitment is satisfied when the read model serves the committed version
    or any later one (a newer version implies the older commit was applied);
    marker equality is only required for the latest committed version itself.
    """
    missing: list[int] = []
    version_mismatch: list[tuple[int, int, int]] = []
    marker_mismatch: list[int] = []
    for order_id, expected in upstream_orders.items():
        observed = fetch_downstream_versions(cursor, [order_id]).get(order_id)
        if observed is None:
            missing.append(order_id)
            continue
        down_version, _down_state, down_marker = observed
        if down_version < expected.version:
            version_mismatch.append((order_id, expected.version, down_version))
        elif down_version == expected.version and down_marker != expected.marker:
            marker_mismatch.append(order_id)
    return PairingReport(
        checked=len(upstream_orders),
        missing=tuple(sorted(missing)),
        version_mismatch=tuple(sorted(version_mismatch)),
        marker_mismatch=tuple(sorted(marker_mismatch)),
    )


def count_paid_orders(cursor) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {DOWNSTREAM_DATABASE}.{ORDERS_TABLE} WHERE state = 'paid'")
    return int(cursor.fetchall()[0][0])
