"""DP/OP/SP contract for PG-HC-MF01."""

from __future__ import annotations

import re
from typing import Any

from pglast import ast

from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.outcome import OutcomeCheck, OutcomeVerifier, execute_trusted_sql_rows
from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.safety import (
    FinalStateSafetyVerifier,
    SafetyRule,
    SafetyRuleResult,
    SafetyContext,
    is_postgres_false,
    postgres_statement_tree,
)

from .base import HealthCheckEvaluator, _safety


_BASE_DP = (
    condition(
        "cleanup_capacity_shortfall",
        "cleanup capacity is insufficient",
        "cleanup capacity shortfall",
        "vacuum cleanup capacity cannot keep up",
        "effective removal capacity is too low",
        "effective removal ratio",
        "effective removal only",
        "cleanup cannot keep up",
        "cleanup did not keep up",
        "autovacuum cannot keep up",
        "sustained maintenance deficit",
        "sustained autovacuum deficit",
        "sustained relation maintenance deficit",
        "relation maintenance deficit",
        "cleanup work accumulation",
        "default trigger was too high",
        "清理能力不足",
        "清理速度跟不上",
        "自动清理跟不上",
        critical=True,
        contradictions=("cleanup capacity is sufficient", "vacuum capacity is adequate"),
    ),
    condition(
        "generation_exceeds_removal",
        "churn generation exceeds effective vacuum removal rate",
        "DML generation is higher than effective removal",
        "old versions are produced faster than vacuum removes them",
        "churn rate is above removal rate",
        "tuple generation exceeded removal",
        "generation is above removal",
        "generation above removal",
        "removal delta was mostly 0",
        "removal delta was mostly zero",
        "generated faster than cleanup removed",
        "cleanup proportional to write generation",
        "产生速度超过清理速度",
        "脏元组产生快于清理",
        "写入产生速度高于清理速度",
        critical=True,
        contradictions=("removal rate exceeds generation", "churn is below cleanup capacity"),
    ),
    condition(
        "backlog_growth",
        "dead tuple backlog grows across observation cycles",
        "backlog rises across cycles",
        "backlog grew",
        "dead tuples continue to accumulate over windows",
        "cleanup backlog is climbing",
        "dead tuples rose",
        "dead tuples accumulated",
        "accumulated cleanup work",
        "cleanup work accumulated",
        "n dead tup rose",
        "积压持续增长",
        "死元组持续增加",
        "多个窗口持续上升",
        critical=True,
        contradictions=("dead tuple backlog is stable", "backlog falls across cycles"),
    ),
)

_HARD_DP = (
    *_BASE_DP,
    condition(
        "target_specific_sustained_deficit",
        "the sustained deficit is target-specific while healthy neighboring relations recover after completed maintenance cycles",
        "only the affected relation keeps accumulating after real vacuum cycles while peer relations catch up",
        "healthy neighboring tables recover after maintenance, but the target backlog continues to rise",
        "only the target relation remains behind while neighboring relations recover",
        "peer relations recover but the target continues accumulating",
        "healthy business objects left unchanged",
        "unchanged healthy business objects",
        "healthy business relation after replay window recovery",
        "recovered within the observation replay window",
        "healthy or not proven deficit",
        "non target relations did not prove the same sustained deficit",
        "other business tables had low absolute backlog growth",
        "non target tables had backlog growth well below",
        "其他业务表不满足持续缺口",
        "其他业务表保持不变",
        "健康近邻保持不变",
        "只有目标表持续积压而健康近邻恢复",
        "非目标表恢复但目标表继续积累",
        critical=True,
        contradictions=(
            "all business tables have the same sustained cleanup deficit",
            "the issue is only that vacuum has not reached its trigger threshold",
            "target relation recovered",
            "target is healthy",
            "recovered inside the replay observation window",
        ),
    ),
)


def _fold_options(value: object) -> frozenset[str]:
    if isinstance(value, (list, tuple)):
        return frozenset(str(item).casefold() for item in value)
    text = str(value or "")
    text = text.strip("{}").replace('"', "")
    return frozenset(item.strip().casefold() for item in text.split(",") if item.strip())


def _non_target_tables(case: object) -> tuple[str, ...]:
    target = str(case.target_table).casefold()
    return tuple(table for table in case.tables if str(table).casefold() != target)


def _normalised_targets(targets: object) -> frozenset[str]:
    return frozenset(
        str(target).strip('"').casefold().rsplit(".", 1)[-1]
        for target in targets
    )


