import json
import os
import sys
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.prompt_manager import PromptManager
from src.execution.environments import postgres as environment
from src.execution.environments.postgres import PGEnv
from src.scenarios.runtime.orchestrator import Orchestrator
from src.knowledge.pg_knowledge_base import (
    PGKnowledgeBase,
    default_docs_dir,
    default_embed_batch_size,
    default_embed_parallel_process,
    default_embed_target_devices,
    default_persist_dir,
)


def test_pg_prompt_includes_general_knowledge_tool_by_default():
    env = PGEnv(deployment=object())
    prompt = PromptManager().get_system_prompt(
        "PGEnv",
        tool_instructions=env.build_tool_instructions(use_native_tools=False),
    )

    assert "query_knowledge_base" in prompt
    assert "query_hierarchical_knowledge_base" not in prompt
    assert "PostgreSQL 16" in prompt
    assert "kb_type" not in prompt


def test_non_pg_prompt_does_not_include_pg_knowledge_tool():
    prompt = PromptManager().get_system_prompt("DefaultEnv", tool_instructions="无可用工具")

    assert "query_knowledge_base" not in prompt


def test_pg_hierarchical_prompt_includes_hierarchical_knowledge_tool():
    env = PGEnv(deployment=object(), tool_profile="hierarchical_knowledge")
    prompt = PromptManager().get_system_prompt(
        "PGEnv",
        tool_instructions=env.build_tool_instructions(use_native_tools=False),
    )

    assert "query_knowledge_base" in prompt
    assert "query_hierarchical_knowledge_base" not in prompt
    assert "kb_type" in prompt


def test_pg_native_tool_schema_uses_general_tool_by_default():
    schemas = PGEnv(deployment=object()).get_tool_schemas()

    names = {schema["function"]["name"] for schema in schemas}
    assert "query_knowledge_base" in names
    assert "query_hierarchical_knowledge_base" not in names
    knowledge_schema = next(
        schema for schema in schemas
        if schema["function"]["name"] == "query_knowledge_base"
    )
    assert "kb_type" not in knowledge_schema["function"]["parameters"]["properties"]


def test_pg_tool_instructions_explain_structured_submit_shape():
    instructions = PGEnv(deployment=object()).build_tool_instructions(use_native_tools=True)

    assert "report 顶层只能有 diagnosis、outcome、summary" in instructions
    assert "diagnosis 只能有 conditions" in instructions
    assert "outcome 只能有 changes、verification" in instructions


def test_pg_native_tool_schema_uses_hierarchical_tool_when_requested():
    schemas = PGEnv(deployment=object(), tool_profile="hierarchical_knowledge").get_tool_schemas()

    names = {schema["function"]["name"] for schema in schemas}
    assert "query_knowledge_base" in names
    assert "query_hierarchical_knowledge_base" not in names
    knowledge_schema = next(
        schema for schema in schemas
        if schema["function"]["name"] == "query_knowledge_base"
    )
    assert "kb_type" in knowledge_schema["function"]["parameters"]["properties"]


def test_pg_knowledge_mode_defaults_are_separate(monkeypatch):
    for name in (
        "AIOPS_PG_KB_DOCS_DIR",
        "AIOPS_PG_GENERAL_KB_DOCS_DIR",
        "AIOPS_PG_HIERARCHICAL_KB_DOCS_DIR",
        "AIOPS_PG_KB_DIR",
        "AIOPS_PG_GENERAL_KB_DIR",
        "AIOPS_PG_HIERARCHICAL_KB_DIR",
    ):
        monkeypatch.delenv(name, raising=False)

    assert default_docs_dir("general").parts[-2:] == ("pg_src", "pg16-docs-md")
    assert default_docs_dir("hierarchical").parts[-2:] == ("knowledge", "pg")
    assert default_persist_dir("sqlite", "general").name == "pg16_docs"
    assert default_persist_dir("sqlite", "hierarchical").name == "pg16_hierarchical_docs"


def test_pg_knowledge_embed_batch_size_env_is_coerced(monkeypatch):
    monkeypatch.setenv("AIOPS_PG_KB_EMBED_BATCH_SIZE", "0")
    assert default_embed_batch_size() == 1

    monkeypatch.setenv("AIOPS_PG_KB_EMBED_BATCH_SIZE", "256")
    assert default_embed_batch_size() == 128

    monkeypatch.setenv("AIOPS_PG_KB_EMBED_BATCH_SIZE", "3")
    assert default_embed_batch_size() == 3


def test_pg_knowledge_embed_parallel_env(monkeypatch):
    monkeypatch.setenv("AIOPS_PG_KB_EMBED_PARALLEL", "true")
    monkeypatch.setenv("AIOPS_PG_KB_EMBED_TARGET_DEVICES", "cuda:0, cuda:1")

    assert default_embed_parallel_process() is True
    assert default_embed_target_devices() == ["cuda:0", "cuda:1"]

    monkeypatch.setenv("AIOPS_PG_KB_EMBED_PARALLEL", "0")
    assert default_embed_parallel_process() is False


