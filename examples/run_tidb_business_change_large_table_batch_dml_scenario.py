import argparse
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.tidb import TidbBusinessChangeLargeTableBatchDmlScenario
from src.execution.tidb_runtime import tidb_runtime
from src.execution.deployments.tidb import TiDBDockerDeployment
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


def _target_update_sql(case, wave_id: int, lower: int, upper: int) -> str:
    return (
        f"UPDATE {case.source_db}.{case.table} AS t "
        f"JOIN {case.control_db}.{case.stage_table} AS s "
        f"ON s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
        f"AND s.wave_id={wave_id} "
        f"AND s.event_id=t.{case.pk_column} "
        f"SET t.{case.target_column}=s.expected_risk_bucket, t.version=s.expected_version "
        f"WHERE t.{case.pk_column} > {lower} AND t.{case.pk_column} <= {upper}"
    )


def _wave_ranges(case, wave_id: int, *, first_batch_uses_initial_limit: bool):
    if wave_id == case.canary_wave_id:
        lower = 0
        limit = case.canary_row_count * 2
    elif wave_id == case.bulk_wave_id:
        lower = case.canary_row_count * 2
        limit = case.approved_row_count * 2
    else:
        raise ValueError(f"unknown BC04 wave_id={wave_id}")
    first = first_batch_uses_initial_limit
    while lower < limit:
        batch_limit = case.initial_batch_rows if first else case.continuation_batch_rows
        upper = min(lower + batch_limit * 2, limit)
        yield lower, upper, (upper - lower) // 2
        lower = upper
        first = False


def _batch_record_actions(case, wave_id: int, lower: int, upper: int, rows_in_batch: int, batch_count: int, processed_rows: int):
    return [
        {
            "api": "execute_sql",
            "args": {"sql_query": _target_update_sql(case, wave_id, lower, upper)},
        },
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"INSERT INTO {case.control_db}.{case.audit_table} "
                    "(job_id, wave_id, first_event_id, last_event_id, rows_changed, batch_seconds, "
                    "frontend_p95_ms, action, created_at) "
                    f"VALUES ('{case.job_id}', {wave_id}, {lower + 2}, {upper}, {rows_in_batch}, "
                    "0.320, 680.0, 'UPDATE_BATCH', CURRENT_TIMESTAMP(6))"
                )
            },
        },
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"UPDATE {case.control_db}.{case.job_table} SET "
                    f"status='running', last_event_id={upper}, processed_rows={processed_rows}, "
                    "index_state='pending', updated_at=CURRENT_TIMESTAMP(6) "
                    f"WHERE job_id='{case.job_id}'"
                )
            },
        },
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"UPDATE {case.control_db}.{case.checkpoint_table} SET "
                    f"last_event_id={upper}, processed_rows={processed_rows}, batch_count={batch_count}, "
                    "checkpoint_state='running', updated_at=CURRENT_TIMESTAMP(6) "
                    f"WHERE job_id='{case.job_id}'"
                )
            },
        },
    ]


