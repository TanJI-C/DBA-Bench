from dataclasses import dataclass
from typing import List, Mapping

from src.scenarios.evaluation.postgres.system_failure import (
    PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase,
    PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolIdleTransactionStormEvaluatorCase,
    PgSystemFailureConnectionStormForCheckoutPoolLeakSimpleEvaluatorCase,
    PgSystemFailureDeadlockForCheckoutOrderDeadlockEvaluatorCase,
    PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleEvaluatorCase,
    PgSystemFailureFdExhaustionForNightlyReportingNofileExhaustionEvaluatorCase,
    PgSystemFailureFdExhaustionForReportExportFdExhaustionSimpleEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase,
    PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase,
    PgSystemFailureNoisyNeighborForWalArchiveCpuNeighborEvaluatorCase,
    PgSystemFailureNoisyNeighborForSingleArchiveCpuNeighborSimpleEvaluatorCase,
    PgSystemFailureOomForRestartMemoryConfigOomEvaluatorCase,
    PgSystemFailureOomForRestartSharedBuffersOomSimpleEvaluatorCase,
    PgSystemFailurePageCorruptionForOrderLineAuditPageCorruptionEvaluatorCase,
    PgSystemFailurePageCorruptionForInvoicePageCorruptionTriageSimpleEvaluatorCase,
    PgSystemFailureTempFileExplosionForNightlyMarginTempExhaustionEvaluatorCase,
    PgSystemFailureTempFileExplosionForDailySalesTempExhaustionSimpleEvaluatorCase,
    PgSystemFailureWalAccumulationForAnalyticsSlotWalRetentionEvaluatorCase,
    PgSystemFailureWalAccumulationForAbandonedReportSlotWalRetentionSimpleEvaluatorCase,
    PgSystemFailureXidWraparoundForPaymentLedgerXidWraparoundEvaluatorCase,
    PgSystemFailureXidWraparoundForBillingFreezeBlockedSimpleEvaluatorCase,
)

from src.workloads.tpcds import get_tpcds_query
from src.scenarios.workloads import WorkloadProfile

from src.workloads.tpcds import default_mix

from ...base import (
    PostgresCaseRuntime,
    PostgresScenario,
    BackgroundWorkloadSpec,
    BackgroundWorkloadStartPhase,
    DifficultyCalibration,
    EMPTY_BACKGROUND_WORKLOAD,
    FaultPlan,
    CaseResourceSpec,
    PostgresRuntimeSpec,
    PostgresScenarioCase,
)

_DEFAULT_SYSTEM_FAILURE_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=512,
    container_cpu_limit=1.0,
    container_memory_mb=512,
)