def test_pg_knowledge_missing_index_returns_build_command(tmp_path, monkeypatch):
    monkeypatch.setenv("AIOPS_PG_KB_SQLITE_DIR", str(tmp_path / "missing_sqlite"))
    kb = PGKnowledgeBase(persist_dir=tmp_path / "missing")

    result = kb.query("pg_stat_activity wait events")

    assert result["status"] == "error"
    assert "not built" in result["error"]
    assert "scripts/build_pg_knowledge_base.py" in result["build_command"]
    assert "--backend chroma" in result["build_command"]


def test_pg_knowledge_sqlite_build_and_query(tmp_path):
    source_dir = tmp_path / "docs"
    monitor_doc = source_dir / "partIII_server_administration" / "13_monitoring.md"
    vacuum_doc = source_dir / "partIII_server_administration" / "10_maintenance.md"
    monitor_doc.parent.mkdir(parents=True)
    monitor_doc.write_text(
        "# Monitoring Database Activity\n\n"
        "## Viewing Locks\n\n"
        "Use `pg_stat_activity` with `pg_locks` to identify blocking sessions "
        "and wait events.\n",
        encoding="utf-8",
    )
    vacuum_doc.write_text(
        "# Routine Vacuuming\n\n"
        "Autovacuum removes dead tuples and helps prevent table bloat.\n",
        encoding="utf-8",
    )
    kb = PGKnowledgeBase(persist_dir=tmp_path / "kb", backend="sqlite")

    stats = kb.build(source_dir=source_dir, chunk_size=300, chunk_overlap=40)
    result = kb.query("pg_stat_activity pg_locks blocking sessions", top_k=2)

    assert stats["status"] == "success"
    assert stats["backend"] == "sqlite"
    assert stats["document_count"] == 2
    assert stats["node_count"] >= 2
    assert Path(stats["database_path"]).exists()
    assert result["status"] == "success"
    assert result["count"] >= 1
    assert result["index"]["backend"] == "sqlite"
    assert "pg_stat_activity" in result["results"][0]["content"]


def test_pg_knowledge_sqlite_filters_by_kb_type(tmp_path):
    source_dir = tmp_path / "pg"
    guide_doc = source_dir / "guide" / "lock_contention.md"
    config_doc = source_dir / "configuration" / "lock_timeout.md"
    ignored_doc = source_dir / "mappings" / "pg16_review_summary.md"
    readme_doc = source_dir / "README.md"
    guide_doc.parent.mkdir(parents=True)
    config_doc.parent.mkdir(parents=True)
    ignored_doc.parent.mkdir(parents=True)
    guide_doc.write_text(
        "# Lock Contention Diagnosis\n\n"
        "Use `pg_locks` and `pg_stat_activity` to identify blocking sessions.\n",
        encoding="utf-8",
    )
    config_doc.write_text(
        "# lock_timeout Configuration\n\n"
        "`lock_timeout` controls how long a statement waits for a lock.\n",
        encoding="utf-8",
    )
    ignored_doc.write_text("# Review Summary\n\npg_locks should not be indexed here.\n", encoding="utf-8")
    readme_doc.write_text("# Generated Knowledge Base\n\npg_locks should not be indexed here.\n", encoding="utf-8")
    kb = PGKnowledgeBase(persist_dir=tmp_path / "kb", backend="sqlite")

    stats = kb.build(source_dir=source_dir, chunk_size=300, chunk_overlap=40)
    guide_result = kb.query("pg_locks blocking sessions", kb_type="guide", top_k=5)
    config_result = kb.query("pg_locks blocking sessions", kb_type="configuration", top_k=5)
    invalid_result = kb.query("pg_locks", kb_type="troubleshooting")

    assert stats["document_count"] == 2
    assert guide_result["status"] == "success"
    assert guide_result["kb_type"] == "guide"
    assert guide_result["count"] >= 1
    assert {item["kb_type"] for item in guide_result["results"]} == {"guide"}
    assert all(item["source"].startswith("guide/") for item in guide_result["results"])
    assert config_result["status"] == "success"
    assert all(item["kb_type"] == "configuration" for item in config_result["results"])
    assert invalid_result["status"] == "error"
    assert "kb_type must be one of" in invalid_result["error"]