def _batch_actions(case):
    actions = []
    processed_rows = 0
    batch_count = 0
    bulk_review_last_event_id = (case.canary_row_count + case.bulk_review_row_count) * 2
    for wave_id, first_batch_uses_initial_limit in (
        (case.canary_wave_id, True),
        (case.bulk_wave_id, False),
    ):
        for lower, upper, rows_in_batch in _wave_ranges(
            case,
            wave_id,
            first_batch_uses_initial_limit=first_batch_uses_initial_limit,
        ):
            batch_count += 1
            processed_rows += rows_in_batch
            actions.extend(_batch_record_actions(case, wave_id, lower, upper, rows_in_batch, batch_count, processed_rows))
            if wave_id == case.canary_wave_id and upper == case.canary_row_count * 2:
                actions.extend(
                    [
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT job_id, completed_batches, last_event_id, processed_rows, max_next_rows, "
                                    f"feedback_phase, phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, "
                                    f"bulk_review_gate_state "
                                    f"FROM {case.control_db}.{case.feedback_view} WHERE job_id='{case.job_id}'"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, s.expected_version, "
                                    f"s.expected_risk_bucket))), 0) "
                                    f"FROM {case.source_db}.{case.table} t JOIN {case.control_db}.{case.stage_table} s "
                                    f"ON s.event_id=t.event_id WHERE s.release_id='{case.release_id}' "
                                    f"AND s.scope_state='{case.required_scope}' AND s.wave_id={case.canary_wave_id} "
                                    "AND t.risk_bucket=s.expected_risk_bucket AND t.version=s.expected_version"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, t.version, "
                                    f"COALESCE(t.risk_bucket, '')))), 0) "
                                    f"FROM {case.source_db}.{case.table} t JOIN {case.control_db}.{case.stage_table} s "
                                    f"ON s.event_id=t.event_id WHERE s.release_id='{case.release_id}' "
                                    f"AND s.scope_state='{case.required_scope}' AND s.wave_id={case.bulk_wave_id}"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COALESCE(MAX(frontend_p95_ms), 0) FROM {case.control_db}.{case.audit_table} "
                                    f"WHERE job_id='{case.job_id}' AND wave_id={case.canary_wave_id}"
                                )
                            },
                        },
                        {
                            "api": "query_metrics",
                            "args": {"metric_type": "query_latency"},
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"INSERT INTO {case.control_db}.{case.gate_table} "
                                    "(job_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
                                    "remaining_apply_crc, frontend_p95_ms, decision_code, created_at) "
                                    f"SELECT '{case.job_id}', c.canary_wave_id, canary_state.verified_rows, "
                                    f"canary_state.verified_crc, bulk_state.remaining_rows, bulk_state.remaining_crc, "
                                    "p95.frontend_p95_ms, 1, CURRENT_TIMESTAMP(6) "
                                    f"FROM {case.control_db}.{case.contract_table} c "
                                    "CROSS JOIN ("
                                    f"SELECT COUNT(*) AS verified_rows, COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, s.expected_version, "
                                    f"s.expected_risk_bucket))), 0) AS verified_crc FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.canary_wave_id} AND t.risk_bucket=s.expected_risk_bucket "
                                    "AND t.version=s.expected_version"
                                    ") canary_state CROSS JOIN ("
                                    f"SELECT COUNT(*) AS remaining_rows, COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, t.version, "
                                    f"COALESCE(t.risk_bucket, '')))), 0) AS remaining_crc FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.bulk_wave_id}"
                                    ") bulk_state CROSS JOIN ("
                                    f"SELECT COALESCE(MAX(frontend_p95_ms), 0) AS frontend_p95_ms FROM {case.control_db}.{case.audit_table} "
                                    f"WHERE job_id='{case.job_id}' AND wave_id={case.canary_wave_id}"
                                    ") p95 "
                                    f"WHERE c.contract_id='{case.contract_id}' "
                                    "AND canary_state.verified_rows=c.canary_expected_rows "
                                    "AND canary_state.verified_crc=c.canary_expected_crc "
                                    "AND bulk_state.remaining_rows=c.bulk_expected_rows "
                                    "AND bulk_state.remaining_crc=c.bulk_baseline_crc "
                                    "AND p95.frontend_p95_ms <= c.frontend_slo_p95_ms"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, bulk_review_gate_state "
                                    f"FROM {case.control_db}.{case.feedback_view} WHERE job_id='{case.job_id}'"
                                )
                            },
                        },
                    ]
                )
            if wave_id == case.bulk_wave_id and upper == bulk_review_last_event_id:
                actions.extend(
                    [
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, "
                                    f"bulk_review_gate_state FROM {case.control_db}.{case.feedback_view} "
                                    f"WHERE job_id='{case.job_id}'"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, s.expected_version, "
                                    f"s.expected_risk_bucket))), 0) FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.bulk_wave_id} AND s.event_id <= {bulk_review_last_event_id} "
                                    "AND t.risk_bucket=s.expected_risk_bucket AND t.version=s.expected_version"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, t.version, "
                                    f"COALESCE(t.risk_bucket, '')))), 0) FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.bulk_wave_id} AND s.event_id > {bulk_review_last_event_id}"
                                )
                            },
                        },
                        {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT COALESCE(MAX(frontend_p95_ms), 0) FROM {case.control_db}.{case.audit_table} "
                                    f"WHERE job_id='{case.job_id}' AND wave_id={case.bulk_wave_id} "
                                    f"AND last_event_id <= {bulk_review_last_event_id}"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"INSERT INTO {case.control_db}.{case.gate_table} "
                                    "(job_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
                                    "remaining_apply_crc, frontend_p95_ms, decision_code, created_at) "
                                    f"SELECT '{case.job_id}', c.bulk_wave_id, review_state.verified_rows, "
                                    f"review_state.verified_crc, remaining_state.remaining_rows, remaining_state.remaining_crc, "
                                    "p95.frontend_p95_ms, 1, CURRENT_TIMESTAMP(6) "
                                    f"FROM {case.control_db}.{case.contract_table} c "
                                    "CROSS JOIN ("
                                    f"SELECT COUNT(*) AS verified_rows, COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, s.expected_version, "
                                    f"s.expected_risk_bucket))), 0) AS verified_crc FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.bulk_wave_id} AND s.event_id <= {bulk_review_last_event_id} "
                                    f"AND t.risk_bucket=s.expected_risk_bucket AND t.version=s.expected_version"
                                    ") review_state CROSS JOIN ("
                                    f"SELECT COUNT(*) AS remaining_rows, COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, "
                                    f"t.status, t.amount_cents, t.event_time, t.payload, t.version, "
                                    f"COALESCE(t.risk_bucket, '')))), 0) AS remaining_crc FROM {case.source_db}.{case.table} t "
                                    f"JOIN {case.control_db}.{case.stage_table} s ON s.event_id=t.event_id "
                                    f"WHERE s.release_id='{case.release_id}' AND s.scope_state='{case.required_scope}' "
                                    f"AND s.wave_id={case.bulk_wave_id} AND s.event_id > {bulk_review_last_event_id}"
                                    ") remaining_state CROSS JOIN ("
                                    f"SELECT COALESCE(MAX(frontend_p95_ms), 0) AS frontend_p95_ms FROM {case.control_db}.{case.audit_table} "
                                    f"WHERE job_id='{case.job_id}' AND wave_id={case.bulk_wave_id} "
                                    f"AND last_event_id <= {bulk_review_last_event_id}"
                                    ") p95 "
                                    f"WHERE c.contract_id='{case.contract_id}' "
                                    "AND review_state.verified_rows=c.bulk_review_rows "
                                    "AND review_state.verified_crc=c.bulk_review_expected_crc "
                                    "AND remaining_state.remaining_rows=c.bulk_expected_rows-c.bulk_review_rows "
                                    "AND remaining_state.remaining_crc=c.bulk_review_remaining_crc "
                                    "AND p95.frontend_p95_ms <= c.frontend_slo_p95_ms"
                                )
                            },
                        },
                        {
                            "api": "execute_sql",
                            "args": {
                                "sql_query": (
                                    f"SELECT phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, bulk_review_gate_state "
                                    f"FROM {case.control_db}.{case.feedback_view} WHERE job_id='{case.job_id}'"
                                )
                            },
                        },
                    ]
                )
    return actions


