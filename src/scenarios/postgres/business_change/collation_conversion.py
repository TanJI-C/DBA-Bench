from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.business_change import (
    PgBusinessChangeCollationConversionForStoreReturnsCollationConversionEvaluatorCase,
    PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleEvaluatorCase,
    PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillEvaluatorCase,
    PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleEvaluatorCase,
    PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase,
    PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase,
)


from src.scenarios.workloads import WorkloadProfile

from ...base import (
    PostgresCaseRuntime,
    BackgroundWorkloadSpec,
    DifficultyCalibration,
    PostgresScenario,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresScenarioCase,
)


POSTGRES_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeCollationConversionCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    column: str
    source_column: str
    old_collation: str
    target_collation: str
    old_index_name: str
    like_index_name: str
    audit_column: str
    legacy_column: str
    audit_index_name: str
    legacy_index_name: str
    like_prefix: str
    sample_rows: int
    slow_queries: tuple[str, ...]
    preview_view_name: str = ""
    archive_table: str = ""
    archive_column: str = ""
    archive_index_name: str = ""

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeCollationConversionForStoreReturnsCollationConversionScenarioCase(PgBusinessChangeCollationConversionCase):
    pass

def build_collation_conversion_noise_profiles(
    table: str = "store_returns",
    ticket_column: str = "sr_ticket_number_txt",
    source_column: str = "sr_ticket_number",
    audit_column: str = "sr_ticket_number_audit_txt",
    legacy_column: str = "sr_ticket_number_legacy_txt",
    like_prefix: str = "100%",
    archive_table: str = "",
    archive_column: str = "",
) -> List[WorkloadProfile]:
    """Same-domain noise for the collation conversion scenario.

    The real fault is the release column whose collation must be converted and
    then backed by a LIKE-friendly text_pattern_ops index. These profiles keep
    workload_activity/topsql busy with adjacent ticket text columns and release
    validation probes, so a correct agent must inspect metadata and plans
    instead of acting on the first ticket-like B-tree it sees.
    """
    profiles = [
        WorkloadProfile(
            name="returns_ticket_prefix_probe",
            sql=(
                f"SELECT count(*) AS matching_returns "
                f"FROM {table} "
                f"WHERE {ticket_column} LIKE '{like_prefix}'"
            ),
            qps=0.45,
            tier="LIGHT",
            application_name="returns-ticket-search-api",
        ),
        WorkloadProfile(
            name="returns_ticket_audit_prefix_probe",
            sql=(
                f"SELECT count(*) AS audit_matches "
                f"FROM {table} "
                f"WHERE {audit_column} LIKE '{like_prefix}'"
            ),
            qps=0.35,
            tier="LIGHT",
            application_name="returns-audit-preview",
        ),
        WorkloadProfile(
            name="returns_ticket_legacy_sort_preview",
            sql=(
                f"SELECT {legacy_column} "
                f"FROM {table} "
                f"WHERE {legacy_column} IS NOT NULL "
                f"ORDER BY {legacy_column} "
                "LIMIT 25"
            ),
            qps=0.25,
            tier="MEDIUM",
            application_name="returns-legacy-ticket-sort",
        ),
        WorkloadProfile(
            name="returns_numeric_ticket_rollup",
            sql=(
                f"SELECT ({source_column} / 1000) AS ticket_bucket, count(*) "
                f"FROM {table} "
                f"GROUP BY ticket_bucket "
                "ORDER BY count(*) DESC "
                "LIMIT 20"
            ),
            qps=0.25,
            tier="LIGHT",
            application_name="returns-ticket-rollup",
        ),
        WorkloadProfile(
            name="missing_returns_locale_cache_noise",
            sql="SELECT count(*) FROM returns_ticket_locale_cache_missing;",
            qps=0.2,
            tier="LOG_NOISE",
            application_name="returns-locale-cache-refresh",
        ),
    ]
    if archive_table:
        profiles.append(
            WorkloadProfile(
                name="returns_archive_prefix_probe",
                sql=(
                    f"SELECT count(*) AS archive_matches "
                    f"FROM {archive_table} "
                    f"WHERE {archive_column} LIKE '{like_prefix}'"
                ),
                qps=0.15,
                tier="LIGHT",
                application_name="returns-archive-audit",
            ),
        )
    return profiles

