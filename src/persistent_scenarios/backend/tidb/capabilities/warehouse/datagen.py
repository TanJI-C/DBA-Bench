"""Deterministic batch generators for the warehouse delivery service.

Every batch is reproducible from its spec (fixed seed, hash-driven distributions):
the history batch is a mild natural distribution, batch A concentrates on regions
1-3 and batch B shifts the same skew class onto regions 8-10.
The same generator feeds the staging tables and the frozen
report truth, so the expected report results can always be recomputed.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterator

from .schema import (
    BATCH_A_ID,
    BATCH_B_ID,
    BATCH_SPECS,
    CHANNELS,
    HISTORY_BATCH_ID,
    HISTORY_ROW_COUNT,
    ITEM_COUNT,
    REGION_COUNT,
    WAREHOUSE_COUNT,
)

SEED_HISTORY = 20260918
SEED_BATCH_A = 20260919
SEED_BATCH_B = 20260920
SEED_BACKFILL = 20260921

COST_RATIO = 0.72
HOT_ITEM_COUNT = 40
HOT_ITEM_SHARE = 0.30

_HISTORY_START = datetime(2026, 9, 10, 0, 0, 0)
_BATCH_WINDOWS = {
    BATCH_A_ID: datetime(2026, 9, 18, 6, 0, 0),
    BATCH_B_ID: datetime(2026, 9, 18, 18, 0, 0),
    3: datetime(2026, 9, 18, 12, 0, 0),
}
_BATCH_HOURS = 4


def _first_order_id(batch_id: int) -> int:
    return batch_id * 10_000_000


def _seed(batch_id: int) -> int:
    return {HISTORY_BATCH_ID: SEED_HISTORY, BATCH_A_ID: SEED_BATCH_A, BATCH_B_ID: SEED_BATCH_B, 3: SEED_BACKFILL}[batch_id]


def _skew_region_chooser(batch_id: int, rng: random.Random) -> tuple[int, ...]:
    """Region weights: mild natural skew for history, contract skew for staged batches."""
    if batch_id == HISTORY_BATCH_ID:
        weights = [30, 14, 11, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    else:
        skew_regions, share = next(
            (spec.skew_regions, spec.skew_share) for spec in BATCH_SPECS if spec.batch_id == batch_id
        )
        remaining = 1.0 - share
        rest = REGION_COUNT - len(skew_regions)
        weights = []
        for region in range(1, REGION_COUNT + 1):
            if region in skew_regions:
                weights.append(int(share / len(skew_regions) * 1000))
            else:
                weights.append(int(remaining / rest * 1000))
    population = list(range(1, REGION_COUNT + 1))
    return tuple(rng.choices(population, weights=weights, k=1)[0] for _ in range(0))


def _region_weights(batch_id: int) -> list[int]:
    if batch_id == HISTORY_BATCH_ID:
        return [30, 14, 11, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    skew_regions, share = next(
        (spec.skew_regions, spec.skew_share) for spec in BATCH_SPECS if spec.batch_id == batch_id
    )
    remaining = 1.0 - share
    rest = REGION_COUNT - len(skew_regions)
    return [
        int(share / len(skew_regions) * 1000) if region in skew_regions else int(remaining / rest * 1000)
        for region in range(1, REGION_COUNT + 1)
    ]


def _warehouse_for_region(rng: random.Random, region_id: int) -> int:
    per_region = WAREHOUSE_COUNT // REGION_COUNT
    start = (region_id - 1) * per_region
    return start + rng.randrange(per_region)


def _item_id(rng: random.Random) -> int:
    if rng.random() < HOT_ITEM_SHARE:
        return 1 + rng.randrange(HOT_ITEM_COUNT)
    return HOT_ITEM_COUNT + 1 + rng.randrange(ITEM_COUNT - HOT_ITEM_COUNT)


def _price(item_id: int) -> float:
    base = 5.0 + (item_id * 37 % 200) / 4.0
    return round(base, 2)


def generate_rows(batch_id: int, row_count: int | None = None) -> Iterator[tuple]:
    """Yield fact rows for one batch, deterministic in batch_id and row_count."""
    rng = random.Random(_seed(batch_id))
    if batch_id == HISTORY_BATCH_ID:
        count = HISTORY_ROW_COUNT
    else:
        count = next(spec.row_count for spec in BATCH_SPECS if spec.batch_id == batch_id)
    if row_count is not None:
        count = row_count
    weights = _region_weights(batch_id)
    region_population = list(range(1, REGION_COUNT + 1))
    window_start = _HISTORY_START if batch_id == HISTORY_BATCH_ID else _BATCH_WINDOWS[batch_id]
    window_seconds = 24 * 3600 if batch_id == HISTORY_BATCH_ID else _BATCH_HOURS * 3600
    first_order_id = _first_order_id(batch_id)
    for index in range(count):
        region_id = rng.choices(region_population, weights=weights, k=1)[0]
        item = _item_id(rng)
        price = _price(item)
        quantity = 1 + rng.randrange(5)
        cost = round(price * (COST_RATIO + (rng.random() - 0.5) * 0.04), 2)
        yield (
            first_order_id + index,
            batch_id,
            region_id,
            _warehouse_for_region(rng, region_id),
            item,
            CHANNELS[rng.randrange(len(CHANNELS))],
            quantity,
            price,
            cost,
            round(price * quantity, 2),
            window_start + timedelta(seconds=rng.randrange(window_seconds)),
        )


INSERT_STAGING_SQL = (
    "INSERT INTO {stage_table} (order_id, batch_id, region_id, warehouse_id, item_id, channel, "
    "quantity, unit_price, unit_cost, amount, order_ts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
)
