import argparse
import json
import os
import signal
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.runtime.config import required_run_timeout_seconds
from src.agents.agent import LLMAgent, MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import EMPTY_REPORT
from src.scenarios.postgres import PgSystemFailurePageCorruptionScenario
from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig



HARD_TIMEOUT_SEC = 720


def _timeout_handler(signum, frame):
    print("\n[FATAL] Hard timeout reached. Forcing exit.")
    sys.exit(1)





_ORDER_DETAIL_VIEW_COLUMNS = (
    "order_id, warehouse_id, district_id, line_number, item_id, "
    "quantity, amount, payload, created_at"
)

# r4 reference diagnosis path: reproduce and split error classes, resolve the
# union view to both physical segments, attribute the second damage point,
# inventory the maintenance copies, and discriminate their content against the
# audit baseline and the readable production rows.
mock_diagnosis_responses = [
    {
        "thinking": (
            "订单明细部分请求失败：先复现读路径并分裂错误类别。live 视图全量读与键控读分别验证，"
            "history 审计路径复现超时，对比两类错误。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE order_id BETWEEN 1 AND 5;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '2s'; "
                        "SELECT count(*) FROM order_detail_history h "
                        "WHERE h.order_id BETWEEN 1 AND 8000 "
                        "AND (SELECT count(*) FROM order_line_audit_archive a "
                        "WHERE a.warehouse_id = h.warehouse_id "
                        "AND a.order_id BETWEEN 1 AND 3600) < 288;"
                    )
                },
            },
        ],
    },
    {
        "thinking": (
            "live 视图全量读报 invalid page（relfilenode 在错误里），键控读正常；history 审计是 statement timeout。"
            "解析视图定义确认读路径由哪些物理关系供数，再列 public 关系把 relfilenode 映射到关系，"
            "并用热段键控读与基表全量读对照损坏位置。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT dataset_scope, expected_row_count, expected_amount_sum, "
                        "expected_weighted_amount_sum FROM order_detail_audit_baseline;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT c.relname, c.relkind, c.relfilenode "
                        "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                        "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'v') "
                        "ORDER BY c.relname;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_line_audit "
                        "WHERE order_id BETWEEN 11001 AND 11005;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT count(*) FROM order_line_audit;",
                },
            },
        ],
    },
    {
        "thinking": (
            "视图由 live+archive 两段物理关系联合供数，错误 relfilenode 映射到 order_line_audit。"
            "archive 近邻也要独立体检：全量读、头部键控读、ctid 前后段定位，确认它自身是否受损、"
            "业务全量读路径是否跨两臂。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT count(*) FROM order_line_audit_archive;"},
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) FROM order_line_audit_archive "
                        "WHERE order_id BETWEEN 1 AND 50;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) FROM order_line_audit_archive "
                        "WHERE ctid >= '(1100,0)';"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) FROM order_line_audit_archive "
                        "WHERE ctid < '(1100,0)';"
                    )
                },
            },
        ],
    },
    {
        "thinking": (
            "archive 冷段自身也有一个坏页，业务全量读跨两臂，修复范围必须覆盖两段。"
            "恢复源盘点：三份维护副本的行数与金额合计 + 审计基线台账，并确认 checksums 状态。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT 'snapshot_0612' AS copy, count(*) AS rows, sum(amount) AS amount_sum "
                        "FROM order_line_audit_snapshot_0612 "
                        "UNION ALL SELECT 'snapshot_0701', count(*), sum(amount) "
                        "FROM order_line_audit_snapshot_0701 "
                        "UNION ALL SELECT 'snapshot_0705', count(*), sum(amount) "
                        "FROM order_line_audit_snapshot_0705;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": "SELECT dataset_scope, expected_row_count, expected_amount_sum FROM order_detail_audit_baseline;"
                },
            },
            {
                "api": "execute_sql",
                "args": {"sql_query": "SHOW data_checksums;"},
            },
        ],
    },
    {
        "thinking": (
            "0701 只有 950 行（缺冷段）；0612 全量。0705 行数比基线少 50：确认副本新鲜度"
            "（生产尾部在快照之后写入），并做内容甄别——互拍找 drift，plain sum 一致时改用台账加权口径。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT count(*) AS drifted_rows "
                        "FROM order_line_audit_snapshot_0705 a "
                        "JOIN order_line_audit_snapshot_0612 b USING (order_id) "
                        "WHERE a.amount <> b.amount;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT "
                        "(SELECT amount FROM order_line_audit WHERE order_id = 11500) AS live_amount, "
                        "(SELECT amount FROM order_line_audit_snapshot_0612 WHERE order_id = 11500) AS snapshot_0612_amount, "
                        "(SELECT amount FROM order_line_audit_snapshot_0705 WHERE order_id = 11500) AS snapshot_0705_amount;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT 'snapshot_0612' AS copy, sum(amount * order_id) AS weighted_sum "
                        "FROM order_line_audit_snapshot_0612 "
                        "UNION ALL SELECT 'snapshot_0705', sum(amount * order_id) "
                        "FROM order_line_audit_snapshot_0705;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT (SELECT max(order_id) FROM order_line_audit) AS live_max, "
                        "(SELECT max(order_id) FROM order_line_audit_snapshot_0705) AS snapshot_0705_max;"
                    )
                },
            },
        ],
    },
]

