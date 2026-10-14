"""The agent-facing language switch: helper, manifest contract and English PostgreSQL text."""
import json
import re

import pytest
import yaml

from src.agent_language import AGENT_LANGUAGE_ENV, agent_language, agent_text
from src.benchmark.manifest import load_manifest

CJK = re.compile(r"[一-鿿　-〿＀-￯]")


def test_default_language_is_chinese(monkeypatch):
    monkeypatch.delenv(AGENT_LANGUAGE_ENV, raising=False)
    assert agent_language() == "zh"
    assert agent_text(zh="中文", en="English") == "中文"


def test_english_language_selects_english(monkeypatch):
    monkeypatch.setenv(AGENT_LANGUAGE_ENV, "en")
    assert agent_text(zh="中文", en="English") == "English"


def test_unknown_language_fails(monkeypatch):
    monkeypatch.setenv(AGENT_LANGUAGE_ENV, "fr")
    with pytest.raises(ValueError, match="AIOPS_AGENT_LANGUAGE must be one of zh, en, got 'fr'"):
        agent_text(zh="中文", en="English")


def _manifest(tmp_path, *, runtime=None, systems=("postgresql",), agent=None, benchmark=None):
    raw = {
        "experiment_id": "language-contract",
        "benchmark": benchmark or {
            "systems": list(systems),
            "categories": ["query_perf"],
            "scenarios": "all",
        },
        "agents": [agent or {"id": "a", "mode": "llm", "model": "m"}],
    }
    if runtime is not None:
        raw["runtime"] = runtime
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(raw))
    return load_manifest(path)


def test_manifest_defaults_to_chinese(tmp_path):
    assert _manifest(tmp_path).runtime.agent_language == "zh"


def test_manifest_accepts_english_for_postgresql(tmp_path):
    manifest = _manifest(tmp_path, runtime={"agent_language": "en"})
    assert manifest.runtime.agent_language == "en"


@pytest.mark.parametrize("kwargs, message", [
    ({"runtime": {"agent_language": "fr"}}, "agent_language must be one of zh, en"),
    ({"runtime": {"agent_language": "en"}, "systems": ("postgresql", "tidb")}, "covers PostgreSQL only"),
    ({"runtime": {"agent_language": "en"}, "agent": {"id": "d", "mode": "dbaiops", "model": "m", "settings": {}}}, "Chinese prompts"),
    ({"runtime": {"agent_language": "en"}, "benchmark": {"scenario_kind": "persistent", "scenarios": ["pg_continuous_ops"]}}, "bounded scenarios only"),
])
def test_manifest_rejects_untranslated_english_runs(tmp_path, kwargs, message):
    with pytest.raises(ValueError, match=message):
        _manifest(tmp_path, **kwargs)


def _tool_text(env):
    schemas = env.get_tool_schemas()
    return {
        "schemas": schemas,
        "help": {s["function"]["name"]: env.help(s["function"]["name"]) for s in schemas},
        "instructions": [
            env.build_tool_instructions(use_native_tools=True),
            env.build_tool_instructions(use_native_tools=False),
        ],
    }


def _frozen_history_env():
    """A PGEnv whose help carries the frozen-history runtime sections, without a database."""
    from types import SimpleNamespace

    from src.execution.environments.postgres import PGEnv
    from src.execution.history.records import HistoricalRecordSource

    env = PGEnv(deployment=object())
    env._history_timeline = SimpleNamespace(
        visible_start_ms=1_700_000_000_000,
        visible_end_ms=1_700_003_600_000,
        base_step_seconds=15,
        overview_step_seconds=60,
    )
    env._history_sql_archive = object()
    env._case = SimpleNamespace(frozen_history=SimpleNamespace(
        max_history_query_seconds=3600,
        record_sources=(HistoricalRecordSource.COMPONENT_LOG, HistoricalRecordSource.OPERATION_EVENT),
        max_history_records_per_response=200,
    ))
    return env


def _postgres_registrations():
    from src.scenarios import POSTGRES_SCENARIO_REGISTRY

    registry = POSTGRES_SCENARIO_REGISTRY
    return registry.values() if hasattr(registry, "values") else registry


