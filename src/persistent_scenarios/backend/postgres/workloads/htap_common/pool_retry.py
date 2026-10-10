"""Failed-plan re-drive for the instance OLTP pools.

The core pool reports identities whose latest attempt recorded a
non-committed outcome (statement timeout, connection error) through
``failed_plans()`` and guarantees a re-enqueued identity cannot be scheduled
twice. The driver owns the retry policy: the calendar loop re-drives failed
plans on its sweep cadence mid-run so transient failures can still complete
inside their original deadline, and the stop path performs one final sweep
after input stop and drain, where every remaining plan records its incomplete
terminal (INCOMPLETE_OUTSTANDING, or INCOMPLETE_TIMEOUT past the deadline)
without racing a worker.
"""

from __future__ import annotations


def retry_failed_plans(pool) -> int:
    plans = pool.failed_plans()
    for plan in plans:
        pool.submit_retry(plan)
    return len(plans)