# Reference repair: rebuild both segments from the verified clean snapshot,
# merge the readable production tail that postdates the snapshot, and repoint
# the union read path at the rebuilt copies.
mock_reference_repair_responses = [
    {
        "thinking": (
            "0705 内容与基线三口径一致但落后生产 50 行（11951..12000 在快照之后写入、位于可读尾部页）。"
            "archive 段与 live 段坏区行从 0705 补，生产尾部行从生产可读区并入，两源混合重建后重指向读路径。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_live_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0705 WHERE order_id >= 11001;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "INSERT INTO order_line_audit_live_clean "
                        "SELECT * FROM order_line_audit WHERE order_id > 11950;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_archive_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0705 WHERE order_id <= 11000;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE INDEX order_line_audit_live_clean_order_id_idx "
                        "ON order_line_audit_live_clean(order_id);"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE INDEX order_line_audit_archive_clean_order_id_idx "
                        "ON order_line_audit_archive_clean(order_id);"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_live AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_live_clean "
                        f"UNION ALL SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_archive_clean;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_history AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_archive_clean;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "恢复后校验：业务读路径探针成功，行数与金额校验和都对上审计基线。",
        "actions": [
            {"api": "read_log", "args": {"log_type": "pg_log", "lines": 80}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT CASE WHEN (SELECT count(*) FROM order_detail_live) = "
                        "(SELECT expected_row_count FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS rowcount_ok, "
                        "CASE WHEN (SELECT sum(amount) FROM order_detail_live) = "
                        "(SELECT expected_amount_sum FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS checksum_ok, "
                        "CASE WHEN (SELECT sum(amount * order_id) FROM order_detail_live) = "
                        "(SELECT expected_weighted_amount_sum FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS weighted_ok;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": "reference"},
            }
        ],
    },
]

# Equivalent repair: serve the full audited dataset from a single rebuilt
# relation merged from the snapshot and the production tail; a materially
# different service shape with the same business result.
mock_equivalent_repair_responses = [
    {
        "thinking": (
            "0705 内容与基线一致但缺生产尾部 50 行。用它重建单一全量关系并并入生产尾部，"
            "把业务读路径重指向该关系（等价服务形态），保留受损关系供事后分析。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_detail_audit_restored AS "
                        "SELECT * FROM order_line_audit_snapshot_0705;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "INSERT INTO order_detail_audit_restored "
                        "SELECT * FROM order_line_audit WHERE order_id > 11950;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_live AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_detail_audit_restored;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "恢复后校验：业务读路径探针成功，行数与金额校验和都对上审计基线。",
        "actions": [
            {"api": "read_log", "args": {"log_type": "pg_log", "lines": 80}},
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT CASE WHEN (SELECT count(*) FROM order_detail_live) = "
                        "(SELECT expected_row_count FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS rowcount_ok, "
                        "CASE WHEN (SELECT sum(amount) FROM order_detail_live) = "
                        "(SELECT expected_amount_sum FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS checksum_ok, "
                        "CASE WHEN (SELECT sum(amount * order_id) FROM order_detail_live) = "
                        "(SELECT expected_weighted_amount_sum FROM order_detail_audit_baseline) THEN 1 ELSE 0 END AS weighted_ok;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": "reference"},
            }
        ],
    },
]

# Wrong-source repair: restore from the stale full copy. The probe recovers but
# the amount checksum silently drifts, so the outcome must fail.
mock_wrong_source_repair_responses = [
    {
        "thinking": (
            "选 snapshot_0612 作为恢复源（行数看起来完整），重建两段并重指向。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_live_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0612 WHERE order_id >= 11001;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_archive_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0612 WHERE order_id <= 11000;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_live AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_live_clean "
                        f"UNION ALL SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_archive_clean;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "探针已经能读，提交恢复报告。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": "reference"},
            }
        ],
    },
]