def _mock_responses(case):
    contract_sql = (
        f"SELECT release_id, required_scope, expected_rows, expected_sum_cents, expected_crc, out_of_scope_rows, "
        f"out_of_scope_crc, first_event_id, last_event_id, index_columns, max_batch_seconds, "
        f"frontend_slo_p95_ms, immutable_marker, initial_batch_rows, continuation_batch_rows, feedback_view, "
        f"canary_wave_id, canary_expected_rows, canary_expected_crc, bulk_wave_id, bulk_expected_rows, "
        f"bulk_baseline_crc, gate_table, bulk_review_rows, bulk_review_last_event_id, "
        f"bulk_review_expected_crc, bulk_review_remaining_crc "
        f"FROM {case.control_db}.{case.contract_table} "
        f"WHERE contract_id='{case.contract_id}'"
    )
    stage_sql = (
        f"SELECT release_id, scope_state, wave_id, COUNT(*), MIN(event_id), MAX(event_id) "
        f"FROM {case.control_db}.{case.stage_table} "
        "GROUP BY release_id, scope_state, wave_id ORDER BY release_id, scope_state, wave_id"
    )
    job_sql = (
        f"SELECT job_id, release_id, status, last_event_id, processed_rows, batch_size, index_name, index_state "
        f"FROM {case.control_db}.{case.job_table} WHERE job_id='{case.job_id}'"
    )
    feedback_sql = (
        f"SELECT job_id, completed_batches, last_event_id, processed_rows, max_next_rows, feedback_phase, "
        f"phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, bulk_review_gate_state "
        f"FROM {case.control_db}.{case.feedback_view} WHERE job_id='{case.job_id}'"
    )
    checksum_sql = (
        f"SELECT COUNT(*), COALESCE(SUM(t.amount_cents), 0), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', "
        f"t.event_id, t.tenant_id, t.status, t.amount_cents, t.event_time, t.payload, "
        f"s.expected_version, s.expected_risk_bucket))), 0), MAX(t.event_id) "
        f"FROM {case.source_db}.{case.table} t JOIN {case.control_db}.{case.stage_table} s "
        f"ON s.event_id=t.event_id WHERE s.release_id='{case.release_id}' "
        f"AND s.scope_state='{case.required_scope}' "
        "AND t.risk_bucket=s.expected_risk_bucket AND t.version=s.expected_version"
    )
    scope_sql = (
        f"SELECT COUNT(*), COALESCE(BIT_XOR(CRC32(CONCAT_WS('|', t.event_id, t.tenant_id, t.status, "
        f"t.amount_cents, t.event_time, t.payload, t.version, COALESCE(t.risk_bucket, '')))), 0), "
        f"COALESCE(SUM(t.amount_cents), 0) FROM {case.source_db}.{case.table} t WHERE NOT EXISTS "
        f"(SELECT 1 FROM {case.control_db}.{case.stage_table} s WHERE s.release_id='{case.release_id}' "
        f"AND s.scope_state='{case.required_scope}' AND s.event_id=t.event_id)"
    )
    index_sql = (
        "SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) "
        f"FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA='{case.source_db}' "
        f"AND TABLE_NAME='{case.table}' GROUP BY INDEX_NAME"
    )
    final_job_sql = (
        f"SELECT j.status, j.last_event_id, j.processed_rows, j.index_state, c.last_event_id, "
        f"c.processed_rows, c.batch_count, c.checkpoint_state FROM {case.control_db}.{case.job_table} j "
        f"JOIN {case.control_db}.{case.checkpoint_table} c ON c.job_id=j.job_id "
        f"WHERE j.job_id='{case.job_id}'"
    )
    inspection_actions = [
        {
            "api": "execute_sql",
            "args": {"sql_query": contract_sql},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": stage_sql},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": job_sql},
        },
        {
            "api": "execute_sql",
            "args": {"sql_query": feedback_sql},
        },
        {
            "api": "execute_sql",
            "args": {
                "sql_query": (
                    f"SELECT gate_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
                    f"remaining_apply_crc, frontend_p95_ms, decision_code, created_at FROM {case.control_db}.{case.gate_table} "
                    f"WHERE job_id='{case.job_id}' ORDER BY gate_id"
                )
            },
        },
        {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
        {"api": "query_metrics", "args": {"metric_type": "query_latency"}},
    ]
    batch_actions = _batch_actions(case)
    final_actions = [
            {"api": "execute_sql", "args": {"sql_query": checksum_sql}},
            {"api": "execute_sql", "args": {"sql_query": scope_sql}},
            {
                "api": "execute_sql",
                "args": {"sql_query": f"ADMIN CHECKSUM TABLE {case.source_db}.{case.table}"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"ALTER TABLE {case.source_db}.{case.table} ADD INDEX {case.allowed_index_name} "
                        f"({', '.join(case.allowed_index_columns)})"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"UPDATE {case.control_db}.{case.job_table} SET status='completed', index_state='ready', "
                        f"updated_at=CURRENT_TIMESTAMP(6) WHERE job_id='{case.job_id}'"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"UPDATE {case.control_db}.{case.checkpoint_table} SET checkpoint_state='complete', "
                        f"updated_at=CURRENT_TIMESTAMP(6) WHERE job_id='{case.job_id}'"
                    )
                },
            },
            {"api": "execute_sql", "args": {"sql_query": final_job_sql}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"SELECT wave_id, COUNT(*), COALESCE(SUM(rows_changed), 0), MIN(first_event_id), MAX(last_event_id) "
                        f"FROM {case.control_db}.{case.audit_table} WHERE job_id='{case.job_id}' "
                        "GROUP BY wave_id ORDER BY wave_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"SELECT gate_id, wave_id, verified_rows, verified_crc, remaining_apply_rows, "
                        f"remaining_apply_crc, frontend_p95_ms, decision_code, created_at FROM {case.control_db}.{case.gate_table} "
                        f"WHERE job_id='{case.job_id}' ORDER BY gate_id"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"SELECT phase_id, next_wave_id, gate_required, gate_state, canary_rows, bulk_rows, bulk_review_gate_state "
                        f"FROM {case.control_db}.{case.feedback_view} WHERE job_id='{case.job_id}'"
                    )
                },
            },
            {"api": "query_metrics", "args": {"metric_type": "active_connections"}},
            {"api": "query_metrics", "args": {"metric_type": "qps"}},
            {
                "api": "submit",
                "args": {"report": case.reference_report},
            },
        ]
    return [
        {
            "thinking": "Inspect the immutable release contract, stage bounds, job state, and foreground baseline before changing the live table.",
            "actions": inspection_actions,
        },
        {
            "thinking": "Execute the initial bounded batch, read the committed feedback transition, and use its continuation allowance for the remaining batches.",
            "actions": batch_actions,
        },
        {
            "thinking": "Verify checksum and scope before the online covering index, then close the checkpoint and validate SLO and logs.",
            "actions": final_actions,
        },
    ]


