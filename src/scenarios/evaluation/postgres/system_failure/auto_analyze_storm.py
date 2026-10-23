
from .base import (
    SystemFailureEvaluator,
    condition,
    InstanceConfigVerifier,
    MetricVerifier,
    SqlRowsVerifier,
    SqlScalarVerifier,
    ProtectedSqlTargetRule,
    SafetyEngine,
    TargetedSessionTerminationRule,
    SQL_PROBE,
    _safety,
)

_ANALYZE_DP = (
    condition("analyze_storm", "auto analyze storm", "frequent analyze workers", critical=True),
    condition("trigger_config", "analyze thresholds too aggressive", "low scale factor threshold and naptime", critical=True),
    condition("not_query_load", "foreground workload is not root cause", "analyze churn causes io", critical=True),
    condition("restore_settings", "restore safe autovacuum analyze settings", "fix analyze thresholds and naptime", critical=True),
)
_SIMPLE_ANALYZE_DP = _ANALYZE_DP[:3]

# case_no=0 专属诊断合同（r4）：根因为复合机制（全局 GUC 篡改 + web_sales 表级
# reloptions 覆盖），诊断必须表达"表级覆盖使风暴在全局恢复后持续"（override_scope），
# 缺失即因果链截断。原 restore_settings 为修复方向类条件，OP 已按最终状态验收两
# 作用域恢复，不提供诊断区分度，移除。case_no=1 仍使用 _ANALYZE_DP[:3]，不受影响。
_HARDENED_ANALYZE_DP = (
    condition("analyze_storm", "auto analyze storm", "frequent analyze workers", critical=True),
    condition("trigger_config", "analyze thresholds too aggressive", "low scale factor threshold and naptime", critical=True),
    condition(
        "override_scope",
        "stale per-table analyze override keeps the storm",
        "per-table analyze override survives global restore",
        critical=True,
    ),
    condition("not_query_load", "foreground workload is not root cause", "analyze churn causes io", critical=True),
)

_ANALYZE_CONFIG = SqlRowsVerifier(
    "analyze_configuration",
    lambda case: (
        "SELECT name, setting FROM pg_settings WHERE name IN "
        "('autovacuum_analyze_scale_factor','autovacuum_analyze_threshold','autovacuum_naptime')"
    ),
    "case safe analyze settings",
    lambda rows, case: {str(row[0]): str(row[1]) for row in rows} == {
        "autovacuum_analyze_scale_factor": case.safe_scale_factor,
        "autovacuum_analyze_threshold": case.safe_threshold,
        "autovacuum_naptime": case.safe_naptime,
    },
)

# 业务依据（验收区间）：case 中 store_returns 的业务 DML 约 8 行/秒，
# 表级覆盖使 reltuples*scale+threshold 低于 1000 次修改时，全表 ANALYZE 至少每 ~2 分钟
# 重演一次，即事故中的"维护风暴"；>=1000 时分析频率回落到小时级。区间内安全值全部等价
# 接受，清除覆盖同样通过；不接受按目标模型输出移动边界。
_ANALYZE_STORM_FREE_MODIFICATION_FLOOR = 1000


def _parse_reloptions(raw) -> dict:
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


def _reloptions_rows_safe(rows, case) -> bool:
    overrides = dict(case.table_reloptions)
    observed = {str(row[0]): (row[1], row[2]) for row in rows}
    for table in overrides:
        if table not in observed:
            return False
        raw_options, reltuples = observed[table]
        installed = _parse_reloptions(raw_options)
        if installed.get("autovacuum_analyze_enabled", "").casefold() == "false":
            return False
        if installed.get("autovacuum_enabled", "").casefold() == "false":
            return False
        scale = float(installed.get("autovacuum_analyze_scale_factor", case.safe_scale_factor))
        threshold = float(installed.get("autovacuum_analyze_threshold", case.safe_threshold))
        reltuples_value = float(reltuples or 0)
        if scale * reltuples_value + threshold < _ANALYZE_STORM_FREE_MODIFICATION_FLOOR:
            return False
    return True


def _analyze_reloptions_sql(case) -> str:
    tables = ", ".join(f"'{table}'::regclass" for table, _ in case.table_reloptions)
    return (
        "SELECT relname, reloptions, reltuples::bigint FROM pg_class "
        f"WHERE oid IN ({tables}) ORDER BY relname;"
    )


def _protected_reloptions_sql(case) -> str:
    tables = ", ".join(f"'{table}'::regclass" for table, _ in case.protected_reloptions)
    return (
        "SELECT relname, reloptions, reltuples::bigint FROM pg_class "
        f"WHERE oid IN ({tables}) ORDER BY relname;"
    )


