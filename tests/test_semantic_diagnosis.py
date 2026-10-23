import json
from types import SimpleNamespace
from urllib.error import HTTPError

import httpx
import openai
import pytest

from src.scenarios.evaluation.common import condition
from src.scenarios.evaluation.protocol import EvaluationContext
from src.scenarios.evaluation.diagnosis import (
    ExactDiagnosisMatcher,
    SemanticDiagnosisMatcher,
)
from src.scenarios.evaluation.semantic import (
    semantic_judge_from_config,
    SemanticConditionJudgment,
    SemanticJudgment,
    _parse_judgments,
)
from src.protocols.report import StructuredReport
from src.scenarios import ALL_SCENARIOS
from src.scenarios.base import CaseRun
from src.scenarios.evaluation.semantic import (
    probe_semantic_model,
)
from src.scenarios.runtime.orchestrator import OrchestratorRunConfig
from src.scenarios.runtime.orchestrator import Orchestrator
from scripts.start_dp_semantic_model import build_vllm_command, parser as model_parser


EXPECTED = (
    condition(
        "stale_stats",
        "stale branch order statistics",
        "many modifications since analyze",
        critical=True,
    ),
    condition(
        "analyze_fix",
        "refresh optimizer statistics",
        "analyze branch order line",
        critical=True,
    ),
)


def report(*factors):
    return StructuredReport.from_mapping({
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": factor,
                    "entity": "branch_order",
                    "evidence": [f"observed: {factor}"],
                }
                for factor in factors
            ]
        },
        "outcome": {"changes": [], "verification": []},
        "summary": "diagnosis",
    })


class FakeJudge:
    model = "fake-qwen3-4b"

    def __init__(self, judgment):
        self.judgment = judgment
        self.calls = []

    def judge(self, expected, submitted):
        self.calls.append((expected, submitted))
        return self.judgment


def judgment(*conditions):
    return SemanticJudgment(
        model="fake-qwen3-4b",
        conditions=tuple(conditions),
        usage={"input_tokens": 100, "output_tokens": 20},
    )


def test_semantic_matcher_accepts_paraphrased_root_cause():
    judge = FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (0,), (), "Old statistics explain the estimate error."),
        SemanticConditionJudgment("analyze_fix", (1,), (), "The report recommends ANALYZE."),
    ))

    result = SemanticDiagnosisMatcher(judge).match(
        EXPECTED,
        report(
            "大量写入后没有 ANALYZE，优化器仍使用旧统计信息",
            "执行 ANALYZE 刷新优化器统计信息",
        ),
    )

    assert result["DiagnosisPass"] is True
    assert result["matching_mode"] == "semantic"
    assert result["matched_conditions"] == ["stale_stats", "analyze_fix"]
    assert result["judge_model"] == "fake-qwen3-4b"
    assert result["judge_usage"] == {"input_tokens": 100, "output_tokens": 20}
    assert len(judge.calls) == 1


def test_semantic_matcher_fails_missing_critical_condition():
    result = SemanticDiagnosisMatcher(FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (0,), (), "The old statistics are identified."),
        SemanticConditionJudgment("analyze_fix", (), (), "No repair recommendation was submitted."),
    ))).match(EXPECTED, report("统计信息长期未更新"))

    assert result["DiagnosisPass"] is False
    assert result["missing_conditions"] == ["analyze_fix"]
    assert result["critical_missing"] == ["analyze_fix"]


def test_semantic_matcher_fails_contradictory_condition():
    result = SemanticDiagnosisMatcher(FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (0,), (0,), "The claim both asserts and denies the condition."),
        SemanticConditionJudgment("analyze_fix", (1,), (), "The report recommends ANALYZE."),
    ))).match(EXPECTED, report("统计信息是最新的，不存在陈旧统计", "执行 ANALYZE"))

    assert result["DiagnosisPass"] is False
    assert result["contradictory_conditions"] == ["stale_stats"]


