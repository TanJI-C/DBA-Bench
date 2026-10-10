from __future__ import annotations

import pytest

from src.scenarios.tidb.business_change.pitr_checkpoint_recovery import (
    TidbBusinessChangePitrCheckpointRecoveryScenario,
)
from src.scenarios.tidb.system_failure.ticdc_gc_safepoint import (
    TidbSystemFailureTiCdcGcSafepointScenario,
)
from src.scenarios.tidb.business_change.timezone_ddl_backpressure import (
    TidbBusinessChangeTimezoneDdlBackpressureScenario,
)
from src.scenarios.tidb.business_change.timezone_ddl_backpressure_frozen_history import (
    TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario,
)
from src.scenarios.tidb.health_check.empty_region_leader_skew_frozen_history import (
    TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario,
)
from src.scenarios.tidb.health_check.ticdc_replication_trend_frozen_history import (
    TidbHealthCheckTiCdcReplicationTrendFrozenHistoryScenario,
)
from src.scenarios.tidb.query_perf.set_autocommit_storm_frozen_history import (
    TidbQueryPerfSetAutocommitStormFrozenHistoryScenario,
)
from src.scenarios.tidb.system_failure.table_cache_lease_frozen_history import (
    TidbSystemFailureTableCacheLeaseFrozenHistoryScenario,
)
from src.scenarios.tidb.query_perf.optimistic_write_conflict_frozen_history import (
    TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario,
)
from src.scenarios.tidb.query_perf.statistics_drift_frozen_history import (
    TidbQueryPerfStatisticsDriftFrozenHistoryScenario,
)
from src.scenarios.tidb.resource_governance.br_slo_frozen_history import (
    TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario,
)
from src.scenarios.tidb.resource_governance.lightning_budget_frozen_history import (
    TidbResourceGovernanceLightningBudgetFrozenHistoryScenario,
)
from src.scenarios.tidb.resource_governance.ru_budget_calibration_frozen_history import (
    TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario,
)
from src.scenarios.tidb.system_failure.clustered_index_consistency import (
    TidbSystemFailureClusteredIndexConsistencyScenario,
)
from src.scenarios.tidb.system_failure.gc_mvcc_recovery import (
    TidbSystemFailureGcMvccRecoveryScenario,
)
from src.scenarios.tidb.system_failure.pd_total_metadata_loss_recovery import (
    TidbSystemFailurePdTotalMetadataLossRecoveryScenario,
)
from src.scenarios.tidb.system_failure.pending_offline import (
    TidbSystemFailurePendingOfflineScenario,
)


EXPANSIONS = (
    (
        TidbQueryPerfOptimisticWriteConflictFrozenHistoryScenario,
        "optimistic_write_conflict_hotspot_history_investigation",
        "probe_rounds",
    ),
    (
        TidbQueryPerfStatisticsDriftFrozenHistoryScenario,
        "statistics_drift_partition_history_investigation",
        "skew_rows",
    ),
    (
        TidbSystemFailurePendingOfflineScenario,
        "store_migration_pending_offline",
        "worker_count",
    ),
    (
        TidbSystemFailurePdTotalMetadataLossRecoveryScenario,
        "pd_metadata_recovery",
        "new_event_id",
    ),
    (
        TidbSystemFailureClusteredIndexConsistencyScenario,
        "clustered_index_consistency_recovery",
        "worker_count",
    ),
    (
        TidbSystemFailureGcMvccRecoveryScenario,
        "gc_mvcc_recovery",
        "worker_count",
    ),
    (
        TidbResourceGovernanceRuBudgetCalibrationFrozenHistoryScenario,
        "ru_budget_history_investigation",
        "orders_row_count",
    ),
    (
        TidbResourceGovernanceBrSloAdaptiveThrottlingFrozenHistoryScenario,
        "br_slo_history_investigation",
        "row_count",
    ),
    (
        TidbResourceGovernanceLightningBudgetFrozenHistoryScenario,
        "lightning_budget_history_investigation",
        "staging_table",
    ),
    (
        TidbHealthCheckEmptyRegionLeaderSkewFrozenHistoryScenario,
        "empty_region_leader_reduced_inventory_review",
        "risk_table_count",
    ),
    (
        TidbHealthCheckTiCdcReplicationTrendFrozenHistoryScenario,
        "ticdc_replication_moderate_sink_history_investigation",
        "source_batch_rows",
    ),
    (
        TidbBusinessChangePitrCheckpointRecoveryScenario,
        "resume_single_interruption_pitr_checkpoint",
        "worker_count",
    ),
    (
        TidbBusinessChangeTimezoneDdlBackpressureScenario,
        "dr_cutover_timezone_ddl_reduced_backpressure",
        "post_fault_rows",
    ),
    (
        TidbSystemFailureTiCdcGcSafepointScenario,
        "ticdc_gc_safepoint_reduced_oom_burst",
        "oom_burst_rows",
    ),
    (
        TidbBusinessChangeTimezoneDdlBackpressureFrozenHistoryScenario,
        "timezone_ddl_backpressure_reduced_history_investigation",
        "ddl_delay_seconds",
    ),
    (
        TidbSystemFailureTableCacheLeaseFrozenHistoryScenario,
        "table_cache_lease_narrow_catalog_investigation",
        "catalog_row_count",
    ),
    (
        TidbQueryPerfSetAutocommitStormFrozenHistoryScenario,
        "set_autocommit_focused_cohort_history_investigation",
        "worker_count",
    ),
)


def _variant_value(case, key: str):
    if key == "worker_count":
        return case.background_workload.worker_count
    return getattr(case, key)


@pytest.mark.parametrize(("scenario_type", "case_id", "changed_key"), EXPANSIONS)
def test_expanded_case_has_independent_identity_and_real_configuration_variant(
    scenario_type,
    case_id: str,
    changed_key: str,
) -> None:
    scenario = scenario_type()
    original, expanded = scenario.cases

    assert (original.case_no, expanded.case_no) == (0, 1)
    assert expanded.case_id == case_id
    assert expanded.evaluator.scenario_id == scenario.scenario_id
    assert expanded.evaluator.case_id == expanded.case_id
    assert expanded.evaluator is not original.evaluator
    assert _variant_value(expanded, changed_key) != _variant_value(original, changed_key)

    plans = scenario.build_fault_plan(expanded)
    assert len(plans) == 1
    if changed_key != "worker_count":
        assert plans[0].config[changed_key] == getattr(expanded, changed_key)


def test_all_expanded_case_ids_are_unique() -> None:
    case_ids = [scenario_type().cases[1].case_id for scenario_type, _case_id, _key in EXPANSIONS]
    assert len(case_ids) == len(set(case_ids))