def _postgres_agent_text():
    from src.agents.context_compaction import burst_warning_prefix, prompt_tool_result_prefix
    from src.agents.prompt_manager import PromptManager
    from src.execution.backup_rpo import RpoPGEnv, RpoTopology
    from src.execution.environments.sql import SQL_TRUNCATION_HINT, SQL_TRUNCATION_HINT_EN
    from src.execution.environments.postgres import PGEnv
    from src.execution.history.metrics import QUERY_METRICS_TRUNCATION_HINT, QUERY_METRICS_TRUNCATION_HINT_EN
    from src.execution.postgres_replica_fleet import PgReplicaFleetDeployment, PgReplicaFleetEnv
    from src.scenarios.postgres.resource_governance.container_cpu_budget import CpuBudgetPGEnv

    env = PGEnv(deployment=object())
    instructions = env.build_tool_instructions(use_native_tools=True)
    prompts = PromptManager()
    return {
        "envs": {
            "PGEnv": _tool_text(env),
            "frozen_history": _tool_text(_frozen_history_env()),
            "CpuBudgetPGEnv": _tool_text(CpuBudgetPGEnv(deployment=object())),
            "RpoPGEnv": _tool_text(RpoPGEnv(topology=RpoTopology.for_run(run_id="lang", case_id="throughput_gap"))),
            "PgReplicaFleetEnv": _tool_text(
                PgReplicaFleetEnv(deployment=PgReplicaFleetDeployment(identity="lang"))
            ),
        },
        "prompts": [
            prompts.get_system_prompt("PGEnv", instructions),
            prompts.get_user_prompt("alert"),
            prompts.get_user_prompt(None),
        ],
        "notes": [
            burst_warning_prefix(),
            prompt_tool_result_prefix(),
            agent_text(zh=SQL_TRUNCATION_HINT, en=SQL_TRUNCATION_HINT_EN),
            agent_text(zh=QUERY_METRICS_TRUNCATION_HINT, en=QUERY_METRICS_TRUNCATION_HINT_EN),
        ],
        "alerts": {
            f"{getattr(r, 'scenario', r).scenario_id}/{case.case_id}": case.agent_alert()
            for r in _postgres_registrations()
            for case in getattr(getattr(r, "scenario", r), "cases", ()) or ()
        },
    }


def test_english_postgresql_agent_text_has_no_chinese(monkeypatch):
    monkeypatch.setenv(AGENT_LANGUAGE_ENV, "en")
    text = json.dumps(_postgres_agent_text(), ensure_ascii=False)
    hits = sorted({match.group(0) for match in CJK.finditer(text)})
    assert not hits, f"Chinese characters remain in English agent text: {''.join(hits)[:200]}"


def test_frozen_history_help_lists_the_history_surface(monkeypatch):
    monkeypatch.setenv(AGENT_LANGUAGE_ENV, "en")
    help_text = json.loads(_frozen_history_env().help("execute_sql"))
    surfaces = help_text["definition"]["runtime"]["connection_surfaces"]
    assert [surface["name"] for surface in surfaces] == ["primary", "history"]


def test_chinese_postgresql_agent_text_is_unchanged(monkeypatch):
    from src.agents.prompt_manager import PromptManager

    monkeypatch.delenv(AGENT_LANGUAGE_ENV, raising=False)
    prompts = PromptManager()
    assert prompts.get_user_prompt("ALERT") == "当前场景状态：\nALERT\n\n请根据上述场景开始诊断。"
    assert prompts.get_user_prompt(None) == "初始状态：数据库运行正常，现在等待你开始诊断。"
    assert prompts.get_system_prompt("PGEnv", "TOOLS").startswith("你是一个专业的PostgreSQL数据库运维专家。")
    translated = [
        case
        for r in _postgres_registrations()
        for case in getattr(getattr(r, "scenario", r), "cases", ()) or ()
        if case.alert_en is not None
    ]
    assert translated
    assert all(case.agent_alert() == case.alert for case in translated)
