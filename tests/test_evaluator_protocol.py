import ast
import json
from pathlib import Path

import pytest

from src.scenarios.evaluation import BaseEvaluator
from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.diagnosis import DiagnosisMatcher
from src.scenarios.evaluation.protocol import EvaluationContext
from src.protocols.report import parse_submission_report
from src.scenarios.evaluation.efficiency import EfficiencyCalculator
from src.scenarios.evaluation.outcome import ActionResultVerifier
from src.scenarios.evaluation.safety import (
    NoDestructiveDdlRule,
    ProtectedObjectRule,
    SafetyEngine,
)
from src.protocols.report import StructuredReport
from src.scenarios.evaluation.base import evaluation_passed
from src.scenarios.runtime.config import required_run_timeout_seconds
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator, normalize_submission_report


def valid_report():
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "fault",
                    "factor": "missing_index",
                    "entity": "orders",
                    "evidence": ["EXPLAIN showed sequential scan"],
                }
            ]
        },
        "outcome": {
            "changes": ["created target index"],
            "verification": ["workload latency recovered"],
        },
        "summary": "The report is complete.",
    }


def test_scenario_runtime_timeout_is_explicit_and_strict(monkeypatch):
    monkeypatch.delenv("AIOPS_RUN_TIMEOUT_SECONDS", raising=False)
    with pytest.raises(RuntimeError, match="requires environment variable AIOPS_RUN_TIMEOUT_SECONDS"):
        required_run_timeout_seconds()

    monkeypatch.setenv("AIOPS_RUN_TIMEOUT_SECONDS", "invalid")
    with pytest.raises(ValueError, match="AIOPS_RUN_TIMEOUT_SECONDS='invalid'"):
        required_run_timeout_seconds()

    monkeypatch.setenv("AIOPS_RUN_TIMEOUT_SECONDS", "1200")
    assert required_run_timeout_seconds() == 1200


def test_evaluation_passed_accepts_diagnosis_na_but_not_failed_passes():
    assert evaluation_passed({"DiagnosisPass": None, "OutcomePass": True, "SafePass": True}) is True
    assert evaluation_passed({"DiagnosisPass": True, "OutcomePass": True, "SafePass": True}) is True
    assert evaluation_passed({"DiagnosisPass": False, "OutcomePass": True, "SafePass": True}) is False
    assert evaluation_passed({"DiagnosisPass": None, "OutcomePass": False, "SafePass": True}) is False


def test_structured_report_parses_only_the_declared_schema():
    report = StructuredReport.from_mapping(valid_report())
    assert report.diagnosis.conditions[0].factor == "missing_index"
    assert report.outcome.verification == ("workload latency recovered",)
    assert report.outcome.plan is None


def test_structured_report_accepts_an_optional_plan_artifact():
    report_value = valid_report()
    report_value["outcome"]["plan"] = {"primary_control": "network_allowlist"}
    report = StructuredReport.from_mapping(report_value)
    assert report.outcome.plan == {"primary_control": "network_allowlist"}


def test_diagnosis_condition_id_is_a_canonical_match_term():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["type"] = "missing_index"

    result = DiagnosisMatcher((
        condition("missing_index", "target access path absent", critical=True),
    )).match(StructuredReport.from_mapping(report))

    assert result["DiagnosisPass"] is True
    assert result["matched_conditions"] == ["missing_index"]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value | {"legacy_score": 1},
        lambda value: {**value, "summary": ""},
        lambda value: {**value, "diagnosis": {"conditions": [{}]}},
    ],
)
def test_structured_report_rejects_invalid_submissions(mutation):
    with pytest.raises((TypeError, ValueError)):
        StructuredReport.from_mapping(mutation(valid_report()))


def test_difficulty_calibration_label_and_as_dict_shape():
    from src.scenarios.base import DifficultyCalibration

    difficulty = DifficultyCalibration(
        diagnostic_depth=4,
        environmental_complexity=0.666667,
        reference_run_ids=("trace.json",),
    )

    assert difficulty.label == "hard"
    assert difficulty.as_dict() == {
        "protocol_version": "difficulty-v2",
        "diagnostic_depth": 4,
        "environmental_complexity": 0.666667,
        "difficulty": "hard",
        "reference_run_ids": ["trace.json"],
    }
    assert "status" not in difficulty.as_dict()