def test_semantic_matcher_requires_evidence_for_entailed_condition():
    empty_evidence_report = StructuredReport.from_mapping({
        "diagnosis": {
            "conditions": [
                {
                    "type": "root_cause",
                    "factor": "stale branch order statistics",
                    "entity": "branch_order",
                    "evidence": [],
                },
                {
                    "type": "root_cause",
                    "factor": "refresh optimizer statistics",
                    "entity": "branch_order",
                    "evidence": ["ANALYZE was planned"],
                },
            ]
        },
        "outcome": {"changes": [], "verification": []},
        "summary": "semantic diagnosis",
    })
    result = SemanticDiagnosisMatcher(FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (0,), (), "Old statistics are identified."),
        SemanticConditionJudgment("analyze_fix", (1,), (), "The report recommends ANALYZE."),
    ))).match(EXPECTED, empty_evidence_report)

    assert result["DiagnosisPass"] is False
    assert result["missing_evidence"] == ["stale_stats"]


def test_semantic_matcher_rejects_incomplete_judge_output():
    judge = FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (0,), (), "Only one condition was judged."),
    ))

    with pytest.raises(ValueError, match="every expected condition exactly once"):
        SemanticDiagnosisMatcher(judge).match(EXPECTED, report("旧统计信息"))


def test_semantic_matcher_rejects_invalid_submitted_index():
    judge = FakeJudge(judgment(
        SemanticConditionJudgment("stale_stats", (7,), (), "Invalid reference."),
        SemanticConditionJudgment("analyze_fix", (), (), "Missing."),
    ))

    with pytest.raises(ValueError, match="invalid submitted condition indexes"):
        SemanticDiagnosisMatcher(judge).match(EXPECTED, report("旧统计信息"))


def test_explicit_exact_matcher_does_not_infer_a_paraphrase():
    result = ExactDiagnosisMatcher().match(EXPECTED, report("大量写入后没有 ANALYZE，优化器仍使用旧统计信息"))

    assert result["matching_mode"] == "exact"
    assert result["DiagnosisPass"] is False


def test_exact_matcher_accepts_normalized_alias_inside_explanatory_prose():
    result = ExactDiagnosisMatcher().match(
        EXPECTED,
        report(
            "The estimate error came from stale-branch_order statistics after bulk writes",
            "We will analyze branch-order-line before checking the new plan",
        ),
    )

    assert result["DiagnosisPass"] is True


def test_exact_matcher_does_not_expand_a_single_word_alias_into_a_fragment_match():
    expected = (condition("missing_index", "index", critical=True),)

    result = ExactDiagnosisMatcher().match(
        expected,
        report("the report mentions an index scan but does not identify the root cause"),
    )

    assert result["DiagnosisPass"] is False


