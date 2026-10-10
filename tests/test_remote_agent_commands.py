"""Every registered scenario entrypoint accepts a remote agent from a manifest."""
from pathlib import Path

import yaml


def test_all_registered_case_commands_accept_remote_agent(tmp_path):
    from src.scenarios import SCENARIO_REGISTRY
    from src.benchmark.manifest import load_manifest
    from src.benchmark.planner import plan_runs
    from src.benchmark.adapters.scenario import build_scenario_command, script_options
    root = Path(__file__).resolve().parents[1]
    for registration in SCENARIO_REGISTRY:
        if registration.entrypoint is None:
            continue
        raw = {'experiment_id': 'remote-contract',
               'benchmark': {'systems': [registration.system.value], 'categories': [registration.category.value], 'scenarios': [registration.scenario_id]},
               'agents': [{'id': 'external-1', 'mode': 'remote', 'max_turns': 25, 'settings': {'endpoint': 'http://127.0.0.1:9236'}}],
               'runtime': {'port_base': 25000}}
        path = tmp_path / 'manifest.yaml'; path.write_text(yaml.safe_dump(raw))
        manifest = load_manifest(path)
        for spec in plan_runs(manifest):
            command = build_scenario_command(spec, manifest, root)
            options = script_options(root / 'examples' / spec.script)
            assert command[command.index('--model') + 1] == 'remote', command
            mode_flag = '--mode' if '--mode' in command else '--agent'
            assert command[command.index(mode_flag) + 1] == 'llm', command
            if '--max-turns' in options:
                assert command[command.index('--max-turns') + 1] == '25', command
            assert '--reasoning-effort' not in command, command
            assert command[command.index('--case') + 1] == spec.case_id
