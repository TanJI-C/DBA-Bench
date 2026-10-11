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


def _postgres_agent_text():
    from src.agents.prompt_manager import PromptManager
    from src.execution.environment import PGEnv
    from src.scenarios import POSTGRES_SCENARIO_REGISTRY

    env = PGEnv(deployment=object())
    schemas = env.get_tool_schemas()
    instructions = env.build_tool_instructions(use_native_tools=True)
    prompts = PromptManager()
    registrations = (
        POSTGRES_SCENARIO_REGISTRY.values()
        if hasattr(POSTGRES_SCENARIO_REGISTRY, "values") else POSTGRES_SCENARIO_REGISTRY
    )
    return {
        "schemas": schemas,
        "help": {s["function"]["name"]: env.help(s["function"]["name"]) for s in schemas},
        "instructions": [instructions, env.build_tool_instructions(use_native_tools=False)],
        "prompts": [
            prompts.get_system_prompt("PGEnv", instructions),
            prompts.get_user_prompt("alert"),
            prompts.get_user_prompt(None),
        ],
        "alerts": {
            f"{getattr(r, 'scenario', r).scenario_id}/{case.case_id}": case.agent_alert()
            for r in registrations
            for case in getattr(getattr(r, "scenario", r), "cases", ()) or ()
        },
    }


def test_english_postgresql_agent_text_has_no_chinese(monkeypatch):
    monkeypatch.setenv(AGENT_LANGUAGE_ENV, "en")
    text = json.dumps(_postgres_agent_text(), ensure_ascii=False)
    hits = sorted({match.group(0) for match in CJK.finditer(text)})
    assert not hits, f"Chinese characters remain in English agent text: {''.join(hits)[:200]}"


def test_chinese_postgresql_agent_text_is_still_chinese(monkeypatch):
    monkeypatch.delenv(AGENT_LANGUAGE_ENV, raising=False)
    text = json.dumps(_postgres_agent_text(), ensure_ascii=False)
    assert CJK.search(text)