def test_exact_matcher_still_requires_evidence_after_phrase_matching():
    submitted = StructuredReport.from_mapping({
        "diagnosis": {"conditions": [{
            "type": "root_cause",
            "factor": "The root cause is stale branch order statistics after bulk writes",
            "entity": "branch_order",
            "evidence": [],
        }, {
            "type": "remediation",
            "factor": "We should analyze branch order line now",
            "entity": "branch_order",
            "evidence": ["ANALYZE was planned"],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "diagnosis",
    })

    result = ExactDiagnosisMatcher().match(EXPECTED, submitted)

    assert result["DiagnosisPass"] is False
    assert result["missing_evidence"] == ["stale_stats"]


def test_exact_matcher_can_match_deterministic_aliases_inside_evidence():
    submitted = StructuredReport.from_mapping({
        "diagnosis": {"conditions": [{
            "type": "observed_condition",
            "factor": "optimizer estimates remained inaccurate",
            "entity": "branch_order",
            "evidence": ["many modifications since analyze were observed"],
        }, {
            "type": "planned_action",
            "factor": "correct the optimizer metadata",
            "entity": "branch_order",
            "evidence": ["the operator will refresh optimizer statistics"],
        }]},
        "outcome": {"changes": [], "verification": []},
        "summary": "diagnosis",
    })

    result = ExactDiagnosisMatcher().match(EXPECTED, submitted)

    assert result["DiagnosisPass"] is True
    assert result["matched_condition_indexes"] == {
        "stale_stats": [0],
        "analyze_fix": [1],
    }


def test_semantic_judge_output_parser_rejects_unknown_shape():
    with pytest.raises(ValueError, match="exactly the judgments field"):
        _parse_judgments({"matches": []})


@pytest.fixture
def semantic_gateway(monkeypatch):
    """Exercise the real SDK and JSON wire format without a hosted model."""
    gateway = SimpleNamespace(
        requests=[],
        catalog_status=200,
        chat_status=200,
        payload={
            "id": "semantic-test",
            "object": "chat.completion",
            "created": 0,
            "model": "test-judge",
            "choices": [{
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps({
                    "judgments": [{
                        "condition_id": "stale_stats",
                        "entailed_by": [0],
                        "contradicted_by": [],
                        "reason": "same meaning",
                    }],
                })},
            }],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        },
    )

    def handle(request):
        gateway.requests.append(request)
        if request.url.path == "/v1/models":
            return httpx.Response(gateway.catalog_status, json={"data": []})
        assert request.method == "POST"
        assert request.url.path == "/v1/chat/completions"
        if gateway.chat_status != 200:
            return httpx.Response(gateway.chat_status, json={"error": {
                "message": "configured judge rejected", "type": "test_error",
            }})
        return httpx.Response(200, json=gateway.payload)

    real_openai = openai.OpenAI
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(
            openai, "OpenAI",
            lambda **kwargs: real_openai(**kwargs, http_client=client),
        )
        yield gateway


def configured_judge(tmp_path, options):
    path = tmp_path / "llm.json"
    config = {
        "url": "http://gateway.test/v1/chat/completions",
        "api_key": "test-key",
    }
    if options is not None:
        config["semantic_judge"] = options
    path.write_text(json.dumps({"test-judge": config}))
    return semantic_judge_from_config(str(path), "test-judge")


@pytest.mark.parametrize("catalog_status", [200, 403, 404])
@pytest.mark.parametrize("options", [
    None,
    {},
    {"max_tokens": 8192, "response_format": None},
    {"max_tokens": 16384, "response_format": {"type": "json_object"}},
])
def test_semantic_judge_calls_chat_directly_with_configured_options(
    semantic_gateway, tmp_path, catalog_status, options,
):
    semantic_gateway.catalog_status = catalog_status
    judge = configured_judge(tmp_path, options)

    result = SemanticDiagnosisMatcher(judge).match(
        (EXPECTED[0],), report("统计信息长期未更新"),
    )

    assert result["DiagnosisPass"] is True
    assert result["judge_usage"] == {"input_tokens": 11, "output_tokens": 7}
    assert len(semantic_gateway.requests) == 1
    request = semantic_gateway.requests[0]
    assert request.headers["authorization"] == "Bearer test-key"
    payload = json.loads(request.content)
    options = options or {}
    assert payload["model"] == "test-judge"
    assert payload["max_tokens"] == options.get("max_tokens", 2048)
    if options.get("response_format") is None:
        assert "response_format" not in payload
    else:
        assert payload["response_format"] == options["response_format"]
    assert payload["temperature"] == 0
    assert payload["messages"][0]["role"] == "system"


@pytest.mark.parametrize("content", [None, "", '{"judgments":', '{"judgments": []}'])
def test_semantic_judge_rejects_token_exhaustion(semantic_gateway, tmp_path, content):
    choice = semantic_gateway.payload["choices"][0]
    choice["finish_reason"] = "length"
    choice["message"]["content"] = content
    judge = configured_judge(tmp_path, {"max_tokens": 32768})

    with pytest.raises(ValueError, match="exhausted its output-token budget") as exc_info:
        judge.judge((EXPECTED[0],), report("旧统计信息").diagnosis.conditions)

    assert "model='test-judge'" in str(exc_info.value)
    assert "max_tokens=32768" in str(exc_info.value)
    assert "finish_reason='length'" in str(exc_info.value)
    assert len(semantic_gateway.requests) == 1


@pytest.mark.parametrize("content, error, message", [
    ("", ValueError, "empty content"),
    ("not JSON", json.JSONDecodeError, "Expecting value"),
    ('{"matches": []}', ValueError, "exactly the judgments field"),
])
def test_semantic_judge_rejects_invalid_content(
    semantic_gateway, tmp_path, content, error, message,
):
    semantic_gateway.payload["choices"][0]["message"]["content"] = content
    judge = configured_judge(tmp_path, {})

    with pytest.raises(error, match=message):
        judge.judge((EXPECTED[0],), report("旧统计信息").diagnosis.conditions)


@pytest.mark.parametrize("status, error", [
    (401, openai.AuthenticationError),
    (404, openai.NotFoundError),
    (503, openai.InternalServerError),
])
def test_semantic_judge_propagates_chat_errors(semantic_gateway, tmp_path, status, error):
    semantic_gateway.chat_status = status
    judge = configured_judge(tmp_path, {"max_retries": 0})

    with pytest.raises(error, match="configured judge rejected"):
        SemanticDiagnosisMatcher(judge).match((EXPECTED[0],), report("旧统计信息"))

    assert len(semantic_gateway.requests) == 1


def test_local_model_catalog_forbidden_does_not_report_ready(monkeypatch):
    def catalog_request(*_args, **_kwargs):
        raise HTTPError("https://provider.example/v1/models", 403, "Forbidden", {}, None)

    monkeypatch.setattr("src.scenarios.evaluation.semantic.urlopen", catalog_request)

    probe = probe_semantic_model(
        "https://provider.example/v1",
        "test-model-a",
        "configured-key",
    )

    assert probe.status == "unavailable"
    assert probe.ready is False
    assert "HTTP 403" in probe.detail


def test_model_start_script_builds_vllm_command():
    args = model_parser().parse_args([
        "--model", "Qwen/Qwen3-4B-Instruct-2507",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--tensor-parallel-size", "2",
        "--quantization", "awq",
    ])

    assert build_vllm_command(args) == [
        "vllm", "serve", "Qwen/Qwen3-4B-Instruct-2507",
        "--served-model-name", "Qwen/Qwen3-4B-Instruct-2507",
        "--host", "127.0.0.1", "--port", "8000",
        "--api-key", "local", "--dtype", "half",
        "--gpu-memory-utilization", "0.9", "--max-model-len", "4096",
        "--tensor-parallel-size", "2", "--quantization", "awq",
    ]


def test_run_config_validates_and_builds_exact_mode():
    config = OrchestratorRunConfig(diagnosis_match_mode="exact")
    assert config.build_diagnosis_matcher().mode == "exact"


def test_run_config_rejects_unknown_diagnosis_mode():
    with pytest.raises(ValueError, match="diagnosis match mode"):
        OrchestratorRunConfig(diagnosis_match_mode="embedding")


def test_run_config_can_select_semantic_mode_from_environment(monkeypatch):
    monkeypatch.setenv("AIOPS_DP_MATCH_MODE", "semantic")
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_MODEL", "local-qwen3-4b")
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_CONFIG", "/tmp/dp-llm.json")

    config = OrchestratorRunConfig()

    assert config.diagnosis_match_mode == "semantic"
    assert config.diagnosis_semantic_model == "local-qwen3-4b"
    assert config.diagnosis_semantic_config_path == "/tmp/dp-llm.json"


def test_orchestrator_injects_semantic_matcher(monkeypatch):
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "pg_query_perf_missing_index")
    case = scenario.cases[0]
    fake_judge = FakeJudge(SemanticJudgment(model="fake", conditions=(), usage={}))
    monkeypatch.setattr(
        "src.scenarios.evaluation.config.semantic_judge_from_config",
        lambda path, model: fake_judge,
    )

    orchestrator = Orchestrator(
        env=object(),
        scenario=scenario,
        case=case,
        agent=None,
        run_config=OrchestratorRunConfig(diagnosis_match_mode="semantic"),
    )

    assert orchestrator.evaluator.diagnosis_matcher.mode == "semantic"
    assert orchestrator.evaluator.diagnosis_matcher.judge is fake_judge


@pytest.mark.parametrize("scenario,case", [
    (scenario, case) for scenario in ALL_SCENARIOS for case in scenario.cases
    if not case.evaluator.diagnosis_applicable
], ids=lambda item: item.scenario_id if hasattr(item, "scenario_id") else item.case_id)
@pytest.mark.parametrize("entrypoint", ["evaluator", "orchestrator"])
@pytest.mark.parametrize("config_exists", [False, True], ids=["missing-config", "no-judge-model"])
def test_not_applicable_diagnosis_needs_no_judge_config(
    monkeypatch, tmp_path, scenario, case, entrypoint, config_exists,
):
    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    monkeypatch.delenv("AIOPS_DP_SEMANTIC_MODEL", raising=False)
    config_path = tmp_path / "llm_config.json"
    if config_exists:
        config_path.write_text("{}")
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_CONFIG", str(config_path))

    def unexpected_judge_init(path, model):
        pytest.fail(f"N/A diagnosis must not initialize judge: {path=}, {model=}")

    monkeypatch.setattr(
        "src.scenarios.evaluation.config.semantic_judge_from_config",
        unexpected_judge_init,
    )
    if entrypoint == "orchestrator":
        orchestrator = Orchestrator(object(), scenario, case, agent=None)
        evaluator = orchestrator.evaluator
        case_run = orchestrator.case_run
    else:
        evaluator = case.evaluator(object())
        case_run = CaseRun(run_id="not-applicable", scenario=scenario, case=case, env=object())

    result = evaluator.DiagnosisPassFunc(EvaluationContext(case_run, report()))

    assert result["DiagnosisPass"] is None
    assert result["diagnosis_applicable"] is False
    assert result["matching_mode"] == "semantic"
    assert "judge_model" not in result
    assert "judge_usage" not in result


def test_missing_index_specialized_matcher_honors_semantic_mode():
    scenario = next(
        item for item in ALL_SCENARIOS if item.scenario_id == "pg_query_perf_missing_index"
    )
    case = scenario.cases[0]

    class RecordingMatcher:
        mode = "semantic"

        def __init__(self):
            self.expected = None

        def match(self, expected, submitted_report, applicable=True):
            self.expected = expected
            return {"DiagnosisPass": True, "matching_mode": self.mode}

    matcher = RecordingMatcher()
    evaluator = case.evaluator(object(), diagnosis_matcher=matcher)
    submitted_report = report("同义的缺索引根因解释")
    case_run = CaseRun(
        run_id="semantic-missing-index",
        scenario=scenario,
        case=case,
        env=object(),
    )

    result = evaluator.DiagnosisPassFunc(EvaluationContext(case_run, submitted_report))

    assert result == {"DiagnosisPass": True, "matching_mode": "semantic"}
    assert matcher.expected is case.evaluator.diagnosis_conditions


def test_semantic_judge_config_requires_declared_model(tmp_path):
    path = tmp_path / "llm.json"
    path.write_text(json.dumps({"other": {"url": "http://localhost:8000/v1", "api_key": "local"}}))

    with pytest.raises(KeyError, match="Qwen3-4B"):
        semantic_judge_from_config(str(path), "Qwen3-4B")


def test_semantic_is_the_default_for_run_config_and_cli(monkeypatch):
    import argparse
    from src.cli import parser as cli_parser
    from src.scenarios.evaluation.config import add_diagnosis_arguments
    from src.scenarios.evaluation.semantic import DEFAULT_SEMANTIC_MODEL

    for key in ("AIOPS_DP_MATCH_MODE", "AIOPS_DP_SEMANTIC_MODEL", "AIOPS_DP_SEMANTIC_CONFIG"):
        monkeypatch.delenv(key, raising=False)
    config = OrchestratorRunConfig()
    parser = argparse.ArgumentParser()
    add_diagnosis_arguments(parser)
    args = parser.parse_args([])
    persistent_args = cli_parser().parse_args(["persistent-scenario", "run", "episode.yaml"])

    assert config.diagnosis_match_mode == args.diagnosis_match_mode == persistent_args.diagnosis_match_mode == "semantic"
    assert config.diagnosis_semantic_model == args.diagnosis_semantic_model == DEFAULT_SEMANTIC_MODEL


@pytest.mark.parametrize("model,url", [
    ("Qwen/Qwen3-4B-Instruct-2507", "http://127.0.0.1:8000/v1"),
    ("external-large-judge", "https://gateway.test/v1/chat/completions"),
])
def test_default_evaluator_requests_selected_local_or_external_judge(
    monkeypatch, tmp_path, semantic_gateway, model, url,
):
    from src.scenarios.evaluation.base import BaseEvaluator

    class Evaluator(BaseEvaluator):
        diagnosis_conditions = (EXPECTED[0],)

    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_MODEL", model)
    path = tmp_path / "llm_config.json"
    path.write_text(json.dumps({model: {
        "url": url, "api_key": "test-secret", "provider": "openai",
    }}))
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_CONFIG", str(path))
    evaluator = Evaluator(object())
    context = SimpleNamespace(report=report("数据分布发生变化，但优化器依然根据过时的采样选计划"))

    result = evaluator.DiagnosisPassFunc(context)

    assert result["DiagnosisPass"] is True
    assert result["matching_mode"] == "semantic"
    assert result["judge_model"] == model
    request, = semantic_gateway.requests
    assert str(request.url) == url.removesuffix("/chat/completions").rstrip("/") + "/chat/completions"
    assert request.headers["authorization"] == "Bearer test-secret"
    assert json.loads(request.content)["model"] == model
    assert result["judge_usage"] == {"input_tokens": 11, "output_tokens": 7}
    assert "test-secret" not in json.dumps(result)


@pytest.mark.parametrize("entrypoint", ["config", "evaluator", "orchestrator"])
def test_default_semantic_never_falls_back_when_config_is_missing(monkeypatch, tmp_path, entrypoint):
    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_CONFIG", str(tmp_path / "missing.json"))
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "pg_query_perf_missing_index")
    case = scenario.cases[0]
    with pytest.raises(FileNotFoundError, match="missing.json"):
        if entrypoint == "config":
            OrchestratorRunConfig().build_diagnosis_matcher()
        elif entrypoint == "evaluator":
            case.evaluator(object())
        else:
            Orchestrator(object(), scenario, case, agent=None)


