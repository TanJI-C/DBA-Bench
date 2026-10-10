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
class PgSystemFailureDeadlockCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    dataset_scale: int
    table: str
    order_ids: tuple[int, ...]
    job_ids: tuple[int, ...]
    job_step_table: str
    worker_a: str
    worker_b: str
    order_ids_2: tuple[int, ...]
    job_ids_2: tuple[int, ...]
    trigger_rounds: int
    trigger_interval_seconds: float
    business_noise_repeats: int
    timeout_noise_count: int
    dashboard_noise_count: int
    inventory_noise_count: int
    # 良性锁等待链（健康近邻）。holder 长事务持行锁，waiter 在其上等待，
    # 与目标死锁链同时可见；Agent 必须按证据辨别目标链，且不得终止这两个会话。
    decoy_holder_app: str
    decoy_waiter_app: str
    decoy_table: str
    decoy_hold_seconds: float
    # 排序规则由 planner 视图持有，函数只消费视图；
    # 诊断需跨函数→视图→底层 steps 三层定位真正的排序来源。
    job_plan_view: str
    # 复合根因——反序规则的"所有权"在上游计划源表，同步例程周期
    # 回写 steps 并重部署消费例程。只改函数/只改 steps 会在下一个同步周期复发；
    # 只改上游不解除已发布反序也无法立即停损。Agent 必须识别完整因果链。
    plan_source_table: str
    plan_sync_function: str
    plan_sync_interval_seconds: float
    plan_sync_application: str
    # 仅 checkout 配置：同构健康孪生计划线。上游 planning service
    # 同一同步作业一并发布 checkout（反序、事故线）与 returns（全升序、健康线）两条
    # 业务线的计划；Agent 必须凭等待链/日志/函数绑定证据把事故定界到 checkout 计划源，
    # 修复 blast radius 不得覆盖健康线（OP 由 healthy_plan_line_preserved 验收业务真值）。
    healthy_plan_source_table: str | None = None
    healthy_job_step_table: str | None = None
    healthy_job_plan_view: str | None = None
    healthy_job_function: str | None = None
    healthy_job_ids: tuple[int, ...] = ()
    healthy_order_ids: tuple[int, ...] = ()
    healthy_worker_a: str = "batch_job_executor_5"
    healthy_worker_b: str = "batch_job_executor_6"
    # 仅 checkout 配置：计划同步调度层。sync 例程本体由
    # plan_sync_job_registry 控制面持有的模板周期重部署——直接改写/删除 sync 例程会被
    # 调度层在下个 tick 还原；完整修复必须处理控制面（status 停用/删行/改正模板）。
    plan_sync_registry_table: str | None = None
    # 两 case 共有：同一批处理计划线下的 staged 健康 job 对
    # ((job_a, job_b), (order_a, order_b))...，计划全升序、staged 不执行；steps/source
    # 中的同表健康对照行（n），事故对仍由 deadlock ERROR/函数绑定证据唯一锁定。
    extra_job_pairs: tuple[tuple[tuple[int, int], tuple[int, int]], ...] = ()
    # 两 case 共有：第二条同形态良性等待链（holder 长事务 + waiter 行锁等待），
    # 420s 自解；两链会话均在 SP 保护集内。
    decoy2_holder_app: str = "billing_snapshot"
    decoy2_waiter_app: str = "retention_purger"
    decoy2_table: str = "billing_snapshot_watermark"
    # 两 case 共有：应用连接池常驻空闲会话（(application_name, connections)...），
    # pg_stat_activity 未过滤快照中的确定性真实业务观测。
    idle_pool_apps: tuple[tuple[str, int], ...] = ()
    # RAISE 噪声按 case 截取，防止纯噪声数量淹没因果证据（easy 的 C_s 预算）。
    # Hard 档每发射 8 LOG + 8 WARNING 互不相同的真实业务观测。
    log_noise_per_repeat: int
    warning_noise_per_repeat: int

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureDeadlockForCheckoutOrderDeadlockScenarioCase(PgSystemFailureDeadlockCase):
    pass

def build_deadlock_distraction_profile(
    table: str = "orders",
    extra_order_ids: tuple = (2001, 2002, 3001, 3002, 4001, 4002),
) -> List[WorkloadProfile]:
    # system_failure deadlock 场景专用——让 runner 自己也跑 orders 表的
    # UPDATE，制造与故障事务**无关**的小 UPDATE 噪声（pg_stat_activity 里能看到
    # 这些 worker 持续跑 UPDATE orders 行 2001/2002/3001/3002，跟 1001/1002 互锁
    # 不相关）。目的是让 agent 看到"PG 上有大量 UPDATE 在跑"却不确定哪条是诱因。
    # qps 0.5 + 6 worker = 3 exec/秒，让 _recent 累积 18+ 条，agent 看得见但 grep 难筛。
    profiles = []
    for pair in [(2001, 2002), (3001, 3002), (4001, 4002)]:
        oid_a, oid_b = pair
        profiles.append(WorkloadProfile(
            name=f"distraction_update_{table}_{oid_a}_{oid_b}",
            sql=(
                f"UPDATE {table} "
                f"SET o_total_amount = o_total_amount + 0.01, "
                f"o_payload = 'distraction_worker' "
                f"WHERE o_id IN ({oid_a}, {oid_b})"
            ),
            qps=round(0.5 + 0.1 * (oid_a % 3), 3),
            tier="LIGHT",
            commit=False,
        ))
    return profiles

def build_deadlock_log_noise_profiles() -> List[WorkloadProfile]:
    # 这些 SQL 故意失败，让 PostgreSQL 在故障发生后继续写 ERROR/STATEMENT。
    # 比一次性 fake log 更能干扰 read_log 分页；不 commit，不改业务状态。
    # 难度校准：只保留一个极低速率 profile（约 2 行日志/分钟），live 噪声保持
    # 存在但不再淹没校准窗口里的 deadlock 因果证据（easy 的 C_s 预算）。
    return [
        WorkloadProfile(
            name="log_noise_statement_timeout_dashboard_refresh",
            sql="SET LOCAL statement_timeout = '25ms'; SELECT pg_sleep(0.2);",
            qps=0.02,
            tier="LOG_NOISE",
        ),
    ]

def build_default_mix_with_distraction() -> List[WorkloadProfile]:
    # 给 system_failure deadlock 用——同时跑 TPC-DS 默认 mix + orders 表
    # distraction profile，制造业务噪声让 agent 不能秒判根因。
    return (
        list(default_mix())
        + build_deadlock_distraction_profile()
        + build_deadlock_log_noise_profiles()
    )

_PGSYSTEMFAILUREDEADLOCKSCENARIO_CASE = PgSystemFailureDeadlockForCheckoutOrderDeadlockScenarioCase(
    case_id='checkout_order_deadlock',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "postgres deadlock detected",
                    "entity": "checkout_order_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed postgres deadlock detected"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "two transaction lock cycle",
                    "entity": "checkout_order_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed two transaction lock cycle"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "conflicting order and job statements identified",
                    "entity": "checkout_order_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed conflicting order and job statements identified"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "consistent lock order",
                    "entity": "checkout_order_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed consistent lock order"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "upstream scheduler redeploys the plan sync from plan_sync_job_registry and the sync republishes the conflicting ordering",
                    "entity": "checkout_order_deadlock",
                    "evidence": [
                        "scripted diagnostic actions observed the scheduler redeploying the plan sync and the sync republishing the conflicting ordering"
                    ]
                }
            ]
        },
        "outcome": {
            "changes": [
                "pause the plan sync scheduler job, enforce consistent lock order, correct the upstream plan source, and republish the plan package"
            ],
            "verification": [
                "worker A and worker B formed the lock cycle"
            ]
        },
        "summary": "The scripted mock completed its case-specific diagnosis and verification."
    },
    case_no=0,
    evaluator=PgSystemFailureDeadlockForCheckoutOrderDeadlockEvaluatorCase,
    runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
    base_image_name='aiopsbench-pg-tpcds:latest',
    workload_tag='tpcds',
    dataset_scale=1,
    title='Simulates intermittent checkout failures caused by non-canonical batch lock ordering.',
    # OP 依赖 Agent 实际落地修复：
    # 题面必须给出业务目标（批处理可靠完成）并授权事故范围内的库端变更。
    alert='Alert: Order reporting dashboards intermittently show stale data while checkout-api error rate briefly spikes. Affected requests return generic 500s, and customer support reports that retrying the same order a few seconds later usually succeeds. Reporting, archiving, and checkout batch jobs overlap during the incident window. Separate the customer-impacting write failure from background batch noise, make the checkout batch jobs complete reliably again, and submit an evidence-backed root cause and prevention plan. Within this incident scope you are authorized to apply the database-side changes needed to stop these failures; do not touch unrelated business objects.',
    initial_state={'status': 'degraded', 'symptom': 'intermittent_checkout_500s'},
    expected_target={'status': 'analyzed', 'deadlock_chain': 'extracted', 'recommendation': 'consistent_lock_order'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_default_mix_with_distraction()),
        worker_count=6,
        seed=0,
        start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
    ),
    table='orders',
    order_ids=(1001, 1002),
    job_ids=(101, 102),
    job_step_table='checkout_job_steps',
    # blocker 会话名不自报 pair 身份，pg_stat_activity 里只看到
    # 两个中性批处理执行器。
    worker_a='batch_job_executor_1',
    worker_b='batch_job_executor_2',
    order_ids_2=(1001, 1002),
    job_ids_2=(101, 102),
    trigger_rounds=3,
    trigger_interval_seconds=30.0,
    business_noise_repeats=2,
    timeout_noise_count=2,
    dashboard_noise_count=3,
    inventory_noise_count=2,
    decoy_holder_app='reporting_archiver',
    decoy_waiter_app='maintenance_purger',
    decoy_table='reporting_archive_watermark',
    decoy_hold_seconds=420.0,
    job_plan_view='checkout_job_plan',
    plan_source_table='checkout_plan_source',
    plan_sync_function='checkout_plan_sync',
    plan_sync_interval_seconds=45.0,
    plan_sync_application='plan_sync_scheduler',
    # 同构健康孪生计划线。returns 线（job 201/202 → orders 5001/5002）
    # 由同一 checkout_plan_sync 一并发布，计划全升序、业务无死锁推进；orders 行号刻意
    # 避开 distraction worker 的 2001/2002/3001/3002/4001/4002。会话名与 checkout 执行器
    # 同为中性 batch_job_executor_*，Agent 只能靠语句/函数/job_id 绑定证据定界事故实体。
    healthy_plan_source_table='returns_plan_source',
    healthy_job_step_table='returns_job_steps',
    healthy_job_plan_view='returns_job_plan',
    healthy_job_function='returns_process_job',
    healthy_job_ids=(201, 202),
    healthy_order_ids=(5001, 5002),
    # sync 例程本体由调度层从 plan_sync_job_registry 模板周期重部署；
    # 仅"替换 sync 例程"或"DROP sync"的修复在重部署面前不完整。
    plan_sync_registry_table='plan_sync_job_registry',
    # 同批处理计划线 staged 健康 job 对、第二条良性等待链、
    # 连接池空闲会话——关键工具未过滤结果中的同域非因果观测（n）。
    extra_job_pairs=(
        ((107, 108), (6001, 6002)),
        ((109, 110), (7001, 7002)),
    ),
    idle_pool_apps=(('checkout_api_pool', 3), ('reporting_pool', 2)),
    log_noise_per_repeat=8,
    warning_noise_per_repeat=8,
    # 校准（未过滤实测，机械口径）：
    # read_log 29/44、function 1/0、view 1/0、steps 4/8、source 4/8、syncdef 1/0、
    # returns_source 0/4、registry 1/0、activity 0/19、topsql 3/5 → m=45 n=107，
    # rho_s=0.296，C_s=0.704（≥0.5）→ hard。D_s=6。
    difficulty=DifficultyCalibration(
        diagnostic_depth=6,
        environmental_complexity=0.704,
        reference_run_ids=(
            'reference-263__pg_system_failure_deadlock__checkout_order_deadlock__mock__r001/attempts/001/trace.json',
        ),
    ),
)

