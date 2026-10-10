from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from src.agents.agent import LLMAgent
from src.agents.context_compaction import ContextCompactionConfig
from src.agents.loop_guard import LoopGuardConfig
from src.agents.baselines.dbaiops.agent import DbaiopsAgent
from src.agents.baselines.dbot.agent import DbotAgent
from src.agents.baselines.dbot.mcts import TreeSearchConfig


DBOT_SETTING_KEYS = {
    "knowledge_paths",
    "knowledge_sha256",
    "knowledge_top_k",
    "max_hired_experts",
    "max_parallel_experts",
    "mode",
    "search",
    "use_native_tools",
}
DBAIOPS_SETTING_KEYS = {
    "adf_score_threshold",
    "adf_theta",
    "frequency_m",
    "frequency_n",
    "graph_path",
    "graph_sha256",
    "max_evolution_depth",
    "top_k",
}
SEARCH_SETTING_KEYS = {
    "epsilon_new_node",
    "simulation_count",
    "single_chain_max_step",
    "vote_candidates",
}


def _require_exact_keys(settings: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(settings)
    if actual != expected:
        raise ValueError(
            f"{context} settings must contain exactly {sorted(expected)}, got {sorted(actual)}"
        )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_sha256(path: str) -> str:
    root = Path(path)
    if root.is_file():
        return _file_sha256(root)
    if not root.is_dir():
        raise FileNotFoundError(f"Agent knowledge artifact does not exist: {path}")
    digest = hashlib.sha256()
    files = sorted(item for item in root.rglob("*") if item.is_file())
    if not files:
        raise RuntimeError(f"Agent knowledge directory contains no files: {path}")
    for item in files:
        digest.update(item.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_file_sha256(item)))
    return digest.hexdigest()


def _verify_artifact(path: str, expected_sha256: str, context: str) -> None:
    actual = _path_sha256(path)
    if actual != expected_sha256:
        raise ValueError(
            f"{context} hash mismatch: path={path!r}, expected={expected_sha256!r}, "
            f"actual={actual!r}"
        )


def parse_agent_settings(raw: str) -> dict[str, Any]:
    settings = json.loads(raw)
    if not isinstance(settings, dict):
        raise ValueError(f"--agent-settings must decode to a JSON object, got {type(settings).__name__}")
    return settings


def build_benchmark_agent(
    agent_name: str,
    model: str,
    config_path: str,
    settings: dict[str, Any],
    seed: int,
    max_output_tokens: int | None = None,
    reasoning_effort: str | None = None,
):
    if agent_name == "human":
        from src.agents.browser_human import BrowserHumanAgent

        return BrowserHumanAgent(**settings)
    if agent_name == "remote":
        from src.agents.remote_agent import RemoteAgent

        _require_exact_keys(settings, {"endpoint"}, "Remote agent")
        return RemoteAgent(endpoint=settings["endpoint"])
    if agent_name == "llm":
        context_compaction = ContextCompactionConfig.from_settings(
            {"context_compaction": settings["context_compaction"]}
            if "context_compaction" in settings else {}
        )
        loop_guard = LoopGuardConfig.from_settings(settings.get("loop_guard"))
        return LLMAgent(
            model=model,
            config_path=config_path,
            use_native_tools=True,
            max_output_tokens=max_output_tokens,
            context_compaction=context_compaction,
            loop_guard=loop_guard,
            reasoning_effort=reasoning_effort,
        )
    if reasoning_effort is not None:
        raise ValueError(
            f"reasoning_effort is only supported for agent_name='llm', got {agent_name!r}"
        )
    if max_output_tokens is not None:
        raise ValueError(
            f"max_output_tokens is only supported for agent_name='llm', got {agent_name!r}"
        )
    if agent_name == "dbot":
        _require_exact_keys(settings, DBOT_SETTING_KEYS, "D-Bot")
        search = settings["search"]
        if not isinstance(search, dict):
            raise ValueError(f"D-Bot search settings must be a JSON object, got {type(search).__name__}")
        _require_exact_keys(search, SEARCH_SETTING_KEYS, "D-Bot search")
        knowledge_paths = settings["knowledge_paths"]
        knowledge_hashes = settings["knowledge_sha256"]
        if not isinstance(knowledge_paths, list) or not knowledge_paths:
            raise ValueError(f"D-Bot knowledge_paths must be a non-empty list, got {knowledge_paths!r}")
        if not isinstance(knowledge_hashes, dict) or set(knowledge_hashes) != set(knowledge_paths):
            raise ValueError(
                f"D-Bot knowledge_sha256 keys must match knowledge_paths: "
                f"paths={knowledge_paths!r}, hashes={knowledge_hashes!r}"
            )
        for path in knowledge_paths:
            _verify_artifact(path, knowledge_hashes[path], "D-Bot knowledge")
        agent = DbotAgent(
            mode=settings["mode"],
            model=model,
            config_path=config_path,
            use_native_tools=bool(settings["use_native_tools"]),
            max_hired_experts=int(settings["max_hired_experts"]),
            max_parallel_experts=int(settings["max_parallel_experts"]),
            knowledge_paths=knowledge_paths,
            knowledge_top_k=int(settings["knowledge_top_k"]),
            search_config=TreeSearchConfig(**search),
            seed=seed,
        )
        agent._ensure_llm()
        return agent
    if agent_name == "dbaiops":
        _require_exact_keys(settings, DBAIOPS_SETTING_KEYS, "DBAIOps")
        _verify_artifact(settings["graph_path"], settings["graph_sha256"], "DBAIOps graph")
        return DbaiopsAgent(
            model=model,
            graph_path=settings["graph_path"],
            config_path=config_path,
            adf_theta=float(settings["adf_theta"]),
            adf_score_threshold=float(settings["adf_score_threshold"]),
            frequency_m=int(settings["frequency_m"]),
            frequency_n=int(settings["frequency_n"]),
            max_evolution_depth=int(settings["max_evolution_depth"]),
            top_k=int(settings["top_k"]),
        )
    raise ValueError(
        f"Unsupported agent_name={agent_name!r}; choose llm, dbot, dbaiops, human, or remote"
    )


def build_experiment_agent(
    model: str,
    config_path: str,
    use_native_tools: bool = True,
    max_output_tokens: int | None = None,
    reasoning_effort: str | None = None,
):
    if use_native_tools is not True:
        raise ValueError(
            f"Experiment agents require native tools, got use_native_tools={use_native_tools!r}"
        )
    required = ("AIOPS_AGENT_MODE", "AIOPS_AGENT_SETTINGS", "AIOPS_SEED")
    missing = [name for name in required if name not in os.environ]
    if missing:
        raise RuntimeError(
            "Real scenario agents must be created by scripts/run_experiment.py: "
            f"missing_environment={missing!r}"
        )
    return build_benchmark_agent(
        agent_name=os.environ["AIOPS_AGENT_MODE"],
        model=model,
        config_path=config_path,
        settings=parse_agent_settings(os.environ["AIOPS_AGENT_SETTINGS"]),
        seed=int(os.environ["AIOPS_SEED"]),
        max_output_tokens=max_output_tokens,
        reasoning_effort=(
            reasoning_effort
            if reasoning_effort is not None
            else os.environ.get("AIOPS_REASONING_EFFORT")
        ),
    )
