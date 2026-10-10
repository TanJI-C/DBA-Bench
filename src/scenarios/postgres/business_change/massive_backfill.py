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

# Loyalty fixture timeline: the approved release list is loaded in two
# passes (initial + delta) and a leftover experimental draft batch from the
# previous quarter stays staged alongside it, with its own audit sample.
# Post-freeze release-desk scope rulings live in the operation event log: an
# annulment defers a listed row to the next release window, and a later restore
# puts the row back into the current window. The latest ruling governs.
LEGACY_DRAFT_SOURCE_NAME = "crm_decade_estimator_experimental_v2"
LEGACY_DRAFT_LOADED_AT = "2024-12-18 22:15:00+00"
STAGE_INITIAL_LOADED_AT = "2025-01-02 18:00:00+00"
STAGE_DELTA_LOADED_AT = "2025-01-08 09:30:00+00"
AUDIT_APPROVED_CHECKED_AT = "2025-01-05 08:00:00+00"
AUDIT_DRAFT_CHECKED_AT = "2024-12-19 08:00:00+00"
LOYALTY_EVENT_TABLE = "customer_loyalty_operation_event"
EVENT_ANNUL_AT = "2025-01-07 10:30:00+00"
EVENT_RESTORE_AT = "2025-01-09 14:00:00+00"
EVENT_DELTA_ANNUL_AT = "2025-01-09 11:00:00+00"
EVENT_DRAFT_WITHDRAWN_AT = "2024-12-20 09:00:00+00"
EVENT_ANNUL_NOTE = (
    "loyalty decade dispute filed; row annulled from the current release window "
    "and deferred to the next release window"
)
EVENT_RESTORE_NOTE = (
    "dispute resolved in favor of the approved correction; annulment reversed "
    "and the row is back in the current release window"
)
EVENT_DRAFT_WITHDRAWN_NOTE = (
    "experimental estimator batch withdrawn from release; rows return to the "
    "pending pool for re-estimation"
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeMassiveBackfillCase(PostgresScenarioCase):
    base_image_name: str
    workload_tag: str
    table: str
    pk_column: str
    source_column: str
    target_column: str
    stage_table: str
    preview_table: str
    audit_table: str
    release_batch_id: str
    stage_value_column: str
    batch_size: int
    estimated_rows: int
    slow_queries: tuple[str, ...]
    legacy_draft_batch_id: str | None = None
    release_freeze_cutoff: str | None = None
    operation_event_table: str | None = None

@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillScenarioCase(PgBusinessChangeMassiveBackfillCase):
    pass

def build_massive_backfill_noise_profiles(
    table: str = "customer_backfill",
    stage_table: str = "customer_backfill_release_stage",
    preview_table: str = "customer_backfill_preview",
    audit_table: str = "customer_backfill_audit_shadow",
    pk_column: str = "c_customer_sk",
    target_column: str = "c_birth_decade_corrected",
    stage_value_column: str = "corrected_decade",
    release_batch_id: str = "birth_decade_2024q4",
) -> List[WorkloadProfile]:
    """Same-domain noise for the massive backfill scenario.

    The real task is not "fill every NULL with a derivable formula"; it is to apply
    one release stage to the hot customer table. These profiles keep adjacent
    preview and audit backfill work visible so the agent must distinguish the
    target release slice from plausible but wrong pending-row signals.
    """
    return [
        WorkloadProfile(
            name="customer_backfill_stage_pending_probe",
            sql=(
                f"SELECT s.release_batch_id, count(*) AS staged_rows, "
                f"count(*) FILTER (WHERE t.{target_column} IS NULL) AS pending_rows, "
                f"min(s.{pk_column}) AS first_stage_pk, max(s.{pk_column}) AS last_stage_pk "
                f"FROM {stage_table} s JOIN {table} t USING ({pk_column}) "
                f"WHERE s.release_batch_id = '{release_batch_id}' "
                "GROUP BY s.release_batch_id"
            ),
            qps=0.35,
            tier="LIGHT",
            application_name="release-stage-validator",
        ),
        WorkloadProfile(
            name="customer_backfill_preview_pending_decoy",
            sql=(
                f"SELECT preview_batch_id, count(*) AS pending_rows, "
                f"min({pk_column}) AS first_pk, max({pk_column}) AS last_pk "
                f"FROM {preview_table} "
                f"WHERE {target_column} IS NULL "
                "GROUP BY preview_batch_id "
                "ORDER BY pending_rows DESC"
            ),
            qps=0.45,
            tier="LIGHT",
            application_name="future-backfill-preview",
        ),
        WorkloadProfile(
            name="customer_backfill_audit_delta_rollup",
            sql=(
                f"SELECT release_batch_id, "
                f"count(*) FILTER (WHERE previous_decade IS DISTINCT FROM {stage_value_column}) AS changed_rows, "
                f"count(*) AS sampled_rows "
                f"FROM {audit_table} "
                "GROUP BY release_batch_id "
                "ORDER BY changed_rows DESC"
            ),
            qps=0.25,
            tier="MEDIUM",
            application_name="birth-decade-audit",
        ),
        WorkloadProfile(
            name="customer_backfill_hot_writer_preview",
            sql=(
                f"UPDATE {table} "
                "SET c_last_update = now() "
                f"WHERE {pk_column} IN ("
                f"SELECT {pk_column} FROM {table} "
                "WHERE release_batch_id <> "
                f"'{release_batch_id}' "
                f"ORDER BY {pk_column} LIMIT 20)"
            ),
            qps=0.3,
            tier="DML_NOISE",
            commit=True,
            application_name="customer-profile-writer",
        ),
        WorkloadProfile(
            name="missing_backfill_control_cache_noise",
            sql="SELECT count(*) FROM customer_backfill_control_cache_missing;",
            qps=0.2,
            tier="LOG_NOISE",
            application_name="backfill-control-cache",
        ),
    ]

_PGBUSINESSCHANGEMASSIVEBACKFILLSCENARIO_CASE = PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillScenarioCase(
    case_id='customer_birth_decade_backfill',
    reference_report={
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": "hundred million row backfill",
                    "entity": "customer_birth_decade_backfill",
                    "evidence": [
                        "scripted diagnostic actions observed hundred million row backfill"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "release stage defines target rows",
                    "entity": "customer_birth_decade_backfill",
                    "evidence": [
                        "scripted diagnostic actions observed release stage defines target rows"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "single massive update risks locks and io",
                    "entity": "customer_birth_decade_backfill",
                    "evidence": [
                        "scripted diagnostic actions observed single massive update risks locks and io"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "primary key range batching with throttling",
                    "entity": "customer_birth_decade_backfill",
                    "evidence": [
                        "scripted diagnostic actions observed primary key range batching with throttling"
                    ]
                },
                {
                    "type": "finding",
                    "factor": "update only release batch rows",
                    "entity": "customer_birth_decade_backfill",
                    "evidence": [
                        "scripted diagnostic actions observed update only release batch rows"
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
    evaluator=PgBusinessChangeMassiveBackfillForCustomerBirthDecadeBackfillEvaluatorCase,
    base_image_name='aiopsbench-pg-initialized:latest',
    workload_tag='initialized',
    title='Simulates a massive historical data backfill that must be chunked and throttled.',
    alert='变更发布告警：业务要求重新计算 customer_backfill 历史一年数据中的订正字段 c_birth_decade_corrected。当前 customer_backfill 仍有高并发读写，监控显示写入吞吐和 I/O 对批量变更非常敏感。请先评估变更风险，并在执行过程中持续确认业务负载保持稳定。',
    initial_state={'status': 'change_requested',
 'backfill': 'pending',
 'risk': 'full_table_update_would_create_long_transaction'},
    expected_target={'status': 'recovered',
 'backfill': 'completed',
 'strategy': 'primary_key_range_batching_with_throttling'},
    background_workload=BackgroundWorkloadSpec(
        profiles=tuple(build_massive_backfill_noise_profiles()),
        worker_count=2,
        seed=0,
        warmup_seconds=4,
    ),
    runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
    table='customer_backfill',
    pk_column='c_customer_sk',
    source_column='c_birth_year',
    target_column='c_birth_decade_corrected',
    stage_table='customer_backfill_release_stage',
    preview_table='customer_backfill_preview',
    audit_table='customer_backfill_audit_shadow',
    release_batch_id='birth_decade_2024q4',
    stage_value_column='corrected_decade',
    batch_size=5000,
    estimated_rows=100000000,
    slow_queries=('UPDATE customer_backfill SET c_birth_decade_corrected = FLOOR(c_birth_year / 10) * 10;',),
    difficulty=DifficultyCalibration(
        diagnostic_depth=2,
        environmental_complexity=0.266667,
        reference_run_ids=(
            "reference-48__pg_business_change_massive_backfill__"
            "customer_birth_decade_backfill__mock__r001",
        ),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleScenarioCase(
    PgBusinessChangeMassiveBackfillCase
):
    pass


_PGBUSINESSCHANGEMASSIVEBACKFILLSCENARIO_SIMPLE_CASE = (
    PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleScenarioCase(
        case_id="customer_loyalty_decade_backfill_simple",
        reference_report={
            "diagnosis": {
                "conditions": [
                    {
                        "type": "finding",
                        "factor": "staged loyalty backfill",
                        "entity": "customer_loyalty_decade_backfill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed staged loyalty backfill"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "approved release stage defines target rows",
                        "entity": "customer_loyalty_decade_backfill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed approved release stage defines target rows"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "single update risks online writes",
                        "entity": "customer_loyalty_decade_backfill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed single update risks online writes"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "primary key batching with throttling",
                        "entity": "customer_loyalty_decade_backfill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed primary key batching with throttling"
                        ]
                    },
                    {
                        "type": "finding",
                        "factor": "preserve rows outside the release stage",
                        "entity": "customer_loyalty_decade_backfill_simple",
                        "evidence": [
                            "scripted diagnostic actions observed preserve rows outside the release stage"
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
        evaluator=PgBusinessChangeMassiveBackfillForCustomerLoyaltyDecadeSimpleEvaluatorCase,
        base_image_name="aiopsbench-pg-initialized:latest",
        workload_tag="initialized",
        title="Simplified staged loyalty-decade backfill under a low-rate writer.",
        alert=(
            "发布告警：客户忠诚度历史分段需要按本次已审核发布清单完成订正。"
            "本次发布以 2025-01-06 00:00:00+00 冻结的清单快照为准，"
            "冻结后追加的清单行随下一发布窗口执行、本次不得修改。"
            "冻结后发布台仍会对个别在册行登记范围裁定（作废或回退），"
            "最新裁定以发布操作事件记录为准，请按最新裁定确定本次订正范围。"
            "线上客户资料仍有低频写入，未来批次预览与历史批次残留同时可见；"
            "资料表上的批次标签存在漂移，请以发布清单确定订正范围。"
            "请采用可控批次完成变更，并验证冻结切片外的记录保持原状。"
        ),
        initial_state={
            "status": "change_requested",
            "backfill": "pending",
            "symptom": "approved_slice_not_materialized",
        },
        expected_target={
            "status": "recovered",
            "backfill": "completed",
            "strategy": "stage_driven_primary_key_batching",
        },
        background_workload=BackgroundWorkloadSpec(
            profiles=tuple(
                build_massive_backfill_noise_profiles(
                    table="customer_loyalty_backfill",
                    stage_table="customer_loyalty_release_stage",
                    preview_table="customer_loyalty_preview",
                    audit_table="customer_loyalty_audit_shadow",
                    pk_column="c_customer_sk",
                    target_column="c_loyalty_decade_corrected",
                    stage_value_column="corrected_decade",
                    release_batch_id="loyalty_decade_2025q1",
                )[:2]
            ),
            worker_count=1,
            seed=0x4102,
            warmup_seconds=2,
        ),
        runtime=PostgresCaseRuntime(resources=POSTGRES_RESOURCES),
        table="customer_loyalty_backfill",
        pk_column="c_customer_sk",
        source_column="c_loyalty_year",
        target_column="c_loyalty_decade_corrected",
        stage_table="customer_loyalty_release_stage",
        preview_table="customer_loyalty_preview",
        audit_table="customer_loyalty_audit_shadow",
        release_batch_id="loyalty_decade_2025q1",
        stage_value_column="corrected_decade",
        batch_size=1000,
        estimated_rows=5000000,
        slow_queries=(
            "UPDATE customer_loyalty_backfill "
            "SET c_loyalty_decade_corrected = FLOOR(c_loyalty_year / 10) * 10;",
        ),
        legacy_draft_batch_id="loyalty_decade_2024q4",
        release_freeze_cutoff="2025-01-06 00:00:00+00",
        operation_event_table=LOYALTY_EVENT_TABLE,
        difficulty=DifficultyCalibration(
            diagnostic_depth=2,
            environmental_complexity=0.5,
            reference_run_ids=(
                "logs/traces/"
                "run_pg_business_change_massive_backfill_"
                "customer_loyalty_decade_backfill_simple_MockLLMAgent.json",
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

class PgBusinessChangeMassiveBackfillInjector(BaseFaultInjector):
    """
    模拟大规模历史字段回填变更。
    目标列被重置为 NULL，同时后台 writer 持续小批量更新业务表，暴露并发写入、QPS 和 I/O 压力。
    """

    def __init__(self):
        self._stop_event = None
        self._writer_thread = None
        self._writer_conn = None

    def install(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        print(f"[FaultInjector:PgBusinessChangeMassiveBackfillInjector] Preparing {self.table}.{self.target_column}")

        self.env.execute_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self.pk_column} integer PRIMARY KEY,
                {self.source_column} integer,
                release_batch_id text,
                c_last_update timestamptz DEFAULT now()
            );
            """
        )
        self.env.execute_sql(f"ALTER TABLE {self.table} ADD COLUMN IF NOT EXISTS release_batch_id text;")
        self.env.execute_sql(f"ALTER TABLE {self.table} ADD COLUMN IF NOT EXISTS {self.target_column} integer;")
        self.env.execute_sql(f"TRUNCATE TABLE {self.table};")
        self.env.execute_sql(
            f"""
            INSERT INTO {self.table} ({self.pk_column}, {self.source_column}, release_batch_id, {self.target_column})
            SELECT
                g * 10 + (g % 7) AS {self.pk_column},
                1970 + (g % 45) AS {self.source_column},
                CASE
                    WHEN g <= 12000 THEN '{self.release_batch_id}'
                    ELSE 'future_birth_decade_2025q1'
                END AS release_batch_id,
                NULL::integer AS {self.target_column}
            FROM generate_series(1, 20000) AS g;
            """
        )
        if self.legacy_draft_batch_id:
            # Profile tag drift: a slice of listed frozen rows carries the
            # future tag; the release list stays the correction authority.
            self.env.execute_sql(
                f"""
                UPDATE {self.table}
                SET release_batch_id = 'future_birth_decade_2025q1'
                WHERE release_batch_id = '{self.release_batch_id}'
                  AND ({self.pk_column} % 128) = 5
                  AND ({self.pk_column} % 40) <> 0;
                """
            )
            # Interrupted earlier pass: the unapproved experimental estimator
            # (round every customer up one decade) already wrote a slice of
            # listed frozen rows; the approved correction must overwrite them,
            # so completion means matching the list, not filling NULLs.
            self.env.execute_sql(
                f"""
                UPDATE {self.table}
                SET {self.target_column} = (FLOOR({self.source_column} / 10) * 10) + 10
                WHERE release_batch_id = '{self.release_batch_id}'
                  AND ({self.pk_column} % 77) = 3
                  AND ({self.pk_column} % 40) <> 0;
                """
            )
        if self.legacy_draft_batch_id:
            # Fixture: overlapping staged batches require a composite
            # key so the draft batch can coexist with the approved release list.
            self.env.execute_sql(
                f"""
                CREATE TABLE IF NOT EXISTS {self.stage_table} (
                    {self.pk_column} integer,
                    release_batch_id text NOT NULL,
                    {self.stage_value_column} integer NOT NULL,
                    source_name text NOT NULL,
                    loaded_at timestamptz DEFAULT now(),
                    PRIMARY KEY ({self.pk_column}, release_batch_id)
                );
                """
            )
        else:
            self.env.execute_sql(
                f"""
                CREATE TABLE IF NOT EXISTS {self.stage_table} (
                    {self.pk_column} integer PRIMARY KEY,
                    release_batch_id text NOT NULL,
                    {self.stage_value_column} integer NOT NULL,
                    source_name text NOT NULL,
                    loaded_at timestamptz DEFAULT now()
                );
                """
            )
        self.env.execute_sql(f"TRUNCATE TABLE {self.stage_table};")
        if self.legacy_draft_batch_id:
            self.env.execute_sql(
                f"""
                INSERT INTO {self.stage_table} (
                    {self.pk_column}, release_batch_id, {self.stage_value_column}, source_name, loaded_at
                )
                SELECT
                    g * 10 + (g % 7),
                    '{self.release_batch_id}',
                    (((1970 + (g % 45)) + CASE WHEN ((g * 10 + (g % 7)) % 11) = 0 THEN 10 ELSE 0 END) / 10) * 10,
                    'crm_birth_year_correction_delta',
                    CASE WHEN ((g * 10 + (g % 7)) % 40) = 0
                        THEN '{STAGE_DELTA_LOADED_AT}'
                        ELSE '{STAGE_INITIAL_LOADED_AT}'
                    END::timestamptz
                FROM generate_series(1, 12000) AS g;
                """
            )
            self.env.execute_sql(
                f"""
                INSERT INTO {self.stage_table} (
                    {self.pk_column}, release_batch_id, {self.stage_value_column}, source_name, loaded_at
                )
                SELECT
                    g * 10 + (g % 7),
                    '{self.legacy_draft_batch_id}',
                    ((1970 + (g % 45)) / 10) * 10 + 10,
                    '{LEGACY_DRAFT_SOURCE_NAME}',
                    '{LEGACY_DRAFT_LOADED_AT}'
                FROM generate_series(1, 20000) AS g
                WHERE (g % 23 = 5 AND g <= 12000) OR (g % 29 = 7 AND g > 12000);
                """
            )
        else:
            self.env.execute_sql(
                f"""
                INSERT INTO {self.stage_table} (
                    {self.pk_column}, release_batch_id, {self.stage_value_column}, source_name
                )
                SELECT
                    {self.pk_column},
                    '{self.release_batch_id}',
                    (({self.source_column} + CASE WHEN ({self.pk_column} % 11) = 0 THEN 10 ELSE 0 END) / 10) * 10,
                    'crm_birth_year_correction_delta'
                FROM {self.table}
                WHERE release_batch_id = '{self.release_batch_id}';
                """
            )
        self.env.execute_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {self.preview_table} (
                {self.pk_column} integer PRIMARY KEY,
                {self.source_column} integer,
                {self.target_column} integer,
                preview_batch_id text,
                updated_at timestamptz DEFAULT now()
            );
            """
        )
        self.env.execute_sql(f"TRUNCATE TABLE {self.preview_table};")
        self.env.execute_sql(
            f"""
            INSERT INTO {self.preview_table} ({self.pk_column}, {self.source_column}, {self.target_column}, preview_batch_id)
            SELECT
                900000 + g,
                1970 + (g % 45),
                NULL::integer,
                'preview_birth_decade_2025q1'
            FROM generate_series(1, 6000) AS g;
            """
        )
        self.env.execute_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {self.audit_table} (
                audit_id bigserial PRIMARY KEY,
                {self.pk_column} integer,
                release_batch_id text,
                previous_decade integer,
                {self.stage_value_column} integer,
                checked_at timestamptz DEFAULT now()
            );
            """
        )
        self.env.execute_sql(f"TRUNCATE TABLE {self.audit_table};")
        if self.legacy_draft_batch_id:
            self.env.execute_sql(
                f"""
                INSERT INTO {self.audit_table} (
                    {self.pk_column}, release_batch_id, previous_decade, {self.stage_value_column}, checked_at
                )
                SELECT
                    s.{self.pk_column},
                    s.release_batch_id,
                    (t.{self.source_column} / 10) * 10,
                    s.{self.stage_value_column},
                    '{AUDIT_APPROVED_CHECKED_AT}'
                FROM {self.stage_table} s
                JOIN {self.table} t USING ({self.pk_column})
                WHERE s.release_batch_id = '{self.release_batch_id}'
                  AND s.loaded_at = '{STAGE_INITIAL_LOADED_AT}'
                  AND (s.{self.pk_column} % 17) = 0;
                """
            )
            self.env.execute_sql(
                f"""
                INSERT INTO {self.audit_table} (
                    {self.pk_column}, release_batch_id, previous_decade, {self.stage_value_column}, checked_at
                )
                SELECT
                    s.{self.pk_column},
                    s.release_batch_id,
                    (t.{self.source_column} / 10) * 10,
                    s.{self.stage_value_column},
                    '{AUDIT_DRAFT_CHECKED_AT}'
                FROM {self.stage_table} s
                JOIN {self.table} t USING ({self.pk_column})
                WHERE s.release_batch_id = '{self.legacy_draft_batch_id}'
                  AND (s.{self.pk_column} % 13) = 0;
                """
            )
        else:
            self.env.execute_sql(
                f"""
                INSERT INTO {self.audit_table} (
                    {self.pk_column}, release_batch_id, previous_decade, {self.stage_value_column}
                )
                SELECT
                    s.{self.pk_column},
                    s.release_batch_id,
                    (t.{self.source_column} / 10) * 10,
                    s.{self.stage_value_column}
                FROM {self.stage_table} s
                JOIN {self.table} t USING ({self.pk_column})
                WHERE (s.{self.pk_column} % 17) = 0;
                """
            )
        if self.operation_event_table:
            self._install_operation_events()
        self.env.execute_sql(f"ALTER TABLE {self.table} SET (autovacuum_enabled = false);")
        self.env.execute_sql(f"ANALYZE {self.table};")
        self.env.execute_sql(f"ANALYZE {self.stage_table};")
        self.env.execute_sql(f"ANALYZE {self.preview_table};")
        self.env.execute_sql(f"ANALYZE {self.audit_table};")
        self.env.execute_sql(
            f"UPDATE pg_class SET reltuples = {self.estimated_rows} "
            f"WHERE oid = '{self.table}'::regclass;"
        )
        self.env.execute_sql(
            f"UPDATE pg_class SET reltuples = 40000000 "
            f"WHERE oid = '{self.preview_table}'::regclass;"
        )
        self._start_runtime()

    def _install_operation_events(self) -> None:
        """Post-freeze release-desk scope rulings, visible to the agent.

        Final-void rows: frozen listed rows annulled after the freeze with no
        later restore, so they roll to the next release window and must stay
        uncorrected in this window. Restored rows: annulled and later reversed,
        so they stay in scope. Delta/draft annulments and window notes are
        same-domain ruling noise already excluded by the freeze cutoff and the
        batch identity respectively.
        """
        event_table = self.operation_event_table
        self.env.execute_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {event_table} (
                event_id bigserial PRIMARY KEY,
                {self.pk_column} integer,
                release_batch_id text,
                event_type text NOT NULL
                    CHECK (event_type IN ('row_annulled', 'row_restored', 'window_noted')),
                event_note text NOT NULL,
                event_at timestamptz NOT NULL
            );
            """
        )
        self.env.execute_sql(f"TRUNCATE TABLE {event_table};")
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            VALUES
                (NULL, '{self.release_batch_id}', 'window_noted',
                 'release window frozen; the frozen list snapshot governs this window',
                 '2025-01-06 00:05:00+00'::timestamptz),
                (NULL, '{self.release_batch_id}', 'window_noted',
                 'post-freeze list delta staged; deferred rows roll to the next release window',
                 '2025-01-08 09:35:00+00'::timestamptz);
            """
        )
        # Final-void annulments: frozen, not value-drift, not annul-then-restored.
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            SELECT
                s.{self.pk_column},
                '{self.release_batch_id}',
                'row_annulled',
                '{EVENT_ANNUL_NOTE}',
                '{EVENT_ANNUL_AT}'::timestamptz
            FROM {self.stage_table} s
            WHERE s.release_batch_id = '{self.release_batch_id}'
              AND (s.{self.pk_column} % 40) <> 0
              AND (s.{self.pk_column} % 173) = 17
              AND (s.{self.pk_column} % 77) <> 3
              AND (s.{self.pk_column} % 997) <> 42;
            """
        )
        # Annul-then-restored rows: the reversal puts them back into this window.
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            SELECT
                s.{self.pk_column},
                '{self.release_batch_id}',
                'row_annulled',
                '{EVENT_ANNUL_NOTE}',
                '{EVENT_ANNUL_AT}'::timestamptz
            FROM {self.stage_table} s
            WHERE s.release_batch_id = '{self.release_batch_id}'
              AND (s.{self.pk_column} % 40) <> 0
              AND (s.{self.pk_column} % 997) = 42;
            """
        )
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            SELECT
                s.{self.pk_column},
                '{self.release_batch_id}',
                'row_restored',
                '{EVENT_RESTORE_NOTE}',
                '{EVENT_RESTORE_AT}'::timestamptz
            FROM {self.stage_table} s
            WHERE s.release_batch_id = '{self.release_batch_id}'
              AND (s.{self.pk_column} % 40) <> 0
              AND (s.{self.pk_column} % 997) = 42;
            """
        )
        # Ruling noise: post-freeze rows annulled after already rolling out of
        # the window, and the historical withdrawal of the draft batch.
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            SELECT
                s.{self.pk_column},
                '{self.release_batch_id}',
                'row_annulled',
                '{EVENT_ANNUL_NOTE}',
                '{EVENT_DELTA_ANNUL_AT}'::timestamptz
            FROM {self.stage_table} s
            WHERE s.release_batch_id = '{self.release_batch_id}'
              AND (s.{self.pk_column} % 40) = 0
              AND (s.{self.pk_column} % 89) = 13;
            """
        )
        self.env.execute_sql(
            f"""
            INSERT INTO {event_table} ({self.pk_column}, release_batch_id, event_type, event_note, event_at)
            SELECT
                s.{self.pk_column},
                '{self.legacy_draft_batch_id}',
                'row_annulled',
                '{EVENT_DRAFT_WITHDRAWN_NOTE}',
                '{EVENT_DRAFT_WITHDRAWN_AT}'::timestamptz
            FROM {self.stage_table} s
            WHERE s.release_batch_id = '{self.legacy_draft_batch_id}'
              AND (s.{self.pk_column} % 13) = 0;
            """
        )
        self.env.execute_sql(f"ANALYZE {event_table};")

    def _configure(self, config: Mapping[str, object], env) -> None:
        self.env = env
        self.table = _validate_sql_identifier(config['table'], "table")
        self.pk_column = _validate_sql_identifier(config['pk_column'], "pk_column")
        self.source_column = _validate_sql_identifier(config['source_column'], "source_column")
        self.target_column = _validate_sql_identifier(config['target_column'], "target_column")
        self.stage_table = _validate_sql_identifier(
            config['stage_table'], "stage_table")
        self.preview_table = _validate_sql_identifier(
            config['preview_table'], "preview_table")
        self.audit_table = _validate_sql_identifier(
            config['audit_table'], "audit_table")
        self.release_batch_id = str(config['release_batch_id'])
        self.stage_value_column = _validate_sql_identifier(
            config['stage_value_column'], "stage_value_column")
        self.batch_size = int(config['batch_size'])
        self.estimated_rows = int(config['estimated_rows'])
        self.legacy_draft_batch_id = config.get('legacy_draft_batch_id')
        self.operation_event_table = config.get('operation_event_table')

    def _start_runtime(self) -> None:
        import threading
        import time

        self._stop_event = threading.Event()
        self._writer_thread = threading.Thread(target=self._business_writer_loop, daemon=True)
        self._writer_thread.start()
        time.sleep(1.0)
        print("[FaultInjector:PgBusinessChangeMassiveBackfillInjector] Background writer started.")

    def _verify_persistent_state(self) -> None:
        payload = _json_object(
            self.env.execute_sql(
                f"SELECT count(*) FILTER (WHERE {self.target_column} IS NULL), "
                f"(SELECT count(*) FROM {self.stage_table} "
                f"WHERE release_batch_id = '{self.release_batch_id}'), "
                "c.reloptions "
                f"FROM {self.table} t CROSS JOIN pg_class c "
                f"WHERE c.oid = '{self.table}'::regclass GROUP BY c.reloptions;"
            ),
            "verify massive-backfill fault image",
        )
        null_rows, stage_rows, reloptions = payload["result"][0]
        if (
            int(null_rows) <= 0
            or int(stage_rows) <= 0
            or "autovacuum_enabled=false" not in (reloptions or [])
        ):
            raise RuntimeError(
                f"Massive-backfill fault image does not match the Case: "
                f"null_rows={null_rows}, stage_rows={stage_rows}, reloptions={reloptions}"
            )
        if self.operation_event_table:
            events = _json_object(
                self.env.execute_sql(
                    f"SELECT count(*) FROM {self.operation_event_table};"
                ),
                "verify massive-backfill operation event log",
            )
            event_rows = int(events["result"][0][0])
            if event_rows <= 0:
                raise RuntimeError(
                    "Massive-backfill operation event log is empty: "
                    f"event_table={self.operation_event_table}, event_rows={event_rows}"
                )

    def _business_writer_loop(self):
        import time
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.dbname,
                application_name="aiopsbench_massive_backfill_writer",
                connect_timeout=3,
            )
            conn.autocommit = True
            self._writer_conn = conn
            offset = 0
            while self._stop_event and not self._stop_event.is_set():
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        UPDATE {self.table}
                        SET c_last_update = now()
                        WHERE {self.pk_column} IN (
                            SELECT {self.pk_column}
                            FROM {self.table}
                            ORDER BY {self.pk_column}
                            OFFSET %s LIMIT 25
                        );
                        """,
                        (offset,),
                    )
                offset = (offset + 25) % max(self.batch_size, 25)
                time.sleep(0.2)
        except Exception as exc:
            print(f"[FaultInjector:PgBusinessChangeMassiveBackfillInjector] Writer stopped: {exc}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def prepare_observability(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        pending_state = env.execute_sql(
            f"SELECT count(*) AS pending_rows, min({self.pk_column}), max({self.pk_column}) "
            f"FROM {self.table} WHERE {self.target_column} IS NULL;"
        )
        return {"pending_state": pending_state}

    def quiesce(self, context: FaultLifecycleContext):
        """Clean up background writer thread for teardown."""
        print("[FaultInjector:PgBusinessChangeMassiveBackfillInjector] quiesce...")
        if self._stop_event:
            self._stop_event.set()
        steps = []
        if self._writer_conn is not None:
            steps.append(("close writer connection", self._writer_conn.close))
        if self._writer_thread is not None:
            steps.append((
                "join writer thread",
                lambda: _join_thread(
                    self._writer_thread,
                    5,
                    "massive-backfill writer thread",
                ),
            ))
        _run_cleanup_steps(
            f"Massive-backfill cleanup for {context.scenario_id}/{context.case_id}",
            steps,
        )
        self._writer_thread = None
        self._writer_conn = None
        self._stop_event = None

    def recover(self, context: FaultLifecycleContext):
        self.quiesce(context)
        env = context.env
        self._configure(context.config, env)
        print("[FaultInjector:PgBusinessChangeMassiveBackfillInjector] Recovering target table state...")
        if not env.reconnect():
            raise RuntimeError(
                f"Massive-backfill recovery could not reconnect: "
                f"scenario={context.scenario_id}, case={context.case_id}"
            )
        statements = (
            f"DROP TABLE IF EXISTS {self.audit_table};",
            f"DROP TABLE IF EXISTS {self.preview_table};",
            f"DROP TABLE IF EXISTS {self.stage_table};",
        )
        if self.operation_event_table:
            statements += (f"DROP TABLE IF EXISTS {self.operation_event_table};",)
        statements += (
            f"ALTER TABLE {self.table} DROP COLUMN IF EXISTS {self.target_column};",
            f"ALTER TABLE {self.table} RESET (autovacuum_enabled);",
            f"ANALYZE {self.table};",
        )
        for statement in statements:
            _require_sql_success(
                env.execute_sql(statement),
                f"recover massive-backfill artifact with {statement}",
            )

    def activate(self, context: FaultLifecycleContext):
        config = context.config
        env = context.env
        self._configure(config, env)
        self._verify_persistent_state()
        self._start_runtime()
        print("[FaultInjector:PgBusinessChangeMassiveBackfillInjector] Background writer re-activated.")


class PgBusinessChangeMassiveBackfillScenario(PostgresScenario):
    scenario_id = 'pg_business_change_massive_backfill'
    description = 'Simulates a massive historical data backfill that must be chunked and throttled.'
    cases = (
        _PGBUSINESSCHANGEMASSIVEBACKFILLSCENARIO_CASE,
        _PGBUSINESSCHANGEMASSIVEBACKFILLSCENARIO_SIMPLE_CASE,
    )

    def build_fault_plan(self, case: PgBusinessChangeMassiveBackfillCase) -> tuple[FaultPlan, ...]:
        return (
            FaultPlan(
                injector_type=PgBusinessChangeMassiveBackfillInjector,
                config={
                    'table': case.table,
                    'pk_column': case.pk_column,
                    'source_column': case.source_column,
                    'target_column': case.target_column,
                    'stage_table': case.stage_table,
                    'preview_table': case.preview_table,
                    'audit_table': case.audit_table,
                    'release_batch_id': case.release_batch_id,
                    'stage_value_column': case.stage_value_column,
                    'batch_size': case.batch_size,
                    'estimated_rows': case.estimated_rows,
                    'legacy_draft_batch_id': case.legacy_draft_batch_id,
                    'operation_event_table': case.operation_event_table,
                },
            ),
        )