def main() -> None:
    scenario = TidbBusinessChangeLargeTableBatchDmlScenario()
    parser = argparse.ArgumentParser(description="Run the TiDB BC04 large-table batch DML/DDL scenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--port", type=int, default=21440)
    parser.add_argument("--container-name", default="tidb-business-change-bc04-large-table")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off"), default="off")
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    parser.add_argument("--warmup-seconds", type=float)
    parser.add_argument(
        "--topology",
        choices=("case", "single"),
        default="single",
        help="Use a 1/1/1 smoke topology by default; pass case for the formal 3/3/2 topology.",
    )
    args = parser.parse_args()
    if args.mode == "llm" and not args.model:
        parser.error("--model is required when --mode=llm")
    if (args.storage_key is None) != (args.storage_root is None):
        parser.error("--storage-key and --storage-root must be supplied together")

    case = scenario.get_case(args.case)
    if args.topology == "single":
        case = replace(
            case,
            runtime=tidb_runtime(
                release=case.runtime.release,
                pd_count=1,
                tikv_count=1,
                tidb_count=1,
                sql_timeout_seconds=case.runtime.sql_timeout_seconds,
            ),
        )
    env = TiDBEnv(
        deployment=TiDBDockerDeployment(
            run_id=args.container_name.removeprefix("aiopsbench-"),
            port_base=args.port,
            storage_key=args.storage_key,
            storage_root=args.storage_root,
        )
    )
    if args.mode == "mock":
        agent = MockLLMAgent(
            url="mock",
            api_key="mock",
            system_prompt="You are a TiDB DBA performing a controlled live business change.",
            use_native_tools=False,
        )
        agent.set_mock_responses(_mock_responses(case))
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(
            fault_snapshot_mode=args.fault_snapshot_mode,
            runtime_warmup_seconds=args.warmup_seconds,
        ),
    ).run()
    print(f"Final result: {result}")
    if args.mode == "mock":
        observed = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
        if observed != (None, True, True):
            raise AssertionError(f"BC04 mock path must pass (None, True, True), observed={observed!r}")


if __name__ == "__main__":
    main()
