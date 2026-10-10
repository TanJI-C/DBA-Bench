from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from .dataset import DatasetSpec, load_dataset_lock, sha256
from .token_accounting import Tokenizers, account_tokens, load_token_config
from src.scenarios.case_tags import CASE_TAGS


SCENARIO_ATTRIBUTE_PATHS = {
    "postgresql": Path("data/scenarios/postgres_case_attributes.yaml"),
    "tidb": Path("data/scenarios/tidb_case_attributes.yaml"),
}
DATABASE_LABELS = {"postgresql": "PostgreSQL", "tidb": "TiDB"}
TOKEN_CONFIG_PATH = Path("data/model_token_costs.yaml")
TOKENIZER_CACHE_PATH = Path(".cache/tokenizers")
MODEL_GROUP_PATH = Path("data/model_groups.yaml")
SCENARIO_ATTRIBUTE_VALUES = {
    "category": {
        "query_perf",
        "system_failure",
        "health_check",
        "business_change",
        "resource_governance",
    },
    "difficulty": {"easy", "hard"},
    "diagnostic_depth": {"direct", "deep"},
    "environmental_complexity": {"low", "high"},
    "evidence_modality": {"single", "multiple"},
    "temporal_requirement": {"snapshot", "cross_window", "causal_sequence"},
}
SCENARIO_CATEGORY_VALUES = {
    "postgresql": {"query_perf", "system_failure", "health_check", "business_change", "resource_governance"},
    "tidb": SCENARIO_ATTRIBUTE_VALUES["category"],
}
RUN_COLUMNS = (
    "dataset_id",
    "dataset_lock_sha256",
    "data_status",
    "metric_contract",
    "scenario_annotation_version",
    "scenario_annotation_status",
    "database",
    "category",
    "difficulty",
    "diagnostic_depth",
    "environmental_complexity",
    "evidence_modality",
    "evidence_modality_count",
    "temporal_requirement",
    "scenario_id",
    "case_id",
    "citation_tag",
    "baseline_id",
    "source_agent_id",
    "agent_mode",
    "model",
    "model_group",
    "experiment_id",
    "run_id",
    "attempt",
    "repetition",
    "seed",
    "terminal_status",
    "run_status",
    "failure_category",
    "provider",
    "retry_count",
    "timeout_seconds",
    "valid_for_aggregate",
    "duration_seconds",
    "outcome_pass",
    "diagnosis_pass",
    "safe_pass",
    "evaluator",
    "case_no",
    "turn_count",
    "tool_call_count",
    "distinct_tool_count",
    "query_metrics_count",
    "execute_sql_count",
    "manage_instance_count",
    "read_log_count",
    "knowledge_call_count",
    "submit_count",
    "llm_call_count",
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "total_tokens",
    "input_token_cost_usd",
    "output_token_cost_usd",
    "total_token_cost_usd",
    "token_accounting_method",
    "tokenizer_match",
    "cost_status",
    "pricing_version",
    "trace_available",
    "trace_sha256",
    "evaluator_sha256",
    "evaluation_json",
)


def load_scenario_attributes(project_root: Path) -> dict[tuple[str, str, str], dict]:
    expected = {"schema_version", "annotation_version", "annotation_status", "cases"}
    case_fields = {
        "scenario_id",
        "case_id",
        "category",
        "difficulty",
        "diagnostic_depth",
        "environmental_complexity",
        "evidence_modality",
        "temporal_requirement",
    }
    index = {}
    for system, relative_path in SCENARIO_ATTRIBUTE_PATHS.items():
        path = project_root / relative_path
        registry = yaml.safe_load(path.read_text(encoding="utf-8"))
        if set(registry) != expected or registry["schema_version"] != 1:
            raise ValueError(
                f"Scenario attribute registry schema mismatch: path={path}, fields={sorted(registry)}"
            )
        for case in registry["cases"]:
            if set(case) != case_fields:
                raise ValueError(
                    f"Scenario attribute fields mismatch: path={path}, case={case}"
                )
            allowed_values = {
                **SCENARIO_ATTRIBUTE_VALUES,
                "category": SCENARIO_CATEGORY_VALUES[system],
            }
            invalid = {
                field: case[field]
                for field, allowed in allowed_values.items()
                if case[field] not in allowed
            }
            if invalid:
                raise ValueError(
                    f"Scenario attribute values are invalid: path={path}, "
                    f"scenario_id={case['scenario_id']!r}, case_id={case['case_id']!r}, "
                    f"invalid={invalid}"
                )
            key = (system, case["scenario_id"], case["case_id"])
            if key in index:
                raise ValueError(f"Duplicate scenario attribute key={key}: path={path}")
            index[key] = {
                **case,
                "_annotation_version": registry["annotation_version"],
                "_annotation_status": registry["annotation_status"],
            }
    return index