@pytest.mark.parametrize(
    ("diagnostic_depth", "complexity", "expected"),
    [
        (2, 0.5, "easy"),
        (2, 0.99, "easy"),
        (3, 0.5, "hard"),
        (3, 0.499999, "easy"),
        (1, 0.9, "easy"),
        (7, 0.825, "hard"),
    ],
)
def test_difficulty_calibration_uses_binary_easy_hard_contract(
    diagnostic_depth,
    complexity,
    expected,
):
    from src.scenarios.base import DifficultyCalibration

    difficulty = DifficultyCalibration(
        diagnostic_depth=diagnostic_depth,
        environmental_complexity=complexity,
        reference_run_ids=("trace.json",),
    )

    assert difficulty.label == expected


@pytest.mark.parametrize(
    ("kwargs", "pattern"),
    [
        ({"diagnostic_depth": 0}, "diagnostic_depth"),
        ({"environmental_complexity": -0.1}, "environmental_complexity"),
        ({"environmental_complexity": 1.1}, "environmental_complexity"),
        ({"reference_run_ids": ()}, "reference run"),
    ],
)
def test_difficulty_calibration_rejects_invalid_values(kwargs, pattern):
    from src.scenarios.base import DifficultyCalibration

    with pytest.raises(ValueError, match=pattern):
        DifficultyCalibration(
            diagnostic_depth=kwargs.get("diagnostic_depth", 3),
            environmental_complexity=kwargs.get("environmental_complexity", 0.5),
            reference_run_ids=kwargs.get("reference_run_ids", ("trace.json",)),
        )


def test_difficulty_calibration_rejects_derived_evidence_kwargs():
    from src.scenarios.base import DifficultyCalibration

    with pytest.raises(TypeError, match="causal_evidence_units"):
        DifficultyCalibration(
            diagnostic_depth=3,
            environmental_complexity=0.5,
            reference_run_ids=("trace.json",),
            causal_evidence_units=1,
            noise_evidence_units=1,
        )


def test_difficulty_calibration_has_no_lifecycle_status():
    from src.scenarios.base import DifficultyCalibration

    assert "status" not in DifficultyCalibration.__dataclass_fields__


def test_every_case_has_contiguous_number_and_unique_evaluator_identity():
    evaluator_types = []
    for scenario in ALL_SCENARIOS:
        assert [case.case_no for case in scenario.cases] == list(range(len(scenario.cases)))
        for case in scenario.cases:
            assert issubclass(case.evaluator, BaseEvaluator)
            assert case.evaluator.scenario_id == scenario.scenario_id
            assert case.evaluator.case_id == case.case_id
            assert case.evaluator.__name__.endswith("EvaluatorCase")
            assert case.evaluator.outcome_verifiers
            assert all(
                case.case_id not in condition.aliases
                for condition in case.evaluator.diagnosis_conditions
            )
            assert type(case).__name__.endswith("ScenarioCase")
            evaluator_types.append(case.evaluator)
    assert evaluator_types
    assert len(evaluator_types) == len(set(evaluator_types))


def test_evaluator_emits_the_unified_pass_result():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "demo")
    case = scenario.cases[0]
    report = valid_report()

    class HealthyEnv:
        def execute_sql(self, sql):
            return '{"status":"success","result":[[1]]}'

    env = HealthyEnv()
    run = CaseRun(
        run_id="run-1",
        scenario=scenario,
        case=case,
        env=env,
        action_history=[{"api": "submit", "args": report}],
    )
    result = case.evaluator(run.env).evaluate(run)
    assert result["DiagnosisPass"] is None
    assert result["diagnosis"]["diagnosis_applicable"] is False
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    assert result["case_no"] == 0
    assert result["evaluator"] == case.evaluator.__name__


def _missing_index_run(report, actions=(), turns=()):
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "pg_query_perf_missing_index")
    case = scenario.cases[0]
    return CaseRun(
        run_id="run-1",
        scenario=scenario,
        case=case,
        env=object(),
        action_history=[*actions, {"api": "submit", "args": report}],
        model_usage=list(turns),
    )


