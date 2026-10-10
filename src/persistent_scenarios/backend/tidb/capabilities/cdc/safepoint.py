"""Upstream GC safepoint checkpoint-stall mechanism (composite factor B).

Production chain on the frozen deployment (TiDB v8.1.0 + TiCDC v8.1.0):

1. The sink apply of the released schema fails (downstream ALTER privilege
   drifted, factor A). The changefeed retries the DDL forever while its
   checkpoint stays pinned at the pre-DDL TSO and it keeps reporting
   ``state=normal`` (verified by live anchors).
2. A pinned changefeed checkpoint holds the PD service safepoint, so the
   cluster GC safepoint stops advancing. This is the factor-B stall: it
   develops BECAUSE factor A keeps the DDL retry loop alive, and it does not
   dissolve on its own.
3. The deployment runs a freshness-critical fail-fast replication config:
   the changefeed gives up its GC pin after ``PIN_RELEASE_STALL_SECONDS`` of
   frozen checkpoint (the TiCDC ``gc-ttl`` analogue), and the upstream GC
   retention baseline is ``GC_LIFE_TIME_BASELINE``. After the pin release the
   changefeed stays parked (a failed apply loop never self-heals into a
   resumed catch-up), the GC safepoint resumes advancing at
   ``now - life_time``, and change history becomes GC-eligible again.
4. Consequences the agent must handle: resuming the catch-up requires the
   GC boundary to still cover the pinned checkpoint (secure retention with
   the authorized ``tidb_gc_life_time`` GUC, or resume before the boundary
   bites), and only-privilege repairs leave the replication parked - the
   catch-up runs into the safepoint/checkpoint stall and the watermark
   contract stays unmet.

The numbers here are mechanism facts of the frozen deployment (chosen with a
business rationale), not SO budgets: they never
gate a service objective by themselves; the data-level verifiers (watermark
pairing, catch-up) decide the contract. The deployment must configure the
changefeed ``gc-ttl`` to match ``PIN_RELEASE_STALL_SECONDS``.
"""

from __future__ import annotations

from typing import Mapping, Sequence

# Fail-fast GC pin release: the changefeed was deployed with gc-ttl=600s so a
# stuck checkpoint never blocks upstream GC for long (freshness-critical
# pipeline protects the upstream first).
PIN_RELEASE_STALL_SECONDS = 600.0
# Upstream GC retention baseline: generous retention so a released pin leaves
# a bounded recovery window for the replication boundary (TiDB GUC
# tidb_gc_life_time, deploy baseline 30m).
GC_LIFE_TIME_BASELINE_SECONDS = 1800.0
GC_LIFE_TIME_VARIABLE = "tidb_gc_life_time"
GC_SAFE_POINT_VARIABLE = "tikv_gc_safe_point"


def parse_gc_duration(value: str) -> float:
    """Parse TiDB duration strings ("30m0s", "600s", "1h30m") into seconds."""
    text = value.strip().lower()
    if not text:
        raise ValueError(f"empty GC duration value: {value!r}")
    total = 0.0
    number = ""
    for char in text:
        if char.isdigit() or char == ".":
            number += char
            continue
        seconds = {"s": 1.0, "m": 60.0, "h": 3600.0}.get(char)
        if seconds is None or not number:
            raise ValueError(f"unsupported GC duration value: {value!r}")
        total += float(number) * seconds
        number = ""
    if number:
        raise ValueError(f"GC duration value must carry a unit: {value!r}")
    return total


def format_gc_duration(seconds: float) -> str:
    """Format seconds as a TiDB duration string ("30m0s", "24h0m0s", "10m0s").

    Inverse of :func:`parse_gc_duration` for whole-second values; the deploy
    baseline must round-trip so the deployed value and the schema_release
    payload fact display identically to the agent.
    """
    total = int(seconds)
    if total != seconds or total < 0:
        raise ValueError(f"GC duration must be whole non-negative seconds: {seconds!r}")
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if hours or minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return "".join(parts)