@dataclass(frozen=True, slots=True, kw_only=True)
class PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleScenarioCase(
    PgSystemFailureDeadlockCase
):
    pass


_PGSYSTEMFAILUREDEADLOCKSCENARIO_SIMPLE_CASE = (
    PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleScenarioCase(
        case_id='single_order_pair_deadlock_simple',
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "postgres deadlock detected",
                        "entity": "single_order_pair_deadlock_simple",
                        "evidence": [
                            "scripted diagnostic actions observed postgres deadlock detected"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "two transaction lock cycle",
                        "entity": "single_order_pair_deadlock_simple",
                        "evidence": [
                            "scripted diagnostic actions observed two transaction lock cycle"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "conflicting order and job statements identified",
                        "entity": "single_order_pair_deadlock_simple",
                        "evidence": [
                            "scripted diagnostic actions observed conflicting order and job statements identified"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "consistent lock order",
                        "entity": "single_order_pair_deadlock_simple",
                        "evidence": [
                            "scripted diagnostic actions observed consistent lock order"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "upstream plan sync republishes the conflicting ordering",
                        "entity": "single_order_pair_deadlock_simple",
                        "evidence": [
                            "scripted diagnostic actions observed upstream plan sync republishing the conflicting ordering"
                        ]
                    }
                ]
            },
            "outcome": {
                "changes": [
                    "enforce consistent lock order and retry the victim transaction"
                ],
                "verification": [
                    "worker A and worker B formed the lock cycle"
                ]
            },
            "summary": "The scripted mock completed its case-specific diagnosis and verification."
        },
        case_no=1,
        evaluator=PgSystemFailureDeadlockForSingleOrderPairDeadlockSimpleEvaluatorCase,
        runtime=PostgresCaseRuntime(resources=_DEFAULT_SYSTEM_FAILURE_RESOURCES),
        difficulty=DifficultyCalibration(
            diagnostic_depth=5,
            environmental_complexity=0.578,
            reference_run_ids=(
                'reference-263__pg_system_failure_deadlock__single_order_pair_deadlock_simple__mock__r001/attempts/001/trace.json',
            ),
        ),
        base_image_name='aiopsbench-pg-tpcds:latest',
        workload_tag='tpcds',
        dataset_scale=1,
        title='A single checkout order pair deadlocks under inconsistent batch ordering.',
        # 题面只保留业务症状，不点名 deadlock / 冲突语句 / 排序规则。
        # 根因假设、诊断路径和预防方向由 Agent 自行从环境证据建立。
        # 题面给出业务目标与事故范围内的库端变更授权。
        alert=(
            'Alert: two checkout batch jobs intermittently fail with retryable 500 errors '
            'while the database itself stays available; retrying the same batch a few '
            'seconds later usually succeeds. A low-rate reporting query is also running '
            'on the same database. Make both checkout batch jobs complete reliably again, '
            'and submit an evidence-backed root cause with your prevention plan. Within '
            'this incident scope you are authorized to apply the database-side changes '
            'needed to stop these failures; do not touch unrelated business objects.'
        ),
        initial_state={
            'status': 'degraded',
            'symptom': 'two_checkout_batches_retry',
            'database': 'available',
        },
        expected_target={
            'status': 'analyzed',
            'deadlock_chain': 'single_order_pair_extracted',
            'recommendation': 'consistent_lock_order',
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=(
                WorkloadProfile(
                    name='checkout_calendar_health_probe',
                    sql='SELECT count(*) FROM date_dim WHERE d_year = 2001;',
                    qps=0.1,
                    tier='LIGHT',
                    application_name='checkout_health_probe',
                ),
            ),
            worker_count=1,
            seed=0x2F02,
            start_phase=BackgroundWorkloadStartPhase.BEFORE_FAULTS,
        ),
        table='orders',
        order_ids=(1101, 1102),
        job_ids=(201, 202),
        job_step_table='checkout_pair_steps',
        # 中性会话身份，同 checkout case。
        worker_a='batch_job_executor_3',
        worker_b='batch_job_executor_4',
        order_ids_2=(1101, 1102),
        job_ids_2=(201, 202),
        trigger_rounds=1,
        trigger_interval_seconds=0.0,
        business_noise_repeats=1,
        timeout_noise_count=1,
        dashboard_noise_count=1,
        inventory_noise_count=1,
        decoy_holder_app='reporting_archiver',
        decoy_waiter_app='maintenance_purger',
        decoy_table='reporting_archive_watermark',
        decoy_hold_seconds=420.0,
        job_plan_view='checkout_pair_plan',
        plan_source_table='checkout_plan_source',
        plan_sync_function='checkout_plan_sync',
        plan_sync_interval_seconds=45.0,
        plan_sync_application='plan_sync_scheduler',
        # simple case 与 checkout 共享同域噪声扩展（staged 健康
        # job 对、第二条良性等待链、池会话）；调度层机制仅 checkout 配置。
        extra_job_pairs=(
            ((107, 108), (6001, 6002)),
            ((109, 110), (7001, 7002)),
        ),
        idle_pool_apps=(('checkout_api_pool', 2), ('reporting_pool', 1)),
        log_noise_per_repeat=8,
        warning_noise_per_repeat=8,
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

class PgSystemFailureDeadlockInjector(BaseFaultInjector):
    """
    模拟 PostgreSQL 订单更新死锁。
    两个会话按相反顺序更新同一组订单行，触发 deadlock detector；
    故障本身会被 PostgreSQL 自动解除，Agent 需要从错误日志中提取证据链。
    """

    DEFAULT_WORKER_A = "checkout_worker_a"
    DEFAULT_WORKER_B = "checkout_worker_b"

    def __init__(self):
        self._stop_event = None
        self._trigger_thread = None
        self._sync_thread = None
        self._connections = []
        self._log_offsets = {}
        self._log_text = ""
        self._published_log_text = ""

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._install_persistent_state()
        self._activate_runtime()

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        with env.metrics_hidden():
            self._verify_persistent_state()
        self._activate_runtime()

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        order_ids = config['order_ids']
        if len(order_ids) != 2:
            raise ValueError("PgSystemFailureDeadlockInjector requires exactly two order_ids.")
        self.order_ids = [int(order_ids[0]), int(order_ids[1])]
        job_ids = config['job_ids']
        if len(job_ids) != 2:
            raise ValueError("PgSystemFailureDeadlockInjector requires exactly two job_ids.")
        self.job_ids = [int(job_ids[0]), int(job_ids[1])]
        self.job_step_table = _validate_sql_identifier(config['job_step_table'], "job_step_table")
        self.worker_a = config['worker_a']
        self.worker_b = config['worker_b']
        self.trigger_rounds = int(config['trigger_rounds'])
        self.trigger_interval_seconds = float(config['trigger_interval_seconds'])
        self.business_noise_repeats = int(config['business_noise_repeats'])
        self.timeout_noise_count = int(config['timeout_noise_count'])
        self.dashboard_noise_count = int(config['dashboard_noise_count'])
        self.inventory_noise_count = int(config['inventory_noise_count'])
        self.decoy_holder_app = str(config['decoy_holder_app'])
        self.decoy_waiter_app = str(config['decoy_waiter_app'])
        self.decoy_table = _validate_sql_identifier(config['decoy_table'], "decoy_table")
        self.decoy_hold_seconds = float(config['decoy_hold_seconds'])
        self.job_plan_view = _validate_sql_identifier(config['job_plan_view'], "job_plan_view")
        self.plan_source_table = _validate_sql_identifier(config['plan_source_table'], "plan_source_table")
        self.plan_sync_function = _validate_sql_identifier(config['plan_sync_function'], "plan_sync_function")
        self.plan_sync_interval_seconds = float(config['plan_sync_interval_seconds'])
        self.plan_sync_application = str(config['plan_sync_application'])
        if self.plan_sync_interval_seconds <= 0:
            raise ValueError("plan_sync_interval_seconds must be positive")
        # 健康孪生计划线，仅 checkout case 配置；未配置时全部健康路径关闭，
        # simple case 行为不变。
        self.healthy_plan_source_table = (
            _validate_sql_identifier(config['healthy_plan_source_table'], "healthy_plan_source_table")
            if config.get('healthy_plan_source_table') else None
        )
        self.healthy_job_step_table = (
            _validate_sql_identifier(config['healthy_job_step_table'], "healthy_job_step_table")
            if config.get('healthy_job_step_table') else None
        )
        self.healthy_job_plan_view = (
            _validate_sql_identifier(config['healthy_job_plan_view'], "healthy_job_plan_view")
            if config.get('healthy_job_plan_view') else None
        )
        self.healthy_job_function = (
            _validate_sql_identifier(config['healthy_job_function'], "healthy_job_function")
            if config.get('healthy_job_function') else None
        )
        healthy_job_ids = config.get('healthy_job_ids') or ()
        healthy_order_ids = config.get('healthy_order_ids') or ()
        if (self.healthy_plan_source_table or self.healthy_job_step_table) and not (
            self.healthy_plan_source_table
            and self.healthy_job_step_table
            and self.healthy_job_plan_view
            and self.healthy_job_function
            and len(healthy_job_ids) == 2
            and len(healthy_order_ids) == 2
        ):
            raise ValueError(
                "healthy plan line requires source/steps/view/function tables, "
                "exactly two healthy job ids and two healthy order ids"
            )
        self.healthy_job_ids = [int(healthy_job_ids[0]), int(healthy_job_ids[1])] if healthy_job_ids else []
        self.healthy_order_ids = [int(healthy_order_ids[0]), int(healthy_order_ids[1])] if healthy_order_ids else []
        self.healthy_worker_a = str(config.get('healthy_worker_a') or "batch_job_executor_5")
        self.healthy_worker_b = str(config.get('healthy_worker_b') or "batch_job_executor_6")
        # 调度层控制面（仅 checkout 配置；未配置时使用直接周期同步语义）。
        self.plan_sync_registry_table = (
            _validate_sql_identifier(config['plan_sync_registry_table'], "plan_sync_registry_table")
            if config.get('plan_sync_registry_table') else None
        )
        # staged 健康 job 对、第二条良性等待链、池会话（两 case 共有）。
        self.extra_job_pairs = tuple(
            ((int(job_a), int(job_b)), (int(order_a), int(order_b)))
            for (job_a, job_b), (order_a, order_b) in (config.get('extra_job_pairs') or ())
        )
        self.decoy2_holder_app = str(config.get('decoy2_holder_app') or 'billing_snapshot')
        self.decoy2_waiter_app = str(config.get('decoy2_waiter_app') or 'retention_purger')
        self.decoy2_table = _validate_sql_identifier(
            config.get('decoy2_table') or 'billing_snapshot_watermark', "decoy2_table"
        )
        self.idle_pool_apps = tuple(
            (str(name), int(count)) for name, count in (config.get('idle_pool_apps') or ())
        )
        self.log_noise_per_repeat = int(config['log_noise_per_repeat'])
        self.warning_noise_per_repeat = int(config['warning_noise_per_repeat'])
        if self.trigger_rounds < 1:
            raise ValueError("trigger_rounds must be at least 1")

    def _install_persistent_state(self) -> None:
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Preparing order rows in {self.table}..."
        )
        self._ensure_order_rows(self.env)
        self._ensure_extra_business_order_rows(self.env)
        self._ensure_healthy_order_rows(self.env)
        self._ensure_checkout_jobs(self.env)
        self._ensure_job_plan_view(self.env)
        self._ensure_checkout_function(self.env)
        self._ensure_plan_source(self.env)
        self._ensure_healthy_plan_line(self.env)
        sync_ddl = self._ensure_plan_sync(self.env)
        self._ensure_plan_sync_registry(self.env, sync_ddl)
        self._ensure_red_herring_functions(self.env)
        self._ensure_decoy_table(self.env)
        self._ensure_decoy2_table(self.env)

    def _extra_order_rows(self):
        # staged 健康 job 对引用的业务订单。行号避开事故（1001/1002、
        # 1101/1102）、健康线（5001/5002）与 distraction worker（2001-4002）。
        rows = []
        for (_job_a, _job_b), (order_a, order_b) in self.extra_job_pairs:
            rows.extend((order_a, order_b))
        return sorted(set(rows))

    def _ensure_extra_business_order_rows(self, env):
        order_ids = self._extra_order_rows()
        if not order_ids:
            return
        values = ", ".join(
            "({order_id}, 3, 1, {customer}, 1, 150.00, now(), 'order-{tag}')".format(
                order_id=order_id, customer=701 + index, tag=chr(ord("e") + index)
            )
            for index, order_id in enumerate(order_ids)
        )
        env.execute_sql(f"""
            INSERT INTO {self.table} (
                o_id, o_w_id, o_d_id, o_c_id, o_carrier_id,
                o_total_amount, o_entry_d, o_payload
            )
            VALUES {values}
            ON CONFLICT (o_id) DO UPDATE
            SET o_total_amount = EXCLUDED.o_total_amount,
                o_entry_d = EXCLUDED.o_entry_d,
                o_payload = EXCLUDED.o_payload;
        """)
        env.execute_sql(f"ANALYZE {self.table};")

    def _extra_step_rows(self, table_kind: str):
        # staged 健康 job 对的 steps/source 行（计划全升序；source 列与表语义一致）。
        if not self.extra_job_pairs:
            return ""
        default_source = "checkout_planner" if table_kind == "steps" else None
        values = []
        for (job_a, job_b), (order_a, order_b) in self.extra_job_pairs:
            for job_id, order_id in ((job_a, order_a), (job_a, order_b), (job_b, order_a), (job_b, order_b)):
                values.append((job_id, 10 if order_id == order_a else 20, order_id))
        rendered = []
        for job_id, rank, order_id in values:
            if table_kind == "steps":
                rendered.append(
                    f"({job_id}, {rank}, {order_id}, '{default_source}')"
                )
            else:
                rendered.append(
                    f"({job_id}, {rank}, {order_id}, 'upstream-2026.36')"
                )
        return ",\n                ".join(rendered)

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                "SELECT to_regclass('public.%s'), to_regclass('public.%s'), "
                "to_regclass('public.%s'), to_regclass('public.%s'), "
                "to_regprocedure('process_checkout_job(integer)'), "
                "to_regprocedure('%s()');"
                % (
                    self.table,
                    self.job_step_table,
                    self.job_plan_view,
                    self.plan_source_table,
                    self.plan_sync_function,
                )
            ),
            "verify deadlock fault image objects",
        )
        row = payload["result"][0]
        if any(value is None for value in row):
            raise RuntimeError(
                f"Deadlock fault image is missing persistent objects: "
                f"table={self.table}, job_step_table={self.job_step_table}, "
                f"plan_source_table={self.plan_source_table}, "
                f"plan_sync_function={self.plan_sync_function}, objects={row}"
            )
        if self.plan_sync_registry_table:
            staged_job_ids = ", ".join(
                str(job_a)
                for (job_a, _job_b), _orders in self.extra_job_pairs
            ) or "0"
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT to_regclass('public.%s'), "
                    "(SELECT count(*) FROM %s WHERE job_id IN (%s));"
                    % (
                        self.plan_sync_registry_table,
                        self.job_step_table,
                        staged_job_ids,
                    )
                ),
                "verify plan sync scheduler registry",
            )
            row = payload["result"][0]
            if row[0] is None or int(row[1] or 0) != 2 * len(self.extra_job_pairs):
                raise RuntimeError(
                    f"Plan sync scheduler registry verification failed: objects={row}, "
                    f"expected staged job rows={2 * len(self.extra_job_pairs)}"
                )
        if self.healthy_plan_source_table:
            payload = _json_object(
                self.env.execute_sql(
                    "SELECT to_regclass('public.%s'), to_regclass('public.%s'), "
                    "to_regclass('public.%s'), to_regprocedure('%s(integer)');"
                    % (
                        self.healthy_plan_source_table,
                        self.healthy_job_step_table,
                        self.healthy_job_plan_view,
                        self.healthy_job_function,
                    )
                ),
                "verify healthy plan line objects",
            )
            row = payload["result"][0]
            if any(value is None for value in row):
                raise RuntimeError(
                    f"Healthy plan line is missing persistent objects: objects={row}"
                )

    def _activate_runtime(self) -> None:
        import threading

        self._connections = []
        self._errors = []

        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Triggering cross-lock update on {self.table}..."
        )
        with self.env.metrics_hidden():
            self._run_red_herring_queries(self.env)
        # 激活时先执行一次计划同步——确定性地发布反序计划并留下
        # 同步证据行（RAISE LOG），随后由周期循环重复。初始同步必须在
        # metrics_hidden 之外执行：同步证据行是 Agent-visible evidence，
        # 不能被日志隐藏窗口吞掉（与 RAISE 噪声同窗可见的合同一致）。
        # checkout 的激活同步以完整调度 tick 形态执行
        # （重部署 + 重部署证据行 + 执行）——调度层所有权的证据与 sync 证据行
        # 同窗确定性可见。
        if self.plan_sync_registry_table:
            self._run_scheduler_tick_once(self.env)
        else:
            self._run_plan_sync_once(self.env)
        self._emit_business_noise_logs(self.env)
        # 批处理协调器心跳（dispatch/complete），同窗真实业务日志。
        self._emit_batch_coordinator_logs(self.env)
        deployment = self.env.get_deployment()
        self._log_offsets = deployment.postgres_log_sizes()
        self._log_text = ""
        self._stop_event = threading.Event()
        self._trigger_thread = threading.Thread(
            target=self._periodic_trigger_loop,
            args=(self.env,),
            daemon=True,
        )
        self._trigger_thread.start()
        if self.plan_sync_registry_table:
            self._start_plan_sync_scheduler_loop()
        else:
            self._start_plan_sync_loop()
        # 与目标死锁同窗的良性锁等待链。holder 长事务持
        # decoy_table 行锁，waiter 在其上等待；二者与 checkout 事故无关、无
        # deadlock ERROR，且在 decoy_hold_seconds 后自行解除。
        # 第二条同形态良性链（不同表/会话名），排除推理必须逐链进行。
        self._start_decoy_chain(
            self.decoy_holder_app, self.decoy_waiter_app, self.decoy_table
        )
        self._start_decoy_chain(
            self.decoy2_holder_app, self.decoy2_waiter_app, self.decoy2_table
        )
        # 应用连接池常驻空闲会话（确定性真实业务观测）。
        self._open_idle_pool_connections(self.env)
        # Docker/PG log delivery can lag the detector while the fault is
        # already real; this is an admission wait, not an incident duration.
        self._wait_until_log_visible(self.env, timeout_seconds=30)
        print("[FaultInjector:PgSystemFailureDeadlockInjector] Deadlock incident recorded in PostgreSQL logs.")

    def _ensure_order_rows(self, env):
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                o_id integer PRIMARY KEY,
                o_w_id integer NOT NULL,
                o_d_id integer NOT NULL,
                o_c_id integer NOT NULL,
                o_carrier_id integer NOT NULL,
                o_total_amount numeric(12, 2) NOT NULL,
                o_entry_d timestamp NOT NULL,
                o_payload text NOT NULL
            );
        """)
        env.execute_sql(f"""
            INSERT INTO {self.table} (
                o_id, o_w_id, o_d_id, o_c_id, o_carrier_id,
                o_total_amount, o_entry_d, o_payload
            )
            VALUES
                ({self.order_ids[0]}, 1, 1, 501, 1, 100.00, now(), repeat('order-a', 16)),
                ({self.order_ids[1]}, 1, 1, 502, 1, 200.00, now(), repeat('order-b', 16))
            ON CONFLICT (o_id) DO UPDATE
            SET o_total_amount = EXCLUDED.o_total_amount,
                o_entry_d = EXCLUDED.o_entry_d,
                o_payload = EXCLUDED.o_payload;
        """)
        env.execute_sql(f"ANALYZE {self.table};")

    def _ensure_checkout_jobs(self, env):
        env.execute_sql(f"DROP VIEW IF EXISTS {self.job_plan_view};")
        env.execute_sql(f"DROP TABLE IF EXISTS {self.job_step_table};")
        env.execute_sql(f"""
            CREATE TABLE {self.job_step_table} (
                job_id integer NOT NULL,
                priority_rank integer NOT NULL,
                order_id integer NOT NULL REFERENCES {self.table}(o_id),
                source text NOT NULL DEFAULT 'checkout_planner',
                PRIMARY KEY (job_id, priority_rank)
            );
        """)
        env.execute_sql(f"""
            DELETE FROM {self.job_step_table}
            WHERE job_id IN ({self.job_ids[0]}, {self.job_ids[1]});
            INSERT INTO {self.job_step_table} (job_id, priority_rank, order_id, source)
            VALUES
                ({self.job_ids[0]}, 10, {self.order_ids[0]}, 'checkout_planner'),
                ({self.job_ids[0]}, 20, {self.order_ids[1]}, 'checkout_planner'),
                ({self.job_ids[1]}, 10, {self.order_ids[1]}, 'checkout_planner'),
                ({self.job_ids[1]}, 20, {self.order_ids[0]}, 'checkout_planner'){self._extra_step_values("steps")};
        """)
        env.execute_sql(f"ANALYZE {self.job_step_table};")

    def _extra_step_values(self, table_kind: str) -> str:
        rows = self._extra_step_rows(table_kind)
        if not rows:
            return ""
        return ",\n                " + rows

    def _connect(self, env, application_name: str):
        import psycopg2

        conn = psycopg2.connect(
            host=env.host,
            port=env.port,
            user=env.user,
            password=env.password,
            dbname=env.dbname,
            application_name=application_name,
            connect_timeout=5,
        )
        conn.autocommit = False
        self._connections.append(conn)
        return conn

    def _ensure_job_plan_view(self, env):
        # planner 视图。排序规则的所有权在计划层，函数只消费视图；
        # 当前规则是 pass-through（plan_rank = priority_rank）。
        env.execute_sql(f"""
            CREATE OR REPLACE VIEW {self.job_plan_view} AS
            SELECT job_id, order_id, priority_rank AS plan_rank, source
            FROM {self.job_step_table};
        """)

    def _checkout_function_body(self) -> str:
        # 函数体模板化。sync 例程重部署"计划包例程"时必须与 install 完全一致，
        # 保证快照 save/use 与周期重部署的函数语义稳定。
        return f"""
            DECLARE
                step record;
            BEGIN
                FOR step IN
                    SELECT order_id
                    FROM {self.job_plan_view}
                    WHERE job_id = p_job_id
                    ORDER BY plan_rank
                LOOP
                    UPDATE {self.table}
                    SET o_total_amount = o_total_amount + 1,
                        o_payload = p_job_id::text
                    WHERE o_id = step.order_id;

                    PERFORM pg_sleep(0.25);
                END LOOP;
            END
        """

    def _checkout_function_ddl(self, dollar_tag: str = "$$") -> str:
        return (
            "CREATE OR REPLACE FUNCTION process_checkout_job(p_job_id integer)\n"
            "RETURNS void\n"
            "LANGUAGE plpgsql\n"
            f"AS {dollar_tag}{self._checkout_function_body()}{dollar_tag};\n"
        )

    def _ensure_checkout_function(self, env):
        env.execute_sql("DROP FUNCTION IF EXISTS checkout_apply_batch(text);")
        env.execute_sql(self._checkout_function_ddl())

    def _ensure_plan_source(self, env):
        # 上游计划源表。upstream planning service 持有的反序
        # 规则先落到这张 staging 表，再由 checkout_plan_sync 周期发布到 DB。
        # last_synced_at 由每次同步刷新，是"数据由回写持有"的 Agent-visible 证据。
        plan_version = "upstream-2026.36"
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.plan_source_table} (
                job_id integer NOT NULL,
                upstream_priority integer NOT NULL,
                order_id integer NOT NULL REFERENCES {self.table}(o_id),
                plan_version text NOT NULL,
                last_synced_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (job_id, upstream_priority)
            );
        """)
        env.execute_sql(f"""
            DELETE FROM {self.plan_source_table};
            INSERT INTO {self.plan_source_table}
                (job_id, upstream_priority, order_id, plan_version)
            VALUES
                ({self.job_ids[0]}, 10, {self.order_ids[0]}, '{plan_version}'),
                ({self.job_ids[0]}, 20, {self.order_ids[1]}, '{plan_version}'),
                ({self.job_ids[1]}, 10, {self.order_ids[1]}, '{plan_version}'),
                ({self.job_ids[1]}, 20, {self.order_ids[0]}, '{plan_version}'){self._extra_step_values("source")};
        """)
        env.execute_sql(f"ANALYZE {self.plan_source_table};")

    def _ensure_healthy_order_rows(self, env):
        # 健康线业务订单。行号避开 checkout（1001/1002）与 distraction
        # worker（2001-4002），保证健康线与事故线无共享行、无锁交互。
        if not self.healthy_plan_source_table:
            return
        env.execute_sql(f"""
            INSERT INTO {self.table} (
                o_id, o_w_id, o_d_id, o_c_id, o_carrier_id,
                o_total_amount, o_entry_d, o_payload
            )
            VALUES
                ({self.healthy_order_ids[0]}, 2, 1, 601, 1, 300.00, now(), repeat('order-c', 16)),
                ({self.healthy_order_ids[1]}, 2, 1, 602, 1, 400.00, now(), repeat('order-d', 16))
            ON CONFLICT (o_id) DO UPDATE
            SET o_total_amount = EXCLUDED.o_total_amount,
                o_entry_d = EXCLUDED.o_entry_d,
                o_payload = EXCLUDED.o_payload;
        """)

    def _healthy_function_body(self) -> str:
        # 健康线消费例程与 process_checkout_job 同构（按 plan_rank 循环
        # UPDATE + pg_sleep），区别仅在底层计划本身是全升序的健康计划。
        return f"""
            DECLARE
                step record;
            BEGIN
                FOR step IN
                    SELECT order_id
                    FROM {self.healthy_job_plan_view}
                    WHERE job_id = p_job_id
                    ORDER BY plan_rank
                LOOP
                    UPDATE {self.table}
                    SET o_total_amount = o_total_amount + 1,
                        o_payload = p_job_id::text
                    WHERE o_id = step.order_id;

                    PERFORM pg_sleep(0.25);
                END LOOP;
            END
        """

    def _healthy_function_ddl(self, dollar_tag: str = "$$") -> str:
        return (
            f"CREATE OR REPLACE FUNCTION {self.healthy_job_function}(p_job_id integer)\n"
            "RETURNS void\n"
            "LANGUAGE plpgsql\n"
            f"AS {dollar_tag}{self._healthy_function_body()}{dollar_tag};\n"
        )

    def _ensure_healthy_plan_line(self, env):
        # 健康孪生计划线——结构与 checkout 线完全同构，仅数据内容
        # （全升序、无死锁）与关联订单对不同。install 先发布一份 returns_planner
        # 初版 steps；激活时 checkout_plan_sync 的双源分支会以 plan_sync:<version>
        # 重灌并重部署，与 checkout 线形态一致。
        if not self.healthy_plan_source_table:
            return
        plan_version = "upstream-2026.36"
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {self.healthy_plan_source_table} (
                job_id integer NOT NULL,
                upstream_priority integer NOT NULL,
                order_id integer NOT NULL REFERENCES {self.table}(o_id),
                plan_version text NOT NULL,
                last_synced_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (job_id, upstream_priority)
            );
        """)
        env.execute_sql(f"""
            DELETE FROM {self.healthy_plan_source_table};
            INSERT INTO {self.healthy_plan_source_table}
                (job_id, upstream_priority, order_id, plan_version)
            VALUES
                ({self.healthy_job_ids[0]}, 10, {self.healthy_order_ids[0]}, '{plan_version}'),
                ({self.healthy_job_ids[0]}, 20, {self.healthy_order_ids[1]}, '{plan_version}'),
                ({self.healthy_job_ids[1]}, 10, {self.healthy_order_ids[0]}, '{plan_version}'),
                ({self.healthy_job_ids[1]}, 20, {self.healthy_order_ids[1]}, '{plan_version}');
        """)
        env.execute_sql(f"ANALYZE {self.healthy_plan_source_table};")
        env.execute_sql(f"DROP VIEW IF EXISTS {self.healthy_job_plan_view};")
        env.execute_sql(f"DROP TABLE IF EXISTS {self.healthy_job_step_table};")
        env.execute_sql(f"""
            CREATE TABLE {self.healthy_job_step_table} (
                job_id integer NOT NULL,
                priority_rank integer NOT NULL,
                order_id integer NOT NULL REFERENCES {self.table}(o_id),
                source text NOT NULL DEFAULT 'returns_planner',
                PRIMARY KEY (job_id, priority_rank)
            );
        """)
        env.execute_sql(f"""
            INSERT INTO {self.healthy_job_step_table} (job_id, priority_rank, order_id, source)
            VALUES
                ({self.healthy_job_ids[0]}, 10, {self.healthy_order_ids[0]}, 'returns_planner'),
                ({self.healthy_job_ids[0]}, 20, {self.healthy_order_ids[1]}, 'returns_planner'),
                ({self.healthy_job_ids[1]}, 10, {self.healthy_order_ids[0]}, 'returns_planner'),
                ({self.healthy_job_ids[1]}, 20, {self.healthy_order_ids[1]}, 'returns_planner');
        """)
        env.execute_sql(f"""
            CREATE OR REPLACE VIEW {self.healthy_job_plan_view} AS
            SELECT job_id, order_id, priority_rank AS plan_rank, source
            FROM {self.healthy_job_step_table};
        """)
        env.execute_sql(self._healthy_function_ddl())

    def _plan_sync_ddl(self) -> str:
        # sync 例程定义。DDL 文本是单一来源：install 直接执行，同时作为
        # plan_sync_job_registry.template_definition 的初始模板——调度层重部署安装的例程
        # 与装机版本逐字一致，保证快照 save/use 与周期重部署语义稳定。
        inner_function_ddl = self._checkout_function_ddl(dollar_tag="$fn$")
        if self.healthy_plan_source_table:
            declares = "synced integer; synced_returns integer;"
            healthy_publish = f"""
                DELETE FROM {self.healthy_job_step_table}
                WHERE job_id IN (SELECT DISTINCT job_id FROM {self.healthy_plan_source_table});

                INSERT INTO {self.healthy_job_step_table} (job_id, priority_rank, order_id, source)
                SELECT job_id, upstream_priority, order_id,
                       'plan_sync:' || plan_version
                FROM {self.healthy_plan_source_table}
                ORDER BY job_id, upstream_priority;

                GET DIAGNOSTICS synced_returns = ROW_COUNT;

                {self._healthy_function_ddl(dollar_tag="$fn$")}

                UPDATE {self.healthy_plan_source_table} SET last_synced_at = now();
            """
            healthy_log = (
                "RAISE LOG 'checkout_plan_sync: republished % returns plan steps from "
                f"{self.healthy_plan_source_table} and shipped the returns plan package', "
                "synced_returns;"
            )
        else:
            declares = "synced integer;"
            healthy_publish = ""
            healthy_log = ""
        return f"""
            CREATE OR REPLACE FUNCTION {self.plan_sync_function}()
            RETURNS integer
            LANGUAGE plpgsql
            AS $plan_sync$
            DECLARE
                {declares}
            BEGIN
                DELETE FROM {self.job_step_table}
                WHERE job_id IN (SELECT DISTINCT job_id FROM {self.plan_source_table});

                INSERT INTO {self.job_step_table} (job_id, priority_rank, order_id, source)
                SELECT job_id, upstream_priority, order_id,
                       'plan_sync:' || plan_version
                FROM {self.plan_source_table}
                ORDER BY job_id, upstream_priority;

                GET DIAGNOSTICS synced = ROW_COUNT;

                {inner_function_ddl}
{healthy_publish}
                UPDATE {self.plan_source_table} SET last_synced_at = now();

                RAISE LOG 'checkout_plan_sync: republished % plan steps from {self.plan_source_table} and shipped the checkout plan package', synced;
                {healthy_log}
                RETURN synced;
            END
            $plan_sync$;
        """

    def _ensure_plan_sync(self, env) -> str:
        # 计划同步例程。一个调度周期 = 从上游源重灌 steps +
        # 版本锁定地重部署消费例程 + 留一行同步证据日志。函数/视图/steps 任一层
        # 的库端单点修复都会被该例程在下一个周期还原。
        # 双源发布——checkout 反序计划与 returns 健康计划
        # 由同一调度作业一并发布（各一条 RAISE LOG 证据行）。健康分支的发布内容
        # 来自未被事故污染的 returns_plan_source，因此"只改 checkout 源 + 发布"的
        # 正确修复不影响健康线；把健康分支/健康源改坏的修复会被 OP 健康不变量
        # 在该发布周期后验收失败。
        ddl = self._plan_sync_ddl()
        env.execute_sql(ddl)
        return ddl

    @staticmethod
    def _sql_literal(value: str) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    def _ensure_plan_sync_registry(self, env, sync_ddl: str) -> None:
        # 仅 checkout 配置：计划同步调度层控制面。host 侧调度器
        # 每 tick 扫描本表：对 status='scheduled' 的作业从 template_definition verbatim
        # 重部署目标函数再执行。status 由公开 CHECK 约束枚举，表/列 COMMENT 说明调度
        # 语义——控制面对 Agent 完全可发现，"谁在重装例程"由公开证据唯一确定。
        if not self.plan_sync_registry_table:
            return
        registry = self.plan_sync_registry_table
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {registry} (
                job_name text PRIMARY KEY,
                target_function text NOT NULL,
                schedule_interval_seconds integer NOT NULL CHECK (schedule_interval_seconds > 0),
                status text NOT NULL DEFAULT 'scheduled',
                template_definition text NOT NULL,
                template_revision integer NOT NULL DEFAULT 1,
                last_redeployed_at timestamptz,
                CONSTRAINT {registry}_status_allowed
                    CHECK (status IN ('scheduled', 'paused', 'disabled'))
            );
        """)
        table_comment = (
            "Plan-sync scheduler control plane (upstream planning service). The host-side "
            "scheduler scans this table on every tick; jobs with status = 'scheduled' are "
            "redeployed from template_definition (CREATE OR REPLACE FUNCTION, applied "
            "verbatim) and then executed. Changes applied directly to the target function "
            "do not survive the next scheduler redeploy; to make routine changes permanent, "
            "correct template_definition or set status to 'paused' or 'disabled' (legal "
            "values enforced by the status check constraint)."
        )
        status_comment = (
            "scheduler state: scheduled = redeploy from template_definition and run on "
            "every tick; paused = tick skips this job (resumable); disabled = job retired"
        )
        template_comment = (
            "full CREATE OR REPLACE FUNCTION statement redeployed verbatim on each tick "
            "while status = scheduled; the running routine is always the deployed template"
        )
        env.execute_sql(
            f"COMMENT ON TABLE {registry} IS {self._sql_literal(table_comment)};"
        )
        env.execute_sql(
            f"COMMENT ON COLUMN {registry}.status IS {self._sql_literal(status_comment)};"
        )
        env.execute_sql(
            f"COMMENT ON COLUMN {registry}.template_definition IS {self._sql_literal(template_comment)};"
        )
        env.execute_sql(f"""
            INSERT INTO {registry}
                (job_name, target_function, schedule_interval_seconds, status,
                 template_definition, template_revision, last_redeployed_at)
            VALUES
                ('plan_sync_publish', '{self.plan_sync_function}',
                 {int(self.plan_sync_interval_seconds)}, 'scheduled',
                 {self._sql_literal(sync_ddl)}, 7, now())
            ON CONFLICT (job_name) DO UPDATE
            SET target_function = EXCLUDED.target_function,
                schedule_interval_seconds = EXCLUDED.schedule_interval_seconds,
                status = 'scheduled',
                template_definition = EXCLUDED.template_definition;
        """)

    _SYNC_LOG_SESSION_SETTINGS = (
        "SET log_error_verbosity = 'terse'; "
        "SET log_min_error_statement = 'panic';"
    )
    _SYNC_LOG_SESSION_RESET = (
        "RESET log_error_verbosity; RESET log_min_error_statement;"
    )

    def _run_plan_sync_once(self, env) -> None:
        # 与 RAISE 噪声路径同先例：同步会话级 terse+panic，让每条同步证据行只落
        # 1 行日志（默认 verbose 会附 CONTEXT/STATEMENT 各 1 行）。
        env.execute_sql(self._SYNC_LOG_SESSION_SETTINGS)
        _json_object(
            env.execute_sql(f"SELECT {self.plan_sync_function}();"),
            "run checkout plan sync",
        )
        env.execute_sql(self._SYNC_LOG_SESSION_RESET)

    def _registry_scheduled_jobs(self, env):
        # 读取调度控制面（Agent 同样可读的公开表）。返回 scheduled 作业
        # (job_name, template_revision)。注意：故意不把 template_definition 拉过
        # env.execute_sql 的 JSON 绑定（_bound_sql_value 会截断长字符串值，
        # 3136 字符的模板被截断后产生 unterminated dollar-quoted 解析错误）；
        # 模板统一由服务端 DO 块在库内 EXECUTE（见 _scheduler_deploy_statement）。
        registry = self.plan_sync_registry_table
        payload = _json_object(
            env.execute_sql(
                f"SELECT job_name, status, template_revision "
                f"FROM {registry} "
                f"WHERE target_function = '{self.plan_sync_function}' "
                f"ORDER BY job_name;"
            ),
            "read plan sync scheduler registry",
        )
        jobs = []
        for row in payload["result"]:
            if len(row) < 3:
                continue
            if str(row[1]) == "scheduled":
                jobs.append((str(row[0]), int(row[2] or 1)))
        return jobs

    def _scheduler_deploy_statement(self, job_name: str) -> str:
        # 服务端重部署：模板文本在库内读取并 EXECUTE，从不过线，模型对
        # template_definition 的改正对下一次重部署即时生效。
        registry = self.plan_sync_registry_table
        return (
            f"DO $scheduler_deploy$ DECLARE t text; BEGIN "
            f"SELECT template_definition INTO t FROM {registry} "
            f"WHERE target_function = '{self.plan_sync_function}' "
            f"AND job_name = '{job_name}' AND status = 'scheduled'; "
            f"IF t IS NOT NULL THEN EXECUTE t; END IF; "
            f"END $scheduler_deploy$;"
        )

    def _scheduler_tick_statements(self, job_name: str, revision: int):
        # 一个调度 tick = 服务端模板重部署 → revision/时间戳推进 →
        # 重部署证据行（RAISE LOG，terse 1 行）→ 执行 sync。重部署证据行是
        # Agent-visible evidence；revision 推进让"调度层活着"可被 Agent 交叉验证。
        registry = self.plan_sync_registry_table
        redeploy_line = (
            f"plan_sync_control: redeployed {self.plan_sync_function} from {registry} "
            f"(job={job_name} revision={revision + 1} status=scheduled)"
        )
        return (
            self._scheduler_deploy_statement(job_name),
            (
                f"UPDATE {registry} SET template_revision = template_revision + 1, "
                f"last_redeployed_at = now() WHERE job_name = '{job_name}';"
            ),
            (
                f"DO $scheduler_tick$ BEGIN RAISE LOG "
                f"{self._sql_literal(redeploy_line)}; END $scheduler_tick$;"
            ),
            f"SELECT {self.plan_sync_function}();",
        )

    def _run_scheduler_tick_once(self, env) -> None:
        # 激活期执行一个完整调度 tick（确定性落入未过滤日志窗口）。
        # 每条语句的结果都检查：任何失败打印并抛出，防止静默半执行。
        jobs = self._registry_scheduled_jobs(env)
        env.execute_sql(self._SYNC_LOG_SESSION_SETTINGS)
        try:
            for job_name, revision in jobs:
                for statement in self._scheduler_tick_statements(job_name, revision):
                    payload = _json_object(env.execute_sql(statement), "scheduler tick step")
                    if payload.get("status") != "success":
                        raise RuntimeError(
                            f"Scheduler tick step failed for job {job_name}: "
                            f"{str(payload.get('error'))[:200]}"
                        )
        finally:
            env.execute_sql(self._SYNC_LOG_SESSION_RESET)

    def _start_plan_sync_loop(self):
        # 周期同步线程。每 plan_sync_interval_seconds 执行一次计划同步，
        # 直到 recover 触发 _stop_event。确定性周期（无随机窗口），每个 tick
        # 独立短连接并登记/关闭，恢复路径可完整清理。
        import threading

        env = self.env

        def loop():
            while not self._stop_event.wait(self.plan_sync_interval_seconds):
                conn = None
                try:
                    conn = self._connect(env, self.plan_sync_application)
                    with conn.cursor() as cur:
                        cur.execute(self._SYNC_LOG_SESSION_SETTINGS)
                        cur.execute(f"SELECT {self.plan_sync_function}();")
                    conn.commit()
                except Exception as exc:
                    print(
                        "[FaultInjector:PgSystemFailureDeadlockInjector] "
                        f"Plan sync tick failed: {exc}"
                    )
                    try:
                        if conn is not None:
                            conn.rollback()
                    except Exception:
                        pass
                finally:
                    if conn is not None:
                        try:
                            conn.close()
                        except Exception:
                            pass

        self._sync_thread = threading.Thread(target=loop, daemon=True)
        self._sync_thread.start()
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Plan sync loop started (interval={self.plan_sync_interval_seconds}s)."
        )

    def _start_plan_sync_scheduler_loop(self):
        # 调度层循环（仅 checkout）。每 tick 读注册表，对
        # status='scheduled' 的作业执行"模板重部署 → revision 推进 → 重部署证据行 →
        # 执行 sync"。重部署由服务端 DO 块在库内 EXECUTE 当前模板——模型对
        # template_definition 的改正对下一次重部署即时生效；直接改写/删除 sync 例程
        # 会被本循环还原——这是复发驱动的所有权层。
        import threading

        env = self.env
        registry = self.plan_sync_registry_table

        def loop():
            while not self._stop_event.wait(self.plan_sync_interval_seconds):
                conn = None
                try:
                    conn = self._connect(env, self.plan_sync_application)
                    with conn.cursor() as cur:
                        cur.execute(self._SYNC_LOG_SESSION_SETTINGS)
                        cur.execute(
                            f"SELECT job_name, status, template_revision "
                            f"FROM {registry} "
                            f"WHERE target_function = '{self.plan_sync_function}' "
                            f"ORDER BY job_name;"
                        )
                        jobs = [
                            (str(row[0]), int(row[2] or 1))
                            for row in cur.fetchall()
                            if len(row) >= 3 and str(row[1]) == "scheduled"
                        ]
                        for job_name, revision in jobs:
                            for statement in self._scheduler_tick_statements(job_name, revision):
                                cur.execute(statement)
                    conn.commit()
                except Exception as exc:
                    print(
                        "[FaultInjector:PgSystemFailureDeadlockInjector] "
                        f"Plan sync scheduler tick failed: {exc}"
                    )
                    try:
                        if conn is not None:
                            conn.rollback()
                    except Exception:
                        pass
                finally:
                    if conn is not None:
                        try:
                            conn.close()
                        except Exception:
                            pass

        self._sync_thread = threading.Thread(target=loop, daemon=True)
        self._sync_thread.start()
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Plan sync scheduler loop started (registry={registry}, "
            f"interval={self.plan_sync_interval_seconds}s)."
        )

    def _ensure_red_herring_functions(self, env):
        env.execute_sql("""
            CREATE OR REPLACE FUNCTION refresh_dashboard_tile(p_tile_id integer)
            RETURNS integer
            LANGUAGE plpgsql
            AS $$
            BEGIN
                PERFORM pg_sleep(0.35);
                RETURN p_tile_id;
            END
            $$;

            CREATE OR REPLACE FUNCTION inventory_rollup_refresh(p_region text)
            RETURNS text
            LANGUAGE plpgsql
            AS $$
            BEGIN
                PERFORM pg_sleep(0.25);
                RETURN p_region;
            END
            $$;
        """)

    def _ensure_decoy_table(self, env):
        # 良性等待链的业务对象。归档水印表与 checkout 事故
        # 完全无关，属于健康近邻；Agent 通过表名/会话上下文可排除。
        self._ensure_chain_table(env, self.decoy_table)

    def _ensure_decoy2_table(self, env):
        # 第二条良性等待链的业务对象（快照/水印维护表，与事故无关）。
        self._ensure_chain_table(env, self.decoy2_table)

    def _ensure_chain_table(self, env, table: str):
        env.execute_sql(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                region text PRIMARY KEY,
                synced_at timestamptz NOT NULL,
                payload text NOT NULL
            );
        """)
        env.execute_sql(f"""
            INSERT INTO {table} (region, synced_at, payload)
            VALUES ('global', now(), 'init')
            ON CONFLICT (region) DO UPDATE
            SET synced_at = EXCLUDED.synced_at, payload = EXCLUDED.payload;
        """)

    def _start_decoy_chain(self, holder_app: str, waiter_app: str, table: str):
        # holder 长事务持有 decoy 行锁 decoy_hold_seconds 后提交；waiter 的
        # UPDATE 在行锁上等待（wait_event_type=Lock），期间在 pg_stat_activity
        # 与 pg_locks 中持续可见。两个会话均登记进 _connections 便于恢复。
        import threading
        import time

        env = self.env
        holder = self._connect(env, holder_app)
        waiter = self._connect(env, waiter_app)

        def hold():
            try:
                with holder.cursor() as cur:
                    # psycopg2 隐式开启事务；只发 UPDATE，长事务由 commit 前的等待窗口构成。
                    cur.execute(
                        f"UPDATE {table} "
                        "SET synced_at = now(), payload = payload || '.archiver_tick' "
                        "WHERE region = 'global'"
                    )
                self._stop_event.wait(self.decoy_hold_seconds)
                if not self._stop_event.is_set():
                    holder.commit()
            except Exception:
                try:
                    holder.rollback()
                except Exception:
                    pass

        def wait_behind():
            try:
                with waiter.cursor() as cur:
                    cur.execute(
                        f"UPDATE {table} "
                        "SET payload = payload || '.purge_tick' "
                        "WHERE region = 'global'"
                    )
                waiter.commit()
            except Exception:
                try:
                    waiter.rollback()
                except Exception:
                    pass

        threading.Thread(target=hold, daemon=True).start()
        time.sleep(0.5)
        threading.Thread(target=wait_behind, daemon=True).start()
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Decoy wait chain started: holder={holder_app}, "
            f"waiter={waiter_app}."
        )

    def _open_idle_pool_connections(self, env):
        # 应用连接池常驻空闲后端（state=idle、不执行语句）。
        # pg_stat_activity 未过滤快照中的确定性真实业务观测；连接登记进
        # _connections，recover 时统一关闭。
        for app_name, count in self.idle_pool_apps:
            for index in range(count):
                self._connect(env, f"{app_name}_{index + 1}" if count > 1 else app_name)
        if self.idle_pool_apps:
            total = sum(count for _name, count in self.idle_pool_apps)
            print(
                "[FaultInjector:PgSystemFailureDeadlockInjector] "
                f"Idle pool connections opened: {total}."
            )

    def _run_red_herring_queries(self, env):
        for _ in range(self.dashboard_noise_count):
            env.execute_sql("SELECT refresh_dashboard_tile(8101);")
        for _ in range(self.inventory_noise_count):
            env.execute_sql("SELECT inventory_rollup_refresh('north_america');")

    def _trigger_deadlock(self, env):
        import threading

        barrier = threading.Barrier(2, timeout=10)

        def run_txn(application_name: str, job_id: int):
            conn = None
            try:
                conn = self._connect(env, application_name)
                with conn.cursor() as cur:
                    cur.execute("SET deadlock_timeout = '200ms';")
                    cur.execute("SET lock_timeout = '8s';")
                    cur.execute("SET statement_timeout = '12s';")
                    barrier.wait()
                    cur.execute("SELECT process_checkout_job(%s);", (job_id,))
                    conn.commit()
            except Exception as exc:
                self._errors.append(f"{application_name}: {exc}")
                try:
                    if conn is not None:
                        conn.rollback()
                except Exception:
                    pass
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        thread_a = threading.Thread(
            target=run_txn,
            args=(self.worker_a, self.job_ids[0]),
            daemon=True,
        )
        thread_b = threading.Thread(
            target=run_txn,
            args=(self.worker_b, self.job_ids[1]),
            daemon=True,
        )
        thread_a.start()
        thread_b.start()
        thread_a.join(timeout=15)
        thread_b.join(timeout=15)

        errors_text = " | ".join(self._errors).lower()
        if "deadlock" not in errors_text:
            raise RuntimeError(
                f"Deadlock trigger did not produce a deadlock error: errors={self._errors}"
            )
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            f"Deadlock triggered: {self._errors[0][:140]}"
        )

    def _run_healthy_line_once(self, env):
        # 健康线业务推进。returns job 对按同一（正确）顺序并发处理
        # 健康订单对——只串行化、不死锁，是同管道的健康近邻而非第二个故障。
        # 健康线不允许失败：任何报错都意味着场景前提破坏，硬失败以保证运行无效
        # 可见（与 _trigger_deadlock 的断言对称）。
        if not self.healthy_plan_source_table:
            return
        import threading

        errors = []
        barrier = threading.Barrier(2, timeout=10)

        def run_job(application_name: str, job_id: int):
            conn = None
            try:
                conn = self._connect(env, application_name)
                with conn.cursor() as cur:
                    cur.execute("SET lock_timeout = '8s';")
                    cur.execute("SET statement_timeout = '12s';")
                    barrier.wait()
                    cur.execute(f"SELECT {self.healthy_job_function}(%s);", (job_id,))
                conn.commit()
            except Exception as exc:
                errors.append(f"{application_name}: {exc}")
                try:
                    if conn is not None:
                        conn.rollback()
                except Exception:
                    pass
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        thread_a = threading.Thread(
            target=run_job,
            args=(self.healthy_worker_a, self.healthy_job_ids[0]),
            daemon=True,
        )
        thread_b = threading.Thread(
            target=run_job,
            args=(self.healthy_worker_b, self.healthy_job_ids[1]),
            daemon=True,
        )
        thread_a.start()
        thread_b.start()
        thread_a.join(timeout=15)
        thread_b.join(timeout=15)
        if errors:
            raise RuntimeError(
                f"Healthy returns plan line must progress without errors: errors={errors}"
            )
        print(
            "[FaultInjector:PgSystemFailureDeadlockInjector] "
            "Healthy returns jobs completed (business progressing)."
        )

    def _wait_until_log_visible(self, env, timeout_seconds: float = 10.0):
        import time

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            self._read_new_postgres_logs()
            text = self._log_text.casefold()
            if (
                "deadlock detected" in text
                and "process" in text
                and all(str(job_id) in text for job_id in self.job_ids)
                and "process_checkout_job" in text
            ):
                self._publish_compatibility_window(env)
                return
            time.sleep(0.5)
        raise RuntimeError(
            f"Deadlock log was not fully visible after {timeout_seconds}s: "
            f"job_ids={self.job_ids}"
        )

    def _read_compatibility_log_content(self, env) -> str:
        # pg-entrypoint 用 pg_ctl -l 把启动期 stderr 写进 postgresql.log；
        # 兼容快照发布必须保留既有内容，否则文件缩小会触发可见性快照的
        # shrink 保护，Agent 的 read_log(pg_log) 会直接报错。
        try:
            payload = _json_object(
                env.execute_sql(
                    "SELECT pg_read_file('/var/log/postgresql/postgresql.log', 0, "
                    "GREATEST((pg_stat_file('/var/log/postgresql/postgresql.log')).size, 0)) "
                    "AS compat_log;"
                ),
                "read postgresql compatibility log",
            )
            row = payload["result"][0]
            return str(row[0]) if row and row[0] is not None else ""
        except Exception:
            return ""

    def _publish_compatibility_window(self, env) -> None:
        existing = self._read_compatibility_log_content(env)
        if existing and not existing.endswith("\n"):
            existing += "\n"
        window = self._log_text
        published = getattr(self, "_published_log_text", "")
        if published and window.startswith(published):
            delta = window[len(published):]
        else:
            delta = window
        self._log_offsets = env.get_deployment().publish_postgres_log_compatibility_snapshot(
            existing + delta
        )
        self._published_log_text = window

    def _read_new_postgres_logs(self) -> None:
        output, offsets = self.env.get_deployment().read_postgres_logs_after(self._log_offsets)
        self._log_offsets = offsets
        self._log_text += output

    def _periodic_trigger_loop(self, env):
        # 间隔 30 秒反复触发 3 次 deadlock，agent 必须识别是 recurring fault 而非偶然单次事务冲突。
        # 后台 daemon 线程，inject() 不阻塞立即返回；recover() 触发 _stop_event。
        for round_idx in range(1, self.trigger_rounds + 1):
            if self._stop_event.is_set():
                break
            try:
                self._trigger_deadlock(env)
                print(
                    f"[FaultInjector:PgSystemFailureDeadlockInjector] "
                    f"Round {round_idx} triggered. Sleeping 30s before next."
                )
            except Exception as exc:
                print(
                    f"[FaultInjector:PgSystemFailureDeadlockInjector] "
                    f"Round {round_idx} trigger failed: {exc}"
                )
            if (
                self.healthy_plan_source_table
                and not self._stop_event.is_set()
            ):
                # 健康线与事故线同一调度节奏推进；健康 job 的执行
                # 不产生任何日志行（无错无超时），日志口径与故障线一致。
                # recover 置位 stop_event 后不再开启新一轮健康执行。
                try:
                    self._run_healthy_line_once(env)
                except Exception as exc:
                    print(
                        f"[FaultInjector:PgSystemFailureDeadlockInjector] "
                        f"Round {round_idx} healthy line run failed: {exc}"
                    )
            if round_idx < self.trigger_rounds:
                self._stop_event.wait(self.trigger_interval_seconds)

    def _emit_business_noise_logs(self, env):
        # 一条 DO 语句批量 RAISE LOG/WARNING，比起造几十个后台会话更便宜。
        # 列表前若干条是与死锁最易混淆的真实近邻 warning（锁超时、
        # 序列化失败、autovacuum 锁冲突、应用重试），按 case 截取 log/warning_noise_per_repeat
        # 条；截取后保留竞争假设，但纯噪声数量不再淹没因果证据（easy 的 C_s 预算）。
        log_messages = [
            "duration: 1842.331 ms  statement: SELECT refresh_dashboard_tile(8101)",
            "checkpoint starting: time",
            "duration: 1776.005 ms  bind <unnamed>: SELECT checkout_retry_queue($1)",
            "duration: 901.114 ms  parse <unnamed>: SELECT * FROM catalog_sales WHERE cs_sold_date_sk = $1",
            "checkpoint complete: wrote 1827 buffers (11.2%); sync files=41, longest=247.091 ms",
            "temporary file: path \"base/pgsql_tmp/pgsql_tmp914.0\", size 73400320",
            "automatic analyze of table \"public.store_sales\" system usage: CPU 0.29s/1.88u sec elapsed 7.11 sec",
            "connection authorized: user=postgres database=testdb application_name=reporting_pool",
            "disconnection: session time: 0:00:08.245 user=postgres database=testdb host=[local]",
            "duration: 2201.880 ms  execute <unnamed>: UPDATE orders_archive SET synced=true WHERE batch_id=42",
            "statement: SELECT inventory_rollup_refresh('north_america')",
            "background worker \"parallel worker\" exited with exit code 1",
        ]
        warning_messages = [
            "lock timeout while refreshing dashboard cache for report_id=8101",
            "could not serialize access due to concurrent update in reporting refresh",
            "autovacuum worker skipped relation public.store_sales due to conflicting lock",
            "application warning: order service retried transaction after client disconnect",
            "canceling statement due to statement timeout in inventory_rollup",
            "connection pool retry storm: checkout-api observed SQLSTATE 40001",
            "analytics_worker blocked by process 77 while reading catalog_sales",
            "DDL migration waiting for AccessExclusiveLock on public.customer",
            "replication apply lag exceeded 20s on reporting subscriber",
            "lock wait still active for pid 322 on relation public.order_items",
            "dead tuple cleanup delayed by long-running reader on store_returns",
            "canceling autovacuum task because of conflicting lock request",
        ]
        log_messages = log_messages[: max(int(self.log_noise_per_repeat), 0)]
        warning_messages = warning_messages[: max(int(self.warning_noise_per_repeat), 0)]
        def sql_literal(value: str) -> str:
            return "'" + value.replace("'", "''") + "'"

        log_values = ", ".join(f"({sql_literal(message)})" for message in log_messages)
        warning_values = ", ".join(f"({sql_literal(message)})" for message in warning_messages)
        # 会话级 terse + log_min_error_statement='panic'（同 cpu_lock_spin 先例）：
        # RAISE LOG/WARNING 每条只落一行日志，不带 CONTEXT，也不把整段 DO 源码
        # 作为 STATEMENT 转储。噪声仍是真实业务告警，只是不再以 10 倍体积淹没
        # 因果证据（easy 的 C_s 预算）。
        env.execute_sql(f"""
            SET log_error_verbosity = 'terse';
            SET log_min_error_statement = 'panic';
            DO $$
            DECLARE
                msg text;
                i integer;
            BEGIN
                FOR i IN 1..{self.business_noise_repeats} LOOP
                    FOR msg IN SELECT column1 FROM (VALUES {log_values}) AS noise(column1) LOOP
                        RAISE LOG '%', msg;
                    END LOOP;
                    FOR msg IN SELECT column1 FROM (VALUES {warning_values}) AS noise(column1) LOOP
                        RAISE WARNING '%', msg;
                    END LOOP;
                END LOOP;
            END $$;
            RESET log_error_verbosity;
            RESET log_min_error_statement;
        """)
        for _ in range(self.timeout_noise_count):
            env.execute_sql("SET LOCAL statement_timeout = '20ms'; SELECT pg_sleep(0.2);")

    def _emit_batch_coordinator_logs(self, env):
        # 批处理协调器心跳日志（dispatch/complete，4 个周期各 2 行，
        # terse 1 行/条）。与事故无因果（不提及反序/回写/死锁），但与 staged job 对
        # 数量自洽，是 read_log 未过滤窗口中的同域真实业务观测。激活期确定性发射。
        pair_count = 1 + len(self.extra_job_pairs)
        job_count = 2 * pair_count
        env.execute_sql(self._SYNC_LOG_SESSION_SETTINGS)
        try:
            for cycle in range(418, 422):
                dispatch_line = self._sql_literal(
                    'checkout_batch_coordinator: cycle ' + str(cycle)
                    + ' dispatched ' + str(pair_count) + ' job pairs ('
                    + str(job_count) + ' jobs) from the batch planner'
                )
                complete_line = self._sql_literal(
                    'checkout_batch_coordinator: cycle ' + str(cycle)
                    + ' complete: batch window closed, follow-up jobs queued'
                )
                env.execute_sql(
                    "DO $coordinator$ BEGIN RAISE LOG "
                    f"{dispatch_line}; END $coordinator$;"
                )
                env.execute_sql(
                    "DO $coordinator$ BEGIN RAISE LOG "
                    f"{complete_line}; END $coordinator$;"
                )
        finally:
            env.execute_sql(self._SYNC_LOG_SESSION_RESET)

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        activity = env.execute_sql(
            "SELECT pid, application_name, state, wait_event_type, wait_event, query "
            "FROM pg_stat_activity WHERE datname = current_database() ORDER BY pid;"
        )
        self._read_new_postgres_logs()
        self._publish_compatibility_window(env)
        pg_log = self._log_text
        log_text = pg_log.casefold()
        required = [
            "deadlock detected",
            "blocked by process",
            "process_checkout_job",
            *(str(job_id) for job_id in self.job_ids),
        ]
        missing = [marker for marker in required if marker not in log_text]
        if missing:
            raise RuntimeError(
                f"Deadlock log trace is incomplete: missing={missing}, log={pg_log}"
            )
        return {"activity": activity, "pg_log": pg_log}

    def quiesce(self, context: FaultLifecycleContext):
        self.recover(context)

    def recover(self, context: FaultLifecycleContext):
        env = context.env
        self._configure(context.config, env)
        if self._stop_event is not None:
            self._stop_event.set()
        # 触发线程的"忙窗口"= 一轮死锁触发 + 一次健康线执行（每项内部 join
        # 各上限 15s）。recover 必须等该有界窗口走完而不是 2s 即判失败，否则
        # 恰逢忙窗口的提交会被误判为 harness 失败（运行作废）。窗口有界且确定，
        # 不引入任何随机性。
        if self._trigger_thread is not None and self._trigger_thread.is_alive():
            self._trigger_thread.join(timeout=45.0)
            if self._trigger_thread.is_alive():
                raise RuntimeError(
                    f"Deadlock trigger thread did not stop: "
                    f"scenario={context.scenario_id}, case={context.case_id}"
                )
        if self._sync_thread is not None and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=2.0)
            if self._sync_thread.is_alive():
                raise RuntimeError(
                    f"Plan sync thread did not stop: "
                    f"scenario={context.scenario_id}, case={context.case_id}"
                )
        self._sync_thread = None
        print("[FaultInjector:PgSystemFailureDeadlockInjector] Recovering lingering sessions...")
        # 两条良性链会话、池会话与健康线执行器一并终止（良性链属受保护对象——
        # 终止它们的 Agent 动作由 SP 判定；本处的终止是 injector 恢复自有运行时资源）。
        app_names = [
            self.worker_a, self.worker_b,
            self.decoy_holder_app, self.decoy_waiter_app,
            self.decoy2_holder_app, self.decoy2_waiter_app,
        ]
        if self.healthy_plan_source_table:
            app_names.extend((self.healthy_worker_a, self.healthy_worker_b))
        for name, count in self.idle_pool_apps:
            app_names.extend(
                f"{name}_{index + 1}" if count > 1 else name
                for index in range(count)
            )
        rendered_apps = ",\n                    ".join(repr(name) for name in app_names)
        _require_sql_success(
            env.execute_sql(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE application_name IN (
                    {rendered_apps}
                )
                  AND pid <> pg_backend_pid();
            """),
            "terminate deadlock scenario sessions",
        )
        for conn in self._connections:
            conn.close()
        self._connections = []
        self._log_offsets = {}
        self._log_text = ""
        self._published_log_text = ""
        self._trigger_thread = None
        self._stop_event = None
        print("[FaultInjector:PgSystemFailureDeadlockInjector] Recovery complete.")


