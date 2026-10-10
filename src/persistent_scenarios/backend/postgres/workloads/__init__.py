"""Shared PostgreSQL workload execution and ledger wiring.

These modules carry only the mechanics the five production instances need:
OLTP logical-transaction execution, job-queue execution, watermark sampling
and PostgreSQL error classification. Instance business SQL, queue tables and
capability implementations live in the instance packages
(`oltp_core/` substrate plus `business_priority/` and `online_change/`
mechanisms).
"""

from .olap import JobControl, JobQueueRunner, JobQueueStore, QueuedJob
from .oltp import LogicalTransactionPlan, OltpTransactionPool
from .pgerrors import (
    WorkloadConnectionFailure,
    classify_job_outcome,
    classify_transaction_outcome,
)
from .watermark import FreshnessRecorder

__all__ = (
    "FreshnessRecorder",
    "JobControl",
    "JobQueueRunner",
    "JobQueueStore",
    "LogicalTransactionPlan",
    "OltpTransactionPool",
    "QueuedJob",
    "WorkloadConnectionFailure",
    "classify_job_outcome",
    "classify_transaction_outcome",
)