def _artifact_json(project_root: Path, artifact: dict[str, str] | None) -> dict | None:
    if artifact is None:
        return None
    path = (project_root / artifact["path"]).resolve()
    path.relative_to(project_root.resolve())
    return json.loads(path.read_text(encoding="utf-8"))


def _trace_metrics(trace: dict | None) -> dict[str, Any]:
    if trace is None:
        return {
            "turn_count": None,
            "tool_call_count": None,
            "distinct_tool_count": None,
            "query_metrics_count": None,
            "execute_sql_count": None,
            "manage_instance_count": None,
            "read_log_count": None,
            "knowledge_call_count": None,
            "submit_count": None,
        }
    turns = trace["turns"]
    actions = [action for turn in turns for action in turn.get("actions", [])]
    names = [action["api"] for action in actions]
    return {
        "turn_count": len(turns),
        "tool_call_count": len(actions),
        "distinct_tool_count": len(set(names)),
        "query_metrics_count": names.count("query_metrics"),
        "execute_sql_count": names.count("execute_sql"),
        "manage_instance_count": names.count("manage_instance"),
        "read_log_count": names.count("read_log"),
        "knowledge_call_count": sum(
            names.count(tool_name)
            for tool_name in ("query_knowledge_base", "search_knowledge")
        ),
        "submit_count": names.count("submit"),
    }


def _pass_metrics(run: dict) -> dict[str, bool | None]:
    if not run["valid_for_aggregate"]:
        return {
            "outcome_pass": None,
            "diagnosis_pass": None,
            "safe_pass": None,
        }
    required = {"outcome_pass", "diagnosis_pass", "safe_pass"}
    missing = {field for field in required if run[field] is None}
    if missing:
        raise ValueError(
            f"Valid run lacks required DP/OP/SP results: run_id={run['run_id']!r}, "
            f"missing={sorted(missing)}"
        )
    return {
        "outcome_pass": run["outcome_pass"],
        "diagnosis_pass": run["diagnosis_pass"],
        "safe_pass": run["safe_pass"],
    }


def _empty_token_metrics(pricing_version: str) -> dict[str, Any]:
    return {
        "llm_call_count": None,
        "input_tokens": None,
        "cached_input_tokens": None,
        "cache_write_input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "input_token_cost_usd": None,
        "output_token_cost_usd": None,
        "total_token_cost_usd": None,
        "token_accounting_method": "trace_unavailable",
        "tokenizer_match": None,
        "cost_status": "trace_unavailable",
        "pricing_version": pricing_version,
    }


def _load_model_groups(project_root: Path) -> dict[str, str]:
    payload = yaml.safe_load((project_root / MODEL_GROUP_PATH).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"Unsupported model groups schema: path={MODEL_GROUP_PATH}")
    return payload["groups"]