_PGBUSINESSCHANGECOLLATIONCONVERSIONSCENARIO_CASE = PgBusinessChangeCollationConversionForStoreReturnsCollationConversionScenarioCase(
    case_id='store_returns_collation_conversion',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "ticket text uses c collation",
                    "entity": "store_returns_collation_conversion",
                    "evidence": [
                        "scripted diagnostic actions observed ticket text uses c collation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "collation conversion rewrites table",
                    "entity": "store_returns_collation_conversion",
                    "evidence": [
                        "scripted diagnostic actions observed collation conversion rewrites table"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "prefix like needs text pattern ops",
                    "entity": "store_returns_collation_conversion",
                    "evidence": [
                        "scripted diagnostic actions observed prefix like needs text pattern ops"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "convert ticket column to regional collation",
                    "entity": "store_returns_collation_conversion",
                    "evidence": [
                        "scripted diagnostic actions observed convert ticket column to regional collation"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "create concurrent like pattern index",
                    "entity": "store_returns_collation_conversion",
                    "evidence": [
                        "scripted diagnostic actions observed create concurrent like pattern index"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "applied the case-specific remediation"
            ],
            "verification": [
                "verified the case-specific final state"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.538462,
        reference_run_ids=(
            'logs/traces/'
            'run_pg_business_change_collation_conversion_'
            'store_returns_collation_conversion_MockLLMAgent.json',
        ),
        protocol_version='difficulty-v2',
    ),
    case_no=0,
    evaluator=PgBusinessChangeCollationConversionForStoreReturnsCollationConversionEvaluatorCase,
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates an online collation conversion on a TPC-DS fact table that invalidates LIKE-friendly B-tree access paths.',
    alert='业务变更窗口提醒：退货报表发布硬性要求承载线上 LIKE 前缀检索的主票号文本字段完成区域性排序改造。发布验收以数据库目录元数据为准：该列 collation 必须已转换为非 C 的区域性 collation，转换后 LIKE 前缀检索条件必须继续由索引条件承载，随附的发布预览视图在变更后必须仍然可用并按区域性排序语义返回。变更需以低锁方式在低峰期完成；同表的审计票号与历史预览字段及其索引不得变更。请先用业务负载与目录元数据区分目标字段与相邻字段，评估表重写、锁等待、依赖对象与空间膨胀影响，再实施变更并用元数据查询与 EXPLAIN 验证；确认闭环后必须调用 submit 结束流程。',
    initial_state={'status': 'change_requested',
 'table': 'store_returns',
 'column': 'sr_ticket_number_txt',
 'current_collation': 'C',
 'risk': 'table_rewrite_and_like_index_regression_with_view_dependency'},
    expected_target={'status': 'converted',
 'table': 'store_returns',
 'column': 'sr_ticket_number_txt',
 'target_collation': 'non_C_regional_collation',
 'like_index': 'idx_store_returns_ticket_txt_like_ops',
 'plan': 'index_scan_for_like_prefix'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_collation_conversion_noise_profiles(
            archive_table='store_returns_archive',
            archive_column='sr_ticket_number_archive_txt',
        )),
        worker_count=2,
        seed=0,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='store_returns',
    column='sr_ticket_number_txt',
    source_column='sr_ticket_number',
    old_collation='C',
    target_collation='en_US.utf8',
    old_index_name='idx_store_returns_ticket_txt_btree',
    like_index_name='idx_store_returns_ticket_txt_like_ops',
    audit_column='sr_ticket_number_audit_txt',
    legacy_column='sr_ticket_number_legacy_txt',
    audit_index_name='idx_store_returns_ticket_audit_txt_btree',
    legacy_index_name='idx_store_returns_ticket_legacy_expr',
    like_prefix='100%',
    sample_rows=50000,
    slow_queries=("SELECT count(*) FROM store_returns WHERE sr_ticket_number_txt LIKE '100%';",),
    preview_view_name='returns_regional_sort_preview',
    archive_table='store_returns_archive',
    archive_column='sr_ticket_number_archive_txt',
    archive_index_name='idx_store_returns_archive_ticket_btree',
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleScenarioCase(
    PgBusinessChangeCollationConversionCase
):
    pass


_PGBUSINESSCHANGECOLLATIONCONVERSIONSCENARIO_SIMPLE_CASE = (
    PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleScenarioCase(
        case_id="store_returns_ticket_locale_simple",
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "ticket locale text uses c collation",
                        "entity": "store_returns_ticket_locale_simple",
                        "evidence": [
                            "scripted diagnostic actions observed ticket locale text uses c collation"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "collation conversion rewrites the column",
                        "entity": "store_returns_ticket_locale_simple",
                        "evidence": [
                            "scripted diagnostic actions observed collation conversion rewrites the column"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "prefix like needs text pattern ops",
                        "entity": "store_returns_ticket_locale_simple",
                        "evidence": [
                            "scripted diagnostic actions observed prefix like needs text pattern ops"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "convert locale text to regional collation",
                        "entity": "store_returns_ticket_locale_simple",
                        "evidence": [
                            "scripted diagnostic actions observed convert locale text to regional collation"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "restore the prefix pattern index",
                        "entity": "store_returns_ticket_locale_simple",
                        "evidence": [
                            "scripted diagnostic actions observed restore the prefix pattern index"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "applied the case-specific remediation"
                ],
                "verification": [
                    "verified the case-specific final state"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgBusinessChangeCollationConversionForStoreReturnsTicketLocaleSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-tpcds:latest",
        workload_tag="tpcds",
        dataset_scale=1,
        title="Simplified regional collation conversion with one adjacent ticket-search decoy.",
        alert=(
            "变更窗口告警：退货检索服务需要支持区域化文本排序，发布预检显示前缀查询计划可能回退。"
            "请确认真正承载线上检索的字段，评估转换与索引影响，安全完成变更并验证查询计划；"
            "审计预览流量仍在低频运行。"
        ),
        initial_state={
            "status": "change_requested",
            "symptom": "regional_sorting_and_prefix_plan_risk",
        },
        expected_target={
            "status": "converted",
            "collation": "non_C_regional_collation",
            "plan": "index_scan_for_like_prefix",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(
                build_collation_conversion_noise_profiles(
                    table="store_returns",
                    ticket_column="sr_ticket_number_locale_txt",
                    source_column="sr_ticket_number",
                    audit_column="sr_ticket_number_locale_audit_txt",
                    legacy_column="sr_ticket_number_locale_legacy_txt",
                    like_prefix="20%",
                )[:2]
            ),
            worker_count=1,
            seed=0x4103,
            warmup_seconds=2,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="store_returns",
        column="sr_ticket_number_locale_txt",
        source_column="sr_ticket_number",
        old_collation="C",
        target_collation="en_US.utf8",
        old_index_name="idx_store_returns_ticket_locale_btree",
        like_index_name="idx_store_returns_ticket_locale_like_ops",
        audit_column="sr_ticket_number_locale_audit_txt",
        legacy_column="sr_ticket_number_locale_legacy_txt",
        audit_index_name="idx_store_returns_ticket_locale_audit",
        legacy_index_name="idx_store_returns_ticket_locale_legacy",
        like_prefix="20%",
        sample_rows=8000,
        slow_queries=(
            "SELECT count(*) FROM store_returns "
            "WHERE sr_ticket_number_locale_txt LIKE '20%';",
        ),
        difficulty=DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.142857,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_collation_conversion_"
                "store_returns_ticket_locale_simple_MockLLMAgent.json",
            ),
        ),
    )
)


import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from src.scenarios.faults import BaseFaultInjector, FaultLifecycleContext
from src.scenarios.postgres.common import (
    PgQueryPerfFaultFingerprintProbe,
    _cancel_open_connection,
    _join_thread,
    _json_object,
    _json_response,
    _require_sql_success,
    _run_cleanup_steps,
    _validate_sql_identifier,
)

class PgBusinessChangeCollationConversionInjector(BaseFaultInjector):
    """
    准备"字符集与排序规则在线转换"业务变更场景。
    注入后环境处于待变更状态：TPC-DS 事实表上存在 C collation 文本列和
    普通 B-tree LIKE 依赖索引，Agent 需要执行 collation 转换并重建
    LIKE 可用索引。
    """

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print("[FaultInjector:PgBusinessChangeCollationConversionInjector] "
              f"Preparing {self.table}.{self.column} with C collation...")

        self._exec_sql(
            f"ALTER TABLE {self.table} "
            f"ADD COLUMN IF NOT EXISTS {self.column} text COLLATE \"C\";")
        self._exec_sql(
            f"UPDATE {self.table} "
            f"SET {self.column} = {self.source_column}::text "
            f"WHERE ctid IN ("
            f"SELECT ctid FROM {self.table} "
            f"WHERE {self.column} IS NULL "
            f"LIMIT {self.sample_rows});")
        self._exec_sql(
            f"ALTER TABLE {self.table} ALTER COLUMN {self.column} "
            f"TYPE text COLLATE \"C\" USING {self.column}::text;")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.like_index_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.old_index_name};")
        self._exec_sql(
            f"CREATE INDEX {self.old_index_name} "
            f"ON {self.table} ({self.column});")
        self._prepare_decoy_ticket_columns()
        if self.archive_table:
            self._prepare_archive_decoy_table()
        if self.preview_view_name:
            self._exec_sql(
                f"CREATE VIEW {self.preview_view_name} AS "
                f"SELECT sr_item_sk, sr_ticket_number, {self.column} "
                f"FROM {self.table} "
                f"ORDER BY {self.column} COLLATE \"C\";")
        self._exec_sql(f"ANALYZE {self.table};")

        self._exec_sql("SET statement_timeout = '30s';")
        self._exec_sql(
            f"EXPLAIN SELECT count(*) FROM {self.table} "
            f"WHERE {self.column} LIKE '{self.like_prefix}';")

        print("[FaultInjector:PgBusinessChangeCollationConversionInjector] "
              f"Prepared baseline index {self.old_index_name}; business "
              "change is pending.")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.column = _validate_sql_identifier(config['column'], "column")
        self.source_column = _validate_sql_identifier(config['source_column'], "source_column")
        self.old_index_name = _validate_sql_identifier(config['old_index_name'], "old_index_name")
        self.like_index_name = _validate_sql_identifier(config['like_index_name'], "like_index_name")
        self.audit_column = _validate_sql_identifier(config['audit_column'], "audit_column")
        self.legacy_column = _validate_sql_identifier(config['legacy_column'], "legacy_column")
        self.audit_index_name = _validate_sql_identifier(config['audit_index_name'], "audit_index_name")
        self.legacy_index_name = _validate_sql_identifier(config['legacy_index_name'], "legacy_index_name")
        self.like_prefix = config['like_prefix']
        self.sample_rows = int(config['sample_rows'])
        self.preview_view_name = str(config.get('preview_view_name', ''))
        self.archive_table = str(config.get('archive_table', ''))
        self.archive_column = str(config.get('archive_column', ''))
        self.archive_index_name = str(config.get('archive_index_name', ''))

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        column_state = env.execute_sql(
            "SELECT a.attname, c.collname "
            "FROM pg_attribute a "
            "JOIN pg_class t ON t.oid = a.attrelid "
            "JOIN pg_collation c ON c.oid = a.attcollation "
            f"WHERE t.relname = '{self.table}' AND a.attname = '{self.column}';"
        )
        index_state = env.execute_sql(
            "SELECT indexname, indexdef FROM pg_indexes "
            f"WHERE tablename = '{self.table}' AND indexdef LIKE '%{self.column}%';"
        )
        plan = env.execute_sql(
            f"EXPLAIN SELECT count(*) FROM {self.table} "
            f"WHERE {self.column} LIKE '{self.like_prefix}';"
        )
        return {
            "column_state": column_state,
            "index_state": index_state,
            "fault_plan": plan,
        }

    def quiesce(self, context: FaultLifecycleContext):
        """No background threads or runtime resources to clean up."""
        pass

    def recover(self, context: FaultLifecycleContext):
        print("[FaultInjector:PgBusinessChangeCollationConversionInjector] "
              "Recovering collation conversion scenario...")
        if self.preview_view_name:
            self._exec_sql(f"DROP VIEW IF EXISTS {self.preview_view_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.like_index_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.old_index_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.audit_index_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.legacy_index_name};")
        if self.archive_index_name:
            self._exec_sql(f"DROP INDEX IF EXISTS {self.archive_index_name};")
        if self.archive_table:
            self._exec_sql(f"DROP TABLE IF EXISTS {self.archive_table};")
        self._exec_sql(f"ALTER TABLE {self.table} DROP COLUMN IF EXISTS {self.audit_column};")
        self._exec_sql(f"ALTER TABLE {self.table} DROP COLUMN IF EXISTS {self.legacy_column};")
        self._exec_sql(
            f"ALTER TABLE {self.table} DROP COLUMN IF EXISTS {self.column};")
        self._exec_sql(f"ANALYZE {self.table};")

    def _prepare_archive_decoy_table(self):
        self._exec_sql(f"DROP TABLE IF EXISTS {self.archive_table};")
        self._exec_sql(f"""
            CREATE TABLE {self.archive_table} (
                id integer PRIMARY KEY,
                sr_ticket_number integer NOT NULL,
                {self.archive_column} text COLLATE "C"
            );
        """)
        self._exec_sql(f"""
            INSERT INTO {self.archive_table} (id, sr_ticket_number, {self.archive_column})
            SELECT g, g, g::text
            FROM generate_series(1, 500) AS g;
        """)
        self._exec_sql(
            f"CREATE INDEX {self.archive_index_name} "
            f"ON {self.archive_table} ({self.archive_column});")

    def _prepare_decoy_ticket_columns(self):
        self._exec_sql(
            f"ALTER TABLE {self.table} ADD COLUMN IF NOT EXISTS {self.audit_column} text COLLATE \"C\";")
        self._exec_sql(
            f"ALTER TABLE {self.table} ADD COLUMN IF NOT EXISTS {self.legacy_column} text COLLATE \"C\";")
        self._exec_sql(
            f"UPDATE {self.table} SET {self.audit_column} = 'RET-' || {self.source_column}::text, "
            f"{self.legacy_column} = {self.source_column}::text WHERE ctid IN "
            f"(SELECT ctid FROM {self.table} WHERE {self.audit_column} IS NULL "
            f"OR {self.legacy_column} IS NULL LIMIT {self.sample_rows});")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.audit_index_name};")
        self._exec_sql(f"DROP INDEX IF EXISTS {self.legacy_index_name};")
        self._exec_sql(f"CREATE INDEX {self.audit_index_name} ON {self.table} ({self.audit_column});")
        self._exec_sql(f"CREATE INDEX {self.legacy_index_name} ON {self.table} (lower({self.legacy_column}));")

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        payload = _json_object(
            env.execute_sql(
                "SELECT c.collname, "
                f"to_regclass('public.{self.old_index_name}')::text, "
                f"to_regclass('public.{self.like_index_name}')::text "
                "FROM pg_attribute a "
                "JOIN pg_class t ON t.oid = a.attrelid "
                "JOIN pg_collation c ON c.oid = a.attcollation "
                f"WHERE t.relname = '{self.table}' AND a.attname = '{self.column}';"
            ),
            "verify collation-conversion fault image",
        )
        expected = [["C", self.old_index_name, None]]
        if payload["result"] != expected:
            raise RuntimeError(
                f"Collation-conversion fault image does not match the Case: "
                f"expected={expected}, observed={payload['result']}"
            )

    def _exec_sql(self, sql: str):
        import json as _json
        raw = self.env.execute_sql(sql)
        try:
            result = _json.loads(raw)
        except Exception as exc:
            raise RuntimeError(f"SQL did not return JSON: {raw}") from exc
        if result.get("status") != "success":
            raise RuntimeError(
                "Collation conversion injector SQL failed: "
                f"{result.get('error', raw)}"
            )
        return result


class PgBusinessChangeCollationConversionScenario(PostgresScenario):
    scenario_id = 'pg_business_change_collation_conversion'
    description = 'Simulates an online collation conversion on a TPC-DS fact table that invalidates LIKE-friendly B-tree access paths.'
    cases = (
        _PGBUSINESSCHANGECOLLATIONCONVERSIONSCENARIO_CASE,
        _PGBUSINESSCHANGECOLLATIONCONVERSIONSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgBusinessChangeCollationConversionCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeCollationConversionInjector,
                config={
                    'table': case.table,
                    'column': case.column,
                    'source_column': case.source_column,
                    'old_collation': case.old_collation,
                    'target_collation': case.target_collation,
                    'old_index_name': case.old_index_name,
                    'like_index_name': case.like_index_name,
                    'audit_column': case.audit_column,
                    'legacy_column': case.legacy_column,
                    'audit_index_name': case.audit_index_name,
                    'legacy_index_name': case.legacy_index_name,
                    'like_prefix': case.like_prefix,
                    'sample_rows': case.sample_rows,
                    'preview_view_name': case.preview_view_name,
                    'archive_table': case.archive_table,
                    'archive_column': case.archive_column,
                    'archive_index_name': case.archive_index_name,
                },
            ),
        )
