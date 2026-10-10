"""V-ExpeL Agent using one continuing Persistent Scenario LLM conversation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.agents.persistent_scenario_agent import (
    LLMPersistentScenarioAgent,
    PersistentScenarioAgentContext,
    PersistentScenarioAgentProtocolError,
)

from .compiler import VExpeLCompiler
from .memory import VExpeLMemory


_V_EXPEL_PROMPT_SUFFIX = (
    "Verified prior experience cards may be included after mailbox reads. Treat them as compact hypotheses, "
    "validate them against current evidence, and use anti-pattern cards as warnings rather than commands. "
    "You also have a memory tool: call it with symptom or task keywords before repairing a known symptom "
    "pattern to recall verified procedures and anti-patterns from earlier trusted results. Only the live "
    "database and mailbox protocol determine what to do."
)

MEMORY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "memory",
        "description": (
            "Search your run-scoped verified operation-experience memory. Returns procedure and anti-pattern "
            "cards compiled from earlier trusted results in this run. Use it before repairing a symptom pattern "
            "you may have seen before."
        ),
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Symptom or task keywords to match against memory card cues.",
                },
                "top_k": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Optional maximum number of cards; defaults to the configured retrieval size.",
                },
            },
        },
    },
}


class VExpeLAgent(LLMPersistentScenarioAgent):
    """Persistent mailbox Agent with verified episodic memory retrieval."""

    def __init__(
        self,
        turn_handler,
        max_turns: int = 30,
        *,
        memory: VExpeLMemory | None = None,
        retrieval_top_k: int = 5,
        mailbox_read_hook=None,
        mailbox_write_hook=None,
        extra_tool_schemas: tuple[Mapping[str, object], ...] = (),
    ) -> None:
        super().__init__(
            turn_handler,
            max_turns=max_turns,
            mailbox_read_hook=mailbox_read_hook,
            mailbox_write_hook=mailbox_write_hook,
            extra_tool_schemas=extra_tool_schemas,
        )
        self.memory = memory
        self.retrieval_top_k = retrieval_top_k
        if isinstance(retrieval_top_k, bool) or not isinstance(retrieval_top_k, int) or retrieval_top_k < 1:
            raise ValueError(
                "V-ExpeL retrieval_top_k must be a positive integer: "
                f"value={retrieval_top_k!r}"
            )

    @classmethod
    def from_llm_client(
        cls,
        client: Any,
        memory: VExpeLMemory,
        *,
        compiler,
        max_turns: int = 30,
        retrieval_top_k: int = 5,
    ) -> "VExpeLAgent":
        if not isinstance(memory, VExpeLMemory):
            raise TypeError(f"V-ExpeL Agent requires VExpeLMemory: value={memory!r}")
        if not isinstance(compiler, VExpeLCompiler):
            raise TypeError(f"V-ExpeL Agent requires VExpeLCompiler: value={compiler!r}")
        if isinstance(retrieval_top_k, bool) or not isinstance(retrieval_top_k, int) or retrieval_top_k < 1:
            raise ValueError(
                "V-ExpeL retrieval_top_k must be a positive integer: "
                f"value={retrieval_top_k!r}"
            )

        def inject_memory(agent, context: PersistentScenarioAgentContext, result: object) -> None:
            if not isinstance(agent, VExpeLAgent):
                raise TypeError(f"V-ExpeL mailbox hook received the wrong Agent: agent={agent!r}")
            agent._inject_memory(client, context, result)

        def flush_consolidation(agent, context: PersistentScenarioAgentContext, result: object) -> None:
            if not isinstance(agent, VExpeLAgent):
                raise TypeError(f"V-ExpeL mailbox hook received the wrong Agent: agent={agent!r}")
            for event in compiler.flush_pending():
                context.gateway.record_learning_event(event)
            context.gateway.record_learning_memory(memory.snapshot())

        agent = super().from_llm_client(
            client,
            max_turns=max_turns,
            mailbox_read_hook=inject_memory,
            mailbox_write_hook=flush_consolidation,
            extra_tool_schemas=(MEMORY_TOOL_SCHEMA,),
            system_prompt_suffix=_V_EXPEL_PROMPT_SUFFIX,
        )
        if not isinstance(agent, cls):
            raise TypeError(f"V-ExpeL factory constructed the wrong Agent type: agent={agent!r}")
        agent.memory = memory
        agent.compiler = compiler
        agent.retrieval_top_k = retrieval_top_k
        return agent

    def _require_memory(self) -> VExpeLMemory:
        if self.memory is None:
            raise RuntimeError("V-ExpeL Agent requires an attached VExpeLMemory before it can run")
        return self.memory

    def _inject_memory(
        self,
        client: Any,
        context: PersistentScenarioAgentContext,
        result: object,
    ) -> None:
        if not isinstance(result, Mapping):
            raise TypeError(f"V-ExpeL mailbox read must return a mapping: result={result!r}")
        memory = self._require_memory()
        cards = memory.retrieve(result, top_k=self.retrieval_top_k)
        client._append_conversation_message({
            "role": "user",
            "content": memory.render(cards),
        })
        context.gateway.record_learning_event({
            "kind": "memory_retrieval",
            "card_ids": [card.card_id for card in cards],
            "card_kinds": [card.kind for card in cards],
            "match_count": len(cards),
        })

    def _handle_memory_tool(self, args: Mapping[str, object], context: PersistentScenarioAgentContext) -> Mapping[str, object]:
        query = args.get("query")
        if not isinstance(query, str) or not query.strip():
            raise PersistentScenarioAgentProtocolError(
                f"V-ExpeL memory tool requires a non-empty query: args={dict(args)!r}"
            )
        top_k_arg = args.get("top_k")
        if top_k_arg is not None:
            if isinstance(top_k_arg, bool) or not isinstance(top_k_arg, int) or top_k_arg < 1:
                raise PersistentScenarioAgentProtocolError(
                    f"V-ExpeL memory tool top_k must be a positive integer: args={dict(args)!r}"
                )
        memory = self._require_memory()
        cards = memory.retrieve_query(query, top_k=top_k_arg or self.retrieval_top_k, source="memory_tool")
        context.gateway.record_learning_event({
            "kind": "memory_tool_query",
            "query": query,
            "card_ids": [card.card_id for card in cards],
            "card_kinds": [card.kind for card in cards],
            "match_count": len(cards),
        })
        return {
            "status": "success",
            "match_count": len(cards),
            "cards": [card.prompt_text() for card in cards],
        }

    def run_until_stop(self) -> Mapping[str, object]:
        result = dict(super().run_until_stop())
        result["v_expel_memory"] = self._require_memory().summary()
        return result