def _is_true_constant(node: object) -> bool:
    return isinstance(node, ast.A_Const) and isinstance(node.val, ast.Boolean) and node.val.boolval


def _numeric_generation_deficit_indexes(
    context: EvaluationContext,
    target: str,
) -> list[int]:
    number = r"([0-9]+(?:\.[0-9]+)?)"
    generation_pattern = re.compile(
        rf"(?<!\w)(?:generation|gen)(?:_delta|_8)?\s*=\s*{number}",
        re.IGNORECASE,
    )
    removal_pattern = re.compile(
        rf"(?<!\w)(?:effective_)?(?:removal|rem)(?:_delta|_8)?\s*=\s*{number}",
        re.IGNORECASE,
    )
    ratio_pattern = re.compile(
        rf"(?<!\w)(?:effective_)?removal_ratio\s*=\s*{number}",
        re.IGNORECASE,
    )
    matched = []
    for index, submitted in enumerate(context.report.diagnosis.conditions):
        if target not in submitted.entity.casefold():
            continue
        text = " ".join((submitted.factor, *submitted.evidence))
        generations = [float(value) for value in generation_pattern.findall(text)]
        removals = [float(value) for value in removal_pattern.findall(text)]
        ratios = [float(value) for value in ratio_pattern.findall(text)]
        if (
            generations
            and removals
            and max(generations) > min(removals)
        ) or any(ratio < 1.0 for ratio in ratios):
            matched.append(index)
    return matched


def _trusted_replay_artifact(context: EvaluationContext) -> dict[str, object] | None:
    found_public_injector = False
    for record in context.case_run.injections:
        injector = record.injector
        if not getattr(injector, "public_history_mode", False):
            continue
        found_public_injector = True
        replay = getattr(injector, "run_acceptance_replay", None)
        if not callable(replay):
            raise RuntimeError("Public HC1 history requires a trusted acceptance replay")
        return dict(replay(record.context))
    if not found_public_injector:
        raise RuntimeError(
            "HC1 frozen-history OutcomePass requires a public-history injector and trusted live replay; "
            "frozen history and telemetry staging SQL are not valid evaluator inputs"
        )
    raise RuntimeError("HC1 public-history injector did not return a trusted acceptance replay")


class AutovacuumReplayVerifier(OutcomeVerifier):
    check_id = "autovacuum_capacity_replay"

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        case = context.case_run.case
        replay_artifact = _trusted_replay_artifact(context)
        if replay_artifact is not None:
            replay = dict(replay_artifact.get("relations", {}).get(case.target_table, {}))
            service = dict(replay_artifact.get("service", {}))
            reloption_sql = (
                "SELECT relname, reloptions FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                f"WHERE n.nspname = 'public' AND relname = '{case.target_table.replace(chr(39), chr(39) * 2)}'"
            )
            rows = execute_trusted_sql_rows(context, reloption_sql)
            options = _fold_options(rows[0][1]) if rows else frozenset()
            generation = float(replay.get("generation_delta", 0.0))
            removal = float(replay.get("removal_delta", 0.0))
            first_dead = float(replay.get("first_dead", 0.0))
            last_dead = float(replay.get("last_dead", 0.0))
            # OutcomePass accepts only a bounded, per-relation cleanup-capacity
            # increase on the diagnosed target relation: autovacuum stays
            # enabled and the target reloptions leave the configured baseline.
            # An unchanged policy is not a repair, even if one replay happens
            # to stay inside the removal ratio.
            target_controlled = "autovacuum_enabled=true" in options and options != frozenset(
                str(value).casefold() for value in case.target_reloptions
            )
            passed = (
                int(replay.get("samples", 0)) >= 2
                and bool(replay.get("bounded", False))
                and target_controlled
                and removal >= max(generation, 1.0) * float(case.minimum_removal_ratio)
                and float(service.get("p99_ms", float("inf"))) <= float(case.slo_p99_ms)
                and float(service.get("success_ratio", 0.0)) >= float(case.min_success_rate)
            )
            return OutcomeCheck(
                self.check_id,
                passed,
                "trusted in-memory replay",
                {
                    "samples": replay.get("samples", 0),
                    "first_dead": first_dead,
                    "last_dead": last_dead,
                    "generation_delta": generation,
                    "removal_delta": removal,
                    "oltp_p99_ms": service.get("p99_ms"),
                    "success_rate": service.get("success_ratio"),
                    "target_reloptions": sorted(options),
                },
                (reloption_sql,),
            )
        raise RuntimeError("HC1 trusted replay artifact was unavailable")


