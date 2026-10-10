import json
import re
from pathlib import Path

import pytest

from src.execution.environment import PGEnv
from src.execution.tidb_tool_definitions import TIDB_TOOL_DEFINITIONS
from src.execution.postgres_metrics import POSTGRES_QUERY_METRICS_TOOL_DEFINITION


VOCABULARY_DOC = (
    Path(__file__).resolve().parents[1]
    / "docs" / "standards" / "evaluation" / "agent-facing-vocabulary.standard.md"
)

_needs_vocabulary_doc = pytest.mark.skipif(
    not VOCABULARY_DOC.exists(),
    reason="the vocabulary configuration is not present in this checkout",
)


def forbidden_vocabulary() -> tuple[str, ...]:
    """Parse the canonical vocabulary block from the agent-facing vocabulary standard."""
    text = VOCABULARY_DOC.read_text(encoding="utf-8")
    block = re.search(r"```vocabulary\n(.*?)```", text, re.DOTALL)
    assert block, f"vocabulary block missing in {VOCABULARY_DOC}"
    terms = tuple(line.strip() for line in block.group(1).splitlines() if line.strip())
    assert terms, f"vocabulary block is empty in {VOCABULARY_DOC}"
    return terms


def _text(value):
    return json.dumps(value, ensure_ascii=False).casefold()


@_needs_vocabulary_doc
def test_public_tool_definitions_do_not_expose_development_taxonomy():
    public = [TIDB_TOOL_DEFINITIONS, POSTGRES_QUERY_METRICS_TOOL_DEFINITION]
    public.append(PGEnv(deployment=object()).build_tool_instructions())
    payload = _text(public)
    for term in forbidden_vocabulary():
        assert term.casefold() not in payload, term


@_needs_vocabulary_doc
def test_postgres_hierarchical_knowledge_description_is_not_procedural():
    payload = _text([spec.agent_description() for spec in PGEnv(deployment=object()).get_tool_specs()])
    assert "先查guide" not in payload
    for term in forbidden_vocabulary():
        assert term.casefold() not in payload, term
