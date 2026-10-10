"""TiDB Persistent Scenario backend.

The package implements the ``backend/contracts.py`` provider protocols for
TiDB persistent scenarios: NodeSpec-driven topology expansion, docker compose
deployment, pymysql workload executors sharing the core ``TrustedLedger``,
the agent tool surface (execute_sql / query_metrics / manage_instance /
read_log), and the TiDB action-classifier vocabulary.

Assembly (who imports the provider and with which routing keys) belongs to the
integration package; this package only ships importable implementations with
documented construction shapes.
"""

from .topology import TIDB_NODE_ROLES, expand_topology
from .provider import TiDBEnvironmentProvider
from .environment import PersistentTiDBEnvironment
from .classifier import TiDBActionClassifier
from .changefeed import CdcChangefeedAdmin, TICDC_CLI
from .workloads import (
    TiDBJobQueueRunner,
    TiDBJobQueueStore,
    TiDBOltpTransactionPool,
    TiDBQueuedJob,
)
from .freshness import (
    CdcChangefeedCheckpointSampler,
    TiDBFreshnessRecorder,
    tso_lag_seconds,
    tso_to_unix_ms,
)
from .tidberrors import classify_job_outcome, classify_transaction_outcome

__all__ = [
    "TIDB_NODE_ROLES",
    "expand_topology",
    "TiDBEnvironmentProvider",
    "PersistentTiDBEnvironment",
    "TiDBActionClassifier",
    "CdcChangefeedAdmin",
    "TICDC_CLI",
    "TiDBJobQueueRunner",
    "TiDBJobQueueStore",
    "TiDBOltpTransactionPool",
    "TiDBQueuedJob",
    "CdcChangefeedCheckpointSampler",
    "TiDBFreshnessRecorder",
    "tso_lag_seconds",
    "tso_to_unix_ms",
    "classify_job_outcome",
    "classify_transaction_outcome",
]