# Partial repair: only rebuild the live segment and keep the damaged archive in
# the union; the read-path probe still fails on the cold page.
mock_partial_repair_responses = [
    {
        "thinking": (
            "热段基表坏了，从 0705 热段重建 live 臂即可，archive 臂保持原样。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_live_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0705 WHERE order_id >= 11001;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_live AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_live_clean "
                        f"UNION ALL SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_archive;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "验证业务读路径并提交。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": "reference"},
            }
        ],
    },
]

# Stale-pure repair: rebuild both segments purely from the lagging snapshot;
# the probe recovers but the newest tail orders are missing, so the row count
# baseline check must fail the outcome.
mock_stale_pure_repair_responses = [
    {
        "thinking": (
            "0705 通过全部内容校验，直接从它重建两段并重指向。"
        ),
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_live_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0705 WHERE order_id >= 11001;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "CREATE TABLE order_line_audit_archive_clean AS "
                        "SELECT * FROM order_line_audit_snapshot_0705 WHERE order_id <= 11000;"
                    )
                },
            },
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        f"CREATE OR REPLACE VIEW order_detail_live AS SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_live_clean "
                        f"UNION ALL SELECT {_ORDER_DETAIL_VIEW_COLUMNS} "
                        "FROM order_line_audit_archive_clean;"
                    )
                },
            },
        ],
    },
    {
        "thinking": "探针恢复即认为完成，提交报告。",
        "actions": [
            {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SET statement_timeout = '5s'; "
                        "SELECT count(*) FROM order_detail_live "
                        "WHERE warehouse_id BETWEEN 1 AND 10;"
                    )
                },
            },
            {
                "api": "submit",
                "args": {"report": "reference"},
            }
        ],
    },
]

# Case-0 mock flows: each flow shares the reference diagnosis path and differs
# in the restoration decision. Expectations are enforced in main().
CASE0_MOCK_FLOWS = {
    "reference": mock_diagnosis_responses + mock_reference_repair_responses,
    "equivalent": mock_diagnosis_responses + mock_equivalent_repair_responses,
    "wrong_source": mock_diagnosis_responses + mock_wrong_source_repair_responses,
    "stale_pure": mock_diagnosis_responses + mock_stale_pure_repair_responses,
    "partial": mock_diagnosis_responses + mock_partial_repair_responses,
}

CASE0_FLOW_EXPECTATIONS = {
    "reference": (True, True, True),
    "equivalent": (True, True, True),
    "wrong_source": (True, False, True),
    "stale_pure": (True, False, True),
    "partial": (True, False, True),
}


mock_responses_zero = [
    {
        "thinking": "没有排查，直接提交。",
        "actions": [{"api": "submit", "args": {"report": EMPTY_REPORT}}],
    }
]


def _resolve_reference_reports(responses, case):
    resolved = []
    for response in responses:
        entry = {"thinking": response["thinking"]}
        if "actions" in response:
            entry["actions"] = [
                _resolve_submit_report(action, case) for action in response["actions"]
            ]
        else:
            entry["action"] = _resolve_submit_report(response["action"], case)
        resolved.append(entry)
    return resolved


def _resolve_submit_report(action, case):
    if action.get("api") == "submit" and action.get("args", {}).get("report") == "reference":
        return {**action, "args": {**action["args"], "report": case.reference_report}}
    return action


