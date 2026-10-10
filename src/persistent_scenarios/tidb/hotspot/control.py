"""Client retry policy control plane for the OLTP instance.

The control table is the public, agent-writable authorization surface for
application retry/routing behaviour (the agent must get a real,
discoverable, effective control interface). Publication is validated by the
driver-side poller as a trusted client protection: a stale or unsafe policy
row is rejected instead of adopted, which is the genuine "prevented" path of
the legacy client release capability.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping


_ORDER_ID_PREFIX_PATTERN = re.compile(r"[A-Za-z0-9._-]+")
# shop.orders.order_id/idempotency_key are VARCHAR(64); the generated identity
# is "<prefix>-o" plus an 8-digit sequence (10 chars beyond the prefix).
_ORDER_ID_SUFFIX_LENGTH = 10
ORDER_ID_COLUMN_LENGTH = 64
# ops.client_config.order_id_prefix is VARCHAR(16); the poller mirrors the
# column bound so an over-wide publication is rejected before adoption.
ORDER_ID_PREFIX_MAX_LENGTH = 16


@dataclass(frozen=True, slots=True)
class ClientPolicy:
    config_version: int
    request_timeout_ms: int
    max_retries: int
    retry_backoff_ms: int
    retry_jitter_ms: int
    max_connection_lifetime_seconds: int
    connect_bias: str | None
    lock_wait_timeout_seconds: int
    order_id_prefix: str | None
    settlement_paused: int

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "ClientPolicy":
        return cls(
            config_version=int(row["config_version"]),
            request_timeout_ms=int(row["request_timeout_ms"]),
            max_retries=int(row["max_retries"]),
            retry_backoff_ms=int(row["retry_backoff_ms"]),
            retry_jitter_ms=int(row["retry_jitter_ms"]),
            max_connection_lifetime_seconds=int(row["max_connection_lifetime_seconds"]),
            connect_bias=None if row.get("connect_bias") is None else str(row["connect_bias"]),
            lock_wait_timeout_seconds=int(row["lock_wait_timeout_seconds"]),
            order_id_prefix=None if row.get("order_id_prefix") is None else str(row["order_id_prefix"]),
            settlement_paused=int(row["settlement_paused"]),
        )


READ_CLIENT_POLICY_SQL = (
    "SELECT config_version, request_timeout_ms, max_retries, retry_backoff_ms, retry_jitter_ms, "
    "max_connection_lifetime_seconds, connect_bias, lock_wait_timeout_seconds, "
    "order_id_prefix, settlement_paused "
    "FROM ops.client_config WHERE id = 1"
)

PUBLISH_CLIENT_POLICY_SQL = (
    "UPDATE ops.client_config SET config_version = %s, request_timeout_ms = %s, max_retries = %s, "
    "retry_backoff_ms = %s, retry_jitter_ms = %s, max_connection_lifetime_seconds = %s, "
    "connect_bias = %s, lock_wait_timeout_seconds = %s WHERE id = 1"
)


def validate_policy_transition(previous: ClientPolicy, next_policy: ClientPolicy) -> None:
    """Trusted client protection. Raises on unsafe/stale publications."""
    if next_policy.config_version <= previous.config_version:
        raise ValueError(
            "client config version must strictly increase: "
            f"applied_version={previous.config_version}, published_version={next_policy.config_version}"
        )
    if next_policy.request_timeout_ms <= 0:
        raise ValueError(f"request_timeout_ms must be positive: value={next_policy.request_timeout_ms}")
    if next_policy.max_retries < 0:
        raise ValueError(f"max_retries must be non-negative: value={next_policy.max_retries}")
    if next_policy.retry_backoff_ms < 0 or next_policy.retry_jitter_ms < 0:
        raise ValueError(
            "retry backoff/jitter must be non-negative: "
            f"backoff={next_policy.retry_backoff_ms}, jitter={next_policy.retry_jitter_ms}"
        )
    if next_policy.max_connection_lifetime_seconds < 1:
        raise ValueError(
            f"max_connection_lifetime_seconds must be at least 1: value={next_policy.max_connection_lifetime_seconds}"
        )
    if next_policy.lock_wait_timeout_seconds < 1:
        raise ValueError(
            f"lock_wait_timeout_seconds must be at least 1: value={next_policy.lock_wait_timeout_seconds}"
        )
    if next_policy.order_id_prefix is not None:
        prefix = next_policy.order_id_prefix
        if (
            not 1 <= len(prefix) <= ORDER_ID_PREFIX_MAX_LENGTH
            or _ORDER_ID_PREFIX_PATTERN.fullmatch(prefix) is None
        ):
            raise ValueError(
                f"order_id_prefix must be 1..{ORDER_ID_PREFIX_MAX_LENGTH} characters of [A-Za-z0-9._-]: "
                f"value={prefix!r}"
            )
        if len(prefix) + _ORDER_ID_SUFFIX_LENGTH > ORDER_ID_COLUMN_LENGTH:
            raise ValueError(
                f"order_id_prefix leaves generated order ids wider than shop.orders.order_id: "
                f"prefix={prefix!r}, generated_length={len(prefix) + _ORDER_ID_SUFFIX_LENGTH}, "
                f"column_length={ORDER_ID_COLUMN_LENGTH}"
            )
    if next_policy.settlement_paused not in (0, 1):
        raise ValueError(
            f"settlement_paused must be 0 or 1: value={next_policy.settlement_paused}"
        )
