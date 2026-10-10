import json
from unittest.mock import MagicMock

from src.scenarios.postgres.query_perf import PgQueryPerfMissingIndexScenario
from src.scenarios.postgres.query_perf.missing_index import PgQueryPerfMissingIndexInjector


def _success(rows=None):
    return json.dumps({"status": "success", "result": rows or []})


def _substring_case_config():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")
    return case, scenario.build_fault_plan(case)[0].config


def test_missing_index_injector_does_not_drop_plain_column_index():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")
    config = scenario.build_fault_plan(case)[0].config
    injector = PgQueryPerfMissingIndexInjector()
    env = MagicMock()
    env.execute_sql.return_value = _success([])

    injector._configure_from_config(config, env)
    injector._drop_target_expression_indexes()

    executed_sql = "\n".join(str(call.args[0]) for call in env.execute_sql.call_args_list)
    assert f"DROP INDEX IF EXISTS {case.index_name};" not in executed_sql
    assert f"DROP INDEX IF EXISTS {case.remediation_index_name};" in executed_sql


def test_missing_index_injector_creates_visible_plain_column_index_when_shadow_hides_original():
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.table = "customer"
    injector.column = "c_last_name"
    injector.visible_column_index_name = "idx_customer_last_visible"
    injector.env.execute_sql.return_value = _success([])

    injector._ensure_visible_column_index()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert "CREATE INDEX IF NOT EXISTS idx_customer_last_visible ON customer(c_last_name);" in executed_sql


def test_missing_index_injector_reuses_existing_visible_plain_column_index():
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.table = "customer"
    injector.column = "c_last_name"
    injector.visible_column_index_name = "idx_customer_last_visible"
    injector.env.execute_sql.return_value = _success([
        [
            "idx_customer_last",
            "CREATE INDEX idx_customer_last ON public.customer USING btree (c_last_name)",
        ]
    ])

    injector._ensure_visible_column_index()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert "CREATE INDEX IF NOT EXISTS idx_customer_last_visible" not in executed_sql


def test_substring_case_installs_neighbor_pattern_index_and_placeholder_batch_protection():
    case, config = _substring_case_config()
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = _success([])
    injector._configure_from_config(config, MagicMock())
    injector.placeholder_feed_rows = 1_500_000

    injector._ensure_neighbor_pattern_index()
    injector._protect_placeholder_batch()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert (
        f"CREATE INDEX IF NOT EXISTS {case.neighbor_pattern_index_name} "
        f"ON {case.table}({case.column} bpchar_pattern_ops);" in executed_sql
    )
    assert f"ALTER TABLE {case.table} ADD CONSTRAINT {case.table}_pkey PRIMARY KEY (pr_product_sk);" in executed_sql
    assert (
        f"ALTER TABLE {case.placeholder_batch_fk_table} ADD CONSTRAINT "
        f"{case.placeholder_batch_fk_constraint} FOREIGN KEY ({case.placeholder_batch_fk_column}) "
        f"REFERENCES {case.table} (pr_product_sk);" in executed_sql
    )
    assert "INSERT INTO campaign" in executed_sql
    assert f"generate_series(1, {1_500_000 // case.placeholder_batch_campaign_stride})" in executed_sql


def test_substring_case_release_removes_campaign_rows_and_foreign_key():
    case, config = _substring_case_config()
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = _success([])
    injector._configure_from_config(config, MagicMock())

    injector._release_placeholder_batch()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert (
        f"DELETE FROM {case.placeholder_batch_fk_table} "
        f"WHERE {case.placeholder_batch_fk_column} >= 2000000000;" in executed_sql
    )
    assert (
        f"ALTER TABLE {case.placeholder_batch_fk_table} DROP CONSTRAINT IF EXISTS "
        f"{case.placeholder_batch_fk_constraint};" in executed_sql
    )


def test_simple_case_has_no_neighbor_index_or_placeholder_batch():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_prefix_simple")
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = _success([])
    injector._configure_from_config(scenario.build_fault_plan(case)[0].config, MagicMock())

    injector._ensure_neighbor_pattern_index()
    injector._ensure_repair_decision_decoy_indexes()
    injector._protect_placeholder_batch()
    injector._release_placeholder_batch()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert executed_sql == ""


def test_substring_case_fingerprint_includes_margin_predicate():
    """fingerprint 携带第二个真实谓词（跨列 margin 过滤），构成
    "该在哪列建索引"的目标辨别面；简单 case 不受影响。"""
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    assert "AND i.pr_wholesale_cost < i.pr_current_price" in case.fault_fingerprint_sql
    assert all(
        "AND i.pr_wholesale_cost < i.pr_current_price" in sql
        for sql in case.slow_queries
    )

    simple = scenario.get_case("product_category_prefix_simple")
    assert "pr_wholesale_cost" not in simple.fault_fingerprint_sql


