from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml

from src.agents.context_compaction import ContextCompactionConfig
from src.agents.loop_guard import LoopGuardConfig
from src.agents.baselines.v_expel.config import VExpeLConfig
from src.scenarios.base import DatabaseSystem
from src.scenarios.registry import ScenarioCategory

from src.agent_language import DEFAULT_AGENT_LANGUAGE, validate_agent_language

from .models import AgentSpec, IsolationPolicySpec, RuntimeSpec, ScenarioKind
from .isolation import expand_linux_set

# Agent modes whose own prompts exist only in Chinese; English runs refuse them.
UNTRANSLATED_AGENT_MODES = frozenset({"dbot", "dbaiops", "v-expel"})


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class BenchmarkSpec:
    scenario_kind: ScenarioKind
    systems: tuple[DatabaseSystem, ...]
    categories: tuple[ScenarioCategory, ...]
    scenarios: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentManifest:
    experiment_id: str
    benchmark: BenchmarkSpec
    agents: tuple[AgentSpec, ...]
    exclude_cells: frozenset[tuple[str, str, str]]
    repetitions: int
    seeds: tuple[int, ...]
    runtime: RuntimeSpec
    source_path: Path
    raw: dict[str, Any]


def _require_mapping(data: Any, context: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{context} must be a mapping, got {type(data).__name__}")
    return data


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"{context} contains unknown fields: {sorted(unknown)}")