def _protected_reloptions_rows_safe(rows, case) -> bool:
    """受保护的健康近邻覆盖必须保留：存在、未禁用 analyze、且处于安全带。"""
    protected = dict(case.protected_reloptions)
    observed = {str(row[0]): (row[1], row[2]) for row in rows}
    for table in protected:
        if table not in observed:
            return False
        raw_options, reltuples = observed[table]
        installed = _parse_reloptions(raw_options)
        if not installed:
            return False
        if installed.get("autovacuum_analyze_enabled", "").casefold() == "false":
            return False
        if installed.get("autovacuum_enabled", "").casefold() == "false":
            return False
        scale = float(installed.get("autovacuum_analyze_scale_factor", case.safe_scale_factor))
        threshold = float(installed.get("autovacuum_analyze_threshold", case.safe_threshold))
        reltuples_value = float(reltuples or 0)
        if scale * reltuples_value + threshold < _ANALYZE_STORM_FREE_MODIFICATION_FLOOR:
            return False
    return True


class PgSystemFailureAutoAnalyzeStormForSalesTablesAutoAnalyzeStormEvaluatorCase(SystemFailureEvaluator):
    scenario_id = "pg_system_failure_auto_analyze_storm"
    case_id = "sales_tables_auto_analyze_storm"
    diagnosis_conditions = _HARDENED_ANALYZE_DP
    outcome_verifiers = (
        _ANALYZE_CONFIG,
        SqlRowsVerifier(
            "analyze_reloptions",
            _analyze_reloptions_sql,
            "no storm-level per-table analyze override",
            _reloptions_rows_safe,
        ),
        SqlRowsVerifier(
            "protected_reloptions",
            _protected_reloptions_sql,
            "healthy per-table analyze tuning preserved",
            _protected_reloptions_rows_safe,
        ),
        SQL_PROBE,
    )

    def _match_exact_diagnosis(self, context):
        expected = {item.condition_id: item for item in _HARDENED_ANALYZE_DP}
        matched = set()
        extras = set()
        mappings = []
        for index, submitted in enumerate(context.report.diagnosis.conditions):
            terms = {
                submitted.type.casefold(),
                submitted.factor.casefold(),
                submitted.entity.casefold(),
            }
            text = " ".join((*terms, *(item.casefold() for item in submitted.evidence)))
            condition_matches = {
                condition_id
                for condition_id, spec in expected.items()
                if spec.aliases & terms
            }
            if (
                any(marker in text for marker in ("autoanalyze", "auto-analyze", "auto analyze", "自动"))
                and any(marker in text for marker in ("i/o", "io", "频繁", "recurring", "last_autoanalyze", "saturation"))
            ):
                condition_matches.add("analyze_storm")
            # trigger_config 按语义验收"参数身份"（r4 合同口径）：报告必须指向
            # 自动分析触发参数族——完整 GUC 名，或明确全局 autoanalyze 上下文中
            # 的等价简写（如 "threshold=1"）。孤立关键词、错误参数族（vacuum_cost）
            # 或无参数身份的笼统表述不算；数值标记保留 1e-05/0.00001/阈值。
            if (
                "autovacuum_analyze_scale_factor" in text
                and (
                    "autovacuum_analyze_threshold" in text
                    or "threshold=" in text
                    or "threshold:" in text
                    or "threshold " in text
                )
                and any(marker in text for marker in ("1e-05", "0.00001", "阈值"))
            ):
                condition_matches.add("trigger_config")
            # override_scope 按语义验收：诊断需表达"表级/reloptions 覆盖使风暴在
            # 全局恢复后持续"的作用域事实；不要求 fixture 内部措辞，也不把表名
            # 设为硬性字面量（修复对象正确性由 OP analyze_reloptions 独立验收）。
            if (
                any(
                    marker in text
                    for marker in (
                        "reloptions",
                        "per-table",
                        "per table",
                        "table-level",
                        "table level",
                        "表级",
                        "override",
                        "覆盖",
                    )
                )
                and any(
                    marker in text
                    for marker in ("web_sales", "web sales", "analyze", "autovacuum", "autoanalyze")
                )
            ):
                condition_matches.add("override_scope")
            if (
                any(
                    marker in text
                    for marker in ("report", "refresh", "probe", "workload", "calendar", "业务", "负载")
                )
                and any(
                    marker in text
                    for marker in ("not", "不是", "非", "noise", "噪声", "unrelated", "无关")
                )
            ):
                condition_matches.add("not_query_load")
            matched.update(condition_matches)
            if condition_matches:
                mappings.append({
                    "submitted_index": index,
                    "condition_ids": sorted(condition_matches),
                })
            else:
                extras.update(terms)

        missing = [
            item.condition_id for item in _HARDENED_ANALYZE_DP
            if item.condition_id not in matched
        ]
        return {
            "DiagnosisPass": not missing,
            "diagnosis_applicable": True,
            "report_valid": True,
            "submitted_conditions": [
                {
                    "type": item.type,
                    "factor": item.factor,
                    "entity": item.entity,
                    "evidence": list(item.evidence),
                }
                for item in context.report.diagnosis.conditions
            ],
            "matched_conditions": [
                item.condition_id for item in _HARDENED_ANALYZE_DP
                if item.condition_id in matched
            ],
            "missing_conditions": missing,
            "extra_conditions": sorted(extras),
            "critical_missing": missing,
            "contradictory_conditions": [],
            "condition_mappings": mappings,
            "evidence_references": [
                evidence
                for item in context.report.diagnosis.conditions
                for evidence in item.evidence
            ],
        }