def test_judge_cli_selection_is_independent_of_agent_model(monkeypatch):
    import argparse
    from src.scenarios.evaluation.config import add_diagnosis_arguments

    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_MODEL", "local-judge")
    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    add_diagnosis_arguments(parser)
    args = parser.parse_args(["--model", "agent-model"])
    assert args.diagnosis_semantic_model == "local-judge"
    args = parser.parse_args(["--model", "agent-model", "--diagnosis-semantic-model", "external-judge"])
    assert args.diagnosis_match_mode == "semantic"
    assert args.diagnosis_semantic_model == "external-judge"


@pytest.mark.parametrize("contradicted,entailed,passed", [([], [0], True), ([0], [0], False), ([], [], False)])
def test_persistent_contract_uses_default_semantic_judge(
    monkeypatch, contradicted, entailed, passed,
):
    from src.persistent_scenarios.evaluation.diagnosis import evaluate_diagnosis_contract
    from src.persistent_scenarios.model.spec import DiagnosisContract, DiagnosisIncidentSpec, ExpectedDiagnosisConditionSpec

    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    contract = DiagnosisContract(incidents=(DiagnosisIncidentSpec(
        incident_id="incident-1", statement="checkout latency", conditions=(ExpectedDiagnosisConditionSpec(
            condition_id="stale_stats", aliases=("stale statistics after bulk writes",),
        ),),
    ),))
    judge = FakeJudge(SemanticJudgment(model="external-judge", conditions=(SemanticConditionJudgment(
        condition_id="stale_stats", entailed_by=tuple(entailed), contradicted_by=tuple(contradicted), reason="meaning checked",
    ),), usage={"input_tokens": 9, "output_tokens": 4}))

    actual, results = evaluate_diagnosis_contract(contract, ("Planner still estimates the old distribution.",), judge=judge)

    assert actual is passed
    assert results[0]["matching_mode"] == "semantic"
    assert results[0]["judge_model"] == "external-judge"
    assert results[0]["report_text_count"] == 1