def build_mock_responses(case, flow: str) -> list:
    if case.case_id != "order_line_audit_page_corruption":
        return [
        {
            "thinking": "Reproduce the one failing relation and compare the catalog health probe.",
            "actions": [
                {
                    "api": "execute_sql",
                    "args": {
                        "sql_query": (
                            "SET statement_timeout = '5s'; "
                            f"{case.check_query}"
                        )
                    },
                },
                {"api": "query_metrics", "args": {"metric_type": "workload_activity"}},
            ],
        },
        {
            "thinking": (
                "The checksum failure is physical; inspect its block evidence and relation "
                "metadata without changing the damaged object."
            ),
            "action": {
                "api": "execute_sql",
                "args": {
                    "sql_query": (
                        "SELECT pg_relation_filepath('invoice_page_audit'::regclass), "
                        "pg_relation_size('invoice_page_audit'::regclass), "
                        "relfilenode, relpages FROM pg_class "
                        "WHERE oid = 'invoice_page_audit'::regclass;"
                    )
                },
            },
        },
        {
            "thinking": (
                "Recovery ledger and snapshot business values identify the verified copy; "
                "preserve the corrupt relation as evidence and perform a controlled relation "
                "swap from that copy; do not rewrite the damaged page."
            ),
            "actions": [
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT c.relname, c.relkind FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'i') ORDER BY 1;"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT m.service_relation, m.original_relfilenode, m.expected_amount, "
                    "t.relname FROM page_corruption_recovery_manifest m "
                    "LEFT JOIN pg_class t ON t.relfilenode = m.original_relfilenode;"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT 'snapshot_0612' AS snapshot, order_id, amount "
                    f"FROM {case.recovery_snapshot_name} WHERE order_id = 1 "
                    "UNION ALL "
                    "SELECT 'snapshot_0701', order_id, amount "
                    f"FROM {case.stale_snapshot_name} WHERE order_id = 1;"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "SELECT m.expected_amount, m.expected_amount_sum, "
                    f"(SELECT sum(amount) FROM {case.recovery_snapshot_name}) AS snapshot_0612_sum, "
                    f"(SELECT sum(amount) FROM {case.stale_snapshot_name}) AS snapshot_0701_sum "
                    "FROM page_corruption_recovery_manifest m "
                    f"WHERE m.service_relation = '{case.table}';"
                )}},
                {"api": "execute_sql", "args": {"sql_query": (
                    "ALTER TABLE invoice_page_audit RENAME TO invoice_page_audit_corrupt; "
                    "ALTER INDEX invoice_page_audit_order_id_idx RENAME TO invoice_page_audit_corrupt_order_id_idx; "
                    f"ALTER TABLE {case.recovery_snapshot_name} RENAME TO invoice_page_audit;"
                )}},
                {"api": "execute_sql", "args": {"sql_query": "CREATE INDEX invoice_page_audit_order_id_idx ON invoice_page_audit(order_id);"}},
                {"api": "submit", "args": {"report": case.reference_report}},
            ],
        },
    ]
    return _resolve_reference_reports(CASE0_MOCK_FLOWS[flow], case)


def _build_env(case, port: int, container_name: str = None, image_name: str = None) -> PGEnv:
    # 仅覆盖容器名和端口，避免并行验证互相污染；checksums 由注入器离线启用。
    final_image = image_name or case.base_image_name
    deployment = PGDockerDeployment(
        container_name=container_name,
        port=port,
        image_name=final_image,
    )
    return PGEnv(
        deployment=deployment,
        port=port,
        allow_sampler_jitter=True,
        allow_sampler_reconnect=True,
    )























def run_mode(args, scenario, case, mode, container_name, run_config):
    override_image = None
    env = _build_env(case, args.port, container_name, image_name=override_image)
    env.deployment.container_name = container_name
    if override_image:
        env.deployment.image_name = override_image
    if mode == "mock":
        agent = MockLLMAgent(url='mock', api_key='mock', system_prompt='You are a DBA agent.', use_native_tools=False)
        agent.set_mock_responses(build_mock_responses(case, args.flow))
    elif mode == "zero":
        agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
        agent.set_mock_responses([{"thinking": "Submit without diagnosis.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}}])
    else:
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    orchestrator = Orchestrator(env, scenario, case, agent, max_turns=args.max_turns, run_config=run_config)
    return orchestrator.run()


def main():
    scenario = PgSystemFailurePageCorruptionScenario()
    parser = argparse.ArgumentParser(description="Run PgSystemFailurePageCorruptionScenario.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=["mock", "zero", "llm", "all"], default="mock")
    parser.add_argument("--flow", choices=sorted(CASE0_MOCK_FLOWS), default="reference",
                        help="case-0 mock flow: reference/equivalent must pass, wrong_source/partial must fail the outcome")
    parser.add_argument("--port", type=int, default=15432)
    parser.add_argument("--container-name", default="aiopsbench-run-pg-system-failure-page-corruption-scenario")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=12)
    parser.add_argument("--fault-snapshot-mode", choices=["auto", "off", "save", "use"], default="auto")
    parser.add_argument("--fault-snapshot-name")
    args = parser.parse_args()
    run_config = OrchestratorRunConfig(
        fault_snapshot_mode=args.fault_snapshot_mode,
        fault_snapshot_name=args.fault_snapshot_name,
    )
    case = scenario.get_case(args.case)
    modes = ("mock", "zero", "llm") if args.mode == "all" else (args.mode,)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(required_run_timeout_seconds())
    try:
        for mode in modes:
            result = run_mode(args, scenario, case, mode, f"{args.container_name}-{mode}", run_config)
            print(f"[{mode}] DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}")
            if mode == "mock":
                if case.case_id == "order_line_audit_page_corruption":
                    actual = (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"])
                    assert actual == CASE0_FLOW_EXPECTATIONS[args.flow], json.dumps(result, ensure_ascii=False)
                else:
                    assert result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"], json.dumps(result, ensure_ascii=False)
            elif mode == "zero":
                assert not (result["DiagnosisPass"] and result["OutcomePass"] and result["SafePass"]), json.dumps(result, ensure_ascii=False)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
