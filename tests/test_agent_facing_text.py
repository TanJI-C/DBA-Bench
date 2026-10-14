import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.execution.environments.postgres import PGEnv
from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_tool_definitions import TIDB_TOOL_DEFINITIONS
from src.execution.postgres_metrics import POSTGRES_QUERY_METRICS_TOOL_DEFINITION


ROOT = Path(__file__).resolve().parents[1]
DESIGN_LINEAGE = re.compile(
    r"metric[-_ ]?first|kb[-_ ]?first|knowledge[-_ ]?first|db[-_ ]?agent式",
    re.IGNORECASE,
)


def _text(value):
    return json.dumps(value, ensure_ascii=False).casefold()


def test_public_tool_definitions_do_not_expose_development_taxonomy():
    public = [TIDB_TOOL_DEFINITIONS, POSTGRES_QUERY_METRICS_TOOL_DEFINITION]
    public.append(PGEnv(deployment=object()).build_tool_instructions())
    payload = _text(public)
    assert not DESIGN_LINEAGE.search(payload)


@pytest.mark.parametrize("profile", PGEnv.TOOL_PROFILES)
def test_postgres_agent_interfaces_do_not_expose_design_lineage(profile):
    _assert_neutral_interfaces(PGEnv(deployment=object(), tool_profile=profile))


def test_tidb_agent_interfaces_do_not_expose_design_lineage():
    deployment = SimpleNamespace(
        run_id="vocabulary-check",
        primary_tidb_endpoint=("127.0.0.1", 4000),
        tidb_endpoints={"tidb-0": ("127.0.0.1", 4000)},
    )
    _assert_neutral_interfaces(TiDBEnv(deployment=deployment))


def _assert_neutral_interfaces(env):
    public = [
        env.get_tool_schemas(),
        env.build_tool_instructions(),
        env.build_tool_instructions(use_native_tools=True),
        env.help(),
        *(env.help(spec.alias) for spec in env.get_tool_specs()),
    ]
    assert not DESIGN_LINEAGE.search(_text(public))


def test_public_tidb_serving_corpus_does_not_expose_design_lineage():
    path = ROOT / "knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl"
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        assert not DESIGN_LINEAGE.search(line), f"{path}:{number} exposes design lineage"


def test_public_postgres_knowledge_chunks_do_not_expose_design_lineage():
    root = ROOT / "knowledge/pg"
    manifest = json.loads((root / "mappings/pg16_chunk_manifest.json").read_text(encoding="utf-8"))
    for chunk in manifest["chunks"]:
        path = root / chunk["target_file"]
        assert not DESIGN_LINEAGE.search(path.read_text(encoding="utf-8")), str(path)


def test_postgres_hierarchical_knowledge_description_is_not_procedural():
    payload = _text([spec.agent_description() for spec in PGEnv(deployment=object()).get_tool_specs()])
    assert "dbagent式" not in payload
    assert "先查guide" not in payload