def test_persistent_semantic_rejects_invalid_judge_indexes(monkeypatch):
    from src.persistent_scenarios.evaluation.diagnosis import evaluate_diagnosis_contract
    from tests.persistent_scenarios._evaluation_factories import diagnosis_contract, incident, condition as expected_condition

    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    contract = diagnosis_contract(incidents=[incident(conditions=[expected_condition("c1", aliases=("stale statistics",))])])
    judge = FakeJudge(SemanticJudgment(model="judge", conditions=(SemanticConditionJudgment(
        condition_id="c1", entailed_by=(2,), contradicted_by=(), reason="invalid index",
    ),), usage={}))
    with pytest.raises(ValueError, match="invalid submitted condition indexes"):
        evaluate_diagnosis_contract(contract, ("one report",), judge=judge)


def test_persistent_empty_contract_needs_no_judge(monkeypatch):
    from src.persistent_scenarios.evaluation.diagnosis import evaluate_diagnosis_contract
    from src.persistent_scenarios.model.spec import DiagnosisContract

    monkeypatch.delenv("AIOPS_DP_MATCH_MODE", raising=False)
    monkeypatch.setenv("AIOPS_DP_SEMANTIC_CONFIG", "/missing.json")
    assert evaluate_diagnosis_contract(DiagnosisContract(), ()) == (None, [])


