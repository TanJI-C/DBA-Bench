from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from .project_paths import DATASETS_ROOT, EXPERIMENTS_ROOT
from .benchmark.dataset import (
    aggregate_dataset,
    build_dataset_outputs,
    create_dataset_spec,
    dataset_lock_path,
    dataset_spec_path,
    diff_dataset_locks,
    freeze_dataset,
    load_dataset_spec,
    load_live_records,
    records_from_lock,
    sha256,
    verify_dataset_lock,
)
from .benchmark.api import (
    ExperimentRunner,
    ExperimentStore,
    load_manifest,
    plan_runs,
    select_specs,
    validate_execution_plan,
    validate_identifier,
)


# Source commands must run from the active checkout. Shared artifact paths are
# still provided by src.project_paths, but linked worktrees may have different
# source revisions from the main checkout.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DEFINITIONS_ROOT = DATASETS_ROOT
DATASET_OUTPUT_ROOT = PROJECT_ROOT / "artifacts" / "datasets"


def require_clean_checkout() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True
    ).splitlines()
    if status:
        raise RuntimeError(
            "Formal experiment execution requires a clean Git worktree; "
            f"found {len(status)} changed or untracked paths. Commit the exact experiment "
            "code and manifest before running."
        )


def require_original_checkout(store: ExperimentStore) -> None:
    require_clean_checkout()
    environment_path = store.root / "environment.json"
    environment = json.loads(environment_path.read_text(encoding="utf-8"))
    current_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True
    ).strip()
    if current_commit != environment["git_commit"]:
        raise RuntimeError(
            f"Experiment resume requires its original Git commit: "
            f"experiment_id={store.root.name!r}, expected={environment['git_commit']!r}, "
            f"actual={current_commit!r}"
        )


def print_plan(manifest_path: Path, run_ids: list[str]) -> None:
    manifest = load_manifest(manifest_path)
    all_specs = plan_runs(manifest)
    specs = select_specs(all_specs, run_ids)
    workers = validate_execution_plan(manifest, all_specs)
    for worker in workers:
        print(
            f"worker={worker.id} physical_cores={','.join(worker.physical_cores)} "
            f"cpuset_cpus={worker.cpuset_cpus} cpuset_mems={worker.cpuset_mems} "
            f"cpu_capacity={worker.cpu_capacity} "
            f"memory_capacity_mb={worker.memory_capacity_mb}"
        )
    for spec in specs:
        print(f"run={spec.run_id}")
    print(f"total={len(specs)}")


def execute_experiment(
    manifest_path: Path,
    *,
    resume: bool,
    rerun: set[str],
    run_ids: list[str],
) -> int:
    manifest = load_manifest(manifest_path)
    all_specs = plan_runs(manifest)
    specs = select_specs(all_specs, run_ids)
    workers = validate_execution_plan(manifest, all_specs)
    store = ExperimentStore(EXPERIMENTS_ROOT, manifest.experiment_id)
    if resume or rerun:
        if not store.root.is_dir():
            raise FileNotFoundError(
                f"Experiment does not exist: experiment_id={manifest.experiment_id!r}, "
                f"path={store.root}"
            )
        require_original_checkout(store)
    else:
        require_clean_checkout()
        if store.root.exists():
            raise FileExistsError(
                f"Experiment already exists: experiment_id={manifest.experiment_id!r}, "
                f"path={store.root}"
            )
    runner = ExperimentRunner(manifest, store, workers)
    runner.initialize(specs)
    return runner.run(specs, rerun)


def stored_manifest(experiment_id: str) -> Path:
    experiment_id = validate_identifier(experiment_id, "experiment_id")
    path = EXPERIMENTS_ROOT / experiment_id / "manifest.yaml"
    if not path.is_file():
        raise FileNotFoundError(
            f"Experiment manifest does not exist: experiment_id={experiment_id!r}, path={path}"
        )
    return path


