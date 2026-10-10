import os
import sys
from contextlib import nullcontext
from unittest.mock import MagicMock

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.postgres.query_perf.heavy_offset_pagination import PgQueryPerfHeavyOffsetPaginationInjector


def test_recover_drops_account_rollup_index():
    injector = PgQueryPerfHeavyOffsetPaginationInjector()
    env = MagicMock()
    env.metrics_hidden.return_value = nullcontext()

    def execute_sql(sql):
        if sql == "SELECT count(*) FROM branch_order_line;":
            return {"status": "success", "result": [[900_001]]}
        return {"status": "success", "result": []}

    env.execute_sql.side_effect = execute_sql
    injector._activate_runtime = MagicMock()
    context = FaultLifecycleContext(
        run_id="test-run",
        scenario_id="pg_query_perf_heavy_offset_pagination",
        case_id="branch_order_deep_offset",
        case=object(),
        config={
            "table": "branch_order_line",
            "order_column": "bol_receipt_number",
            "offset_value": 900_000,
            "index_name": "idx_aiopsbench_bol_event_order",
            "fault_fingerprint_sql": "SELECT 1;",
        },
        env=env,
    )
    injector.install(context)
    env.execute_sql.reset_mock()

    injector.recover(context)

    env.execute_sql.assert_called_once_with(
        "DROP INDEX IF EXISTS idx_aiopsbench_bol_event_order; "
        "DROP INDEX IF EXISTS idx_aiopsbench_bol_account_rollup;"
    )
