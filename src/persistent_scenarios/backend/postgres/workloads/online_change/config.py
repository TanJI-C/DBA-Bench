"""Instance parameters for pg_oltp_online_change.

Same split as `business_priority/config.py`: the frozen spec owns the time
boundaries, routing key and service contracts; this module owns the driver,
release-task and dataset parameters. All numbers follow the three-path
difficulty calibration.
"""

from __future__ import annotations

from ..oltp_core.control import ClientConfig
from ..oltp_core.runtime import DriverConfig
from ..oltp_core.traffic import TrafficPlan, TrafficTier

WORKLOAD_KEY = "online_change"
BASE_IMAGE = "aiopsbench-pg5-oltp-online-change:h2-promo-campaign"

TRADE_TIERS = TrafficPlan(tiers=(
    TrafficTier("normal", 0.0, 4.0, 8.0, 10000),
    TrafficTier("promo", 2640.0, 8.0, 16.0, 15000),
))

DRIVER_CONFIG = DriverConfig(pool_size=8, control_poll_seconds=5.0, seed=20260919)

HISTORY_ORDER_COUNT = 500_000
PROMO_INITIAL_QTY = 20_000

# Role credentials for the dataset image; integration's required-state
# sampler opens fresh role-scoped connections from this mapping (interface
# v1: guc_effective with scope=role needs a fresh connection per role).
ROLE_CREDENTIALS = {
    "shop_app": {"user": "shop_app", "password": "shop_app"},
    "shop_auditor": {"user": "shop_auditor", "password": "shop_auditor"},
    "postgres": {"user": "postgres", "password": "password"},
}

INITIAL_CLIENT_CONFIG = ClientConfig(
    config_version=1, request_timeout_ms=8000, max_retries=1,
    retry_backoff_ms=500, retry_jitter_ms=200,
)

NEW_VERSION_COLUMN = "promo_tier"
HISTORY_CUTOFF_CREATED_AT = 1_750_000_000.0

COLUMN_TASK_ID = "release_promo_tier_column"
CONSTRAINT_TASK_ID = "release_promo_tier_constraint"
INDEX_TASK_ID = "release_promo_tier_index"
BACKFILL_TASK_ID = "backfill_promo_tier"

# Scenario-seconds window of the release-governance constraint (AccessExclusive
# ADD CONSTRAINT ... NOT VALID): the change calendar schedules it after the
# promotion peak opens, so an unhandled second long transaction (arriving
# t=3120) queues it until past the horizon. The deploy tool's third pass is the
# only pass whose deploy budget reaches the window.
CONSTRAINT_WINDOW_SECONDS = 3300.0

# --- promo-campaign caliber override -----------------------------------------
# The campaign opens with the promotion peak (promo_peak, t=2640) and publishes
# its own VIP threshold; the backfill worker resolves its tier boundary at
# batch time, so batches processed while the campaign is active write the
# campaign caliber instead of the canonical VIP_AMOUNT_CENTS derivation. The
# drift band is [VIP_AMOUNT_CENTS, PROMO_VIP_THRESHOLD_OVERRIDE_CENTS): image
# history rows at amount 260_000 * 5 = 1_300_000 cents are exactly the band
# population, so every campaign-window batch silently mislabels them.
PROMO_CAMPAIGN_ID = "promo-2026-h2"
PROMO_VIP_THRESHOLD_OVERRIDE_CENTS = 2_000_000
PROMO_PEAK_SECONDS = 2640.0

# Default backfill rate (rows/s): the zero-action backfill cannot start before
# the first long transaction releases shop.orders (600 + 1500 = 2100 scenario
# seconds), so its duration floor HISTORY_ORDER_COUNT / this rate must keep the
# backfill running past PROMO_PEAK_SECONDS — that overlap is what makes the
# definition drift a mechanism, not a timing accident.
BACKFILL_RATE_ROWS_PER_SECOND = 800
LONG_TX1_EXIT_LOWER_BOUND_SECONDS = 2100.0