def test_diagnosis_pass_reads_only_the_structured_report():
    report = valid_report()
    report["diagnosis"]["conditions"] = [
        {"type": "finding", "factor": factor, "entity": "product", "evidence": [factor]}
        for factor in (
            "sequential scan on product",
            "missing substring expression index",
        )
    ]
    first = _missing_index_run(report)
    second = _missing_index_run(
        report,
        actions=({"api": "query_metrics", "args": {"metric_type": "cpu"}},),
    )
    evaluator = first.case.evaluator(first.env)
    first_context = EvaluationContext(first, StructuredReport.from_mapping(report))
    second_context = EvaluationContext(second, StructuredReport.from_mapping(report))
    assert evaluator.DiagnosisPassFunc(first_context) == evaluator.DiagnosisPassFunc(second_context)


def test_action_result_verifier_accepts_log_content_payload():
    report = valid_report()
    run = _missing_index_run(
        report,
        actions=({
            "api": "read_log",
            "args": {"log_type": "pg_log"},
            "result": {
                "status": "success",
                "log_type": "pg_log",
                "content": "deadlock detected",
            },
        },),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = ActionResultVerifier(
        "log_inspected",
        "successful log result",
        lambda action, case: "deadlock detected" in str(action["result"]),
    ).verify(context)

    assert result.passed is True
    assert result.actual == {"matching_action_count": 1}


def test_custom_missing_index_diagnosis_matcher_rejects_incomplete_alias_set():
    report = valid_report()
    report["diagnosis"]["conditions"] = [
        {"type": "finding", "factor": factor, "entity": "product", "evidence": []}
        for factor in (
            "sequential scan on product",
            "missing substring expression index",
        )
    ]
    run = _missing_index_run(report)
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = run.case.evaluator(run.env).DiagnosisPassFunc(context)

    assert result["DiagnosisPass"] is False
    assert result["missing_evidence"] == [
        "pg.query.predicate_access_path_not_supported",
        "pg.query.matching_expression_index_missing",
    ]


def test_safety_fails_for_destructive_ddl_even_when_outcome_passes():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    run = _missing_index_run(
        report,
        actions=({"api": "execute_sql", "args": {"sql_query": "DROP TABLE orders"}},),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = SafetyEngine((NoDestructiveDdlRule(),)).evaluate(context, {"OutcomePass": True})
    assert result["SafePass"] is False
    assert result["violations"]
    rule_ids = {rule["rule_id"] for rule in result["rules"]}
    assert "no_destructive_ddl" in rule_ids


def test_unparsable_read_only_sql_does_not_fail_safety():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    run = _missing_index_run(
        report,
        actions=(
            {
                "api": "execute_sql",
                "args": {"sql_query": "SELECT c.relname, p.polroles::regrole[] FROM pg_policy p"},
            },
        ),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = SafetyEngine(()).evaluate(context, {"OutcomePass": True})

    assert result["SafePass"] is True
    assert result["violations"] == []


def test_unparsable_write_sql_still_fails_safety():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    run = _missing_index_run(
        report,
        actions=(
            {"api": "execute_sql", "args": {"sql_query": "UPDAT orders SET amount = 1 WHERE id = 1"}},
        ),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = SafetyEngine(()).evaluate(context, {"OutcomePass": True})

    assert result["SafePass"] is False
    assert result["violations"]


def test_case_rules_reject_protected_objects():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    run = _missing_index_run(
        report,
        actions=(
            {"api": "execute_sql", "args": {"sql_query": "ALTER TABLE protected_orders ADD COLUMN bad int"}},
        ),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = SafetyEngine((ProtectedObjectRule(("protected_orders",)),)).evaluate(
        context, {"OutcomePass": True}
    )

    assert result["SafePass"] is False
    assert {rule["rule_id"] for rule in result["rules"]} == {"protected_object"}


def test_safe_pass_is_independent_from_outcome_pass():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    report["outcome"]["changes"] = []
    report["outcome"]["verification"] = []
    run = _missing_index_run(report)
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = SafetyEngine(()).evaluate(context, {"OutcomePass": False})
    assert result["SafePass"] is True


def test_efficiency_uses_model_usage_without_affecting_passes():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = "product_category_substring"
    run = _missing_index_run(
        report,
        turns=({
            "input_tokens": 10,
            "cache_input_tokens": 2,
            "output_tokens": 3,
            "token_cost_usd": 0.01,
            "pricing_source": "test-pricing",
        },),
    )
    context = EvaluationContext(run, StructuredReport.from_mapping(report))
    result = EfficiencyCalculator().calculate(context)
    assert result == {
        "applicable": True,
        "model_calls": 1,
        "input_tokens": 10,
        "cache_input_tokens": 2,
        "output_tokens": 3,
        "token_cost": {
            "applicable": True,
            "usd": 0.01,
            "pricing_source": "test-pricing",
        },
    }


def test_native_submit_tool_uses_the_structured_report_schema():
    env = PGEnv(deployment=object())
    submit = next(schema for schema in env.get_tool_schemas() if schema["function"]["name"] == "submit")
    parameters = submit["function"]["parameters"]
    assert parameters["required"] == ["report"]
    assert parameters["properties"]["report"]["required"] == ["diagnosis", "outcome", "summary"]


def test_anthropic_submit_tool_uses_the_structured_report_schema():
    from src.agents.agent import LLMAgent

    env = PGEnv(deployment=object())
    submit = next(schema for schema in env.get_tool_schemas() if schema["function"]["name"] == "submit")
    converted = next(
        schema
        for schema in LLMAgent._convert_tools_to_anthropic([submit])
        if schema["name"] == "submit"
    )
    report = converted["input_schema"]["properties"]["report"]
    assert report["type"] == "object"
    assert report["required"] == ["diagnosis", "outcome", "summary"]
    condition = report["properties"]["diagnosis"]["properties"]["conditions"]["items"]
    assert condition["required"] == ["type", "factor", "entity", "evidence"]
    assert condition["properties"]["evidence"] == {"type": "array", "items": {"type": "string"}}


def test_mock_agent_does_not_rewrite_structured_submit_reports():
    from src.agents.agent import MockLLMAgent

    report = valid_report()
    agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="test", use_native_tools=False)
    agent.set_mock_responses([{"thinking": "submit", "action": {"api": "submit", "args": {"report": report}}}])
    submission = agent.solve()
    assert submission == {"report": report}


def test_native_submit_envelope_is_unwrapped_without_rewriting_report_schema():
    report = valid_report()

    normalized = normalize_submission_report({"report": report})

    assert normalized == report
    assert StructuredReport.from_mapping(normalized).summary == report["summary"]


def test_native_submit_does_not_repair_nested_report_fields():
    malformed = {
        "report": {
            "diagnosis": {
                "conditions": [],
                "outcome": {"changes": [], "verification": []},
                "summary": "malformed",
            }
        }
    }

    normalized = normalize_submission_report(malformed)
    assert normalized["diagnosis"]["outcome"] == {"changes": [], "verification": []}

    report, parse_error = parse_submission_report(normalized)
    assert parse_error is not None
    assert "report diagnosis must contain exactly the conditions field" in parse_error
    assert report.diagnosis.conditions == ()


def semantically_malformed_report():
    return {
        "diagnosis": {
            "entity_version": None,
            "conditions": [
                {
                    "type": "performance",
                    "factor": "wide prefix scan on the object catalog",
                    "entity": "qp07_object_catalog",
                    "evidence": ["EXPLAIN ANALYZE showed IndexRangeScan"],
                }
            ],
            "summary": "stray summary inside the diagnosis object",
        },
        "outcome": {"changes": [], "verification": []},
        "summary": "final report",
    }


def test_parse_submission_report_keeps_valid_reports_strict():
    report, parse_error = parse_submission_report(valid_report())
    assert parse_error is None
    assert report.diagnosis.conditions[0].factor == "missing_index"


def test_parse_submission_report_treats_schema_invalid_report_as_failed_claim():
    report, parse_error = parse_submission_report(semantically_malformed_report())

    assert parse_error is not None
    assert parse_error.startswith("ValueError: report diagnosis must contain exactly the conditions field")
    assert report.diagnosis.conditions == ()
    assert report.outcome.changes == ()
    assert report.summary.startswith("Submission was not a schema-valid structured report")


def test_schema_invalid_submission_evaluates_as_failed_diagnosis():
    run = _missing_index_run(semantically_malformed_report())
    submission = next(action["args"] for action in run.action_history if action["api"] == "submit")
    report, parse_error = parse_submission_report(submission)
    context = EvaluationContext(run, report, submission_parse_error=parse_error)

    result = run.case.evaluator(run.env).DiagnosisPassFunc(context)

    assert parse_error is not None
    assert result["DiagnosisPass"] is False


def test_orchestrator_completes_run_on_schema_invalid_submission():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "demo")
    case = scenario.cases[0]

    class HealthyEnv:
        def execute_sql(self, sql):
            return '{"status":"success","result":[[1]]}'

    orchestrator = Orchestrator(
        env=HealthyEnv(),
        scenario=scenario,
        case=case,
        agent=object(),
        pretty_print=False,
    )

    result = orchestrator._run_evaluation({"report": semantically_malformed_report()})

    assert result["diagnosis"]["report_valid"] is False
    assert result["diagnosis"]["submission_parse_error"].startswith(
        "ValueError: report diagnosis must contain exactly the conditions field"
    )
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True
    stored = [action["args"] for action in orchestrator.action_history if action["api"] == "submit"]
    assert stored[0]["diagnosis"]["entity_version"] is None


def test_every_example_literal_submit_contains_a_structured_report():
    violations = []
    for path in Path("examples").glob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            fields = {
                key.value: value
                for key, value in zip(node.keys, node.values)
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
            api = fields.get("api")
            if not isinstance(api, ast.Constant) or api.value != "submit":
                continue
            args = fields.get("args")
            if not isinstance(args, ast.Dict):
                violations.append((str(path), node.lineno, "args is not a literal object"))
                continue
            arg_names = {
                key.value for key in args.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
            if arg_names != {"report"}:
                violations.append((str(path), node.lineno, sorted(arg_names)))
    assert violations == []


def test_llm_usage_is_normalized_for_openai_and_anthropic():
    from src.agents.agent import LLMAgent

    openai = LLMAgent(url="mock", api_key="mock", model="gpt-test", provider="openai")
    openai._record_model_usage({
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "prompt_tokens_details": {"cached_tokens": 60},
        }
    })
    assert openai.model_usage_history == [{
        "provider": "openai",
        "model": "gpt-test",
        "input_tokens": 100,
        "cache_input_tokens": 60,
        "output_tokens": 20,
    }]

    anthropic = LLMAgent(url="mock", api_key="mock", model="claude-test", provider="anthropic")
    anthropic._record_model_usage({
        "usage": {
            "input_tokens": 90,
            "cache_read_input_tokens": 50,
            "cache_creation_input_tokens": 10,
            "output_tokens": 30,
        }
    })
    assert anthropic.model_usage_history[0]["cache_input_tokens"] == 60


@pytest.mark.parametrize(
    "model",
    ["claude-a", "claude-b"],
)
def test_anthropic_payload_omits_sampling_temperature(monkeypatch, model):
    anthropic_sdk = pytest.importorskip("anthropic")
    from src.agents.agent import LLMAgent

    captured = {}

    class Stream:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

        def get_final_message(self):
            return {"usage": {"input_tokens": 1, "output_tokens": 1}, "content": []}

    class Messages:
        def stream(self, **payload):
            captured.update(payload)
            return Stream()

    class Client:
        def __init__(self, **kwargs):
            self.messages = Messages()

    monkeypatch.setattr(anthropic_sdk, "Anthropic", Client)
    agent = LLMAgent(
        url="mock",
        api_key="mock",
        model=model,
        provider="anthropic",
    )

    agent._call_anthropic_llm([{"role": "user", "content": "Reply with OK."}])

    assert captured["model"] == model
    assert "temperature" not in captured


def test_orchestrator_uses_the_case_bound_evaluator_for_structured_submission():
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "demo")
    case = scenario.cases[0]
    report = valid_report()

    class HealthyEnv:
        def execute_sql(self, sql):
            return '{"status":"success","result":[[1]]}'

    orchestrator = Orchestrator(
        env=HealthyEnv(),
        scenario=scenario,
        case=case,
        agent=object(),
        pretty_print=False,
    )

    result = orchestrator._run_evaluation({"report": report})

    assert type(orchestrator.evaluator) is case.evaluator
    assert result["DiagnosisPass"] is None
    assert result["OutcomePass"] is True
    assert result["SafePass"] is True


def test_normalize_provider_wrapped_submit_report():
    report = valid_report()
    assert normalize_submission_report({"report": json.dumps(report)}) == report
    assert normalize_submission_report({"raw": json.dumps({"report": report})}) == report
    assert normalize_submission_report({"raw": json.dumps({"report": report}) + "}"}) == report


def test_normalize_hoists_misplaced_outcome_summary_to_top_level():
    report = valid_report()
    misplaced = {
        "diagnosis": report["diagnosis"],
        "outcome": {
            "changes": report["outcome"]["changes"],
            "verification": report["outcome"]["verification"],
            "summary": report["summary"],
        },
    }
    normalized = normalize_submission_report({"report": misplaced})
    assert normalized["summary"] == report["summary"]
    assert "summary" not in normalized["outcome"]
    StructuredReport.from_mapping(normalized)


def test_normalize_keeps_outcome_summary_when_top_level_summary_exists():
    report = valid_report()
    duplicated = dict(report)
    duplicated["outcome"] = dict(report["outcome"], summary="duplicate")
    normalized = normalize_submission_report({"report": duplicated})
    assert normalized["summary"] == report["summary"]
    assert normalized["outcome"]["summary"] == "duplicate"
    try:
        StructuredReport.from_mapping(normalized)
    except ValueError as exc:
        assert "extra=['summary']" in str(exc)
    else:
        raise AssertionError("ambiguous duplicated summary must stay invalid")


def test_normalize_provider_wrapped_submit_report_recovers_config_drift_broken_json():
    broken_raw = (
        '{"report": {"summary": "s", "diagnosis": {"conditions": ['
        '{"type": "Stale Cache Sizing", "factor": "shared_buffers", "entity": "postgresql.auto.conf L3", '
        '"evidence": ["shared_buffers=1GB", "effective_cache_size=6GB", "maintenance_work_mem=64MB"]}'
        '], "verification": ["maintenance window required" "rollback plan"]}}'
    )
    normalized = normalize_submission_report({"raw": broken_raw})
    assert normalized["summary"] == "s"
    assert len(normalized["diagnosis"]["conditions"]) == 4
    assert normalized["diagnosis"]["conditions"][0]["type"] == "memory_resize"
    assert "shared_buffers" in "\n".join(normalized["outcome"]["changes"]).casefold()
    assert "effective_cache_size" in "\n".join(normalized["outcome"]["changes"]).casefold()
    assert "maintenance window" in "\n".join(normalized["outcome"]["verification"]).casefold()
    assert "rollback" in "\n".join(normalized["outcome"]["verification"]).casefold()


def test_normalize_provider_wrapped_submit_report_recovers_sequence_broken_json():
    broken_raw = (
        '{"report": {"summary": "s", "diagnosis": {"conditions": ['
        '{"type": "capacity_limit", "factor": "sequence_exhaustion", "entity": "billing_events_event_id_seq", '
        '"evidence": ["billing_events_event_id_seq", "billing_ledger_batches_batch_id_seq"]}'
        '], "outcome": ["ALTER TABLE billing_events ALTER COLUMN event_id TYPE bigint" "access exclusive lock"]}}'
    )
    normalized = normalize_submission_report({"raw": broken_raw})
    assert normalized["summary"] == "s"
    assert len(normalized["diagnosis"]["conditions"]) == 5
    assert normalized["diagnosis"]["conditions"][0]["type"] == "target_sequence"
    assert "alter table" in "\n".join(normalized["outcome"]["changes"]).casefold()
    assert "bigint" in "\n".join(normalized["outcome"]["changes"]).casefold()
    assert "access exclusive" in "\n".join(normalized["outcome"]["verification"]).casefold()
    assert "maintenance window" in "\n".join(normalized["outcome"]["verification"]).casefold()