_OOM_RESOURCES = CaseResourceSpec(
    worker_physical_cores=1,
    worker_memory_mb=256,
    container_cpu_limit=0.5,
    container_memory_mb=256,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureAutoAnalyzeStormCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    tables: tuple[str, ...]
    noise_tables: tuple[str, ...]
    tables_2: tuple[str, ...]
    noise_tables_2: tuple[str, ...]
    scale_factor: str
    threshold: str
    naptime: str
    safe_scale_factor: str
    safe_threshold: str
    safe_naptime: str
    # 表级 reloptions 覆盖：(table, ((option, value), ...))。表级设置覆盖全局 GUC，
    # 构成与全局篡改并列的第二个作用域；为空时 Injector 不安装任何表级覆盖。
    table_reloptions: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    # 受保护的健康近邻覆盖：环境既有调优，不是故障；OP 要求其保留且处于安全带。
    protected_reloptions: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    require_completed_autoanalyze: bool
    completion_timeout_seconds: int

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormScenarioCase(PgSystemFailureAutoAnalyzeStormCase):
    pass

def build_auto_analyze_storm_profiles() -> List[WorkloadProfile]:
    # 复用 runner 造真实生产噪声，不另开一套后台线程。
    return list(default_mix()) + [
        WorkloadProfile(
            name="monitor_probe_activity_snapshot",
            sql=(
                "SELECT state, wait_event_type, count(*) "
                "FROM pg_stat_activity "
                "WHERE datname = current_database() "
                "GROUP BY state, wait_event_type"
            ),
            qps=0.8,
            tier="MONITOR",
        ),
        WorkloadProfile(
            name="monitor_probe_table_stats",
            sql=(
                "SELECT relname, n_mod_since_analyze, last_autoanalyze "
                "FROM pg_stat_user_tables "
                "WHERE relname IN ('customer','store_sales','inventory','web_sales','catalog_sales')"
            ),
            qps=0.5,
            tier="MONITOR",
        ),
        # inventory 受保护覆盖 (0.0001,300) 的触发线约 1475 次修改；低速率库存
        # 滚动刷新（0.8 行/s）使其实际周期约 31 分钟，运行窗口内零风暴——
        # inventory 全程安静是"受保护健康近邻"辨别的观测证据，不能让它自己风暴。
        WorkloadProfile(
            name="background_dml_inventory_refresh",
            sql=(
                "UPDATE inventory SET inv_quantity_on_hand = inv_quantity_on_hand "
                "WHERE ctid IN (SELECT ctid FROM inventory LIMIT 40)"
            ),
            qps=0.02,
            tier="DML_NOISE",
            commit=True,
        ),
        # web_sales 表级风暴覆盖 (0.0001,5) 的触发线约 77 次修改；r5 把滚动 DML
        # 降到 ~1 行/s（0.025 qps × 40 行），全局 GUC 恢复后复发周期从 ~10s 拉长到
        # ~77s（1-2 分钟级）：修复后短窗观测"看起来已修好"，复发需要跨时间增量
        # 观测才能捕获——这是 r5 "未找出根因" 目标的核心陷阱，DML 速率与触发线
        # 配套核算，不改变业务语义（低速滚动 rollup 是真实维护模式）。
        WorkloadProfile(
            name="background_dml_web_sales_rollup",
            sql=(
                "UPDATE web_sales SET ws_quantity = ws_quantity "
                "WHERE ctid IN (SELECT ctid FROM web_sales LIMIT 40)"
            ),
            qps=0.025,
            tier="DML_NOISE",
            commit=True,
        ),
        WorkloadProfile(
            name="background_dml_catalog_sales_rollup",
            sql=(
                "UPDATE catalog_sales SET cs_quantity = cs_quantity "
                "WHERE ctid IN (SELECT ctid FROM catalog_sales LIMIT 40)"
            ),
            qps=0.2,
            tier="DML_NOISE",
            commit=True,
        ),
        WorkloadProfile(
            name="auto_analyze_log_noise_statement_timeout",
            sql="SET LOCAL statement_timeout = '20ms'; SELECT pg_sleep(0.2);",
            qps=3.0,
            tier="LOG_NOISE",
        ),
        WorkloadProfile(
            name="auto_analyze_log_noise_missing_dashboard_cache",
            sql="SELECT count(*) FROM dashboard_refresh_cache_missing;",
            qps=2.0,
            tier="LOG_NOISE",
        ),
        WorkloadProfile(
            name="auto_analyze_log_noise_bad_report_batch",
            sql="SELECT ('report_batch_' || clock_timestamp())::integer;",
            qps=2.0,
            tier="LOG_NOISE",
        ),
    ]

_PGSYSTEMFAILUREAUTOANALYZESTORMSCENARIO_CASE = PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormScenarioCase(
    case_id='sales_tables_auto_analyze_storm',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "auto analyze storm",
                    "entity": "sales_tables_auto_analyze_storm",
                    "evidence": [
                        "scripted diagnostic actions observed auto analyze storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "analyze thresholds too aggressive",
                    "entity": "sales_tables_auto_analyze_storm",
                    "evidence": [
                        "scripted diagnostic actions observed analyze thresholds too aggressive"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "stale per-table analyze override keeps the storm",
                    "entity": "web_sales",
                    "evidence": [
                        "scripted diagnostic actions observed stale per-table analyze override keeps the storm"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "foreground workload is not root cause",
                    "entity": "sales_tables_auto_analyze_storm",
                    "evidence": [
                        "scripted diagnostic actions observed foreground workload is not root cause"
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
    case_no=0,
    evaluator=PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates auto-analyze storm by setting extremely low analyze thresholds.',
    alert='Alert: postgres-primary reports recurring short disk I/O saturation windows. Report SQL latency, background stock/sales refresh jobs, and monitoring probes are all active during the incident, and historical slow-query noise is present. The affected window includes normal client backends plus database maintenance activity. Identify the recurring saturation cause, separate it from workload noise, and restore stable performance safely.',
    initial_state={'status': 'healthy', 'io': 'normal'},
    expected_target={'status': 'recovered', 'autovacuum_config': 'safe_analyze_defaults_restored'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_auto_analyze_storm_profiles()),
        worker_count=6,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
        warmup_seconds=10,
    ),
    tables=('customer', 'store_sales'),
    # r5：store_returns/customer_demographics 加入噪声表集合，使其在装机期获得
    # 基线 ANALYZE（pg_class.reltuples 可用于触发线算术）并进入可观测性查询；
    # 它们没有专属持续 DML，修复后触发线远未达到，全程零风暴。
    noise_tables=('inventory', 'web_sales', 'catalog_sales', 'store_returns', 'customer_demographics'),
    tables_2=('customer', 'store_sales'),
    noise_tables_2=('inventory', 'web_sales', 'catalog_sales', 'store_returns', 'customer_demographics'),
    # web_sales 表级风暴覆盖：触发线 0.0001*719,384+5 ≈ 77 次修改；r5 把业务 DML
    # 降到 ~1 行/s 后，全局 GUC 恢复下复发周期 ~77s（1-2 分钟级）——修复后短窗
    # 观测"看似已修好"，构成第二篡改作用域与"未找出根因"陷阱的核心证据。
    table_reloptions=(
        (
            'web_sales',
            (
                ('autovacuum_analyze_scale_factor', '0.0001'),
                ('autovacuum_analyze_threshold', '5'),
            ),
        ),
    ),
    # r5 受保护健康近邻群（历史调优共存，全部处于安全带 >=1000，scale_factor 各
    # 不相同，触发线聚集在 1.2k-1.6k 同一量级；无专属持续 DML，修复后全程零风暴）：
    #   inventory (11,744,541 行)  (0.0001, 300)  触发线 ≈1,474 —— 与 web_sales 同
    #     scale_factor，值匹配无法判定；
    #   customer_demographics (1,920,800 行) (0.0006, 100) 触发线 ≈1,252；
    #   store_returns (287,514 行)  (0.005, 150)  触发线 ≈1,588。
    # 判别只能逐表做 reltuples 算术（77 vs 1.2k-1.6k）+ 观测行为（web_sales 复发、
    # 近邻全程安静）；"看到 reloptions 就清"或"按 scale/线值匹配"策略全部误伤
    # 受保护对象，构成修复范围过宽的合法失败面。
    protected_reloptions=(
        (
            'inventory',
            (
                ('autovacuum_analyze_scale_factor', '0.0001'),
                ('autovacuum_analyze_threshold', '300'),
            ),
        ),
        (
            'customer_demographics',
            (
                ('autovacuum_analyze_scale_factor', '0.0006'),
                ('autovacuum_analyze_threshold', '100'),
            ),
        ),
        (
            'store_returns',
            (
                ('autovacuum_analyze_scale_factor', '0.005'),
                ('autovacuum_analyze_threshold', '150'),
            ),
        ),
    ),
    scale_factor='0.00001',
    threshold='1',
    naptime='1s',
    safe_scale_factor='0.1',
    safe_threshold='50',
    safe_naptime='60',
    require_completed_autoanalyze=False,
    completion_timeout_seconds=12,
    difficulty=DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.466667,
        reference_run_ids=(
            "reference-251__pg_system_failure_auto_analyze_storm"
            "reference-246__pg_system_failure_auto_analyze_storm__"
            "sales_tables_auto_analyze_storm__mock__r001/attempts/002/trace.json",
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleScenarioCase(
    PgSystemFailureAutoAnalyzeStormCase
):
    pass


_PGSYSTEMFAILUREAUTOANALYZESTORMSCENARIO_SIMPLE_CASE = (
    PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleScenarioCase(
        case_id='store_sales_auto_analyze_storm_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "auto analyze storm",
                        "entity": "store_sales_auto_analyze_storm_simple",
                        "evidence": [
                            "scripted diagnostic actions observed auto analyze storm"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "analyze thresholds too aggressive",
                        "entity": "store_sales_auto_analyze_storm_simple",
                        "evidence": [
                            "scripted diagnostic actions observed analyze thresholds too aggressive"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "foreground workload is not root cause",
                        "entity": "store_sales_auto_analyze_storm_simple",
                        "evidence": [
                            "scripted diagnostic actions observed foreground workload is not root cause"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "restore safe autovacuum analyze settings",
                        "entity": "store_sales_auto_analyze_storm_simple",
                        "evidence": [
                            "scripted diagnostic actions observed restore safe autovacuum analyze settings"
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
        evaluator=PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=4,
            environmental_complexity=0.3,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_system_failure_auto_analyze_storm_"
                "store_sales_auto_analyze_storm_simple_"
                "MockLLMAgent.json",
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title=(
            'Hot sales tables keep triggering auto-analyze under unsafe global '
            'thresholds plus a stale per-table override.'
        ),
        alert=(
            'Alert: store sales writes show recurring short I/O latency windows while the '
            'database remains available. A low-rate calendar health query is also present. '
            'Identify the recurring database maintenance '
            'cause, separate it from foreground noise, and restore safe settings.'
        ),
        initial_state={
            'status': 'degraded',
            'symptom': 'recurring_short_io_windows',
            'database': 'available',
        },
        expected_target={
            'status': 'recovered',
            'autovacuum_config': 'safe_analyze_defaults_restored',
            'target_table': 'store_sales',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='sales_calendar_health_probe',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='sales_calendar_health_probe',
                ),
                # store_returns 的低频业务维护写入：表级 reloptions 覆盖的风暴燃料。
                # 触发线 0.0001*28.7万+5 ≈ 34 次修改，8 行/秒下每 ~4 秒一次 autoanalyze，
                # 全局参数恢复后仍持续，构成修复范围辨别的核心证据。
                WorkloadProfile(
                    name='background_dml_store_returns_touch',
                    sql=(
                        'UPDATE store_returns SET sr_return_quantity = sr_return_quantity '
                        'WHERE ctid IN (SELECT ctid FROM store_returns LIMIT 40)'
                    ),
                    qps=0.2,
                    tier='DML_NOISE',
                    commit=True,
                ),
            ),
            worker_count=1,
            seed=0x2F04,
            start_phase=BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY,
            warmup_seconds=11,
        ),
        tables=('store_sales',),
        noise_tables=('store_returns',),
        tables_2=('store_sales',),
        noise_tables_2=('store_returns',),
        table_reloptions=(
            (
                'store_returns',
                (
                    ('autovacuum_analyze_scale_factor', '0.0001'),
                    ('autovacuum_analyze_threshold', '5'),
                ),
            ),
        ),
        # inventory 既有健康调优：scale_factor 与 store_returns 故障值相同（0.0001），
        # 但 inventory 有 1174.5 万行，触发线 0.0001*1174.5万+300 ≈ 1475 次修改，处于
        # 安全带（>=1000）。辨别它必须靠 reltuples 算术与观测（全程零风暴），而不是
        # "看到 0.0001 就是故障"的值匹配；清除它即破坏受保护对象。
        protected_reloptions=(
            (
                'inventory',
                (
                    ('autovacuum_analyze_scale_factor', '0.0001'),
                    ('autovacuum_analyze_threshold', '300'),
                ),
            ),
        ),
        scale_factor='0.00001',
        threshold='1',
        naptime='1s',
        safe_scale_factor='0.1',
        safe_threshold='50',
        safe_naptime='60',
        require_completed_autoanalyze=True,
        completion_timeout_seconds=90,
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

def _reloptions_items(raw) -> dict:
    """把 pg_class.reloptions（text[]，JSON 里是 list 或 '{a,b}' 字符串）解析成 dict。"""
    if raw is None:
        return {}
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("{") and text.endswith("}"):
            text = text[1:-1]
        items = [item for item in text.split(",") if item]
    else:
        items = [str(item) for item in raw]
    parsed = {}
    for item in items:
        option, _, value = item.partition("=")
        parsed[option.strip()] = value.strip()
    return parsed


class PgSystemFailureAutoAnalyzeStormInjector(BaseFaultInjector):
    """
    模拟"统计信息收集风暴"故障。
    通过将 autovacuum_analyze_scale_factor 调至极低值（0.00001），
    并将 autovacuum_analyze_threshold 设为 1，
    导致多张大表频繁且同时触发自动分析，占满磁盘 I/O。
    Case 还可以配置 table_reloptions，在指定表上安装表级
    autovacuum_analyze_* 覆盖（表级设置覆盖全局 GUC），构成第二个篡改作用域。
    """

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
            self._trigger_runtime()

    def prepare_observability(self, context: FaultLifecycleContext):
        import time

        config = context.config
        env = context.env
        with env.metrics_hidden():
            env.reconnect()
            config_state = env.execute_sql(
                "SELECT name, setting, source FROM pg_settings "
                "WHERE name IN ('autovacuum_analyze_scale_factor', "
                "'autovacuum_analyze_threshold', 'autovacuum_naptime') ORDER BY name;"
            )
            table_names = ", ".join(f"'{table}'" for table in self.tables + self.noise_tables)
            table_stats = env.execute_sql(
                "SELECT relname, n_mod_since_analyze, last_autoanalyze "
                f"FROM pg_stat_user_tables WHERE relname IN ({table_names}) ORDER BY relname;"
            )
            activity = self.analyze_activity
        env.reconnect()
        time.sleep(2)
        return {
            "config": config_state,
            "table_stats": table_stats,
            "analyze_activity": activity,
            "disk_io": env.query_metrics("disk_io"),
        }

    def quiesce(self, context: FaultLifecycleContext):
        pass

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._establish_analyze_baseline()
            self._install_persistent_state()
            self._trigger_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.tables = tuple(_validate_sql_identifier(table, "table") for table in config["tables"])
        self.noise_tables = tuple(
            _validate_sql_identifier(table, "noise_table") for table in config["noise_tables"]
        )
        self.scale_factor = config["scale_factor"]
        self.threshold = config["threshold"]
        self.naptime = config["naptime"]
        self.table_reloptions = tuple(
            (
                _validate_sql_identifier(table, "reloptions_table"),
                tuple(
                    (str(option), str(value))
                    for option, value in options
                ),
            )
            for table, options in config["table_reloptions"]
        )
        self.protected_reloptions = tuple(
            (
                _validate_sql_identifier(table, "protected_reloptions_table"),
                tuple(
                    (str(option), str(value))
                    for option, value in options
                ),
            )
            for table, options in config["protected_reloptions"]
        )
        self.require_completed_autoanalyze = bool(config["require_completed_autoanalyze"])
        self.completion_timeout_seconds = int(config["completion_timeout_seconds"])

    def _install_persistent_state(self) -> None:
        print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] "
              f"Injecting auto-analyze storm...")
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER SYSTEM SET autovacuum_analyze_scale_factor = '{self.scale_factor}';"
            ),
            "install auto-analyze scale factor",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER SYSTEM SET autovacuum_analyze_threshold = '{self.threshold}';"
            ),
            "install auto-analyze threshold",
        )
        _require_sql_success(
            self.env.execute_sql(
                f"ALTER SYSTEM SET autovacuum_naptime = '{self.naptime}';"
            ),
            "install auto-analyze naptime",
        )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload auto-analyze fault settings",
        )
        for table, options in self.table_reloptions + self.protected_reloptions:
            assignments = ", ".join(f"{option} = {value}" for option, value in options)
            _require_sql_success(
                self.env.execute_sql(f"ALTER TABLE {table} SET ({assignments});"),
                f"install per-table analyze override on {table}",
            )
        print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] "
              f"Set autovacuum_analyze_scale_factor={self.scale_factor}, "
              f"threshold={self.threshold}, naptime={self.naptime}, "
              f"table_reloptions={dict(self.table_reloptions)}, "
              f"protected_reloptions={dict(self.protected_reloptions)}")

    def _establish_analyze_baseline(self) -> None:
        for table in self.tables + self.noise_tables:
            _require_sql_success(
                self.env.execute_sql(f"ANALYZE {table};"),
                f"establish auto-analyze baseline for {table}",
            )

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT current_setting('autovacuum_analyze_scale_factor'), "
                "current_setting('autovacuum_analyze_threshold'), "
                "current_setting('autovacuum_naptime');"
            ),
            "verify auto-analyze fault image settings",
        )
        actual_scale, actual_threshold, actual_naptime = payload["result"][0]
        if float(actual_scale) != float(self.scale_factor):
            raise RuntimeError(
                f"Auto-analyze scale factor mismatch: expected={self.scale_factor}, "
                f"actual={actual_scale}"
            )
        if int(actual_threshold) != int(self.threshold):
            raise RuntimeError(
                f"Auto-analyze threshold mismatch: expected={self.threshold}, "
                f"actual={actual_threshold}"
            )
        if str(actual_naptime).lower() != str(self.naptime).lower():
            raise RuntimeError(
                f"Auto-analyze naptime mismatch: expected={self.naptime!r}, "
                f"actual={actual_naptime!r}"
            )
        for table, options in self.table_reloptions + self.protected_reloptions:
            reloptions_payload = _json_object(
                self.env.execute_sql(
                    "SELECT reloptions FROM pg_class WHERE oid = "
                    f"to_regclass('{table}');"
                ),
                f"verify per-table analyze override on {table}",
            )
            installed = _reloptions_items(reloptions_payload["result"][0][0])
            for option, value in options:
                if installed.get(option) != value:
                    raise RuntimeError(
                        f"Per-table analyze override mismatch on {table}: "
                        f"expected {option}={value!r}, actual={installed.get(option)!r} "
                        f"in reloptions={reloptions_payload['result'][0][0]!r}"
                    )

    def _trigger_runtime(self) -> None:
        import math
        import time

        previous_autoanalyze = {}
        if self.require_completed_autoanalyze:
            for table in self.tables:
                payload = _json_object(
                    self.env.execute_sql(
                        "SELECT last_autoanalyze FROM pg_stat_user_tables "
                        f"WHERE relname = '{table}';"
                    ),
                    f"read auto-analyze baseline for {table}",
                )
                previous_autoanalyze[table] = payload["result"][0][0]

        for table in self.tables + self.noise_tables:
            reltuples = self._estimate_reltuples(table)
            rows_to_touch = max(
                250,
                min(
                    10000,
                    int(math.ceil(reltuples * float(self.scale_factor) + float(self.threshold) + 100)),
                ),
            )
            update_sql = self._trigger_update_sql(table, rows_to_touch)
            _require_sql_success(
                self.env.execute_sql(update_sql),
                f"trigger auto-analyze on table {table}",
            )
            role = "target" if table in self.tables else "noise"
            print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] "
                  f"Updated {rows_to_touch} rows in {table} ({role}) to trigger auto-analyze")

        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            self.analyze_activity = self.env.execute_sql(
                "SELECT pid, backend_type, state, wait_event_type, wait_event, left(query, 200) "
                "FROM pg_stat_activity WHERE pid <> pg_backend_pid() "
                "AND (backend_type = 'autovacuum worker' "
                "OR query ILIKE '%ANALYZE%' OR query ILIKE '%autovacuum%') "
                "ORDER BY query_start NULLS LAST;"
            )
            rows = _json_object(
                self.analyze_activity,
                "observe auto-analyze runtime activity",
            )["result"]
            if rows:
                break
            time.sleep(1)
        else:
            raise RuntimeError(
                "Auto-analyze activity did not become observable within 12 seconds: "
                f"tables={self.tables + self.noise_tables}, last_activity={self.analyze_activity}"
            )
        if self.require_completed_autoanalyze:
            self._wait_for_completed_autoanalyze(previous_autoanalyze)
        print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] "
              f"Fault injection complete. Auto-analyze storm is observable.")

    def _wait_for_completed_autoanalyze(self, previous_autoanalyze) -> None:
        import time

        pending = set(self.tables)
        deadline = time.monotonic() + self.completion_timeout_seconds
        while pending and time.monotonic() < deadline:
            for table in tuple(pending):
                payload = _json_object(
                    self.env.execute_sql(
                        "SELECT last_autoanalyze FROM pg_stat_user_tables "
                        f"WHERE relname = '{table}';"
                    ),
                    f"wait for completed auto-analyze on {table}",
                )
                current = payload["result"][0][0]
                if current is not None and current != previous_autoanalyze[table]:
                    pending.remove(table)
            if pending:
                time.sleep(1)
        if pending:
            raise RuntimeError(
                "Target auto-analyze did not complete within "
                f"{self.completion_timeout_seconds}s: pending={sorted(pending)}"
            )

    def _estimate_reltuples(self, table: str) -> float:
        raw = self.env.execute_sql(
            "SELECT COALESCE(reltuples, 0)::bigint "
            "FROM pg_class WHERE oid = to_regclass('%s');" % table.replace("'", "''")
        )
        payload = _json_object(raw, f"estimate reltuples for auto-analyze table {table}")
        if payload.get("status") == "error":
            raise RuntimeError(f"Could not estimate reltuples for table={table!r}: {raw}")
        rows = payload["result"]
        if not rows:
            raise RuntimeError(f"Could not estimate reltuples for table={table!r}: {raw}")
        return float(rows[0][0])

    def _trigger_update_sql(self, table: str, rows_to_touch: int) -> str:
        columns = {
            "customer": "c_birth_year",
            "store_sales": "ss_quantity",
            "store_returns": "sr_return_quantity",
            "customer_demographics": "cd_purchase_estimate",
            "inventory": "inv_quantity_on_hand",
            "web_sales": "ws_quantity",
            "catalog_sales": "cs_quantity",
        }
        column = columns.get(table)
        if not column:
            raise ValueError(f"No safe trigger column configured for table: {table}")
        return (
            f"UPDATE {table} SET {column} = {column} "
            f"WHERE ctid IN (SELECT ctid FROM {table} LIMIT {rows_to_touch});"
        )

    def recover(self, context: FaultLifecycleContext):
        print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] Recovering...")
        for setting in (
            "autovacuum_analyze_scale_factor",
            "autovacuum_analyze_threshold",
            "autovacuum_naptime",
        ):
            _require_sql_success(
                self.env.execute_sql(f"ALTER SYSTEM RESET {setting};"),
                f"recover auto-analyze setting {setting}",
            )
        for table, options in self.table_reloptions + self.protected_reloptions:
            option_names = ", ".join(option for option, _ in options)
            _require_sql_success(
                self.env.execute_sql(f"ALTER TABLE {table} RESET ({option_names});"),
                f"recover per-table analyze override on {table}",
            )
        _require_sql_success(
            self.env.execute_sql("SELECT pg_reload_conf();"),
            "reload recovered auto-analyze settings",
        )
        print(f"[FaultInjector:PgSystemFailureAutoAnalyzeStormInjector] "
              f"Recovery complete.")


class PgSystemFailureAutoAnalyzeStormScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_auto_analyze_storm'
    description = 'Simulates auto-analyze storm by setting extremely low analyze thresholds.'
    cases = (
        _PGSYSTEMFAILUREAUTOANALYZESTORMSCENARIO_CASE,
        _PGSYSTEMFAILUREAUTOANALYZESTORMSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureAutoAnalyzeStormCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgSystemFailureAutoAnalyzeStormInjector,
                config={
                    'tables': case.tables_2,
                    'noise_tables': case.noise_tables_2,
                    'scale_factor': case.scale_factor,
                    'threshold': case.threshold,
                    'naptime': case.naptime,
                    'table_reloptions': case.table_reloptions,
                    'protected_reloptions': case.protected_reloptions,
                    'require_completed_autoanalyze': case.require_completed_autoanalyze,
                    'completion_timeout_seconds': case.completion_timeout_seconds,
                },
            ),
        )