def sample_upstream_gc_state(cursor) -> Mapping[str, object]:
    """Read the real upstream GC surfaces (agent-visible with plain SQL).

    ``SHOW VARIABLES LIKE 'tidb_gc_life_time'`` and
    ``SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME =
    'tikv_gc_safe_point'`` are the production diagnostics for a safepoint
    stall; both must answer or the sampling fails (no fabricated evidence).
    """
    cursor.execute(f"SHOW VARIABLES LIKE '{GC_LIFE_TIME_VARIABLE}'")
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"upstream did not expose {GC_LIFE_TIME_VARIABLE!r}")
    life_time_value = str(rows[0][1])
    cursor.execute(
        f"SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME = '{GC_SAFE_POINT_VARIABLE}'"
    )
    safe_point_rows = cursor.fetchall()
    if not safe_point_rows:
        raise ValueError(f"upstream did not expose {GC_SAFE_POINT_VARIABLE!r}")
    return {
        "gc_life_time": life_time_value,
        "gc_life_time_seconds": parse_gc_duration(life_time_value),
        "tikv_gc_safe_point": str(safe_point_rows[0][0]),
    }


def safepoint_stalled(first: Mapping[str, object], second: Mapping[str, object]) -> bool:
    """Two samples taken at different times report the same GC safepoint.

    This is the frozen-safepoint signature of a pinned changefeed checkpoint;
    an advancing safepoint yields different values and excludes the stall."""
    return str(first["tikv_gc_safe_point"]) == str(second["tikv_gc_safe_point"])


def pin_release_at(stall_started_at: float,
                   pin_release_stall_seconds: float = PIN_RELEASE_STALL_SECONDS) -> float:
    """When the changefeed gives up its GC pin after the checkpoint froze."""
    return stall_started_at + pin_release_stall_seconds


def checkpoint_pinned(now: float, stall_started_at: float,
                      pin_released_at: float | None = None) -> bool:
    """The checkpoint is pinned from the stall start until the pin release."""
    if now < stall_started_at:
        return False
    return pin_released_at is None or now < pin_released_at


def gc_eligible_from(commit_time: float, life_time_seconds: float,
                     pin_released_at: float | None) -> float | None:
    """Earliest time GC may delete the change history of one commit.

    While the changefeed holds its pin (``pin_released_at is None``) the
    service safepoint blocks GC entirely and nothing is eligible. After the
    release the boundary is ``now - life_time``, so a commit becomes eligible
    at ``commit_time + life_time`` - or immediately at the release when the
    stall already outlived the retention.
    """
    if pin_released_at is None:
        return None
    return max(pin_released_at, commit_time + life_time_seconds)


def exposed_commits(commit_times: Sequence[float], *, now: float, life_time_seconds: float,
                    pin_released_at: float | None,
                    replicated_through: float) -> tuple[float, ...]:
    """Stall-window commits whose change history GC has already deleted.

    These commits can never be replicated by a resumed catch-up: the resumed
    changefeed stops at the GC boundary and the watermark keeps permanent
    downstream holes. ``replicated_through`` is the newest commit time the
    sink already applied (the pinned checkpoint value while stalled).

    When the operator raised the retention at ``secured_at``, a retention
    raise preempts future deletions but never restores deleted history: call
    this function twice - once with the baseline life at ``now=secured_at``
    (what was lost before the raise) and once with the raised life at the
    final sampling (what the new retention still exposes) - and union the
    results for the honest permanent-hole set.
    """
    if pin_released_at is None:
        return ()
    return tuple(sorted(
        commit_time for commit_time in commit_times
        if commit_time > replicated_through and gc_eligible_from(
            commit_time, life_time_seconds, pin_released_at) <= now
    ))


def retention_secured(life_time_seconds: float, now: float,
                      pinned_checkpoint_time: float) -> bool:
    """The retention covers the unreplicated checkpoint gap, so a resumed
    catch-up replays retained history instead of colliding with the GC
    boundary (the authorized ``tidb_gc_life_time`` raise, or an early resume
    while the baseline still covers the stall)."""
    return life_time_seconds >= now - pinned_checkpoint_time
