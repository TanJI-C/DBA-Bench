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
    OpenAISemanticDiagnosisJudge,
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
from src.scenarios.runtime import orchestrator as orchestrator_module
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


def test_exact_matcher_remains_default_and_does_not_infer_a_paraphrase():
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
    return OpenAISemanticDiagnosisJudge.from_config(str(path), "test-judge")


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
    scenario = next(item for item in ALL_SCENARIOS if item.scenario_id == "demo")
    case = scenario.cases[0]
    fake_judge = FakeJudge(SemanticJudgment(model="fake", conditions=(), usage={}))
    monkeypatch.setattr(
        orchestrator_module.OpenAISemanticDiagnosisJudge,
        "from_config",
        classmethod(lambda cls, path, model: fake_judge),
    )

    orchestrator = Orchestrator(
        env=object(),
        scenario=scenario,
        case=case,
        agent=None,
        run_config=OrchestratorRunConfig(diagnosis_match_mode="semantic"),
    )

    assert orchestrator.evaluator.diagnosis_matcher.mode == "semantic"


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
        OpenAISemanticDiagnosisJudge.from_config(str(path), "Qwen3-4B")
