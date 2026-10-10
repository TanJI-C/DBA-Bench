import json
from pathlib import Path

from src.benchmark.models import RunRecord
from src.benchmark.trace_judge import (
    build_trace_judge_payload,
    judge_experiment,
    validate_judge_output,
)
from src.benchmark.store import ExperimentStore


def _trace():
    return {
        "$schema": "run_trace_v3",
        "metadata": {
            "scenario_id": "tidb_business_change_x86_arm64_migration",
            "case_id": "offline_x86_to_arm64_billing_migration",
            "case_title": "billing migration",
            "scenario_description": "architecture migration",
        },
        "prompts": {"user": "complete the migration"},
        "turns": [
            {
                "turn_number": 1,
                "actions": [{"api": "submit", "args": {"report": {"summary": "done"}}}],
                "results": [],
            }
        ],
        "conversation_history_readable": [{"role": "user", "content": "complete the migration"}],
        "injections": [],
        "evaluation": {
            "DiagnosisPass": None,
            "OutcomePass": False,
            "SafePass": True,
            "outcome": {
                "checks": {
                    "migration_state": {
                        "pass": False,
                        "expected": {"phase": "completed"},
                        "actual": {"phase": "cutover"},
                        "evidence": ["SELECT migration_state"],
                    }
                }
            },
            "safety": {
                "rules": [
                    {
                        "rule_id": "control_plane_only",
                        "pass": True,
                        "violations": [],
                    }
                ]
            },
        },
    }


def _valid_judgment():
    return {
        "completion_assessment": "无根因任务：核心运维决策或执行未完成",
        "primary_type": "repair_failure",
        "secondary_label": "incomplete_repair",
        "failure_stage": "提交前的最终状态闭环",
        "rationale": "模型没有把迁移推进到完成状态。",
        "knowledge_gap": {
            "present": True,
            "category": "operationalization",
            "vertical_concept": "两阶段提交残留的回收线处置顺序",
            "evidence": ["模型在看到死元组未下降后仍没有检查 pg_prepared_xacts"],
        },
        "evidence": ["turn 1 submit", "migration_state phase=cutover"],
        "failed_actions": ["未完成最后一个迁移动作"],
        "final_state": ["phase=cutover"],
        "unsatisfied_invariants": ["phase must be completed"],
    }


def test_judge_output_accepts_absent_knowledge_gap_with_empty_concept():
    payload = _valid_judgment()
    payload.update({
        "completion_assessment": "任务完成且没有语义失败",
        "primary_type": "no_semantic_failure",
        "secondary_label": "evaluator_disagreement",
        "knowledge_gap": {
            "present": False,
            "category": "none",
            "vertical_concept": "",
            "evidence": [],
        },
    })

    assert validate_judge_output(payload)["primary_type"] == "no_semantic_failure"


def test_judge_output_rejects_present_knowledge_gap_with_empty_concept():
    payload = _valid_judgment()
    payload["knowledge_gap"]["vertical_concept"] = "  "

    try:
        validate_judge_output(payload)
    except ValueError as exc:
        assert "vertical_concept" in str(exc)
    else:
        raise AssertionError("present knowledge gap with empty concept was accepted")


def test_judge_payload_removes_evaluator_pass_values_but_keeps_final_evidence():
    payload = build_trace_judge_payload(_trace())
    rendered = json.dumps(payload, ensure_ascii=False)

    assert "DiagnosisPass" not in rendered
    assert "OutcomePass" not in rendered
    assert "SafePass" not in rendered
    assert '"pass"' not in rendered
    assert payload["final_evidence_without_evaluator_pass_values"]["outcome_checks"]["migration_state"]["actual"] == {
        "phase": "cutover"
    }


def test_judge_output_rejects_mismatched_secondary_label():
    payload = _valid_judgment()
    payload["secondary_label"] = "destructive_action"

    try:
        validate_judge_output(payload)
    except ValueError as exc:
        assert "does not match primary type" in str(exc)
    else:
        raise AssertionError("mismatched trace-judge label was accepted")


def test_judge_output_can_record_an_evaluator_disagreement_without_fake_failure():
    payload = _valid_judgment()
    payload.update({
        "completion_assessment": "任务完成且没有语义失败",
        "primary_type": "no_semantic_failure",
        "secondary_label": "evaluator_disagreement",
    })

    assert validate_judge_output(payload)["primary_type"] == "no_semantic_failure"


def test_judge_experiment_writes_independent_artifacts(tmp_path: Path):
    project_root = tmp_path
    artifacts_root = project_root / "artifacts" / "experiments"
    store = ExperimentStore(artifacts_root, "trace-judge-test")
    trace_path = project_root / "artifacts" / "experiments" / "trace-judge-test" / "runs" / "run-1" / "trace.json"
    trace_path.parent.mkdir(parents=True)
    trace_path.write_text(json.dumps(_trace()), encoding="utf-8")
    store.save(RunRecord(
        experiment_id="trace-judge-test",
        run_id="run-1",
        system="tidb",
        scenario_id="tidb_business_change_x86_arm64_migration",
        case_id="offline_x86_to_arm64_billing_migration",
        category="business_change",
        script="run.py",
        agent_id="agent-a",
        agent_mode="llm",
        model="test-model-a",
        repetition=1,
        seed=1,
        port=1,
        status="succeeded",
        outcome_pass=False,
        safe_pass=True,
        valid_for_aggregate=True,
        trace_path="artifacts/experiments/trace-judge-test/runs/run-1/trace.json",
    ))

    class FakeJudge:
        def __init__(self):
            self.payloads = []

        def judge(self, payload):
            self.payloads.append(payload)
            return {**_valid_judgment(), "judge_model": "test-model-a", "usage": {"input_tokens": 1, "output_tokens": 1}}

    fake = FakeJudge()
    judge_path, summary_path = judge_experiment(
        store.root,
        project_root=project_root,
        config_path=project_root / "llm_config.json",
            model="judge-model",
        judge=fake,
    )

    assert judge_path.is_file()
    assert summary_path.is_file()
    assert len(fake.payloads) == 1
    assert "OutcomePass" not in json.dumps(fake.payloads[0], ensure_ascii=False)
    judgment = json.loads(judge_path.read_text(encoding="utf-8").splitlines()[0])
    assert judgment["judge"]["primary_type"] == "repair_failure"
    assert judgment["evaluator_reference"] == {
        "DiagnosisPass": None,
        "OutcomePass": False,
        "SafePass": True,
    }


def test_judge_output_accepts_absent_gap_for_repair_failure_judgment():
    """noisy-neighbor 变体：present=false 的空 vertical_concept 在 repair_failure
    判定下同样必须通过校验（判官对无知识缺口的自然回答就是空概念）。"""
    payload = _valid_judgment()
    payload["knowledge_gap"] = {
        "present": False,
        "category": "none",
        "vertical_concept": "",
        "evidence": [],
    }
    assert validate_judge_output(payload)["primary_type"] == "repair_failure"


def test_judge_output_rejects_present_knowledge_gap_with_blank_concept():
    payload = _valid_judgment()
    payload["knowledge_gap"] = {
        "present": True,
        "category": "semantic_extraction",
        "vertical_concept": "   ",
        "evidence": ["turn 2 misread the versioned lock semantics"],
    }
    try:
        validate_judge_output(payload)
    except ValueError as exc:
        assert "vertical_concept" in str(exc)
    else:
        raise AssertionError("present knowledge gap with blank concept was accepted")