def test_substring_case_installs_repair_decision_decoy_indexes():
    """诱饵索引：同列 left() 表达式残迹 + 价格列索引，install 预装、
    清理逻辑不删除（它们不是 remediation 表达式索引）。"""
    case, config = _substring_case_config()
    injector = PgQueryPerfMissingIndexInjector()
    injector.env = MagicMock()
    injector.env.execute_sql.return_value = _success([])
    injector._configure_from_config(config, MagicMock())

    injector._ensure_repair_decision_decoy_indexes()

    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert (
        f"CREATE INDEX IF NOT EXISTS {case.remnant_expression_index_name} "
        f"ON {case.table}((left({case.column}, 3)));" in executed_sql
    )
    assert (
        f"CREATE INDEX IF NOT EXISTS {case.neighbor_price_index_name} "
        f"ON {case.table}(pr_current_price);" in executed_sql
    )

    injector.env.execute_sql.reset_mock()
    injector._drop_target_expression_indexes()
    executed_sql = "\n".join(str(call.args[0]) for call in injector.env.execute_sql.call_args_list)
    assert case.remnant_expression_index_name not in executed_sql
    assert case.neighbor_price_index_name not in executed_sql


def test_substring_case_declares_merch_price_band_audit_profile():
    """价格带审计 profile 真实使用价格列诱饵索引，是非因果 pgss 噪声。"""
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")
    profile = next(
        item for item in case.background_workload.profiles
        if item.name == "merch_price_band_audit"
    )
    assert "pr_current_price BETWEEN 20 AND 40" in profile.sql
    assert profile.application_name == "merch_price_band_audit"
    assert all(profile.name != "merch_price_band_audit" for profile in
               scenario.get_case("product_category_prefix_simple").background_workload.profiles)


def test_substring_case_alert_does_not_disclose_the_fault_query():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    assert "substring" not in case.alert
    assert "pr_category" not in case.alert
    assert "Hint:" not in case.alert
    assert "Affected query" not in case.alert
    assert "~200ms to ~8s" in case.alert


def test_substring_case_declares_full_environment_contract():
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    assert case.shadow_table_name == "product_prestage_base"
    assert case.neighbor_pattern_index_name == "idx_product_pr_category_pattern"
    assert case.remnant_expression_index_name == "idx_product_pr_category_left"
    assert case.neighbor_price_index_name == "idx_product_pr_current_price"
    assert case.placeholder_batch_fk_table == "campaign"
    assert case.placeholder_batch_fk_column == "camp_product_sk"
    assert case.placeholder_batch_fk_constraint == "fk_campaign_product"
    assert case.placeholder_batch_campaign_stride == 37
    profile_names = [profile.name for profile in case.background_workload.profiles]
    assert "catalog_autocomplete" in profile_names
    autocomplete = next(
        profile for profile in case.background_workload.profiles if profile.name == "catalog_autocomplete"
    )
    assert "LIKE 'Sho%'" in autocomplete.sql

    simple = scenario.get_case("product_category_prefix_simple")
    assert simple.neighbor_pattern_index_name is None
    assert simple.placeholder_batch_fk_table is None
    assert simple.shadow_table_name is None
    assert all(profile.name != "catalog_autocomplete" for profile in simple.background_workload.profiles)


def test_substring_case_declares_resource_contract_above_starvation_defaults():
    # 默认 0.5 CPU / 256MB 容器内注入器会触发 cgroup OOM 崩溃并摧毁 fault
    # 数据集；case 必须声明能存活整个 run 的资源合同（worker 覆盖 container）。
    scenario = PgQueryPerfMissingIndexScenario()
    case = scenario.get_case("product_category_substring")

    resources = case.runtime.resources
    assert resources is not None
    assert resources.container_memory_mb >= 2048
    assert resources.container_cpu_limit >= 2.0
    assert resources.worker_memory_mb >= resources.container_memory_mb
    assert resources.worker_physical_cores >= resources.container_cpu_limit

    simple = scenario.get_case("product_category_prefix_simple")
    # 并行执行要求每个 case 声明显式资源合同（derive_worker_demand）；simple
    # case 与部署默认一致：1 CPU / 512MB，不低于饥饿默认值。
    simple_resources = simple.runtime.resources
    assert simple_resources is not None
    assert simple_resources.container_memory_mb >= 512
    assert simple_resources.container_cpu_limit >= 1.0
    assert simple_resources.worker_memory_mb >= simple_resources.container_memory_mb
    assert simple_resources.worker_physical_cores >= simple_resources.container_cpu_limit