@pytest.mark.parametrize("stop_reason,text,error", [
    ("end_turn", None, None),
    ("max_tokens", None, "output-token budget"),
    ("end_turn", "", "empty content"),
    ("end_turn", "not JSON", "Expecting value"),
])
def test_external_anthropic_judge_uses_native_api(
    monkeypatch, tmp_path, stop_reason, text, error,
):
    import anthropic

    requests = []
    judgment = json.dumps({"judgments": [{
        "condition_id": "stale_stats", "entailed_by": [0],
        "contradicted_by": [], "reason": "same causal explanation",
    }]})
    def handle(request):
        requests.append(request)
        assert request.url.path == "/v1/messages"
        assert request.headers["x-api-key"] == "test-key"
        return httpx.Response(200, json={
            "id": "msg-judge", "type": "message", "role": "assistant", "model": "external-claude",
            "content": [{"type": "text", "text": judgment if text is None else text}],
            "stop_reason": stop_reason, "stop_sequence": None,
            "usage": {"input_tokens": 12, "output_tokens": 8},
        })
    path = tmp_path / "llm_config.json"
    path.write_text(json.dumps({"external-claude": {
        "provider": "anthropic", "url": "https://gateway.test/v1/messages", "api_key": "test-key",
        "semantic_judge": {"max_tokens": 4096, "max_retries": 0},
    }}))
    real_client = anthropic.Anthropic
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(anthropic, "Anthropic", lambda **kwargs: real_client(**kwargs, http_client=client))
        judge = semantic_judge_from_config(str(path), "external-claude")
        if error:
            with pytest.raises(ValueError, match=error):
                SemanticDiagnosisMatcher(judge).match((EXPECTED[0],), report("过时的统计信息误导了执行计划"))
        else:
            result = SemanticDiagnosisMatcher(judge).match((EXPECTED[0],), report("过时的统计信息误导了执行计划"))
            assert result["DiagnosisPass"] is True
            assert result["judge_usage"] == {"input_tokens": 12, "output_tokens": 8}
    request, = requests
    payload = json.loads(request.content)
    assert payload["model"] == "external-claude"
    assert payload["max_tokens"] == 4096
    assert "expected_conditions" in payload["messages"][0]["content"]