def _require_nonempty_string(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string, got {value!r}")
    return value.strip()


def validate_identifier(value: str, context: str) -> str:
    if not IDENTIFIER_RE.fullmatch(value) or "__" in value:
        raise ValueError(
            f"{context} must contain only letters, digits, '_' or '-' and must not "
            f"contain '__', got {value!r}"
        )
    return value


def _require_identifier(data: dict[str, Any], key: str, context: str) -> str:
    value = _require_nonempty_string(data, key, context)
    return validate_identifier(value, f"{context}.{key}")


def load_manifest(path: str | Path) -> ExperimentManifest:
    source_path = Path(path).resolve()
    raw = _require_mapping(yaml.safe_load(source_path.read_text(encoding="utf-8")), "manifest")
    _reject_unknown_keys(
        raw,
        {
            "experiment_id",
            "benchmark",
            "agents",
            "exclude_cells",
            "repetitions",
            "seeds",
            "runtime",
        },
        "manifest",
    )
    experiment_id = _require_identifier(raw, "experiment_id", "manifest")

    benchmark_data = _require_mapping(raw.get("benchmark"), "manifest.benchmark")
    _reject_unknown_keys(
        benchmark_data,
        {"scenario_kind", "systems", "categories", "scenarios"},
        "manifest.benchmark",
    )
    scenario_kind_value = str(benchmark_data.get("scenario_kind", ScenarioKind.BOUNDED.value))
    try:
        scenario_kind = ScenarioKind(scenario_kind_value)
    except ValueError as exc:
        raise ValueError(
            "manifest.benchmark.scenario_kind must be bounded or persistent: "
            f"value={scenario_kind_value!r}"
        ) from exc
    if scenario_kind is ScenarioKind.PERSISTENT:
        persistent_keys = {"scenario_kind", "scenarios"}
        if set(benchmark_data) != persistent_keys:
            raise ValueError(
                "manifest.benchmark scenario_kind=persistent only accepts scenarios: "
                f"fields={sorted(benchmark_data)}"
            )
        scenarios_value = benchmark_data.get("scenarios")
        if not isinstance(scenarios_value, list) or not scenarios_value:
            raise ValueError("manifest.benchmark.scenarios must be a non-empty list")
        scenarios = tuple(validate_identifier(str(item), "manifest.benchmark.scenarios[]") for item in scenarios_value)
        if len(set(scenarios)) != len(scenarios):
            raise ValueError("manifest.benchmark.scenarios contains duplicates")
        systems = ()
        categories = ()
    else:
        systems_value = benchmark_data.get("systems")
        if not isinstance(systems_value, list) or not systems_value:
            raise ValueError("manifest.benchmark.systems must be a non-empty list")
        systems = tuple(DatabaseSystem(str(item)) for item in systems_value)
        if len(set(systems)) != len(systems):
            raise ValueError("manifest.benchmark.systems contains duplicates")
        categories_value = benchmark_data.get("categories")
        if not isinstance(categories_value, list) or not categories_value:
            raise ValueError("manifest.benchmark.categories must be a non-empty list")
        categories = tuple(ScenarioCategory(str(item)) for item in categories_value)
        if len(set(categories)) != len(categories):
            raise ValueError("manifest.benchmark.categories contains duplicates")
        scenarios_value = benchmark_data.get("scenarios", "all")
        if scenarios_value == "all":
            scenarios = ()
        elif isinstance(scenarios_value, list):
            scenarios = tuple(str(item) for item in scenarios_value)
        else:
            raise ValueError(
                "manifest.benchmark.scenarios must be 'all' or a list, "
                f"got {scenarios_value!r}"
            )
    agent_items = raw.get("agents")
    if not isinstance(agent_items, list) or not agent_items:
        raise ValueError("manifest.agents must be a non-empty list")
    agents = []
    for index, item in enumerate(agent_items):
        context = f"manifest.agents[{index}]"
        data = _require_mapping(item, context)
        _reject_unknown_keys(
            data,
            {
                "id",
                "mode",
                "model",
                "reasoning_effort",
                "max_turns",
                "max_output_tokens",
                "settings",
            },
            context,
        )
        mode = _require_nonempty_string(data, "mode", context)
        if mode not in {"mock", "zero", "llm", "human", "remote", "v-expel", "dbot", "dbaiops"}:
            raise ValueError(
                f"manifest.agents[{index}].mode must be mock, zero, llm, v-expel, dbot, "
                f"dbaiops, human, or remote, got {mode!r}"
            )
        if mode == "v-expel" and scenario_kind is not ScenarioKind.PERSISTENT:
            raise ValueError("v-expel is only supported when benchmark.scenario_kind='persistent'")
        max_turns = int(data.get("max_turns", 30))
        if max_turns < 1:
            raise ValueError(f"manifest.agents[{index}].max_turns must be >= 1, got {max_turns}")
        max_output_tokens = data.get("max_output_tokens")
        if max_output_tokens is not None:
            max_output_tokens = int(max_output_tokens)
            if max_output_tokens < 1:
                raise ValueError(
                    f"manifest.agents[{index}].max_output_tokens must be >= 1, "
                    f"got {max_output_tokens}"
                )
        model = data.get("model")
        if mode in {"llm", "v-expel", "dbot", "dbaiops"} and not model:
            raise ValueError(f"{context}.model is required when mode={mode!r}")
        reasoning_effort = data.get("reasoning_effort")
        if reasoning_effort is not None:
            if mode not in {"llm", "v-expel"}:
                raise ValueError(
                    f"{context}.reasoning_effort is only supported when mode is 'llm' or 'v-expel'"
                )
            reasoning_effort = _require_nonempty_string(data, "reasoning_effort", context)
            if reasoning_effort not in {"low", "medium", "high", "xhigh"}:
                raise ValueError(
                    f"{context}.reasoning_effort must be low, medium, high, or xhigh, "
                    f"got {reasoning_effort!r}"
                )
        settings = _require_mapping(data.get("settings", {}), f"{context}.settings")
        if mode == "human":
            if scenario_kind is ScenarioKind.PERSISTENT:
                raise ValueError("human currently supports bounded scenarios only")
            if set(settings) != {"console_url", "participant"}:
                raise ValueError(f"{context}.settings requires console_url and participant")
            _require_nonempty_string(settings, "console_url", context)
            _require_nonempty_string(settings, "participant", context)
        if mode == "remote":
            if scenario_kind is ScenarioKind.PERSISTENT:
                raise ValueError("remote currently supports bounded scenarios only")
            if set(settings) != {"endpoint"}:
                raise ValueError(
                    f"{context}.settings must contain exactly ['endpoint'], got {sorted(settings)}"
                )
            from src.agents.remote_agent import validate_endpoint

            validate_endpoint(settings["endpoint"])
            if max_output_tokens is not None:
                raise ValueError(f"{context}.max_output_tokens is not supported when mode='remote'")
        if mode == "zero" and settings:
            raise ValueError(f"{context}.settings must be empty when mode={mode!r}")
        if mode == "llm":
            unexpected = set(settings) - {"context_compaction", "loop_guard"}
            if unexpected:
                raise ValueError(
                    f"{context}.settings has unknown keys: {sorted(unexpected)}"
                )
            ContextCompactionConfig.from_settings(
                {"context_compaction": settings["context_compaction"]}
                if "context_compaction" in settings else {}
            )
            LoopGuardConfig.from_settings(settings.get("loop_guard"))
        if mode == "v-expel":
            VExpeLConfig.from_settings(settings)
        agents.append(AgentSpec(
            id=_require_identifier(data, "id", context),
            mode=mode,
            model=model,
            reasoning_effort=reasoning_effort,
            max_turns=max_turns,
            max_output_tokens=max_output_tokens,
            settings=settings,
        ))
    if len({agent.id for agent in agents}) != len(agents):
        raise ValueError("manifest.agents contains duplicate id values")

    exclude_items = raw.get("exclude_cells", [])
    if not isinstance(exclude_items, list):
        raise ValueError(
            f"manifest.exclude_cells must be a list, got {type(exclude_items).__name__}"
        )
    exclude_cells = []
    for index, item in enumerate(exclude_items):
        context = f"manifest.exclude_cells[{index}]"
        data = _require_mapping(item, context)
        required_keys = {"scenario", "case", "agent"}
        if set(data) != required_keys:
            raise ValueError(
                f"{context} must contain exactly {sorted(required_keys)}, got {sorted(data)}"
            )
        exclude_cells.append((
            _require_identifier(data, "scenario", context),
            _require_identifier(data, "case", context),
            _require_identifier(data, "agent", context),
        ))
    if len(set(exclude_cells)) != len(exclude_cells):
        raise ValueError("manifest.exclude_cells contains duplicate cells")
    if scenario_kind is ScenarioKind.PERSISTENT and exclude_cells:
        raise ValueError("manifest.exclude_cells is not allowed when scenario_kind=persistent")

    repetitions = int(raw.get("repetitions", 1))
    if repetitions < 1:
        raise ValueError(f"manifest.repetitions must be >= 1, got {repetitions}")
    seeds = tuple(int(seed) for seed in raw.get("seeds", range(repetitions)))
    if len(seeds) != repetitions:
        raise ValueError(
            f"manifest.seeds must contain exactly {repetitions} values, got {len(seeds)}"
        )

    runtime_data = _require_mapping(raw.get("runtime", {}), "manifest.runtime")
    _reject_unknown_keys(
        runtime_data,
        {
            "concurrency",
            "timeout_seconds",
            "port_base",
            "container_prefix",
            "fault_snapshot",
            "llm_config",
            "tidb_storage_key",
            "tidb_storage_root",
            "tidb_cold_start_timeout_sec",
            "tidb_warm_start_timeout_sec",
            "postgres_cold_start_timeout_sec",
            "postgres_storage_root",
            "diagnosis_match_mode",
            "diagnosis_semantic_model",
            "agent_language",
            "isolation",
            "run_mode",
            "time_scale",
        },
        "manifest.runtime",
    )
    isolation_value = runtime_data.get("isolation")
    isolation = None
    if isolation_value is not None:
        isolation_data = _require_mapping(isolation_value, "manifest.runtime.isolation")
        allowed_keys = {"numa_policy", "cpuset_cpus"}
        if not set(isolation_data) <= allowed_keys or "numa_policy" not in isolation_data:
            raise ValueError(
                "manifest.runtime.isolation must contain exactly one numa_policy and "
                f"optional cpuset_cpus, got {sorted(isolation_data)}"
            )
        cpuset_cpus = isolation_data.get("cpuset_cpus")
        if cpuset_cpus is not None:
            if not isinstance(cpuset_cpus, str) or not cpuset_cpus:
                raise ValueError(
                    "manifest.runtime.isolation.cpuset_cpus must be a non-empty CPU set: "
                    f"value={cpuset_cpus!r}"
                )
            expand_linux_set(cpuset_cpus, "manifest.runtime.isolation.cpuset_cpus")
        isolation = IsolationPolicySpec(
            numa_policy=str(isolation_data["numa_policy"]),
            cpuset_cpus=cpuset_cpus,
        )
        if isolation.numa_policy not in {"local", "separate"}:
            raise ValueError(
                "manifest.runtime.isolation.numa_policy must be local or separate, "
                f"got {isolation.numa_policy!r}"
            )
    runtime = RuntimeSpec(
        concurrency=int(runtime_data.get("concurrency", 1)),
        timeout_seconds=int(runtime_data.get("timeout_seconds", 1800)),
        port_base=int(runtime_data.get("port_base", 16432)),
        container_prefix=str(runtime_data.get("container_prefix", "aiopsbench-experiment")),
        fault_snapshot=str(runtime_data.get("fault_snapshot", "auto")),
        llm_config=str(runtime_data.get("llm_config", "config/llm_config.json")),
        tidb_storage_key=(
            str(runtime_data["tidb_storage_key"])
            if runtime_data.get("tidb_storage_key") is not None else None
        ),
        tidb_storage_root=(
            str(runtime_data["tidb_storage_root"])
            if runtime_data.get("tidb_storage_root") is not None else None
        ),
        tidb_cold_start_timeout_sec=int(runtime_data.get("tidb_cold_start_timeout_sec", 900)),
        tidb_warm_start_timeout_sec=int(runtime_data.get("tidb_warm_start_timeout_sec", 300)),
        postgres_cold_start_timeout_sec=int(runtime_data.get("postgres_cold_start_timeout_sec", 600)),
        postgres_storage_root=(
            str(runtime_data["postgres_storage_root"])
            if runtime_data.get("postgres_storage_root") is not None else None
        ),
        diagnosis_match_mode=str(runtime_data.get("diagnosis_match_mode", "exact")),
        diagnosis_semantic_model=str(
            runtime_data.get("diagnosis_semantic_model", "Qwen/Qwen3-4B-Instruct-2507")
        ),
        agent_language=validate_agent_language(
            runtime_data.get("agent_language", DEFAULT_AGENT_LANGUAGE),
            "manifest.runtime.agent_language",
        ),
        isolation=isolation,
        run_mode=str(runtime_data.get("run_mode", "formal")),
        time_scale=float(runtime_data.get("time_scale", 1.0)),
    )
    if runtime.concurrency < 1:
        raise ValueError(f"manifest.runtime.concurrency must be >= 1, got {runtime.concurrency}")
    if runtime.timeout_seconds < 1:
        raise ValueError(
            f"manifest.runtime.timeout_seconds must be >= 1, got {runtime.timeout_seconds}"
        )
    if runtime.fault_snapshot not in {"auto", "off", "save", "use"}:
        raise ValueError(
            "manifest.runtime.fault_snapshot must be auto, off, save, or use, "
            f"got {runtime.fault_snapshot!r}"
        )
    if runtime.run_mode not in {"formal", "development", "development_compressed", "calibration_failure_probe"}:
        raise ValueError(
            "manifest.runtime.run_mode must be formal, development, development_compressed, "
            f"or calibration_failure_probe, got {runtime.run_mode!r}"
        )
    if runtime.time_scale <= 0:
        raise ValueError(f"manifest.runtime.time_scale must be positive: value={runtime.time_scale!r}")
    if runtime.run_mode == "development_compressed" and runtime.time_scale <= 1:
        raise ValueError(
            "manifest.runtime.time_scale must be > 1 for development_compressed: "
            f"value={runtime.time_scale!r}"
        )
    if runtime.run_mode != "development_compressed" and runtime.time_scale != 1.0:
        raise ValueError(
            "manifest.runtime.time_scale must be 1 for non-compressed runs: "
            f"run_mode={runtime.run_mode!r}, value={runtime.time_scale!r}"
        )
    if runtime.tidb_cold_start_timeout_sec <= 0 or runtime.tidb_warm_start_timeout_sec <= 0:
        raise ValueError(
            "manifest.runtime TiDB readiness timeouts must be positive: "
            f"cold={runtime.tidb_cold_start_timeout_sec}, warm={runtime.tidb_warm_start_timeout_sec}"
        )
    if runtime.postgres_cold_start_timeout_sec <= 0:
        raise ValueError(
            "manifest.runtime PostgreSQL cold-start timeout must be positive: "
            f"cold={runtime.postgres_cold_start_timeout_sec}"
        )
    if runtime.diagnosis_match_mode not in {"exact", "semantic"}:
        raise ValueError(
            "manifest.runtime.diagnosis_match_mode must be exact or semantic, "
            f"got {runtime.diagnosis_match_mode!r}"
        )
    if not runtime.diagnosis_semantic_model.strip():
        raise ValueError("manifest.runtime.diagnosis_semantic_model must be non-empty")
    if runtime.agent_language == "en":
        untranslated_systems = sorted(
            system.value for system in systems if system is not DatabaseSystem.POSTGRESQL
        )
        if untranslated_systems:
            raise ValueError(
                "manifest.runtime.agent_language='en' covers PostgreSQL only; agent-facing text "
                f"for {untranslated_systems} is Chinese. Use agent_language: zh for these systems."
            )
        if scenario_kind is ScenarioKind.PERSISTENT:
            raise ValueError(
                "manifest.runtime.agent_language='en' covers bounded scenarios only; "
                "persistent episodes are Chinese. Use agent_language: zh."
            )
        untranslated_agents = sorted(
            agent.id for agent in agents if agent.mode in UNTRANSLATED_AGENT_MODES
        )
        if untranslated_agents:
            raise ValueError(
                "manifest.runtime.agent_language='en' needs agents whose own prompts are "
                f"translated; agents {untranslated_agents} use modes "
                f"{sorted(UNTRANSLATED_AGENT_MODES)} with Chinese prompts."
            )
    if runtime.concurrency > 1:
        if runtime.isolation is None:
            raise ValueError(
                "Parallel experiments require manifest.runtime.isolation NUMA policy"
            )

    return ExperimentManifest(
        experiment_id=experiment_id,
        benchmark=BenchmarkSpec(
            scenario_kind=scenario_kind,
            systems=systems,
            categories=categories,
            scenarios=scenarios,
        ),
        agents=tuple(agents),
        exclude_cells=frozenset(exclude_cells),
        repetitions=repetitions,
        seeds=seeds,
        runtime=runtime,
        source_path=source_path,
        raw=raw,
    )