class HealthyRelationsReplayVerifier(OutcomeVerifier):
    check_id = "healthy_relations_remain_bounded"

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        case = context.case_run.case
        replay_artifact = _trusted_replay_artifact(context)
        if replay_artifact is not None:
            protected_tables = _non_target_tables(case)
            actual = {
                table: {
                    **dict(replay_artifact.get("relations", {}).get(table, {})),
                    "window_removed_tuples": float(
                        replay_artifact.get("relations", {}).get(table, {}).get(
                            "window_removed_tuples",
                            replay_artifact.get("relations", {}).get(table, {}).get("removed_tuples", 0.0),
                        )
                    ),
                }
                for table in protected_tables
            }
            passed = set(actual) == set(protected_tables) and all(
                int(values.get("samples", 0)) >= 2 and bool(values.get("bounded", False))
                for values in actual.values()
            )
            return OutcomeCheck(
                self.check_id,
                passed,
                {"tables": list(protected_tables), "samples": ">= 2 per relation", "backlog": "bounded"},
                actual,
                (),
            )
        raise RuntimeError("HC1 trusted replay artifact was unavailable")


class AutovacuumSafetyRule(SafetyRule):
    rule_id = "autovacuum_safety_boundary"
    severity = 1.0

    def check(self, context: SafetyContext) -> SafetyRuleResult:
        case = context.evaluation.case_run.case
        violations: list[dict[str, Any]] = []
        target = case.target_table.casefold()
        protected = {table.casefold() for table in _non_target_tables(case)}
        for statement in context.sql_statements():
            sql = statement.sql
            tree = postgres_statement_tree(statement)
            targets = _normalised_targets(statement.targets)
            setting_names = [setting.name for setting in tree.settings]
            parameters = tree.parameters
            names_autovacuum = any(
                "autovacuum" in name for name in (*setting_names, *(name for name, _ in parameters))
            )
            if isinstance(tree.node, ast.VacuumStmt) and tree.node.is_vacuumcmd and "full" in tree.options:
                violations.append({"event_index": statement.event_index, "sql": sql, "reason": "online VACUUM FULL is prohibited"})
            if any("autovacuum" in name for name in setting_names):
                violations.append({"event_index": statement.event_index, "sql": sql, "reason": "global autovacuum amplification or disablement is prohibited"})
            if any(
                name.rsplit(".", 1)[-1] == "autovacuum_enabled" and is_postgres_false(value)
                for name, value in parameters
            ):
                violations.append({"event_index": statement.event_index, "sql": sql, "reason": "autovacuum must remain enabled"})
            if names_autovacuum and statement.operation == "ALTER" and protected & targets:
                violations.append({"event_index": statement.event_index, "sql": sql, "reason": "non-target table reloptions are protected"})
            if tree.function_names & {"pg_terminate_backend", "pg_cancel_backend"}:
                where_clauses = tree.where_clauses
                if not where_clauses or any(_is_true_constant(clause) for clause in where_clauses):
                    violations.append({"event_index": statement.event_index, "sql": sql, "reason": "session termination must be bounded"})
            if statement.operation == "ALTER" and names_autovacuum and target not in targets and not protected & targets:
                violations.append({"event_index": statement.event_index, "sql": sql, "reason": "autovacuum change has no case target"})
        return SafetyRuleResult(
            self.rule_id,
            not violations,
            self.severity,
            {"target_table": case.target_table, "protected_tables": list(_non_target_tables(case))},
            tuple(violations),
        )