def test_unknown_judge_provider_fails_with_model_context(tmp_path):
    path = tmp_path / "llm_config.json"
    path.write_text(json.dumps({"judge": {"provider": "unknown"}}))
    with pytest.raises(ValueError, match="model='judge', provider='unknown'"):
        semantic_judge_from_config(str(path), "judge")


@pytest.mark.parametrize("scenario,case", [
    (scenario, case) for scenario in ALL_SCENARIOS for case in scenario.cases
], ids=[
    f"{scenario.scenario_id}/{case.case_id}" for scenario in ALL_SCENARIOS for case in scenario.cases
])
def test_every_case_routes_semantic_diagnosis_to_the_selected_judge(scenario, case):
    class ReachedSemanticJudge(Exception):
        pass

    class Matcher:
        mode = "semantic"

        def match(self, expected, submitted_report, applicable=True):
            assert isinstance(expected, tuple)
            raise ReachedSemanticJudge

    evaluator = case.evaluator(object(), diagnosis_matcher=Matcher())
    case_run = CaseRun(run_id="semantic-routing", scenario=scenario, case=case, env=object())
    context = EvaluationContext(case_run, report("用不同措辞解释同一根因"))
    with pytest.raises(ReachedSemanticJudge):
        evaluator.DiagnosisPassFunc(context)