def test_pg_knowledge_chroma_missing_falls_back_to_sqlite(tmp_path, monkeypatch):
    source_dir = tmp_path / "docs"
    doc_path = source_dir / "partIII_server_administration" / "13_monitoring.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text(
        "# Monitoring Database Activity\n\n"
        "Use `pg_stat_activity` with `pg_locks` to identify blocking sessions.\n",
        encoding="utf-8",
    )
    sqlite_dir = tmp_path / "sqlite"
    PGKnowledgeBase(persist_dir=sqlite_dir, backend="sqlite").build(
        source_dir=source_dir,
        chunk_size=300,
        chunk_overlap=40,
    )
    monkeypatch.setenv("AIOPS_PG_KB_SQLITE_DIR", str(sqlite_dir))

    kb = PGKnowledgeBase(persist_dir=tmp_path / "missing_chroma", backend="chroma")
    result = kb.query("pg_stat_activity blocking sessions")

    assert result["status"] == "success"
    assert result["fallback_for"] == "chroma"
    assert result["index"]["backend"] == "sqlite"
    assert result["index"]["fallback_for"] == "chroma"


def test_pg_env_dispatches_general_knowledge_tool(monkeypatch):
    class FakeKnowledgeBase:
        def __init__(self, *args, **kwargs):
            self.knowledge_base_mode = kwargs.get("knowledge_base_mode")

        def query(self, query, top_k=5, max_chars_per_result=1600, kb_type=None):
            return {
                "status": "success",
                "knowledge_base_mode": self.knowledge_base_mode,
                "query": query,
                "kb_type": kb_type,
                "top_k": top_k,
                "results": [{"source": "doc.md", "content": "hit"}],
            }

    monkeypatch.setattr(environment, "PGKnowledgeBase", FakeKnowledgeBase)
    env = PGEnv(deployment=object())

    raw = env.execute_action(
        "query_knowledge_base",
        {
            "query": "autovacuum dead tuples",
            "top_k": "2",
            "max_chars_per_result": "400",
        },
    )
    result = json.loads(raw)

    assert result["status"] == "success"
    assert result["knowledge_base_mode"] == "general"
    assert result["query"] == "autovacuum dead tuples"
    assert result["kb_type"] is None
    assert result["top_k"] == 2
    assert result["results"][0]["source"] == "doc.md"


def test_pg_env_rejects_kb_type_on_general_knowledge_tool():
    env = PGEnv(deployment=object())

    raw = env.execute_action(
        "query_knowledge_base",
        {"query": "autovacuum dead tuples", "kb_type": "solution"},
    )
    result = json.loads(raw)

    assert result["status"] == "error"
    assert "Unexpected argument" in result["error"]


def test_pg_env_dispatches_hierarchical_knowledge_tool(monkeypatch):
    class FakeKnowledgeBase:
        def __init__(self, *args, **kwargs):
            self.knowledge_base_mode = kwargs.get("knowledge_base_mode")

        def query(self, query, top_k=5, max_chars_per_result=1600, kb_type=None):
            return {
                "status": "success",
                "knowledge_base_mode": self.knowledge_base_mode,
                "query": query,
                "kb_type": kb_type,
                "top_k": top_k,
                "results": [{"source": "solution/doc.md", "content": "hit"}],
            }

    monkeypatch.setattr(environment, "PGKnowledgeBase", FakeKnowledgeBase)
    env = PGEnv(deployment=object(), tool_profile="hierarchical_knowledge")

    raw = env.execute_action(
        "query_knowledge_base",
        {
            "query": "autovacuum dead tuples",
            "kb_type": "solution",
            "top_k": "2",
            "max_chars_per_result": "400",
        },
    )
    result = json.loads(raw)

    assert result["status"] == "success"
    assert result["knowledge_base_mode"] == "hierarchical"
    assert result["query"] == "autovacuum dead tuples"
    assert result["kb_type"] == "solution"
    assert result["top_k"] == 2
    assert result["results"][0]["source"] == "solution/doc.md"


def test_pg_env_help_tracks_tool_profile():
    env = PGEnv(deployment=object(), tool_profile="general_knowledge")

    general_help = json.loads(env.help())
    general_names = {tool["name"] for tool in general_help["tools"]}
    assert "query_knowledge_base" in general_names
    assert "query_hierarchical_knowledge_base" not in general_names
    general_tool = json.loads(env.help("query_knowledge_base"))
    general_arg_names = {
        parameter["name"]
        for parameter in general_tool["definition"]["parameters"]
    }
    assert "kb_type" not in general_arg_names

    env = PGEnv(deployment=object(), tool_profile="hierarchical_knowledge")
    hierarchical_help = json.loads(env.help())
    hierarchical_names = {tool["name"] for tool in hierarchical_help["tools"]}
    assert "query_knowledge_base" in hierarchical_names
    assert "query_hierarchical_knowledge_base" not in hierarchical_names
    hierarchical_tool = json.loads(env.help("query_knowledge_base"))
    hierarchical_arg_names = {
        parameter["name"]
        for parameter in hierarchical_tool["definition"]["parameters"]
    }
    assert "kb_type" in hierarchical_arg_names