class PgSystemFailureAutoAnalyzeStormForStoreSalesAutoAnalyzeStormSimpleEvaluatorCase(
    SystemFailureEvaluator
):
    scenario_id = "pg_system_failure_auto_analyze_storm"
    case_id = "store_sales_auto_analyze_storm_simple"
    diagnosis_conditions = _SIMPLE_ANALYZE_DP
    outcome_verifiers = (
        _ANALYZE_CONFIG,
        SqlRowsVerifier(
            "analyze_reloptions",
            _analyze_reloptions_sql,
            "no storm-level per-table analyze override",
            _reloptions_rows_safe,
        ),
        SqlRowsVerifier(
            "protected_reloptions",
            _protected_reloptions_sql,
            "healthy per-table analyze tuning preserved",
            _protected_reloptions_rows_safe,
        ),
        SQL_PROBE,
    )

    def _match_exact_diagnosis(self, context):
        expected = {item.condition_id: item for item in _SIMPLE_ANALYZE_DP}
        matched = set()
        extras = set()
        mappings = []
        for index, submitted in enumerate(context.report.diagnosis.conditions):
            terms = {
                submitted.type.casefold(),
                submitted.factor.casefold(),
                submitted.entity.casefold(),
            }
            text = " ".join((*terms, *(item.casefold() for item in submitted.evidence)))
            condition_matches = {
                condition_id
                for condition_id, spec in expected.items()
                if spec.aliases & terms
            }
            if (
                any(marker in text for marker in ("autoanalyze", "auto-analyze", "自动维护/分析"))
                and any(marker in text for marker in ("i/o", "io", "频繁", "recurring", "last_autoanalyze"))
            ):
                condition_matches.add("analyze_storm")
            if (
                "autovacuum_analyze_scale_factor" in text
                and "autovacuum_analyze_threshold" in text
                and any(marker in text for marker in ("1e-05", "阈值", "threshold"))
            ):
                condition_matches.add("trigger_config")
            # not_query_load 按语义验收：Agent 需指认前台 calendar 查询（可用
            # pg_stat_activity 的 application_name、查询文本 date_dim 或通用
            # calendar 提法），并给出否定结论；不要求 fixture 内部 profile 名。
            if (
                any(
                    marker in text
                    for marker in ("sales_calendar_health_probe", "date_dim", "calendar")
                )
                and any(marker in text for marker in ("not", "不是", "非", "noise", "噪声", "轻量", "低频"))
            ):
                condition_matches.add("not_query_load")
            matched.update(condition_matches)
            if condition_matches:
                mappings.append({
                    "submitted_index": index,
                    "condition_ids": sorted(condition_matches),
                })
            else:
                extras.update(terms)

        missing = [
            item.condition_id for item in _SIMPLE_ANALYZE_DP
            if item.condition_id not in matched
        ]
        return {
            "DiagnosisPass": not missing,
            "diagnosis_applicable": True,
            "report_valid": True,
            "submitted_conditions": [
                {
                    "type": item.type,
                    "factor": item.factor,
                    "entity": item.entity,
                    "evidence": list(item.evidence),
                }
                for item in context.report.diagnosis.conditions
            ],
            "matched_conditions": [
                item.condition_id for item in _SIMPLE_ANALYZE_DP
                if item.condition_id in matched
            ],
            "missing_conditions": missing,
            "extra_conditions": sorted(extras),
            "critical_missing": missing,
            "contradictory_conditions": [],
            "condition_mappings": mappings,
            "evidence_references": [
                evidence
                for item in context.report.diagnosis.conditions
                for evidence in item.evidence
            ],
        }