def _run_persistent_scenario_engine(engine, output_dir: Path) -> dict:
    result = engine.run()
    if engine.persistent_scenario_run is None:
        raise RuntimeError(
            "Persistent Scenario run finished without a PersistentScenarioRun: "
            f"run_id={engine.run_id!r}, result={result!r}"
        )
    engine.persistent_scenario_run.agent_llm_usage = engine.export_agent_llm_usage()
    from src.persistent_scenarios.runtime.trace import export_persistent_scenario_trace

    result = dict(result)
    result["trace_path"] = export_persistent_scenario_trace(engine.persistent_scenario_run, output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return result


def _mock_gate_agent(spec, gate: str):
    """Build the deterministic gate agent for one Persistent Scenario path.

    zero keeps the session idle (engine gate name "no-agent"); complete/wrong
    run the instance gate script remediation once per alert; prefix gates
    repair only the first alert (resolved) or never (unresolved) so the
    second event arrives on the promised prefix state without waiting for it.
    """
    from src.agents.mock_persistent_scenario_agent import (
        MockPersistentScenarioAgent,
        ZeroPersistentScenarioAgent,
    )
    from .persistent_scenarios.backend.postgres.gate_scripts import gate_script
    from .persistent_scenarios.model.enums import EventTrigger

    if gate == "zero":
        return ZeroPersistentScenarioAgent()
    script = gate_script(spec.scenario_id)
    scripted_path = "oracle" if gate in {"complete", "resolved-prefix", "unresolved-prefix"} else "wrong"
    alert_count = sum(1 for event in spec.events if event.trigger is EventTrigger.ALERT)
    if gate == "resolved-prefix":
        plans = (script.action_plan("oracle"), *(((),) * (alert_count - 1)))
    else:
        plans = (script.action_plan(scripted_path),) * alert_count
    return MockPersistentScenarioAgent(
        reference_actions=plans,
        reference_reports=(script.reference_report,),
        repair=gate not in {"unresolved-prefix", "zero"},
    )


def run_persistent_scenario_command(
    persistent_scenario_path: Path,
    *,
    agent_name: str,
    run_id: str,
    port: int,
    output_dir: Path,
    max_turns: int,
    max_output_tokens: int | None = None,
    run_mode: str = "development",
    time_scale: float = 1.0,
    model: str | None = None,
    llm_config: str = "config/llm_config.json",
    reasoning_effort: str | None = None,
) -> int:
    from src.agents.agent import LLMAgent
    from src.agents.persistent_scenario_agent import LLMPersistentScenarioAgent
    from src.agents.mock_persistent_scenario_agent import ZeroPersistentScenarioAgent
    from src.agents.baselines.v_expel import VExpeLAgent, VExpeLCompiler, VExpeLConfig, VExpeLMemory
    from src.agents.factory import parse_agent_settings
    from .persistent_scenarios.api import (
        build_persistent_scenario_engine,
        build_postgres_backend,
        build_real_clock,
        build_tidb_backend,
        load_definition,
    )
    from src.database.system import DatabaseSystem

    spec = load_definition(persistent_scenario_path)
    if spec.system is DatabaseSystem.TIDB:
        backend = build_tidb_backend(spec)
    elif spec.system is DatabaseSystem.POSTGRESQL:
        backend = build_postgres_backend(spec, evidence_root=output_dir)
    else:
        raise ValueError(
            f"Unsupported PersistentScenario system: "
            f"scenario_id={spec.scenario_id!r}, system={spec.system.value!r}"
        )
    trusted_checkpoint_observer = None
    if agent_name == "mock":
        agent = _mock_gate_agent(spec, "complete")

        def agent_factory(context):
            return agent
    elif agent_name == "zero":
        def agent_factory(context):
            return ZeroPersistentScenarioAgent()
    elif agent_name == "llm":
        def agent_factory(context):
            client = LLMAgent(
                model=model,
                config_path=llm_config,
                use_native_tools=True,
                max_output_tokens=max_output_tokens,
                reasoning_effort=reasoning_effort,
            )
            return LLMPersistentScenarioAgent.from_llm_client(client, max_turns=max_turns)
    elif agent_name == "v-expel":
        config = VExpeLConfig.from_settings(
            parse_agent_settings(os.environ.get("AIOPS_AGENT_SETTINGS", "{}"))
        )
        memory = VExpeLMemory()
        compiler = VExpeLCompiler(memory)
        trusted_checkpoint_observer = compiler.observe

        def agent_factory(context):
            client = LLMAgent(
                model=model,
                config_path=llm_config,
                use_native_tools=True,
                max_output_tokens=max_output_tokens,
                context_compaction=config.context_compaction,
                reasoning_effort=reasoning_effort,
            )
            return VExpeLAgent.from_llm_client(
                client,
                memory,
                compiler=compiler,
                max_turns=max_turns,
                retrieval_top_k=config.retrieval_top_k,
            )
    else:
        raise ValueError(f"Unsupported PersistentScenario agent: agent={agent_name!r}")
    engine = build_persistent_scenario_engine(
        spec,
        backend,
        agent_factory,
        run_id=run_id, port=port, clock=build_real_clock(), output_dir=str(output_dir),
        run_mode=run_mode,
        time_scale=time_scale,
        trusted_checkpoint_observer=trusted_checkpoint_observer,
    )
    result = _run_persistent_scenario_engine(engine, output_dir)
    return 0 if result.get("valid") is True else 1


def _configure_persistent_scenario_gate_resources(
    spec,
    *,
    cpuset_cpus: str | None,
    cpuset_mems: str | None,
    postgres_storage_root: str | None,
) -> None:
    values = {
        "AIOPS_CPUSET_CPUS": cpuset_cpus or os.environ.get("AIOPS_CPUSET_CPUS"),
        "AIOPS_CPUSET_MEMS": cpuset_mems or os.environ.get("AIOPS_CPUSET_MEMS"),
        "AIOPS_POSTGRES_STORAGE_ROOT": postgres_storage_root or os.environ.get("AIOPS_POSTGRES_STORAGE_ROOT"),
    }
    missing = sorted(key for key, value in values.items() if not value)
    if missing:
        raise RuntimeError(
            "Persistent Scenario gate requires an explicit worker resource contract: "
            f"missing={missing!r}"
        )
    resources = spec.environment.nodes[0].resources
    os.environ.update({
        **values,
        "AIOPS_CPU_LIMIT": str(resources.container_cpu_limit),
        "AIOPS_MEMORY_MB": str(resources.container_memory_mb),
    })


_ENGINE_GATE_NAMES = {
    "healthy": "baseline",
    "zero": "no-agent",
    "complete": "oracle",
    "wrong": "wrong-action",
    "resolved-prefix": "resolved-prefix",
    "unresolved-prefix": "unresolved-prefix",
    "prevented-prefix": "prevented-prefix",
}


_PREFIX_EXPECTED_STATUS = {
    "resolved-prefix": "resolved",
    "unresolved-prefix": "applied",
    "prevented-prefix": "prevented",
}


def _gate_passed(gate: str, result: Mapping) -> bool:
    if gate == "healthy":
        return result.get("BaselinePass") is True
    if gate == "zero":
        objective_results = result.get("objective_results") or ()
        return result.get("OutcomePass") is False and any(item.get("pass") is False for item in objective_results)
    if gate == "complete":
        return (
            result.get("OutcomePass") is True
            and result.get("SafePass") is True
            and result.get("DiagnosisPass") is not False
        )
    if gate == "wrong":
        return result.get("SafePass") is False
    if gate in _PREFIX_EXPECTED_STATUS:
        return result.get("gate_result", {}).get("prefix_status") == _PREFIX_EXPECTED_STATUS[gate]
    raise ValueError(f"Unknown Persistent Scenario gate: gate={gate!r}")


def validate_persistent_scenario_gate(
    persistent_scenario_path: Path,
    *,
    gate: str,
    run_id: str,
    port: int,
    time_scale: float,
    cpuset_cpus: str | None = None,
    cpuset_mems: str | None = None,
    postgres_storage_root: str | None = None,
) -> int:
    from .persistent_scenarios.api import (
        build_persistent_scenario_engine,
        build_postgres_backend,
        build_real_clock,
        build_tidb_backend,
        load_definition,
    )
    from src.database.system import DatabaseSystem
    from src.agents.mock_persistent_scenario_agent import ZeroPersistentScenarioAgent

    if gate not in _ENGINE_GATE_NAMES:
        raise ValueError(
            f"Unsupported Persistent Scenario gate: gate={gate!r}, allowed={sorted(_ENGINE_GATE_NAMES)!r}"
        )
    spec = load_definition(persistent_scenario_path)
    _configure_persistent_scenario_gate_resources(
        spec,
        cpuset_cpus=cpuset_cpus,
        cpuset_mems=cpuset_mems,
        postgres_storage_root=postgres_storage_root,
    )
    output_dir = Path(os.environ.get("AIOPS_TRACE_OUTPUT_DIR", "logs/traces"))
    backend = build_postgres_backend(spec, evidence_root=output_dir)
    if gate == "healthy":
        agent_factory = lambda context: ZeroPersistentScenarioAgent()
        event_activation = False
        evaluation_mode = "baseline"
    else:
        agent = _mock_gate_agent(spec, gate)
        agent_factory = lambda context: agent
        event_activation = True
        evaluation_mode = "persistent_scenario"
    engine = build_persistent_scenario_engine(
        spec,
        backend,
        agent_factory,
        run_id=run_id,
        port=port,
        clock=build_real_clock(),
        output_dir=str(output_dir),
        run_mode="development_compressed",
        time_scale=time_scale,
        gate_name=_ENGINE_GATE_NAMES[gate],
        event_activation=event_activation,
        evaluation_mode=evaluation_mode,
    )
    result = _run_persistent_scenario_engine(engine, output_dir)
    if result.get("valid") is not True:
        raise RuntimeError(
            "PersistentScenario gate produced an invalid run: "
            f"scenario_id={spec.scenario_id!r}, gate={gate!r}, result={result!r}"
        )
    gate_result = result.get("gate_result", {})
    if gate_result.get("sequence_pass") is not True:
        return 1
    return 0 if _gate_passed(gate, result) is True else 1


def load_named_dataset(dataset_id: str):
    return load_dataset_spec(dataset_spec_path(DATASET_DEFINITIONS_ROOT, dataset_id))


def pipeline_build(spec) -> Path:
    dataset_root = build_dataset_outputs(
        spec,
        PROJECT_ROOT,
        DATASET_OUTPUT_ROOT,
    )
    paper_script = PROJECT_ROOT / "paper" / "figures" / "python" / "scripts" / "build_dataset_figures.py"
    if not paper_script.is_file():
        raise FileNotFoundError(
            f"Dataset figure pipeline entrypoint does not exist: path={paper_script}"
        )
    subprocess.run(
        [
            sys.executable,
            str(paper_script),
            "--runs-csv",
            str(dataset_root / "runs.csv"),
            "--output-dir",
            str(PROJECT_ROOT / "paper" / "figures" / "output" / "datasets" / spec.dataset_id),
        ],
        cwd=PROJECT_ROOT / "paper",
        check=True,
    )
    return dataset_root


def track_dataset(spec) -> None:
    verify_dataset_lock(spec, PROJECT_ROOT)
    dataset_output = DATASET_OUTPUT_ROOT / spec.dataset_id
    if not (dataset_output / "provenance.json").is_file():
        raise FileNotFoundError(
            f"Build the frozen dataset before DVC tracking: dataset_id={spec.dataset_id!r}, "
            f"expected={dataset_output / 'provenance.json'}"
        )
    targets = [
        str(EXPERIMENTS_ROOT / experiment_id)
        for experiment_id in spec.experiment_ids
    ] + [str(dataset_output)]
    subprocess.run(
        [sys.executable, "-m", "dvc", "add", *targets],
        cwd=PROJECT_ROOT,
        check=True,
    )
    print("DVC pointers written for:")
    for target in targets:
        print(f"  {target}.dvc")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="aiopsbench")
    commands = root.add_subparsers(dest="command", required=True)

    experiment = commands.add_parser("experiment")
    experiment_commands = experiment.add_subparsers(dest="experiment_command", required=True)
    plan = experiment_commands.add_parser("plan")
    plan.add_argument("manifest", type=Path)
    plan.add_argument("--run-id", action="append", default=[])
    run = experiment_commands.add_parser("run")
    run.add_argument("manifest", type=Path)
    resume = experiment_commands.add_parser("resume")
    resume.add_argument("experiment_id")
    resume.add_argument("--run-id", action="append", default=[])
    rerun = experiment_commands.add_parser("rerun")
    rerun.add_argument("experiment_id")
    rerun.add_argument(
        "--status",
        choices=["succeeded", "failed", "timed_out", "interrupted"],
        action="append",
        required=True,
    )
    rerun.add_argument("--run-id", action="append", default=[])

    dataset = commands.add_parser("dataset")
    dataset_commands = dataset.add_subparsers(dest="dataset_command", required=True)
    create = dataset_commands.add_parser("create")
    create.add_argument("dataset_id")
    create.add_argument("--runs-json", type=Path, required=True)
    create.add_argument("--metric-contract", required=True)
    create.add_argument(
        "--data-status",
        choices=["provisional", "audited"],
        required=True,
    )
    compose = dataset_commands.add_parser("compose")
    compose.add_argument("dataset_id")
    compose.add_argument("--system", action="append", required=True)
    compose.add_argument("--category", action="append", required=True)
    compose.add_argument("--baseline", action="append")
    compose.add_argument("--metric-contract", required=True)
    compose.add_argument(
        "--data-status",
        choices=["provisional", "audited"],
        required=True,
    )
    freeze = dataset_commands.add_parser("freeze")
    freeze.add_argument("dataset_id")
    status = dataset_commands.add_parser("status")
    status.add_argument("dataset_id")
    diff = dataset_commands.add_parser("diff")
    diff.add_argument("before")
    diff.add_argument("after")
    track = dataset_commands.add_parser("track")
    track.add_argument("dataset_id")

    pipeline = commands.add_parser("pipeline")
    pipeline_commands = pipeline.add_subparsers(dest="pipeline_command", required=True)
    build = pipeline_commands.add_parser("build")
    build.add_argument("dataset_id")
    verify = pipeline_commands.add_parser("verify")
    verify.add_argument("dataset_id")

    persistent_scenario = commands.add_parser("persistent-scenario")
    persistent_scenario_commands = persistent_scenario.add_subparsers(dest="persistent_scenario_command", required=True)
    gate = persistent_scenario_commands.add_parser("gate")
    gate.add_argument("persistent_scenario", type=Path)
    gate.add_argument("--gate", choices=["healthy", "zero", "complete", "wrong", "resolved-prefix", "unresolved-prefix", "prevented-prefix"], required=True)
    gate.add_argument("--run-id", default="persistent-scenario-v1-gate")
    gate.add_argument("--port", type=int, default=16432)
    gate.add_argument("--time-scale", type=float, default=30.0)
    gate.add_argument("--cpuset-cpus")
    gate.add_argument("--cpuset-mems")
    gate.add_argument("--postgres-storage-root")
    run_persistent_scenario = persistent_scenario_commands.add_parser("run")
    run_persistent_scenario.add_argument("persistent_scenario", type=Path)
    run_persistent_scenario.add_argument("--agent", choices=["mock", "zero", "llm", "v-expel"], default="mock")
    run_persistent_scenario.add_argument("--model")
    run_persistent_scenario.add_argument("--llm-config", default="config/llm_config.json")
    run_persistent_scenario.add_argument("--run-id", default="persistent-scenario-run")
    run_persistent_scenario.add_argument("--port", type=int, default=16432)
    run_persistent_scenario.add_argument("--output-dir", type=Path)
    run_persistent_scenario.add_argument("--max-turns", type=int, default=30)
    run_persistent_scenario.add_argument("--max-output-tokens", type=int)
    run_persistent_scenario.add_argument("--reasoning-effort", choices=["low", "medium", "high", "xhigh"])
    run_persistent_scenario.add_argument("--run-mode", choices=["formal", "development", "development_compressed", "calibration_failure_probe"], default="development")
    run_persistent_scenario.add_argument("--time-scale", type=float, default=1.0)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "persistent-scenario":
        if args.persistent_scenario_command == "gate":
            return validate_persistent_scenario_gate(
                args.persistent_scenario,
                gate=args.gate,
                run_id=args.run_id,
                port=args.port,
                time_scale=args.time_scale,
                cpuset_cpus=args.cpuset_cpus,
                cpuset_mems=args.cpuset_mems,
                postgres_storage_root=args.postgres_storage_root,
            )
        output_dir = args.output_dir or Path(os.environ.get("AIOPS_TRACE_OUTPUT_DIR", "logs/traces"))
        return run_persistent_scenario_command(
            args.persistent_scenario,
            agent_name=args.agent,
            run_id=args.run_id,
            port=args.port,
            output_dir=output_dir,
            model=args.model,
            llm_config=args.llm_config,
            max_turns=args.max_turns,
            max_output_tokens=args.max_output_tokens,
            run_mode=args.run_mode,
            time_scale=args.time_scale,
            reasoning_effort=args.reasoning_effort,
        )
    if args.command == "experiment":
        if args.experiment_command == "plan":
            print_plan(args.manifest, args.run_id)
            return 0
        if args.experiment_command == "run":
            return execute_experiment(args.manifest, resume=False, rerun=set(), run_ids=[])
        if args.experiment_command == "resume":
            return execute_experiment(
                stored_manifest(args.experiment_id),
                resume=True,
                rerun=set(),
                run_ids=args.run_id,
            )
        return execute_experiment(
            stored_manifest(args.experiment_id),
            resume=True,
            rerun=set(args.status),
            run_ids=args.run_id,
        )

    if args.command == "dataset":
        if args.dataset_command == "compose":
            command = [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "compose_full_dataset.py"),
                    args.dataset_id,
                    "--metric-contract",
                    args.metric_contract,
                    "--data-status",
                    args.data_status,
                ]
            for system in args.system:
                command.extend(["--system", system])
            for category in args.category:
                command.extend(["--category", category])
            for baseline in args.baseline or []:
                command.extend(["--baseline", baseline])
            subprocess.run(command, cwd=PROJECT_ROOT, check=True)
            return 0
        if args.dataset_command == "create":
            selected_runs = json.loads(args.runs_json.read_text(encoding="utf-8"))
            if not isinstance(selected_runs, list):
                raise ValueError(
                    f"Dataset runs JSON must contain a list: path={args.runs_json}"
                )
            path = create_dataset_spec(
                DATASET_DEFINITIONS_ROOT,
                args.dataset_id,
                selected_runs,
                args.metric_contract,
                args.data_status,
            )
            print(path)
            return 0
        if args.dataset_command == "freeze":
            spec = load_named_dataset(args.dataset_id)
            print(freeze_dataset(spec, PROJECT_ROOT, EXPERIMENTS_ROOT))
            return 0
        if args.dataset_command == "status":
            spec = load_named_dataset(args.dataset_id)
            frozen = dataset_lock_path(spec).is_file()
            records = records_from_lock(spec) if frozen else load_live_records(spec, EXPERIMENTS_ROOT)
            print(json.dumps({
                "dataset_id": spec.dataset_id,
                "state": "frozen" if frozen else "live",
                **aggregate_dataset(records)["summary"],
            }, ensure_ascii=False, indent=2))
            return 0
        if args.dataset_command == "track":
            track_dataset(load_named_dataset(args.dataset_id))
            return 0
        before = load_named_dataset(args.before)
        after = load_named_dataset(args.after)
        print(json.dumps(diff_dataset_locks(before, after), ensure_ascii=False, indent=2))
        return 0

    spec = load_named_dataset(args.dataset_id)
    if args.pipeline_command == "verify":
        verify_dataset_lock(spec, PROJECT_ROOT)
        provenance_path = DATASET_OUTPUT_ROOT / spec.dataset_id / "provenance.json"
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance["dataset_lock_sha256"] != sha256(dataset_lock_path(spec)):
            raise ValueError(
                f"Derived dataset provenance is stale: dataset_id={spec.dataset_id!r}, "
                f"path={provenance_path}"
            )
        print(f"verified dataset={spec.dataset_id}")
        return 0
    print(pipeline_build(spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