def build_run_rows(spec: DatasetSpec, project_root: Path) -> list[dict[str, Any]]:
    lock = load_dataset_lock(spec)
    attributes = load_scenario_attributes(project_root)
    selected_cases = {
        (
            entry["run"]["system"],
            entry["run"]["scenario_id"],
            entry["run"]["case_id"],
        )
        for entry in lock["runs"]
    }
    missing_attributes = selected_cases - set(attributes)
    if missing_attributes:
        raise ValueError(
            f"Dataset cases lack scenario attributes: dataset_id={spec.dataset_id!r}, "
            f"missing_attributes={sorted(missing_attributes)}"
        )
    missing_tags = (
        {(entry["run"]["scenario_id"], entry["run"]["case_id"]) for entry in lock["runs"]}
        - set(CASE_TAGS)
    )
    if missing_tags:
        raise ValueError(
            f"Dataset cases lack citation tags: dataset_id={spec.dataset_id!r}, "
            f"missing_tags={sorted(missing_tags)}"
        )
    token_config = load_token_config(project_root / TOKEN_CONFIG_PATH)
    tokenizers = Tokenizers(token_config, project_root / TOKENIZER_CACHE_PATH)
    model_groups = _load_model_groups(project_root)
    lock_sha = sha256(spec.source_path.with_suffix(".lock.json"))
    rows = []
    for entry in lock["runs"]:
        run = entry["run"]
        baseline_id = entry["baseline_id"]
        if baseline_id not in model_groups:
            raise ValueError(f"Unknown baseline_id={baseline_id!r}: run_id={run['run_id']!r}")
        scenario = attributes[(run["system"], run["scenario_id"], run["case_id"])]
        scenario_fields = {
            key: value for key, value in scenario.items() if not key.startswith("_")
        }
        trace = _artifact_json(project_root, entry["artifacts"]["trace"])
        token_metrics = (
            account_tokens(trace, run["model"], token_config, tokenizers)
            if trace is not None
            else _empty_token_metrics(token_config["pricing_version"])
        )
        row = {
            "dataset_id": spec.dataset_id,
            "dataset_lock_sha256": lock_sha,
            "data_status": spec.data_status,
            "metric_contract": spec.metric_contract,
            "scenario_annotation_version": scenario["_annotation_version"],
            "scenario_annotation_status": scenario["_annotation_status"],
            "database": DATABASE_LABELS[run["system"]],
            "citation_tag": CASE_TAGS[(run["scenario_id"], run["case_id"])],
            **scenario_fields,
            "evidence_modality_count": 1 if scenario["evidence_modality"] == "single" else 2,
            "baseline_id": baseline_id,
            "source_agent_id": run["agent_id"],
            "agent_mode": run["agent_mode"],
            "model": run["model"],
            "model_group": model_groups[baseline_id],
            "experiment_id": entry["experiment_id"],
            "run_id": entry["run_id"],
            "attempt": entry["attempt"],
            "repetition": run["repetition"],
            "seed": run["seed"],
            "terminal_status": run["status"],
            "run_status": run["run_status"],
            "failure_category": run["failure_category"],
            "provider": run["provider"],
            "retry_count": run["retry_count"],
            "timeout_seconds": run["timeout_seconds"],
            "valid_for_aggregate": run["valid_for_aggregate"],
            "duration_seconds": run["duration_seconds"],
            **_pass_metrics(run),
            "evaluator": run["evaluator"],
            "case_no": run["case_no"],
            **_trace_metrics(trace),
            **token_metrics,
            "trace_available": trace is not None,
            "trace_sha256": None
            if entry["artifacts"]["trace"] is None
            else entry["artifacts"]["trace"]["sha256"],
            "evaluator_sha256": None
            if entry["artifacts"]["evaluator"] is None
            else entry["artifacts"]["evaluator"]["sha256"],
            "evaluation_json": json.dumps(run["evaluation"], ensure_ascii=False, sort_keys=True),
        }
        if set(row) != set(RUN_COLUMNS):
            raise ValueError(
                f"Canonical run row schema mismatch: run_id={run['run_id']!r}, "
                f"missing={sorted(set(RUN_COLUMNS) - set(row))}, "
                f"extra={sorted(set(row) - set(RUN_COLUMNS))}"
            )
        rows.append(row)
    return rows


def write_runs_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=RUN_COLUMNS)
        writer.writeheader()
        writer.writerows(
            {
                key: (
                    "true"
                    if value is True
                    else "false"
                    if value is False
                    else ""
                    if value is None
                    else value
                )
                for key, value in row.items()
            }
            for row in rows
        )