class PgSystemFailureDeadlockScenario(PostgresScenario):
    scenario_id = 'pg_system_failure_deadlock'
    description = 'Simulates intermittent checkout failures caused by non-canonical batch lock ordering.'
    cases = (
        _PGSYSTEMFAILUREDEADLOCKSCENARIO_CASE,
        _PGSYSTEMFAILUREDEADLOCKSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgSystemFailureDeadlockCase) -> tuple[FaultPlan, ...]:
        config = {
            'table': case.table,
            'order_ids': case.order_ids_2,
            'job_ids': case.job_ids_2,
            'job_step_table': case.job_step_table,
            'worker_a': case.worker_a,
            'worker_b': case.worker_b,
            'trigger_rounds': case.trigger_rounds,
            'trigger_interval_seconds': case.trigger_interval_seconds,
            'business_noise_repeats': case.business_noise_repeats,
            'timeout_noise_count': case.timeout_noise_count,
            'dashboard_noise_count': case.dashboard_noise_count,
            'inventory_noise_count': case.inventory_noise_count,
            'decoy_holder_app': case.decoy_holder_app,
            'decoy_waiter_app': case.decoy_waiter_app,
            'decoy_table': case.decoy_table,
            'decoy_hold_seconds': case.decoy_hold_seconds,
            'job_plan_view': case.job_plan_view,
            'plan_source_table': case.plan_source_table,
            'plan_sync_function': case.plan_sync_function,
            'plan_sync_interval_seconds': case.plan_sync_interval_seconds,
            'plan_sync_application': case.plan_sync_application,
            'log_noise_per_repeat': case.log_noise_per_repeat,
            'warning_noise_per_repeat': case.warning_noise_per_repeat,
            # staged 健康 job 对、第二条良性等待链、池会话（两 case）。
            'extra_job_pairs': [
                (list(job_ids), list(order_ids))
                for job_ids, order_ids in case.extra_job_pairs
            ],
            'decoy2_holder_app': case.decoy2_holder_app,
            'decoy2_waiter_app': case.decoy2_waiter_app,
            'decoy2_table': case.decoy2_table,
            'idle_pool_apps': [
                (name, count) for name, count in case.idle_pool_apps
            ],
        }
        # 健康孪生计划线仅 checkout case 配置；simple case 不携带这些键，
        # 注入器健康路径全部关闭。
        if getattr(case, 'healthy_plan_source_table', None):
            config.update({
                'healthy_plan_source_table': case.healthy_plan_source_table,
                'healthy_job_step_table': case.healthy_job_step_table,
                'healthy_job_plan_view': case.healthy_job_plan_view,
                'healthy_job_function': case.healthy_job_function,
                'healthy_job_ids': case.healthy_job_ids,
                'healthy_order_ids': case.healthy_order_ids,
            })
        # 调度层控制面仅 checkout case 配置；simple 不携带该键，
        # 注入器保持直接同步语义。
        if getattr(case, 'plan_sync_registry_table', None):
            config['plan_sync_registry_table'] = case.plan_sync_registry_table
        return (
            FaultPlan(
                injector_type=PgSystemFailureDeadlockInjector,
                config=config,
            ),
        )