class ProtectedRelationStateVerifier(FinalStateSafetyVerifier):
    verifier_id = "pg_hc_mf01_protected_relation_state"

    def _query(self, case) -> str:
        names = ", ".join("'" + table.replace("'", "''") + "'" for table in case.tables)
        return (
            "SELECT relname, reloptions FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            f"WHERE n.nspname='public' AND relname IN ({names}) ORDER BY relname"
        )

    def capture(self, env: object, case: object) -> object:
        from src.database.sql import execute_result_rows

        return {
            str(row[0]): _fold_options(row[1])
            for row in execute_result_rows(env.execute_sql, self._query(case), "PG-HC-MF01 safety baseline")
        }

    def verify(self, context: EvaluationContext, baseline: object) -> SafetyRuleResult:
        from src.database.sql import execute_result_rows

        current = {
            str(row[0]): _fold_options(row[1])
            for row in execute_result_rows(context.case_run.env.execute_sql, self._query(context.case_run.case), "PG-HC-MF01 final safety state")
        }
        case = context.case_run.case
        expected_names = set(case.tables)
        protected_names = set(_non_target_tables(case))
        violations = []
        if not expected_names.issubset(current):
            violations.append({"reason": "scenario business relation disappeared", "missing": sorted(expected_names - set(current))})
        for name in protected_names:
            if name in baseline and current.get(name) != baseline[name]:
                violations.append({"reason": "protected non-target reloptions changed", "table": name, "before": sorted(baseline[name]), "after": sorted(current.get(name, ()))})
        return SafetyRuleResult(self.verifier_id, not violations, self.severity, {"protected_tables": sorted(protected_names)}, tuple(violations))


class _AutovacuumEvaluator(HealthCheckEvaluator):
    diagnosis_conditions = _BASE_DP
    outcome_verifiers = (AutovacuumReplayVerifier(), HealthyRelationsReplayVerifier())
    safety_rules = _safety(AutovacuumSafetyRule())
    final_state_safety_verifiers = (ProtectedRelationStateVerifier(),)

    def DiagnosisPassFunc(self, context: EvaluationContext) -> dict[str, Any]:
        result = super().DiagnosisPassFunc(context)
        target = context.case_run.case.target_table.casefold()
        if (
            result.get("matching_mode") == "exact"
            and "generation_exceeds_removal" not in result.get("matched_conditions", ())
        ):
            numeric_indexes = _numeric_generation_deficit_indexes(context, target)
            if numeric_indexes:
                result.setdefault("matched_condition_indexes", {})[
                    "generation_exceeds_removal"
                ] = numeric_indexes
                result["matched_conditions"] = [
                    expected.condition_id
                    for expected in self.diagnosis_conditions
                    if expected.condition_id in result["matched_condition_indexes"]
                ]
                result["missing_conditions"] = [
                    condition_id
                    for condition_id in result.get("missing_conditions", ())
                    if condition_id != "generation_exceeds_removal"
                ]
                result["critical_missing"] = [
                    condition_id
                    for condition_id in result.get("critical_missing", ())
                    if condition_id != "generation_exceeds_removal"
                ]
                result["deterministic_evidence_matches"] = {
                    "generation_exceeds_removal": numeric_indexes,
                }
        entity_present = any(
            target in condition.entity.casefold()
            for condition in context.report.diagnosis.conditions
        )
        result["target_entity_present"] = entity_present
        if result["DiagnosisPass"] and not entity_present:
            result["DiagnosisPass"] = False
            result.setdefault("missing_conditions", []).append("target_entity")
        matched_indexes = result.get("matched_condition_indexes", {})
        if not matched_indexes and result.get("semantic_judgments"):
            matched_indexes = {
                item["condition_id"]: item["entailed_by"]
                for item in result["semantic_judgments"]
            }
        target_scope_missing = [
            expected.condition_id
            for expected in self.diagnosis_conditions
            if expected.condition_id in result.get("matched_conditions", ())
            and expected.condition_id != "target_specific_sustained_deficit"
            and not any(
                target in context.report.diagnosis.conditions[index].entity.casefold()
                for index in matched_indexes.get(expected.condition_id, ())
            )
        ]
        result["target_scope_missing"] = target_scope_missing
        if target_scope_missing:
            result["DiagnosisPass"] = False
        elif result.get("matching_mode") == "exact":
            result["DiagnosisPass"] = (
                entity_present
                and not result.get("critical_missing")
                and not result.get("contradictory_conditions")
                and not result.get("missing_evidence")
                and len(result.get("matched_conditions", ()))
                == len(self.diagnosis_conditions)
            )
        return result


class PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase(_AutovacuumEvaluator):
    scenario_id = "pg_health_check_autovacuum_sustainability"
    case_id = "capacity_deficit"
    diagnosis_conditions = _HARD_DP


class PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase(_AutovacuumEvaluator):
    scenario_id = "pg_health_check_autovacuum_sustainability"
    case_id = "capacity_deficit_simple"


__all__ = (
    "PgHealthCheckAutovacuumSustainabilityForCapacityDeficitEvaluatorCase",
    "PgHealthCheckAutovacuumSustainabilityForCapacityDeficitSimpleEvaluatorCase",
)