def test_pg_env_enabled_tools_selects_internal_tool_implementation():
    env = PGEnv(
        deployment=object(),
        enabled_tools=[
            "query_metrics",
            "execute_sql",
            "query_hierarchical_knowledge_base",
            "help",
            "submit",
            "exit",
        ],
    )

    schemas = env.get_tool_schemas()
    names = {schema["function"]["name"] for schema in schemas}
    knowledge_schema = next(
        schema for schema in schemas
        if schema["function"]["name"] == "query_knowledge_base"
    )

    assert "query_knowledge_base" in names
    assert "query_hierarchical_knowledge_base" not in names
    assert "kb_type" in knowledge_schema["function"]["parameters"]["properties"]


def test_pg_env_enabled_tools_rejects_ambiguous_tool_alias():
    try:
        PGEnv(
            deployment=object(),
            enabled_tools=["query_knowledge_base"],
        )
    except ValueError as exc:
        assert "maps to multiple implementations" in str(exc)
    else:
        raise AssertionError("Expected ambiguous query_knowledge_base alias to be rejected")


def test_pg_env_enabled_tools_can_select_general_internal_tool_id():
    env = PGEnv(
        deployment=object(),
        enabled_tools=[
            "query_metrics",
            "execute_sql",
            "query_general_knowledge_base",
            "help",
            "submit",
            "exit",
        ],
    )

    schemas = env.get_tool_schemas()
    names = {schema["function"]["name"] for schema in schemas}
    knowledge_schema = next(
        schema for schema in schemas
        if schema["function"]["name"] == "query_knowledge_base"
    )

    assert "query_knowledge_base" in names
    assert "query_general_knowledge_base" not in names
    assert "query_hierarchical_knowledge_base" not in names
    assert "kb_type" not in knowledge_schema["function"]["parameters"]["properties"]


def test_orchestrator_uses_env_tool_profile():
    class DummyScenario:
        scenario_id = "dummy"
        description = "dummy"

    class DummyCase:
        case_id = "dummy_case"
        case_no = 0
        alert = "alert"

    class DummyEvaluator:
        def __init__(self, env, *, diagnosis_matcher):
            self.env = env

    DummyCase.evaluator = DummyEvaluator

    class DummyAgent:
        use_native_tools = True

    env = PGEnv(deployment=object(), tool_profile="hierarchical_knowledge")
    orchestrator = Orchestrator(
        env=env,
        scenario=DummyScenario(),
        case=DummyCase(),
        agent=DummyAgent(),
    )

    prompt = orchestrator._get_system_prompt()
    schemas = orchestrator._get_tool_schemas()
    names = {schema["function"]["name"] for schema in schemas}
    knowledge_schema = next(
        schema for schema in schemas
        if schema["function"]["name"] == "query_knowledge_base"
    )

    assert "query_knowledge_base" in prompt
    assert "query_knowledge_base" in names
    assert "query_hierarchical_knowledge_base" not in names
    assert "kb_type" in knowledge_schema["function"]["parameters"]["properties"]


def test_pg_doc_metadata_extracts_title(tmp_path):
    source_dir = tmp_path / "docs"
    doc_path = source_dir / "partIII_server_administration" / "13_monitoring.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("# Monitoring Database Activity\n\n## pg_stat_activity\n", encoding="utf-8")

    metadata = PGKnowledgeBase._metadata_for_file(doc_path, source_dir)

    assert metadata["relative_path"] == str(Path("partIII_server_administration") / "13_monitoring.md")
    assert metadata["part"] == "partIII_server_administration"
    assert metadata["kb_type"] == ""
    assert metadata["title"] == "Monitoring Database Activity"
    assert "pg_stat_activity" in metadata["headings"]


def test_pg_doc_metadata_extracts_kb_type(tmp_path):
    source_dir = tmp_path / "pg"
    doc_path = source_dir / "guide" / "lock_contention.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("# Lock Contention\n\n## pg_locks\n", encoding="utf-8")

    metadata = PGKnowledgeBase._metadata_for_file(doc_path, source_dir)

    assert metadata["relative_path"] == str(Path("guide") / "lock_contention.md")
    assert metadata["part"] == "guide"
    assert metadata["kb_type"] == "guide"


def test_pg_chroma_metadata_is_flat(tmp_path):
    source_dir = tmp_path / "docs"
    doc_path = source_dir / "partIII_server_administration" / "13_monitoring.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("# Monitoring Database Activity\n\n## pg_stat_activity\n", encoding="utf-8")

    metadata = PGKnowledgeBase._chroma_metadata_for_file(doc_path, source_dir)

    assert metadata["headings"] == "Monitoring Database Activity > pg_stat_activity"
    assert all(not isinstance(value, (list, dict)) for value in metadata.values())
