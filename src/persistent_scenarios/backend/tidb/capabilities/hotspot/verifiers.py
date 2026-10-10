"""Business-truth verifier bindings for the hotspot instance package.

Verifiers follow the standard convention
``verifier(port, connection, ledger_view, params) -> Mapping``. The tuple is
exposed for the backend ``StateFactProvider`` assembly.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from src.persistent_scenarios.tidb.hotspot.verifiers import (
    commerce_ledger_conservation,
    orders_idempotency_uniqueness,
    unknown_commit_dedup,
)


def _params_verifier(func: Callable[..., Mapping[str, Any]], required: frozenset[str]) -> Callable[..., Mapping[str, Any]]:
    def verify(port: Any, connection: Any, ledger_view: Any, params: Mapping[str, Any]) -> Mapping[str, Any]:
        missing = sorted(required - set(params))
        if missing:
            raise ValueError(f"{func.__name__} is missing required params: missing={missing!r}")
        return func(port, connection, ledger_view, params)

    verify.verifier_id = func.__name__
    return verify


commerce_ledger_conservation_verifier = _params_verifier(commerce_ledger_conservation, frozenset())
orders_idempotency_uniqueness_verifier = _params_verifier(orders_idempotency_uniqueness, frozenset())
unknown_commit_dedup_verifier = _params_verifier(unknown_commit_dedup, frozenset())

VERIFIERS: tuple[tuple[str, Callable[..., Mapping[str, Any]]], ...] = (
    ("commerce_ledger_conservation", commerce_ledger_conservation_verifier),
    ("orders_idempotency_uniqueness", orders_idempotency_uniqueness_verifier),
    ("unknown_commit_dedup", unknown_commit_dedup_verifier),
)
