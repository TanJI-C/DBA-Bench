"""Instance parameters for pg_continuous_ops_business_priority.

The persistent-scenario-v2 spec does not carry instance mechanism parameters;
the frozen spec owns the boundaries (warmup/input_stop/agent_stop/horizon),
the environment routing key and the service contracts, while this module owns
the driver configuration that integration's WorkloadProvider uses to assemble
`OltpWorkloadDriver`. All numbers follow the three-path difficulty calibration.
"""

from __future__ import annotations

from ..oltp_core.control import ClientConfig
from ..oltp_core.runtime import DriverConfig
from ..oltp_core.traffic import TrafficPlan, TrafficTier

WORKLOAD_KEY = "business_priority"
BASE_IMAGE = "aiopsbench-pg5-oltp-business:latest"

TRADE_TIERS = TrafficPlan(tiers=(
    TrafficTier("normal", 0.0, 4.0, 8.0, 10000),
    TrafficTier("promo", 480.0, 8.0, 16.0, 15000),
    TrafficTier("peak", 2640.0, 12.0, 24.0, 15000),
))

DRIVER_CONFIG = DriverConfig(pool_size=10, control_poll_seconds=5.0, seed=20260918)

HISTORY_ORDER_COUNT = 300_000
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

ARCHIVE_JOB_ID = "orders-history-archive"
HISTORY_CUTOFF_CREATED_AT = 1_750_000_000.0

# Archive delivery tradeoff (contract published in ops.delivery_contract; the
# numbers follow the three-path difficulty calibration).
#
# Feasibility over the 300k-row history with the archive enabled at t=1440 and
# the delivery deadline at t=3480:
# - seed rate 130 rows/s alone needs ~2308s -> completes ~t=3800: the naive
#   schedule misses delivery by a robust margin and violates the peak cap, so
#   the zero path fails both observables without depending on timing noise;
# - compliant throttle (rate 100 inside the 2640-3000 peak window, 400 after)
#   completes ~t=3270 (~210s slack);
# - a full-budget deferral (pause 420s, then 400 rows/s) still delivers
#   (~t=3420), while anything beyond the budget misses both the budget and,
#   past ~480s of pause, the deadline: the two constraints close the escape
#   hatches in opposite directions.
ARCHIVE_SEED_RATE_ROWS_PER_SECOND = 130
ARCHIVE_SEED_BATCH_ROWS = 600
PEAK_WINDOW_START_SECONDS = 2640.0
PEAK_WINDOW_END_SECONDS = 3000.0
PEAK_ARCHIVE_RATE_CAP_ROWS_PER_SECOND = 100
ARCHIVE_RATE_CEILING_ROWS_PER_SECOND = 400
ARCHIVE_DEFERRAL_BUDGET_SECONDS = 420.0
